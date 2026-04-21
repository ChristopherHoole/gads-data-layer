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
and services_not_advertised are empty, we can't classify meaningfully -> mark every
term today as review with reason='client_not_configured'.
"""
import json
import logging
from datetime import date
from typing import Iterable

import duckdb

from act_dashboard.engine.negatives._common import (
    normalize, tokenize, normalize_set, phrase_appears_in,
    split_comma_list, tokenize_set,
)
from act_dashboard.engine.negatives.reference_locations import (
    is_location_shaped, UK_POSTCODE_OUTCODE_RE,
)

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
        """SELECT services_not_advertised, services_advertised,
                  service_locations, client_brand_terms,
                  rule_7_exclude_tokens
           FROM act_v2_clients WHERE client_id = ?""",
        [client_id],
    ).fetchone()
    if not row:
        return None
    (services_not_adv_raw, services_adv_raw, locations_raw,
     brand_raw, rule7_exclude_raw) = row

    advertised_phrases = normalize_set(services_adv_raw)
    # Wave E1: keep the phrase-level normalized set for the line-173 precheck
    # (only its emptiness matters there), AND add a flat tokenised set for
    # Rule 4 so tokens like "hammersmith" match multi-word config entries
    # like "hammersmith and fulham".
    service_locations_set = normalize_set(locations_raw)
    service_locations_tokens = tokenize_set(locations_raw)
    brand_phrases = normalize_set(brand_raw)

    # Wave C13: Pass 1 reads the explicit denylist directly — no more
    # runtime subtraction of (all_services - advertised). Keeps the UI
    # field and engine input identical; singular/plural mismatches and
    # configuration gaps are now visible in one place.
    denylist_phrases = normalize_set(services_not_adv_raw)
    # Legacy name retained in the cfg dict for any downstream consumer.
    all_services_phrases = denylist_phrases

    # Wave D1: exact_neg_phrases is a dict mapping normalized keyword -> sorted
    # distinct list_roles that contain it. Dict `in` still works for Rule 2
    # equality check, and the Rule 2/3 returns now surface which list(s) caught
    # the match (pass1_reason_detail) so the UI can show context.
    exact_rows = con.execute(
        """SELECT DISTINCT kw.keyword_text, l.list_role
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
    exact_neg_phrases: dict[str, list[str]] = {}
    exact_neg_single_words: set[str] = set()
    for kw_text, list_role in exact_rows:
        n = normalize(kw_text)
        if not n:
            continue
        roles = exact_neg_phrases.setdefault(n, [])
        if list_role not in roles:
            roles.append(list_role)
        if ' ' not in n:
            exact_neg_single_words.add(n)
    for k in exact_neg_phrases:
        exact_neg_phrases[k].sort()

    # All keywords (any length) from LINKED phrase-match lists — Rule 3 substring map.
    phrase_rows = con.execute(
        """SELECT DISTINCT kw.keyword_text, l.list_role
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
    phrase_neg_phrases: dict[str, list[str]] = {}
    for kw_text, list_role in phrase_rows:
        n = normalize(kw_text)
        if not n:
            continue
        roles = phrase_neg_phrases.setdefault(n, [])
        if list_role not in roles:
            roles.append(list_role)
    for k in phrase_neg_phrases:
        phrase_neg_phrases[k].sort()

    # Wave C9/C12: behavioural toggles.
    def _toggle(key: str, default: bool = True) -> bool:
        row = con.execute(
            "SELECT setting_value FROM act_v2_client_settings "
            "WHERE client_id = ? AND setting_key = ?",
            [client_id, key],
        ).fetchone()
        if row is None:
            return default
        return (row[0] or '').lower() == 'true'
    block_offered_not_advertised = _toggle('block_offered_not_advertised', True)
    rule_7_auto_block = _toggle('rule_7_auto_block', True)

    # Wave C12: Rule 7 exclusion subset. Tokens in this set are excluded
    # ONLY from Rule 7 — Rule 2 still uses the full exact_neg_single_words.
    rule7_exclude_tokens = tokenize_set(split_comma_list(rule7_exclude_raw))
    exact_neg_single_words_for_rule_7 = exact_neg_single_words - rule7_exclude_tokens

    return {
        'brand_phrases': brand_phrases,
        'exact_neg_phrases': exact_neg_phrases,            # Rule 2 (equality)
        'phrase_neg_phrases': phrase_neg_phrases,          # Rule 3 (substring)
        'exact_neg_single_words': exact_neg_single_words,  # (full set, for Rule 2 context)
        'exact_neg_single_words_for_rule_7': exact_neg_single_words_for_rule_7,  # C12
        'advertised_phrases': advertised_phrases,
        'all_services_phrases': all_services_phrases,
        'denylist_phrases': denylist_phrases,
        'service_locations_set': service_locations_set,
        'service_locations_tokens': service_locations_tokens,
        'block_offered_not_advertised': block_offered_not_advertised,
        'rule_7_auto_block': rule_7_auto_block,
    }


def _is_client_configured(cfg: dict) -> bool:
    """At minimum we need locations, plus at least one of all/advertised."""
    if not cfg['service_locations_set']:
        return False
    if not cfg['advertised_phrases'] and not cfg['all_services_phrases']:
        return False
    return True


# ---------------------------------------------------------------------------
# Rule evaluation — first match wins (Wave C12: returns (status, reason, detail))
# ---------------------------------------------------------------------------
def _longest_then_alpha(phrases, text_normalized: str) -> str | None:
    """Return the longest phrase from `phrases` (set, list, or dict keys) that
    substrings `text_normalized`. Tie-break alphabetically. None if no match."""
    matches = [p for p in phrases if p and p in text_normalized]
    if not matches:
        return None
    matches.sort(key=lambda p: (-len(p), p))
    return matches[0]


def classify_term(search_term: str, cfg: dict) -> tuple[str, str, str | None]:
    """Return (pass1_status, pass1_reason, pass1_reason_detail). Rules 1–8
    in order, first match wins. Detail is the matched term/phrase where
    meaningful, else None."""
    t_norm = normalize(search_term)
    if not t_norm:
        return ('review', 'empty_term', None)
    t_tokens = t_norm.split()
    t_token_set = set(t_tokens)

    # Rule 1 — brand protection (always wins); detail = longest matching brand
    brand_match = _longest_then_alpha(cfg['brand_phrases'], t_norm)
    if brand_match is not None:
        return ('keep', 'brand_protection', brand_match)

    # Rule 2 — EQUALITY match against any exact-match neg. Detail =
    # comma-joined list_roles that contain this keyword (for UI context).
    if t_norm in cfg['exact_neg_phrases']:
        detail = ','.join(cfg['exact_neg_phrases'][t_norm])
        return ('block', 'existing_exact_neg_match', detail)

    # Rule 3 — SUBSTRING match against any phrase-match neg. Detail =
    # "phrase|role1,role2" so the UI can show both the matched phrase and
    # which list(s) it lives in.
    phrase_match = _longest_then_alpha(list(cfg['phrase_neg_phrases'].keys()), t_norm)
    if phrase_match is not None:
        list_roles = ','.join(cfg['phrase_neg_phrases'][phrase_match])
        detail = f"{phrase_match}|{list_roles}" if list_roles else phrase_match
        return ('block', 'existing_phrase_neg_match', detail)

    # Rule 4 — any location-shaped token NOT in service area.
    # Wave E1: match against the tokenised location set (so "hammersmith"
    # matches multi-word config entries like "hammersmith and fulham"), and
    # fall back to UK postcode district equivalence so short outcodes like
    # "sw1" match configured sub-units "sw1a/sw1p/sw1v" — but NOT "sw10"
    # (different district).
    loc_tokens = cfg['service_locations_tokens']

    def _postcode_district(p: str) -> str:
        """Normalise UK outcode to district form.
        'sw1'->'sw1', 'sw1a'->'sw1' (trailing letter stripped),
        'sw10'->'sw10' (trailing digit kept), 'e1w'->'e1'."""
        if UK_POSTCODE_OUTCODE_RE.match(p) and len(p) >= 3 and p[-1].isalpha():
            return p[:-1]
        return p

    def _in_service_area(tk: str) -> bool:
        if tk in loc_tokens:
            return True
        if UK_POSTCODE_OUTCODE_RE.match(tk):
            tk_district = _postcode_district(tk)
            for loc in loc_tokens:
                if UK_POSTCODE_OUTCODE_RE.match(loc) and _postcode_district(loc) == tk_district:
                    return True
        return False

    outside_locs = sorted({tk for tk in t_tokens
                           if is_location_shaped(tk) and not _in_service_area(tk)})
    if outside_locs:
        return ('block', 'location_outside_service_area', outside_locs[0])

    # Rule 5 — denylist (service we do but don't advertise)
    denylist_match = _longest_then_alpha(cfg['denylist_phrases'], t_norm)
    if denylist_match is not None:
        status = 'block' if cfg['block_offered_not_advertised'] else 'review'
        return (status, 'service_not_advertised', denylist_match)

    # Rule 6 — advertised service match (must beat Rule 7)
    advertised_match = _longest_then_alpha(cfg['advertised_phrases'], t_norm)
    if advertised_match is not None:
        return ('keep', 'advertised_service_match', advertised_match)

    # Rule 7 — SOFT signal: token intersects the Rule-7-scoped single-word
    # negs (exclusion list applied). Detail = alphabetically-first match.
    # Wave C12: auto_block toggle flips 'block' -> 'review' when OFF.
    rule7_matches = sorted(t_token_set & cfg['exact_neg_single_words_for_rule_7'])
    if rule7_matches:
        status = 'block' if cfg['rule_7_auto_block'] else 'review'
        return (status, 'contains_neg_vocabulary', rule7_matches[0])

    # Rule 8 — fallthrough
    return ('review', 'ambiguous', None)


# ---------------------------------------------------------------------------
# Term loader — pull today's distinct search terms for client
# ---------------------------------------------------------------------------
def _load_terms_for_today(con, client_id: str, analysis_date: date,
                          lookback_days: int | None = None) -> list[dict]:
    """Return the distinct search terms to classify for this client on this
    analysis run.

    Wave B: narrowed from a 7-day rolling union to "most recent snapshot_date
    for this client strictly before analysis_date". Matches the user's
    'review yesterday's terms' mental model. Rows for the same term across
    different contexts (campaign/ad_group/keyword) still aggregate.

    The `lookback_days` kwarg is retained for backwards compatibility with
    older callers but is ignored; supply None (default) for current behaviour.
    """
    # Find the latest snapshot_date for this client strictly before the
    # analysis_date (so Pass 1 running on the morning of day N classifies
    # day N-1 data, which is what the overnight ingestion landed).
    latest_row = con.execute(
        """SELECT MAX(snapshot_date) FROM act_v2_search_terms
           WHERE client_id = ? AND snapshot_date < ?""",
        [client_id, analysis_date],
    ).fetchone()
    latest = latest_row[0] if latest_row else None
    if latest is None:
        return []

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
             AND snapshot_date = ?
             AND search_term IS NOT NULL AND LENGTH(TRIM(search_term)) > 0
           GROUP BY search_term""",
        [client_id, latest],
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

    Wave C12 idempotent semantics:
      - Rows with review_status IN ('approved','pushed','rejected','expired')
        for the target analysis_date are LEFT UNTOUCHED.
      - Rows with review_status = 'pending' are UPDATEd with fresh
        pass1_status / pass1_reason / pass1_reason_detail; pass2_target_list_role
        is cleared so Pass 2 re-routes on its next run.
      - Terms not yet in the review table for this date are INSERTed.

    Returns a summary dict including per-rule counts (histogram) plus
    {'inserted': N, 'updated': M, 'preserved': K}.
    """
    if analysis_date is None:
        analysis_date = date.today()

    con = duckdb.connect(db_path)
    try:
        cfg = _load_client_config(con, client_id)
        if cfg is None:
            raise ValueError(f'client_id {client_id} not found')

        terms = _load_terms_for_today(con, client_id, analysis_date)

        # Map existing review rows for this date -> review_status + id, so we
        # know which terms to INSERT vs UPDATE vs PRESERVE.
        existing_rows = con.execute(
            """SELECT id, search_term, review_status
               FROM act_v2_search_term_reviews
               WHERE client_id = ? AND analysis_date = ?""",
            [client_id, analysis_date],
        ).fetchall()
        existing_by_term = {r[1]: {'id': r[0], 'review_status': r[2]}
                            for r in existing_rows}
        preserved_statuses = {'approved', 'pushed', 'rejected', 'expired'}

        configured = _is_client_configured(cfg)
        if not configured:
            logger.warning(f'[pass1] {client_id}: client_not_configured — marking all {len(terms)} terms as review')

        histogram: dict[str, int] = {}
        rows_to_insert: list = []
        rows_to_update: list = []   # tuples (status, reason, detail, id)
        preserved_count = 0
        status_counts = {'keep': 0, 'block': 0, 'review': 0}

        for t in terms:
            if configured:
                status, reason, detail = classify_term(t['search_term'], cfg)
            else:
                status, reason, detail = ('review', 'client_not_configured', None)
            histogram[reason] = histogram.get(reason, 0) + 1
            status_counts[status] = status_counts.get(status, 0) + 1

            existing = existing_by_term.get(t['search_term'])
            if existing and existing['review_status'] in preserved_statuses:
                preserved_count += 1
                continue
            if existing:
                rows_to_update.append((status, reason, detail, existing['id']))
            else:
                rows_to_insert.append((
                    client_id, t['search_term'], analysis_date,
                    t['first_seen'], t['last_seen'],
                    t['impr'], t['clicks'], t['cost'], t['conv'],
                    status, reason, detail,
                ))

        if rows_to_insert:
            con.executemany(
                """INSERT INTO act_v2_search_term_reviews
                   (client_id, search_term, analysis_date,
                    first_seen_date, last_seen_date,
                    total_impressions, total_clicks, total_cost, total_conversions,
                    pass1_status, pass1_reason, pass1_reason_detail)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                rows_to_insert,
            )
        if rows_to_update:
            con.executemany(
                """UPDATE act_v2_search_term_reviews
                   SET pass1_status = ?,
                       pass1_reason = ?,
                       pass1_reason_detail = ?,
                       pass2_target_list_role = NULL
                   WHERE id = ? AND review_status = 'pending'""",
                rows_to_update,
            )

        summary = {
            'client_id': client_id,
            'analysis_date': analysis_date.isoformat(),
            'terms_classified': len(terms),
            'inserted': len(rows_to_insert),
            'updated': len(rows_to_update),
            'preserved': preserved_count,
            'configured': configured,
            'status_counts': status_counts,
            'reason_histogram': histogram,
        }
        logger.info(
            f'[pass1] {client_id} ({analysis_date}): '
            f'{len(terms)} terms, ins={len(rows_to_insert)} '
            f'upd={len(rows_to_update)} preserved={preserved_count}; '
            f'blocks={status_counts["block"]} keeps={status_counts["keep"]} '
            f'reviews={status_counts["review"]}'
        )
        return summary
    finally:
        con.close()
