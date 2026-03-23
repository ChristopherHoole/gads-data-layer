import json

# Load rules_config.json
with open('act_autopilot/rules_config.json', 'r') as f:
    data = json.load(f)

# data is a list of rules directly
shopping_rules = [r for r in data if r.get('entity_type') == 'shopping']

print(f"\n=== SHOPPING RULES IN rules_config.json ===")
print(f"Total: {len(shopping_rules)}\n")

# Group by action_type
from collections import defaultdict
by_type = defaultdict(list)
for rule in shopping_rules:
    action_type = rule.get('action_type', 'unknown')
    by_type[action_type].append(rule.get('name'))

for action_type, names in sorted(by_type.items()):
    print(f"\n{action_type.upper()}: {len(names)}")
    for i, name in enumerate(names, 1):
        print(f"  {i}. {name}")

print(f"\n=== TOTAL BY TYPE ===")
for action_type, names in sorted(by_type.items()):
    print(f"{action_type}: {len(names)}")
