import duckdb

conn = duckdb.connect('warehouse.duckdb')
conn.execute("ATTACH 'warehouse_readonly.duckdb' AS ro (READ_ONLY)")

# Check all Shopping/Product tables
print("=" * 60)
print("SHOPPING/PRODUCT TABLES")
print("=" * 60)
tables = conn.execute("""
    SELECT table_schema, table_name 
    FROM information_schema.tables 
    WHERE table_name LIKE '%shopping%' OR table_name LIKE '%product%'
    ORDER BY table_schema, table_name
""").fetchall()

if tables:
    for t in tables:
        print(f"{t[0]}.{t[1]}")
else:
    print("NONE FOUND")

print()

# Check shopping_campaign_daily schema
print("=" * 60)
print("SHOPPING_CAMPAIGN_DAILY COLUMNS")
print("=" * 60)
cols = conn.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'shopping_campaign_daily' 
    AND table_schema = 'analytics'
    ORDER BY ordinal_position
""").fetchall()

if cols:
    for c in cols:
        print(f"{c[0]:40} {c[1]}")
else:
    print("TABLE NOT FOUND")

print()

# Check for optimization_score
print("=" * 60)
print("OPTIMIZATION_SCORE COLUMNS")
print("=" * 60)
opt_cols = conn.execute("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name = 'shopping_campaign_daily' 
    AND table_schema = 'analytics'
    AND column_name LIKE '%optim%'
""").fetchall()

if opt_cols:
    for c in opt_cols:
        print(c[0])
else:
    print("NONE FOUND")

print()

# Check for data
print("=" * 60)
print("SHOPPING DATA COUNTS")
print("=" * 60)
try:
    result = conn.execute("""
        SELECT 
            COUNT(*) as rows,
            COUNT(DISTINCT customer_id) as customers,
            COUNT(DISTINCT campaign_id) as campaigns
        FROM ro.analytics.shopping_campaign_daily
    """).fetchone()
    print(f"Total Rows:      {result[0]:,}")
    print(f"Unique Customers: {result[1]:,}")
    print(f"Unique Campaigns: {result[2]:,}")
except Exception as e:
    print(f"ERROR: {e}")

print()

# Check product-level tables
print("=" * 60)
print("PRODUCT-LEVEL TABLES")
print("=" * 60)
product_tables = conn.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'analytics' 
    AND table_name LIKE '%product%'
""").fetchall()

if product_tables:
    for t in product_tables:
        print(t[0])
else:
    print("NONE FOUND")

conn.close()
