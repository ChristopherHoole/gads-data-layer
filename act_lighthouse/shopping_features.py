from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional

import duckdb

from .config import ClientConfig


@dataclass(frozen=True)
class ProductFeatureBuildResult:
    rows_inserted: int
    has_conversion_value: bool
    start_date: date
    end_date: date


# ── Windows ──────────────────────────────────────────────────────────
WINDOWS = [7, 14, 30, 90]
BASE_METRICS = ["impressions", "clicks", "cost_micros", "conversions", "conversions_value"]


# ── Table DDL ────────────────────────────────────────────────────────

def _ensure_product_features_table(con: duckdb.DuckDBPyConnection) -> None:
    con.execute("CREATE SCHEMA IF NOT EXISTS analytics;")
    
    # DROP existing table to avoid column mismatch
    con.execute("DROP TABLE IF EXISTS analytics.product_features_daily;")

    cols: list[tuple[str, str, bool]] = []

    # Identity
    cols.extend([
        ("client_id", "TEXT", True),
        ("customer_id", "TEXT", True),
        ("campaign_id", "TEXT", True),
        ("ad_group_id", "TEXT", True),
        ("product_id", "TEXT", True),
        ("snapshot_date", "DATE", True),
    ])

    # Dimensions
    cols.extend([
        ("product_title", "TEXT", False),
        ("product_brand", "TEXT", False),
        ("product_category", "TEXT", False),
        ("product_type_l1", "TEXT", False),
        ("product_type_l2", "TEXT", False),
        ("availability", "TEXT", False),
        ("condition", "TEXT", False),
        ("custom_label_0", "TEXT", False),
        ("custom_label_1", "TEXT", False),
    ])

    # Price
    cols.extend([
        ("product_price_micros", "BIGINT", False),
        ("product_sale_price_micros", "BIGINT", False),
    ])

    # Meta
    cols.extend([
        ("feature_set_version", "TEXT", True),
        ("schema_version", "INTEGER", True),
        ("generated_at_utc", "TIMESTAMP", True),
        ("source_table", "TEXT", True),
    ])

    # Rolling window sums: 7, 14, 30, 90 days
    for w in WINDOWS:
        for m in BASE_METRICS:
            cols.append((f"{m}_w{w}_sum", "DOUBLE", False))

    # Derived efficiency metrics per window
    for w in WINDOWS:
        cols.append((f"ctr_w{w}", "DOUBLE", False))
        cols.append((f"cpc_w{w}", "DOUBLE", False))
        cols.append((f"cvr_w{w}", "DOUBLE", False))
        cols.append((f"cpa_w{w}", "DOUBLE", False))
        cols.append((f"roas_w{w}", "DOUBLE", False))

    # vs_prev percentages (7d only)
    cols.append(("cpa_w7_vs_prev_pct", "DOUBLE", False))
    cols.append(("roas_w7_vs_prev_pct", "DOUBLE", False))
    cols.append(("ctr_w7_vs_prev_pct", "DOUBLE", False))
    cols.append(("cvr_w7_vs_prev_pct", "DOUBLE", False))

    # Volatility
    cols.append(("cost_w14_cv", "DOUBLE", False))

    # Benchmark comparison
    cols.append(("benchmark_ctr_w30", "DOUBLE", False))
    cols.append(("ctr_vs_benchmark_pct", "DOUBLE", False))

    # Stock-out detection
    cols.append(("stock_out_flag", "BOOLEAN", False))
    cols.append(("stock_out_days_w30", "INTEGER", False))

    # Feed quality
    cols.append(("feed_quality_score", "DOUBLE", False))
    cols.append(("has_price_mismatch", "BOOLEAN", False))
    cols.append(("has_disapproval", "BOOLEAN", False))

    # Lifecycle flags
    cols.append(("new_product_flag", "BOOLEAN", False))
    cols.append(("days_live", "INTEGER", False))
    cols.append(("low_data_flag", "BOOLEAN", False))

    # Build DDL
    col_defs = [
        f"{name} {dtype}{' NOT NULL' if notnull else ''}"
        for name, dtype, notnull in cols
    ]

    ddl = f"""
    CREATE TABLE IF NOT EXISTS analytics.product_features_daily (
        {', '.join(col_defs)}
    );
    """
    con.execute(ddl)


# ── Build Features ───────────────────────────────────────────────────

def build_product_features_daily(
    con: duckdb.DuckDBPyConnection,
    cfg: ClientConfig,
    snapshot_date: date,
    feature_set_version: str = "lighthouse_shopping_v0",
    schema_version: int = 1,
) -> ProductFeatureBuildResult:
    """
    Reads from raw_product_performance_daily and raw_product_feed_quality,
    writes into analytics.product_features_daily.
    """
    _ensure_product_features_table(con)

    end_date = snapshot_date
    start_date = snapshot_date - timedelta(days=89)
    vol_start = snapshot_date - timedelta(days=13)

    # Check if conversion_value column exists
    try:
        test = con.execute(
            "SELECT conversions_value FROM raw_product_performance_daily LIMIT 0"
        ).fetchall()
        has_conv_value = True
    except Exception:
        has_conv_value = False

    conv_value_col = "conversions_value" if has_conv_value else "0 AS conversions_value"

    # Build SQL
    sql = f"""
    WITH product_daily AS (
        SELECT
            '{cfg.client_id}' AS client_id,
            customer_id, campaign_id, ad_group_id, product_id, snapshot_date,
            product_title, product_brand, product_category,
            product_type_l1, product_type_l2,
            product_price_micros, product_sale_price_micros,
            availability, condition, custom_label_0, custom_label_1,
            impressions, clicks, cost_micros, conversions,
            {conv_value_col},
            CASE WHEN availability = 'OUT_OF_STOCK' THEN 1 ELSE 0 END AS stock_out_day
        FROM raw_product_performance_daily
        WHERE snapshot_date BETWEEN '{start_date}' AND '{end_date}'
            AND customer_id = '{cfg.customer_id}'
    ),
    
    product_latest AS (
        SELECT
            client_id, customer_id, campaign_id, ad_group_id, product_id,
            snapshot_date, product_title, product_brand, product_category,
            product_type_l1, product_type_l2, product_price_micros,
            product_sale_price_micros, availability, condition,
            custom_label_0, custom_label_1
        FROM product_daily
        WHERE snapshot_date = '{end_date}'
    ),
    
    windows AS (
        SELECT
            p.client_id, p.customer_id, p.campaign_id, p.ad_group_id, p.product_id,
            -- 7d
            SUM(CASE WHEN pd.snapshot_date BETWEEN '{end_date - timedelta(days=6)}' AND '{end_date}' THEN pd.impressions ELSE 0 END) AS impressions_w7_sum,
            SUM(CASE WHEN pd.snapshot_date BETWEEN '{end_date - timedelta(days=6)}' AND '{end_date}' THEN pd.clicks ELSE 0 END) AS clicks_w7_sum,
            SUM(CASE WHEN pd.snapshot_date BETWEEN '{end_date - timedelta(days=6)}' AND '{end_date}' THEN pd.cost_micros ELSE 0 END) AS cost_micros_w7_sum,
            SUM(CASE WHEN pd.snapshot_date BETWEEN '{end_date - timedelta(days=6)}' AND '{end_date}' THEN pd.conversions ELSE 0 END) AS conversions_w7_sum,
            SUM(CASE WHEN pd.snapshot_date BETWEEN '{end_date - timedelta(days=6)}' AND '{end_date}' THEN pd.conversions_value ELSE 0 END) AS conversions_value_w7_sum,
            -- 14d
            SUM(CASE WHEN pd.snapshot_date BETWEEN '{end_date - timedelta(days=13)}' AND '{end_date}' THEN pd.impressions ELSE 0 END) AS impressions_w14_sum,
            SUM(CASE WHEN pd.snapshot_date BETWEEN '{end_date - timedelta(days=13)}' AND '{end_date}' THEN pd.clicks ELSE 0 END) AS clicks_w14_sum,
            SUM(CASE WHEN pd.snapshot_date BETWEEN '{end_date - timedelta(days=13)}' AND '{end_date}' THEN pd.cost_micros ELSE 0 END) AS cost_micros_w14_sum,
            SUM(CASE WHEN pd.snapshot_date BETWEEN '{end_date - timedelta(days=13)}' AND '{end_date}' THEN pd.conversions ELSE 0 END) AS conversions_w14_sum,
            SUM(CASE WHEN pd.snapshot_date BETWEEN '{end_date - timedelta(days=13)}' AND '{end_date}' THEN pd.conversions_value ELSE 0 END) AS conversions_value_w14_sum,
            -- 30d
            SUM(CASE WHEN pd.snapshot_date BETWEEN '{end_date - timedelta(days=29)}' AND '{end_date}' THEN pd.impressions ELSE 0 END) AS impressions_w30_sum,
            SUM(CASE WHEN pd.snapshot_date BETWEEN '{end_date - timedelta(days=29)}' AND '{end_date}' THEN pd.clicks ELSE 0 END) AS clicks_w30_sum,
            SUM(CASE WHEN pd.snapshot_date BETWEEN '{end_date - timedelta(days=29)}' AND '{end_date}' THEN pd.cost_micros ELSE 0 END) AS cost_micros_w30_sum,
            SUM(CASE WHEN pd.snapshot_date BETWEEN '{end_date - timedelta(days=29)}' AND '{end_date}' THEN pd.conversions ELSE 0 END) AS conversions_w30_sum,
            SUM(CASE WHEN pd.snapshot_date BETWEEN '{end_date - timedelta(days=29)}' AND '{end_date}' THEN pd.conversions_value ELSE 0 END) AS conversions_value_w30_sum,
            -- 90d
            SUM(CASE WHEN pd.snapshot_date BETWEEN '{end_date - timedelta(days=89)}' AND '{end_date}' THEN pd.impressions ELSE 0 END) AS impressions_w90_sum,
            SUM(CASE WHEN pd.snapshot_date BETWEEN '{end_date - timedelta(days=89)}' AND '{end_date}' THEN pd.clicks ELSE 0 END) AS clicks_w90_sum,
            SUM(CASE WHEN pd.snapshot_date BETWEEN '{end_date - timedelta(days=89)}' AND '{end_date}' THEN pd.cost_micros ELSE 0 END) AS cost_micros_w90_sum,
            SUM(CASE WHEN pd.snapshot_date BETWEEN '{end_date - timedelta(days=89)}' AND '{end_date}' THEN pd.conversions ELSE 0 END) AS conversions_w90_sum,
            SUM(CASE WHEN pd.snapshot_date BETWEEN '{end_date - timedelta(days=89)}' AND '{end_date}' THEN pd.conversions_value ELSE 0 END) AS conversions_value_w90_sum,
            -- Volatility
            CASE 
                WHEN AVG(CASE WHEN pd.snapshot_date BETWEEN '{vol_start}' AND '{end_date}' THEN pd.cost_micros END) > 0 
                THEN STDDEV(CASE WHEN pd.snapshot_date BETWEEN '{vol_start}' AND '{end_date}' THEN pd.cost_micros END) 
                     / AVG(CASE WHEN pd.snapshot_date BETWEEN '{vol_start}' AND '{end_date}' THEN pd.cost_micros END)
                ELSE NULL
            END AS cost_w14_cv,
            -- Stock-out
            SUM(CASE WHEN pd.snapshot_date BETWEEN '{end_date - timedelta(days=29)}' AND '{end_date}' THEN pd.stock_out_day ELSE 0 END) AS stock_out_days_w30,
            -- First seen
            MIN(pd.snapshot_date) AS first_seen_date
        FROM product_latest p
        LEFT JOIN product_daily pd ON p.product_id = pd.product_id AND p.customer_id = pd.customer_id
        GROUP BY 1, 2, 3, 4, 5
    ),
    
    feed_quality AS (
        SELECT
            product_id,
            CASE 
                WHEN approval_status = 'APPROVED' AND price_mismatch = FALSE 
                     AND (disapproval_reasons IS NULL OR disapproval_reasons = [])
                THEN 1.0
                WHEN approval_status = 'APPROVED' AND price_mismatch = TRUE THEN 0.7
                WHEN approval_status = 'APPROVED' THEN 0.8
                WHEN approval_status = 'DISAPPROVED' THEN 0.3
                ELSE 0.5
            END AS feed_quality_score,
            price_mismatch AS has_price_mismatch,
            CASE WHEN approval_status = 'DISAPPROVED' THEN TRUE ELSE FALSE END AS has_disapproval
        FROM raw_product_feed_quality
        WHERE snapshot_date = '{end_date}' AND customer_id = '{cfg.customer_id}'
    )
    
    INSERT INTO analytics.product_features_daily
    SELECT
        pl.client_id, pl.customer_id, pl.campaign_id, pl.ad_group_id, pl.product_id,
        '{end_date}' AS snapshot_date,
        pl.product_title, pl.product_brand, pl.product_category,
        pl.product_type_l1, pl.product_type_l2,
        pl.availability, pl.condition, pl.custom_label_0, pl.custom_label_1,
        pl.product_price_micros, pl.product_sale_price_micros,
        '{feature_set_version}' AS feature_set_version,
        {schema_version} AS schema_version,
        CURRENT_TIMESTAMP AS generated_at_utc,
        'raw_product_performance_daily' AS source_table,
        -- Window sums (20 columns: 4 windows × 5 metrics)
        w.impressions_w7_sum, w.clicks_w7_sum, w.cost_micros_w7_sum, w.conversions_w7_sum, w.conversions_value_w7_sum,
        w.impressions_w14_sum, w.clicks_w14_sum, w.cost_micros_w14_sum, w.conversions_w14_sum, w.conversions_value_w14_sum,
        w.impressions_w30_sum, w.clicks_w30_sum, w.cost_micros_w30_sum, w.conversions_w30_sum, w.conversions_value_w30_sum,
        w.impressions_w90_sum, w.clicks_w90_sum, w.cost_micros_w90_sum, w.conversions_w90_sum, w.conversions_value_w90_sum,
        -- Derived metrics (20 columns: 4 windows × 5 metrics) - GROUPED BY WINDOW
        -- W7 metrics
        CASE WHEN w.impressions_w7_sum > 0 THEN w.clicks_w7_sum / w.impressions_w7_sum ELSE 0 END AS ctr_w7,
        CASE WHEN w.clicks_w7_sum > 0 THEN (w.cost_micros_w7_sum / 1000000.0) / w.clicks_w7_sum ELSE 0 END AS cpc_w7,
        CASE WHEN w.clicks_w7_sum > 0 THEN w.conversions_w7_sum / w.clicks_w7_sum ELSE 0 END AS cvr_w7,
        CASE WHEN w.conversions_w7_sum > 0 THEN w.cost_micros_w7_sum / w.conversions_w7_sum ELSE 0 END AS cpa_w7,
        CASE WHEN w.cost_micros_w7_sum > 0 THEN w.conversions_value_w7_sum / w.cost_micros_w7_sum ELSE 0 END AS roas_w7,
        -- W14 metrics
        CASE WHEN w.impressions_w14_sum > 0 THEN w.clicks_w14_sum / w.impressions_w14_sum ELSE 0 END AS ctr_w14,
        CASE WHEN w.clicks_w14_sum > 0 THEN (w.cost_micros_w14_sum / 1000000.0) / w.clicks_w14_sum ELSE 0 END AS cpc_w14,
        CASE WHEN w.clicks_w14_sum > 0 THEN w.conversions_w14_sum / w.clicks_w14_sum ELSE 0 END AS cvr_w14,
        CASE WHEN w.conversions_w14_sum > 0 THEN w.cost_micros_w14_sum / w.conversions_w14_sum ELSE 0 END AS cpa_w14,
        CASE WHEN w.cost_micros_w14_sum > 0 THEN w.conversions_value_w14_sum / w.cost_micros_w14_sum ELSE 0 END AS roas_w14,
        -- W30 metrics
        CASE WHEN w.impressions_w30_sum > 0 THEN w.clicks_w30_sum / w.impressions_w30_sum ELSE 0 END AS ctr_w30,
        CASE WHEN w.clicks_w30_sum > 0 THEN (w.cost_micros_w30_sum / 1000000.0) / w.clicks_w30_sum ELSE 0 END AS cpc_w30,
        CASE WHEN w.clicks_w30_sum > 0 THEN w.conversions_w30_sum / w.clicks_w30_sum ELSE 0 END AS cvr_w30,
        CASE WHEN w.conversions_w30_sum > 0 THEN w.cost_micros_w30_sum / w.conversions_w30_sum ELSE 0 END AS cpa_w30,
        CASE WHEN w.cost_micros_w30_sum > 0 THEN w.conversions_value_w30_sum / w.cost_micros_w30_sum ELSE 0 END AS roas_w30,
        -- W90 metrics
        CASE WHEN w.impressions_w90_sum > 0 THEN w.clicks_w90_sum / w.impressions_w90_sum ELSE 0 END AS ctr_w90,
        CASE WHEN w.clicks_w90_sum > 0 THEN (w.cost_micros_w90_sum / 1000000.0) / w.clicks_w90_sum ELSE 0 END AS cpc_w90,
        CASE WHEN w.clicks_w90_sum > 0 THEN w.conversions_w90_sum / w.clicks_w90_sum ELSE 0 END AS cvr_w90,
        CASE WHEN w.conversions_w90_sum > 0 THEN w.cost_micros_w90_sum / w.conversions_w90_sum ELSE 0 END AS cpa_w90,
        CASE WHEN w.cost_micros_w90_sum > 0 THEN w.conversions_value_w90_sum / w.cost_micros_w90_sum ELSE 0 END AS roas_w90,
        -- vs_prev (4 columns - 7d only, set to NULL)
        NULL AS cpa_w7_vs_prev_pct,
        NULL AS roas_w7_vs_prev_pct,
        NULL AS ctr_w7_vs_prev_pct,
        NULL AS cvr_w7_vs_prev_pct,
        -- Volatility (1 column)
        w.cost_w14_cv,
        -- Benchmarks (2 columns)
        0.025 AS benchmark_ctr_w30,
        CASE WHEN (w.clicks_w30_sum / NULLIF(w.impressions_w30_sum, 0)) > 0 
             THEN (((w.clicks_w30_sum / NULLIF(w.impressions_w30_sum, 0)) - 0.025) / 0.025) * 100 
             ELSE 0 
        END AS ctr_vs_benchmark_pct,
        -- Stock-out (2 columns)
        CASE WHEN w.stock_out_days_w30 > 0 THEN TRUE ELSE FALSE END AS stock_out_flag,
        w.stock_out_days_w30,
        -- Feed quality (3 columns)
        COALESCE(fq.feed_quality_score, 0.5) AS feed_quality_score,
        COALESCE(fq.has_price_mismatch, FALSE) AS has_price_mismatch,
        COALESCE(fq.has_disapproval, FALSE) AS has_disapproval,
        -- Lifecycle (3 columns)
        CASE WHEN ('{end_date}'::DATE - w.first_seen_date) <= 30 THEN TRUE ELSE FALSE END AS new_product_flag,
        ('{end_date}'::DATE - w.first_seen_date) AS days_live,
        CASE WHEN w.clicks_w30_sum < 10 OR w.conversions_w30_sum < 2 THEN TRUE ELSE FALSE END AS low_data_flag
    FROM product_latest pl
    INNER JOIN windows w ON pl.product_id = w.product_id AND pl.customer_id = w.customer_id
    LEFT JOIN feed_quality fq ON pl.product_id = fq.product_id
    """

    con.execute(sql)
    
    result = con.execute(
        f"SELECT COUNT(*) AS cnt FROM analytics.product_features_daily WHERE snapshot_date = '{end_date}' AND customer_id = '{cfg.customer_id}'"
    ).fetchone()
    
    rows_inserted = result[0] if result else 0

    return ProductFeatureBuildResult(
        rows_inserted=rows_inserted,
        has_conversion_value=has_conv_value,
        start_date=start_date,
        end_date=end_date,
    )
