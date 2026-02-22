import duckdb
conn = duckdb.connect('warehouse.duckdb')
for table in ['campaign_daily','ad_group_daily','keyword_daily','ad_features_daily','shopping_campaign_daily']:
    cols = [c[0] for c in conn.execute(f'DESCRIBE analytics.{table}').fetchall()]
    rows = conn.execute(f"SELECT COUNT(*) FROM analytics.{table} WHERE customer_id='9999999999'").fetchone()[0]
    print(f'{table}: {rows} rows | cols: {len(cols)}')
conn.close()
