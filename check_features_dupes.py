import duckdb
conn = duckdb.connect('warehouse.duckdb')
conn.execute("ATTACH 'warehouse_readonly.duckdb' AS ro (READ_ONLY)")

# Check total rows and duplicates
total = conn.execute("SELECT COUNT(*) FROM ro.analytics.campaign_features_daily WHERE customer_id='1254895944'").fetchone()[0]
nullnames = conn.execute("SELECT COUNT(*) FROM ro.analytics.campaign_features_daily WHERE customer_id='1254895944' AND campaign_name IS NULL").fetchone()[0]
withnames = conn.execute("SELECT COUNT(*) FROM ro.analytics.campaign_features_daily WHERE customer_id='1254895944' AND campaign_name IS NOT NULL").fetchone()[0]

print(f"Total rows: {total}")
print(f"Rows with NULL campaign_name: {nullnames}")
print(f"Rows with valid campaign_name: {withnames}")

# Check if same snapshot_date has both
sample = conn.execute("""
    SELECT snapshot_date, COUNT(*) as cnt
    FROM ro.analytics.campaign_features_daily
    WHERE customer_id='1254895944' AND campaign_id='1001'
    GROUP BY snapshot_date
    ORDER BY snapshot_date DESC
    LIMIT 5
""").fetchall()
print("\nRows per date for campaign 1001:")
for r in sample:
    print(f"  {r[0]}: {r[1]} rows")

conn.close()
