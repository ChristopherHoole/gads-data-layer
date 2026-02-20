# tools/testing/generate_synthetic_ad_group_data.py
# Chat 23 M2: Generate synthetic ad group daily performance data.
# Produces realistic ad group data for customer_id 9999999999.
# Date range: last 365 days (dynamic, ending today).
#
# Usage (PowerShell):
#   cd C:/Users/User/Desktop/gads-data-layer
#   .venv/Scripts/Activate.ps1
#   python tools/testing/generate_synthetic_ad_group_data.py

import random
import duckdb
import shutil
from datetime import date, datetime, timedelta
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────────────────
CUSTOMER_ID   = "9999999999"
RUN_ID        = "synthetic-v2-M2-adgroups"
DB_PATH       = "warehouse.duckdb"
DB_RO_PATH    = "warehouse_readonly.duckdb"

END_DATE      = date.today()
START_DATE    = END_DATE - timedelta(days=364)

random.seed(42)

# ── Campaign / Ad Group structure ────────────────────────────────────────────
# Mirrors the 20 synthetic campaigns from generate_synthetic_data_v2.py
# Each campaign gets 2-4 ad groups
CAMPAIGNS = [
    (1001, "Growth Strong",       "ENABLED"),
    (1002, "Growth Moderate",     "ENABLED"),
    (1003, "Growth Slow",         "ENABLED"),
    (1004, "Recovery Turnaround", "ENABLED"),
    (1005, "Volatile Medium",     "ENABLED"),
    (1006, "Volatile High",       "ENABLED"),
    (1007, "Stable Low",          "ENABLED"),
    (1008, "Stable High",         "ENABLED"),
    (1009, "Declining Slow",      "PAUSED"),
    (1010, "Declining Fast",      "PAUSED"),
    (1011, "New Campaign A",      "ENABLED"),
    (1012, "New Campaign B",      "ENABLED"),
    (1013, "Budget Constrained A","ENABLED"),
    (1014, "Budget Constrained B","ENABLED"),
    (1015, "Seasonal Peak",       "ENABLED"),
    (1016, "Seasonal Trough",     "PAUSED"),
    (1017, "Brand Search",        "ENABLED"),
    (1018, "NonBrand Search",     "ENABLED"),
    (1019, "Display Awareness",   "ENABLED"),
    (1020, "Shopping Feed",       "ENABLED"),
]

AD_GROUP_TEMPLATES = [
    ("General",     1.0),
    ("High Intent", 1.3),
    ("Broad Match", 0.8),
    ("Exact Match", 1.2),
]


def build_ad_groups():
    """Generate list of (ad_group_id, ad_group_name, ad_group_status, campaign_id, campaign_name, cpc_bid_micros, target_cpa_micros, perf_multiplier)."""
    groups = []
    ag_id = 2000001
    for camp_id, camp_name, camp_status in CAMPAIGNS:
        # 2 ad groups per paused campaign, 3-4 for active
        n_groups = 2 if camp_status == "PAUSED" else random.choice([3, 4])
        templates = random.sample(AD_GROUP_TEMPLATES, n_groups)
        for ag_name_suffix, perf_mult in templates:
            ag_name = f"{camp_name} – {ag_name_suffix}"
            ag_status = camp_status  # inherit campaign status
            cpc_bid = random.randint(500_000, 3_000_000)  # $0.50–$3.00
            target_cpa = random.choice([None, random.randint(5_000_000, 50_000_000)])
            groups.append((ag_id, ag_name, ag_status, camp_id, camp_name, cpc_bid, target_cpa, perf_mult))
            ag_id += 1
    return groups


def generate_ad_group_day(ag_id, ag_name, ag_status, camp_id, camp_name, cpc_bid, target_cpa, perf_mult, snap_date):
    """Generate one row of daily performance for an ad group."""
    if ag_status == "PAUSED":
        # Paused: low/zero activity
        impressions = random.randint(0, 50)
    else:
        impressions = int(random.gauss(3000, 800) * perf_mult)
        impressions = max(100, impressions)

    clicks = int(impressions * random.uniform(0.02, 0.08))
    clicks = max(0, clicks)

    cpc = (cpc_bid / 1_000_000) * random.uniform(0.8, 1.2)
    cost_micros = int(clicks * cpc * 1_000_000)

    conv_rate = random.uniform(0.03, 0.12) * perf_mult
    conversions = round(clicks * conv_rate, 2)

    avg_order_value = random.uniform(20, 150)
    conversions_value = round(conversions * avg_order_value, 2)

    # IS metrics — correlated to perf_mult, lower for paused
    if ag_status == "PAUSED":
        sis = round(random.uniform(0.20, 0.45), 4)
    else:
        sis = round(random.uniform(0.40, 0.85) * perf_mult, 4)
        sis = min(sis, 1.0)
    top_is  = round(sis * random.uniform(0.40, 0.70), 4)
    abs_is  = round(top_is * random.uniform(0.30, 0.60), 4)
    cs      = round(sis * random.uniform(0.50, 0.85), 4)

    return {
        "run_id":                               RUN_ID,
        "ingested_at":                          datetime.utcnow(),
        "customer_id":                          CUSTOMER_ID,
        "snapshot_date":                        snap_date,
        "campaign_id":                          camp_id,
        "campaign_name":                        camp_name,
        "ad_group_id":                          ag_id,
        "ad_group_name":                        ag_name,
        "ad_group_status":                      ag_status,
        "cpc_bid_micros":                       cpc_bid,
        "target_cpa_micros":                    target_cpa,
        "impressions":                          impressions,
        "clicks":                               clicks,
        "cost_micros":                          cost_micros,
        "conversions":                          conversions,
        "conversions_value":                    conversions_value,
        "search_impression_share":              sis,
        "search_top_impression_share":          top_is,
        "search_absolute_top_impression_share": abs_is,
        "click_share":                          cs,
    }


def main():
    conn = duckdb.connect(DB_PATH)

    # Ensure table exists
    conn.execute("""
        CREATE TABLE IF NOT EXISTS snap_ad_group_daily (
            run_id VARCHAR,
            ingested_at TIMESTAMP,
            customer_id VARCHAR,
            snapshot_date DATE,
            campaign_id BIGINT,
            campaign_name VARCHAR,
            ad_group_id BIGINT,
            ad_group_name VARCHAR,
            ad_group_status VARCHAR,
            cpc_bid_micros BIGINT,
            target_cpa_micros BIGINT,
            impressions BIGINT,
            clicks BIGINT,
            cost_micros BIGINT,
            conversions DOUBLE,
            conversions_value DOUBLE,
            search_impression_share DOUBLE,
            search_top_impression_share DOUBLE,
            search_absolute_top_impression_share DOUBLE,
            click_share DOUBLE
        );
    """)

    # Ensure analytics schema + view
    conn.execute("CREATE SCHEMA IF NOT EXISTS analytics;")
    conn.execute("""
        CREATE OR REPLACE VIEW analytics.ad_group_daily AS
        SELECT
            run_id, ingested_at, customer_id, snapshot_date,
            campaign_id, campaign_name,
            ad_group_id, ad_group_name, ad_group_status,
            cpc_bid_micros, target_cpa_micros,
            impressions, clicks, cost_micros,
            cost_micros / 1000000.0 AS cost,
            conversions, conversions_value,
            CASE WHEN impressions > 0 THEN clicks * 1.0 / impressions ELSE NULL END AS ctr,
            CASE WHEN clicks > 0 THEN (cost_micros / 1000000.0) / clicks ELSE NULL END AS cpc,
            CASE WHEN cost_micros > 0 THEN conversions_value / (cost_micros / 1000000.0) ELSE NULL END AS roas,
            CASE WHEN conversions > 0 THEN (cost_micros / 1000000.0) / conversions ELSE NULL END AS cpa,
            search_impression_share,
            search_top_impression_share,
            search_absolute_top_impression_share,
            click_share
        FROM snap_ad_group_daily;
    """)

    # Wipe existing synthetic data for this customer
    conn.execute("DELETE FROM snap_ad_group_daily WHERE customer_id = ? AND run_id = ?", [CUSTOMER_ID, RUN_ID])

    # Build ad groups
    ad_groups = build_ad_groups()
    print(f"Ad groups defined: {len(ad_groups)}")

    # Generate rows
    COLS = [
        "run_id", "ingested_at", "customer_id", "snapshot_date",
        "campaign_id", "campaign_name", "ad_group_id", "ad_group_name",
        "ad_group_status", "cpc_bid_micros", "target_cpa_micros",
        "impressions", "clicks", "cost_micros", "conversions", "conversions_value",
        "search_impression_share", "search_top_impression_share",
        "search_absolute_top_impression_share", "click_share",
    ]

    rows = []
    current = START_DATE
    while current <= END_DATE:
        for ag_id, ag_name, ag_status, camp_id, camp_name, cpc_bid, target_cpa, perf_mult in ad_groups:
            row = generate_ad_group_day(ag_id, ag_name, ag_status, camp_id, camp_name, cpc_bid, target_cpa, perf_mult, current)
            rows.append(tuple(row[c] for c in COLS))
        current += timedelta(days=1)

    conn.executemany(f"INSERT INTO snap_ad_group_daily ({', '.join(COLS)}) VALUES ({', '.join(['?']*len(COLS))})", rows)

    total = conn.execute("SELECT COUNT(*) FROM snap_ad_group_daily WHERE customer_id = ?", [CUSTOMER_ID]).fetchone()[0]
    print(f"Rows inserted: {total}")

    # Verify
    check = conn.execute("""
        SELECT
            COUNT(DISTINCT ad_group_id) as n_groups,
            MIN(snapshot_date) as min_date,
            MAX(snapshot_date) as max_date,
            AVG(conversions) as avg_conv,
            COUNT(*) FILTER (WHERE conversions IS NULL) as nulls
        FROM snap_ad_group_daily WHERE customer_id = ?
    """, [CUSTOMER_ID]).fetchone()
    print(f"Ad groups: {check[0]} | Dates: {check[1]} to {check[2]} | Avg conv: {check[3]:.2f} | Nulls: {check[4]}")

    conn.close()

    # Copy to readonly DB
    shutil.copy2(DB_PATH, DB_RO_PATH)
    print(f"Copied to {DB_RO_PATH}")
    print("Done.")


if __name__ == "__main__":
    main()
