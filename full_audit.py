import duckdb, json

conn = duckdb.connect(r'C:\Users\User\Desktop\gads-data-layer\warehouse.duckdb')

print("=== RULES ===")
rows = conn.execute("""
    SELECT id, name, type, action_type, campaign_type_lock, enabled, is_template
    FROM rules
    WHERE rule_or_flag = 'rule' AND is_template = FALSE
    ORDER BY type, id
""").fetchall()
print(f"Total: {len(rows)}")
for r in rows:
    print(f"  ID {r[0]:3d}: [{r[2]:8s}] {r[4]:12s} enabled={r[5]} — {r[1]}")

print("\n=== FLAGS ===")
rows = conn.execute("""
    SELECT id, name, type, enabled, is_template
    FROM rules
    WHERE rule_or_flag = 'flag' AND is_template = FALSE
    ORDER BY type, id
""").fetchall()
print(f"Total: {len(rows)}")
for r in rows:
    print(f"  ID {r[0]:3d}: [{r[2]:12s}] enabled={r[3]} — {r[1]}")

print("\n=== TEMPLATES ===")
rows = conn.execute("""
    SELECT id, name, rule_or_flag, type, is_template, enabled
    FROM rules
    WHERE is_template = TRUE
    ORDER BY id
""").fetchall()
print(f"Total: {len(rows)}")
for r in rows:
    print(f"  ID {r[0]:3d}: [{r[2]:5s}/{r[3]:8s}] enabled={r[4]} — {r[1]}")

print(f"\n=== GRAND TOTAL: {conn.execute('SELECT COUNT(*) FROM rules').fetchone()[0]} rows ===")
conn.close()
