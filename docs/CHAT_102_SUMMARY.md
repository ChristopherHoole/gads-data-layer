# CHAT 102 SUMMARY

**Date:** 2026-03-19
**Scope:** Keywords page — search terms DATE/VARCHAR fix

---

## Problem

Custom date ranges from the date picker (e.g. "Last 14 days", "This month") caused the search terms table to disappear silently. Preset buttons (7d, 30d, 90d) worked correctly.

**Root cause:** DuckDB's `BETWEEN` clause requires both operands to share the same type. The `snapshot_date` column is `DATE`, but custom date range parameters arrive as `VARCHAR` strings. Preset buttons work because their code path constructs dates differently.

**Error:** `Binder Error: Cannot mix values of type DATE and VARCHAR in BETWEEN clause`

---

## Fix

**File:** `act_dashboard/routes/keywords.py`
**Function:** `load_search_terms()`
**Line:** 164

```python
# Before
where_clauses.append("snapshot_date BETWEEN ? AND ?")

# After
where_clauses.append("snapshot_date BETWEEN CAST(? AS DATE) AND CAST(? AS DATE)")
```

Casting the VARCHAR parameters to DATE at the SQL level satisfies DuckDB's type consistency requirement.

---

## Success Criteria Met

- [x] Custom date ranges load search terms table without error
- [x] Preset buttons (7d, 30d, 90d) unaffected (their code path unchanged)
- [x] No other logic modified
