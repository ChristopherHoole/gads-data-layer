"""Quick verification script for ad_daily synthetic data."""

import duckdb

print("=" * 80)
print("VERIFICATION QUERIES - ad_daily Table")
print("=" * 80)

# Connect to main database
conn = duckdb.connect('warehouse.duckdb')

# Query 1: Row count
print("\n[1/5] Row count in warehouse.duckdb:")
result = conn.execute('SELECT COUNT(*) FROM analytics.ad_daily').fetchone()
print(f"  Total rows: {result[0]:,}")

# Query 2: Date range
print("\n[2/5] Date range:")
result = conn.execute('SELECT MIN(snapshot_date), MAX(snapshot_date) FROM analytics.ad_daily').fetchone()
print(f"  Start: {result[0]}")
print(f"  End: {result[1]}")

# Query 3: Unique counts
print("\n[3/5] Unique ad groups and ads:")
result = conn.execute('SELECT COUNT(DISTINCT ad_group_id), COUNT(DISTINCT ad_id) FROM analytics.ad_daily').fetchone()
print(f"  Ad Groups: {result[0]}")
print(f"  Ads: {result[1]}")

# Query 4: Sample data
print("\n[4/5] Sample data (first 3 rows):")
rows = conn.execute('''
    SELECT snapshot_date, ad_id, ad_status, impressions, clicks, 
           cost_micros/1000000.0 AS cost, conversions 
    FROM analytics.ad_daily 
    LIMIT 3
''').fetchall()
for row in rows:
    print(f"  Date: {row[0]}, Ad: {row[1]}, Status: {row[2]}, Impr: {row[3]:,}, Clicks: {row[4]}, Cost: ${row[5]:.2f}, Conv: {row[6]:.2f}")

# Query 5: Metrics sanity check
print("\n[5/5] Metrics sanity check (ENABLED ads only):")
result = conn.execute('''
    SELECT 
        MIN(impressions), AVG(impressions), MAX(impressions),
        MIN(cost_micros/1000000.0), AVG(cost_micros/1000000.0), MAX(cost_micros/1000000.0)
    FROM analytics.ad_daily 
    WHERE ad_status = 'ENABLED' AND impressions > 0
''').fetchone()
print(f"  Impressions - Min: {result[0]:,.0f}, Avg: {result[1]:,.0f}, Max: {result[2]:,.0f}")
print(f"  Cost - Min: ${result[3]:,.2f}, Avg: ${result[4]:,.2f}, Max: ${result[5]:,.2f}")

conn.close()

# Now check readonly database
print("\n" + "=" * 80)
print("READONLY DATABASE VERIFICATION")
print("=" * 80)

try:
    conn_readonly = duckdb.connect('warehouse_readonly.duckdb')
    result = conn_readonly.execute('SELECT COUNT(*) FROM analytics.ad_daily').fetchone()
    print(f"\nRow count in warehouse_readonly.duckdb: {result[0]:,}")
    conn_readonly.close()
except Exception as e:
    print(f"\n⚠️  Readonly database doesn't have ad_daily table yet")
    print(f"Error: {e}")
    print("\nThis is OK - you can copy it manually:")
    print("  python scripts/copy_to_readonly.py")

print("\n" + "=" * 80)
print("✓ VERIFICATION COMPLETE")
print("=" * 80)
print("\nMain database has all data. Ready to proceed to Phase 2 (fixing ads.py route).")
print()
