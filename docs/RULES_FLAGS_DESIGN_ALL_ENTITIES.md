# RULES & FLAGS DESIGN - AD GROUPS, KEYWORDS, ADS, SHOPPING
**Generated:** 2026-03-20
**Purpose:** Complete design specification for rules/flags expansion across 4 entity types
**Reference:** Campaigns has 18 rules + 30 flags (baseline pattern)

---

## DESIGN PHILOSOPHY

**Rules** = Automated optimization actions (change bids, pause/enable, adjust settings)
**Flags** = Alert/notification system (performance issues, anomalies, technical problems)

**Categories for ALL entities:**
- **Rules:** Budget/Bid, Status, Optimization
- **Flags:** Performance, Anomaly, Technical

---

# 1. AD GROUPS - RULES & FLAGS

## AD GROUPS - RULES (12 total)

### BUDGET CATEGORY (N/A - ad groups don't have individual budgets)
Ad groups inherit budget from campaigns. Skip this category.

### BID CATEGORY (8 rules)

**AG-BID-001: Increase CPC Bid - Strong Performance**
- Condition: roas_w14_mean > 6.0 AND conversions_w14_sum ≥ 10
- Action: Increase cpc_bid_micros by 15%
- Cooldown: 14 days
- Rationale: High ROAS + sufficient conversions → can bid more aggressively

**AG-BID-002: Decrease CPC Bid - Weak ROAS**
- Condition: roas_w14_mean < 2.0 AND conversions_w14_sum ≥ 5
- Action: Decrease cpc_bid_micros by 15%
- Cooldown: 14 days
- Rationale: Low ROAS with data → reduce spend

**AG-BID-003: Increase CPC Bid - Lost Impression Share**
- Condition: search_impression_share < 50% AND impression_share_lost_rank > 30%
- Action: Increase cpc_bid_micros by 20%
- Cooldown: 14 days
- Rationale: Losing rank → bid up to compete

**AG-BID-004: Decrease CPC Bid - High CPA**
- Condition: cpa_w14_mean > target_cpa * 1.5 AND conversions_w14_sum ≥ 5
- Action: Decrease cpc_bid_micros by 20%
- Cooldown: 14 days
- Rationale: CPA 50% over target → reduce bids

**AG-BID-005: Increase tCPA Target - Underdelivering Conversions**
- Condition: conversions_w14_sum < 5 AND target_cpa IS NOT NULL
- Action: Increase target_cpa by 20%
- Cooldown: 14 days
- Rationale: Not getting conversions → loosen target

**AG-BID-006: Decrease tCPA Target - Strong Performance**
- Condition: cpa_w14_mean < target_cpa * 0.7 AND conversions_w14_sum ≥ 10
- Action: Decrease target_cpa by 15%
- Cooldown: 14 days
- Rationale: Beating target → tighten to improve efficiency

**AG-BID-007: Increase CPC Bid - High CTR Low Conversions**
- Condition: ctr_w7_mean > 0.05 AND conversions_w7_sum < 3 AND clicks_w7_sum ≥ 30
- Action: Increase cpc_bid_micros by 10%
- Cooldown: 7 days
- Rationale: Good engagement but low volume → bid up

**AG-BID-008: Decrease CPC Bid - Low CTR**
- Condition: ctr_w7_mean < 0.02 AND clicks_w7_sum ≥ 30
- Action: Decrease cpc_bid_micros by 15%
- Cooldown: 7 days
- Rationale: Poor engagement → reduce bids

### STATUS CATEGORY (4 rules)

**AG-STATUS-001: Pause - Poor ROAS**
- Condition: roas_w30_mean < 1.5 AND conversions_w30_sum ≥ 10 AND cost_w30_sum > 100000000 (£100)
- Action: Pause ad group
- Cooldown: 30 days
- Rationale: Unprofitable with sufficient data

**AG-STATUS-002: Pause - High CPA No Conversions**
- Condition: conversions_w30_sum = 0 AND cost_w30_sum > 50000000 (£50)
- Action: Pause ad group
- Cooldown: 30 days
- Rationale: Wasted spend with no conversions

**AG-STATUS-003: Enable - Previously Paused Now Improved**
- Condition: ad_group_status = 'PAUSED' AND roas_w7_mean > 4.0
- Action: Enable ad group
- Cooldown: 14 days
- Rationale: Performance recovered → re-enable

**AG-STATUS-004: Pause - Low Quality Score**
- Condition: optimization_score < 0.3 AND cost_w30_sum > 100000000
- Action: Pause ad group
- Cooldown: 30 days
- Rationale: Poor optimization + spend → needs fixing

---

## AD GROUPS - FLAGS (18 total)

### PERFORMANCE CATEGORY (8 flags)

**AG-PERF-001: ROAS Decline**
- Condition: roas_w7_vs_prev_pct < -0.30 AND conversions_w7_sum ≥ 5
- Severity: HIGH
- Cooldown: 7 days

**AG-PERF-002: CPA Spike**
- Condition: cpa_w7_vs_prev_pct > 0.50 AND conversions_w7_sum ≥ 3
- Severity: HIGH
- Cooldown: 7 days

**AG-PERF-003: CTR Drop**
- Condition: ctr_w7_vs_prev_pct < -0.25 AND clicks_w7_sum ≥ 30
- Severity: MEDIUM
- Cooldown: 7 days

**AG-PERF-004: CVR Decline**
- Condition: cvr_w7_vs_prev_pct < -0.30 AND conversions_w7_sum ≥ 5
- Severity: HIGH
- Cooldown: 7 days

**AG-PERF-005: Conversion Drop**
- Condition: conversions_w7_vs_prev_pct < -0.40 AND conversions_w7_sum ≥ 3
- Severity: HIGH
- Cooldown: 7 days

**AG-PERF-006: Cost Increase No Conversion Increase**
- Condition: cost_w7_vs_prev_pct > 0.30 AND conversions_w7_vs_prev_pct < 0.10
- Severity: MEDIUM
- Cooldown: 7 days

**AG-PERF-007: Wasted Spend - Zero Conversions**
- Condition: conversions_w30_sum = 0 AND cost_w30_sum > 50000000
- Severity: HIGH
- Cooldown: 30 days

**AG-PERF-008: Below Target CPA**
- Condition: cpa_w14_mean < target_cpa * 0.5 AND conversions_w14_sum ≥ 10
- Severity: LOW
- Cooldown: 14 days
- Rationale: Opportunity to scale

### ANOMALY CATEGORY (6 flags)

**AG-ANOM-001: Cost Spike**
- Condition: anomaly_cost_z > 2.0
- Severity: HIGH
- Cooldown: 3 days

**AG-ANOM-002: Cost Drop**
- Condition: anomaly_cost_z < -2.0
- Severity: MEDIUM
- Cooldown: 3 days

**AG-ANOM-003: Click Spike**
- Condition: anomaly_clicks_z > 2.0
- Severity: MEDIUM
- Cooldown: 3 days

**AG-ANOM-004: Conversion Drop Anomaly**
- Condition: anomaly_conversions_z < -2.0
- Severity: HIGH
- Cooldown: 3 days

**AG-ANOM-005: High Cost Volatility**
- Condition: cost_w14_cv > 1.5
- Severity: MEDIUM
- Cooldown: 14 days

**AG-ANOM-006: High Click Volatility**
- Condition: clicks_w14_cv > 1.0
- Severity: LOW
- Cooldown: 14 days

### TECHNICAL CATEGORY (4 flags)

**AG-TECH-001: Low Impression Share - Rank**
- Condition: search_impression_share < 40% AND impression_share_lost_rank > 30%
- Severity: MEDIUM
- Cooldown: 7 days

**AG-TECH-002: Low Impression Share - Budget**
- Condition: search_impression_share < 40% AND impression_share_lost_budget > 30%
- Severity: HIGH
- Cooldown: 7 days

**AG-TECH-003: Low Optimization Score**
- Condition: optimization_score < 0.4
- Severity: MEDIUM
- Cooldown: 14 days

**AG-TECH-004: Low Data Warning**
- Condition: low_data_flag = TRUE
- Severity: LOW
- Cooldown: 7 days

---

# 2. KEYWORDS - RULES & FLAGS

## KEYWORDS - RULES (12 total)

### BID CATEGORY (8 rules)

**KW-BID-001: Increase Max CPC - Strong Performance**
- Condition: roas_w14 > 5.0 AND conversions_w14_sum ≥ 5
- Action: Increase bid_micros by 20%
- Cooldown: 14 days

**KW-BID-002: Decrease Max CPC - Weak ROAS**
- Condition: roas_w14 < 2.0 AND conversions_w14_sum ≥ 3
- Action: Decrease bid_micros by 20%
- Cooldown: 14 days

**KW-BID-003: Increase Max CPC - High Quality Score**
- Condition: quality_score ≥ 8 AND conversions_w7_sum ≥ 3
- Action: Increase bid_micros by 15%
- Cooldown: 7 days
- Rationale: High QS = efficient → bid up

**KW-BID-004: Decrease Max CPC - Low Quality Score**
- Condition: quality_score ≤ 4 AND cost_w30_sum > 20000000
- Action: Decrease bid_micros by 25%
- Cooldown: 14 days

**KW-BID-005: Increase Max CPC - Below First Page CPC**
- Condition: bid_micros < first_page_cpc_micros * 0.8 AND conversions_w14_sum ≥ 3
- Action: Increase bid_micros to match first_page_cpc_micros
- Cooldown: 14 days

**KW-BID-006: Decrease Max CPC - High CPA**
- Condition: cpa_w14 > 50000000 (£50) AND conversions_w14_sum ≥ 3
- Action: Decrease bid_micros by 20%
- Cooldown: 14 days

**KW-BID-007: Increase Max CPC - Lost Impression Share**
- Condition: clicks_w7_sum < 10 AND impressions_w7_sum > 100
- Action: Increase bid_micros by 20%
- Cooldown: 7 days
- Rationale: Low CTR but high impressions → bid up to improve position

**KW-BID-008: Decrease Max CPC - Low CTR**
- Condition: ctr_w7 < 0.02 AND clicks_w7_sum ≥ 20
- Action: Decrease bid_micros by 15%
- Cooldown: 7 days

### STATUS CATEGORY (4 rules)

**KW-STATUS-001: Pause - Poor Performance No Conversions**
- Condition: conversions_w90_sum = 0 AND cost_micros_w90_sum > 50000000
- Action: Pause keyword
- Cooldown: 30 days

**KW-STATUS-002: Pause - Low Quality Score High Spend**
- Condition: quality_score ≤ 3 AND cost_w30_sum > 30000000
- Action: Pause keyword
- Cooldown: 30 days

**KW-STATUS-003: Enable - Quality Score Improved**
- Condition: status = 'PAUSED' AND quality_score ≥ 7
- Action: Enable keyword
- Cooldown: 14 days

**KW-STATUS-004: Pause - High CPA Low ROAS**
- Condition: cpa_w30 > 100000000 AND roas_w30 < 1.5 AND conversions_w30_sum ≥ 5
- Action: Pause keyword
- Cooldown: 30 days

---

## KEYWORDS - FLAGS (20 total)

### PERFORMANCE CATEGORY (9 flags)

**KW-PERF-001: Quality Score Drop**
- Condition: quality_score ≤ 4 AND cost_w7_sum > 10000000
- Severity: HIGH
- Cooldown: 7 days

**KW-PERF-002: ROAS Decline**
- Condition: roas_w7_vs_prev_pct < -0.30 AND conversions_w7_sum ≥ 3
- Severity: HIGH
- Cooldown: 7 days

**KW-PERF-003: CPA Spike**
- Condition: cpa_w7_vs_prev_pct > 0.50 AND conversions_w7_sum ≥ 2
- Severity: HIGH
- Cooldown: 7 days

**KW-PERF-004: CTR Drop**
- Condition: ctr_w7_vs_prev_pct < -0.30 AND clicks_w7_sum ≥ 20
- Severity: MEDIUM
- Cooldown: 7 days

**KW-PERF-005: CVR Decline**
- Condition: cvr_w7_vs_prev_pct < -0.30 AND conversions_w7_sum ≥ 3
- Severity: HIGH
- Cooldown: 7 days

**KW-PERF-006: Wasted Spend - Zero Conversions**
- Condition: conversions_w30_sum = 0 AND cost_w30_sum > 30000000
- Severity: HIGH
- Cooldown: 30 days

**KW-PERF-007: Low CTR High Impressions**
- Condition: ctr_w7 < 0.01 AND impressions_w7_sum > 500
- Severity: MEDIUM
- Cooldown: 7 days
- Rationale: Poor relevance or ad copy

**KW-PERF-008: Bid Below First Page CPC**
- Condition: bid_micros < first_page_cpc_micros * 0.6
- Severity: LOW
- Cooldown: 14 days

**KW-PERF-009: Bid Above Top of Page CPC**
- Condition: bid_micros > top_of_page_cpc_micros * 1.5 AND conversions_w14_sum < 3
- Severity: MEDIUM
- Cooldown: 14 days
- Rationale: Overbidding without results

### ANOMALY CATEGORY (6 flags)

**KW-ANOM-001: Cost Spike**
- Condition: cost_w14_cv > 2.0
- Severity: HIGH
- Cooldown: 7 days

**KW-ANOM-002: Click Pattern Change**
- Condition: clicks_w7_vs_prev_pct > 1.0 OR clicks_w7_vs_prev_pct < -0.5
- Severity: MEDIUM
- Cooldown: 7 days

**KW-ANOM-003: Conversion Drop**
- Condition: conversions_w7_vs_prev_pct < -0.50 AND conversions_w7_sum ≥ 2
- Severity: HIGH
- Cooldown: 7 days

**KW-ANOM-004: Cost Increase No Performance Gain**
- Condition: cost_w7_vs_prev_pct > 0.40 AND conversions_w7_vs_prev_pct < 0.05
- Severity: MEDIUM
- Cooldown: 7 days

**KW-ANOM-005: Quality Score Sudden Drop**
- Condition: quality_score ≤ 5 AND quality_score_creative ≤ 3
- Severity: HIGH
- Cooldown: 7 days

**KW-ANOM-006: High Cost Volatility**
- Condition: cost_w14_cv > 1.5
- Severity: MEDIUM
- Cooldown: 14 days

### TECHNICAL CATEGORY (5 flags)

**KW-TECH-001: Low Quality Score - Creative**
- Condition: quality_score_creative ≤ 3
- Severity: MEDIUM
- Cooldown: 14 days

**KW-TECH-002: Low Quality Score - Landing Page**
- Condition: quality_score_landing_page ≤ 3
- Severity: MEDIUM
- Cooldown: 14 days

**KW-TECH-003: Low Quality Score - Relevance**
- Condition: quality_score_relevance ≤ 3
- Severity: MEDIUM
- Cooldown: 14 days

**KW-TECH-004: Broad Match High Waste**
- Condition: match_type = 'BROAD' AND ctr_w7 < 0.015 AND cost_w7_sum > 20000000
- Severity: HIGH
- Cooldown: 7 days
- Rationale: Broad match wasting spend

**KW-TECH-005: Low Data Warning**
- Condition: low_data_flag = TRUE
- Severity: LOW
- Cooldown: 7 days

---

# 3. ADS - RULES & FLAGS

## ADS - RULES (8 total)

### STATUS CATEGORY (8 rules)
Ads have limited actions available - primarily pause/enable

**AD-STATUS-001: Pause - Poor CTR**
- Condition: ctr_w14_mean < 0.015 AND clicks_w14_sum ≥ 50
- Action: Pause ad
- Cooldown: 30 days

**AD-STATUS-002: Pause - Zero Conversions High Spend**
- Condition: conversions_w30_sum = 0 AND cost_w30_sum > 30000000
- Action: Pause ad
- Cooldown: 30 days

**AD-STATUS-003: Pause - Low ROAS**
- Condition: roas_w14_mean < 1.5 AND conversions_w14_sum ≥ 5
- Action: Pause ad
- Cooldown: 30 days

**AD-STATUS-004: Pause - Poor Ad Strength**
- Condition: ad_strength IN ('POOR', 'AVERAGE') AND cost_w14_sum > 20000000
- Action: Pause ad
- Cooldown: 30 days

**AD-STATUS-005: Enable - Ad Strength Improved**
- Condition: ad_status = 'PAUSED' AND ad_strength IN ('GOOD', 'EXCELLENT')
- Action: Enable ad
- Cooldown: 14 days

**AD-STATUS-006: Pause - High CPA**
- Condition: cpa_w14_mean > 80000000 AND conversions_w14_sum ≥ 3
- Action: Pause ad
- Cooldown: 30 days

**AD-STATUS-007: Enable - Performance Recovered**
- Condition: ad_status = 'PAUSED' AND roas_w7_mean > 4.0 AND conversions_w7_sum ≥ 3
- Action: Enable ad
- Cooldown: 14 days

**AD-STATUS-008: Pause - CTR Declining Trend**
- Condition: ctr_w7_vs_prev_pct < -0.40 AND clicks_w7_sum ≥ 30
- Action: Pause ad
- Cooldown: 30 days
- Rationale: Creative fatigue

---

## ADS - FLAGS (15 total)

### PERFORMANCE CATEGORY (7 flags)

**AD-PERF-001: CTR Drop - Creative Fatigue**
- Condition: ctr_w7_vs_prev_pct < -0.30 AND clicks_w7_sum ≥ 30
- Severity: HIGH
- Cooldown: 7 days

**AD-PERF-002: ROAS Decline**
- Condition: roas_w7_vs_prev_pct < -0.30 AND conversions_w7_sum ≥ 3
- Severity: HIGH
- Cooldown: 7 days

**AD-PERF-003: CVR Drop**
- Condition: cvr_w7_vs_prev_pct < -0.30 AND conversions_w7_sum ≥ 3
- Severity: HIGH
- Cooldown: 7 days

**AD-PERF-004: Wasted Spend - Zero Conversions**
- Condition: conversions_w30_sum = 0 AND cost_w30_sum > 30000000
- Severity: HIGH
- Cooldown: 30 days

**AD-PERF-005: Low Impression Share**
- Condition: search_impression_share < 30%
- Severity: MEDIUM
- Cooldown: 14 days

**AD-PERF-006: CPA Spike**
- Condition: cpa_w7_vs_prev_pct > 0.50 AND conversions_w7_sum ≥ 2
- Severity: HIGH
- Cooldown: 7 days

**AD-PERF-007: Low CTR High Impressions**
- Condition: ctr_w7_mean < 0.01 AND impressions_w7_sum > 1000
- Severity: MEDIUM
- Cooldown: 7 days

### ANOMALY CATEGORY (4 flags)

**AD-ANOM-001: Cost Spike**
- Condition: cost_w14_cv > 2.0
- Severity: HIGH
- Cooldown: 7 days

**AD-ANOM-002: Click Drop**
- Condition: clicks_w7_vs_prev_pct < -0.50 AND clicks_w7_sum ≥ 20
- Severity: MEDIUM
- Cooldown: 7 days

**AD-ANOM-003: Conversion Drop**
- Condition: conversions_w7_vs_prev_pct < -0.50 AND conversions_w7_sum ≥ 2
- Severity: HIGH
- Cooldown: 7 days

**AD-ANOM-004: Impression Drop**
- Condition: impressions_w7_vs_prev_pct < -0.40 AND impressions_w7_sum ≥ 500
- Severity: MEDIUM
- Cooldown: 7 days

### TECHNICAL CATEGORY (4 flags)

**AD-TECH-001: Poor Ad Strength**
- Condition: ad_strength = 'POOR'
- Severity: HIGH
- Cooldown: 14 days

**AD-TECH-002: Average Ad Strength High Spend**
- Condition: ad_strength = 'AVERAGE' AND cost_w14_sum > 50000000
- Severity: MEDIUM
- Cooldown: 14 days

**AD-TECH-003: Ad Approval Issues**
- Condition: ad_status = 'DISAPPROVED'
- Severity: HIGH
- Cooldown: 1 day
- Note: Requires ad_status column in daily table

**AD-TECH-004: Low Data Warning**
- Condition: low_data_flag = TRUE
- Severity: LOW
- Cooldown: 7 days

---

# 4. SHOPPING - RULES & FLAGS

## SHOPPING - RULES (10 total)

### BID CATEGORY (6 rules)

**SH-BID-001: Increase Bid - Strong ROAS**
- Condition: roas_w14_mean > 5.0 AND conversions_w14_sum ≥ 10
- Action: Increase campaign bid adjustment by 15%
- Cooldown: 14 days

**SH-BID-002: Decrease Bid - Weak ROAS**
- Condition: roas_w14_mean < 2.0 AND conversions_w14_sum ≥ 5
- Action: Decrease campaign bid adjustment by 15%
- Cooldown: 14 days

**SH-BID-003: Increase Bid - Low Impression Share**
- Condition: search_impression_share < 40%
- Action: Increase campaign bid adjustment by 20%
- Cooldown: 14 days

**SH-BID-004: Decrease Bid - High CPA**
- Condition: cpa_w14_mean > 60000000 AND conversions_w14_sum ≥ 5
- Action: Decrease campaign bid adjustment by 20%
- Cooldown: 14 days

**SH-BID-005: Increase Bid - High CTR Low Conversions**
- Condition: ctr_w7_mean > 0.015 AND conversions_w7_sum < 3 AND clicks_w7_sum ≥ 50
- Action: Increase campaign bid adjustment by 10%
- Cooldown: 7 days

**SH-BID-006: Decrease Bid - Low CTR**
- Condition: ctr_w7_mean < 0.01 AND clicks_w7_sum ≥ 30
- Action: Decrease campaign bid adjustment by 15%
- Cooldown: 7 days

### STATUS CATEGORY (4 rules)

**SH-STATUS-001: Pause - Poor ROAS**
- Condition: roas_w30_mean < 1.5 AND conversions_w30_sum ≥ 10 AND cost_w30_sum > 100000000
- Action: Pause shopping campaign
- Cooldown: 30 days

**SH-STATUS-002: Pause - Zero Conversions High Spend**
- Condition: conversions_w30_sum = 0 AND cost_w30_sum > 50000000
- Action: Pause shopping campaign
- Cooldown: 30 days

**SH-STATUS-003: Enable - Performance Recovered**
- Condition: campaign_status = 'PAUSED' AND roas_w7_mean > 4.0
- Action: Enable shopping campaign
- Cooldown: 14 days

**SH-STATUS-004: Pause - Low Optimization Score**
- Condition: optimization_score < 0.3 AND cost_w30_sum > 100000000
- Action: Pause shopping campaign
- Cooldown: 30 days

---

## SHOPPING - FLAGS (18 total)

### PERFORMANCE CATEGORY (8 flags)

**SH-PERF-001: ROAS Decline**
- Condition: roas_w7_vs_prev_pct < -0.30 AND conversions_w7_sum ≥ 5
- Severity: HIGH
- Cooldown: 7 days

**SH-PERF-002: CPA Spike**
- Condition: cpa_w7_vs_prev_pct > 0.50 AND conversions_w7_sum ≥ 3
- Severity: HIGH
- Cooldown: 7 days

**SH-PERF-003: CTR Drop**
- Condition: ctr_w7_vs_prev_pct < -0.25 AND clicks_w7_sum ≥ 50
- Severity: MEDIUM
- Cooldown: 7 days

**SH-PERF-004: CVR Decline**
- Condition: cvr_w7_vs_prev_pct < -0.30 AND conversions_w7_sum ≥ 5
- Severity: HIGH
- Cooldown: 7 days

**SH-PERF-005: Wasted Spend - Zero Conversions**
- Condition: conversions_w30_sum = 0 AND cost_w30_sum > 50000000
- Severity: HIGH
- Cooldown: 30 days

**SH-PERF-006: Low Impression Share**
- Condition: search_impression_share < 30%
- Severity: MEDIUM
- Cooldown: 14 days

**SH-PERF-007: Low Optimization Score**
- Condition: optimization_score < 0.4
- Severity: MEDIUM
- Cooldown: 14 days

**SH-PERF-008: Cost Increase No Conversion Increase**
- Condition: cost_w7_vs_prev_pct > 0.30 AND conversions_w7_vs_prev_pct < 0.10
- Severity: MEDIUM
- Cooldown: 7 days

### ANOMALY CATEGORY (6 flags)

**SH-ANOM-001: Cost Spike**
- Condition: cost_w14_cv > 2.0
- Severity: HIGH
- Cooldown: 7 days

**SH-ANOM-002: Cost Drop**
- Condition: cost_w7_vs_prev_pct < -0.50
- Severity: MEDIUM
- Cooldown: 7 days

**SH-ANOM-003: Click Spike**
- Condition: clicks_w7_vs_prev_pct > 1.0
- Severity: MEDIUM
- Cooldown: 7 days

**SH-ANOM-004: Conversion Drop**
- Condition: conversions_w7_vs_prev_pct < -0.50 AND conversions_w7_sum ≥ 3
- Severity: HIGH
- Cooldown: 7 days

**SH-ANOM-005: Impression Spike**
- Condition: impressions_w7_vs_prev_pct > 1.0
- Severity: LOW
- Cooldown: 7 days

**SH-ANOM-006: High Cost Volatility**
- Condition: cost_w14_cv > 1.5
- Severity: MEDIUM
- Cooldown: 14 days

### TECHNICAL CATEGORY (4 flags)

**SH-TECH-001: Feed Quality Issue**
- Condition: optimization_score < 0.3
- Severity: HIGH
- Cooldown: 7 days
- Rationale: Low opt score often indicates feed issues

**SH-TECH-002: Low Product Coverage**
- Condition: search_impression_share < 20%
- Severity: HIGH
- Cooldown: 14 days

**SH-TECH-003: Product Disapprovals**
- Condition: (placeholder for product disapproval count when available)
- Severity: HIGH
- Cooldown: 3 days
- Note: Requires feed quality data

**SH-TECH-004: Low Data Warning**
- Condition: low_data_flag = TRUE
- Severity: LOW
- Cooldown: 7 days

---

# SUMMARY - RULES & FLAGS COUNT

| Entity | Rules | Flags | Total |
|--------|-------|-------|-------|
| **Campaigns** (existing) | 18 | 30 | 48 |
| **Ad Groups** | 12 | 18 | 30 |
| **Keywords** | 12 | 20 | 32 |
| **Ads** | 8 | 15 | 23 |
| **Shopping** | 10 | 18 | 28 |
| **TOTAL** | **60** | **101** | **161** |

---

# METRIC MAP REQUIREMENTS

Based on this design, here's what each entity's metric map needs:

**AD_GROUP_METRIC_MAP:** ~45 metrics
- All w7/w14/w30 aggregations (base + derived + vs_prev)
- Anomaly detection (z-scores, CV)
- Low data flags
- Entity-specific: target_cpa, optimization_score, impression shares

**KEYWORD_METRIC_MAP:** ~35 metrics
- All w7/w14/w30 aggregations
- w90 for long-term pause rules
- Quality score breakdown (4 fields)
- Bid benchmarks (first_page_cpc, top_of_page_cpc)
- Low data flags

**AD_METRIC_MAP:** ~25 metrics
- All w7/w14/w30 aggregations
- Anomaly detection (cost_cv)
- Low data flags
- Entity-specific: ad_strength, search_impression_share

**SHOPPING_METRIC_MAP:** ~25 metrics
- All w7/w14/w30 aggregations
- Anomaly detection (cost_cv)
- Low data flags
- Entity-specific: optimization_score, search_impression_share

---

**Next Step:** Wireframes for each entity's Rules/Flags UI
