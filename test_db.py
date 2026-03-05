import duckdb
conn = duckdb.connect('warehouse.duckdb')
conn.execute("ATTACH 'warehouse_readonly.duckdb' AS ro (READ_ONLY)")
result = conn.execute("SELECT COUNT(*) FROM ro.analytics.campaign_daily WHERE customer_id = '9999999999'").fetchone()
print('campaign_daily rows for synthetic client:', result[0])
result2 = conn.execute("SELECT COUNT(*) FROM ro.analytics.campaign_features_daily WHERE customer_id = '9999999999'").fetchone()
print('campaign_features_daily rows for synthetic client:', result2[0])
conn.close()
