import duckdb
import json


def seed_ad_rules():
    conn = duckdb.connect('warehouse.duckdb')

    # Check for existing ad rules
    existing = conn.execute("SELECT COUNT(*) FROM rules WHERE entity_type='ad'").fetchone()[0]
    if existing > 0:
        print(f"Found {existing} existing ad rules. Deleting before re-seeding...")
        conn.execute("DELETE FROM rules WHERE entity_type='ad'")
        conn.commit()

    # Get next ID
    next_id = conn.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM rules").fetchone()[0]

    rules = [
        # ── STATUS RULES (1-8) ──────────────────────────────────────────
        {
            'name': 'Pause - Poor CTR',
            'rule_or_flag': 'rule',
            'type': 'status',
            'conditions': [
                {'metric': 'ctr_w14_mean', 'op': 'lt', 'value': 0.015, 'ref': 'absolute'},
                {'metric': 'clicks_w14_sum', 'op': 'gte', 'value': 50, 'ref': 'absolute'},
            ],
            'action_type': 'pause',
            'action_magnitude': None,
            'cooldown_days': 30,
            'risk_level': 'medium',
            'plain_english': 'Pause ad when CTR (14d) < 1.5% with 50+ clicks',
        },
        {
            'name': 'Pause - Zero Conversions High Spend',
            'rule_or_flag': 'rule',
            'type': 'status',
            'conditions': [
                {'metric': 'conversions_w30_sum', 'op': 'eq', 'value': 0, 'ref': 'absolute'},
                {'metric': 'cost_w30_sum', 'op': 'gt', 'value': 30, 'ref': 'absolute'},
            ],
            'action_type': 'pause',
            'action_magnitude': None,
            'cooldown_days': 30,
            'risk_level': 'medium',
            'plain_english': 'Pause ad when zero conversions (30d) and Cost > 30',
        },
        {
            'name': 'Pause - Low ROAS',
            'rule_or_flag': 'rule',
            'type': 'status',
            'conditions': [
                {'metric': 'roas_w14_mean', 'op': 'lt', 'value': 1.5, 'ref': 'absolute'},
                {'metric': 'conversions_w14_sum', 'op': 'gte', 'value': 5, 'ref': 'absolute'},
            ],
            'action_type': 'pause',
            'action_magnitude': None,
            'cooldown_days': 30,
            'risk_level': 'medium',
            'plain_english': 'Pause ad when ROAS (14d) < 1.5 with 5+ conversions',
        },
        {
            'name': 'Pause - Poor Ad Strength',
            'rule_or_flag': 'rule',
            'type': 'status',
            'conditions': [
                {'metric': 'ad_strength', 'op': 'in', 'value': ['POOR', 'AVERAGE'], 'ref': 'absolute'},
                {'metric': 'cost_w14_sum', 'op': 'gt', 'value': 20, 'ref': 'absolute'},
            ],
            'action_type': 'pause',
            'action_magnitude': None,
            'cooldown_days': 30,
            'risk_level': 'medium',
            'plain_english': 'Pause ad when Ad Strength is Poor/Average with Cost > 20',
        },
        {
            'name': 'Enable - Ad Strength Improved',
            'rule_or_flag': 'rule',
            'type': 'status',
            'conditions': [
                {'metric': 'ad_strength', 'op': 'in', 'value': ['GOOD', 'EXCELLENT'], 'ref': 'absolute'},
            ],
            'action_type': 'enable',
            'action_magnitude': None,
            'cooldown_days': 14,
            'risk_level': 'low',
            'plain_english': 'Enable ad when Ad Strength is Good or Excellent',
        },
        {
            'name': 'Pause - High CPA',
            'rule_or_flag': 'rule',
            'type': 'status',
            'conditions': [
                {'metric': 'cpa_w14_mean', 'op': 'gt', 'value': 80, 'ref': 'absolute'},
                {'metric': 'conversions_w14_sum', 'op': 'gte', 'value': 3, 'ref': 'absolute'},
            ],
            'action_type': 'pause',
            'action_magnitude': None,
            'cooldown_days': 30,
            'risk_level': 'medium',
            'plain_english': 'Pause ad when CPA (14d) > 80 with 3+ conversions',
        },
        {
            'name': 'Enable - Performance Recovered',
            'rule_or_flag': 'rule',
            'type': 'status',
            'conditions': [
                {'metric': 'roas_w7_mean', 'op': 'gt', 'value': 4.0, 'ref': 'absolute'},
                {'metric': 'conversions_w7_sum', 'op': 'gte', 'value': 3, 'ref': 'absolute'},
            ],
            'action_type': 'enable',
            'action_magnitude': None,
            'cooldown_days': 14,
            'risk_level': 'low',
            'plain_english': 'Enable ad when ROAS (7d) > 4.0 and 3+ conversions',
        },
        {
            'name': 'Pause - CTR Declining Trend',
            'rule_or_flag': 'rule',
            'type': 'status',
            'conditions': [
                {'metric': 'ctr_w7_vs_prev_pct', 'op': 'lt', 'value': -0.40, 'ref': 'absolute'},
                {'metric': 'clicks_w7_sum', 'op': 'gte', 'value': 30, 'ref': 'absolute'},
            ],
            'action_type': 'pause',
            'action_magnitude': None,
            'cooldown_days': 30,
            'risk_level': 'medium',
            'plain_english': 'Pause ad when CTR dropped 40%+ with 30+ clicks',
        },

        # ── PERFORMANCE FLAGS (9-15) ──────────────────────────────────────
        {
            'name': 'CTR Drop - Creative Fatigue',
            'rule_or_flag': 'flag',
            'type': 'performance',
            'conditions': [
                {'metric': 'ctr_w7_vs_prev_pct', 'op': 'lt', 'value': -0.30, 'ref': 'absolute'},
                {'metric': 'clicks_w7_sum', 'op': 'gte', 'value': 30, 'ref': 'absolute'},
            ],
            'action_type': None,
            'action_magnitude': None,
            'cooldown_days': 7,
            'risk_level': 'high',
            'plain_english': 'CTR dropped 30%+ week on week - possible creative fatigue',
        },
        {
            'name': 'ROAS Decline',
            'rule_or_flag': 'flag',
            'type': 'performance',
            'conditions': [
                {'metric': 'roas_w7_vs_prev_pct', 'op': 'lt', 'value': -0.30, 'ref': 'absolute'},
                {'metric': 'conversions_w7_sum', 'op': 'gte', 'value': 3, 'ref': 'absolute'},
            ],
            'action_type': None,
            'action_magnitude': None,
            'cooldown_days': 7,
            'risk_level': 'high',
            'plain_english': 'ROAS declined more than 30% week on week',
        },
        {
            'name': 'CVR Drop',
            'rule_or_flag': 'flag',
            'type': 'performance',
            'conditions': [
                {'metric': 'cvr_w7_vs_prev_pct', 'op': 'lt', 'value': -0.30, 'ref': 'absolute'},
                {'metric': 'conversions_w7_sum', 'op': 'gte', 'value': 3, 'ref': 'absolute'},
            ],
            'action_type': None,
            'action_magnitude': None,
            'cooldown_days': 7,
            'risk_level': 'high',
            'plain_english': 'Conversion rate dropped 30%+ week on week',
        },
        {
            'name': 'Wasted Spend Zero Conversions',
            'rule_or_flag': 'flag',
            'type': 'performance',
            'conditions': [
                {'metric': 'conversions_w30_sum', 'op': 'eq', 'value': 0, 'ref': 'absolute'},
                {'metric': 'cost_w30_sum', 'op': 'gt', 'value': 30, 'ref': 'absolute'},
            ],
            'action_type': None,
            'action_magnitude': None,
            'cooldown_days': 30,
            'risk_level': 'high',
            'plain_english': 'Ad has zero conversions with over 30 in spend (30d)',
        },
        {
            'name': 'Low Impression Share',
            'rule_or_flag': 'flag',
            'type': 'performance',
            'conditions': [
                {'metric': 'search_impression_share', 'op': 'lt', 'value': 0.30, 'ref': 'absolute'},
            ],
            'action_type': None,
            'action_magnitude': None,
            'cooldown_days': 7,
            'risk_level': 'medium',
            'plain_english': 'Ad impression share below 30%',
        },
        {
            'name': 'CPA Spike',
            'rule_or_flag': 'flag',
            'type': 'performance',
            'conditions': [
                {'metric': 'cpa_w7_vs_prev_pct', 'op': 'gt', 'value': 0.50, 'ref': 'absolute'},
                {'metric': 'conversions_w7_sum', 'op': 'gte', 'value': 2, 'ref': 'absolute'},
            ],
            'action_type': None,
            'action_magnitude': None,
            'cooldown_days': 7,
            'risk_level': 'high',
            'plain_english': 'CPA risen more than 50% week on week',
        },
        {
            'name': 'Low CTR High Impressions',
            'rule_or_flag': 'flag',
            'type': 'performance',
            'conditions': [
                {'metric': 'ctr_w7_mean', 'op': 'lt', 'value': 0.01, 'ref': 'absolute'},
                {'metric': 'impressions_w7_sum', 'op': 'gt', 'value': 1000, 'ref': 'absolute'},
            ],
            'action_type': None,
            'action_magnitude': None,
            'cooldown_days': 7,
            'risk_level': 'medium',
            'plain_english': 'CTR below 1% despite 1000+ impressions',
        },

        # ── ANOMALY FLAGS (16-19) ─────────────────────────────────────────
        {
            'name': 'Cost Spike',
            'rule_or_flag': 'flag',
            'type': 'anomaly',
            'conditions': [
                {'metric': 'cost_w14_cv', 'op': 'gt', 'value': 2.0, 'ref': 'absolute'},
            ],
            'action_type': None,
            'action_magnitude': None,
            'cooldown_days': 3,
            'risk_level': 'medium',
            'plain_english': 'Statistical cost spike - coefficient of variation > 2.0',
        },
        {
            'name': 'Click Drop',
            'rule_or_flag': 'flag',
            'type': 'anomaly',
            'conditions': [
                {'metric': 'clicks_w7_vs_prev_pct', 'op': 'lt', 'value': -0.50, 'ref': 'absolute'},
                {'metric': 'clicks_w7_sum', 'op': 'gte', 'value': 20, 'ref': 'absolute'},
            ],
            'action_type': None,
            'action_magnitude': None,
            'cooldown_days': 3,
            'risk_level': 'medium',
            'plain_english': 'Clicks dropped more than 50% week on week',
        },
        {
            'name': 'Conversion Drop',
            'rule_or_flag': 'flag',
            'type': 'anomaly',
            'conditions': [
                {'metric': 'conversions_w7_vs_prev_pct', 'op': 'lt', 'value': -0.50, 'ref': 'absolute'},
                {'metric': 'conversions_w7_sum', 'op': 'gte', 'value': 2, 'ref': 'absolute'},
            ],
            'action_type': None,
            'action_magnitude': None,
            'cooldown_days': 3,
            'risk_level': 'high',
            'plain_english': 'Conversions dropped more than 50% week on week',
        },
        {
            'name': 'Impression Drop',
            'rule_or_flag': 'flag',
            'type': 'anomaly',
            'conditions': [
                {'metric': 'impressions_w7_vs_prev_pct', 'op': 'lt', 'value': -0.40, 'ref': 'absolute'},
                {'metric': 'impressions_w7_sum', 'op': 'gte', 'value': 500, 'ref': 'absolute'},
            ],
            'action_type': None,
            'action_magnitude': None,
            'cooldown_days': 3,
            'risk_level': 'medium',
            'plain_english': 'Impressions dropped 40%+ week on week',
        },

        # ── TECHNICAL FLAGS (20-23) ──────────────────────────────────────
        {
            'name': 'Poor Ad Strength',
            'rule_or_flag': 'flag',
            'type': 'technical',
            'conditions': [
                {'metric': 'ad_strength', 'op': 'eq', 'value': 'POOR', 'ref': 'absolute'},
            ],
            'action_type': None,
            'action_magnitude': None,
            'cooldown_days': 14,
            'risk_level': 'medium',
            'plain_english': 'Ad strength rated as Poor',
        },
        {
            'name': 'Average Ad Strength High Spend',
            'rule_or_flag': 'flag',
            'type': 'technical',
            'conditions': [
                {'metric': 'ad_strength', 'op': 'eq', 'value': 'AVERAGE', 'ref': 'absolute'},
                {'metric': 'cost_w14_sum', 'op': 'gt', 'value': 50, 'ref': 'absolute'},
            ],
            'action_type': None,
            'action_magnitude': None,
            'cooldown_days': 14,
            'risk_level': 'low',
            'plain_english': 'Ad strength is Average with significant spend',
        },
        {
            'name': 'Ad Approval Issues',
            'rule_or_flag': 'flag',
            'type': 'technical',
            'conditions': [
                {'metric': 'ad_status', 'op': 'eq', 'value': 'DISAPPROVED', 'ref': 'absolute'},
            ],
            'action_type': None,
            'action_magnitude': None,
            'cooldown_days': 7,
            'risk_level': 'high',
            'plain_english': 'Ad has been disapproved',
        },
        {
            'name': 'Low Data Warning',
            'rule_or_flag': 'flag',
            'type': 'technical',
            'conditions': [
                {'metric': 'low_data_flag', 'op': 'eq', 'value': 1, 'ref': 'absolute'},
            ],
            'action_type': None,
            'action_magnitude': None,
            'cooldown_days': 7,
            'risk_level': 'low',
            'plain_english': 'Ad has insufficient data for reliable analysis',
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
            ) VALUES (?, ?, 'ad', ?, ?, ?, NULL, '{"scope":"all"}', ?, ?, ?, ?, ?, TRUE, FALSE, ?)
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

    count = conn.execute("SELECT COUNT(*) FROM rules WHERE entity_type='ad'").fetchone()[0]
    print(f"Seeded {count} ad rules and flags")

    # Show breakdown
    breakdown = conn.execute("""
        SELECT rule_or_flag, type, COUNT(*)
        FROM rules WHERE entity_type='ad'
        GROUP BY rule_or_flag, type
        ORDER BY rule_or_flag, type
    """).fetchall()
    for row in breakdown:
        print(f"  {row[0]} / {row[1]}: {row[2]}")

    conn.close()


if __name__ == '__main__':
    seed_ad_rules()
