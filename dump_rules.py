import duckdb, json

conn = duckdb.connect(r'C:\Users\User\Desktop\gads-data-layer\warehouse.duckdb')

rows = conn.execute("""
    SELECT id, name, conditions, action_type, action_magnitude
    FROM rules
    WHERE client_config = 'client_christopher_hoole'
    ORDER BY type, name
""").fetchall()

for row in rows:
    print("=" * 60)
    print(f"ID:         {row[0]}")
    print(f"Name:       {row[1]}")
    print(f"action_type:{row[3]}")
    print(f"action_mag: {row[4]}")
    try:
        conds = json.loads(row[2]) if row[2] else []
        for i, c in enumerate(conds, 1):
            print(f"Condition {i}: {c}")
    except Exception as e:
        print(f"conditions (raw): {row[2]}")

print("=" * 60)
print(f"Total: {len(rows)} rules")
