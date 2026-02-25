import duckdb

conn = duckdb.connect('warehouse.duckdb')

# Check scope column exists and values
result = conn.execute("""
    SELECT 
        CASE 
            WHEN campaign_id IS NULL THEN 'blanket'
            ELSE 'campaign-specific'
        END as scope_type,
        COUNT(*) as count
    FROM warehouse.recommendations
    GROUP BY scope_type
""").fetchall()

print("Scope distribution:")
for scope, count in result:
    print(f"  {scope}: {count}")

# Check if there's a scope column
columns = conn.execute("DESCRIBE warehouse.recommendations").fetchall()
print("\nColumns in recommendations table:")
for col in columns:
    print(f"  {col[0]}: {col[1]}")

conn.close()
