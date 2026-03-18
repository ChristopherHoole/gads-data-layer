import duckdb, json
conn = duckdb.connect('warehouse.duckdb')

# Check rule 21 - Decrease Max CPC Cap
row = conn.execute("""
    SELECT id, name, type, action_type, action_magnitude, conditions, rule_or_flag
    FROM rules WHERE id=21
""").fetchone()

print(f"id: {row[0]}")
print(f"name: {row[1]}")
print(f"type: {row[2]}")
print(f"action_type: {row[3]}")
print(f"action_magnitude: {row[4]}")
print(f"rule_or_flag: {row[6]}")
print(f"conditions: {row[5]}")

conn.close()
