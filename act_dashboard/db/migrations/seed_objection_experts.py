"""
ACT v2 Seed Data — Objection Experts

Seeds the first client (Objection Experts) with:
- Client record in act_v2_clients
- 6 level states (all OFF) in act_v2_client_level_state
- 71 settings in act_v2_client_settings
- 9 negative keyword list entries in act_v2_negative_keyword_lists

Prerequisites:
- create_act_v2_schema.py must have been run first
- Flask app must be stopped (DuckDB file lock)
- Run from project root: python -m act_dashboard.db.migrations.seed_objection_experts

Idempotent: can be run multiple times safely (uses INSERT OR REPLACE).

Logs to: act_dashboard/db/migrations/migration.log
"""

import logging
import os
import sys

import duckdb

# Import defaults from shared module (single source of truth)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from act_dashboard.db.defaults import DEFAULT_SETTINGS, DEPRECATED_SETTINGS

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
logger = logging.getLogger('act_v2_seed')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

file_handler = logging.FileHandler(LOG_PATH, mode='a', encoding='utf-8')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
CLIENT_ID = 'oe001'
CUSTOMER_ID = '8530211223'
CLIENT_NAME = 'Objection Experts'

LEVELS = ['account', 'campaign', 'ad_group', 'keyword', 'ad', 'shopping']

# Settings imported from shared defaults module (single source of truth)
SETTINGS = DEFAULT_SETTINGS

# 9 negative keyword lists
NEG_KEYWORD_LISTS = [
    ('oe001-list-1word-phrase', '1 WORD phrase', 1, 'phrase'),
    ('oe001-list-1word-exact', '1 WORD exact', 1, 'exact'),
    ('oe001-list-2word-phrase', '2 WORDS phrase', 2, 'phrase'),
    ('oe001-list-2word-exact', '2 WORDS exact', 2, 'exact'),
    ('oe001-list-3word-phrase', '3 WORDS phrase', 3, 'phrase'),
    ('oe001-list-3word-exact', '3 WORDS exact', 3, 'exact'),
    ('oe001-list-4word-phrase', '4 WORDS phrase', 4, 'phrase'),
    ('oe001-list-4word-exact', '4 WORDS exact', 4, 'exact'),
    ('oe001-list-5word-exact', '5+ WORDS exact', 5, 'exact'),
]


def main():
    logger.info('=' * 50)
    logger.info('ACT v2 Seed — Objection Experts — Starting')
    logger.info('=' * 50)
    logger.info(f'Database: {DB_PATH}')

    try:
        con = duckdb.connect(DB_PATH)
    except duckdb.IOException:
        logger.error('ERROR: Database is locked. Stop the Flask app first:')
        logger.error('  taskkill /IM python.exe /F')
        logger.error('Then re-run this script.')
        sys.exit(1)

    try:
        # 1. Insert client (check-then-insert for idempotency — act_v2_clients
        #    has two UNIQUE constraints and child FK references prevent ON CONFLICT)
        logger.info('--- Seeding client ---')
        existing = con.execute(
            "SELECT COUNT(*) FROM act_v2_clients WHERE client_id = ?",
            [CLIENT_ID]
        ).fetchone()[0]
        if existing == 0:
            con.execute("""
                INSERT INTO act_v2_clients
                (client_id, google_ads_customer_id, client_name, persona,
                 monthly_budget, target_cpa, target_roas, active)
                VALUES (?, ?, ?, 'lead_gen_cpa', 1500.00, 25.00, NULL, TRUE)
            """, [CLIENT_ID, CUSTOMER_ID, CLIENT_NAME])
            logger.info(f'  Client: {CLIENT_NAME} ({CLIENT_ID}) — inserted')
        else:
            logger.info(f'  Client: {CLIENT_NAME} ({CLIENT_ID}) — already exists')
        logger.info(f'  Client: {CLIENT_NAME} ({CLIENT_ID})')

        # 2. Insert level states (all OFF)
        logger.info('--- Seeding level states ---')
        for level in LEVELS:
            con.execute("""
                INSERT OR REPLACE INTO act_v2_client_level_state
                (client_id, level, state, updated_by)
                VALUES (?, ?, 'off', 'system')
            """, [CLIENT_ID, level])
            logger.info(f'  Level state: {level} = off')

        # 3. Insert settings (71)
        logger.info('--- Seeding settings ---')
        # Remove deprecated settings from prior versions
        for dep_key in DEPRECATED_SETTINGS:
            con.execute(
                "DELETE FROM act_v2_client_settings WHERE client_id = ? AND setting_key = ?",
                [CLIENT_ID, dep_key]
            )
        for key, value, stype, level in SETTINGS:
            con.execute("""
                INSERT OR REPLACE INTO act_v2_client_settings
                (client_id, setting_key, setting_value, setting_type, level)
                VALUES (?, ?, ?, ?, ?)
            """, [CLIENT_ID, key, value, stype, level])
        settings_count = con.execute(
            "SELECT COUNT(*) FROM act_v2_client_settings WHERE client_id = ?",
            [CLIENT_ID]
        ).fetchone()[0]
        logger.info(f'  Settings seeded: {settings_count}')

        # 4. Insert negative keyword lists (9)
        logger.info('--- Seeding negative keyword lists ---')
        for list_id, list_name, word_count, match_type in NEG_KEYWORD_LISTS:
            con.execute("""
                INSERT OR REPLACE INTO act_v2_negative_keyword_lists
                (list_id, client_id, google_ads_list_id, list_name,
                 word_count, match_type, keyword_count, last_synced_at)
                VALUES (?, ?, NULL, ?, ?, ?, 0, NULL)
            """, [list_id, CLIENT_ID, list_name, word_count, match_type])
            logger.info(f'  List: {list_name} ({list_id})')

        # Summary
        nkl_count = con.execute(
            "SELECT COUNT(*) FROM act_v2_negative_keyword_lists WHERE client_id = ?",
            [CLIENT_ID]
        ).fetchone()[0]

        logger.info('')
        logger.info('=' * 40)
        logger.info('ACT v2 Seed — Objection Experts Complete')
        logger.info('=' * 40)
        logger.info(f'Client: {CLIENT_NAME} ({CLIENT_ID})')
        logger.info(f'Level states: {len(LEVELS)}')
        logger.info(f'Settings: {settings_count}')
        logger.info(f'Negative keyword lists: {nkl_count}')
        logger.info('=' * 40)

    except Exception as e:
        logger.error(f'Seed failed: {e}')
        raise
    finally:
        con.close()


if __name__ == '__main__':
    main()
