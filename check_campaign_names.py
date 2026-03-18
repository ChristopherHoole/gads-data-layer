import duckdb
conn = duckdb.connect('warehouse.duckdb')
conn.execute("ATTACH 'warehouse_readonly.duckdb' AS ro (READ_ONLY)")

rows = conn.execute("""
    SELECT DISTINCT campaign_id, campaign_name 
    FROM ro.analytics.campaign_features_daily
    WHERE customer_id = '1254895944'
    ORDER BY campaign_id
""").fetchall()

for r in rows:
    print(f"id={r[0]} name={r[1]}")
conn.close()
