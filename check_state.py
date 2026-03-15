import duckdb, json

conn = duckdb.connect(r'C:\Users\User\Desktop\gads-data-layer\warehouse.duckdb')

print("=== ALL ROWS WITH is_template=TRUE ===")
rows = conn.execute("""
    SELECT id, name, is_template, enabled, action_type
    FROM rules WHERE is_template = TRUE ORDER BY id
""").fetchall()
if rows:
    for r in rows:
        print(f"  ID {r[0]}: is_template={r[2]}, enabled={r[3]}, action_type={r[4]} — {r[1]}")
else:
    print("  None")

print("\n=== MOST RECENTLY CREATED ROWS (last 5) ===")
rows = conn.execute("""
    SELECT id, name, is_template, enabled, action_type, created_at
    FROM rules ORDER BY id DESC LIMIT 5
""").fetchall()
for r in rows:
    print(f"  ID {r[0]}: is_template={r[2]}, enabled={r[3]}, action_type={r[4]} — {r[1]}")

print(f"\n=== TOTAL ROWS: {conn.execute('SELECT COUNT(*) FROM rules').fetchone()[0]} ===")
conn.close()
