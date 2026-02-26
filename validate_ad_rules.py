import json

# Load rules
data = json.load(open('act_autopilot/rules_config.json'))
ad_rules = [r for r in data if r['rule_type'] == 'ad']

print(f"Total ad rules: {len(ad_rules)}")
print("\n" + "="*70)
print("CONSTITUTION COMPLIANCE CHECK - AD RULES")
print("="*70)

all_pass = True

for rule in ad_rules:
    print(f"\n{rule['rule_id']} - {rule['name']}")
    print("-" * 70)
    
    # Check cooldown_days
    cooldown_pass = rule['cooldown_days'] >= 7
    print(f"  Cooldown: {rule['cooldown_days']} days (required ≥7) - {'✅ PASS' if cooldown_pass else '❌ FAIL'}")
    if not cooldown_pass:
        all_pass = False
    
    # Check monitoring_days
    monitoring_pass = rule['monitoring_days'] >= 7
    print(f"  Monitoring: {rule['monitoring_days']} days (required ≥7) - {'✅ PASS' if monitoring_pass else '❌ FAIL'}")
    if not monitoring_pass:
        all_pass = False
    
    # Check action_magnitude (should be null for pause/flag)
    magnitude_pass = rule['action_magnitude'] is None
    print(f"  Action magnitude: {rule['action_magnitude']} (pause/flag = null) - {'✅ PASS' if magnitude_pass else '❌ FAIL'}")
    if not magnitude_pass:
        all_pass = False
    
    # Check risk_level
    risk_pass = rule['risk_level'] in ['low', 'medium', 'high']
    print(f"  Risk level: {rule['risk_level']} (valid) - {'✅ PASS' if risk_pass else '❌ FAIL'}")
    if not risk_pass:
        all_pass = False
    
    # Check enabled
    enabled_pass = rule['enabled'] is True
    print(f"  Enabled: {rule['enabled']} - {'✅ PASS' if enabled_pass else '❌ FAIL'}")
    if not enabled_pass:
        all_pass = False
    
    # Check all 24 fields present
    required_fields = [
        'rule_id', 'rule_type', 'rule_number', 'display_name', 'name',
        'scope', 'campaign_id', 'condition_metric', 'condition_operator',
        'condition_value', 'condition_unit', 'condition_2_metric',
        'condition_2_operator', 'condition_2_value', 'condition_2_unit',
        'action_direction', 'action_magnitude', 'risk_level',
        'cooldown_days', 'monitoring_days', 'monitoring_minutes',
        'enabled', 'created_at', 'updated_at'
    ]
    fields_pass = all(field in rule for field in required_fields)
    print(f"  All 24 fields: {'✅ PASS' if fields_pass else '❌ FAIL'}")
    if not fields_pass:
        all_pass = False

print("\n" + "="*70)
if all_pass:
    print("✅ ALL AD RULES CONSTITUTION COMPLIANT")
else:
    print("❌ SOME AD RULES FAILED CONSTITUTION COMPLIANCE")
print("="*70)
