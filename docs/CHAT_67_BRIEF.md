# CHAT 67 BRIEF — Real Data Ingestion Pipeline

**Date:** 2026-03-07
**Objective:** Fix the data pipeline so real Google Ads data from account `1254895944` flows into the dashboard.

---

## CONTEXT

The dashboard reads from `ro.analytics.*` tables in `warehouse_readonly.duckdb`.
The pipeline (`v1_runner.py`) already has complete live API pull functions for all 5 entity types.

**Current problem:**
- `v1_runner.py` writes directly to `warehouse_readonly.duckdb` — it should write to `warehouse.duckdb` first
- `copy_to_readonly.py` only copies `ad_daily` — it is a one-off workaround, not a full pipeline
- No orchestration script exists to run pull + copy in a single command

---

## TASKS

### Task 1 — Fix `src/gads_pipeline/v1_runner.py`

In `main()`, change the DB connection from `warehouse_readonly.duckdb` to `warehouse.duckdb`.

Current (wrong):
```python
db_path = Path('warehouse_readonly.duckdb')
```

Correct:
```python
db_path = Path('warehouse.duckdb')
```

All 5 pull functions write to `analytics.*` tables. Table names do not change — only the target database changes.

Must also create the `analytics` schema if it does not exist (already done in current code — keep it).

---

### Task 2 — Create `scripts/copy_all_to_readonly.py`

New script that copies all 5 analytics tables from `warehouse.duckdb` → `warehouse_readonly.duckdb`.

Tables to copy:
- `analytics.campaign_daily`
- `analytics.keyword_daily`
- `analytics.search_term_daily`
- `analytics.ad_group_daily`
- `analytics.ad_daily`

Pattern per table (same as existing `copy_to_readonly.py`):
1. Read all rows from `warehouse.duckdb`
2. Connect to `warehouse_readonly.duckdb`
3. `DROP TABLE IF EXISTS analytics.<table>`
4. `CREATE TABLE analytics.<table>` with correct schema
5. `INSERT` all rows
6. Print row count confirmation

Script must be run from `C:\Users\User\Desktop\gads-data-layer`.

Get the correct CREATE TABLE schema for each table from `v1_runner.py` — the schemas are already defined there in each pull function.

---

### Task 3 — Create `tools/run_ingestion.py`

Single orchestration script. Runs pull + copy in one command.

Usage:
```
python tools/run_ingestion.py --customer-id 1254895944 --date 2026-03-07 --mode live
```

Steps:
1. Import and call all 5 pull functions from `v1_runner.py` (campaign, keyword, search_term, ad_group, ad)
2. Call `copy_all_to_readonly.py` logic (import as module or subprocess)
3. Print a summary table of row counts per table in both databases

Must support `--mode mock` for safe testing without API calls.

Must be run from `C:\Users\User\Desktop\gads-data-layer` with venv active.

Credentials are in `act_dashboard/secrets/google-ads.yaml` — do not modify, do not commit.

---

### Task 4 — Test live

Run:
```powershell
python tools/run_ingestion.py --customer-id 1254895944 --date 2026-03-07 --mode live
```

Account `1254895944` has 2 campaigns but 0 impressions/clicks yet.

**Expected result:** No errors. API connection confirmed. Row counts print as 0 for all tables (correct — no data yet).

If any API authentication error occurs, check `act_dashboard/secrets/google-ads.yaml` is present and `login_customer_id` is set to `4434379827`.

---

## FILES

**Modify:**
- `C:\Users\User\Desktop\gads-data-layer\src\gads_pipeline\v1_runner.py`

**Create:**
- `C:\Users\User\Desktop\gads-data-layer\scripts\copy_all_to_readonly.py`
- `C:\Users\User\Desktop\gads-data-layer\tools\run_ingestion.py`

**Do not touch:**
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\secrets\google-ads.yaml`
- `C:\Users\User\Desktop\gads-data-layer\warehouse_readonly.duckdb` (only `copy_all_to_readonly.py` writes to this)

---

## DELIVERABLES

1. Modified `v1_runner.py`
2. New `copy_all_to_readonly.py`
3. New `run_ingestion.py`
4. Successful test run output (pasted into handoff)
5. `CHAT_67_SUMMARY.md` saved to `docs/`
6. `CHAT_67_HANDOFF.md` saved to `docs/`
7. Git commit with message: `Chat 67: Real data ingestion pipeline`

---

## RUN COMMANDS (for Claude Code)

Always start fresh:
```powershell
taskkill /IM python.exe /F
cd C:\Users\User\Desktop\gads-data-layer
.\.venv\Scripts\Activate.ps1
```

Test mock first:
```powershell
python tools/run_ingestion.py --customer-id 1254895944 --date 2026-03-07 --mode mock
```

Then live:
```powershell
python tools/run_ingestion.py --customer-id 1254895944 --date 2026-03-07 --mode live
```
