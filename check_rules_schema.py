import duckdb

conn = duckdb.connect('warehouse.duckdb')

print("\n=== RULES TABLE SCHEMA ===\n")

# Get column info
columns = conn.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'rules'
    ORDER BY ordinal_position
""").fetchall()

for col in columns:
    print(f"{col[0]}: {col[1]}")

print(f"\nTotal columns: {len(columns)}")

# Show a sample rule
print("\n=== SAMPLE SHOPPING RULE (for reference) ===\n")
sample = conn.execute("""
    SELECT * 
    FROM rules 
    WHERE entity_type='shopping' AND is_template=FALSE
    LIMIT 1
""").fetchone()

if sample:
    col_names = [desc[0] for desc in conn.execute("SELECT * FROM rules LIMIT 0").description]
    for i, col_name in enumerate(col_names):
        print(f"{col_name}: {sample[i]}")

conn.close()
