"""
Build keyword_features_daily directly from keyword_daily using SQL.
No pipeline, no WAL issues. Same approach as build_ad_features_direct.py.
"""
import duckdb
from datetime import date, timedelta

CID       = "1254895944"
SNAP_DATE = date(2026, 3, 16)

print("=" * 60)
print("BUILD keyword_features_daily — Christopher Hoole")
print("=" * 60)

conn = duckdb.connect('warehouse.duckdb')
conn.execute("ATTACH 'warehouse_readonly.duckdb' AS ro (READ_ONLY)")

snap  = str(SNAP_DATE)
d7    = str(SNAP_DATE - timedelta(days=7))
d14   = str(SNAP_DATE - timedelta(days=14))
d30   = str(SNAP_DATE - timedelta(days=30))
d90   = str(SNAP_DATE - timedelta(days=90))
dp7   = str(SNAP_DATE - timedelta(days=14))   # prev 7d start
dp30  = str(SNAP_DATE - timedelta(days=60))   # prev 30d start

print(f"\nBuilding features for snapshot_date={snap}...")

conn.execute("DROP TABLE IF EXISTS analytics.keyword_features_daily")
conn.execute(f"""
CREATE TABLE analytics.keyword_features_daily AS
WITH dims AS (
    -- Latest dimension values per keyword
    SELECT
        customer_id,
        campaign_id,
        campaign_name,
        ad_group_id,
        ad_group_name,
        keyword_id,
        keyword_text,
        match_type,
        status,
        quality_score,
        quality_score_creative,
        quality_score_landing_page,
        quality_score_relevance,
        bid_micros,
        first_page_cpc_micros,
        top_of_page_cpc_micros
    FROM ro.analytics.keyword_daily
    WHERE customer_id = '{CID}'
      AND snapshot_date = '{snap}'
),
agg AS (
    SELECT
        customer_id,
        keyword_id,
        -- w7 sums
        SUM(CASE WHEN snapshot_date >= '{d7}'  THEN impressions ELSE 0 END) AS impressions_w7_sum,
        SUM(CASE WHEN snapshot_date >= '{d7}'  THEN clicks      ELSE 0 END) AS clicks_w7_sum,
        SUM(CASE WHEN snapshot_date >= '{d7}'  THEN cost_micros ELSE 0 END) AS cost_micros_w7_sum,
        SUM(CASE WHEN snapshot_date >= '{d7}'  THEN conversions ELSE 0 END) AS conversions_w7_sum,
        SUM(CASE WHEN snapshot_date >= '{d7}'  THEN conversions_value ELSE 0 END) AS conversion_value_w7_sum,
        -- w7 prev
        SUM(CASE WHEN snapshot_date BETWEEN '{dp7}' AND '{d7}' THEN impressions ELSE 0 END) AS impressions_w7_prev,
        SUM(CASE WHEN snapshot_date BETWEEN '{dp7}' AND '{d7}' THEN clicks      ELSE 0 END) AS clicks_w7_prev,
        SUM(CASE WHEN snapshot_date BETWEEN '{dp7}' AND '{d7}' THEN cost_micros ELSE 0 END) AS cost_micros_w7_prev,
        SUM(CASE WHEN snapshot_date BETWEEN '{dp7}' AND '{d7}' THEN conversions ELSE 0 END) AS conversions_w7_prev,
        -- w14 sums
        SUM(CASE WHEN snapshot_date >= '{d14}' THEN impressions ELSE 0 END) AS impressions_w14_sum,
        SUM(CASE WHEN snapshot_date >= '{d14}' THEN clicks      ELSE 0 END) AS clicks_w14_sum,
        SUM(CASE WHEN snapshot_date >= '{d14}' THEN cost_micros ELSE 0 END) AS cost_micros_w14_sum,
        SUM(CASE WHEN snapshot_date >= '{d14}' THEN conversions ELSE 0 END) AS conversions_w14_sum,
        -- w30 sums
        SUM(CASE WHEN snapshot_date >= '{d30}' THEN impressions ELSE 0 END) AS impressions_w30_sum,
        SUM(CASE WHEN snapshot_date >= '{d30}' THEN clicks      ELSE 0 END) AS clicks_w30_sum,
        SUM(CASE WHEN snapshot_date >= '{d30}' THEN cost_micros ELSE 0 END) AS cost_micros_w30_sum,
        SUM(CASE WHEN snapshot_date >= '{d30}' THEN conversions ELSE 0 END) AS conversions_w30_sum,
        SUM(CASE WHEN snapshot_date >= '{d30}' THEN conversions_value ELSE 0 END) AS conversion_value_w30_sum,
        -- w30 prev
        SUM(CASE WHEN snapshot_date BETWEEN '{dp30}' AND '{d30}' THEN impressions ELSE 0 END) AS impressions_w30_prev,
        SUM(CASE WHEN snapshot_date BETWEEN '{dp30}' AND '{d30}' THEN clicks      ELSE 0 END) AS clicks_w30_prev,
        SUM(CASE WHEN snapshot_date BETWEEN '{dp30}' AND '{d30}' THEN cost_micros ELSE 0 END) AS cost_micros_w30_prev,
        SUM(CASE WHEN snapshot_date BETWEEN '{dp30}' AND '{d30}' THEN conversions ELSE 0 END) AS conversions_w30_prev,
        -- w90 sums
        SUM(CASE WHEN snapshot_date >= '{d90}' THEN cost_micros ELSE 0 END) AS cost_micros_w90_sum,
        SUM(CASE WHEN snapshot_date >= '{d90}' THEN conversions ELSE 0 END) AS conversions_w90_sum,
        SUM(CASE WHEN snapshot_date >= '{d90}' THEN conversions_value ELSE 0 END) AS conversion_value_w90_sum
    FROM ro.analytics.keyword_daily
    WHERE customer_id = '{CID}'
      AND snapshot_date <= '{snap}'
    GROUP BY customer_id, keyword_id
)
SELECT
    '{CID}'                                         AS client_id,
    dims.customer_id,
    dims.campaign_id,
    dims.ad_group_id,
    dims.keyword_id,
    '{snap}'::DATE                                  AS snapshot_date,
    dims.keyword_text,
    dims.match_type,
    dims.status,
    dims.campaign_name,
    dims.ad_group_name,
    dims.quality_score,
    dims.quality_score_creative,
    dims.quality_score_landing_page,
    dims.quality_score_relevance,
    dims.bid_micros,
    dims.first_page_cpc_micros,
    dims.top_of_page_cpc_micros,
    'direct_sql_v1'                                 AS feature_set_version,
    1                                               AS schema_version,
    NOW()                                           AS generated_at_utc,
    -- w7
    agg.impressions_w7_sum,
    agg.clicks_w7_sum,
    agg.cost_micros_w7_sum,
    agg.conversions_w7_sum,
    agg.conversion_value_w7_sum,
    agg.impressions_w7_prev,
    agg.clicks_w7_prev,
    agg.cost_micros_w7_prev,
    agg.conversions_w7_prev,
    -- w7 derived
    CASE WHEN agg.impressions_w7_sum > 0 THEN agg.clicks_w7_sum::DOUBLE / agg.impressions_w7_sum ELSE NULL END AS ctr_w7,
    CASE WHEN agg.clicks_w7_sum > 0 THEN agg.cost_micros_w7_sum::DOUBLE / agg.clicks_w7_sum ELSE NULL END AS cpc_w7,
    CASE WHEN agg.clicks_w7_sum > 0 THEN agg.conversions_w7_sum::DOUBLE / agg.clicks_w7_sum ELSE NULL END AS cvr_w7,
    CASE WHEN agg.conversions_w7_sum > 0 THEN agg.cost_micros_w7_sum::DOUBLE / agg.conversions_w7_sum ELSE NULL END AS cpa_w7,
    CASE WHEN agg.cost_micros_w7_sum > 0 THEN agg.conversion_value_w7_sum / (agg.cost_micros_w7_sum/1e6) ELSE NULL END AS roas_w7,
    -- w14
    agg.impressions_w14_sum,
    agg.clicks_w14_sum,
    agg.cost_micros_w14_sum,
    agg.conversions_w14_sum,
    -- w30
    agg.impressions_w30_sum,
    agg.clicks_w30_sum,
    agg.cost_micros_w30_sum,
    agg.conversions_w30_sum,
    agg.conversion_value_w30_sum,
    agg.impressions_w30_prev,
    agg.clicks_w30_prev,
    agg.cost_micros_w30_prev,
    agg.conversions_w30_prev,
    -- w30 derived
    CASE WHEN agg.impressions_w30_sum > 0 THEN agg.clicks_w30_sum::DOUBLE / agg.impressions_w30_sum ELSE NULL END AS ctr_w30,
    CASE WHEN agg.clicks_w30_sum > 0 THEN agg.cost_micros_w30_sum::DOUBLE / agg.clicks_w30_sum ELSE NULL END AS cpc_w30,
    CASE WHEN agg.clicks_w30_sum > 0 THEN agg.conversions_w30_sum::DOUBLE / agg.clicks_w30_sum ELSE NULL END AS cvr_w30,
    CASE WHEN agg.conversions_w30_sum > 0 THEN agg.cost_micros_w30_sum::DOUBLE / agg.conversions_w30_sum ELSE NULL END AS cpa_w30,
    CASE WHEN agg.cost_micros_w30_sum > 0 THEN agg.conversion_value_w30_sum / (agg.cost_micros_w30_sum/1e6) ELSE NULL END AS roas_w30,
    -- vs prev pct
    CASE WHEN agg.impressions_w7_prev > 0 THEN (agg.impressions_w7_sum - agg.impressions_w7_prev)::DOUBLE / agg.impressions_w7_prev ELSE NULL END AS impressions_w7_vs_prev_pct,
    CASE WHEN agg.clicks_w7_prev > 0 THEN (agg.clicks_w7_sum - agg.clicks_w7_prev)::DOUBLE / agg.clicks_w7_prev ELSE NULL END AS clicks_w7_vs_prev_pct,
    CASE WHEN agg.cost_micros_w7_prev > 0 THEN (agg.cost_micros_w7_sum - agg.cost_micros_w7_prev)::DOUBLE / agg.cost_micros_w7_prev ELSE NULL END AS cost_micros_w7_vs_prev_pct,
    CASE WHEN agg.impressions_w30_prev > 0 THEN (agg.impressions_w30_sum - agg.impressions_w30_prev)::DOUBLE / agg.impressions_w30_prev ELSE NULL END AS impressions_w30_vs_prev_pct,
    CASE WHEN agg.clicks_w30_prev > 0 THEN (agg.clicks_w30_sum - agg.clicks_w30_prev)::DOUBLE / agg.clicks_w30_prev ELSE NULL END AS clicks_w30_vs_prev_pct,
    CASE WHEN agg.cost_micros_w30_prev > 0 THEN (agg.cost_micros_w30_sum - agg.cost_micros_w30_prev)::DOUBLE / agg.cost_micros_w30_prev ELSE NULL END AS cost_micros_w30_vs_prev_pct,
    -- w90
    agg.cost_micros_w90_sum,
    agg.conversions_w90_sum,
    agg.conversion_value_w90_sum,
    -- volatility (placeholder)
    NULL::DOUBLE AS cost_w14_cv,
    -- low data flags
    agg.clicks_w7_sum < 10                          AS low_data_clicks_7d,
    agg.impressions_w7_sum < 100                    AS low_data_impressions_7d,
    agg.conversions_w30_sum < 5                     AS low_data_conversions_30d,
    (agg.clicks_w7_sum < 10 OR agg.impressions_w7_sum < 100) AS low_data_flag
FROM dims
JOIN agg ON dims.customer_id = agg.customer_id AND dims.keyword_id = agg.keyword_id
""")

n = conn.execute("SELECT COUNT(*) FROM analytics.keyword_features_daily WHERE customer_id=?", [CID]).fetchone()[0]
print(f"  ✅ Created {n:,} rows in keyword_features_daily")

conn.execute("DETACH ro")
conn.close()
print("  ✅ Connection closed cleanly (no WAL)")

# Copy to readonly
print("\nCopying to warehouse_readonly.duckdb...")
conn_ro = duckdb.connect('warehouse_readonly.duckdb')
conn_ro.execute("ATTACH 'warehouse.duckdb' AS src (READ_ONLY)")
for table in ['keyword_features_daily', 'ad_features_daily', 'campaign_features_daily']:
    try:
        conn_ro.execute(f"DROP TABLE IF EXISTS analytics.{table}")
        conn_ro.execute(f"CREATE TABLE analytics.{table} AS SELECT * FROM src.analytics.{table}")
        n = conn_ro.execute(f"SELECT COUNT(*) FROM analytics.{table} WHERE customer_id=?", [CID]).fetchone()[0]
        print(f"  ✅ {table}: {n} Christopher Hoole rows")
    except Exception as e:
        print(f"  ❌ {table}: {e}")
conn_ro.execute("DETACH src")
conn_ro.close()

print("\n✅ All done. Start Flask now.")
