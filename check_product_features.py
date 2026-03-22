import duckdb

conn = duckdb.connect('warehouse.duckdb')
conn.execute("ATTACH 'warehouse_readonly.duckdb' AS ro (READ_ONLY)")

print("=" * 60)
print("PRODUCT_FEATURES_DAILY SCHEMA")
print("=" * 60)

cols = conn.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'product_features_daily' 
    AND table_schema = 'analytics'
    ORDER BY ordinal_position
""").fetchall()

if cols:
    for c in cols:
        print(f"{c[0]:40} {c[1]}")
else:
    print("TABLE NOT FOUND")

print()
print("=" * 60)
print("SAMPLE PRODUCT DATA")
print("=" * 60)

try:
    # Get column names for display
    col_names = [c[0] for c in cols]
    
    # Get one sample row
    sample = conn.execute("""
        SELECT * 
        FROM ro.analytics.product_features_daily 
        LIMIT 1
    """).fetchone()
    
    if sample:
        print("First row values:")
        for i, col_name in enumerate(col_names):
            value = sample[i]
            print(f"  {col_name:40} = {value}")
    else:
        print("NO DATA")
except Exception as e:
    print(f"ERROR: {e}")

conn.close()
