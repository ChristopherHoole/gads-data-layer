"""Tier 2.1 Stage 11 — add manual_override flag to act_v2_phrase_suggestions.

The Pass 3 AI engine writes target_list_role directly onto each phrase
suggestion. When Chris overrides the AI's choice via the UI's role
dropdown, we want to know it was hand-set (so future Pass 3 re-runs
don't trample manual decisions and so the UI can render a "manually
edited" indicator).

Schema change: one new column on act_v2_phrase_suggestions.
  manual_override BOOLEAN NOT NULL DEFAULT FALSE

Idempotent: probes information_schema before adding.

Run:
    python -m act_dashboard.db.migrations.migrate_t21_stage11_manual_override
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

logger = logging.getLogger('t21_stage11_manual_override')
logger.setLevel(logging.INFO)
fmt = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
if not logger.handlers:
    sh = logging.StreamHandler(sys.stdout); sh.setFormatter(fmt); logger.addHandler(sh)
    try:
        fh = logging.FileHandler(LOG_PATH, mode='a', encoding='utf-8')
        fh.setFormatter(fmt); logger.addHandler(fh)
    except OSError:
        pass


def main() -> int:
    logger.info('=' * 60)
    logger.info('Tier 2.1 Stage 11 - manual_override column')
    logger.info('=' * 60)
    try:
        con = duckdb.connect(DB_PATH)
    except duckdb.IOException:
        logger.error('Database locked. Stop the Flask app first.')
        return 1
    try:
        exists = con.execute(
            "SELECT 1 FROM information_schema.columns "
            "WHERE table_name = 'act_v2_phrase_suggestions' "
            "AND column_name = 'manual_override' LIMIT 1"
        ).fetchone()
        if exists:
            logger.info('manual_override column already exists; no-op.')
            return 0
        # DuckDB 1.1.0 doesn't support ALTER TABLE ADD COLUMN with NOT NULL
        # + DEFAULT in one shot — add the column nullable, backfill, then
        # rely on app-level defaults. New inserts via the engine pass
        # manual_override explicitly so NULLs only ever appear on pre-
        # migration rows.
        con.execute(
            "ALTER TABLE act_v2_phrase_suggestions "
            "ADD COLUMN manual_override BOOLEAN"
        )
        con.execute(
            "UPDATE act_v2_phrase_suggestions "
            "SET manual_override = FALSE WHERE manual_override IS NULL"
        )
        n = con.execute(
            "SELECT COUNT(*) FROM information_schema.columns "
            "WHERE table_name = 'act_v2_phrase_suggestions' "
            "AND column_name = 'manual_override'"
        ).fetchone()[0]
        if n != 1:
            logger.error('Post-add probe failed (n=%s). Migration aborted.', n)
            return 1
        logger.info('manual_override added successfully.')
        return 0
    except Exception as e:  # noqa: BLE001
        logger.exception('Migration failed: %s', e)
        return 1
    finally:
        con.close()


if __name__ == '__main__':
    sys.exit(main())
