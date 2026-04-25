"""Tier 2.1 Stage 5 — single-row deep reasoning via Opus 4.7.

Mirrors classifier.py structure but works on one row at a time:
fetch context, build a user message including any prior AI verdict,
call Claude, persist user question + assistant response to
act_v2_ai_chat_log.

Locks: shares the per-client Lock from locks.get_client_lock so
classify-terms / explain-row / chat for the same client serialise
naturally without contending across clients.

No idempotency cache: each click is a fresh call by design. A
double-click inside 30s sends two requests to Claude — acceptable
for MVP, prevents stale explanations.

Persistence ordering: the user-question row is INSERTed BEFORE the
Claude call so the question is preserved even if Claude subsequently
fails. The assistant row is INSERTed only on success.
"""
from __future__ import annotations

import logging

from act_dashboard.ai import claude_subprocess, context, locks, prompt_loader
# TODO Tier 2.2: move _log_error to a shared act_dashboard/ai/_db_helpers.py.
# Importing it from classifier works fine but is smelly cross-module reach
# for what should be a generic AI-error logger.
from act_dashboard.ai.classifier import _log_error
from act_dashboard.ai.prompts import (
    PROMPT_FILE_EXPLAIN,
    PROMPT_VERSION_EXPLAIN,
)

logger = logging.getLogger(__name__)

# Same value as classifier.MODEL_BATCH post-Stage-4.5; kept as a separate
# constant so a future split (e.g. cheaper model for explain) is a
# one-line change here, not a search-and-replace across both modules.
MODEL_EXPLAIN = 'claude-opus-4-7'


def explain_row(con, client_id: str, review_id: int, flow: str,
                analysis_date: str, question: str | None) -> dict:
    """Returns dict matching the endpoint's response schema.

    May raise locks.LockContentionError (caller -> 409).
    May raise claude_subprocess.ClaudeError after retry (caller -> 502).
    """
    client_lock = locks.get_client_lock(client_id)
    if not client_lock.acquire(blocking=False):
        raise locks.LockContentionError(client_id)

    try:
        rows = context.get_review_rows(con, [review_id])
        if not rows:
            # Endpoint already validated existence — defensive fallback for
            # a race where the row was deleted between validation and here.
            raise ValueError(f"review_id {review_id} not found")
        row = rows[0]

        client_ctx = context.get_client_context(con, client_id)
        existing_verdict = _fetch_latest_classification(con, review_id)

        system_prompt = prompt_loader.load_prompt(PROMPT_FILE_EXPLAIN)
        effective_question = (
            question.strip() if (question and question.strip())
            else 'Explain why this verdict is correct, or why the row is ambiguous.'
        )
        user_message = _build_user_message(
            row, client_id, client_ctx,
            existing_verdict, effective_question,
        )

        # Persist the user question BEFORE the Claude call so the question
        # is preserved even if Claude fails.
        _insert_chat_user(
            con, client_id, flow, analysis_date,
            effective_question, review_id,
        )

        # Call Claude (retry once on failure).
        explanation: str | None = None
        usage: dict = {}
        wall_ms = 0
        for attempt in (1, 2):
            try:
                explanation, usage, wall_ms = claude_subprocess.run_claude(
                    MODEL_EXPLAIN, system_prompt, user_message,
                )
                break
            except claude_subprocess.ClaudeError as e:
                logger.warning(
                    'explain_row attempt %d failed: client=%s review_id=%d '
                    'error_type=%s msg=%s',
                    attempt, client_id, review_id, e.error_type, str(e)[:300],
                )
                if attempt == 2:
                    _log_error(
                        con, client_id, analysis_date, flow,
                        [review_id], e.error_type, str(e),
                        getattr(e, 'raw_output', ''),
                    )
                    raise

        # Defensive: strip markdown fences if Opus added them despite the
        # prompt's "no markdown fences" instruction. Mirrors the same
        # defence in classifier._parse_result.
        explanation_text = (explanation or '').strip()
        if explanation_text.startswith('```'):
            first_nl = explanation_text.find('\n')
            if first_nl != -1:
                explanation_text = explanation_text[first_nl + 1:]
            if explanation_text.endswith('```'):
                explanation_text = explanation_text[:-3]
            explanation_text = explanation_text.strip()

        assistant_row_id = _insert_chat_assistant(
            con, client_id, flow, analysis_date,
            explanation_text, review_id,
            MODEL_EXPLAIN, PROMPT_VERSION_EXPLAIN,
            int(usage.get('input_tokens', 0) or 0),
            int(usage.get('output_tokens', 0) or 0),
            wall_ms,
        )

        return {
            'review_id': review_id,
            'explanation': explanation_text,
            'model_version': MODEL_EXPLAIN,
            'tokens_used': (
                int(usage.get('input_tokens', 0) or 0)
                + int(usage.get('output_tokens', 0) or 0)
            ),
            'wall_clock_ms': wall_ms,
            'chat_log_id': assistant_row_id,
        }

    finally:
        client_lock.release()


# ===========================================================================
# Helpers
# ===========================================================================
def _fetch_latest_classification(con, review_id: int) -> dict | None:
    """Latest AI classification for this review_id (any prompt_version), or
    None if never classified. Gives Opus the prior verdict for context so
    the explanation can build on / question / nuance the batch result."""
    row = con.execute(
        """SELECT ai_verdict, ai_confidence, ai_reasoning, ai_intent_tag,
                  model_version, prompt_version
             FROM act_v2_ai_classifications
            WHERE review_id = ?
            ORDER BY classified_at DESC
            LIMIT 1""",
        [review_id],
    ).fetchone()
    if row is None:
        return None
    return {
        'ai_verdict': row[0],
        'ai_confidence': row[1],
        'ai_reasoning': row[2],
        'ai_intent_tag': row[3],
        'model_version': row[4],
        'prompt_version': row[5],
    }


def _build_user_message(row: dict, client_id: str, client_ctx: dict,
                         existing_verdict: dict | None,
                         question: str) -> str:
    """Render the row + client context + optional prior verdict + question
    into the user message Opus receives. The system prompt
    (explain_row_v1.txt) describes the expected output format and is
    static (no placeholders) — all dynamic context lives here."""
    cost = row.get('total_cost') or 0
    clicks = row.get('total_clicks') or 0
    impressions = row.get('total_impressions') or 0
    conversions = row.get('total_conversions') or 0

    parts: list[str] = []
    parts.append('ROW CONTEXT:')
    parts.append(f'  [{row["review_id"]}] "{row["search_term"]}"')
    parts.append(
        f'  pass1_reason: {row.get("pass1_reason") or "—"} '
        f'/ detail: {row.get("pass1_reason_detail") or "—"}'
    )
    parts.append(
        f'  cost: £{float(cost):.2f} | clicks: {clicks} '
        f'| impressions: {impressions} | conversions: {conversions}'
    )
    parts.append(
        f'  triggered by keyword: "{row.get("triggering_keywords") or "—"}"'
    )
    parts.append(f'  campaigns: {row.get("campaigns") or "—"}')
    parts.append('')
    parts.append('CLIENT CONTEXT:')
    parts.append(f'  Client: {client_ctx["client_name"]} ({client_id})')
    parts.append(f'  Persona: {client_ctx["persona"]}')
    parts.append(f'  Target CPA: £{client_ctx["target_cpa"]}')
    parts.append(f'  Service area: {client_ctx["service_area"]}')
    parts.append(f'  Clinic location: {client_ctx["clinic_location"]}')
    parts.append(
        f'  Services advertised: {client_ctx["services_advertised_csv"]}'
    )
    parts.append(
        f'  Services NOT advertised: {client_ctx["services_not_advertised_csv"]}'
    )
    parts.append(f'  Brand terms: {client_ctx["brand_terms_csv"]}')
    parts.append(f'  Competitor brands: {client_ctx["competitor_brands_csv"]}')
    parts.append(
        f'  30-day converters: {client_ctx["converters_last_30d_csv"]}'
    )
    parts.append('')
    if existing_verdict:
        parts.append(
            'PRIOR AI VERDICT (from batch classifier — your job is to add '
            'nuance/confidence):'
        )
        parts.append(f'  verdict: {existing_verdict["ai_verdict"]}')
        parts.append(f'  confidence: {existing_verdict["ai_confidence"]}')
        parts.append(f'  intent_tag: {existing_verdict["ai_intent_tag"]}')
        parts.append(f'  reasoning: {existing_verdict["ai_reasoning"]}')
        parts.append('')
    parts.append(f'USER QUESTION: {question}')

    return '\n'.join(parts)


def _insert_chat_user(con, client_id: str, flow: str, analysis_date: str,
                      message: str, related_review_id: int) -> int:
    """INSERT user-role row to act_v2_ai_chat_log. Return new row's id."""
    result = con.execute(
        """INSERT INTO act_v2_ai_chat_log
              (client_id, flow, analysis_date, role, message, related_review_id)
           VALUES (?, ?, ?, 'user', ?, ?)
           RETURNING id""",
        [client_id, flow, analysis_date, message, related_review_id],
    ).fetchone()
    return result[0]


def _insert_chat_assistant(con, client_id: str, flow: str, analysis_date: str,
                            message: str, related_review_id: int,
                            model_version: str, prompt_version: str,
                            tokens_in: int, tokens_out: int,
                            latency_ms: int) -> int:
    """INSERT assistant-role row to act_v2_ai_chat_log. Return new row's id."""
    result = con.execute(
        """INSERT INTO act_v2_ai_chat_log
              (client_id, flow, analysis_date, role, message, related_review_id,
               model_version, prompt_version, tokens_in, tokens_out, latency_ms)
           VALUES (?, ?, ?, 'assistant', ?, ?, ?, ?, ?, ?, ?)
           RETURNING id""",
        [
            client_id, flow, analysis_date, message, related_review_id,
            model_version, prompt_version, tokens_in, tokens_out, latency_ms,
        ],
    ).fetchone()
    return result[0]
