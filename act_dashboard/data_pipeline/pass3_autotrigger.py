"""Tier 2.1 Part C - 2-minute debounce auto-trigger for the daily pipeline
(which includes Pass 3) after a PMax CSV ingest.

Pattern:
  - schedule(client_id) is called from the PMax CSV watcher right after
    a successful ingest+archive.
  - The first call starts a 2-minute timer; subsequent calls for the
    same client within that window RESET the timer (so back-to-back
    CSVs coalesce into a single pipeline run).
  - When the timer fires, run_daily_pipeline(client_id) is invoked on
    a daemon thread. A single scheduler_runs row with phase
    'pass3_ai_autotrigger' wraps the entire call so the audit trail
    distinguishes "Pass 3 fired because of a CSV drop" from "Pass 3
    fired on the overnight cycle".
  - DBD-only via ALLOWED_CLIENTS_V1; other clients are no-op'd.

This module replaces the immediate fire-and-forget run_daily_pipeline
call that lived inline in pmax_csv_watcher.process_file - the watcher
now calls schedule() and returns.

Idempotency:
  - Daily-pipeline stage-level idempotency (act_v2_scheduler_runs lookup
    inside run_daily_pipeline) still applies. The autotrigger does NOT
    replicate that logic - if a CSV drops AFTER the overnight cycle has
    already run today's Pass 3, the inner stages will be 'skipped' and
    the autotrigger row will still record the wrapper call.
"""
from __future__ import annotations

import json
import logging
import threading
import time
from datetime import date as _date
from typing import Dict

import duckdb

# Reuse daily_pipeline's ALLOWED_CLIENTS_V1 + DB_PATH so the guard
# matches the rest of the auto-trigger chain.
from act_dashboard.engine.daily_pipeline import ALLOWED_CLIENTS_V1, DB_PATH

logger = logging.getLogger('pass3_autotrigger')
logger.setLevel(logging.INFO)
if not logger.handlers:
    h = logging.StreamHandler()
    h.setFormatter(logging.Formatter(
        '%(asctime)s [%(levelname)s] [pass3_autotrigger] %(message)s'))
    logger.addHandler(h)

DEBOUNCE_SECONDS = 120  # 2 minutes per the brief

# Per-client timer + lock so a second CSV resets the same client's
# countdown without racing the firing path.
_timers: Dict[str, threading.Timer] = {}
_lock = threading.Lock()


def _log_run(client_id: str, status: str,
             started_at: float, error: str | None = None,
             details: dict | None = None) -> None:
    """Write one act_v2_scheduler_runs row under phase pass3_ai_autotrigger."""
    try:
        con = duckdb.connect(DB_PATH)
    except duckdb.IOException as e:
        logger.error('DB locked, cannot log autotrigger run: %s', e)
        return
    try:
        completed = 'CURRENT_TIMESTAMP' if status != 'running' else 'NULL'
        # Inline the timestamp expression because DuckDB's parameter
        # binding for TIMESTAMP NULL is fiddly across versions.
        con.execute(
            f"""INSERT INTO act_v2_scheduler_runs
               (client_id, run_date, phase, status, started_at,
                completed_at, error_message, details_json)
               VALUES (?, ?, 'pass3_ai_autotrigger', ?, ?, {completed}, ?, ?)""",
            [
                client_id, _date.today(), status,
                # started_at = timestamp at scheduling time (so a long
                # debounce is visible in the audit trail) when running;
                # CURRENT_TIMESTAMP otherwise.
                # We pass an ISO string DuckDB will cast.
                _isoformat_unix(started_at),
                error,
                json.dumps(details) if details else None,
            ],
        )
    except Exception:  # noqa: BLE001
        logger.exception('Failed to write pass3_ai_autotrigger row')
    finally:
        con.close()


def _isoformat_unix(ts: float) -> str:
    from datetime import datetime
    return datetime.fromtimestamp(ts).isoformat(timespec='seconds')


def _fire(client_id: str, scheduled_at: float) -> None:
    """Timer callback. Runs run_daily_pipeline on this thread (the
    Timer's own daemon thread) and wraps it in a single
    pass3_ai_autotrigger scheduler_runs row."""
    try:
        from act_dashboard.engine.daily_pipeline import run_daily_pipeline
    except Exception:  # noqa: BLE001
        logger.exception('Import failed for run_daily_pipeline')
        return

    logger.info('firing daily_pipeline for %s (scheduled %.0fs ago)',
                client_id, time.time() - scheduled_at)

    result: dict = {}
    try:
        result = run_daily_pipeline(client_id) or {}
    except Exception as e:  # noqa: BLE001
        logger.exception('daily_pipeline crashed for %s: %s', client_id, e)
        _log_run(
            client_id, 'failed',
            started_at=scheduled_at,
            error=f'daily_pipeline crashed: {str(e)[:200]}',
        )
        _clear_timer(client_id)
        return

    overall = result.get('overall')
    status = 'success' if overall in ('success', 'partial', 'skipped') else 'failed'
    err = None if status == 'success' else (
        result.get('halt_reason')
        or (result.get('stages') and ', '.join(
            f"{s.get('name')}={s.get('status')}" for s in result['stages']))
        or 'unknown'
    )
    _log_run(
        client_id, status,
        started_at=scheduled_at,
        error=err,
        details={
            'overall': overall,
            'stages': result.get('stages'),
            'reason': result.get('reason'),
        },
    )
    _clear_timer(client_id)


def _clear_timer(client_id: str) -> None:
    with _lock:
        _timers.pop(client_id, None)


def schedule(client_id: str) -> str:
    """Public entry point. Called from the PMax CSV watcher after a
    successful ingest+archive. Returns a short status string for the
    caller's log line.

    Behaviour:
      - DBD-only v1 (ALLOWED_CLIENTS_V1 guard).
      - First call for a client: starts a DEBOUNCE_SECONDS timer.
      - Subsequent call for the SAME client within the window: cancels
        the prior timer and starts a fresh one (debounce).
      - Other clients can have their own timers running in parallel.
    """
    if client_id not in ALLOWED_CLIENTS_V1:
        logger.info('skip (not in allowlist): client=%s', client_id)
        return 'skipped (not in v1 allowlist)'

    scheduled_at = time.time()
    with _lock:
        prev = _timers.pop(client_id, None)
        if prev is not None:
            prev.cancel()
            logger.info(
                'debounce: cancelled prior timer for %s (window was %ds)',
                client_id, DEBOUNCE_SECONDS,
            )
        t = threading.Timer(
            DEBOUNCE_SECONDS,
            _fire,
            args=(client_id, scheduled_at),
        )
        t.daemon = True
        t.name = f'pass3-autotrigger-{client_id}'
        t.start()
        _timers[client_id] = t

    logger.info(
        'scheduled daily_pipeline for %s in %ds',
        client_id, DEBOUNCE_SECONDS,
    )
    return 'scheduled'


def cancel(client_id: str) -> bool:
    """Test hook: cancel a pending timer if one exists. Returns True if
    a timer was cancelled."""
    with _lock:
        t = _timers.pop(client_id, None)
    if t is None:
        return False
    t.cancel()
    logger.info('cancelled timer for %s', client_id)
    return True


def is_scheduled(client_id: str) -> bool:
    """Test hook: True if a debounce timer is currently armed for the
    client."""
    with _lock:
        return client_id in _timers
