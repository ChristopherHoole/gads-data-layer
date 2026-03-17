"""
Check why keywords and ads tables show no rows in ACT
"""
import duckdb

CID = "1254895944"
conn = duckdb.connect('warehouse_readonly.duckdb')

print("=" * 70)
print("KEYWORDS + ADS TABLE QUERY DIAGNOSTIC")
print("=" * 70)

# Check how customer_id is stored vs what routes might pass
print("\n--- customer_id format in each table ---")
for t in ['keyword_daily', 'ad_daily', 'campaign_daily', 'ad_group_daily']:
    row = conn.execute(f"SELECT customer_id, pg_typeof(customer_id) FROM analytics.{t} LIMIT 1").fetchone()
    if row:
        print(f"  {t}: '{row[0]}' (type: {row[1]})")

# Try the exact query the keywords route likely uses
print("\n--- keyword_daily snapshot_date range ---")
row = conn.execute("SELECT MIN(snapshot_date), MAX(snapshot_date) FROM analytics.keyword_daily WHERE customer_id=?", [CID]).fetchone()
print(f"  {row[0]} → {row[1]}")

# Check what snapshot_date the route would use (today = 2026-03-16)
print("\n--- keyword_daily rows for last 30 days ---")
n = conn.execute("""
    SELECT COUNT(*) FROM analytics.keyword_daily 
    WHERE customer_id=? AND snapshot_date >= '2026-02-15'
""", [CID]).fetchone()[0]
print(f"  Rows with snapshot_date >= 2026-02-15: {n}")

# Check ad_daily similarly
print("\n--- ad_daily rows for last 30 days ---")
n = conn.execute("""
    SELECT COUNT(*) FROM analytics.ad_daily 
    WHERE customer_id=? AND snapshot_date >= '2026-02-15'
""", [CID]).fetchone()[0]
print(f"  Rows with snapshot_date >= 2026-02-15: {n}")

# Check if routes might be querying by campaign_id join
print("\n--- keyword_daily: distinct campaign_ids ---")
rows = conn.execute("SELECT DISTINCT campaign_id FROM analytics.keyword_daily WHERE customer_id=?", [CID]).fetchall()
print(f"  campaign_ids: {[r[0] for r in rows]}")

print("\n--- campaign_daily: distinct campaign_ids ---")
rows = conn.execute("SELECT DISTINCT campaign_id FROM analytics.campaign_daily WHERE customer_id=?", [CID]).fetchall()
print(f"  campaign_ids: {[r[0] for r in rows]}")

# Type check — campaign_id is BIGINT in keyword_daily but VARCHAR in campaign_daily
print("\n--- campaign_id type per table ---")
for t in ['campaign_daily', 'keyword_daily', 'ad_group_daily', 'ad_daily']:
    cols = conn.execute(f"PRAGMA table_info('analytics.{t}')").fetchall()
    for c in cols:
        if c[1] == 'campaign_id':
            print(f"  {t}.campaign_id: {c[2]}")

conn.close()
print("\n✅ Done.")
