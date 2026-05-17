"""Tier 2.1 Part C - widen act_v2_scheduler_runs.phase CHECK with
'pass3_ai_autotrigger'.

The watcher's PMax-ingest-triggered Pass 3 path now logs its own
scheduler_runs row under this new phase label (separate from the
overnight scheduler's `neg_pass3` rows) so the audit trail
distinguishes "Pass 3 fired because of a CSV drop" from "Pass 3 fired
on the overnight cycle".

Mirrors the migrate_fix12 / migrate_n10_kw_history_phase_check pattern:
probe with a real INSERT, no-op if the CHECK already accepts the new
value, otherwise rebuild the table with the widened list.

Run:
    python -m act_dashboard.db.migrations.migrate_t21_pass3_autotrigger_phase
"""
from __future__ import annotations

import logging
import os
import sys

import duckdb

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..'))
DB_PATH = os.path.join(PROJECT_ROOT, 'warehouse.duckdb')
LOG_PATH = os.path.join(SCRIPT_DIR, 'migration.log')

logger = logging.getLogger('t21_pass3_autotrigger_phase')
logger.setLevel(logging.INFO)
fmt = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
if not logger.handlers:
    sh = logging.StreamHandler(sys.stdout); sh.setFormatter(fmt); logger.addHandler(sh)
    try:
        fh = logging.FileHandler(LOG_PATH, mode='a', encoding='utf-8')
        fh.setFormatter(fmt); logger.addHandler(fh)
    except OSError:
        pass

# Sync with overnight_run.py + daily_pipeline.py + earlier migrations.
WIDENED_PHASES = (
    'ingestion', 'engine',
    'neg_sticky_expiry', 'neg_stale_cleanup',
    'neg_pass1', 'neg_pass2', 'neg_pass3',
    'kw_history_mapping',
    'pass3_ai_autotrigger',
)


def main() -> int:
    logger.info('=' * 60)
    logger.info('Tier 2.1 Part C - widen scheduler_runs.phase CHECK')
    logger.info('=' * 60)
    try:
        con = duckdb.connect(DB_PATH)
    except duckdb.IOException:
        logger.error('Database locked. Stop the Flask app first.')
        return 1
    try:
        probe = con.execute(
            "SELECT client_id FROM act_v2_clients ORDER BY client_id LIMIT 1"
        ).fetchone()
        if not probe:
            logger.error('No clients in act_v2_clients; cannot probe.')
            return 1
        probe_cid = probe[0]
        try:
            con.execute(
                """INSERT INTO act_v2_scheduler_runs
                   (client_id, run_date, phase, status, started_at, error_message)
                   VALUES (?, CURRENT_DATE, 'pass3_ai_autotrigger',
                           'success', CURRENT_TIMESTAMP, '__t21_probe__')""",
                [probe_cid],
            )
            con.execute(
                "DELETE FROM act_v2_scheduler_runs WHERE error_message = '__t21_probe__'"
            )
            logger.info('CHECK already wide enough - no-op.')
            return 0
        except duckdb.ConstraintException:
            logger.info('CHECK too narrow; rebuilding table.')

        check_list = ', '.join(f"'{p}'" for p in WIDENED_PHASES)
        con.execute("BEGIN")
        try:
            con.execute(
                "CREATE TABLE _scheduler_runs_backup AS "
                "SELECT * FROM act_v2_scheduler_runs"
            )
            con.execute("DROP TABLE act_v2_scheduler_runs")
            con.execute(f"""
                CREATE TABLE act_v2_scheduler_runs (
                    run_id        INTEGER PRIMARY KEY DEFAULT nextval('seq_act_v2_scheduler_runs'),
                    client_id     VARCHAR(20) NOT NULL,
                    run_date      DATE NOT NULL,
                    phase         VARCHAR(30) NOT NULL CHECK (phase IN ({check_list})),
                    status        VARCHAR(15) NOT NULL,
                    started_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at  TIMESTAMP,
                    error_message VARCHAR,
                    details_json  VARCHAR
                );
            """)
            con.execute(
                """INSERT INTO act_v2_scheduler_runs
                   (run_id, client_id, run_date, phase, status,
                    started_at, completed_at, error_message, details_json)
                   SELECT run_id, client_id, run_date, phase, status,
                          started_at, completed_at, error_message, details_json
                   FROM _scheduler_runs_backup"""
            )
            con.execute("DROP TABLE _scheduler_runs_backup")
            con.execute("COMMIT")
            logger.info('Rebuilt act_v2_scheduler_runs with widened CHECK.')
            return 0
        except Exception:
            con.execute("ROLLBACK")
            raise
    except Exception as e:  # noqa: BLE001
        logger.exception('Migration failed: %s', e)
        return 1
    finally:
        con.close()


if __name__ == '__main__':
    sys.exit(main())
