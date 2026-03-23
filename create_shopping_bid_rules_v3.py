import duckdb
import json
from datetime import datetime

conn = duckdb.connect('warehouse.duckdb')

# Get the maximum current ID
max_id = conn.execute("SELECT COALESCE(MAX(id), 0) FROM rules").fetchone()[0]
print(f"\nCurrent max rule ID: {max_id}")
print(f"New rules will start at ID: {max_id + 1}\n")

# The 8 Bid rules to create
rules = [
    {
        "name": "Increase Target ROAS - High Performance",
        "type": "bid",
        "action_type": "increase_target_roas",
        "conditions": [
            {"metric": "roas_7d", "op": "gte", "value": 4.5, "ref": "absolute"},
            {"metric": "conversions_7d", "op": "gte", "value": 10, "ref": "absolute"}
        ],
        "action_magnitude": 10.0,
        "cooldown_days": 7,
        "risk_level": "low",
        "plain_english": "Increase Target ROAS by 10% when ROAS (7d) >= 4.5 and Conversions >= 10"
    },
    {
        "name": "Decrease Target ROAS - IS Lost to Rank",
        "type": "bid",
        "action_type": "decrease_target_roas",
        "conditions": [
            {"metric": "search_impression_share_7d", "op": "lt", "value": 0.4, "ref": "absolute"},
            {"metric": "search_rank_lost_impression_share_7d", "op": "gt", "value": 0.2, "ref": "absolute"}
        ],
        "action_magnitude": 10.0,
        "cooldown_days": 7,
        "risk_level": "medium",
        "plain_english": "Decrease Target ROAS by 10% when Search IS < 0.4 and Search Rank Lost IS > 0.2"
    },
    {
        "name": "Decrease Target ROAS - Low Search IS",
        "type": "bid",
        "action_type": "decrease_target_roas",
        "conditions": [
            {"metric": "search_impression_share_7d", "op": "lt", "value": 0.3, "ref": "absolute"},
            {"metric": "roas_7d", "op": "gt", "value": 3.0, "ref": "absolute"}
        ],
        "action_magnitude": 15.0,
        "cooldown_days": 7,
        "risk_level": "medium",
        "plain_english": "Decrease Target ROAS by 15% when Search IS < 0.3 and ROAS (7d) > 3.0"
    },
    {
        "name": "Increase Target ROAS - Stable High Performer",
        "type": "bid",
        "action_type": "increase_target_roas",
        "conditions": [
            {"metric": "roas_7d", "op": "gte", "value": 4.0, "ref": "absolute"},
            {"metric": "conversions_7d", "op": "gte", "value": 15, "ref": "absolute"},
            {"metric": "search_impression_share_7d", "op": "gt", "value": 0.6, "ref": "absolute"}
        ],
        "action_magnitude": 5.0,
        "cooldown_days": 14,
        "risk_level": "low",
        "plain_english": "Increase Target ROAS by 5% when ROAS >= 4.0, Conversions >= 15, and Search IS > 0.6"
    },
    {
        "name": "Increase Max CPC - IS Lost to Rank",
        "type": "bid",
        "action_type": "increase_max_cpc",
        "conditions": [
            {"metric": "search_impression_share_7d", "op": "lt", "value": 0.4, "ref": "absolute"},
            {"metric": "search_rank_lost_impression_share_7d", "op": "gt", "value": 0.2, "ref": "absolute"}
        ],
        "action_magnitude": 15.0,
        "cooldown_days": 7,
        "risk_level": "medium",
        "plain_english": "Increase Max CPC by 15% when Search IS < 0.4 and Search Rank Lost IS > 0.2"
    },
    {
        "name": "Increase Max CPC - Low Search IS with Good ROAS",
        "type": "bid",
        "action_type": "increase_max_cpc",
        "conditions": [
            {"metric": "search_impression_share_7d", "op": "lt", "value": 0.3, "ref": "absolute"},
            {"metric": "roas_7d", "op": "gt", "value": 3.0, "ref": "absolute"}
        ],
        "action_magnitude": 20.0,
        "cooldown_days": 7,
        "risk_level": "medium",
        "plain_english": "Increase Max CPC by 20% when Search IS < 0.3 and ROAS (7d) > 3.0"
    },
    {
        "name": "Decrease Max CPC - High CPC Low CTR",
        "type": "bid",
        "action_type": "decrease_max_cpc",
        "conditions": [
            {"metric": "cpc_7d", "op": "gt", "value": 5.0, "ref": "absolute"},
            {"metric": "ctr_7d", "op": "lt", "value": 0.01, "ref": "absolute"}
        ],
        "action_magnitude": 20.0,
        "cooldown_days": 7,
        "risk_level": "low",
        "plain_english": "Decrease Max CPC by 20% when CPC (7d) > £5.00 and CTR < 1%"
    },
    {
        "name": "Decrease Max CPC - Poor ROAS",
        "type": "bid",
        "action_type": "decrease_max_cpc",
        "conditions": [
            {"metric": "roas_7d", "op": "lt", "value": 2.0, "ref": "absolute"},
            {"metric": "conversions_7d", "op": "gte", "value": 10, "ref": "absolute"}
        ],
        "action_magnitude": 15.0,
        "cooldown_days": 7,
        "risk_level": "medium",
        "plain_english": "Decrease Max CPC by 15% when ROAS (7d) < 2.0 and Conversions >= 10"
    }
]

print("=== CREATING 8 SHOPPING BID RULES ===\n")

created_ids = []
next_id = max_id + 1

for rule in rules:
    # Insert rule with explicit ID
    conn.execute("""
        INSERT INTO rules (
            id, client_config, entity_type, name, rule_or_flag, type,
            campaign_type_lock, entity_scope, conditions, action_type,
            action_magnitude, cooldown_days, risk_level, enabled,
            plain_english, is_template, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        next_id,
        'client_christopher_hoole',
        'shopping',
        rule["name"],
        'rule',
        rule["type"],
        None,  # campaign_type_lock
        json.dumps({"scope": "all"}),
        json.dumps(rule["conditions"]),
        rule["action_type"],
        rule["action_magnitude"],
        rule["cooldown_days"],
        rule["risk_level"],
        True,  # enabled
        rule["plain_english"],
        False,  # is_template
        datetime.now(),
        datetime.now()
    ])
    
    created_ids.append(next_id)
    print(f"✅ Created: {rule['name']} (ID: {next_id})")
    next_id += 1

print(f"\n✅ SUCCESS: Created {len(created_ids)} Bid rules")
print(f"IDs: {created_ids}")

# Verify final count
counts = conn.execute("""
    SELECT type, COUNT(*) as count
    FROM rules
    WHERE entity_type='shopping' AND is_template=FALSE AND rule_or_flag='rule'
    GROUP BY type
    ORDER BY type
""").fetchall()

print("\n=== FINAL SHOPPING RULES COUNT ===")
total = 0
for row in counts:
    rule_type = row[0]
    count = row[1]
    total += count
    print(f"{rule_type}: {count}")

print(f"\nTOTAL SHOPPING RULES: {total}")

conn.close()

print("\n✅ DONE - Restart Flask and check Shopping > Rules tab")
print("Expected: Budget (3) + Status (3) + Bid (8) = 14 rules total")
