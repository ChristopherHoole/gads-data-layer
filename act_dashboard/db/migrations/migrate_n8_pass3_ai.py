"""N8 — schema for AI-driven Pass 3 (2.1e).

Adds 4 columns to act_v2_phrase_suggestions to carry AI metadata, and
creates a sibling act_v2_pass3_themes table for the theme banner the
Pass 3 tab will render.

Per the 2.1e brief Q2: themes table mirrors the existing phrase_suggestions
date column name (analysis_date) — NOT snapshot_date — so any future
join between themes and fragments is a clean USING (client_id, analysis_date).
The AI engine reads act_v2_search_terms.snapshot_date as input but persists
to analysis_date everywhere downstream.

Idempotent. Safe to re-run; subsequent runs no-op cleanly via IF NOT EXISTS
guards on sequences, tables, columns, and indexes (last via _index_exists).

Run:
    python -m act_dashboard.db.migrations.migrate_n8_pass3_ai
"""
import logging
import os
import sys

import duckdb

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..'))
DB_PATH = os.path.join(PROJECT_ROOT, 'warehouse.duckdb')
LOG_PATH = os.path.join(SCRIPT_DIR, 'migration.log')

logger = logging.getLogger('act_v2_n8')
logger.setLevel(logging.INFO)
fmt = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
if not logger.handlers:
    sh = logging.StreamHandler(sys.stdout); sh.setFormatter(fmt); logger.addHandler(sh)
    fh = logging.FileHandler(LOG_PATH, mode='a', encoding='utf-8'); fh.setFormatter(fmt); logger.addHandler(fh)


def _column_exists(con, table: str, column: str) -> bool:
    rows = con.execute(f"DESCRIBE {table}").fetchall()
    return any(r[0] == column for r in rows)


def _index_exists(con, name: str) -> bool:
    return bool(con.execute(
        "SELECT 1 FROM duckdb_indexes() WHERE index_name = ?", [name]
    ).fetchall())


def _add_column_if_absent(con, table: str, column: str, ddl_type: str) -> None:
    if _column_exists(con, table, column):
        logger.info(f'  {table}.{column}: already exists (no-op)')
    else:
        con.execute(f'ALTER TABLE {table} ADD COLUMN {column} {ddl_type}')
        logger.info(f'  added {table}.{column} ({ddl_type})')


def main():
    logger.info('=' * 60)
    logger.info('N8 — Pass 3 AI schema (2.1e) — Starting')
    logger.info('=' * 60)

    try:
        con = duckdb.connect(DB_PATH)
    except duckdb.IOException:
        logger.error('DB locked — stop Flask + watcher first.')
        sys.exit(1)

    try:
        # ----- act_v2_phrase_suggestions: 4 new cols -----
        logger.info('--- act_v2_phrase_suggestions: AI metadata cols ---')
        _add_column_if_absent(con, 'act_v2_phrase_suggestions',
                              'confidence', 'DOUBLE')
        _add_column_if_absent(con, 'act_v2_phrase_suggestions',
                              'rationale', 'TEXT')
        _add_column_if_absent(con, 'act_v2_phrase_suggestions',
                              'theme_id', 'BIGINT')
        _add_column_if_absent(con, 'act_v2_phrase_suggestions',
                              'source_count', 'INTEGER')

        # ----- act_v2_pass3_themes: new table -----
        logger.info('--- act_v2_pass3_themes ---')
        con.execute('CREATE SEQUENCE IF NOT EXISTS seq_act_v2_pass3_themes;')
        logger.info('  sequence ready: seq_act_v2_pass3_themes')

        con.execute("""
            CREATE TABLE IF NOT EXISTS act_v2_pass3_themes (
                id BIGINT PRIMARY KEY DEFAULT nextval('seq_act_v2_pass3_themes'),
                client_id VARCHAR NOT NULL,
                analysis_date DATE NOT NULL,
                theme_text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        logger.info('  table ready: act_v2_pass3_themes')

        if _index_exists(con, 'idx_pass3_themes_client_date'):
            logger.info('  index idx_pass3_themes_client_date: already exists (no-op)')
        else:
            con.execute(
                'CREATE INDEX idx_pass3_themes_client_date '
                'ON act_v2_pass3_themes(client_id, analysis_date);'
            )
            logger.info('  created index idx_pass3_themes_client_date')

        # ----- Verification (read back what we just wrote) -----
        new_cols = {'confidence', 'rationale', 'theme_id', 'source_count'}
        existing = {r[0] for r in con.execute(
            'DESCRIBE act_v2_phrase_suggestions'
        ).fetchall()}
        missing = new_cols - existing
        assert not missing, f'phrase_suggestions missing new cols: {missing}'

        themes_cols = {r[0] for r in con.execute(
            'DESCRIBE act_v2_pass3_themes'
        ).fetchall()}
        assert {'id', 'client_id', 'analysis_date', 'theme_text', 'created_at'} <= themes_cols, \
            f'themes cols incomplete: {themes_cols}'

        logger.info('=' * 60)
        logger.info('N8 — Complete')
        logger.info('=' * 60)
    finally:
        con.close()


if __name__ == '__main__':
    main()
