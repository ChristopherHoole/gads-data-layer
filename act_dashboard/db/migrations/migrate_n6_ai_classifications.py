"""Tier 2.1 Stage 1 — AI classification + errors + chat log tables.

Three tables introduced by Tier 2.1's AI-assisted negatives flow:

  1. act_v2_ai_classifications  — one row per (source row, prompt_version)
                                  carrying the AI verdict, reasoning,
                                  intent tag, model version, latency,
                                  and post-hoc user_action.
  2. act_v2_ai_errors           — per scope §5.3; one row per
                                  subprocess/API failure (with raw stdout
                                  for diagnostics).
  3. act_v2_ai_chat_log         — per addendum §17; AI assistant chat
                                  history with soft-delete (cleared_at).

WARNING — DuckDB 1.1.0 UPDATE-on-UNIQUE bug (per project memory):
prompt_version, review_id, and phrase_suggestion_id are part of UNIQUE
constraints. NEVER UPDATE these columns in place — DuckDB throws false-
positive PK errors. Cache-skip logic in Stage 4+ must INSERT new rows
or read existing rows only — never UPDATE the UNIQUE-constrained ones.
The user_action / user_actioned_at columns are the only post-INSERT
mutation path on this table and they are deliberately NOT in any UNIQUE
constraint.

Idempotent. Re-runs no-op cleanly thanks to IF NOT EXISTS guards on
sequences, tables, and indexes (the last via _index_exists()).

Run:
    python -m act_dashboard.db.migrations.migrate_n6_ai_classifications
"""
import logging
import os
import sys

import duckdb

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..'))
DB_PATH = os.path.join(PROJECT_ROOT, 'warehouse.duckdb')
LOG_PATH = os.path.join(SCRIPT_DIR, 'migration.log')

logger = logging.getLogger('act_v2_n6')
logger.setLevel(logging.INFO)
fmt = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
if not logger.handlers:
    sh = logging.StreamHandler(sys.stdout); sh.setFormatter(fmt); logger.addHandler(sh)
    fh = logging.FileHandler(LOG_PATH, mode='a', encoding='utf-8'); fh.setFormatter(fmt); logger.addHandler(fh)


def _index_exists(con, name: str) -> bool:
    """Pattern copied from migrate_n1b_negatives_engine. duckdb_indexes()
    returns one row per index; checking by index_name is sufficient
    because index names are global within a schema in DuckDB."""
    return bool(con.execute(
        "SELECT 1 FROM duckdb_indexes() WHERE index_name = ?", [name]
    ).fetchall())


def _create_index_if_absent(con, name: str, ddl: str) -> None:
    if _index_exists(con, name):
        logger.info(f'  index {name}: already exists (no-op)')
    else:
        con.execute(ddl)
        logger.info(f'  created index {name}')


def main():
    logger.info('=' * 50)
    logger.info('N6 — AI classification tables — Starting')
    logger.info('=' * 50)

    try:
        con = duckdb.connect(DB_PATH)
    except duckdb.IOException:
        logger.error('DB locked — stop Flask + watcher first.')
        sys.exit(1)

    try:
        # -------------------------------------------------------------------
        # Sequences first (FKs / DEFAULT nextval depend on these existing).
        # -------------------------------------------------------------------
        for seq in (
            'seq_act_v2_ai_classifications',
            'seq_act_v2_ai_errors',
            'seq_act_v2_ai_chat_log',
        ):
            con.execute(f'CREATE SEQUENCE IF NOT EXISTS {seq};')
            logger.info(f'  sequence ready: {seq}')

        # -------------------------------------------------------------------
        # Table 1 — act_v2_ai_classifications
        # -------------------------------------------------------------------
        logger.info('--- act_v2_ai_classifications ---')
        # WARNING: prompt_version, review_id, and phrase_suggestion_id are part
        # of UNIQUE constraints. NEVER UPDATE these columns in place —
        # DuckDB 1.1.0 throws false-positive PK errors. Cache-skip logic
        # must INSERT new or read existing only.
        con.execute("""
            CREATE TABLE IF NOT EXISTS act_v2_ai_classifications (
                id BIGINT PRIMARY KEY DEFAULT nextval('seq_act_v2_ai_classifications'),
                review_id BIGINT,
                phrase_suggestion_id BIGINT,
                client_id VARCHAR NOT NULL,
                analysis_date DATE NOT NULL,
                search_term VARCHAR,
                fragment VARCHAR,
                flow VARCHAR NOT NULL,
                ai_verdict VARCHAR,
                ai_target_list_role VARCHAR,
                ai_reasoning TEXT,
                ai_confidence VARCHAR NOT NULL,
                ai_intent_tag VARCHAR,
                model_version VARCHAR NOT NULL,
                prompt_version VARCHAR NOT NULL,
                tokens_in INTEGER,
                tokens_out INTEGER,
                latency_ms INTEGER,
                classified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_action VARCHAR,
                user_actioned_at TIMESTAMP,
                CHECK (
                    (flow = 'pass3'
                        AND phrase_suggestion_id IS NOT NULL
                        AND review_id IS NULL
                        AND ai_target_list_role IS NOT NULL)
                    OR
                    (flow IN ('search_block','search_review','pmax_block','pmax_review')
                        AND review_id IS NOT NULL
                        AND phrase_suggestion_id IS NULL
                        AND ai_verdict IS NOT NULL)
                ),
                UNIQUE (review_id, prompt_version),
                UNIQUE (phrase_suggestion_id, prompt_version),
                FOREIGN KEY (client_id) REFERENCES act_v2_clients(client_id),
                FOREIGN KEY (review_id) REFERENCES act_v2_search_term_reviews(id),
                FOREIGN KEY (phrase_suggestion_id) REFERENCES act_v2_phrase_suggestions(id)
            );
        """)
        # NULL semantics in DuckDB UNIQUE: NULLs are distinct (SQL standard).
        # Two pass3 rows with review_id=NULL + same prompt_version don't
        # collide because (NULL, 'v1') != (NULL, 'v1'). Same for the
        # phrase_suggestion_id pair. Each constraint guards its own column.
        _create_index_if_absent(
            con, 'idx_ai_class_review_id',
            "CREATE INDEX idx_ai_class_review_id "
            "ON act_v2_ai_classifications(review_id);",
        )
        _create_index_if_absent(
            con, 'idx_ai_class_phrase_suggestion_id',
            "CREATE INDEX idx_ai_class_phrase_suggestion_id "
            "ON act_v2_ai_classifications(phrase_suggestion_id);",
        )
        _create_index_if_absent(
            con, 'idx_ai_class_client_date_flow',
            "CREATE INDEX idx_ai_class_client_date_flow "
            "ON act_v2_ai_classifications(client_id, analysis_date, flow);",
        )
        _create_index_if_absent(
            con, 'idx_ai_class_user_action',
            "CREATE INDEX idx_ai_class_user_action "
            "ON act_v2_ai_classifications(user_action);",
        )

        # -------------------------------------------------------------------
        # Table 2 — act_v2_ai_errors
        # -------------------------------------------------------------------
        logger.info('--- act_v2_ai_errors ---')
        con.execute("""
            CREATE TABLE IF NOT EXISTS act_v2_ai_errors (
                id BIGINT PRIMARY KEY DEFAULT nextval('seq_act_v2_ai_errors'),
                client_id VARCHAR,
                analysis_date DATE,
                flow VARCHAR,
                review_ids_in_batch TEXT,
                error_type VARCHAR NOT NULL,
                error_message TEXT,
                raw_output TEXT,
                occurred_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (client_id) REFERENCES act_v2_clients(client_id)
            );
        """)
        _create_index_if_absent(
            con, 'idx_ai_errors_client_date',
            "CREATE INDEX idx_ai_errors_client_date "
            "ON act_v2_ai_errors(client_id, occurred_at);",
        )
        _create_index_if_absent(
            con, 'idx_ai_errors_type',
            "CREATE INDEX idx_ai_errors_type "
            "ON act_v2_ai_errors(error_type);",
        )

        # -------------------------------------------------------------------
        # Table 3 — act_v2_ai_chat_log
        # -------------------------------------------------------------------
        logger.info('--- act_v2_ai_chat_log ---')
        con.execute("""
            CREATE TABLE IF NOT EXISTS act_v2_ai_chat_log (
                id BIGINT PRIMARY KEY DEFAULT nextval('seq_act_v2_ai_chat_log'),
                client_id VARCHAR NOT NULL,
                flow VARCHAR NOT NULL,
                analysis_date DATE NOT NULL,
                role VARCHAR NOT NULL,
                message TEXT NOT NULL,
                model_version VARCHAR,
                prompt_version VARCHAR,
                tokens_in INTEGER,
                tokens_out INTEGER,
                latency_ms INTEGER,
                related_review_id BIGINT,
                cleared_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CHECK (role IN ('user','assistant','system')),
                FOREIGN KEY (client_id) REFERENCES act_v2_clients(client_id),
                FOREIGN KEY (related_review_id) REFERENCES act_v2_search_term_reviews(id)
            );
        """)
        _create_index_if_absent(
            con, 'idx_ai_chat_client_flow_date',
            "CREATE INDEX idx_ai_chat_client_flow_date "
            "ON act_v2_ai_chat_log(client_id, flow, analysis_date, created_at);",
        )

        logger.info('N6 migration complete.')
        return 0
    finally:
        con.close()


if __name__ == '__main__':
    sys.exit(main())
