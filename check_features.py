import duckdb

conn = duckdb.connect('warehouse.duckdb')

# Check product_features_daily
count = conn.execute(
    "SELECT COUNT(*) FROM analytics.product_features_daily WHERE customer_id = '1254895944'"
).fetchone()[0]

print(f"product_features_daily rows for customer 1254895944: {count}")

# Check if table exists and show sample
if count > 0:
    sample = conn.execute(
        "SELECT product_id, snapshot_date, roas_w7, cpa_w7, stock_out_flag FROM analytics.product_features_daily WHERE customer_id = '1254895944' LIMIT 3"
    ).fetchall()
    print("\nSample rows:")
    for row in sample:
        print(f"  {row}")
else:
    print("\n⚠️  No rows found - features table not populated")

conn.close()
