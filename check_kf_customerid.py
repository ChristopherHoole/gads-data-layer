import duckdb
conn = duckdb.connect('warehouse_readonly.duckdb')

print("--- keyword_features_daily customer_id values ---")
rows = conn.execute("""
    SELECT customer_id, COUNT(*) as cnt, MAX(snapshot_date) as latest
    FROM analytics.keyword_features_daily
    GROUP BY customer_id
""").fetchall()
for r in rows:
    print(f"  customer_id='{r[0]}'  count={r[1]}  latest={r[2]}")

print("\n--- keyword_features_daily columns: client_id, customer_id ---")
row = conn.execute("SELECT client_id, customer_id, snapshot_date FROM analytics.keyword_features_daily LIMIT 3").fetchall()
for r in row:
    print(f"  client_id='{r[0]}'  customer_id='{r[1]}'  snapshot_date={r[2]}")

conn.close()
