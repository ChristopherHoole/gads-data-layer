# CHAT 100: Engine Fix — Query Most Recent Valid Data Date

**Date:** 2026-03-18
**Priority:** HIGH
**Estimated Time:** 30 minutes
**Dependencies:** None

---

## CONTEXT

The recommendations engine loads ALL rows from `campaign_features_daily` ordered by
`snapshot_date DESC`. The synthetic data was generated up to 2026-03-16. The rebuild
script (Chat 99) created feature rows for 2026-03-17 and 2026-03-18 but with NULL
`campaign_name` and incomplete metrics because `campaign_daily` has no source rows
for those dates.

The engine iterates all 360 rows (4 campaigns × 90 days) instead of just the 4 most
recent valid rows. The most recent rows (2026-03-17, 2026-03-18) have NULL names, so
campaigns fall back to `campaign_1001` style ID names.

**Confirmed by diagnostic scripts:**
- `campaign_daily` has NO rows for 2026-03-17 or 2026-03-18
- `campaign_features_daily` has NULL `campaign_name` for all 4 campaigns on those dates
- Engine loads 360 rows and processes all of them

---

## OBJECTIVE

Fix the engine to only load the most recent snapshot date that has valid data (non-NULL
campaign name) for each entity type.

---

## THE FIX

**File:** `C:\Users\User\Desktop\gads-data-layer\act_autopilot\recommendations_engine.py`

Read the file first. Find the entity data query inside the main processing loop. It
currently looks like this:

```python
query = f"""
    SELECT * FROM {table_name}
    WHERE customer_id = ?
    ORDER BY snapshot_date DESC
"""
entity_data = conn.execute(query, [customer_id]).df()
```

Replace with a query that:
1. Finds the most recent `snapshot_date` where `campaign_name IS NOT NULL` (or the
   equivalent name column for each entity type)
2. Only loads rows from that date

The name column varies by entity type — use `id_col` and `name_col` which are already
resolved before the query runs. Use `name_col` for the NOT NULL check.

The fixed query should be:

```python
query = f"""
    SELECT * FROM {table_name}
    WHERE customer_id = ?
      AND snapshot_date = (
          SELECT MAX(snapshot_date)
          FROM {table_name}
          WHERE customer_id = ?
            AND {name_col} IS NOT NULL
      )
    ORDER BY {id_col}
"""
entity_data = conn.execute(query, [customer_id, customer_id]).df()
```

Note: the query now takes TWO `customer_id` parameters — one for the outer WHERE and
one for the subquery.

---

## DELIVERABLES

1. `C:\Users\User\Desktop\gads-data-layer\act_autopilot\recommendations_engine.py`
   — MODIFY: entity data query only
2. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_100_HANDOFF.md` — CREATE

---

## REQUIREMENTS

- Read the file before editing
- Only change the entity data query — do not touch anything else
- The fix must work for ALL entity types (campaign, keyword, ad_group, shopping, ad)
  since they all use the same query pattern
- Add a print statement after the query:
  `print(f"[ENGINE] Using snapshot_date: {entity_data['snapshot_date'].iloc[0] if not entity_data.empty else 'N/A'}")`
- Read back the modified section to verify

---

## SUCCESS CRITERIA

- [ ] Engine log shows `[ENGINE] Loaded 4 campaign rows` (not 360)
- [ ] Engine log shows the correct snapshot date (2026-03-16 or earlier)
- [ ] Campaign names show correctly (PPC Freelancer, Google Ads Consultant etc.)
- [ ] Flask starts cleanly
- [ ] No other engine behaviour changed

---

## HOW TO TEST

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
