# CHAT 92 SUMMARY: Add impression_share_lost_rank to Features Pipeline

**Date:** 2026-03-14
**Status:** COMPLETE ✅

---

## What Was Done

Added `impression_share_lost_rank` as a real computed column to `analytics.campaign_features_daily`, replacing the missing entry in `CAMPAIGN_METRIC_MAP` so that 4 seeded rules can evaluate against actual data.

---

## Files Changed

### 1. `act_lighthouse/features.py`
- Added `("impression_share_lost_rank", "DOUBLE", False)` to the DDL cols list in `_ensure_features_table()`, after `has_impr_share`
- Bumped `schema_version` default from `1` → `2`
- Added `rank_lost_is_expr = _pick_expr(cols, "search_rank_lost_impression_share", "DOUBLE")` (safe fallback to NULL if column absent)
- **src CTE:** added `{rank_lost_is_expr} AS rank_lost_is`
- **dense CTE:** added `src.rank_lost_is AS rank_lost_is` (no COALESCE — NULLs preserved)
- **roll CTE:** added `rank_lost_is,` to explicit column list (feeds through to roll2 via `r.*`)
- **final SELECT:** added 7-day rolling AVG window function:
  ```sql
  AVG(roll2.rank_lost_is) OVER (
      PARTITION BY roll2.customer_id, roll2.campaign_id
      ORDER BY roll2.snapshot_date
      ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
  ) AS impression_share_lost_rank
  ```
- Added `"impression_share_lost_rank"` to `insert_cols` list

### 2. `act_autopilot/recommendations_engine.py`
- Added to `CAMPAIGN_METRIC_MAP`:
  ```python
  "impression_share_lost_rank": ("impression_share_lost_rank", None, None),
  ```
  (replaces missing entry; 4 rules now resolve to a real column)

### 3. `scripts/add_impression_share_col.py` (NEW)
- Migration script: `ALTER TABLE analytics.campaign_features_daily ADD COLUMN impression_share_lost_rank DOUBLE`
- Applied to both `warehouse.duckdb` and `warehouse_readonly.duckdb`
- Safe to re-run (catches existing column errors)

---

## Test Results

| Check | Result |
|---|---|
| Migration script on warehouse.duckdb | ✅ column added |
| Migration script on warehouse_readonly.duckdb | ✅ column added |
| `build_campaign_features_daily()` runs without error | ✅ 20 rows inserted |
| Column present in campaign_features_daily | ✅ confirmed via PRAGMA |
| Values | NULL (expected — `search_rank_lost_impression_share` absent from synthetic data; real GA data will populate it) |
| CAMPAIGN_METRIC_MAP entry | ✅ real column, not proxy |

---

## Architecture Note

`search_rank_lost_impression_share` is not present in the current synthetic `analytics.campaign_daily`. The `_pick_expr()` helper detects this at build time and substitutes `CAST(NULL AS DOUBLE)`, which means `impression_share_lost_rank` will be NULL until real GA data (from `snap_campaign_daily`) populates the source column. This is the correct behavior per the NULL handling requirement.
