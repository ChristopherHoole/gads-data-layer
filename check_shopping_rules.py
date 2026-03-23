import duckdb

conn = duckdb.connect('warehouse.duckdb')

# Check rules by action_type
print("\n=== SHOPPING RULES BY ACTION TYPE ===")
result = conn.execute("""
    SELECT action_type, COUNT(*) as count 
    FROM rules 
    WHERE entity_type='shopping' AND is_template=FALSE 
    GROUP BY action_type
    ORDER BY action_type
""").fetchall()

for row in result:
    print(f"{row[0]}: {row[1]}")

# Get total count
total = conn.execute("""
    SELECT COUNT(*) 
    FROM rules 
    WHERE entity_type='shopping' AND is_template=FALSE
""").fetchone()[0]

print(f"\nTOTAL SHOPPING RULES: {total}")

# List all rules with names
print("\n=== ALL SHOPPING RULES (NAMES) ===")
rules = conn.execute("""
    SELECT id, name, action_type, enabled
    FROM rules 
    WHERE entity_type='shopping' AND is_template=FALSE
    ORDER BY action_type, name
""").fetchall()

for rule in rules:
    enabled_str = "ON" if rule[3] else "OFF"
    print(f"[{enabled_str}] {rule[0]}: {rule[2]} - {rule[1]}")

conn.close()
