import duckdb

conn = duckdb.connect('warehouse.duckdb')
conn.execute("ATTACH 'warehouse_readonly.duckdb' AS ro (READ_ONLY)")

print("=" * 60)
print("SAMPLE SHOPPING DATA")
print("=" * 60)

# Try to get a sample row from shopping_campaign_daily
try:
    sample = conn.execute("""
        SELECT * 
        FROM ro.analytics.shopping_campaign_daily 
        LIMIT 1
    """).fetchone()
    
    if sample:
        cols = conn.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'shopping_campaign_daily' 
            AND table_schema = 'analytics'
            ORDER BY ordinal_position
        """).fetchall()
        
        print("First row values:")
        for i, col in enumerate(cols):
            value = sample[i]
            print(f"  {col[0]:40} = {value}")
    else:
        print("NO DATA IN TABLE")
except Exception as e:
    print(f"ERROR: {e}")

print()

# Check customer IDs in Shopping data
print("=" * 60)
print("CUSTOMER IDs IN SHOPPING DATA")
print("=" * 60)

try:
    customers = conn.execute("""
        SELECT DISTINCT customer_id
        FROM ro.analytics.shopping_campaign_daily
        ORDER BY customer_id
    """).fetchall()
    
    if customers:
        for c in customers:
            print(f"  {c[0]}")
    else:
        print("  NONE")
except Exception as e:
    print(f"ERROR: {e}")

print()

# Check if product tables have data
print("=" * 60)
print("PRODUCT TABLE DATA")
print("=" * 60)

product_tables = conn.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'analytics' 
    AND table_name LIKE '%product%'
""").fetchall()

if product_tables:
    for table in product_tables:
        table_name = table[0]
        try:
            count = conn.execute(f"""
                SELECT COUNT(*) 
                FROM ro.analytics.{table_name}
            """).fetchone()[0]
            print(f"  {table_name}: {count:,} rows")
        except Exception as e:
            print(f"  {table_name}: ERROR - {e}")
else:
    print("  NO PRODUCT TABLES FOUND")

conn.close()
