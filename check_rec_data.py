"""
Diagnostic: Check what data recommendations/cards endpoint returns
Checks plain_english, conditions, rule_type, rule_or_flag per entity type
"""
import duckdb
import json

conn = duckdb.connect('warehouse.duckdb')
conn.execute("ATTACH 'warehouse_readonly.duckdb' AS ro (READ_ONLY)")

print("=" * 70)
print("RECOMMENDATIONS DATA DIAGNOSTIC")
print("=" * 70)

# Check recommendations table columns
print("\n--- Recommendations table columns ---")
cols = conn.execute("PRAGMA table_info('recommendations')").fetchall()
for c in cols:
    print(f"  {c[1]} ({c[2]})")

# Sample one rec per entity type
print("\n--- Sample recommendation per entity type ---")
entity_types = ['campaign', 'keyword', 'ad', 'shopping_product', 'ad_group']
for et in entity_types:
    row = conn.execute("""
        SELECT r.entity_type, r.rule_id, r.entity_name,
               ru.plain_english, ru.rule_or_flag, ru.action_type,
               ru.conditions, ru.risk_level, ru.cooldown_days
        FROM recommendations r
        LEFT JOIN rules ru ON r.rule_id = CAST(ru.id AS VARCHAR)
        WHERE r.entity_type = ? AND r.status = 'pending'
        LIMIT 1
    """, [et]).fetchone()
    if row:
        print(f"\n  [{et}]")
        print(f"    rule_id:       {row[1]}")
        print(f"    entity_name:   {row[2]}")
        print(f"    plain_english: {row[3]}")
        print(f"    rule_or_flag:  {row[4]}")
        print(f"    action_type:   {row[5]}")
        print(f"    conditions:    {row[6]}")
        print(f"    risk_level:    {row[7]}")
        print(f"    cooldown_days: {row[8]}")
    else:
        print(f"\n  [{et}] — no pending recommendations found")

# Check rule_id format mismatch
print("\n--- Rule ID format check ---")
rec_ids = conn.execute("SELECT DISTINCT rule_id FROM recommendations LIMIT 10").fetchall()
db_ids = conn.execute("SELECT DISTINCT CAST(id AS VARCHAR) FROM rules LIMIT 10").fetchall()
print(f"  Sample rec rule_ids:  {[r[0] for r in rec_ids]}")
print(f"  Sample DB rule ids:   {[r[0] for r in db_ids]}")

# Check join success rate
print("\n--- Join success rate (how many recs match a rule) ---")
total = conn.execute("SELECT COUNT(*) FROM recommendations WHERE status='pending'").fetchone()[0]
matched = conn.execute("""
    SELECT COUNT(*) FROM recommendations r
    JOIN rules ru ON r.rule_id = CAST(ru.id AS VARCHAR)
    WHERE r.status = 'pending'
""").fetchone()[0]
print(f"  Total pending recs:  {total}")
print(f"  Matched to rules:    {matched}")
print(f"  Unmatched:           {total - matched}")

# Check unmatched rule_ids
print("\n--- Unmatched rule_ids (first 10) ---")
unmatched = conn.execute("""
    SELECT DISTINCT r.rule_id, r.entity_type
    FROM recommendations r
    LEFT JOIN rules ru ON r.rule_id = CAST(ru.id AS VARCHAR)
    WHERE r.status = 'pending' AND ru.id IS NULL
    LIMIT 10
""").fetchall()
for row in unmatched:
    print(f"  rule_id={row[0]}  entity_type={row[1]}")

conn.close()
print("\n✅ Diagnostic complete.")
