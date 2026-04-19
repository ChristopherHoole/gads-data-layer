"""
ACT v2 Shared API Routes

Endpoints used by ALL level pages (Account, Campaign, etc.)
- Approve/decline recommendations
"""

import os
import threading
from datetime import datetime

import duckdb
from flask import Blueprint, request, jsonify

v2_api_bp = Blueprint('v2_api', __name__, url_prefix='/v2/api')

_WAREHOUSE_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "warehouse.duckdb")
)

# Serialize writes within this Flask process to avoid DuckDB UPDATE races
# (DuckDB implements UPDATE as DELETE+INSERT; concurrent writers on the same
# row raise a PK-constraint or tuple-deletion conflict).
_write_lock = threading.Lock()


def _get_db():
    return duckdb.connect(_WAREHOUSE_PATH)


@v2_api_bp.route('/recommendations/<int:rec_id>/approve', methods=['POST'])
def approve_recommendation(rec_id):
    """Approve a recommendation (idempotent: no-op if already actioned)."""
    with _write_lock:
        con = _get_db()
        try:
            con.execute("""
                UPDATE act_v2_recommendations
                SET status = 'approved', actioned_at = CURRENT_TIMESTAMP, actioned_by = 'user'
                WHERE recommendation_id = ? AND status = 'pending'
            """, [rec_id])
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
        finally:
            con.close()


@v2_api_bp.route('/recommendations/<int:rec_id>/decline', methods=['POST'])
def decline_recommendation(rec_id):
    """Decline a recommendation (idempotent: no-op if already actioned)."""
    with _write_lock:
        con = _get_db()
        try:
            con.execute("""
                UPDATE act_v2_recommendations
                SET status = 'declined', actioned_at = CURRENT_TIMESTAMP, actioned_by = 'user'
                WHERE recommendation_id = ? AND status = 'pending'
            """, [rec_id])
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
        finally:
            con.close()


@v2_api_bp.route('/recommendations/bulk-approve', methods=['POST'])
def bulk_approve_recommendations():
    """Approve multiple recommendations in one call.

    Payload: {"ids": [1, 2, 3]}
    Returns: {"success": true, "results": [{"id": 1, "success": true}, ...]}
    """
    data = request.get_json() or {}
    ids = data.get('ids', [])
    if not isinstance(ids, list) or not ids:
        return jsonify({'success': False, 'error': 'ids must be a non-empty list'}), 400

    results = []
    with _write_lock:
        con = _get_db()
        try:
            for rec_id in ids:
                try:
                    con.execute("""
                        UPDATE act_v2_recommendations
                        SET status = 'approved', actioned_at = CURRENT_TIMESTAMP, actioned_by = 'user'
                        WHERE recommendation_id = ? AND status = 'pending'
                    """, [rec_id])
                    results.append({'id': rec_id, 'success': True})
                except Exception as e:
                    results.append({'id': rec_id, 'success': False, 'error': str(e)[:200]})
            return jsonify({'success': True, 'results': results})
        finally:
            con.close()


@v2_api_bp.route('/actions/<int:action_id>/undo-request', methods=['POST'])
def undo_request_action(action_id):
    """Mark an executed action as undo-requested (DB flag only, no API revert).

    The actual Google Ads API revert will be implemented in the G-series
    (execution/rollback layer). For now, this endpoint only sets the
    undo_requested_at timestamp so the UI can show an "Undo requested" state.
    """
    con = _get_db()
    try:
        con.execute("""
            UPDATE act_v2_executed_actions
            SET undo_requested_at = CURRENT_TIMESTAMP
            WHERE action_id = ?
        """, [action_id])
        return jsonify({
            'success': True,
            'note': 'Undo marked in DB. Google Ads API revert will land with G-series.'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        con.close()
