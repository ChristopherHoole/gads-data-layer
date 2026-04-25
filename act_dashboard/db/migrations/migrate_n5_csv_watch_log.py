"""N5 / Fix 1.6 — act_v2_csv_watch_log table.

Tracks every Search-terms CSV the pmax_csv_watcher process picks up out of
~/Downloads/. One row per detected file: status walks
'detected' -> 'ingested' (success) or 'detected' -> 'failed' / 'skipped'.

The Morning Review banner queries this table for last-24h activity:
  - any 'failed' row in last 24h -> red banner with file + error
  - latest 'ingested' row in last 24h -> green pill with row count + age

Idempotent. Run:
    python -m act_dashboard.db.migrations.migrate_n5_csv_watch_log
"""
import logging
import os
import sys

import duckdb

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..'))
DB_PATH = os.path.join(PROJECT_ROOT, 'warehouse.duckdb')
LOG_PATH = os.path.join(SCRIPT_DIR, 'migration.log')

logger = logging.getLogger('act_v2_n5')
logger.setLevel(logging.INFO)
fmt = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
if not logger.handlers:
    sh = logging.StreamHandler(sys.stdout); sh.setFormatter(fmt); logger.addHandler(sh)
    fh = logging.FileHandler(LOG_PATH, mode='a', encoding='utf-8'); fh.setFormatter(fmt); logger.addHandler(fh)


def main():
    logger.info('=' * 50)
    logger.info('N5 csv_watch_log — Starting')
    logger.info('=' * 50)
    try:
        con = duckdb.connect(DB_PATH)
    except duckdb.IOException:
        logger.error('Database locked. Stop the Flask app + watcher first.')
        sys.exit(1)
    try:
        con.execute('CREATE SEQUENCE IF NOT EXISTS seq_act_v2_csv_watch_log START 1;')
        # Status check matches the four states the watcher writes:
        #   detected  - file picked up, ingestion not yet run
        #   ingested  - ingest_csv() returned a result; file archived
        #   failed    - ingest_csv() raised; file left in place
        #   skipped   - file recognised but ignored (e.g. already-archived
        #               filename appears, or pre-flight client detect found
        #               no match in act_v2_campaign_roles)
        con.execute("""
            CREATE TABLE IF NOT EXISTS act_v2_csv_watch_log (
                id BIGINT PRIMARY KEY DEFAULT nextval('seq_act_v2_csv_watch_log'),
                file_path VARCHAR NOT NULL,
                client_id VARCHAR,
                status VARCHAR NOT NULL CHECK (status IN (
                    'detected', 'ingested', 'failed', 'skipped'
                )),
                rows_ingested INTEGER,
                error_message TEXT,
                detected_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                processed_at TIMESTAMP
            );
        """)
        con.execute("""
            CREATE INDEX IF NOT EXISTS idx_csv_watch_log_recent
              ON act_v2_csv_watch_log (detected_at DESC);
        """)
        n = con.execute('SELECT COUNT(*) FROM act_v2_csv_watch_log').fetchone()[0]
        logger.info(f'  table ready ({n} prior rows preserved)')
        logger.info('N5 complete.')
        return 0
    finally:
        con.close()


if __name__ == '__main__':
    sys.exit(main())
