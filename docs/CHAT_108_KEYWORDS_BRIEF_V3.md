# CHAT 108: KEYWORDS RULES & FLAGS IMPLEMENTATION

**Date:** 2026-03-21
**Estimated Time:** 2–3 hours
**Priority:** HIGH
**Dependencies:** Chat 107 (Ad Groups) complete ✅

---

## CONTEXT

Chat 107 successfully implemented Ad Groups Rules & Flags with full CRUD functionality. Found and fixed 5 bugs:
1. Missing entity_type filter (campaigns showing ad group rules)
2. Modal visible on page load (display:none missing)
3. Modal at bottom of page (position:fixed CSS incomplete)
4. Toast at bottom of page (CSS missing for entity-specific toast container)
5. Risk level always "High" (auto-risk overwriting dropdown on edit)

All lessons documented in KNOWN_PITFALLS.md (pitfalls 76-80) and LESSONS_LEARNED.md (lessons 93-97).

**This brief implements Keywords using the EXACT same pattern as Ad Groups, with all bug fixes pre-applied.**

---

## OBJECTIVE

Implement Keywords Rules & Flags tab on the Keywords page with full CRUD functionality, following the proven Ad Groups implementation pattern.

---

## DELIVERABLES

### Files to CREATE:

**1. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\components\kw_rules_flags_tab.html`**
- Keywords-specific rules & flags tab UI
- **Pattern:** Copy `ag_rules_flags_tab.html` exactly, replace all `ag` prefixes with `kw`
- **Search/Replace:**
  - `ag-` → `kw-` (CSS IDs)
  - `ag` → `kw` (JavaScript function prefixes)
  - `_agRfb` → `_kwRfb` (state variables)
  - `Ad Groups` → `Keywords`
  - `/ad_groups/` → `/keywords/` (API endpoints)

**2. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\components\kw_rules_flow_builder.html`**
- Keywords-specific flow builder modal (10 steps for rules, 6 for flags)
- **Pattern:** Copy `ag_rules_flow_builder.html` exactly, same search/replace as above
- **CRITICAL ADDITIONS:**
  - Line ~50: Modal overlay must have `style="display:none;"`
  - Line ~916: `kwRfbAutoRisk()` function MUST start with `if (_kwRfbEditId) return;`
  
**3. `C:\Users\User\Desktop\gads-data-layer\scripts\seed_keyword_rules.py`**
- Seeds 32 rows with `entity_type='keyword'`: 12 rules + 20 flags
- **Pattern:** Copy structure from `seed_ad_group_rules.py`
- **IMPORTANT:** Run this script immediately after creation to populate database

### Files to MODIFY:

**4. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\keywords.html`**

Add Rules & Flags tab after existing tabs. Insert this block before the closing `</div>` of tab content area:

```html
<!-- Rules & Flags Tab -->
<div class="tab-pane fade" id="keywords-rules-tab" role="tabpanel">
    {% include 'components/kw_rules_flags_tab.html' %}
</div>
```

Also add tab navigation button in the `<ul class="nav nav-tabs">` section:
```html
<li class="nav-item">
    <a class="nav-link" id="keywords-rules-link" data-bs-toggle="tab" href="#keywords-rules-tab">
        <i class="material-symbols-outlined">rule</i> Rules & Flags
    </a>
</li>
```

**5. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\keywords.py`**

Add these functions at the end of the file, before the final return statement:

```python
# ============================================================================
# RULES & FLAGS - KEYWORDS
# ============================================================================

@keywords_bp.route('/keywords/rules', methods=['GET'])
def kw_list_rules():
    """List all keyword rules and flags"""
    conn = _get_warehouse()
    
    # CRITICAL: Filter by entity_type='keyword'
    rules = conn.execute("""
        SELECT * FROM rules 
        WHERE entity_type = 'keyword' 
        ORDER BY created_at DESC
    """).fetchall()
    
    return jsonify({
        'success': True,
        'rules': [dict(r) for r in rules]
    })

@keywords_bp.route('/keywords/rules/create', methods=['POST'])
def kw_create_rule():
    """Create new keyword rule or flag"""
    data = request.get_json()
    conn = _get_warehouse()
    
    # Set entity_type to 'keyword'
    data['entity_type'] = 'keyword'
    
    # Insert into rules table
    conn.execute("""
        INSERT INTO rules (
            name, entity_type, rule_or_flag, type, action_type,
            enabled, conditions, change_pct, cooldown_days, 
            risk_level, scope, is_template
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        data['name'],
        'keyword',  # CRITICAL
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

@keywords_bp.route('/keywords/rules/<int:rule_id>/update', methods=['PUT'])
def kw_update_rule(rule_id):
    """Update existing keyword rule or flag"""
    data = request.get_json()
    conn = _get_warehouse()
    
    # Verify entity_type is 'keyword'
    existing = conn.execute(
        "SELECT entity_type FROM rules WHERE id = ?", 
        [rule_id]
    ).fetchone()
    
    if not existing or existing[0] != 'keyword':
        return jsonify({'success': False, 'error': 'Invalid rule'}), 404
    
    conn.execute("""
        UPDATE rules SET
            name = ?,
            conditions = ?,
            change_pct = ?,
            cooldown_days = ?,
            risk_level = ?,
            scope = ?
        WHERE id = ? AND entity_type = 'keyword'
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

@keywords_bp.route('/keywords/rules/<int:rule_id>/delete', methods=['DELETE'])
def kw_delete_rule(rule_id):
    """Delete keyword rule or flag"""
    conn = _get_warehouse()
    
    conn.execute(
        "DELETE FROM rules WHERE id = ? AND entity_type = 'keyword'",
        [rule_id]
    )
    
    return jsonify({'success': True})

@keywords_bp.route('/keywords/rules/<int:rule_id>/toggle', methods=['POST'])
def kw_toggle_rule(rule_id):
    """Toggle keyword rule enabled status"""
    conn = _get_warehouse()
    
    conn.execute("""
        UPDATE rules 
        SET enabled = NOT enabled 
        WHERE id = ? AND entity_type = 'keyword'
    """, [rule_id])
    
    return jsonify({'success': True})

@keywords_bp.route('/keywords/rules/<int:rule_id>/save-as-template', methods=['POST'])
def kw_save_as_template(rule_id):
    """Save keyword rule as template"""
    conn = _get_warehouse()
    
    # Get existing rule
    rule = conn.execute(
        "SELECT * FROM rules WHERE id = ? AND entity_type = 'keyword'",
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
        'keyword',
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

@keywords_bp.route('/api/keywords-list', methods=['GET'])
def kw_api_keywords_list():
    """API endpoint for keyword scope picker"""
    config = get_current_config()
    customer_id = str(config.config.get("customer_id"))
    
    conn = duckdb.connect('warehouse.duckdb')
    conn.execute("ATTACH 'warehouse_readonly.duckdb' AS ro (READ_ONLY)")
    
    keywords = conn.execute("""
        SELECT 
            keyword_id,
            keyword_text,
            ad_group_name
        FROM ro.analytics.keyword_daily
        WHERE customer_id = ?
        ORDER BY keyword_text
    """, [customer_id]).fetchall()
    
    conn.close()
    
    return jsonify({
        'success': True,
        'keywords': [
            {
                'id': str(k[0]),
                'name': f"{k[1]} ({k[2]})"
            }
            for k in keywords
        ]
    })

def rfb_keywords(config):
    """Context data for keywords rules flow builder"""
    return {
        'entity_type': 'keyword',
        'entity_label': 'Keywords',
        'entity_label_singular': 'Keyword',
        
        # Metric options for Step 4 (condition builder)
        'metrics': [
            # Performance metrics
            {'value': 'roas_w14', 'label': 'ROAS (14d)', 'has_prev': True},
            {'value': 'roas_w7', 'label': 'ROAS (7d)', 'has_prev': True},
            {'value': 'roas_w30', 'label': 'ROAS (30d)', 'has_prev': True},
            {'value': 'cpa_w14', 'label': 'CPA (14d)', 'has_prev': True},
            {'value': 'cpa_w7', 'label': 'CPA (7d)', 'has_prev': True},
            {'value': 'cpa_w30', 'label': 'CPA (30d)', 'has_prev': True},
            {'value': 'ctr_w7', 'label': 'CTR (7d)', 'has_prev': True},
            {'value': 'cvr_w7', 'label': 'CVR (7d)', 'has_prev': True},
            
            # Volume metrics
            {'value': 'conversions_w7_sum', 'label': 'Conversions (7d)', 'has_prev': True},
            {'value': 'conversions_w14_sum', 'label': 'Conversions (14d)', 'has_prev': True},
            {'value': 'conversions_w30_sum', 'label': 'Conversions (30d)', 'has_prev': True},
            {'value': 'clicks_w7_sum', 'label': 'Clicks (7d)', 'has_prev': True},
            {'value': 'impressions_w7_sum', 'label': 'Impressions (7d)', 'has_prev': False},
            {'value': 'cost_w7_sum', 'label': 'Cost (7d)', 'has_prev': True},
            {'value': 'cost_w14_sum', 'label': 'Cost (14d)', 'has_prev': True},
            {'value': 'cost_w30_sum', 'label': 'Cost (30d)', 'has_prev': True},
            
            # Quality Score
            {'value': 'quality_score', 'label': 'Quality Score', 'has_prev': False},
            {'value': 'quality_score_creative', 'label': 'QS - Creative', 'has_prev': False},
            {'value': 'quality_score_landing_page', 'label': 'QS - Landing Page', 'has_prev': False},
            {'value': 'quality_score_relevance', 'label': 'QS - Relevance', 'has_prev': False},
            
            # Bidding
            {'value': 'bid_micros', 'label': 'Max CPC Bid', 'has_prev': False},
            {'value': 'first_page_cpc_micros', 'label': 'First Page CPC', 'has_prev': False},
            {'value': 'top_of_page_cpc_micros', 'label': 'Top of Page CPC', 'has_prev': False},
            
            # Anomaly detection
            {'value': 'cost_w14_cv', 'label': 'Cost Volatility (14d CV)', 'has_prev': False},
            {'value': 'clicks_w7_vs_prev_pct', 'label': 'Clicks WoW %', 'has_prev': False},
            {'value': 'cost_w7_vs_prev_pct', 'label': 'Cost WoW %', 'has_prev': False},
            
            # Status
            {'value': 'status', 'label': 'Keyword Status', 'has_prev': False},
            {'value': 'match_type', 'label': 'Match Type', 'has_prev': False},
            {'value': 'low_data_flag', 'label': 'Low Data Flag', 'has_prev': False},
        ],
        
        # Action types for Step 4 (action builder)
        'action_types': {
            'bid': [
                {'value': 'increase_bid', 'label': 'Increase Max CPC bid'},
                {'value': 'decrease_bid', 'label': 'Decrease Max CPC bid'},
                {'value': 'increase_bid_to_first_page', 'label': 'Increase bid to First Page CPC'},
            ],
            'status': [
                {'value': 'pause', 'label': 'Pause keyword'},
                {'value': 'enable', 'label': 'Enable keyword'},
            ]
        }
    }
```

**Also register the context function in the keywords route's main function** (find where other context is added):
```python
'rfb_keywords': rfb_keywords(config),
```

**6. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\app.py`**

Find the CSRF exemptions section (around line 170-185). After the ad_groups exemptions, add:

```python
# Keywords Rules & Flags CRUD
csrf.exempt(keywords_bp)  # This exempts ALL routes in keywords_bp
```

OR if you want to be specific (preferred pattern from campaigns):

```python
# Keywords Rules & Flags CRUD  
from act_dashboard.routes.keywords import (
    kw_list_rules, kw_create_rule, kw_update_rule,
    kw_delete_rule, kw_toggle_rule, kw_save_as_template
)
csrf.exempt(kw_list_rules)
csrf.exempt(kw_create_rule)
csrf.exempt(kw_update_rule)
csrf.exempt(kw_delete_rule)
csrf.exempt(kw_toggle_rule)
csrf.exempt(kw_save_as_template)
```

**7. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\static\css\rules.css`**

Find line ~883 (search for `#rules-toast-wrap,`). The current rule looks like:
```css
#rules-toast-wrap,
#ag-rules-toast-wrap {
    position: fixed;
    bottom: 24px;
    right: 24px;
    z-index: 1060;
    max-width: 400px;
}
```

Change to:
```css
#rules-toast-wrap,
#ag-rules-toast-wrap,
#kw-rules-toast-wrap {
    position: fixed;
    bottom: 24px;
    right: 24px;
    z-index: 1060;
    max-width: 400px;
}
```

**8. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_108_HANDOFF.md`** — CREATE

**9. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_108_SUMMARY.md`** — CREATE

---

## SEED SCRIPT STRUCTURE

**File:** `C:\Users\User\Desktop\gads-data-layer\scripts\seed_keyword_rules.py`

```python
import duckdb
import json

def seed_keyword_rules():
    conn = duckdb.connect('warehouse.duckdb')
    
    # Delete existing keyword rules/flags
    conn.execute("DELETE FROM rules WHERE entity_type = 'keyword'")
    
    rules = [
        # Rule 1: Increase Max CPC - Strong Performance
        {
            'name': 'Increase Max CPC – Strong Performance',
            'entity_type': 'keyword',
            'rule_or_flag': 'rule',
            'type': 'bid',
            'action_type': 'increase_bid',
            'enabled': True,
            'conditions': json.dumps([
                {'metric': 'roas_w14', 'op': 'gt', 'value': 5.0, 'ref': None},
                {'metric': 'conversions_w14_sum', 'op': 'gte', 'value': 5, 'ref': None}
            ]),
            'change_pct': 0.20,
            'cooldown_days': 14,
            'risk_level': 'low',
            'scope': json.dumps({'scope': 'all'}),
            'is_template': False
        },
        # ... (add all 32 rows here - 12 rules + 20 flags)
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
    print(f"✅ Seeded {len(rules)} keyword rules and flags")

if __name__ == '__main__':
    seed_keyword_rules()
```

---

## COMPLETE RULES & FLAGS DATA

### RULES (12 total: 8 Bid + 4 Status)

I've provided complete JSON for the first 6 rules in the deliverables section above. Here are rules 7-12:

**7. KW-BID-007: Increase Max CPC – Lost Impression Share**
- Conditions: clicks_w7_sum < 10 AND impressions_w7_sum > 100
- Action: Increase bid by 20%
- Cooldown: 7 days, Risk: medium

**8. KW-BID-008: Decrease Max CPC – Low CTR**
- Conditions: ctr_w7 < 0.02 AND clicks_w7_sum ≥ 20
- Action: Decrease bid by 15%
- Cooldown: 7 days, Risk: low

**9. KW-STATUS-001: Pause – Poor Performance No Conversions**
- Conditions: conversions_w30_sum = 0 AND cost_w30_sum > 50000000 (£50)
- Action: Pause
- Cooldown: 30 days, Risk: medium

**10. KW-STATUS-002: Pause – Low Quality Score High Spend**
- Conditions: quality_score ≤ 3 AND cost_w30_sum > 30000000 (£30)
- Action: Pause
- Cooldown: 30 days, Risk: medium

**11. KW-STATUS-003: Enable – Quality Score Improved**
- Conditions: status = 'PAUSED' AND quality_score ≥ 7
- Action: Enable
- Cooldown: 14 days, Risk: low

**12. KW-STATUS-004: Pause – High CPA Low ROAS**
- Conditions: cpa_w30 > 100000000 (£100) AND roas_w30 < 1.5 AND conversions_w30_sum ≥ 5
- Action: Pause
- Cooldown: 30 days, Risk: medium

### FLAGS (20 total: 9 Performance + 6 Anomaly + 5 Technical)

**Performance Flags (9):**
1. Quality Score Drop — quality_score ≤ 4 AND cost_w7_sum > 10000000
2. ROAS Decline — roas_w7_vs_prev_pct < -0.30 AND conversions_w7_sum ≥ 3
3. CPA Spike — cpa_w7_vs_prev_pct > 0.50 AND conversions_w7_sum ≥ 2
4. CTR Drop — ctr_w7_vs_prev_pct < -0.30 AND clicks_w7_sum ≥ 20
5. CVR Decline — cvr_w7_vs_prev_pct < -0.30 AND conversions_w7_sum ≥ 3
6. Wasted Spend Zero Conversions — conversions_w30_sum = 0 AND cost_w30_sum > 30000000
7. Low CTR High Impressions — ctr_w7 < 0.01 AND impressions_w7_sum > 500
8. Bid Below First Page CPC — bid_micros < first_page_cpc_micros * 0.6
9. Bid Above Top of Page CPC — bid_micros > top_of_page_cpc_micros * 1.5 AND conversions_w14_sum < 3

**Anomaly Flags (6):**
10. Cost Spike — cost_w14_cv > 2.0
11. Click Pattern Change — clicks_w7_vs_prev_pct > 1.0 OR clicks_w7_vs_prev_pct < -0.5
12. Conversion Drop — conversions_w7_vs_prev_pct < -0.50 AND conversions_w7_sum ≥ 2
13. Cost Increase No Performance Gain — cost_w7_vs_prev_pct > 0.40 AND conversions_w7_vs_prev_pct < 0.05
14. Quality Score Sudden Drop — quality_score ≤ 5 AND quality_score_creative ≤ 3
15. High Cost Volatility — cost_w14_cv > 1.5

**Technical Flags (5):**
16. Low Quality Score Creative — quality_score_creative ≤ 3
17. Low Quality Score Landing Page — quality_score_landing_page ≤ 3
18. Low Quality Score Relevance — quality_score_relevance ≤ 3
19. Broad Match High Waste — match_type = 'BROAD' AND ctr_w7 < 0.015 AND cost_w7_sum > 20000000
20. Low Data Warning — low_data_flag = TRUE

---

## SUCCESS CRITERIA

**Before reporting complete, ALL must pass:**

- [ ] Seed script runs successfully: `python scripts/seed_keyword_rules.py`
- [ ] Database shows 32 new rows with `entity_type='keyword'`
- [ ] Keywords page loads without errors
- [ ] Rules & Flags tab visible on Keywords page
- [ ] Modal hidden on page load (NOT visible at bottom)
- [ ] Click "Add rule or flag" → Modal appears centered as popup with dark overlay
- [ ] Click Close/X → Modal disappears completely
- [ ] Rules tab shows 12 keyword rules (8 Bid + 4 Status)
- [ ] Flags tab shows 20 keyword flags (9 Performance + 6 Anomaly + 5 Technical)
- [ ] NO campaign or ad group rules visible on Keywords page
- [ ] Campaigns page still shows ONLY campaign rules (18 total)
- [ ] Ad Groups page still shows ONLY ad group rules (12 total)
- [ ] Create new rule → Saves successfully, appears in list
- [ ] Edit existing rule → Modal pre-populates correctly
- [ ] Edit rule with "Low" risk → Save → Still shows "Low" (NOT "High")
- [ ] Edit rule with "Medium" risk → Save → Still shows "Medium"
- [ ] Toggle rule on/off → Updates correctly
- [ ] Delete rule → Removes from list
- [ ] Save as template → Creates template with "(Template)" suffix
- [ ] Toast slides in from bottom-right corner (NOT at bottom of page)
- [ ] Zero console errors on Keywords page
- [ ] Zero console errors on Campaigns page (regression check)
- [ ] Zero console errors on Ad Groups page (regression check)
- [ ] Flask starts cleanly with no errors

---

## TESTING INSTRUCTIONS

### Step 1: Run Seed Script
```powershell
cd C:\Users\User\Desktop\gads-data-layer
.\.venv\Scripts\Activate.ps1
python scripts/seed_keyword_rules.py
```
**Expected output:** "✅ Seeded 32 keyword rules and flags"

### Step 2: Verify Database
```powershell
python -c "import duckdb; conn = duckdb.connect('warehouse.duckdb'); print('Keyword rules:', conn.execute('SELECT COUNT(*) FROM rules WHERE entity_type=\"keyword\"').fetchone()[0]); conn.close()"
```
**Expected output:** "Keyword rules: 32"

### Step 3: Start Flask
```powershell
taskkill /IM python.exe /F
python act_dashboard/app.py
```
**Expected:** Flask starts with no errors

### Step 4: Test Keywords Page
- Open: `http://localhost:5000/keywords`
- Click Rules & Flags tab
- Verify modal hidden on load
- Click "Add rule or flag"
- Verify modal centered with dark overlay
- Close modal, verify disappears
- Count rules: Should see 12
- Click Flags tab
- Count flags: Should see 20

### Step 5: Test Edit
- Click Edit on first rule
- Note the risk level (Low/Medium/High)
- Don't change anything
- Click Save
- Verify risk level unchanged

### Step 6: Test Toast
- Edit any rule
- Change cooldown from 14d → 7d
- Click Save
- Verify toast slides from bottom-right

### Step 7: Regression Check
- Go to Campaigns page → Rules & Flags tab
- Count: Should see 18 campaign rules only
- Go to Ad Groups page → Rules & Flags tab
- Count: Should see 12 ad group rules only
- Go back to Keywords page
- Verify still showing 12 keyword rules

### Step 8: Console Check
- Open F12 → Console
- Navigate through: Keywords → Campaigns → Ad Groups → Keywords
- Verify zero errors on all pages

### Step 9: Report
After all tests pass:
- Create CHAT_108_SUMMARY.md with test results
- Create CHAT_108_HANDOFF.md
- Report: "Chat 108 complete - all 22 success criteria passed"

---

## CRITICAL REMINDERS

**From KNOWN_PITFALLS.md (Pitfalls 76-80):**

1. **Pitfall 76:** Filter EVERY rules query with `WHERE entity_type='keyword'`
2. **Pitfall 77:** Modal overlay MUST have `style="display:none;"`
3. **Pitfall 78:** Modal CSS needs FULL positioning (position:fixed + top:0 + left:0 + width:100% + height:100% + z-index:1050 + display:none + align-items:center + justify-content:center)
4. **Pitfall 79:** Toast container `#kw-rules-toast-wrap` MUST be in combined CSS rule
5. **Pitfall 80:** Auto-risk function needs `if (_kwRfbEditId) return;` guard at start

**From LESSONS_LEARNED.md (Lessons 93-97):**

1. **Lesson 93:** NEVER rely on seeded data separation - always filter by entity_type explicitly
2. **Lesson 94:** Modal visibility uses `.show` class toggle, base state is `display:none`
3. **Lesson 95:** Copy modal CSS from working entity, just change ID prefix
4. **Lesson 96:** Add toast container ID immediately when creating entity modal
5. **Lesson 97:** Auto-calc functions are for NEW rules - check edit state first

---

## REFERENCE FILES

**Copy these files exactly (with prefix replacements):**
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\components\ag_rules_flags_tab.html`
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\components\ag_rules_flow_builder.html`

**Use as pattern reference:**
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\ad_groups.py` (routes structure)
- `C:\Users\User\Desktop\gads-data-layer\scripts\seed_ad_group_rules.py` (seed script pattern)
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\ad_groups.html` (tab structure)

---

## CONSTRAINTS

- Do NOT modify campaigns.py or ad_groups.py (except CSS file for toast container)
- Do NOT change entity_type for existing rules
- Do NOT create new tables
- Use existing `rules` table with `entity_type='keyword'`

---

**Document Version:** 3.0 (Final - Ready for Claude Code)
**Last Updated:** 2026-03-21
**Estimated Completion:** 2–3 hours
