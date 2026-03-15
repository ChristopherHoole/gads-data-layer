import duckdb, json

conn = duckdb.connect(r'C:\Users\User\Desktop\gads-data-layer\warehouse.duckdb')
rows = conn.execute("""
    SELECT id, name, conditions, action_type, action_magnitude
    FROM rules
    WHERE is_template = TRUE
    ORDER BY id DESC
    LIMIT 3
""").fetchall()

for row in rows:
    print("=" * 60)
    print(f"ID:          {row[0]}")
    print(f"Name:        {row[1]}")
    print(f"action_type: {row[3]}")
    print(f"action_mag:  {row[4]}")
    print(f"conditions (raw): {row[2]}")
    try:
        parsed = json.loads(row[2])
        print(f"conditions (parsed): {parsed}")
    except Exception as e:
        print(f"conditions parse error: {e}")

print(f"\nTotal templates: {len(rows)}")
conn.close()
