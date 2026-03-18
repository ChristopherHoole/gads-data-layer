import duckdb
conn = duckdb.connect('warehouse.duckdb')

# Enable rules for Test 3
enable_ids = [1, 6, 16, 25, 27]
for rule_id in enable_ids:
    conn.execute("UPDATE rules SET enabled=TRUE WHERE id=?", [rule_id])
    row = conn.execute("SELECT id, name, enabled FROM rules WHERE id=?", [rule_id]).fetchone()
    print(f"id={row[0]} enabled={row[2]} name={row[1]}")

print(f"\nTotal enabled: {conn.execute('SELECT COUNT(*) FROM rules WHERE enabled=TRUE AND is_template=FALSE').fetchone()[0]}")
conn.close()
print("Done.")
