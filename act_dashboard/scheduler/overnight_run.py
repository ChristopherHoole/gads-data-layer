"""
ACT v2 Overnight Scheduler — Standalone Script

Runs the overnight cycle for all active clients:
1. For each client in act_v2_clients WHERE active = TRUE:
   - Phase 1: Ingest yesterday's Google Ads data
   - Phase 2: Run enabled engine levels

Writes per-client, per-phase status to act_v2_scheduler_runs.

Design:
- Standalone script, NOT a Flask thread (survives deployments, cron-friendly)
- Trigger externally: Windows Task Scheduler locally, cron in production
- Idempotent: if today already has a successful run, exits cleanly
- Per-client error isolation: one client's failure doesn't block others
- Short-lived DB connections only (each ingestion + engine opens its own)

Usage (from project root):
    # Run for yesterday (default):
    python -m act_dashboard.scheduler.overnight_run

    # Run for a specific date:
    python -m act_dashboard.scheduler.overnight_run --date 2026-04-17

    # Force re-run even if today already succeeded:
    python -m act_dashboard.scheduler.overnight_run --force

Prerequisites:
    - Flask app must be STOPPED (DuckDB lock for ingestion + engine)
    - Google Ads credentials configured in secrets/google-ads.yaml

Logs to: act_dashboard/scheduler/overnight.log (append mode)
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import duckdb

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
DB_PATH = str(PROJECT_ROOT / "warehouse.duckdb")
LOG_PATH = str(SCRIPT_DIR / "overnight.log")

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logger = logging.getLogger('act_v2_overnight')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')

if not logger.handlers:
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    file_handler = logging.FileHandler(LOG_PATH, mode='a', encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


# ---------------------------------------------------------------------------
# Status tracking helpers (short-lived DB connections)
# ---------------------------------------------------------------------------
def _write_status_start(client_id, run_date, phase):
    """Write a 'running' row. Returns run_id for later update."""
    con = duckdb.connect(DB_PATH)
    try:
        row = con.execute(
            """INSERT INTO act_v2_scheduler_runs
               (client_id, run_date, phase, status, started_at)
               VALUES (?, ?, ?, 'running', CURRENT_TIMESTAMP)
               RETURNING run_id""",
            [client_id, run_date, phase]
        ).fetchone()
        return row[0] if row else None
    finally:
        con.close()


def _write_status_end(run_id, status, error_message=None, details=None):
    """Update a run row with final status."""
    con = duckdb.connect(DB_PATH)
    try:
        con.execute(
            """UPDATE act_v2_scheduler_runs
               SET status = ?, completed_at = CURRENT_TIMESTAMP,
                   error_message = ?, details_json = ?
               WHERE run_id = ?""",
            [status, error_message,
             json.dumps(details) if details else None,
             run_id]
        )
    finally:
        con.close()


def _check_today_succeeded():
    """Check if ALL active clients have successful runs for both phases
    started on the current calendar day (idempotent re-run protection)."""
    con = duckdb.connect(DB_PATH, read_only=True)
    try:
        active_clients = con.execute(
            "SELECT client_id FROM act_v2_clients WHERE active = TRUE"
        ).fetchall()
        if not active_clients:
            return False

        for (cid,) in active_clients:
            for phase in ('ingestion', 'engine'):
                # Filter by started_at calendar day (not run_date, which is eval_date)
                row = con.execute(
                    """SELECT status FROM act_v2_scheduler_runs
                       WHERE client_id = ? AND phase = ?
                       AND CAST(started_at AS DATE) = CURRENT_DATE
                       ORDER BY started_at DESC LIMIT 1""",
                    [cid, phase]
                ).fetchone()
                if not row or row[0] != 'success':
                    return False
        return True
    finally:
        con.close()


def _get_active_clients():
    """Return list of active clients: [{client_id, client_name, customer_id}]."""
    con = duckdb.connect(DB_PATH, read_only=True)
    try:
        rows = con.execute(
            """SELECT client_id, client_name, google_ads_customer_id
               FROM act_v2_clients
               WHERE active = TRUE
               ORDER BY client_id"""
        ).fetchall()
        return [{'client_id': r[0], 'client_name': r[1], 'customer_id': r[2]}
                for r in rows]
    finally:
        con.close()


def _get_enabled_levels(client_id):
    """Return list of levels that are monitor_only or active for this client."""
    con = duckdb.connect(DB_PATH, read_only=True)
    try:
        rows = con.execute(
            """SELECT level, state FROM act_v2_client_level_state
               WHERE client_id = ? AND state IN ('monitor_only', 'active')""",
            [client_id]
        ).fetchall()
        return [r[0] for r in rows]
    finally:
        con.close()


# ---------------------------------------------------------------------------
# Phase runners — each calls existing module entry points
# ---------------------------------------------------------------------------
def run_ingestion_phase(client, eval_date):
    """Run data ingestion for a single client. Returns (success: bool, error: str, details: dict)."""
    from act_dashboard.data_pipeline.google_ads_ingestion import GoogleAdsDataPipeline

    logger.info(f"  [INGESTION] {client['client_name']} ({client['client_id']}) for {eval_date}")
    pipeline = GoogleAdsDataPipeline(client['client_id'], client['customer_id'])
    try:
        result = pipeline.ingest_date(eval_date)
        details = {'campaigns': result.get('campaigns', 0),
                   'ad_groups': result.get('ad_groups', 0),
                   'keywords': result.get('keywords', 0),
                   'ads': result.get('ads', 0),
                   'search_terms': result.get('search_terms', 0),
                   'segments': result.get('segments', 0)}
        logger.info(f"  [INGESTION] Success: {details}")
        return True, None, details
    except Exception as e:
        err_msg = str(e)[:500]
        logger.error(f"  [INGESTION] Failed for {client['client_id']}: {err_msg}")
        return False, err_msg, None
    finally:
        pipeline.close()


def run_neg_sticky_expiry_phase(client, eval_date):
    """N3 Part A: flip sticky rejections whose expires_at has passed into
    the 'auto_expired' state so Rule 0 stops blocking them. Runs BEFORE
    Pass 1 so the cfg load picks up the updated active set.
    """
    con = duckdb.connect(DB_PATH)
    try:
        n = con.execute(
            """UPDATE act_v2_sticky_rejections
               SET unrejected_at = CURRENT_TIMESTAMP,
                   unrejected_reason = 'auto_expired'
               WHERE client_id = ?
                 AND expires_at <= CURRENT_TIMESTAMP
                 AND unrejected_at IS NULL""",
            [client['client_id']],
        ).fetchone()
        expired = int(n[0]) if n else 0
        logger.info(f"  [NEG-STICKY-EXPIRY] {client['client_name']}: expired {expired} stickies")
        return True, None, {'expired': expired}
    except Exception as e:
        err = str(e)[:500]
        logger.error(f"  [NEG-STICKY-EXPIRY] Failed: {err}")
        return False, err, None
    finally:
        con.close()


def run_neg_stale_cleanup_phase(client, eval_date):
    """Expire any PRIOR-DATE pending search-term reviews for this client.

    Edge-case: only rows with analysis_date < today get expired, so a same-day
    re-run of the scheduler leaves today's freshly-written pending rows alone
    and just lets Pass 1 DELETE+re-INSERT them.

    Returns (ok, err, details).
    """
    con = duckdb.connect(DB_PATH)
    try:
        n = con.execute(
            """UPDATE act_v2_search_term_reviews
               SET review_status = 'expired'
               WHERE client_id = ?
                 AND review_status = 'pending'
                 AND analysis_date < CURRENT_DATE""",
            [client['client_id']],
        ).fetchone()
        # DuckDB UPDATE returns a (rowcount,) tuple
        expired = int(n[0]) if n else 0
        logger.info(f"  [NEG-CLEAN] {client['client_name']}: expired {expired} prior-date pending rows")
        return True, None, {'expired': expired}
    except Exception as e:
        err = str(e)[:500]
        logger.error(f"  [NEG-CLEAN] Failed: {err}")
        return False, err, None
    finally:
        con.close()


def run_neg_pass1_phase(client, eval_date):
    """Pass 1 classifier for today's search terms (analysis_date = today)."""
    from datetime import date as _date
    from act_dashboard.engine.negatives.pass1 import run_pass1
    try:
        summary = run_pass1(client['client_id'], DB_PATH, _date.today())
        logger.info(
            f"  [NEG-PASS1] {client['client_name']}: "
            f"{summary['terms_classified']} terms, "
            f"status={summary['status_counts']}, configured={summary['configured']}"
        )
        return True, None, summary
    except Exception as e:
        err = str(e)[:500]
        logger.error(f"  [NEG-PASS1] Failed: {err}")
        return False, err, None


def run_neg_pass2_phase(client, eval_date):
    """Pass 2 routing (target list_role) for today's block rows."""
    from datetime import date as _date
    from act_dashboard.engine.negatives.pass2 import run_pass2
    try:
        summary = run_pass2(client['client_id'], DB_PATH, _date.today())
        logger.info(
            f"  [NEG-PASS2] {client['client_name']}: "
            f"routed {summary['routed']} blocks"
        )
        return True, None, summary
    except Exception as e:
        err = str(e)[:500]
        logger.error(f"  [NEG-PASS2] Failed: {err}")
        return False, err, None


def run_engine_phase(client, eval_date):
    """Run all enabled engine levels for a single client."""
    enabled = _get_enabled_levels(client['client_id'])
    if not enabled:
        logger.info(f"  [ENGINE] {client['client_name']}: no levels enabled, skipping")
        return True, None, {'skipped': 'no_levels_enabled'}

    logger.info(f"  [ENGINE] {client['client_name']} — running levels: {enabled}")
    details = {}

    # Currently only Account Level exists (B1). Campaign/Keyword/Ad/Shopping come later.
    if 'account' in enabled:
        from act_dashboard.engine.account_level import AccountLevelEngine
        engine = AccountLevelEngine(client['client_id'])
        try:
            result = engine.run(eval_date)
            details['account'] = result
            logger.info(f"  [ENGINE] Account: {result}")
        except Exception as e:
            err_msg = str(e)[:500]
            logger.error(f"  [ENGINE] Account failed: {err_msg}")
            return False, f"account level: {err_msg}", details
        finally:
            engine.close()

    # Future: campaign, ad_group, keyword, ad, shopping engines plug in here
    for future_level in ['campaign', 'ad_group', 'keyword', 'ad', 'shopping']:
        if future_level in enabled:
            logger.info(f"  [ENGINE] {future_level}: engine not yet built (will come in C1+)")
            details[future_level] = 'not_yet_implemented'

    return True, None, details


# ---------------------------------------------------------------------------
# Per-client orchestration
# ---------------------------------------------------------------------------
def run_client_cycle(client, eval_date):
    """Run ingestion + engine for one client. Returns dict summary."""
    logger.info(f"--- {client['client_name']} ({client['client_id']}) ---")
    summary = {'client_id': client['client_id'],
               'client_name': client['client_name'],
               'ingestion_status': None,
               'engine_status': None}

    # Phase 1: Ingestion
    run_id = _write_status_start(client['client_id'], eval_date, 'ingestion')
    try:
        ok, err, details = run_ingestion_phase(client, eval_date)
    except Exception as e:
        ok, err, details = False, str(e)[:500], None
    status = 'success' if ok else 'failed'
    _write_status_end(run_id, status, err, details)
    summary['ingestion_status'] = status

    if not ok:
        logger.warning(f"  Skipping engine phase for {client['client_id']} because ingestion failed")
        summary['engine_status'] = 'skipped'
        # Write a skipped row for engine phase so F2 can show the status
        eng_run_id = _write_status_start(client['client_id'], eval_date, 'engine')
        _write_status_end(eng_run_id, 'skipped', 'ingestion_failed', None)
        return summary

    # Phase 2: Engine
    run_id = _write_status_start(client['client_id'], eval_date, 'engine')
    try:
        ok, err, details = run_engine_phase(client, eval_date)
    except Exception as e:
        ok, err, details = False, str(e)[:500], None
    status = 'success' if ok else 'failed'
    _write_status_end(run_id, status, err, details)
    summary['engine_status'] = status

    # -------------------------------------------------------------------
    # N1b — Negatives engine phases (run regardless of engine status;
    # classification depends only on the data just ingested).
    # -------------------------------------------------------------------
    for phase_name, runner, key in (
        # N3: sticky expiry must run BEFORE pass1 so the cfg load sees the
        # freshly-unrejected set and re-classifies those terms normally.
        ('neg_sticky_expiry', run_neg_sticky_expiry_phase, 'neg_sticky_expiry_status'),
        ('neg_stale_cleanup', run_neg_stale_cleanup_phase, 'neg_stale_cleanup_status'),
        ('neg_pass1',         run_neg_pass1_phase,          'neg_pass1_status'),
        ('neg_pass2',         run_neg_pass2_phase,          'neg_pass2_status'),
    ):
        run_id = _write_status_start(client['client_id'], eval_date, phase_name)
        try:
            ok_n, err_n, details_n = runner(client, eval_date)
        except Exception as e:
            ok_n, err_n, details_n = False, str(e)[:500], None
        _write_status_end(run_id,
                          'success' if ok_n else 'failed',
                          err_n, details_n)
        summary[key] = 'success' if ok_n else 'failed'

    return summary


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description='ACT v2 Overnight Scheduler')
    parser.add_argument('--date', help='Evaluation date YYYY-MM-DD (default: yesterday)')
    parser.add_argument('--force', action='store_true',
                        help='Force run even if today already succeeded')
    parser.add_argument('--client', help='Run only for this client_id (e.g. dbd001). '
                                         'Still records to act_v2_scheduler_runs; other '
                                         "clients' runs for today aren't touched.")
    args = parser.parse_args()

    eval_date = args.date or (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    today = datetime.now().strftime('%Y-%m-%d')

    logger.info('=' * 60)
    logger.info(f'ACT v2 OVERNIGHT RUN — {today}')
    logger.info(f'Evaluation date: {eval_date}')
    logger.info('=' * 60)

    # Idempotent re-run protection (skip when --client is set: the caller
    # is being explicit about wanting this client run again).
    if not args.force and not args.client and _check_today_succeeded():
        logger.info('All active clients already have successful runs today. Exiting.')
        logger.info('(Use --force to re-run anyway.)')
        return 0

    t0 = time.time()
    clients = _get_active_clients()
    if not clients:
        logger.warning('No active clients found. Exiting.')
        return 0

    if args.client:
        clients = [c for c in clients if c['client_id'] == args.client]
        if not clients:
            logger.error(f"No active client with client_id={args.client!r}. Exiting.")
            return 1
        logger.info(f'Single-client mode: {args.client}')

    logger.info(f'Active clients: {len(clients)}')
    summaries = []

    for client in clients:
        try:
            summaries.append(run_client_cycle(client, eval_date))
        except Exception as e:
            # Last-resort safety net — per-client error isolation
            logger.error(f'FATAL cycle error for {client["client_id"]}: {e}')
            summaries.append({
                'client_id': client['client_id'],
                'client_name': client['client_name'],
                'ingestion_status': 'unknown',
                'engine_status': 'unknown',
                'error': str(e)[:500],
            })

    elapsed = time.time() - t0

    # Final summary
    logger.info('')
    logger.info('=' * 60)
    logger.info('OVERNIGHT RUN COMPLETE')
    logger.info('=' * 60)
    for s in summaries:
        logger.info(f'  {s["client_name"]}: ingestion={s["ingestion_status"]}, engine={s["engine_status"]}')
    logger.info(f'Total time: {elapsed:.1f}s')
    logger.info('=' * 60)

    # Exit code reflects whether all clients succeeded
    any_failed = any(s.get('ingestion_status') == 'failed' or s.get('engine_status') == 'failed'
                     for s in summaries)
    return 1 if any_failed else 0


if __name__ == '__main__':
    sys.exit(main())
