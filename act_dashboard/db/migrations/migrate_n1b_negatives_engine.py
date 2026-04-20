"""N1b Gate 1 — Rules engine / review UI schema migration.

Applies:
 1. Drop old indexes on act_v2_search_term_reviews (N1a left them pointing at
    last_seen_date; new spec uses analysis_date)
 2. DROP + CREATE act_v2_search_term_reviews with new column set
    (adds analysis_date, pushed_google_ads_criterion_id, push_error;
    drops pass3_phrase_suggestions JSON — moved to its own table)
 3. CREATE SEQUENCE seq_act_v2_phrase_suggestions
 4. CREATE act_v2_phrase_suggestions
 5. Insert 5 new default settings for each existing client (neg_pass1_enabled,
    neg_pass3_threshold_1word / _2word / _3word, neg_pass3_stopwords)

Discipline: no secondary index includes a column that gets UPDATEd post-insert
(review_status, pass1_status, pass2_target_list_role, push_error).

Idempotent. Run: python -m act_dashboard.db.migrations.migrate_n1b_negatives_engine
"""
import logging
import os
import sys

import duckdb

from act_dashboard.db.defaults import NEG_ENGINE_SETTINGS

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..'))
DB_PATH = os.path.join(PROJECT_ROOT, 'warehouse.duckdb')
LOG_PATH = os.path.join(SCRIPT_DIR, 'migration.log')

logger = logging.getLogger('act_v2_n1b')
logger.setLevel(logging.INFO)
fmt = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
if not logger.handlers:
    sh = logging.StreamHandler(sys.stdout); sh.setFormatter(fmt); logger.addHandler(sh)
    fh = logging.FileHandler(LOG_PATH, mode='a', encoding='utf-8'); fh.setFormatter(fmt); logger.addHandler(fh)


def _index_exists(con, name: str) -> bool:
    return bool(con.execute(
        "SELECT 1 FROM duckdb_indexes() WHERE index_name = ?", [name]
    ).fetchall())


def main():
    logger.info('=' * 50)
    logger.info('N1b Gate 1 Migration — Starting')
    logger.info('=' * 50)

    try:
        con = duckdb.connect(DB_PATH)
    except duckdb.IOException:
        logger.error('DB locked — stop Flask first.')
        sys.exit(1)

    try:
        # -------------------------------------------------------------------
        # 1. Drop old indexes on the search-term-reviews table
        # -------------------------------------------------------------------
        for old_idx in ('idx_st_review_client', 'idx_st_review_client_date'):
            if _index_exists(con, old_idx):
                con.execute(f'DROP INDEX {old_idx};')
                logger.info(f'  dropped old index: {old_idx}')

        # -------------------------------------------------------------------
        # 2. Rebuild act_v2_search_term_reviews
        # -------------------------------------------------------------------
        logger.info('--- act_v2_search_term_reviews (DROP + CREATE) ---')
        con.execute('DROP TABLE IF EXISTS act_v2_search_term_reviews;')
        # Seq already exists from N1a — verify or create
        con.execute('CREATE SEQUENCE IF NOT EXISTS seq_act_v2_st_reviews;')
        con.execute("""
            CREATE TABLE act_v2_search_term_reviews (
                id BIGINT PRIMARY KEY DEFAULT nextval('seq_act_v2_st_reviews'),
                client_id VARCHAR NOT NULL,
                search_term VARCHAR NOT NULL,
                analysis_date DATE NOT NULL,
                first_seen_date DATE NOT NULL,
                last_seen_date DATE NOT NULL,
                total_impressions INTEGER,
                total_clicks INTEGER,
                total_cost DECIMAL(10,2),
                total_conversions DECIMAL(10,2),
                pass1_status VARCHAR,               -- UPDATEd — NEVER index
                pass1_reason VARCHAR,
                pass2_target_list_role VARCHAR,     -- UPDATEd — NEVER index
                review_status VARCHAR DEFAULT 'pending',  -- UPDATEd — NEVER index
                reviewed_at TIMESTAMP,
                reviewed_by VARCHAR,
                pushed_to_ads_at TIMESTAMP,
                pushed_google_ads_criterion_id VARCHAR,
                push_error VARCHAR,
                UNIQUE(client_id, search_term, analysis_date),
                FOREIGN KEY (client_id) REFERENCES act_v2_clients(client_id)
            );
        """)
        con.execute("""
            CREATE INDEX idx_st_review_client_date
            ON act_v2_search_term_reviews(client_id, analysis_date);
        """)
        logger.info('  rebuilt + idx_st_review_client_date(client_id, analysis_date)')

        # -------------------------------------------------------------------
        # 3. Phrase suggestions sequence + table
        # -------------------------------------------------------------------
        logger.info('--- act_v2_phrase_suggestions ---')
        con.execute('CREATE SEQUENCE IF NOT EXISTS seq_act_v2_phrase_suggestions;')
        con.execute("""
            CREATE TABLE IF NOT EXISTS act_v2_phrase_suggestions (
                id BIGINT PRIMARY KEY DEFAULT nextval('seq_act_v2_phrase_suggestions'),
                client_id VARCHAR NOT NULL,
                analysis_date DATE NOT NULL,
                fragment VARCHAR NOT NULL,
                word_count INTEGER NOT NULL,
                target_list_role VARCHAR NOT NULL,
                source_search_terms JSON NOT NULL,
                occurrence_count INTEGER NOT NULL,
                risk_level VARCHAR NOT NULL,
                review_status VARCHAR DEFAULT 'pending',  -- UPDATEd — NEVER index
                reviewed_at TIMESTAMP,
                reviewed_by VARCHAR,
                pushed_to_ads_at TIMESTAMP,
                pushed_google_ads_criterion_id VARCHAR,
                push_error VARCHAR,
                UNIQUE(client_id, analysis_date, fragment, target_list_role),
                FOREIGN KEY (client_id) REFERENCES act_v2_clients(client_id)
            );
        """)
        if not _index_exists(con, 'idx_phrase_sugg_client_date'):
            con.execute("""
                CREATE INDEX idx_phrase_sugg_client_date
                ON act_v2_phrase_suggestions(client_id, analysis_date);
            """)
        logger.info('  table + idx_phrase_sugg_client_date(client_id, analysis_date)')

        # -------------------------------------------------------------------
        # 3b. Widen act_v2_scheduler_runs.phase CHECK to accept N1b phases
        # -------------------------------------------------------------------
        logger.info('--- act_v2_scheduler_runs: widen phase CHECK ---')
        # Detect whether migration already applied (constraint already wide)
        try:
            con.execute(
                """INSERT INTO act_v2_scheduler_runs
                   (client_id, run_date, phase, status, started_at)
                   VALUES ('__probe__', CURRENT_DATE, 'neg_pass1', 'success', CURRENT_TIMESTAMP)"""
            )
            con.execute(
                "DELETE FROM act_v2_scheduler_runs WHERE client_id = '__probe__'"
            )
            logger.info('  phase CHECK already widened (no-op)')
        except duckdb.ConstraintException:
            # Rebuild table with widened CHECK, preserving rows
            logger.info('  rebuilding act_v2_scheduler_runs to widen phase CHECK...')
            con.execute("CREATE TABLE act_v2_scheduler_runs_new AS SELECT * FROM act_v2_scheduler_runs;")
            con.execute('DROP TABLE act_v2_scheduler_runs;')
            con.execute("""
                CREATE TABLE act_v2_scheduler_runs (
                    run_id BIGINT PRIMARY KEY DEFAULT nextval('seq_act_v2_scheduler_runs'),
                    client_id VARCHAR NOT NULL,
                    run_date DATE NOT NULL,
                    phase VARCHAR(30) NOT NULL CHECK (phase IN (
                        'ingestion', 'engine',
                        'neg_stale_cleanup', 'neg_pass1', 'neg_pass2', 'neg_pass3'
                    )),
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
            logger.info(f'  rebuilt; {preserved} prior rows preserved')

        # -------------------------------------------------------------------
        # 4. Backfill 5 new settings for every existing client
        # -------------------------------------------------------------------
        logger.info('--- Backfilling 5 settings for active clients ---')
        client_ids = [r[0] for r in con.execute(
            'SELECT client_id FROM act_v2_clients ORDER BY client_id'
        ).fetchall()]
        for cid in client_ids:
            for key, value, stype, level in NEG_ENGINE_SETTINGS:
                existing = con.execute(
                    "SELECT 1 FROM act_v2_client_settings WHERE client_id = ? AND setting_key = ?",
                    [cid, key],
                ).fetchone()
                if not existing:
                    con.execute("""
                        INSERT INTO act_v2_client_settings
                        (client_id, setting_key, setting_value, setting_type, level)
                        VALUES (?, ?, ?, ?, ?)
                    """, [cid, key, value, stype, level])
            logger.info(f'  {cid}: 5 keys ensured')

        logger.info('=' * 50)
        logger.info('N1b Gate 1 Migration Complete')
        logger.info('=' * 50)

    except Exception as e:
        logger.error(f'Migration failed: {e}')
        raise
    finally:
        con.close()


if __name__ == '__main__':
    main()
