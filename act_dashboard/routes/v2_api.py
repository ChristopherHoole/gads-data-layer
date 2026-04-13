"""
ACT v2 Shared API Routes

Endpoints used by ALL level pages (Account, Campaign, etc.)
- Approve/decline recommendations
"""

import os
from datetime import datetime

import duckdb
from flask import Blueprint, request, jsonify

v2_api_bp = Blueprint('v2_api', __name__, url_prefix='/v2/api')

_WAREHOUSE_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "warehouse.duckdb")
)


def _get_db():
    return duckdb.connect(_WAREHOUSE_PATH)


@v2_api_bp.route('/recommendations/<int:rec_id>/approve', methods=['POST'])
def approve_recommendation(rec_id):
    """Approve a recommendation."""
    con = _get_db()
    try:
        con.execute("""
            UPDATE act_v2_recommendations
            SET status = 'approved', actioned_at = CURRENT_TIMESTAMP, actioned_by = 'user'
            WHERE recommendation_id = ?
        """, [rec_id])
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        con.close()


@v2_api_bp.route('/recommendations/<int:rec_id>/decline', methods=['POST'])
def decline_recommendation(rec_id):
    """Decline a recommendation."""
    con = _get_db()
    try:
        con.execute("""
            UPDATE act_v2_recommendations
            SET status = 'declined', actioned_at = CURRENT_TIMESTAMP, actioned_by = 'user'
            WHERE recommendation_id = ?
        """, [rec_id])
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        con.close()
