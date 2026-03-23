import duckdb
import json

conn = duckdb.connect('warehouse.duckdb')

print("\n=== PRODUCT RULES DIAGNOSTIC ===\n")

rows = conn.execute("""
    SELECT id, name, type, conditions 
    FROM rules 
    WHERE entity_type='shopping_product' 
      AND rule_or_flag='rule'
    ORDER BY id
""").fetchall()

print(f"Total Product Rules: {len(rows)}\n")

for r in rows:
    rule_id = r[0]
    name = r[1]
    rule_type = r[2] if r[2] else "NULL"
    conditions = json.loads(r[3])
    
    print(f"ID {rule_id}: {name}")
    print(f"  Type: {rule_type}")
    print(f"  Conditions: {conditions}")
    
    # Check for cost values
    for cond in conditions:
        if 'cost' in cond.get('metric', ''):
            print(f"  ⚠️  COST VALUE: {cond['value']} (should be < 1000 if in pounds)")
    
    print()

# Check for NULL types
null_types = conn.execute("""
    SELECT COUNT(*) FROM rules 
    WHERE entity_type='shopping_product' 
      AND rule_or_flag='rule'
      AND (type IS NULL OR type = '')
""").fetchone()[0]

print(f"Rules with NULL/blank type: {null_types}")

conn.close()

print("\n✅ DONE")
