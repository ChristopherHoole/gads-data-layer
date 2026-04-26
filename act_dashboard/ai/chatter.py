"""Tier 2.1 Stage 9 — free-text chat panel via Opus 4.7.

Mirrors classifier.py / explainer.py structure: orchestrator + helpers,
per-client lock, retry-once, full error logging. Chat is scoped to
(client_id, flow, analysis_date) — each context has its own thread.

Persistence ordering: user-message row INSERTed BEFORE the Claude call
(same trick as explainer.py) so the user's question is preserved if
Claude fails. Assistant row INSERTed only on success.
"""
from __future__ import annotations

import logging

from act_dashboard.ai import (
    claude_subprocess,
    context,
    locks,
    prompt_loader,
)
# TODO Tier 2.2: move _log_error + _ParseError to a shared
# act_dashboard/ai/_db_helpers.py — currently imported from classifier
# which works fine but is smelly cross-module reach.
from act_dashboard.ai.classifier import _ParseError, _log_error
from act_dashboard.ai.prompts import (
    PROMPT_FILE_CHAT,
    PROMPT_VERSION_CHAT,
)

logger = logging.getLogger(__name__)

# Stage 4.5 revised model decision: Opus for both batch + explain + chat.
MODEL_CHAT = 'claude-opus-4-7'

# How many prior chat turns to thread back into the next user message
# for multi-turn memory. Tight on purpose — long histories blow tokens
# fast and the chat panel is a working surface, not a research tool.
HISTORY_TURNS = 8


# ===========================================================================
# Public entry point
# ===========================================================================
def chat(con, client_id: str, flow: str, analysis_date: str,
         message: str, visible_rows: list[dict] | None = None) -> dict:
    """Returns dict matching endpoint response schema.

    visible_rows is the optional snapshot of the current page's rows the
    user is looking at - sent by Stage 9.5 frontend as a list of dicts
    with id/search_term/cost/clicks/conversions/pass1_reason/review_status
    /ai_verdict/ai_confidence/ai_intent_tag. Empty/None means no row
    snapshot was provided (older clients, or page state not yet hydrated)
    and the chat falls back to page-summary counts only.

    May raise locks.LockContentionError (caller -> 409).
    May raise claude_subprocess.ClaudeError after retry (caller -> 502).
    """
    client_lock = locks.get_client_lock(client_id)
    if not client_lock.acquire(blocking=False):
        raise locks.LockContentionError(client_id)

    try:
        # Persist user-message row BEFORE the Claude call so it's
        # preserved on failure (same pattern as explainer.py).
        user_row_id = _insert_chat_user(
            con, client_id, flow, analysis_date, message,
        )

        # Recent history excludes the just-inserted user row + cleared
        # rows (cleared_at IS NULL filter).
        recent = _fetch_recent_history(
            con, client_id, flow, analysis_date,
            limit=HISTORY_TURNS, exclude_id=user_row_id,
        )

        client_ctx = context.get_client_context(con, client_id)
        page_summary = _fetch_page_summary(con, client_id, flow, analysis_date)

        system_prompt = prompt_loader.load_prompt(PROMPT_FILE_CHAT)
        user_message = _build_user_message(
            client_id, flow, analysis_date,
            client_ctx, page_summary, recent, message,
            visible_rows or [],
        )

        # Call Opus (retry once). Empty response counts as a parse
        # failure so the retry kicks in — empty assistant rows are
        # useless and would confuse the UI.
        response_text: str = ''
        usage: dict = {}
        wall_ms = 0
        for attempt in (1, 2):
            try:
                raw, usage, wall_ms = claude_subprocess.run_claude(
                    MODEL_CHAT, system_prompt, user_message,
                )
                response_text = _strip_fences((raw or '').strip())
                if not response_text:
                    raise _ParseError('empty response from model')
                break
            except (claude_subprocess.ClaudeError, _ParseError) as e:
                error_type = getattr(e, 'error_type', 'invalid_json')
                logger.warning(
                    'chat attempt %d failed: client=%s flow=%s '
                    'error_type=%s msg=%s',
                    attempt, client_id, flow, error_type, str(e)[:300],
                )
                if attempt == 2:
                    _log_error(
                        con, client_id, analysis_date, flow,
                        [user_row_id], error_type, str(e),
                        getattr(e, 'raw_output', ''),
                    )
                    if isinstance(e, claude_subprocess.ClaudeError):
                        raise
                    raise claude_subprocess.ClaudeError(
                        'invalid_json', str(e),
                        getattr(e, 'raw_output', ''),
                    ) from e

        assistant_row_id = _insert_chat_assistant(
            con, client_id, flow, analysis_date,
            response_text, MODEL_CHAT, PROMPT_VERSION_CHAT,
            int(usage.get('input_tokens', 0) or 0),
            int(usage.get('output_tokens', 0) or 0),
            wall_ms,
        )

        return {
            'chat_log_id': assistant_row_id,
            'response': response_text,
            'model_version': MODEL_CHAT,
            'tokens_used': (
                int(usage.get('input_tokens', 0) or 0)
                + int(usage.get('output_tokens', 0) or 0)
            ),
            'wall_clock_ms': wall_ms,
        }

    finally:
        client_lock.release()


# ===========================================================================
# Helpers
# ===========================================================================
def _fetch_recent_history(con, client_id: str, flow: str, analysis_date: str,
                           limit: int, exclude_id: int) -> list[dict]:
    """Last N non-cleared messages for this scope, oldest first.
    Excludes the just-inserted user row to avoid the model seeing its
    own current input twice."""
    rows = con.execute(
        """SELECT role, message
             FROM act_v2_ai_chat_log
            WHERE client_id = ? AND flow = ? AND analysis_date = ?
              AND cleared_at IS NULL
              AND id != ?
            ORDER BY created_at DESC
            LIMIT ?""",
        [client_id, flow, analysis_date, exclude_id, limit],
    ).fetchall()
    return [{'role': r[0], 'message': r[1]} for r in reversed(rows)]


def _fetch_page_summary(con, client_id: str, flow: str,
                         analysis_date: str) -> dict:
    """Lightweight {total, pending, approved, rejected} aggregate so the
    chat user message includes a sense of scale + decision split for
    the current view."""
    if flow == 'pass3':
        rows = con.execute(
            """SELECT review_status, COUNT(*)
                 FROM act_v2_phrase_suggestions
                WHERE client_id = ? AND analysis_date = ?
                GROUP BY review_status""",
            [client_id, analysis_date],
        ).fetchall()
    else:
        # 'block' / 'review' suffix in the flow string maps to
        # pass1_status. Search vs PMax distinction would need an extra
        # JOIN to act_v2_search_terms; the chat doesn't need that
        # precision — counts by pass1_status are good enough.
        pass1_status = 'block' if 'block' in flow else 'review'
        rows = con.execute(
            """SELECT review_status, COUNT(*)
                 FROM act_v2_search_term_reviews
                WHERE client_id = ? AND analysis_date = ?
                  AND pass1_status = ?
                GROUP BY review_status""",
            [client_id, analysis_date, pass1_status],
        ).fetchall()

    by_status = {r[0]: r[1] for r in rows}
    return {
        'total': sum(by_status.values()),
        'pending': by_status.get('pending', 0),
        # Approved and Pushed both reflect "user said block" decisions
        # in the negatives-module taxonomy; collapse them for the
        # chat-context summary.
        'approved': by_status.get('approved', 0) + by_status.get('pushed', 0),
        'rejected': by_status.get('rejected', 0),
    }


def _build_user_message(client_id: str, flow: str, analysis_date: str,
                         client_ctx: dict, page_summary: dict,
                         recent: list[dict], message: str,
                         visible_rows: list[dict]) -> str:
    flow_label = {
        'search_block': 'Search > Block',
        'search_review': 'Search > Review',
        'pmax_block': 'PMax > Block',
        'pmax_review': 'PMax > Review',
        'pass3': 'Pass 3 Phrase Suggestions',
    }.get(flow, flow)

    parts: list[str] = []
    parts.append('=== PAGE CONTEXT ===')
    parts.append(f'Client: {client_ctx.get("client_name", "—")} ({client_id})')
    parts.append(f'Flow: {flow_label}')
    parts.append(f'Analysis date: {analysis_date}')
    if page_summary:
        parts.append(
            f'Rows: {page_summary.get("total", "?")} total '
            f'({page_summary.get("pending", 0)} pending, '
            f'{page_summary.get("approved", 0)} approved, '
            f'{page_summary.get("rejected", 0)} rejected)'
        )
    parts.append('')
    parts.append('=== CLIENT CONFIG (relevant excerpts) ===')
    parts.append(
        f'Services advertised: {client_ctx.get("services_advertised_csv", "—")}'
    )
    parts.append(
        f'Services NOT advertised: '
        f'{client_ctx.get("services_not_advertised_csv", "—")}'
    )
    parts.append(f'Brand terms: {client_ctx.get("brand_terms_csv", "—")}')
    parts.append(
        f'Competitor brands: {client_ctx.get("competitor_brands_csv", "—")}'
    )
    parts.append('')
    if recent:
        parts.append('=== RECENT CONVERSATION (oldest first) ===')
        for turn in recent:
            tag = 'USER' if turn['role'] == 'user' else 'ASSISTANT'
            parts.append(f'[{tag}] {turn["message"]}')
        parts.append('')
    if visible_rows:
        # Stage 9.5: snapshot of the rows the user can actually see right
        # now. One line per row keeps the budget bounded (~50 rows ≈
        # 1500 tokens). Only enabled fields the row actually has — empty
        # AI fields are omitted from the line so unclassified rows look
        # cleaner than a row of "/?/?/?".
        parts.append('=== VISIBLE ROWS (current page, top by cost) ===')
        for r in visible_rows:
            cost = r.get('total_cost') or 0
            clicks = r.get('total_clicks') or 0
            convs = r.get('total_conversions') or 0
            ai_part = ''
            if r.get('ai_verdict'):
                ai_part = (
                    f' | AI: {r["ai_verdict"]}'
                    f'/{r.get("ai_confidence", "?")}'
                )
                if r.get('ai_intent_tag'):
                    ai_part += f' ({r["ai_intent_tag"]})'
            status = r.get('review_status') or 'pending'
            try:
                cost_str = f'£{float(cost):.2f}'
            except (TypeError, ValueError):
                cost_str = '£?'
            parts.append(
                f'  [{r.get("id", "?")}] "{r.get("search_term", "?")}" | '
                f'{cost_str} | {clicks} clk | {convs} conv | '
                f'{status}{ai_part}'
            )
        parts.append('')
    parts.append('=== USER MESSAGE ===')
    parts.append(message)

    return '\n'.join(parts)


def _strip_fences(text: str) -> str:
    """Defensive markdown-fence stripping. The chat system prompt says
    'no code fences' but model output drifts; this stays tolerant."""
    if text.startswith('```'):
        first_nl = text.find('\n')
        if first_nl != -1:
            text = text[first_nl + 1:]
        if text.endswith('```'):
            text = text[:-3]
        text = text.strip()
    return text


def _insert_chat_user(con, client_id: str, flow: str, analysis_date: str,
                      message: str) -> int:
    """INSERT user-role row to act_v2_ai_chat_log. Return new row's id."""
    result = con.execute(
        """INSERT INTO act_v2_ai_chat_log
              (client_id, flow, analysis_date, role, message)
           VALUES (?, ?, ?, 'user', ?)
           RETURNING id""",
        [client_id, flow, analysis_date, message],
    ).fetchone()
    return result[0]


def _insert_chat_assistant(con, client_id: str, flow: str, analysis_date: str,
                            message: str,
                            model_version: str, prompt_version: str,
                            tokens_in: int, tokens_out: int,
                            latency_ms: int) -> int:
    """INSERT assistant-role row to act_v2_ai_chat_log. Return new row's id."""
    result = con.execute(
        """INSERT INTO act_v2_ai_chat_log
              (client_id, flow, analysis_date, role, message,
               model_version, prompt_version,
               tokens_in, tokens_out, latency_ms)
           VALUES (?, ?, ?, 'assistant', ?, ?, ?, ?, ?, ?)
           RETURNING id""",
        [
            client_id, flow, analysis_date, message,
            model_version, prompt_version,
            tokens_in, tokens_out, latency_ms,
        ],
    ).fetchone()
    return result[0]
