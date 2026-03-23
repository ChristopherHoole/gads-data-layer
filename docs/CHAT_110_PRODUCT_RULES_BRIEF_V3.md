# CHAT 110: SHOPPING PRODUCT RULES & FLAGS

**Date:** 2026-03-22
**Estimated Time:** 4-6 hours
**Priority:** HIGH
**Dependencies:** Phase 1 complete (Christopher Hoole Shopping data in product_features_daily)

---

## CONTEXT

Chats 107-109 built Rules & Flags for Ad Groups, Keywords, and Ads. Shopping has 14 campaign-level rules but NO product-level rules. Christopher Hoole now has 100 products with 90 days of performance data in product_features_daily. Product rules enable feed quality monitoring, performance optimization, lifecycle management, and stock control at the individual product level.

**Important:** product_features_daily has WoW comparison columns (cpa_w7_vs_prev_pct, roas_w7_vs_prev_pct, etc.) set to 0.0 due to DuckDB nested window function limitation. Do NOT use these columns in seed rules — use absolute thresholds only.

---

## OBJECTIVE

Build complete Product Rules & Flags system with flow builder UI, CRUD routes, seed data (18 total: 10 rules + 8 flags), and engine integration for entity_type='product'.

---

## DELIVERABLES

1. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\components\product_rules_flow_builder.html` — CREATE
2. `C:\Users\User\Desktop\gads-data-layer\scripts\seed_product_rules.py` — CREATE (18 total: 10 rules + 8 flags)
3. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\shopping.py` — MODIFY (add 7 CRUD routes after existing campaign routes)
4. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\shopping_new.html` — MODIFY (add toggle buttons inside Rules tab)
5. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\app.py` — MODIFY (add 7 CSRF exemptions)
6. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\static\css\rules.css` — MODIFY (add #product-rules-toast-wrap)
7. `C:\Users\User\Desktop\gads-data-layer\act_autopilot\recommendations_engine.py` — MODIFY (add PRODUCT_METRIC_MAP + product entity block)
8. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_110_HANDOFF.md` — CREATE
9. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_110_SUMMARY.md` — CREATE

---

## REQUIREMENTS

### UI Integration (shopping_new.html)

**Location:** Inside existing Rules tab (after line ~80 where shopping_rules_tab.html is included)

**Add toggle buttons:**
```html
<!-- Toggle between Campaign and Product rules -->
<div class="mb-3">
  <div class="btn-group" role="group">
    <button type="button" class="btn btn-sm btn-outline-primary active" id="campaign-rules-toggle">
      Campaign Rules (14)
    </button>
    <button type="button" class="btn btn-sm btn-outline-primary" id="product-rules-toggle">
      Product Rules (<span id="product-rules-count">0</span>)
    </button>
  </div>
</div>

<!-- Campaign rules section (existing) -->
<div id="campaign-rules-section">
  {% include 'components/shopping_rules_tab.html' %}
</div>

<!-- Product rules section (NEW) -->
<div id="product-rules-section" style="display:none;">
  {% include 'components/product_rules_flow_builder.html' %}
</div>
```

**JavaScript (add to shopping_new.html bottom):**
```javascript
document.getElementById('campaign-rules-toggle').addEventListener('click', function() {
  document.getElementById('campaign-rules-section').style.display = 'block';
  document.getElementById('product-rules-section').style.display = 'none';
  this.classList.add('active');
  document.getElementById('product-rules-toggle').classList.remove('active');
});

document.getElementById('product-rules-toggle').addEventListener('click', function() {
  document.getElementById('campaign-rules-section').style.display = 'none';
  document.getElementById('product-rules-section').style.display = 'block';
  this.classList.add('active');
  document.getElementById('campaign-rules-toggle').classList.remove('active');
  loadProductRules(); // Lazy load
});
```

### Scope Picker (Two-Step)

**Step 1: Campaigns (required)**
Reuse existing campaign dropdown from shopping_rules_tab.html pattern.

**Step 2: Product Filters (optional)**
Add 3 dropdowns populated by `/api/products-list`:
- Brand dropdown (distinct product_brand values)
- Category dropdown (distinct product_category values)
- Type dropdown (distinct product_type_l1 values)

**Scope JSON examples:**
```json
{"scope": "all"}
{"scope": {"campaigns": ["1001", "1002"]}}
{"scope": {"campaigns": ["1001"], "brand": "EcoWare"}}
{"scope": {"campaigns": ["1001"], "brand": "EcoWare", "category": "Kitchen"}}
```

### Routes to Add (shopping.py)

Add these 7 routes AFTER existing campaign rules routes (~line 400):

```python
@shopping_bp.route('/shopping/product_list_rules', methods=['GET'])
def product_list_rules():
    # Returns: {"rules": [...], "templates": [...]}
    # WHERE entity_type='product' AND (is_template=FALSE for rules, is_template=TRUE for templates)
    
@shopping_bp.route('/shopping/product_create_rule', methods=['POST'])
def product_create_rule():
    # Expects: name, type, action_type, conditions (JSON), scope (JSON), enabled, is_template, etc.
    # Sets: entity_type='product', rule_or_flag based on action_type
    # Returns: {"success": true, "rule": {...}}
    
@shopping_bp.route('/shopping/product_update_rule', methods=['POST'])
def product_update_rule():
    # Expects: id + fields to update
    # WHERE id=? AND entity_type='product'
    # Returns: {"success": true}
    
@shopping_bp.route('/shopping/product_delete_rule', methods=['POST'])
def product_delete_rule():
    # Expects: id
    # WHERE id=? AND entity_type='product'
    # Returns: {"success": true}
    
@shopping_bp.route('/shopping/product_toggle_rule', methods=['POST'])
def product_toggle_rule():
    # Expects: id, enabled (boolean)
    # WHERE id=? AND entity_type='product'
    # Returns: {"success": true}
    
@shopping_bp.route('/shopping/product_save_as_template', methods=['POST'])
def product_save_as_template():
    # Expects: id
    # Copies rule with is_template=TRUE, name="[Template] " + original_name
    # Returns: {"success": true, "template_id": new_id}
    
@shopping_bp.route('/api/products-list', methods=['GET'])
def api_products_list():
    # Query product_features_daily for distinct brand/category/type values
    # Returns: {"brands": [...], "categories": [...], "types": [...]}
```

### CSRF Exemptions (app.py)

Add after existing shopping exemptions (~line 85):
```python
csrf.exempt(shopping_bp.route('/shopping/product_list_rules'))
csrf.exempt(shopping_bp.route('/shopping/product_create_rule'))
csrf.exempt(shopping_bp.route('/shopping/product_update_rule'))
csrf.exempt(shopping_bp.route('/shopping/product_delete_rule'))
csrf.exempt(shopping_bp.route('/shopping/product_toggle_rule'))
csrf.exempt(shopping_bp.route('/shopping/product_save_as_template'))
csrf.exempt(shopping_bp.route('/api/products-list'))
```

### PRODUCT_METRIC_MAP (recommendations_engine.py)

Add after existing SHOPPING_METRIC_MAP (~line 420):

```python
PRODUCT_METRIC_MAP = {
    # Performance ratios (w7/w14/w30/w90)
    "roas_w7": ("roas_w7", None, None, None),
    "roas_w14": ("roas_w14", None, None, None),
    "roas_w30": ("roas_w30", None, None, None),
    "roas_w90": ("roas_w90", None, None, None),
    
    "cpa_w7": ("cpa_w7", None, None, 1_000_000),  # Micros to £
    "cpa_w14": ("cpa_w14", None, None, 1_000_000),
    "cpa_w30": ("cpa_w30", None, None, 1_000_000),
    "cpa_w90": ("cpa_w90", None, None, 1_000_000),
    
    "ctr_w7": ("ctr_w7", None, None, None),
    "ctr_w14": ("ctr_w14", None, None, None),
    "ctr_w30": ("ctr_w30", None, None, None),
    "ctr_w90": ("ctr_w90", None, None, None),
    
    "cvr_w7": ("cvr_w7", None, None, None),
    "cvr_w14": ("cvr_w14", None, None, None),
    "cvr_w30": ("cvr_w30", None, None, None),
    "cvr_w90": ("cvr_w90", None, None, None),
    
    "cpc_w7": ("cpc_w7", None, None, 1_000_000),
    "cpc_w14": ("cpc_w14", None, None, 1_000_000),
    "cpc_w30": ("cpc_w30", None, None, 1_000_000),
    "cpc_w90": ("cpc_w90", None, None, 1_000_000),
    
    # Sums (w7/w14/w30/w90)
    "clicks_w7_sum": ("clicks_w7_sum", None, None, None),
    "clicks_w14_sum": ("clicks_w14_sum", None, None, None),
    "clicks_w30_sum": ("clicks_w30_sum", None, None, None),
    "clicks_w90_sum": ("clicks_w90_sum", None, None, None),
    
    "cost_micros_w7_sum": ("cost_micros_w7_sum", None, None, 1_000_000),
    "cost_micros_w14_sum": ("cost_micros_w14_sum", None, None, 1_000_000),
    "cost_micros_w30_sum": ("cost_micros_w30_sum", None, None, 1_000_000),
    "cost_micros_w90_sum": ("cost_micros_w90_sum", None, None, 1_000_000),
    
    "conversions_w7_sum": ("conversions_w7_sum", None, None, None),
    "conversions_w14_sum": ("conversions_w14_sum", None, None, None),
    "conversions_w30_sum": ("conversions_w30_sum", None, None, None),
    "conversions_w90_sum": ("conversions_w90_sum", None, None, None),
    
    "conversions_value_w7_sum": ("conversions_value_w7_sum", None, None, 1_000_000),
    "conversions_value_w14_sum": ("conversions_value_w14_sum", None, None, 1_000_000),
    "conversions_value_w30_sum": ("conversions_value_w30_sum", None, None, 1_000_000),
    "conversions_value_w90_sum": ("conversions_value_w90_sum", None, None, 1_000_000),
    
    # Feed quality flags
    "stock_out_flag": ("stock_out_flag", None, None, None),
    "has_price_mismatch": ("has_price_mismatch", None, None, None),
    "has_disapproval": ("has_disapproval", None, None, None),
    "feed_quality_score": ("feed_quality_score", None, None, None),
    "stock_out_days_w30": ("stock_out_days_w30", None, None, None),
    
    # Lifecycle flags
    "new_product_flag": ("new_product_flag", None, None, None),
    "days_live": ("days_live", None, None, None),
    "low_data_flag": ("low_data_flag", None, None, None),
    
    # Product attributes (for scope filtering)
    "product_brand": ("product_brand", None, None, None),
    "product_category": ("product_category", None, None, None),
    "product_type_l1": ("product_type_l1", None, None, None),
    "availability": ("availability", None, None, None),
}
```

**Engine query block** (add after shopping campaign block ~line 680):
```python
elif entity_type == 'product':
    metric_map = PRODUCT_METRIC_MAP
    query = """
        SELECT 
            product_id,
            product_title,
            offer_id,
            {columns}
        FROM ro.analytics.product_features_daily
        WHERE customer_id = ?
          AND snapshot_date = (
              SELECT MAX(snapshot_date) 
              FROM ro.analytics.product_features_daily 
              WHERE customer_id = ? 
                AND product_title IS NOT NULL
          )
    """
    params = [customer_id, customer_id]
```

### Seed Script (18 total: 10 rules + 8 flags)

**Feed Quality (1 rule + 3 flags = 4 total):**
1. Name: "Pause: Out of Stock 7+ Days"
   - action_type: "pause"
   - rule_or_flag: "rule"
   - conditions: [{"metric": "stock_out_days_w30", "op": "gte", "value": 7, "ref": null}]
   - cooldown_days: 14, monitoring_days: 7

2. Name: "Flag: Price Mismatch Detected"
   - action_type: "flag"
   - rule_or_flag: "flag"
   - conditions: [{"metric": "has_price_mismatch", "op": "eq", "value": true, "ref": null}]
   - cooldown_days: 7, monitoring_days: 0

3. Name: "Flag: Product Disapproval"
   - action_type: "flag"
   - rule_or_flag: "flag"
   - conditions: [{"metric": "has_disapproval", "op": "eq", "value": true, "ref": null}]
   - cooldown_days: 7, monitoring_days: 0

4. Name: "Flag: Low Feed Quality Score"
   - action_type: "flag"
   - rule_or_flag: "flag"
   - conditions: [{"metric": "feed_quality_score", "op": "lt", "value": 0.5, "ref": null}]
   - cooldown_days: 7, monitoring_days: 0

**Performance (6 rules + 0 flags = 6 total):**
5. Name: "Pause: Low ROAS (7d)"
   - action_type: "pause"
   - rule_or_flag: "rule"
   - conditions: [{"metric": "roas_w7", "op": "lt", "value": 2.0, "ref": null}]
   - cooldown_days: 14, monitoring_days: 7

6. Name: "Pause: High CPA (7d)"
   - action_type: "pause"
   - rule_or_flag: "rule"
   - conditions: [{"metric": "cpa_w7", "op": "gt", "value": 50.0, "ref": null}]
   - cooldown_days: 14, monitoring_days: 7

7. Name: "Pause: Low CTR (7d)"
   - action_type: "pause"
   - rule_or_flag: "rule"
   - conditions: [{"metric": "ctr_w7", "op": "lt", "value": 0.01, "ref": null}]
   - cooldown_days: 14, monitoring_days: 7

8. Name: "Enable: Good ROAS When Paused"
   - action_type: "enable"
   - rule_or_flag: "rule"
   - conditions: [
       {"metric": "roas_w7", "op": "gt", "value": 3.0, "ref": null},
       {"metric": "status", "op": "eq", "value": "PAUSED", "ref": null}
     ]
   - cooldown_days: 14, monitoring_days: 7

9. Name: "Increase Bid: High ROAS (7d)"
   - action_type: "increase_bid"
   - rule_or_flag: "rule"
   - conditions: [{"metric": "roas_w7", "op": "gt", "value": 5.0, "ref": null}]
   - change_magnitude: 0.15 (15%)
   - cooldown_days: 14, monitoring_days: 7

10. Name: "Decrease Bid: High CPA (7d)"
    - action_type: "decrease_bid"
    - rule_or_flag: "rule"
    - conditions: [{"metric": "cpa_w7", "op": "gt", "value": 40.0, "ref": null}]
    - change_magnitude: -0.10 (10%)
    - cooldown_days: 14, monitoring_days: 7

**Lifecycle (1 rule + 3 flags = 4 total):**
11. Name: "Flag: New Product Low Conversions"
    - action_type: "flag"
    - rule_or_flag: "flag"
    - conditions: [
        {"metric": "new_product_flag", "op": "eq", "value": true, "ref": null},
        {"metric": "conversions_w7_sum", "op": "lt", "value": 2, "ref": null}
      ]
    - cooldown_days: 7, monitoring_days: 0

12. Name: "Flag: Mature Product Declining ROAS"
    - action_type: "flag"
    - rule_or_flag: "flag"
    - conditions: [
        {"metric": "days_live", "op": "gt", "value": 30, "ref": null},
        {"metric": "roas_w7", "op": "lt", "value": 3.0, "ref": null}
      ]
    - cooldown_days: 7, monitoring_days: 0

13. Name: "Flag: Low Data High Spend"
    - action_type: "flag"
    - rule_or_flag: "flag"
    - conditions: [
        {"metric": "low_data_flag", "op": "eq", "value": true, "ref": null},
        {"metric": "cost_micros_w7_sum", "op": "gt", "value": 100000000, "ref": null}
      ]
    - cooldown_days: 7, monitoring_days: 0

14. Name: "Pause: New Product High Spend No Conversions"
    - action_type: "pause"
    - rule_or_flag: "rule"
    - conditions: [
        {"metric": "new_product_flag", "op": "eq", "value": true, "ref": null},
        {"metric": "cost_micros_w7_sum", "op": "gt", "value": 50000000, "ref": null},
        {"metric": "conversions_w7_sum", "op": "eq", "value": 0, "ref": null}
      ]
    - cooldown_days: 14, monitoring_days: 7

**Stock Management (2 rules + 2 flags = 4 total):**
15. Name: "Flag: Going Out of Stock"
    - action_type: "flag"
    - rule_or_flag: "flag"
    - conditions: [
        {"metric": "stock_out_days_w30", "op": "gt", "value": 3, "ref": null},
        {"metric": "stock_out_days_w30", "op": "lt", "value": 7, "ref": null}
      ]
    - cooldown_days: 7, monitoring_days: 0

16. Name: "Pause: Out of Stock Still Spending"
    - action_type: "pause"
    - rule_or_flag: "rule"
    - conditions: [
        {"metric": "stock_out_flag", "op": "eq", "value": true, "ref": null},
        {"metric": "cost_micros_w7_sum", "op": "gt", "value": 10000000, "ref": null}
      ]
    - cooldown_days: 14, monitoring_days: 7

17. Name: "Flag: Preorder No Conversions"
    - action_type: "flag"
    - rule_or_flag: "flag"
    - conditions: [
        {"metric": "availability", "op": "eq", "value": "PREORDER", "ref": null},
        {"metric": "conversions_w14_sum", "op": "eq", "value": 0, "ref": null}
      ]
    - cooldown_days: 7, monitoring_days: 0

18. Name: "Pause: High Cost Out of Stock"
    - action_type: "pause"
    - rule_or_flag: "rule"
    - conditions: [
        {"metric": "stock_out_flag", "op": "eq", "value": true, "ref": null},
        {"metric": "cost_micros_w14_sum", "op": "gt", "value": 100000000, "ref": null}
      ]
    - cooldown_days: 14, monitoring_days: 7

### Technical Constraints

- **ALWAYS filter:** WHERE entity_type='product' on ALL product rules queries
- **Modal:** style="display:none;" by default in product_rules_flow_builder.html
- **Toast CSS:** Add `#product-rules-toast-wrap` to combined toast rule in rules.css (line ~45)
- **Auto-risk guard:** Add `if (_productRfbEditId) return;` at top of auto-risk calculation function
- **Operators:** Use "gt", "lt", "gte", "lte", "eq", "is_not_null" (NOT symbols like > or <)
- **Boolean conditions:** stock_out_flag = true uses operator "eq" with value true (not "is_not_null")
- **Cost values:** Always in micros (50000000 = £50)
- **Condition ref:** Always null for product rules (no WoW % comparisons due to DuckDB limitation)

---

## SUCCESS CRITERIA

- [ ] Toggle button switches between Campaign Rules (14) and Product Rules (18)
- [ ] Create product rule via flow builder → saves with entity_type='product'
- [ ] Edit product rule → loads correctly, saves changes
- [ ] Delete product rule → removes from DB
- [ ] Toggle product rule enabled → updates status
- [ ] Save as template → creates template copy
- [ ] Scope picker: campaigns dropdown + brand/category/type filters all work
- [ ] `python scripts/seed_product_rules.py` → creates exactly 18 rows
- [ ] DB verification: `SELECT COUNT(*) FROM rules WHERE entity_type='product' AND is_template=FALSE` returns 18
- [ ] Flask starts cleanly with no SQL errors in terminal
- [ ] No JavaScript console errors in browser

ALL must pass before reporting complete.

---

## REFERENCE FILES

**Flow Builder Pattern:**
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\components\ads_rules_flow_builder.html` — Most recent pattern (Chat 109)
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\components\shopping_rules_tab.html` — Existing campaign rules UI for Shopping

**CRUD Routes Pattern:**
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\ads.py` — Most recent routes (Chat 109)
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\shopping.py` — Existing shopping routes

**Seed Script Pattern:**
- `C:\Users\User\Desktop\gads-data-layer\scripts\seed_ad_rules.py` — Most recent seed (Chat 109)

**Engine Pattern:**
- `C:\Users\User\Desktop\gads-data-layer\act_autopilot\recommendations_engine.py` — Shows CAMPAIGN_METRIC_MAP structure and entity_type blocks

---

## TESTING

**Phase 1: UI Testing**
1. Start Flask, navigate to Shopping page
2. Click Rules tab
3. Click "Product Rules" toggle → section switches, campaign rules hide
4. Click "Create rule" → product flow builder modal opens
5. Create simple rule: ROAS w7 < 2.0 → pause
6. Save → check Flask terminal for INSERT log
7. Rule appears in Active tab
8. Toggle enabled OFF → status updates
9. Toggle enabled ON → status updates
10. Edit rule → modal loads with correct data, save changes → updates
11. Delete rule → removes from table
12. Save as template → creates template in Templates tab

**Phase 2: Seed Script**
1. Run: `python scripts/seed_product_rules.py`
2. Expected output: "Created 18 product rules/flags (10 rules, 8 flags)"
3. Refresh page → all 18 rules visible in table

**Phase 3: Database Verification**
```python
import duckdb
conn = duckdb.connect('warehouse.duckdb')

# Count rules
rules = conn.execute("""
    SELECT COUNT(*) 
    FROM rules 
    WHERE entity_type='product' 
      AND is_template=FALSE 
      AND rule_or_flag='rule'
""").fetchone()[0]

# Count flags
flags = conn.execute("""
    SELECT COUNT(*) 
    FROM rules 
    WHERE entity_type='product' 
      AND is_template=FALSE 
      AND rule_or_flag='flag'
""").fetchone()[0]

print(f"Rules: {rules}, Flags: {flags}, Total: {rules + flags}")
# Expected: Rules: 10, Flags: 8, Total: 18
```

**Phase 4: Flask Health**
- No SQL errors in terminal
- No JavaScript console errors
- All 7 product routes responding with 200 status

Report exact Flask log output for any SQL operations.

---

**Brief Version:** 3.0 (Final)
**Lines:** 481
