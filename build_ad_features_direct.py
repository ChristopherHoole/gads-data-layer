"""
Build ad_features_daily directly from ad_daily using a single SQL query.
Faster and simpler than the per-ad pipeline approach.
"""
import duckdb
from datetime import date, timedelta

CID       = "1254895944"
SNAP_DATE = date(2026, 3, 16)

print("=" * 60)
print("BUILD ad_features_daily — Christopher Hoole")
print("=" * 60)

conn = duckdb.connect('warehouse.duckdb')
conn.execute("ATTACH 'warehouse_readonly.duckdb' AS ro (READ_ONLY)")

snap = str(SNAP_DATE)
d7   = str(SNAP_DATE - timedelta(days=7))
d14  = str(SNAP_DATE - timedelta(days=14))
d30  = str(SNAP_DATE - timedelta(days=30))
d90  = str(SNAP_DATE - timedelta(days=90))

print(f"\nBuilding features for snapshot_date={snap}...")

# Drop and recreate
conn.execute("DROP TABLE IF EXISTS analytics.ad_features_daily")
conn.execute(f"""
CREATE TABLE analytics.ad_features_daily AS
WITH base AS (
    SELECT
        customer_id,
        ad_id,
        MAX(ad_name)       AS ad_name,
        MAX(campaign_id)   AS campaign_id,
        MAX(campaign_name) AS campaign_name,
        MAX(ad_group_id)   AS ad_group_id,
        MAX(ad_group_name) AS ad_group_name,
        MAX(ad_type)       AS ad_type,
        MAX(ad_status)     AS ad_status,
        MAX(ad_strength)   AS ad_strength,
        -- 7d
        SUM(CASE WHEN snapshot_date >= '{d7}' THEN impressions ELSE 0 END)       AS impressions_7d,
        SUM(CASE WHEN snapshot_date >= '{d7}' THEN clicks ELSE 0 END)            AS clicks_7d,
        SUM(CASE WHEN snapshot_date >= '{d7}' THEN cost_micros ELSE 0 END)       AS cost_micros_7d,
        SUM(CASE WHEN snapshot_date >= '{d7}' THEN conversions ELSE 0 END)       AS conversions_7d,
        SUM(CASE WHEN snapshot_date >= '{d7}' THEN conversions_value ELSE 0 END) AS conversions_value_7d,
        -- 14d
        SUM(CASE WHEN snapshot_date >= '{d14}' THEN impressions ELSE 0 END)       AS impressions_14d,
        SUM(CASE WHEN snapshot_date >= '{d14}' THEN clicks ELSE 0 END)            AS clicks_14d,
        SUM(CASE WHEN snapshot_date >= '{d14}' THEN cost_micros ELSE 0 END)       AS cost_micros_14d,
        SUM(CASE WHEN snapshot_date >= '{d14}' THEN conversions ELSE 0 END)       AS conversions_14d,
        SUM(CASE WHEN snapshot_date >= '{d14}' THEN conversions_value ELSE 0 END) AS conversions_value_14d,
        -- 30d
        SUM(CASE WHEN snapshot_date >= '{d30}' THEN impressions ELSE 0 END)       AS impressions_30d,
        SUM(CASE WHEN snapshot_date >= '{d30}' THEN clicks ELSE 0 END)            AS clicks_30d,
        SUM(CASE WHEN snapshot_date >= '{d30}' THEN cost_micros ELSE 0 END)       AS cost_micros_30d,
        SUM(CASE WHEN snapshot_date >= '{d30}' THEN conversions ELSE 0 END)       AS conversions_30d,
        SUM(CASE WHEN snapshot_date >= '{d30}' THEN conversions_value ELSE 0 END) AS conversions_value_30d,
        -- 90d
        SUM(CASE WHEN snapshot_date >= '{d90}' THEN impressions ELSE 0 END)       AS impressions_90d,
        SUM(CASE WHEN snapshot_date >= '{d90}' THEN clicks ELSE 0 END)            AS clicks_90d,
        SUM(CASE WHEN snapshot_date >= '{d90}' THEN cost_micros ELSE 0 END)       AS cost_micros_90d,
        SUM(CASE WHEN snapshot_date >= '{d90}' THEN conversions ELSE 0 END)       AS conversions_90d,
        SUM(CASE WHEN snapshot_date >= '{d90}' THEN conversions_value ELSE 0 END) AS conversions_value_90d
    FROM ro.analytics.ad_daily
    WHERE customer_id = '{CID}'
      AND snapshot_date <= '{snap}'
    GROUP BY customer_id, ad_id
)
SELECT
    customer_id,
    '{snap}'::DATE                                          AS snapshot_date,
    ad_id,
    ad_name,
    campaign_id,
    campaign_name,
    ad_group_id,
    ad_group_name,
    ad_type,
    ad_status,
    ad_strength,
    NULL::VARCHAR                                           AS final_url,
    -- 7d
    impressions_7d,
    clicks_7d,
    cost_micros_7d,
    conversions_7d,
    conversions_value_7d,
    CASE WHEN impressions_7d > 0 THEN clicks_7d::DOUBLE / impressions_7d ELSE 0 END AS ctr_7d,
    CASE WHEN clicks_7d > 0 THEN conversions_7d::DOUBLE / clicks_7d ELSE 0 END      AS cvr_7d,
    CASE WHEN conversions_7d > 0 THEN cost_micros_7d / conversions_7d ELSE 0 END    AS cpa_7d,
    CASE WHEN cost_micros_7d > 0 THEN conversions_value_7d / (cost_micros_7d/1e6) ELSE 0 END AS roas_7d,
    -- 14d
    impressions_14d,
    clicks_14d,
    cost_micros_14d,
    conversions_14d,
    conversions_value_14d,
    -- 30d
    impressions_30d,
    clicks_30d,
    cost_micros_30d,
    conversions_30d,
    conversions_value_30d,
    CASE WHEN impressions_30d > 0 THEN clicks_30d::DOUBLE / impressions_30d ELSE 0 END AS ctr_30d,
    CASE WHEN clicks_30d > 0 THEN conversions_30d::DOUBLE / clicks_30d ELSE 0 END      AS cvr_30d,
    CASE WHEN conversions_30d > 0 THEN cost_micros_30d / conversions_30d ELSE 0 END    AS cpa_30d,
    CASE WHEN cost_micros_30d > 0 THEN conversions_value_30d / (cost_micros_30d/1e6) ELSE 0 END AS roas_30d,
    -- 90d
    impressions_90d,
    clicks_90d,
    cost_micros_90d,
    conversions_90d,
    conversions_value_90d,
    -- trends
    0.0 AS ctr_trend_7d_vs_30d,
    0.0 AS cvr_trend_7d_vs_30d,
    1.0 AS ctr_vs_ad_group,
    1.0 AS cvr_vs_ad_group,
    0   AS days_since_creation,
    impressions_30d < 1000 AS low_data_impressions,
    clicks_30d < 100       AS low_data_clicks,
    (impressions_30d < 1000 OR clicks_30d < 100) AS low_data_flag
FROM base
""")

n = conn.execute("SELECT COUNT(*) FROM analytics.ad_features_daily").fetchone()[0]
print(f"  Created ad_features_daily: {n:,} rows")

conn.close()

# Copy to readonly
print("\nCopying to warehouse_readonly.duckdb...")
conn_ro = duckdb.connect('warehouse_readonly.duckdb')
conn_ro.execute("ATTACH 'warehouse.duckdb' AS src (READ_ONLY)")

for table in ['ad_features_daily', 'campaign_features_daily', 'keyword_features_daily']:
    try:
        existing = conn_ro.execute(
            "SELECT table_type FROM information_schema.tables WHERE table_schema='analytics' AND table_name=?",
            [table]
        ).fetchone()
        if existing:
            drop = "DROP VIEW" if existing[0] == 'VIEW' else "DROP TABLE"
            conn_ro.execute(f"{drop} analytics.{table}")
        conn_ro.execute(f"CREATE TABLE analytics.{table} AS SELECT * FROM src.analytics.{table}")
        n = conn_ro.execute(f"SELECT COUNT(*) FROM analytics.{table}").fetchone()[0]
        cid_n = conn_ro.execute(f"SELECT COUNT(*) FROM analytics.{table} WHERE customer_id=?", [CID]).fetchone()[0]
        print(f"  ✅ {table}: {n:,} total ({cid_n:,} Christopher Hoole)")
    except Exception as e:
        print(f"  ❌ {table}: {e}")

conn_ro.execute("DETACH src")
conn_ro.close()

print("\n✅ Done. Restart Flask and test /ads and /keywords.")
