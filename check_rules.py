import duckdb
conn = duckdb.connect('warehouse.duckdb')
rows = conn.execute("SELECT id, name, enabled FROM rules WHERE is_template=FALSE ORDER BY id").fetchall()
for r in rows:
    print(f"id={r[0]} enabled={r[2]} name={r[1]}")
conn.close()
