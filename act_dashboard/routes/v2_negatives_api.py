"""N1b Gate 4 — Negatives Module JSON API.

Blueprint: v2_negatives_api_bp, URL prefix /v2/api/negatives.

Endpoints:
  GET  /search-term-review/<client_id>       (paginated list, view filter)
  POST /search-term-review/bulk-update       (approve/reject/override)
  POST /push-approved                         (mutate to Google Ads)
  POST /run-pass3                             (phrase-fragment engine)
  GET  /phrase-suggestions/<client_id>       (paginated list, view filter)
  POST /phrase-suggestions/bulk-update
  POST /push-phrase-suggestions
"""
import json
import logging
import os
import threading
import time
from datetime import date, datetime

import duckdb
from flask import Blueprint, jsonify, request

from act_dashboard.engine.negatives.pass3 import run_pass3
from act_dashboard.data_pipeline.google_ads_mutate import (
    push_negatives_to_shared_lists,
)

# N2 Part 2 + 4: per-client in-memory locks to stop two refresh or reclassify
# jobs racing against the same DuckDB + Google Ads customer. Keys are bare
# strings so the dict grows at most once per active client and we don't have
# to GC it (entries are cheap).
_REFRESH_LOCKS: dict[str, threading.Lock] = {}
_RECLASSIFY_LOCKS: dict[tuple[str, str], threading.Lock] = {}
_LOCKS_GUARD = threading.Lock()


def _refresh_lock(client_id: str) -> threading.Lock:
    with _LOCKS_GUARD:
        lk = _REFRESH_LOCKS.get(client_id)
        if lk is None:
            lk = _REFRESH_LOCKS[client_id] = threading.Lock()
        return lk


def _reclassify_lock(client_id: str, analysis_date_iso: str) -> threading.Lock:
    key = (client_id, analysis_date_iso)
    with _LOCKS_GUARD:
        lk = _RECLASSIFY_LOCKS.get(key)
        if lk is None:
            lk = _RECLASSIFY_LOCKS[key] = threading.Lock()
        return lk

v2_negatives_api_bp = Blueprint('v2_negatives_api', __name__,
                                url_prefix='/v2/api/negatives')

_WAREHOUSE_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'warehouse.duckdb')
)

logger = logging.getLogger('act_v2_neg_api')


def _db():
    return duckdb.connect(_WAREHOUSE_PATH)


def _err(code: str, detail: str, http: int = 400):
    return jsonify({'error': code, 'detail': detail}), http


def _parse_date(raw: str | None) -> date:
    if not raw:
        return date.today()
    return datetime.strptime(raw, '%Y-%m-%d').date()


# ---------------------------------------------------------------------------
# GET /search-term-review/<client_id>?date=YYYY-MM-DD&view=pending&page=1
# ---------------------------------------------------------------------------
# Wave A: 'all' returns unrestricted; 'block'/'review' split the pending bucket;
# 'keep' is unrestricted on review_status (keep rows stay pending forever);
# status-only buckets filter review_status. 'pending' kept for backwards-compat.
_ST_VIEW_FILTERS = {
    'all':      "1=1",
    'pending':  "pass1_status IN ('block','review') AND review_status='pending'",
    'block':    "pass1_status='block' AND review_status='pending'",
    'review':   "pass1_status='review' AND review_status='pending'",
    'keep':     "pass1_status='keep'",
    'approved': "review_status='approved'",
    'pushed':   "review_status='pushed'",
    'rejected': "review_status='rejected'",
    'expired':  "review_status='expired'",
}


@v2_negatives_api_bp.route('/search-term-review/<client_id>', methods=['GET'])
def list_search_term_reviews(client_id):
    try:
        analysis_date = _parse_date(request.args.get('date'))
    except ValueError:
        return _err('bad_date', "date must be YYYY-MM-DD")
    view = request.args.get('view', 'pending')
    if view not in _ST_VIEW_FILTERS:
        return _err('bad_view', f"view must be one of {sorted(_ST_VIEW_FILTERS)}")
    try:
        page = max(1, int(request.args.get('page', 1)))
        page_size = max(1, min(500, int(request.args.get('page_size', 100))))
    except ValueError:
        return _err('bad_paging', "page / page_size must be integers")

    # Wave C10: campaign_source filter. 'all' uses stored r.total_* metrics;
    # 'search'/'pmax' re-aggregates from act_v2_search_terms filtered by
    # campaign_type, and scopes rows/counts to those with non-zero
    # contribution from that source.
    campaign_source = request.args.get('campaign_source', 'all').lower()
    if campaign_source not in ('all', 'search', 'pmax'):
        return _err('bad_campaign_source',
                    "campaign_source must be one of all|search|pmax")

    offset = (page - 1) * page_size

    # Build WHERE clauses in two qualified forms side-by-side so that:
    #  - standalone queries (total / counts / reason_counts) use unqualified
    #    columns on act_v2_search_term_reviews,
    #  - the rows query, which LEFT JOINs act_v2_search_terms, uses
    #    r.client_id / r.analysis_date / r.id to stay unambiguous post-join.
    # Both forms share the same parameter list (positional bindings).
    where_clauses: list[str] = []
    where_clauses_r: list[str] = []
    params: list = []

    where_clauses.append("client_id = ?")
    where_clauses_r.append("r.client_id = ?")
    params.append(client_id)

    where_clauses.append("analysis_date = ?")
    where_clauses_r.append("r.analysis_date = ?")
    params.append(analysis_date)

    # view filter (e.g. 1=1 for 'all'); columns like pass1_status/
    # review_status exist only on act_v2_search_term_reviews so they're
    # unambiguous in both contexts — reuse verbatim.
    where_clauses.append(_ST_VIEW_FILTERS[view])
    where_clauses_r.append(_ST_VIEW_FILTERS[view])

    # Wave A: optional reasons= CSV param (AND with view, OR among reasons)
    reasons_raw = request.args.get('reasons') or ''
    reasons = [r.strip() for r in reasons_raw.split(',') if r.strip()]
    if reasons:
        placeholders = ','.join(['?'] * len(reasons))
        where_clauses.append(f"pass1_reason IN ({placeholders})")
        where_clauses_r.append(f"r.pass1_reason IN ({placeholders})")
        params.extend(reasons)

    # Wave C10: source-ids subquery restricts review rows to those with at
    # least one matching-type source row (impr>0 or clicks>0). The
    # subquery itself is identical in both forms (inner r2.* references
    # are unaffected by the outer alias); only the outer `id` column needs
    # qualification.
    source_ids_params: list = []
    source_ids_subquery_body = ''
    if campaign_source != 'all':
        ct = 'SEARCH' if campaign_source == 'search' else 'PERFORMANCE_MAX'
        source_ids_subquery_body = """ IN (
            SELECT r2.id FROM act_v2_search_term_reviews r2
            JOIN act_v2_search_terms st2
              ON st2.client_id   = r2.client_id
             AND st2.search_term = r2.search_term
             AND st2.snapshot_date BETWEEN r2.first_seen_date AND r2.last_seen_date
            WHERE r2.client_id = ?
              AND r2.analysis_date = ?
              AND st2.campaign_type = ?
            GROUP BY r2.id
            HAVING COALESCE(SUM(st2.impressions),0) > 0
                OR COALESCE(SUM(st2.clicks),0) > 0
        )"""
        source_ids_params = [client_id, analysis_date, ct]
        where_clauses.append(f"id{source_ids_subquery_body}")
        where_clauses_r.append(f"r.id{source_ids_subquery_body}")
        params.extend(source_ids_params)

    where      = ' AND '.join(where_clauses)
    where_rows = ' AND '.join(where_clauses_r)

    con = _db()
    try:
        total = con.execute(
            f"SELECT COUNT(*) FROM act_v2_search_term_reviews WHERE {where}",
            params,
        ).fetchone()[0]
        # Wave C11: aggregate FIRST over the full filtered set, then sort +
        # LIMIT/OFFSET. Previous version (Wave C10) put LIMIT/OFFSET inside
        # a base CTE that sliced review rows BEFORE the JOIN+SUM ran, so
        # pagination with small page_size returned arbitrary rows instead
        # of the highest-impression ones. Tie-break on total_clicks then
        # r.id so ordering is stable across pages.
        st_type_filter = ''
        st_type_filter_params: list = []
        if campaign_source != 'all':
            ct = 'SEARCH' if campaign_source == 'search' else 'PERFORMANCE_MAX'
            st_type_filter = 'AND st.campaign_type = ?'
            st_type_filter_params = [ct]

        rows = con.execute(
            f"""
            WITH source_agg AS (
              SELECT r.id, r.search_term, r.analysis_date,
                     r.first_seen_date, r.last_seen_date,
                     COALESCE(SUM(st.impressions), 0)  AS total_impressions,
                     COALESCE(SUM(st.clicks), 0)       AS total_clicks,
                     SUM(st.cost)                      AS total_cost,
                     COALESCE(SUM(st.conversions), 0)  AS total_conversions,
                     r.pass1_status, r.pass1_reason, r.pass1_reason_detail,
                     r.pass2_target_list_role,
                     r.review_status, r.reviewed_at, r.reviewed_by,
                     r.pushed_to_ads_at, r.pushed_google_ads_criterion_id,
                     r.push_error,
                     STRING_AGG(DISTINCT st.campaign_name, ', ') AS campaigns,
                     STRING_AGG(DISTINCT st.campaign_type, ', ') AS campaign_types,
                     STRING_AGG(DISTINCT st.ad_group_name, ', ') AS ad_groups,
                     STRING_AGG(DISTINCT st.keyword_text, ', ')  AS keywords,
                     STRING_AGG(DISTINCT st.match_type, ', ')    AS match_types,
                     STRING_AGG(DISTINCT st.status, ', ')        AS statuses,
                     CASE WHEN SUM(st.clicks) > 0
                          THEN SUM(st.cost) / SUM(st.clicks) ELSE NULL END AS agg_avg_cpc,
                     CASE WHEN SUM(st.impressions) > 0
                          THEN SUM(st.clicks)::DOUBLE / SUM(st.impressions)
                          ELSE NULL END                                    AS agg_ctr,
                     CASE WHEN SUM(st.conversions) > 0
                          THEN SUM(st.cost) / SUM(st.conversions) ELSE NULL END AS agg_cost_per_conv,
                     CASE WHEN SUM(st.clicks) > 0
                          THEN SUM(st.conversions)::DOUBLE / SUM(st.clicks)
                          ELSE NULL END                                    AS agg_conv_rate
              FROM act_v2_search_term_reviews r
              LEFT JOIN act_v2_search_terms st
                     ON st.client_id   = r.client_id
                    AND st.search_term = r.search_term
                    AND st.snapshot_date BETWEEN r.first_seen_date AND r.last_seen_date
                    {st_type_filter}
              WHERE {where_rows}
              GROUP BY r.id, r.search_term, r.analysis_date,
                       r.first_seen_date, r.last_seen_date,
                       r.pass1_status, r.pass1_reason, r.pass1_reason_detail,
                       r.pass2_target_list_role,
                       r.review_status, r.reviewed_at, r.reviewed_by,
                       r.pushed_to_ads_at, r.pushed_google_ads_criterion_id,
                       r.push_error
            )
            SELECT id, search_term, analysis_date,
                   first_seen_date, last_seen_date,
                   total_impressions, total_clicks, total_cost, total_conversions,
                   pass1_status, pass1_reason, pass1_reason_detail,
                   pass2_target_list_role,
                   review_status, reviewed_at, reviewed_by,
                   pushed_to_ads_at, pushed_google_ads_criterion_id, push_error,
                   campaigns, campaign_types, ad_groups, keywords, match_types, statuses,
                   agg_avg_cpc, agg_ctr, agg_cost_per_conv, agg_conv_rate
            FROM source_agg
            ORDER BY total_impressions DESC NULLS LAST,
                     total_clicks DESC NULLS LAST,
                     id ASC
            LIMIT ? OFFSET ?
            """,
            st_type_filter_params + params + [page_size, offset],
        ).fetchall()

        # Wave D1 (Fix 5) — cross-filtering cascade: chip counts should reflect
        # the OTHER active filter so what the user sees in the table matches the
        # counts on the pills they haven't clicked.
        #   status chips   -> scope = client+date+campaign_source+reasons  (ignore view)
        #   reason chips   -> scope = client+date+campaign_source+view     (ignore reasons)
        # campaign_source chips stay globally scoped (client+date only) so users
        # can see absolute totals for each source regardless of other filters.
        src_clause = (' AND id' + source_ids_subquery_body) if source_ids_subquery_body else ''
        src_params = list(source_ids_params)

        # reasons clause (for status-chip scope)
        reasons_clause = ''
        reasons_params: list = []
        if reasons:
            ph = ','.join(['?'] * len(reasons))
            reasons_clause = f" AND pass1_reason IN ({ph})"
            reasons_params = list(reasons)

        # view clause (for reason-chip scope) — reuse the same SQL fragment the
        # rows query uses, but only when view != 'all'. When view='all' (1=1)
        # we don't need to append anything.
        view_sql = _ST_VIEW_FILTERS[view]
        view_clause = f" AND ({view_sql})" if view_sql != "1=1" else ''

        counts_row = con.execute(
            f"""SELECT
                 COUNT(*) FILTER (WHERE review_status='pending' AND pass1_status='block')  AS block,
                 COUNT(*) FILTER (WHERE review_status='pending' AND pass1_status='review') AS review,
                 COUNT(*) FILTER (WHERE pass1_status='keep')                               AS keep,
                 COUNT(*) FILTER (WHERE review_status='approved')                          AS approved,
                 COUNT(*) FILTER (WHERE review_status='pushed')                            AS pushed,
                 COUNT(*) FILTER (WHERE review_status='rejected')                          AS rejected,
                 COUNT(*) FILTER (WHERE review_status='expired')                           AS expired,
                 COUNT(*)                                                                   AS total
               FROM act_v2_search_term_reviews
               WHERE client_id = ? AND analysis_date = ?{src_clause}{reasons_clause}""",
            [client_id, analysis_date] + src_params + reasons_params,
        ).fetchone()
        counts = {
            'all':      int(counts_row[7] or 0),
            'block':    int(counts_row[0] or 0),
            'review':   int(counts_row[1] or 0),
            'keep':     int(counts_row[2] or 0),
            'approved': int(counts_row[3] or 0),
            'pushed':   int(counts_row[4] or 0),
            'rejected': int(counts_row[5] or 0),
            'expired':  int(counts_row[6] or 0),
        }
        reason_rows = con.execute(
            f"""SELECT pass1_reason, COUNT(*)
               FROM act_v2_search_term_reviews
               WHERE client_id = ? AND analysis_date = ?{src_clause}{view_clause}
               GROUP BY pass1_reason""",
            [client_id, analysis_date] + src_params,
        ).fetchall()
        reason_counts = {(r[0] or 'unknown'): int(r[1]) for r in reason_rows}

        # Wave D1 (Fix 3) — approved-but-not-pushed count for the whole
        # client+date (NOT scoped by any chip filter). Drives the Push button:
        # if the user approved rows from Block view, then switched away, they
        # shouldn't lose access to the Push action just because those rows are
        # no longer visible.
        approved_ready_count = int(con.execute(
            """SELECT COUNT(*) FROM act_v2_search_term_reviews
               WHERE client_id = ? AND analysis_date = ?
                 AND review_status = 'approved'
                 AND pushed_to_ads_at IS NULL""",
            [client_id, analysis_date],
        ).fetchone()[0] or 0)

        # Wave C10: campaign_source chip counts. 'all' = distinct review
        # rows for today (global, unaffected by current source filter so
        # the chip the user just clicked still shows the absolute figure).
        # 'search'/'pmax' = distinct reviews with at least one matching-type
        # source row (impr>0 OR clicks>0). Search+PMax may exceed All due to
        # overlap — that's correct (same term from both campaigns).
        cs_row = con.execute(
            """SELECT
                 (SELECT COUNT(*) FROM act_v2_search_term_reviews
                  WHERE client_id = ? AND analysis_date = ?)                 AS all_count,
                 (SELECT COUNT(DISTINCT r.id)
                  FROM act_v2_search_term_reviews r
                  JOIN act_v2_search_terms st
                    ON st.client_id = r.client_id
                   AND st.search_term = r.search_term
                   AND st.snapshot_date BETWEEN r.first_seen_date AND r.last_seen_date
                   AND st.campaign_type = 'SEARCH'
                   AND (COALESCE(st.impressions,0) > 0 OR COALESCE(st.clicks,0) > 0)
                  WHERE r.client_id = ? AND r.analysis_date = ?)             AS search_count,
                 (SELECT COUNT(DISTINCT r.id)
                  FROM act_v2_search_term_reviews r
                  JOIN act_v2_search_terms st
                    ON st.client_id = r.client_id
                   AND st.search_term = r.search_term
                   AND st.snapshot_date BETWEEN r.first_seen_date AND r.last_seen_date
                   AND st.campaign_type = 'PERFORMANCE_MAX'
                   AND (COALESCE(st.impressions,0) > 0 OR COALESCE(st.clicks,0) > 0)
                  WHERE r.client_id = ? AND r.analysis_date = ?)             AS pmax_count
            """,
            [client_id, analysis_date,
             client_id, analysis_date,
             client_id, analysis_date],
        ).fetchone()
        campaign_source_counts = {
            'all':    int(cs_row[0] or 0),
            'search': int(cs_row[1] or 0),
            'pmax':   int(cs_row[2] or 0),
        }

        # Wave C4: live target-list labels — read current names from the
        # ingested negative-keyword lists so the dropdown stays in sync
        # when user renames lists in Google Ads (next ingestion refreshes
        # this map, page reload picks it up). Only LINKED lists.
        tl_rows = con.execute(
            """SELECT list_role, list_name
               FROM act_v2_negative_keyword_lists
               WHERE client_id = ?
                 AND list_role IS NOT NULL
                 AND is_linked_to_campaign = TRUE""",
            [client_id],
        ).fetchall()
        target_list_labels = {r[0]: r[1] for r in tl_rows}

        # Wave B Gate C: PMax "Other search terms" bucket aggregated across
        # all PMax campaigns for this client on analysis_date. Always computed
        # from the latest snapshot_date the reviews reference (last_seen_date),
        # which for the narrowed 1-day window = yesterday's ingestion.
        # Returns None when no Other-bucket row exists (no PMax or bucket
        # wasn't populated for that date).
        st_latest = con.execute(
            """SELECT MAX(last_seen_date) FROM act_v2_search_term_reviews
               WHERE client_id = ? AND analysis_date = ?""",
            [client_id, analysis_date],
        ).fetchone()[0]
        pmax_other = None
        if st_latest is not None:
            bucket_row = con.execute(
                """SELECT SUM(impressions), SUM(clicks), SUM(cost),
                          SUM(conversions), SUM(distinct_term_count),
                          MIN(snapshot_date)
                   FROM act_v2_pmax_other_bucket
                   WHERE client_id = ? AND snapshot_date = ?""",
                [client_id, st_latest],
            ).fetchone()
            if bucket_row and bucket_row[0] is not None:
                pmax_other = {
                    'snapshot_date':         bucket_row[5].isoformat() if bucket_row[5] else None,
                    'impressions':           int(bucket_row[0] or 0),
                    'clicks':                int(bucket_row[1] or 0),
                    'cost':                  float(bucket_row[2]) if bucket_row[2] is not None else None,
                    'conversions':           float(bucket_row[3]) if bucket_row[3] is not None else None,
                    'distinct_term_count':   int(bucket_row[4]) if bucket_row[4] is not None else None,
                }
    finally:
        con.close()

    items = []
    for r in rows:
        items.append({
            'id': r[0], 'search_term': r[1],
            'analysis_date': r[2].isoformat() if r[2] else None,
            'first_seen_date': r[3].isoformat() if r[3] else None,
            'last_seen_date':  r[4].isoformat() if r[4] else None,
            'total_impressions': r[5], 'total_clicks': r[6],
            'total_cost': float(r[7]) if r[7] is not None else None,
            'total_conversions': float(r[8]) if r[8] is not None else None,
            'pass1_status': r[9], 'pass1_reason': r[10],
            'pass1_reason_detail': r[11],
            'pass2_target_list_role': r[12],
            'review_status': r[13],
            'reviewed_at': r[14].isoformat() if r[14] else None,
            'reviewed_by': r[15],
            'pushed_to_ads_at': r[16].isoformat() if r[16] else None,
            'pushed_google_ads_criterion_id': r[17],
            'push_error': r[18],
            # Wave B Gate C context aggregates (comma-sep strings)
            'campaigns':      r[19],
            'campaign_types': r[20],
            'ad_groups':      r[21],
            'keywords':       r[22],
            'match_types':    r[23],
            'statuses':       r[24],
            'avg_cpc':             float(r[25]) if r[25] is not None else None,
            'ctr':                 float(r[26]) if r[26] is not None else None,
            'cost_per_conversion': float(r[27]) if r[27] is not None else None,
            'conversion_rate':     float(r[28]) if r[28] is not None else None,
        })
    return jsonify({
        'items': items, 'total': int(total),
        'page': page, 'page_size': page_size,
        'view': view, 'analysis_date': analysis_date.isoformat(),
        'counts': counts,
        'reason_counts': reason_counts,
        'reasons_filter': reasons,
        'pmax_other_bucket': pmax_other,
        'target_list_labels': target_list_labels,
        'campaign_source': campaign_source,
        'campaign_source_counts': campaign_source_counts,
        'approved_ready_count': approved_ready_count,
    })


# ---------------------------------------------------------------------------
# POST /search-term-review/bulk-update
#   body: {client_id, items: [{id, review_status, pass2_target_list_role_override?}]}
# ---------------------------------------------------------------------------
@v2_negatives_api_bp.route('/search-term-review/bulk-update', methods=['POST'])
def bulk_update_search_term_reviews():
    data = request.get_json(silent=True) or {}
    client_id = data.get('client_id')
    items = data.get('items') or []
    if not client_id:
        return _err('missing_client_id', 'client_id required')
    if not isinstance(items, list) or not items:
        return _err('missing_items', 'items must be a non-empty array')

    allowed = {'approved', 'rejected', 'pending'}
    updated = 0
    con = _db()
    try:
        for it in items:
            try:
                row_id = int(it.get('id'))
            except (TypeError, ValueError):
                continue
            new_status = it.get('review_status')
            if new_status not in allowed:
                continue
            override = it.get('pass2_target_list_role_override')
            if override is None:
                con.execute(
                    """UPDATE act_v2_search_term_reviews
                       SET review_status = ?, reviewed_at = CURRENT_TIMESTAMP,
                           reviewed_by = 'user'
                       WHERE id = ? AND client_id = ?""",
                    [new_status, row_id, client_id],
                )
            else:
                con.execute(
                    """UPDATE act_v2_search_term_reviews
                       SET review_status = ?, reviewed_at = CURRENT_TIMESTAMP,
                           reviewed_by = 'user',
                           pass2_target_list_role = ?
                       WHERE id = ? AND client_id = ?""",
                    [new_status, override, row_id, client_id],
                )
            updated += 1
    finally:
        con.close()
    return jsonify({'updated_count': updated})


# ---------------------------------------------------------------------------
# POST /push-approved
#   body: {client_id, analysis_date?}
# ---------------------------------------------------------------------------
@v2_negatives_api_bp.route('/push-approved', methods=['POST'])
def push_approved_search_terms():
    data = request.get_json(silent=True) or {}
    client_id = data.get('client_id')
    if not client_id:
        return _err('missing_client_id', 'client_id required')
    try:
        analysis_date = _parse_date(data.get('analysis_date'))
    except ValueError:
        return _err('bad_date', 'analysis_date must be YYYY-MM-DD')

    # Load approved-not-yet-pushed rows
    con = _db()
    try:
        rows = con.execute(
            """SELECT id, search_term, pass2_target_list_role
               FROM act_v2_search_term_reviews
               WHERE client_id = ? AND analysis_date = ?
                 AND review_status = 'approved'
                 AND pushed_to_ads_at IS NULL""",
            [client_id, analysis_date],
        ).fetchall()
    finally:
        con.close()
    if not rows:
        return jsonify({'succeeded_count': 0, 'failed_count': 0, 'failed_items': []})

    items = [{
        'source_table': 'search_term_reviews',
        'source_row_id': r[0],
        'keyword_text': r[1],
        'match_type': 'EXACT',
        'list_role': r[2],
    } for r in rows]

    result = push_negatives_to_shared_lists(client_id=client_id, items=items)

    # Persist results
    con = _db()
    try:
        for s in result['succeeded']:
            con.execute(
                """UPDATE act_v2_search_term_reviews
                   SET pushed_to_ads_at = CURRENT_TIMESTAMP,
                       pushed_google_ads_criterion_id = ?,
                       review_status = 'pushed',
                       push_error = NULL
                   WHERE id = ? AND client_id = ?""",
                [s['criterion_id'], s['source_row_id'], client_id],
            )
        for f in result['failed']:
            con.execute(
                """UPDATE act_v2_search_term_reviews
                   SET push_error = ?
                   WHERE id = ? AND client_id = ?""",
                [f['error'][:500], f['source_row_id'], client_id],
            )
    finally:
        con.close()

    return jsonify({
        'succeeded_count': len(result['succeeded']),
        'failed_count': len(result['failed']),
        'failed_items': [
            {'id': f['source_row_id'], 'search_term': f['keyword_text'], 'error': f['error']}
            for f in result['failed']
        ],
        'ops_budget_remaining': result.get('ops_budget_remaining'),
    })


# ---------------------------------------------------------------------------
# POST /run-pass3
#   body: {client_id, analysis_date?}
# ---------------------------------------------------------------------------
@v2_negatives_api_bp.route('/run-pass3', methods=['POST'])
def run_pass3_endpoint():
    data = request.get_json(silent=True) or {}
    client_id = data.get('client_id')
    if not client_id:
        return _err('missing_client_id', 'client_id required')
    try:
        analysis_date = _parse_date(data.get('analysis_date'))
    except ValueError:
        return _err('bad_date', 'analysis_date must be YYYY-MM-DD')

    try:
        summary = run_pass3(client_id, _WAREHOUSE_PATH, analysis_date)
    except Exception as e:  # noqa: BLE001
        logger.exception('pass3 failed')
        return _err('pass3_failed', str(e)[:400], http=500)
    return jsonify({'suggestions_created': summary['suggestions_created'],
                    'summary': summary})


# ---------------------------------------------------------------------------
# GET /phrase-suggestions/<client_id>
# ---------------------------------------------------------------------------
_PS_VIEW_FILTERS = {
    'pending':  "review_status='pending'",
    'approved': "review_status='approved'",
    'pushed':   "review_status='pushed'",
    'rejected': "review_status='rejected'",
}


@v2_negatives_api_bp.route('/phrase-suggestions/<client_id>', methods=['GET'])
def list_phrase_suggestions(client_id):
    try:
        analysis_date = _parse_date(request.args.get('date'))
    except ValueError:
        return _err('bad_date', "date must be YYYY-MM-DD")
    view = request.args.get('view', 'pending')
    if view not in _PS_VIEW_FILTERS:
        return _err('bad_view', f"view must be one of {sorted(_PS_VIEW_FILTERS)}")
    try:
        page = max(1, int(request.args.get('page', 1)))
        page_size = max(1, min(500, int(request.args.get('page_size', 100))))
    except ValueError:
        return _err('bad_paging', "page / page_size must be integers")

    offset = (page - 1) * page_size
    where = f"client_id = ? AND analysis_date = ? AND {_PS_VIEW_FILTERS[view]}"

    con = _db()
    try:
        total = con.execute(
            f"SELECT COUNT(*) FROM act_v2_phrase_suggestions WHERE {where}",
            [client_id, analysis_date],
        ).fetchone()[0]
        rows = con.execute(
            f"""SELECT id, analysis_date, fragment, word_count, target_list_role,
                       source_search_terms, occurrence_count, risk_level,
                       review_status, reviewed_at, reviewed_by,
                       pushed_to_ads_at, pushed_google_ads_criterion_id, push_error
                FROM act_v2_phrase_suggestions
                WHERE {where}
                ORDER BY word_count, occurrence_count DESC, id
                LIMIT ? OFFSET ?""",
            [client_id, analysis_date, page_size, offset],
        ).fetchall()
        # N1r: global approved-not-pushed count (unscoped by current view)
        # so the Push button on the frontend can enable regardless of what
        # the active filter is showing. Mirrors the search-term-review endpoint.
        approved_ready_count = int(con.execute(
            """SELECT COUNT(*) FROM act_v2_phrase_suggestions
               WHERE client_id = ? AND analysis_date = ?
                 AND review_status = 'approved' AND pushed_to_ads_at IS NULL""",
            [client_id, analysis_date],
        ).fetchone()[0])
        # N1u: per-status counts for chip labels on Pass 3 tab
        counts_rows = con.execute(
            """SELECT review_status, COUNT(*) FROM act_v2_phrase_suggestions
               WHERE client_id = ? AND analysis_date = ?
               GROUP BY review_status""",
            [client_id, analysis_date],
        ).fetchall()
        ps_counts = {s: 0 for s in ('pending', 'approved', 'pushed', 'rejected')}
        for status, n in counts_rows:
            if status in ps_counts:
                ps_counts[status] = int(n)
    finally:
        con.close()

    items = []
    for r in rows:
        sources = r[5]
        if isinstance(sources, str):
            try:
                sources = json.loads(sources)
            except json.JSONDecodeError:
                sources = []
        items.append({
            'id': r[0],
            'analysis_date': r[1].isoformat() if r[1] else None,
            'fragment': r[2], 'word_count': r[3],
            'target_list_role': r[4],
            'source_search_terms': sources,
            'occurrence_count': r[6], 'risk_level': r[7],
            'review_status': r[8],
            'reviewed_at': r[9].isoformat() if r[9] else None,
            'reviewed_by': r[10],
            'pushed_to_ads_at': r[11].isoformat() if r[11] else None,
            'pushed_google_ads_criterion_id': r[12],
            'push_error': r[13],
        })
    return jsonify({
        'items': items, 'total': int(total),
        'approved_ready_count': approved_ready_count,
        'counts': ps_counts,
        'page': page, 'page_size': page_size,
        'view': view, 'analysis_date': analysis_date.isoformat(),
    })


# ---------------------------------------------------------------------------
# POST /phrase-suggestions/bulk-update
# ---------------------------------------------------------------------------
@v2_negatives_api_bp.route('/phrase-suggestions/bulk-update', methods=['POST'])
def bulk_update_phrase_suggestions():
    data = request.get_json(silent=True) or {}
    client_id = data.get('client_id')
    items = data.get('items') or []
    if not client_id:
        return _err('missing_client_id', 'client_id required')
    if not isinstance(items, list) or not items:
        return _err('missing_items', 'items must be a non-empty array')

    allowed = {'approved', 'rejected', 'pending'}
    updated = 0
    con = _db()
    try:
        for it in items:
            try:
                row_id = int(it.get('id'))
            except (TypeError, ValueError):
                continue
            new_status = it.get('review_status')
            if new_status not in allowed:
                continue
            override = it.get('target_list_role_override')

            # N1q: DuckDB 1.1.0 raises a false-positive PK duplicate error
            # when UPDATE touches a UNIQUE-constrained column, even with the
            # same value. target_list_role is part of the UNIQUE on this
            # table — only set it when the value is actually changing.
            # Frontend always sends the dropdown value, so this is the
            # common path.
            touch_role = False
            if override is not None:
                current = con.execute(
                    """SELECT target_list_role
                       FROM act_v2_phrase_suggestions
                       WHERE id = ? AND client_id = ?""",
                    [row_id, client_id],
                ).fetchone()
                if current and current[0] != override:
                    touch_role = True

            if touch_role:
                con.execute(
                    """UPDATE act_v2_phrase_suggestions
                       SET review_status = ?, reviewed_at = CURRENT_TIMESTAMP,
                           reviewed_by = 'user',
                           target_list_role = ?
                       WHERE id = ? AND client_id = ?""",
                    [new_status, override, row_id, client_id],
                )
            else:
                con.execute(
                    """UPDATE act_v2_phrase_suggestions
                       SET review_status = ?, reviewed_at = CURRENT_TIMESTAMP,
                           reviewed_by = 'user'
                       WHERE id = ? AND client_id = ?""",
                    [new_status, row_id, client_id],
                )
            updated += 1
    finally:
        con.close()
    return jsonify({'updated_count': updated})


# ---------------------------------------------------------------------------
# POST /push-phrase-suggestions
# ---------------------------------------------------------------------------
@v2_negatives_api_bp.route('/push-phrase-suggestions', methods=['POST'])
def push_phrase_suggestions():
    data = request.get_json(silent=True) or {}
    client_id = data.get('client_id')
    if not client_id:
        return _err('missing_client_id', 'client_id required')
    try:
        analysis_date = _parse_date(data.get('analysis_date'))
    except ValueError:
        return _err('bad_date', 'analysis_date must be YYYY-MM-DD')

    con = _db()
    try:
        rows = con.execute(
            """SELECT id, fragment, target_list_role
               FROM act_v2_phrase_suggestions
               WHERE client_id = ? AND analysis_date = ?
                 AND review_status = 'approved'
                 AND pushed_to_ads_at IS NULL""",
            [client_id, analysis_date],
        ).fetchall()
    finally:
        con.close()
    if not rows:
        return jsonify({'succeeded_count': 0, 'failed_count': 0, 'failed_items': []})

    items = [{
        'source_table': 'phrase_suggestions',
        'source_row_id': r[0],
        'keyword_text': r[1],
        'match_type': 'PHRASE',  # Pass 3 always produces phrase-match negs
        'list_role': r[2],
    } for r in rows]

    result = push_negatives_to_shared_lists(client_id=client_id, items=items)

    con = _db()
    try:
        for s in result['succeeded']:
            con.execute(
                """UPDATE act_v2_phrase_suggestions
                   SET pushed_to_ads_at = CURRENT_TIMESTAMP,
                       pushed_google_ads_criterion_id = ?,
                       review_status = 'pushed',
                       push_error = NULL
                   WHERE id = ? AND client_id = ?""",
                [s['criterion_id'], s['source_row_id'], client_id],
            )
        for f in result['failed']:
            con.execute(
                """UPDATE act_v2_phrase_suggestions
                   SET push_error = ?
                   WHERE id = ? AND client_id = ?""",
                [f['error'][:500], f['source_row_id'], client_id],
            )
    finally:
        con.close()

    return jsonify({
        'succeeded_count': len(result['succeeded']),
        'failed_count': len(result['failed']),
        'failed_items': [
            {'id': f['source_row_id'], 'fragment': f['keyword_text'], 'error': f['error']}
            for f in result['failed']
        ],
        'ops_budget_remaining': result.get('ops_budget_remaining'),
    })


# ---------------------------------------------------------------------------
# N2 Part 2 — POST /refresh-snapshot  (pull current neg-list state from GAds)
# ---------------------------------------------------------------------------
@v2_negatives_api_bp.route('/refresh-snapshot', methods=['POST'])
def refresh_snapshot():
    data = request.get_json(silent=True) or {}
    client_id = data.get('client_id')
    if not client_id:
        return _err('missing_client_id', 'client_id required')

    lock = _refresh_lock(client_id)
    if not lock.acquire(blocking=False):
        return jsonify({
            'status': 'error',
            'message': 'A refresh is already in progress for this client.',
        }), 409

    try:
        con = _db()
        try:
            row = con.execute(
                "SELECT google_ads_customer_id FROM act_v2_clients WHERE client_id = ?",
                [client_id],
            ).fetchone()
        finally:
            con.close()
        if not row or not row[0]:
            return _err('bad_client', f'no customer_id for client_id={client_id}', 404)
        customer_id = row[0]

        from act_dashboard.data_pipeline.google_ads_ingestion import GoogleAdsDataPipeline

        today = date.today().strftime('%Y-%m-%d')
        start = time.time()
        pipeline = GoogleAdsDataPipeline(client_id=client_id, customer_id=customer_id)
        try:
            result = pipeline.ingest_negative_lists(today)
        finally:
            pipeline.close()
        duration = time.time() - start

        return jsonify({
            'status': 'ok',
            'snapshot_date': today,
            'list_count': result['lists'],
            'keyword_count': result['keywords'],
            'unmatched_names': result.get('unmatched_names', []),
            'duration_seconds': round(duration, 1),
        })
    except Exception as e:
        logger.exception(f'[refresh-snapshot] client_id={client_id}')
        return jsonify({
            'status': 'error',
            'message': str(e)[:500],
            'error_class': type(e).__name__,
        }), 500
    finally:
        lock.release()


# ---------------------------------------------------------------------------
# N2 Part 3 — GET /lists  (read-only viewer for Client Config tab)
# ---------------------------------------------------------------------------
@v2_negatives_api_bp.route('/lists', methods=['GET'])
def list_negative_lists():
    client_id = request.args.get('client_id')
    if not client_id:
        return _err('missing_client_id', 'client_id required')
    con = _db()
    try:
        snap_row = con.execute(
            "SELECT MAX(snapshot_date) FROM act_v2_negative_list_keywords WHERE client_id = ?",
            [client_id],
        ).fetchone()
        snapshot_date = snap_row[0] if snap_row and snap_row[0] else None
        if snapshot_date is None:
            return jsonify({
                'status': 'ok',
                'snapshot_date': None,
                'last_synced_at': None,
                'total_lists': 0,
                'total_keywords': 0,
                'lists': [],
            })

        last_sync_row = con.execute(
            "SELECT MAX(last_synced_at) FROM act_v2_negative_keyword_lists WHERE client_id = ?",
            [client_id],
        ).fetchone()
        last_synced_at = last_sync_row[0] if last_sync_row else None

        lists_rows = con.execute(
            """SELECT list_id, list_name, list_role, match_type,
                      keyword_count, is_linked_to_campaign
               FROM act_v2_negative_keyword_lists
               WHERE client_id = ?
               ORDER BY list_name""",
            [client_id],
        ).fetchall()

        kw_rows = con.execute(
            """SELECT list_id, keyword_text, match_type, added_at, added_by
               FROM act_v2_negative_list_keywords
               WHERE client_id = ? AND snapshot_date = ?
               ORDER BY list_id, keyword_text""",
            [client_id, snapshot_date],
        ).fetchall()

        by_list: dict[str, list] = {}
        for r in kw_rows:
            by_list.setdefault(r[0], []).append({
                'keyword_text': r[1],
                'match_type': r[2],
                'added_at': r[3].isoformat() if r[3] else None,
                'added_by': r[4] or 'unknown',
            })

        lists_payload = []
        total_kw = 0
        for lr in lists_rows:
            list_id, name, role, match_type, _kw_count, linked = lr
            kws = by_list.get(list_id, [])
            actual = len(kws)
            total_kw += actual
            lists_payload.append({
                'list_id': list_id,
                'list_name': name,
                'list_role': role,
                'match_type': match_type,
                'keyword_count': actual,
                'is_linked_to_campaign': bool(linked),
                'keywords': kws,
            })

        return jsonify({
            'status': 'ok',
            'snapshot_date': snapshot_date.isoformat() if hasattr(snapshot_date, 'isoformat') else str(snapshot_date),
            'last_synced_at': last_synced_at.isoformat() if last_synced_at else None,
            'total_lists': len(lists_payload),
            'total_keywords': total_kw,
            'lists': lists_payload,
        })
    finally:
        con.close()


# ---------------------------------------------------------------------------
# N2 Part 4 — POST /reclassify-now  (re-run Pass 1 + Pass 2 for today)
# ---------------------------------------------------------------------------
@v2_negatives_api_bp.route('/reclassify-now', methods=['POST'])
def reclassify_now():
    data = request.get_json(silent=True) or {}
    client_id = data.get('client_id')
    if not client_id:
        return _err('missing_client_id', 'client_id required')
    try:
        analysis_date = _parse_date(data.get('analysis_date'))
    except ValueError:
        return _err('bad_date', 'analysis_date must be YYYY-MM-DD')

    lock = _reclassify_lock(client_id, analysis_date.isoformat())
    if not lock.acquire(blocking=False):
        return jsonify({
            'status': 'error',
            'message': 'A reclassify is already in progress for this client/date.',
        }), 409
    try:
        from act_dashboard.engine.negatives.pass1 import run_pass1
        start = time.time()
        summary = run_pass1(client_id, _WAREHOUSE_PATH, analysis_date)
        duration = time.time() - start
        return jsonify({
            'status': 'ok',
            'analysis_date': analysis_date.isoformat(),
            'snapshot_date_used': summary.get('neg_snapshot_date'),
            'inserted': summary.get('inserted', 0),
            'updated': summary.get('updated', 0),
            'preserved': summary.get('preserved', 0),
            'duration_seconds': round(duration, 1),
        })
    except Exception as e:
        logger.exception(f'[reclassify-now] client_id={client_id}')
        return jsonify({
            'status': 'error',
            'message': str(e)[:500],
            'error_class': type(e).__name__,
        }), 500
    finally:
        lock.release()
