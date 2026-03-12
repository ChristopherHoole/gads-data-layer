# CHAT 88 SUMMARY — AD_DAILY TABLE + DATABASE INDEXES

**Date:** 2026-03-12

---

## Objective

The ACT dashboard had 4 Ad rules that could not generate recommendations because
`analytics.ad_daily` did not exist. Additionally, no database indexes existed on
any analytics tables. This chat created the ad_daily table, seeded it, wired up
the recommendations engine for Ad entities, added 13 indexes to
`warehouse_readonly.duckdb`, and verified all 5 entity pages load cleanly.

---

## Deliverables completed

1. **`tools/seed_ad_daily.py`** — Creates and seeds `analytics.ad_daily` in
   `warehouse.duckdb` with 1,350 rows (15 ads × 90 days). Schema matches the
   column names expected by `ads.py` and `shared.py`: `cost_micros`,
   `conversions_value`, plus four impression share columns.

2. **`scripts/copy_all_to_readonly.py`** — Already included `ad_daily`; no
   changes required. Confirmed it copies 1,350 rows to `warehouse_readonly.duckdb`.

3. **`scripts/add_indexes.py`** — Adds 13 indexes across 5 analytics tables in
   `warehouse_readonly.duckdb`. Verifies using `duckdb_indexes()` system function.

4. **Recommendations engine** — Ad entity support added. 25 Ad recommendations
   generated: ad_1 (low CTR) = 15, ad_2 (POOR strength) = 4, ad_3 (AVERAGE
   strength) = 4, ad_4 (low ROAS) = 2.

5. **`/recommendations` template** — Red "AD" badge added, entity filter dropdown
   updated with dynamic counts and "Ads (25)" entry.

---

## Key decisions

- **Column naming**: Used `cost_micros` (BIGINT, value × 1,000,000) and
  `conversions_value` to match the column names used by all other entity tables
  and the shared query infrastructure.

- **`_detect_entity_type` fix**: `"ad_group_1".split("_")[0]` returns `"ad"` not
  `"ad_group"`. Added `if rule_id.startswith("ad_group_"):` guard before the
  generic split to prevent ad_group rules from routing to the ad entity.

- **Base impressions scaling**: Set Brand=25,000, Non-brand=18,000, Competitor=
  10,000 impressions/day so that `conversions >= 10` threshold (ad_4 rule) fires
  naturally without artificial overrides.

- **Indexes on readonly only**: `add_indexes.py` connects directly to
  `warehouse_readonly.duckdb` — never `warehouse.duckdb`.

---

## Test results

```
python tools/seed_ad_daily.py          -> 1,350 rows, no errors
python scripts/copy_all_to_readonly.py -> ad_daily: 1,350 rows
python scripts/add_indexes.py          -> 13 indexes created, 0 errors
Recommendations engine                 -> 25 Ad recs generated
/ads page                              -> Cost $433.6k, ROAS 4.24x, Impressions 8.08M
All 5 entity pages                     -> Load without errors
```
