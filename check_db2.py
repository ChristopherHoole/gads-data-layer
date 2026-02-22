import duckdb

conn = duckdb.connect('warehouse.duckdb')

tables = ['ad_features_daily', 'shopping_campaign_daily', 'campaign_features_daily', 'keyword_features_daily']

for table in tables:
    print(f'\n=== {table} ===')
    try:
        cols = conn.execute(f'DESCRIBE analytics.{table}').fetchall()
        for c in cols:
            print(f'  {c[0]:<45} {c[1]}')
        rows = conn.execute(f"SELECT COUNT(*) FROM analytics.{table} WHERE customer_id='9999999999'").fetchone()[0]
        print(f'  --- Rows (synthetic): {rows}')
    except Exception as e:
        print(f'  ERROR: {e}')

conn.close()
print('\nDONE')
