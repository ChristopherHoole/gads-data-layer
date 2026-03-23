# CHAT 112: SHOPPING PRODUCT RULES + CAMPAIGN/PRODUCT TOGGLE (V2)

**Date:** 2026-03-23  
**Priority:** HIGH  
**Estimated Time:** 4-6 hours  
**Dependencies:** Chat 111 Redux complete (Shopping Campaign Rules working)

---

## OBJECTIVE

Add Product Rules functionality to Shopping page with Campaign/Product toggle buttons. Users can switch between Campaign Rules view (existing) and Product Rules view (new). Create flow builder, routes, and database rules for 10 Product Rules + 6 Product Flags.

---

## ⚠️ CRITICAL PRE-FLIGHT CHECK

**BEFORE starting Step 1, you MUST verify the product table structure.**

Run this diagnostic script to check what columns exist:

```python
import duckdb
conn = duckdb.connect('warehouse.duckdb')

print("\n=== PRODUCT FEATURES TABLE SCHEMA ===\n")
cols = conn.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_schema='analytics' AND table_name='product_features_daily'
    ORDER BY ordinal_position
""").fetchall()

for col in cols:
    print(f"{col[0]}: {col[1]}")

print("\n=== SAMPLE PRODUCT ROW ===\n")
sample = conn.execute("SELECT * FROM analytics.product_features_daily LIMIT 1").fetchone()
if sample:
    col_names = [desc[0] for desc in conn.execute("SELECT * FROM analytics.product_features_daily LIMIT 0").description]
    for i, col_name in enumerate(col_names):
        print(f"{col_name}: {sample[i]}")

conn.close()
```

**STOP and report back with output BEFORE proceeding.**

**If there is NO "priority" column:** We will need to adjust the rules specification. Report this immediately.

**Expected WoW columns:** `roas_vs_prev_pct`, `cost_vs_prev_pct`, `ctr_vs_prev_pct` will exist but ALL values are 0.0 due to DuckDB nested window function limitation. This means WoW-based flags will never fire on synthetic data, but the rules/flags should still be created for when real data is available.

---

## SCOPE

**✅ IN SCOPE:**
- Campaign/Product toggle buttons at top of Rules section
- Product Rules flow builder component
- Product Rules CRUD routes (6 routes: list, create, update, delete, toggle, save-as-template)
- Product Rules table UI (matches campaign rules pattern)
- JavaScript for toggle functionality + table population
- Database migration script: create 10 Product Rules + 6 Product Flags
- Comprehensive testing with specific test cases
- All functionality tested and verified working

**❌ OUT OF SCOPE:**
- Any changes to Campaign Rules (already complete)
- Any changes to Flags tab (already complete)
- Shopping campaign-level functionality
- Product recommendations engine integration (future work)
- Fixing WoW columns (known DuckDB limitation)

---

## PRODUCT RULES SPECIFICATION

### 10 Product Rules (All entity_type='shopping_product'):

**IMPORTANT:** If "priority" column doesn't exist in product_features_daily, STOP and report. We will adjust rules.

**Priority Optimization (4 rules):**
1. **Increase Priority - High ROAS Product**
   - Conditions: `[{"metric": "roas_7d", "op": "gte", "value": 5.0, "ref": "absolute"}, {"metric": "conversions_7d", "op": "gte", "value": 5, "ref": "absolute"}]`
   - Action: `increase_priority` (magnitude: 1.0)
   - Type: `priority`, Risk: `low`, Cooldown: 7 days
   - Plain English: "Increase Priority by 1 level when ROAS (7d) >= 5.0 and Conversions >= 5"

2. **Decrease Priority - Poor ROAS Product**
   - Conditions: `[{"metric": "roas_7d", "op": "lt", "value": 2.0, "ref": "absolute"}, {"metric": "conversions_7d", "op": "gte", "value": 5, "ref": "absolute"}]`
   - Action: `decrease_priority` (magnitude: 1.0)
   - Type: `priority`, Risk: `medium`, Cooldown: 7 days
   - Plain English: "Decrease Priority by 1 level when ROAS (7d) < 2.0 and Conversions >= 5"

3. **Increase Priority - High CTR Product**
   - Conditions: `[{"metric": "ctr_7d", "op": "gt", "value": 0.02, "ref": "absolute"}, {"metric": "impressions_7d", "op": "gte", "value": 100, "ref": "absolute"}]`
   - Action: `increase_priority` (magnitude: 1.0)
   - Type: `priority`, Risk: `low`, Cooldown: 7 days
   - Plain English: "Increase Priority by 1 level when CTR (7d) > 2% and Impressions >= 100"

4. **Decrease Priority - Low CTR Product**
   - Conditions: `[{"metric": "ctr_7d", "op": "lt", "value": 0.005, "ref": "absolute"}, {"metric": "impressions_7d", "op": "gte", "value": 200, "ref": "absolute"}]`
   - Action: `decrease_priority` (magnitude: 1.0)
   - Type: `priority`, Risk: `low`, Cooldown: 7 days
   - Plain English: "Decrease Priority by 1 level when CTR (7d) < 0.5% and Impressions >= 200"

**Status Rules (4 rules):**
5. **Pause Product - Zero Conversions High Spend**
   - Conditions: `[{"metric": "cost_7d", "op": "gte", "value": 50.0, "ref": "absolute"}, {"metric": "conversions_7d", "op": "eq", "value": 0, "ref": "absolute"}]`
   - Action: `pause` (magnitude: null)
   - Type: `status`, Risk: `medium`, Cooldown: 14 days
   - Plain English: "Pause Product when Cost (7d) >= £50 and Conversions = 0"

6. **Pause Product - Extremely Poor ROAS**
   - Conditions: `[{"metric": "roas_7d", "op": "lt", "value": 1.0, "ref": "absolute"}, {"metric": "conversions_7d", "op": "gte", "value": 5, "ref": "absolute"}]`
   - Action: `pause` (magnitude: null)
   - Type: `status`, Risk: `high`, Cooldown: 14 days
   - Plain English: "Pause Product when ROAS (7d) < 1.0 and Conversions >= 5"

7. **Pause Product - High Cost Low ROAS**
   - Conditions: `[{"metric": "cost_7d", "op": "gte", "value": 100.0, "ref": "absolute"}, {"metric": "roas_7d", "op": "lt", "value": 2.0, "ref": "absolute"}]`
   - Action: `pause` (magnitude: null)
   - Type: `status`, Risk: `medium`, Cooldown: 14 days
   - Plain English: "Pause Product when Cost (7d) >= £100 and ROAS < 2.0"

8. **Pause Product - Low CTR High Cost**
   - Conditions: `[{"metric": "ctr_7d", "op": "lt", "value": 0.005, "ref": "absolute"}, {"metric": "cost_7d", "op": "gte", "value": 30.0, "ref": "absolute"}]`
   - Action: `pause` (magnitude: null)
   - Type: `status`, Risk: `medium`, Cooldown: 7 days
   - Plain English: "Pause Product when CTR (7d) < 0.5% and Cost >= £30"

**Volume Rules (2 rules):**
9. **Increase Priority - High Volume Product**
   - Conditions: `[{"metric": "impressions_7d", "op": "gte", "value": 1000, "ref": "absolute"}, {"metric": "ctr_7d", "op": "gt", "value": 0.015, "ref": "absolute"}]`
   - Action: `increase_priority` (magnitude: 1.0)
   - Type: `priority`, Risk: `low`, Cooldown: 7 days
   - Plain English: "Increase Priority by 1 level when Impressions >= 1000 and CTR > 1.5%"

10. **Decrease Priority - Low Engagement High Visibility**
    - Conditions: `[{"metric": "impressions_7d", "op": "gte", "value": 500, "ref": "absolute"}, {"metric": "ctr_7d", "op": "lt", "value": 0.005, "ref": "absolute"}]`
    - Action: `decrease_priority` (magnitude: 1.0)
    - Type: `priority`, Risk: `low`, Cooldown: 7 days
    - Plain English: "Decrease Priority by 1 level when Impressions >= 500 and CTR < 0.5%"

### 6 Product Flags (All entity_type='shopping_product', rule_or_flag='flag'):

1. **Flag - High Cost Zero Conversions**
   - Conditions: `[{"metric": "cost_7d", "op": "gte", "value": 30.0, "ref": "absolute"}, {"metric": "conversions_7d", "op": "eq", "value": 0, "ref": "absolute"}]`
   - Type: `performance`, Cooldown: 7 days
   - Plain English: "Flag when Cost (7d) >= £30 and Conversions = 0"

2. **Flag - Product ROAS Drop**
   - Conditions: `[{"metric": "roas_vs_prev_pct", "op": "lt", "value": -0.40, "ref": "week_over_week"}]`
   - Type: `anomaly`, Cooldown: 7 days
   - Plain English: "Flag when ROAS declined > 40% vs previous 7d"
   - **NOTE:** Will not fire on synthetic data (WoW columns are 0.0)

3. **Flag - Product CTR Drop**
   - Conditions: `[{"metric": "ctr_vs_prev_pct", "op": "lt", "value": -0.30, "ref": "week_over_week"}]`
   - Type: `anomaly`, Cooldown: 7 days
   - Plain English: "Flag when CTR declined > 30% vs previous 7d"
   - **NOTE:** Will not fire on synthetic data (WoW columns are 0.0)

4. **Flag - High Impression Share Loss**
   - Conditions: `[{"metric": "impression_share_lost_rank", "op": "gt", "value": 0.30, "ref": "absolute"}]`
   - Type: `performance`, Cooldown: 7 days
   - Plain English: "Flag when Impression Share Lost to Rank > 30%"

5. **Flag - Sudden Cost Spike**
   - Conditions: `[{"metric": "cost_vs_prev_pct", "op": "gt", "value": 0.50, "ref": "week_over_week"}]`
   - Type: `anomaly`, Cooldown: 7 days
   - Plain English: "Flag when Cost increased > 50% vs previous 7d"
   - **NOTE:** Will not fire on synthetic data (WoW columns are 0.0)

6. **Flag - High CTR Opportunity**
   - Conditions: `[{"metric": "ctr_7d", "op": "gt", "value": 0.02, "ref": "absolute"}, {"metric": "impressions_7d", "op": "gte", "value": 200, "ref": "absolute"}]`
   - Type: `performance`, Cooldown: 7 days
   - Plain English: "Flag when CTR (7d) > 2% and Impressions >= 200"

---

## TECHNICAL CONSTRAINTS

### Entity Type
- **Database:** `entity_type = 'shopping_product'` (NOT 'product', NOT 'shopping', NOT 'shopping_campaign')
- **All queries MUST filter:** `WHERE entity_type = 'shopping_product'`

### Toggle State
- Use JavaScript to show/hide campaign vs product tables
- Default view: Campaign Rules
- State persists in JavaScript variable (not session — page refresh = default)

### Operators
- Use string operators: "gt", "lt", "gte", "lte", "eq"
- NOT symbols: ">", "<", ">=", etc.

### Cost/Percentage Values
- **Cost:** Store as pounds (not micros): £50 = 50.0, £100 = 100.0
- **Percentages as decimals:** 2% = 0.02, 40% = 0.40, -40% = -0.40
- **CTR stored as decimal:** 2% CTR = 0.02

### JavaScript
- All functions called from onclick MUST be exposed via `window.fnName`
- Apostrophes in strings MUST be escaped: `\'` or use double quotes
- Bootstrap 5: `data-bs-toggle="dropdown"` NOT `data-toggle`

---

## EXECUTION PLAN

### STEP 0: Pre-Flight Schema Verification

**Run the diagnostic script from "CRITICAL PRE-FLIGHT CHECK" section above.**

**STOP and report schema before proceeding to Step 1.**

---

### STEP 1: Create Product Rules Flow Builder Component

**File:** `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\components\product_rules_flow_builder.html`

**Action:**
1. Copy `shopping_campaign_rules_flow_builder.html`
2. Global find/replace: `shoppingCampaignRfb` → `productRfb`
3. Update modal ID: `shoppingCampaignRulesFlowModal` → `productRulesFlowModal`
4. Update toast wrapper ID: `shopping-campaign-rules-toast-wrap` → `product-rules-toast-wrap`
5. Update all entity type references: `'shopping'` → `'shopping_product'`

**Action Types Dropdown:**
Update to include product-specific actions:
```javascript
const ACTION_TYPE_OPTIONS = {
    'priority': [
        {value: 'increase_priority', label: 'Increase Priority'},
        {value: 'decrease_priority', label: 'Decrease Priority'}
    ],
    'status': [
        {value: 'pause', label: 'Pause Product'}
    ]
};
```

**Metrics Dropdown:**
Update to include product metrics:
```javascript
const PRODUCT_METRICS = [
    {value: 'roas_7d', label: 'ROAS (7d)'},
    {value: 'roas_14d', label: 'ROAS (14d)'},
    {value: 'roas_30d', label: 'ROAS (30d)'},
    {value: 'cost_7d', label: 'Cost (7d)'},
    {value: 'cost_14d', label: 'Cost (14d)'},
    {value: 'cost_30d', label: 'Cost (30d)'},
    {value: 'conversions_7d', label: 'Conversions (7d)'},
    {value: 'conversions_14d', label: 'Conversions (14d)'},
    {value: 'conversions_30d', label: 'Conversions (30d)'},
    {value: 'ctr_7d', label: 'CTR (7d)'},
    {value: 'ctr_14d', label: 'CTR (14d)'},
    {value: 'ctr_30d', label: 'CTR (30d)'},
    {value: 'impressions_7d', label: 'Impressions (7d)'},
    {value: 'impressions_14d', label: 'Impressions (14d)'},
    {value: 'impressions_30d', label: 'Impressions (30d)'},
    {value: 'clicks_7d', label: 'Clicks (7d)'},
    {value: 'clicks_14d', label: 'Clicks (14d)'},
    {value: 'clicks_30d', label: 'Clicks (30d)'},
    {value: 'roas_vs_prev_pct', label: 'ROAS % Change (WoW)'},
    {value: 'ctr_vs_prev_pct', label: 'CTR % Change (WoW)'},
    {value: 'cost_vs_prev_pct', label: 'Cost % Change (WoW)'},
    {value: 'impression_share_lost_rank', label: 'IS Lost to Rank'},
    {value: 'impression_share_lost_budget', label: 'IS Lost to Budget'}
];
```

**Checkpoint:**
- Save file
- Restart Flask
- Navigate to Shopping page
- Open browser console (F12)
- Check for SyntaxError
- **STOP if any JavaScript errors found**
- **Report:** "Step 1 complete - zero console errors"

---

### STEP 2: Add Toggle Buttons to Shopping Page

**File:** `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\shopping_new.html`

**Location:** Find the line `<div id="shopping-campaign-rules-section">` and insert IMMEDIATELY BEFORE it:

```html
<!-- Campaign/Product Toggle Buttons -->
<div class="btn-group mb-3" role="group" aria-label="Rules view toggle">
    <button type="button" class="btn btn-sm btn-primary active" id="btnCampaignRules" onclick="showCampaignRules()">
        Campaign Rules
    </button>
    <button type="button" class="btn btn-sm btn-outline-primary" id="btnProductRules" onclick="showProductRules()">
        Product Rules
    </button>
</div>
```

**Checkpoint:**
- Save file
- Restart Flask
- Navigate to Shopping > Rules tab
- Verify toggle buttons appear above table
- **STOP if buttons don't render**
- **Report:** "Step 2 complete - toggle buttons visible"

---

### STEP 3: Add Product Rules Section to Shopping Page

**File:** `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\shopping_new.html`

**Location:** Find the closing `</div>` of `shopping-campaign-rules-section` and insert IMMEDIATELY AFTER it:

```html
<!-- Product Rules Section (hidden by default) -->
<div id="shopping-product-rules-section" style="display: none;">
    <div class="d-flex justify-content-between align-items-center mb-3">
        <h5>Shopping product rules & flags</h5>
        <div>
            <button class="btn btn-sm btn-outline-secondary me-2" onclick="productUseTemplate()">
                Use template
            </button>
            <button class="btn btn-sm btn-primary" onclick="productOpenRulesFlow('create')">
                <i class="bi bi-plus-circle me-1"></i> Add rule or flag
            </button>
        </div>
    </div>

    <!-- Product Rules Table -->
    <div id="product-rules-content">
        <p class="text-muted">Loading product rules...</p>
    </div>

    {% include 'components/product_rules_flow_builder.html' %}
</div>
```

**Checkpoint:**
- Save file
- Restart Flask
- Navigate to Shopping > Rules tab
- Product section should be hidden by default
- Console should have zero errors
- **STOP if console shows errors**
- **Report:** "Step 3 complete - product section added (hidden)"

---

### STEP 4: Add JavaScript Toggle Functions

**File:** `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\shopping_new.html`

**Location:** Find the `<script>` section at bottom of file and add BEFORE the closing `</script>`:

```javascript
// ============================================================================
// CAMPAIGN/PRODUCT TOGGLE FUNCTIONS
// ============================================================================

window.productRulesLoaded = false;

window.showCampaignRules = function() {
    document.getElementById('shopping-campaign-rules-section').style.display = 'block';
    document.getElementById('shopping-product-rules-section').style.display = 'none';
    
    document.getElementById('btnCampaignRules').classList.add('active', 'btn-primary');
    document.getElementById('btnCampaignRules').classList.remove('btn-outline-primary');
    
    document.getElementById('btnProductRules').classList.remove('active', 'btn-primary');
    document.getElementById('btnProductRules').classList.add('btn-outline-primary');
};

window.showProductRules = function() {
    document.getElementById('shopping-campaign-rules-section').style.display = 'none';
    document.getElementById('shopping-product-rules-section').style.display = 'block';
    
    document.getElementById('btnCampaignRules').classList.remove('active', 'btn-primary');
    document.getElementById('btnCampaignRules').classList.add('btn-outline-primary');
    
    document.getElementById('btnProductRules').classList.add('active', 'btn-primary');
    document.getElementById('btnProductRules').classList.remove('btn-outline-primary');
    
    // Load product rules if not already loaded
    if (!window.productRulesLoaded) {
        loadProductRules();
        window.productRulesLoaded = true;
    }
};

window.loadProductRules = function() {
    fetch('/shopping/product_rules')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                renderProductRulesTable(data.rules, data.templates);
            } else {
                document.getElementById('product-rules-content').innerHTML = 
                    '<div class="alert alert-warning">Failed to load product rules</div>';
            }
        })
        .catch(error => {
            console.error('Error loading product rules:', error);
            document.getElementById('product-rules-content').innerHTML = 
                '<div class="alert alert-danger">Error loading product rules</div>';
        });
};

window.renderProductRulesTable = function(rules, templates) {
    let html = `
        <!-- Rule Type Filter Tabs -->
        <ul class="nav nav-tabs mb-3" id="productRuleTabs">
            <li class="nav-item">
                <a class="nav-link active" data-filter="all" href="#" onclick="filterProductRules('all'); return false;">
                    All
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link" data-filter="priority" href="#" onclick="filterProductRules('priority'); return false;">
                    Priority
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link" data-filter="status" href="#" onclick="filterProductRules('status'); return false;">
                    Status
                </a>
            </li>
        </ul>

        <!-- Rules Table -->
        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th style="width: 60px;">ON/OFF</th>
                        <th style="width: 250px;">RULE NAME</th>
                        <th style="width: 120px;">PRODUCTS</th>
                        <th>PLAIN ENGLISH</th>
                        <th style="width: 80px;">RULE/FLAG</th>
                        <th style="width: 100px;">RULE TYPE</th>
                        <th style="width: 150px;">CONDITIONS</th>
                        <th style="width: 150px;">ACTION</th>
                        <th style="width: 80px;">COOLDOWN</th>
                        <th style="width: 120px;">GUARDRAIL</th>
                        <th style="width: 80px;">RISK</th>
                        <th style="width: 60px;">ACTIONS</th>
                    </tr>
                </thead>
                <tbody id="productRulesTableBody">
    `;

    const displayRules = rules.filter(r => r.rule_or_flag === 'rule');
    
    displayRules.forEach(rule => {
        const riskBadge = rule.risk_level === 'low' ? 'success' : rule.risk_level === 'medium' ? 'warning' : 'danger';
        const ruleTypeBadge = rule.type === 'priority' ? 'info' : rule.type === 'status' ? 'warning' : 'primary';
        
        html += `
            <tr class="product-rule-row" data-rule-type="${rule.type}">
                <td>
                    <div class="form-check form-switch">
                        <input class="form-check-input" type="checkbox" ${rule.enabled ? 'checked' : ''} 
                               onclick="toggleProductRule(${rule.id})">
                    </div>
                </td>
                <td><strong>${rule.name}</strong></td>
                <td><span class="badge bg-secondary">All products</span></td>
                <td>${rule.plain_english || ''}</td>
                <td><span class="badge bg-primary">${rule.rule_or_flag}</span></td>
                <td><span class="badge bg-${ruleTypeBadge}">${rule.type}</span></td>
                <td>${formatConditions(rule.conditions)}</td>
                <td>${formatAction(rule.action_type, rule.action_magnitude)}</td>
                <td>${rule.cooldown_days} days</td>
                <td><span class="badge bg-info">Capped by Client Settings</span></td>
                <td><span class="badge bg-${riskBadge}">${rule.risk_level}</span></td>
                <td>
                    <div class="dropdown">
                        <button class="btn btn-sm btn-link" type="button" data-bs-toggle="dropdown">
                            <i class="bi bi-three-dots-vertical"></i>
                        </button>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="#" onclick="productEditRule(${rule.id}); return false;">Edit</a></li>
                            <li><a class="dropdown-item" href="#" onclick="productSaveAsTemplate(${rule.id}); return false;">Save as template</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item text-danger" href="#" onclick="productDeleteRule(${rule.id}); return false;">Delete</a></li>
                        </ul>
                    </div>
                </td>
            </tr>
        `;
    });

    html += `
                </tbody>
            </table>
        </div>

        <!-- Templates Section -->
        <div class="mt-4">
            <h6>Templates <span class="badge bg-secondary">${templates.length}</span></h6>
            <div id="productTemplatesSection">
    `;

    if (templates.length === 0) {
        html += '<p class="text-muted">No templates saved yet</p>';
    } else {
        templates.forEach(tpl => {
            html += `
                <div class="card mb-2">
                    <div class="card-body p-2">
                        <strong>${tpl.name}</strong>
                        <button class="btn btn-sm btn-primary float-end" onclick="productUseThisTemplate(${tpl.id})">
                            Use template
                        </button>
                    </div>
                </div>
            `;
        });
    }

    html += `
            </div>
        </div>
    `;

    document.getElementById('product-rules-content').innerHTML = html;
};

function formatConditions(conditions) {
    try {
        const conds = JSON.parse(conditions);
        return conds.map(c => `${c.metric} ${c.op} ${c.value}`).join(', ');
    } catch {
        return 'N/A';
    }
}

function formatAction(actionType, magnitude) {
    if (actionType === 'increase_priority' || actionType === 'decrease_priority') {
        const direction = actionType.includes('increase') ? '↑' : '↓';
        return `${direction} Priority ${magnitude || 1} level`;
    }
    if (actionType === 'pause') {
        return '⏸ Pause Product';
    }
    return actionType;
}

window.filterProductRules = function(type) {
    document.querySelectorAll('#productRuleTabs .nav-link').forEach(link => {
        link.classList.remove('active');
    });
    document.querySelector(`#productRuleTabs [data-filter="${type}"]`).classList.add('active');
    
    document.querySelectorAll('.product-rule-row').forEach(row => {
        if (type === 'all' || row.dataset.ruleType === type) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
};

window.toggleProductRule = function(id) {
    fetch(`/shopping/product_rules/${id}/toggle`, {method: 'POST'})
        .then(response => response.json())
        .then(data => {
            if (!data.success) {
                alert('Failed to toggle rule');
            }
        });
};

window.productEditRule = function(id) {
    // Load rule data and open flow builder in edit mode
    fetch(`/shopping/product_rules`)
        .then(response => response.json())
        .then(data => {
            const rule = data.rules.find(r => r.id === id);
            if (rule) {
                window.productRfbOpenFlow('edit', rule);
            }
        });
};

window.productSaveAsTemplate = function(id) {
    if (confirm('Save this rule as a template?')) {
        fetch(`/shopping/product_rules/${id}/save-as-template`, {method: 'POST'})
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    window.productRulesLoaded = false;
                    loadProductRules();
                }
            });
    }
};

window.productDeleteRule = function(id) {
    if (confirm('Delete this rule permanently?')) {
        fetch(`/shopping/product_rules/${id}`, {method: 'DELETE'})
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    window.productRulesLoaded = false;
                    loadProductRules();
                }
            });
    }
};

window.productUseTemplate = function() {
    alert('Select a template from the Templates section below');
};

window.productUseThisTemplate = function(id) {
    fetch(`/shopping/product_rules`)
        .then(response => response.json())
        .then(data => {
            const template = data.templates.find(t => t.id === id);
            if (template) {
                window.productRfbOpenFlow('create', template);
            }
        });
};

window.productOpenRulesFlow = function(mode, data) {
    window.productRfbOpenFlow(mode, data);
};
```

**Checkpoint:**
- Save file
- Restart Flask
- Navigate to Shopping > Rules tab
- Click "Product Rules" button
- Section should switch
- Console should show zero errors
- **STOP if toggle doesn't work or console has errors**
- **Report:** "Step 4 complete - toggle working, zero console errors"

---

### STEP 5: Add Product Rules CRUD Routes

**File:** `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\shopping.py`

**Location:** Add at end of file, before final imports/exports

**Complete implementation:**

```python
# ============================================================================
# PRODUCT RULES CRUD ROUTES (Chat 112)
# ============================================================================

@shopping_bp.route('/shopping/product_rules', methods=['GET'])
def product_list_rules():
    """List all product rules and templates"""
    try:
        client_config = session.get('current_client_config')
        if not client_config:
            return jsonify({'success': False, 'message': 'No client selected'}), 400
        
        conn = _get_warehouse()
        
        # Get rules
        rules = conn.execute("""
            SELECT id, client_config, entity_type, name, rule_or_flag, type,
                   campaign_type_lock, entity_scope, conditions, action_type,
                   action_magnitude, cooldown_days, risk_level, enabled,
                   plain_english, is_template, created_at, updated_at
            FROM rules
            WHERE client_config = ?
              AND entity_type = 'shopping_product'
              AND (is_template = FALSE OR is_template IS NULL)
            ORDER BY type, name
        """, [client_config]).fetchall()
        
        # Get templates
        templates = conn.execute("""
            SELECT id, name, type, conditions, action_type, action_magnitude,
                   cooldown_days, risk_level
            FROM rules
            WHERE client_config = ?
              AND entity_type = 'shopping_product'
              AND is_template = TRUE
            ORDER BY name
        """, [client_config]).fetchall()
        
        conn.close()
        
        # Convert to dicts
        rules_list = [dict(zip([desc[0] for desc in rules], row)) for row in rules]
        templates_list = [dict(zip([desc[0] for desc in templates], row)) for row in templates]
        
        return jsonify({'success': True, 'rules': rules_list, 'templates': templates_list})
        
    except Exception as e:
        print(f"[ERROR] product_list_rules: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@shopping_bp.route('/shopping/product_rules', methods=['POST'])
def product_create_rule():
    """Create new product rule"""
    try:
        client_config = session.get('current_client_config')
        if not client_config:
            return jsonify({'success': False, 'message': 'No client selected'}), 400
        
        data = request.get_json()
        
        conn = _get_warehouse()
        
        # Get max ID
        max_id = conn.execute("SELECT COALESCE(MAX(id), 0) FROM rules").fetchone()[0]
        new_id = max_id + 1
        
        # Insert
        conn.execute("""
            INSERT INTO rules (
                id, client_config, entity_type, name, rule_or_flag, type,
                campaign_type_lock, entity_scope, conditions, action_type,
                action_magnitude, cooldown_days, risk_level, enabled,
                plain_english, is_template, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            new_id,
            client_config,
            'shopping_product',
            data['name'],
            data.get('rule_or_flag', 'rule'),
            data['type'],
            data.get('campaign_type_lock'),
            json.dumps(data.get('entity_scope', {'scope': 'all'})),
            json.dumps(data['conditions']),
            data.get('action_type'),
            data.get('action_magnitude'),
            data['cooldown_days'],
            data['risk_level'],
            data.get('enabled', True),
            data.get('plain_english', ''),
            False,
            datetime.now(),
            datetime.now()
        ])
        
        conn.close()
        
        return jsonify({'success': True, 'id': new_id})
        
    except Exception as e:
        print(f"[ERROR] product_create_rule: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@shopping_bp.route('/shopping/product_rules/<int:rule_id>', methods=['PUT'])
def product_update_rule(rule_id):
    """Update existing product rule"""
    try:
        data = request.get_json()
        
        conn = _get_warehouse()
        
        conn.execute("""
            UPDATE rules
            SET name = ?,
                type = ?,
                conditions = ?,
                action_type = ?,
                action_magnitude = ?,
                cooldown_days = ?,
                risk_level = ?,
                plain_english = ?,
                updated_at = ?
            WHERE id = ?
              AND entity_type = 'shopping_product'
        """, [
            data['name'],
            data['type'],
            json.dumps(data['conditions']),
            data.get('action_type'),
            data.get('action_magnitude'),
            data['cooldown_days'],
            data['risk_level'],
            data.get('plain_english', ''),
            datetime.now(),
            rule_id
        ])
        
        conn.close()
        
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"[ERROR] product_update_rule: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@shopping_bp.route('/shopping/product_rules/<int:rule_id>', methods=['DELETE'])
def product_delete_rule(rule_id):
    """Delete product rule"""
    try:
        conn = _get_warehouse()
        
        conn.execute("""
            DELETE FROM rules
            WHERE id = ?
              AND entity_type = 'shopping_product'
        """, [rule_id])
        
        conn.close()
        
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"[ERROR] product_delete_rule: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@shopping_bp.route('/shopping/product_rules/<int:rule_id>/toggle', methods=['POST'])
def product_toggle_rule(rule_id):
    """Toggle product rule enabled status"""
    try:
        conn = _get_warehouse()
        
        conn.execute("""
            UPDATE rules
            SET enabled = NOT enabled,
                updated_at = ?
            WHERE id = ?
              AND entity_type = 'shopping_product'
        """, [datetime.now(), rule_id])
        
        conn.close()
        
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"[ERROR] product_toggle_rule: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@shopping_bp.route('/shopping/product_rules/<int:rule_id>/save-as-template', methods=['POST'])
def product_save_as_template(rule_id):
    """Save product rule as template"""
    try:
        conn = _get_warehouse()
        
        # Get source rule
        rule = conn.execute("""
            SELECT * FROM rules WHERE id = ?
        """, [rule_id]).fetchone()
        
        if not rule:
            return jsonify({'success': False, 'message': 'Rule not found'}), 404
        
        # Get max ID
        max_id = conn.execute("SELECT COALESCE(MAX(id), 0) FROM rules").fetchone()[0]
        new_id = max_id + 1
        
        # Insert template copy
        conn.execute("""
            INSERT INTO rules (
                id, client_config, entity_type, name, rule_or_flag, type,
                campaign_type_lock, entity_scope, conditions, action_type,
                action_magnitude, cooldown_days, risk_level, enabled,
                plain_english, is_template, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            new_id,
            rule[1],  # client_config
            rule[2],  # entity_type
            rule[3] + ' (Template)',  # name
            rule[4],  # rule_or_flag
            rule[5],  # type
            rule[6],  # campaign_type_lock
            rule[7],  # entity_scope
            rule[8],  # conditions
            rule[9],  # action_type
            rule[10], # action_magnitude
            rule[11], # cooldown_days
            rule[12], # risk_level
            False,    # enabled
            rule[18], # plain_english
            True,     # is_template
            datetime.now(),
            datetime.now()
        ])
        
        conn.close()
        
        return jsonify({'success': True, 'id': new_id})
        
    except Exception as e:
        print(f"[ERROR] product_save_as_template: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
```

**Checkpoint:**
- Save file
- Restart Flask
- Check Flask startup log — should see NO errors during load
- Navigate to Shopping > Rules > Product Rules
- Click "Add rule or flag" button
- Modal should open
- **STOP if modal doesn't open or Flask errors appear**
- **Report:** "Step 5 complete - routes added, modal opens"

---

### STEP 6: Add CSRF Exemptions

**File:** `C:\Users\User\Desktop\gads-data-layer\act_dashboard/__init__.py`

**Location:** Find the CSRF exemption section (search for "Chat 111") and add AFTER the shopping campaign exemptions:

```python
# Chat 112: Product Rules CSRF Exemptions
print("✅ [Chat 112] CSRF exempted: shopping.product_list_rules")
csrf.exempt(shopping_bp.product_list_rules)
print("✅ [Chat 112] CSRF exempted: shopping.product_create_rule")
csrf.exempt(shopping_bp.product_create_rule)
print("✅ [Chat 112] CSRF exempted: shopping.product_update_rule")
csrf.exempt(shopping_bp.product_update_rule)
print("✅ [Chat 112] CSRF exempted: shopping.product_delete_rule")
csrf.exempt(shopping_bp.product_delete_rule)
print("✅ [Chat 112] CSRF exempted: shopping.product_toggle_rule")
csrf.exempt(shopping_bp.product_toggle_rule)
print("✅ [Chat 112] CSRF exempted: shopping.product_save_as_template")
csrf.exempt(shopping_bp.product_save_as_template)
```

**Checkpoint:**
- Save file
- Restart Flask
- Flask startup log MUST show 6 new CSRF exemption lines
- **STOP if exemptions don't appear**
- **Report:** "Step 6 complete - 6 CSRF exemptions confirmed in log"

---

### STEP 7: Create Database Migration Script

**File:** `C:\Users\User\Desktop\gads-data-layer\scripts\create_product_rules_and_flags.py`

**Complete script:**

```python
import duckdb
import json
from datetime import datetime

conn = duckdb.connect('warehouse.duckdb')

# Get current max ID
max_id = conn.execute("SELECT COALESCE(MAX(id), 0) FROM rules").fetchone()[0]
print(f"\nCurrent max rule ID: {max_id}")
print(f"New rules will start at ID: {max_id + 1}\n")

# Define all 16 rules/flags
items = [
    # 10 Product Rules
    {
        "name": "Increase Priority - High ROAS Product",
        "rule_or_flag": "rule",
        "type": "priority",
        "conditions": [
            {"metric": "roas_7d", "op": "gte", "value": 5.0, "ref": "absolute"},
            {"metric": "conversions_7d", "op": "gte", "value": 5, "ref": "absolute"}
        ],
        "action_type": "increase_priority",
        "action_magnitude": 1.0,
        "cooldown_days": 7,
        "risk_level": "low",
        "plain_english": "Increase Priority by 1 level when ROAS (7d) >= 5.0 and Conversions >= 5"
    },
    {
        "name": "Decrease Priority - Poor ROAS Product",
        "rule_or_flag": "rule",
        "type": "priority",
        "conditions": [
            {"metric": "roas_7d", "op": "lt", "value": 2.0, "ref": "absolute"},
            {"metric": "conversions_7d", "op": "gte", "value": 5, "ref": "absolute"}
        ],
        "action_type": "decrease_priority",
        "action_magnitude": 1.0,
        "cooldown_days": 7,
        "risk_level": "medium",
        "plain_english": "Decrease Priority by 1 level when ROAS (7d) < 2.0 and Conversions >= 5"
    },
    {
        "name": "Increase Priority - High CTR Product",
        "rule_or_flag": "rule",
        "type": "priority",
        "conditions": [
            {"metric": "ctr_7d", "op": "gt", "value": 0.02, "ref": "absolute"},
            {"metric": "impressions_7d", "op": "gte", "value": 100, "ref": "absolute"}
        ],
        "action_type": "increase_priority",
        "action_magnitude": 1.0,
        "cooldown_days": 7,
        "risk_level": "low",
        "plain_english": "Increase Priority by 1 level when CTR (7d) > 2% and Impressions >= 100"
    },
    {
        "name": "Decrease Priority - Low CTR Product",
        "rule_or_flag": "rule",
        "type": "priority",
        "conditions": [
            {"metric": "ctr_7d", "op": "lt", "value": 0.005, "ref": "absolute"},
            {"metric": "impressions_7d", "op": "gte", "value": 200, "ref": "absolute"}
        ],
        "action_type": "decrease_priority",
        "action_magnitude": 1.0,
        "cooldown_days": 7,
        "risk_level": "low",
        "plain_english": "Decrease Priority by 1 level when CTR (7d) < 0.5% and Impressions >= 200"
    },
    {
        "name": "Pause Product - Zero Conversions High Spend",
        "rule_or_flag": "rule",
        "type": "status",
        "conditions": [
            {"metric": "cost_7d", "op": "gte", "value": 50.0, "ref": "absolute"},
            {"metric": "conversions_7d", "op": "eq", "value": 0, "ref": "absolute"}
        ],
        "action_type": "pause",
        "action_magnitude": None,
        "cooldown_days": 14,
        "risk_level": "medium",
        "plain_english": "Pause Product when Cost (7d) >= £50 and Conversions = 0"
    },
    {
        "name": "Pause Product - Extremely Poor ROAS",
        "rule_or_flag": "rule",
        "type": "status",
        "conditions": [
            {"metric": "roas_7d", "op": "lt", "value": 1.0, "ref": "absolute"},
            {"metric": "conversions_7d", "op": "gte", "value": 5, "ref": "absolute"}
        ],
        "action_type": "pause",
        "action_magnitude": None,
        "cooldown_days": 14,
        "risk_level": "high",
        "plain_english": "Pause Product when ROAS (7d) < 1.0 and Conversions >= 5"
    },
    {
        "name": "Pause Product - High Cost Low ROAS",
        "rule_or_flag": "rule",
        "type": "status",
        "conditions": [
            {"metric": "cost_7d", "op": "gte", "value": 100.0, "ref": "absolute"},
            {"metric": "roas_7d", "op": "lt", "value": 2.0, "ref": "absolute"}
        ],
        "action_type": "pause",
        "action_magnitude": None,
        "cooldown_days": 14,
        "risk_level": "medium",
        "plain_english": "Pause Product when Cost (7d) >= £100 and ROAS < 2.0"
    },
    {
        "name": "Pause Product - Low CTR High Cost",
        "rule_or_flag": "rule",
        "type": "status",
        "conditions": [
            {"metric": "ctr_7d", "op": "lt", "value": 0.005, "ref": "absolute"},
            {"metric": "cost_7d", "op": "gte", "value": 30.0, "ref": "absolute"}
        ],
        "action_type": "pause",
        "action_magnitude": None,
        "cooldown_days": 7,
        "risk_level": "medium",
        "plain_english": "Pause Product when CTR (7d) < 0.5% and Cost >= £30"
    },
    {
        "name": "Increase Priority - High Volume Product",
        "rule_or_flag": "rule",
        "type": "priority",
        "conditions": [
            {"metric": "impressions_7d", "op": "gte", "value": 1000, "ref": "absolute"},
            {"metric": "ctr_7d", "op": "gt", "value": 0.015, "ref": "absolute"}
        ],
        "action_type": "increase_priority",
        "action_magnitude": 1.0,
        "cooldown_days": 7,
        "risk_level": "low",
        "plain_english": "Increase Priority by 1 level when Impressions >= 1000 and CTR > 1.5%"
    },
    {
        "name": "Decrease Priority - Low Engagement High Visibility",
        "rule_or_flag": "rule",
        "type": "priority",
        "conditions": [
            {"metric": "impressions_7d", "op": "gte", "value": 500, "ref": "absolute"},
            {"metric": "ctr_7d", "op": "lt", "value": 0.005, "ref": "absolute"}
        ],
        "action_type": "decrease_priority",
        "action_magnitude": 1.0,
        "cooldown_days": 7,
        "risk_level": "low",
        "plain_english": "Decrease Priority by 1 level when Impressions >= 500 and CTR < 0.5%"
    },
    # 6 Product Flags
    {
        "name": "Flag - High Cost Zero Conversions",
        "rule_or_flag": "flag",
        "type": "performance",
        "conditions": [
            {"metric": "cost_7d", "op": "gte", "value": 30.0, "ref": "absolute"},
            {"metric": "conversions_7d", "op": "eq", "value": 0, "ref": "absolute"}
        ],
        "action_type": None,
        "action_magnitude": None,
        "cooldown_days": 7,
        "risk_level": "low",
        "plain_english": "Flag when Cost (7d) >= £30 and Conversions = 0"
    },
    {
        "name": "Flag - Product ROAS Drop",
        "rule_or_flag": "flag",
        "type": "anomaly",
        "conditions": [
            {"metric": "roas_vs_prev_pct", "op": "lt", "value": -0.40, "ref": "week_over_week"}
        ],
        "action_type": None,
        "action_magnitude": None,
        "cooldown_days": 7,
        "risk_level": "low",
        "plain_english": "Flag when ROAS declined > 40% vs previous 7d"
    },
    {
        "name": "Flag - Product CTR Drop",
        "rule_or_flag": "flag",
        "type": "anomaly",
        "conditions": [
            {"metric": "ctr_vs_prev_pct", "op": "lt", "value": -0.30, "ref": "week_over_week"}
        ],
        "action_type": None,
        "action_magnitude": None,
        "cooldown_days": 7,
        "risk_level": "low",
        "plain_english": "Flag when CTR declined > 30% vs previous 7d"
    },
    {
        "name": "Flag - High Impression Share Loss",
        "rule_or_flag": "flag",
        "type": "performance",
        "conditions": [
            {"metric": "impression_share_lost_rank", "op": "gt", "value": 0.30, "ref": "absolute"}
        ],
        "action_type": None,
        "action_magnitude": None,
        "cooldown_days": 7,
        "risk_level": "low",
        "plain_english": "Flag when Impression Share Lost to Rank > 30%"
    },
    {
        "name": "Flag - Sudden Cost Spike",
        "rule_or_flag": "flag",
        "type": "anomaly",
        "conditions": [
            {"metric": "cost_vs_prev_pct", "op": "gt", "value": 0.50, "ref": "week_over_week"}
        ],
        "action_type": None,
        "action_magnitude": None,
        "cooldown_days": 7,
        "risk_level": "low",
        "plain_english": "Flag when Cost increased > 50% vs previous 7d"
    },
    {
        "name": "Flag - High CTR Opportunity",
        "rule_or_flag": "flag",
        "type": "performance",
        "conditions": [
            {"metric": "ctr_7d", "op": "gt", "value": 0.02, "ref": "absolute"},
            {"metric": "impressions_7d", "op": "gte", "value": 200, "ref": "absolute"}
        ],
        "action_type": None,
        "action_magnitude": None,
        "cooldown_days": 7,
        "risk_level": "low",
        "plain_english": "Flag when CTR (7d) > 2% and Impressions >= 200"
    }
]

print("=== CREATING 16 PRODUCT RULES/FLAGS ===\n")

created_ids = []
next_id = max_id + 1

for item in items:
    conn.execute("""
        INSERT INTO rules (
            id, client_config, entity_type, name, rule_or_flag, type,
            campaign_type_lock, entity_scope, conditions, action_type,
            action_magnitude, cooldown_days, risk_level, enabled,
            plain_english, is_template, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        next_id,
        'client_christopher_hoole',
        'shopping_product',
        item["name"],
        item["rule_or_flag"],
        item["type"],
        None,
        json.dumps({"scope": "all"}),
        json.dumps(item["conditions"]),
        item["action_type"],
        item["action_magnitude"],
        item["cooldown_days"],
        item["risk_level"],
        True,
        item["plain_english"],
        False,
        datetime.now(),
        datetime.now()
    ])
    
    created_ids.append(next_id)
    category = "Rule" if item["rule_or_flag"] == "rule" else "Flag"
    print(f"✅ Created {category}: {item['name']} (ID: {next_id})")
    next_id += 1

print(f"\n✅ SUCCESS: Created {len(created_ids)} product rules/flags")

# Verify
rules_count = conn.execute("""
    SELECT COUNT(*) FROM rules 
    WHERE entity_type='shopping_product' AND rule_or_flag='rule'
""").fetchone()[0]

flags_count = conn.execute("""
    SELECT COUNT(*) FROM rules 
    WHERE entity_type='shopping_product' AND rule_or_flag='flag'
""").fetchone()[0]

print(f"\n=== VERIFICATION ===")
print(f"Product Rules: {rules_count}")
print(f"Product Flags: {flags_count}")
print(f"Total: {rules_count + flags_count}")

conn.close()

print("\n✅ DONE - Restart Flask and check Shopping > Rules > Product Rules")
```

**Checkpoint:**
- Save script to `C:\Users\User\Desktop\gads-data-layer\scripts\create_product_rules_and_flags.py`
- Run in PowerShell: `python scripts/create_product_rules_and_flags.py`
- Output MUST show: "Created 10 rules + 6 flags"
- Verification MUST show: "Product Rules: 10, Product Flags: 6"
- **STOP if counts are wrong**
- **Report:** "Step 7 complete - 10 rules + 6 flags created"

---

### STEP 8: Update rules.css for Product Toast

**File:** `C:\Users\User\Desktop\gads-data-layer\act_dashboard\static\css\rules.css`

**Action:**
Find the toast wrapper rule (search for `toast-wrap`) and add `#product-rules-toast-wrap`:

```css
#campaign-rules-toast-wrap,
#ag-rules-toast-wrap,
#kw-rules-toast-wrap,
#ad-rules-toast-wrap,
#shopping-campaign-rules-toast-wrap,
#product-rules-toast-wrap {
    position: fixed;
    top: 80px;
    right: 20px;
    z-index: 9999;
}
```

**Checkpoint:**
- Save file
- Restart Flask
- No visual change expected
- Console should have zero errors
- **Report:** "Step 8 complete - toast CSS updated"

---

### STEP 9: Final Integration Test

**DO NOT skip this step. Run ALL tests below.**

**Test 1: Page Load**
- Navigate to http://localhost:5000/shopping
- Click "Rules (14)" tab
- Verify: Campaign Rules showing by default
- Verify: Toggle buttons visible
- **Screenshot 1:** Take screenshot

**Test 2: Toggle to Product Rules**
- Click "Product Rules" button
- Verify: View switches to Product Rules section
- Verify: Table shows 10 rules
- Verify: All columns populated
- Verify: Console has ZERO errors
- **Screenshot 2:** Take screenshot of Product Rules table

**Test 3: Console Verification**
- Open console (F12)
- Verify: Zero SyntaxError
- Verify: Zero 404 errors
- Verify: Zero undefined function errors
- **Screenshot 3:** Take screenshot of console (must show zero errors)

**Test 4: Toggle Rule**
- Click toggle switch on any product rule
- Verify: Switch changes state
- Verify: No page reload
- Flask log should show: `POST /shopping/product_rules/{id}/toggle - 200`

**Test 5: Create Rule**
- Click "Add rule or flag" button
- Verify: Modal opens
- Fill in test rule and save
- Verify: New rule appears in table
- Flask log should show: `POST /shopping/product_rules - 200`

**Test 6: Edit Rule**
- Click Actions (⋮) dropdown on any rule
- Click "Edit"
- Verify: Modal opens with pre-populated fields
- Change something and save
- Verify: Changes reflected in table
- Flask log should show: `PUT /shopping/product_rules/{id} - 200`

**Test 7: Save as Template**
- Click Actions (⋮) dropdown on any rule
- Click "Save as template"
- Verify: Confirmation dialog appears
- Confirm
- Verify: Templates section increments count
- Flask log should show: `POST /shopping/product_rules/{id}/save-as-template - 200`

**Test 8: Delete Rule**
- Click Actions (⋮) dropdown on your test rule
- Click "Delete"
- Verify: Confirmation dialog
- Confirm
- Verify: Rule removed from table
- Flask log should show: `DELETE /shopping/product_rules/{id} - 200`

**Test 9: Toggle Back to Campaign**
- Click "Campaign Rules" button
- Verify: Switches back to Campaign Rules
- Verify: 14 campaign rules showing
- Verify: Console still has zero errors

**Test 10: Database Verification**
Run in PowerShell:
```powershell
python -c "import duckdb; conn = duckdb.connect('warehouse.duckdb'); print(f\"Product rules: {conn.execute('SELECT COUNT(*) FROM rules WHERE entity_type=\\'shopping_product\\' AND rule_or_flag=\\'rule\\'').fetchone()[0]}\"); print(f\"Product flags: {conn.execute('SELECT COUNT(*) FROM rules WHERE entity_type=\\'shopping_product\\' AND rule_or_flag=\\'flag\\'').fetchone()[0]}\"); conn.close()"
```
Expected: `Product rules: 10, Product flags: 6` (may be 11/7 after test rule creation)

---

## SUCCESS CRITERIA - ALL MUST PASS

**Visual:**
- ✅ Toggle buttons visible
- ✅ Campaign Rules is default view
- ✅ Product Rules button switches correctly
- ✅ 10 product rules in table
- ✅ All columns populated
- ✅ Templates section visible

**Console:**
- ✅ Zero SyntaxError
- ✅ Zero 404 errors
- ✅ All 6 routes return 200 OK

**Functional (All 8 tests above):**
- ✅ Toggle works
- ✅ Create works
- ✅ Edit works
- ✅ Toggle rule works
- ✅ Save template works
- ✅ Delete works
- ✅ Switch back to campaign works
- ✅ Database counts correct

**Flask Log:**
- ✅ 6 CSRF exemptions shown on startup
- ✅ All routes returning 200 OK

**Proof Required:**
- Screenshot 1: Product Rules table
- Screenshot 2: Console showing zero errors
- Screenshot 3: Flask log showing 200 responses
- Confirmation: All 10 tests passed

---

## CRITICAL PITFALLS

1. **Entity type must be 'shopping_product'** - not 'product' or 'shopping'
2. **WoW flags won't fire on synthetic data** - columns are 0.0, this is expected
3. **Priority field must exist** - verify in Step 0 pre-flight check
4. **Cost as pounds not micros** - product costs are stored as pounds
5. **Apostrophes in strings** - must escape or use double quotes
6. **Functions must be on window** - or onclick won't work

---

## DELIVERABLES

**Files Created:**
1. `product_rules_flow_builder.html`
2. `create_product_rules_and_flags.py`

**Files Modified:**
1. `shopping_new.html` - toggle buttons, product section, JavaScript
2. `shopping.py` - 6 product routes
3. `__init__.py` - 6 CSRF exemptions
4. `rules.css` - product toast wrapper

**Database:**
- 10 Product Rules inserted
- 6 Product Flags inserted

---

**END OF BRIEF V2**
