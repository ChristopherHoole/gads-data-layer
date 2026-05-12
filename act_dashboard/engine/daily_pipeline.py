"""Section 7 (12 May 2026) — Daily pipeline orchestrator.

Runs the full Pass 1 → Pass 2 → Pass 3 chain for one client/day in
sequence. Triggered by data-ingest hooks (PMax CSV watcher today,
Search API ingest later), NOT by the overnight scheduler — this is
an event-driven path layered on top of stage-level idempotency.

Per-stage idempotency:
  Each stage checks act_v2_scheduler_runs for a successful run today
  for this client. If found, the stage is logged as 'skipped' and
  the function moves on. This means re-dropping the same CSV the
  same day does NOT double-charge Opus or duplicate phrase_suggestions.

Fail-fast:
  If a stage fails, downstream stages do NOT run (each stage assumes
  upstream success — e.g. Pass 3 needs Pass 1+2 results to be sensible).
  Stage failure is logged to act_v2_scheduler_runs with status='failed'
  and surfaced in the function's return value.

Manual overrides:
  The /reclassify-now endpoint and the Run Pass 3 button both force
  re-runs — they do NOT consult this idempotency check. User intent
  takes precedence over auto-throttle.

DBD-only for v1:
  The hook only fires for client_id 'dbd001'. Other clients will get
  the hook in a follow-up section once their daily ingest path exists.
  Guard sits at the top of run_daily_pipeline — easy to remove.

Phase labels (must match act_v2_scheduler_runs.phase CHECK constraint;
see migrate_fix12_scheduler_phase_check.py — widened set is
ingestion / engine / neg_sticky_expiry / neg_stale_cleanup /
neg_pass1 / neg_pass2 / neg_pass3):
  - 'neg_stale_cleanup'  → expire prior-date pending reviews
  - 'neg_pass1'          → classifier (block / review / keep)
  - 'neg_pass2'          → route block rows to target lists
  - 'neg_pass3'          → AI Pass 3 (engine/pass3_ai.py)
"""
from __future__ import annotations

import json
import logging
import os
import time
from datetime import date as _date

import duckdb

logger = logging.getLogger('act_v2_daily_pipeline')
logger.setLevel(logging.INFO)
if not logger.handlers:
    h = logging.StreamHandler()
    h.setFormatter(logging.Formatter(
        '%(asctime)s [%(levelname)s] [daily_pipeline] %(message)s'))
    logger.addHandler(h)

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..'))
DB_PATH = os.path.join(PROJECT_ROOT, 'warehouse.duckdb')

# Section 7 v1 scope: only DBD's pipeline auto-fires today. Other clients
# will be enrolled in a follow-up section once their daily ingest path
# exists. Easy to remove by deleting this constant + the guard.
ALLOWED_CLIENTS_V1 = {'dbd001'}


def _has_success_today(con, client_id: str, run_date: _date, phase: str) -> bool:
    """Idempotency check — has this stage already succeeded today?"""
    row = con.execute(
        """SELECT 1 FROM act_v2_scheduler_runs
           WHERE client_id = ? AND run_date = ?
             AND phase = ? AND status = 'success'
           LIMIT 1""",
        [client_id, run_date, phase],
    ).fetchone()
    return bool(row)


def _start_run(con, client_id: str, run_date: _date, phase: str) -> int:
    row = con.execute(
        """INSERT INTO act_v2_scheduler_runs
           (client_id, run_date, phase, status, started_at)
           VALUES (?, ?, ?, 'running', CURRENT_TIMESTAMP)
           RETURNING run_id""",
        [client_id, run_date, phase],
    ).fetchone()
    return row[0] if row else 0


def _end_run(con, run_id: int, status: str,
             error_message: str | None = None,
             details: dict | None = None) -> None:
    con.execute(
        """UPDATE act_v2_scheduler_runs
           SET status = ?, completed_at = CURRENT_TIMESTAMP,
               error_message = ?, details_json = ?
           WHERE run_id = ?""",
        [status, (error_message or None),
         json.dumps(details) if details else None,
         run_id],
    )


def _log_skip(con, client_id: str, run_date: _date, phase: str) -> None:
    """Write a 'skipped' row when idempotency check fires. Keeps the
    audit trail honest — every run attempt is recorded, even no-ops."""
    con.execute(
        """INSERT INTO act_v2_scheduler_runs
           (client_id, run_date, phase, status, started_at, completed_at,
            error_message)
           VALUES (?, ?, ?, 'skipped', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
                   'already_run_today')""",
        [client_id, run_date, phase],
    )


# ---------------------------------------------------------------------------
# Stage runners — thin shims around existing entry points. Each returns
# (ok: bool, details: dict | None, error: str | None).
# ---------------------------------------------------------------------------
def _run_stale_cleanup(client_id: str) -> tuple[bool, dict | None, str | None]:
    con = duckdb.connect(DB_PATH)
    try:
        n = con.execute(
            """UPDATE act_v2_search_term_reviews
               SET review_status = 'expired'
               WHERE client_id = ?
                 AND review_status = 'pending'
                 AND analysis_date < CURRENT_DATE""",
            [client_id],
        ).fetchone()
        return True, {'expired': int(n[0]) if n else 0}, None
    except Exception as e:  # noqa: BLE001
        return False, None, str(e)[:500]
    finally:
        con.close()


def _run_pass1(client_id: str) -> tuple[bool, dict | None, str | None]:
    try:
        from act_dashboard.engine.negatives.pass1 import run_pass1
        summary = run_pass1(client_id, DB_PATH, _date.today())
        return True, summary, None
    except Exception as e:  # noqa: BLE001
        return False, None, str(e)[:500]


def _run_pass2(client_id: str) -> tuple[bool, dict | None, str | None]:
    try:
        from act_dashboard.engine.negatives.pass2 import run_pass2
        summary = run_pass2(client_id, DB_PATH, _date.today())
        return True, summary, None
    except Exception as e:  # noqa: BLE001
        return False, None, str(e)[:500]


def _run_pass3_ai(client_id: str) -> tuple[bool, dict | None, str | None]:
    """Pass 3 AI uses a different invocation style than Pass 1+2 — it
    takes an open connection rather than a DB_PATH, and runs via the
    engine/pass3_ai.py orchestrator. We open a dedicated connection
    here, hand it over, and close after."""
    try:
        from act_dashboard.engine.pass3_ai import run_pass3_ai
        con = duckdb.connect(DB_PATH)
        try:
            result = run_pass3_ai(con, client_id, _date.today().isoformat())
        finally:
            con.close()
        # Cheap shape — full result has tokens/cost/themes which are
        # fine to persist in details_json for diagnostics.
        details = {
            'suggestions_created': result.get('suggestions_created'),
            'themes_count': len(result.get('themes') or []),
            'tokens_in': result.get('tokens_in'),
            'tokens_out': result.get('tokens_out'),
            'cost_usd': result.get('cost_usd'),
            'wall_clock_ms': result.get('wall_clock_ms'),
        }
        return True, details, None
    except Exception as e:  # noqa: BLE001
        return False, None, str(e)[:500]


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------
STAGES: tuple[tuple[str, callable], ...] = (
    ('neg_stale_cleanup', _run_stale_cleanup),
    ('neg_pass1',         _run_pass1),
    ('neg_pass2',         _run_pass2),
    ('neg_pass3',         _run_pass3_ai),
)


def run_daily_pipeline(client_id: str) -> dict:
    """Chain neg_stale_cleanup → pass1 → pass2 → pass3_ai for one client.

    Returns {stages: [{name, status, duration_ms, error}], overall}.
    overall ∈ {'success', 'partial', 'failed', 'skipped'}.
    """
    if client_id not in ALLOWED_CLIENTS_V1:
        logger.info('skipped (not in v1 allowlist): client=%s', client_id)
        return {'overall': 'skipped',
                'reason': f'client_id {client_id!r} not in v1 allowlist',
                'stages': []}

    run_date = _date.today()
    stage_results: list[dict] = []
    abort = False

    for phase, runner in STAGES:
        if abort:
            stage_results.append({'name': phase, 'status': 'not_run',
                                  'duration_ms': 0, 'error': None})
            continue

        # Idempotency check on its own connection (don't hold across the
        # long-running stage call).
        con = duckdb.connect(DB_PATH)
        try:
            if _has_success_today(con, client_id, run_date, phase):
                _log_skip(con, client_id, run_date, phase)
                logger.info('skip %s: already_run_today (client=%s)',
                            phase, client_id)
                stage_results.append({'name': phase, 'status': 'skipped',
                                      'duration_ms': 0, 'error': None})
                continue
            run_id = _start_run(con, client_id, run_date, phase)
        finally:
            con.close()

        t0 = time.monotonic()
        ok, details, error = runner(client_id)
        dur_ms = int((time.monotonic() - t0) * 1000)

        con = duckdb.connect(DB_PATH)
        try:
            _end_run(con, run_id,
                     'success' if ok else 'failed',
                     error_message=error, details=details)
        finally:
            con.close()

        stage_results.append({
            'name': phase,
            'status': 'success' if ok else 'failed',
            'duration_ms': dur_ms,
            'error': error,
        })

        if ok:
            logger.info('ok %s in %dms (client=%s)', phase, dur_ms, client_id)
        else:
            logger.error('FAILED %s after %dms (client=%s): %s',
                         phase, dur_ms, client_id, error)
            # Downstream stages assume upstream success — abort the chain.
            abort = True

    # Overall: success if all four passed (or were idempotency-skipped);
    # failed if NONE ran successfully; partial otherwise.
    ran_ok = sum(1 for s in stage_results if s['status'] in ('success', 'skipped'))
    if abort and ran_ok < len(STAGES):
        overall = 'partial' if ran_ok > 0 else 'failed'
    else:
        overall = 'success'

    logger.info('pipeline %s for client=%s: %s',
                overall, client_id,
                ', '.join(f"{s['name']}={s['status']}" for s in stage_results))
    return {'overall': overall, 'stages': stage_results}
