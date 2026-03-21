import duckdb
import json


def seed_keyword_rules():
    conn = duckdb.connect('warehouse.duckdb')

    # Check for existing keyword rules
    existing = conn.execute("SELECT COUNT(*) FROM rules WHERE entity_type='keyword'").fetchone()[0]
    if existing > 0:
        print(f"Found {existing} existing keyword rules. Deleting before re-seeding...")
        conn.execute("DELETE FROM rules WHERE entity_type='keyword'")
        conn.commit()

    # Get next ID
    next_id = conn.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM rules").fetchone()[0]

    rules = [
        # ── BID RULES (1-8) ──────────────────────────────────────────────
        {
            'name': 'Increase Max CPC - Strong Performance',
            'rule_or_flag': 'rule',
            'type': 'bid',
            'conditions': [
                {'metric': 'roas_w14', 'op': 'gt', 'value': 5.0, 'ref': 'absolute'},
                {'metric': 'conversions_w14_sum', 'op': 'gte', 'value': 5, 'ref': 'absolute'},
            ],
            'action_type': 'increase_bid',
            'action_magnitude': 20.0,
            'cooldown_days': 14,
            'risk_level': 'low',
            'plain_english': 'Increase Max CPC by 20% when ROAS (14d) > 5.0 and Conversions (14d) >= 5',
        },
        {
            'name': 'Decrease Max CPC - Weak ROAS',
            'rule_or_flag': 'rule',
            'type': 'bid',
            'conditions': [
                {'metric': 'roas_w14', 'op': 'lt', 'value': 2.0, 'ref': 'absolute'},
                {'metric': 'conversions_w14_sum', 'op': 'gte', 'value': 5, 'ref': 'absolute'},
            ],
            'action_type': 'decrease_bid',
            'action_magnitude': 15.0,
            'cooldown_days': 14,
            'risk_level': 'low',
            'plain_english': 'Decrease Max CPC by 15% when ROAS (14d) < 2.0 and Conversions (14d) >= 5',
        },
        {
            'name': 'Increase Max CPC - High QS Good CTR',
            'rule_or_flag': 'rule',
            'type': 'bid',
            'conditions': [
                {'metric': 'quality_score', 'op': 'gte', 'value': 7, 'ref': 'absolute'},
                {'metric': 'ctr_w7', 'op': 'gt', 'value': 0.04, 'ref': 'absolute'},
            ],
            'action_type': 'increase_bid',
            'action_magnitude': 15.0,
            'cooldown_days': 14,
            'risk_level': 'low',
            'plain_english': 'Increase Max CPC by 15% when Quality Score >= 7 and CTR (7d) > 4%',
        },
        {
            'name': 'Decrease Max CPC - Low QS',
            'rule_or_flag': 'rule',
            'type': 'bid',
            'conditions': [
                {'metric': 'quality_score', 'op': 'lte', 'value': 4, 'ref': 'absolute'},
                {'metric': 'cost_w14_sum', 'op': 'gt', 'value': 20, 'ref': 'absolute'},
            ],
            'action_type': 'decrease_bid',
            'action_magnitude': 20.0,
            'cooldown_days': 14,
            'risk_level': 'medium',
            'plain_english': 'Decrease Max CPC by 20% when Quality Score <= 4 and Cost (14d) > 20',
        },
        {
            'name': 'Increase Max CPC - Below First Page CPC',
            'rule_or_flag': 'rule',
            'type': 'bid',
            'conditions': [
                {'metric': 'bid_micros', 'op': 'lt', 'value': 0.6, 'ref': 'first_page_cpc_ratio'},
            ],
            'action_type': 'increase_bid_to_first_page',
            'action_magnitude': None,
            'cooldown_days': 7,
            'risk_level': 'medium',
            'plain_english': 'Increase bid to First Page CPC when current bid is < 60% of First Page CPC',
        },
        {
            'name': 'Decrease Max CPC - High CPA',
            'rule_or_flag': 'rule',
            'type': 'bid',
            'conditions': [
                {'metric': 'cpa_w14', 'op': 'gt', 'value': 100, 'ref': 'absolute'},
                {'metric': 'conversions_w14_sum', 'op': 'gte', 'value': 3, 'ref': 'absolute'},
            ],
            'action_type': 'decrease_bid',
            'action_magnitude': 20.0,
            'cooldown_days': 14,
            'risk_level': 'medium',
            'plain_english': 'Decrease Max CPC by 20% when CPA (14d) > 100 and Conversions (14d) >= 3',
        },
        {
            'name': 'Increase Max CPC - Lost Impression Share',
            'rule_or_flag': 'rule',
            'type': 'bid',
            'conditions': [
                {'metric': 'clicks_w7_sum', 'op': 'lt', 'value': 10, 'ref': 'absolute'},
                {'metric': 'impressions_w7_sum', 'op': 'gt', 'value': 100, 'ref': 'absolute'},
            ],
            'action_type': 'increase_bid',
            'action_magnitude': 20.0,
            'cooldown_days': 7,
            'risk_level': 'medium',
            'plain_english': 'Increase Max CPC by 20% when Clicks (7d) < 10 but Impressions (7d) > 100',
        },
        {
            'name': 'Decrease Max CPC - Low CTR',
            'rule_or_flag': 'rule',
            'type': 'bid',
            'conditions': [
                {'metric': 'ctr_w7', 'op': 'lt', 'value': 0.02, 'ref': 'absolute'},
                {'metric': 'clicks_w7_sum', 'op': 'gte', 'value': 20, 'ref': 'absolute'},
            ],
            'action_type': 'decrease_bid',
            'action_magnitude': 15.0,
            'cooldown_days': 7,
            'risk_level': 'low',
            'plain_english': 'Decrease Max CPC by 15% when CTR (7d) < 2% and Clicks (7d) >= 20',
        },

        # ── STATUS RULES (9-12) ──────────────────────────────────────────
        {
            'name': 'Pause - No Conversions High Spend',
            'rule_or_flag': 'rule',
            'type': 'status',
            'conditions': [
                {'metric': 'conversions_w30_sum', 'op': 'eq', 'value': 0, 'ref': 'absolute'},
                {'metric': 'cost_w30_sum', 'op': 'gt', 'value': 50, 'ref': 'absolute'},
            ],
            'action_type': 'pause',
            'action_magnitude': None,
            'cooldown_days': 30,
            'risk_level': 'medium',
            'plain_english': 'Pause keyword when zero conversions (30d) and Cost (30d) > 50',
        },
        {
            'name': 'Pause - Low QS High Spend',
            'rule_or_flag': 'rule',
            'type': 'status',
            'conditions': [
                {'metric': 'quality_score', 'op': 'lte', 'value': 3, 'ref': 'absolute'},
                {'metric': 'cost_w30_sum', 'op': 'gt', 'value': 30, 'ref': 'absolute'},
            ],
            'action_type': 'pause',
            'action_magnitude': None,
            'cooldown_days': 30,
            'risk_level': 'medium',
            'plain_english': 'Pause keyword when Quality Score <= 3 and Cost (30d) > 30',
        },
        {
            'name': 'Enable - Quality Score Improved',
            'rule_or_flag': 'rule',
            'type': 'status',
            'conditions': [
                {'metric': 'quality_score', 'op': 'gte', 'value': 7, 'ref': 'absolute'},
            ],
            'action_type': 'enable',
            'action_magnitude': None,
            'cooldown_days': 14,
            'risk_level': 'low',
            'plain_english': 'Enable keyword when Quality Score >= 7',
        },
        {
            'name': 'Pause - High CPA Low ROAS',
            'rule_or_flag': 'rule',
            'type': 'status',
            'conditions': [
                {'metric': 'cpa_w30', 'op': 'gt', 'value': 100, 'ref': 'absolute'},
                {'metric': 'roas_w30', 'op': 'lt', 'value': 1.5, 'ref': 'absolute'},
            ],
            'action_type': 'pause',
            'action_magnitude': None,
            'cooldown_days': 30,
            'risk_level': 'medium',
            'plain_english': 'Pause keyword when CPA (30d) > 100 and ROAS (30d) < 1.5',
        },

        # ── PERFORMANCE FLAGS (13-21) ──────────────────────────────────────
        {
            'name': 'Quality Score Drop',
            'rule_or_flag': 'flag',
            'type': 'performance',
            'conditions': [
                {'metric': 'quality_score', 'op': 'lte', 'value': 4, 'ref': 'absolute'},
                {'metric': 'cost_w7_sum', 'op': 'gt', 'value': 10, 'ref': 'absolute'},
            ],
            'action_type': None,
            'action_magnitude': None,
            'cooldown_days': 7,
            'risk_level': 'high',
            'plain_english': 'Alert when Quality Score <= 4 with significant spend',
        },
        {
            'name': 'ROAS Decline',
            'rule_or_flag': 'flag',
            'type': 'performance',
            'conditions': [
                {'metric': 'roas_w7_vs_prev_pct', 'op': 'lt', 'value': -0.30, 'ref': 'absolute'},
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
                {'metric': 'cpa_w7_vs_prev_pct', 'op': 'gt', 'value': 0.50, 'ref': 'absolute'},
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
                {'metric': 'ctr_w7_vs_prev_pct', 'op': 'lt', 'value': -0.30, 'ref': 'absolute'},
                {'metric': 'clicks_w7_sum', 'op': 'gte', 'value': 20, 'ref': 'absolute'},
            ],
            'action_type': None,
            'action_magnitude': None,
            'cooldown_days': 7,
            'risk_level': 'medium',
            'plain_english': 'Alert when CTR has dropped more than 30% week on week with sufficient clicks',
        },
        {
            'name': 'CVR Decline',
            'rule_or_flag': 'flag',
            'type': 'performance',
            'conditions': [
                {'metric': 'cvr_w7_vs_prev_pct', 'op': 'lt', 'value': -0.30, 'ref': 'absolute'},
            ],
            'action_type': None,
            'action_magnitude': None,
            'cooldown_days': 7,
            'risk_level': 'high',
            'plain_english': 'Alert when conversion rate declined more than 30% week on week',
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
            'cooldown_days': 14,
            'risk_level': 'high',
            'plain_english': 'Alert when keyword has zero conversions with over 30 in spend (30d)',
        },
        {
            'name': 'Low CTR High Impressions',
            'rule_or_flag': 'flag',
            'type': 'performance',
            'conditions': [
                {'metric': 'ctr_w7', 'op': 'lt', 'value': 0.01, 'ref': 'absolute'},
                {'metric': 'impressions_w7_sum', 'op': 'gt', 'value': 500, 'ref': 'absolute'},
            ],
            'action_type': None,
            'action_magnitude': None,
            'cooldown_days': 7,
            'risk_level': 'medium',
            'plain_english': 'Alert when CTR < 1% despite over 500 impressions',
        },
        {
            'name': 'Bid Below First Page CPC',
            'rule_or_flag': 'flag',
            'type': 'performance',
            'conditions': [
                {'metric': 'bid_micros', 'op': 'lt', 'value': 0.6, 'ref': 'first_page_cpc_ratio'},
            ],
            'action_type': None,
            'action_magnitude': None,
            'cooldown_days': 14,
            'risk_level': 'medium',
            'plain_english': 'Alert when bid is below 60% of First Page CPC',
        },
        {
            'name': 'Bid Above Top of Page CPC',
            'rule_or_flag': 'flag',
            'type': 'performance',
            'conditions': [
                {'metric': 'bid_micros', 'op': 'gt', 'value': 1.5, 'ref': 'top_of_page_cpc_ratio'},
                {'metric': 'conversions_w14_sum', 'op': 'lt', 'value': 3, 'ref': 'absolute'},
            ],
            'action_type': None,
            'action_magnitude': None,
            'cooldown_days': 14,
            'risk_level': 'low',
            'plain_english': 'Alert when overbidding above Top of Page CPC with low conversions',
        },

        # ── ANOMALY FLAGS (22-27) ─────────────────────────────────────────
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
            'plain_english': 'Statistical cost spike detected - coefficient of variation > 2.0',
        },
        {
            'name': 'Click Pattern Change',
            'rule_or_flag': 'flag',
            'type': 'anomaly',
            'conditions': [
                {'metric': 'clicks_w7_vs_prev_pct', 'op': 'gt', 'value': 1.0, 'ref': 'absolute'},
            ],
            'action_type': None,
            'action_magnitude': None,
            'cooldown_days': 3,
            'risk_level': 'low',
            'plain_english': 'Click volume doubled week on week - check for invalid clicks',
        },
        {
            'name': 'Conversion Drop',
            'rule_or_flag': 'flag',
            'type': 'anomaly',
            'conditions': [
                {'metric': 'conversions_w7_vs_prev_pct', 'op': 'lt', 'value': -0.50, 'ref': 'absolute'},
            ],
            'action_type': None,
            'action_magnitude': None,
            'cooldown_days': 3,
            'risk_level': 'high',
            'plain_english': 'Conversions dropped more than 50% week on week',
        },
        {
            'name': 'Cost Increase No Performance Gain',
            'rule_or_flag': 'flag',
            'type': 'anomaly',
            'conditions': [
                {'metric': 'cost_w7_vs_prev_pct', 'op': 'gt', 'value': 0.40, 'ref': 'absolute'},
                {'metric': 'conversions_w7_vs_prev_pct', 'op': 'lt', 'value': 0.05, 'ref': 'absolute'},
            ],
            'action_type': None,
            'action_magnitude': None,
            'cooldown_days': 7,
            'risk_level': 'medium',
            'plain_english': 'Cost up 40%+ but conversions are flat',
        },
        {
            'name': 'Quality Score Sudden Drop',
            'rule_or_flag': 'flag',
            'type': 'anomaly',
            'conditions': [
                {'metric': 'quality_score', 'op': 'lte', 'value': 5, 'ref': 'absolute'},
                {'metric': 'quality_score_creative', 'op': 'lte', 'value': 3, 'ref': 'absolute'},
            ],
            'action_type': None,
            'action_magnitude': None,
            'cooldown_days': 7,
            'risk_level': 'high',
            'plain_english': 'Quality Score dropped with poor creative component',
        },
        {
            'name': 'High Cost Volatility',
            'rule_or_flag': 'flag',
            'type': 'anomaly',
            'conditions': [
                {'metric': 'cost_w14_cv', 'op': 'gt', 'value': 1.5, 'ref': 'absolute'},
            ],
            'action_type': None,
            'action_magnitude': None,
            'cooldown_days': 7,
            'risk_level': 'medium',
            'plain_english': 'Keyword cost is highly volatile - coefficient of variation > 1.5',
        },

        # ── TECHNICAL FLAGS (28-32) ──────────────────────────────────────
        {
            'name': 'Low QS - Creative',
            'rule_or_flag': 'flag',
            'type': 'technical',
            'conditions': [
                {'metric': 'quality_score_creative', 'op': 'lte', 'value': 3, 'ref': 'absolute'},
            ],
            'action_type': None,
            'action_magnitude': None,
            'cooldown_days': 14,
            'risk_level': 'medium',
            'plain_english': 'Quality Score creative component is below average',
        },
        {
            'name': 'Low QS - Landing Page',
            'rule_or_flag': 'flag',
            'type': 'technical',
            'conditions': [
                {'metric': 'quality_score_landing_page', 'op': 'lte', 'value': 3, 'ref': 'absolute'},
            ],
            'action_type': None,
            'action_magnitude': None,
            'cooldown_days': 14,
            'risk_level': 'medium',
            'plain_english': 'Quality Score landing page component is below average',
        },
        {
            'name': 'Low QS - Relevance',
            'rule_or_flag': 'flag',
            'type': 'technical',
            'conditions': [
                {'metric': 'quality_score_relevance', 'op': 'lte', 'value': 3, 'ref': 'absolute'},
            ],
            'action_type': None,
            'action_magnitude': None,
            'cooldown_days': 14,
            'risk_level': 'medium',
            'plain_english': 'Quality Score relevance component is below average',
        },
        {
            'name': 'Broad Match High Waste',
            'rule_or_flag': 'flag',
            'type': 'technical',
            'conditions': [
                {'metric': 'match_type', 'op': 'eq', 'value': 'BROAD', 'ref': 'absolute'},
                {'metric': 'ctr_w7', 'op': 'lt', 'value': 0.015, 'ref': 'absolute'},
                {'metric': 'cost_w7_sum', 'op': 'gt', 'value': 20, 'ref': 'absolute'},
            ],
            'action_type': None,
            'action_magnitude': None,
            'cooldown_days': 7,
            'risk_level': 'medium',
            'plain_english': 'Broad match keyword with low CTR and significant spend',
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
            'plain_english': 'Keyword has insufficient data for reliable analysis',
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
            ) VALUES (?, ?, 'keyword', ?, ?, ?, NULL, '{"scope":"all"}', ?, ?, ?, ?, ?, TRUE, FALSE, ?)
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

    count = conn.execute("SELECT COUNT(*) FROM rules WHERE entity_type='keyword'").fetchone()[0]
    print(f"Seeded {count} keyword rules and flags")

    # Show breakdown
    breakdown = conn.execute("""
        SELECT rule_or_flag, type, COUNT(*)
        FROM rules WHERE entity_type='keyword'
        GROUP BY rule_or_flag, type
        ORDER BY rule_or_flag, type
    """).fetchall()
    for row in breakdown:
        print(f"  {row[0]} / {row[1]}: {row[2]}")

    conn.close()


if __name__ == '__main__':
    seed_keyword_rules()
