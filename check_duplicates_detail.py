import duckdb, json

conn = duckdb.connect(r'C:\Users\User\Desktop\gads-data-layer\warehouse.duckdb')

print("=== Duplicate rows and their campaign_type_lock ===")
rows = conn.execute("""
    SELECT id, name, campaign_type_lock, type, action_type,
           json_extract_string(conditions, '$[0].metric') as c1_metric
    FROM rules WHERE id IN (59, 60, 1, 7)
    ORDER BY id
""").fetchall()
for r in rows:
    print(f"  ID {r[0]}: lock='{r[2]}', type={r[3]}, action={r[4]}, c1={r[5]} — {r[1]}")

conn.close()
