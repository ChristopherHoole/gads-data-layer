import duckdb, json

conn = duckdb.connect('warehouse.duckdb')

# Read current conditions
row = conn.execute("SELECT conditions FROM rules WHERE id=33").fetchone()
conds = json.loads(row[0])
print("BEFORE:", conds)

# Lower threshold from -0.3 to -0.05 (5% drop)
for c in conds:
    if c.get('metric') == 'conversions_w7_vs_prev_pct':
        c['value'] = -0.05
        print(f"Changed threshold to {c['value']}")

conn.execute("UPDATE rules SET conditions=? WHERE id=33", [json.dumps(conds)])
print("AFTER:", conds)
print("\nDone. Remember to restore to -0.3 after testing.")
conn.close()
