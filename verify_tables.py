import duckdb

conn = duckdb.connect('warehouse.duckdb')
tables = ['campaign_daily', 'ad_group_daily', 'keyword_daily', 'ad_features_daily', 'shopping_campaign_daily']

for t in tables:
    cols = len(conn.execute(f'DESCRIBE analytics.{t}').fetchall())
    rows = conn.execute(f"SELECT COUNT(*) FROM analytics.{t} WHERE customer_id='9999999999'").fetchone()[0]
    print(f'{t}: {rows} rows | {cols} cols')

conn.close()
print('\nDone.')
