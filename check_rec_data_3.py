"""
Deep diagnostic part 2 — fix crash and get remaining sections
"""
import duckdb
import json
from pathlib import Path

conn = duckdb.connect('warehouse.duckdb')
conn.execute("ATTACH 'warehouse_readonly.duckdb' AS ro (READ_ONLY)")

print("=" * 70)
print("DEEP DIAGNOSTIC PART 2")
print("=" * 70)

# 1. Rules table — all rows including flags (handle NULLs safely)
print("\n--- Rules table — flags (non-campaign) ---")
rows = conn.execute("""
    SELECT id, COALESCE(entity_type,'NULL'), COALESCE(action_type,'NULL'),
           COALESCE(rule_or_flag,'NULL'),
           plain_english IS NOT NULL as has_pe,
           name
    FROM rules
    WHERE is_template = FALSE AND entity_type != 'campaign'
    ORDER BY id
""").fetchall()
if rows:
    for r in rows:
        print(f"  id={r[0]:<4} entity={r[1]:<12} action={r[2]:<25} rf={r[3]:<5} pe={r[4]}  {r[5]}")
else:
    print("  No non-campaign rules in DB rules table")

# 2. rules_config.json — non-campaign rules
print("\n--- rules_config.json non-campaign rules ---")
config_path = Path('act_autopilot/rules_config.json')
if config_path.exists():
    config = json.loads(config_path.read_text())
    rules = config.get('rules', [])
    non_campaign = [r for r in rules if r.get('entity_type') != 'campaign']
    print(f"  Total non-campaign rules in JSON: {len(non_campaign)}")
    for r in non_campaign[:10]:
        has_pe = bool(r.get('plain_english', '').strip()) if r.get('plain_english') else False
        print(f"  id={str(r.get('id','')):<15} entity={str(r.get('entity_type','')):<12} pe={has_pe}  name={r.get('name','')[:50]}")
else:
    print("  rules_config.json not found")

# 3. Prefix strip test
print("\n--- Prefix strip: can we match rec rule_ids to rules table? ---")
test_cases = [
    'db_campaign_2', 'db_campaign_5', 'keyword_5', 'ad_1', 'ad_group_3', 'shopping_2'
]
for rule_id in test_cases:
    for prefix in ['db_campaign_', 'keyword_', 'ad_group_', 'ad_', 'shopping_']:
        if rule_id.startswith(prefix):
            numeric = rule_id[len(prefix):]
            match = conn.execute(
                "SELECT id, name FROM rules WHERE CAST(id AS VARCHAR) = ? LIMIT 1",
                [numeric]
            ).fetchone()
            print(f"  {rule_id:<25} → strip → '{numeric}' → match: {match}")
            break

# 4. What does trigger_summary look like - is it usable as conditions?
print("\n--- trigger_summary samples per entity type ---")
for et in ['campaign', 'keyword', 'ad', 'ad_group']:
    row = conn.execute("""
        SELECT entity_type, rule_id, trigger_summary, action_direction, confidence
        FROM recommendations
        WHERE status = 'pending' AND entity_type = ?
        LIMIT 1
    """, [et]).fetchone()
    if row:
        print(f"\n  [{row[0]}] rule_id={row[1]}")
        print(f"    trigger_summary: {row[2]}")
        print(f"    action_dir:      {row[3]}")
        print(f"    confidence:      {row[4]}")

# 5. What rule_type column contains in recommendations table
print("\n--- rule_type column in recommendations table ---")
rows = conn.execute("""
    SELECT entity_type, rule_type, COUNT(*) as cnt
    FROM recommendations
    WHERE status = 'pending'
    GROUP BY entity_type, rule_type
    ORDER BY entity_type, cnt DESC
""").fetchall()
for r in rows:
    print(f"  entity={r[0]:<15} rule_type={str(r[1]):<20} count={r[2]}")

conn.close()
print("\n✅ Part 2 complete.")
