import duckdb
conn = duckdb.connect('warehouse_readonly.duckdb', read_only=True)

try:
    result = conn.execute("SELECT COUNT(*), MIN(snapshot_date), MAX(snapshot_date) FROM analytics.ad_daily WHERE customer_id = '9999999999'").fetchone()
    if result[0] > 0:
        print(f'ad_daily: {result[0]:,} rows from {result[1]} to {result[2]}')
    else:
        print('ad_daily: 0 rows')
except Exception as e:
    print(f'ad_daily: Table does not exist or error - {str(e)[:60]}')

conn.close()
