"""N4 — PMax CSV ingestion schema migration.

Creates raw_pmax_search_term_csv — a per-client, per-day archive of whatever
the Google Ads UI's scheduled "Search terms report" CSV contains. This
table is the auditable source of truth; the ingestion CLI also upserts a
subset of this data into act_v2_search_terms and act_v2_pmax_other_bucket
so the existing negatives engine picks up real PMax cost/conversion data
without any engine-code change.

PK (client_id, snapshot_date, search_term) — all VARCHAR/DATE, no DECIMAL
PK issues. Idempotent ingestion uses DELETE+INSERT by
(client_id, snapshot_date) — no UPDATEs, so DuckDB 1.1.0's false-positive
UNIQUE-column UPDATE bug isn't reachable.

Run: python -m act_dashboard.db.migrations.migrate_n4_pmax_csv
"""
import logging
import os
import sys

import duckdb

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..'))
DB_PATH = os.path.join(PROJECT_ROOT, 'warehouse.duckdb')
LOG_PATH = os.path.join(SCRIPT_DIR, 'migration.log')

logger = logging.getLogger('act_v2_n4')
logger.setLevel(logging.INFO)
fmt = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
if not logger.handlers:
    sh = logging.StreamHandler(sys.stdout); sh.setFormatter(fmt); logger.addHandler(sh)
    fh = logging.FileHandler(LOG_PATH, mode='a', encoding='utf-8'); fh.setFormatter(fmt); logger.addHandler(fh)


def main():
    logger.info('=' * 50)
    logger.info('N4 PMax CSV Ingestion schema — Starting')
    logger.info('=' * 50)
    try:
        con = duckdb.connect(DB_PATH)
    except duckdb.IOException:
        logger.error('Database locked. Stop the Flask app: taskkill /IM python.exe /F')
        sys.exit(1)
    try:
        con.execute("""
            CREATE TABLE IF NOT EXISTS raw_pmax_search_term_csv (
                client_id VARCHAR NOT NULL,
                snapshot_date DATE NOT NULL,
                campaign_id VARCHAR(30),
                campaign_name VARCHAR(500),
                campaign_type VARCHAR,
                search_term VARCHAR NOT NULL,
                match_type VARCHAR,
                added_excluded VARCHAR,
                cost DECIMAL(18,2),
                impressions INTEGER,
                clicks INTEGER,
                avg_cpc DECIMAL(10,4),
                ctr DECIMAL(10,6),
                device_click_summary VARCHAR,
                conversions DECIMAL(10,2),
                cost_per_conversion DECIMAL(10,2),
                conversion_rate DECIMAL(10,6),
                conversion_value DECIMAL(18,2),
                conversion_value_per_cost DECIMAL(10,4),
                currency VARCHAR(3),
                source_file VARCHAR,
                ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (client_id, snapshot_date, search_term)
            );
        """)
        con.execute("""
            CREATE INDEX IF NOT EXISTS idx_raw_pmax_csv_lookup
              ON raw_pmax_search_term_csv(client_id, snapshot_date);
        """)
        logger.info('  raw_pmax_search_term_csv + idx_raw_pmax_csv_lookup')
        logger.info('N4 complete.')
    finally:
        con.close()


if __name__ == '__main__':
    main()
