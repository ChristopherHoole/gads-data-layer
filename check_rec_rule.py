import duckdb
conn = duckdb.connect('warehouse.duckdb')

# Check the 4 pending recs we generated
rows = conn.execute("SELECT rec_id, rule_id, rule_type FROM recommendations WHERE status='pending'").fetchall()
for r in rows:
    print(f"rule_id='{r[1]}' type={r[2]}")

print()
# Get rule 7 name specifically
row = conn.execute("SELECT id, name FROM rules WHERE id=7").fetchone()
print(f"Rule 7: id={row[0]} name='{row[1]}' -> key='db_campaign_7'")

print()
# Simulate name_map lookup
name_map = {}
rows2 = conn.execute("SELECT id, name FROM rules WHERE entity_type='campaign' AND rule_or_flag='rule' AND is_template=FALSE").fetchall()
for r in rows2:
    key = "db_campaign_{}".format(r[0])
    name_map[key] = r[1]
    print(f"  {key} -> '{r[1]}'")

print()
print("Lookup 'db_campaign_7':", name_map.get('db_campaign_7', 'NOT FOUND'))
conn.close()
