import duckdb

con = duckdb.connect('warehouse_readonly.duckdb', read_only=True)
con.execute("ATTACH 'warehouse.duckdb' AS writable")

print('=== TABLES WITH search_term IN NAME ===')
result = con.execute("""
    SELECT table_schema, table_name 
    FROM information_schema.tables 
    WHERE table_name LIKE '%search_term%'
""").fetchall()
print(result if result else 'NO TABLES FOUND')

print('\n=== ALL ANALYTICS TABLES ===')
all_tables = con.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'analytics' 
    ORDER BY table_name
""").fetchall()
for t in all_tables:
    print(t[0])

con.close()