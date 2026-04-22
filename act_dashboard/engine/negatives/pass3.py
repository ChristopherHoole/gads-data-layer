"""Pass 3 — phrase-fragment mining from today's pushed negatives.

Operates ONLY on rows where pass1/2 already pushed -> Google Ads
(review_status = 'pushed') for the given analysis_date. Extracts
1–4-word contiguous fragments; counts distinct source terms per fragment;
filters fragments that contain any "protected" word (stopwords, brand
tokens, advertised-service tokens, service-location tokens); applies
word-count thresholds; dedups against the client's entire existing linked
neg-keyword universe; then writes surviving fragments into
act_v2_phrase_suggestions as review_status='pending'.

Risk mapping:
  1-word  -> high    (broadest blast radius)
  2-word  -> medium
  3-word  -> low
  4-word  -> low

Target list_role is always '{word_count}_word_phrase' (Pass 3 produces
phrase-match negatives, not exact).
"""
import json
import logging
from collections import defaultdict
from datetime import date

import duckdb

from act_dashboard.engine.negatives._common import (
    normalize, tokenize, normalize_set, tokenize_set,
)
from act_dashboard.engine.negatives.reference_locations import is_location_shaped

logger = logging.getLogger('act_v2_neg_pass3')
if not logger.handlers:
    import sys
    h = logging.StreamHandler(sys.stdout)
    h.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
    logger.addHandler(h)
logger.setLevel(logging.INFO)


_WORD_THRESHOLDS_HARDCODED_4 = 2  # brief: 4-word threshold hardcoded at 2


def _load_client_settings(con, client_id: str) -> dict:
    """Load the 5 neg_pass3_* settings with defaults."""
    rows = con.execute(
        """SELECT setting_key, setting_value FROM act_v2_client_settings
           WHERE client_id = ? AND setting_key LIKE 'neg_pass3_%'""",
        [client_id],
    ).fetchall()
    s = dict(rows)
    return {
        'threshold_1': int(s.get('neg_pass3_threshold_1word') or 5),
        'threshold_2': int(s.get('neg_pass3_threshold_2word') or 3),
        'threshold_3': int(s.get('neg_pass3_threshold_3word') or 2),
        'stopwords': s.get('neg_pass3_stopwords') or '',
    }


def _load_protected_words(con, client_id: str, stopwords: str) -> tuple[set[str], set[str]]:
    """Return (protected, service_location_tokens).
      protected             = union of stopwords + brand + advertised + location
                              tokens. Filters fragments OUT of suggestion pool.
      service_location_tokens = just the tokenised service_locations set. Used
                              by the N1s location-override threshold rule so
                              outside-area 1-word locations can be suggested
                              on a single occurrence."""
    row = con.execute(
        """SELECT services_advertised, service_locations, client_brand_terms
           FROM act_v2_clients WHERE client_id = ?""",
        [client_id],
    ).fetchone()
    if not row:
        return set(), set()
    advertised_raw, locations_raw, brand_raw = row

    service_location_tokens: set[str] = tokenize_set(locations_raw)
    protected: set[str] = set()
    protected |= tokenize_set(stopwords)
    protected |= tokenize_set(brand_raw)
    protected |= tokenize_set(advertised_raw)
    # In-area locations stay in the protected set so "sidcup", "hammersmith"
    # etc. aren't suggested as phrase negs — only their out-of-area siblings
    # make it through the filter below.
    protected |= service_location_tokens
    return protected, service_location_tokens


def _load_denylist_tokens(con, client_id: str) -> set[str]:
    """Wave C13: read tokens directly from the explicit denylist column
    services_not_advertised. Used so Pass 3 can route fragments containing
    those tokens to the dedicated offered_not_advertised_phrase list."""
    row = con.execute(
        """SELECT services_not_advertised
           FROM act_v2_clients WHERE client_id = ?""",
        [client_id],
    ).fetchone()
    if not row:
        return set()
    return tokenize_set(row[0])


def _load_existing_negs_normalized(con, client_id: str) -> set[str]:
    """All normalized keyword_text across LINKED neg lists (any role, any
    match type). Used for dedup so we never re-suggest what's already there.

    N2 Part 1: scope to the latest snapshot_date so we don't dedup against
    keywords the user has since removed from Google Ads.
    """
    latest_row = con.execute(
        "SELECT MAX(snapshot_date) FROM act_v2_negative_list_keywords WHERE client_id = ?",
        [client_id],
    ).fetchone()
    latest = latest_row[0] if latest_row and latest_row[0] else None
    if latest is None:
        return set()
    rows = con.execute(
        """SELECT DISTINCT kw.keyword_text
           FROM act_v2_negative_list_keywords kw
           JOIN act_v2_negative_keyword_lists l ON kw.list_id = l.list_id
           WHERE kw.client_id = ?
             AND kw.snapshot_date = ?
             AND l.is_linked_to_campaign = TRUE""",
        [client_id, latest],
    ).fetchall()
    return {normalize(r[0]) for r in rows if r[0]}


def _load_pushed_terms(con, client_id: str, analysis_date: date) -> list[str]:
    rows = con.execute(
        """SELECT DISTINCT search_term
           FROM act_v2_search_term_reviews
           WHERE client_id = ?
             AND analysis_date = ?
             AND review_status = 'pushed'""",
        [client_id, analysis_date],
    ).fetchall()
    return [r[0] for r in rows if r[0]]


def _extract_fragments(tokens: list[str]) -> list[tuple[str, int]]:
    """Return list of (fragment_text, word_count) for all contiguous 1/2/3/4
    word fragments in `tokens`."""
    out: list[tuple[str, int]] = []
    n = len(tokens)
    for size in (1, 2, 3, 4):
        if n < size:
            break
        for i in range(n - size + 1):
            frag = ' '.join(tokens[i:i + size])
            out.append((frag, size))
    return out


def _risk_for(word_count: int) -> str:
    return {1: 'high', 2: 'medium', 3: 'low', 4: 'low'}.get(word_count, 'low')


def _threshold_for(settings: dict, wc: int, fragment: str,
                   service_location_tokens: set[str]) -> int:
    # N1s location override: a 1-word fragment that is location-shaped AND
    # NOT in the client's service area needs only a single occurrence to be
    # worth suggesting as a phrase-match neg. Outside-area locations are
    # binary — one hit is enough to warrant a standing block.
    if (wc == 1
            and is_location_shaped(fragment)
            and fragment not in service_location_tokens):
        return 1
    return {
        1: settings['threshold_1'],
        2: settings['threshold_2'],
        3: settings['threshold_3'],
        4: _WORD_THRESHOLDS_HARDCODED_4,
    }.get(wc, 999)


def run_pass3(client_id: str, db_path: str,
              analysis_date: date | None = None) -> dict:
    if analysis_date is None:
        analysis_date = date.today()

    con = duckdb.connect(db_path)
    try:
        settings = _load_client_settings(con, client_id)
        protected, service_location_tokens = _load_protected_words(
            con, client_id, settings['stopwords'])
        denylist_tokens = _load_denylist_tokens(con, client_id)
        existing = _load_existing_negs_normalized(con, client_id)
        pushed_terms = _load_pushed_terms(con, client_id, analysis_date)

        # fragment_key (normalized) -> {'word_count', 'source_terms': set[str]}
        bucket: dict[str, dict] = defaultdict(lambda: {'word_count': 0, 'source_terms': set()})
        for term in pushed_terms:
            toks = tokenize(term)
            if not toks:
                continue
            for frag, wc in _extract_fragments(toks):
                # Filter: any token in fragment protected -> skip
                if any(tk in protected for tk in frag.split()):
                    continue
                b = bucket[frag]
                b['word_count'] = wc
                b['source_terms'].add(term)

        # N1t: Idempotent re-run wipes ONLY pending suggestions. Preserve rows
        # the user has already decided on (approved/pushed/rejected). Pass 1
        # follows the same preservation strategy — a pushed phrase neg is a
        # real Google Ads change, losing local tracking creates sync drift.
        con.execute(
            """DELETE FROM act_v2_phrase_suggestions
               WHERE client_id = ? AND analysis_date = ?
                 AND review_status = 'pending'""",
            [client_id, analysis_date],
        )

        # N1t: include fragments already decided in today's act_v2_phrase_suggestions
        # in the dedup set — so a fragment the user already approved/pushed/
        # rejected today doesn't get re-surfaced as a fresh pending suggestion
        # (would also violate UNIQUE(client_id, analysis_date, fragment, role)).
        decided_today = con.execute(
            """SELECT DISTINCT fragment FROM act_v2_phrase_suggestions
               WHERE client_id = ? AND analysis_date = ?
                 AND review_status IN ('approved', 'pushed', 'rejected')""",
            [client_id, analysis_date],
        ).fetchall()
        existing = existing | {r[0] for r in decided_today if r[0]}

        created = 0
        risk_histogram: dict[str, int] = {}
        wc_histogram: dict[int, int] = {}
        skipped_below_threshold = 0
        skipped_dedup = 0

        for frag, info in bucket.items():
            wc = info['word_count']
            occurrence = len(info['source_terms'])
            if occurrence < _threshold_for(settings, wc, frag, service_location_tokens):
                skipped_below_threshold += 1
                continue
            if frag in existing:
                skipped_dedup += 1
                continue

            # Wave C9: fragments that contain a denylist token route to
            # the dedicated Off-Not-Adv phrase list regardless of word
            # count — cleaner audit trail vs scattering across N-word lists.
            frag_tokens = frag.split()
            if any(tk in denylist_tokens for tk in frag_tokens):
                target_role = 'offered_not_advertised_phrase'
            else:
                target_role = f'{wc}_word_phrase'
            risk = _risk_for(wc)
            sources = sorted(info['source_terms'])
            con.execute(
                """INSERT INTO act_v2_phrase_suggestions
                   (client_id, analysis_date, fragment, word_count,
                    target_list_role, source_search_terms,
                    occurrence_count, risk_level, review_status)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending')""",
                [client_id, analysis_date, frag, wc, target_role,
                 json.dumps(sources), occurrence, risk],
            )
            created += 1
            risk_histogram[risk] = risk_histogram.get(risk, 0) + 1
            wc_histogram[wc] = wc_histogram.get(wc, 0) + 1

        summary = {
            'client_id': client_id,
            'analysis_date': analysis_date.isoformat(),
            'pushed_terms_considered': len(pushed_terms),
            'fragments_evaluated': len(bucket),
            'suggestions_created': created,
            'skipped_below_threshold': skipped_below_threshold,
            'skipped_dedup': skipped_dedup,
            'risk_histogram': risk_histogram,
            'word_count_histogram': wc_histogram,
            'thresholds_used': {
                '1w': settings['threshold_1'],
                '2w': settings['threshold_2'],
                '3w': settings['threshold_3'],
                '4w': _WORD_THRESHOLDS_HARDCODED_4,
            },
        }
        logger.info(
            f"[pass3] {client_id} ({analysis_date}): {created} suggestions "
            f"from {len(pushed_terms)} pushed terms ({len(bucket)} fragments evaluated)"
        )
        return summary
    finally:
        con.close()
