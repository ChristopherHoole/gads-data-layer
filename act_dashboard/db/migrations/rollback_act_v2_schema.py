"""
ACT v2 Schema Rollback

Drops ALL act_v2_* tables and sequences. This is destructive and irreversible.
Must be run interactively — requires typing 'YES' to confirm.

Prerequisites:
- Flask app must be stopped (DuckDB file lock)
- Run from project root: python -m act_dashboard.db.migrations.rollback_act_v2_schema

Logs to: act_dashboard/db/migrations/migration.log
"""

import logging
import os
import sys

import duckdb

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..'))
DB_PATH = os.path.join(PROJECT_ROOT, 'warehouse.duckdb')
LOG_PATH = os.path.join(SCRIPT_DIR, 'migration.log')

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logger = logging.getLogger('act_v2_rollback')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

file_handler = logging.FileHandler(LOG_PATH, mode='a', encoding='utf-8')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Drop order: children first, then parents
TABLES_DROP_ORDER = [
    'act_v2_monitoring',
    'act_v2_executed_actions',
    'act_v2_recommendations',
    'act_v2_alerts',
    'act_v2_search_terms',
    'act_v2_campaign_segments',
    'act_v2_snapshots',
    'act_v2_negative_keyword_lists',
    'act_v2_campaign_roles',
    'act_v2_client_settings',
    'act_v2_client_level_state',
    'act_v2_checks',
    'act_v2_clients',
]

SEQUENCES = [
    'seq_act_v2_snapshots',
    'seq_act_v2_recommendations',
    'seq_act_v2_executed_actions',
    'seq_act_v2_monitoring',
    'seq_act_v2_alerts',
    'seq_act_v2_search_terms',
    'seq_act_v2_campaign_segments',
]


def main():
    logger.info('=' * 50)
    logger.info('ACT v2 Schema Rollback')
    logger.info('=' * 50)

    print()
    print('WARNING: This will DELETE all act_v2_* tables and all data in them.')
    print('This action cannot be undone.')
    confirmation = input("Type 'YES' (all caps) to confirm: ")

    if confirmation != 'YES':
        logger.info('Rollback cancelled.')
        print('Rollback cancelled.')
        return

    try:
        con = duckdb.connect(DB_PATH)
    except duckdb.IOException:
        logger.error('ERROR: Database is locked. Stop the Flask app first:')
        logger.error('  taskkill /IM python.exe /F')
        logger.error('Then re-run this script.')
        sys.exit(1)

    try:
        tables_dropped = 0
        seqs_dropped = 0

        # Drop tables in dependency order
        logger.info('--- Dropping tables ---')
        for table in TABLES_DROP_ORDER:
            con.execute(f'DROP TABLE IF EXISTS {table};')
            logger.info(f'  Dropped: {table}')
            tables_dropped += 1

        # Drop sequences
        logger.info('--- Dropping sequences ---')
        for seq in SEQUENCES:
            con.execute(f'DROP SEQUENCE IF EXISTS {seq};')
            logger.info(f'  Dropped: {seq}')
            seqs_dropped += 1

        logger.info('')
        logger.info('=' * 40)
        logger.info('ACT v2 Schema Rollback Complete')
        logger.info('=' * 40)
        logger.info(f'Tables dropped: {tables_dropped}')
        logger.info(f'Sequences dropped: {seqs_dropped}')
        logger.info('=' * 40)

    except Exception as e:
        logger.error(f'Rollback failed: {e}')
        raise
    finally:
        con.close()


if __name__ == '__main__':
    main()
