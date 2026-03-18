# CHAT 99: Engine Fixes — CPC Micros, Broken Rules, Impression Share

**Date:** 2026-03-18
**Priority:** HIGH
**Estimated Time:** 2–3 hours
**Architecture:** Claude Code reads files directly — no uploads needed

---

## CONTEXT

The recommendations engine (`act_autopilot/recommendations_engine.py`) has 3 confirmed bugs
found during Test 4 (all bid rules enabled). Diagnostic scripts confirmed:

1. Rule 21 fires on all campaigns incorrectly — CPC metric stored in micros but compared as pounds
2. Rules 19 & 20 have `op=None` in their DB conditions — engine silently skips them
3. `impression_share_lost_rank` is NULL for all campaigns — rules 17 & 20 always fail

---

## BUILD PLAN

### Task 1 — Fix CPC micros conversion in `_get_metric_value()`

**File:** `C:\Users\User\Desktop\gads-data-layer\act_autopilot\recommendations_engine.py`

**Problem:** `cpc_w7_mean`, `cpc_w14_mean`, `cpc_w30_mean` in `campaign_features_daily` are stored
in **micros** (e.g. 5390056 = £5.39). The `CAMPAIGN_METRIC_MAP` maps `cpc_avg_7d` → `cpc_w7_mean`
with no conversion. Rule 21 condition is `cpc_avg_7d > 5` (£5) but gets value 5390056, so it
always evaluates as true.

**Root cause confirmed:** `_get_metric_value()` returns raw feature value with no conversion.
The comment in CAMPAIGN_METRIC_MAP says "micros → divided by 1,000,000 in evaluation" for
cost metrics but this conversion is NEVER actually applied anywhere in the code.

**Fix:**
The CAMPAIGN_METRIC_MAP tuple is `(db_column, override_op, override_threshold)`.
Add a 4th element — a `divisor` — to entries that need unit conversion:

```python
# Old:
"cpc_avg_7d": ("cpc_w7_mean", None, None),

# New:
"cpc_avg_7d": ("cpc_w7_mean", None, None, 1_000_000),
```

Apply the same `1_000_000` divisor to:
- `cpc_avg_7d`, `cpc_avg_14d`, `cpc_avg_30d`
- `cost_7d`, `cost_14d`, `cost_30d`
- `cost_w7_vs_prev_pct` (this is a percentage, NOT micros — leave as-is, verify first)

Update `_get_metric_value()` to apply the divisor:
```python
def _get_metric_value(features, metric_name, metric_map):
    if metric_name not in metric_map:
        return None, metric_name
    entry = metric_map[metric_name]
    db_col = entry[0]
    divisor = entry[3] if len(entry) > 3 else 1
    value = features.get(db_col)
    if value is not None and divisor and divisor != 1:
        value = float(value) / divisor
    return value, db_col
```

Also update all other metric maps (KEYWORD_METRIC_MAP, AD_GROUP_METRIC_MAP, etc.)
that reference `cpc` or `cost` micros columns — apply the same 4th element pattern.

**Verification:** After fix, rule 21 should only fire on campaigns where actual avg CPC > £5.
With synthetic data, `cpc_w7_mean` ~5390056 micros = £5.39 — rule should still fire for most
campaigns (just now correctly). Rule 16/18 ROAS conditions are already correct (no micros).

---

### Task 2 — Fix broken conditions on rules 19 and 20 in DB

**File:** Write a Python migration script at
`C:\Users\User\Desktop\gads-data-layer\scripts\fix_rules_19_20_conditions.py`

**Problem:** Rules 19 and 20 were created via the flow builder but their condition operators
(`op`) and reference types (`ref`) were saved as `None`. The engine's `_evaluate()` function
receives `operator=None` and returns `False`, so these rules never fire.

Current broken state (confirmed by diagnostic):
```
Rule 19 — Loosen tCPA Target – Volume Constrained:
  condition 1: metric=cpa_14d  op=None  value=1.05  ref=None
  condition 2: metric=impression_share_lost_rank  op=None  value=20  ref=None

Rule 20 — Increase Max CPC Cap – Low Impression Share:
  condition 1: metric=impression_share_lost_rank  op=None  value=30  ref=None
  condition 2: metric=clicks_7d  op=None  value=20  ref=None
```

**Correct conditions (based on rule names and plain English logic):**
```
Rule 19 — Loosen tCPA Target – Volume Constrained:
  condition 1: metric=cpa_14d  op="gte"  value=1.05  ref="x_target"
               (CPA is above target — campaign struggling to convert)
  condition 2: metric=impression_share_lost_rank  op="gt"  value=20  ref="pct"
               (Losing IS due to rank, not budget — bid is too low)

Rule 20 — Increase Max CPC Cap – Low Impression Share:
  condition 1: metric=impression_share_lost_rank  op="gt"  value=30  ref="pct"
               (Significant IS loss due to rank)
  condition 2: metric=clicks_7d  op="gte"  value=20  ref="absolute"
               (Enough volume to justify raising the cap)
```

**Script should:**
1. Connect to `warehouse.duckdb`
2. Read current conditions for rules 19 and 20 and print them (verify before changing)
3. Update conditions JSON with correct `op` and `ref` values
4. Print updated conditions to confirm
5. Close connection

---

### Task 3 — Fix `impression_share_lost_rank` being NULL

**Files:**
- `C:\Users\User\Desktop\gads-data-layer\act_lighthouse\features.py`
- New script: `C:\Users\User\Desktop\gads-data-layer\scripts\rebuild_campaign_features.py`

**Problem:** `impression_share_lost_rank` is NULL for all campaigns. Root cause confirmed:

In `features.py`, `_pick_expr()` checks if `search_rank_lost_impression_share` exists in
`campaign_daily` columns. If it doesn't exist, it returns `CAST(NULL AS DOUBLE)`. The
synthetic data table `campaign_daily` has `search_impression_share` but NOT
`search_rank_lost_impression_share` — so the column is always NULL.

**Confirmed column names in campaign_daily (from synthetic data generator):**
- `search_impression_share` — EXISTS ✅
- `search_top_impression_share` — EXISTS ✅
- `search_absolute_top_impression_share` — EXISTS ✅
- `search_rank_lost_impression_share` — DOES NOT EXIST ❌

**Fix in `features.py`:** Update `_pick_expr` call for `rank_lost_is_expr` to also
try `search_impression_share` as a fallback approximation. Or better — add a derived
expression that approximates rank-lost IS as `1 - search_impression_share` when
`search_rank_lost_impression_share` is not available:

```python
# Instead of:
rank_lost_is_expr = _pick_expr(cols, "search_rank_lost_impression_share", "DOUBLE")

# Use:
if "search_rank_lost_impression_share" in cols:
    rank_lost_is_expr = "CAST(cd.search_rank_lost_impression_share AS DOUBLE)"
elif "search_impression_share" in cols:
    # Approximate: lost rank IS ≈ 1 - search_impression_share (as percentage 0-100)
    rank_lost_is_expr = "CAST((1.0 - cd.search_impression_share) * 100.0 AS DOUBLE)"
else:
    rank_lost_is_expr = "CAST(NULL AS DOUBLE)"
```

**After fixing features.py**, write `scripts/rebuild_campaign_features.py` that:
1. Drops and rebuilds `analytics.campaign_features_daily` using the updated features.py logic
   for customer_id `1254895944` for the last 90 days
2. Copies to readonly DB using the same pattern as existing copy scripts
3. Prints row count and sample `impression_share_lost_rank` values to confirm non-NULL

---

## DELIVERABLES

1. `C:\Users\User\Desktop\gads-data-layer\act_autopilot\recommendations_engine.py` — MODIFY
   - 4th element (divisor) added to CPC and cost metric map entries
   - `_get_metric_value()` updated to apply divisor
   - All metric maps updated consistently

2. `C:\Users\User\Desktop\gads-data-layer\scripts\fix_rules_19_20_conditions.py` — CREATE
   - Fixes op and ref on rules 19 and 20 in warehouse.duckdb

3. `C:\Users\User\Desktop\gads-data-layer\act_lighthouse\features.py` — MODIFY
   - `rank_lost_is_expr` falls back to `(1 - search_impression_share) * 100`

4. `C:\Users\User\Desktop\gads-data-layer\scripts\rebuild_campaign_features.py` — CREATE
   - Rebuilds campaign_features_daily with correct impression_share_lost_rank values

5. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_99_HANDOFF.md` — CREATE
   - Summary of changes, files modified, how to test

---

## REQUIREMENTS

- Read every file before editing
- Run `fix_rules_19_20_conditions.py` and verify output before considering Task 2 complete
- Run `rebuild_campaign_features.py` and verify non-NULL impression_share values before considering Task 3 complete
- Do NOT touch any HTML, CSS, or dashboard route files
- Do NOT modify the rules table other than fixing conditions on rules 19 and 20

---

## SUCCESS CRITERIA

- [ ] Rule 21 only fires on campaigns where actual CPC (in £) > £5 threshold
- [ ] Rules 19 and 20 have valid `op` and `ref` in their conditions
- [ ] `impression_share_lost_rank` is non-NULL in campaign_features_daily for customer 1254895944
- [ ] Running the recommendations engine with all 6 bid rules enabled generates recs from
      rules 16, 17, 18, 19, 20, 21 (not just 21)
- [ ] Flask starts cleanly
- [ ] No other rules or features are broken

---

## HOW TO TEST AFTER COMPLETION

```powershell
# In PowerShell
cd C:\Users\User\Desktop\gads-data-layer
.\.venv\Scripts\Activate.ps1
python scripts/fix_rules_19_20_conditions.py
python scripts/rebuild_campaign_features.py
python act_dashboard/app.py
```

Then in Opera:
1. Campaigns → Rules & Flags → enable all 6 bid rules
2. Recommendations tab → Run Recommendations Now
3. Confirm recs generated from multiple bid rule types, not just rule 21
4. Confirm CPC cap recs show sensible £ values in the action column

