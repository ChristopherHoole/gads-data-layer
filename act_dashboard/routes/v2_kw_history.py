"""KW + Search Term History Viewer — Flask route + JSON API (Phase 3).

Brief: docs/BRIEF_KW_ST_HISTORY_VIEWER.md

Exposes:
  GET  /v2/kw-history                page shell
  GET  /v2/api/kw-history/rows       paginated + filtered rows (JSON)
  GET  /v2/api/kw-history/export.csv  current view as CSV (UTF-8 BOM)
  POST /v2/api/kw-history/override    set proposed_ad_group manually,
                                      flips proposal_method='manual'

DBD-only via ALLOWED_CLIENTS_V1; other clients return an empty result.

Server-side filtering + pagination — must load <2s with 40k+ rows.
DuckDB handles this comfortably for 145k rows with column-store scan.
"""
from __future__ import annotations

import csv
import io
import os
from datetime import date, datetime

import duckdb
from flask import Blueprint, Response, jsonify, render_template, request

v2_kw_history_bp = Blueprint('v2_kw_history', __name__)

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..'))
DB_PATH = os.path.join(PROJECT_ROOT, 'warehouse.duckdb')

ALLOWED_CLIENTS_V1 = {'dbd001'}

# Allow-listed sort + filter values so user input can't smuggle SQL.
ALLOWED_SORT = {
    'term': 'term', 'type': 'type',
    'impressions_total': 'impressions_total',
    'clicks_total': 'clicks_total',
    'cost_total': 'cost_total',
    'conversions_total': 'conversions_total',
    'old_campaign': 'old_campaign',
    'old_ad_group': 'old_ad_group',
    'in_new_ex': 'in_new_ex',
    'current_new_ex_ad_group': 'current_new_ex_ad_group',
    'proposed_ad_group': 'proposed_ad_group',
    'proposal_method': 'proposal_method',
}
ALLOWED_DIR = {'asc', 'desc'}
ALLOWED_TYPE_FILTER = {'all', 'keyword', 'search_term', 'both'}
ALLOWED_STATUS_FILTER = {'all', 'in_ex', 'proposed', 'unmapped', 'brand', 'low_volume'}
ALLOWED_METHOD_FILTER = {'all', 'rule', 'ai', 'manual',
                         'skip_brand', 'skip_low_volume', 'unset'}


def _db():
    return duckdb.connect(DB_PATH, read_only=True)


def _build_where_clause(args: dict) -> tuple[str, list]:
    """Return (sql_fragment, params) starting with WHERE — never trailing
    placeholders. Always anchors on client_id."""
    client_id = args.get('client', 'dbd001')
    # v1 hard-coded allowlist guard.
    if client_id not in ALLOWED_CLIENTS_V1:
        client_id = 'dbd001'

    where = ['client_id = ?']
    params: list = [client_id]

    type_f = args.get('type', 'all')
    if type_f in ALLOWED_TYPE_FILTER and type_f != 'all':
        where.append('type = ?')
        params.append(type_f)

    # Status filter buckets (16 May 2026 round 3): every non-'all' value
    # is a disjoint partition of the table — pill counts sum to total.
    # The old 'mapped' / 'unmapped' labels were ambiguous (the latter
    # silently included rule/AI/manual proposals); split into explicit
    # in_ex / proposed / unmapped buckets matching the card definitions.
    status_f = args.get('status', 'all')
    if status_f == 'in_ex':
        where.append('in_new_ex = TRUE')
    elif status_f == 'proposed':
        where.append('in_new_ex = FALSE')
        where.append("proposal_method IN ('rule','ai','manual')")
    elif status_f == 'unmapped':
        # Tightened in round 3 to exclude in_new_ex rows (which also
        # have proposal_method IS NULL because the engine doesn't
        # write a method when a row is already mapped). Without the
        # extra clause the pill double-counts the 1,044 in-ex rows.
        where.append('proposal_method IS NULL')
        where.append('in_new_ex = FALSE')
    elif status_f == 'brand':
        where.append("proposal_method = 'skip_brand'")
    elif status_f == 'low_volume':
        where.append("proposal_method = 'skip_low_volume'")

    method_f = args.get('method', 'all')
    if method_f in ALLOWED_METHOD_FILTER and method_f != 'all':
        if method_f == 'unset':
            where.append('proposal_method IS NULL')
        else:
            where.append('proposal_method = ?')
            params.append(method_f)

    campaign = (args.get('campaign') or '').strip()
    if campaign and campaign != 'all':
        where.append('old_campaign = ?')
        params.append(campaign)

    ex_ag = (args.get('ex_ad_group') or '').strip()
    if ex_ag and ex_ag != 'all':
        where.append('current_new_ex_ad_group = ?')
        params.append(ex_ag)

    q = (args.get('q') or '').strip()
    if q:
        where.append('term ILIKE ?')
        params.append(f'%{q}%')

    return 'WHERE ' + ' AND '.join(where), params


# ---------------------------------------------------------------------------
# Page route
# ---------------------------------------------------------------------------
@v2_kw_history_bp.route('/v2/kw-history')
def kw_history_page():
    client_id = request.args.get('client', 'dbd001')
    con = _db()
    try:
        clients = [
            {'id': r[0], 'name': r[1]}
            for r in con.execute(
                "SELECT client_id, client_name FROM act_v2_clients "
                "WHERE active=TRUE ORDER BY client_name"
            ).fetchall()
        ]
        row = con.execute(
            "SELECT client_id, client_name FROM act_v2_clients WHERE client_id = ?",
            [client_id],
        ).fetchone()
        if row:
            current_client = {'id': row[0], 'name': row[1]}
        else:
            current_client = clients[0] if clients else {'id': '', 'name': 'No Client'}

        # ACT last ran badge data (same source as Morning Review).
        last_ran_row = con.execute(
            "SELECT MAX(completed_at) FROM act_v2_scheduler_runs "
            "WHERE status = 'success'"
        ).fetchone()
        last_ran_raw = last_ran_row[0] if last_ran_row else None
        if isinstance(last_ran_raw, datetime):
            last_ran = last_ran_raw.strftime('%d %b %Y, %H:%M')
        elif last_ran_raw:
            last_ran = str(last_ran_raw)
        else:
            last_ran = None
        any_running_row = con.execute(
            "SELECT COUNT(*) FROM act_v2_scheduler_runs "
            "WHERE CAST(started_at AS DATE) = CURRENT_DATE AND status = 'running'"
        ).fetchone()
        any_running = bool(any_running_row and any_running_row[0])

        # Filter dropdown options.
        campaigns = [r[0] for r in con.execute(
            "SELECT DISTINCT old_campaign FROM kw_st_history "
            "WHERE client_id = ? AND old_campaign IS NOT NULL "
            "ORDER BY old_campaign",
            [current_client['id']],
        ).fetchall()]
        ex_ad_groups = [r[0] for r in con.execute(
            "SELECT DISTINCT current_new_ex_ad_group FROM kw_st_history "
            "WHERE client_id = ? AND current_new_ex_ad_group IS NOT NULL "
            "ORDER BY current_new_ex_ad_group",
            [current_client['id']],
        ).fetchall()]

        # Counts for the stats strip + status pill badges (round 3,
        # 16 May 2026): every bucket is a disjoint partition keyed on
        # the spec definitions, so cards 2+3 == card 1 AND cards
        # 4+5+6+7 == card 1 always hold. JS does a sanity check on
        # render and console.warns on drift.
        totals_row = con.execute(
            """SELECT
                 COUNT(*)                                                          AS total,
                 SUM(CASE WHEN in_new_ex                          THEN 1 ELSE 0 END) AS in_ex,
                 SUM(CASE WHEN NOT in_new_ex                      THEN 1 ELSE 0 END) AS not_in_ex,
                 SUM(CASE WHEN in_new_ex OR proposal_method IN ('rule','ai','manual')
                                                                  THEN 1 ELSE 0 END) AS total_mapped,
                 SUM(CASE WHEN NOT in_new_ex AND proposal_method IN ('rule','ai','manual')
                                                                  THEN 1 ELSE 0 END) AS proposed,
                 SUM(CASE WHEN proposal_method IS NULL AND NOT in_new_ex
                                                                  THEN 1 ELSE 0 END) AS unmapped,
                 SUM(CASE WHEN proposal_method = 'skip_brand'     THEN 1 ELSE 0 END) AS brand,
                 SUM(CASE WHEN proposal_method = 'skip_low_volume' THEN 1 ELSE 0 END) AS low_vol
               FROM kw_st_history WHERE client_id = ?""",
            [current_client['id']],
        ).fetchone()
        stats = {
            'total':        int(totals_row[0] or 0),
            'in_ex':        int(totals_row[1] or 0),
            'not_in_ex':    int(totals_row[2] or 0),
            'total_mapped': int(totals_row[3] or 0),
            'proposed':     int(totals_row[4] or 0),
            'unmapped':     int(totals_row[5] or 0),
            'brand':        int(totals_row[6] or 0),
            'low_volume':   int(totals_row[7] or 0),
        }
    finally:
        con.close()

    return render_template(
        'v2/kw_history.html',
        client=current_client,
        clients=clients,
        active_page='kw-history',
        today_date=date.today().strftime('%a %d %b %Y'),
        last_ran=last_ran,
        any_running=any_running,
        campaigns=campaigns,
        ex_ad_groups=ex_ad_groups,
        stats=stats,
    )


# ---------------------------------------------------------------------------
# JSON rows endpoint — pagination + filter + sort
# ---------------------------------------------------------------------------
@v2_kw_history_bp.route('/v2/api/kw-history/rows', methods=['GET'])
def kw_history_rows():
    args = request.args
    client_id = args.get('client', 'dbd001')
    if client_id not in ALLOWED_CLIENTS_V1:
        return jsonify({'status': 'skipped',
                        'reason': f'{client_id!r} not in v1 allowlist',
                        'rows': [], 'total': 0, 'page': 1, 'page_size': 100})

    try:
        page = max(1, int(args.get('page', '1')))
    except ValueError:
        page = 1
    try:
        page_size = int(args.get('page_size', '100'))
    except ValueError:
        page_size = 100
    page_size = max(10, min(500, page_size))

    sort_key = args.get('sort', 'clicks_total')
    sort_col = ALLOWED_SORT.get(sort_key, 'clicks_total')
    sort_dir = (args.get('dir', 'desc') or 'desc').lower()
    if sort_dir not in ALLOWED_DIR:
        sort_dir = 'desc'

    where_sql, params = _build_where_clause(args)

    con = _db()
    try:
        total = con.execute(
            f"SELECT COUNT(*) FROM kw_st_history {where_sql}",
            params,
        ).fetchone()[0]

        offset = (page - 1) * page_size
        # Default secondary tie-break: impressions DESC, term ASC.
        rows = con.execute(
            f"""SELECT
                    term, type, term_raw,
                    impressions_total, clicks_total, cost_total, conversions_total,
                    old_campaign, old_ad_group,
                    is_brand_campaign,
                    in_new_ex, current_new_ex_ad_group,
                    proposed_ad_group, proposal_method, proposal_rationale,
                    ai_cached_at
                FROM kw_st_history {where_sql}
                ORDER BY {sort_col} {sort_dir} NULLS LAST,
                         impressions_total DESC, term ASC
                LIMIT ? OFFSET ?""",
            params + [page_size, offset],
        ).fetchall()
    finally:
        con.close()

    items = [
        {
            'term': r[0], 'type': r[1], 'term_raw': r[2],
            'impressions_total': int(r[3] or 0),
            'clicks_total': int(r[4] or 0),
            'cost_total': float(r[5] or 0),
            'conversions_total': float(r[6] or 0),
            'old_campaign': r[7],
            'old_ad_group': r[8],
            'is_brand_campaign': bool(r[9]),
            'in_new_ex': bool(r[10]),
            'current_new_ex_ad_group': r[11],
            'proposed_ad_group': r[12],
            'proposal_method': r[13],
            'proposal_rationale': r[14],
            'ai_cached_at': r[15].isoformat() if r[15] else None,
        }
        for r in rows
    ]

    return jsonify({
        'status': 'ok',
        'total': int(total),
        'page': page,
        'page_size': page_size,
        'rows': items,
    })


# ---------------------------------------------------------------------------
# CSV export — current view (filters + sort respected)
# ---------------------------------------------------------------------------
@v2_kw_history_bp.route('/v2/api/kw-history/export.csv', methods=['GET'])
def kw_history_export_csv():
    args = request.args
    client_id = args.get('client', 'dbd001')
    if client_id not in ALLOWED_CLIENTS_V1:
        return Response('client_id not in v1 allowlist', status=403)

    sort_key = args.get('sort', 'clicks_total')
    sort_col = ALLOWED_SORT.get(sort_key, 'clicks_total')
    sort_dir = (args.get('dir', 'desc') or 'desc').lower()
    if sort_dir not in ALLOWED_DIR:
        sort_dir = 'desc'

    where_sql, params = _build_where_clause(args)

    con = _db()
    try:
        rows = con.execute(
            f"""SELECT
                    term, type,
                    impressions_total, clicks_total, cost_total, conversions_total,
                    old_campaign, old_ad_group,
                    is_brand_campaign,
                    in_new_ex, current_new_ex_ad_group,
                    proposed_ad_group, proposal_method, proposal_rationale
                FROM kw_st_history {where_sql}
                ORDER BY {sort_col} {sort_dir} NULLS LAST,
                         impressions_total DESC, term ASC""",
            params,
        ).fetchall()
    finally:
        con.close()

    # UTF-8 with BOM so Excel opens £/° cleanly. No em-dashes anywhere.
    buf = io.StringIO()
    buf.write('﻿')
    w = csv.writer(buf, quoting=csv.QUOTE_MINIMAL)
    w.writerow([
        'term', 'type',
        'impressions_total', 'clicks_total', 'cost_total', 'conversions_total',
        'old_campaign', 'old_ad_group', 'is_brand_campaign',
        'in_new_ex', 'current_new_ex_ad_group',
        'proposed_ad_group', 'proposal_method', 'proposal_rationale',
    ])
    for r in rows:
        clean = []
        for v in r:
            if isinstance(v, str):
                # Strip any em-dashes that may have slipped in (defensive).
                v = v.replace('—', '-').replace('–', '-')
            clean.append('' if v is None else v)
        w.writerow(clean)

    csv_bytes = buf.getvalue().encode('utf-8')
    stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    fname = f'kw_history_{client_id}_{stamp}.csv'
    return Response(
        csv_bytes,
        mimetype='text/csv; charset=utf-8',
        headers={'Content-Disposition': f'attachment; filename="{fname}"'},
    )


# ---------------------------------------------------------------------------
# "Export for AI" CSV — term + key context columns for ChatGPT prompts
# ---------------------------------------------------------------------------
@v2_kw_history_bp.route('/v2/api/kw-history/export-terms.csv', methods=['GET'])
def kw_history_export_terms_csv():
    """AI-friendly export: term + impressions / clicks / cost /
    conversions / already_in_ex / matched_ad_group_if_any. Original
    casing on term (term_raw). Same filter + sort semantics as the
    full export.

    Round 5 (16 May 2026): renamed in the UI to "Export for AI";
    URL slug + filename keep the legacy `_terms_` token so downstream
    tools that have already pinned to the path don't break.

    Filename: kw_history_terms_<status>_<YYYY-MM-DD>.csv. Status is
    the active Status pill (or 'all'); other filters don't influence
    the filename per spec.
    """
    args = request.args
    client_id = args.get('client', 'dbd001')
    if client_id not in ALLOWED_CLIENTS_V1:
        return Response('client_id not in v1 allowlist', status=403)

    sort_key = args.get('sort', 'clicks_total')
    sort_col = ALLOWED_SORT.get(sort_key, 'clicks_total')
    sort_dir = (args.get('dir', 'desc') or 'desc').lower()
    if sort_dir not in ALLOWED_DIR:
        sort_dir = 'desc'

    where_sql, params = _build_where_clause(args)

    con = _db()
    try:
        rows = con.execute(
            f"""SELECT
                    COALESCE(term_raw, term)    AS term_out,
                    impressions_total,
                    clicks_total,
                    cost_total,
                    conversions_total,
                    in_new_ex,
                    current_new_ex_ad_group
                FROM kw_st_history {where_sql}
                ORDER BY {sort_col} {sort_dir} NULLS LAST,
                         impressions_total DESC, term ASC""",
            params,
        ).fetchall()
    finally:
        con.close()

    # UTF-8 with BOM — same encoding pattern as the full export.
    # Snake_case headers because the output gets pasted straight into
    # ChatGPT prompts; consistent column tokens matter.
    buf = io.StringIO()
    buf.write('﻿')
    w = csv.writer(buf, quoting=csv.QUOTE_MINIMAL)
    w.writerow([
        'term', 'impressions', 'clicks', 'cost', 'conversions',
        'already_in_ex', 'matched_ad_group_if_any',
    ])
    for r in rows:
        term, impr, clk, cost, conv, in_ex, ag = r
        # Defensive em-dash strip on free-text values.
        if isinstance(term, str):
            term = term.replace('—', '-').replace('–', '-')
        if isinstance(ag, str):
            ag = ag.replace('—', '-').replace('–', '-')
        w.writerow([
            term if term is not None else '',
            int(impr or 0),
            int(clk or 0),
            f'{float(cost or 0):.2f}',
            f'{float(conv or 0):.2f}',
            # Literal lowercase true/false per spec — avoids Python's
            # default `True` / `False` casing that ChatGPT sometimes
            # mis-parses.
            'true' if bool(in_ex) else 'false',
            ag if ag is not None else '',
        ])
    csv_bytes = buf.getvalue().encode('utf-8')

    status_label = args.get('status', 'all') or 'all'
    if status_label not in ALLOWED_STATUS_FILTER:
        status_label = 'all'
    today = date.today().isoformat()
    fname = f'kw_history_terms_{status_label}_{today}.csv'
    return Response(
        csv_bytes,
        mimetype='text/csv; charset=utf-8',
        headers={'Content-Disposition': f'attachment; filename="{fname}"'},
    )


# ---------------------------------------------------------------------------
# Manual override — set proposed_ad_group + flip proposal_method='manual'
# ---------------------------------------------------------------------------
@v2_kw_history_bp.route('/v2/api/kw-history/override', methods=['POST'])
def kw_history_override():
    body = request.get_json(silent=True) or {}
    client_id = body.get('client_id', 'dbd001')
    term = body.get('term')
    type_ = body.get('type')
    ag = (body.get('proposed_ad_group') or '').strip()

    if client_id not in ALLOWED_CLIENTS_V1:
        return jsonify({'status': 'error',
                        'message': f'{client_id!r} not in v1 allowlist'}), 403
    if not term or not type_:
        return jsonify({'status': 'error',
                        'message': 'term + type required'}), 400
    if not ag:
        return jsonify({'status': 'error',
                        'message': 'proposed_ad_group required'}), 400
    # No em-dashes in stored values.
    ag = ag.replace('—', '-').replace('–', '-')

    con = duckdb.connect(DB_PATH)
    try:
        n = con.execute(
            """UPDATE kw_st_history
               SET proposed_ad_group = ?,
                   proposal_method = 'manual',
                   proposal_rationale = 'manual override (' || ? || ')',
                   last_updated = CURRENT_TIMESTAMP
               WHERE client_id = ? AND term = ? AND type = ?""",
            [ag, datetime.now().isoformat(timespec='seconds'),
             client_id, term, type_],
        ).fetchone()
        affected = int(n[0]) if n else 0
    finally:
        con.close()

    if affected == 0:
        return jsonify({'status': 'error',
                        'message': 'no matching row'}), 404
    return jsonify({'status': 'ok', 'affected': affected,
                    'proposed_ad_group': ag})
