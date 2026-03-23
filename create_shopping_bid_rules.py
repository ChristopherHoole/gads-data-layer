import duckdb
import json
from datetime import datetime

conn = duckdb.connect('warehouse.duckdb')

# The 8 Bid rules to create
rules = [
    {
        "name": "Increase Target ROAS - High Performance",
        "entity_type": "shopping",
        "action_type": "increase_target_roas",
        "description": "Increase Target ROAS by 10% when ROAS is strong with sufficient conversions",
        "enabled": True,
        "cooldown_days": 7,
        "risk_level": "low",
        "conditions": json.dumps([
            {"metric": "roas_7d", "op": "gte", "value": 4.5, "ref": None},
            {"metric": "conversions_7d", "op": "gte", "value": 10, "ref": None}
        ]),
        "change_magnitude": 0.10,
        "scope_type": "all",
        "campaign_type_lock": None
    },
    {
        "name": "Decrease Target ROAS - IS Lost to Rank",
        "entity_type": "shopping",
        "action_type": "decrease_target_roas",
        "description": "Decrease Target ROAS by 10% when losing impression share to rank",
        "enabled": True,
        "cooldown_days": 7,
        "risk_level": "medium",
        "conditions": json.dumps([
            {"metric": "search_impression_share_7d", "op": "lt", "value": 0.4, "ref": None},
            {"metric": "search_rank_lost_impression_share_7d", "op": "gt", "value": 0.2, "ref": None}
        ]),
        "change_magnitude": 0.10,
        "scope_type": "all",
        "campaign_type_lock": None
    },
    {
        "name": "Decrease Target ROAS - Low Search IS",
        "entity_type": "shopping",
        "action_type": "decrease_target_roas",
        "description": "Decrease Target ROAS by 15% when search IS is low but ROAS is good",
        "enabled": True,
        "cooldown_days": 7,
        "risk_level": "medium",
        "conditions": json.dumps([
            {"metric": "search_impression_share_7d", "op": "lt", "value": 0.3, "ref": None},
            {"metric": "roas_7d", "op": "gt", "value": 3.0, "ref": None}
        ]),
        "change_magnitude": 0.15,
        "scope_type": "all",
        "campaign_type_lock": None
    },
    {
        "name": "Increase Target ROAS - Stable High Performer",
        "entity_type": "shopping",
        "action_type": "increase_target_roas",
        "description": "Increase Target ROAS by 5% for stable high performers with good impression share",
        "enabled": True,
        "cooldown_days": 14,
        "risk_level": "low",
        "conditions": json.dumps([
            {"metric": "roas_7d", "op": "gte", "value": 4.0, "ref": None},
            {"metric": "conversions_7d", "op": "gte", "value": 15, "ref": None},
            {"metric": "search_impression_share_7d", "op": "gt", "value": 0.6, "ref": None}
        ]),
        "change_magnitude": 0.05,
        "scope_type": "all",
        "campaign_type_lock": None
    },
    {
        "name": "Increase Max CPC - IS Lost to Rank",
        "entity_type": "shopping",
        "action_type": "increase_max_cpc",
        "description": "Increase Max CPC by 15% when losing impression share to rank",
        "enabled": True,
        "cooldown_days": 7,
        "risk_level": "medium",
        "conditions": json.dumps([
            {"metric": "search_impression_share_7d", "op": "lt", "value": 0.4, "ref": None},
            {"metric": "search_rank_lost_impression_share_7d", "op": "gt", "value": 0.2, "ref": None}
        ]),
        "change_magnitude": 0.15,
        "scope_type": "all",
        "campaign_type_lock": None
    },
    {
        "name": "Increase Max CPC - Low Search IS with Good ROAS",
        "entity_type": "shopping",
        "action_type": "increase_max_cpc",
        "description": "Increase Max CPC by 20% when search IS is low but profitable",
        "enabled": True,
        "cooldown_days": 7,
        "risk_level": "medium",
        "conditions": json.dumps([
            {"metric": "search_impression_share_7d", "op": "lt", "value": 0.3, "ref": None},
            {"metric": "roas_7d", "op": "gt", "value": 3.0, "ref": None}
        ]),
        "change_magnitude": 0.20,
        "scope_type": "all",
        "campaign_type_lock": None
    },
    {
        "name": "Decrease Max CPC - High CPC Low CTR",
        "entity_type": "shopping",
        "action_type": "decrease_max_cpc",
        "description": "Decrease Max CPC by 20% when CPC is high and CTR is low",
        "enabled": True,
        "cooldown_days": 7,
        "risk_level": "low",
        "conditions": json.dumps([
            {"metric": "cpc_7d", "op": "gt", "value": 5.0, "ref": None},
            {"metric": "ctr_7d", "op": "lt", "value": 0.01, "ref": None}
        ]),
        "change_magnitude": 0.20,
        "scope_type": "all",
        "campaign_type_lock": None
    },
    {
        "name": "Decrease Max CPC - Poor ROAS",
        "entity_type": "shopping",
        "action_type": "decrease_max_cpc",
        "description": "Decrease Max CPC by 15% when ROAS is poor with sufficient data",
        "enabled": True,
        "cooldown_days": 7,
        "risk_level": "medium",
        "conditions": json.dumps([
            {"metric": "roas_7d", "op": "lt", "value": 2.0, "ref": None},
            {"metric": "conversions_7d", "op": "gte", "value": 10, "ref": None}
        ]),
        "change_magnitude": 0.15,
        "scope_type": "all",
        "campaign_type_lock": None
    }
]

print("\n=== CREATING 8 SHOPPING BID RULES ===\n")

created_ids = []

for rule in rules:
    # Insert rule
    result = conn.execute("""
        INSERT INTO rules (
            name, entity_type, action_type, description, enabled,
            cooldown_days, risk_level, conditions, change_magnitude,
            scope_type, campaign_type_lock, is_template,
            created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        RETURNING id
    """, [
        rule["name"],
        rule["entity_type"],
        rule["action_type"],
        rule["description"],
        rule["enabled"],
        rule["cooldown_days"],
        rule["risk_level"],
        rule["conditions"],
        rule["change_magnitude"],
        rule["scope_type"],
        rule["campaign_type_lock"],
        False,  # is_template
        datetime.now().isoformat(),
        datetime.now().isoformat()
    ]).fetchone()
    
    rule_id = result[0]
    created_ids.append(rule_id)
    print(f"✅ Created: {rule['name']} (ID: {rule_id})")

print(f"\n✅ SUCCESS: Created {len(created_ids)} Bid rules")
print(f"IDs: {created_ids}")

# Verify final count
counts = conn.execute("""
    SELECT action_type, COUNT(*) as count
    FROM rules
    WHERE entity_type='shopping' AND is_template=FALSE
    GROUP BY action_type
    ORDER BY action_type
""").fetchall()

print("\n=== FINAL SHOPPING RULES COUNT ===")
total = 0
for row in counts:
    action = row[0] if row[0] else "flags"
    count = row[1]
    total += count
    print(f"{action}: {count}")

print(f"\nTOTAL SHOPPING RULES: {total}")

conn.close()

print("\n✅ DONE - Run Flask and check Shopping > Rules tab")
