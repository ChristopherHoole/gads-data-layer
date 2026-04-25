"""Tier 2.1 Stage 4 — batch classify orchestrator.

Pure function called by the v2_ai_api.classify_terms endpoint. Loads
prompts, fetches context, calls Claude (Sonnet via subprocess), parses,
persists to act_v2_ai_classifications, logs failures to act_v2_ai_errors.

Concurrency:
  - Per-client lock (acquired non-blocking — concurrent calls for the
    same client return 409 LockContentionError to the caller).
  - 30-second in-memory idempotency cache short-circuits identical
    repeat calls before lock acquisition.

Retries:
  - Single retry on any ClaudeError or _ParseError (transient subprocess
    blips, malformed JSON). Both attempts share the same per-row context.

Persistence:
  - DELETE+INSERT (autocommit, no transaction wrapper) when
    force_reclassify=True — DuckDB 1.1.0 false-positive PK errors on
    UPDATE-of-UNIQUE forbid the simpler UPDATE path. Mirror of the
    pattern in v2_negatives_api.bulk_update_phrase_suggestions().
  - Per-row INSERT failures are caught and logged so a single bad row
    doesn't crash the whole batch.

Returns dict matching the endpoint's response schema (no "stub" key —
that flag was scaffolding only and is gone now).
"""
from __future__ import annotations

import json
import logging

from act_dashboard.ai import (
    claude_subprocess,
    context,
    idempotency,
    locks,
    prompt_loader,
)
from act_dashboard.ai.prompts import (
    PROMPT_FILE_CLASSIFY,
    PROMPT_FILE_PASS3,
    PROMPT_FILE_PASS3_USER,
    PROMPT_FILE_USER,
    PROMPT_VERSION_CLASSIFY,
    PROMPT_VERSION_PASS3,
)

logger = logging.getLogger(__name__)

# Stage 4.5 (revised 25 Apr PM): switched from Sonnet 4.6 to Opus 4.7 for
# both batch classify and (Stage 5) explain-row. Reasoning logged in scope
# §13 Q4. Full slug used (not the 'opus' alias) — version locking is
# critical for agreement-rate measurements over time.
MODEL_BATCH = 'claude-opus-4-7'


class _ParseError(Exception):
    """Internal — Claude returned malformed/mismatched output. Caller
    upgrades to ClaudeError(invalid_json) only after the retry."""


# ============================================================================
# Public entry point
# ============================================================================
def classify_batch(con, client_id: str, analysis_date: str, flow: str,
                   ids: list[int], force_reclassify: bool) -> dict:
    """Returns dict matching the endpoint's response schema.

    May raise locks.LockContentionError (caller maps to 409).
    May raise claude_subprocess.ClaudeError after retry (caller maps to 502).
    """
    is_pass3 = (flow == 'pass3')
    prompt_version = (
        PROMPT_VERSION_PASS3 if is_pass3 else PROMPT_VERSION_CLASSIFY
    )

    # ---- Idempotency check (BEFORE lock — short-circuit duplicate calls) ----
    cache_key = idempotency.make_key(
        client_id, flow, ids, prompt_version, force_reclassify,
    )
    cached = idempotency.get(cache_key)
    if cached is not None:
        logger.info(
            'classify_batch idempotency hit: client=%s flow=%s n=%d',
            client_id, flow, len(ids),
        )
        return cached

    # ---- Acquire per-client lock (non-blocking) ----
    client_lock = locks.get_client_lock(client_id)
    if not client_lock.acquire(blocking=False):
        raise locks.LockContentionError(client_id)

    try:
        # ---- Fetch row context (preserves input order — see context.py) ----
        if is_pass3:
            rows = context.get_phrase_suggestion_rows(con, ids)
            id_key = 'phrase_id'
        else:
            rows = context.get_review_rows(con, ids)
            id_key = 'review_id'

        if not rows:
            result = _empty_result()
            idempotency.set(cache_key, result)
            return result

        # ---- Skip-if-classified (or DELETE if force_reclassify) ----
        if force_reclassify:
            _force_reclassify_delete(
                con, is_pass3,
                [r[id_key] for r in rows], prompt_version,
            )
            rows_to_classify = rows
            skipped = 0
        else:
            already_done = _fetch_already_classified_ids(
                con, is_pass3, [r[id_key] for r in rows], prompt_version,
            )
            rows_to_classify = [r for r in rows if r[id_key] not in already_done]
            skipped = len(rows) - len(rows_to_classify)

        if not rows_to_classify:
            result = {
                'classified': 0,
                'results': [],
                'skipped_already_classified': skipped,
                'tokens_used': 0,
                'wall_clock_ms': 0,
            }
            idempotency.set(cache_key, result)
            return result

        # ---- Render prompts ----
        client_ctx = context.get_client_context(con, client_id)

        if is_pass3:
            system_template = prompt_loader.load_prompt(PROMPT_FILE_PASS3)
            user_template = prompt_loader.load_prompt(PROMPT_FILE_PASS3_USER)
            rendered_list = context.render_phrase_list(rows_to_classify)
            user_message = prompt_loader.render(
                user_template,
                count=len(rows_to_classify),
                client_id=client_id,
                analysis_date=analysis_date,
                rendered_phrase_list=rendered_list,
            )
            # pass3 system prompt has no client-context placeholders
            system_prompt = system_template
        else:
            system_template = prompt_loader.load_prompt(PROMPT_FILE_CLASSIFY)
            user_template = prompt_loader.load_prompt(PROMPT_FILE_USER)
            rendered_list = context.render_term_list(rows_to_classify)
            user_message = prompt_loader.render(
                user_template,
                count=len(rows_to_classify),
                client_id=client_id,
                analysis_date=analysis_date,
                flow=flow,
                rendered_term_list=rendered_list,
            )
            # client_id merged in here; client_ctx intentionally omits it
            system_prompt = prompt_loader.render(
                system_template, client_id=client_id, **client_ctx,
            )

        # ---- Call Claude (retry once on failure) ----
        result_text = None
        usage: dict = {}
        wall_ms = 0
        parsed: list[dict] = []
        last_error: Exception | None = None
        for attempt in (1, 2):
            try:
                result_text, usage, wall_ms = claude_subprocess.run_claude(
                    MODEL_BATCH, system_prompt, user_message,
                )
                parsed = _parse_result(
                    result_text, is_pass3, len(rows_to_classify),
                )
                last_error = None
                break  # success
            except (claude_subprocess.ClaudeError, _ParseError) as e:
                last_error = e
                error_type = getattr(e, 'error_type', 'invalid_json')
                logger.warning(
                    'classify_batch attempt %d failed: client=%s flow=%s '
                    'error_type=%s msg=%s',
                    attempt, client_id, flow, error_type, str(e)[:300],
                )
                if attempt == 2:
                    _log_error(
                        con, client_id, analysis_date, flow,
                        [r[id_key] for r in rows_to_classify],
                        error_type, str(e), getattr(e, 'raw_output', ''),
                    )
                    # Surface a ClaudeError to the endpoint regardless of
                    # which class fired (parse failures wrap as invalid_json).
                    if isinstance(e, claude_subprocess.ClaudeError):
                        raise
                    raise claude_subprocess.ClaudeError(
                        'invalid_json', str(e),
                        getattr(e, 'raw_output', ''),
                    ) from e

        if last_error is not None:  # defensive — both attempts failed but
            raise last_error           # didn't raise above (shouldn't happen)

        # ---- Persist classifications (per-row try/except) ----
        n = max(1, len(rows_to_classify))
        per_row_tokens_in = (usage.get('input_tokens', 0) or 0) // n
        per_row_tokens_out = (usage.get('output_tokens', 0) or 0) // n
        per_row_latency = wall_ms // n

        results_payload: list[dict] = []
        for row, parsed_item in zip(rows_to_classify, parsed):
            try:
                _insert_classification(
                    con, row, parsed_item, flow, is_pass3,
                    client_id, analysis_date, prompt_version,
                    MODEL_BATCH, per_row_tokens_in,
                    per_row_tokens_out, per_row_latency,
                )
                results_payload.append(
                    _build_response_item(row, parsed_item, is_pass3),
                )
            except Exception as row_err:
                # Per-row failure must NOT crash the batch — log + continue.
                # Common cause: race-condition UNIQUE violation if
                # force=False but another request inserted between our
                # skip-check and our INSERT.
                logger.warning(
                    'per-row INSERT failed: client=%s flow=%s id=%s err=%s',
                    client_id, flow, row[id_key], str(row_err)[:300],
                )
                _log_error(
                    con, client_id, analysis_date, flow,
                    [row[id_key]], 'insert_failed',
                    str(row_err), '',
                )
                # don't append — caller sees only successes

        result = {
            'classified': len(results_payload),
            'results': results_payload,
            'skipped_already_classified': skipped,
            'tokens_used': (
                (usage.get('input_tokens', 0) or 0)
                + (usage.get('output_tokens', 0) or 0)
            ),
            'wall_clock_ms': wall_ms,
        }
        idempotency.set(cache_key, result)
        return result

    finally:
        client_lock.release()


# ============================================================================
# Helpers
# ============================================================================
def _empty_result() -> dict:
    return {
        'classified': 0,
        'results': [],
        'skipped_already_classified': 0,
        'tokens_used': 0,
        'wall_clock_ms': 0,
    }


def _fetch_already_classified_ids(con, is_pass3: bool, ids: list[int],
                                   prompt_version: str) -> set[int]:
    """Return set of IDs already in act_v2_ai_classifications at this
    prompt_version."""
    fk_col = 'phrase_suggestion_id' if is_pass3 else 'review_id'
    placeholders = ','.join(['?'] * len(ids))
    rows = con.execute(
        f"SELECT {fk_col} FROM act_v2_ai_classifications "
        f"WHERE {fk_col} IN ({placeholders}) AND prompt_version = ?",
        [*ids, prompt_version],
    ).fetchall()
    return {r[0] for r in rows}


def _force_reclassify_delete(con, is_pass3: bool, ids: list[int],
                              prompt_version: str) -> None:
    """Delete existing classifications so a subsequent INSERT can repopulate.

    DuckDB 1.1.0 Python connection is autocommit by default; do NOT wrap
    in con.begin()/commit(). DELETE+INSERT inside one transaction triggers
    the false-positive PK error documented in project memory. Same pattern
    as v2_negatives_api.bulk_update_phrase_suggestions().
    """
    fk_col = 'phrase_suggestion_id' if is_pass3 else 'review_id'
    placeholders = ','.join(['?'] * len(ids))
    con.execute(
        f"DELETE FROM act_v2_ai_classifications "
        f"WHERE {fk_col} IN ({placeholders}) AND prompt_version = ?",
        [*ids, prompt_version],
    )


def _parse_result(result_text: str, is_pass3: bool,
                  expected_count: int) -> list[dict]:
    """Parse Claude's response. Strip markdown fences defensively.
    Validate schema. Raises _ParseError on any issue."""
    txt = (result_text or '').strip()
    # System prompt says no fences, but be tolerant — tend to drift.
    if txt.startswith('```'):
        first_nl = txt.find('\n')
        if first_nl != -1:
            txt = txt[first_nl + 1:]
        if txt.endswith('```'):
            txt = txt[:-3]
        txt = txt.strip()

    try:
        items = json.loads(txt)
    except json.JSONDecodeError as e:
        raise _ParseError(f'inner JSON parse failed: {e}')

    if not isinstance(items, list):
        raise _ParseError(
            f'expected JSON array, got {type(items).__name__}',
        )

    if len(items) != expected_count:
        raise _ParseError(
            f'count mismatch: got {len(items)}, expected {expected_count}',
        )

    for i, item in enumerate(items):
        if not isinstance(item, dict):
            raise _ParseError(f'item {i} is not a dict')
        if is_pass3:
            required = (
                'phrase_id', 'ai_target_list_role',
                'ai_confidence', 'ai_reasoning',
            )
        else:
            required = (
                'review_id', 'ai_verdict', 'ai_confidence',
                'ai_reasoning', 'ai_intent_tag',
            )
        missing = [k for k in required if k not in item]
        if missing:
            raise _ParseError(f'item {i} missing keys: {missing}')
        if not is_pass3 and item['ai_verdict'] not in (
                'approve', 'reject', 'unsure'):
            raise _ParseError(
                f'item {i} bad ai_verdict: {item["ai_verdict"]!r}',
            )
        if item['ai_confidence'] not in ('high', 'medium', 'low'):
            raise _ParseError(
                f'item {i} bad ai_confidence: {item["ai_confidence"]!r}',
            )

    return items


def _insert_classification(con, row, parsed, flow, is_pass3, client_id,
                            analysis_date, prompt_version, model_version,
                            tokens_in, tokens_out, latency_ms) -> None:
    """INSERT one row into act_v2_ai_classifications.

    Block/review:
        review_id set, phrase_suggestion_id NULL,
        ai_verdict set, ai_target_list_role NULL,
        ai_intent_tag set, search_term set, fragment NULL.
    Pass3:
        phrase_suggestion_id set, review_id NULL,
        ai_verdict NULL, ai_target_list_role set,
        ai_intent_tag NULL, search_term NULL, fragment set.

    The CHECK constraint on the table enforces this layout — see
    act_v2_ai_classifications migration (Stage 1).
    """
    if is_pass3:
        con.execute("""
            INSERT INTO act_v2_ai_classifications (
                review_id, phrase_suggestion_id, client_id, analysis_date,
                search_term, fragment, flow,
                ai_verdict, ai_target_list_role, ai_reasoning, ai_confidence,
                ai_intent_tag, model_version, prompt_version,
                tokens_in, tokens_out, latency_ms
            ) VALUES (NULL, ?, ?, ?, NULL, ?, ?,
                      NULL, ?, ?, ?,
                      NULL, ?, ?, ?, ?, ?)
        """, [
            row['phrase_id'], client_id, analysis_date,
            row['fragment'], flow,
            parsed['ai_target_list_role'], parsed['ai_reasoning'],
            parsed['ai_confidence'],
            model_version, prompt_version,
            tokens_in, tokens_out, latency_ms,
        ])
    else:
        con.execute("""
            INSERT INTO act_v2_ai_classifications (
                review_id, phrase_suggestion_id, client_id, analysis_date,
                search_term, fragment, flow,
                ai_verdict, ai_target_list_role, ai_reasoning, ai_confidence,
                ai_intent_tag, model_version, prompt_version,
                tokens_in, tokens_out, latency_ms
            ) VALUES (?, NULL, ?, ?, ?, NULL, ?,
                      ?, NULL, ?, ?,
                      ?, ?, ?, ?, ?, ?)
        """, [
            row['review_id'], client_id, analysis_date,
            row['search_term'], flow,
            parsed['ai_verdict'], parsed['ai_reasoning'],
            parsed['ai_confidence'],
            parsed.get('ai_intent_tag'), model_version, prompt_version,
            tokens_in, tokens_out, latency_ms,
        ])


def _build_response_item(row, parsed, is_pass3) -> dict:
    """Shape per scope §6.1 response."""
    if is_pass3:
        return {
            'phrase_suggestion_id': row['phrase_id'],
            'fragment': row['fragment'],
            'ai_target_list_role': parsed['ai_target_list_role'],
            'ai_confidence': parsed['ai_confidence'],
            'ai_reasoning': parsed['ai_reasoning'],
        }
    return {
        'review_id': row['review_id'],
        'search_term': row['search_term'],
        'ai_verdict': parsed['ai_verdict'],
        'ai_confidence': parsed['ai_confidence'],
        'ai_reasoning': parsed['ai_reasoning'],
        'ai_intent_tag': parsed.get('ai_intent_tag'),
    }


def _log_error(con, client_id, analysis_date, flow, ids, error_type,
               error_message, raw_output) -> None:
    """INSERT into act_v2_ai_errors. Never raises — logger-only on failure
    so the original error reaches the caller untouched."""
    try:
        con.execute(
            "INSERT INTO act_v2_ai_errors "
            "(client_id, analysis_date, flow, review_ids_in_batch, "
            " error_type, error_message, raw_output) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            [
                client_id, analysis_date, flow, json.dumps(ids),
                error_type, (error_message or '')[:4096],
                (raw_output or '')[:4096],
            ],
        )
    except Exception as log_err:
        logger.error(
            'failed to log AI error to DB: %s | original error: %s/%s',
            log_err, error_type, (error_message or '')[:200],
        )
