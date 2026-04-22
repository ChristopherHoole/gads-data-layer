"""N3 — Sticky Rejections schema migration.

Creates act_v2_sticky_rejections + seq_act_v2_sticky_rej + active-lookup
index. Each row is one rejection event; cycle_number tracks how many times
the user has rejected the same normalized term for the same client.

Idempotent. Run: python -m act_dashboard.db.migrations.migrate_n3_sticky_rejections
"""
import logging
import os
import sys

import duckdb

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..'))
DB_PATH = os.path.join(PROJECT_ROOT, 'warehouse.duckdb')
LOG_PATH = os.path.join(SCRIPT_DIR, 'migration.log')

logger = logging.getLogger('act_v2_n3')
logger.setLevel(logging.INFO)
fmt = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
if not logger.handlers:
    sh = logging.StreamHandler(sys.stdout); sh.setFormatter(fmt); logger.addHandler(sh)
    fh = logging.FileHandler(LOG_PATH, mode='a', encoding='utf-8'); fh.setFormatter(fmt); logger.addHandler(fh)


def main():
    logger.info('=' * 50)
    logger.info('N3 Sticky Rejections — Starting')
    logger.info('=' * 50)
    try:
        con = duckdb.connect(DB_PATH)
    except duckdb.IOException:
        logger.error('Database locked. Stop the Flask app: taskkill /IM python.exe /F')
        sys.exit(1)
    try:
        con.execute('CREATE SEQUENCE IF NOT EXISTS seq_act_v2_sticky_rej START 1;')
        con.execute("""
            CREATE TABLE IF NOT EXISTS act_v2_sticky_rejections (
                id BIGINT PRIMARY KEY DEFAULT nextval('seq_act_v2_sticky_rej'),
                client_id VARCHAR NOT NULL,
                search_term_normalized VARCHAR NOT NULL,
                search_term_original VARCHAR NOT NULL,
                rejected_at TIMESTAMP NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                cycle_number INTEGER NOT NULL,
                reason_at_rejection VARCHAR,
                reason_detail_at_rejection VARCHAR,
                campaign_type_at_rejection VARCHAR,
                rejected_by VARCHAR,
                unrejected_at TIMESTAMP NULL,
                unrejected_reason VARCHAR
            );
        """)
        # Index covers the hot "active sticky for this term?" lookup path.
        con.execute("""
            CREATE INDEX IF NOT EXISTS idx_sticky_rej_active
              ON act_v2_sticky_rejections
                 (client_id, search_term_normalized, expires_at, unrejected_at);
        """)
        logger.info('  act_v2_sticky_rejections + idx_sticky_rej_active')
        logger.info('N3 complete.')
    finally:
        con.close()


if __name__ == '__main__':
    main()
