import duckdb, json

conn = duckdb.connect(r'C:\Users\User\Desktop\gads-data-layer\warehouse.duckdb')
rows = conn.execute("""
    SELECT name, conditions, action_type
    FROM rules
    WHERE name LIKE '%Poor ROAS%'
    OR name LIKE '%CTR copy%'
    OR name LIKE '%ROAS (7d) test%'
""").fetchall()

for row in rows:
    print("=" * 60)
    print(f"Name:        {row[0]}")
    print(f"action_type: {row[2]}")
    try:
        conds = json.loads(row[1]) if row[1] else []
        for i, c in enumerate(conds, 1):
            print(f"Condition {i}: {c}")
    except:
        print(f"conditions (raw): {row[1]}")
