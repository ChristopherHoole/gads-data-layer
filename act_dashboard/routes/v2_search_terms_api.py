"""Tier 2.1e — search-terms API blueprint.

New blueprint at /v2/api/search-terms/ for endpoints that operate on the
full day's search-term dataset (cross-cutting Search + PMax). Currently
hosts the AI-driven Pass 3 endpoint and the themes-banner GET; future
discovery endpoints (cluster summaries, anomaly detection) will land
here too.

Distinct from /v2/api/negatives/ (which is per-row review/push mechanics)
because Pass 3 AI is a discovery operation over the whole dataset, not
a CRUD action on individual review rows.
"""
from __future__ import annotations

import logging
import os

import duckdb
from flask import Blueprint, jsonify, request

from act_dashboard.ai import claude_subprocess, locks
from act_dashboard.engine.pass3_ai import run_pass3_ai

logger = logging.getLogger(__name__)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))
_WAREHOUSE_PATH = os.path.join(PROJECT_ROOT, 'warehouse.duckdb')

v2_search_terms_api_bp = Blueprint(
    'v2_search_terms_api', __name__,
    url_prefix='/v2/api/search-terms',
)


def _err(code: str, message: str, http: int = 400):
    return jsonify({'error': code, 'message': message}), http


def _db():
    return duckdb.connect(_WAREHOUSE_PATH)


# ---------------------------------------------------------------------------
# POST /run-pass3-ai
#   body: {client_id, analysis_date}
# ---------------------------------------------------------------------------
@v2_search_terms_api_bp.route('/run-pass3-ai', methods=['POST'])
def run_pass3_ai_endpoint():
    data = request.get_json(silent=True) or {}
    client_id = (data.get('client_id') or '').strip()
    analysis_date = (data.get('analysis_date') or '').strip()
    if not client_id:
        return _err('missing_client_id', 'client_id required')
    if not analysis_date:
        return _err('missing_analysis_date',
                    'analysis_date required (YYYY-MM-DD)')

    con = _db()
    try:
        result = run_pass3_ai(con, client_id, analysis_date)
    except locks.LockContentionError:
        con.close()
        return _err(
            'lock_contention',
            f'another pass3-ai run is already in flight for {client_id}',
            http=409,
        )
    except claude_subprocess.ClaudeError as e:
        con.close()
        logger.exception('pass3-ai claude error')
        return _err(
            getattr(e, 'error_type', 'claude_error'),
            str(e)[:400], http=502,
        )
    except Exception as e:  # noqa: BLE001
        con.close()
        logger.exception('pass3-ai failed')
        return _err('pass3_ai_failed', str(e)[:400], http=500)
    con.close()
    return jsonify(result)


# ---------------------------------------------------------------------------
# GET /last-pass3-status?client_id=X
#   Section 7 (12 May 2026): drives the failure banner on the Phrase
#   Suggestions tab. Returns the latest neg_pass3 row from
#   act_v2_scheduler_runs for today + this client. If status='failed',
#   the UI surfaces a banner with Re-run / Dismiss actions.
# ---------------------------------------------------------------------------
@v2_search_terms_api_bp.route('/last-pass3-status', methods=['GET'])
def get_last_pass3_status():
    client_id = (request.args.get('client_id') or '').strip()
    if not client_id:
        return _err('missing_client_id', 'client_id required')
    con = _db()
    try:
        row = con.execute(
            """SELECT status, started_at, completed_at, error_message
               FROM act_v2_scheduler_runs
               WHERE client_id = ?
                 AND phase = 'neg_pass3'
                 AND run_date = CURRENT_DATE
               ORDER BY started_at DESC
               LIMIT 1""",
            [client_id],
        ).fetchone()
    finally:
        con.close()
    if not row:
        # No run yet today — banner stays hidden. Empty-state CTA in the
        # tab body is the right surface for this case.
        return jsonify({'client_id': client_id, 'status': None})
    status, started_at, completed_at, error_message = row
    return jsonify({
        'client_id':       client_id,
        'status':          status,
        'started_at':      started_at.isoformat() if started_at else None,
        'completed_at':    completed_at.isoformat() if completed_at else None,
        'error_message':   error_message,
    })


# ---------------------------------------------------------------------------
# GET /last-pass3-cost?client_id=X
#   Stage 11 (17 May 2026): drives the cost-report banner at the top of
#   the Pass 3 pane. Pulls the most recent successful neg_pass3 row +
#   parses details_json (tokens_in/out, cost_usd, wall_clock_ms, theme
#   count, suggestions_created) so the UI can render "Last run: 12s,
#   $0.18, 8 suggestions, 3 themes".
# ---------------------------------------------------------------------------
@v2_search_terms_api_bp.route('/last-pass3-cost', methods=['GET'])
def get_last_pass3_cost():
    import json as _json
    client_id = (request.args.get('client_id') or '').strip()
    if not client_id:
        return _err('missing_client_id', 'client_id required')
    con = _db()
    try:
        row = con.execute(
            """SELECT status, started_at, completed_at, details_json
               FROM act_v2_scheduler_runs
               WHERE client_id = ?
                 AND phase IN ('neg_pass3', 'pass3_ai_autotrigger')
                 AND status = 'success'
               ORDER BY started_at DESC
               LIMIT 1""",
            [client_id],
        ).fetchone()
    finally:
        con.close()
    if not row:
        return jsonify({'client_id': client_id, 'status': None})
    status, started_at, completed_at, details_raw = row
    details = {}
    if details_raw:
        try:
            details = _json.loads(details_raw) if isinstance(details_raw, str) else (details_raw or {})
        except (ValueError, TypeError):
            details = {}
    cost_usd = details.get('cost_usd')
    # GBP conversion mirrors the kw_history_mapping constant.
    cost_gbp = round(float(cost_usd) * 0.79, 4) if cost_usd is not None else None
    return jsonify({
        'client_id':            client_id,
        'status':               status,
        'started_at':           started_at.isoformat() if started_at else None,
        'completed_at':         completed_at.isoformat() if completed_at else None,
        'tokens_in':            details.get('tokens_in'),
        'tokens_out':           details.get('tokens_out'),
        'cost_usd':             cost_usd,
        'cost_gbp':             cost_gbp,
        'wall_clock_ms':        details.get('wall_clock_ms'),
        'suggestions_created':  details.get('suggestions_created'),
        'themes_count':         details.get('themes_count'),
    })


# ---------------------------------------------------------------------------
# GET /pass3-themes/<client_id>?date=YYYY-MM-DD
# ---------------------------------------------------------------------------
@v2_search_terms_api_bp.route('/pass3-themes/<client_id>', methods=['GET'])
def get_pass3_themes(client_id):
    analysis_date = (request.args.get('date') or '').strip()
    if not analysis_date:
        return _err('missing_date', 'date required (YYYY-MM-DD)')
    con = _db()
    try:
        rows = con.execute(
            """SELECT id, theme_text, created_at
               FROM act_v2_pass3_themes
               WHERE client_id = ? AND analysis_date = ?
               ORDER BY id ASC""",
            [client_id, analysis_date],
        ).fetchall()
    finally:
        con.close()
    return jsonify({
        'client_id': client_id,
        'analysis_date': analysis_date,
        'themes': [
            {
                'id': r[0],
                'theme_text': r[1],
                'created_at': r[2].isoformat() if r[2] else None,
            }
            for r in rows
        ],
    })
