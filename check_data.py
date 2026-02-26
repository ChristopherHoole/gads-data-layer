import duckdb

# Connect to readonly database
conn = duckdb.connect('warehouse_readonly.duckdb', read_only=True)

# Check each table for synthetic customer 9999999999
tables_to_check = [
    'analytics.campaign_features_daily',
    'analytics.keyword_daily', 
    'analytics.ad_group_daily',
    'analytics.ad_daily',
    'analytics.shopping_campaign_daily',
    'analytics.product_daily'
]

print("=== DATA AVAILABILITY CHECK ===")
for table in tables_to_check:
    try:
        count = conn.execute(f'SELECT COUNT(*) FROM {table} WHERE customer_id=9999999999').fetchone()[0]
        print(f'✅ {table}: {count} rows')
    except Exception as e:
        print(f'❌ {table}: NOT FOUND - {str(e)[:50]}')

print("\n=== SCHEMA INVESTIGATION ===")
# For tables that exist, get column names
for table in tables_to_check:
    try:
        result = conn.execute(f'DESCRIBE {table}').fetchall()
        print(f'\n{table} columns:')
        for row in result[:10]:  # First 10 columns
            print(f'  - {row[0]} ({row[1]})')
        if len(result) > 10:
            print(f'  ... and {len(result)-10} more columns')
    except:
        pass

conn.close()