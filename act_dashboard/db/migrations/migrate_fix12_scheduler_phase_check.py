"""Fix 1.2 — widen act_v2_scheduler_runs.phase CHECK to include 'neg_sticky_expiry'.

Problem
-------
N3 (Sticky Rejections) added a 'neg_sticky_expiry' phase to the overnight
scheduler (act_dashboard/scheduler/overnight_run.py:run_neg_sticky_expiry_phase),
but the CHECK constraint on act_v2_scheduler_runs.phase wasn't widened to match.

Result: every overnight cycle aborts with
    Constraint Error: CHECK constraint failed on table act_v2_scheduler_runs
    with expression CHECK((phase IN ('ingestion', 'engine',
    'neg_stale_cleanup', 'neg_pass1', 'neg_pass2', 'neg_pass3')))
which propagates as a FATAL cycle error in main(), and the cycle's per-phase
status rows never write — so Morning Review shows ingestion/engine = 'unknown'
even though both succeeded.

Fix
---
Rebuild act_v2_scheduler_runs with the wider CHECK list:
    ingestion, engine,
    neg_sticky_expiry, neg_stale_cleanup, neg_pass1, neg_pass2, neg_pass3

Idempotent: probes the constraint first; rebuilds only on ConstraintException.

Run:
    python -m act_dashboard.db.migrations.migrate_fix12_scheduler_phase_check
"""
import logging
import os
import sys

import duckdb

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..'))
DB_PATH = os.path.join(PROJECT_ROOT, 'warehouse.duckdb')
LOG_PATH = os.path.join(SCRIPT_DIR, 'migration.log')

logger = logging.getLogger('act_v2_fix12')
logger.setLevel(logging.INFO)
fmt = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
if not logger.handlers:
    sh = logging.StreamHandler(sys.stdout); sh.setFormatter(fmt); logger.addHandler(sh)
    fh = logging.FileHandler(LOG_PATH, mode='a', encoding='utf-8'); fh.setFormatter(fmt); logger.addHandler(fh)


WIDENED_PHASES = (
    'ingestion', 'engine',
    'neg_sticky_expiry', 'neg_stale_cleanup',
    'neg_pass1', 'neg_pass2', 'neg_pass3',
)


def main():
    logger.info('=' * 50)
    logger.info("Fix 1.2 — widen scheduler_runs.phase CHECK")
    logger.info('=' * 50)
    try:
        con = duckdb.connect(DB_PATH)
    except duckdb.IOException:
        logger.error('Database locked. Stop the Flask app: taskkill /IM python.exe /F')
        sys.exit(1)
    try:
        # Probe via a real existing client_id so we only hit the CHECK
        # constraint (FK validation otherwise dominates with '__probe__').
        probe_client = con.execute(
            "SELECT client_id FROM act_v2_clients ORDER BY client_id LIMIT 1"
        ).fetchone()
        if not probe_client:
            logger.error('No clients in act_v2_clients; cannot probe. Aborting.')
            return 1
        probe_cid = probe_client[0]

        try:
            con.execute(
                """INSERT INTO act_v2_scheduler_runs
                   (client_id, run_date, phase, status, started_at,
                    error_message)
                   VALUES (?, CURRENT_DATE, 'neg_sticky_expiry',
                           'success', CURRENT_TIMESTAMP, '__fix12_probe__')""",
                [probe_cid],
            )
            con.execute(
                "DELETE FROM act_v2_scheduler_runs "
                "WHERE error_message = '__fix12_probe__'"
            )
            logger.info("  phase CHECK already permits 'neg_sticky_expiry' — no-op")
            return 0
        except duckdb.ConstraintException:
            logger.info("  CHECK rejects 'neg_sticky_expiry'; rebuilding table...")

        # Rebuild preserving rows
        con.execute("CREATE TABLE act_v2_scheduler_runs_new AS "
                    "SELECT * FROM act_v2_scheduler_runs;")
        con.execute('DROP TABLE act_v2_scheduler_runs;')
        check_list = ', '.join(f"'{p}'" for p in WIDENED_PHASES)
        con.execute(f"""
            CREATE TABLE act_v2_scheduler_runs (
                run_id BIGINT PRIMARY KEY DEFAULT nextval('seq_act_v2_scheduler_runs'),
                client_id VARCHAR NOT NULL,
                run_date DATE NOT NULL,
                phase VARCHAR(30) NOT NULL CHECK (phase IN ({check_list})),
                status VARCHAR(20) NOT NULL CHECK (status IN ('running', 'success', 'failed', 'skipped')),
                started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                error_message VARCHAR,
                details_json JSON,
                FOREIGN KEY (client_id) REFERENCES act_v2_clients(client_id)
            );
        """)
        con.execute("""
            INSERT INTO act_v2_scheduler_runs
              (run_id, client_id, run_date, phase, status,
               started_at, completed_at, error_message, details_json)
            SELECT run_id, client_id, run_date, phase, status,
                   started_at, completed_at, error_message, details_json
            FROM act_v2_scheduler_runs_new;
        """)
        con.execute('DROP TABLE act_v2_scheduler_runs_new;')
        preserved = con.execute('SELECT COUNT(*) FROM act_v2_scheduler_runs').fetchone()[0]
        logger.info(f"  rebuilt; {preserved} prior rows preserved")

        # Verify by probing with a real client
        con.execute(
            """INSERT INTO act_v2_scheduler_runs
               (client_id, run_date, phase, status, started_at,
                error_message)
               VALUES (?, CURRENT_DATE, 'neg_sticky_expiry',
                       'success', CURRENT_TIMESTAMP, '__fix12_probe__')""",
            [probe_cid],
        )
        con.execute(
            "DELETE FROM act_v2_scheduler_runs "
            "WHERE error_message = '__fix12_probe__'"
        )
        logger.info("  verified: 'neg_sticky_expiry' now accepted")
        logger.info('Fix 1.2 complete.')
        return 0
    finally:
        con.close()


if __name__ == '__main__':
    sys.exit(main())
