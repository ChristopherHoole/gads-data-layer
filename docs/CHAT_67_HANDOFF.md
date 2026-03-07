# CHAT 67 HANDOFF

**Date:** 2026-03-07
**Status:** Pipeline built and tested. Blocked on developer token access level.

---

## What Works

- `tools/run_ingestion.py --mode mock` runs end-to-end cleanly
- `scripts/copy_all_to_readonly.py` copies all 5 tables correctly
- `v1_runner.py` now writes to `warehouse.duckdb` (not readonly)
- Mock summary shows matching row counts across both DBs

## Blocker: Developer Token Not Approved

Live mode fails with:
```
DEVELOPER_TOKEN_NOT_APPROVED: The developer token is only approved for
use with test accounts.
```

**Fix required (not in code):** Apply for Basic or Standard access at:
https://developers.google.com/google-ads/api/docs/access-levels

Once approved, run:
```
python tools/run_ingestion.py --customer-id 1254895944 --date 2026-03-07 --mode live
```

Expected result after approval: 0 rows for all tables (account has 2 campaigns, 0 impressions/clicks yet). Pipeline will work correctly.

---

## Next Steps for Chat 68

1. After developer token is approved, run live ingestion
2. Confirm 0-row result (correct for new account)
3. Once campaigns generate impressions, run again to see real data flow into dashboard
4. Consider adding a scheduled task (`tools/schedule_daily_ingestion.py`) to run ingestion daily

---

## Key Files

```
src/gads_pipeline/v1_runner.py         -- pull functions (writes to warehouse.duckdb)
scripts/copy_all_to_readonly.py        -- copy 5 tables to readonly DB
tools/run_ingestion.py                 -- orchestration: pull + copy + summary
secrets/google-ads.yaml                -- credentials (login_customer_id: 4434379827)
warehouse.duckdb                       -- main data warehouse
warehouse_readonly.duckdb              -- dashboard reads from here (ro.analytics.*)
```

---

## Run Commands

```powershell
# From gads-data-layer root with venv active:

# Safe test (no API calls):
python tools/run_ingestion.py --customer-id 1254895944 --date 2026-03-07 --mode mock

# Live pull (requires developer token approval):
python tools/run_ingestion.py --customer-id 1254895944 --date 2026-03-07 --mode live
```
