"""
Synthetic Shopping Campaign Data Generator v2
M4 — Chat 25

Populates analytics.shopping_campaign_daily with:
- 20 campaigns × 365 days = 7,300 rows
- ROAS-based performance (conv_value / cost = 3.0–6.0 range)
- Adds 10 new columns via ALTER TABLE before INSERT

Usage (PowerShell):
    cd C:\\Users\\User\\Desktop\\gads-data-layer
    .venv\\Scripts\\Activate.ps1
    python tools/testing/generate_synthetic_shopping_v2.py
"""

import random
from datetime import date, timedelta
import duckdb
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
CUSTOMER_ID = "9999999999"
DB_PATH     = "warehouse.duckdb"
END_DATE    = date.today()
START_DATE  = END_DATE - timedelta(days=364)
DAYS        = 365

random.seed(99)

# ── Bid strategy options (shopping-appropriate per brief) ──────────────────────
BID_STRATEGY_TYPES = ["TARGET_ROAS", "MAXIMIZE_CONVERSION_VALUE"]

# ── 20 shopping campaigns ──────────────────────────────────────────────────────
CAMPAIGNS = [
    {"id": 5001, "name": "Shopping – All Products",          "priority": 1, "target_roas": 4.0, "status": "ENABLED"},
    {"id": 5002, "name": "Shopping – Best Sellers",          "priority": 2, "target_roas": 5.0, "status": "ENABLED"},
    {"id": 5003, "name": "Shopping – Clearance",             "priority": 0, "target_roas": 3.0, "status": "ENABLED"},
    {"id": 5004, "name": "Shopping – Electronics",           "priority": 2, "target_roas": 4.5, "status": "ENABLED"},
    {"id": 5005, "name": "Shopping – Home & Garden",         "priority": 1, "target_roas": 3.5, "status": "ENABLED"},
    {"id": 5006, "name": "Shopping – Apparel",               "priority": 1, "target_roas": 4.0, "status": "ENABLED"},
    {"id": 5007, "name": "Shopping – Seasonal Promos",       "priority": 2, "target_roas": 5.5, "status": "ENABLED"},
    {"id": 5008, "name": "Shopping – Brand Protection",      "priority": 2, "target_roas": 6.0, "status": "ENABLED"},
    {"id": 5009, "name": "Shopping – New Arrivals",          "priority": 1, "target_roas": 3.5, "status": "ENABLED"},
    {"id": 5010, "name": "Shopping – High Margin",           "priority": 2, "target_roas": 5.0, "status": "ENABLED"},
    {"id": 5011, "name": "Shopping – Low Margin",            "priority": 0, "target_roas": 3.0, "status": "ENABLED"},
    {"id": 5012, "name": "Shopping – Sports & Outdoors",     "priority": 1, "target_roas": 4.0, "status": "ENABLED"},
    {"id": 5013, "name": "Shopping – Beauty",                "priority": 1, "target_roas": 4.5, "status": "ENABLED"},
    {"id": 5014, "name": "Shopping – Kitchen",               "priority": 1, "target_roas": 3.5, "status": "ENABLED"},
    {"id": 5015, "name": "Shopping – Toys & Games",          "priority": 0, "target_roas": 3.2, "status": "ENABLED"},
    {"id": 5016, "name": "Shopping – Automotive",            "priority": 0, "target_roas": 3.0, "status": "PAUSED"},
    {"id": 5017, "name": "Shopping – Office Supplies",       "priority": 1, "target_roas": 3.8, "status": "PAUSED"},
    {"id": 5018, "name": "Shopping – Health & Wellness",     "priority": 1, "target_roas": 4.2, "status": "ENABLED"},
    {"id": 5019, "name": "Shopping – Luxury",                "priority": 2, "target_roas": 5.8, "status": "ENABLED"},
    {"id": 5020, "name": "Shopping – Budget Range",          "priority": 0, "target_roas": 3.1, "status": "ENABLED"},
]


def generate_campaign_day(campaign: dict, snapshot_date: date, day_index: int) -> dict:
    """Generate one day of data for a shopping campaign."""
    status = campaign["status"]
    target_roas = campaign["target_roas"]

    if status == "PAUSED":
        impressions = random.randint(0, 100)
        clicks = 0
        cost = 0.0
        conversions = 0.0
        conv_value = 0.0
    else:
        # Base impressions scaled by priority
        base_impr = 3000 + campaign["priority"] * 1500
        noise = random.uniform(0.80, 1.20)
        impressions = max(100, int(base_impr * noise))
        ctr = random.uniform(0.015, 0.040)
        clicks = max(0, int(impressions * ctr))
        avg_cpc = random.uniform(0.40, 1.80)
        cost = round(clicks * avg_cpc, 2)
        # ROAS-based conv_value: cost * roas_multiplier
        roas_actual = target_roas * random.uniform(0.85, 1.15)
        roas_actual = max(3.0, min(6.5, roas_actual))
        conv_value = round(cost * roas_actual, 2)
        # Conversions from avg order value ~£45–£120
        avg_order = random.uniform(45, 120)
        conversions = round(conv_value / avg_order, 2) if avg_order > 0 else 0.0

    # Impression share metrics
    if status == "PAUSED":
        sis = round(random.uniform(0.10, 0.30), 4)
    else:
        sis = round(random.uniform(0.30, 0.90), 4)

    top_is     = round(random.uniform(0.15, sis * 0.85), 4)
    abs_top_is = round(random.uniform(0.05, top_is * 0.75), 4)
    click_share = round(random.uniform(sis * 0.40, sis * 0.90), 4)

    all_conv_ratio = random.uniform(1.05, 1.15)
    all_conversions       = round(conversions * all_conv_ratio, 2)
    all_conversions_value = round(conv_value * all_conv_ratio, 2)

    return {
        "customer_id":                          CUSTOMER_ID,
        "snapshot_date":                        snapshot_date,
        "campaign_id":                          campaign["id"],
        "campaign_name":                        campaign["name"],
        "campaign_priority":                    campaign["priority"],
        "enable_local":                         False,
        "feed_label":                           "US",
        "country_of_sale":                      "US",
        "impressions":                          impressions,
        "clicks":                               clicks,
        "cost_micros":                          int(cost * 1_000_000),
        "conversions":                          conversions,
        "conversions_value":                    round(conv_value, 2),
        # New M4 columns
        "campaign_status":                      status,
        "channel_type":                         "SHOPPING",
        "all_conversions":                      all_conversions,
        "all_conversions_value":                all_conversions_value,
        "search_impression_share":              sis,
        "search_top_impression_share":          top_is,
        "search_absolute_top_impression_share": abs_top_is,
        "click_share":                          click_share,
        "optimization_score":                   round(random.uniform(0.50, 0.95), 4),
        "bid_strategy_type":                    random.choice(BID_STRATEGY_TYPES),
    }


def main():
    print("Shopping Synthetic Data Generator v2 (M4)")
    print(f"  Campaigns:    {len(CAMPAIGNS)}")
    print(f"  Date range:   {START_DATE} to {END_DATE} ({DAYS} days)")
    print(f"  Expected rows: {len(CAMPAIGNS) * DAYS}")
    print()

    conn = duckdb.connect(DB_PATH)

    # ── Step 1: ALTER TABLE to add the 10 new columns ─────────────────────────
    print("Step 1: Adding new columns to analytics.shopping_campaign_daily...")
    new_cols = [
        ("campaign_status",                      "VARCHAR"),
        ("channel_type",                         "VARCHAR"),
        ("all_conversions",                      "DOUBLE"),
        ("all_conversions_value",                "DOUBLE"),
        ("search_impression_share",              "DOUBLE"),
        ("search_top_impression_share",          "DOUBLE"),
        ("search_absolute_top_impression_share", "DOUBLE"),
        ("click_share",                          "DOUBLE"),
        ("optimization_score",                   "DOUBLE"),
        ("bid_strategy_type",                    "VARCHAR"),
    ]
    for col_name, col_type in new_cols:
        conn.execute(
            f"ALTER TABLE analytics.shopping_campaign_daily "
            f"ADD COLUMN IF NOT EXISTS {col_name} {col_type}"
        )
        print(f"  ✅ {col_name} {col_type}")

    # ── Step 2: Delete existing synthetic rows ─────────────────────────────────
    print(f"\nStep 2: Deleting existing rows for customer {CUSTOMER_ID}...")
    deleted = conn.execute(
        "DELETE FROM analytics.shopping_campaign_daily WHERE customer_id = ?",
        [CUSTOMER_ID]
    ).rowcount
    print(f"  Deleted {deleted} existing rows")

    # ── Step 3: Generate all rows ──────────────────────────────────────────────
    print(f"\nStep 3: Generating {len(CAMPAIGNS) * DAYS} rows...")
    rows = []
    for day_index in range(DAYS):
        snap = START_DATE + timedelta(days=day_index)
        for camp in CAMPAIGNS:
            rows.append(generate_campaign_day(camp, snap, day_index))

    print(f"  Generated {len(rows)} rows")

    # ── Step 4: Insert ────────────────────────────────────────────────────────
    print("\nStep 4: Inserting rows...")

    COLS = [
        "customer_id", "snapshot_date", "campaign_id", "campaign_name",
        "campaign_priority", "enable_local", "feed_label", "country_of_sale",
        "impressions", "clicks", "cost_micros", "conversions", "conversions_value",
        "campaign_status", "channel_type",
        "all_conversions", "all_conversions_value",
        "search_impression_share", "search_top_impression_share",
        "search_absolute_top_impression_share", "click_share",
        "optimization_score", "bid_strategy_type",
    ]

    tuples = [tuple(r[c] for c in COLS) for r in rows]
    placeholders = ", ".join(["?"] * len(COLS))
    cols_sql = ", ".join(COLS)

    conn.executemany(
        f"INSERT INTO analytics.shopping_campaign_daily ({cols_sql}) VALUES ({placeholders})",
        tuples
    )

    # ── Step 5: Verify ────────────────────────────────────────────────────────
    print("\nStep 5: Verifying...")
    total = conn.execute(
        "SELECT COUNT(*) FROM analytics.shopping_campaign_daily WHERE customer_id = ?",
        [CUSTOMER_ID]
    ).fetchone()[0]

    enabled = conn.execute(
        "SELECT COUNT(*) FROM analytics.shopping_campaign_daily WHERE customer_id = ? AND campaign_status = 'ENABLED'",
        [CUSTOMER_ID]
    ).fetchone()[0]

    avg_roas = conn.execute(
        """SELECT AVG(CASE WHEN cost_micros > 0
                    THEN conversions_value / (cost_micros / 1000000.0)
                    ELSE NULL END)
           FROM analytics.shopping_campaign_daily WHERE customer_id = ?""",
        [CUSTOMER_ID]
    ).fetchone()[0]

    col_check = conn.execute(
        "SELECT COUNT(*) FROM information_schema.columns "
        "WHERE table_name = 'shopping_campaign_daily' AND table_schema = 'analytics'"
    ).fetchone()[0]

    conn.close()

    print(f"  Total rows:    {total}")
    print(f"  ENABLED rows:  {enabled}")
    print(f"  Avg ROAS:      {avg_roas:.2f}" if avg_roas else "  Avg ROAS: N/A")
    print(f"  Total columns: {col_check}")
    print()

    if total == len(CAMPAIGNS) * DAYS:
        print("✅ A5 COMPLETE — shopping_campaign_daily populated")
    else:
        print(f"⚠️  Row count mismatch. Expected {len(CAMPAIGNS) * DAYS}, got {total}")

    print()
    print("Next: Copy-Item -Force warehouse.duckdb warehouse_readonly.duckdb")


if __name__ == "__main__":
    main()
