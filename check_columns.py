import duckdb

conn = duckdb.connect('warehouse_readonly.duckdb', read_only=True)

# Get all columns for each table
tables = {
    'keyword_daily': 'analytics.keyword_daily',
    'ad_group_daily': 'analytics.ad_group_daily',
    'shopping_campaign_daily': 'analytics.shopping_campaign_daily'
}

for name, table in tables.items():
    print(f'\n=== {name} ===')
    result = conn.execute(f'DESCRIBE {table}').fetchall()
    for row in result:
        print(f'{row[0]}: {row[1]}')

conn.close()
