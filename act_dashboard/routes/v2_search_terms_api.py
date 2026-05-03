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
