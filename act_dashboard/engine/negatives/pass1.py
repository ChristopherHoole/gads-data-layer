"""Pass 1 — rules-based classifier for today's search terms.

Loads config once per client, walks today's distinct search terms (from
act_v2_search_terms), applies the 7-rule tree, writes rows into
act_v2_search_term_reviews with analysis_date=today.

Rule order (first match wins):
    1. brand_protection           -> keep
    2. existing_exact_neg_match   -> block   (EQUALITY vs any exact-match neg)
    3. existing_phrase_neg_match  -> block   (SUBSTRING vs any phrase-match neg)
    4. location_outside_service_area -> block
    5. service_not_advertised     -> block
    6. advertised_service_match   -> keep
    7. contains_neg_vocabulary    -> block   (SOFT: any token in single-word
                                              exact neg vocabulary)
    8. (fallthrough)              -> review  (reason='ambiguous')

Rules 2+3 are the "leak detector" — terms that Google Ads already blocks.
They should rarely fire; most serving still lets queries through.

Rule 7 is a soft semantic signal, weaker than "already blocked": the client's
single-word exact-match neg list is treated as a vocabulary of known-bad
tokens, but only applied AFTER rule 6 gives advertised services a chance.
So "dental implants" keeps on rule 6 (advertised), never hits rule 7, even
if "dental" and "implants" both live in the 1-word exact neg list.

Client precheck: if service_locations is empty AND both services_advertised
and services_all are empty, we can't classify meaningfully -> mark every
term today as review with reason='client_not_configured'.
"""
import json
import logging
from datetime import date
from typing import Iterable

import duckdb

from act_dashboard.engine.negatives._common import (
    normalize, tokenize, normalize_set, phrase_appears_in,
)
from act_dashboard.engine.negatives.reference_locations import is_location_shaped

logger = logging.getLogger('act_v2_neg_pass1')
if not logger.handlers:
    import sys
    h = logging.StreamHandler(sys.stdout)
    h.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
    logger.addHandler(h)
logger.setLevel(logging.INFO)


# ---------------------------------------------------------------------------
# Config loader — pulls all Pass-1 inputs in one DB pass per client
# ---------------------------------------------------------------------------
def _load_client_config(con, client_id: str) -> dict:
    """Return all normalized inputs Pass 1 needs. Never raises on missing data;
    empty fields become empty sets."""
    row = con.execute(
        """SELECT services_all, services_advertised,
                  service_locations, client_brand_terms
           FROM act_v2_clients WHERE client_id = ?""",
        [client_id],
    ).fetchone()
    if not row:
        return None
    services_all_raw, services_adv_raw, locations_raw, brand_raw = row

    all_services_phrases = normalize_set(services_all_raw)
    advertised_phrases = normalize_set(services_adv_raw)
    service_locations_set = normalize_set(locations_raw)
    brand_phrases = normalize_set(brand_raw)

    # "Denylist" = services the client DOES but is NOT advertising = shouldn't match ads.
    denylist_phrases = all_services_phrases - advertised_phrases

    # All keyword_texts from LINKED exact-match lists (any word count).
    # Rule 2 checks equality against this whole set; Rule 7 uses only the
    # single-token subset.
    exact_rows = con.execute(
        """SELECT DISTINCT kw.keyword_text
           FROM act_v2_negative_list_keywords kw
           JOIN act_v2_negative_keyword_lists l ON kw.list_id = l.list_id
           WHERE kw.client_id = ?
             AND l.is_linked_to_campaign = TRUE
             AND l.list_role IN (
               '1_word_exact','2_word_exact','3_word_exact','4_word_exact',
               '5plus_word_exact','location_exact','competitor_exact'
             )
             AND kw.match_type = 'EXACT'""",
        [client_id],
    ).fetchall()
    exact_neg_phrases: set[str] = set()
    exact_neg_single_words: set[str] = set()
    for (kw_text,) in exact_rows:
        n = normalize(kw_text)
        if not n:
            continue
        exact_neg_phrases.add(n)
        if ' ' not in n:
            exact_neg_single_words.add(n)

    # All keywords (any length) from LINKED phrase-match lists — Rule 3 substring set.
    phrase_rows = con.execute(
        """SELECT DISTINCT kw.keyword_text
           FROM act_v2_negative_list_keywords kw
           JOIN act_v2_negative_keyword_lists l ON kw.list_id = l.list_id
           WHERE kw.client_id = ?
             AND l.is_linked_to_campaign = TRUE
             AND l.list_role IN (
               '1_word_phrase','2_word_phrase','3_word_phrase','4_word_phrase',
               'location_phrase','competitor_phrase'
             )""",
        [client_id],
    ).fetchall()
    phrase_neg_phrases: set[str] = set()
    for (kw_text,) in phrase_rows:
        n = normalize(kw_text)
        if n:
            phrase_neg_phrases.add(n)

    return {
        'brand_phrases': brand_phrases,
        'exact_neg_phrases': exact_neg_phrases,            # Rule 2 (equality)
        'phrase_neg_phrases': phrase_neg_phrases,          # Rule 3 (substring)
        'exact_neg_single_words': exact_neg_single_words,  # Rule 7 (soft token signal)
        'advertised_phrases': advertised_phrases,
        'all_services_phrases': all_services_phrases,
        'denylist_phrases': denylist_phrases,
        'service_locations_set': service_locations_set,
    }


def _is_client_configured(cfg: dict) -> bool:
    """At minimum we need locations, plus at least one of all/advertised."""
    if not cfg['service_locations_set']:
        return False
    if not cfg['advertised_phrases'] and not cfg['all_services_phrases']:
        return False
    return True


# ---------------------------------------------------------------------------
# Rule evaluation — first match wins
# ---------------------------------------------------------------------------
def classify_term(search_term: str, cfg: dict) -> tuple[str, str]:
    """Return (pass1_status, pass1_reason). Rules 1–8 in order, first match wins."""
    t_norm = normalize(search_term)
    if not t_norm:
        return ('review', 'empty_term')
    t_tokens = t_norm.split()
    t_token_set = set(t_tokens)

    # Rule 1 — brand protection (always wins)
    if phrase_appears_in(cfg['brand_phrases'], t_norm):
        return ('keep', 'brand_protection')

    # Rule 2 — EQUALITY match against any exact-match neg (Google Ads semantics)
    if t_norm in cfg['exact_neg_phrases']:
        return ('block', 'existing_exact_neg_match')

    # Rule 3 — SUBSTRING match against any phrase-match neg (Google Ads semantics)
    if phrase_appears_in(cfg['phrase_neg_phrases'], t_norm):
        return ('block', 'existing_phrase_neg_match')

    # Rule 4 — any location-shaped token NOT in service area
    locs = cfg['service_locations_set']
    for tk in t_tokens:
        if is_location_shaped(tk) and tk not in locs:
            return ('block', 'location_outside_service_area')

    # Rule 5 — denylist (service we do but don't advertise)
    if phrase_appears_in(cfg['denylist_phrases'], t_norm):
        return ('block', 'service_not_advertised')

    # Rule 6 — advertised service match (must beat Rule 7 so advertised
    # services with incidental neg-vocabulary tokens stay as keep)
    if phrase_appears_in(cfg['advertised_phrases'], t_norm):
        return ('keep', 'advertised_service_match')

    # Rule 7 — SOFT signal: any token is in the client's single-word
    # exact-neg vocabulary. Rules 2/3 handle true already-blocked terms;
    # this catches semantically-similar queries the user's own neg list
    # says are unwanted.
    if t_token_set & cfg['exact_neg_single_words']:
        return ('block', 'contains_neg_vocabulary')

    # Rule 8 — fallthrough
    return ('review', 'ambiguous')


# ---------------------------------------------------------------------------
# Term loader — pull today's distinct search terms for client
# ---------------------------------------------------------------------------
def _load_terms_for_today(con, client_id: str, analysis_date: date,
                          lookback_days: int = 7) -> list[dict]:
    """Return the distinct search terms to classify for this client on this
    analysis run. Uses last `lookback_days` days from act_v2_search_terms,
    aggregated; first_seen / last_seen derived from that window.

    A 7-day lookback lets us catch low-volume terms (which might not appear on
    any single day but matter cumulatively) without letting ancient history
    drown out the signal.
    """
    from datetime import timedelta
    start = analysis_date - timedelta(days=lookback_days - 1)
    rows = con.execute(
        """SELECT search_term,
                  MIN(snapshot_date) AS first_seen,
                  MAX(snapshot_date) AS last_seen,
                  SUM(COALESCE(impressions, 0))   AS impr,
                  SUM(COALESCE(clicks, 0))        AS clicks,
                  SUM(COALESCE(cost, 0))          AS cost,
                  SUM(COALESCE(conversions, 0))   AS conv
           FROM act_v2_search_terms
           WHERE client_id = ?
             AND snapshot_date BETWEEN ? AND ?
             AND search_term IS NOT NULL AND LENGTH(TRIM(search_term)) > 0
           GROUP BY search_term""",
        [client_id, start, analysis_date],
    ).fetchall()
    return [
        {
            'search_term': r[0],
            'first_seen': r[1],
            'last_seen': r[2],
            'impr': int(r[3] or 0),
            'clicks': int(r[4] or 0),
            'cost': float(r[5] or 0),
            'conv': float(r[6] or 0),
        }
        for r in rows
    ]


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------
def run_pass1(client_id: str, db_path: str,
              analysis_date: date | None = None) -> dict:
    """Execute Pass 1 for one client. Writes into act_v2_search_term_reviews.

    Idempotent for the same analysis_date: callers are expected to run the
    stale-cleanup phase first (which expires prior-date 'pending' rows), and
    this function deletes+re-inserts today's rows before writing fresh.

    Returns a summary dict including per-rule counts (histogram).
    """
    if analysis_date is None:
        analysis_date = date.today()

    con = duckdb.connect(db_path)
    try:
        cfg = _load_client_config(con, client_id)
        if cfg is None:
            raise ValueError(f'client_id {client_id} not found')

        terms = _load_terms_for_today(con, client_id, analysis_date)

        # Idempotent re-run: wipe today's existing rows for this client first
        con.execute(
            """DELETE FROM act_v2_search_term_reviews
               WHERE client_id = ? AND analysis_date = ?""",
            [client_id, analysis_date],
        )

        configured = _is_client_configured(cfg)
        if not configured:
            logger.warning(f'[pass1] {client_id}: client_not_configured — marking all {len(terms)} terms as review')

        # Histogram of reason codes
        histogram: dict[str, int] = {}
        rows_to_insert = []
        for t in terms:
            if configured:
                status, reason = classify_term(t['search_term'], cfg)
            else:
                status, reason = ('review', 'client_not_configured')
            histogram[reason] = histogram.get(reason, 0) + 1
            rows_to_insert.append((
                client_id, t['search_term'], analysis_date,
                t['first_seen'], t['last_seen'],
                t['impr'], t['clicks'], t['cost'], t['conv'],
                status, reason,
            ))

        # Batch insert
        if rows_to_insert:
            con.executemany(
                """INSERT INTO act_v2_search_term_reviews
                   (client_id, search_term, analysis_date,
                    first_seen_date, last_seen_date,
                    total_impressions, total_clicks, total_cost, total_conversions,
                    pass1_status, pass1_reason)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                rows_to_insert,
            )

        # Status tallies (keep/block/review)
        status_counts = {'keep': 0, 'block': 0, 'review': 0}
        for r in rows_to_insert:
            s = r[9]
            status_counts[s] = status_counts.get(s, 0) + 1

        summary = {
            'client_id': client_id,
            'analysis_date': analysis_date.isoformat(),
            'terms_classified': len(rows_to_insert),
            'configured': configured,
            'status_counts': status_counts,
            'reason_histogram': histogram,
        }
        logger.info(
            f'[pass1] {client_id} ({analysis_date}): '
            f'{len(rows_to_insert)} terms, '
            f'blocks={status_counts["block"]} keeps={status_counts["keep"]} '
            f'reviews={status_counts["review"]}'
        )
        return summary
    finally:
        con.close()
