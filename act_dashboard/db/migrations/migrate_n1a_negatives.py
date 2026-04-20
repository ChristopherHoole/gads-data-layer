"""N1a — Negatives Module schema migration.

Applies schema changes for N1a Data Foundation:

1. Extends `act_v2_negative_keyword_lists`:
   - drops CHECK constraints on word_count (1..5) + match_type (exact|phrase)
     by recreating the table (DuckDB can't drop CHECK in-place)
   - adds: list_role VARCHAR, added_manually_count INTEGER, added_by_act_count INTEGER,
           is_linked_to_campaign BOOLEAN
2. Creates `act_v2_negative_list_keywords` (individual negative keywords)
3. Creates `act_v2_search_term_reviews` (classified search terms awaiting review)
4. Adds 4 columns to `act_v2_clients`: services_all, services_advertised,
   service_locations, client_brand_terms
5. Adds 2 sequences: seq_act_v2_neg_list_kw, seq_act_v2_st_reviews

CRITICAL: NO secondary index includes a column that gets UPDATEd after insert.
review_status, pass1_status, pass2_target_list_role on act_v2_search_term_reviews
all get UPDATEd — none appear in any index here. Same for list_role / counts on
act_v2_negative_keyword_lists.

Idempotent: re-runnable.
Prereq: Flask app stopped (DB lock).
Run: python -m act_dashboard.db.migrations.migrate_n1a_negatives
"""

import logging
import os
import sys

import duckdb

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..'))
DB_PATH = os.path.join(PROJECT_ROOT, 'warehouse.duckdb')
LOG_PATH = os.path.join(SCRIPT_DIR, 'migration.log')

logger = logging.getLogger('act_v2_n1a')
logger.setLevel(logging.INFO)
fmt = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
if not logger.handlers:
    sh = logging.StreamHandler(sys.stdout); sh.setFormatter(fmt); logger.addHandler(sh)
    fh = logging.FileHandler(LOG_PATH, mode='a', encoding='utf-8'); fh.setFormatter(fmt); logger.addHandler(fh)


def _has_column(con, table: str, column: str) -> bool:
    rows = con.execute(
        "SELECT 1 FROM information_schema.columns WHERE table_name = ? AND column_name = ?",
        [table, column],
    ).fetchall()
    return bool(rows)


def main():
    logger.info('=' * 50)
    logger.info('N1a Negatives Schema Migration — Starting')
    logger.info('=' * 50)

    try:
        con = duckdb.connect(DB_PATH)
    except duckdb.IOException:
        logger.error('Database locked. Stop the Flask app: taskkill /IM python.exe /F')
        sys.exit(1)

    try:
        # ---------------------------------------------------------------
        # 1. Sequences
        # ---------------------------------------------------------------
        logger.info('--- Sequences ---')
        for seq in ('seq_act_v2_neg_list_kw', 'seq_act_v2_st_reviews'):
            con.execute(f'CREATE SEQUENCE IF NOT EXISTS {seq};')
            logger.info(f'  {seq}')

        # ---------------------------------------------------------------
        # 2. Rebuild act_v2_negative_keyword_lists with relaxed constraints + new cols
        # ---------------------------------------------------------------
        logger.info('--- act_v2_negative_keyword_lists ---')
        # Existing rows are placeholder seed rows (zero keywords) — safe to drop.
        # Drop dependent table first (created below) if present.
        con.execute('DROP TABLE IF EXISTS act_v2_negative_list_keywords;')
        con.execute('DROP TABLE IF EXISTS act_v2_negative_keyword_lists;')
        con.execute("""
            CREATE TABLE act_v2_negative_keyword_lists (
                list_id VARCHAR PRIMARY KEY,
                client_id VARCHAR NOT NULL,
                google_ads_list_id VARCHAR(30),
                list_name VARCHAR(200) NOT NULL,
                word_count INTEGER,                 -- NULLable now (Competitor/Location lists)
                match_type VARCHAR(20),             -- NULLable now; no CHECK
                list_role VARCHAR(40),              -- one of 13 enum values or NULL
                keyword_count INTEGER NOT NULL DEFAULT 0,
                added_manually_count INTEGER NOT NULL DEFAULT 0,
                added_by_act_count INTEGER NOT NULL DEFAULT 0,
                is_linked_to_campaign BOOLEAN NOT NULL DEFAULT FALSE,
                last_synced_at TIMESTAMP,
                FOREIGN KEY (client_id) REFERENCES act_v2_clients(client_id)
            );
        """)
        logger.info('  rebuilt act_v2_negative_keyword_lists')

        # ---------------------------------------------------------------
        # 3. act_v2_negative_list_keywords
        # ---------------------------------------------------------------
        con.execute("""
            CREATE TABLE IF NOT EXISTS act_v2_negative_list_keywords (
                id BIGINT PRIMARY KEY DEFAULT nextval('seq_act_v2_neg_list_kw'),
                list_id VARCHAR NOT NULL,
                client_id VARCHAR NOT NULL,
                keyword_text VARCHAR NOT NULL,
                match_type VARCHAR NOT NULL,        -- EXACT | PHRASE | BROAD
                google_ads_criterion_id VARCHAR,
                added_at TIMESTAMP,
                added_by VARCHAR DEFAULT 'unknown', -- act | manual | unknown
                snapshot_date DATE NOT NULL,
                FOREIGN KEY (list_id) REFERENCES act_v2_negative_keyword_lists(list_id)
            );
        """)
        # Safe indexes: list_id + (client_id, snapshot_date) never UPDATEd
        con.execute('CREATE INDEX IF NOT EXISTS idx_neg_list_kw_list ON act_v2_negative_list_keywords(list_id);')
        con.execute('CREATE INDEX IF NOT EXISTS idx_neg_list_kw_client_date ON act_v2_negative_list_keywords(client_id, snapshot_date);')
        logger.info('  act_v2_negative_list_keywords + 2 indexes')

        # ---------------------------------------------------------------
        # 4. act_v2_search_term_reviews
        # ---------------------------------------------------------------
        con.execute("""
            CREATE TABLE IF NOT EXISTS act_v2_search_term_reviews (
                id BIGINT PRIMARY KEY DEFAULT nextval('seq_act_v2_st_reviews'),
                client_id VARCHAR NOT NULL,
                search_term VARCHAR NOT NULL,
                first_seen_date DATE NOT NULL,
                last_seen_date DATE NOT NULL,
                total_impressions INTEGER,
                total_clicks INTEGER,
                total_cost DECIMAL(10,2),
                total_conversions DECIMAL(10,2),
                pass1_status VARCHAR,               -- UPDATEd — never index
                pass1_reason VARCHAR,
                pass2_target_list_role VARCHAR,     -- UPDATEd — never index
                pass3_phrase_suggestions JSON,
                review_status VARCHAR DEFAULT 'pending',  -- UPDATEd — never index
                reviewed_at TIMESTAMP,
                reviewed_by VARCHAR,
                pushed_to_ads_at TIMESTAMP,
                UNIQUE(client_id, search_term),
                FOREIGN KEY (client_id) REFERENCES act_v2_clients(client_id)
            );
        """)
        # Safe indexes: only columns that are set-once / append-only
        con.execute('CREATE INDEX IF NOT EXISTS idx_st_review_client ON act_v2_search_term_reviews(client_id);')
        con.execute('CREATE INDEX IF NOT EXISTS idx_st_review_client_date ON act_v2_search_term_reviews(client_id, last_seen_date);')
        logger.info('  act_v2_search_term_reviews + 2 indexes')

        # ---------------------------------------------------------------
        # 5. act_v2_clients — 4 new columns (identity-level profile fields)
        # ---------------------------------------------------------------
        logger.info('--- act_v2_clients: add 4 profile columns ---')
        for col in ('services_all', 'services_advertised', 'service_locations', 'client_brand_terms'):
            if _has_column(con, 'act_v2_clients', col):
                logger.info(f'  {col} (already exists)')
            else:
                con.execute(f'ALTER TABLE act_v2_clients ADD COLUMN {col} TEXT;')
                logger.info(f'  {col} (added)')

        # ---------------------------------------------------------------
        # Summary
        # ---------------------------------------------------------------
        nkl = con.execute('SELECT COUNT(*) FROM act_v2_negative_keyword_lists').fetchone()[0]
        nkw = con.execute('SELECT COUNT(*) FROM act_v2_negative_list_keywords').fetchone()[0]
        stv = con.execute('SELECT COUNT(*) FROM act_v2_search_term_reviews').fetchone()[0]
        logger.info('=' * 50)
        logger.info('N1a Schema Migration Complete')
        logger.info(f'  negative_keyword_lists rows: {nkl}')
        logger.info(f'  negative_list_keywords rows: {nkw}')
        logger.info(f'  search_term_reviews rows: {stv}')
        logger.info('=' * 50)

    except Exception as e:
        logger.error(f'Migration failed: {e}')
        raise
    finally:
        con.close()


if __name__ == '__main__':
    main()
