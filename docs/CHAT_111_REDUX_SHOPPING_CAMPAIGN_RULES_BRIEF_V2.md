# CHAT 111 REDUX: SHOPPING CAMPAIGN RULES MIGRATION - CARDS TO TABLE

**Date:** 2026-03-23  
**Priority:** HIGH  
**Estimated Time:** 3-4 hours  
**Dependencies:** Shopping data generated (Chat Phase 1 complete)

---

## OBJECTIVE

Migrate Shopping campaign rules from card-based UI to standardized table-based UI with flow builder modal, matching the pattern established in Campaigns, Ad Groups, Keywords, and Ads pages.

**CRITICAL:** This is ONLY for campaign rules. Product rules and Campaign/Product toggle buttons are Chat 112 work.

---

## SCOPE - WHAT IS INCLUDED

**✅ IN SCOPE:**
- Create `shopping_campaign_rules_flow_builder.html` component
- Replace card UI in `shopping_new.html` with table layout
- Add 6 CRUD routes to `shopping.py` for campaign rules only
- Wire up JavaScript for table population and modal interactions
- Migrate 14 existing campaign rules from `rules_config.json` to database
- Update `rules.css` to include Shopping toast wrapper styles
- Test all CRUD operations (create, edit, toggle, delete, save-as-template)

**❌ OUT OF SCOPE - DO NOT INCLUDE:**
- Product rules section (Chat 112)
- Campaign/Product toggle buttons (Chat 112)
- Product routes (Chat 112)
- Flags migration (already complete via Chat 101)
- Any Shopping product-level functionality

---

## BACKGROUND CONTEXT

### Current State
Shopping page (`shopping_new.html`) displays rules in a card-based UI:
- Each rule is a Bootstrap card
- Cards show rule name, type, conditions, enabled status
- Click card to expand details
- No modal flow builder
- No standardized table layout
- 14 campaign rules exist in `rules_config.json` with `entity_type: 'shopping'`

### Target State
Shopping page will display rules in standardized table layout:
- Bootstrap 5 table with sortable columns
- Columns: Rule Name, Type, Action, Conditions, Enabled, Actions (dropdown)
- Flow builder modal for create/edit
- CRUD routes in `shopping.py`
- Rules stored in database with `entity_type='shopping'`
- Matches patterns from Campaigns, Ad Groups, Keywords, Ads

### Why This Migration
- Consistency across all entity pages
- Easier to add product rules in Chat 112 with toggle system
- Better UX (modal vs inline cards)
- Prepares for rules expansion

---

## DATABASE SCHEMA REFERENCE

### Rules Table Structure
```sql
CREATE TABLE rules (
    id INTEGER PRIMARY KEY,
    name VARCHAR,
    type VARCHAR,  -- 'budget' or 'bid' or 'status'
    action_type VARCHAR,  -- e.g. 'increase_budget', 'decrease_budget', 'increase_bid', 'pause_campaign'
    entity_type VARCHAR,  -- 'shopping' for this migration
    enabled BOOLEAN,
    conditions JSON,  -- Array of condition objects
    scope_type VARCHAR,  -- 'all' or 'specific'
    scope_value VARCHAR,  -- NULL for 'all', campaign_id for 'specific'
    is_template BOOLEAN,  -- FALSE for rules, TRUE for templates
    cooldown_days INTEGER,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### Conditions JSON Structure
```json
[
    {
        "metric": "cpa",
        "op": "gt",
        "value": 50,
        "ref": null
    },
    {
        "metric": "conversions",
        "op": "gte",
        "value": 10,
        "ref": null
    }
]
```

**Operators:** "gt", "lt", "gte", "lte", "eq", "is_not_null"

---

## CRITICAL TECHNICAL CONSTRAINTS

### Entity Type
- Database column `entity_type` stores value `'shopping'` (NOT `'shopping_campaign'`)
- All queries MUST filter: `WHERE entity_type = 'shopping'`
- Chat 111 attempt found this - verified correct

### JavaScript Pitfalls
- **Apostrophes:** All label strings must escape apostrophes as `\'` in single-quoted JS strings
- **Function exposure:** Any function called from `onclick` must be exposed via `window.fnName`
- **Bootstrap 5:** Use `data-bs-toggle="dropdown"` NOT `data-toggle="dropdown"`

### Operators
- Use string operators: "gt", "lt", "gte", "lte", "eq", "is_not_null"
- NOT symbols: ">", "<", ">=", etc.

### Cost Values
- All cost/bid values in micros
- Example: 50000000 = £50
- Display: divide by 1,000,000 and format with £ symbol

### Scope Types
- `scope_type = 'all'` → applies to all campaigns, `scope_value = NULL`
- `scope_type = 'specific'` → applies to one campaign, `scope_value = campaign_id`

---

## SHOPPING CAMPAIGN METRICS (COMPLETE LIST)

Use these exact metric keys in the flow builder dropdown:

**Volume Metrics:**
- clicks
- impressions
- conversions
- cost_micros

**Rate Metrics:**
- ctr (Click-through rate)
- conversion_rate
- cpa (Cost per acquisition)
- roas (Return on ad spend)

**Reference:** These match `SHOPPING_CAMPAIGN_METRIC_MAP` in `act_autopilot/recommendations_engine.py`

---

## TYPE & ACTION LABELS

### Type Labels
- `budget` → "Budget"
- `bid` → "Bid"
- `status` → "Status"

### Action Labels (partial list - copy complete list from ads.py get_action_label() function)
- `increase_budget` → "Increase budget by X%"
- `decrease_budget` → "Decrease budget by X%"
- `increase_bid` → "Increase bid by X%"
- `decrease_bid` → "Decrease bid by X%"
- `pause_campaign` → "Pause campaign"
- `enable_campaign` → "Enable campaign"

---

## EXISTING RULES TO MIGRATE (14 TOTAL)

From `rules_config.json` with `entity_type: 'shopping'`:

**Budget Rules (likely 8-10):**
- Increase/decrease budget based on ROAS, CPA, conversion rate
- Pause campaigns with poor performance

**Bid Rules (likely 4-6):**
- Adjust bids based on conversion metrics
- Optimize for target ROAS

**Note:** Exact rule names/details are in `act_autopilot/rules_config.json` - migration script should read from there.

---

## EXECUTION PLAN

### STEP 1: CREATE FLOW BUILDER COMPONENT

**File to create:** `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\components\shopping_campaign_rules_flow_builder.html`

**Actions:**
1. Copy `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\components\ads_rules_flow_builder.html`
2. Rename all function prefixes from `adRfb` to `shoppingCampaignRfb`
3. Change all entity references from `'ad'` to `'shopping'`
4. Update modal ID from `adRulesFlowModal` to `shoppingCampaignRulesFlowModal`
5. Update toast wrapper ID from `ad-rules-toast-wrap` to `shopping-campaign-rules-toast-wrap`

**Critical modifications:**

**Function exposure:**
All functions must be exposed to global scope:
```javascript
window.shoppingCampaignRfbOpen = function(...) { ... };
window.shoppingCampaignRfbClose = function(...) { ... };
window.shoppingCampaignRfbSave = function(...) { ... };
window.openShoppingCampaignRulesFlow = function(...) { ... };
// etc. for ALL functions
```

**Apostrophe check:**
Search entire file for apostrophes in string literals. Escape any found:
- ❌ `'campaign's baseline'`
- ✅ `'campaign\'s baseline'`

**Metric dropdown:**
Populate metric select with Shopping metrics (see SHOPPING CAMPAIGN METRICS section above):
```html
<select id="shoppingCampaignRfbMetric" class="form-select">
    <option value="">Select metric...</option>
    <option value="clicks">Clicks</option>
    <option value="impressions">Impressions</option>
    <option value="conversions">Conversions</option>
    <option value="cost_micros">Cost</option>
    <option value="ctr">CTR</option>
    <option value="conversion_rate">Conversion Rate</option>
    <option value="cpa">CPA</option>
    <option value="roas">ROAS</option>
</select>
```

**Campaign scope dropdown:**
The scope section needs to call `/api/campaigns-list` to populate campaign options:
```javascript
fetch('/api/campaigns-list')
    .then(res => res.json())
    .then(data => {
        // Populate campaign dropdown with data.campaigns
    });
```
This endpoint already exists - just call it. Filter campaigns by current client.

**Checkpoint 1 - Component Created:**
- File exists at path above
- File is valid HTML (no syntax errors)
- All `adRfb` prefixes changed to `shoppingCampaignRfb`
- Modal ID updated
- Toast wrapper ID updated
- All functions exposed via `window.fnName`
- All apostrophes escaped
- Metric dropdown has Shopping metrics
- Run syntax check: Load page and check console

**Visual Verification Required:**
1. Save file
2. Restart Flask
3. Open Opera to http://localhost:5000/shopping
4. Click "Rules (14)" tab
5. Take screenshot of current state
6. Open console (F12) → Take screenshot of console tab
7. Report back: "Checkpoint 1 - Component file created. Console check: [attach screenshots]"

**STOP IF:** Any SyntaxError appears in console. Fix before proceeding.

---

### STEP 2: UPDATE SHOPPING_NEW.HTML - REPLACE CARDS WITH TABLE

**File to modify:** `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\shopping_new.html`

**Current structure (approximate):**
```html
<!-- Rules Tab -->
<div class="tab-pane fade" id="rules-tab-pane">
    <!-- Card-based UI here -->
    {% for rule in rules %}
        <div class="card">...</div>
    {% endfor %}
</div>
```

**Target structure:**
Replace entire Rules tab content with:
```html
<!-- Rules Tab -->
<div class="tab-pane fade" id="rules-tab-pane">
    <div class="d-flex justify-content-between align-items-center mb-3">
        <div>
            <h5 class="mb-0">Campaign Rules</h5>
            <small class="text-muted">Automation rules for Shopping campaigns</small>
        </div>
        <button class="btn btn-primary btn-sm" onclick="window.openShoppingCampaignRulesFlow()">
            <i class="bi bi-plus-circle"></i> Create Rule
        </button>
    </div>

    <!-- Loading State -->
    <div id="shopping-campaign-rules-loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
        </div>
        <p class="text-muted mt-2">Loading rules...</p>
    </div>

    <!-- Empty State -->
    <div id="shopping-campaign-rules-empty" class="alert alert-info" style="display:none;">
        <i class="bi bi-info-circle"></i> No campaign rules configured yet. Click "Create Rule" to get started.
    </div>

    <!-- Rules Table -->
    <div id="shopping-campaign-rules-table-wrap" style="display:none;">
        <table class="table table-hover">
            <thead>
                <tr>
                    <th style="width: 25%;">Rule Name</th>
                    <th style="width: 12%;">Type</th>
                    <th style="width: 20%;">Action</th>
                    <th style="width: 28%;">Conditions</th>
                    <th style="width: 10%;">Enabled</th>
                    <th style="width: 5%;"></th>
                </tr>
            </thead>
            <tbody id="shopping-campaign-rules-tbody">
                <!-- Populated via JavaScript -->
            </tbody>
        </table>
    </div>

    <!-- Templates Section (collapsible) -->
    <div id="shopping-campaign-templates-section" style="display:none;" class="mt-4">
        <div class="d-flex justify-content-between align-items-center mb-2">
            <h6 class="mb-0">
                <i class="bi bi-chevron-right" id="shopping-campaign-templates-chevron"></i>
                Templates
                <span class="badge bg-secondary ms-2" id="shopping-campaign-templates-count">0</span>
            </h6>
            <button class="btn btn-link btn-sm text-decoration-none" onclick="window.toggleShoppingCampaignTemplates()">
                <span id="shopping-campaign-templates-toggle-text">Show</span>
            </button>
        </div>
        <div id="shopping-campaign-templates-collapse" style="display:none;">
            <table class="table table-sm">
                <thead>
                    <tr>
                        <th>Template Name</th>
                        <th>Type</th>
                        <th>Action</th>
                        <th></th>
                    </tr>
                </thead>
                <tbody id="shopping-campaign-templates-tbody">
                    <!-- Populated via JavaScript -->
                </tbody>
            </table>
        </div>
    </div>

    <!-- Include Flow Builder Modal -->
    {% include 'components/shopping_campaign_rules_flow_builder.html' %}

    <!-- Toast Notifications -->
    <div id="shopping-campaign-rules-toast-wrap"></div>
</div>
```

**JavaScript section to add:**

Find the existing `<script>` tag in shopping_new.html (should be near bottom of file, before `</body>`).

Add this JavaScript INSIDE the DOMContentLoaded wrapper:

```javascript
document.addEventListener('DOMContentLoaded', function() {
    // ... existing Shopping page JavaScript ...

    // ===== SHOPPING CAMPAIGN RULES JAVASCRIPT =====
    
    // Load rules on page load
    loadShoppingCampaignRules();

    // Main load function
    function loadShoppingCampaignRules() {
        fetch('/shopping/campaign_rules')
            .then(res => res.json())
            .then(data => {
                if (data.rules && data.rules.length > 0) {
                    // Hide loading, show table
                    document.getElementById('shopping-campaign-rules-loading').style.display = 'none';
                    document.getElementById('shopping-campaign-rules-table-wrap').style.display = 'block';
                    
                    // Render rules
                    renderShoppingCampaignRules(data.rules);
                } else {
                    // Hide loading, show empty state
                    document.getElementById('shopping-campaign-rules-loading').style.display = 'none';
                    document.getElementById('shopping-campaign-rules-empty').style.display = 'block';
                }
                
                // Handle templates
                if (data.templates && data.templates.length > 0) {
                    document.getElementById('shopping-campaign-templates-section').style.display = 'block';
                    document.getElementById('shopping-campaign-templates-count').textContent = data.templates.length;
                    renderShoppingCampaignTemplates(data.templates);
                }
            })
            .catch(err => {
                console.error('Error loading Shopping campaign rules:', err);
                document.getElementById('shopping-campaign-rules-loading').style.display = 'none';
                document.getElementById('shopping-campaign-rules-empty').innerHTML = 
                    '<i class="bi bi-exclamation-triangle"></i> Error loading rules. Check console.';
                document.getElementById('shopping-campaign-rules-empty').style.display = 'block';
            });
    }

    // Render rules rows
    function renderShoppingCampaignRules(rules) {
        const tbody = document.getElementById('shopping-campaign-rules-tbody');
        tbody.innerHTML = '';
        
        rules.forEach(rule => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${escapeHtml(rule.name)}</td>
                <td><span class="badge bg-secondary">${getTypeLabel(rule.type)}</span></td>
                <td>${getActionLabel(rule)}</td>
                <td>${getConditionsText(rule.conditions)}</td>
                <td>
                    <div class="form-check form-switch">
                        <input class="form-check-input" type="checkbox" 
                               ${rule.enabled ? 'checked' : ''} 
                               onchange="window.toggleShoppingCampaignRule(${rule.id}, this.checked)">
                    </div>
                </td>
                <td>
                    <div class="dropdown">
                        <button class="btn btn-sm btn-link text-dark" type="button" 
                                data-bs-toggle="dropdown" aria-expanded="false">
                            <i class="bi bi-three-dots-vertical"></i>
                        </button>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="#" onclick="window.editShoppingCampaignRule(${rule.id}); return false;">
                                <i class="bi bi-pencil"></i> Edit
                            </a></li>
                            <li><a class="dropdown-item" href="#" onclick="window.saveShoppingCampaignRuleAsTemplate(${rule.id}); return false;">
                                <i class="bi bi-save"></i> Save as template
                            </a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item text-danger" href="#" onclick="window.deleteShoppingCampaignRule(${rule.id}); return false;">
                                <i class="bi bi-trash"></i> Delete
                            </a></li>
                        </ul>
                    </div>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    // Render templates rows
    function renderShoppingCampaignTemplates(templates) {
        const tbody = document.getElementById('shopping-campaign-templates-tbody');
        tbody.innerHTML = '';
        
        templates.forEach(tmpl => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${escapeHtml(tmpl.name)}</td>
                <td><span class="badge bg-secondary">${getTypeLabel(tmpl.type)}</span></td>
                <td>${getActionLabel(tmpl)}</td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="window.useShoppingCampaignTemplate(${tmpl.id})">
                        <i class="bi bi-box-arrow-in-down"></i> Use template
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    // Helper: Get type label
    function getTypeLabel(type) {
        const labels = {
            'budget': 'Budget',
            'bid': 'Bid',
            'status': 'Status'
        };
        return labels[type] || type;
    }

    // Helper: Get action label
    function getActionLabel(rule) {
        // This should match the backend get_action_label() logic
        // Copy from ads.html - shows action with value/percentage
        // e.g., "Increase budget by 15%"
        return rule.action_label || rule.action_type;
    }

    // Helper: Get conditions text
    function getConditionsText(conditions) {
        if (!conditions || conditions.length === 0) return 'No conditions';
        return conditions.map(c => {
            const opText = {
                'gt': '>',
                'lt': '<',
                'gte': '≥',
                'lte': '≤',
                'eq': '=',
                'is_not_null': 'is not null'
            }[c.op] || c.op;
            return `${c.metric} ${opText} ${c.value}`;
        }).join(', ');
    }

    // Helper: Escape HTML
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Toggle templates section
    window.toggleShoppingCampaignTemplates = function() {
        const collapse = document.getElementById('shopping-campaign-templates-collapse');
        const chevron = document.getElementById('shopping-campaign-templates-chevron');
        const toggleText = document.getElementById('shopping-campaign-templates-toggle-text');
        
        if (collapse.style.display === 'none') {
            collapse.style.display = 'block';
            chevron.className = 'bi bi-chevron-down';
            toggleText.textContent = 'Hide';
        } else {
            collapse.style.display = 'none';
            chevron.className = 'bi bi-chevron-right';
            toggleText.textContent = 'Show';
        }
    };

    // Toggle rule enabled/disabled
    window.toggleShoppingCampaignRule = function(ruleId, enabled) {
        fetch(`/shopping/campaign_rules/${ruleId}/toggle`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ enabled: enabled })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                showToast(data.message || 'Rule toggled successfully', 'success');
            } else {
                showToast(data.message || 'Failed to toggle rule', 'danger');
                loadShoppingCampaignRules(); // Reload to revert toggle
            }
        })
        .catch(err => {
            console.error('Error toggling rule:', err);
            showToast('Error toggling rule', 'danger');
            loadShoppingCampaignRules(); // Reload to revert toggle
        });
    };

    // Edit rule
    window.editShoppingCampaignRule = function(ruleId) {
        fetch(`/shopping/campaign_rules/${ruleId}`)
            .then(res => res.json())
            .then(rule => {
                // Call flow builder's edit function
                window.shoppingCampaignRfbEdit(rule);
            })
            .catch(err => {
                console.error('Error loading rule:', err);
                showToast('Error loading rule', 'danger');
            });
    };

    // Delete rule
    window.deleteShoppingCampaignRule = function(ruleId) {
        if (!confirm('Are you sure you want to delete this rule?')) return;
        
        fetch(`/shopping/campaign_rules/${ruleId}`, {
            method: 'DELETE'
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                showToast(data.message || 'Rule deleted successfully', 'success');
                loadShoppingCampaignRules();
            } else {
                showToast(data.message || 'Failed to delete rule', 'danger');
            }
        })
        .catch(err => {
            console.error('Error deleting rule:', err);
            showToast('Error deleting rule', 'danger');
        });
    };

    // Save rule as template
    window.saveShoppingCampaignRuleAsTemplate = function(ruleId) {
        const templateName = prompt('Enter template name:');
        if (!templateName) return;
        
        fetch(`/shopping/campaign_rules/${ruleId}/save-as-template`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ template_name: templateName })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                showToast(data.message || 'Template saved successfully', 'success');
                loadShoppingCampaignRules();
            } else {
                showToast(data.message || 'Failed to save template', 'danger');
            }
        })
        .catch(err => {
            console.error('Error saving template:', err);
            showToast('Error saving template', 'danger');
        });
    };

    // Use template
    window.useShoppingCampaignTemplate = function(templateId) {
        fetch(`/shopping/campaign_rules/${templateId}`)
            .then(res => res.json())
            .then(template => {
                // Call flow builder's use-template function
                window.shoppingCampaignRfbUseTemplate(template);
            })
            .catch(err => {
                console.error('Error loading template:', err);
                showToast('Error loading template', 'danger');
            });
    };

    // Show toast notification
    function showToast(message, type) {
        const toastWrap = document.getElementById('shopping-campaign-rules-toast-wrap');
        const toastId = 'toast-' + Date.now();
        
        const toast = document.createElement('div');
        toast.id = toastId;
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        toastWrap.appendChild(toast);
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // Remove after hidden
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }

    // ===== END SHOPPING CAMPAIGN RULES JAVASCRIPT =====
});
```

**Reference:** `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\ads.html` lines ~650-950 for complete pattern

**Key adaptations:**
- All endpoint paths use `/shopping/campaign_` prefix
- All element IDs use `shopping-campaign-rules-` prefix
- All function names use `shoppingCampaignRfb` or `shoppingCampaign` prefix
- ALL functions exposed via `window.fnName = function(...) {...}`
- Load trigger is `loadShoppingCampaignRules()` called on DOMContentLoaded

**Checkpoint 2 - UI Replaced:**

**Visual Verification Required:**
1. Save file
2. Restart Flask
3. Navigate to http://localhost:5000/shopping
4. Click "Rules (14)" tab
5. Take screenshot of page
6. Open console (F12 → Console tab)
7. Take screenshot of console
8. Report back: "Checkpoint 2 - UI replaced. Current state: [attach screenshots]"

**Expected state:**
- Page shows "Loading rules..." spinner (table hasn't loaded yet because routes don't exist)
- Console shows 404 error for `/shopping/campaign_rules` (expected - routes not created yet)
- NO SyntaxError in console
- Page is not blank

**STOP IF:** 
- Page is completely blank (HTML structure error)
- Console shows SyntaxError (JavaScript syntax error - likely apostrophe)
- Console shows multiple errors beyond expected 404

---

### STEP 3: UPDATE CSS FOR TOAST WRAPPER

**File to modify:** `C:\Users\User\Desktop\gads-data-layer\act_dashboard\static\css\rules.css`

**Find this line (approximate line 10-20):**
```css
#campaign-rules-toast-wrap,
#ad-group-rules-toast-wrap,
#keyword-rules-toast-wrap,
#ad-rules-toast-wrap {
    position: fixed;
    top: 80px;
    right: 20px;
    z-index: 9999;
}
```

**Add Shopping toast wrapper to the list:**
```css
#campaign-rules-toast-wrap,
#ad-group-rules-toast-wrap,
#keyword-rules-toast-wrap,
#ad-rules-toast-wrap,
#shopping-campaign-rules-toast-wrap {
    position: fixed;
    top: 80px;
    right: 20px;
    z-index: 9999;
}
```

**Note:** This ensures toast notifications appear in the correct position on the Shopping page.

---

### STEP 4: ADD CRUD ROUTES TO SHOPPING.PY

**File to modify:** `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\shopping.py`

**Add these imports at top of file (if not already present):**
```python
from flask import jsonify, request
import duckdb
import json
from datetime import datetime
```

**Routes to add (6 total) - add after existing Shopping routes:**

**Route 1: List Rules (GET /shopping/campaign_rules)**
```python
@shopping_bp.route('/shopping/campaign_rules', methods=['GET'])
def shopping_campaign_list_rules():
    """List all Shopping campaign rules and templates"""
    try:
        conn = _get_warehouse()
        
        # Get rules (not templates)
        rules_query = """
            SELECT id, name, type, action_type, enabled, conditions, scope_type, scope_value, 
                   cooldown_days, created_at, updated_at
            FROM rules
            WHERE entity_type = 'shopping' 
              AND (is_template = FALSE OR is_template IS NULL)
            ORDER BY created_at DESC
        """
        rules = conn.execute(rules_query).fetchall()
        
        # Get templates
        templates_query = """
            SELECT id, name, type, action_type, enabled, conditions, scope_type, scope_value,
                   cooldown_days, created_at, updated_at
            FROM rules
            WHERE entity_type = 'shopping' 
              AND is_template = TRUE
            ORDER BY name
        """
        templates = conn.execute(templates_query).fetchall()
        
        conn.close()
        
        # Format rules
        rules_list = []
        for r in rules:
            rules_list.append({
                'id': r[0],
                'name': r[1],
                'type': r[2],
                'action_type': r[3],
                'enabled': r[4],
                'conditions': json.loads(r[5]) if r[5] else [],
                'scope_type': r[6],
                'scope_value': r[7],
                'cooldown_days': r[8],
                'created_at': r[9],
                'updated_at': r[10]
            })
        
        # Format templates
        templates_list = []
        for t in templates:
            templates_list.append({
                'id': t[0],
                'name': t[1],
                'type': t[2],
                'action_type': t[3],
                'enabled': t[4],
                'conditions': json.loads(t[5]) if t[5] else [],
                'scope_type': t[6],
                'scope_value': t[7],
                'cooldown_days': t[8],
                'created_at': t[9],
                'updated_at': t[10]
            })
        
        return jsonify({
            'success': True,
            'rules': rules_list,
            'templates': templates_list
        })
        
    except Exception as e:
        print(f"[ERROR] shopping_campaign_list_rules: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
```

**Route 2: Create Rule (POST /shopping/campaign_rules)**
```python
@shopping_bp.route('/shopping/campaign_rules', methods=['POST'])
def shopping_campaign_create_rule():
    """Create new Shopping campaign rule"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required = ['name', 'type', 'action_type']
        for field in required:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400
        
        # Validate conditions
        conditions = data.get('conditions', [])
        if not isinstance(conditions, list):
            return jsonify({'success': False, 'message': 'Conditions must be an array'}), 400
        
        conn = _get_warehouse()
        
        insert_query = """
            INSERT INTO rules (
                name, type, action_type, entity_type, enabled, conditions, 
                scope_type, scope_value, is_template, cooldown_days, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        conn.execute(insert_query, [
            data['name'],
            data['type'],
            data['action_type'],
            'shopping',
            data.get('enabled', True),
            json.dumps(conditions),
            data.get('scope_type', 'all'),
            data.get('scope_value', None),
            False,  # is_template
            data.get('cooldown_days', 7),
            datetime.utcnow(),
            datetime.utcnow()
        ])
        
        conn.close()
        
        return jsonify({'success': True, 'message': 'Rule created successfully'})
        
    except Exception as e:
        print(f"[ERROR] shopping_campaign_create_rule: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
```

**Route 3: Update Rule (PUT /shopping/campaign_rules/<id>)**
```python
@shopping_bp.route('/shopping/campaign_rules/<int:rule_id>', methods=['PUT'])
def shopping_campaign_update_rule(rule_id):
    """Update existing Shopping campaign rule"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required = ['name', 'type', 'action_type']
        for field in required:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400
        
        # Validate conditions
        conditions = data.get('conditions', [])
        if not isinstance(conditions, list):
            return jsonify({'success': False, 'message': 'Conditions must be an array'}), 400
        
        conn = _get_warehouse()
        
        update_query = """
            UPDATE rules
            SET name = ?, type = ?, action_type = ?, conditions = ?, 
                scope_type = ?, scope_value = ?, cooldown_days = ?, updated_at = ?
            WHERE id = ? AND entity_type = 'shopping'
        """
        
        conn.execute(update_query, [
            data['name'],
            data['type'],
            data['action_type'],
            json.dumps(conditions),
            data.get('scope_type', 'all'),
            data.get('scope_value', None),
            data.get('cooldown_days', 7),
            datetime.utcnow(),
            rule_id
        ])
        
        conn.close()
        
        return jsonify({'success': True, 'message': 'Rule updated successfully'})
        
    except Exception as e:
        print(f"[ERROR] shopping_campaign_update_rule: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
```

**Route 4: Delete Rule (DELETE /shopping/campaign_rules/<id>)**
```python
@shopping_bp.route('/shopping/campaign_rules/<int:rule_id>', methods=['DELETE'])
def shopping_campaign_delete_rule(rule_id):
    """Delete Shopping campaign rule"""
    try:
        conn = _get_warehouse()
        
        delete_query = "DELETE FROM rules WHERE id = ? AND entity_type = 'shopping'"
        conn.execute(delete_query, [rule_id])
        
        conn.close()
        
        return jsonify({'success': True, 'message': 'Rule deleted successfully'})
        
    except Exception as e:
        print(f"[ERROR] shopping_campaign_delete_rule: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
```

**Route 5: Toggle Rule (POST /shopping/campaign_rules/<id>/toggle)**
```python
@shopping_bp.route('/shopping/campaign_rules/<int:rule_id>/toggle', methods=['POST'])
def shopping_campaign_toggle_rule(rule_id):
    """Toggle Shopping campaign rule enabled status"""
    try:
        data = request.get_json()
        enabled = data.get('enabled', True)
        
        conn = _get_warehouse()
        
        update_query = """
            UPDATE rules
            SET enabled = ?, updated_at = ?
            WHERE id = ? AND entity_type = 'shopping'
        """
        
        conn.execute(update_query, [enabled, datetime.utcnow(), rule_id])
        
        conn.close()
        
        status = "enabled" if enabled else "disabled"
        return jsonify({'success': True, 'message': f'Rule {status} successfully'})
        
    except Exception as e:
        print(f"[ERROR] shopping_campaign_toggle_rule: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
```

**Route 6: Save as Template (POST /shopping/campaign_rules/<id>/save-as-template)**
```python
@shopping_bp.route('/shopping/campaign_rules/<int:rule_id>/save-as-template', methods=['POST'])
def shopping_campaign_save_as_template(rule_id):
    """Save Shopping campaign rule as template"""
    try:
        data = request.get_json()
        template_name = data.get('template_name')
        
        if not template_name:
            return jsonify({'success': False, 'message': 'Template name required'}), 400
        
        conn = _get_warehouse()
        
        # Get original rule
        get_query = """
            SELECT name, type, action_type, conditions, scope_type, scope_value, cooldown_days
            FROM rules
            WHERE id = ? AND entity_type = 'shopping'
        """
        rule = conn.execute(get_query, [rule_id]).fetchone()
        
        if not rule:
            conn.close()
            return jsonify({'success': False, 'message': 'Rule not found'}), 404
        
        # Create template
        insert_query = """
            INSERT INTO rules (
                name, type, action_type, entity_type, enabled, conditions, 
                scope_type, scope_value, is_template, cooldown_days, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        conn.execute(insert_query, [
            template_name,
            rule[1],  # type
            rule[2],  # action_type
            'shopping',
            True,
            rule[3],  # conditions
            rule[4],  # scope_type
            rule[5],  # scope_value
            True,  # is_template
            rule[6],  # cooldown_days
            datetime.utcnow(),
            datetime.utcnow()
        ])
        
        conn.close()
        
        return jsonify({'success': True, 'message': 'Template saved successfully'})
        
    except Exception as e:
        print(f"[ERROR] shopping_campaign_save_as_template: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
```

**Helper function (if not already present):**
```python
def _get_warehouse():
    """Get writable warehouse connection"""
    return duckdb.connect('warehouse.duckdb')
```

**CSRF exemptions:**
Add to `C:\Users\User\Desktop\gads-data-layer\act_dashboard\__init__.py` after line with "Chat 109" CSRF exemptions:
```python
✅ [Chat 111 Redux] CSRF exempted: shopping.shopping_campaign_list_rules
✅ [Chat 111 Redux] CSRF exempted: shopping.shopping_campaign_create_rule
✅ [Chat 111 Redux] CSRF exempted: shopping.shopping_campaign_update_rule
✅ [Chat 111 Redux] CSRF exempted: shopping.shopping_campaign_delete_rule
✅ [Chat 111 Redux] CSRF exempted: shopping.shopping_campaign_toggle_rule
✅ [Chat 111 Redux] CSRF exempted: shopping.shopping_campaign_save_as_template
```

**Checkpoint 3 - Routes Added:**

**Visual Verification Required:**
1. Save files (shopping.py + __init__.py)
2. Restart Flask
3. Check Flask startup log for CSRF exemption confirmations
4. Navigate to http://localhost:5000/shopping
5. Click "Rules (14)" tab
6. Take screenshot of page
7. Open console (F12 → Console tab)
8. Take screenshot of console
9. Check Flask terminal - take screenshot of last 30 lines showing GET request
10. Report back: "Checkpoint 3 - Routes added. Status: [attach screenshots]"

**Expected state:**
- Page shows table with rules OR empty state (depending on if migration script run)
- Console shows 200 OK for `/shopping/campaign_rules` (not 404)
- NO SyntaxError in console
- Flask log shows: `127.0.0.1 - - [timestamp] "GET /shopping/campaign_rules HTTP/1.1" 200 -`

**STOP IF:**
- Console shows 500 error (route has Python error)
- Console shows 404 (route not registered)
- Console shows SyntaxError (JavaScript issue)
- Flask crashes on startup

---

### STEP 5: CREATE AND RUN MIGRATION SCRIPT

**File to create:** `C:\Users\User\Desktop\gads-data-layer\scripts\migrate_shopping_campaign_rules_to_db.py`

**Complete implementation:**
```python
import duckdb
import json
from pathlib import Path
from datetime import datetime

def migrate_shopping_campaign_rules():
    """Migrate Shopping campaign rules from rules_config.json to database"""
    
    # Load rules_config.json
    config_path = Path(__file__).parent.parent / 'act_autopilot' / 'rules_config.json'
    
    if not config_path.exists():
        print(f"ERROR: rules_config.json not found at {config_path}")
        return
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Filter shopping rules
    shopping_rules = [r for r in config.get('rules', []) if r.get('entity_type') == 'shopping']
    
    print(f"Found {len(shopping_rules)} shopping campaign rules to migrate")
    
    if len(shopping_rules) == 0:
        print("No shopping rules found - check rules_config.json")
        return
    
    # Connect to database
    conn = duckdb.connect('warehouse.duckdb')
    
    # Check if rules table exists
    table_check = conn.execute("""
        SELECT COUNT(*) FROM information_schema.tables 
        WHERE table_name = 'rules'
    """).fetchone()[0]
    
    if table_check == 0:
        print("ERROR: rules table does not exist in database")
        conn.close()
        return
    
    # Check for existing shopping rules
    existing = conn.execute("""
        SELECT COUNT(*) FROM rules 
        WHERE entity_type = 'shopping' AND (is_template = FALSE OR is_template IS NULL)
    """).fetchone()[0]
    
    print(f"Existing shopping campaign rules in DB: {existing}")
    
    if existing > 0:
        confirm = input(f"WARNING: {existing} shopping rules already exist. Proceed anyway? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Migration cancelled")
            conn.close()
            return
    
    # Insert each rule
    insert_query = """
        INSERT INTO rules (
            name, type, action_type, entity_type, enabled, conditions, 
            scope_type, scope_value, is_template, cooldown_days, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    migrated = 0
    errors = 0
    
    for rule in shopping_rules:
        try:
            conn.execute(insert_query, [
                rule.get('name', 'Unnamed Rule'),
                rule.get('type', 'budget'),
                rule.get('action_type', ''),
                'shopping',  # entity_type
                rule.get('enabled', True),
                json.dumps(rule.get('conditions', [])),
                rule.get('scope_type', 'all'),
                rule.get('scope_value', None),
                False,  # is_template
                rule.get('cooldown_days', 7),
                datetime.utcnow(),
                datetime.utcnow()
            ])
            migrated += 1
            print(f"✓ Migrated: {rule.get('name')}")
        except Exception as e:
            errors += 1
            print(f"✗ Error migrating {rule.get('name')}: {e}")
    
    conn.close()
    
    print(f"\nMigration complete:")
    print(f"  Migrated: {migrated}")
    print(f"  Errors: {errors}")
    print(f"  Total: {len(shopping_rules)}")

if __name__ == '__main__':
    migrate_shopping_campaign_rules()
```

**Run migration:**
```powershell
cd C:\Users\User\Desktop\gads-data-layer
python scripts/migrate_shopping_campaign_rules_to_db.py
```

**Verify migration:**
```powershell
python -c "import duckdb; conn = duckdb.connect('warehouse.duckdb'); rows = conn.execute(\"SELECT id, name, type, enabled FROM rules WHERE entity_type='shopping' AND (is_template=FALSE OR is_template IS NULL) ORDER BY id\").fetchall(); print(f'Found {len(rows)} shopping campaign rules:'); [print(f'  {r[0]}: {r[1]} ({r[2]}) - {\"enabled\" if r[3] else \"disabled\"}') for r in rows]; conn.close()"
```

**Expected output:** List of 14 rules with IDs, names, types

**Checkpoint 4 - Migration Complete:**

**Visual Verification Required:**
1. Run migration script
2. Copy terminal output showing migration results
3. Run verification query
4. Copy verification query output
5. Refresh Shopping page Rules tab (hard refresh: Ctrl+Shift+R)
6. Take screenshot showing table with 14 rules
7. Open console - take screenshot showing zero errors
8. Report back: "Checkpoint 4 - Migration complete. [attach screenshots + terminal output]"

**Expected state:**
- Table shows 14 rules
- Each rule has name, type, action, conditions, enabled toggle
- Actions dropdown on each row (⋮ icon)
- Templates section shows "Templates (0)" (no templates yet)

**STOP IF:**
- Migration script errors
- Database query returns 0 rows
- Table still shows "Loading..." or empty state
- Console shows JavaScript errors

---

### STEP 6: FUNCTIONAL TESTING

**Test 1: Create New Rule**

**Steps:**
1. Click "Create Rule" button
2. Modal opens with title "Create Campaign Rule"
3. Fill in:
   - Name: "Test Rule - High CPA"
   - Type: Budget
   - Action: Decrease budget by 15%
   - Scope: All campaigns
   - Condition: CPA > £50
4. Click "Save"
5. Modal closes
6. Table refreshes
7. New rule appears in table

**Verify:**
- Toast notification: "Rule created successfully"
- New rule visible in table
- Rule shows correct name, type, action, condition
- Enabled toggle is ON
- Console has zero errors
- Flask log shows: `POST /shopping/campaign_rules HTTP/1.1 200`

**Visual Verification Required:**
- Screenshot of filled modal before clicking Save
- Screenshot of table after rule created
- Screenshot of console showing zero errors
- Screenshot of Flask terminal showing POST 200

---

**Test 2: Edit Existing Rule**

**Steps:**
1. Click ⋮ dropdown on any rule
2. Click "Edit"
3. Modal opens with title "Edit Campaign Rule"
4. Fields pre-populated with rule data
5. Change name to "Modified Rule Name"
6. Click "Update"
7. Modal closes
8. Table refreshes
9. Rule shows updated name

**Verify:**
- Toast notification: "Rule updated successfully"
- Updated name visible in table
- All other fields unchanged
- Console has zero errors
- Flask log shows: `PUT /shopping/campaign_rules/{id} HTTP/1.1 200`

**Visual Verification Required:**
- Screenshot of pre-populated modal
- Screenshot of table showing updated name
- Screenshot of console showing zero errors

---

**Test 3: Toggle Enable/Disable**

**Steps:**
1. Click toggle switch on any enabled rule
2. Toggle animates to OFF position
3. Table updates immediately (no page reload)
4. Toast notification appears

**Verify:**
- Toast: "Rule disabled"
- Rule row appears slightly dimmed or greyed
- Flask log shows: `POST /shopping/campaign_rules/{id}/toggle HTTP/1.1 200`

**Visual Verification Required:**
- Screenshot showing rule in disabled state
- Screenshot of Flask terminal showing POST 200

---

**Test 4: Save As Template**

**Steps:**
1. Click ⋮ dropdown on any rule
2. Click "Save as template"
3. Prompt appears asking for template name
4. Enter name: "High CPA Template"
5. Click OK
6. Toast notification appears
7. Templates section badge updates to "Templates (1)"

**Verify:**
- Toast: "Template saved successfully"
- Templates badge incremented
- Click "Show" on Templates section - template appears
- Console has zero errors
- Flask log shows: `POST /shopping/campaign_rules/{id}/save-as-template HTTP/1.1 200`

**Visual Verification Required:**
- Screenshot of prompt dialog
- Screenshot of Templates section expanded showing new template
- Screenshot of console showing zero errors

---

**Test 5: Delete Rule**

**Steps:**
1. Click ⋮ dropdown on test rule created in Test 1
2. Click "Delete"
3. Confirm dialog appears
4. Click "OK" to confirm
5. Rule disappears from table

**Verify:**
- Toast: "Rule deleted successfully"
- Rule no longer in table
- Console has zero errors
- Flask log shows: `DELETE /shopping/campaign_rules/{id} HTTP/1.1 200`

**Visual Verification Required:**
- Screenshot of table after deletion (test rule gone)
- Screenshot of console showing zero errors

---

**Checkpoint 5 - All Tests Passed:**

**Report back with:**
- Confirmation that all 5 functional tests completed successfully
- Collection of all screenshots from tests 1-5
- Statement: "Zero console errors throughout all testing"
- Statement: "All Flask routes returned 200 status"
- Final screenshot of working table with all features functional

**STOP IF:**
- Any test fails
- Console errors appear during testing
- Modal doesn't open or doesn't populate
- CRUD operations return errors

---

## REFERENCE FILES

**Primary references (copy patterns from these):**

1. **Flow Builder Component:**
   - `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\components\ads_rules_flow_builder.html`
   - Most recent pattern, cleanest implementation
   - Copy entire file, rename functions, update IDs

2. **Page Template with Table:**
   - `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\ads.html` (lines 500-950)
   - Shows complete Rules tab structure
   - JavaScript functions for load/render/actions
   - Template section with collapse

3. **CRUD Routes:**
   - `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\ads.py` (lines 200-500)
   - All 6 routes with correct patterns
   - Validation, error handling, JSON responses
   - Database queries with entity_type filter

4. **Alternative Reference (if needed):**
   - `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\keywords.html`
   - `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\keywords.py`
   - Similar patterns, slightly older implementation

5. **Metric Map Reference:**
   - `C:\Users\User\Desktop\gads-data-layer\act_autopilot\recommendations_engine.py`
   - Search for `SHOPPING_CAMPAIGN_METRIC_MAP`
   - Use these exact metric keys in flow builder dropdown

---

## CRITICAL PITFALLS TO AVOID

### Pitfall 1: JavaScript Syntax Errors (Chat 111 failure cause)
**Problem:** Unescaped apostrophes in label strings cause `SyntaxError: Unexpected string`  
**Example:** `'campaign's baseline'` breaks JavaScript parser  
**Fix:** Escape as `'campaign\'s baseline'` OR use double quotes `"campaign's baseline"`  
**Check:** After creating flow builder, load page and check console BEFORE proceeding

### Pitfall 2: Entity Type Mismatch
**Problem:** Using `'shopping_campaign'` instead of `'shopping'` returns zero results  
**Fix:** ALL queries use `entity_type = 'shopping'`  
**Verified:** Chat 111 found correct value is `'shopping'`

### Pitfall 3: Function Not Exposed to Global Scope
**Problem:** `onclick="someFunction()"` fails silently - function not accessible  
**Fix:** Expose via `window.someFunction = function(...) {...}`  
**Example:**
```javascript
(function() {
    function myFunction() { ... }
    window.myFunction = myFunction;  // ← Must expose
})();
```

### Pitfall 4: Bootstrap 5 vs Bootstrap 4 Syntax
**Problem:** Using `data-toggle="dropdown"` instead of `data-bs-toggle="dropdown"`  
**Fix:** Bootstrap 5 requires `data-bs-` prefix for all data attributes  
**Check:** Search codebase for any `data-toggle=` and update to `data-bs-toggle=`

### Pitfall 5: CSRF Exemptions Not Applied
**Problem:** Routes return 400 Bad Request due to missing CSRF token  
**Fix:** Add all 6 routes to CSRF exemption list in `__init__.py`  
**Verify:** Flask startup log should show 6 `✅ [Chat 111 Redux] CSRF exempted:` lines

### Pitfall 6: Wrong Reference File
**Problem:** Using old patterns from campaigns.py (Chat 91) instead of ads.py (Chat 109)  
**Fix:** ALWAYS use ads.py and ads.html as reference - most recent, cleanest patterns  
**Why:** Ads implementation (Chat 109) includes all improvements from earlier entities

### Pitfall 7: Reporting Success Without Visual Verification
**Problem:** Flask log shows 200 OK but page is actually blank or broken  
**Fix:** MUST load page in Opera browser and verify table renders with data  
**Proof Required:** Screenshots of working page + console showing zero errors

### Pitfall 8: Forgetting to Call loadShoppingCampaignRules() on Page Load
**Problem:** Table never loads - shows spinner forever
**Fix:** Call `loadShoppingCampaignRules()` inside DOMContentLoaded event listener
**Location:** In shopping_new.html JavaScript section

### Pitfall 9: Missing CSS Toast Wrapper Rule
**Problem:** Toast notifications appear in wrong position or not at all
**Fix:** Add `#shopping-campaign-rules-toast-wrap` to rules.css combined selector

### Pitfall 10: Wrong JSON Response Format
**Problem:** Frontend JavaScript expects specific keys but routes return different format
**Fix:** List route MUST return `{success: true, rules: [...], templates: [...]}`
**Fix:** Other routes MUST return `{success: true/false, message: "..."}`

---

## SUCCESS CRITERIA - ALL MUST PASS

**Visual Verification:**
- ✅ Shopping > Rules tab shows table (not cards, not blank)
- ✅ Table displays 14 campaign rules with all columns populated
- ✅ "Create Rule" button visible and functional
- ✅ Each rule row has ⋮ Actions dropdown
- ✅ Templates section shows "Templates (X)" badge

**Console Verification:**
- ✅ Zero SyntaxError in browser console
- ✅ Zero 404 errors in console
- ✅ All `/shopping/campaign_rules` requests return 200 OK

**Functional Verification:**
- ✅ Create rule: Modal opens, save works, new rule appears
- ✅ Edit rule: Modal pre-populates, update works, changes reflected
- ✅ Toggle: Switch works, status changes, no page reload
- ✅ Save template: Creates template, increments badge, template appears in section
- ✅ Delete: Removes rule from table, no errors

**Flask Log Verification:**
- ✅ 6 CSRF exemption lines in startup log
- ✅ GET /shopping/campaign_rules returns 200
- ✅ POST /shopping/campaign_rules returns 200 (create)
- ✅ PUT /shopping/campaign_rules/{id} returns 200 (update)
- ✅ POST /shopping/campaign_rules/{id}/toggle returns 200
- ✅ POST /shopping/campaign_rules/{id}/save-as-template returns 200
- ✅ DELETE /shopping/campaign_rules/{id} returns 200

**Database Verification:**
```powershell
python -c "import duckdb; conn = duckdb.connect('warehouse.duckdb'); print(f\"Campaign rules: {conn.execute('SELECT COUNT(*) FROM rules WHERE entity_type=\\'shopping\\' AND (is_template=FALSE OR is_template IS NULL)').fetchone()[0]}\"); print(f\"Templates: {conn.execute('SELECT COUNT(*) FROM rules WHERE entity_type=\\'shopping\\' AND is_template=TRUE').fetchone()[0]}\"); conn.close()"
```
Expected: `Campaign rules: 14+, Templates: 1+` (after tests)

**Proof of Completion:**
- Screenshot of table with rules visible
- Screenshot of console showing zero errors
- Screenshot of Flask log showing 200 responses
- Confirmation that all 5 functional tests passed

---

## DELIVERABLES

### Files Created:
1. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\components\shopping_campaign_rules_flow_builder.html`
2. `C:\Users\User\Desktop\gads-data-layer\scripts\migrate_shopping_campaign_rules_to_db.py`

### Files Modified:
1. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\shopping_new.html`
   - Rules tab section replaced (lines ~400-600, approximate)
   - JavaScript functions added inside DOMContentLoaded (lines ~900-1400, approximate)

2. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\shopping.py`
   - 6 new routes added for campaign rules CRUD operations
   - Imports updated (json, datetime)

3. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\__init__.py`
   - 6 CSRF exemption lines added

4. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\static\css\rules.css`
   - Added `#shopping-campaign-rules-toast-wrap` to combined toast position rule

### Database Changes:
- 14 rules inserted into `rules` table with `entity_type='shopping'`
- Existing rules preserved (not modified)

---

## HANDOFF DOCUMENTATION

Create `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_111_REDUX_HANDOFF.md` with:
- Summary of changes made
- Files created/modified with line counts
- Database queries to verify state
- Screenshots of working UI
- Known issues or limitations
- Next steps (Chat 112: Product rules + toggle)

---

## FINAL NOTES

**Scope discipline:** This brief is laser-focused on campaign rules ONLY. Product rules, toggle buttons, and any product-level functionality belongs in Chat 112.

**Testing discipline:** Visual verification is mandatory at each checkpoint. Do not proceed to next step if any checkpoint fails. Do not report complete without screenshots proving success.

**Reference discipline:** Always use ads.py and ads.html as primary reference. They contain the most recent patterns and all improvements from previous entity implementations.

**Visual verification is NON-NEGOTIABLE:** After each major step, you MUST load the page in Opera browser, take screenshots of the page and console, and verify the expected state matches reality before proceeding. Flask logs alone are not sufficient proof.

**JSON Response Formats:** All routes must return consistent JSON structure. List route returns `{success, rules, templates}`. All other routes return `{success, message}`.

**Function Exposure:** ALL JavaScript functions called from inline onclick or from flow builder must be exposed via `window.fnName = function(...) {...}`. Functions defined inside IIFEs or DOMContentLoaded wrappers are NOT accessible from inline handlers unless explicitly exposed.

**Database Entity Type:** Use `entity_type = 'shopping'` in ALL queries. NOT `'shopping_campaign'`. This is verified correct from Chat 111 findings.

---

**END OF BRIEF**
