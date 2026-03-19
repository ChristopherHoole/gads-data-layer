# CHAT 104: Campaign Rules Strategic Changes

**Date:** 2026-03-19
**Estimated Time:** 30-45 minutes
**Priority:** HIGH
**Dependencies:** None

---

## CONTEXT

Strategic review of all 19 campaign rules identified issues: 4 pacing rules don't apply at campaign level (pacing is account-level), 3 rules have data thresholds too low/high, and 2 pause rules have inconsistent cooldowns. This task deletes 4 pacing rules and updates 5 rules with corrected thresholds and cooldowns.

---

## OBJECTIVE

Delete 4 pacing-based budget rules and update 5 campaign rules with corrected thresholds and cooldowns based on strategic review.

---

## DELIVERABLES

1. `C:\Users\User\Desktop\gads-data-layer\scripts\update_campaign_rules.py` — CREATE
   - SQL migration script to delete and update rules
2. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_104_HANDOFF.md` — CREATE
3. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_104_SUMMARY.md` — CREATE

---

## REQUIREMENTS

### DELETE (4 rules)
- Rule 4: Pacing Reduction – Over Budget (pacing is account-level, not campaign-level)
- Rule 5: Pacing Increase – Under Budget (tROAS variant)
- Rule 10: Pacing Increase – Under Budget (tCPA variant)
- Rule 15: Pacing Increase – Under Budget (CTR variant)

### UPDATE (5 rules)
- **Rule 7:** conversions_7d threshold 3 → 10 (3 conversions too low for reliable signal)
- **Rule 11:** ctr_7d threshold 5.0% → 4.0% (5% too high for typical Search campaigns)
- **Rule 20:** clicks_7d threshold 20 → 30 (consistency with other click thresholds)
- **Rule 23:** cooldown_days 14 → 30 (pause rules should have consistent cooldown)
- **Rule 24:** cooldown_days 14 → 30 (match Rule 22 and Rule 23)

### SQL Operations
```sql
-- Delete pacing rules
DELETE FROM rules WHERE id IN (4, 5, 10, 15);

-- Rule 7: Update conversions threshold 3 → 10
UPDATE rules 
SET conditions = '[{"metric":"cpa_7d","op":"gt","value":"1.2","ref":"x_target"},{"metric":"conversions_7d","op":"gt","value":"10","ref":"absolute"}]' 
WHERE id = 7;

-- Rule 11: Update CTR threshold 5.0 → 4.0
UPDATE rules 
SET conditions = '[{"metric":"ctr_7d","operator":">=","value":4.0,"unit":"percent"},{"metric":"clicks_7d","operator":">=","value":50,"unit":"absolute"}]' 
WHERE id = 11;

-- Rule 20: Update clicks threshold 20 → 30
UPDATE rules 
SET conditions = '[{"metric":"impression_share_lost_rank","op":"gt","value":30,"ref":"pct"},{"metric":"clicks_7d","op":"gte","value":"30","ref":"absolute"}]' 
WHERE id = 20;

-- Rules 23 & 24: Update cooldown 14 → 30 days
UPDATE rules 
SET cooldown_days = 30 
WHERE id IN (23, 24);
```

---

## BUILD PLAN

**Create migration script:**
1. Create `scripts/update_campaign_rules.py`
2. Connect to warehouse.duckdb
3. Execute DELETE for rules 4, 5, 10, 15
4. Execute 5 UPDATE statements for rules 7, 11, 20, 23, 24
5. Print confirmation of changes
6. Close connection

**Script structure:**
```python
import duckdb

conn = duckdb.connect('warehouse.duckdb')

# Delete pacing rules
conn.execute("DELETE FROM rules WHERE id IN (4, 5, 10, 15)")
print("Deleted 4 pacing rules (4, 5, 10, 15)")

# Update Rule 7 (conversions 3→10)
# Update Rule 11 (CTR 5→4%)
# Update Rule 20 (clicks 20→30)
# Update Rules 23 & 24 (cooldown 14→30)

print("All updates complete")
conn.close()
```

---

## SUCCESS CRITERIA

- [ ] Script executes without errors
- [ ] 4 pacing rules deleted (4, 5, 10, 15)
- [ ] Rule 7 conversions threshold = 10
- [ ] Rule 11 CTR threshold = 4.0
- [ ] Rule 20 clicks threshold = 30
- [ ] Rules 23 & 24 cooldown = 30 days
- [ ] Diagnostic query confirms all changes

ALL must pass before reporting complete.

---

## REFERENCE FILES

- `C:\Users\User\Desktop\gads-data-layer\warehouse.duckdb` — Target database

---

## TESTING

1. Run migration script: `python scripts/update_campaign_rules.py`
2. Verify deletions:
```sql
SELECT COUNT(*) FROM rules WHERE id IN (4, 5, 10, 15);
-- Should return 0
```
3. Verify updates:
```sql
SELECT id, name, conditions, cooldown_days FROM rules WHERE id IN (7, 11, 20, 23, 24);
```
4. Report all changes confirmed with exact values

---

**Brief Version:** 1.0
**Template Version:** 5.0
