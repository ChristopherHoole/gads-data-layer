"""
ACT v2 Default Settings

Single source of truth for the 71 default client settings.
Used by both the seed script and the reset endpoint.

Each entry: (setting_key, setting_value, setting_type, level)
setting_value is a string (or None for nullable fields).
"""

DEFAULT_SETTINGS = [
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

# Deprecated settings to clean up when re-seeding
DEPRECATED_SETTINGS = [
    'max_single_tcpa_move_pct',
    'max_single_troas_move_pct',
    'troas_adjustment_cooldown_days',
    'tcpa_adjustment_cooldown_days',
]
