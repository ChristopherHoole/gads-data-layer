"""N10 — widen act_v2_scheduler_runs.phase CHECK to include 'kw_history_mapping'.

The KW + Search Term History overnight refresh phase (Phase 4 of the
brief) writes a status row per nightly run; without this widening the
INSERT trips the CHECK constraint and the cycle aborts.

Mirrors the fix12 pattern exactly: probe via a real client to isolate
the CHECK error, then rebuild the table with the wider list (data +
PK + indexes preserved).

Run:
    python -m act_dashboard.db.migrations.migrate_n10_kw_history_phase_check
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

logger = logging.getLogger('act_n10_kw_history_phase')
logger.setLevel(logging.INFO)
fmt = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
if not logger.handlers:
    sh = logging.StreamHandler(sys.stdout); sh.setFormatter(fmt); logger.addHandler(sh)
    try:
        fh = logging.FileHandler(LOG_PATH, mode='a', encoding='utf-8')
        fh.setFormatter(fmt); logger.addHandler(fh)
    except OSError:
        pass

# Keep this list in sync with the runtime stage list in overnight_run.py
# + daily_pipeline.py. New phases require a new migration step.
WIDENED_PHASES = (
    'ingestion', 'engine',
    'neg_sticky_expiry', 'neg_stale_cleanup',
    'neg_pass1', 'neg_pass2', 'neg_pass3',
    'kw_history_mapping',
)


def main() -> int:
    logger.info('=' * 60)
    logger.info('N10 — widen scheduler_runs.phase CHECK for kw_history_mapping')
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

        # Try a probe INSERT with the new phase. If it succeeds, the CHECK
        # is already wide enough and we no-op.
        try:
            con.execute(
                """INSERT INTO act_v2_scheduler_runs
                   (client_id, run_date, phase, status, started_at, error_message)
                   VALUES (?, CURRENT_DATE, 'kw_history_mapping',
                           'success', CURRENT_TIMESTAMP, '__n10_probe__')""",
                [probe_cid],
            )
            con.execute(
                "DELETE FROM act_v2_scheduler_runs WHERE error_message = '__n10_probe__'"
            )
            logger.info('CHECK already wide enough — no-op.')
            return 0
        except duckdb.ConstraintException:
            logger.info('CHECK too narrow; rebuilding table with widened set.')

        # Rebuild path: copy → drop → recreate with new CHECK → insert back.
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
