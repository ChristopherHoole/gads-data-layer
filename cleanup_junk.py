import duckdb

conn = duckdb.connect(r'C:\Users\User\Desktop\gads-data-layer\warehouse.duckdb')

junk_ids = [55, 56, 57, 60]

rows = conn.execute(f"SELECT id, name FROM rules WHERE id IN ({','.join(str(i) for i in junk_ids)})").fetchall()
print("Deleting:")
for r in rows:
    print(f"  ID {r[0]}: {r[1]}")

conn.execute(f"DELETE FROM rules WHERE id IN ({','.join(str(i) for i in junk_ids)})")
conn.commit()

total = conn.execute("SELECT COUNT(*) FROM rules").fetchone()[0]
rules = conn.execute("SELECT COUNT(*) FROM rules WHERE rule_or_flag='rule' AND is_template=FALSE").fetchone()[0]
flags = conn.execute("SELECT COUNT(*) FROM rules WHERE rule_or_flag='flag' AND is_template=FALSE").fetchone()[0]
templates = conn.execute("SELECT COUNT(*) FROM rules WHERE is_template=TRUE").fetchone()[0]

print(f"\nDone.")
print(f"  Rules:     {rules}")
print(f"  Flags:     {flags}")
print(f"  Templates: {templates}")
print(f"  Total:     {total}")
conn.close()
