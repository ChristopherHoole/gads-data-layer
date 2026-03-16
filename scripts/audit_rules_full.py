import duckdb
import json

conn = duckdb.connect('warehouse.duckdb')

print('=== RULES — FULL DETAIL ===')
rules = conn.execute(
    "SELECT id, name, campaign_type_lock, conditions, action_type, action_magnitude, "
    "cooldown_days, risk_level, plain_english "
    "FROM rules WHERE is_template = FALSE AND rule_or_flag = 'rule' "
    "ORDER BY id"
).fetchall()

for r in rules:
    id_, name, lock, conditions, action_type, magnitude, cooldown, risk, plain = r
    print(f"\n--- Rule {id_}: {name} ---")
    print(f"  Campaign type lock : {lock}")
    print(f"  Action             : {action_type} | magnitude: {magnitude}%")
    print(f"  Cooldown           : {cooldown}d | Risk: {risk}")
    print(f"  Plain English      : {plain}")
    try:
        conds = json.loads(conditions) if isinstance(conditions, str) else conditions
        for i, c in enumerate(conds, 1):
            print(f"  Condition {i}        : {c}")
    except Exception as e:
        print(f"  Conditions (raw)   : {conditions}")

print()
print('=== FLAGS — FULL DETAIL ===')
flags = conn.execute(
    "SELECT id, name, conditions, cooldown_days, plain_english "
    "FROM rules WHERE is_template = FALSE AND rule_or_flag = 'flag' "
    "ORDER BY id"
).fetchall()

for f in flags:
    id_, name, conditions, cooldown, plain = f
    print(f"\n--- Flag {id_}: {name} ---")
    print(f"  Cooldown      : {cooldown}d")
    print(f"  Plain English : {plain}")
    try:
        conds = json.loads(conditions) if isinstance(conditions, str) else conditions
        for i, c in enumerate(conds, 1):
            print(f"  Condition {i}   : {c}")
    except Exception as e:
        print(f"  Conditions (raw): {conditions}")

conn.close()
