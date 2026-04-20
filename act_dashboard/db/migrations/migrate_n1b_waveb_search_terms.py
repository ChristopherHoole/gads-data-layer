"""N1b Wave B Gate B — extend act_v2_search_terms with status + campaign_type.

Adds two nullable VARCHAR columns:
 - status         (Google Ads search_term_view.status: NONE/ADDED/EXCLUDED/
                  ADDED_EXCLUDED/UNKNOWN)
 - campaign_type  (campaign.advertising_channel_type: SEARCH/PERFORMANCE_MAX/
                  SHOPPING/DISPLAY/VIDEO/...)

Idempotent: skips if columns already present.

Note on PMax rows: synthetic match_type='PMAX' plus ad_group_id/name =
'PMAX_ASSET_GROUP' (keeps existing NOT NULL constraint intact).
"""
import logging
import os
import sys

import duckdb

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..'))
DB_PATH = os.path.join(PROJECT_ROOT, 'warehouse.duckdb')
LOG_PATH = os.path.join(SCRIPT_DIR, 'migration.log')

logger = logging.getLogger('act_v2_waveb')
logger.setLevel(logging.INFO)
fmt = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
if not logger.handlers:
    sh = logging.StreamHandler(sys.stdout); sh.setFormatter(fmt); logger.addHandler(sh)
    fh = logging.FileHandler(LOG_PATH, mode='a', encoding='utf-8'); fh.setFormatter(fmt); logger.addHandler(fh)


def _has_column(con, table, col):
    return bool(con.execute(
        "SELECT 1 FROM information_schema.columns WHERE table_name=? AND column_name=?",
        [table, col]
    ).fetchall())


def main():
    logger.info('=' * 50)
    logger.info('Wave B schema migration — act_v2_search_terms + pmax_other_bucket')
    logger.info('=' * 50)
    con = duckdb.connect(DB_PATH)
    try:
        for col in ('status', 'campaign_type'):
            if _has_column(con, 'act_v2_search_terms', col):
                logger.info(f'  search_terms.{col} (already exists)')
            else:
                con.execute(f'ALTER TABLE act_v2_search_terms ADD COLUMN {col} VARCHAR;')
                logger.info(f'  search_terms.{col} (added)')

        # Wave B addition: Other-bucket transparency for PMax
        con.execute('CREATE SEQUENCE IF NOT EXISTS seq_act_v2_pmax_other;')
        con.execute("""
            CREATE TABLE IF NOT EXISTS act_v2_pmax_other_bucket (
                id BIGINT PRIMARY KEY DEFAULT nextval('seq_act_v2_pmax_other'),
                client_id VARCHAR NOT NULL,
                snapshot_date DATE NOT NULL,
                campaign_id VARCHAR NOT NULL,
                campaign_name VARCHAR,
                impressions INTEGER,
                clicks INTEGER,
                cost DECIMAL(18,2),
                conversions DECIMAL(10,2),
                distinct_term_count INTEGER,
                ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(client_id, campaign_id, snapshot_date),
                FOREIGN KEY (client_id) REFERENCES act_v2_clients(client_id)
            );
        """)
        logger.info('  seq_act_v2_pmax_other + act_v2_pmax_other_bucket (ensured)')
        logger.info('=' * 50)
    finally:
        con.close()


if __name__ == '__main__':
    main()
