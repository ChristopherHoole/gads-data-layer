import duckdb

conn = duckdb.connect('warehouse.duckdb')

print('=== ALL COLUMNS IN RULES TABLE ===')
cols = conn.execute("DESCRIBE rules").fetchall()
for c in cols:
    print(c)

print()
print('=== RULES (rule_or_flag = rule) ===')
rules = conn.execute(
    "SELECT id, name, entity_type, action_type, enabled, cooldown_days "
    "FROM rules WHERE is_template = FALSE AND rule_or_flag = 'rule' "
    "ORDER BY entity_type, id"
).fetchall()
for r in rules:
    print(r)

print()
print('=== FLAGS (rule_or_flag = flag) ===')
flags = conn.execute(
    "SELECT id, name, entity_type, enabled, cooldown_days "
    "FROM rules WHERE is_template = FALSE AND rule_or_flag = 'flag' "
    "ORDER BY entity_type, id"
).fetchall()
for f in flags:
    print(f)

print()
print('=== COUNTS BY entity_type + rule_or_flag ===')
counts = conn.execute(
    "SELECT entity_type, rule_or_flag, COUNT(id) "
    "FROM rules WHERE is_template = FALSE "
    "GROUP BY entity_type, rule_or_flag ORDER BY entity_type, rule_or_flag"
).fetchall()
for c in counts:
    print(c)

conn.close()
