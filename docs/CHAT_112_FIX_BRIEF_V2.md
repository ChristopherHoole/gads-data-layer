# CHAT 112 FIX: PRODUCT RULES CORRECTIONS (V2)

**Date:** 2026-03-23  
**Priority:** HIGH  
**Estimated Time:** 30 minutes

---

## CONTEXT

Chat 112 created Shopping Product Rules. Testing in Opera revealed 2 issues:
1. **Type pills missing** - RULE TYPE column shows blanks for some rules
2. **Cost values in micros** - showing 50000000 instead of 50

UI shows 10 product rules and toggles work. Rules exist and are being returned by `/shopping/product_rules` route.

---

## OBJECTIVE

Fix cost values (convert micros to pounds) and ensure all type pills render in UI.

---

## CRITICAL: CLIENT FILTER

**ALL queries must include:**
```sql
WHERE client_config = 'client_christopher_hoole'
```

Do NOT modify rules for other clients.

---

## STEP 1: DIAGNOSTIC

Run this query to see current state:

```sql
SELECT id, name, type, rule_or_flag, entity_type, conditions
FROM rules
WHERE client_config = 'client_christopher_hoole'
  AND entity_type = 'shopping_product'
ORDER BY id;
```

Report back:
- How many rules found?
- What are the distinct `type` values?
- Which rules have NULL or empty `type`?
- Which rules have cost_* metrics in conditions?

---

## STEP 2: FIX COST VALUES (MICROS → POUNDS)

**Problem:** Product costs stored as micros (50000000) should be pounds (50.0).

**Action:**

For each product rule:
1. Parse `conditions` JSON
2. Loop through conditions array
3. Find any condition where `metric` contains 'cost'
4. If `value` > 1000: divide by 1,000,000
5. Update the conditions JSON in database

**Example:**

Before:
```json
[{"metric": "cost_7d", "op": "gte", "value": 50000000, "ref": "absolute"}]
```

After:
```json
[{"metric": "cost_7d", "op": "gte", "value": 50.0, "ref": "absolute"}]
```

**Update query pattern:**
```sql
UPDATE rules
SET conditions = ?,
    updated_at = NOW()
WHERE id = ?
  AND client_config = 'client_christopher_hoole'
  AND entity_type = 'shopping_product'
```

**Report:**
- How many rules had cost conditions?
- How many were in micros (value > 1000)?
- List of IDs updated

---

## STEP 3: FIX MISSING TYPE VALUES

**Check:** Are there any product rules where `type` is NULL or empty string?

**If yes:**

Set type based on action_type:
- `increase_priority` or `decrease_priority` → type = 'performance' (or 'priority' if that's what you used)
- `pause` → type = 'performance' (or 'status')
- Rules with cost/roas/cpa metrics → type = 'performance'
- Rules with stock metrics → type = 'stock'
- Rules with feed quality metrics → type = 'feed_quality'

**Update query:**
```sql
UPDATE rules
SET type = ?,
    updated_at = NOW()
WHERE id = ?
  AND client_config = 'client_christopher_hoole'
  AND entity_type = 'shopping_product'
```

**Report:**
- How many rules had NULL/empty type?
- List of IDs updated with new type values

---

## STEP 4: VERIFY UI RENDERING

**Check `renderProductRulesTable()` in shopping_new.html:**

1. Find the type badge rendering code (search for `ruleTypeBadge`)
2. Verify it has mappings for ALL type values found in database
3. If any types missing from badge mapping, add them

**Example badge mapping:**
```javascript
const ruleTypeBadge = 
    rule.type === 'performance' ? 'primary' : 
    rule.type === 'feed_quality' ? 'warning' :
    rule.type === 'lifecycle' ? 'info' :
    rule.type === 'stock' ? 'success' :
    'secondary';
```

Add any missing type values.

---

## STEP 5: TEST

1. Restart Flask
2. Navigate to Shopping > Product Rules
3. Verify:
   - All rules show type pills (no blanks)
   - Cost conditions show as pounds: "Cost (7d) > 50" not "Cost (7d) > 50000000"
4. Take screenshot

---

## SUCCESS CRITERIA

**Database:**
- ✅ All cost values in conditions are < 1000 (pounds, not micros)
- ✅ All product rules have non-NULL `type` field

**UI:**
- ✅ RULE TYPE column shows colored pills for all 10 rules
- ✅ CONDITIONS column shows cost as pounds (50, 100, not 50000000)
- ✅ Zero blanks in RULE TYPE column

---

## DELIVERABLES

**Report format:**

```
=== DIAGNOSTIC ===
- Found: X product rules
- Types in use: [list]
- Rules with NULL type: [count]
- Rules with cost conditions: [count]
- Rules with cost in micros: [count]

=== FIXES APPLIED ===
- Updated cost values: [list of IDs]
- Updated type values: [list of IDs]
- UI badge mapping: [added/already correct]

=== VERIFICATION ===
- Screenshot attached
- All type pills visible: YES/NO
- Cost values in pounds: YES/NO
```

**Include screenshot of Product Rules table after fixes.**

---

**END OF BRIEF V2**
