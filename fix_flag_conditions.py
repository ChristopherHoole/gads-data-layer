import duckdb, json

conn = duckdb.connect('warehouse.duckdb')

# Check all flag conditions that use _vs_prev_pct metrics
# These store as decimal ratios (-0.30 = -30%) not percentages (-30)
rows = conn.execute("""
    SELECT id, name, conditions 
    FROM rules 
    WHERE rule_or_flag = 'flag' AND conditions IS NOT NULL
    ORDER BY id
""").fetchall()

print("=== ALL FLAG CONDITIONS using vs_prev_pct metrics ===\n")
needs_fix = []
for row in rows:
    conds = json.loads(row[2]) if row[2] else []
    for c in conds:
        metric = c.get('metric','')
        val = c.get('value')
        if 'vs_prev_pct' in metric and val is not None:
            print(f"id={row[0]} name={row[1]}")
            print(f"  metric={metric} op={c.get('op')} value={val} ref={c.get('ref')}")
            # If value is stored as whole number percentage (e.g. -30) not decimal (-0.30)
            if abs(float(val)) > 1:
                print(f"  *** NEEDS FIX: {val} should be {float(val)/100}")
                needs_fix.append(row[0])
            print()

print(f"\nFlags needing fix: {needs_fix}")
conn.close()
