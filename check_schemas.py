"""
Show all column schemas for every analytics table in warehouse_readonly.duckdb
"""
import duckdb

conn = duckdb.connect('warehouse_readonly.duckdb')

tables = [
    'campaign_daily',
    'keyword_daily', 
    'ad_group_daily',
    'ad_daily',
    'search_term_daily',
    'campaign_features_daily',
]

print("=" * 70)
print("ALL ANALYTICS TABLE SCHEMAS")
print("=" * 70)

for table in tables:
    try:
        cols = conn.execute(f"PRAGMA table_info('analytics.{table}')").fetchall()
        count = conn.execute(f"SELECT COUNT(*) FROM analytics.{table}").fetchone()[0]
        print(f"\n{'='*50}")
        print(f"TABLE: analytics.{table}  ({count:,} rows)")
        print(f"{'='*50}")
        for c in cols:
            print(f"  {c[1]:<45} {c[2]}")
    except Exception as e:
        print(f"\n  analytics.{table} — NOT FOUND or ERROR: {e}")

conn.close()
print("\n✅ Done.")
