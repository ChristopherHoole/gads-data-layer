"""
Fix campaign_id type mismatch.
keyword_daily and ad_daily have campaign_id as BIGINT.
campaign_daily has it as VARCHAR.
Routes that join on campaign_id fail due to type mismatch.
Fix: recreate tables with campaign_id as VARCHAR.
"""
import duckdb

print("=" * 60)
print("FIX: campaign_id type mismatch")
print("=" * 60)

# Fix warehouse.duckdb first
conn = duckdb.connect('warehouse.duckdb')

for table in ['keyword_daily', 'ad_daily', 'ad_group_daily', 'search_term_daily']:
    try:
        # Check current type
        cols = conn.execute(f"PRAGMA table_info('analytics.{table}')").fetchall()
        camp_col = next((c for c in cols if c[1] == 'campaign_id'), None)
        if not camp_col:
            print(f"  {table} — no campaign_id column, skipping")
            continue
        if camp_col[2] == 'VARCHAR':
            print(f"  {table} — already VARCHAR, skipping")
            continue

        print(f"\n  Fixing {table} (campaign_id: {camp_col[2]} → VARCHAR)...")

        # Get all column definitions, replace campaign_id type
        col_defs = []
        for c in cols:
            col_name = c[1]
            col_type = 'VARCHAR' if col_name == 'campaign_id' else c[2]
            col_defs.append(f"{col_name} {col_type}")

        # Recreate table with correct types
        conn.execute(f"CREATE TABLE analytics.{table}_new AS SELECT * REPLACE (CAST(campaign_id AS VARCHAR) AS campaign_id) FROM analytics.{table}")
        conn.execute(f"DROP TABLE analytics.{table}")
        conn.execute(f"ALTER TABLE analytics.{table}_new RENAME TO {table}")

        # Verify
        n = conn.execute(f"SELECT COUNT(*) FROM analytics.{table}").fetchone()[0]
        sample = conn.execute(f"SELECT campaign_id, pg_typeof(campaign_id) FROM analytics.{table} LIMIT 1").fetchone()
        print(f"    ✅ {n:,} rows, campaign_id now: '{sample[0]}' ({sample[1]})")

    except Exception as e:
        print(f"  ❌ {table}: {e}")

conn.close()

# Now copy fixed tables to readonly
print("\nCopying fixed tables to warehouse_readonly.duckdb...")
conn_ro = duckdb.connect('warehouse_readonly.duckdb')
conn_ro.execute("CREATE SCHEMA IF NOT EXISTS analytics")
conn_ro.execute("ATTACH 'warehouse.duckdb' AS src (READ_ONLY)")

for table in ['keyword_daily', 'ad_daily', 'ad_group_daily', 'search_term_daily']:
    try:
        existing = conn_ro.execute(
            "SELECT table_type FROM information_schema.tables WHERE table_schema='analytics' AND table_name=?",
            [table]
        ).fetchone()
        if existing:
            drop_cmd = "DROP VIEW" if existing[0] == 'VIEW' else "DROP TABLE"
            conn_ro.execute(f"{drop_cmd} analytics.{table}")
        conn_ro.execute(f"CREATE TABLE analytics.{table} AS SELECT * FROM src.analytics.{table}")
        n = conn_ro.execute(f"SELECT COUNT(*) FROM analytics.{table}").fetchone()[0]
        sample = conn_ro.execute(f"SELECT campaign_id, pg_typeof(campaign_id) FROM analytics.{table} LIMIT 1").fetchone()
        print(f"  ✅ {table}: {n:,} rows, campaign_id='{sample[0]}' ({sample[1]})")
    except Exception as e:
        print(f"  ❌ {table}: {e}")

conn_ro.execute("DETACH src")
conn_ro.close()

print("\n✅ Fix complete. Restart Flask and test keywords/ads pages.")
