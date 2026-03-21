# CHAT 107: AD GROUPS RULES & FLAGS IMPLEMENTATION

**Date:** 2026-03-21
**Estimated Time:** 3-4 hours
**Priority:** HIGH
**Dependencies:** Chat 106 investigation complete

---

## CONTEXT

Investigation (Chat 106) confirmed infrastructure is ready:
- Database `rules` table has `entity_type` column
- Engine has `AD_GROUP_METRIC_MAP` for ad groups
- CSS is entity-agnostic and fully reusable
- Action labels already support `ad_group` entity

**Current state:**
- Campaigns Rules & Flags is complete and working
- 19 campaign rules already seeded in database with `entity_type='campaign'`
- All infrastructure tested and stable

**Strategy:** Copy Campaigns implementation EXACTLY → Change only entity-specific parts

---

## OBJECTIVE

Implement complete Rules & Flags system for Ad Groups by copying Campaigns and adapting for `entity_type='ad_group'`.

---

## DELIVERABLES

1. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\ad_groups.html` — MODIFY
   - Add Rules & Flags tab (copy from campaigns.html)

2. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\ad_groups.py` — MODIFY
   - Add all rules CRUD routes (copy from campaigns.py)
   - Add `/api/ad-groups-list` endpoint for Step 1 picker

3. `C:\Users\User\Desktop\gads-data-layer\scripts\seed_ad_group_rules.py` — CREATE
   - Script to insert all 12 rules + 18 flags into database

4. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_107_HANDOFF.md` — CREATE

5. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_107_SUMMARY.md` — CREATE

---

## CRITICAL ENTITY-SPECIFIC CHANGES

### 1. TEMPLATE CHANGES (ad_groups.html)

**WHERE TO ADD:**
- Find the existing tabs section (should have "Ad Groups" tab and "Recommendations" tab)
- Insert "Rules & Flags" tab BETWEEN them (same position as in campaigns.html)

**WHAT TO COPY FROM campaigns.html:**
- Lines with `<li class="nav-item">` containing Rules & Flags tab
- The entire `<div class="tab-pane">` for Rules & Flags content
- Include `rules_flow_builder.html` component
- Include `rules_flags_tab.html` component

**ENTITY-SPECIFIC REPLACEMENTS:**
- Change all references: "campaign" → "ad_group", "campaigns" → "ad groups", "Campaign" → "Ad Group"
- API endpoint: `/campaigns/rules` → `/ad_groups/rules`
- JavaScript scope var: `selectedCampaigns` → `selectedAdGroups`

### 2. MODAL STEP 1 CHANGES (entity picker)

**Current (Campaigns):**
```html
<div class="flow-section-label">Select the campaigns this rule applies to</div>
<!-- Campaign list loaded from /api/campaigns-list -->
```

**New (Ad Groups):**
```html
<div class="flow-section-label">Select the ad groups this rule applies to</div>
<!-- Ad group list loaded from /api/ad-groups-list -->
```

**New API endpoint needed in ad_groups.py:**
```python
@ad_groups_bp.route('/api/ad-groups-list', methods=['GET'])
def get_ad_groups_list():
    """Return ad groups for Step 1 picker"""
    # Query: SELECT ad_group_id, ad_group_name, status, bid_strategy 
    # FROM ad_group_daily WHERE customer_id = ?
    # Return: [{"id": "123", "name": "Google Ads Consultant", "status": "ENABLED", "bid_strategy": "TARGET_CPA"}]
```

**Scope JSON format:**
- All ad groups: `{"scope": "all"}`
- Specific ad groups: `{"scope": {"ad_groups": ["123", "456"]}}`

### 3. MODAL STEP 3 CHANGES (type selection)

**REMOVE Budget category card entirely:**

Current campaigns.html Step 3 has 3 cards:
```html
<div class="type-card" data-type="budget">Budget</div>
<div class="type-card" data-type="bid">Bid</div>
<div class="type-card" data-type="status">Status</div>
```

Ad Groups Step 3 should have ONLY 2 cards:
```html
<div class="type-card" data-type="bid">Bid</div>
<div class="type-card" data-type="status">Status</div>
```

**JavaScript changes:**
- Remove "budget" from `RULE_TYPES` array
- Filter pills: Only "All", "Bid", "Status" (remove "Budget")

### 4. MODAL STEP 4 CHANGES (metrics and actions)

**Metric dropdown options (MUST match AD_GROUP_METRIC_MAP):**

Verify against `recommendations_engine.py` → `AD_GROUP_METRIC_MAP`:
- roas_w7_mean, roas_w14_mean, roas_w30_mean
- cpa_w7_mean, cpa_w14_mean, cpa_w30_mean
- ctr_w7_mean, ctr_w14_mean, ctr_w30_mean
- cpc_w7_mean, cpc_w14_mean, cpc_w30_mean
- conversions_w7_sum, conversions_w14_sum, conversions_w30_sum
- cost_w7_sum, cost_w14_sum, cost_w30_sum
- clicks_w7_sum, clicks_w14_sum, clicks_w30_sum
- impressions_w7_sum, impressions_w14_sum, impressions_w30_sum
- search_impression_share, impression_share_lost_rank, impression_share_lost_budget
- optimization_score
- roas_wow_pct, cpa_wow_pct, ctr_wow_pct, cvr_wow_pct, conversions_wow_pct, cost_wow_pct
- cost_z, clicks_z, conversions_z
- cost_cv, clicks_cv
- low_data_flag

**Action type dropdown options:**

Verify against `recommendations.py` → `_ACTION_TYPE_TO_RULE_TYPE`:
- increase_cpc_bid
- decrease_cpc_bid
- increase_tcpa_target (NOT increase_tcpa)
- decrease_tcpa_target (NOT decrease_tcpa)
- pause_ad_group
- enable_ad_group

**REMOVE these action types (budget-related):**
- increase_budget
- decrease_budget
- emergency_budget_cut

**Operator values (use these exact strings):**
- "gt" (greater than >)
- "lt" (less than <)
- "gte" (greater than or equal >=)
- "lte" (less than or equal <=)
- "eq" (equal =)

**Reference unit values:**
- "absolute" (raw value)
- "target" (× target multiplier)
- "pct" (% change)

### 5. SAVE PAYLOAD FORMAT

**Complete rule save payload example:**
```json
{
  "id": "ag_bid_001",
  "entity_type": "ad_group",
  "name": "Increase CPC Bid – Strong Performance",
  "type": "bid",
  "action_type": "increase_cpc_bid",
  "scope": "all",
  "conditions": [
    {
      "metric": "roas_w14_mean",
      "op": "gt",
      "value": 6.0,
      "ref": "absolute"
    },
    {
      "metric": "conversions_w14_sum",
      "op": "gte",
      "value": 10,
      "ref": "absolute"
    }
  ],
  "action": {
    "type": "increase_cpc_bid",
    "magnitude": 15
  },
  "cooldown_days": 14,
  "risk_level": "low",
  "enabled": true,
  "is_template": false,
  "rule_or_flag": "rule"
}
```

**Complete flag save payload example:**
```json
{
  "id": "ag_perf_001",
  "entity_type": "ad_group",
  "name": "ROAS Decline",
  "type": "performance",
  "scope": "all",
  "conditions": [
    {
      "metric": "roas_wow_pct",
      "op": "lt",
      "value": -0.30,
      "ref": "absolute"
    }
  ],
  "cooldown_days": 7,
  "risk_level": "high",
  "enabled": true,
  "is_template": false,
  "rule_or_flag": "flag",
  "direction": "negative"
}
```

### 6. DUPLICATE DETECTION

**MUST filter by entity_type when checking duplicates:**

```python
def check_duplicate_rule(type, action_type, condition_metric, entity_type):
    conn = _get_warehouse()
    query = """
        SELECT COUNT(*) as count
        FROM rules
        WHERE entity_type = ?
        AND type = ?
        AND action_type = ?
        AND json_extract_string(conditions, '$[0].metric') = ?
        AND is_template = FALSE
    """
    result = conn.execute(query, [entity_type, type, action_type, condition_metric]).fetchone()
    return result['count'] > 0
```

### 7. PLAIN ENGLISH GENERATION

**Reference function:** `get_action_label()` in `recommendations.py`

**Pattern:**
```python
def generate_plain_english(rule, entity_type):
    # entity_type = 'ad_group'
    entity_singular = 'ad group'  # NOT 'campaign'
    entity_plural = 'ad groups'   # NOT 'campaigns'
    
    # Example output:
    # "When ROAS (14d) > 6.0 and Conversions ≥ 10, increase CPC bid by 15%"
    # "When ad group status is PAUSED and ROAS (7d) > 4.0, enable ad group"
```

---

## AD GROUPS RULES (12 total)

**Database insert format:**

```sql
INSERT INTO rules (
  id, entity_type, name, type, action_type, scope, conditions, action,
  cooldown_days, risk_level, enabled, is_template, rule_or_flag
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
```

### BID CATEGORY (8 rules)

**ag_bid_001: Increase CPC Bid – Strong Performance**
```json
{
  "id": "ag_bid_001",
  "entity_type": "ad_group",
  "name": "Increase CPC Bid – Strong Performance",
  "type": "bid",
  "action_type": "increase_cpc_bid",
  "scope": "all",
  "conditions": [
    {"metric": "roas_w14_mean", "op": "gt", "value": 6.0, "ref": "absolute"},
    {"metric": "conversions_w14_sum", "op": "gte", "value": 10, "ref": "absolute"}
  ],
  "action": {"type": "increase_cpc_bid", "magnitude": 15},
  "cooldown_days": 14,
  "risk_level": "low",
  "enabled": true,
  "is_template": false,
  "rule_or_flag": "rule"
}
```

**ag_bid_002: Decrease CPC Bid – Weak ROAS**
```json
{
  "id": "ag_bid_002",
  "entity_type": "ad_group",
  "name": "Decrease CPC Bid – Weak ROAS",
  "type": "bid",
  "action_type": "decrease_cpc_bid",
  "scope": "all",
  "conditions": [
    {"metric": "roas_w14_mean", "op": "lt", "value": 2.0, "ref": "absolute"},
    {"metric": "conversions_w14_sum", "op": "gte", "value": 5, "ref": "absolute"}
  ],
  "action": {"type": "decrease_cpc_bid", "magnitude": 15},
  "cooldown_days": 14,
  "risk_level": "low",
  "enabled": true,
  "is_template": false,
  "rule_or_flag": "rule"
}
```

**ag_bid_003: Increase CPC Bid – Lost Impression Share**
```json
{
  "id": "ag_bid_003",
  "entity_type": "ad_group",
  "name": "Increase CPC Bid – Lost Impression Share",
  "type": "bid",
  "action_type": "increase_cpc_bid",
  "scope": "all",
  "conditions": [
    {"metric": "search_impression_share", "op": "lt", "value": 0.5, "ref": "absolute"},
    {"metric": "impression_share_lost_rank", "op": "gt", "value": 0.3, "ref": "absolute"}
  ],
  "action": {"type": "increase_cpc_bid", "magnitude": 20},
  "cooldown_days": 14,
  "risk_level": "medium",
  "enabled": true,
  "is_template": false,
  "rule_or_flag": "rule"
}
```

**ag_bid_004: Decrease CPC Bid – High CPA**
```json
{
  "id": "ag_bid_004",
  "entity_type": "ad_group",
  "name": "Decrease CPC Bid – High CPA",
  "type": "bid",
  "action_type": "decrease_cpc_bid",
  "scope": "all",
  "conditions": [
    {"metric": "cpa_w14_mean", "op": "gt", "value": 1.5, "ref": "target"},
    {"metric": "conversions_w14_sum", "op": "gte", "value": 5, "ref": "absolute"}
  ],
  "action": {"type": "decrease_cpc_bid", "magnitude": 20},
  "cooldown_days": 14,
  "risk_level": "medium",
  "enabled": true,
  "is_template": false,
  "rule_or_flag": "rule"
}
```

**ag_bid_005: Increase tCPA Target – Underdelivering**
```json
{
  "id": "ag_bid_005",
  "entity_type": "ad_group",
  "name": "Increase tCPA Target – Underdelivering",
  "type": "bid",
  "action_type": "increase_tcpa_target",
  "scope": "all",
  "conditions": [
    {"metric": "conversions_w14_sum", "op": "lt", "value": 5, "ref": "absolute"},
    {"metric": "target_cpa", "op": "is_not_null", "value": null, "ref": "absolute"}
  ],
  "action": {"type": "increase_tcpa_target", "magnitude": 20},
  "cooldown_days": 14,
  "risk_level": "medium",
  "enabled": true,
  "is_template": false,
  "rule_or_flag": "rule"
}
```

**ag_bid_006: Decrease tCPA Target – Strong Performance**
```json
{
  "id": "ag_bid_006",
  "entity_type": "ad_group",
  "name": "Decrease tCPA Target – Strong Performance",
  "type": "bid",
  "action_type": "decrease_tcpa_target",
  "scope": "all",
  "conditions": [
    {"metric": "cpa_w14_mean", "op": "lt", "value": 0.7, "ref": "target"},
    {"metric": "conversions_w14_sum", "op": "gte", "value": 10, "ref": "absolute"},
    {"metric": "target_cpa", "op": "is_not_null", "value": null, "ref": "absolute"}
  ],
  "action": {"type": "decrease_tcpa_target", "magnitude": 15},
  "cooldown_days": 14,
  "risk_level": "medium",
  "enabled": true,
  "is_template": false,
  "rule_or_flag": "rule"
}
```

**ag_bid_007: Increase CPC Bid – High CTR Low Conv**
```json
{
  "id": "ag_bid_007",
  "entity_type": "ad_group",
  "name": "Increase CPC Bid – High CTR Low Conv",
  "type": "bid",
  "action_type": "increase_cpc_bid",
  "scope": "all",
  "conditions": [
    {"metric": "ctr_w7_mean", "op": "gt", "value": 0.05, "ref": "absolute"},
    {"metric": "conversions_w7_sum", "op": "lt", "value": 3, "ref": "absolute"},
    {"metric": "clicks_w7_sum", "op": "gte", "value": 30, "ref": "absolute"}
  ],
  "action": {"type": "increase_cpc_bid", "magnitude": 10},
  "cooldown_days": 7,
  "risk_level": "low",
  "enabled": true,
  "is_template": false,
  "rule_or_flag": "rule"
}
```

**ag_bid_008: Decrease CPC Bid – Low CTR**
```json
{
  "id": "ag_bid_008",
  "entity_type": "ad_group",
  "name": "Decrease CPC Bid – Low CTR",
  "type": "bid",
  "action_type": "decrease_cpc_bid",
  "scope": "all",
  "conditions": [
    {"metric": "ctr_w7_mean", "op": "lt", "value": 0.02, "ref": "absolute"},
    {"metric": "clicks_w7_sum", "op": "gte", "value": 30, "ref": "absolute"}
  ],
  "action": {"type": "decrease_cpc_bid", "magnitude": 15},
  "cooldown_days": 7,
  "risk_level": "low",
  "enabled": true,
  "is_template": false,
  "rule_or_flag": "rule"
}
```

### STATUS CATEGORY (4 rules)

**ag_status_001: Pause – Poor ROAS**
```json
{
  "id": "ag_status_001",
  "entity_type": "ad_group",
  "name": "Pause – Poor ROAS",
  "type": "status",
  "action_type": "pause_ad_group",
  "scope": "all",
  "conditions": [
    {"metric": "roas_w30_mean", "op": "lt", "value": 1.5, "ref": "absolute"},
    {"metric": "conversions_w30_sum", "op": "gte", "value": 10, "ref": "absolute"},
    {"metric": "cost_w30_sum", "op": "gt", "value": 100000000, "ref": "absolute"}
  ],
  "action": {"type": "pause_ad_group", "magnitude": null},
  "cooldown_days": 30,
  "risk_level": "medium",
  "enabled": true,
  "is_template": false,
  "rule_or_flag": "rule"
}
```

**ag_status_002: Pause – No Conversions High Spend**
```json
{
  "id": "ag_status_002",
  "entity_type": "ad_group",
  "name": "Pause – No Conversions High Spend",
  "type": "status",
  "action_type": "pause_ad_group",
  "scope": "all",
  "conditions": [
    {"metric": "conversions_w30_sum", "op": "eq", "value": 0, "ref": "absolute"},
    {"metric": "cost_w30_sum", "op": "gt", "value": 50000000, "ref": "absolute"}
  ],
  "action": {"type": "pause_ad_group", "magnitude": null},
  "cooldown_days": 30,
  "risk_level": "medium",
  "enabled": true,
  "is_template": false,
  "rule_or_flag": "rule"
}
```

**ag_status_003: Enable – Performance Recovered**
```json
{
  "id": "ag_status_003",
  "entity_type": "ad_group",
  "name": "Enable – Performance Recovered",
  "type": "status",
  "action_type": "enable_ad_group",
  "scope": "all",
  "conditions": [
    {"metric": "ad_group_status", "op": "eq", "value": "PAUSED", "ref": "absolute"},
    {"metric": "roas_w7_mean", "op": "gt", "value": 4.0, "ref": "absolute"}
  ],
  "action": {"type": "enable_ad_group", "magnitude": null},
  "cooldown_days": 14,
  "risk_level": "low",
  "enabled": true,
  "is_template": false,
  "rule_or_flag": "rule"
}
```

**ag_status_004: Pause – Low Optimization Score**
```json
{
  "id": "ag_status_004",
  "entity_type": "ad_group",
  "name": "Pause – Low Optimization Score",
  "type": "status",
  "action_type": "pause_ad_group",
  "scope": "all",
  "conditions": [
    {"metric": "optimization_score", "op": "lt", "value": 0.3, "ref": "absolute"},
    {"metric": "cost_w30_sum", "op": "gt", "value": 100000000, "ref": "absolute"}
  ],
  "action": {"type": "pause_ad_group", "magnitude": null},
  "cooldown_days": 30,
  "risk_level": "medium",
  "enabled": true,
  "is_template": false,
  "rule_or_flag": "rule"
}
```

---

## AD GROUPS FLAGS (18 total)

**Flag-specific fields:**
- `rule_or_flag`: "flag" (not "rule")
- `direction`: "negative" | "positive" | "neutral"
- No `action` field (flags don't have actions)

### PERFORMANCE CATEGORY (8 flags)

**ag_perf_001: ROAS Decline**
```json
{
  "id": "ag_perf_001",
  "entity_type": "ad_group",
  "name": "ROAS Decline",
  "type": "performance",
  "scope": "all",
  "conditions": [
    {"metric": "roas_wow_pct", "op": "lt", "value": -0.30, "ref": "absolute"}
  ],
  "cooldown_days": 7,
  "risk_level": "high",
  "enabled": true,
  "is_template": false,
  "rule_or_flag": "flag",
  "direction": "negative"
}
```

**ag_perf_002: CPA Spike**
```json
{
  "id": "ag_perf_002",
  "entity_type": "ad_group",
  "name": "CPA Spike",
  "type": "performance",
  "scope": "all",
  "conditions": [
    {"metric": "cpa_wow_pct", "op": "gt", "value": 0.50, "ref": "absolute"}
  ],
  "cooldown_days": 7,
  "risk_level": "high",
  "enabled": true,
  "is_template": false,
  "rule_or_flag": "flag",
  "direction": "negative"
}
```

**ag_perf_003: CTR Drop**
```json
{
  "id": "ag_perf_003",
  "entity_type": "ad_group",
  "name": "CTR Drop",
  "type": "performance",
  "scope": "all",
  "conditions": [
    {"metric": "ctr_wow_pct", "op": "lt", "value": -0.25, "ref": "absolute"}
  ],
  "cooldown_days": 7,
  "risk_level": "medium",
  "enabled": true,
  "is_template": false,
  "rule_or_flag": "flag",
  "direction": "negative"
}
```

**ag_perf_004: CVR Decline**
```json
{
  "id": "ag_perf_004",
  "entity_type": "ad_group",
  "name": "CVR Decline",
  "type": "performance",
  "scope": "all",
  "conditions": [
    {"metric": "cvr_wow_pct", "op": "lt", "value": -0.30, "ref": "absolute"}
  ],
  "cooldown_days": 7,
  "risk_level": "high",
  "enabled": true,
  "is_template": false,
  "rule_or_flag": "flag",
  "direction": "negative"
}
```

**ag_perf_005: Conversion Drop**
```json
{
  "id": "ag_perf_005",
  "entity_type": "ad_group",
  "name": "Conversion Drop",
  "type": "performance",
  "scope": "all",
  "conditions": [
    {"metric": "conversions_wow_pct", "op": "lt", "value": -0.40, "ref": "absolute"}
  ],
  "cooldown_days": 7,
  "risk_level": "high",
  "enabled": true,
  "is_template": false,
  "rule_or_flag": "flag",
  "direction": "negative"
}
```

**ag_perf_006: Cost Up Conversions Flat**
```json
{
  "id": "ag_perf_006",
  "entity_type": "ad_group",
  "name": "Cost Up Conversions Flat",
  "type": "performance",
  "scope": "all",
  "conditions": [
    {"metric": "cost_wow_pct", "op": "gt", "value": 0.30, "ref": "absolute"},
    {"metric": "conversions_wow_pct", "op": "lt", "value": 0.10, "ref": "absolute"}
  ],
  "cooldown_days": 7,
  "risk_level": "medium",
  "enabled": true,
  "is_template": false,
  "rule_or_flag": "flag",
  "direction": "negative"
}
```

**ag_perf_007: Wasted Spend Zero Conversions**
```json
{
  "id": "ag_perf_007",
  "entity_type": "ad_group",
  "name": "Wasted Spend Zero Conversions",
  "type": "performance",
  "scope": "all",
  "conditions": [
    {"metric": "conversions_w30_sum", "op": "eq", "value": 0, "ref": "absolute"},
    {"metric": "cost_w30_sum", "op": "gt", "value": 50000000, "ref": "absolute"}
  ],
  "cooldown_days": 14,
  "risk_level": "high",
  "enabled": true,
  "is_template": false,
  "rule_or_flag": "flag",
  "direction": "negative"
}
```

**ag_perf_008: Below Target CPA**
```json
{
  "id": "ag_perf_008",
  "entity_type": "ad_group",
  "name": "Below Target CPA",
  "type": "performance",
  "scope": "all",
  "conditions": [
    {"metric": "cpa_w14_mean", "op": "lt", "value": 0.5, "ref": "target"},
    {"metric": "target_cpa", "op": "is_not_null", "value": null, "ref": "absolute"}
  ],
  "cooldown_days": 14,
  "risk_level": "low",
  "enabled": true,
  "is_template": false,
  "rule_or_flag": "flag",
  "direction": "positive"
}
```

### ANOMALY CATEGORY (6 flags)

**ag_anom_001: Cost Spike**
```json
{
  "id": "ag_anom_001",
  "entity_type": "ad_group",
  "name": "Cost Spike",
  "type": "anomaly",
  "scope": "all",
  "conditions": [
    {"metric": "cost_z", "op": "gt", "value": 2.0, "ref": "absolute"}
  ],
  "cooldown_days": 3,
  "risk_level": "medium",
  "enabled": true,
  "is_template": false,
  "rule_or_flag": "flag",
  "direction": "neutral"
}
```

**ag_anom_002: Cost Drop**
```json
{
  "id": "ag_anom_002",
  "entity_type": "ad_group",
  "name": "Cost Drop",
  "type": "anomaly",
  "scope": "all",
  "conditions": [
    {"metric": "cost_z", "op": "lt", "value": -2.0, "ref": "absolute"}
  ],
  "cooldown_days": 3,
  "risk_level": "medium",
  "enabled": true,
  "is_template": false,
  "rule_or_flag": "flag",
  "direction": "neutral"
}
```

**ag_anom_003: Click Spike**
```json
{
  "id": "ag_anom_003",
  "entity_type": "ad_group",
  "name": "Click Spike",
  "type": "anomaly",
  "scope": "all",
  "conditions": [
    {"metric": "clicks_z", "op": "gt", "value": 2.0, "ref": "absolute"}
  ],
  "cooldown_days": 3,
  "risk_level": "low",
  "enabled": true,
  "is_template": false,
  "rule_or_flag": "flag",
  "direction": "neutral"
}
```

**ag_anom_004: Conversion Drop Anomaly**
```json
{
  "id": "ag_anom_004",
  "entity_type": "ad_group",
  "name": "Conversion Drop Anomaly",
  "type": "anomaly",
  "scope": "all",
  "conditions": [
    {"metric": "conversions_z", "op": "lt", "value": -2.0, "ref": "absolute"}
  ],
  "cooldown_days": 3,
  "risk_level": "high",
  "enabled": true,
  "is_template": false,
  "rule_or_flag": "flag",
  "direction": "neutral"
}
```

**ag_anom_005: High Cost Volatility**
```json
{
  "id": "ag_anom_005",
  "entity_type": "ad_group",
  "name": "High Cost Volatility",
  "type": "anomaly",
  "scope": "all",
  "conditions": [
    {"metric": "cost_cv", "op": "gt", "value": 1.5, "ref": "absolute"}
  ],
  "cooldown_days": 7,
  "risk_level": "medium",
  "enabled": true,
  "is_template": false,
  "rule_or_flag": "flag",
  "direction": "neutral"
}
```

**ag_anom_006: High Click Volatility**
```json
{
  "id": "ag_anom_006",
  "entity_type": "ad_group",
  "name": "High Click Volatility",
  "type": "anomaly",
  "scope": "all",
  "conditions": [
    {"metric": "clicks_cv", "op": "gt", "value": 1.0, "ref": "absolute"}
  ],
  "cooldown_days": 7,
  "risk_level": "low",
  "enabled": true,
  "is_template": false,
  "rule_or_flag": "flag",
  "direction": "neutral"
}
```

### TECHNICAL CATEGORY (4 flags)

**ag_tech_001: Low IS Lost to Rank**
```json
{
  "id": "ag_tech_001",
  "entity_type": "ad_group",
  "name": "Low IS Lost to Rank",
  "type": "technical",
  "scope": "all",
  "conditions": [
    {"metric": "search_impression_share", "op": "lt", "value": 0.4, "ref": "absolute"},
    {"metric": "impression_share_lost_rank", "op": "gt", "value": 0.3, "ref": "absolute"}
  ],
  "cooldown_days": 7,
  "risk_level": "medium",
  "enabled": true,
  "is_template": false,
  "rule_or_flag": "flag",
  "direction": "neutral"
}
```

**ag_tech_002: Low IS Lost to Budget**
```json
{
  "id": "ag_tech_002",
  "entity_type": "ad_group",
  "name": "Low IS Lost to Budget",
  "type": "technical",
  "scope": "all",
  "conditions": [
    {"metric": "search_impression_share", "op": "lt", "value": 0.4, "ref": "absolute"},
    {"metric": "impression_share_lost_budget", "op": "gt", "value": 0.3, "ref": "absolute"}
  ],
  "cooldown_days": 7,
  "risk_level": "medium",
  "enabled": true,
  "is_template": false,
  "rule_or_flag": "flag",
  "direction": "neutral"
}
```

**ag_tech_003: Low Optimization Score**
```json
{
  "id": "ag_tech_003",
  "entity_type": "ad_group",
  "name": "Low Optimization Score",
  "type": "technical",
  "scope": "all",
  "conditions": [
    {"metric": "optimization_score", "op": "lt", "value": 0.4, "ref": "absolute"}
  ],
  "cooldown_days": 14,
  "risk_level": "low",
  "enabled": true,
  "is_template": false,
  "rule_or_flag": "flag",
  "direction": "neutral"
}
```

**ag_tech_004: Low Data Warning**
```json
{
  "id": "ag_tech_004",
  "entity_type": "ad_group",
  "name": "Low Data Warning",
  "type": "technical",
  "scope": "all",
  "conditions": [
    {"metric": "low_data_flag", "op": "eq", "value": true, "ref": "absolute"}
  ],
  "cooldown_days": 7,
  "risk_level": "low",
  "enabled": true,
  "is_template": false,
  "rule_or_flag": "flag",
  "direction": "neutral"
}
```

---

## DATABASE SEEDING

**Create seed script:** `scripts/seed_ad_group_rules.py`

**Pattern (reference campaigns seed script if it exists):**

```python
import duckdb
import json

def seed_ad_group_rules():
    conn = duckdb.connect('warehouse.duckdb')
    
    rules = [
        # All 12 rules from above as Python dicts
        # All 18 flags from above as Python dicts
    ]
    
    for rule in rules:
        conn.execute("""
            INSERT INTO rules (
                id, entity_type, name, type, action_type, scope,
                conditions, action, cooldown_days, risk_level,
                enabled, is_template, rule_or_flag, direction
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            rule['id'],
            rule['entity_type'],
            rule['name'],
            rule['type'],
            rule.get('action_type'),
            json.dumps(rule['scope']),
            json.dumps(rule['conditions']),
            json.dumps(rule.get('action')),
            rule['cooldown_days'],
            rule['risk_level'],
            rule['enabled'],
            rule['is_template'],
            rule['rule_or_flag'],
            rule.get('direction')
        ])
    
    conn.commit()
    conn.close()
    print(f"Seeded {len(rules)} ad group rules and flags")

if __name__ == '__main__':
    seed_ad_group_rules()
```

**Run after implementation:**
```powershell
cd C:\Users\User\Desktop\gads-data-layer
.\.venv\Scripts\Activate.ps1
python scripts/seed_ad_group_rules.py
```

---

## SUCCESS CRITERIA

- [ ] Ad Groups page has Rules & Flags tab (matches Campaigns UI)
- [ ] Modal Step 1 loads ad groups from `/api/ad-groups-list`
- [ ] Modal Step 3 shows ONLY Bid and Status (NO Budget)
- [ ] Modal Step 4 metrics match `AD_GROUP_METRIC_MAP`
- [ ] Modal Step 4 actions include ad_group types only (no budget actions)
- [ ] Rules table shows 12 rules with Bid/Status badges
- [ ] Flags table shows 18 flags with Performance/Anomaly/Technical badges
- [ ] Filter pills work (Rules: All/Bid/Status, Flags: All/Performance/Anomaly/Technical)
- [ ] Create new rule saves with `entity_type='ad_group'`
- [ ] Edit rule loads correctly
- [ ] Delete rule works
- [ ] Toggle enable/disable works
- [ ] Save as template works
- [ ] Templates tab shows ad group templates
- [ ] No console errors in browser DevTools
- [ ] No Flask errors in terminal
- [ ] Database shows 30 rows with `entity_type='ad_group'`
- [ ] Engine can load ad group rules without errors

---

## TESTING INSTRUCTIONS

1. **Start Flask:**
```powershell
taskkill /IM python.exe /F
cd C:\Users\User\Desktop\gads-data-layer
.\.venv\Scripts\Activate.ps1
python act_dashboard/app.py
```

2. **Seed database:**
```powershell
python scripts/seed_ad_group_rules.py
```

3. **Test in Opera:** http://localhost:5000/ad_groups

4. **Verify Rules & Flags tab visible**

5. **Click "Add rule or flag"** → Modal opens

6. **Step 1:** Verify ad groups loaded (not campaigns)

7. **Step 2:** Select "Rule" → Next

8. **Step 3:** Verify ONLY Bid and Status cards (NO Budget)

9. **Select Bid → Next**

10. **Step 4:** Create test rule → Save

11. **Verify rule appears in table** with correct badge and type

12. **Switch to Flags sub-tab** → Verify 18 flags visible

13. **Test filter pills** (All/Bid/Status for rules)

14. **Test Edit/Delete/Toggle/Template** actions

15. **Check database:**
```python
import duckdb
conn = duckdb.connect('warehouse.duckdb')
result = conn.execute("SELECT COUNT(*), entity_type FROM rules WHERE entity_type='ad_group' GROUP BY entity_type").fetchall()
print(result)  # Should show [(30, 'ad_group')]
```

16. **Test engine:**
```python
from act_autopilot.recommendations_engine import generate_recommendations
recs = generate_recommendations(entity_type='ad_group', customer_id='1254895944', dry_run=True)
print(f"Generated {len(recs)} ad group recommendations")
```

---

## REFERENCE FILES

**Primary (copy from these):**
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\campaigns.html`
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\campaigns.py`

**Components:**
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\components\rules_flow_builder.html`
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\components\rules_flags_tab.html`

**CSS:**
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\static\css\rules.css`

**Engine:**
- `C:\Users\User\Desktop\gads-data-layer\act_autopilot\recommendations_engine.py` — Check `AD_GROUP_METRIC_MAP`

**Routes:**
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\recommendations.py` — Check `_ACTION_TYPE_TO_RULE_TYPE` and `get_action_label()`

**Investigation:**
- `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_106_INVESTIGATION_REPORT.md`
- `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_106_HANDOFF.md`

**Rules spec:**
- `C:\Users\User\Desktop\gads-data-layer\docs\RULES_FLAGS_DESIGN_ALL_ENTITIES1.md`

---

## CRITICAL REMINDERS

1. **NO Budget category** — Ad Groups have Bid and Status only. Remove Budget from Step 3 type grid.

2. **Scope JSON format** — Use `"scope": "all"` or `{"scope": {"ad_groups": ["123"]}}` NOT `{"campaigns": [...]}`

3. **Action types** — Use exact strings: `increase_tcpa_target` NOT `increase_tcpa`

4. **Operators** — Use "gt", "lt", "gte", "lte", "eq", "is_not_null" NOT symbols

5. **Decimal ratios** — WoW % thresholds are decimals: -0.30 NOT -30

6. **Micros** — Cost values in micros: 100000000 = £100

7. **IS NOT NULL checks** — Always use `{"op": "is_not_null", "value": null}` for target_cpa conditions

8. **Entity filter** — Duplicate detection MUST include `WHERE entity_type='ad_group'`

9. **Metric verification** — All metrics MUST exist in `AD_GROUP_METRIC_MAP` in recommendations_engine.py

10. **Copy exactly** — Copy Campaigns UI structure exactly, change ONLY entity-specific parts

---

**Document Version:** 2.0 (Improved)
**Last Updated:** 2026-03-21
