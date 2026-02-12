import duckdb
con = duckdb.connect('warehouse.duckdb')
r = con.execute("SELECT campaign_id, cost_w14_cv FROM analytics.campaign_features_daily WHERE campaign_id='2007' AND snapshot_date='2026-02-11'").fetchall()
print(r)
con.close()