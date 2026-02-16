from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional

import duckdb

from .config import ClientConfig


@dataclass(frozen=True)
class KeywordFeatureBuildResult:
    rows_inserted: int
    has_conversion_value: bool
    start_date: date
    end_date: date


# ── Windows ──────────────────────────────────────────────────────────
WINDOWS = [7, 14, 30]
BASE_METRICS = ["impressions", "clicks", "cost_micros", "conversions", "conversion_value"]


# ── Table DDL ────────────────────────────────────────────────────────

def _ensure_keyword_features_table(con: duckdb.DuckDBPyConnection) -> None:
    con.execute("CREATE SCHEMA IF NOT EXISTS analytics;")

    cols: list[tuple[str, str, bool]] = []

    # Identity
    cols.extend([
        ("client_id", "TEXT", True),
        ("customer_id", "TEXT", True),
        ("campaign_id", "TEXT", True),
        ("ad_group_id", "TEXT", True),
        ("keyword_id", "TEXT", True),
        ("snapshot_date", "DATE", True),
    ])

    # Dimensions
    cols.extend([
        ("keyword_text", "TEXT", False),
        ("match_type", "TEXT", False),
        ("status", "TEXT", False),
        ("campaign_name", "TEXT", False),
        ("ad_group_name", "TEXT", False),
    ])

    # Quality Score
    cols.extend([
        ("quality_score", "INTEGER", False),
        ("quality_score_creative", "INTEGER", False),
        ("quality_score_landing_page", "INTEGER", False),
        ("quality_score_relevance", "INTEGER", False),
    ])

    # Bid
    cols.extend([
        ("bid_micros", "BIGINT", False),
        ("first_page_cpc_micros", "BIGINT", False),
        ("top_of_page_cpc_micros", "BIGINT", False),
    ])

    # Meta
    cols.extend([
        ("feature_set_version", "TEXT", True),
        ("schema_version", "INTEGER", True),
        ("generated_at_utc", "TIMESTAMP", True),
        ("source_table", "TEXT", True),
    ])

    # Rolling window sums: 7, 14, 30 days
    for w in WINDOWS:
        for m in BASE_METRICS:
            cols.append((f"{m}_w{w}_sum", "DOUBLE", False))

    # 90d sums for cost + conversions only (KW-PAUSE-002 needs 90d)
    cols.append(("cost_micros_w90_sum", "DOUBLE", False))
    cols.append(("conversions_w90_sum", "DOUBLE", False))
    cols.append(("conversion_value_w90_sum", "DOUBLE", False))

    # Derived efficiency metrics per window
    for w in WINDOWS:
        cols.append((f"ctr_w{w}", "DOUBLE", False))
        cols.append((f"cpc_w{w}", "DOUBLE", False))
        cols.append((f"cvr_w{w}", "DOUBLE", False))
        cols.append((f"cpa_w{w}", "DOUBLE", False))
        cols.append((f"roas_w{w}", "DOUBLE", False))

    # vs_prev percentages (current window vs equal previous period)
    for w in WINDOWS:
        cols.append((f"cpa_w{w}_vs_prev_pct", "DOUBLE", False))
        cols.append((f"roas_w{w}_vs_prev_pct", "DOUBLE", False))
        cols.append((f"ctr_w{w}_vs_prev_pct", "DOUBLE", False))
        cols.append((f"cvr_w{w}_vs_prev_pct", "DOUBLE", False))

    # Volatility
    cols.append(("cost_w14_cv", "DOUBLE", False))

    # Low data flags
    cols.extend([
        ("low_data_clicks_7d", "BOOLEAN", False),
        ("low_data_conversions_30d", "BOOLEAN", False),
        ("low_data_flag", "BOOLEAN", False),
    ])

    ddl_cols = []
    for name, typ, not_null in cols:
        nn = " NOT NULL" if not_null else ""
        ddl_cols.append(f"  {name} {typ}{nn}")

    ddl = "CREATE TABLE IF NOT EXISTS analytics.keyword_features_daily (\n"
    ddl += ",\n".join(ddl_cols)
    ddl += ",\n  PRIMARY KEY (client_id, customer_id, keyword_id, snapshot_date)\n);"

    con.execute(ddl)


# ── Date helpers ─────────────────────────────────────────────────────

def _fmt(d: date) -> str:
    return d.strftime("%Y-%m-%d")


# ── SQL builder ──────────────────────────────────────────────────────

def _build_agg_sql(snapshot_date: date) -> str:
    """Build the CASE WHEN aggregation expressions for all windows."""
    parts: list[str] = []

    for w in WINDOWS:
        w_start = snapshot_date - timedelta(days=w - 1)
        prev_start = snapshot_date - timedelta(days=2 * w - 1)
        prev_end = snapshot_date - timedelta(days=w)

        for m in BASE_METRICS:
            src_col = "conversions_value" if m == "conversion_value" else m
            # Current window sum
            parts.append(
                f"SUM(CASE WHEN snapshot_date >= '{_fmt(w_start)}' "
                f"THEN COALESCE({src_col}, 0) ELSE 0 END) AS {m}_w{w}_sum"
            )
            # Previous window sum
            parts.append(
                f"SUM(CASE WHEN snapshot_date BETWEEN '{_fmt(prev_start)}' AND '{_fmt(prev_end)}' "
                f"THEN COALESCE({src_col}, 0) ELSE 0 END) AS {m}_w{w}_prev"
            )

    # 90d sums (no prev needed)
    w90_start = snapshot_date - timedelta(days=89)
    parts.append(
        f"SUM(CASE WHEN snapshot_date >= '{_fmt(w90_start)}' "
        f"THEN COALESCE(cost_micros, 0) ELSE 0 END) AS cost_micros_w90_sum"
    )
    parts.append(
        f"SUM(CASE WHEN snapshot_date >= '{_fmt(w90_start)}' "
        f"THEN COALESCE(conversions, 0) ELSE 0 END) AS conversions_w90_sum"
    )
    parts.append(
        f"SUM(CASE WHEN snapshot_date >= '{_fmt(w90_start)}' "
        f"THEN COALESCE(conversions_value, 0) ELSE 0 END) AS conversion_value_w90_sum"
    )

    return ",\n        ".join(parts)


def _build_derived_sql() -> str:
    """Build derived efficiency metrics from aggregated sums."""
    parts: list[str] = []

    for w in WINDOWS:
        # CTR = clicks / impressions
        parts.append(
            f"CASE WHEN agg.impressions_w{w}_sum > 0 "
            f"THEN agg.clicks_w{w}_sum::DOUBLE / agg.impressions_w{w}_sum "
            f"ELSE NULL END AS ctr_w{w}"
        )
        # CPC = cost / clicks (in micros)
        parts.append(
            f"CASE WHEN agg.clicks_w{w}_sum > 0 "
            f"THEN agg.cost_micros_w{w}_sum::DOUBLE / agg.clicks_w{w}_sum "
            f"ELSE NULL END AS cpc_w{w}"
        )
        # CVR = conversions / clicks
        parts.append(
            f"CASE WHEN agg.clicks_w{w}_sum > 0 "
            f"THEN agg.conversions_w{w}_sum::DOUBLE / agg.clicks_w{w}_sum "
            f"ELSE NULL END AS cvr_w{w}"
        )
        # CPA = cost_micros / conversions
        parts.append(
            f"CASE WHEN agg.conversions_w{w}_sum > 0 "
            f"THEN agg.cost_micros_w{w}_sum::DOUBLE / agg.conversions_w{w}_sum "
            f"ELSE NULL END AS cpa_w{w}"
        )
        # ROAS = conversion_value / (cost_micros / 1e6)
        parts.append(
            f"CASE WHEN agg.cost_micros_w{w}_sum > 0 "
            f"THEN agg.conversion_value_w{w}_sum::DOUBLE / (agg.cost_micros_w{w}_sum::DOUBLE / 1000000.0) "
            f"ELSE NULL END AS roas_w{w}"
        )

    return ",\n        ".join(parts)


def _build_vs_prev_sql() -> str:
    """Build vs_prev percentage change expressions."""
    parts: list[str] = []

    for w in WINDOWS:
        # CPA vs prev: ((curr_cost/curr_conv) - (prev_cost/prev_conv)) / (prev_cost/prev_conv)
        parts.append(
            f"CASE WHEN agg.conversions_w{w}_sum > 0 AND agg.conversions_w{w}_prev > 0 "
            f"AND agg.cost_micros_w{w}_prev > 0 "
            f"THEN ((agg.cost_micros_w{w}_sum::DOUBLE / agg.conversions_w{w}_sum) "
            f"     - (agg.cost_micros_w{w}_prev::DOUBLE / agg.conversions_w{w}_prev)) "
            f"     / NULLIF(agg.cost_micros_w{w}_prev::DOUBLE / agg.conversions_w{w}_prev, 0) "
            f"ELSE NULL END AS cpa_w{w}_vs_prev_pct"
        )
        # ROAS vs prev
        parts.append(
            f"CASE WHEN agg.cost_micros_w{w}_sum > 0 AND agg.cost_micros_w{w}_prev > 0 "
            f"AND agg.conversion_value_w{w}_prev > 0 "
            f"THEN ((agg.conversion_value_w{w}_sum::DOUBLE / (agg.cost_micros_w{w}_sum::DOUBLE / 1000000.0)) "
            f"     - (agg.conversion_value_w{w}_prev::DOUBLE / (agg.cost_micros_w{w}_prev::DOUBLE / 1000000.0))) "
            f"     / NULLIF(agg.conversion_value_w{w}_prev::DOUBLE / (agg.cost_micros_w{w}_prev::DOUBLE / 1000000.0), 0) "
            f"ELSE NULL END AS roas_w{w}_vs_prev_pct"
        )
        # CTR vs prev
        parts.append(
            f"CASE WHEN agg.impressions_w{w}_sum > 0 AND agg.impressions_w{w}_prev > 0 "
            f"AND agg.clicks_w{w}_prev > 0 "
            f"THEN ((agg.clicks_w{w}_sum::DOUBLE / agg.impressions_w{w}_sum) "
            f"     - (agg.clicks_w{w}_prev::DOUBLE / agg.impressions_w{w}_prev)) "
            f"     / NULLIF(agg.clicks_w{w}_prev::DOUBLE / agg.impressions_w{w}_prev, 0) "
            f"ELSE NULL END AS ctr_w{w}_vs_prev_pct"
        )
        # CVR vs prev
        parts.append(
            f"CASE WHEN agg.clicks_w{w}_sum > 0 AND agg.clicks_w{w}_prev > 0 "
            f"AND agg.conversions_w{w}_prev > 0 "
            f"THEN ((agg.conversions_w{w}_sum::DOUBLE / agg.clicks_w{w}_sum) "
            f"     - (agg.conversions_w{w}_prev::DOUBLE / agg.clicks_w{w}_prev)) "
            f"     / NULLIF(agg.conversions_w{w}_prev::DOUBLE / agg.clicks_w{w}_prev, 0) "
            f"ELSE NULL END AS cvr_w{w}_vs_prev_pct"
        )

    return ",\n        ".join(parts)


# ── Insert column list ───────────────────────────────────────────────

def _insert_columns() -> list[str]:
    """Return ordered list of columns for INSERT INTO."""
    cols = [
        "client_id", "customer_id", "campaign_id", "ad_group_id",
        "keyword_id", "snapshot_date",
        "keyword_text", "match_type", "status", "campaign_name", "ad_group_name",
        "quality_score", "quality_score_creative",
        "quality_score_landing_page", "quality_score_relevance",
        "bid_micros", "first_page_cpc_micros", "top_of_page_cpc_micros",
        "feature_set_version", "schema_version", "generated_at_utc", "source_table",
    ]

    for w in WINDOWS:
        for m in BASE_METRICS:
            cols.append(f"{m}_w{w}_sum")

    cols.extend(["cost_micros_w90_sum", "conversions_w90_sum", "conversion_value_w90_sum"])

    for w in WINDOWS:
        cols.extend([f"ctr_w{w}", f"cpc_w{w}", f"cvr_w{w}", f"cpa_w{w}", f"roas_w{w}"])

    for w in WINDOWS:
        cols.extend([
            f"cpa_w{w}_vs_prev_pct", f"roas_w{w}_vs_prev_pct",
            f"ctr_w{w}_vs_prev_pct", f"cvr_w{w}_vs_prev_pct",
        ])

    cols.append("cost_w14_cv")
    cols.extend(["low_data_clicks_7d", "low_data_conversions_30d", "low_data_flag"])

    return cols


# ── Main builder ─────────────────────────────────────────────────────

def build_keyword_features_daily(
    con: duckdb.DuckDBPyConnection,
    cfg: ClientConfig,
    snapshot_date: date,
    feature_set_version: str = "lighthouse_keyword_v0",
    schema_version: int = 1,
) -> KeywordFeatureBuildResult:
    """
    Reads from ro.analytics.keyword_daily (readonly DB attached as 'ro'),
    writes into analytics.keyword_features_daily (build DB).

    Computes rolling window aggregates (7/14/30/90 day), derived efficiency
    metrics, QS tracking, bid info, volatility, and low-data flags for each
    keyword at the snapshot_date.
    """
    _ensure_keyword_features_table(con)

    end_date = snapshot_date
    # Need 60 days for 30d + prev_30d comparison, 90 days for w90 sums
    start_date = snapshot_date - timedelta(days=89)
    vol_start = snapshot_date - timedelta(days=13)  # 14d for CV

    # Check if conversion_value column exists
    try:
        test = con.execute(
            "SELECT conversions_value FROM ro.analytics.keyword_daily LIMIT 0"
        ).fetchall()
        has_conv_value = True
    except Exception:
        has_conv_value = False

    agg_sql = _build_agg_sql(snapshot_date)
    derived_sql = _build_derived_sql()
    vs_prev_sql = _build_vs_prev_sql()

    insert_cols = _insert_columns()
    insert_cols_sql = ", ".join(insert_cols)

    # Build select columns matching insert order
    select_parts = [
        "? AS client_id",
        "agg.customer_id",
        "agg.campaign_id",
        "agg.ad_group_id",
        "agg.keyword_id",
        f"'{_fmt(snapshot_date)}'::DATE AS snapshot_date",
        "dims.keyword_text",
        "dims.match_type",
        "dims.status",
        "dims.campaign_name",
        "dims.ad_group_name",
        "dims.quality_score",
        "dims.quality_score_creative",
        "dims.quality_score_landing_page",
        "dims.quality_score_relevance",
        "dims.bid_micros",
        "dims.first_page_cpc_micros",
        "dims.top_of_page_cpc_micros",
        f"? AS feature_set_version",
        f"? AS schema_version",
        "NOW() AS generated_at_utc",
        "'analytics.keyword_daily' AS source_table",
    ]

    # Rolling window sums
    for w in WINDOWS:
        for m in BASE_METRICS:
            select_parts.append(f"agg.{m}_w{w}_sum")

    select_parts.extend([
        "agg.cost_micros_w90_sum",
        "agg.conversions_w90_sum",
        "agg.conversion_value_w90_sum",
    ])

    # Derived (these are computed in the outer select)
    # Added via derived_sql placeholder below

    # vs_prev (computed in outer select)
    # Added via vs_prev_sql placeholder below

    # Volatility + low data
    # Added below

    sql = f"""
    WITH kw_data AS (
        SELECT
            CAST(customer_id AS VARCHAR) AS customer_id,
            CAST(campaign_id AS VARCHAR) AS campaign_id,
            CAST(ad_group_id AS VARCHAR) AS ad_group_id,
            CAST(keyword_id AS VARCHAR) AS keyword_id,
            CAST(snapshot_date AS DATE) AS snapshot_date,
            keyword_text,
            match_type,
            status,
            campaign_name,
            ad_group_name,
            quality_score,
            quality_score_creative,
            quality_score_landing_page,
            quality_score_relevance,
            bid_micros,
            first_page_cpc_micros,
            top_of_page_cpc_micros,
            COALESCE(impressions, 0) AS impressions,
            COALESCE(clicks, 0) AS clicks,
            COALESCE(cost_micros, 0) AS cost_micros,
            COALESCE(conversions, 0) AS conversions,
            COALESCE(conversions_value, 0) AS conversions_value
        FROM ro.analytics.keyword_daily
        WHERE CAST(customer_id AS VARCHAR) = ?
          AND CAST(snapshot_date AS DATE) BETWEEN '{_fmt(start_date)}' AND '{_fmt(end_date)}'
    ),
    kw_agg AS (
        SELECT
            customer_id,
            campaign_id,
            ad_group_id,
            keyword_id,
            {agg_sql}
        FROM kw_data
        GROUP BY customer_id, campaign_id, ad_group_id, keyword_id
    ),
    kw_dims AS (
        SELECT * FROM (
            SELECT
                keyword_id AS dims_keyword_id,
                keyword_text,
                match_type,
                status,
                campaign_name,
                ad_group_name,
                quality_score,
                quality_score_creative,
                quality_score_landing_page,
                quality_score_relevance,
                bid_micros,
                first_page_cpc_micros,
                top_of_page_cpc_micros,
                ROW_NUMBER() OVER (
                    PARTITION BY keyword_id
                    ORDER BY snapshot_date DESC
                ) AS rn
            FROM kw_data
        ) sub
        WHERE rn = 1
    ),
    kw_vol AS (
        SELECT
            keyword_id AS vol_keyword_id,
            CASE WHEN AVG(cost_micros) = 0 OR COUNT(*) < 3 THEN NULL
                 ELSE STDDEV_SAMP(cost_micros) / NULLIF(AVG(cost_micros), 0)
            END AS cost_w14_cv
        FROM kw_data
        WHERE snapshot_date >= '{_fmt(vol_start)}'
        GROUP BY keyword_id
    )
    SELECT
        ? AS client_id,
        agg.customer_id,
        agg.campaign_id,
        agg.ad_group_id,
        agg.keyword_id,
        '{_fmt(snapshot_date)}'::DATE AS snapshot_date,

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

        ? AS feature_set_version,
        ? AS schema_version,
        NOW() AS generated_at_utc,
        'analytics.keyword_daily' AS source_table,

        {", ".join(f"agg.{m}_w{w}_sum" for w in WINDOWS for m in BASE_METRICS)},

        agg.cost_micros_w90_sum,
        agg.conversions_w90_sum,
        agg.conversion_value_w90_sum,

        {derived_sql},

        {vs_prev_sql},

        vol.cost_w14_cv,

        (agg.clicks_w7_sum < 30) AS low_data_clicks_7d,
        (agg.conversions_w30_sum < 15) AS low_data_conversions_30d,
        ((agg.clicks_w7_sum < 30) OR (agg.conversions_w30_sum < 15)) AS low_data_flag

    FROM kw_agg agg
    LEFT JOIN kw_dims dims ON dims.dims_keyword_id = agg.keyword_id
    LEFT JOIN kw_vol vol ON vol.vol_keyword_id = agg.keyword_id;
    """

    # Idempotent delete
    con.execute(
        """
        DELETE FROM analytics.keyword_features_daily
        WHERE client_id = ?
          AND customer_id = ?
          AND snapshot_date = ?;
        """,
        [cfg.client_id, cfg.customer_id, snapshot_date],
    )

    params = [
        cfg.customer_id,   # WHERE customer_id = ?
        cfg.client_id,     # client_id
        feature_set_version,
        schema_version,
    ]

    con.execute(
        f"INSERT INTO analytics.keyword_features_daily ({insert_cols_sql}) " + sql,
        params,
    )

    rows = con.execute(
        """
        SELECT COUNT(*)
        FROM analytics.keyword_features_daily
        WHERE client_id = ? AND customer_id = ? AND snapshot_date = ?;
        """,
        [cfg.client_id, cfg.customer_id, snapshot_date],
    ).fetchone()[0]

    return KeywordFeatureBuildResult(
        rows_inserted=int(rows),
        has_conversion_value=has_conv_value,
        start_date=start_date,
        end_date=end_date,
    )
