"""
Copy all 5 analytics tables from warehouse.duckdb to warehouse_readonly.duckdb.

Uses DuckDB ATTACH so schemas are copied automatically — no hardcoded CREATE TABLE.

Run from: gads-data-layer root directory.
"""

import duckdb

TABLES = [
    "campaign_daily",
    "keyword_daily",
    "search_term_daily",
    "ad_group_daily",
    "ad_daily",
]


def copy_all_to_readonly():
    """Copy all 5 analytics tables from warehouse.duckdb to warehouse_readonly.duckdb."""
    print("=" * 70)
    print("COPY ALL ANALYTICS TABLES -> warehouse_readonly.duckdb")
    print("=" * 70)

    row_counts = {}

    conn_ro = duckdb.connect("warehouse_readonly.duckdb")
    conn_ro.execute("CREATE SCHEMA IF NOT EXISTS analytics")
    conn_ro.execute("ATTACH 'warehouse.duckdb' AS src (READ_ONLY)")

    for table_name in TABLES:
        full_name = f"analytics.{table_name}"
        print(f"\n[copy] Copying {full_name}...")

        # Check source table exists
        exists = conn_ro.execute(
            "SELECT COUNT(*) FROM information_schema.tables "
            "WHERE table_schema = 'analytics' AND table_name = ? AND table_catalog = 'src'",
            [table_name],
        ).fetchone()[0]

        if not exists:
            print(f"  [copy] {full_name} not found in warehouse.duckdb - skipping")
            row_counts[table_name] = 0
            continue

        # Drop existing object (may be a VIEW or TABLE) in readonly
        existing = conn_ro.execute(
            "SELECT table_type FROM information_schema.tables "
            "WHERE table_schema = 'analytics' AND table_name = ?",
            [table_name],
        ).fetchone()
        if existing:
            if existing[0] == "VIEW":
                conn_ro.execute(f"DROP VIEW analytics.{table_name}")
            else:
                conn_ro.execute(f"DROP TABLE analytics.{table_name}")

        # Create table by copying from source
        conn_ro.execute(
            f"CREATE TABLE {full_name} AS SELECT * FROM src.{full_name}"
        )

        count = conn_ro.execute(f"SELECT COUNT(*) FROM {full_name}").fetchone()[0]
        row_counts[table_name] = count
        print(f"  [copy] {full_name}: {count:,} rows")

    conn_ro.execute("DETACH src")
    conn_ro.close()

    print("\n" + "=" * 70)
    print("COPY COMPLETE")
    print("=" * 70)
    return row_counts


if __name__ == "__main__":
    copy_all_to_readonly()
