import duckdb

conn = duckdb.connect(r'C:\Users\User\Desktop\gads-data-layer\warehouse.duckdb')

print("=== All Pacing Reduction rows ===")
rows = conn.execute("""
    SELECT id, name, campaign_type_lock, is_template, enabled
    FROM rules 
    WHERE name LIKE '%Pacing%'
    ORDER BY id
""").fetchall()
for r in rows:
    print(f"  ID {r[0]}: lock={r[2]}, is_template={r[3]}, enabled={r[4]} — {r[1]}")

print(f"\n=== TOTAL ROWS: {conn.execute('SELECT COUNT(*) FROM rules').fetchone()[0]} ===")
conn.close()
