# Chat 17: Architectural Analysis - Dual Recommendation Systems

**Date:** 2026-02-17  
**Status:** COMPLETED - Root cause identified

---

## EXECUTIVE SUMMARY

**Problem:** Dashboard has TWO different ways of generating recommendations:
1. ✅ **Proper:** Rules engine (keywords, ads)
2. ❌ **Broken:** Hardcoded dicts (shopping)

**Impact:** Shopping page generates recommendations with missing fields, causing execution failures.

**Root Cause:** Shopping rules file doesn't exist. Routes.py falls back to hardcoded dict creation.

---

## CURRENT RECOMMENDATION FLOW

### 1. KEYWORDS PAGE (✅ PROPER PATTERN)

**File:** `routes.py` lines 1017-1147

**Flow:**
```
1. Import rule functions from keyword_rules.py
   Line 1017: from act_autopilot.rules.keyword_rules import KEYWORD_RULES, SEARCH_TERM_RULES

2. Create RuleContext for each keyword
   Lines 1077-1091: Build context with features, config, etc.

3. Call each rule function
   Lines 1092-1098: for rule_fn in SEARCH_TERM_RULES: rec = rule_fn(ctx)

4. Collect Recommendation objects
   Line 1096: kw_recs.append(rec)

5. Convert to dicts for cache (with 'id' field)
   Lines 1116-1143: Manual dict mapping from Recommendation fields

6. Store in cache
   Line 1147: current_app.config['RECOMMENDATIONS_CACHE']['keywords'] = keywords_cache

7. Template displays from cache
```

**Recommendation Object Fields:**
```python
{
    'id': idx,                              # Added for frontend
    'rule_id': rec.rule_id,                 # From Recommendation
    'rule_name': rec.rule_name,             # From Recommendation
    'entity_type': rec.entity_type,         # From Recommendation
    'entity_id': rec.entity_id,             # From Recommendation
    'action_type': mapped_action_type,      # Mapped from rec.action_type
    'risk_tier': rec.risk_tier,             # From Recommendation
    'confidence': rec.confidence or 0.0,    # From Recommendation
    'current_value': rec.current_value,     # From Recommendation
    'recommended_value': rec.recommended_value, # From Recommendation
    'change_pct': rec.change_pct,           # From Recommendation
    'rationale': rec.rationale or '',       # From Recommendation
    'campaign_name': rec.campaign_name or '', # From Recommendation
    'blocked': rec.blocked or False,        # From Recommendation
    'block_reason': rec.block_reason or '', # From Recommendation
    'priority': rec.priority if rec.priority is not None else 50, # From Recommendation
    'constitution_refs': rec.constitution_refs or [], # From Recommendation
    'guardrails_checked': rec.guardrails_checked or [], # From Recommendation
    'evidence': rec.evidence if rec.evidence else {}, # From Recommendation ✅ CRITICAL
    'triggering_diagnosis': rec.triggering_diagnosis or '', # From Recommendation
    'triggering_confidence': rec.triggering_confidence or 0.0, # From Recommendation
    'expected_impact': rec.expected_impact or '', # From Recommendation
}
```

---

### 2. ADS PAGE (✅ PROPER PATTERN)

**File:** `routes.py` lines 1200-1350 (similar to keywords)

**Flow:**
```
1. Import rule functions from ad_rules.py
2. Create RuleContext for each ad
3. Call each rule function
4. Collect Recommendation objects
5. Convert to dicts for cache (with 'id' field)
6. Store in cache
7. Template displays from cache
```

**Same dict structure as keywords** - Full Recommendation fields present

---

### 3. SHOPPING PAGE (❌ BROKEN PATTERN)

**File:** `routes.py` lines 1569-1642

**Flow:**
```
1. TRY to import shopping_rules (Line 1574)
   from act_autopilot.rules import shopping_rules
   
2. FAIL because shopping_rules.py doesn't exist
   
3. FALLBACK to hardcoded dict creation (Lines 1593-1631)
   - Manually query products_df
   - Manually filter high ROAS products
   - Manually loop and create dicts
   - NO Recommendation objects created
   - NO rule functions called

4. Create hardcoded dicts directly (Lines 1601-1631)
   recommendations_list.append({
       "rule_id": "SHOP-BID-001",
       "rule_name": "High ROAS Product Bid Increase",
       "entity_type": "product",
       "entity_id": row['product_id'],
       "action_type": "update_product_bid",
       # ... hardcoded fields
       "evidence": {
           "product_id": row['product_id'],
           "product_title": row['product_title'],
           "roas_w30": float(row['roas_w30']),
           "clicks_w30": int(row['clicks_w30_sum']),
           "conversions_w30": int(row['conversions_w30_sum']),
           "cost_w30": float(row['cost_micros_w30_sum']) / 1_000_000,
           "avg_cpc_dollars": current_bid_dollars,
           # ❌ MISSING: "ad_group_id" ← CRITICAL
       },
   })

5. Add 'id' field (Lines 1637-1638)
   for i, rec in enumerate(recommendations_list):
       rec['id'] = i

6. Store in cache (Line 1642)
   current_app.config['RECOMMENDATIONS_CACHE']['shopping'] = recommendations_list
```

**Hardcoded Dict Fields:**
```python
{
    'id': i,                                # Added after creation
    'rule_id': "SHOP-BID-001",              # Hardcoded string
    'rule_name': "High ROAS Product Bid Increase", # Hardcoded string
    'entity_type': "product",               # Hardcoded string
    'entity_id': row['product_id'],         # From database
    'action_type': "update_product_bid",    # Hardcoded string
    'risk_tier': "low",                     # Hardcoded string
    'confidence': 0.85,                     # Hardcoded float
    'current_value': current_bid_dollars,   # Calculated
    'recommended_value': recommended_bid_dollars, # Calculated
    'change_pct': 0.15,                     # Hardcoded float
    'rationale': f"High ROAS ({row['roas_w30']:.2f})...", # Formatted string
    'campaign_name': None,                  # Hardcoded None
    'blocked': False,                       # Hardcoded bool
    'block_reason': None,                   # Hardcoded None
    'priority': 50,                         # Hardcoded int
    'constitution_refs': [],                # Empty list
    'guardrails_checked': [],               # Empty list
    'evidence': {
        "product_id": row['product_id'],    # ✅ Present
        "product_title": row['product_title'], # ✅ Present
        "roas_w30": float(row['roas_w30']), # ✅ Present
        "clicks_w30": int(row['clicks_w30_sum']), # ✅ Present
        "conversions_w30": int(row['conversions_w30_sum']), # ✅ Present
        "cost_w30": float(row['cost_micros_w30_sum']) / 1_000_000, # ✅ Present
        "avg_cpc_dollars": current_bid_dollars, # ✅ Present
        # ❌ MISSING: "ad_group_id" ← EXECUTOR REQUIRES THIS
    },
    'triggering_diagnosis': "HIGH_ROAS_PRODUCT", # Hardcoded string
    'triggering_confidence': 0.85,          # Hardcoded float
    'expected_impact': f"Increase visibility...", # Formatted string
}
```

---

## EXECUTOR REQUIREMENTS

### Shopping Bid Executor (`_execute_shopping_bid`)

**File:** `executor.py` lines 1005-1059

**Required Fields:**

```python
def _execute_shopping_bid(self, rec: Recommendation, dry_run: bool) -> ExecutionResult:
    # Line 1019: Extract ad_group_id from evidence
    ad_group_id = rec.evidence.get("ad_group_id")  # ❌ NOT IN HARDCODED DICT
    
    # Line 1020: Extract partition_id from entity_id
    partition_id = rec.entity_id  # ✅ Present
    
    # Line 1021: Calculate bid from recommended_value
    new_bid_micros = int((rec.recommended_value or 0) * 1_000_000)  # ✅ Present
    
    # Line 1023: Validation check
    if not all([ad_group_id, partition_id, new_bid_micros]):
        return ExecutionResult(
            success=False,
            message="Missing required parameters",  # ← FAILS HERE
            error="Missing required parameters",
        )
```

**Validation Requirements:**

```python
def _validate_shopping_action(self, rec: Recommendation, action: str) -> Dict:
    # Line 1145: Needs product_id from entity_id OR evidence
    product_id = rec.entity_id or rec.evidence.get("product_id")  # ✅ Present
    
    # Line 1166: Checks out_of_stock flag
    is_out_of_stock = rec.evidence.get("out_of_stock", False)  # ⚠️  Not provided (defaults False)
    
    # Line 1174: Checks feed_quality_issue flag
    feed_quality_issue = rec.evidence.get("feed_quality_issue", False)  # ⚠️  Not provided (defaults False)
```

---

## FIELD COMPARISON TABLE

| Field                  | Executor Needs | Keywords Has | Ads Has | Shopping Has | Missing? |
|------------------------|----------------|--------------|---------|--------------|----------|
| **entity_id**          | ✅ Yes         | ✅ Yes       | ✅ Yes  | ✅ Yes       | ✅ OK    |
| **recommended_value**  | ✅ Yes         | ✅ Yes       | ✅ Yes  | ✅ Yes       | ✅ OK    |
| **evidence dict**      | ✅ Yes         | ✅ Yes       | ✅ Yes  | ✅ Yes       | ✅ OK    |
| **evidence.ad_group_id** | ✅ **CRITICAL** | N/A          | N/A     | ❌ **NO**    | ❌ **MISSING** |
| **evidence.product_id** | ⚠️  Optional   | N/A          | N/A     | ✅ Yes       | ✅ OK    |
| **evidence.out_of_stock** | ⚠️  Optional | N/A          | N/A     | ❌ No (defaults False) | ⚠️  Not provided |
| **evidence.feed_quality_issue** | ⚠️  Optional | N/A | N/A | ❌ No (defaults False) | ⚠️  Not provided |

---

## ROOT CAUSE ANALYSIS

### PRIMARY PROBLEM: Missing `ad_group_id`

**Where Used:**
- `executor.py` line 1019: `ad_group_id = rec.evidence.get("ad_group_id")`
- `executor.py` line 1034: `ad_group_id=str(ad_group_id)` passed to API

**Why Missing:**
- Shopping recommendations are hardcoded in `routes.py`
- Hardcoded dict only includes product-level data
- No ad_group_id in `product_features_daily` table
- No rule logic to fetch ad_group_id from related tables

**Impact:**
- Line 1023 validation fails: `if not all([ad_group_id, partition_id, new_bid_micros])`
- Returns: `ExecutionResult(success=False, message="Missing required parameters")`
- Red error toast in dashboard

### SECONDARY PROBLEM: Missing shopping_rules.py

**Expected Location:**
- `act_autopilot/rules/shopping_rules.py`

**Current State:**
- File does not exist
- Import attempt fails silently (line 1574 in try/except)
- Routes.py falls back to hardcoded logic

**Missing Components:**
- No `apply_rules()` function
- No individual rule functions (e.g., `shop_bid_001_high_roas`)
- No Recommendation object creation
- No proper evidence dict structure

---

## IDENTIFIED PROBLEMS

### 1. **Architectural Inconsistency**
- Keywords: Rules → Recommendation → Dict
- Ads: Rules → Recommendation → Dict
- Shopping: **NO RULES** → Hardcoded Dict (wrong pattern)

### 2. **Missing File**
- `act_autopilot/rules/shopping_rules.py` does not exist
- No rule-based recommendation generation for shopping

### 3. **Incomplete Evidence Dictionary**
- Shopping evidence missing `ad_group_id`
- Shopping evidence missing optional flags (`out_of_stock`, `feed_quality_issue`)
- Cannot execute because validation fails

### 4. **Data Source Limitation**
- `product_features_daily` table lacks `ad_group_id`
- Would need JOIN to `raw_shopping_product_partitions` or similar table
- Hardcoded approach cannot access related data

### 5. **No Error Visibility**
- Try/except swallows import error (line 1632-1634)
- User sees empty recommendations, no error message
- Silent failure mode

---

## PROPOSED SOLUTION

### Fix 1: Create `shopping_rules.py`

**File:** `act_autopilot/rules/shopping_rules.py`

**Structure:**
```python
"""
Shopping product bid optimization rules.
"""

from typing import List, Dict, Optional
from ..models import Recommendation

def apply_rules(product_features: List[Dict], ctx) -> List[Recommendation]:
    """Apply shopping rules to product features."""
    recommendations = []
    for product in product_features:
        # Rule: High ROAS Product Bid Increase
        rec = _apply_shop_bid_001(product, ctx)
        if rec:
            recommendations.append(rec)
    return recommendations

def _apply_shop_bid_001(product: Dict, ctx) -> Optional[Recommendation]:
    """Rule: Increase bid on high-ROAS products."""
    # Calculate bid from avg CPC
    # Build Recommendation with COMPLETE evidence dict including ad_group_id
    return Recommendation(
        rule_id="SHOP-BID-001",
        entity_id=str(product['product_id']),
        action_type="update_product_bid",
        evidence={
            "product_id": str(product['product_id']),
            "ad_group_id": str(product['ad_group_id']),  # ✅ CRITICAL
            "product_title": product.get('product_title', ''),
            # ... other fields
        },
        # ... other Recommendation fields
    )
```

### Fix 2: Update `routes.py` Shopping Section

**File:** `act_dashboard/routes.py` lines 1569-1642

**Replace hardcoded logic with:**
```python
# Import shopping rules
from act_autopilot.rules import shopping_rules

# Generate recommendations using rules (like keywords/ads)
shopping_recs = shopping_rules.apply_rules(
    products_df.to_dict('records'), 
    ctx  # Pass context if needed
)

# Convert to dicts for cache (with 'id' field)
shopping_cache = []
for idx, rec in enumerate(shopping_recs):
    from dataclasses import asdict
    rec_dict = asdict(rec)
    rec_dict['id'] = idx
    shopping_cache.append(rec_dict)

# Store in cache
current_app.config['RECOMMENDATIONS_CACHE']['shopping'] = shopping_cache
```

### Fix 3: Data Source Enhancement

**Query to include `ad_group_id`:**
```sql
SELECT 
    p.*,
    sp.ad_group_id  -- ✅ Add this field
FROM analytics.product_features_daily p
LEFT JOIN raw_shopping_product_partitions sp 
    ON p.product_id = sp.product_id 
    AND p.customer_id = sp.customer_id
WHERE p.customer_id = ?
  AND p.snapshot_date = ?
```

---

## VERIFICATION CHECKLIST

After implementing fixes:

- [ ] `shopping_rules.py` file exists
- [ ] `apply_rules()` function defined
- [ ] Rule functions return Recommendation objects
- [ ] Evidence dict includes `ad_group_id`
- [ ] Routes.py uses `shopping_rules.apply_rules()`
- [ ] Recommendations stored in cache as dicts
- [ ] Dry-run execution succeeds (green toast)
- [ ] No "Missing required parameters" errors

---

## ARCHITECTURAL CONSISTENCY

**BEFORE (Current State):**
```
Keywords → keyword_rules.py ✅
Ads      → ad_rules.py ✅
Shopping → hardcoded in routes.py ❌
```

**AFTER (Target State):**
```
Keywords → keyword_rules.py ✅
Ads      → ad_rules.py ✅
Shopping → shopping_rules.py ✅

ALL follow same pattern:
1. Rules generate Recommendation objects
2. Routes convert to dicts for cache
3. Template displays
4. Executor receives and validates
```

---

## NEXT STEPS

1. Create `shopping_rules.py` with proper rule structure
2. Update routes.py to use shopping rules
3. Test with synthetic data
4. Verify execution works (green toasts)
5. Document in CHAT_17_HANDOFF.md
6. Git commit with comprehensive message

---

**END OF ANALYSIS**
