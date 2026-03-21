import duckdb
import json


def seed_ad_group_rules():
    conn = duckdb.connect('warehouse.duckdb')

    # Check for existing ad_group rules
    existing = conn.execute("SELECT COUNT(*) FROM rules WHERE entity_type='ad_group'").fetchone()[0]
    if existing > 0:
        print(f"Found {existing} existing ad_group rules. Deleting before re-seeding...")
        conn.execute("DELETE FROM rules WHERE entity_type='ad_group'")
        conn.commit()

    # Get next ID
    next_id = conn.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM rules").fetchone()[0]

    rules = [
        # ── BID RULES (1-8) ──────────────────────────────────────────────
        {
            'name': 'Increase CPC Bid - Strong Performance',
            'rule_or_flag': 'rule',
            'type': 'bid',
            'conditions': [
                {'metric': 'roas_w14_mean', 'op': 'gt', 'value': 6.0, 'ref': 'absolute'},
                {'metric': 'conversions_w14_sum', 'op': 'gte', 'value': 10, 'ref': 'absolute'},
            ],
            'action_type': 'increase_cpc_bid',
            'action_magnitude': 15.0,
            'cooldown_days': 14,
            'risk_level': 'low',
            'plain_english': 'Increase CPC bid by 15% when ROAS (14d) > 6.0 and Conversions (14d) >= 10',
        },
        {
            'name': 'Decrease CPC Bid - Weak ROAS',
            'rule_or_flag': 'rule',
            'type': 'bid',
            'conditions': [
                {'metric': 'roas_w14_mean', 'op': 'lt', 'value': 2.0, 'ref': 'absolute'},
                {'metric': 'conversions_w14_sum', 'op': 'gte', 'value': 5, 'ref': 'absolute'},
            ],
            'action_type': 'decrease_cpc_bid',
            'action_magnitude': 15.0,
            'cooldown_days': 14,
            'risk_level': 'low',
            'plain_english': 'Decrease CPC bid by 15% when ROAS (14d) < 2.0 and Conversions (14d) >= 5',
        },
        {
            'name': 'Increase CPC Bid - Lost Impression Share',
            'rule_or_flag': 'rule',
            'type': 'bid',
            'conditions': [
                {'metric': 'search_impression_share', 'op': 'lt', 'value': 0.5, 'ref': 'absolute'},
                {'metric': 'impression_share_lost_rank', 'op': 'gt', 'value': 0.3, 'ref': 'absolute'},
            ],
            'action_type': 'increase_cpc_bid',
            'action_magnitude': 20.0,
            'cooldown_days': 14,
            'risk_level': 'medium',
            'plain_english': 'Increase CPC bid by 20% when Search IS < 50% and IS Lost to Rank > 30%',
        },
        {
            'name': 'Decrease CPC Bid - High CPA',
            'rule_or_flag': 'rule',
            'type': 'bid',
            'conditions': [
                {'metric': 'cpa_w14_mean', 'op': 'gt', 'value': 1.5, 'ref': 'target'},
                {'metric': 'conversions_w14_sum', 'op': 'gte', 'value': 5, 'ref': 'absolute'},
            ],
            'action_type': 'decrease_cpc_bid',
            'action_magnitude': 20.0,
            'cooldown_days': 14,
            'risk_level': 'medium',
            'plain_english': 'Decrease CPC bid by 20% when CPA (14d) > 1.5x target and Conversions (14d) >= 5',
        },
        {
            'name': 'Increase tCPA Target - Underdelivering',
            'rule_or_flag': 'rule',
            'type': 'bid',
            'conditions': [
                {'metric': 'conversions_w14_sum', 'op': 'lt', 'value': 5, 'ref': 'absolute'},
            ],
            'action_type': 'increase_tcpa_target',
            'action_magnitude': 20.0,
            'cooldown_days': 14,
            'risk_level': 'medium',
            'plain_english': 'Increase tCPA target by 20% when Conversions (14d) < 5',
        },
        {
            'name': 'Decrease tCPA Target - Strong Performance',
            'rule_or_flag': 'rule',
            'type': 'bid',
            'conditions': [
                {'metric': 'cpa_w14_mean', 'op': 'lt', 'value': 0.7, 'ref': 'target'},
                {'metric': 'conversions_w14_sum', 'op': 'gte', 'value': 10, 'ref': 'absolute'},
            ],
            'action_type': 'decrease_tcpa_target',
            'action_magnitude': 15.0,
            'cooldown_days': 14,
            'risk_level': 'medium',
            'plain_english': 'Decrease tCPA target by 15% when CPA (14d) < 0.7x target and Conversions (14d) >= 10',
        },
        {
            'name': 'Increase CPC Bid - High CTR Low Conv',
            'rule_or_flag': 'rule',
            'type': 'bid',
            'conditions': [
                {'metric': 'ctr_w7_mean', 'op': 'gt', 'value': 0.05, 'ref': 'absolute'},
                {'metric': 'conversions_w7_sum', 'op': 'lt', 'value': 3, 'ref': 'absolute'},
            ],
            'action_type': 'increase_cpc_bid',
            'action_magnitude': 10.0,
            'cooldown_days': 7,
            'risk_level': 'low',
            'plain_english': 'Increase CPC bid by 10% when CTR (7d) > 5% and Conversions (7d) < 3',
        },
        {
            'name': 'Decrease CPC Bid - Low CTR',
            'rule_or_flag': 'rule',
            'type': 'bid',
            'conditions': [
                {'metric': 'ctr_w7_mean', 'op': 'lt', 'value': 0.02, 'ref': 'absolute'},
                {'metric': 'clicks_w7_sum', 'op': 'gte', 'value': 30, 'ref': 'absolute'},
            ],
            'action_type': 'decrease_cpc_bid',
            'action_magnitude': 15.0,
            'cooldown_days': 7,
            'risk_level': 'low',
            'plain_english': 'Decrease CPC bid by 15% when CTR (7d) < 2% and Clicks (7d) >= 30',
        },

        # ── STATUS RULES (9-12) ──────────────────────────────────────────
        {
            'name': 'Pause - Poor ROAS',
            'rule_or_flag': 'rule',
            'type': 'status',
            'conditions': [
                {'metric': 'roas_w30_mean', 'op': 'lt', 'value': 1.5, 'ref': 'absolute'},
                {'metric': 'cost_w30_sum', 'op': 'gt', 'value': 100, 'ref': 'absolute'},
            ],
            'action_type': 'pause_ad_group',
            'action_magnitude': None,
            'cooldown_days': 30,
            'risk_level': 'medium',
            'plain_english': 'Pause ad group when ROAS (30d) < 1.5 and Cost (30d) > 100',
        },
        {
            'name': 'Pause - No Conversions High Spend',
            'rule_or_flag': 'rule',
            'type': 'status',
            'conditions': [
                {'metric': 'conversions_w30_sum', 'op': 'eq', 'value': 0, 'ref': 'absolute'},
                {'metric': 'cost_w30_sum', 'op': 'gt', 'value': 50, 'ref': 'absolute'},
            ],
            'action_type': 'pause_ad_group',
            'action_magnitude': None,
            'cooldown_days': 30,
            'risk_level': 'medium',
            'plain_english': 'Pause ad group when zero conversions (30d) and Cost (30d) > 50',
        },
        {
            'name': 'Enable - Performance Recovered',
            'rule_or_flag': 'rule',
            'type': 'status',
            'conditions': [
                {'metric': 'roas_w7_mean', 'op': 'gt', 'value': 4.0, 'ref': 'absolute'},
            ],
            'action_type': 'enable_ad_group',
            'action_magnitude': None,
            'cooldown_days': 14,
            'risk_level': 'low',
            'plain_english': 'Enable ad group when ROAS (7d) > 4.0',
        },
        {
            'name': 'Pause - Low Optimization Score',
            'rule_or_flag': 'rule',
            'type': 'status',
            'conditions': [
                {'metric': 'optimization_score', 'op': 'lt', 'value': 0.3, 'ref': 'absolute'},
            ],
            'action_type': 'pause_ad_group',
            'action_magnitude': None,
            'cooldown_days': 30,
            'risk_level': 'medium',
            'plain_english': 'Pause ad group when Optimization Score < 30%',
        },

        # ── PERFORMANCE FLAGS (1-8) ──────────────────────────────────────
        {
            'name': 'ROAS Decline',
            'rule_or_flag': 'flag',
            'type': 'performance',
            'conditions': [
                {'metric': 'roas_wow_pct', 'op': 'lt', 'value': -0.30, 'ref': 'absolute'},
            ],
            'action_type': None,
            'action_magnitude': None,
            'cooldown_days': 7,
            'risk_level': 'high',
            'plain_english': 'Alert when ROAS has declined more than 30% week on week',
        },
        {
            'name': 'CPA Spike',
            'rule_or_flag': 'flag',
            'type': 'performance',
            'conditions': [
                {'metric': 'cpa_wow_pct', 'op': 'gt', 'value': 0.50, 'ref': 'absolute'},
            ],
            'action_type': None,
            'action_magnitude': None,
            'cooldown_days': 7,
            'risk_level': 'high',
            'plain_english': 'Alert when CPA has risen more than 50% week on week',
        },
        {
            'name': 'CTR Drop',
            'rule_or_flag': 'flag',
            'type': 'performance',
            'conditions': [
                {'metric': 'ctr_wow_pct', 'op': 'lt', 'value': -0.25, 'ref': 'absolute'},
            ],
            'action_type': None,
            'action_magnitude': None,
            'cooldown_days': 7,
            'risk_level': 'medium',
            'plain_english': 'Alert when CTR has dropped more than 25% week on week',
        },
        {
            'name': 'CVR Decline',
            'rule_or_flag': 'flag',
            'type': 'performance',
            'conditions': [
                {'metric': 'cvr_wow_pct', 'op': 'lt', 'value': -0.30, 'ref': 'absolute'},
            ],
            'action_type': None,
            'action_magnitude': None,
            'cooldown_days': 7,
            'risk_level': 'high',
            'plain_english': 'Alert when conversion rate has declined more than 30% week on week',
        },
        {
            'name': 'Conversion Drop',
            'rule_or_flag': 'flag',
            'type': 'performance',
            'conditions': [
                {'metric': 'conversions_wow_pct', 'op': 'lt', 'value': -0.40, 'ref': 'absolute'},
            ],
            'action_type': None,
            'action_magnitude': None,
            'cooldown_days': 7,
            'risk_level': 'high',
            'plain_english': 'Alert when conversions have dropped more than 40% week on week',
        },
        {
            'name': 'Cost Up Conversions Flat',
            'rule_or_flag': 'flag',
            'type': 'performance',
            'conditions': [
                {'metric': 'cost_wow_pct', 'op': 'gt', 'value': 0.30, 'ref': 'absolute'},
                {'metric': 'conversions_wow_pct', 'op': 'lt', 'value': 0.10, 'ref': 'absolute'},
            ],
            'action_type': None,
            'action_magnitude': None,
            'cooldown_days': 7,
            'risk_level': 'medium',
            'plain_english': 'Alert when cost is up 30%+ but conversions are flat',
        },
        {
            'name': 'Wasted Spend Zero Conversions',
            'rule_or_flag': 'flag',
            'type': 'performance',
            'conditions': [
                {'metric': 'conversions_w30_sum', 'op': 'eq', 'value': 0, 'ref': 'absolute'},
                {'metric': 'cost_w30_sum', 'op': 'gt', 'value': 50, 'ref': 'absolute'},
            ],
            'action_type': None,
            'action_magnitude': None,
            'cooldown_days': 14,
            'risk_level': 'high',
            'plain_english': 'Alert when ad group has zero conversions with over 50 in spend (30d)',
        },
        {
            'name': 'Below Target CPA',
            'rule_or_flag': 'flag',
            'type': 'performance',
            'conditions': [
                {'metric': 'cpa_w14_mean', 'op': 'lt', 'value': 0.5, 'ref': 'target'},
            ],
            'action_type': None,
            'action_magnitude': None,
            'cooldown_days': 14,
            'risk_level': 'low',
            'plain_english': 'Positive alert: CPA is well below target - opportunity to scale',
        },

        # ── ANOMALY FLAGS (9-14) ─────────────────────────────────────────
        {
            'name': 'Cost Spike',
            'rule_or_flag': 'flag',
            'type': 'anomaly',
            'conditions': [
                {'metric': 'cost_z', 'op': 'gt', 'value': 2.0, 'ref': 'absolute'},
            ],
            'action_type': None,
            'action_magnitude': None,
            'cooldown_days': 3,
            'risk_level': 'medium',
            'plain_english': 'Statistical cost spike detected',
        },
        {
            'name': 'Cost Drop',
            'rule_or_flag': 'flag',
            'type': 'anomaly',
            'conditions': [
                {'metric': 'cost_z', 'op': 'lt', 'value': -2.0, 'ref': 'absolute'},
            ],
            'action_type': None,
            'action_magnitude': None,
            'cooldown_days': 3,
            'risk_level': 'medium',
            'plain_english': 'Statistical cost drop detected',
        },
        {
            'name': 'Click Spike',
            'rule_or_flag': 'flag',
            'type': 'anomaly',
            'conditions': [
                {'metric': 'clicks_z', 'op': 'gt', 'value': 2.0, 'ref': 'absolute'},
            ],
            'action_type': None,
            'action_magnitude': None,
            'cooldown_days': 3,
            'risk_level': 'low',
            'plain_english': 'Statistical click volume spike detected',
        },
        {
            'name': 'Conversion Drop Anomaly',
            'rule_or_flag': 'flag',
            'type': 'anomaly',
            'conditions': [
                {'metric': 'conversions_z', 'op': 'lt', 'value': -2.0, 'ref': 'absolute'},
            ],
            'action_type': None,
            'action_magnitude': None,
            'cooldown_days': 3,
            'risk_level': 'high',
            'plain_english': 'Statistical conversion drop detected - check tracking',
        },
        {
            'name': 'High Cost Volatility',
            'rule_or_flag': 'flag',
            'type': 'anomaly',
            'conditions': [
                {'metric': 'cost_cv', 'op': 'gt', 'value': 1.5, 'ref': 'absolute'},
            ],
            'action_type': None,
            'action_magnitude': None,
            'cooldown_days': 7,
            'risk_level': 'medium',
            'plain_english': 'Ad group cost is highly volatile - coefficient of variation > 1.5',
        },
        {
            'name': 'High Click Volatility',
            'rule_or_flag': 'flag',
            'type': 'anomaly',
            'conditions': [
                {'metric': 'clicks_cv', 'op': 'gt', 'value': 1.0, 'ref': 'absolute'},
            ],
            'action_type': None,
            'action_magnitude': None,
            'cooldown_days': 7,
            'risk_level': 'low',
            'plain_english': 'Ad group click volume is highly volatile',
        },

        # ── TECHNICAL FLAGS (15-18) ──────────────────────────────────────
        {
            'name': 'Low IS Lost to Rank',
            'rule_or_flag': 'flag',
            'type': 'technical',
            'conditions': [
                {'metric': 'search_impression_share', 'op': 'lt', 'value': 0.4, 'ref': 'absolute'},
                {'metric': 'impression_share_lost_rank', 'op': 'gt', 'value': 0.3, 'ref': 'absolute'},
            ],
            'action_type': None,
            'action_magnitude': None,
            'cooldown_days': 7,
            'risk_level': 'medium',
            'plain_english': 'Low search impression share with significant losses to ad rank',
        },
        {
            'name': 'Low IS Lost to Budget',
            'rule_or_flag': 'flag',
            'type': 'technical',
            'conditions': [
                {'metric': 'search_impression_share', 'op': 'lt', 'value': 0.4, 'ref': 'absolute'},
                {'metric': 'impression_share_lost_budget', 'op': 'gt', 'value': 0.3, 'ref': 'absolute'},
            ],
            'action_type': None,
            'action_magnitude': None,
            'cooldown_days': 7,
            'risk_level': 'medium',
            'plain_english': 'Low search impression share with significant losses to budget',
        },
        {
            'name': 'Low Optimization Score',
            'rule_or_flag': 'flag',
            'type': 'technical',
            'conditions': [
                {'metric': 'optimization_score', 'op': 'lt', 'value': 0.4, 'ref': 'absolute'},
            ],
            'action_type': None,
            'action_magnitude': None,
            'cooldown_days': 14,
            'risk_level': 'low',
            'plain_english': 'Optimization score below 40% - review settings',
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
            'plain_english': 'Ad group has insufficient data for reliable analysis',
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
            ) VALUES (?, ?, 'ad_group', ?, ?, ?, NULL, '{"scope":"all"}', ?, ?, ?, ?, ?, TRUE, FALSE, ?)
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

    count = conn.execute("SELECT COUNT(*) FROM rules WHERE entity_type='ad_group'").fetchone()[0]
    print(f"Seeded {count} ad group rules and flags")

    # Show breakdown
    breakdown = conn.execute("""
        SELECT rule_or_flag, type, COUNT(*)
        FROM rules WHERE entity_type='ad_group'
        GROUP BY rule_or_flag, type
        ORDER BY rule_or_flag, type
    """).fetchall()
    for row in breakdown:
        print(f"  {row[0]} / {row[1]}: {row[2]}")

    conn.close()


if __name__ == '__main__':
    seed_ad_group_rules()
