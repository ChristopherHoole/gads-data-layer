import duckdb
conn = duckdb.connect('warehouse.duckdb')
conn.execute("ATTACH 'warehouse_readonly.duckdb' AS ro (READ_ONLY)")

rows = conn.execute("""
    SELECT campaign_id, campaign_name, snapshot_date
    FROM ro.analytics.campaign_features_daily
    WHERE customer_id='1254895944' AND campaign_name IS NULL
    ORDER BY campaign_id, snapshot_date
""").fetchall()

print("Rows with NULL campaign_name:")
for r in rows:
    print(f"  campaign_id={r[0]} name={r[1]} date={r[2]}")

conn.close()
