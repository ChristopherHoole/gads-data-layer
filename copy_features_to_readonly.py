import duckdb

CID = "1254895944"
conn_ro = duckdb.connect('warehouse_readonly.duckdb')
conn_ro.execute("ATTACH 'warehouse.duckdb' AS src (READ_ONLY)")

for table in ['campaign_features_daily', 'keyword_features_daily', 'ad_features_daily']:
    try:
        conn_ro.execute(f"DROP TABLE IF EXISTS analytics.{table}")
        conn_ro.execute(f"CREATE TABLE analytics.{table} AS SELECT * FROM src.analytics.{table}")
        n = conn_ro.execute(f"SELECT COUNT(*) FROM analytics.{table}").fetchone()[0]
        cid_n = conn_ro.execute(f"SELECT COUNT(*) FROM analytics.{table} WHERE customer_id=?", [CID]).fetchone()[0]
        print(f"  ✅ {table}: {n:,} total ({cid_n:,} Christopher Hoole)")
    except Exception as e:
        print(f"  ❌ {table}: {e}")

conn_ro.execute("DETACH src")
conn_ro.close()
print("✅ Done. Restart Flask and test.")
