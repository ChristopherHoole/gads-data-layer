import duckdb

conn = duckdb.connect('warehouse.duckdb')

tables = ['campaign_daily', 'ad_group_daily', 'keyword_daily', 'ad_daily']

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

print('\n=== ALL TABLES IN analytics SCHEMA ===')
try:
    tables_list = conn.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='analytics' ORDER BY table_name").fetchall()
    for t in tables_list:
        print(f'  {t[0]}')
except Exception as e:
    print(f'  ERROR: {e}')

conn.close()
print('\nDONE')
