"""Brief 2.1g — AI Triage feedback loop (Pass 1/2 only).

Two mechanisms, both prompt-only (no model fine-tuning, no embeddings):

  1. Exact-match auto-fill: before any AI call, look up the term's
     normalised text in the user's last-90-days decision history. On a
     single unambiguous match, synthesise an AI-style verdict from the
     historical decision and skip the model call.

  2. Few-shot examples: for novel terms, inject the user's last 30
     decisions (last 30 days) into the AI Triage prompt as examples.

Scope (v1):
  - Pass 1/2 only. Pass 3 has its own loop in pass3_ai.py.
  - DBD-only (`ALLOWED_CLIENTS_V1`).
  - Per-client feature flag `act_v2_clients.enable_ai_feedback_loop`.

ACT terminology reminder — INVERTED from colloquial:
  review_status='approved' = user approved the BLOCK = ai_verdict='approve'
  review_status='rejected' = user rejected the block (keep running) =
                             ai_verdict='reject'
"""
from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)

# DBD-only for v1, same pattern as engine/daily_pipeline.py.
ALLOWED_CLIENTS_V1: set[str] = {'dbd001'}

EXACT_MATCH_DAYS = 90
FEW_SHOT_DAYS = 30
FEW_SHOT_LIMIT = 30

# Synthetic markers persisted on auto-filled rows so downstream UI /
# telemetry can identify them without calling the AI.
HISTORICAL_INTENT_TAG = 'historical_match'
HISTORICAL_MODEL_VERSION = 'historical_match'


# ---------------------------------------------------------------------------
# Feature-flag check
# ---------------------------------------------------------------------------
def is_enabled(con, client_id: str) -> bool:
    """True only if (a) client is in v1 allowlist AND (b) per-client flag
    is set in act_v2_clients.enable_ai_feedback_loop.

    Defensive against the column not existing yet (pre-N9 DBs)."""
    if client_id not in ALLOWED_CLIENTS_V1:
        return False
    try:
        row = con.execute(
            "SELECT COALESCE(enable_ai_feedback_loop, FALSE) "
            "FROM act_v2_clients WHERE client_id = ?",
            [client_id],
        ).fetchone()
    except Exception as e:
        # Column missing on a pre-migration DB — fail closed.
        logger.warning(
            'feedback_loop.is_enabled: column lookup failed (%s); '
            'treating as disabled', e,
        )
        return False
    return bool(row and row[0])


# ---------------------------------------------------------------------------
# Term normalisation
# ---------------------------------------------------------------------------
_WS_RE = re.compile(r'\s+')
_PUNCT_RE = re.compile(r'[^\w\s]+', re.UNICODE)


def normalise_term(term: str) -> str:
    """Lowercase, strip punctuation, collapse whitespace."""
    if not term:
        return ''
    s = term.lower().strip()
    s = _PUNCT_RE.sub(' ', s)
    s = _WS_RE.sub(' ', s).strip()
    return s


# ---------------------------------------------------------------------------
# Mechanism 1 — exact-match auto-fill
# ---------------------------------------------------------------------------
def get_exact_match_decision(con, client_id: str, term: str,
                              days: int = EXACT_MATCH_DAYS) -> dict | None:
    """Look up the user's recent decision history for `term`.

    Returns:
      - dict {'verdict': 'approve'|'reject', 'last_decided_at': ts,
              'match_count': N} on a single-direction match
      - None if no match, or if approved-and-rejected both exist
        (conflict — fall through to AI)

    `verdict` uses AI vocabulary (approve/reject), not review_status.
    """
    norm = normalise_term(term)
    if not norm:
        return None

    rows = con.execute(
        f"""SELECT review_status, MAX(reviewed_at), COUNT(*)
              FROM act_v2_search_term_reviews
             WHERE client_id = ?
               AND review_status IN ('approved', 'rejected')
               AND reviewed_at IS NOT NULL
               AND reviewed_at >= now() - INTERVAL '{int(days)} days'
               AND lower(trim(search_term)) = ?
             GROUP BY review_status""",
        [client_id, norm.lower()],
    ).fetchall()

    if not rows:
        # Fallback: normalised match (strip punctuation). The trim-only
        # version above catches the common case fast via index on raw
        # search_term; this catches "implants, london" vs "implants london".
        rows = con.execute(
            f"""SELECT review_status, MAX(reviewed_at), COUNT(*)
                  FROM act_v2_search_term_reviews
                 WHERE client_id = ?
                   AND review_status IN ('approved', 'rejected')
                   AND reviewed_at IS NOT NULL
                   AND reviewed_at >= now() - INTERVAL '{int(days)} days'
                   AND regexp_replace(lower(trim(search_term)),
                                      '[^a-z0-9 ]+', ' ', 'g') = ?
                 GROUP BY review_status""",
            [client_id, norm],
        ).fetchall()

    if not rows:
        return None

    by_status = {r[0]: (r[1], r[2]) for r in rows}
    has_approve = 'approved' in by_status
    has_reject = 'rejected' in by_status

    if has_approve and has_reject:
        # Conflict — let the AI sort it out with few-shot context.
        return None
    if has_approve:
        ts, n = by_status['approved']
        return {'verdict': 'approve', 'last_decided_at': ts, 'match_count': n}
    if has_reject:
        ts, n = by_status['rejected']
        return {'verdict': 'reject', 'last_decided_at': ts, 'match_count': n}
    return None


def build_historical_match_payload(verdict: str, match_count: int) -> dict:
    """Shape a `parsed_item` look-alike for the classifier persistence
    layer, so auto-fill writes through the same INSERT path as AI rows."""
    return {
        'ai_verdict': verdict,
        'ai_confidence': 'high',
        'ai_reasoning': (
            f"Auto-filled from {match_count} historical user decision(s) "
            f"on this exact term within the last {EXACT_MATCH_DAYS} days. "
            "AI model was not called."
        ),
        'ai_intent_tag': HISTORICAL_INTENT_TAG,
    }


# ---------------------------------------------------------------------------
# Mechanism 2 — few-shot examples
# ---------------------------------------------------------------------------
def get_recent_decisions(con, client_id: str,
                          limit: int = FEW_SHOT_LIMIT,
                          days: int = FEW_SHOT_DAYS) -> list[dict]:
    """Return up to `limit` most-recent user decisions in the last `days`,
    most-recent first. Used as few-shot examples for novel terms."""
    rows = con.execute(
        f"""SELECT search_term, review_status, reviewed_at, pass1_reason
              FROM act_v2_search_term_reviews
             WHERE client_id = ?
               AND review_status IN ('approved', 'rejected')
               AND reviewed_at IS NOT NULL
               AND reviewed_at >= now() - INTERVAL '{int(days)} days'
               AND search_term IS NOT NULL
             ORDER BY reviewed_at DESC
             LIMIT ?""",
        [client_id, int(limit)],
    ).fetchall()

    out: list[dict] = []
    for term, status, ts, p1r in rows:
        # Map review_status → ACT-terminology verb for the prompt.
        verdict = 'BLOCK' if status == 'approved' else 'DON\'T BLOCK'
        out.append({
            'search_term': term,
            'verdict': verdict,
            'decided_at': ts,
            'pass1_reason': p1r,
        })
    return out


def render_few_shot_block(examples: list[dict]) -> str:
    """Render few-shot examples into a prompt-friendly block. Empty string
    when no examples — caller can substitute it directly without an `if`."""
    if not examples:
        return ''
    lines = [
        '==========================================================================',
        'USER\'S RECENT DECISIONS ON THIS ACCOUNT '
        f'(last {FEW_SHOT_DAYS} days, most recent first)',
        '==========================================================================',
        '',
        'Apply consistent judgement — these are your reference for the '
        'user\'s style on novel terms.',
        '',
    ]
    for ex in examples:
        ts = ex['decided_at']
        try:
            date_str = ts.strftime('%Y-%m-%d') if hasattr(ts, 'strftime') else str(ts)[:10]
        except Exception:
            date_str = str(ts)[:10]
        reason = ex.get('pass1_reason') or '—'
        lines.append(
            f'  [{date_str}] "{ex["search_term"]}" → {ex["verdict"]} '
            f'(pass1_reason: {reason})'
        )
    lines.append('')
    return '\n'.join(lines)
