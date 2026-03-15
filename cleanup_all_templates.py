import duckdb

conn = duckdb.connect(r'C:\Users\User\Desktop\gads-data-layer\warehouse.duckdb')

# Show everything with (template) in the name
rows = conn.execute("""
    SELECT id, name, is_template, enabled
    FROM rules
    WHERE name LIKE '%(template)%'
    ORDER BY id
""").fetchall()

print("All rows with (template) in name:")
for r in rows:
    print(f"  ID {r[0]}: is_template={r[2]}, enabled={r[3]} — {r[1]}")

# Delete ALL of them for a clean slate
conn.execute("DELETE FROM rules WHERE name LIKE '%(template)%'")
conn.commit()

remaining = conn.execute("SELECT COUNT(*) FROM rules WHERE name LIKE '%(template)%'").fetchone()[0]
print(f"\nDeleted all. Remaining: {remaining}")
print(f"Total rules remaining: {conn.execute('SELECT COUNT(*) FROM rules').fetchone()[0]}")
conn.close()
