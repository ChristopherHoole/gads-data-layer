"""N3 Part A — /v2/rejected-terms page route.

Renders the shell; all data is fetched client-side via
/v2/api/sticky-rejections endpoints. Mirrors the v2_search_term_review
pattern for client-switcher + topbar consistency.
"""
import os
from datetime import date

import duckdb
from flask import Blueprint, render_template, request

v2_rejected_terms_bp = Blueprint('v2_rejected_terms', __name__)

_WAREHOUSE_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'warehouse.duckdb')
)


def _db():
    return duckdb.connect(_WAREHOUSE_PATH, read_only=True)


@v2_rejected_terms_bp.route('/v2/rejected-terms')
def rejected_terms_page():
    client_filter = request.args.get('client', 'all')

    con = _db()
    try:
        clients = [
            {'id': r[0], 'name': r[1]}
            for r in con.execute(
                "SELECT client_id, client_name FROM act_v2_clients "
                "WHERE active=TRUE ORDER BY client_name"
            ).fetchall()
        ]
        if client_filter == 'all':
            current_client = clients[0] if clients else {'id': '', 'name': 'No Client'}
        else:
            row = con.execute(
                "SELECT client_id, client_name FROM act_v2_clients WHERE client_id = ?",
                [client_filter],
            ).fetchone()
            if not row:
                return f"Client '{client_filter}' not found", 404
            current_client = {'id': row[0], 'name': row[1]}
    finally:
        con.close()

    return render_template(
        'v2/rejected_terms.html',
        client=current_client,
        clients=clients,
        active_page='rejected-terms',
        today_date=date.today().strftime('%a %d %b %Y'),
    )
