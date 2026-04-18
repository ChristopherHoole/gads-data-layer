"""
ACT v2 Generalised Client Seeder

Seeds any client into the ACT v2 database with:
- Client record in act_v2_clients
- 6 level states (all OFF) in act_v2_client_level_state
- 71 default settings in act_v2_client_settings
- 9 standard negative keyword lists in act_v2_negative_keyword_lists

Can be called as a CLI tool or imported as a function.

CLI usage (from project root):
    python -m act_dashboard.db.migrations.seed_client \\
        --id dbd001 --name "Dental by Design" \\
        --customer-id 1234567890 \\
        --persona lead_gen_cpa --target-cpa 75 --budget 45000

Idempotent: can be run multiple times safely.
Logs to: act_dashboard/db/migrations/migration.log
"""

import argparse
import logging
import os
import sys

import duckdb

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

if not logger.handlers:
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    file_handler = logging.FileHandler(LOG_PATH, mode='a', encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
LEVELS = ['account', 'campaign', 'ad_group', 'keyword', 'ad', 'shopping']


def seed_client(client_id, client_name, customer_id, persona,
                monthly_budget, target_cpa=None, target_roas=None):
    """Seed a client into the ACT v2 database.

    Args:
        client_id: Internal ACT client ID (e.g. 'dbd001')
        client_name: Display name (e.g. 'Dental by Design')
        customer_id: Google Ads customer ID, digits only (e.g. '1234567890')
        persona: 'lead_gen_cpa' or 'ecommerce_roas'
        monthly_budget: Monthly ad spend budget in GBP
        target_cpa: Target CPA in GBP (required for lead_gen_cpa)
        target_roas: Target ROAS multiplier (required for ecommerce_roas)
    """
    logger.info('=' * 50)
    logger.info(f'ACT v2 Seed — {client_name} ({client_id}) — Starting')
    logger.info('=' * 50)
    logger.info(f'Database: {DB_PATH}')

    try:
        con = duckdb.connect(DB_PATH)
    except duckdb.IOException:
        logger.error('ERROR: Database is locked. Stop the Flask app first:')
        logger.error('  taskkill /IM python.exe /F')
        sys.exit(1)

    try:
        # 1. Insert client (check-then-insert for idempotency)
        logger.info('--- Seeding client ---')
        existing = con.execute(
            "SELECT COUNT(*) FROM act_v2_clients WHERE client_id = ?",
            [client_id]
        ).fetchone()[0]
        if existing == 0:
            con.execute("""
                INSERT INTO act_v2_clients
                (client_id, google_ads_customer_id, client_name, persona,
                 monthly_budget, target_cpa, target_roas, active)
                VALUES (?, ?, ?, ?, ?, ?, ?, TRUE)
            """, [client_id, customer_id, client_name, persona,
                  monthly_budget, target_cpa, target_roas])
            logger.info(f'  Client: {client_name} ({client_id}) — inserted')
        else:
            logger.info(f'  Client: {client_name} ({client_id}) — already exists')

        # 2. Insert level states (all OFF)
        logger.info('--- Seeding level states ---')
        for level in LEVELS:
            con.execute("""
                INSERT OR REPLACE INTO act_v2_client_level_state
                (client_id, level, state, updated_by)
                VALUES (?, ?, 'off', 'system')
            """, [client_id, level])
        logger.info(f'  Level states: {len(LEVELS)} (all off)')

        # 3. Insert settings (71 defaults)
        logger.info('--- Seeding settings ---')
        for dep_key in DEPRECATED_SETTINGS:
            con.execute(
                "DELETE FROM act_v2_client_settings WHERE client_id = ? AND setting_key = ?",
                [client_id, dep_key]
            )
        for key, value, stype, level in DEFAULT_SETTINGS:
            con.execute("""
                INSERT OR REPLACE INTO act_v2_client_settings
                (client_id, setting_key, setting_value, setting_type, level)
                VALUES (?, ?, ?, ?, ?)
            """, [client_id, key, value, stype, level])
        settings_count = con.execute(
            "SELECT COUNT(*) FROM act_v2_client_settings WHERE client_id = ?",
            [client_id]
        ).fetchone()[0]
        logger.info(f'  Settings seeded: {settings_count}')

        # 4. Insert 9 standard negative keyword lists
        logger.info('--- Seeding negative keyword lists ---')
        nkl_defs = [
            (f'{client_id}-list-1word-phrase', '1 WORD phrase', 1, 'phrase'),
            (f'{client_id}-list-1word-exact', '1 WORD exact', 1, 'exact'),
            (f'{client_id}-list-2word-phrase', '2 WORDS phrase', 2, 'phrase'),
            (f'{client_id}-list-2word-exact', '2 WORDS exact', 2, 'exact'),
            (f'{client_id}-list-3word-phrase', '3 WORDS phrase', 3, 'phrase'),
            (f'{client_id}-list-3word-exact', '3 WORDS exact', 3, 'exact'),
            (f'{client_id}-list-4word-phrase', '4 WORDS phrase', 4, 'phrase'),
            (f'{client_id}-list-4word-exact', '4 WORDS exact', 4, 'exact'),
            (f'{client_id}-list-5word-exact', '5+ WORDS exact', 5, 'exact'),
        ]
        for list_id, list_name, word_count, match_type in nkl_defs:
            con.execute("""
                INSERT OR REPLACE INTO act_v2_negative_keyword_lists
                (list_id, client_id, google_ads_list_id, list_name,
                 word_count, match_type, keyword_count, last_synced_at)
                VALUES (?, ?, NULL, ?, ?, ?, 0, NULL)
            """, [list_id, client_id, list_name, word_count, match_type])
        nkl_count = con.execute(
            "SELECT COUNT(*) FROM act_v2_negative_keyword_lists WHERE client_id = ?",
            [client_id]
        ).fetchone()[0]
        logger.info(f'  Negative keyword lists: {nkl_count}')

        # Summary
        logger.info('')
        logger.info('=' * 40)
        logger.info(f'ACT v2 Seed — {client_name} Complete')
        logger.info('=' * 40)
        logger.info(f'Client: {client_name} ({client_id})')
        logger.info(f'Customer ID: {customer_id}')
        logger.info(f'Persona: {persona}')
        logger.info(f'Budget: {monthly_budget}')
        logger.info(f'Target: CPA={target_cpa}, ROAS={target_roas}')
        logger.info(f'Level states: {len(LEVELS)}')
        logger.info(f'Settings: {settings_count}')
        logger.info(f'Neg keyword lists: {nkl_count}')
        logger.info('=' * 40)

    except Exception as e:
        logger.error(f'Seed failed: {e}')
        raise
    finally:
        con.close()


def main():
    parser = argparse.ArgumentParser(description='ACT v2 Client Seeder')
    parser.add_argument('--id', required=True, help='Internal client ID (e.g. dbd001)')
    parser.add_argument('--name', required=True, help='Client display name')
    parser.add_argument('--customer-id', required=True, help='Google Ads customer ID (digits only)')
    parser.add_argument('--persona', required=True, choices=['lead_gen_cpa', 'ecommerce_roas'])
    parser.add_argument('--budget', required=True, type=float, help='Monthly budget in GBP')
    parser.add_argument('--target-cpa', type=float, help='Target CPA in GBP (required for lead_gen_cpa)')
    parser.add_argument('--target-roas', type=float, help='Target ROAS (required for ecommerce_roas)')
    args = parser.parse_args()

    if args.persona == 'lead_gen_cpa' and not args.target_cpa:
        parser.error('--target-cpa is required for lead_gen_cpa persona')
    if args.persona == 'ecommerce_roas' and not args.target_roas:
        parser.error('--target-roas is required for ecommerce_roas persona')

    seed_client(
        client_id=args.id,
        client_name=args.name,
        customer_id=args.customer_id,
        persona=args.persona,
        monthly_budget=args.budget,
        target_cpa=args.target_cpa,
        target_roas=args.target_roas,
    )


if __name__ == '__main__':
    main()
