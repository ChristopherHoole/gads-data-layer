"""N1b Gate 5 — /v2/search-term-review page route.

All data fetching happens client-side via the v2_negatives_api JSON endpoints.
This route's only job is to render the page shell: client switcher context,
date default, initial status counts, and Pass-3-available flag.
"""
import os
from datetime import date, datetime

import duckdb
from flask import Blueprint, render_template, request

v2_search_term_review_bp = Blueprint('v2_search_term_review', __name__)

_WAREHOUSE_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'warehouse.duckdb')
)


def _db():
    return duckdb.connect(_WAREHOUSE_PATH, read_only=True)


@v2_search_term_review_bp.route('/v2/search-term-review')
def search_term_review_page():
    client_filter = request.args.get('client', 'all')
    analysis_date_raw = request.args.get('date')
    try:
        analysis_date = (datetime.strptime(analysis_date_raw, '%Y-%m-%d').date()
                         if analysis_date_raw else date.today())
    except ValueError:
        analysis_date = date.today()

    con = _db()
    try:
        clients = [
            {'id': r[0], 'name': r[1]}
            for r in con.execute(
                "SELECT client_id, client_name FROM act_v2_clients WHERE active=TRUE ORDER BY client_name"
            ).fetchall()
        ]
        if client_filter == 'all':
            # Default to first client; this page is per-client (no multi-client table yet).
            current_client = clients[0] if clients else {'id': '', 'name': 'No Client'}
        else:
            row = con.execute(
                "SELECT client_id, client_name FROM act_v2_clients WHERE client_id = ?",
                [client_filter],
            ).fetchone()
            if not row:
                return f"Client '{client_filter}' not found", 404
            current_client = {'id': row[0], 'name': row[1]}

        # Summary counts for the 5 badges at top of page
        counts = {}
        for key, where in (
            ('pending_block_review',
             "pass1_status IN ('block','review') AND review_status='pending'"),
            ('approved', "review_status='approved'"),
            ('rejected', "review_status='rejected'"),
            ('pushed',   "review_status='pushed'"),
            ('expired',  "review_status='expired'"),
        ):
            counts[key] = con.execute(
                f"""SELECT COUNT(*) FROM act_v2_search_term_reviews
                    WHERE client_id = ? AND analysis_date = ? AND {where}""",
                [current_client['id'], analysis_date],
            ).fetchone()[0]

        # Pass 3 availability — tab enabled only if at least one push landed today
        pushed_today = counts['pushed'] > 0
        # ...and suggestions present (if run_pass3 was invoked)
        sugg_count = con.execute(
            """SELECT COUNT(*) FROM act_v2_phrase_suggestions
               WHERE client_id = ? AND analysis_date = ?""",
            [current_client['id'], analysis_date],
        ).fetchone()[0]

    finally:
        con.close()

    return render_template(
        'v2/search_term_review.html',
        client=current_client,
        clients=clients,
        counts=counts,
        analysis_date=analysis_date.isoformat(),
        pushed_today=pushed_today,
        phrase_suggestions_count=sugg_count,
        active_page='search-term-review',
        today_date=date.today().strftime('%a %d %b %Y'),
    )
