from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional
import calendar
import duckdb

from .config import ClientConfig


@dataclass(frozen=True)
class FeatureBuildResult:
    rows_inserted: int
    has_conversion_value: bool
    start_date: date
    end_date: date


def _month_bounds(d: date) -> tuple[date, date, int, int]:
    month_start = date(d.year, d.month, 1)
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    month_end = date(d.year, d.month, days_in_month)
    days_elapsed = (d - month_start).days + 1
    return month_start, month_end, days_elapsed, days_in_month


def _lower_cols(con: duckdb.DuckDBPyConnection) -> set[str]:
    rows = con.execute("PRAGMA table_info('ro.analytics.campaign_daily');").fetchall()
    return set(str(r[1]).lower() for r in rows)


def _pick_expr(cols: set[str], col_name: str, cast_sql: str) -> str:
    if col_name.lower() in cols:
        return f"CAST(cd.{col_name} AS {cast_sql})"
    return f"CAST(NULL AS {cast_sql})"


def _conversion_value_expr(cols: set[str]) -> tuple[str, bool]:
    # Your schema has `conversions_value` (confirmed in PRAGMA).
    if "conversions_value" in cols:
        return "CAST(cd.conversions_value AS DOUBLE)", True
    if "conversion_value" in cols:
        return "CAST(cd.conversion_value AS DOUBLE)", True
    if "conversions_value_micros" in cols:
        return "CAST(cd.conversions_value_micros AS DOUBLE) / 1000000.0", True
    if "conversion_value_micros" in cols:
        return "CAST(cd.conversion_value_micros AS DOUBLE) / 1000000.0", True
    return "CAST(NULL AS DOUBLE)", False


def _ensure_features_table(con: duckdb.DuckDBPyConnection) -> None:
    con.execute("CREATE SCHEMA IF NOT EXISTS analytics;")

    windows = [1, 3, 7, 14, 30]
    base_metrics: list[tuple[str, str]] = [
        ("impressions", "BIGINT"),
        ("clicks", "BIGINT"),
        ("cost_micros", "BIGINT"),
        ("conversions", "DOUBLE"),
        ("conversion_value", "DOUBLE"),
    ]

    cols: list[tuple[str, str, bool]] = []

    cols.extend(
        [
            ("client_id", "TEXT", True),
            ("customer_id", "TEXT", True),
            ("campaign_id", "TEXT", True),
            ("snapshot_date", "DATE", True),
            ("campaign_name", "TEXT", False),
            ("campaign_status", "TEXT", False),
            ("channel_type", "TEXT", False),
            ("feature_set_version", "TEXT", True),
            ("schema_version", "INTEGER", True),
            ("generated_at_utc", "TIMESTAMP", True),
            ("source_table", "TEXT", True),
            ("has_conversion_value", "BOOLEAN", True),
            ("has_impr_share", "BOOLEAN", True),
        ]
    )

    for m, mtype in base_metrics:
        for w in windows:
            cols.append((f"{m}_w{w}_sum", mtype, False))
            cols.append((f"{m}_w{w}_mean", "DOUBLE", False))
            cols.append((f"{m}_w{w}_vs_prev_abs", "DOUBLE", False))
            cols.append((f"{m}_w{w}_vs_prev_pct", "DOUBLE", False))

    # Efficiency metrics are ratio-of-sums over the window (locked decision).
    for w in windows:
        cols.append((f"ctr_w{w}_mean", "DOUBLE", False))
        cols.append((f"cpc_w{w}_mean", "DOUBLE", False))
        cols.append((f"cvr_w{w}_mean", "DOUBLE", False))
        cols.append((f"cpa_w{w}_mean", "DOUBLE", False))
        cols.append((f"roas_w{w}_mean", "DOUBLE", False))

        cols.append((f"ctr_w{w}_vs_prev_pct", "DOUBLE", False))
        cols.append((f"cvr_w{w}_vs_prev_pct", "DOUBLE", False))
        cols.append((f"cpa_w{w}_vs_prev_pct", "DOUBLE", False))
        cols.append((f"roas_w{w}_vs_prev_pct", "DOUBLE", False))

    cols.extend(
        [
            ("cost_w14_cv", "DOUBLE", False),
            ("clicks_w14_cv", "DOUBLE", False),
            ("conversions_w30_cv", "DOUBLE", False),
            ("anomaly_cost_z", "DOUBLE", False),
        ]
    )

    cols.extend(
        [
            ("low_data_clicks_7d", "BOOLEAN", False),
            ("low_data_conversions_30d", "BOOLEAN", False),
            ("low_data_impressions_7d", "BOOLEAN", False),
            ("low_data_flag", "BOOLEAN", False),
        ]
    )

    # Account-level spend caps/pacing fields (account-level only for now)
    cols.extend(
        [
            ("acct_daily_cap_micros", "BIGINT", False),
            ("acct_monthly_cap_micros", "BIGINT", False),
            ("acct_mtd_cost_micros", "BIGINT", False),
            ("acct_projected_month_cost_micros", "BIGINT", False),
            ("acct_pacing_vs_cap_pct", "DOUBLE", False),
            ("acct_daily_cap_usage_pct", "DOUBLE", False),
            ("pacing_flag_over_105", "BOOLEAN", False),
        ]
    )

    ddl_cols = []
    for name, typ, not_null in cols:
        nn = " NOT NULL" if not_null else ""
        ddl_cols.append(f"  {name} {typ}{nn}")

    ddl = "CREATE TABLE IF NOT EXISTS analytics.campaign_features_daily (\n"
    ddl += ",\n".join(ddl_cols)
    ddl += ",\n  PRIMARY KEY (client_id, customer_id, campaign_id, snapshot_date)\n);"

    con.execute(ddl)


def build_campaign_features_daily(
    con: duckdb.DuckDBPyConnection,
    cfg: ClientConfig,
    snapshot_date: date,
    feature_set_version: str = "lighthouse_campaign_v0",
    schema_version: int = 1,
) -> FeatureBuildResult:
    """
    Reads from ro.analytics.campaign_daily (readonly DB attached as 'ro'),
    writes into analytics.campaign_features_daily (build DB).

    Derived efficiency metrics are computed as ratio-of-sums over the window.
    """
    _ensure_features_table(con)

    end_date = snapshot_date
    start_date = snapshot_date - timedelta(days=59)

    cols = _lower_cols(con)
    conv_value_expr, has_conv_value = _conversion_value_expr(cols)

    campaign_name_expr = _pick_expr(cols, "campaign_name", "VARCHAR")
    campaign_status_expr = _pick_expr(cols, "campaign_status", "VARCHAR")
    channel_type_expr = _pick_expr(cols, "channel_type", "VARCHAR")

    windows = [1, 3, 7, 14, 30]
    base_metrics: list[tuple[str, str]] = [
        ("impressions", "BIGINT"),
        ("clicks", "BIGINT"),
        ("cost_micros", "BIGINT"),
        ("conversions", "DOUBLE"),
        ("conversion_value", "DOUBLE"),
    ]

    # roll: sums + means
    roll_parts: list[str] = []
    for m, _typ in base_metrics:
        for w in windows:
            frame = f"ROWS BETWEEN {w-1} PRECEDING AND CURRENT ROW"
            roll_parts.append(
                f"SUM({m}) OVER (PARTITION BY customer_id, campaign_id ORDER BY snapshot_date {frame}) AS {m}_w{w}_sum"
            )
            roll_parts.append(
                f"(SUM({m}) OVER (PARTITION BY customer_id, campaign_id ORDER BY snapshot_date {frame}) / {float(w)}) AS {m}_w{w}_mean"
            )
    roll_sql = ",\n            ".join(roll_parts)

    # roll2: lag prev sums, then compute vs_prev
    lag_parts: list[str] = []
    base_out_parts: list[str] = []
    for m, _typ in base_metrics:
        for w in windows:
            prev = f"LAG({m}_w{w}_sum, {w}) OVER (PARTITION BY customer_id, campaign_id ORDER BY snapshot_date)"
            lag_parts.append(f"{prev} AS {m}_w{w}_sum_prev")

            base_out_parts.append(f"{m}_w{w}_sum")
            base_out_parts.append(f"{m}_w{w}_mean")
            base_out_parts.append(
                f"({m}_w{w}_sum - {m}_w{w}_sum_prev) AS {m}_w{w}_vs_prev_abs"
            )
            base_out_parts.append(f"""CASE
                      WHEN {m}_w{w}_sum_prev IS NULL OR {m}_w{w}_sum_prev = 0 THEN NULL
                      ELSE ({m}_w{w}_sum - {m}_w{w}_sum_prev) / NULLIF({m}_w{w}_sum_prev, 0)
                    END AS {m}_w{w}_vs_prev_pct""")
    lag_sql = ",\n            ".join(lag_parts)

    # Derived metrics (ratio-of-sums) + derived deltas vs prev window
    derived_parts: list[str] = []
    for w in windows:
        derived_parts.append(f"""CASE WHEN impressions_w{w}_sum = 0 THEN NULL
                    ELSE clicks_w{w}_sum::DOUBLE / NULLIF(impressions_w{w}_sum::DOUBLE, 0)
                  END AS ctr_w{w}_mean""")
        derived_parts.append(f"""CASE WHEN clicks_w{w}_sum = 0 THEN NULL
                    ELSE cost_micros_w{w}_sum::DOUBLE / NULLIF(clicks_w{w}_sum::DOUBLE, 0)
                  END AS cpc_w{w}_mean""")
        derived_parts.append(f"""CASE WHEN clicks_w{w}_sum = 0 THEN NULL
                    ELSE conversions_w{w}_sum::DOUBLE / NULLIF(clicks_w{w}_sum::DOUBLE, 0)
                  END AS cvr_w{w}_mean""")
        derived_parts.append(f"""CASE WHEN conversions_w{w}_sum = 0 THEN NULL
                    ELSE cost_micros_w{w}_sum::DOUBLE / NULLIF(conversions_w{w}_sum::DOUBLE, 0)
                  END AS cpa_w{w}_mean""")
        derived_parts.append(f"""CASE
                    WHEN conversion_value_w{w}_sum IS NULL THEN NULL
                    WHEN cost_micros_w{w}_sum = 0 THEN NULL
                    ELSE conversion_value_w{w}_sum::DOUBLE / NULLIF((cost_micros_w{w}_sum::DOUBLE / 1000000.0), 0)
                  END AS roas_w{w}_mean""")

        derived_parts.append(f"""CASE
                    WHEN impressions_w{w}_sum_prev IS NULL OR impressions_w{w}_sum_prev = 0 THEN NULL
                    WHEN clicks_w{w}_sum_prev IS NULL THEN NULL
                    ELSE
                      CASE
                        WHEN (clicks_w{w}_sum_prev::DOUBLE / NULLIF(impressions_w{w}_sum_prev::DOUBLE,0)) = 0 THEN NULL
                        ELSE
                          (
                            (CASE WHEN impressions_w{w}_sum = 0 THEN NULL
                                  ELSE clicks_w{w}_sum::DOUBLE / NULLIF(impressions_w{w}_sum::DOUBLE,0)
                             END)
                            -
                            (clicks_w{w}_sum_prev::DOUBLE / NULLIF(impressions_w{w}_sum_prev::DOUBLE,0))
                          )
                          /
                          NULLIF((clicks_w{w}_sum_prev::DOUBLE / NULLIF(impressions_w{w}_sum_prev::DOUBLE,0)),0)
                      END
                  END AS ctr_w{w}_vs_prev_pct""")

        derived_parts.append(f"""CASE
                    WHEN clicks_w{w}_sum_prev IS NULL OR clicks_w{w}_sum_prev = 0 THEN NULL
                    WHEN conversions_w{w}_sum_prev IS NULL THEN NULL
                    ELSE
                      CASE
                        WHEN (conversions_w{w}_sum_prev::DOUBLE / NULLIF(clicks_w{w}_sum_prev::DOUBLE,0)) = 0 THEN NULL
                        ELSE
                          (
                            (CASE WHEN clicks_w{w}_sum = 0 THEN NULL
                                  ELSE conversions_w{w}_sum::DOUBLE / NULLIF(clicks_w{w}_sum::DOUBLE,0)
                             END)
                            -
                            (conversions_w{w}_sum_prev::DOUBLE / NULLIF(clicks_w{w}_sum_prev::DOUBLE,0))
                          )
                          /
                          NULLIF((conversions_w{w}_sum_prev::DOUBLE / NULLIF(clicks_w{w}_sum_prev::DOUBLE,0)),0)
                      END
                  END AS cvr_w{w}_vs_prev_pct""")

        derived_parts.append(f"""CASE
                    WHEN conversions_w{w}_sum_prev IS NULL OR conversions_w{w}_sum_prev = 0 THEN NULL
                    WHEN cost_micros_w{w}_sum_prev IS NULL THEN NULL
                    ELSE
                      CASE
                        WHEN (cost_micros_w{w}_sum_prev::DOUBLE / NULLIF(conversions_w{w}_sum_prev::DOUBLE,0)) = 0 THEN NULL
                        ELSE
                          (
                            (CASE WHEN conversions_w{w}_sum = 0 THEN NULL
                                  ELSE cost_micros_w{w}_sum::DOUBLE / NULLIF(conversions_w{w}_sum::DOUBLE,0)
                             END)
                            -
                            (cost_micros_w{w}_sum_prev::DOUBLE / NULLIF(conversions_w{w}_sum_prev::DOUBLE,0))
                          )
                          /
                          NULLIF((cost_micros_w{w}_sum_prev::DOUBLE / NULLIF(conversions_w{w}_sum_prev::DOUBLE,0)),0)
                      END
                  END AS cpa_w{w}_vs_prev_pct""")

        derived_parts.append(f"""CASE
                    WHEN conversion_value_w{w}_sum_prev IS NULL OR cost_micros_w{w}_sum_prev IS NULL THEN NULL
                    WHEN cost_micros_w{w}_sum_prev = 0 THEN NULL
                    ELSE
                      CASE
                        WHEN (conversion_value_w{w}_sum_prev::DOUBLE / NULLIF((cost_micros_w{w}_sum_prev::DOUBLE / 1000000.0),0)) = 0 THEN NULL
                        ELSE
                          (
                            (CASE
                               WHEN conversion_value_w{w}_sum IS NULL THEN NULL
                               WHEN cost_micros_w{w}_sum = 0 THEN NULL
                               ELSE conversion_value_w{w}_sum::DOUBLE / NULLIF((cost_micros_w{w}_sum::DOUBLE / 1000000.0),0)
                             END)
                            -
                            (conversion_value_w{w}_sum_prev::DOUBLE / NULLIF((cost_micros_w{w}_sum_prev::DOUBLE / 1000000.0),0))
                          )
                          /
                          NULLIF((conversion_value_w{w}_sum_prev::DOUBLE / NULLIF((cost_micros_w{w}_sum_prev::DOUBLE / 1000000.0),0)),0)
                      END
                  END AS roas_w{w}_vs_prev_pct""")

    derived_sql = ",\n            ".join(derived_parts)

    # IMPORTANT: qualify roll2.* in these window functions to avoid ambiguity after joining dims_today.
    vol_parts = [
        """CASE
              WHEN AVG(roll2.cost_micros) OVER (PARTITION BY roll2.customer_id, roll2.campaign_id ORDER BY roll2.snapshot_date ROWS BETWEEN 13 PRECEDING AND CURRENT ROW) = 0
              THEN NULL
              ELSE STDDEV_SAMP(roll2.cost_micros) OVER (PARTITION BY roll2.customer_id, roll2.campaign_id ORDER BY roll2.snapshot_date ROWS BETWEEN 13 PRECEDING AND CURRENT ROW)
                   / NULLIF(AVG(roll2.cost_micros) OVER (PARTITION BY roll2.customer_id, roll2.campaign_id ORDER BY roll2.snapshot_date ROWS BETWEEN 13 PRECEDING AND CURRENT ROW), 0)
            END AS cost_w14_cv""",
        """CASE
              WHEN AVG(roll2.clicks) OVER (PARTITION BY roll2.customer_id, roll2.campaign_id ORDER BY roll2.snapshot_date ROWS BETWEEN 13 PRECEDING AND CURRENT ROW) = 0
              THEN NULL
              ELSE STDDEV_SAMP(roll2.clicks) OVER (PARTITION BY roll2.customer_id, roll2.campaign_id ORDER BY roll2.snapshot_date ROWS BETWEEN 13 PRECEDING AND CURRENT ROW)
                   / NULLIF(AVG(roll2.clicks) OVER (PARTITION BY roll2.customer_id, roll2.campaign_id ORDER BY roll2.snapshot_date ROWS BETWEEN 13 PRECEDING AND CURRENT ROW), 0)
            END AS clicks_w14_cv""",
        """CASE
              WHEN AVG(roll2.conversions) OVER (PARTITION BY roll2.customer_id, roll2.campaign_id ORDER BY roll2.snapshot_date ROWS BETWEEN 29 PRECEDING AND CURRENT ROW) = 0
              THEN NULL
              ELSE STDDEV_SAMP(roll2.conversions) OVER (PARTITION BY roll2.customer_id, roll2.campaign_id ORDER BY roll2.snapshot_date ROWS BETWEEN 29 PRECEDING AND CURRENT ROW)
                   / NULLIF(AVG(roll2.conversions) OVER (PARTITION BY roll2.customer_id, roll2.campaign_id ORDER BY roll2.snapshot_date ROWS BETWEEN 29 PRECEDING AND CURRENT ROW), 0)
            END AS conversions_w30_cv""",
        """CASE
              WHEN STDDEV_SAMP(roll2.cost_micros) OVER (PARTITION BY roll2.customer_id, roll2.campaign_id ORDER BY roll2.snapshot_date ROWS BETWEEN 13 PRECEDING AND CURRENT ROW) = 0
              THEN NULL
              ELSE (roll2.cost_micros::DOUBLE
                    - AVG(roll2.cost_micros) OVER (PARTITION BY roll2.customer_id, roll2.campaign_id ORDER BY roll2.snapshot_date ROWS BETWEEN 13 PRECEDING AND CURRENT ROW))
                   / NULLIF(STDDEV_SAMP(roll2.cost_micros) OVER (PARTITION BY roll2.customer_id, roll2.campaign_id ORDER BY roll2.snapshot_date ROWS BETWEEN 13 PRECEDING AND CURRENT ROW), 0)
            END AS anomaly_cost_z""",
    ]
    vol_sql = ",\n            ".join(vol_parts)

    base_out_sql = ",\n            ".join(base_out_parts)

    insert_cols: list[str] = [
        "client_id",
        "customer_id",
        "campaign_id",
        "snapshot_date",
        "campaign_name",
        "campaign_status",
        "channel_type",
        "feature_set_version",
        "schema_version",
        "generated_at_utc",
        "source_table",
        "has_conversion_value",
        "has_impr_share",
    ]

    for m, _typ in base_metrics:
        for w in windows:
            insert_cols += [
                f"{m}_w{w}_sum",
                f"{m}_w{w}_mean",
                f"{m}_w{w}_vs_prev_abs",
                f"{m}_w{w}_vs_prev_pct",
            ]

    for w in windows:
        insert_cols += [
            f"ctr_w{w}_mean",
            f"cpc_w{w}_mean",
            f"cvr_w{w}_mean",
            f"cpa_w{w}_mean",
            f"roas_w{w}_mean",
            f"ctr_w{w}_vs_prev_pct",
            f"cvr_w{w}_vs_prev_pct",
            f"cpa_w{w}_vs_prev_pct",
            f"roas_w{w}_vs_prev_pct",
        ]

    insert_cols += [
        "cost_w14_cv",
        "clicks_w14_cv",
        "conversions_w30_cv",
        "anomaly_cost_z",
        "low_data_clicks_7d",
        "low_data_conversions_30d",
        "low_data_impressions_7d",
        "low_data_flag",
    ]

    insert_cols_sql = ", ".join(insert_cols)

    sql = f"""
    WITH src AS (
      SELECT
        CAST(cd.customer_id AS VARCHAR) AS customer_id,
        CAST(cd.campaign_id AS VARCHAR) AS campaign_id,
        CAST(cd.snapshot_date AS DATE) AS snapshot_date,

        {campaign_name_expr} AS campaign_name,
        {campaign_status_expr} AS campaign_status,
        {channel_type_expr} AS channel_type,

        CAST(COALESCE(cd.impressions, 0) AS BIGINT) AS impressions,
        CAST(COALESCE(cd.clicks, 0) AS BIGINT) AS clicks,
        CAST(COALESCE(cd.cost_micros, 0) AS BIGINT) AS cost_micros,
        CAST(COALESCE(cd.conversions, 0) AS DOUBLE) AS conversions,
        {conv_value_expr} AS conversion_value
      FROM ro.analytics.campaign_daily cd
      WHERE CAST(cd.customer_id AS VARCHAR) = ?
        AND CAST(cd.snapshot_date AS DATE) BETWEEN ? AND ?
    ),
    campaigns AS (
      SELECT DISTINCT customer_id, campaign_id FROM src
    ),
    calendar AS (
      SELECT
        c.customer_id,
        c.campaign_id,
        CAST(gs AS DATE) AS snapshot_date
      FROM campaigns c,
           generate_series(?::DATE, ?::DATE, INTERVAL 1 DAY) t(gs)
    ),
    dense AS (
      SELECT
        cal.customer_id,
        cal.campaign_id,
        cal.snapshot_date,
        COALESCE(src.impressions, 0) AS impressions,
        COALESCE(src.clicks, 0) AS clicks,
        COALESCE(src.cost_micros, 0) AS cost_micros,
        COALESCE(src.conversions, 0) AS conversions,
        COALESCE(src.conversion_value, NULL) AS conversion_value
      FROM calendar cal
      LEFT JOIN src
        ON src.customer_id = cal.customer_id
       AND src.campaign_id = cal.campaign_id
       AND src.snapshot_date = cal.snapshot_date
    ),
    dims_today AS (
      SELECT
        customer_id,
        campaign_id,
        MAX(campaign_name) AS campaign_name,
        MAX(campaign_status) AS campaign_status,
        MAX(channel_type) AS channel_type
      FROM src
      WHERE snapshot_date = ?::DATE
      GROUP BY 1,2
    ),
    roll AS (
      SELECT
        customer_id,
        campaign_id,
        snapshot_date,
        impressions,
        clicks,
        cost_micros,
        conversions,
        conversion_value,
        {roll_sql}
      FROM dense
    ),
    roll2 AS (
      SELECT
        r.*,
        {lag_sql}
      FROM roll r
    ),
    final AS (
      SELECT
        ? AS client_id,
        roll2.customer_id AS customer_id,
        roll2.campaign_id AS campaign_id,
        roll2.snapshot_date AS snapshot_date,
        d.campaign_name,
        d.campaign_status,
        d.channel_type,

        ? AS feature_set_version,
        ? AS schema_version,
        NOW() AS generated_at_utc,
        'analytics.campaign_daily' AS source_table,

        ? AS has_conversion_value,
        FALSE AS has_impr_share,

        {base_out_sql},
        {derived_sql},
        {vol_sql},

        (clicks_w7_sum < 30) AS low_data_clicks_7d,
        (conversions_w30_sum < 15) AS low_data_conversions_30d,
        (impressions_w7_sum < 500) AS low_data_impressions_7d,
        ((clicks_w7_sum < 30) OR (conversions_w30_sum < 15) OR (impressions_w7_sum < 500)) AS low_data_flag

      FROM roll2
      LEFT JOIN dims_today d
        ON d.customer_id = roll2.customer_id
       AND d.campaign_id = roll2.campaign_id
      WHERE roll2.snapshot_date = ?::DATE
    )
    SELECT * FROM final;
    """

    # idempotent delete for this client/day
    con.execute(
        """
        DELETE FROM analytics.campaign_features_daily
        WHERE client_id = ?
          AND customer_id = ?
          AND snapshot_date = ?;
        """,
        [cfg.client_id, cfg.customer_id, snapshot_date],
    )

    params = [
        cfg.customer_id,
        start_date,
        end_date,
        start_date,
        end_date,
        snapshot_date,
        cfg.client_id,
        feature_set_version,
        schema_version,
        bool(has_conv_value),
        snapshot_date,
    ]

    con.execute(
        f"INSERT INTO analytics.campaign_features_daily ({insert_cols_sql}) " + sql,
        params,
    )

    rows = con.execute(
        """
        SELECT COUNT(*)
        FROM analytics.campaign_features_daily
        WHERE client_id = ? AND customer_id = ? AND snapshot_date = ?;
        """,
        [cfg.client_id, cfg.customer_id, snapshot_date],
    ).fetchone()[0]

    # account-level pacing
    month_start, _month_end, days_elapsed, days_in_month = _month_bounds(snapshot_date)

    mtd_cost = con.execute(
        """
        SELECT CAST(COALESCE(SUM(cost_micros),0) AS BIGINT)
        FROM ro.analytics.campaign_daily
        WHERE CAST(customer_id AS VARCHAR) = ?
          AND CAST(snapshot_date AS DATE) BETWEEN ? AND ?;
        """,
        [cfg.customer_id, month_start, snapshot_date],
    ).fetchone()[0]

    projected = 0
    if days_elapsed > 0:
        projected = int((mtd_cost / float(days_elapsed)) * float(days_in_month))

    daily_cap_micros = (
        int(cfg.spend_caps.daily * 1_000_000) if cfg.spend_caps.daily else None
    )
    monthly_cap_micros = (
        int(cfg.spend_caps.monthly * 1_000_000) if cfg.spend_caps.monthly else None
    )

    pacing_vs_cap: Optional[float] = None
    pacing_flag: Optional[bool] = None
    if monthly_cap_micros and monthly_cap_micros > 0:
        pacing_vs_cap = (projected / float(monthly_cap_micros)) - 1.0
        pacing_flag = projected > int(1.05 * monthly_cap_micros)

    daily_usage: Optional[float] = None
    if daily_cap_micros and daily_cap_micros > 0:
        day_cost = con.execute(
            """
            SELECT CAST(COALESCE(SUM(cost_micros),0) AS BIGINT)
            FROM ro.analytics.campaign_daily
            WHERE CAST(customer_id AS VARCHAR) = ?
              AND CAST(snapshot_date AS DATE) = ?;
            """,
            [cfg.customer_id, snapshot_date],
        ).fetchone()[0]
        daily_usage = day_cost / float(daily_cap_micros)

    con.execute(
        """
        UPDATE analytics.campaign_features_daily
        SET
          acct_daily_cap_micros = ?,
          acct_monthly_cap_micros = ?,
          acct_mtd_cost_micros = ?,
          acct_projected_month_cost_micros = ?,
          acct_pacing_vs_cap_pct = ?,
          acct_daily_cap_usage_pct = ?,
          pacing_flag_over_105 = ?
        WHERE client_id = ? AND customer_id = ? AND snapshot_date = ?;
        """,
        [
            daily_cap_micros,
            monthly_cap_micros,
            mtd_cost,
            projected,
            pacing_vs_cap,
            daily_usage,
            pacing_flag,
            cfg.client_id,
            cfg.customer_id,
            snapshot_date,
        ],
    )

    return FeatureBuildResult(
        rows_inserted=int(rows),
        has_conversion_value=bool(has_conv_value),
        start_date=start_date,
        end_date=end_date,
    )
