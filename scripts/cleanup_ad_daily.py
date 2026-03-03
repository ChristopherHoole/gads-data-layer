"""
Clean up incomplete ad_daily table before regenerating.

This script:
1. Drops ad_daily table from warehouse.duckdb
2. Confirms cleanup
3. Ready for fresh generation
"""

import duckdb
from pathlib import Path

print("=" * 80)
print("CLEANUP - Removing Incomplete ad_daily Table")
print("=" * 80)

# Connect to main database
db_path = Path(__file__).parent.parent / 'warehouse.duckdb'
print(f"\nConnecting to: {db_path}")
conn = duckdb.connect(str(db_path))

# Check if table exists
try:
    count = conn.execute("SELECT COUNT(*) FROM analytics.ad_daily").fetchone()[0]
    print(f"Found existing table with {count:,} rows")
    
    # Drop the table
    conn.execute("DROP TABLE IF EXISTS analytics.ad_daily")
    print("✓ Dropped analytics.ad_daily table from warehouse.duckdb")
    
except Exception as e:
    print(f"Table doesn't exist or already dropped: {e}")

conn.close()

# Also try to drop from readonly database
readonly_path = Path(__file__).parent.parent / 'warehouse_readonly.duckdb'
print(f"\nConnecting to: {readonly_path}")
conn_readonly = duckdb.connect(str(readonly_path))

try:
    count = conn_readonly.execute("SELECT COUNT(*) FROM analytics.ad_daily").fetchone()[0]
    print(f"Found existing table with {count:,} rows")
    
    conn_readonly.execute("DROP TABLE IF EXISTS analytics.ad_daily")
    print("✓ Dropped analytics.ad_daily table from warehouse_readonly.duckdb")
    
except Exception as e:
    print(f"Table doesn't exist or already dropped: {e}")

conn_readonly.close()

print("\n" + "=" * 80)
print("✓ CLEANUP COMPLETE")
print("=" * 80)
print("\nReady to run: python scripts/generate_ad_daily.py")
print()
