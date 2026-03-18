import duckdb
conn = duckdb.connect('warehouse.duckdb')
conn.execute("ATTACH 'warehouse_readonly.duckdb' AS ro (READ_ONLY)")

# Check what the engine selects - most recent snapshot date
row = conn.execute("""
    SELECT MAX(snapshot_date)
    FROM ro.analytics.campaign_features_daily
    WHERE customer_id='1254895944'
""").fetchone()
print(f"Most recent snapshot_date: {row[0]}")

# Check names on that date
rows = conn.execute("""
    SELECT campaign_id, campaign_name, snapshot_date
    FROM ro.analytics.campaign_features_daily
    WHERE customer_id='1254895944' AND snapshot_date = ?
    ORDER BY campaign_id
""", [row[0]]).fetchall()
print(f"\nCampaigns on most recent date ({row[0]}):")
for r in rows:
    print(f"  campaign_id={r[0]} name={r[1]}")

conn.close()
