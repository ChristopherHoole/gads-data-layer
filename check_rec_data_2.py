"""
Deep diagnostic: Understand rule_id format and available data sources
"""
import duckdb
import json
from pathlib import Path

conn = duckdb.connect('warehouse.duckdb')
conn.execute("ATTACH 'warehouse_readonly.duckdb' AS ro (READ_ONLY)")

print("=" * 70)
print("DEEP RECOMMENDATIONS DIAGNOSTIC")
print("=" * 70)

# 1. Show rule_id patterns by entity type
print("\n--- Rule ID patterns by entity type ---")
rows = conn.execute("""
    SELECT entity_type, rule_id, COUNT(*) as cnt
    FROM recommendations
    WHERE status = 'pending'
    GROUP BY entity_type, rule_id
    ORDER BY entity_type, cnt DESC
    LIMIT 20
""").fetchall()
for r in rows:
    print(f"  {r[0]:<20} {r[1]:<25} ({r[2]} recs)")

# 2. Show rules table - what IDs and names exist
print("\n--- Rules table (all rules, id + name) ---")
rows = conn.execute("""
    SELECT id, name, entity_type, action_type, rule_or_flag,
           plain_english IS NOT NULL as has_plain_english
    FROM rules
    WHERE is_template = FALSE
    ORDER BY id
""").fetchall()
for r in rows:
    print(f"  id={r[0]:<4} entity={r[2]:<12} action={r[3]:<25} rf={r[4]:<5} plain_english={r[5]}  name={r[1]}")

# 3. Check rules_config.json for non-campaign rules
print("\n--- rules_config.json non-campaign rules ---")
config_path = Path('act_autopilot/rules_config.json')
if config_path.exists():
    config = json.loads(config_path.read_text())
    rules = config.get('rules', [])
    non_campaign = [r for r in rules if r.get('entity_type') != 'campaign']
    print(f"  Total non-campaign rules in JSON: {len(non_campaign)}")
    for r in non_campaign[:8]:
        print(f"  id={r.get('id'):<15} entity={r.get('entity_type'):<12} plain_english={bool(r.get('plain_english'))}  name={r.get('name','')[:50]}")
else:
    print("  rules_config.json not found")

# 4. What does the recommendations endpoint actually return right now
print("\n--- Sample of what /recommendations/cards returns (trigger_summary) ---")
rows = conn.execute("""
    SELECT entity_type, rule_id, trigger_summary, action_direction, 
           action_magnitude, current_value, proposed_value, confidence
    FROM recommendations
    WHERE status = 'pending'
    GROUP BY entity_type, rule_id, trigger_summary, action_direction,
             action_magnitude, current_value, proposed_value, confidence
    LIMIT 8
""").fetchall()
for r in rows:
    print(f"  [{r[0]}] rule={r[1]} dir={r[3]} mag={r[4]} trigger={str(r[2])[:60]}")

# 5. Check if rule_id format strips prefix to get integer
print("\n--- Can we extract integer from rule_id to match rules table? ---")
test_cases = [
    ('db_campaign_2', 'campaign'),
    ('keyword_5', 'keyword'),
    ('ad_1', 'ad'),
    ('ad_group_3', 'ad_group'),
    ('shopping_2', 'shopping'),
]
for rule_id, entity in test_cases:
    # Try stripping known prefixes
    for prefix in ['db_campaign_', 'keyword_', 'ad_group_', 'ad_', 'shopping_']:
        if rule_id.startswith(prefix):
            numeric = rule_id[len(prefix):]
            # Check if this matches a rule
            match = conn.execute(
                "SELECT id, name FROM rules WHERE CAST(id AS VARCHAR) = ? LIMIT 1",
                [numeric]
            ).fetchone()
            print(f"  {rule_id} → strip '{prefix}' → '{numeric}' → rule match: {match}")
            break

conn.close()
print("\n✅ Deep diagnostic complete.")
