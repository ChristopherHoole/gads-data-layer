import duckdb

conn = duckdb.connect('warehouse.duckdb')

print("=== DB-sourced recommendations (db_campaign_ prefix) ===")
rows = conn.execute(
    "SELECT rule_id, COUNT(rec_id) as count FROM recommendations "
    "WHERE rule_id LIKE 'db_campaign%' "
    "GROUP BY rule_id ORDER BY rule_id"
).fetchall()
if rows:
    for r in rows:
        print(f"  {r[0]}: {r[1]} recs")
else:
    print("  None found yet")

print()
print("=== All rule_id prefixes in recommendations table ===")
rows2 = conn.execute(
    "SELECT LEFT(rule_id, 15) as prefix, COUNT(rec_id) as count "
    "FROM recommendations "
    "GROUP BY LEFT(rule_id, 15) ORDER BY count DESC"
).fetchall()
for r in rows2:
    print(f"  {r[0]}: {r[1]} recs")

print()
print("=== Recommendations by customer_id ===")
rows3 = conn.execute(
    "SELECT customer_id, status, COUNT(rec_id) as count "
    "FROM recommendations "
    "GROUP BY customer_id, status ORDER BY customer_id, status"
).fetchall()
for r in rows3:
    print(f"  customer={r[0]} status={r[1]}: {r[2]} recs")

conn.close()
