# CHAT 109: ADS RULES & FLAGS IMPLEMENTATION

**Date:** 2026-03-21
**Estimated Time:** 2–3 hours
**Priority:** HIGH
**Dependencies:** Chat 108 (Keywords) complete ✅

---

## CONTEXT

Chat 108 successfully implemented Keywords Rules & Flags with full CRUD functionality. All 5 bug fixes pre-applied, all success criteria passed, zero console errors across all pages.

**Sequential expansion progress:**
- ✅ Chat 107: Ad Groups (12 rules + 18 flags = 30 rows)
- ✅ Chat 108: Keywords (12 rules + 20 flags = 32 rows)
- 🔄 **Chat 109: Ads (8 rules + 15 flags = 23 rows) ← YOU ARE HERE**
- 📋 Chat 110: Shopping (next and final)

**This brief implements Ads using the EXACT same pattern as Keywords, with all bug fixes pre-applied.**

---

## OBJECTIVE

Implement Ads Rules & Flags tab on the Ads page with full CRUD functionality, following the proven Keywords implementation pattern.

---

## DELIVERABLES

### Files to CREATE:

**1. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\components\ad_rules_flags_tab.html`**
- Ads-specific rules & flags tab UI
- **Pattern:** Copy `kw_rules_flags_tab.html` exactly, replace all `kw` prefixes with `ad`
- **Search/Replace:**
  - `kw-` → `ad-` (CSS IDs)
  - `kw` → `ad` (JavaScript function prefixes)
  - `_kwRfb` → `_adRfb` (state variables)
  - `Keywords` → `Ads`
  - `/keywords/` → `/ads/` (API endpoints)

**2. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\components\ad_rules_flow_builder.html`**
- Ads-specific flow builder modal (10 steps for rules, 6 for flags)
- **Pattern:** Copy `kw_rules_flow_builder.html` exactly, same search/replace as above
- **CRITICAL ADDITIONS:**
  - Line ~50: Modal overlay must have `style="display:none;"`
  - Line ~916: `adRfbAutoRisk()` function MUST start with `if (_adRfbEditId) return;`
  
**3. `C:\Users\User\Desktop\gads-data-layer\scripts\seed_ad_rules.py`**
- Seeds 23 rows with `entity_type='ad'`: 8 rules + 15 flags
- **Pattern:** Copy structure from `seed_keyword_rules.py`
- **IMPORTANT:** Run this script immediately after creation to populate database

### Files to MODIFY:

**4. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\ads.html`**

**IMPORTANT:** ads.html already exists. Find the existing tab structure and add the Rules & Flags tab.

Find the tab navigation section (look for `<ul class="nav nav-tabs">`), add this button:
```html
<li class="nav-item">
    <a class="nav-link" id="ads-rules-link" data-bs-toggle="tab" href="#ads-rules-tab">
        <i class="material-symbols-outlined">rule</i> Rules & Flags
    </a>
</li>
```

Find the tab content section (look for existing `<div class="tab-pane"...` blocks), add this tab BEFORE the closing `</div>`:
```html
<!-- Rules & Flags Tab -->
<div class="tab-pane fade" id="ads-rules-tab" role="tabpanel">
    {% include 'components/ad_rules_flags_tab.html' %}
</div>
```

**5. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\ads.py`**

**Add required imports at the top of the file** (if not already present):
```python
import json
import duckdb
from flask import jsonify, request
from act_dashboard.config import get_current_config
```

**Add these functions at the end of the file, before the final return statement:**

```python
# ============================================================================
# RULES & FLAGS - ADS
# ============================================================================

def _get_warehouse():
    """Helper to get warehouse connection"""
    return duckdb.connect('warehouse.duckdb')

@ads_bp.route('/ads/rules', methods=['GET'])
def ad_list_rules():
    """List all ad rules and flags"""
    conn = _get_warehouse()
    
    # CRITICAL: Filter by entity_type='ad'
    rules = conn.execute("""
        SELECT * FROM rules 
        WHERE entity_type = 'ad' 
        ORDER BY created_at DESC
    """).fetchall()
    
    return jsonify({
        'success': True,
        'rules': [dict(r) for r in rules]
    })

@ads_bp.route('/ads/rules/create', methods=['POST'])
def ad_create_rule():
    """Create new ad rule or flag"""
    data = request.get_json()
    conn = _get_warehouse()
    
    # Set entity_type to 'ad'
    data['entity_type'] = 'ad'
    
    # Insert into rules table
    conn.execute("""
        INSERT INTO rules (
            name, entity_type, rule_or_flag, type, action_type,
            enabled, conditions, change_pct, cooldown_days, 
            risk_level, scope, is_template
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        data['name'],
        'ad',  # CRITICAL
        data['rule_or_flag'],
        data['type'],
        data.get('action_type'),
        data.get('enabled', True),
        json.dumps(data['conditions']),
        data.get('change_pct'),
        data.get('cooldown_days', 14),
        data.get('risk_level', 'medium'),
        json.dumps(data.get('scope', {'scope': 'all'})),
        data.get('is_template', False)
    ])
    
    return jsonify({'success': True})

@ads_bp.route('/ads/rules/<int:rule_id>/update', methods=['PUT'])
def ad_update_rule(rule_id):
    """Update existing ad rule or flag"""
    data = request.get_json()
    conn = _get_warehouse()
    
    # Verify entity_type is 'ad'
    existing = conn.execute(
        "SELECT entity_type FROM rules WHERE id = ?", 
        [rule_id]
    ).fetchone()
    
    if not existing or existing[0] != 'ad':
        return jsonify({'success': False, 'error': 'Invalid rule'}), 404
    
    conn.execute("""
        UPDATE rules SET
            name = ?,
            conditions = ?,
            change_pct = ?,
            cooldown_days = ?,
            risk_level = ?,
            scope = ?
        WHERE id = ? AND entity_type = 'ad'
    """, [
        data['name'],
        json.dumps(data['conditions']),
        data.get('change_pct'),
        data.get('cooldown_days'),
        data.get('risk_level'),
        json.dumps(data.get('scope')),
        rule_id
    ])
    
    return jsonify({'success': True})

@ads_bp.route('/ads/rules/<int:rule_id>/delete', methods=['DELETE'])
def ad_delete_rule(rule_id):
    """Delete ad rule or flag"""
    conn = _get_warehouse()
    
    conn.execute(
        "DELETE FROM rules WHERE id = ? AND entity_type = 'ad'",
        [rule_id]
    )
    
    return jsonify({'success': True})

@ads_bp.route('/ads/rules/<int:rule_id>/toggle', methods=['POST'])
def ad_toggle_rule(rule_id):
    """Toggle ad rule enabled status"""
    conn = _get_warehouse()
    
    conn.execute("""
        UPDATE rules 
        SET enabled = NOT enabled 
        WHERE id = ? AND entity_type = 'ad'
    """, [rule_id])
    
    return jsonify({'success': True})

@ads_bp.route('/ads/rules/<int:rule_id>/save-as-template', methods=['POST'])
def ad_save_as_template(rule_id):
    """Save ad rule as template"""
    conn = _get_warehouse()
    
    # Get existing rule
    rule = conn.execute(
        "SELECT * FROM rules WHERE id = ? AND entity_type = 'ad'",
        [rule_id]
    ).fetchone()
    
    if not rule:
        return jsonify({'success': False, 'error': 'Rule not found'}), 404
    
    # Create template copy
    conn.execute("""
        INSERT INTO rules (
            name, entity_type, rule_or_flag, type, action_type,
            enabled, conditions, change_pct, cooldown_days,
            risk_level, scope, is_template
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        rule['name'] + ' (Template)',
        'ad',
        rule['rule_or_flag'],
        rule['type'],
        rule['action_type'],
        False,
        rule['conditions'],
        rule['change_pct'],
        rule['cooldown_days'],
        rule['risk_level'],
        rule['scope'],
        True
    ])
    
    return jsonify({'success': True})

@ads_bp.route('/api/ads-list', methods=['GET'])
def ad_api_ads_list():
    """API endpoint for ad scope picker"""
    config = get_current_config()
    customer_id = str(config.config.get("customer_id"))
    
    conn = duckdb.connect('warehouse.duckdb')
    conn.execute("ATTACH 'warehouse_readonly.duckdb' AS ro (READ_ONLY)")
    
    ads = conn.execute("""
        SELECT 
            ad_id,
            ad_name,
            ad_group_name
        FROM ro.analytics.ad_daily
        WHERE customer_id = ?
        ORDER BY ad_name
    """, [customer_id]).fetchall()
    
    conn.close()
    
    return jsonify({
        'success': True,
        'ads': [
            {
                'id': str(a[0]),
                'name': f"{a[1]} ({a[2]})"
            }
            for a in ads
        ]
    })

def rfb_ads(config):
    """Context data for ads rules flow builder"""
    return {
        'entity_type': 'ad',
        'entity_label': 'Ads',
        'entity_label_singular': 'Ad',
        
        # Metric options for Step 4 (condition builder)
        'metrics': [
            # Performance metrics
            {'value': 'roas_w14_mean', 'label': 'ROAS (14d)', 'has_prev': True},
            {'value': 'roas_w7_mean', 'label': 'ROAS (7d)', 'has_prev': True},
            {'value': 'roas_w30_mean', 'label': 'ROAS (30d)', 'has_prev': True},
            {'value': 'cpa_w14_mean', 'label': 'CPA (14d)', 'has_prev': True},
            {'value': 'cpa_w7_mean', 'label': 'CPA (7d)', 'has_prev': True},
            {'value': 'cpa_w30_mean', 'label': 'CPA (30d)', 'has_prev': True},
            {'value': 'ctr_w14_mean', 'label': 'CTR (14d)', 'has_prev': True},
            {'value': 'ctr_w7_mean', 'label': 'CTR (7d)', 'has_prev': True},
            {'value': 'cvr_w7_mean', 'label': 'CVR (7d)', 'has_prev': True},
            
            # Volume metrics
            {'value': 'conversions_w7_sum', 'label': 'Conversions (7d)', 'has_prev': True},
            {'value': 'conversions_w14_sum', 'label': 'Conversions (14d)', 'has_prev': True},
            {'value': 'conversions_w30_sum', 'label': 'Conversions (30d)', 'has_prev': True},
            {'value': 'clicks_w7_sum', 'label': 'Clicks (7d)', 'has_prev': True},
            {'value': 'clicks_w14_sum', 'label': 'Clicks (14d)', 'has_prev': True},
            {'value': 'impressions_w7_sum', 'label': 'Impressions (7d)', 'has_prev': True},
            {'value': 'cost_w7_sum', 'label': 'Cost (7d)', 'has_prev': True},
            {'value': 'cost_w14_sum', 'label': 'Cost (14d)', 'has_prev': True},
            {'value': 'cost_w30_sum', 'label': 'Cost (30d)', 'has_prev': True},
            
            # Ad-specific metrics
            {'value': 'ad_strength', 'label': 'Ad Strength', 'has_prev': False},
            {'value': 'search_impression_share', 'label': 'Impression Share', 'has_prev': False},
            
            # Anomaly detection
            {'value': 'cost_w14_cv', 'label': 'Cost Volatility (14d CV)', 'has_prev': False},
            {'value': 'clicks_w7_vs_prev_pct', 'label': 'Clicks WoW %', 'has_prev': False},
            {'value': 'cost_w7_vs_prev_pct', 'label': 'Cost WoW %', 'has_prev': False},
            {'value': 'ctr_w7_vs_prev_pct', 'label': 'CTR WoW %', 'has_prev': False},
            {'value': 'conversions_w7_vs_prev_pct', 'label': 'Conversions WoW %', 'has_prev': False},
            {'value': 'impressions_w7_vs_prev_pct', 'label': 'Impressions WoW %', 'has_prev': False},
            
            # Status
            {'value': 'ad_status', 'label': 'Ad Status', 'has_prev': False},
            {'value': 'low_data_flag', 'label': 'Low Data Flag', 'has_prev': False},
        ],
        
        # Action types for Step 4 (action builder)
        # CRITICAL: Ads only have status actions (no bid actions)
        'action_types': {
            'status': [
                {'value': 'pause', 'label': 'Pause ad'},
                {'value': 'enable', 'label': 'Enable ad'},
            ]
        }
    }
```

**Also register the context function.** Find where the ads route renders the template (search for `render_template('ads.html'`), and add `'rfb_ads': rfb_ads(config),` to the context dict.

**6. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\app.py`**

Find the CSRF exemptions section (around line 200). After the keywords exemptions, add:

```python
# Ads Rules & Flags CRUD  
from act_dashboard.routes.ads import (
    ad_list_rules, ad_create_rule, ad_update_rule,
    ad_delete_rule, ad_toggle_rule, ad_save_as_template
)
csrf.exempt(ad_list_rules)
csrf.exempt(ad_create_rule)
csrf.exempt(ad_update_rule)
csrf.exempt(ad_delete_rule)
csrf.exempt(ad_toggle_rule)
csrf.exempt(ad_save_as_template)
```

**7. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\static\css\rules.css`**

Find line ~883 (search for `#kw-rules-toast-wrap`). Change to:
```css
#rules-toast-wrap,
#ag-rules-toast-wrap,
#kw-rules-toast-wrap,
#ad-rules-toast-wrap {
    position: fixed;
    bottom: 24px;
    right: 24px;
    z-index: 1060;
    max-width: 400px;
}
```

**8. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_109_HANDOFF.md`** — CREATE

**9. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_109_SUMMARY.md`** — CREATE

---

## ADS RULES & FLAGS SPECIFICATION

**Total:** 23 rows (8 rules + 15 flags)
**Source:** RULES_FLAGS_DESIGN_ALL_ENTITIES1.md (Ads section)

**CRITICAL NOTES:**
- Operators: `"gt"`, `"lt"`, `"gte"`, `"lte"`, `"eq"`, `"in"` (NOT symbols like >, <)
- WoW percentages: Decimals (`-0.30` NOT `-30`)
- Cost values: Micros (`30000000` = £30)
- Ad strength: Use `"in"` operator with JSON array
- Scope: `{"scope": "all"}` or `{"scope": {"ads": ["123", "456"]}}`

### RULES (8 total: All Status)

**IMPORTANT:** Ads have NO bid rules. All 8 rules are Status rules (pause/enable only).

#### COMPLETE RULE EXAMPLES (Rules 1-4 shown in full, 5-8 follow same pattern)

**1. AD-STATUS-001: Pause – Poor CTR**
```json
{
  "name": "Pause – Poor CTR",
  "entity_type": "ad",
  "rule_or_flag": "rule",
  "type": "status",
  "action_type": "pause",
  "enabled": true,
  "conditions": [
    {"metric": "ctr_w14_mean", "op": "lt", "value": 0.015, "ref": null},
    {"metric": "clicks_w14_sum", "op": "gte", "value": 50, "ref": null}
  ],
  "change_pct": null,
  "cooldown_days": 30,
  "risk_level": "medium",
  "scope": {"scope": "all"}
}
```

**2. AD-STATUS-002: Pause – Zero Conversions High Spend**
```json
{
  "name": "Pause – Zero Conversions High Spend",
  "entity_type": "ad",
  "rule_or_flag": "rule",
  "type": "status",
  "action_type": "pause",
  "enabled": true,
  "conditions": [
    {"metric": "conversions_w30_sum", "op": "eq", "value": 0, "ref": null},
    {"metric": "cost_w30_sum", "op": "gt", "value": 30000000, "ref": null}
  ],
  "change_pct": null,
  "cooldown_days": 30,
  "risk_level": "medium",
  "scope": {"scope": "all"}
}
```

**3. AD-STATUS-003: Pause – Low ROAS**
```json
{
  "name": "Pause – Low ROAS",
  "entity_type": "ad",
  "rule_or_flag": "rule",
  "type": "status",
  "action_type": "pause",
  "enabled": true,
  "conditions": [
    {"metric": "roas_w14_mean", "op": "lt", "value": 1.5, "ref": null},
    {"metric": "conversions_w14_sum", "op": "gte", "value": 5, "ref": null}
  ],
  "change_pct": null,
  "cooldown_days": 30,
  "risk_level": "medium",
  "scope": {"scope": "all"}
}
```

**4. AD-STATUS-004: Pause – Poor Ad Strength**
```json
{
  "name": "Pause – Poor Ad Strength",
  "entity_type": "ad",
  "rule_or_flag": "rule",
  "type": "status",
  "action_type": "pause",
  "enabled": true,
  "conditions": [
    {"metric": "ad_strength", "op": "in", "value": ["POOR", "AVERAGE"], "ref": null},
    {"metric": "cost_w14_sum", "op": "gt", "value": 20000000, "ref": null}
  ],
  "change_pct": null,
  "cooldown_days": 30,
  "risk_level": "medium",
  "scope": {"scope": "all"}
}
```
**NOTE:** The `"in"` operator uses a JSON array as the value. Store it as-is in the database.

**5. AD-STATUS-005: Enable – Ad Strength Improved**
- Conditions: ad_status = 'PAUSED' AND ad_strength IN ['GOOD', 'EXCELLENT']
- Action: Enable, Cooldown: 14d, Risk: low

**6. AD-STATUS-006: Pause – High CPA**
- Conditions: cpa_w14_mean > £80 AND conversions_w14_sum ≥ 3
- Action: Pause, Cooldown: 30d, Risk: medium

**7. AD-STATUS-007: Enable – Performance Recovered**
- Conditions: ad_status = 'PAUSED' AND roas_w7_mean > 4.0 AND conversions_w7_sum ≥ 3
- Action: Enable, Cooldown: 14d, Risk: low

**8. AD-STATUS-008: Pause – CTR Declining Trend**
- Conditions: ctr_w7_vs_prev_pct < -0.40 AND clicks_w7_sum ≥ 30
- Action: Pause, Cooldown: 30d, Risk: medium

### FLAGS (15 total: 7 Performance + 4 Anomaly + 4 Technical)

**CRITICAL:** All flags use `"rule_or_flag": "flag"` (not "rule")

#### COMPLETE FLAG EXAMPLES (Flags 1-4 shown in full, 5-15 follow same pattern)

**1. AD-PERF-001: CTR Drop – Creative Fatigue**
```json
{
  "name": "CTR Drop – Creative Fatigue",
  "entity_type": "ad",
  "rule_or_flag": "flag",
  "type": "performance",
  "action_type": null,
  "enabled": true,
  "conditions": [
    {"metric": "ctr_w7_vs_prev_pct", "op": "lt", "value": -0.30, "ref": null},
    {"metric": "clicks_w7_sum", "op": "gte", "value": 30, "ref": null}
  ],
  "change_pct": null,
  "cooldown_days": 7,
  "risk_level": "high",
  "scope": {"scope": "all"}
}
```

**2. AD-PERF-002: ROAS Decline**
```json
{
  "name": "ROAS Decline",
  "entity_type": "ad",
  "rule_or_flag": "flag",
  "type": "performance",
  "action_type": null,
  "enabled": true,
  "conditions": [
    {"metric": "roas_w7_vs_prev_pct", "op": "lt", "value": -0.30, "ref": null},
    {"metric": "conversions_w7_sum", "op": "gte", "value": 3, "ref": null}
  ],
  "change_pct": null,
  "cooldown_days": 7,
  "risk_level": "high",
  "scope": {"scope": "all"}
}
```

**3. AD-PERF-003: CVR Drop**
```json
{
  "name": "CVR Drop",
  "entity_type": "ad",
  "rule_or_flag": "flag",
  "type": "performance",
  "action_type": null,
  "enabled": true,
  "conditions": [
    {"metric": "cvr_w7_vs_prev_pct", "op": "lt", "value": -0.30, "ref": null},
    {"metric": "conversions_w7_sum", "op": "gte", "value": 3, "ref": null}
  ],
  "change_pct": null,
  "cooldown_days": 7,
  "risk_level": "high",
  "scope": {"scope": "all"}
}
```

**4. AD-PERF-004: Wasted Spend Zero Conversions**
```json
{
  "name": "Wasted Spend Zero Conversions",
  "entity_type": "ad",
  "rule_or_flag": "flag",
  "type": "performance",
  "action_type": null,
  "enabled": true,
  "conditions": [
    {"metric": "conversions_w30_sum", "op": "eq", "value": 0, "ref": null},
    {"metric": "cost_w30_sum", "op": "gt", "value": 30000000, "ref": null}
  ],
  "change_pct": null,
  "cooldown_days": 30,
  "risk_level": "high",
  "scope": {"scope": "all"}
}
```

**REMAINING FLAGS (5-15) - Summary:**

**Performance (5-7):**
5. Low Impression Share — search_impression_share < 0.30
6. CPA Spike — cpa_w7_vs_prev_pct > 0.50 AND conversions_w7_sum ≥ 2
7. Low CTR High Impressions — ctr_w7_mean < 0.01 AND impressions_w7_sum > 1000

**Anomaly (8-11):**
8. Cost Spike — cost_w14_cv > 2.0
9. Click Drop — clicks_w7_vs_prev_pct < -0.50 AND clicks_w7_sum ≥ 20
10. Conversion Drop — conversions_w7_vs_prev_pct < -0.50 AND conversions_w7_sum ≥ 2
11. Impression Drop — impressions_w7_vs_prev_pct < -0.40 AND impressions_w7_sum ≥ 500

**Technical (12-15):**
12. Poor Ad Strength — ad_strength = 'POOR'
13. Average Ad Strength High Spend — ad_strength = 'AVERAGE' AND cost_w14_sum > 50000000
14. Ad Approval Issues — ad_status = 'DISAPPROVED'
15. Low Data Warning — low_data_flag = TRUE

---

## SEED SCRIPT STRUCTURE

**File:** `C:\Users\User\Desktop\gads-data-layer\scripts\seed_ad_rules.py`

```python
import duckdb
import json

def seed_ad_rules():
    conn = duckdb.connect('warehouse.duckdb')
    
    # Delete existing ad rules/flags
    conn.execute("DELETE FROM rules WHERE entity_type = 'ad'")
    
    rules = [
        # Rule 1: Pause – Poor CTR
        {
            'name': 'Pause – Poor CTR',
            'entity_type': 'ad',
            'rule_or_flag': 'rule',
            'type': 'status',
            'action_type': 'pause',
            'enabled': True,
            'conditions': json.dumps([
                {'metric': 'ctr_w14_mean', 'op': 'lt', 'value': 0.015, 'ref': None},
                {'metric': 'clicks_w14_sum', 'op': 'gte', 'value': 50, 'ref': None}
            ]),
            'change_pct': None,
            'cooldown_days': 30,
            'risk_level': 'medium',
            'scope': json.dumps({'scope': 'all'}),
            'is_template': False
        },
        # Rule 2: Pause – Zero Conversions High Spend
        {
            'name': 'Pause – Zero Conversions High Spend',
            'entity_type': 'ad',
            'rule_or_flag': 'rule',
            'type': 'status',
            'action_type': 'pause',
            'enabled': True,
            'conditions': json.dumps([
                {'metric': 'conversions_w30_sum', 'op': 'eq', 'value': 0, 'ref': None},
                {'metric': 'cost_w30_sum', 'op': 'gt', 'value': 30000000, 'ref': None}
            ]),
            'change_pct': None,
            'cooldown_days': 30,
            'risk_level': 'medium',
            'scope': json.dumps({'scope': 'all'}),
            'is_template': False
        },
        # Rule 4: Pause – Poor Ad Strength (NOTE: Uses "in" operator with array)
        {
            'name': 'Pause – Poor Ad Strength',
            'entity_type': 'ad',
            'rule_or_flag': 'rule',
            'type': 'status',
            'action_type': 'pause',
            'enabled': True,
            'conditions': json.dumps([
                {'metric': 'ad_strength', 'op': 'in', 'value': ['POOR', 'AVERAGE'], 'ref': None},
                {'metric': 'cost_w14_sum', 'op': 'gt', 'value': 20000000, 'ref': None}
            ]),
            'change_pct': None,
            'cooldown_days': 30,
            'risk_level': 'medium',
            'scope': json.dumps({'scope': 'all'}),
            'is_template': False
        },
        # ... (add all 23 rows here - 8 rules + 15 flags)
    ]
    
    for rule in rules:
        conn.execute("""
            INSERT INTO rules (
                name, entity_type, rule_or_flag, type, action_type,
                enabled, conditions, change_pct, cooldown_days,
                risk_level, scope, is_template
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            rule['name'],
            rule['entity_type'],
            rule['rule_or_flag'],
            rule['type'],
            rule.get('action_type'),
            rule['enabled'],
            rule['conditions'],
            rule.get('change_pct'),
            rule['cooldown_days'],
            rule['risk_level'],
            rule['scope'],
            rule['is_template']
        ])
    
    conn.close()
    print(f"✅ Seeded {len(rules)} ad rules and flags")

if __name__ == '__main__':
    seed_ad_rules()
```

---

## SUCCESS CRITERIA

**Before reporting complete, ALL must pass:**

- [ ] Seed script runs successfully
- [ ] Database shows 23 new rows with `entity_type='ad'`
- [ ] Ads page loads without errors
- [ ] Rules & Flags tab visible on Ads page
- [ ] Modal hidden on page load (NOT visible at bottom)
- [ ] Click "Add rule or flag" → Modal appears centered with dark overlay
- [ ] Click Close/X → Modal disappears completely
- [ ] Rules tab shows 8 ad rules (all Status - no Bid rules visible)
- [ ] Flags tab shows 15 ad flags (7 Performance + 4 Anomaly + 4 Technical)
- [ ] NO campaign, ad group, or keyword rules visible on Ads page
- [ ] Campaigns page: 18 rules only ✓
- [ ] Ad Groups page: 12 rules only ✓
- [ ] Keywords page: 12 rules only ✓
- [ ] Create new rule → Saves successfully
- [ ] Edit existing rule → Modal pre-populates correctly
- [ ] Edit rule with "Low" risk → Save → Still shows "Low"
- [ ] Edit rule with "Medium" risk → Save → Still shows "Medium"
- [ ] Toggle rule on/off → Updates correctly
- [ ] Delete rule → Removes from list
- [ ] Save as template → Creates template
- [ ] Toast slides in from bottom-right corner
- [ ] Zero console errors on Ads page
- [ ] Zero console errors on all other pages
- [ ] Flask starts cleanly with no errors

---

## TESTING INSTRUCTIONS

### Step 1: Run Seed Script
```powershell
cd C:\Users\User\Desktop\gads-data-layer
.\.venv\Scripts\Activate.ps1
python scripts/seed_ad_rules.py
```
**Expected:** "✅ Seeded 23 ad rules and flags"

### Step 2: Verify Database
```powershell
python -c "import duckdb; conn = duckdb.connect('warehouse.duckdb'); print('Ad rules:', conn.execute('SELECT COUNT(*) FROM rules WHERE entity_type=\"ad\"').fetchone()[0]); conn.close()"
```
**Expected:** "Ad rules: 23"

### Step 3: Start Flask
```powershell
taskkill /IM python.exe /F
python act_dashboard/app.py
```

### Step 4: Test Ads Page
- Open: `http://localhost:5000/ads`
- Click Rules & Flags tab
- Verify modal hidden on load
- Click "Add rule or flag"
- Verify modal centered with overlay
- Count rules: 8 (all Status)
- Click Flags tab
- Count flags: 15

### Step 5: Test Edit
- Edit first rule
- Note risk level
- Don't change anything
- Save
- Verify risk level unchanged

### Step 6: Test Toast
- Edit any rule
- Change cooldown 30d → 14d
- Save
- Verify toast from bottom-right

### Step 7: Regression Check
- Campaigns → Rules & Flags → 18 rules ✓
- Ad Groups → Rules & Flags → 12 rules ✓
- Keywords → Rules & Flags → 12 rules ✓
- Ads → Rules & Flags → 8 rules ✓

### Step 8: Console Check
- F12 → Console
- Navigate: Ads → Campaigns → Ad Groups → Keywords → Ads
- Verify zero errors

### Step 9: Report
- Create CHAT_109_SUMMARY.md
- Create CHAT_109_HANDOFF.md
- Report: "Chat 109 complete - all 24 success criteria passed"

---

## CRITICAL REMINDERS

**From KNOWN_PITFALLS.md (Pitfalls 76-80):**

1. Filter EVERY query: `WHERE entity_type='ad'`
2. Modal overlay: `style="display:none;"`
3. Modal CSS: Full positioning required
4. Toast CSS: `#ad-rules-toast-wrap` in combined rule
5. Auto-risk guard: `if (_adRfbEditId) return;`

**From LESSONS_LEARNED.md (Lessons 93-97):**

1. NEVER rely on seeded data - always filter
2. Modal visibility: `.show` class toggle
3. Copy CSS from working entity
4. Add toast container ID immediately
5. Auto-calc for NEW rules only

---

## SPECIAL NOTES FOR ADS

### 1. Ads Have NO Bid Rules
- All 8 rules are Status rules (pause/enable only)
- No bid adjustments at ad level
- Action types: ONLY `'pause'` and `'enable'`
- No `change_pct` needed

### 2. "in" Operator for Ad Strength
Some conditions use `"op": "in"` with JSON arrays:
```json
{"metric": "ad_strength", "op": "in", "value": ["POOR", "AVERAGE"], "ref": null}
```
Store this AS-IS in the database. The engine will handle the array comparison.

### 3. Ad Strength Values
Valid values: `"POOR"`, `"AVERAGE"`, `"GOOD"`, `"EXCELLENT"`
Always use uppercase strings.

### 4. Ad Status Values
Valid values: `"PAUSED"`, `"ENABLED"`, `"DISAPPROVED"`
Always use uppercase strings.

---

## REFERENCE FILES

**Copy exactly (with prefix replacements):**
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\components\kw_rules_flags_tab.html`
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\components\kw_rules_flow_builder.html`

**Use as pattern:**
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\keywords.py`
- `C:\Users\User\Desktop\gads-data-layer\scripts\seed_keyword_rules.py`
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\keywords.html`

---

## CONSTRAINTS

- Do NOT modify campaigns/ad_groups/keywords files (except CSS for toast)
- Do NOT change entity_type for existing rules
- Do NOT create new tables
- Use existing `rules` table with `entity_type='ad'`

---

**Document Version:** 2.0 (Improved - Ready for Claude Code)
**Last Updated:** 2026-03-21
**Estimated Completion:** 2–3 hours
