"""N9 — Per-client AI feedback-loop flag.

Adds `enable_ai_feedback_loop BOOLEAN DEFAULT FALSE` to act_v2_clients,
and enables it for dbd001 (the v1 rollout client).

Powers Brief 2.1g:
  - Mechanism 1: exact-match auto-fill (90d lookback) skips the AI call.
  - Mechanism 2: few-shot examples (last 30 user decisions) injected into
    the AI Triage prompt for novel terms.

Idempotent — checks pragma_table_info() before adding column; UPDATE for
dbd001 is unconditional but no-op-safe.

Run:
    python -m act_dashboard.db.migrations.migrate_n9_ai_feedback_loop
"""
import logging
import os
import sys

import duckdb

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..'))
DB_PATH = os.path.join(PROJECT_ROOT, 'warehouse.duckdb')
LOG_PATH = os.path.join(SCRIPT_DIR, 'migration.log')

logger = logging.getLogger('act_v2_n9')
logger.setLevel(logging.INFO)
fmt = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
if not logger.handlers:
    sh = logging.StreamHandler(sys.stdout); sh.setFormatter(fmt); logger.addHandler(sh)
    fh = logging.FileHandler(LOG_PATH, mode='a', encoding='utf-8'); fh.setFormatter(fmt); logger.addHandler(fh)


def main():
    logger.info('=' * 50)
    logger.info('N9 — AI feedback-loop flag — Starting')
    logger.info('=' * 50)

    try:
        con = duckdb.connect(DB_PATH)
    except duckdb.IOException:
        logger.error('DB locked — stop Flask + watcher first.')
        sys.exit(1)

    try:
        existing = {r[1] for r in con.execute(
            "PRAGMA table_info('act_v2_clients')"
        ).fetchall()}

        if 'enable_ai_feedback_loop' in existing:
            logger.info('  column already present — no-op')
        else:
            con.execute(
                "ALTER TABLE act_v2_clients "
                "ADD COLUMN enable_ai_feedback_loop BOOLEAN DEFAULT FALSE"
            )
            logger.info('  added column enable_ai_feedback_loop (default FALSE)')

        # Enable for the v1 rollout client (DBD).
        con.execute(
            "UPDATE act_v2_clients SET enable_ai_feedback_loop = TRUE "
            "WHERE client_id = 'dbd001'"
        )
        row = con.execute(
            "SELECT enable_ai_feedback_loop FROM act_v2_clients "
            "WHERE client_id = 'dbd001'"
        ).fetchone()
        logger.info(f"  dbd001 flag now = {row[0] if row else 'MISSING CLIENT'}")

        logger.info('=' * 50)
        logger.info('N9 — Complete')
        logger.info('=' * 50)
    finally:
        con.close()


if __name__ == '__main__':
    main()
