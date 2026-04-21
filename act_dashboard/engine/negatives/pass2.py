"""Pass 2 — route blocked terms to a target list_role.

Rule:
    If pass1_reason == 'location_outside_service_area':
        target = 'location_exact'
    Else:
        wc = token count of search_term
        target = '5plus_word_exact' if wc >= 5 else f'{wc}_word_exact'

Competitor routing deferred to v2 (user overrides via UI dropdown for now).
"""
import logging
from datetime import date

import duckdb

from act_dashboard.engine.negatives._common import tokenize

logger = logging.getLogger('act_v2_neg_pass2')
if not logger.handlers:
    import sys
    h = logging.StreamHandler(sys.stdout)
    h.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
    logger.addHandler(h)
logger.setLevel(logging.INFO)


def _route(pass1_reason: str, search_term: str) -> str:
    # Wave C9: service_not_advertised gets its own dedicated list so user
    # can audit + reverse as a cohort if scope expands.
    if pass1_reason == 'service_not_advertised':
        return 'offered_not_advertised_exact'
    if pass1_reason == 'location_outside_service_area':
        return 'location_exact'
    wc = len(tokenize(search_term))
    if wc <= 0:
        wc = 1
    if wc >= 5:
        return '5plus_word_exact'
    return f'{wc}_word_exact'


def run_pass2(client_id: str, db_path: str,
              analysis_date: date | None = None) -> dict:
    """Update pass2_target_list_role for today's blocked rows."""
    if analysis_date is None:
        analysis_date = date.today()

    con = duckdb.connect(db_path)
    try:
        # Wave G2: also route 'review' rows so the UI dropdown shows a
        # sensible suggestion (previously defaulted to the first <option>
        # = '1_word_exact' regardless of term). Pass 2 stays a suggestion —
        # the user can still override via the dropdown before approving.
        rows = con.execute(
            """SELECT id, search_term, pass1_reason
               FROM act_v2_search_term_reviews
               WHERE client_id = ?
                 AND analysis_date = ?
                 AND pass1_status IN ('block','review')""",
            [client_id, analysis_date],
        ).fetchall()

        routed = 0
        role_histogram: dict[str, int] = {}
        # Update in a single transaction; each UPDATE touches a single
        # non-indexed column (pass2_target_list_role stays out of all indexes).
        for row_id, search_term, reason in rows:
            target = _route(reason, search_term)
            con.execute(
                """UPDATE act_v2_search_term_reviews
                   SET pass2_target_list_role = ?
                   WHERE id = ?""",
                [target, row_id],
            )
            role_histogram[target] = role_histogram.get(target, 0) + 1
            routed += 1

        summary = {
            'client_id': client_id,
            'analysis_date': analysis_date.isoformat(),
            'routed': routed,
            'role_histogram': role_histogram,
        }
        logger.info(f'[pass2] {client_id} ({analysis_date}): routed {routed} blocks -> {role_histogram}')
        return summary
    finally:
        con.close()
