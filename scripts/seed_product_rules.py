import duckdb
import json


def seed_product_rules():
    conn = duckdb.connect('warehouse.duckdb')

    # Check for existing product rules
    existing = conn.execute("SELECT COUNT(*) FROM rules WHERE entity_type='product'").fetchone()[0]
    if existing > 0:
        print(f"Found {existing} existing product rules. Deleting before re-seeding...")
        conn.execute("DELETE FROM rules WHERE entity_type='product'")
        conn.commit()

    # Get next ID
    next_id = conn.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM rules").fetchone()[0]

    rules = [
        # ── FEED QUALITY RULES (1) ─────────────────────────────────────
        {
            'name': 'Pause: Out of Stock 7+ Days',
            'rule_or_flag': 'rule',
            'type': 'feed_quality',
            'conditions': [
                {'metric': 'stock_out_days_w30', 'op': 'gte', 'value': 7, 'ref': 'absolute'},
            ],
            'action_type': 'pause',
            'action_magnitude': None,
            'cooldown_days': 14,
            'risk_level': 'medium',
            'plain_english': 'Pause product when out of stock for 7+ days',
        },

        # ── PERFORMANCE RULES (2-7) ───────────────────────────────────
        {
            'name': 'Pause: Low ROAS (7d)',
            'rule_or_flag': 'rule',
            'type': 'performance',
            'conditions': [
                {'metric': 'roas_w7', 'op': 'lt', 'value': 2.0, 'ref': 'absolute'},
            ],
            'action_type': 'pause',
            'action_magnitude': None,
            'cooldown_days': 14,
            'risk_level': 'medium',
            'plain_english': 'Pause product when ROAS (7d) < 2.0',
        },
        {
            'name': 'Pause: High CPA (7d)',
            'rule_or_flag': 'rule',
            'type': 'performance',
            'conditions': [
                {'metric': 'cpa_w7', 'op': 'gt', 'value': 50.0, 'ref': 'absolute'},
            ],
            'action_type': 'pause',
            'action_magnitude': None,
            'cooldown_days': 14,
            'risk_level': 'medium',
            'plain_english': 'Pause product when CPA (7d) > 50',
        },
        {
            'name': 'Pause: Low CTR (7d)',
            'rule_or_flag': 'rule',
            'type': 'performance',
            'conditions': [
                {'metric': 'ctr_w7', 'op': 'lt', 'value': 0.01, 'ref': 'absolute'},
            ],
            'action_type': 'pause',
            'action_magnitude': None,
            'cooldown_days': 14,
            'risk_level': 'medium',
            'plain_english': 'Pause product when CTR (7d) < 1%',
        },
        {
            'name': 'Enable: Good ROAS When Paused',
            'rule_or_flag': 'rule',
            'type': 'performance',
            'conditions': [
                {'metric': 'roas_w7', 'op': 'gt', 'value': 3.0, 'ref': 'absolute'},
            ],
            'action_type': 'enable',
            'action_magnitude': None,
            'cooldown_days': 14,
            'risk_level': 'low',
            'plain_english': 'Enable product when ROAS (7d) > 3.0',
        },
        {
            'name': 'Increase Bid: High ROAS (7d)',
            'rule_or_flag': 'rule',
            'type': 'performance',
            'conditions': [
                {'metric': 'roas_w7', 'op': 'gt', 'value': 5.0, 'ref': 'absolute'},
            ],
            'action_type': 'increase_bid',
            'action_magnitude': 15,
            'cooldown_days': 14,
            'risk_level': 'low',
            'plain_english': 'Increase bid by 15% when ROAS (7d) > 5.0',
        },
        {
            'name': 'Decrease Bid: High CPA (7d)',
            'rule_or_flag': 'rule',
            'type': 'performance',
            'conditions': [
                {'metric': 'cpa_w7', 'op': 'gt', 'value': 40.0, 'ref': 'absolute'},
            ],
            'action_type': 'decrease_bid',
            'action_magnitude': 10,
            'cooldown_days': 14,
            'risk_level': 'low',
            'plain_english': 'Decrease bid by 10% when CPA (7d) > 40',
        },

        # ── LIFECYCLE RULES (8) ───────────────────────────────────────
        {
            'name': 'Pause: New Product High Spend No Conv',
            'rule_or_flag': 'rule',
            'type': 'lifecycle',
            'conditions': [
                {'metric': 'new_product_flag', 'op': 'eq', 'value': True, 'ref': 'absolute'},
                {'metric': 'cost_micros_w7_sum', 'op': 'gt', 'value': 50000000, 'ref': 'absolute'},
                {'metric': 'conversions_w7_sum', 'op': 'eq', 'value': 0, 'ref': 'absolute'},
            ],
            'action_type': 'pause',
            'action_magnitude': None,
            'cooldown_days': 14,
            'risk_level': 'medium',
            'plain_english': 'Pause new product with high spend and zero conversions',
        },

        # ── STOCK RULES (9-10) ────────────────────────────────────────
        {
            'name': 'Pause: Out of Stock Still Spending',
            'rule_or_flag': 'rule',
            'type': 'stock',
            'conditions': [
                {'metric': 'stock_out_flag', 'op': 'eq', 'value': True, 'ref': 'absolute'},
                {'metric': 'cost_micros_w7_sum', 'op': 'gt', 'value': 10000000, 'ref': 'absolute'},
            ],
            'action_type': 'pause',
            'action_magnitude': None,
            'cooldown_days': 14,
            'risk_level': 'high',
            'plain_english': 'Pause product that is out of stock but still spending',
        },
        {
            'name': 'Pause: High Cost Out of Stock',
            'rule_or_flag': 'rule',
            'type': 'stock',
            'conditions': [
                {'metric': 'stock_out_flag', 'op': 'eq', 'value': True, 'ref': 'absolute'},
                {'metric': 'cost_micros_w14_sum', 'op': 'gt', 'value': 100000000, 'ref': 'absolute'},
            ],
            'action_type': 'pause',
            'action_magnitude': None,
            'cooldown_days': 14,
            'risk_level': 'high',
            'plain_english': 'Pause high-cost product that is out of stock',
        },

        # ── FEED QUALITY FLAGS (11-13) ────────────────────────────────
        {
            'name': 'Flag: Price Mismatch',
            'rule_or_flag': 'flag',
            'type': 'feed_quality',
            'conditions': [
                {'metric': 'has_price_mismatch', 'op': 'eq', 'value': True, 'ref': 'absolute'},
            ],
            'action_type': None,
            'action_magnitude': None,
            'cooldown_days': 7,
            'risk_level': 'medium',
            'plain_english': 'Price mismatch detected between feed and landing page',
        },
        {
            'name': 'Flag: Product Disapproval',
            'rule_or_flag': 'flag',
            'type': 'feed_quality',
            'conditions': [
                {'metric': 'has_disapproval', 'op': 'eq', 'value': True, 'ref': 'absolute'},
            ],
            'action_type': None,
            'action_magnitude': None,
            'cooldown_days': 7,
            'risk_level': 'high',
            'plain_english': 'Product has been disapproved by Google',
        },
        {
            'name': 'Flag: Low Feed Quality',
            'rule_or_flag': 'flag',
            'type': 'feed_quality',
            'conditions': [
                {'metric': 'feed_quality_score', 'op': 'lt', 'value': 0.5, 'ref': 'absolute'},
            ],
            'action_type': None,
            'action_magnitude': None,
            'cooldown_days': 7,
            'risk_level': 'medium',
            'plain_english': 'Feed quality score below 50%',
        },

        # ── LIFECYCLE FLAGS (14-16) ───────────────────────────────────
        {
            'name': 'Flag: New Product Low Conversions',
            'rule_or_flag': 'flag',
            'type': 'lifecycle',
            'conditions': [
                {'metric': 'new_product_flag', 'op': 'eq', 'value': True, 'ref': 'absolute'},
                {'metric': 'conversions_w7_sum', 'op': 'lt', 'value': 2, 'ref': 'absolute'},
            ],
            'action_type': None,
            'action_magnitude': None,
            'cooldown_days': 7,
            'risk_level': 'low',
            'plain_english': 'New product with fewer than 2 conversions this week',
        },
        {
            'name': 'Flag: Mature Product Declining ROAS',
            'rule_or_flag': 'flag',
            'type': 'lifecycle',
            'conditions': [
                {'metric': 'days_live', 'op': 'gt', 'value': 30, 'ref': 'absolute'},
                {'metric': 'roas_w7', 'op': 'lt', 'value': 3.0, 'ref': 'absolute'},
            ],
            'action_type': None,
            'action_magnitude': None,
            'cooldown_days': 7,
            'risk_level': 'medium',
            'plain_english': 'Mature product with ROAS below 3.0',
        },
        {
            'name': 'Flag: Low Data High Spend',
            'rule_or_flag': 'flag',
            'type': 'lifecycle',
            'conditions': [
                {'metric': 'low_data_flag', 'op': 'eq', 'value': True, 'ref': 'absolute'},
                {'metric': 'cost_micros_w7_sum', 'op': 'gt', 'value': 100000000, 'ref': 'absolute'},
            ],
            'action_type': None,
            'action_magnitude': None,
            'cooldown_days': 7,
            'risk_level': 'medium',
            'plain_english': 'Product has low data but significant spend',
        },

        # ── STOCK FLAGS (17-18) ───────────────────────────────────────
        {
            'name': 'Flag: Going Out of Stock',
            'rule_or_flag': 'flag',
            'type': 'stock',
            'conditions': [
                {'metric': 'stock_out_days_w30', 'op': 'gt', 'value': 3, 'ref': 'absolute'},
                {'metric': 'stock_out_days_w30', 'op': 'lt', 'value': 7, 'ref': 'absolute'},
            ],
            'action_type': None,
            'action_magnitude': None,
            'cooldown_days': 7,
            'risk_level': 'medium',
            'plain_english': 'Product showing signs of going out of stock (3-7 days)',
        },
        {
            'name': 'Flag: Preorder No Conversions',
            'rule_or_flag': 'flag',
            'type': 'stock',
            'conditions': [
                {'metric': 'availability', 'op': 'eq', 'value': 'PREORDER', 'ref': 'absolute'},
                {'metric': 'conversions_w14_sum', 'op': 'eq', 'value': 0, 'ref': 'absolute'},
            ],
            'action_type': None,
            'action_magnitude': None,
            'cooldown_days': 7,
            'risk_level': 'low',
            'plain_english': 'Preorder product with zero conversions in 14 days',
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
            ) VALUES (?, ?, 'product', ?, ?, ?, NULL, '{"scope":"all"}', ?, ?, ?, ?, ?, TRUE, FALSE, ?)
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

    count = conn.execute("SELECT COUNT(*) FROM rules WHERE entity_type='product'").fetchone()[0]
    print(f"Seeded {count} product rules and flags")

    # Show breakdown
    breakdown = conn.execute("""
        SELECT rule_or_flag, type, COUNT(*)
        FROM rules WHERE entity_type='product'
        GROUP BY rule_or_flag, type
        ORDER BY rule_or_flag, type
    """).fetchall()
    for row in breakdown:
        print(f"  {row[0]} / {row[1]}: {row[2]}")

    conn.close()


if __name__ == '__main__':
    seed_product_rules()
