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
from datetime import date, datetime

import duckdb
from flask import Blueprint, jsonify, request

from act_dashboard.engine.negatives.pass3 import run_pass3
from act_dashboard.data_pipeline.google_ads_mutate import (
    push_negatives_to_shared_lists,
)

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
_ST_VIEW_FILTERS = {
    'pending':  "pass1_status IN ('block','review') AND review_status='pending'",
    'approved': "review_status='approved'",
    'pushed':   "review_status='pushed'",
    'rejected': "review_status='rejected'",
    'keep':     "pass1_status='keep'",
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

    offset = (page - 1) * page_size
    where = f"client_id = ? AND analysis_date = ? AND {_ST_VIEW_FILTERS[view]}"

    con = _db()
    try:
        total = con.execute(
            f"SELECT COUNT(*) FROM act_v2_search_term_reviews WHERE {where}",
            [client_id, analysis_date],
        ).fetchone()[0]
        rows = con.execute(
            f"""SELECT id, search_term, analysis_date,
                       first_seen_date, last_seen_date,
                       total_impressions, total_clicks, total_cost, total_conversions,
                       pass1_status, pass1_reason, pass2_target_list_role,
                       review_status, reviewed_at, reviewed_by,
                       pushed_to_ads_at, pushed_google_ads_criterion_id, push_error
                FROM act_v2_search_term_reviews
                WHERE {where}
                ORDER BY total_cost DESC NULLS LAST, id
                LIMIT ? OFFSET ?""",
            [client_id, analysis_date, page_size, offset],
        ).fetchall()
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
            'pass2_target_list_role': r[11],
            'review_status': r[12],
            'reviewed_at': r[13].isoformat() if r[13] else None,
            'reviewed_by': r[14],
            'pushed_to_ads_at': r[15].isoformat() if r[15] else None,
            'pushed_google_ads_criterion_id': r[16],
            'push_error': r[17],
        })
    return jsonify({
        'items': items, 'total': int(total),
        'page': page, 'page_size': page_size,
        'view': view, 'analysis_date': analysis_date.isoformat(),
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
            if override is None:
                con.execute(
                    """UPDATE act_v2_phrase_suggestions
                       SET review_status = ?, reviewed_at = CURRENT_TIMESTAMP,
                           reviewed_by = 'user'
                       WHERE id = ? AND client_id = ?""",
                    [new_status, row_id, client_id],
                )
            else:
                con.execute(
                    """UPDATE act_v2_phrase_suggestions
                       SET review_status = ?, reviewed_at = CURRENT_TIMESTAMP,
                           reviewed_by = 'user',
                           target_list_role = ?
                       WHERE id = ? AND client_id = ?""",
                    [new_status, override, row_id, client_id],
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
