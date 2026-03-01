"""
Manually copy ad_daily table from warehouse.duckdb to warehouse_readonly.duckdb.

This is a workaround for the path syntax issue on Windows.
"""

import duckdb
from pathlib import Path

print("=" * 80)
print("MANUAL COPY - ad_daily to warehouse_readonly.duckdb")
print("=" * 80)

# Step 1: Connect to main database and export data
print("\n[1/3] Reading data from warehouse.duckdb...")
conn_main = duckdb.connect('warehouse.duckdb')
rows = conn_main.execute("SELECT * FROM analytics.ad_daily").fetchall()
columns = [desc[0] for desc in conn_main.description]
print(f"Read {len(rows):,} rows from main database")
conn_main.close()

# Step 2: Connect to readonly database
print("\n[2/3] Connecting to warehouse_readonly.duckdb...")
conn_readonly = duckdb.connect('warehouse_readonly.duckdb')

# Drop table if exists
print("Dropping existing table (if exists)...")
conn_readonly.execute("DROP TABLE IF EXISTS analytics.ad_daily")

# Create table structure
print("Creating table structure...")
conn_readonly.execute("""
    CREATE TABLE analytics.ad_daily (
        customer_id VARCHAR,
        snapshot_date DATE,
        ad_group_id VARCHAR,
        ad_id VARCHAR,
        ad_name VARCHAR,
        ad_type VARCHAR,
        ad_status VARCHAR,
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
        click_share DOUBLE,
        PRIMARY KEY (customer_id, snapshot_date, ad_id)
    );
""")

# Step 3: Insert all rows
print(f"\n[3/3] Inserting {len(rows):,} rows into warehouse_readonly.duckdb...")
conn_readonly.executemany("""
    INSERT INTO analytics.ad_daily VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", rows)

# Verify
final_count = conn_readonly.execute("SELECT COUNT(*) FROM analytics.ad_daily").fetchone()[0]
print(f"✓ Inserted {final_count:,} rows")

conn_readonly.close()

print("\n" + "=" * 80)
print("✓ COPY COMPLETE")
print("=" * 80)
print(f"warehouse.duckdb: {len(rows):,} rows")
print(f"warehouse_readonly.duckdb: {final_count:,} rows")
print()
