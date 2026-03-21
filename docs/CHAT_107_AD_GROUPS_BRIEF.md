# CHAT 107: AD GROUPS RULES & FLAGS IMPLEMENTATION

**Date:** 2026-03-21
**Estimated Time:** 3-4 hours
**Priority:** HIGH
**Dependencies:** Chat 106 investigation complete

---

## CONTEXT

Chat 106 investigation confirmed:
- Database ready (`entity_type` column exists)
- Engine already multi-entity (metric maps for all 5 entities)
- CSS fully reusable
- Action labels already entity-aware

**Strategy:** Copy Campaigns Rules & Flags implementation → Adapt for Ad Groups

---

## OBJECTIVE

Implement Rules & Flags for Ad Groups by copying the Campaigns implementation and adapting it with Ad Groups-specific data.

---

## DELIVERABLES

**Templates:**
1. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\ad_groups.html` — MODIFY (add Rules & Flags tab)
2. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\components\ad_groups_rules_flags_tab.html` — CREATE (copy from campaigns)
3. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\components\ad_groups_rules_flow_builder.html` — CREATE (copy from campaigns)

**Routes:**
4. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\ad_groups.py` — MODIFY (add rules CRUD routes)

**Handoff:**
5. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_107_HANDOFF.md` — CREATE
6. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_107_SUMMARY.md` — CREATE

---

## AD GROUPS RULES (12 total)

### BID CATEGORY (8 rules)

**Rule ID: ag_bid_001**
- Name: Increase CPC Bid – Strong Performance
- Condition 1: roas_w14_mean > 6.0
- Condition 2: conversions_w14_sum >= 10
- Action: increase_cpc_bid, magnitude 15%
- Cooldown: 14 days
- Risk: low

**Rule ID: ag_bid_002**
- Name: Decrease CPC Bid – Weak ROAS
- Condition 1: roas_w14_mean < 2.0
- Condition 2: conversions_w14_sum >= 5
- Action: decrease_cpc_bid, magnitude 15%
- Cooldown: 14 days
- Risk: low

**Rule ID: ag_bid_003**
- Name: Increase CPC Bid – Lost Impression Share
- Condition 1: search_impression_share < 0.50
- Condition 2: impression_share_lost_rank > 0.30
- Action: increase_cpc_bid, magnitude 20%
- Cooldown: 14 days
- Risk: medium

**Rule ID: ag_bid_004**
- Name: Decrease CPC Bid – High CPA
- Condition 1: cpa_w14_mean > (target_cpa * 1.5)
- Condition 2: conversions_w14_sum >= 5
- Action: decrease_cpc_bid, magnitude 20%
- Cooldown: 14 days
- Risk: medium

**Rule ID: ag_bid_005**
- Name: Increase tCPA Target – Underdelivering Conversions
- Condition 1: conversions_w14_sum < 5
- Condition 2: target_cpa IS NOT NULL
- Action: increase_tcpa_target, magnitude 20%
- Cooldown: 14 days
- Risk: medium

**Rule ID: ag_bid_006**
- Name: Decrease tCPA Target – Strong Performance
- Condition 1: cpa_w14_mean < (target_cpa * 0.7)
- Condition 2: conversions_w14_sum >= 10
- Condition 3: target_cpa IS NOT NULL
- Action: decrease_tcpa_target, magnitude 15%
- Cooldown: 14 days
- Risk: medium

**Rule ID: ag_bid_007**
- Name: Increase CPC Bid – High CTR Low Conversions
- Condition 1: ctr_w7_mean > 0.05
- Condition 2: conversions_w7_sum < 3
- Condition 3: clicks_w7_sum >= 30
- Action: increase_cpc_bid, magnitude 10%
- Cooldown: 7 days
- Risk: low

**Rule ID: ag_bid_008**
- Name: Decrease CPC Bid – Low CTR
- Condition 1: ctr_w7_mean < 0.02
- Condition 2: clicks_w7_sum >= 30
- Action: decrease_cpc_bid, magnitude 15%
- Cooldown: 7 days
- Risk: low

### STATUS CATEGORY (4 rules)

**Rule ID: ag_status_001**
- Name: Pause – Poor ROAS
- Condition 1: roas_w30_mean < 1.5
- Condition 2: conversions_w30_sum >= 10
- Condition 3: cost_w30_sum > 100000000
- Action: pause_ad_group
- Cooldown: 30 days
- Risk: high

**Rule ID: ag_status_002**
- Name: Pause – High CPA No Conversions
- Condition 1: conversions_w30_sum = 0
- Condition 2: cost_w30_sum > 50000000
- Action: pause_ad_group
- Cooldown: 30 days
- Risk: medium

**Rule ID: ag_status_003**
- Name: Enable – Previously Paused Now Improved
- Condition 1: ad_group_status = 'PAUSED'
- Condition 2: roas_w7_mean > 4.0
- Action: enable_ad_group
- Cooldown: 14 days
- Risk: low

**Rule ID: ag_status_004**
- Name: Pause – Low Quality Score
- Condition 1: optimization_score < 0.3
- Condition 2: cost_w30_sum > 100000000
- Action: pause_ad_group
- Cooldown: 30 days
- Risk: high

---

## AD GROUPS FLAGS (18 total)

### PERFORMANCE CATEGORY (8 flags)

**Flag ID: ag_perf_001**
- Name: ROAS Decline
- Condition: roas_w7_vs_prev_pct < -0.30 AND conversions_w7_sum >= 5
- Severity: HIGH
- Cooldown: 7 days

**Flag ID: ag_perf_002**
- Name: CPA Spike
- Condition: cpa_w7_vs_prev_pct > 0.50 AND conversions_w7_sum >= 3
- Severity: HIGH
- Cooldown: 7 days

**Flag ID: ag_perf_003**
- Name: CTR Drop
- Condition: ctr_w7_vs_prev_pct < -0.25 AND clicks_w7_sum >= 30
- Severity: MEDIUM
- Cooldown: 7 days

**Flag ID: ag_perf_004**
- Name: CVR Decline
- Condition: cvr_w7_vs_prev_pct < -0.30 AND conversions_w7_sum >= 5
- Severity: HIGH
- Cooldown: 7 days

**Flag ID: ag_perf_005**
- Name: Conversion Drop
- Condition: conversions_w7_vs_prev_pct < -0.40 AND conversions_w7_sum >= 3
- Severity: HIGH
- Cooldown: 7 days

**Flag ID: ag_perf_006**
- Name: Cost Increase No Conversion Increase
- Condition: cost_w7_vs_prev_pct > 0.30 AND conversions_w7_vs_prev_pct < 0.10
- Severity: MEDIUM
- Cooldown: 7 days

**Flag ID: ag_perf_007**
- Name: Wasted Spend – Zero Conversions
- Condition: conversions_w30_sum = 0 AND cost_w30_sum > 50000000
- Severity: HIGH
- Cooldown: 30 days

**Flag ID: ag_perf_008**
- Name: Below Target CPA
- Condition: cpa_w14_mean < (target_cpa * 0.5) AND conversions_w14_sum >= 10
- Severity: LOW
- Cooldown: 14 days

### ANOMALY CATEGORY (6 flags)

**Flag ID: ag_anom_001**
- Name: Cost Spike
- Condition: anomaly_cost_z > 2.0
- Severity: HIGH
- Cooldown: 3 days

**Flag ID: ag_anom_002**
- Name: Cost Drop
- Condition: anomaly_cost_z < -2.0
- Severity: MEDIUM
- Cooldown: 3 days

**Flag ID: ag_anom_003**
- Name: Click Spike
- Condition: anomaly_clicks_z > 2.0
- Severity: MEDIUM
- Cooldown: 3 days

**Flag ID: ag_anom_004**
- Name: Conversion Drop Anomaly
- Condition: anomaly_conversions_z < -2.0
- Severity: HIGH
- Cooldown: 3 days

**Flag ID: ag_anom_005**
- Name: High Cost Volatility
- Condition: cost_w14_cv > 1.5
- Severity: MEDIUM
- Cooldown: 14 days

**Flag ID: ag_anom_006**
- Name: High Click Volatility
- Condition: clicks_w14_cv > 1.0
- Severity: LOW
- Cooldown: 14 days

### TECHNICAL CATEGORY (4 flags)

**Flag ID: ag_tech_001**
- Name: Low Impression Share – Rank
- Condition: search_impression_share < 0.40 AND impression_share_lost_rank > 0.30
- Severity: MEDIUM
- Cooldown: 7 days

**Flag ID: ag_tech_002**
- Name: Low Impression Share – Budget
- Condition: search_impression_share < 0.40 AND impression_share_lost_budget > 0.30
- Severity: HIGH
- Cooldown: 7 days

**Flag ID: ag_tech_003**
- Name: Low Optimization Score
- Condition: optimization_score < 0.4
- Severity: MEDIUM
- Cooldown: 14 days

**Flag ID: ag_tech_004**
- Name: Low Data Warning
- Condition: low_data_flag = TRUE
- Severity: LOW
- Cooldown: 14 days

---

## REQUIREMENTS

### Technical Requirements

**Database:**
- All rules/flags use `entity_type = 'ad_group'`
- Duplicate detection MUST filter by `entity_type`

**Templates:**
- Copy Campaigns modal exactly (5-step flow)
- Step 1: Change "campaigns" → "ad groups", scope JSON `{ad_groups: [...]}`
- Step 3: Type categories = Bid, Status (NO Budget category)
- Step 4: Metrics must match engine's AD_GROUP_METRIC_MAP
- All text: "ad group" not "campaign"

**Routes:**
- Copy Campaigns CRUD routes
- Change all "campaign" → "ad_group"
- Entity scope JSON format: `{ad_groups: [...]}` not `{campaigns: [...]}`
- Duplicate check: `entity_type = 'ad_group'`

**CSS:**
- Reuse all existing CSS (no changes needed)
- Badge classes work as-is

**Engine:**
- Engine already has AD_GROUP_METRIC_MAP
- No engine changes needed

### Constraints

**CRITICAL - NO BUDGET CATEGORY:**
- Ad Groups have NO Budget category
- Only show Bid + Status in Step 3 type selector
- Filter pills: All / Bid / Status (not All / Budget / Bid / Status)

**CRITICAL - ENTITY SCOPE JSON:**
- Campaigns use: `{"campaigns": ["123", "456"]}`
- Ad Groups use: `{"ad_groups": ["789", "012"]}`
- This is NOT interchangeable

**CRITICAL - DUPLICATE DETECTION:**
- Must filter by `entity_type = 'ad_group'`
- Without this, duplicate check will match against campaign rules

---

## SUCCESS CRITERIA

- [ ] Rules & Flags tab visible on Ad Groups page
- [ ] "Add rule or flag" button opens modal
- [ ] Step 1 shows ad groups list (not campaigns)
- [ ] Step 3 shows Bid + Status only (no Budget)
- [ ] Can create new rule, saves with `entity_type = 'ad_group'`
- [ ] Can create new flag, saves with `entity_type = 'ad_group'`
- [ ] Can edit existing rule
- [ ] Can save rule as template
- [ ] Filter pills work (All / Bid / Status)
- [ ] Duplicate detection works (doesn't match campaign rules)
- [ ] No console errors
- [ ] Flask starts cleanly

ALL must pass before reporting complete.

---

## REFERENCE FILES (COPY FROM THESE)

**Templates to copy:**
- `act_dashboard/templates/campaigns.html` — Rules & Flags tab integration
- `act_dashboard/templates/components/rules_flow_builder.html` — 5-step modal
- `act_dashboard/templates/components/rules_flags_tab.html` — Tab pane with tables

**Routes to copy:**
- `act_dashboard/routes/campaigns.py` — All rules CRUD routes

**CSS (reuse as-is):**
- `act_dashboard/static/css/rules.css`

**Reference docs:**
- `docs/CHAT_106_INVESTIGATION_REPORT.md` — Patterns and architecture
- `docs/RULES_FLAGS_DESIGN_ALL_ENTITIES1.md` — Full rules/flags spec

---

## TESTING

**Test in Opera browser:**

1. Navigate to Ad Groups page
2. Click Rules & Flags tab
3. Click "Add rule or flag"
4. Verify Step 1 shows ad groups (not campaigns)
5. Create a new Bid rule:
   - Step 1: Select "All ad groups"
   - Step 2: Choose "Rule"
   - Step 3: Choose "Bid"
   - Step 4: Set conditions and action
   - Step 5: Review and save
6. Verify rule appears in table with `entity_type = 'ad_group'`
7. Create a new flag
8. Verify duplicate detection works
9. Test edit rule
10. Test save as template
11. Check Flask console for errors

---

## IMPLEMENTATION PATTERN

**For each file:**

1. **Copy the Campaigns version exactly**
2. **Find-replace:**
   - "campaign" → "ad_group"
   - "Campaign" → "Ad Group"
   - "campaigns" → "ad_groups"
   - "Campaigns" → "Ad Groups"
3. **Remove Budget category code** (Step 3 type selector, filter pills)
4. **Change entity scope JSON format** (Step 1)
5. **Add `entity_type` filter to duplicate detection**
6. **Test before moving to next file**

---

## CRITICAL REMINDERS

- **Copy working code** — Don't rebuild from scratch
- **Test incrementally** — One file at a time
- **No Budget category** — Ad Groups only have Bid + Status
- **Entity scope JSON** — `{ad_groups: [...]}` not `{campaigns: [...]}`
- **Duplicate detection** — Must filter by `entity_type`
- **All text** — "ad group" not "campaign"

---

**Document Version:** 1.0
**Last Updated:** 2026-03-21
