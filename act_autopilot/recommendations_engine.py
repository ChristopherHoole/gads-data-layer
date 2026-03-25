"""
Recommendations Engine — Chat 27 (M6) + Chat 47 Multi-Entity Extension

Reads enabled rules from rules_config.json, evaluates each rule against
entity data (campaigns, keywords, ad_groups, shopping) in the database,
and writes new pending recommendations to the `recommendations` table.

Usage:
    from act_autopilot.recommendations_engine import run_recommendations_engine
    result = run_recommendations_engine(customer_id="9999999999", db_path="warehouse.duckdb")

Returns dict:
    {
        "generated": N,
        "skipped_duplicate": N,
        "skipped_no_data": N,
        "skipped_no_target": N,
        "skipped_no_table": N,
        "errors": [...],
        "customer_id": "...",
        "by_entity_type": {"campaign": N, "keyword": N, ...}
    }

Architecture (Chat 47):
    - Writable connection to warehouse.duckdb
    - ATTACH warehouse_readonly.duckdb as ro
    - Queries 4 entity data sources based on rule_type:
        * campaigns → ro.analytics.campaign_features_daily
        * keywords  → ro.analytics.keyword_daily
        * ad_groups → ro.analytics.ad_group_daily
        * shopping  → ro.analytics.shopping_campaign_daily
    - Ads skipped (table doesn't exist in database)
    - Graceful degradation: missing tables/columns handled
"""

import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import duckdb

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_HERE = Path(__file__).parent
RULES_CONFIG_PATH = _HERE / "rules_config.json"

# ---------------------------------------------------------------------------
# Operator normalisation (DB conditions Format B → engine short codes)
# ---------------------------------------------------------------------------
OP_MAP = {">": "gt", ">=": "gte", "<": "lt", "<=": "lte", "=": "eq", "==": "eq"}

# ---------------------------------------------------------------------------
# action_type → action_direction mapping (DB → engine)
# ---------------------------------------------------------------------------
ACTION_MAP = {
    # Campaign actions
    "increase_budget":     "increase",
    "decrease_budget":     "decrease",
    "increase_troas":      "increase",
    "decrease_troas":      "decrease",
    "increase_target_cpa": "increase",
    "decrease_target_cpa": "decrease",
    "increase_max_cpc":    "increase",
    "decrease_max_cpc":    "decrease",
    # Ad group actions
    "increase_cpc_bid":    "increase",
    "decrease_cpc_bid":    "decrease",
    "increase_tcpa_target":"increase",
    "decrease_tcpa_target":"decrease",
    "pause_ad_group":      "pause",
    "enable_ad_group":     "enable",
    # Keyword actions
    "increase_bid":        "increase",
    "decrease_bid":        "decrease",
    "increase_bid_to_first_page": "increase",
    "pause":               "pause",
    "enable":              "enable",
    # Ad actions
    "pause_ad":            "pause",
    "enable_ad":           "enable",
    # Shopping actions
    "increase_shopping_budget": "increase",
    "decrease_shopping_budget": "decrease",
    "pause_shopping":      "pause",
    "enable_shopping":     "enable",
    "increase_product_bid":"increase",
    "decrease_product_bid":"decrease",
    "decrease_target_roas":"decrease",
    # Generic
    "flag":                "flag",
    "hold":                "hold",
}

# ---------------------------------------------------------------------------
# Entity Type Configuration (Chat 47)
# Maps entity types to their database tables
# ---------------------------------------------------------------------------

ENTITY_TABLES = {
    "campaign": "ro.analytics.campaign_features_daily",
    "keyword":  "ro.analytics.keyword_daily",
    "ad_group": "ro.analytics.ad_group_daily",
    "shopping": "ro.analytics.shopping_campaign_daily",
    "ad":       "ro.analytics.ad_features_daily",
    "product":  "ro.analytics.product_features_daily",
}

# Entity ID and Name column mappings
ENTITY_ID_COLUMNS = {
    "campaign": ("campaign_id", "campaign_name"),
    "keyword":  ("keyword_id", "keyword_text"),
    "ad_group": ("ad_group_id", "ad_group_name"),
    "shopping": ("campaign_id", "campaign_name"),  # Shopping uses campaign-level data
    "ad":       ("ad_id", "ad_name"),
    "product":  ("product_id", "product_title"),
}

# ---------------------------------------------------------------------------
# Metric → DB column mapping (CAMPAIGNS)
# Proxy columns used when original flag columns don't exist in features table.
# ---------------------------------------------------------------------------

# Maps rule condition_metric → (db_column, override_operator, override_threshold)
# override_operator / override_threshold = None means use rule's own values
CAMPAIGN_METRIC_MAP = {
    # ── ROAS ──────────────────────────────────────────────────────────────────
    "roas_7d":              ("roas_w7_mean",             None, None),
    "roas_14d":             ("roas_w14_mean",            None, None),
    "roas_30d":             ("roas_w30_mean",            None, None),

    # ── CPA (micros → divide by 1,000,000 to get £) ──────────────────────────
    "cpa_7d":               ("cpa_w7_mean",              None, None, 1_000_000),
    "cpa_14d":              ("cpa_w14_mean",             None, None, 1_000_000),
    "cpa_30d":              ("cpa_w30_mean",             None, None, 1_000_000),

    # ── CTR ───────────────────────────────────────────────────────────────────
    "ctr_7d":               ("ctr_w7_mean",              None, None),
    "ctr_14d":              ("ctr_w14_mean",             None, None),
    "ctr_30d":              ("ctr_w30_mean",             None, None),

    # ── Avg CPC (micros → divide by 1,000,000 to get £) ──────────────────────
    "cpc_avg_7d":           ("cpc_w7_mean",              None, None, 1_000_000),
    "cpc_avg_14d":          ("cpc_w14_mean",             None, None, 1_000_000),
    "cpc_avg_30d":          ("cpc_w30_mean",             None, None, 1_000_000),

    # ── Clicks ────────────────────────────────────────────────────────────────
    "clicks_7d":            ("clicks_w7_sum",            None, None),
    "clicks_14d":           ("clicks_w14_sum",           None, None),
    "clicks_30d":           ("clicks_w30_sum",           None, None),

    # ── Conversions ───────────────────────────────────────────────────────────
    "conversions_7d":       ("conversions_w7_sum",       None, None),
    "conversions_14d":      ("conversions_w14_sum",      None, None),
    "conversions_30d":      ("conversions_w30_sum",      None, None),

    # ── Cost (micros → divide by 1,000,000 to get £) ─────────────────────────
    "cost_7d":              ("cost_micros_w7_sum",       None, None, 1_000_000),
    "cost_14d":             ("cost_micros_w14_sum",      None, None, 1_000_000),
    "cost_30d":             ("cost_micros_w30_sum",      None, None, 1_000_000),

    # ── Impressions ───────────────────────────────────────────────────────────
    "impressions_7d":       ("impressions_w7_sum",       None, None),
    "impressions_14d":      ("impressions_w14_sum",      None, None),
    "impressions_30d":      ("impressions_w30_sum",      None, None),

    # ── Pacing & impression share ─────────────────────────────────────────────
    "pacing_vs_cap":        ("acct_pacing_vs_cap_pct",   None, None),
    "impression_share_lost_rank": ("impression_share_lost_rank", None, None),

    # ── Week-on-week % change ─────────────────────────────────────────────────
    "roas_w7_vs_prev_pct":              ("roas_w7_vs_prev_pct",             None, None),
    "cpa_w7_vs_prev_pct":               ("cpa_w7_vs_prev_pct",              None, None),
    "ctr_w7_vs_prev_pct":               ("ctr_w7_vs_prev_pct",              None, None),
    "cpc_w7_vs_prev_pct":               ("cpc_w7_vs_prev_pct",              None, None),
    "cvr_w7_vs_prev_pct":               ("cvr_w7_vs_prev_pct",              None, None),
    "conversions_w7_vs_prev_pct":       ("conversions_w7_vs_prev_pct",      None, None),
    "cost_w7_vs_prev_pct":              ("cost_micros_w7_vs_prev_pct",      None, None),
    "impression_share_w7_vs_prev_pct":  ("impressions_w7_vs_prev_pct",      None, None),

    # ── Legacy cv/volatility ──────────────────────────────────────────────────
    "cost_cv_14d":          ("cost_w14_cv",              None, None),

    # ── System signals (fixed operator/threshold) ─────────────────────────────
    "cost_spike_confidence":  ("anomaly_cost_z",         "gte",  2.0),
    "cost_drop_detected":     ("anomaly_cost_z",         "lte", -2.0),
    "pace_over_cap_detected": ("pacing_flag_over_105",   "eq",   True),
    "click_z_score":          ("anomaly_cost_z",         "gte",  2.0),   # proxy until click z added
    "cost_z_score":           ("anomaly_cost_z",         "gte",  2.0),
    "impression_z_score":     ("anomaly_cost_z",         "gte",  2.0),   # proxy until impr z added
    "ctr_drop_detected":      ("ctr_w7_vs_prev_pct",     "lt",  -20.0),
    "cvr_drop_detected":      ("cvr_w7_vs_prev_pct",     "lt",  -20.0),
    "conv_tracking_loss_detected": ("conversions_w7_sum","lte",  0.0),   # proxy
    "landing_page_status":    ("pacing_flag_over_105",   "eq",   False), # proxy
    "landing_page_load_ms":   ("pacing_flag_over_105",   "eq",   False), # proxy
    "ads_disapproved_count":  ("pacing_flag_over_105",   "eq",   False), # proxy
    "billing_issue_detected": ("pacing_flag_over_105",   "eq",   False), # proxy
    "tracking_tag_present":   ("pacing_flag_over_105",   "eq",   False), # proxy
    "budget_exhausted_hour":  ("pacing_flag_over_105",   "eq",   True),  # proxy
}

# ---------------------------------------------------------------------------
# Metric → DB column mapping (KEYWORDS) - Chat 47
# Based on schema investigation: quality_score, bid_micros, cost, conversions, ctr, roas, etc.
# ---------------------------------------------------------------------------

KEYWORD_METRIC_MAP = {
    "quality_score":    ("quality_score", None, None),  # INTEGER field
    "cost":             ("cost", None, None),           # DOUBLE field (already in currency)
    "conversions":      ("conversions", None, None),    # DOUBLE field
    "ctr":              ("ctr", None, None),            # DOUBLE field
    "roas":             ("roas", None, None),           # DOUBLE field  
    "impressions":      ("impressions", None, None),    # BIGINT field
    "clicks":           ("clicks", None, None),         # BIGINT field
}

# ---------------------------------------------------------------------------
# Metric → DB column mapping (AD GROUPS) - Chat 47
# Based on schema investigation: ctr, cost, conversions, roas, etc.
# ---------------------------------------------------------------------------

AD_GROUP_METRIC_MAP = {
    # ── Basic columns (direct) ─────────────────────────────────────────────
    "cost":             ("cost", None, None),
    "conversions":      ("conversions", None, None),
    "ctr":              ("ctr", None, None),
    "roas":             ("roas", None, None),
    "cpa":              ("cpa", None, None),
    "cpc":              ("cpc", None, None),
    "impressions":      ("impressions", None, None),
    "clicks":           ("clicks", None, None),
    "search_impression_share":           ("search_impression_share", None, None),
    "search_top_impression_share":       ("search_top_impression_share", None, None),
    "impression_share_lost_rank":        ("search_impression_share", None, None),  # proxy
    "impression_share_lost_budget":      ("search_impression_share", None, None),  # proxy
    "optimization_score":                ("optimization_score", None, None),

    # ── Windowed aliases (UI sends these — map to raw daily columns) ───────
    # The ad_group_daily table has only raw daily data, not windowed averages.
    # These mappings let rules created via the UI (which use windowed names)
    # evaluate against the most recent daily snapshot.
    "roas_w7_mean":     ("roas", None, None),
    "roas_w14_mean":    ("roas", None, None),
    "roas_w30_mean":    ("roas", None, None),
    "cpa_w7_mean":      ("cpa", None, None),
    "cpa_w14_mean":     ("cpa", None, None),
    "cpa_w30_mean":     ("cpa", None, None),
    "ctr_w7_mean":      ("ctr", None, None),
    "ctr_w14_mean":     ("ctr", None, None),
    "ctr_w30_mean":     ("ctr", None, None),
    "cpc_w7_mean":      ("cpc", None, None),
    "cpc_w14_mean":     ("cpc", None, None),
    "cpc_w30_mean":     ("cpc", None, None),
    "clicks_w7_sum":    ("clicks", None, None),
    "clicks_w14_sum":   ("clicks", None, None),
    "clicks_w30_sum":   ("clicks", None, None),
    "conversions_w7_sum":  ("conversions", None, None),
    "conversions_w14_sum": ("conversions", None, None),
    "conversions_w30_sum": ("conversions", None, None),
    "cost_w7_sum":      ("cost", None, None),
    "cost_w14_sum":     ("cost", None, None),
    "cost_w30_sum":     ("cost", None, None),
    "impressions_w7_sum":  ("impressions", None, None),
    "impressions_w14_sum": ("impressions", None, None),
    "impressions_w30_sum": ("impressions", None, None),

    # ── Week-on-week % change (proxied to raw — no WoW in ad_group_daily) ──
    "roas_wow_pct":        ("roas", None, None),
    "cpa_wow_pct":         ("cpa", None, None),
    "ctr_wow_pct":         ("ctr", None, None),
    "cvr_wow_pct":         ("ctr", None, None),  # proxy
    "conversions_wow_pct": ("conversions", None, None),
    "cost_wow_pct":        ("cost", None, None),

    # ── Anomaly / volatility (proxied) ─────────────────────────────────────
    "cost_z":           ("cost", None, None),  # proxy
    "clicks_z":         ("clicks", None, None),  # proxy
    "conversions_z":    ("conversions", None, None),  # proxy
    "cost_cv":          ("cost", None, None),  # proxy
    "clicks_cv":        ("clicks", None, None),  # proxy

    # ── System ─────────────────────────────────────────────────────────────
    "low_data_flag":    ("clicks", "lte", 5.0),
}

# ---------------------------------------------------------------------------
# Metric → DB column mapping (SHOPPING) - Chat 47
# Based on schema investigation: cost, conversions, ctr, roas, optimization_score
# NOTE: feed_error_count and out_of_stock_product_count do NOT exist
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Metric → DB column mapping (ADS) - Chat 88
# Based on analytics.ad_daily schema: ctr, impressions, ad_strength, roas, conversions
# ---------------------------------------------------------------------------

AD_METRIC_MAP = {
    # ── Direct columns from ad_features_daily ────────────────────────────────
    "ctr":         ("ctr_7d",       None, None),   # DOUBLE (decimal, e.g. 0.05 = 5%)
    "impressions": ("impressions_7d", None, None), # BIGINT
    "ad_strength": ("ad_strength",  None, None),   # VARCHAR (POOR/AVERAGE/GOOD/EXCELLENT)
    "roas":        ("roas_7d",      None, None),   # DOUBLE
    "conversions": ("conversions_7d", None, None), # DOUBLE
    "clicks":      ("clicks_7d",    None, None),   # BIGINT
    "cost":        ("cost_micros_7d", None, None, 1_000_000),  # BIGINT (micros)

    # ── Windowed aliases (UI sends these — map to ad_features_daily columns) ─
    "ctr_w7_mean":      ("ctr_7d",      None, None),
    "ctr_w14_mean":     ("ctr_7d",      None, None),   # 14d not in features, use 7d
    "ctr_w30_mean":     ("ctr_30d",     None, None),
    "roas_w7_mean":     ("roas_7d",     None, None),
    "roas_w14_mean":    ("roas_7d",     None, None),   # 14d not in features, use 7d
    "roas_w30_mean":    ("roas_30d",    None, None),
    "cpa_w7_mean":      ("cpa_7d",      None, None, 1_000_000),
    "cpa_w14_mean":     ("cpa_7d",      None, None, 1_000_000),   # 14d not in features, use 7d
    "cpa_w30_mean":     ("cpa_30d",     None, None, 1_000_000),
    "clicks_w7_sum":    ("clicks_7d",   None, None),
    "clicks_w14_sum":   ("clicks_14d",  None, None),
    "clicks_w30_sum":   ("clicks_30d",  None, None),
    "conversions_w7_sum":  ("conversions_7d",  None, None),
    "conversions_w14_sum": ("conversions_14d", None, None),
    "conversions_w30_sum": ("conversions_30d", None, None),
    "cost_w7_sum":      ("cost_micros_7d",  None, None, 1_000_000),
    "cost_w14_sum":     ("cost_micros_14d", None, None, 1_000_000),
    "cost_w30_sum":     ("cost_micros_30d", None, None, 1_000_000),
    "impressions_w7_sum":  ("impressions_7d",  None, None),
    "impressions_w14_sum": ("impressions_14d", None, None),
    "impressions_w30_sum": ("impressions_30d", None, None),

    # ── Trend columns ────────────────────────────────────────────────────────
    "ctr_w7_vs_prev_pct":  ("ctr_trend_7d_vs_30d",  None, None),
    "cvr_w7_vs_prev_pct":  ("cvr_trend_7d_vs_30d",  None, None),

    # ── System ───────────────────────────────────────────────────────────────
    "low_data_flag":    ("low_data_flag", None, None),
}

SHOPPING_METRIC_MAP = {
    # ── Direct columns ───────────────────────────────────────────────────────
    "cost":                ("cost_micros", None, None, 1_000_000),
    "conversions":         ("conversions", None, None),
    "ctr":                 ("ctr", None, None),
    "roas":                ("roas", None, None),
    "impressions":         ("impressions", None, None),
    "clicks":              ("clicks", None, None),
    "optimization_score":  ("optimization_score", None, None),
    "search_impression_share": ("search_impression_share", None, None),

    # ── _Nd aliases (Shopping rules use roas_7d, conversions_7d, cost_7d) ────
    "roas_7d":          ("roas", None, None),
    "roas_14d":         ("roas", None, None),
    "roas_30d":         ("roas", None, None),
    "conversions_7d":   ("conversions", None, None),
    "conversions_14d":  ("conversions", None, None),
    "conversions_30d":  ("conversions", None, None),
    "cost_7d":          ("cost_micros", None, None, 1_000_000),
    "cost_14d":         ("cost_micros", None, None, 1_000_000),
    "cost_30d":         ("cost_micros", None, None, 1_000_000),
    "clicks_7d":        ("clicks", None, None),
    "impressions_7d":   ("impressions", None, None),
    "ctr_7d":           ("ctr", None, None),

    # ── Windowed aliases (in case UI sends these) ────────────────────────────
    "roas_w7_mean":     ("roas", None, None),
    "roas_w14_mean":    ("roas", None, None),
    "roas_w30_mean":    ("roas", None, None),
    "ctr_w7_mean":      ("ctr", None, None),
    "clicks_w7_sum":    ("clicks", None, None),
    "conversions_w7_sum":  ("conversions", None, None),
    "cost_w7_sum":      ("cost_micros", None, None, 1_000_000),
    "impressions_w7_sum":  ("impressions", None, None),
}

# ---------------------------------------------------------------------------
# Metric → DB column mapping (PRODUCTS) - Chat 113
# Based on analytics.product_features_daily which has full windowed columns
# ---------------------------------------------------------------------------

PRODUCT_METRIC_MAP = {
    # ── Direct columns ───────────────────────────────────────────────────────
    "roas":            ("roas_w7", None, None),
    "impressions":     ("impressions_w7_sum", None, None),
    "clicks":          ("clicks_w7_sum", None, None),
    "conversions":     ("conversions_w7_sum", None, None),
    "cost":            ("cost_micros_w7_sum", None, None, 1_000_000),

    # ── Windowed aliases ─────────────────────────────────────────────────────
    "roas_w7_mean":     ("roas_w7",  None, None),
    "roas_w14_mean":    ("roas_w14", None, None),
    "roas_w30_mean":    ("roas_w30", None, None),
    "clicks_w7_sum":    ("clicks_w7_sum",  None, None),
    "clicks_w14_sum":   ("clicks_w14_sum", None, None),
    "clicks_w30_sum":   ("clicks_w30_sum", None, None),
    "conversions_w7_sum":  ("conversions_w7_sum",  None, None),
    "conversions_w14_sum": ("conversions_w14_sum", None, None),
    "conversions_w30_sum": ("conversions_w30_sum", None, None),
    "cost_w7_sum":      ("cost_micros_w7_sum",  None, None, 1_000_000),
    "cost_w14_sum":     ("cost_micros_w14_sum", None, None, 1_000_000),
    "cost_w30_sum":     ("cost_micros_w30_sum", None, None, 1_000_000),
    "impressions_w7_sum":  ("impressions_w7_sum",  None, None),
    "impressions_w14_sum": ("impressions_w14_sum", None, None),
    "impressions_w30_sum": ("impressions_w30_sum", None, None),
    "conversions_value_w7_sum":  ("conversions_value_w7_sum",  None, None),
    "conversions_value_w14_sum": ("conversions_value_w14_sum", None, None),
    "conversions_value_w30_sum": ("conversions_value_w30_sum", None, None),

    # ── Direct short aliases (product rules use roas_w7, cpa_w7, ctr_w7) ────
    "roas_w7":          ("roas_w7",  None, None),
    "roas_w14":         ("roas_w14", None, None),
    "roas_w30":         ("roas_w30", None, None),
    "cpa_w7":           ("cpa_w7",   None, None),
    "cpa_w14":          ("cpa_w14",  None, None),
    "cpa_w30":          ("cpa_w30",  None, None),
    "ctr_w7":           ("ctr_w7",   None, None),
    "ctr_w14":          ("ctr_w14",  None, None),
    "ctr_w30":          ("ctr_w30",  None, None),
    "cvr_w7":           ("cvr_w7",   None, None),

    # ── Product-specific columns ─────────────────────────────────────────────
    "feed_quality_score":  ("feed_quality_score",  None, None),
    "stock_out_flag":      ("stock_out_flag",      None, None),
    "stock_out_days_w30":  ("stock_out_days_w30",  None, None),
    "has_price_mismatch":  ("has_price_mismatch",  None, None),
    "has_disapproval":     ("has_disapproval",     None, None),
    "availability":        ("availability",        None, None),
    "cost_w14_cv":         ("cost_w14_cv",         None, None),

    # ── System ───────────────────────────────────────────────────────────────
    "low_data_flag":    ("clicks_w7_sum", "lte", 5.0),
}

# Consolidated metric map selector
def _get_metric_map_for_entity(entity_type: str) -> dict:
    """Return appropriate metric map for entity type."""
    if entity_type == "campaign":
        return CAMPAIGN_METRIC_MAP
    elif entity_type == "keyword":
        return KEYWORD_METRIC_MAP
    elif entity_type == "ad_group":
        return AD_GROUP_METRIC_MAP
    elif entity_type == "shopping":
        return SHOPPING_METRIC_MAP
    elif entity_type == "ad":
        return AD_METRIC_MAP
    elif entity_type == "product":
        return PRODUCT_METRIC_MAP
    else:
        return {}

PROXY_METRICS = {
    "cost_spike_confidence", "cost_drop_detected",
    "pace_over_cap_detected", "ctr_drop_detected", "cvr_drop_detected",
}

# Confidence from risk_level
RISK_TO_CONFIDENCE = {
    "low":    "high",
    "medium": "medium",
    "high":   "low",
}

# ---------------------------------------------------------------------------
# Entity Type Detection (Chat 47)
# ---------------------------------------------------------------------------

def _detect_entity_type(rule_id: str) -> str:
    """
    Detect entity type from rule_id.
    Examples: "campaign_1" -> "campaign", "keyword_3" -> "keyword",
              "ad_group_1" -> "ad_group", "ad_1" -> "ad",
              "db_campaign_7" -> "campaign", "db_ad_group_59" -> "ad_group"

    Note: "ad_group" must be checked before "ad" since both share the "ad" prefix.
    """
    if "_" not in rule_id:
        return "campaign"  # fallback

    # Strip "db_" prefix from DB-loaded rules for cleaner detection
    clean_id = rule_id[3:] if rule_id.startswith("db_") else rule_id

    # "ad_group" rules — check before generic split
    if clean_id.startswith("ad_group_"):
        return "ad_group"

    entity_type = clean_id.split("_")[0]

    # Validate known types
    if entity_type in ("campaign", "keyword", "ad", "shopping", "product"):
        return entity_type

    return "campaign"  # fallback for unknown types


def _table_exists(conn, table_name: str) -> bool:
    """Check if table exists in database."""
    try:
        conn.execute(f"SELECT 1 FROM {table_name} LIMIT 1")
        return True
    except:
        return False


# ---------------------------------------------------------------------------
# DB Campaign Rule Loader (Chat 95)
# ---------------------------------------------------------------------------

def _normalise_operator(op_str: str) -> str:
    """Convert symbolic operators to engine short-codes via OP_MAP."""
    return OP_MAP.get(op_str or "", op_str or "gte")


def _load_db_rules(conn, entity_type: str = "campaign") -> list:
    """
    Load enabled rules from the DB rules table for a given entity type.
    Returns a list of rule dicts normalised to the engine's internal format.
    Handles both condition schemas (op/ref and operator/unit).
    """
    rules = []
    try:
        rows = conn.execute("""
            SELECT id, name, type, campaign_type_lock,
                   conditions, action_type, action_magnitude,
                   cooldown_days, risk_level
            FROM rules
            WHERE entity_type = ?
              AND rule_or_flag = 'rule'
              AND is_template = FALSE
              AND enabled = TRUE
        """, [entity_type]).fetchall()
    except Exception as e:
        print(f"[ENGINE] ERROR querying DB {entity_type} rules: {e}")
        return rules

    col_names = [
        "id", "name", "type", "campaign_type_lock",
        "conditions", "action_type", "action_magnitude",
        "cooldown_days", "risk_level",
    ]

    for row in rows:
        rd = dict(zip(col_names, row))

        # Parse conditions JSON safely
        try:
            conds_raw = rd["conditions"]
            conditions = json.loads(conds_raw) if isinstance(conds_raw, str) else (conds_raw or [])
        except Exception as e:
            print(f"[ENGINE] WARNING: Skipping rule {rd['id']} — bad conditions JSON: {e}")
            continue

        if not conditions:
            print(f"[ENGINE] WARNING: Skipping rule {rd['id']} — empty conditions")
            continue

        # Normalise condition 1
        c1 = conditions[0]
        op1  = c1.get("op") or _normalise_operator(c1.get("operator", ""))
        ref1 = c1.get("ref") or c1.get("unit") or "absolute"
        raw_val1 = c1.get("value", 0)
        try:
            val1 = float(raw_val1)
        except (TypeError, ValueError):
            val1 = raw_val1  # Keep as string for 'in' operator etc.

        # Normalise condition 2 (optional)
        c2 = conditions[1] if len(conditions) > 1 else None
        cond2_metric = cond2_op = cond2_val = None
        if c2:
            cond2_metric = c2.get("metric")
            cond2_op     = c2.get("op") or _normalise_operator(c2.get("operator", ""))
            raw_val2 = c2.get("value", 0)
            try:
                cond2_val = float(raw_val2)
            except (TypeError, ValueError):
                cond2_val = raw_val2  # Keep as string for 'in' operator etc.

        action_direction = ACTION_MAP.get(rd["action_type"] or "", rd["action_type"] or "hold")
        try:
            magnitude = float(rd["action_magnitude"]) if rd["action_magnitude"] is not None else 0.0
        except (TypeError, ValueError):
            magnitude = 0.0

        rules.append({
            "rule_id":              f"db_{entity_type}_{rd['id']}",
            "rule_type":            rd["type"] or "budget",
            "condition_metric":     c1.get("metric"),
            "condition_operator":   op1,
            "condition_value":      val1,
            "condition_unit":       ref1,
            "condition_2_metric":   cond2_metric,
            "condition_2_operator": cond2_op,
            "condition_2_value":    cond2_val,
            "action_direction":     action_direction,
            "action_magnitude":     magnitude,
            "risk_level":           rd["risk_level"] or "medium",
            "cooldown_days":        rd["cooldown_days"] or 7,
            "campaign_type_lock":   rd["campaign_type_lock"] or "all",
        })

    print(f"[ENGINE] Loaded {len(rules)} {entity_type} rules from DB")
    return rules


# ---------------------------------------------------------------------------
# Operator evaluation
# ---------------------------------------------------------------------------

def _evaluate(value, operator, threshold) -> bool:
    """Evaluate value op threshold. Returns False if value is None."""
    if value is None:
        return False
    try:
        if operator == "gt":  return float(value) >  float(threshold)
        if operator == "gte": return float(value) >= float(threshold)
        if operator == "lt":  return float(value) <  float(threshold)
        if operator == "lte": return float(value) <= float(threshold)
        if operator == "eq":
            # Handle string comparisons (e.g., ad_strength = "POOR")
            if isinstance(threshold, str):
                return str(value) == threshold
            if isinstance(threshold, bool):
                return bool(value) == threshold
            return float(value) == float(threshold)
        if operator == "in":
            # Handle "in" operator for comma-separated string lists
            # Supports both "GOOD,EXCELLENT" and "['POOR', 'AVERAGE']" formats
            import re
            cleaned = re.sub(r"[\[\]'\"]", "", str(threshold))
            allowed = [s.strip() for s in cleaned.split(",") if s.strip()]
            return str(value).strip() in allowed
    except (TypeError, ValueError):
        return False
    return False


# ---------------------------------------------------------------------------
# Metric fetching helpers
# ---------------------------------------------------------------------------

def _get_metric_value(features: dict, metric_name: str, metric_map: dict) -> tuple[Any, str]:
    """
    Resolve metric_name to a value using provided metric_map.
    Returns (value, db_column_used). Applies divisor if entry has 4th element.
    """
    if metric_name not in metric_map:
        return None, metric_name

    entry = metric_map[metric_name]
    db_col = entry[0]
    divisor = entry[3] if len(entry) > 3 else 1
    value = features.get(db_col)
    if value is not None and divisor and divisor != 1:
        value = float(value) / divisor
    return value, db_col


def _evaluate_condition(features: dict, metric: str, operator: str, threshold, metric_map: dict) -> tuple[bool, str]:
    """
    Evaluate a single condition. Handles proxy overrides.
    Returns (passed, description_for_summary).
    """
    if not metric:
        return True, ""

    if metric not in metric_map:
        return False, "unknown metric"

    entry = metric_map[metric]
    db_col, override_op, override_threshold = entry[0], entry[1], entry[2]
    divisor = entry[3] if len(entry) > 3 else 1
    value = features.get(db_col)
    if value is not None and divisor != 1:
        value = float(value) / divisor

    # Use proxy operator/threshold if this is a flag metric
    effective_op = override_op if override_op else operator
    effective_threshold = override_threshold if override_threshold is not None else threshold

    passed = _evaluate(value, effective_op, effective_threshold)

    # Human-readable description for trigger_summary
    if value is None:
        desc = "{} = NULL".format(db_col)
    elif isinstance(value, bool):
        desc = "{} = {}".format(db_col, value)
    elif isinstance(value, str):
        desc = "{} = {}".format(db_col, value)
    elif isinstance(effective_threshold, float) and effective_threshold < 0:
        desc = "{} {:.1f}%".format(db_col, float(value))
    else:
        try:
            desc = "{} {:.2f}".format(db_col, float(value))
        except (TypeError, ValueError):
            desc = "{} = {}".format(db_col, value)

    return passed, desc


# ---------------------------------------------------------------------------
# Proposed value calculation
# ---------------------------------------------------------------------------

def _calculate_proposed_value(rule: dict, current_value: float) -> float:
    """
    Calculate proposed_value from current_value and rule action.
    hold/flag rules: proposed = current (no change).
    """
    direction = rule["action_direction"]
    magnitude = rule.get("action_magnitude", 0) or 0

    if direction == "increase":
        return round(current_value * (1 + magnitude / 100.0), 4)
    elif direction == "decrease":
        return round(current_value * (1 - magnitude / 100.0), 4)
    else:
        # hold or flag — no change
        return round(current_value, 4)


# ---------------------------------------------------------------------------
# Current value extraction (entity-specific)
# ---------------------------------------------------------------------------

def _get_current_value(entity_type: str, rule_type: str, features: dict) -> float:
    """
    Extract current_value based on entity type and rule type.
    
    For campaigns: budget (cost proxy) or target_roas
    For keywords: bid_micros
    For ad_groups: cpc_bid_micros  
    For shopping: cost_micros (budget proxy)
    """
    if entity_type == "campaign":
        if rule_type == "budget":
            # Use cost_micros_w7_mean as budget proxy
            cost_micros_mean = features.get("cost_micros_w7_mean")
            if cost_micros_mean and float(cost_micros_mean) > 0:
                return float(cost_micros_mean) / 1_000_000
            return 50.0  # fallback
        else:
            # bid/status rules use target_roas
            return 4.0  # target_roas fallback
    
    elif entity_type == "keyword":
        # Keywords: use bid_micros
        bid_micros = features.get("bid_micros")
        if bid_micros and float(bid_micros) > 0:
            return float(bid_micros) / 1_000_000
        return 0.50  # fallback £0.50
    
    elif entity_type == "ad_group":
        # Ad groups: use cpc_bid_micros
        cpc_bid = features.get("cpc_bid_micros")
        if cpc_bid and float(cpc_bid) > 0:
            return float(cpc_bid) / 1_000_000
        return 1.0  # fallback £1.00
    
    elif entity_type == "shopping":
        # Shopping: use cost_micros as budget proxy
        cost_micros = features.get("cost_micros")
        if cost_micros and float(cost_micros) > 0:
            return float(cost_micros) / 1_000_000
        return 100.0  # fallback £100

    elif entity_type == "ad":
        # Ads: use cost as spend proxy
        cost = features.get("cost")
        if cost and float(cost) > 0:
            return float(cost)
        return 10.0  # fallback £10

    return 0.0  # unknown entity type


# ---------------------------------------------------------------------------
# Trigger summary builder
# ---------------------------------------------------------------------------

def _build_trigger_summary(rule: dict, features: dict, target_roas: float, metric_map: dict) -> str:
    """Build the human-readable trigger summary string."""
    parts = []

    metric = rule["condition_metric"]
    op     = rule["condition_operator"]
    val    = rule["condition_value"]
    unit   = rule.get("condition_unit", "absolute")

    _passed, desc = _evaluate_condition(features, metric, op, val, metric_map)

    if unit == "x_target":
        threshold_display = "{:.2f}x (target {:.1f}x x {:.2f})".format(
            target_roas * val, target_roas, val
        )
        # Get actual value for display
        db_col = metric_map.get(metric, (metric,))[0]
        actual = features.get(db_col)
        if actual is not None:
            try:
                parts.append("ROAS {:.2f}x {} {}".format(float(actual), op, threshold_display))
            except (TypeError, ValueError):
                parts.append(desc)
        else:
            parts.append(desc)
    else:
        parts.append(desc)

    # Add condition 2 if present
    metric2 = rule.get("condition_2_metric")
    if metric2:
        _passed2, desc2 = _evaluate_condition(
            features, metric2, rule["condition_2_operator"],
            rule["condition_2_value"], metric_map
        )
        if desc2:
            parts.append(desc2)

    return " AND ".join(parts) if parts else "Triggered"


# ---------------------------------------------------------------------------
# Flag Engine (Chat 101)
# ---------------------------------------------------------------------------

def _run_flag_engine(conn, customer_id: str):
    """
    Evaluate all enabled flag rules and insert new flags into the `flags` table.
    Uses same CAMPAIGN_METRIC_MAP, _evaluate_condition(), and MAX(snapshot_date)
    pattern as the rules engine. Called at end of run_recommendations_engine().
    """
    print("\n[FLAGS ENGINE] Starting flag evaluation...")

    # --- Load enabled flag rules from DB ---
    try:
        rows = conn.execute("""
            SELECT id, name, entity_type, conditions, cooldown_days, risk_level, plain_english
            FROM rules
            WHERE rule_or_flag = 'flag'
              AND enabled = TRUE
              AND is_template = FALSE
        """).fetchall()
    except Exception as e:
        print(f"[FLAGS ENGINE] ERROR querying flag rules: {e}")
        return

    if not rows:
        print("[FLAGS ENGINE] No enabled flag rules found.")
        return

    col_names = ["id", "name", "entity_type", "conditions", "cooldown_days", "risk_level", "plain_english"]
    flag_rules = []
    for row in rows:
        rd = dict(zip(col_names, row))
        try:
            conds_raw = rd["conditions"]
            conditions = json.loads(conds_raw) if isinstance(conds_raw, str) else (conds_raw or [])
        except Exception as e:
            print(f"[FLAGS ENGINE] WARNING: Skipping rule {rd['id']} — bad conditions JSON: {e}")
            continue

        if not conditions:
            continue

        c1 = conditions[0]
        op1 = c1.get("op") or _normalise_operator(c1.get("operator", ""))
        raw_val1 = c1.get("value", 0)
        try:
            val1 = float(raw_val1)
        except (TypeError, ValueError):
            val1 = raw_val1  # Keep as string for 'in' operator etc.

        c2 = conditions[1] if len(conditions) > 1 else None
        cond2_metric = cond2_op = cond2_val = None
        if c2:
            cond2_metric = c2.get("metric")
            cond2_op = c2.get("op") or _normalise_operator(c2.get("operator", ""))
            raw_val2 = c2.get("value", 0)
            try:
                cond2_val = float(raw_val2)
            except (TypeError, ValueError):
                cond2_val = raw_val2  # Keep as string for 'in' operator etc.

        flag_rules.append({
            "rule_id":              f"db_{rd['entity_type'] or 'campaign'}_{rd['id']}",
            "rule_name":            rd["name"],
            "entity_type":          rd["entity_type"] or "campaign",
            "condition_metric":     c1.get("metric"),
            "condition_operator":   op1,
            "condition_value":      val1,
            "condition_unit":       "absolute",
            "condition_2_metric":   cond2_metric,
            "condition_2_operator": cond2_op,
            "condition_2_value":    cond2_val,
            "cooldown_days":        rd["cooldown_days"] or 7,
            "severity":             rd["risk_level"] or "medium",
            "plain_english":        rd["plain_english"] or "",
            "conditions_json":      rd["conditions"] or "[]",
        })

    print(f"[FLAGS ENGINE] Loaded {len(flag_rules)} flag rules")

    # --- Group rules by entity type ---
    rules_by_entity: dict = {}
    for rule in flag_rules:
        et = rule["entity_type"]
        rules_by_entity.setdefault(et, []).append(rule)

    # --- Load existing active/snoozed flags for duplicate prevention ---
    now = datetime.now()
    try:
        existing_rows = conn.execute("""
            SELECT rule_id, entity_id, status, snooze_until
            FROM flags
            WHERE customer_id = ?
              AND status IN ('active', 'snoozed')
        """, [customer_id]).fetchall()

        existing_skip = set()  # (rule_id, entity_id) keys to skip
        for r in existing_rows:
            rule_id_db, entity_id_db, status_db, snooze_until_db = r
            key = (rule_id_db, str(entity_id_db) if entity_id_db else "")
            if status_db == "active":
                existing_skip.add(key)
            elif status_db == "snoozed" and snooze_until_db and snooze_until_db > now:
                existing_skip.add(key)
    except Exception as e:
        print(f"[FLAGS ENGINE] WARNING: Could not fetch existing flags: {e}")
        existing_skip = set()

    # --- Process each entity type ---
    generated = 0
    skipped_dup = 0
    skipped_no_data = 0
    new_flags = []

    for entity_type, rules in rules_by_entity.items():
        if entity_type not in ENTITY_TABLES:
            print(f"[FLAGS ENGINE] Unknown entity type: {entity_type} — skipping")
            continue

        table_name = ENTITY_TABLES[entity_type]
        metric_map = _get_metric_map_for_entity(entity_type)
        id_col, name_col = ENTITY_ID_COLUMNS.get(entity_type, ("id", "name"))

        if not _table_exists(conn, table_name):
            print(f"[FLAGS ENGINE] Table {table_name} not found — skipping {entity_type}")
            continue

        # Query latest entity data (Chat 100 pattern)
        try:
            query = f"""
                SELECT * FROM {table_name}
                WHERE customer_id = ?
                  AND snapshot_date = (
                      SELECT MAX(snapshot_date)
                      FROM {table_name}
                      WHERE customer_id = ?
                        AND {name_col} IS NOT NULL
                  )
                ORDER BY {id_col}
            """
            entity_data = conn.execute(query, [customer_id, customer_id]).df()
            print(f"[FLAGS ENGINE] Loaded {len(entity_data)} {entity_type} rows")
        except Exception as e:
            print(f"[FLAGS ENGINE] ERROR querying {table_name}: {e}")
            continue

        if entity_data.empty:
            continue

        for _, entity_row in entity_data.iterrows():
            features = entity_row.to_dict()
            raw_eid = features.get(id_col, 0)
            try:
                entity_id = str(int(raw_eid))
            except (ValueError, TypeError):
                entity_id = str(raw_eid)
            entity_name = features.get(name_col) or f"{entity_type}_{entity_id}"

            for rule in rules:
                rule_id = rule["rule_id"]
                key = (rule_id, entity_id)

                # Duplicate prevention
                if key in existing_skip:
                    skipped_dup += 1
                    continue

                # Evaluate primary condition
                metric = rule["condition_metric"]
                if not metric or metric not in metric_map:
                    skipped_no_data += 1
                    continue

                entry = metric_map[metric]
                db_col = entry[0]
                override_op = entry[1]
                override_threshold = entry[2]
                divisor = entry[3] if len(entry) > 3 else 1
                actual = features.get(db_col)
                if actual is not None and divisor != 1:
                    actual = float(actual) / divisor

                if actual is None:
                    skipped_no_data += 1
                    continue

                eff_op = override_op if override_op else rule["condition_operator"]
                eff_threshold = override_threshold if override_threshold is not None else rule["condition_value"]

                if not _evaluate(actual, eff_op, eff_threshold):
                    continue

                # Evaluate secondary condition (if present)
                metric2 = rule["condition_2_metric"]
                if metric2:
                    if metric2 not in metric_map:
                        skipped_no_data += 1
                        continue

                    entry2 = metric_map[metric2]
                    db_col2 = entry2[0]
                    override_op2 = entry2[1]
                    override_threshold2 = entry2[2]
                    divisor2 = entry2[3] if len(entry2) > 3 else 1
                    actual2 = features.get(db_col2)
                    if actual2 is not None and divisor2 != 1:
                        actual2 = float(actual2) / divisor2

                    if actual2 is None:
                        skipped_no_data += 1
                        continue

                    eff_op2 = override_op2 if override_op2 else rule["condition_2_operator"]
                    eff_threshold2 = override_threshold2 if override_threshold2 is not None else rule["condition_2_value"]

                    if not _evaluate(actual2, eff_op2, eff_threshold2):
                        continue

                # Both conditions passed — build trigger summary
                trigger_summary = _build_trigger_summary(rule, features, 4.0, metric_map)
                severity = rule["severity"]
                flag_id = str(uuid.uuid4())

                print(f"[FLAGS ENGINE] Generated: {rule_id} | {entity_type} {entity_id} | severity={severity}")

                new_flags.append({
                    "flag_id":        flag_id,
                    "rule_id":        rule_id,
                    "rule_name":      rule["rule_name"],
                    "entity_type":    entity_type,
                    "entity_id":      entity_id,
                    "entity_name":    entity_name,
                    "customer_id":    customer_id,
                    "status":         "active",
                    "severity":       severity,
                    "trigger_summary": trigger_summary,
                    "plain_english":  rule["plain_english"],
                    "conditions":     rule["conditions_json"],
                    "generated_at":   now,
                    "acknowledged_at": None,
                    "snooze_until":   None,
                    "snooze_days":    None,
                    "updated_at":     now,
                })
                existing_skip.add(key)
                generated += 1

    # --- Bulk insert flags ---
    if new_flags:
        conn.executemany("""
            INSERT INTO flags (
                flag_id, rule_id, rule_name, entity_type, entity_id, entity_name,
                customer_id, status, severity, trigger_summary, plain_english, conditions,
                generated_at, acknowledged_at, snooze_until, snooze_days, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            (
                f["flag_id"], f["rule_id"], f["rule_name"],
                f["entity_type"], f["entity_id"], f["entity_name"],
                f["customer_id"], f["status"], f["severity"],
                f["trigger_summary"], f["plain_english"], f["conditions"],
                f["generated_at"], f["acknowledged_at"], f["snooze_until"],
                f["snooze_days"], f["updated_at"],
            )
            for f in new_flags
        ])
        print(f"[FLAGS ENGINE] Inserted {len(new_flags)} flags")

    print(f"[FLAGS ENGINE] Done. Generated={generated} | SkippedDuplicate={skipped_dup} | SkippedNoData={skipped_no_data}")


# ---------------------------------------------------------------------------
# Main Engine Function
# ---------------------------------------------------------------------------

def run_recommendations_engine(
    customer_id: str = "9999999999",
    db_path: str = "warehouse.duckdb",
    readonly_path: str = "warehouse_readonly.duckdb",
) -> dict:
    """
    Run the recommendations engine for all enabled rules across all entity types.
    
    Returns dict with generation stats.
    """
    print("\n" + "="*80)
    print("RECOMMENDATIONS ENGINE — MULTI-ENTITY (Chat 47)")
    print("="*80)
    print("Customer ID: {}".format(customer_id))
    print("Database: {}".format(db_path))

    # --- Load non-campaign rules from JSON ----------------------------------
    # Campaign rules are now the DB source of truth; exclude them from JSON.
    with open(RULES_CONFIG_PATH, "r", encoding="utf-8") as f:
        rules_data = json.load(f)

    json_enabled = [r for r in rules_data if r.get("enabled", False)]
    json_non_campaign = [
        r for r in json_enabled
        if _detect_entity_type(r["rule_id"]) != "campaign"
    ]
    print("[ENGINE] Loaded {} rules from rules_config.json (non-campaign only)".format(
        len(json_non_campaign)))

    # --- Connect to database ------------------------------------------------
    conn = duckdb.connect(db_path)
    conn.execute(f"ATTACH '{readonly_path}' AS ro (READ_ONLY)")
    print("[ENGINE] Connected to warehouse + attached readonly")

    # --- Load rules from DB for ALL entity types -----------------------------
    db_rules_all = []
    for etype in ENTITY_TABLES.keys():
        db_rules = _load_db_rules(conn, etype)
        db_rules_all.extend(db_rules)

    # --- Group all rules by entity type -------------------------------------
    all_rules = json_non_campaign + db_rules_all
    rules_by_entity = {}
    for rule in all_rules:
        entity_type = _detect_entity_type(rule["rule_id"])
        if entity_type not in rules_by_entity:
            rules_by_entity[entity_type] = []
        rules_by_entity[entity_type].append(rule)

    print("[ENGINE] Rules by entity type:")
    for entity_type, rules in rules_by_entity.items():
        print("  - {}: {} rules".format(entity_type, len(rules)))

    # --- Check table availability -------------------------------------------
    available_entities = {}
    for entity_type, table_name in ENTITY_TABLES.items():
        if _table_exists(conn, table_name):
            available_entities[entity_type] = table_name
            print(f"[ENGINE] [OK] {entity_type}: {table_name} available")
        else:
            print(f"[ENGINE] [NO] {entity_type}: {table_name} NOT FOUND - will skip")

    # --- Get existing pending recommendations for duplicate check -----------
    try:
        existing_rows = conn.execute("""
            SELECT entity_id, rule_id 
            FROM recommendations 
            WHERE status = 'pending'
            AND customer_id = ?
        """, [customer_id]).fetchall()
        
        existing_pending = set()
        for row in existing_rows:
            entity_id_str = str(row[0]) if row[0] else None
            if entity_id_str:
                existing_pending.add((entity_id_str, row[1]))
    except Exception as e:
        print("[ENGINE] WARNING: Could not fetch existing pending recs: {}".format(e))
        existing_pending = set()

    print("[ENGINE] {} existing pending recs (duplicate check)".format(len(existing_pending)))

    # --- Process each entity type -------------------------------------------
    generated        = 0
    skipped_duplicate = 0
    skipped_no_data  = 0
    skipped_no_table = 0
    errors           = []
    new_recs         = []
    by_entity_type   = {}
    now              = datetime.now()
    _warned_locks    = set()  # track campaign_type_lock warnings already emitted

    for entity_type, entity_rules in rules_by_entity.items():
        
        # Skip if table doesn't exist
        if entity_type not in available_entities:
            print(f"[ENGINE] Skipping {entity_type} - table not available")
            skipped_no_table += len(entity_rules)
            continue

        table_name = available_entities[entity_type]
        metric_map = _get_metric_map_for_entity(entity_type)
        id_col, name_col = ENTITY_ID_COLUMNS.get(entity_type, ("id", "name"))

        print(f"\n[ENGINE] Processing {entity_type} ({len(entity_rules)} rules)...")

        # Query entity data
        try:
            query = f"""
                SELECT * FROM {table_name}
                WHERE customer_id = ?
                  AND snapshot_date = (
                      SELECT MAX(snapshot_date)
                      FROM {table_name}
                      WHERE customer_id = ?
                        AND {name_col} IS NOT NULL
                  )
                ORDER BY {id_col}
            """
            entity_data = conn.execute(query, [customer_id, customer_id]).df()
            print(f"[ENGINE] Loaded {len(entity_data)} {entity_type} rows")
            print(f"[ENGINE] Using snapshot_date: {entity_data['snapshot_date'].iloc[0] if not entity_data.empty else 'N/A'}")
        except Exception as e:
            print(f"[ENGINE] ERROR querying {table_name}: {e}")
            errors.append(str(e))
            continue

        if entity_data.empty:
            print(f"[ENGINE] No data for {entity_type}")
            continue

        # Process each entity row
        for _, entity_row in entity_data.iterrows():
            features = entity_row.to_dict()
            raw_eid = features.get(id_col, 0)
            try:
                entity_id = str(int(raw_eid))
            except (ValueError, TypeError):
                entity_id = str(raw_eid)
            entity_name = features.get(name_col) or f"{entity_type}_{entity_id}"

            # Get campaign_id for backward compatibility
            raw_cid = features.get("campaign_id", 0)
            try:
                campaign_id = str(int(raw_cid))
            except (ValueError, TypeError):
                campaign_id = str(raw_cid)

            for rule in entity_rules:
                rule_id = rule["rule_id"]
                rule_type = rule["rule_type"]

                # Skip if pending rec already exists
                if (entity_id, rule_id) in existing_pending:
                    skipped_duplicate += 1
                    continue

                # --- campaign_type_lock check (DB campaign rules only) -------
                # bid_strategy_type values from Google Ads API:
                # TARGET_ROAS, TARGET_CPA, MANUAL_CPC, MAXIMIZE_CONVERSIONS,
                # MAXIMIZE_CONVERSION_VALUE, None
                LOCK_TO_STRATEGY = {
                    "troas":      "TARGET_ROAS",
                    "tcpa":       "TARGET_CPA",
                    "max_clicks": "MANUAL_CPC",
                }
                if entity_type == "campaign":
                    lock = rule.get("campaign_type_lock", "all")
                    if lock != "all":
                        bid_strategy = features.get("bid_strategy_type")
                        if bid_strategy is not None:
                            expected = LOCK_TO_STRATEGY.get(lock)
                            if expected and bid_strategy != expected:
                                continue
                        else:
                            if lock not in _warned_locks:
                                print(
                                    f"[ENGINE] WARNING: campaign_type_lock='{lock}' cannot be "
                                    f"enforced — bid_strategy_type is NULL for this campaign."
                                )
                                _warned_locks.add(lock)

                # --- Evaluate primary condition -----------------------------
                metric = rule["condition_metric"]
                operator = rule["condition_operator"]
                value = rule["condition_value"]
                unit = rule.get("condition_unit", "absolute")

                # Check metric exists in map
                if metric not in metric_map:
                    skipped_no_data += 1
                    continue

                _entry = metric_map[metric]
                db_col, override_op, override_threshold = _entry[0], _entry[1], _entry[2]
                _divisor = _entry[3] if len(_entry) > 3 else 1
                actual_value = features.get(db_col)
                if actual_value is not None and _divisor != 1:
                    actual_value = float(actual_value) / _divisor

                if actual_value is None:
                    skipped_no_data += 1
                    continue

                # Determine effective operator and threshold
                eff_op = override_op if override_op else operator
                eff_threshold = override_threshold if override_threshold is not None else value

                # Handle x_target unit
                if unit == "x_target":
                    target_roas = 4.0  # fallback
                    eff_threshold = value * target_roas

                cond1_passed = _evaluate(actual_value, eff_op, eff_threshold)

                if not cond1_passed:
                    continue

                # --- Evaluate secondary condition (if present) --------------
                metric2 = rule.get("condition_2_metric")
                if metric2:
                    op2 = rule["condition_2_operator"]
                    val2 = rule["condition_2_value"]

                    if metric2 not in metric_map:
                        skipped_no_data += 1
                        continue

                    _entry2 = metric_map[metric2]
                    db_col2, override_op2, override_threshold2 = _entry2[0], _entry2[1], _entry2[2]
                    _divisor2 = _entry2[3] if len(_entry2) > 3 else 1
                    actual2 = features.get(db_col2)
                    if actual2 is not None and _divisor2 != 1:
                        actual2 = float(actual2) / _divisor2

                    if actual2 is None:
                        skipped_no_data += 1
                        continue

                    eff_op2 = override_op2 if override_op2 else op2
                    eff_threshold2 = override_threshold2 if override_threshold2 is not None else val2

                    cond2_passed = _evaluate(actual2, eff_op2, eff_threshold2)
                    if not cond2_passed:
                        continue

                # --- Both conditions passed - build recommendation ----------
                current_value = _get_current_value(entity_type, rule_type, features)
                proposed_value = _calculate_proposed_value(rule, current_value)
                trigger_summary = _build_trigger_summary(rule, features, 4.0, metric_map)
                confidence = RISK_TO_CONFIDENCE.get(rule.get("risk_level", "medium"), "medium")

                rec = {
                    "rec_id": str(uuid.uuid4()),
                    "rule_id": rule_id,
                    "rule_type": rule_type,
                    "campaign_id": campaign_id,  # For backward compatibility
                    "campaign_name": features.get("campaign_name", ""),  # For backward compatibility
                    "entity_type": entity_type,  # NEW (Chat 47)
                    "entity_id": entity_id,       # NEW (Chat 47)
                    "entity_name": entity_name,   # NEW (Chat 47)
                    "customer_id": customer_id,
                    "status": "pending",
                    "action_direction": rule["action_direction"],
                    "action_magnitude": rule.get("action_magnitude", 0),
                    "current_value": round(current_value, 4),
                    "proposed_value": round(proposed_value, 4),
                    "trigger_summary": trigger_summary,
                    "confidence": confidence,
                    "generated_at": now,
                    "accepted_at": None,
                    "monitoring_ends_at": None,
                    "resolved_at": None,
                    "outcome_metric": None,
                    "created_at": now,
                    "updated_at": now,
                }

                new_recs.append(rec)
                existing_pending.add((entity_id, rule_id))
                generated += 1
                by_entity_type[entity_type] = by_entity_type.get(entity_type, 0) + 1

                print(f"[ENGINE] Generated: {rule_id} | {entity_type} {entity_id} | {rule['action_direction']}")

    # --- Bulk insert --------------------------------------------------------
    if new_recs:
        conn.executemany("""
            INSERT INTO recommendations (
                rec_id, rule_id, rule_type, campaign_id, campaign_name,
                entity_type, entity_id, entity_name,
                customer_id, status, action_direction, action_magnitude,
                current_value, proposed_value, trigger_summary, confidence,
                generated_at, accepted_at, monitoring_ends_at, resolved_at,
                outcome_metric, created_at, updated_at
            ) VALUES (
                ?, ?, ?, ?, ?,
                ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?
            )
        """, [
            (
                r["rec_id"], r["rule_id"], r["rule_type"],
                r["campaign_id"], r["campaign_name"],
                r["entity_type"], r["entity_id"], r["entity_name"],
                r["customer_id"], r["status"], r["action_direction"], r["action_magnitude"],
                r["current_value"], r["proposed_value"], r["trigger_summary"],
                r["confidence"], r["generated_at"], r["accepted_at"],
                r["monitoring_ends_at"], r["resolved_at"], r["outcome_metric"],
                r["created_at"], r["updated_at"],
            )
            for r in new_recs
        ])
        print(f"[ENGINE] Inserted {len(new_recs)} recommendations")

    # --- Run flag engine (Chat 101) -----------------------------------------
    _run_flag_engine(conn, customer_id)

    conn.close()

    result = {
        "generated": generated,
        "skipped_duplicate": skipped_duplicate,
        "skipped_no_data": skipped_no_data,
        "skipped_no_table": skipped_no_table,
        "errors": errors,
        "customer_id": customer_id,
        "by_entity_type": by_entity_type,
    }

    print("\n[ENGINE] Done. Generated={} | SkippedDuplicate={} | SkippedNoData={} | SkippedNoTable={}".format(
        generated, skipped_duplicate, skipped_no_data, skipped_no_table))
    print("[ENGINE] By entity type: {}".format(by_entity_type))
    print("="*80 + "\n")

    return result
