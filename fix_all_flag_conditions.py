import duckdb, json

conn = duckdb.connect('warehouse.duckdb')

# op mapping for flags with op=None — based on flag name logic
OP_FIX = {
    27: ('gt', 'pct'),   # CPA Spike — CPA increased
    29: ('lt', 'pct'),   # CTR Drop — CTR decreased
    30: ('gt', 'pct'),   # CTR Spike — CTR increased
    31: ('lt', 'pct'),   # CVR Drop — CVR decreased
    32: ('gt', 'pct'),   # CVR Spike — CVR increased
    37: ('lt', 'pct'),   # Impression Share Drop — IS decreased
    38: ('gt', 'pct'),   # Impression Share Spike — IS increased
    40: ('gt', 'pct'),   # CPC Spike — CPC increased
}

rows = conn.execute("""
    SELECT id, name, conditions 
    FROM rules 
    WHERE rule_or_flag = 'flag' AND conditions IS NOT NULL
    ORDER BY id
""").fetchall()

fixed = 0
for row in rows:
    rule_id = row[0]
    conds = json.loads(row[2]) if row[2] else []
    changed = False
    for c in conds:
        metric = c.get('metric', '')
        val = c.get('value')

        # Fix 1: divide vs_prev_pct whole-number values by 100
        if 'vs_prev_pct' in metric and val is not None and abs(float(val)) > 1:
            old_val = val
            c['value'] = float(val) / 100
            print(f"id={rule_id} {row[1]}: {metric} value {old_val} → {c['value']}")
            changed = True

        # Fix 2: set op and ref where op=None
        if c.get('op') is None and rule_id in OP_FIX:
            c['op'] = OP_FIX[rule_id][0]
            c['ref'] = OP_FIX[rule_id][1]
            print(f"id={rule_id} {row[1]}: set op={c['op']} ref={c['ref']}")
            changed = True

    if changed:
        conn.execute("UPDATE rules SET conditions=? WHERE id=?", [json.dumps(conds), rule_id])
        fixed += 1

conn.close()
print(f"\nFixed {fixed} flags.")
