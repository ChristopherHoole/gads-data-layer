# CHAT 88 HANDOFF — AD_DAILY TABLE + DATABASE INDEXES

**Date completed:** 2026-03-12
**Status:** COMPLETE

---

## What was built

### 1. `tools/seed_ad_daily.py` (CREATED)
Drops and recreates `analytics.ad_daily` in `warehouse.duckdb` with 90 days of
synthetic data.

- **15 ads** across 3 campaigns, 6 ad groups
- **1,350 rows** (15 ads × 90 days)
- **Schema matches** what `act_dashboard/routes/ads.py` and `shared.py` expect:
  - `cost_micros` (BIGINT, cost × 1,000,000)
  - `conversions_value` (DOUBLE)
  - `search_impression_share`, `search_top_impression_share`,
    `search_absolute_top_impression_share`, `click_share` (DOUBLE)
- Ad strength mix: EXCELLENT (2), GOOD (5), AVERAGE (4), POOR (4)
- Base impressions scaled to trigger all 4 Ad rules:
  Brand=25000, Non-brand=18000, Competitor=10000 per day

### 2. `scripts/copy_all_to_readonly.py` (NO CHANGE NEEDED)
Already contained `"ad_daily"` in its TABLES list — confirmed working.

### 3. `scripts/add_indexes.py` (CREATED)
Adds 13 indexes to `warehouse_readonly.duckdb` across 5 analytics tables.

| Table | Indexes |
|-------|---------|
| campaign_daily | campaign_id, snapshot_date |
| keyword_daily | keyword_id, campaign_id, snapshot_date |
| ad_group_daily | ad_group_id, campaign_id, snapshot_date |
| ad_daily | ad_id, campaign_id, snapshot_date |
| shopping_campaign_daily | campaign_id, snapshot_date |

### 4. `act_autopilot/recommendations_engine.py` (MODIFIED)
- Added `"ad": "ro.analytics.ad_daily"` to `ENTITY_TABLES`
- Added `"ad": ("ad_id", "ad_name")` to `ENTITY_ID_COLUMNS`
- Added `AD_METRIC_MAP` with 7 metric mappings
- Added `elif entity_type == "ad":` in `_get_metric_map_for_entity`
- Added `"ad"` case in `_get_current_value`
- **Critical fix**: `_detect_entity_type` — `"ad_group_1".split("_")[0]` returns
  `"ad"`, causing ad_group rules to be misrouted. Fixed by adding
  `if rule_id.startswith("ad_group_"):` before the generic split.

### 5. `act_dashboard/templates/recommendations.html` (MODIFIED)
- Added `'ad': 'danger'` to entity_colors (red badge)
- Updated entity filter dropdown with dynamic `selectattr` counts
- Added "Ads" entry with `data-entity="ad"` to the dropdown

---

## Verification results

| Check | Result |
|-------|--------|
| `python tools/seed_ad_daily.py` | 1,350 rows, 15 ads, 90 days |
| `python scripts/copy_all_to_readonly.py` | ad_daily: 1,350 rows copied |
| `python scripts/add_indexes.py` | 13 created, 0 errors |
| Ad recommendations generated | **25 total**: ad_1=15, ad_2=4, ad_3=4, ad_4=2 |
| /recommendations page | Ads (25) visible, red AD badge |
| /campaigns | Loads cleanly |
| /keywords | Loads cleanly |
| /ad-groups | Loads cleanly |
| /ads | Loads cleanly, all metrics populated |
| /shopping | Loads cleanly |
| Flask errors | Pre-existing background thread DuckDB conflict only |

---

## Schema correction (during Chat 88)

Initial seed used `cost` and `conversion_value` columns. The `ads.py` route
and `shared.py` expect `cost_micros` (BIGINT) and `conversions_value` (DOUBLE),
plus four impression share columns. Fixed by updating `seed_ad_daily.py` schema
and re-seeding.

---

## Known issues (pre-existing, not caused by Chat 88)

- `duckdb.ConnectionException: Can't open a connection with different config` on
  `/` (Dashboard) at startup — background threads (radar, poller) hold
  `warehouse.duckdb` open with `read_only=False`; Dashboard route tries
  `read_only=True`. Resolves after first request. Not introduced by Chat 88.

---

## Files changed in Chat 88

```
tools/seed_ad_daily.py                      CREATED
scripts/add_indexes.py                      CREATED
act_autopilot/recommendations_engine.py     MODIFIED
act_dashboard/templates/recommendations.html MODIFIED
```

`scripts/copy_all_to_readonly.py` — no changes needed (ad_daily already listed).
