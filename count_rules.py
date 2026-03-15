import duckdb

conn = duckdb.connect(r'C:\Users\User\Desktop\gads-data-layer\warehouse.duckdb')

print("=== BY RULE_OR_FLAG ===")
rows = conn.execute("""
    SELECT rule_or_flag, COUNT(*) as count
    FROM rules
    WHERE client_config = 'client_christopher_hoole'
    GROUP BY rule_or_flag
    ORDER BY rule_or_flag
""").fetchall()
for r in rows:
    print(f"  {r[0]}: {r[1]}")

print("\n=== BY TYPE ===")
rows = conn.execute("""
    SELECT rule_or_flag, type, COUNT(*) as count
    FROM rules
    WHERE client_config = 'client_christopher_hoole'
    GROUP BY rule_or_flag, type
    ORDER BY rule_or_flag, type
""").fetchall()
for r in rows:
    print(f"  {r[0]} / {r[1]}: {r[2]}")

print("\n=== ENABLED vs DISABLED ===")
rows = conn.execute("""
    SELECT rule_or_flag, enabled, COUNT(*) as count
    FROM rules
    WHERE client_config = 'client_christopher_hoole'
    GROUP BY rule_or_flag, enabled
    ORDER BY rule_or_flag, enabled
""").fetchall()
for r in rows:
    print(f"  {r[0]} enabled={r[1]}: {r[2]}")

print("\n=== TOTAL ===")
row = conn.execute("SELECT COUNT(*) FROM rules WHERE client_config = 'client_christopher_hoole'").fetchone()
print(f"  Total rows: {row[0]}")
