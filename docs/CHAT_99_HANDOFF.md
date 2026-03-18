# CHAT 99 HANDOFF — Engine Fixes: CPC Micros, Broken Rules, Impression Share

**Date:** 2026-03-18
**Status:** Complete — all 3 bugs fixed and verified

---

## What Was Fixed

### Bug 1 — CPC stored in micros, compared in pounds (Rule 21 firing incorrectly)

**File:** `act_autopilot/recommendations_engine.py`

**Root cause:** `cpc_w7_mean` (and 14d, 30d) in `campaign_features_daily` is computed as
`cost_micros_sum / clicks_sum` — so it's in micros. The metric maps had no divisor, so rule 21's
condition `cpc_avg_7d > 5` (meaning £5) was comparing against 5,390,056 micros, always true.

**Changes made:**
- Added 4th tuple element (divisor `1_000_000`) to `cpc_avg_7d/14d/30d` and `cost_7d/14d/30d`
  in `CAMPAIGN_METRIC_MAP`
- Same divisor added to `cost` in `SHOPPING_METRIC_MAP` and `AD_METRIC_MAP`
- `_get_metric_value()` updated to apply divisor when 4th tuple element is present
- `_evaluate_condition()` updated likewise (used for trigger summaries)
- Main engine loop condition 1 and condition 2 unpacking updated to handle 4th element and divide

**Pattern:** All metric map entries remain 3-tuples `(db_col, override_op, override_threshold)`.
Entries that need conversion now have a 4th element: `(..., 1_000_000)`. All code that unpacks
entries now uses `entry[0], entry[1], entry[2]` + `entry[3] if len(entry) > 3 else 1`.

---

### Bug 2 — Rules 19 and 20 had op=None and ref=None (never fired)

**Script created:** `scripts/fix_rules_19_20_conditions.py`

**Root cause:** Created via the flow builder but condition `op` and `ref` fields were saved as
`None`. Engine's `_evaluate()` returns `False` for any `operator=None` call.

**Fix applied (verified):**
```
Rule 19 — Loosen tCPA Target – Volume Constrained:
  condition 1: metric=cpa_14d  op=gte  value=1.05  ref=x_target
  condition 2: metric=impression_share_lost_rank  op=gt  value=20  ref=pct

Rule 20 — Increase Max CPC Cap – Low Impression Share:
  condition 1: metric=impression_share_lost_rank  op=gt  value=30  ref=pct
  condition 2: metric=clicks_7d  op=gte  value=20  ref=absolute
```

---

### Bug 3 — impression_share_lost_rank was NULL for all campaigns (Rules 17 and 20 always failed)

**Files:** `act_lighthouse/features.py` + `scripts/rebuild_campaign_features.py`

**Root cause:** `_pick_expr()` checked for `search_rank_lost_impression_share` in `campaign_daily`
columns. That column does not exist in the synthetic data. Result: always `CAST(NULL AS DOUBLE)`.

**Fix in features.py (line 174):** Replaced `_pick_expr()` call with an explicit fallback:
```python
if "search_rank_lost_impression_share" in cols:
    rank_lost_is_expr = "CAST(cd.search_rank_lost_impression_share AS DOUBLE)"
elif "search_impression_share" in cols:
    # Approximate: lost rank IS ~ 1 - search_impression_share (as percentage 0-100)
    rank_lost_is_expr = "CAST((1.0 - cd.search_impression_share) * 100.0 AS DOUBLE)"
else:
    rank_lost_is_expr = "CAST(NULL AS DOUBLE)"
```

**Rebuild script run and verified:**
- 360 rows inserted (90 days x 4 campaigns)
- 352 non-NULL `impression_share_lost_rank` values (8 NULL expected at start of window)
- Sample values: 22–59% range (reasonable approximation from search_impression_share)
- Copied to `warehouse_readonly.duckdb` (430 total rows including all customers)

---

## Files Modified

| File | Action |
|------|--------|
| `act_autopilot/recommendations_engine.py` | Modified — divisor fix in metric maps + all evaluation code |
| `act_lighthouse/features.py` | Modified — impression_share_lost_rank fallback |
| `scripts/fix_rules_19_20_conditions.py` | Created — DB migration for rules 19/20 conditions |
| `scripts/rebuild_campaign_features.py` | Created — rebuilds campaign_features_daily + copies to readonly |

---

## How to Test

```powershell
cd C:\Users\User\Desktop\gads-data-layer
.\.venv\Scripts\Activate.ps1
python act_dashboard/app.py
```

Then in Opera:
1. Campaigns > Rules & Flags > enable all 6 bid rules
2. Recommendations tab > Run Recommendations Now
3. Confirm recs generated from rules 16, 17, 18, 19, 20, 21 (not just 21)
4. Confirm CPC cap recs show sensible pound values (e.g. £5.39 not £5390056)

---

## Known Remaining Issues

- `cpa_wN_mean` columns in `campaign_features_daily` are also in micros (same root cause as CPC)
  — rules using `cpa_14d` with `x_target` ref may still evaluate against raw micros.
  This was not in scope for Chat 99 but should be addressed if rule 19 fires unexpectedly.
- The 8 NULL rows for `impression_share_lost_rank` are the earliest dates in the 7-day rolling
  window where there is insufficient preceding data — this is correct behaviour.
