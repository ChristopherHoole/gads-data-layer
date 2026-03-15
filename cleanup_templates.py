import duckdb

conn = duckdb.connect(r'C:\Users\User\Desktop\gads-data-layer\warehouse.duckdb')

# Delete all broken template rows (is_template = TRUE)
result = conn.execute("SELECT id, name FROM rules WHERE is_template = TRUE").fetchall()
print(f"Deleting {len(result)} broken template rows:")
for r in result:
    print(f"  ID {r[0]}: {r[1]}")

conn.execute("DELETE FROM rules WHERE is_template = TRUE")
conn.commit()

remaining = conn.execute("SELECT COUNT(*) FROM rules WHERE is_template = TRUE").fetchone()[0]
print(f"\nDone. Templates remaining: {remaining}")
conn.close()
