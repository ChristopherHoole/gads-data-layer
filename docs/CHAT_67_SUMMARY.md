# CHAT 67 SUMMARY — Real Data Ingestion Pipeline

**Date:** 2026-03-07

---

## What Was Done

### Task 1 — Fixed `src/gads_pipeline/v1_runner.py`
Changed `main()` to connect to `warehouse.duckdb` instead of `warehouse_readonly.duckdb`.

```python
# Before (wrong)
db_path = Path('warehouse_readonly.duckdb')

# After (correct)
db_path = Path('warehouse.duckdb')
```

### Task 2 — Created `scripts/copy_all_to_readonly.py`
New script that copies all 5 analytics tables from `warehouse.duckdb` to `warehouse_readonly.duckdb`.

Uses DuckDB's ATTACH feature for schema-agnostic copying (no hardcoded CREATE TABLE needed). Handles both VIEW and TABLE types in the readonly DB.

Tables copied:
- `analytics.campaign_daily`
- `analytics.keyword_daily`
- `analytics.search_term_daily`
- `analytics.ad_group_daily`
- `analytics.ad_daily`

### Task 3 — Created `tools/run_ingestion.py`
Orchestration script that runs pull + copy in one command.

Usage:
```
python tools/run_ingestion.py --customer-id 1254895944 --date 2026-03-07 --mode live
python tools/run_ingestion.py --customer-id 1254895944 --date 2026-03-07 --mode mock
```

Steps:
1. Connects to `warehouse.duckdb` and calls all 5 pull functions
2. Calls `copy_all_to_readonly()` to sync tables to readonly DB
3. Prints a summary table with row counts from both databases

---

## Mock Test Output

```
============================================================
INGESTION PIPELINE - 2026-03-07 - MODE: MOCK
Customer ID: 1254895944
============================================================

[Step 1/3] Pulling data into warehouse.duckdb...
[v1_runner] Pulling campaign data... MOCK MODE - No API call, no data inserted
[v1_runner] Pulling keyword data... MOCK MODE - No API call, no data inserted
[v1_runner] Pulling search term data... MOCK MODE - No API call, no data inserted
[v1_runner] Pulling ad group data... MOCK MODE - No API call, no data inserted
[v1_runner] Pulling ad data... MOCK MODE - No API call, no data inserted
[Step 1/3] Pull complete.

[Step 2/3] Copying tables to warehouse_readonly.duckdb...
  analytics.campaign_daily: 7,335 rows
  analytics.keyword_daily: 77,413 rows
  analytics.search_term_daily: 45,090 rows
  analytics.ad_group_daily: 23,725 rows
  analytics.ad_daily: 21,420 rows
[Step 2/3] Copy complete.

============================================================
INGESTION SUMMARY
============================================================
Table                  warehouse.duckdb  readonly.duckdb
------------------------------------------------------------
campaign_daily                    7,335            7,335
keyword_daily                    77,413           77,413
search_term_daily                45,090           45,090
ad_group_daily                   23,725           23,725
ad_daily                         21,420           21,420
============================================================

NOTE: Mock mode - no API calls made, no data inserted.
```

---

## Live Test Result

The live test connected to the Google Ads API successfully but received:

```
DEVELOPER_TOKEN_NOT_APPROVED: The developer token is only approved for use
with test accounts. To access non-test accounts, apply for Basic or
Standard access.
```

**This is not a code bug.** The pipeline is correct. The Google Ads developer token needs to be upgraded from Test to Basic/Standard access level before it can query real accounts.

- `login_customer_id` is correctly set to `4434379827` in `secrets/google-ads.yaml`
- API connectivity is confirmed (request reached Google's servers)
- Code change required: none

---

## Files Changed

| File | Action |
|------|--------|
| `src/gads_pipeline/v1_runner.py` | Modified — DB path changed to `warehouse.duckdb` |
| `scripts/copy_all_to_readonly.py` | Created — copies all 5 tables |
| `tools/run_ingestion.py` | Created — orchestration script |
