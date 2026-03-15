import duckdb

conn = duckdb.connect(r'C:\Users\User\Desktop\gads-data-layer\warehouse.duckdb')

rows = conn.execute("""
    SELECT id, name, is_template, typeof(is_template)
    FROM rules
    WHERE id >= 58
    ORDER BY id
""").fetchall()

for row in rows:
    print(f"ID {row[0]}: {row[1]}")
    print(f"  is_template value: {row[2]}")
    print(f"  is_template type:  {row[3]}")
    print(f"  bool(is_template): {bool(row[2])}")
    print()

conn.close()
