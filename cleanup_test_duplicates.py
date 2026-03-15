import duckdb

conn = duckdb.connect(r'C:\Users\User\Desktop\gads-data-layer\warehouse.duckdb')

# Delete the two test duplicates created during template testing
rows = conn.execute("SELECT id, name FROM rules WHERE id IN (59, 61)").fetchall()
print("Deleting:")
for r in rows:
    print(f"  ID {r[0]}: {r[1]}")

conn.execute("DELETE FROM rules WHERE id IN (59, 61)")
conn.commit()

total = conn.execute("SELECT COUNT(*) FROM rules").fetchone()[0]
print(f"\nDone. Total rows: {total}")
conn.close()
