"""
Fix rule id=7 (Decrease Budget - Weak CPA) condition 2.
The condition 2 has ref stored as a non-numeric value.
Correct: Conversions (7d) > 3 (need at least 3 conversions to have certainty)
"""
import duckdb, json

conn = duckdb.connect('warehouse.duckdb')

# First check what's currently stored
row = conn.execute("SELECT id, name, conditions FROM rules WHERE id=7").fetchone()
print(f"Rule: {row[1]}")
print(f"Current conditions: {row[2]}")
print()

# Parse and show conditions
conds = json.loads(row[2]) if row[2] else []
for i, c in enumerate(conds):
    print(f"  Condition {i+1}: {c}")

print()

# Fix condition 2: set ref to 3 (numeric) and unit to "absolute"
for c in conds:
    metric = c.get('metric','') or c.get('condition_metric','')
    if 'conversion' in metric.lower():
        old_ref = c.get('ref') or c.get('condition_value')
        c['ref'] = 3
        if 'unit' in c: c['unit'] = 'absolute'
        print(f"Fixed condition: {metric} ref {old_ref} -> 3")

new_conditions = json.dumps(conds)
conn.execute("UPDATE rules SET conditions=? WHERE id=7", [new_conditions])
print(f"\nUpdated conditions: {new_conditions}")
conn.close()
print("\n✅ Done. Restart Flask and re-run recommendations engine.")
