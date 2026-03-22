"""
Build Product Features Daily Table
Master Chat 13 - Phase 1

Reads from raw_product_performance_daily and builds analytics.product_features_daily
with all windowed metrics, WoW comparisons, and feed quality flags.
"""

import duckdb
from datetime import datetime

DB_PATH = "warehouse.duckdb"
CUSTOMER_ID = "1254895944"

print("=" * 70)
print("PRODUCT FEATURES BUILDER")
print("=" * 70)
print(f"Customer ID: {CUSTOMER_ID}")
print()

conn = duckdb.connect(DB_PATH)

# Check source data
source_count = conn.execute(
    "SELECT COUNT(*) FROM raw_product_performance_daily WHERE customer_id = ?",
    [CUSTOMER_ID]
).fetchone()[0]

print(f"Source rows in raw_product_performance_daily: {source_count}")

if source_count == 0:
    print("❌ No source data found!")
    conn.close()
    exit(1)

print()
print("Building product_features_daily...")
print()

# Delete existing features for this customer
deleted = conn.execute(
    "DELETE FROM analytics.product_features_daily WHERE customer_id = ?",
    [CUSTOMER_ID]
).rowcount
print(f"Deleted {deleted} existing feature rows")

# Build features with window functions
print("Calculating windowed metrics...")

conn.execute(f"""
    INSERT INTO analytics.product_features_daily
    SELECT
        '{CUSTOMER_ID}' AS client_id,
        customer_id,
        campaign_id,
        ad_group_id,
        product_id,
        snapshot_date,
        
        -- Product attributes
        product_title,
        product_brand,
        product_category,
        product_type_l1,
        product_type_l2,
        availability,
        condition,
        custom_label_0,
        custom_label_1,
        product_price_micros,
        product_sale_price_micros,
        
        -- Metadata
        '1.0' AS feature_set_version,
        '1.0' AS schema_version,
        CURRENT_TIMESTAMP AS generated_at_utc,
        'raw_product_performance_daily' AS source_table,
        
        -- W7 windowed sums
        SUM(impressions) OVER w7 AS impressions_w7_sum,
        SUM(clicks) OVER w7 AS clicks_w7_sum,
        SUM(cost_micros) OVER w7 AS cost_micros_w7_sum,
        SUM(conversions) OVER w7 AS conversions_w7_sum,
        SUM(conversions_value) OVER w7 AS conversions_value_w7_sum,
        
        -- W14 windowed sums
        SUM(impressions) OVER w14 AS impressions_w14_sum,
        SUM(clicks) OVER w14 AS clicks_w14_sum,
        SUM(cost_micros) OVER w14 AS cost_micros_w14_sum,
        SUM(conversions) OVER w14 AS conversions_w14_sum,
        SUM(conversions_value) OVER w14 AS conversions_value_w14_sum,
        
        -- W30 windowed sums
        SUM(impressions) OVER w30 AS impressions_w30_sum,
        SUM(clicks) OVER w30 AS clicks_w30_sum,
        SUM(cost_micros) OVER w30 AS cost_micros_w30_sum,
        SUM(conversions) OVER w30 AS conversions_w30_sum,
        SUM(conversions_value) OVER w30 AS conversions_value_w30_sum,
        
        -- W90 windowed sums
        SUM(impressions) OVER w90 AS impressions_w90_sum,
        SUM(clicks) OVER w90 AS clicks_w90_sum,
        SUM(cost_micros) OVER w90 AS cost_micros_w90_sum,
        SUM(conversions) OVER w90 AS conversions_w90_sum,
        SUM(conversions_value) OVER w90 AS conversions_value_w90_sum,
        
        -- W7 calculated metrics
        CASE WHEN SUM(impressions) OVER w7 > 0 
             THEN SUM(clicks) OVER w7::DOUBLE / SUM(impressions) OVER w7 
             ELSE 0.0 END AS ctr_w7,
        CASE WHEN SUM(clicks) OVER w7 > 0 
             THEN (SUM(cost_micros) OVER w7 / 1000000.0) / SUM(clicks) OVER w7 
             ELSE 0.0 END AS cpc_w7,
        CASE WHEN SUM(clicks) OVER w7 > 0 
             THEN SUM(conversions) OVER w7 / SUM(clicks) OVER w7 
             ELSE 0.0 END AS cvr_w7,
        CASE WHEN SUM(conversions) OVER w7 > 0 
             THEN (SUM(cost_micros) OVER w7 / 1000000.0) / SUM(conversions) OVER w7 
             ELSE 0.0 END AS cpa_w7,
        CASE WHEN SUM(cost_micros) OVER w7 > 0 
             THEN SUM(conversions_value) OVER w7 / (SUM(cost_micros) OVER w7 / 1000000.0) 
             ELSE 0.0 END AS roas_w7,
        
        -- W14 calculated metrics
        CASE WHEN SUM(impressions) OVER w14 > 0 
             THEN SUM(clicks) OVER w14::DOUBLE / SUM(impressions) OVER w14 
             ELSE 0.0 END AS ctr_w14,
        CASE WHEN SUM(clicks) OVER w14 > 0 
             THEN (SUM(cost_micros) OVER w14 / 1000000.0) / SUM(clicks) OVER w14 
             ELSE 0.0 END AS cpc_w14,
        CASE WHEN SUM(clicks) OVER w14 > 0 
             THEN SUM(conversions) OVER w14 / SUM(clicks) OVER w14 
             ELSE 0.0 END AS cvr_w14,
        CASE WHEN SUM(conversions) OVER w14 > 0 
             THEN (SUM(cost_micros) OVER w14 / 1000000.0) / SUM(conversions) OVER w14 
             ELSE 0.0 END AS cpa_w14,
        CASE WHEN SUM(cost_micros) OVER w14 > 0 
             THEN SUM(conversions_value) OVER w14 / (SUM(cost_micros) OVER w14 / 1000000.0) 
             ELSE 0.0 END AS roas_w14,
        
        -- W30 calculated metrics
        CASE WHEN SUM(impressions) OVER w30 > 0 
             THEN SUM(clicks) OVER w30::DOUBLE / SUM(impressions) OVER w30 
             ELSE 0.0 END AS ctr_w30,
        CASE WHEN SUM(clicks) OVER w30 > 0 
             THEN (SUM(cost_micros) OVER w30 / 1000000.0) / SUM(clicks) OVER w30 
             ELSE 0.0 END AS cpc_w30,
        CASE WHEN SUM(clicks) OVER w30 > 0 
             THEN SUM(conversions) OVER w30 / SUM(clicks) OVER w30 
             ELSE 0.0 END AS cvr_w30,
        CASE WHEN SUM(conversions) OVER w30 > 0 
             THEN (SUM(cost_micros) OVER w30 / 1000000.0) / SUM(conversions) OVER w30 
             ELSE 0.0 END AS cpa_w30,
        CASE WHEN SUM(cost_micros) OVER w30 > 0 
             THEN SUM(conversions_value) OVER w30 / (SUM(cost_micros) OVER w30 / 1000000.0) 
             ELSE 0.0 END AS roas_w30,
        
        -- W90 calculated metrics
        CASE WHEN SUM(impressions) OVER w90 > 0 
             THEN SUM(clicks) OVER w90::DOUBLE / SUM(impressions) OVER w90 
             ELSE 0.0 END AS ctr_w90,
        CASE WHEN SUM(clicks) OVER w90 > 0 
             THEN (SUM(cost_micros) OVER w90 / 1000000.0) / SUM(clicks) OVER w90 
             ELSE 0.0 END AS cpc_w90,
        CASE WHEN SUM(clicks) OVER w90 > 0 
             THEN SUM(conversions) OVER w90 / SUM(clicks) OVER w90 
             ELSE 0.0 END AS cvr_w90,
        CASE WHEN SUM(conversions) OVER w90 > 0 
             THEN (SUM(cost_micros) OVER w90 / 1000000.0) / SUM(conversions) OVER w90 
             ELSE 0.0 END AS cpa_w90,
        CASE WHEN SUM(cost_micros) OVER w90 > 0 
             THEN SUM(conversions_value) OVER w90 / (SUM(cost_micros) OVER w90 / 1000000.0) 
             ELSE 0.0 END AS roas_w90,
        
        -- WoW comparisons (current w7 vs previous w7)
        CASE WHEN LAG(CASE WHEN SUM(conversions) OVER w7 > 0 
                           THEN (SUM(cost_micros) OVER w7 / 1000000.0) / SUM(conversions) OVER w7 
                           ELSE 0.0 END, 7) OVER (PARTITION BY product_id ORDER BY snapshot_date) > 0
             THEN (CASE WHEN SUM(conversions) OVER w7 > 0 
                        THEN (SUM(cost_micros) OVER w7 / 1000000.0) / SUM(conversions) OVER w7 
                        ELSE 0.0 END - 
                   LAG(CASE WHEN SUM(conversions) OVER w7 > 0 
                           THEN (SUM(cost_micros) OVER w7 / 1000000.0) / SUM(conversions) OVER w7 
                           ELSE 0.0 END, 7) OVER (PARTITION BY product_id ORDER BY snapshot_date)) /
                  LAG(CASE WHEN SUM(conversions) OVER w7 > 0 
                           THEN (SUM(cost_micros) OVER w7 / 1000000.0) / SUM(conversions) OVER w7 
                           ELSE 0.0 END, 7) OVER (PARTITION BY product_id ORDER BY snapshot_date)
             ELSE 0.0 END AS cpa_w7_vs_prev_pct,
        
        CASE WHEN LAG(CASE WHEN SUM(cost_micros) OVER w7 > 0 
                           THEN SUM(conversions_value) OVER w7 / (SUM(cost_micros) OVER w7 / 1000000.0) 
                           ELSE 0.0 END, 7) OVER (PARTITION BY product_id ORDER BY snapshot_date) > 0
             THEN (CASE WHEN SUM(cost_micros) OVER w7 > 0 
                        THEN SUM(conversions_value) OVER w7 / (SUM(cost_micros) OVER w7 / 1000000.0) 
                        ELSE 0.0 END - 
                   LAG(CASE WHEN SUM(cost_micros) OVER w7 > 0 
                           THEN SUM(conversions_value) OVER w7 / (SUM(cost_micros) OVER w7 / 1000000.0) 
                           ELSE 0.0 END, 7) OVER (PARTITION BY product_id ORDER BY snapshot_date)) /
                  LAG(CASE WHEN SUM(cost_micros) OVER w7 > 0 
                           THEN SUM(conversions_value) OVER w7 / (SUM(cost_micros) OVER w7 / 1000000.0) 
                           ELSE 0.0 END, 7) OVER (PARTITION BY product_id ORDER BY snapshot_date)
             ELSE 0.0 END AS roas_w7_vs_prev_pct,
        
        CASE WHEN LAG(CASE WHEN SUM(impressions) OVER w7 > 0 
                           THEN SUM(clicks) OVER w7::DOUBLE / SUM(impressions) OVER w7 
                           ELSE 0.0 END, 7) OVER (PARTITION BY product_id ORDER BY snapshot_date) > 0
             THEN (CASE WHEN SUM(impressions) OVER w7 > 0 
                        THEN SUM(clicks) OVER w7::DOUBLE / SUM(impressions) OVER w7 
                        ELSE 0.0 END - 
                   LAG(CASE WHEN SUM(impressions) OVER w7 > 0 
                           THEN SUM(clicks) OVER w7::DOUBLE / SUM(impressions) OVER w7 
                           ELSE 0.0 END, 7) OVER (PARTITION BY product_id ORDER BY snapshot_date)) /
                  LAG(CASE WHEN SUM(impressions) OVER w7 > 0 
                           THEN SUM(clicks) OVER w7::DOUBLE / SUM(impressions) OVER w7 
                           ELSE 0.0 END, 7) OVER (PARTITION BY product_id ORDER BY snapshot_date)
             ELSE 0.0 END AS ctr_w7_vs_prev_pct,
        
        CASE WHEN LAG(CASE WHEN SUM(clicks) OVER w7 > 0 
                           THEN SUM(conversions) OVER w7 / SUM(clicks) OVER w7 
                           ELSE 0.0 END, 7) OVER (PARTITION BY product_id ORDER BY snapshot_date) > 0
             THEN (CASE WHEN SUM(clicks) OVER w7 > 0 
                        THEN SUM(conversions) OVER w7 / SUM(clicks) OVER w7 
                        ELSE 0.0 END - 
                   LAG(CASE WHEN SUM(clicks) OVER w7 > 0 
                           THEN SUM(conversions) OVER w7 / SUM(clicks) OVER w7 
                           ELSE 0.0 END, 7) OVER (PARTITION BY product_id ORDER BY snapshot_date)) /
                  LAG(CASE WHEN SUM(clicks) OVER w7 > 0 
                           THEN SUM(conversions) OVER w7 / SUM(clicks) OVER w7 
                           ELSE 0.0 END, 7) OVER (PARTITION BY product_id ORDER BY snapshot_date)
             ELSE 0.0 END AS cvr_w7_vs_prev_pct,
        
        -- Cost volatility (coefficient of variation over w14)
        CASE WHEN AVG(cost_micros) OVER w14 > 0
             THEN STDDEV(cost_micros) OVER w14 / AVG(cost_micros) OVER w14
             ELSE 0.0 END AS cost_w14_cv,
        
        -- Benchmark comparison
        AVG(benchmark_ctr) OVER w30 AS benchmark_ctr_w30,
        CASE WHEN AVG(benchmark_ctr) OVER w30 > 0
             THEN (CASE WHEN SUM(impressions) OVER w30 > 0 
                        THEN SUM(clicks) OVER w30::DOUBLE / SUM(impressions) OVER w30 
                        ELSE 0.0 END - AVG(benchmark_ctr) OVER w30) / AVG(benchmark_ctr) OVER w30
             ELSE 0.0 END AS ctr_vs_benchmark_pct,
        
        -- Feed quality flags
        CASE WHEN availability = 'OUT_OF_STOCK' THEN TRUE ELSE FALSE END AS stock_out_flag,
        SUM(CASE WHEN availability = 'OUT_OF_STOCK' THEN 1 ELSE 0 END) OVER w30 AS stock_out_days_w30,
        0.85 AS feed_quality_score,  -- Placeholder
        FALSE AS has_price_mismatch,  -- Placeholder
        FALSE AS has_disapproval,     -- Placeholder
        
        -- Product lifecycle
        CASE WHEN ROW_NUMBER() OVER (PARTITION BY product_id ORDER BY snapshot_date) <= 7 
             THEN TRUE ELSE FALSE END AS new_product_flag,
        ROW_NUMBER() OVER (PARTITION BY product_id ORDER BY snapshot_date) AS days_live,
        CASE WHEN SUM(impressions) OVER w7 < 100 THEN TRUE ELSE FALSE END AS low_data_flag
        
    FROM raw_product_performance_daily
    WHERE customer_id = '{CUSTOMER_ID}'
    WINDOW
        w7 AS (PARTITION BY product_id ORDER BY snapshot_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW),
        w14 AS (PARTITION BY product_id ORDER BY snapshot_date ROWS BETWEEN 13 PRECEDING AND CURRENT ROW),
        w30 AS (PARTITION BY product_id ORDER BY snapshot_date ROWS BETWEEN 29 PRECEDING AND CURRENT ROW),
        w90 AS (PARTITION BY product_id ORDER BY snapshot_date ROWS BETWEEN 89 PRECEDING AND CURRENT ROW)
""")

# Verify
final_count = conn.execute(
    "SELECT COUNT(*) FROM analytics.product_features_daily WHERE customer_id = ?",
    [CUSTOMER_ID]
).fetchone()[0]

unique_products = conn.execute(
    "SELECT COUNT(DISTINCT product_id) FROM analytics.product_features_daily WHERE customer_id = ?",
    [CUSTOMER_ID]
).fetchone()[0]

sample = conn.execute(
    """SELECT product_id, snapshot_date, roas_w7, cpa_w7, stock_out_flag, new_product_flag
       FROM analytics.product_features_daily 
       WHERE customer_id = ? 
       ORDER BY snapshot_date DESC 
       LIMIT 3""",
    [CUSTOMER_ID]
).fetchall()

conn.close()

print()
print("=" * 70)
print("BUILD COMPLETE")
print("=" * 70)
print(f"✅ Created {final_count} feature rows")
print(f"✅ Covering {unique_products} unique products")
print()
print("Sample rows (most recent):")
for row in sample:
    print(f"  {row}")
print()
print("=" * 70)
