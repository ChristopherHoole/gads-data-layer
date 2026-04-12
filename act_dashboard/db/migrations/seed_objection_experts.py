"""
ACT v2 Seed Data — Objection Experts

Seeds the first client (Objection Experts) with:
- Client record in act_v2_clients
- 6 level states (all OFF) in act_v2_client_level_state
- 45 settings in act_v2_client_settings
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

# 45 settings: (setting_key, setting_value, setting_type, level)
SETTINGS = [
    # Account-Level Settings (20)
    ('budget_allocation_mode', 'automatic', 'string', 'account'),
    ('budget_shift_cooldown_hours', '72', 'int', 'account'),
    ('max_overnight_budget_move_pct', '10', 'int', 'account'),
    ('performance_scoring_weight_7d', '50', 'int', 'account'),
    ('performance_scoring_weight_14d', '30', 'int', 'account'),
    ('performance_scoring_weight_30d', '20', 'int', 'account'),
    ('signal_window_cpc_days', '7', 'int', 'account'),
    ('signal_window_cvr_days', '14', 'int', 'account'),
    ('signal_window_aov_days', '30', 'int', 'account'),
    ('deviation_threshold_pct', '10', 'int', 'account'),
    ('budget_band_bd_min_pct', '2', 'int', 'account'),
    ('budget_band_bd_max_pct', '8', 'int', 'account'),
    ('budget_band_cp_min_pct', '40', 'int', 'account'),
    ('budget_band_cp_max_pct', '70', 'int', 'account'),
    ('budget_band_rt_min_pct', '5', 'int', 'account'),
    ('budget_band_rt_max_pct', '15', 'int', 'account'),
    ('budget_band_pr_min_pct', '10', 'int', 'account'),
    ('budget_band_pr_max_pct', '30', 'int', 'account'),
    ('budget_band_ts_min_pct', '2', 'int', 'account'),
    ('budget_band_ts_max_pct', '10', 'int', 'account'),

    # Campaign-Level Settings (21)
    ('device_mod_min_pct', '-60', 'int', 'campaign'),
    ('device_mod_max_pct', '30', 'int', 'campaign'),
    ('geo_mod_min_pct', '-50', 'int', 'campaign'),
    ('geo_mod_max_pct', '30', 'int', 'campaign'),
    ('schedule_mod_min_pct', '-50', 'int', 'campaign'),
    ('schedule_mod_max_pct', '25', 'int', 'campaign'),
    ('tcpa_troas_target_cooldown_days', '14', 'int', 'campaign'),
    ('max_cpc_cap_cooldown_days', '7', 'int', 'campaign'),
    ('device_bid_cooldown_days', '7', 'int', 'campaign'),
    ('geo_bid_cooldown_days', '30', 'int', 'campaign'),
    ('schedule_bid_cooldown_days', '30', 'int', 'campaign'),
    ('match_type_migration_enabled', 'true', 'bool', 'campaign'),
    ('search_partners_optout_check_enabled', 'true', 'bool', 'campaign'),
    ('cpc_absolute_floor', '0.10', 'decimal', 'campaign'),
    ('cpc_absolute_ceiling', '5.00', 'decimal', 'campaign'),
    ('tcpa_absolute_floor', None, 'decimal', 'campaign'),
    ('tcpa_absolute_ceiling', None, 'decimal', 'campaign'),
    ('troas_absolute_floor', None, 'decimal', 'campaign'),
    ('troas_absolute_ceiling', None, 'decimal', 'campaign'),
    ('per_cycle_bid_modifier_change_pct', '10', 'int', 'campaign'),
    ('seven_day_max_bid_change_pct', '30', 'int', 'campaign'),

    # Keyword-Level Settings (8)
    ('keyword_bid_adjustment_per_cycle_pct', '10', 'int', 'keyword'),
    ('keyword_bid_cooldown_hours', '72', 'int', 'keyword'),
    ('keyword_bid_7day_cap_pct', '30', 'int', 'keyword'),
    ('auto_pause_spend_multiplier', '1', 'int', 'keyword'),
    ('auto_pause_days_threshold', '14', 'int', 'keyword'),
    ('quality_score_alert_threshold', '4', 'int', 'keyword'),
    ('dead_keyword_days_threshold', '60', 'int', 'keyword'),
    ('quality_score_scan_frequency', 'weekly', 'string', 'keyword'),

    # Ad Group-Level Settings (6)
    ('negative_outlier_spend_pct', '30', 'int', 'ad_group'),
    ('negative_outlier_performance_pct', '50', 'int', 'ad_group'),
    ('positive_outlier_performance_pct', '40', 'int', 'ad_group'),
    ('pause_inactive_days_threshold', '30', 'int', 'ad_group'),
    ('budget_concentration_threshold_2ag_pct', '80', 'int', 'ad_group'),
    ('budget_concentration_threshold_3ag_pct', '50', 'int', 'ad_group'),

    # Ad-Level Settings (10)
    ('ad_scan_frequency', 'weekly', 'string', 'ad'),
    ('ad_strength_minimum', 'good', 'string', 'ad'),
    ('rsa_asset_low_rated_days_threshold', '30', 'int', 'ad'),
    ('min_ads_per_ad_group', '3', 'int', 'ad'),
    ('ad_performance_comparison_pct', '30', 'int', 'ad'),
    ('ad_minimum_days_live', '14', 'int', 'ad'),
    ('min_sitelinks', '4', 'int', 'ad'),
    ('min_callout_extensions', '4', 'int', 'ad'),
    ('min_structured_snippets', '1', 'int', 'ad'),
    ('require_call_extension', 'true', 'bool', 'ad'),

    # Shopping-Level Settings (6)
    ('product_spend_threshold', '50.00', 'decimal', 'shopping'),
    ('product_bid_adjustment_per_cycle_pct', '10', 'int', 'shopping'),
    ('product_bid_cooldown_hours', '72', 'int', 'shopping'),
    ('product_bid_7day_cap_pct', '30', 'int', 'shopping'),
    ('best_seller_tier_pct', '20', 'int', 'shopping'),
    ('underperformer_roas_threshold_pct', '50', 'int', 'shopping'),
]

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
        deprecated = [
            'max_single_tcpa_move_pct',
            'max_single_troas_move_pct',
            'troas_adjustment_cooldown_days',
            'tcpa_adjustment_cooldown_days',
        ]
        for dep_key in deprecated:
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
