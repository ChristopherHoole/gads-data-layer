import duckdb, json
conn = duckdb.connect('warehouse.duckdb')

flags = conn.execute("""
    SELECT id, name, conditions FROM rules 
    WHERE rule_or_flag='flag' AND conditions IS NOT NULL
    ORDER BY id
""").fetchall()

print("=== FLAGS WITHOUT vs_prev_pct conditions ===\n")
for f_row in flags:
    conds = json.loads(f_row[2]) if f_row[2] else []
    has_pct = any('vs_prev_pct' in (c.get('metric') or '') for c in conds)
    if not has_pct:
        print(f"id={f_row[0]} {f_row[1]}")
        for c in conds:
            print(f"  metric={c.get('metric')} op={c.get('op')} value={c.get('value')} ref={c.get('ref')}")
conn.close()
