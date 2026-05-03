"""Tier 2.1e — AI-driven Pass 3 (discovery + routing + theme summary).

Replaces the per-day rule-based fragment generator (act_dashboard/engine/
negatives/pass3.py — left intact as fallback) with a single Claude call
per client per day that:

  1. Reads the FULL day's search-term dataset (Search + PMax) regardless
     of Pass 1+2 outcomes. Pass 1+2 do NOT have to have run first.
  2. Discovers candidate phrase fragments worth blocking.
  3. Routes each to the correct target negative list (validated against
     the client's real linked-list schema before INSERT).
  4. Summarises the day's pattern in 1-4 themes.

Storage:
  - Fragments  -> act_v2_phrase_suggestions (existing table, +4 cols
                  added in migration n8: confidence, rationale, theme_id,
                  source_count). Pending-only wipe before fresh insert
                  (mirrors pass3.py preservation logic).
  - Themes     -> act_v2_pass3_themes (created in n8). One row per theme.

Concurrency / safety:
  - Per-client lock (acquired non-blocking — concurrent calls return 409).
  - 30-second in-memory idempotency cache short-circuits identical
    repeat calls before lock acquisition.
  - Retry-once on ClaudeError / _ParseError.
  - target_list_role values from the AI are validated against the
    client's real linked-list role set; invalid values are dropped (with
    a count surfaced in the response) — no invented list names hit
    the DB.
  - Pending-only DELETE preserves user-decided rows (approved/pushed/
    rejected) — same preservation rule as the existing pass3.py.
  - DuckDB 1.1.0 autocommit pattern (no transaction wrapper around
    DELETE+INSERT — false-positive PK errors otherwise).
"""
from __future__ import annotations

import json
import logging
import os
from datetime import date, datetime, timedelta

from act_dashboard.ai import (
    claude_subprocess,
    idempotency,
    locks,
    prompt_loader,
)
from act_dashboard.ai.classifier import _ParseError, _log_error
from act_dashboard.ai.prompts import (
    PROMPT_FILE_PASS3_AI,
    PROMPT_VERSION_PASS3_AI,
)

logger = logging.getLogger(__name__)

# Pass 3 reuses the same Opus slug as Stages 4-5-9 (per brief Q6) for
# nuanced understanding of off-not-advertised + location intent. Cost
# ceiling ~$0.15/client/day at current Anthropic pricing.
MODEL_PASS3_AI = 'claude-opus-4-7'

# Pass 3 packs the full day's search-term dataset + client config + history
# into a single call (~25-30K input tokens). Output is the throttle, not
# input — 20-50 fragments with rationales + source_terms is 5-10K output
# tokens at Opus's ~30 tok/s = 170-330s of generation. 600s gives ~2x
# headroom over the worst observed case on DBD-sized days (~700 terms).
TIMEOUT_PASS3_S = 600

# Env var feature flag (per brief): 'ai' (default new) or 'rules' (fallback
# routes through the legacy engine — caller is expected to pick the right
# function based on this var, not pass3_ai.py).
ENGINE_ENV = 'ACT_PASS3_ENGINE'
DEFAULT_ENGINE = 'ai'


def get_active_engine() -> str:
    """Returns 'ai' (default) or 'rules' (legacy fallback)."""
    val = (os.environ.get(ENGINE_ENV) or DEFAULT_ENGINE).strip().lower()
    return val if val in ('ai', 'rules') else DEFAULT_ENGINE


# ============================================================================
# Public entry point
# ============================================================================
def run_pass3_ai(con, client_id: str, analysis_date: str) -> dict:
    """Run AI-driven Pass 3 for one client/day. Returns endpoint response shape.

    May raise locks.LockContentionError (caller maps to 409).
    May raise claude_subprocess.ClaudeError after retry (caller maps to 502).
    """
    flow = 'pass3_ai'

    # ---- Idempotency check (BEFORE lock) ----
    cache_key = idempotency.make_key(
        client_id, flow, [analysis_date],  # analysis_date doubles as the "id"
        PROMPT_VERSION_PASS3_AI, False,
    )
    cached = idempotency.get(cache_key)
    if cached is not None:
        logger.info(
            'run_pass3_ai idempotency hit: client=%s date=%s',
            client_id, analysis_date,
        )
        return cached

    # ---- Per-client lock (non-blocking) ----
    client_lock = locks.get_client_lock(client_id)
    if not client_lock.acquire(blocking=False):
        raise locks.LockContentionError(client_id)

    try:
        # ---- Load context ----
        client_ctx = _load_client_context(con, client_id)
        target_lists = _load_target_lists(con, client_id)
        if not target_lists:
            # Without real list names we can't validate the AI's output,
            # so refuse to spend tokens.
            return _empty_result(error='no_linked_neg_lists')

        valid_roles = {tl['list_role'] for tl in target_lists}

        terms = _load_day_search_terms(con, client_id, analysis_date)
        if not terms:
            result = _empty_result(skipped='no_terms_for_date')
            idempotency.set(cache_key, result)
            return result

        suppression = _load_suppression(con, client_id, analysis_date)

        # ---- Render prompts ----
        system_prompt = prompt_loader.load_prompt(PROMPT_FILE_PASS3_AI)
        user_message = _build_user_message(
            client_id, analysis_date,
            client_ctx, target_lists, terms, suppression,
        )

        # ---- Call Claude (retry once) ----
        result_text = ''
        usage: dict = {}
        wall_ms = 0
        parsed: dict | None = None
        for attempt in (1, 2):
            try:
                result_text, usage, wall_ms = claude_subprocess.run_claude(
                    MODEL_PASS3_AI, system_prompt, user_message,
                    timeout_s=TIMEOUT_PASS3_S,
                )
                parsed = _parse_response(result_text, valid_roles)
                break
            except (claude_subprocess.ClaudeError, _ParseError) as e:
                error_type = getattr(e, 'error_type', 'invalid_json')
                logger.warning(
                    'run_pass3_ai attempt %d failed: client=%s date=%s '
                    'error_type=%s msg=%s',
                    attempt, client_id, analysis_date,
                    error_type, str(e)[:300],
                )
                if attempt == 2:
                    _log_error(
                        con, client_id, analysis_date, flow,
                        [], error_type, str(e),
                        getattr(e, 'raw_output', ''),
                    )
                    if isinstance(e, claude_subprocess.ClaudeError):
                        raise
                    raise claude_subprocess.ClaudeError(
                        'invalid_json', str(e),
                        getattr(e, 'raw_output', ''),
                    ) from e

        assert parsed is not None  # for type checker; loop above raises otherwise

        # ---- Validate + filter fragments (drop invalid target_list_role) ----
        ai_themes: list[str] = parsed.get('themes', []) or []
        raw_fragments: list[dict] = parsed.get('fragments', []) or []
        fragments, fragments_dropped = _filter_valid_fragments(
            raw_fragments, valid_roles,
        )

        # ---- Persist (DELETE pending then INSERT; autocommit pattern) ----
        # FK precursor: act_v2_ai_classifications carries Stage 11 router
        # rows keyed on phrase_suggestion_id. Wipe those for the pending
        # rows we're about to delete — otherwise the FK constraint blocks
        # the DELETE below. Production-safe: those classifications were
        # tied to suggestions we're now replacing, so they're stale anyway.
        con.execute(
            """DELETE FROM act_v2_ai_classifications
               WHERE phrase_suggestion_id IN (
                   SELECT id FROM act_v2_phrase_suggestions
                   WHERE client_id = ? AND analysis_date = ?
                     AND review_status = 'pending'
               )""",
            [client_id, analysis_date],
        )
        con.execute(
            """DELETE FROM act_v2_phrase_suggestions
               WHERE client_id = ? AND analysis_date = ?
                 AND review_status = 'pending'""",
            [client_id, analysis_date],
        )
        # Themes: wipe + replace (same single-source-of-truth-per-day rule).
        con.execute(
            "DELETE FROM act_v2_pass3_themes "
            "WHERE client_id = ? AND analysis_date = ?",
            [client_id, analysis_date],
        )

        for theme_text in ai_themes:
            con.execute(
                "INSERT INTO act_v2_pass3_themes "
                "(client_id, analysis_date, theme_text) VALUES (?, ?, ?)",
                [client_id, analysis_date, theme_text],
            )

        suggestions_created = 0
        skipped_dedup = 0
        existing_negs = _load_existing_negs(con, client_id)
        for f in fragments:
            frag = f['fragment']
            # Final dedup against existing linked neg keywords (the AI
            # received this set in suppression, but defensive double-check).
            if frag in existing_negs:
                skipped_dedup += 1
                continue
            try:
                con.execute("""
                    INSERT INTO act_v2_phrase_suggestions
                    (client_id, analysis_date, fragment, word_count,
                     target_list_role, source_search_terms,
                     occurrence_count, risk_level, review_status,
                     confidence, rationale, source_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?, ?, ?)
                """, [
                    client_id, analysis_date, frag,
                    int(f.get('words', 1)),
                    f['target_list_role'],
                    json.dumps(f.get('source_terms', [])),
                    int(f.get('occurrence_count', 0)),
                    str(f.get('risk', 'low')),
                    float(f.get('confidence', 0.0)),
                    str(f.get('rationale', ''))[:4096],
                    int(f.get('occurrence_count', 0)),  # source_count == occurrence_count for now
                ])
                suggestions_created += 1
            except Exception as row_err:
                # Per-row failures must not crash the run.
                logger.warning(
                    'pass3_ai per-row INSERT failed: client=%s frag=%r err=%s',
                    client_id, frag, str(row_err)[:300],
                )

        # Anthropic envelope splits input into 3 buckets — sum them all
        # for an honest tokens_in figure. Cost is computed per bucket
        # using the published Opus 4.7 multipliers (May 2026):
        #   input (uncached) : $15 / M       (1.0×)
        #   cache_creation   : $18.75 / M    (1.25×)
        #   cache_read       : $1.50 / M     (0.10×)
        #   output           : $75 / M       (5.0×)
        in_uncached = int(usage.get('input_tokens', 0) or 0)
        in_cache_creation = int(usage.get('cache_creation_input_tokens', 0) or 0)
        in_cache_read = int(usage.get('cache_read_input_tokens', 0) or 0)
        tokens_in = in_uncached + in_cache_creation + in_cache_read
        tokens_out = int(usage.get('output_tokens', 0) or 0)
        cost_usd = round(
            in_uncached         * 15.00 / 1_000_000
            + in_cache_creation * 18.75 / 1_000_000
            + in_cache_read     *  1.50 / 1_000_000
            + tokens_out        * 75.00 / 1_000_000,
            4,
        )

        result = {
            'engine': 'ai',
            'client_id': client_id,
            'analysis_date': analysis_date,
            'themes': ai_themes,
            'fragments_returned': len(raw_fragments),
            'fragments_dropped': fragments_dropped,
            'suggestions_created': suggestions_created,
            'skipped_dedup': skipped_dedup,
            'terms_considered': len(terms),
            'tokens_in': tokens_in,
            'tokens_out': tokens_out,
            'cost_usd': cost_usd,
            'wall_clock_ms': wall_ms,
            'prompt_version': PROMPT_VERSION_PASS3_AI,
            'model_version': MODEL_PASS3_AI,
        }
        idempotency.set(cache_key, result)
        logger.info(
            'pass3_ai client=%s date=%s themes=%d frags=%d/%d '
            'dropped=%d skipped_dedup=%d tokens_in=%d tokens_out=%d '
            'cost=$%.4f wall=%dms',
            client_id, analysis_date, len(ai_themes),
            suggestions_created, len(raw_fragments),
            fragments_dropped, skipped_dedup,
            tokens_in, tokens_out, cost_usd, wall_ms,
        )
        return result

    finally:
        client_lock.release()


# ============================================================================
# Context loaders
# ============================================================================
def _load_client_context(con, client_id: str) -> dict:
    """Load services_advertised, services_not_advertised, service_locations,
    rule_7_exclude_tokens, client_brand_terms — the fields the AI needs to
    apply the routing rules."""
    row = con.execute(
        """SELECT services_advertised, services_not_advertised,
                  service_locations, rule_7_exclude_tokens, client_brand_terms
           FROM act_v2_clients WHERE client_id = ?""",
        [client_id],
    ).fetchone()
    if not row:
        return {
            'services_advertised': '',
            'services_not_advertised': '',
            'service_locations': '',
            'rule_7_exclude_tokens': '',
            'client_brand_terms': '',
        }
    return {
        'services_advertised':     row[0] or '',
        'services_not_advertised': row[1] or '',
        'service_locations':       row[2] or '',
        'rule_7_exclude_tokens':   row[3] or '',
        'client_brand_terms':      row[4] or '',
    }


def _load_target_lists(con, client_id: str) -> list[dict]:
    """Distinct {list_role, list_name, word_count, match_type} for this
    client's LINKED neg lists. The AI is told to route to one of these
    list_role values; output is validated against this set before INSERT."""
    rows = con.execute(
        """SELECT DISTINCT list_role, list_name, word_count, match_type
           FROM act_v2_negative_keyword_lists
           WHERE client_id = ? AND is_linked_to_campaign = TRUE
             AND list_role IS NOT NULL
           ORDER BY list_role""",
        [client_id],
    ).fetchall()
    return [
        {
            'list_role': r[0],
            'list_name': r[1] or '',
            'word_count': r[2],
            'match_type': r[3] or '',
        }
        for r in rows
    ]


def _load_day_search_terms(con, client_id: str, analysis_date: str) -> list[dict]:
    """Full day's Search + PMax search-term rows.

    Date convention (locked project rule, MEMORY.md "Date picker convention"):
    the picker shows analysis_date which is one day AHEAD of the underlying
    snapshot_date. Overnight ingestion on the morning of day N lands data
    tagged snapshot_date = day N-1. So we resolve the effective snapshot_date
    as MAX(snapshot_date) < analysis_date — same pattern pass1.py L488-492
    uses. Strict less-than (not <=) excludes any same-day ingestion run.

    Joins act_v2_search_term_reviews on analysis_date to surface review_status
    as context (NEVER as a filter). search_term_reviews is correctly keyed on
    analysis_date so that join uses analysis_date verbatim.
    """
    row = con.execute(
        "SELECT MAX(snapshot_date) FROM act_v2_search_terms "
        "WHERE client_id = ? AND snapshot_date < ?",
        [client_id, analysis_date],
    ).fetchone()
    effective_snapshot = row[0] if row else None
    if effective_snapshot is None:
        logger.info(
            'pass3_ai no snapshot < analysis_date=%s for client=%s — empty result',
            analysis_date, client_id,
        )
        return []

    logger.info(
        'pass3_ai resolved snapshot_date=%s for analysis_date=%s (client=%s)',
        effective_snapshot, analysis_date, client_id,
    )

    rows = con.execute(
        """SELECT
              st.search_term,
              st.campaign_type,
              SUM(st.cost)         AS total_cost,
              SUM(st.clicks)       AS total_clicks,
              SUM(st.impressions)  AS total_impressions,
              SUM(st.conversions)  AS total_conversions,
              STRING_AGG(DISTINCT st.match_type, ',') AS match_types,
              MAX(r.review_status) AS review_status
           FROM act_v2_search_terms st
           LEFT JOIN act_v2_search_term_reviews r
                  ON r.client_id = st.client_id
                 AND r.search_term = st.search_term
                 AND r.analysis_date = ?
           WHERE st.client_id = ?
             AND st.snapshot_date = ?
           GROUP BY st.search_term, st.campaign_type
           ORDER BY total_cost DESC NULLS LAST,
                    total_impressions DESC NULLS LAST,
                    st.search_term""",
        [analysis_date, client_id, effective_snapshot],
    ).fetchall()
    return [
        {
            'search_term':   r[0],
            'campaign_type': r[1],
            'cost':          float(r[2] or 0),
            'clicks':        int(r[3] or 0),
            'impressions':   int(r[4] or 0),
            'conversions':   float(r[5] or 0),
            'match_types':   r[6] or '',
            'review_status': r[7] or 'pending',
        }
        for r in rows
    ]


def _load_suppression(con, client_id: str, analysis_date: str) -> dict:
    """Build the SUPPRESSION LIST: fragments the AI must never re-suggest.

      - All sticky-rejected fragments for this client (any date).
      - Yesterday's pushed Pass 3 fragments.
      - Last 30 days of pushed neg keywords (any list).
    """
    rejected_rows = con.execute(
        """SELECT DISTINCT fragment FROM act_v2_phrase_suggestions
           WHERE client_id = ? AND review_status = 'rejected'""",
        [client_id],
    ).fetchall()

    try:
        d = datetime.fromisoformat(analysis_date).date()
    except Exception:  # noqa: BLE001
        d = date.today()
    yesterday = (d - timedelta(days=1)).isoformat()
    thirty_days_ago = (d - timedelta(days=30)).isoformat()

    yesterday_pushed_rows = con.execute(
        """SELECT DISTINCT fragment FROM act_v2_phrase_suggestions
           WHERE client_id = ? AND analysis_date = ?
             AND review_status = 'pushed'""",
        [client_id, yesterday],
    ).fetchall()

    pushed_negs_rows = con.execute(
        """SELECT DISTINCT keyword_text
           FROM act_v2_negative_list_keywords
           WHERE client_id = ?
             AND snapshot_date >= ?""",
        [client_id, thirty_days_ago],
    ).fetchall()

    return {
        'sticky_rejected_fragments': sorted({r[0] for r in rejected_rows if r[0]}),
        'yesterday_pushed_fragments': sorted({r[0] for r in yesterday_pushed_rows if r[0]}),
        'last_30d_pushed_negs': sorted({r[0] for r in pushed_negs_rows if r[0]}),
    }


def _load_existing_negs(con, client_id: str) -> set[str]:
    """Final defensive dedup set against the latest snapshot of all linked
    neg keywords. Mirrors the rule-based pass3.py L104-127 behaviour."""
    latest = con.execute(
        "SELECT MAX(snapshot_date) FROM act_v2_negative_list_keywords "
        "WHERE client_id = ?",
        [client_id],
    ).fetchone()[0]
    if not latest:
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
    return {(r[0] or '').strip().lower() for r in rows if r[0]}


# ============================================================================
# Prompt rendering
# ============================================================================
def _build_user_message(client_id: str, analysis_date: str,
                         client_ctx: dict, target_lists: list[dict],
                         terms: list[dict], suppression: dict) -> str:
    """Render the per-call user message. Sectioned headers match the
    system prompt's section-name references."""
    parts: list[str] = []
    parts.append(f'CLIENT: {client_id}')
    parts.append(f'ANALYSIS DATE: {analysis_date}')
    parts.append('')

    parts.append('=== CLIENT CONFIG ===')
    parts.append(f'Services advertised: {client_ctx["services_advertised"] or "(none)"}')
    parts.append(f'Services NOT advertised: {client_ctx["services_not_advertised"] or "(none)"}')
    parts.append(f'rule_7_exclude_tokens (off-not-advertised priority list): '
                 f'{client_ctx["rule_7_exclude_tokens"] or "(none)"}')
    parts.append(f'Service locations (in-area — NEVER suggest these): '
                 f'{client_ctx["service_locations"] or "(none)"}')
    parts.append(f'Brand terms (NEVER suggest these): '
                 f'{client_ctx["client_brand_terms"] or "(none)"}')
    parts.append('')

    parts.append('=== AVAILABLE TARGET LISTS ===')
    parts.append('list_role values you may use (one per fragment); anything '
                 'else will be rejected:')
    for tl in target_lists:
        parts.append(
            f'  {tl["list_role"]}  '
            f'(name: "{tl["list_name"]}", '
            f'word_count: {tl["word_count"]}, match_type: {tl["match_type"]})'
        )
    parts.append('')

    parts.append('=== SUPPRESSION LIST (NEVER suggest any fragment in here) ===')
    parts.append(f'Sticky-rejected fragments ({len(suppression["sticky_rejected_fragments"])}):')
    for f in suppression['sticky_rejected_fragments'][:200]:
        parts.append(f'  {f}')
    parts.append(f"Yesterday's pushed Pass 3 fragments "
                 f'({len(suppression["yesterday_pushed_fragments"])}):')
    for f in suppression['yesterday_pushed_fragments'][:200]:
        parts.append(f'  {f}')
    parts.append(f"Last-30-day pushed neg keywords (excerpt of "
                 f'{len(suppression["last_30d_pushed_negs"])}):')
    for f in suppression['last_30d_pushed_negs'][:500]:
        parts.append(f'  {f}')
    parts.append('')

    parts.append(f'=== TODAY\'S SEARCH TERMS ({len(terms)} rows) ===')
    parts.append('Format: search_term | campaign_type | cost | clicks | '
                 'impressions | conversions | match_types | review_status')
    parts.append('review_status is CONTEXT ONLY — never a filter on which '
                 'terms to read.')
    for t in terms:
        parts.append(
            f'  {t["search_term"]} | {t["campaign_type"]} | '
            f'£{t["cost"]:.2f} | {t["clicks"]} | {t["impressions"]} | '
            f'{t["conversions"]:.2f} | {t["match_types"]} | {t["review_status"]}'
        )
    parts.append('')
    parts.append('=== END OF INPUT ===')
    parts.append('Now produce the JSON output exactly per the system prompt.')

    return '\n'.join(parts)


# ============================================================================
# Response parsing + validation
# ============================================================================
def _parse_response(result_text: str, valid_roles: set[str]) -> dict:
    """Parse Claude's response. Strip markdown fences defensively. Returns
    the {themes, fragments} dict. Raises _ParseError on any structural
    issue. target_list_role validation is done in _filter_valid_fragments
    (we keep the parse step lenient so we don't throw away the whole
    batch over one bad fragment)."""
    txt = (result_text or '').strip()
    if txt.startswith('```'):
        first_nl = txt.find('\n')
        if first_nl != -1:
            txt = txt[first_nl + 1:]
        if txt.endswith('```'):
            txt = txt[:-3]
        txt = txt.strip()

    try:
        obj = json.loads(txt)
    except json.JSONDecodeError as e:
        raise _ParseError(f'inner JSON parse failed: {e}')

    if not isinstance(obj, dict):
        raise _ParseError(f'expected JSON object, got {type(obj).__name__}')

    themes = obj.get('themes')
    fragments = obj.get('fragments')
    if not isinstance(themes, list):
        raise _ParseError('themes is not a list')
    if not isinstance(fragments, list):
        raise _ParseError('fragments is not a list')

    # Themes: drop non-strings rather than nuke the batch (themes are
    # display-only — a single bad theme shouldn't kill the run).
    clean_themes: list[str] = []
    for i, t in enumerate(themes):
        if isinstance(t, str) and t.strip():
            clean_themes.append(t)
        else:
            logger.warning('pass3_ai dropped themes[%d]: %r', i, t)

    # Fragments: sanitise-and-drop per-item rather than raise. Reasons we
    # drop (logged with a counter so production can monitor drift):
    #   - missing required key
    #   - fragment empty / non-string
    #   - words outside 1..4 (Opus occasionally emits 5+)
    #   - confidence outside 0..1
    # Only structural failures of the OUTER object (themes/fragments not
    # being lists) still raise — those signal Opus genuinely broke the
    # contract and a retry is the right move.
    clean_fragments: list[dict] = []
    drop_reasons: dict[str, int] = {}
    for i, f in enumerate(fragments):
        if not isinstance(f, dict):
            drop_reasons['not_object'] = drop_reasons.get('not_object', 0) + 1
            continue
        missing = [k for k in ('fragment', 'words', 'target_list_role', 'confidence')
                   if k not in f]
        if missing:
            drop_reasons['missing_key'] = drop_reasons.get('missing_key', 0) + 1
            logger.warning('pass3_ai dropped fragments[%d] missing %s', i, missing)
            continue
        if not isinstance(f['fragment'], str) or not f['fragment'].strip():
            drop_reasons['bad_fragment'] = drop_reasons.get('bad_fragment', 0) + 1
            continue
        try:
            wc = int(f['words'])
            cf = float(f['confidence'])
        except (TypeError, ValueError):
            drop_reasons['type_error'] = drop_reasons.get('type_error', 0) + 1
            continue
        if wc < 1 or wc > 4:
            drop_reasons['words_out_of_range'] = drop_reasons.get('words_out_of_range', 0) + 1
            logger.warning(
                'pass3_ai dropped fragment %r: words=%s out of 1..4',
                f.get('fragment'), wc,
            )
            continue
        if cf < 0.0 or cf > 1.0:
            drop_reasons['confidence_out_of_range'] = drop_reasons.get('confidence_out_of_range', 0) + 1
            continue
        # Coerce to in-range types so downstream code sees ints/floats.
        f['words'] = wc
        f['confidence'] = cf
        clean_fragments.append(f)

    if drop_reasons:
        logger.info(
            'pass3_ai _parse_response sanitised: kept=%d dropped=%s',
            len(clean_fragments), drop_reasons,
        )

    return {'themes': clean_themes, 'fragments': clean_fragments}


def _filter_valid_fragments(fragments: list[dict],
                              valid_roles: set[str]) -> tuple[list[dict], int]:
    """Apply 3 production filters before INSERT:

      1. target_list_role must be in the client's real linked-list set
         (no invented list names).
      2. occurrence_count must be > 0 — protects against Opus
         hallucinating fragments not actually in today's data.
      3. dedup by (fragment, target_list_role); keep the highest-
         confidence variant on collision (first-seen if tied), since
         Opus occasionally emits the same fragment twice with slightly
         different rationales / source_terms.

    Returns (kept, total_dropped).
    """
    # Pass 1: structural drops (invalid role, occ=0).
    pass_1: list[dict] = []
    drops = {'invalid_role': 0, 'zero_occurrence': 0, 'duplicate': 0}
    for f in fragments:
        if f.get('target_list_role') not in valid_roles:
            drops['invalid_role'] += 1
            logger.warning(
                'pass3_ai dropped fragment %r: invalid target_list_role=%r',
                f.get('fragment'), f.get('target_list_role'),
            )
            continue
        try:
            occ = int(f.get('occurrence_count') or 0)
        except (TypeError, ValueError):
            occ = 0
        if occ <= 0:
            drops['zero_occurrence'] += 1
            logger.warning(
                'pass3_ai dropped fragment %r: occurrence_count=%s '
                '(probable hallucination — fragment not in dataset)',
                f.get('fragment'), f.get('occurrence_count'),
            )
            continue
        pass_1.append(f)

    # Pass 2: dedup. Key on (fragment, target_list_role); keep the
    # highest-confidence variant. Stable when confidences tie — first-seen
    # wins (preserves Opus's natural ranking order).
    by_key: dict[tuple[str, str], dict] = {}
    for f in pass_1:
        key = (f.get('fragment') or '', f.get('target_list_role') or '')
        existing = by_key.get(key)
        if existing is None:
            by_key[key] = f
        else:
            old_cf = float(existing.get('confidence') or 0)
            new_cf = float(f.get('confidence') or 0)
            if new_cf > old_cf:
                by_key[key] = f
            drops['duplicate'] += 1
            logger.warning(
                'pass3_ai deduplicated fragment %r role=%r '
                '(prev_conf=%.2f, new_conf=%.2f)',
                key[0], key[1], old_cf, new_cf,
            )
    kept = list(by_key.values())

    if any(drops.values()):
        logger.info(
            'pass3_ai _filter_valid_fragments: kept=%d drops=%s',
            len(kept), drops,
        )
    total_dropped = sum(drops.values())
    return kept, total_dropped


def _empty_result(error: str | None = None,
                   skipped: str | None = None) -> dict:
    return {
        'engine': 'ai',
        'themes': [],
        'fragments_returned': 0,
        'fragments_dropped': 0,
        'suggestions_created': 0,
        'skipped_dedup': 0,
        'terms_considered': 0,
        'tokens_in': 0,
        'tokens_out': 0,
        'cost_usd': 0.0,
        'wall_clock_ms': 0,
        'prompt_version': PROMPT_VERSION_PASS3_AI,
        'model_version': MODEL_PASS3_AI,
        **({'error': error} if error else {}),
        **({'skipped': skipped} if skipped else {}),
    }
