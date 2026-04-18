"""
ACT v2 Schema Creation Migration

Creates all act_v2_* tables, sequences, indexes, and populates the act_v2_checks
reference table with all 35 checks from the v54 optimization architecture.

Prerequisites:
- Flask app must be stopped (DuckDB file lock)
- Run from project root: python -m act_dashboard.db.migrations.create_act_v2_schema

Idempotent: can be run multiple times safely.

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
logger = logging.getLogger('act_v2_migration')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

file_handler = logging.FileHandler(LOG_PATH, mode='a', encoding='utf-8')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# ---------------------------------------------------------------------------
# SQL: Sequences (7)
# ---------------------------------------------------------------------------
SEQUENCES = [
    'seq_act_v2_snapshots',
    'seq_act_v2_recommendations',
    'seq_act_v2_executed_actions',
    'seq_act_v2_monitoring',
    'seq_act_v2_alerts',
    'seq_act_v2_search_terms',
    'seq_act_v2_campaign_segments',
    'seq_act_v2_scheduler_runs',
]

# ---------------------------------------------------------------------------
# SQL: Tables (11) — in strict dependency order
# ---------------------------------------------------------------------------
TABLE_SQL = [
    # --- Root tables (no FK dependencies) ---
    (
        'act_v2_clients',
        """
        CREATE TABLE IF NOT EXISTS act_v2_clients (
            client_id VARCHAR PRIMARY KEY,
            google_ads_customer_id VARCHAR(20) UNIQUE NOT NULL,
            client_name VARCHAR(500) NOT NULL,
            persona VARCHAR(50) NOT NULL CHECK (persona IN ('lead_gen_cpa', 'ecommerce_roas')),
            monthly_budget DECIMAL(18,2) NOT NULL,
            target_cpa DECIMAL(10,2),
            target_roas DECIMAL(10,2),
            active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            CHECK (
                (persona = 'lead_gen_cpa' AND target_cpa IS NOT NULL AND target_roas IS NULL) OR
                (persona = 'ecommerce_roas' AND target_roas IS NOT NULL AND target_cpa IS NULL)
            )
        );
        """,
    ),
    (
        'act_v2_checks',
        """
        CREATE TABLE IF NOT EXISTS act_v2_checks (
            check_id VARCHAR(100) PRIMARY KEY,
            level VARCHAR(20) NOT NULL CHECK (level IN ('account', 'campaign', 'ad_group', 'keyword', 'ad', 'shopping')),
            check_name VARCHAR(200) NOT NULL,
            description VARCHAR,
            action_category VARCHAR(20) NOT NULL CHECK (action_category IN ('act', 'monitor', 'investigate', 'alert')),
            auto_execute BOOLEAN NOT NULL DEFAULT FALSE,
            cooldown_hours INTEGER,
            active BOOLEAN NOT NULL DEFAULT TRUE
        );
        """,
    ),
    # --- Tables referencing only clients ---
    (
        'act_v2_client_level_state',
        """
        CREATE TABLE IF NOT EXISTS act_v2_client_level_state (
            client_id VARCHAR NOT NULL,
            level VARCHAR(20) NOT NULL CHECK (level IN ('account', 'campaign', 'ad_group', 'keyword', 'ad', 'shopping')),
            state VARCHAR(20) NOT NULL DEFAULT 'off' CHECK (state IN ('off', 'monitor_only', 'active')),
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_by VARCHAR(100) NOT NULL DEFAULT 'system',
            PRIMARY KEY (client_id, level),
            FOREIGN KEY (client_id) REFERENCES act_v2_clients(client_id)
        );
        """,
    ),
    (
        'act_v2_client_settings',
        """
        CREATE TABLE IF NOT EXISTS act_v2_client_settings (
            client_id VARCHAR NOT NULL,
            setting_key VARCHAR(100) NOT NULL,
            setting_value VARCHAR,
            setting_type VARCHAR(20) NOT NULL CHECK (setting_type IN ('int', 'decimal', 'bool', 'string', 'json')),
            level VARCHAR(20) NOT NULL CHECK (level IN ('account', 'campaign', 'ad_group', 'keyword', 'ad', 'shopping')),
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (client_id, setting_key),
            FOREIGN KEY (client_id) REFERENCES act_v2_clients(client_id)
        );
        """,
    ),
    (
        'act_v2_campaign_roles',
        """
        CREATE TABLE IF NOT EXISTS act_v2_campaign_roles (
            client_id VARCHAR NOT NULL,
            google_ads_campaign_id VARCHAR(30) NOT NULL,
            campaign_name VARCHAR(500),
            role VARCHAR(10) NOT NULL CHECK (role IN ('BD', 'CP', 'RT', 'PR', 'TS')),
            role_assigned_by VARCHAR(100) NOT NULL DEFAULT 'auto',
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (client_id, google_ads_campaign_id),
            FOREIGN KEY (client_id) REFERENCES act_v2_clients(client_id)
        );
        """,
    ),
    (
        'act_v2_negative_keyword_lists',
        """
        CREATE TABLE IF NOT EXISTS act_v2_negative_keyword_lists (
            list_id VARCHAR PRIMARY KEY,
            client_id VARCHAR NOT NULL,
            google_ads_list_id VARCHAR(30),
            list_name VARCHAR(100) NOT NULL,
            word_count INTEGER NOT NULL CHECK (word_count IN (1, 2, 3, 4, 5)),
            match_type VARCHAR(20) NOT NULL CHECK (match_type IN ('exact', 'phrase')),
            keyword_count INTEGER NOT NULL DEFAULT 0,
            last_synced_at TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES act_v2_clients(client_id)
        );
        """,
    ),
    (
        'act_v2_snapshots',
        """
        CREATE TABLE IF NOT EXISTS act_v2_snapshots (
            snapshot_id BIGINT PRIMARY KEY DEFAULT nextval('seq_act_v2_snapshots'),
            client_id VARCHAR NOT NULL,
            snapshot_date DATE NOT NULL,
            level VARCHAR(20) NOT NULL CHECK (level IN ('account', 'campaign', 'ad_group', 'keyword', 'ad', 'product')),
            entity_id VARCHAR(100) NOT NULL,
            entity_name VARCHAR(500),
            parent_entity_id VARCHAR(100),
            metrics_json JSON,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES act_v2_clients(client_id)
        );
        """,
    ),
    (
        'act_v2_alerts',
        """
        CREATE TABLE IF NOT EXISTS act_v2_alerts (
            alert_id BIGINT PRIMARY KEY DEFAULT nextval('seq_act_v2_alerts'),
            client_id VARCHAR NOT NULL,
            level VARCHAR(20) NOT NULL CHECK (level IN ('account', 'campaign', 'ad_group', 'keyword', 'ad', 'shopping')),
            alert_type VARCHAR(50) NOT NULL,
            severity VARCHAR(20) NOT NULL CHECK (severity IN ('info', 'warning', 'critical')),
            title VARCHAR NOT NULL,
            description VARCHAR,
            entity_id VARCHAR(100),
            raised_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            resolved_at TIMESTAMP,
            resolution VARCHAR(30) CHECK (resolution IN ('acknowledged', 'auto_resolved', 'approved_fix')),
            FOREIGN KEY (client_id) REFERENCES act_v2_clients(client_id)
        );
        """,
    ),
    # --- References clients + checks ---
    (
        'act_v2_recommendations',
        """
        CREATE TABLE IF NOT EXISTS act_v2_recommendations (
            recommendation_id BIGINT PRIMARY KEY DEFAULT nextval('seq_act_v2_recommendations'),
            client_id VARCHAR NOT NULL,
            level VARCHAR(20) NOT NULL CHECK (level IN ('account', 'campaign', 'ad_group', 'keyword', 'ad', 'shopping')),
            check_id VARCHAR(100) NOT NULL,
            entity_id VARCHAR(100) NOT NULL,
            entity_name VARCHAR(500),
            parent_entity_id VARCHAR(100),
            action_category VARCHAR(20) NOT NULL CHECK (action_category IN ('act', 'monitor', 'investigate', 'alert')),
            risk_level VARCHAR(20) NOT NULL CHECK (risk_level IN ('low', 'medium', 'high')),
            summary VARCHAR NOT NULL,
            recommendation_text VARCHAR,
            estimated_impact VARCHAR,
            decision_tree_json JSON,
            current_value_json JSON,
            proposed_value_json JSON,
            status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'declined', 'executed', 'rolled_back', 'expired')),
            mode VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (mode IN ('active', 'monitor_only')),
            identified_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            actioned_at TIMESTAMP,
            actioned_by VARCHAR(100),
            FOREIGN KEY (client_id) REFERENCES act_v2_clients(client_id),
            FOREIGN KEY (check_id) REFERENCES act_v2_checks(check_id)
        );
        """,
    ),
    # --- References clients + checks + recommendations ---
    (
        'act_v2_executed_actions',
        """
        CREATE TABLE IF NOT EXISTS act_v2_executed_actions (
            action_id BIGINT PRIMARY KEY DEFAULT nextval('seq_act_v2_executed_actions'),
            client_id VARCHAR NOT NULL,
            recommendation_id BIGINT,
            level VARCHAR(20) NOT NULL CHECK (level IN ('account', 'campaign', 'ad_group', 'keyword', 'ad', 'shopping')),
            check_id VARCHAR(100) NOT NULL,
            entity_id VARCHAR(100) NOT NULL,
            entity_name VARCHAR(500),
            action_type VARCHAR(50) NOT NULL,
            before_value_json JSON,
            after_value_json JSON,
            reason VARCHAR,
            execution_status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (execution_status IN ('success', 'failed', 'pending')),
            error_message VARCHAR,
            executed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            google_ads_api_response JSON,
            FOREIGN KEY (client_id) REFERENCES act_v2_clients(client_id),
            FOREIGN KEY (check_id) REFERENCES act_v2_checks(check_id),
            FOREIGN KEY (recommendation_id) REFERENCES act_v2_recommendations(recommendation_id)
        );
        """,
    ),
    # --- References clients + recommendations + executed_actions ---
    (
        'act_v2_monitoring',
        """
        CREATE TABLE IF NOT EXISTS act_v2_monitoring (
            monitoring_id BIGINT PRIMARY KEY DEFAULT nextval('seq_act_v2_monitoring'),
            client_id VARCHAR NOT NULL,
            recommendation_id BIGINT,
            action_id BIGINT,
            level VARCHAR(20) NOT NULL CHECK (level IN ('account', 'campaign', 'ad_group', 'keyword', 'ad', 'shopping')),
            entity_id VARCHAR(100) NOT NULL,
            monitoring_type VARCHAR(30) NOT NULL CHECK (monitoring_type IN ('cooldown', 'post_action_observation', 'trend_watch')),
            started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            ends_at TIMESTAMP NOT NULL,
            resolved_at TIMESTAMP,
            health_status VARCHAR(30) NOT NULL DEFAULT 'too_early_to_assess' CHECK (health_status IN ('healthy', 'trending_down', 'too_early_to_assess')),
            consecutive_days_stable INTEGER NOT NULL DEFAULT 0,
            metrics_json JSON,
            FOREIGN KEY (client_id) REFERENCES act_v2_clients(client_id),
            FOREIGN KEY (recommendation_id) REFERENCES act_v2_recommendations(recommendation_id),
            FOREIGN KEY (action_id) REFERENCES act_v2_executed_actions(action_id)
        );
        """,
    ),
    # --- A2 additions: search terms and campaign segments ---
    (
        'act_v2_search_terms',
        """
        CREATE TABLE IF NOT EXISTS act_v2_search_terms (
            search_term_id BIGINT PRIMARY KEY DEFAULT nextval('seq_act_v2_search_terms'),
            client_id VARCHAR NOT NULL,
            snapshot_date DATE NOT NULL,
            campaign_id VARCHAR(30) NOT NULL,
            campaign_name VARCHAR(500),
            ad_group_id VARCHAR(30) NOT NULL,
            ad_group_name VARCHAR(500),
            search_term VARCHAR NOT NULL,
            match_type VARCHAR(20),
            keyword_text VARCHAR,
            keyword_id VARCHAR(100),
            cost DECIMAL(18,2),
            impressions INTEGER,
            clicks INTEGER,
            conversions DECIMAL(10,2),
            conversion_value DECIMAL(18,2),
            ctr DECIMAL(10,4),
            avg_cpc DECIMAL(10,2),
            cost_per_conversion DECIMAL(10,2),
            conversion_rate DECIMAL(10,4),
            FOREIGN KEY (client_id) REFERENCES act_v2_clients(client_id)
        );
        """,
    ),
    (
        'act_v2_campaign_segments',
        """
        CREATE TABLE IF NOT EXISTS act_v2_campaign_segments (
            segment_id BIGINT PRIMARY KEY DEFAULT nextval('seq_act_v2_campaign_segments'),
            client_id VARCHAR NOT NULL,
            snapshot_date DATE NOT NULL,
            campaign_id VARCHAR(30) NOT NULL,
            campaign_name VARCHAR(500),
            segment_type VARCHAR(20) NOT NULL CHECK (segment_type IN ('device', 'geo', 'ad_schedule', 'day_of_week')),
            segment_value VARCHAR(200) NOT NULL,
            cost DECIMAL(18,2),
            impressions INTEGER,
            clicks INTEGER,
            conversions DECIMAL(10,2),
            conversion_value DECIMAL(18,2),
            ctr DECIMAL(10,4),
            avg_cpc DECIMAL(10,2),
            cost_per_conversion DECIMAL(10,2),
            conversion_rate DECIMAL(10,4),
            bid_modifier DECIMAL(10,2),
            FOREIGN KEY (client_id) REFERENCES act_v2_clients(client_id)
        );
        """,
    ),
    # --- F1: Scheduler status tracking ---
    (
        'act_v2_scheduler_runs',
        """
        CREATE TABLE IF NOT EXISTS act_v2_scheduler_runs (
            run_id BIGINT PRIMARY KEY DEFAULT nextval('seq_act_v2_scheduler_runs'),
            client_id VARCHAR NOT NULL,
            run_date DATE NOT NULL,
            phase VARCHAR(20) NOT NULL CHECK (phase IN ('ingestion', 'engine')),
            status VARCHAR(20) NOT NULL CHECK (status IN ('running', 'success', 'failed', 'skipped')),
            started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            error_message VARCHAR,
            details_json JSON,
            FOREIGN KEY (client_id) REFERENCES act_v2_clients(client_id)
        );
        """,
    ),
]

# ---------------------------------------------------------------------------
# SQL: Indexes (5)
# ---------------------------------------------------------------------------
INDEX_SQL = [
    (
        'idx_act_v2_snapshots_lookup',
        """CREATE INDEX idx_act_v2_snapshots_lookup
           ON act_v2_snapshots(client_id, snapshot_date, level, entity_id);""",
    ),
    (
        'idx_act_v2_recs_client_status',
        """CREATE INDEX idx_act_v2_recs_client_status
           ON act_v2_recommendations(client_id, status, identified_at);""",
    ),
    (
        'idx_act_v2_actions_client_date',
        """CREATE INDEX idx_act_v2_actions_client_date
           ON act_v2_executed_actions(client_id, executed_at);""",
    ),
    (
        'idx_act_v2_monitoring_active',
        """CREATE INDEX idx_act_v2_monitoring_active
           ON act_v2_monitoring(client_id, resolved_at);""",
    ),
    (
        'idx_act_v2_alerts_client',
        """CREATE INDEX idx_act_v2_alerts_client
           ON act_v2_alerts(client_id, resolved_at, raised_at);""",
    ),
    (
        'idx_act_v2_search_terms_lookup',
        """CREATE INDEX idx_act_v2_search_terms_lookup
           ON act_v2_search_terms(client_id, snapshot_date, campaign_id);""",
    ),
    (
        'idx_act_v2_segments_lookup',
        """CREATE INDEX idx_act_v2_segments_lookup
           ON act_v2_campaign_segments(client_id, snapshot_date, campaign_id, segment_type);""",
    ),
]

# ---------------------------------------------------------------------------
# Checks seed data (35 checks from v54 architecture)
# ---------------------------------------------------------------------------
CHECKS_DATA = [
    # Account Level (1)
    ('account_budget_allocation', 'account', 'Budget Allocation',
     'Reallocates daily budget across campaigns based on performance scoring using a 7-day/14-day/30-day weighted blend to prioritize best-performing campaigns.',
     'act', True, 72),

    # Campaign Level — Universal Levers (5)
    ('campaign_negative_keywords', 'campaign', 'Negative Keywords',
     'Identifies and blocks wasteful search terms with zero conversions or irrelevant patterns to prevent budget waste across all bid strategies.',
     'act', True, None),
    ('campaign_device_modifiers', 'campaign', 'Device Modifiers',
     'Adjusts bid modifiers for mobile, desktop, and tablet based on CPA/ROAS performance variance from account average with 7-day cooldowns.',
     'act', True, 168),
    ('campaign_geo_modifiers', 'campaign', 'Geographic Modifiers',
     'Applies location-based bid adjustments when geographic performance deviates 20%+ from account average CPA/ROAS with 30-day cooldowns.',
     'act', True, 720),
    ('campaign_ad_schedule', 'campaign', 'Ad Schedule Modifiers',
     'Adjusts bid modifiers by time-of-day and day-of-week across 42 individual weekly slots when performance variance exceeds thresholds with 30-day cooldowns.',
     'act', True, 720),
    ('campaign_match_types', 'campaign', 'Match Type Migration',
     'Flags broad match keywords with excessive irrelevant search terms for downgrade to phrase match, and exact match keywords with low volume for expansion testing.',
     'investigate', False, None),

    # Campaign Level — Strategy-Specific (7)
    ('campaign_manual_cpc', 'campaign', 'Manual CPC',
     'Manages campaign-wide settings for Manual CPC campaigns using universal levers; individual keyword bid adjustments are handled at Keyword Level.',
     'act', True, None),
    ('campaign_tcpa', 'campaign', 'Target CPA Adjustment',
     'Adjusts target CPA by maximum 10% per cycle with 14-day cooldowns based on actual CPA vs target; tightening auto-executes, loosening requires approval.',
     'investigate', False, 336),
    ('campaign_troas', 'campaign', 'Target ROAS Adjustment',
     'Adjusts target ROAS by maximum 10% per cycle with 14-day cooldowns based on actual ROAS vs target; tightening auto-executes, loosening requires approval.',
     'investigate', False, 336),
    ('campaign_max_conversions', 'campaign', 'Maximize Conversions',
     'Monitors CPA stability and flags recommendation to graduate to tCPA once CPA has been stable for 21+ days, or alerts if CPA spikes 30%+ in 7 days.',
     'monitor', False, None),
    ('campaign_max_clicks', 'campaign', 'Maximize Clicks',
     'Monitors CPC trends and recommends adding a max CPC cap if volatility increases, or flags switch to conversion-based strategy after 30+ conversions in 30 days.',
     'act', True, 168),
    ('campaign_pmax', 'campaign', 'Performance Max',
     'Manages tCPA/tROAS targets for Performance Max campaigns with maximum 10% changes per cycle and 14-day cooldowns; auto-executes tightening, requires approval for loosening.',
     'monitor', False, None),
    ('campaign_standard_shopping', 'campaign', 'Standard Shopping',
     'Manages product-level optimization for Standard Shopping campaigns including product tiering, search term mining, exclusions, and best seller budget maximization.',
     'act', True, None),

    # Ad Group Level (4)
    ('ag_negative_outlier', 'ad_group', 'Negative Performance Outlier',
     'Flags ad groups with zero conversions after 30%+ of campaign spend over 14+ days, or CPA/ROAS 50%+ worse than campaign average as underperformers.',
     'investigate', False, None),
    ('ag_positive_outlier', 'ad_group', 'Positive Performance Outlier',
     'Identifies ad groups with CPA/ROAS 40%+ better than campaign average for 21+ days with 100+ clicks as potential candidates for standalone campaigns.',
     'investigate', False, None),
    ('ag_budget_concentration', 'ad_group', 'Budget Concentration Alert',
     'Alerts when one ad group consumes 80%+ of campaign spend (2-ad-group scenarios) or 50%+ (3+ scenarios) over 14+ days, indicating budget starvation.',
     'alert', False, None),
    ('ag_pause_recommendation', 'ad_group', 'Pause Recommendation',
     'Recommends pausing ad groups with zero conversions over 21+ days despite significant spend, zero impressions for 30+ days, or sustained underperformance.',
     'investigate', False, None),

    # Keyword Level (8)
    ('kw_performance_monitoring', 'keyword', 'Keyword Performance Monitoring',
     'Monitors keyword CPA/ROAS against target range and auto-adjusts bids (Manual CPC only) or auto-pauses dead/zero-converting keywords.',
     'act', True, None),
    ('kw_search_term_negatives', 'keyword', 'Search Term Mining - Negatives',
     'Identifies search terms with spend exceeding 1x CPA target with zero conversions over 14+ days or irrelevant patterns and auto-adds as negative keywords.',
     'act', True, None),
    ('kw_search_term_discovery', 'keyword', 'Search Term Mining - Discovery',
     'Flags high-performing search terms with 2+ conversions below target CPA or 50+ clicks with good CTR as candidates for addition as phrase match keywords.',
     'investigate', False, None),
    ('kw_quality_score', 'keyword', 'Quality Score Monitoring',
     'Monitors individual keyword quality scores on a configurable weekly scan schedule and flags keywords below QS 4 for ad relevance and landing page improvements.',
     'alert', False, None),
    ('kw_status_monitoring', 'keyword', 'Keyword Status Monitoring',
     'Surfaces Google keyword status flags indicating problems (below first page bid, rarely shown due to low QS) that require human review and action.',
     'alert', False, None),
    ('kw_conflicts', 'keyword', 'Keyword Conflicts & Cannibalisation',
     'Detects duplicate keywords in different ad groups or campaigns that compete against each other and flags for consolidation or removal.',
     'investigate', False, None),
    ('kw_pause_recommendation', 'keyword', 'Keyword Pause Recommendation',
     'Auto-pauses keywords with zero impressions for 60+ days or spend exceeding 1x CPA target with zero conversions for 14+ days; flags high-CPA converting keywords for approval.',
     'investigate', False, None),
    ('kw_bid_management', 'keyword', 'Keyword Bid Management',
     'Adjusts Manual CPC keyword bids by maximum 10% per cycle with 72-hour cooldowns based on keyword CPA vs target, with maximum 30% change in any 7-day period.',
     'act', True, 72),

    # Ad Level (6)
    ('ad_strength_monitoring', 'ad', 'Ad Strength Monitoring',
     'Monitors Google Ad Strength score for RSAs on a weekly schedule and flags ads below Good strength for headline/description improvements.',
     'investigate', False, None),
    ('ad_rsa_asset_performance', 'ad', 'RSA Asset Performance',
     'Identifies individual RSA headline and description assets rated Low for 30+ days on a weekly scan and flags for replacement with new variations.',
     'investigate', False, None),
    ('ad_count_per_ad_group', 'ad', 'Ad Count per Ad Group',
     'Monitors live ad count in each ad group on a weekly schedule, alerting when fewer than 3 live ads exist or zero ads are present.',
     'investigate', False, None),
    ('ad_performance_comparison', 'ad', 'Ad Performance Comparison',
     'Compares ad performance within each ad group on a weekly scan and flags the worst performing ad if CTR/CVR is 30%+ worse than best ad for 21+ days.',
     'investigate', False, None),
    ('ad_disapprovals', 'ad', 'Ad Disapprovals',
     'Checks for disapproved ads every overnight cycle and flags immediately for policy violation fixes or creation of new compliant replacements.',
     'alert', False, None),
    ('ad_extensions_monitoring', 'ad', 'Ad Extensions Monitoring',
     'Scans extensions on a weekly schedule and flags when sitelinks < 4, callouts < 4, structured snippets absent, or call extensions missing.',
     'investigate', False, None),

    # Shopping Level (4)
    ('shop_search_term_negatives', 'shopping', 'Shopping Search Term Mining',
     'Identifies shopping search terms with spend exceeding configurable threshold and zero conversions over 14+ days or irrelevant patterns, and auto-adds as negatives.',
     'act', True, None),
    ('shop_product_tiers', 'shopping', 'Product Performance Tiers',
     'Classifies products into four performance tiers (Best Sellers/Mid-Range/Underperformers/Losers) using multi-window weighted blend of revenue and ROAS.',
     'act', True, 72),
    ('shop_product_exclusions', 'shopping', 'Product Exclusion Recommendations',
     'Recommends excluding products with spend exceeding configurable threshold and zero conversions for 21+ days, or ROAS 50%+ below target for 21+ days.',
     'investigate', False, None),
    ('shop_best_seller_maximisation', 'shopping', 'Best Seller Budget Maximisation',
     'Raises product group bids by 10% per cycle (72-hour cooldown) for best-selling products with ROAS above target and Impression Share lost to budget > 0.',
     'act', True, 72),
]


def main():
    logger.info('=' * 50)
    logger.info('ACT v2 Schema Migration — Starting')
    logger.info('=' * 50)
    logger.info(f'Database: {DB_PATH}')

    # Connect to DuckDB
    try:
        con = duckdb.connect(DB_PATH)
    except duckdb.IOException as e:
        logger.error(f'ERROR: Database is locked. Stop the Flask app first:')
        logger.error(f'  taskkill /IM python.exe /F')
        logger.error(f'Then re-run this migration.')
        sys.exit(1)

    try:
        # 1. Create sequences
        logger.info('--- Creating sequences ---')
        for seq_name in SEQUENCES:
            con.execute(f'CREATE SEQUENCE IF NOT EXISTS {seq_name};')
            logger.info(f'  Sequence: {seq_name}')
        logger.info(f'Sequences created: {len(SEQUENCES)}')

        # 2. Create tables in dependency order
        logger.info('--- Creating tables ---')
        for table_name, sql in TABLE_SQL:
            con.execute(sql)
            logger.info(f'  Table: {table_name}')
        logger.info(f'Tables created: {len(TABLE_SQL)}')

        # 3. Create indexes
        logger.info('--- Creating indexes ---')
        for idx_name, sql in INDEX_SQL:
            # Check if index already exists before creating
            existing = con.execute(
                "SELECT index_name FROM duckdb_indexes() WHERE index_name = ?",
                [idx_name]
            ).fetchall()
            if not existing:
                con.execute(sql)
                logger.info(f'  Index: {idx_name} (created)')
            else:
                logger.info(f'  Index: {idx_name} (already exists)')
        logger.info(f'Indexes processed: {len(INDEX_SQL)}')

        # 4. Populate checks
        logger.info('--- Populating act_v2_checks (35 checks) ---')
        for check in CHECKS_DATA:
            check_id, level, check_name, description, action_cat, auto_exec, cooldown = check
            con.execute(
                """INSERT OR REPLACE INTO act_v2_checks
                   (check_id, level, check_name, description, action_category, auto_execute, cooldown_hours, active)
                   VALUES (?, ?, ?, ?, ?, ?, ?, TRUE)""",
                [check_id, level, check_name, description, action_cat, auto_exec, cooldown]
            )
        check_count = con.execute('SELECT COUNT(*) FROM act_v2_checks').fetchone()[0]
        logger.info(f'Checks populated: {check_count}')

        # Summary
        logger.info('')
        logger.info('=' * 40)
        logger.info('ACT v2 Schema Migration Complete')
        logger.info('=' * 40)
        logger.info(f'Tables created: {len(TABLE_SQL)}')
        logger.info(f'Sequences created: {len(SEQUENCES)}')
        logger.info(f'Indexes created: {len(INDEX_SQL)}')
        logger.info(f'Checks populated: {check_count}')
        logger.info('=' * 40)

    except Exception as e:
        logger.error(f'Migration failed: {e}')
        raise
    finally:
        con.close()


if __name__ == '__main__':
    main()
