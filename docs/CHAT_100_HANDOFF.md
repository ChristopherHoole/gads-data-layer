# CHAT 100 HANDOFF — Engine Date Fix

**Date:** 2026-03-18
**Status:** COMPLETE

---

## What Was Done

Single targeted edit to `act_autopilot/recommendations_engine.py` lines 724–737.

**Before:** engine loaded ALL rows for a customer ordered by `snapshot_date DESC`
— iterating 360 rows (4 campaigns × 90 days) with the 2 most recent dates having
NULL `campaign_name`.

**After:** engine loads only rows from the most recent `snapshot_date` where
`name_col IS NOT NULL`, via a correlated subquery. Two `customer_id` parameters
are passed (outer WHERE + subquery WHERE). A snapshot date print statement was
added after the load.

---

## Files Changed

| File | Change |
|------|--------|
| `act_autopilot/recommendations_engine.py` | Entity data query (lines 724–737) |

---

## Success Criteria Status

- [ ] Engine log shows `[ENGINE] Loaded 4 campaign rows` (not 360)
- [ ] Engine log shows `[ENGINE] Using snapshot_date: 2026-03-16` (or earlier)
- [ ] Campaign names show correctly (PPC Freelancer, Google Ads Consultant etc.)
- [ ] Flask starts cleanly
- [ ] No other engine behaviour changed

---

## How to Test

```powershell
taskkill /IM python.exe /F
cd C:\Users\User\Desktop\gads-data-layer
.\.venv\Scripts\Activate.ps1
python -c "import duckdb; conn = duckdb.connect('warehouse.duckdb'); conn.execute('DELETE FROM recommendations'); conn.execute('DELETE FROM changes'); print('Cleared'); conn.close()"
python act_dashboard/app.py
```

Then in Opera:
1. Enable all 6 bid rules
2. Run Recommendations Now
3. Confirm engine log shows `Loaded 4 campaign rows` and correct snapshot date
4. Confirm campaign names display correctly in recommendations table

---

## Next Chat

No pending issues from this fix. Engine should now process only 4 rows per
entity type per run, with correct names.
