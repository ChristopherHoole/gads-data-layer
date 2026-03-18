import duckdb, json
conn = duckdb.connect('warehouse.duckdb')

# First check actual columns
cols = conn.execute("PRAGMA table_info('recommendations')").fetchall()
print("Columns:", [c[1] for c in cols])
print()

# Then check pending campaign recs
rows = conn.execute("""
    SELECT rule_id, rule_type, trigger_summary, entity_name, customer_id
    FROM recommendations 
    WHERE status='pending' AND rule_id LIKE 'db_campaign%'
    LIMIT 4
""").fetchall()
for r in rows:
    print(f"rule_id='{r[0]}' type={r[1]} entity='{r[3]}'")
    print(f"  trigger_summary: {r[2]}")
    print()
conn.close()
