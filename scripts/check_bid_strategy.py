import duckdb

conn = duckdb.connect('warehouse_readonly.duckdb')
rows = conn.execute(
    "SELECT DISTINCT bid_strategy_type, COUNT(*) as count "
    "FROM analytics.campaign_daily "
    "GROUP BY bid_strategy_type ORDER BY count DESC"
).fetchall()
print('bid_strategy_type values in campaign_daily:')
for r in rows:
    print(f'  {r[0]}: {r[1]} rows')
conn.close()
