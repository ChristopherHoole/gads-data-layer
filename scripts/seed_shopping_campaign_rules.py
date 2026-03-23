"""
Seed Shopping campaign rules into the database rules table.
Migrates the 14 rules from rules_config.json into the DB with entity_type='shopping'.
"""
import duckdb
import json


def seed_shopping_campaign_rules():
    conn = duckdb.connect('warehouse.duckdb')

    # Check/delete existing
    existing = conn.execute("SELECT COUNT(*) FROM rules WHERE entity_type='shopping'").fetchone()[0]
    if existing > 0:
        print(f"Found {existing} existing shopping rules. Deleting before re-seeding...")
        conn.execute("DELETE FROM rules WHERE entity_type='shopping'")
        conn.commit()

    next_id = conn.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM rules").fetchone()[0]

    rules = [
        # 1. Increase budget - high ROAS
        {
            'name': 'Increase Budget - High ROAS Shopping',
            'rule_or_flag': 'rule',
            'type': 'budget',
            'action_type': 'increase_budget',
            'action_magnitude': 15.0,
            'conditions': [
                {'metric': 'roas_7d', 'op': 'gte', 'value': 4.5, 'ref': 'absolute'},
                {'metric': 'conversions_7d', 'op': 'gte', 'value': 10, 'ref': 'absolute'}
            ],
            'cooldown_days': 7,
            'risk_level': 'low',
            'plain_english': 'Increase budget by 15% when ROAS (7d) >= 4.5 and Conversions >= 10',
        },
        # 2. Decrease budget - low ROAS
        {
            'name': 'Decrease Budget - Low ROAS Shopping',
            'rule_or_flag': 'rule',
            'type': 'budget',
            'action_type': 'decrease_budget',
            'action_magnitude': 20.0,
            'conditions': [
                {'metric': 'roas_7d', 'op': 'lt', 'value': 2.0, 'ref': 'absolute'},
                {'metric': 'conversions_7d', 'op': 'gte', 'value': 10, 'ref': 'absolute'}
            ],
            'cooldown_days': 7,
            'risk_level': 'medium',
            'plain_english': 'Decrease budget by 20% when ROAS (7d) < 2.0 and Conversions >= 10',
        },
        # 3. Pause - zero conversions high spend
        {
            'name': 'Pause - Zero Conversions High Spend',
            'rule_or_flag': 'rule',
            'type': 'status',
            'action_type': 'pause',
            'action_magnitude': None,
            'conditions': [
                {'metric': 'cost_7d', 'op': 'gte', 'value': 200, 'ref': 'absolute'},
                {'metric': 'conversions_7d', 'op': 'eq', 'value': 0, 'ref': 'absolute'}
            ],
            'cooldown_days': 14,
            'risk_level': 'high',
            'plain_english': 'Pause campaign when Cost (7d) >= 200 and zero conversions',
        },
        # 4. Flag - low ROAS
        {
            'name': 'Flag - Low ROAS Performance',
            'rule_or_flag': 'flag',
            'type': 'performance',
            'action_type': None,
            'action_magnitude': None,
            'conditions': [
                {'metric': 'roas_7d', 'op': 'lt', 'value': 2.0, 'ref': 'absolute'},
                {'metric': 'conversions_7d', 'op': 'gte', 'value': 10, 'ref': 'absolute'}
            ],
            'cooldown_days': 7,
            'risk_level': 'medium',
            'plain_english': 'Alert when ROAS (7d) < 2.0 with 10+ conversions',
        },
        # 5. Flag - very low ROAS early warning
        {
            'name': 'Flag - Very Low ROAS Early Warning',
            'rule_or_flag': 'flag',
            'type': 'performance',
            'action_type': None,
            'action_magnitude': None,
            'conditions': [
                {'metric': 'roas_7d', 'op': 'lt', 'value': 1.5, 'ref': 'absolute'},
                {'metric': 'conversions_7d', 'op': 'gte', 'value': 5, 'ref': 'absolute'}
            ],
            'cooldown_days': 7,
            'risk_level': 'high',
            'plain_english': 'Early warning: ROAS (7d) < 1.5 with 5+ conversions',
        },
        # 6. Pause - extremely poor ROAS
        {
            'name': 'Pause - Extremely Poor ROAS',
            'rule_or_flag': 'rule',
            'type': 'status',
            'action_type': 'pause',
            'action_magnitude': None,
            'conditions': [
                {'metric': 'roas_7d', 'op': 'lt', 'value': 1.0, 'ref': 'absolute'},
                {'metric': 'conversions_7d', 'op': 'gte', 'value': 10, 'ref': 'absolute'}
            ],
            'cooldown_days': 14,
            'risk_level': 'high',
            'plain_english': 'Pause campaign when ROAS (7d) < 1.0 with 10+ conversions',
        },
        # 7. Flag - high cost zero conversions
        {
            'name': 'Flag - High Cost Zero Conversions',
            'rule_or_flag': 'flag',
            'type': 'performance',
            'action_type': None,
            'action_magnitude': None,
            'conditions': [
                {'metric': 'cost_7d', 'op': 'gte', 'value': 100, 'ref': 'absolute'},
                {'metric': 'conversions_7d', 'op': 'eq', 'value': 0, 'ref': 'absolute'}
            ],
            'cooldown_days': 7,
            'risk_level': 'medium',
            'plain_english': 'Alert when Cost (7d) >= 100 with zero conversions',
        },
        # 8. Flag - high feed errors
        {
            'name': 'Flag - High Feed Error Count',
            'rule_or_flag': 'flag',
            'type': 'technical',
            'action_type': None,
            'action_magnitude': None,
            'conditions': [
                {'metric': 'feed_error_count', 'op': 'gte', 'value': 20, 'ref': 'absolute'},
                {'metric': 'impressions_7d', 'op': 'gte', 'value': 100, 'ref': 'absolute'}
            ],
            'cooldown_days': 7,
            'risk_level': 'medium',
            'plain_english': 'Alert when feed errors >= 20 with active impressions',
        },
        # 9. Pause - critical feed errors
        {
            'name': 'Pause - Critical Feed Error Count',
            'rule_or_flag': 'rule',
            'type': 'status',
            'action_type': 'pause',
            'action_magnitude': None,
            'conditions': [
                {'metric': 'feed_error_count', 'op': 'gte', 'value': 50, 'ref': 'absolute'},
                {'metric': 'impressions_7d', 'op': 'gte', 'value': 100, 'ref': 'absolute'}
            ],
            'cooldown_days': 14,
            'risk_level': 'high',
            'plain_english': 'Pause campaign when feed errors >= 50 with active impressions',
        },
        # 10. Flag - high out of stock
        {
            'name': 'Flag - High Out of Stock Products',
            'rule_or_flag': 'flag',
            'type': 'technical',
            'action_type': None,
            'action_magnitude': None,
            'conditions': [
                {'metric': 'out_of_stock_product_count', 'op': 'gte', 'value': 5, 'ref': 'absolute'},
                {'metric': 'impressions_7d', 'op': 'gte', 'value': 100, 'ref': 'absolute'}
            ],
            'cooldown_days': 7,
            'risk_level': 'low',
            'plain_english': 'Alert when 5+ products out of stock with active impressions',
        },
        # 11. Flag - low search IS
        {
            'name': 'Flag - Low Search Impression Share',
            'rule_or_flag': 'flag',
            'type': 'performance',
            'action_type': None,
            'action_magnitude': None,
            'conditions': [
                {'metric': 'search_impression_share', 'op': 'lt', 'value': 0.30, 'ref': 'absolute'},
                {'metric': 'impressions_7d', 'op': 'gte', 'value': 1000, 'ref': 'absolute'}
            ],
            'cooldown_days': 7,
            'risk_level': 'low',
            'plain_english': 'Alert when Search IS < 30% with 1000+ impressions',
        },
        # 12. Flag - IS lost to budget
        {
            'name': 'Flag - IS Lost to Budget',
            'rule_or_flag': 'flag',
            'type': 'performance',
            'action_type': None,
            'action_magnitude': None,
            'conditions': [
                {'metric': 'search_impression_share', 'op': 'lt', 'value': 0.30, 'ref': 'absolute'},
                {'metric': 'cost_7d', 'op': 'gte', 'value': 150, 'ref': 'absolute'}
            ],
            'cooldown_days': 7,
            'risk_level': 'medium',
            'plain_english': 'Alert when Search IS < 30% and Cost (7d) >= 150',
        },
        # 13. Increase budget - IS constrained high ROAS
        {
            'name': 'Increase Budget - IS Constrained High ROAS',
            'rule_or_flag': 'rule',
            'type': 'budget',
            'action_type': 'increase_budget',
            'action_magnitude': 15.0,
            'conditions': [
                {'metric': 'search_impression_share', 'op': 'lt', 'value': 0.40, 'ref': 'absolute'},
                {'metric': 'roas_7d', 'op': 'gte', 'value': 3.0, 'ref': 'absolute'}
            ],
            'cooldown_days': 7,
            'risk_level': 'low',
            'plain_english': 'Increase budget by 15% when IS < 40% and ROAS (7d) >= 3.0',
        },
        # 14. Flag - low optimization score
        {
            'name': 'Flag - Low Optimization Score',
            'rule_or_flag': 'flag',
            'type': 'technical',
            'action_type': None,
            'action_magnitude': None,
            'conditions': [
                {'metric': 'optimization_score', 'op': 'lt', 'value': 0.60, 'ref': 'absolute'},
                {'metric': 'impressions_7d', 'op': 'gte', 'value': 1000, 'ref': 'absolute'}
            ],
            'cooldown_days': 7,
            'risk_level': 'low',
            'plain_english': 'Alert when Optimization Score < 60% with 1000+ impressions',
        },
    ]

    for i, rule in enumerate(rules):
        rule_id = next_id + i
        conn.execute("""
            INSERT INTO rules (
                id, client_config, entity_type, name,
                rule_or_flag, type, campaign_type_lock,
                entity_scope, conditions,
                action_type, action_magnitude,
                cooldown_days, risk_level, enabled,
                is_template, plain_english
            ) VALUES (?, ?, 'shopping', ?, ?, ?, NULL, '{"scope":"all"}', ?, ?, ?, ?, ?, TRUE, FALSE, ?)
        """, [
            rule_id,
            'client_christopher_hoole',
            rule['name'],
            rule['rule_or_flag'],
            rule['type'],
            json.dumps(rule['conditions']),
            rule.get('action_type'),
            rule.get('action_magnitude'),
            rule['cooldown_days'],
            rule['risk_level'],
            rule['plain_english'],
        ])

    conn.commit()

    count = conn.execute("SELECT COUNT(*) FROM rules WHERE entity_type='shopping'").fetchone()[0]
    print(f"Seeded {count} shopping campaign rules and flags")

    breakdown = conn.execute("""
        SELECT rule_or_flag, type, COUNT(*)
        FROM rules WHERE entity_type='shopping'
        GROUP BY rule_or_flag, type
        ORDER BY rule_or_flag, type
    """).fetchall()
    for row in breakdown:
        print(f"  {row[0]} / {row[1]}: {row[2]}")

    conn.close()


if __name__ == '__main__':
    seed_shopping_campaign_rules()
