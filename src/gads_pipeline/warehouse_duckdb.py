# src/gads_pipeline/warehouse_duckdb.py
from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple, Union, Optional

import duckdb

# -----------------------------
# Column contracts (raw/snap)
# -----------------------------
RAW_CAMPAIGN_DAILY_COLS: List[str] = [
    "run_id",
    "ingested_at",
    "customer_id",
    "snapshot_date",
    "campaign_id",
    "campaign_name",
    "campaign_status",
    "channel_type",
    "impressions",
    "clicks",
    "cost_micros",
    "conversions",
    "conversions_value",
    "all_conversions",
    "all_conversions_value",
    # Chat 23 M2: Impression Share metrics
    "search_impression_share",
    "search_top_impression_share",
    "search_absolute_top_impression_share",
    "click_share",
]

SNAP_CAMPAIGN_DAILY_COLS: List[str] = RAW_CAMPAIGN_DAILY_COLS.copy()

# Idempotency key (partition key)
CAMPAIGN_DAILY_KEY_COLS: List[str] = [
    "customer_id",
    "snapshot_date",
    "campaign_id",
]


# -----------------------------
# Helpers: type normalization
# -----------------------------
def _to_date(v: Any) -> date:
    if isinstance(v, date) and not isinstance(v, datetime):
        return v
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, str):
        # accepts YYYY-MM-DD or timestamp-like; take first 10 chars
        return date.fromisoformat(v.strip()[:10])
    raise TypeError(f"snapshot_date must be date/datetime/str, got {type(v)}")


def _to_datetime(v: Any) -> datetime:
    if isinstance(v, datetime):
        return v
    if isinstance(v, date):
        return datetime(v.year, v.month, v.day)
    if isinstance(v, str):
        s = v.strip()
        # try ISO
        try:
            return datetime.fromisoformat(s.replace("Z", "+00:00"))
        except Exception:
            # last resort: date only
            d = date.fromisoformat(s[:10])
            return datetime(d.year, d.month, d.day)
    raise TypeError(f"ingested_at must be datetime/date/str, got {type(v)}")


def _normalize_campaign_row(row: Dict[str, Any]) -> Dict[str, Any]:
    r = dict(row)
    if "snapshot_date" in r:
        r["snapshot_date"] = _to_date(r["snapshot_date"])
    if "ingested_at" in r:
        r["ingested_at"] = _to_datetime(r["ingested_at"])
    return r


def _rows_to_tuples(
    rows: Sequence[Dict[str, Any]], cols: Sequence[str]
) -> List[Tuple[Any, ...]]:
    out: List[Tuple[Any, ...]] = []
    for row in rows:
        out.append(tuple(row.get(c) for c in cols))
    return out


def _unique_keys(
    rows: Sequence[Dict[str, Any]], key_cols: Sequence[str]
) -> List[Tuple[Any, ...]]:
    seen = set()
    keys: List[Tuple[Any, ...]] = []
    for r in rows:
        k = tuple(r.get(c) for c in key_cols)
        if k not in seen:
            seen.add(k)
            keys.append(k)
    return keys


# -----------------------------
# Connect + init
# -----------------------------
def connect_warehouse(settings_or_path: Any) -> duckdb.DuckDBPyConnection:
    """
    Accepts either:
      - Settings-like object with attribute: warehouse_duckdb_path
      - string/pathlib path: "warehouse.duckdb" / Path("warehouse.duckdb")
    """
    if hasattr(settings_or_path, "warehouse_duckdb_path"):
        db_path = getattr(settings_or_path, "warehouse_duckdb_path")
    else:
        db_path = settings_or_path

    if isinstance(db_path, Path):
        db_path = str(db_path)

    if not isinstance(db_path, str):
        raise TypeError(
            f"connect_warehouse expected Settings(w/ warehouse_duckdb_path) or str path; got {type(settings_or_path)} / db_path={type(db_path)}"
        )

    return duckdb.connect(db_path)


def migrate_add_is_columns(conn: duckdb.DuckDBPyConnection) -> None:
    """
    Chat 23 M2: Add 4 Impression Share columns to raw_campaign_daily and
    snap_campaign_daily if they do not already exist.

    Uses try/except per column — safe to re-run. DuckDB 1.1.0 does not support
    ALTER TABLE ADD COLUMN IF NOT EXISTS, so we catch the error instead.
    """
    is_columns = [
        ("search_impression_share",                "DOUBLE"),
        ("search_top_impression_share",             "DOUBLE"),
        ("search_absolute_top_impression_share",    "DOUBLE"),
        ("click_share",                             "DOUBLE"),
    ]
    tables = ["raw_campaign_daily", "snap_campaign_daily", "snap_ad_group_daily", "snap_keyword_daily"]

    for table in tables:
        for col_name, col_type in is_columns:
            try:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_type};")
            except Exception:
                # Column already exists — safe to ignore
                pass


def init_warehouse(conn: duckdb.DuckDBPyConnection) -> None:
    # Base tables
    conn.execute("""
        CREATE TABLE IF NOT EXISTS raw_campaign_daily (
            run_id VARCHAR,
            ingested_at TIMESTAMP,
            customer_id VARCHAR,
            snapshot_date DATE,
            campaign_id BIGINT,
            campaign_name VARCHAR,
            campaign_status VARCHAR,
            channel_type VARCHAR,
            impressions BIGINT,
            clicks BIGINT,
            cost_micros BIGINT,
            conversions DOUBLE,
            conversions_value DOUBLE,
            all_conversions DOUBLE,
            all_conversions_value DOUBLE,
            search_impression_share DOUBLE,
            search_top_impression_share DOUBLE,
            search_absolute_top_impression_share DOUBLE,
            click_share DOUBLE
        );
        """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS snap_campaign_daily (
            run_id VARCHAR,
            ingested_at TIMESTAMP,
            customer_id VARCHAR,
            snapshot_date DATE,
            campaign_id BIGINT,
            campaign_name VARCHAR,
            campaign_status VARCHAR,
            channel_type VARCHAR,
            impressions BIGINT,
            clicks BIGINT,
            cost_micros BIGINT,
            conversions DOUBLE,
            conversions_value DOUBLE,
            all_conversions DOUBLE,
            all_conversions_value DOUBLE,
            search_impression_share DOUBLE,
            search_top_impression_share DOUBLE,
            search_absolute_top_impression_share DOUBLE,
            click_share DOUBLE
        );
        """)

    # Migrate existing tables to add IS columns (safe to re-run)
    migrate_add_is_columns(conn)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS snap_campaign_config (
            ingested_at TIMESTAMP,
            customer_id VARCHAR,
            config_path VARCHAR,
            config_yaml VARCHAR
        );
        """)


    # Chat 23 M2: Ad Group daily snapshot table
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

    # Latest view (overall latest snapshot_date)
    conn.execute("""
        CREATE OR REPLACE VIEW vw_campaign_daily_latest AS
        SELECT *
        FROM snap_campaign_daily
        WHERE snapshot_date = (SELECT MAX(snapshot_date) FROM snap_campaign_daily);
        """)

    # Analytics layer (safe to create/replace)
    conn.execute("CREATE SCHEMA IF NOT EXISTS analytics;")
    conn.execute("""
        CREATE OR REPLACE VIEW analytics.campaign_daily AS
        SELECT
            run_id,
            ingested_at,
            customer_id,
            snapshot_date,
            campaign_id,
            campaign_name,
            campaign_status,
            channel_type,
            impressions,
            clicks,
            cost_micros,
            cost_micros / 1000000.0 AS cost,
            conversions,
            conversions_value,
            all_conversions,
            all_conversions_value,
            CASE WHEN impressions > 0 THEN clicks * 1.0 / impressions ELSE NULL END AS ctr,
            CASE WHEN clicks > 0 THEN (cost_micros / 1000000.0) / clicks ELSE NULL END AS cpc,
            CASE WHEN impressions > 0 THEN (cost_micros / 1000.0) / impressions ELSE NULL END AS cpm,
            CASE WHEN cost_micros > 0 THEN conversions * 1.0 / (cost_micros / 1000000.0) ELSE NULL END AS roas,
            -- Chat 23 M2: Impression Share metrics
            search_impression_share,
            search_top_impression_share,
            search_absolute_top_impression_share,
            click_share
        FROM snap_campaign_daily;
        """)



    # Chat 23 M2: Ad Group analytics view
    conn.execute("""
        CREATE OR REPLACE VIEW analytics.ad_group_daily AS
        SELECT
            run_id,
            ingested_at,
            customer_id,
            snapshot_date,
            campaign_id,
            campaign_name,
            ad_group_id,
            ad_group_name,
            ad_group_status,
            cpc_bid_micros,
            target_cpa_micros,
            impressions,
            clicks,
            cost_micros,
            cost_micros / 1000000.0 AS cost,
            conversions,
            conversions_value,
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


    # Chat 23 M2: Keyword analytics view (with IS columns)
    conn.execute("""
        CREATE OR REPLACE VIEW analytics.keyword_daily AS
        SELECT
            run_id, ingested_at, customer_id, snapshot_date,
            campaign_id, campaign_name, ad_group_id, ad_group_name,
            keyword_id, keyword_text, match_type, status,
            quality_score, quality_score_creative,
            quality_score_landing_page, quality_score_relevance,
            bid_micros, first_page_cpc_micros, top_of_page_cpc_micros,
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
        FROM snap_keyword_daily;
        """)

# -----------------------------
# Delete + insert (idempotent)
# -----------------------------
def _delete_by_keys(
    conn: duckdb.DuckDBPyConnection,
    table: str,
    key_cols: Sequence[str],
    keys: Sequence[Tuple[Any, ...]],
) -> None:
    if not keys:
        return

    cols_sql = ", ".join(key_cols)
    placeholders = ", ".join(["(" + ", ".join(["?"] * len(key_cols)) + ")"] * len(keys))
    flat_params: List[Any] = []
    for k in keys:
        flat_params.extend(list(k))

    sql = f"DELETE FROM {table} WHERE ({cols_sql}) IN ({placeholders});"
    conn.execute(sql, flat_params)


def _insert_rows(
    conn: duckdb.DuckDBPyConnection,
    table: str,
    cols: Sequence[str],
    rows: Sequence[Dict[str, Any]],
) -> None:
    if not rows:
        return
    cols_sql = ", ".join(cols)
    qmarks = ", ".join(["?"] * len(cols))
    sql = f"INSERT INTO {table} ({cols_sql}) VALUES ({qmarks});"
    tuples = _rows_to_tuples(rows, cols)
    conn.executemany(sql, tuples)


def insert_raw_campaign_daily(
    conn: duckdb.DuckDBPyConnection, rows: Sequence[Dict[str, Any]]
) -> None:
    norm = [_normalize_campaign_row(r) for r in rows]
    keys = _unique_keys(norm, CAMPAIGN_DAILY_KEY_COLS)
    _delete_by_keys(conn, "raw_campaign_daily", CAMPAIGN_DAILY_KEY_COLS, keys)
    _insert_rows(conn, "raw_campaign_daily", RAW_CAMPAIGN_DAILY_COLS, norm)


def insert_snap_campaign_daily(
    conn: duckdb.DuckDBPyConnection, rows: Sequence[Dict[str, Any]]
) -> None:
    norm = [_normalize_campaign_row(r) for r in rows]
    keys = _unique_keys(norm, CAMPAIGN_DAILY_KEY_COLS)
    _delete_by_keys(conn, "snap_campaign_daily", CAMPAIGN_DAILY_KEY_COLS, keys)
    _insert_rows(conn, "snap_campaign_daily", SNAP_CAMPAIGN_DAILY_COLS, norm)


def insert_snap_campaign_config(
    conn: duckdb.DuckDBPyConnection,
    customer_id: str,
    config_path: str,
    config_yaml: str,
    ingested_at: Optional[datetime] = None,
) -> None:
    if ingested_at is None:
        ingested_at = datetime.utcnow()
    conn.execute(
        """
        INSERT INTO snap_campaign_config (ingested_at, customer_id, config_path, config_yaml)
        VALUES (?, ?, ?, ?);
        """,
        [ingested_at, str(customer_id), str(config_path), str(config_yaml)],
    )


def count_latest_rows(conn: duckdb.DuckDBPyConnection) -> int:
    row = conn.execute("SELECT COUNT(*) FROM vw_campaign_daily_latest;").fetchone()
    return int(row[0]) if row else 0
