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
        # Wave H: also consumed by Rule 8 signal filter (drop generic tokens
        # from adv/not-adv display so signals stay discriminative).
        'rule_7_exclude_tokens': rule7_exclude_tokens,
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


def _phrase_tokens_in_sequence(phrase_tokens: list[str], query_tokens: list[str]) -> bool:
    """True if `phrase_tokens` appears as a contiguous subsequence of
    `query_tokens`. Mirrors Google Ads phrase-match semantics (word-based,
    not char-substring). Prevents 'low' matching 'hounslow'."""
    n = len(phrase_tokens)
    if not n or n > len(query_tokens):
        return False
    for i in range(len(query_tokens) - n + 1):
        if query_tokens[i:i + n] == phrase_tokens:
            return True
    return False


def _longest_phrase_token_match(phrases, query_tokens: list[str]) -> str | None:
    """Return the phrase with most tokens whose token sequence appears
    contiguously in query_tokens. Tie-break alphabetically. Accepts set,
    list, or dict keys."""
    best = None
    best_count = 0
    for p in phrases:
        p_tokens = tokenize(p)
        if not p_tokens:
            continue
        if _phrase_tokens_in_sequence(p_tokens, query_tokens):
            n = len(p_tokens)
            if n > best_count or (n == best_count and best is not None and p < best):
                best = p
                best_count = n
    return best


def _most_tokens_then_alpha(phrases, text_token_set: set[str]) -> str | None:
    """Return the phrase whose token-set is a subset of `text_token_set`,
    with most tokens. Tie-break alphabetically. None if no match.
    Accepts set, list, or dict keys for `phrases`. Wave F: lets Rules 5/6
    fire on reordered-word variants (e.g. "replacement teeth cost" matches
    advertised "teeth replacement")."""
    best = None
    best_count = 0
    for p in phrases:
        p_tokens = set(tokenize(p))
        if not p_tokens or not p_tokens.issubset(text_token_set):
            continue
        n = len(p_tokens)
        if n > best_count:
            best = p
            best_count = n
        elif n == best_count and best is not None and p < best:
            best = p
    return best


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

    # Rule 3 — Word-based phrase match. Wave L: token-sequence (contiguous)
    # match instead of char-substring, mirroring Google Ads phrase-match
    # semantics. Example: phrase "low" no longer matches query "hounslow".
    # Detail = "phrase|role1,role2" so the UI can show both the matched
    # phrase and which list(s) it lives in.
    phrase_match = _longest_phrase_token_match(cfg['phrase_neg_phrases'].keys(), t_tokens)
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

    # Rule 5 — denylist (service we do but don't advertise). Wave F:
    # token-subset match so reordered variants still fire.
    denylist_match = _most_tokens_then_alpha(cfg['denylist_phrases'], t_token_set)
    if denylist_match is not None:
        status = 'block' if cfg['block_offered_not_advertised'] else 'review'
        return (status, 'service_not_advertised', denylist_match)

    # Rule 6 — advertised service match (must beat Rule 7). Wave F:
    # token-subset match so "replacement teeth cost" matches "teeth replacement".
    advertised_match = _most_tokens_then_alpha(cfg['advertised_phrases'], t_token_set)
    if advertised_match is not None:
        return ('keep', 'advertised_service_match', advertised_match)

    # Rule 7 — SOFT signal: token intersects the Rule-7-scoped single-word
    # negs (exclusion list applied). Detail = alphabetically-first match.
    # Wave C12: auto_block toggle flips 'block' -> 'review' when OFF.
    rule7_matches = sorted(t_token_set & cfg['exact_neg_single_words_for_rule_7'])
    if rule7_matches:
        status = 'block' if cfg['rule_7_auto_block'] else 'review'
        return (status, 'contains_neg_vocabulary', rule7_matches[0])

    # Rule 8 — ambiguous fallback with signal enrichment (Wave F).
    # Detail is ";"-delimited key=value pairs. Empty -> None.
    signals: list[str] = []

    # brand_near: multi-token brand phrase shares >= max(2, len-1) tokens.
    # Rules out noisy 2-token brands (those would already be caught by Rule 1
    # on exact match) and caps false-positive rate on longer brands.
    best_brand = None
    best_brand_overlap = 0
    for bp in cfg['brand_phrases']:
        bp_tokens = set(tokenize(bp))
        if len(bp_tokens) < 2:
            continue
        overlap = len(bp_tokens & t_token_set)
        threshold = max(2, len(bp_tokens) - 1)
        if overlap >= threshold and overlap > best_brand_overlap:
            best_brand = bp
            best_brand_overlap = overlap
    if best_brand:
        signals.append(f'brand_near={best_brand}')

    # Compute raw token overlaps with advertised and denylist phrases.
    adv_hits: set[str] = set()
    for ap in cfg['advertised_phrases']:
        adv_hits |= (set(tokenize(ap)) & t_token_set)
    notadv_hits: set[str] = set()
    for dp in cfg['denylist_phrases']:
        notadv_hits |= (set(tokenize(dp)) & t_token_set)

    # Wave H: drop non-discriminative tokens before surfacing signals.
    #  (1) Dual-side tokens: appear in BOTH adv and notadv -> don't help triage
    #  (2) rule_7_exclude_tokens: user has explicitly marked these as
    #      industry-generic (consistent with Rule 7's own suppression)
    dual_tokens = adv_hits & notadv_hits
    generic_tokens = cfg.get('rule_7_exclude_tokens', set())
    drop = dual_tokens | generic_tokens
    adv_hits -= drop
    notadv_hits -= drop

    if adv_hits:
        signals.append(f'adv_tokens={",".join(sorted(adv_hits))}')
    if notadv_hits:
        signals.append(f'notadv_tokens={",".join(sorted(notadv_hits))}')

    detail = ';'.join(signals) if signals else None
    return ('review', 'ambiguous', detail)


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
    finally:
        con.close()

    # N1k: always chain Pass 2. Pass 1 clears pass2_target_list_role to NULL
    # on every updated pending row, and if Pass 2 isn't run the UI dropdown
    # silently defaults to the first <option> ('1 WRD [ex]') for every row.
    # Scheduler and reclassify CLI already chain, but any direct caller of
    # run_pass1() would otherwise leave the DB in a broken UI state.
    # Late import avoids a potential circular at module-import time.
    from act_dashboard.engine.negatives.pass2 import run_pass2
    summary['pass2'] = run_pass2(client_id, db_path, analysis_date)
    return summary
