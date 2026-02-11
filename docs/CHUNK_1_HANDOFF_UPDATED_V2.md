# Chunk 1 Handoff (v1) — Read-Only Data Layer
*(Authoritative, numbered, newbie-friendly)*

---

## 1) Status (what is true right now)

1.1) Chunk 1 is **READ-ONLY ONLY** (no Google Ads writes).  
1.2) You have a working local data layer using:
- `warehouse.duckdb` (writable build DB)
- `warehouse_readonly.duckdb` (safe browsing DB)

1.3) You can query this canonical view in `warehouse_readonly.duckdb`:
- `analytics.campaign_daily`

---

## 2) Software list (what tools are in use)

2.1) **Windows PowerShell**  
- Used to run commands and scripts.

2.2) **Docker Desktop**  
- Used to run Postgres locally (metadata DB).

2.3) **DBeaver**  
- Used to *view* DuckDB data (you should browse `warehouse_readonly.duckdb`).

2.4) **VS Code**  
- Used to edit files and save `.md`, `.ps1`, `.py`, `.sql`.

---

## 2.5) Reality status (confirmed in your PowerShell runs)

- **Test Account mode:** ✅ Implemented + working  
  - Command: `python -m gads_pipeline.cli run-v1 test .\configs\client_001.yaml --lookback-days 1`  
  - Writes into DuckDB via the same warehouse path used by the health checks.

- **`--lookback-days`:** ✅ Implemented + working  
  - Same command as above; changing `--lookback-days N` refreshes the last **N** days.

- **Idempotency:** ✅ Implemented + working  
  - Re-running the same customer/date range does **not** create duplicates (warehouse load is idempotent).

- **Production mode (non-test accounts):** ❌ NOT implemented yet  
  - **Blocked** until your MCC gets **Basic Access** approval (API Center → Access level).  
  - Once Basic Access is approved, we’ll add a production runner + config and validate on a real customer.

---

## 3) File locations (where everything is)

3.1) Repo root folder:
- `C:\Users\User\Desktop\gads-data-layer`

3.2) The two DuckDB database files (these are in the repo root):
- `C:\Users\User\Desktop\gads-data-layer\warehouse.duckdb`
- `C:\Users\User\Desktop\gads-data-layer\warehouse_readonly.duckdb`

3.3) Documentation folder:
- `C:\Users\User\Desktop\gads-data-layer\docs\`

3.4) Tools / scripts folder:
- `C:\Users\User\Desktop\gads-data-layer\tools\`

---

## 4) Database roles (very important)

4.1) `warehouse.duckdb`  
- Purpose: pipeline writes here (build artifact)  
- Rule: **do not browse this day-to-day in DBeaver**

4.2) `warehouse_readonly.duckdb`  
- Purpose: safe browsing / querying / dashboards  
- Rule: **this is the one you browse in DBeaver**

---

## 5) Canonical query contract (ONLY approved interface)

5.1) All downstream reading (humans, dashboards, future agents) MUST use:

```sql
SELECT * FROM analytics.campaign_daily;
```

5.2) Optional filter example:

```sql
SELECT *
FROM analytics.campaign_daily
WHERE snapshot_date = CURRENT_DATE - INTERVAL '1 day';
```

5.3) Forbidden to query directly (internal implementation tables):
- `raw_*`
- `snap_*`
- `vw_*`

---

## 6) What Chunk 1 currently contains (data scope)

6.1) Implemented dataset (vertical slice):
- Campaign daily performance (mock-mode driven)

6.2) Implemented analytics view:
- `analytics.campaign_daily` includes:
  - base fields (impressions, clicks, cost_micros, conversions, etc.)
  - derived metrics: `ctr`, `cpc`, `cpm`, `roas`

6.3) Important note (production target vs local dev):
- **Target architecture** (later): BigQuery facts/snapshots + Postgres metadata  
- **Current local dev**: DuckDB acts as the warehouse for rapid iteration.

---

## 7) Readonly rules (MANDATORY)

7.1) Human browsing rule:
- Humans must connect to **warehouse_readonly.duckdb only**.

7.2) Refresh rule:
- Readonly DB is refreshed by **file copy** from `warehouse.duckdb`.

7.3) DBeaver lock rule (MANDATORY):
- Before running refresh scripts, you MUST disconnect in DBeaver:
  1) In DBeaver: right-click `warehouse_readonly.duckdb` → **Disconnect**
  2) Run PowerShell script
  3) Reconnect after the script finishes

---

## 8) Health check authority (MANDATORY)

8.1) The ONLY authoritative health check is:

```powershell
.\tools\check_health.ps1
```

8.2) When it prints:
- `OVERALL: PASS`

It means:
- the core checks passed and the data layer is considered healthy.

---

## 9) Daily run workflow (exact order, explicit)

### 9.1) Step 1 — Prepare DBeaver (disconnect readonly)
**Software: DBeaver**
1) In Database Navigator, right-click `warehouse_readonly.duckdb`
2) Click **Disconnect**

### 9.2) Step 2 — Run refresh pipeline
**Software: PowerShell**
1) Open PowerShell
2) Run:

```powershell
cd C:\Users\User\Desktop\gads-data-layer
.\tools\refresh_readonly.ps1
```

### 9.3) Step 3 — Run health check
**Software: PowerShell**
Run:

```powershell
cd C:\Users\User\Desktop\gads-data-layer
.\tools\check_health.ps1
```

### 9.4) Step 4 — Browse data
**Software: DBeaver**
1) Reconnect `warehouse_readonly.duckdb`
2) Refresh tree (F5)
3) Query:

```sql
SELECT * FROM analytics.campaign_daily LIMIT 50;
```

---

## 10) Troubleshooting (common issues + what to do)

10.1) Problem: “destination is locked” during refresh  
Fix:
1) **Software: DBeaver** → Disconnect `warehouse_readonly.duckdb`
2) Close any tabs that might be querying it
3) Re-run in **PowerShell**:

```powershell
.\tools\refresh_readonly.ps1
```

10.2) Problem: analytics view missing in readonly  
Fix (forces rebuild + copy):  
**Software: PowerShell**

```powershell
cd C:\Users\User\Desktop\gads-data-layer
.\tools\refresh_readonly.ps1
```

10.3) Problem: DBeaver tree doesn’t show analytics schema  
Fix:
1) **Software: DBeaver** → right-click the connection → **Refresh** (or press F5)
2) If still missing: Disconnect then Connect again.

---

## 11) What Chunk 1 deliberately does NOT do (scope boundary)

11.1) No Google Ads changes (no writes).  
11.2) No optimisation decisions.  
11.3) No automation of budgets/bids/keywords/ads.  
11.4) No client account access required yet (mock-mode is supported).

---

## 12) Freeze declaration (must not drift)

12.1) Chunk 1 is frozen as:
- Read-only data layer
- Canonical interface: `analytics.campaign_daily`
- Readonly browsing DB: `warehouse_readonly.duckdb`
- Health authority: `tools/check_health.ps1`

12.2) Any future change MUST be:
- versioned
- documented
- backward compatible (or explicitly migrated)

---

## 13) Remaining planned work for later chunks (not required to run Chunk 1 today)

13.1) Add additional Phase 1 core datasets (beyond campaign daily):
- ad group, keyword, search terms, ads/assets (as per constitution scope)

13.2) Add optional modules (device, geo, etc.)  
13.3) Production-mode connectivity (non-test accounts): **NOT implemented yet**
- ✅ **Test Account mode works** (developer token = *Test Account Access*).
- ❌ **Production mode is blocked** until **Basic Access** is approved in the MCC API Center.
- After Basic Access approval, we’ll add a production runner + prod client config and validate on a real customer.

13.4) BigQuery warehouse migration (target architecture)

---

## 14) Git + GitHub + secrets hygiene (added during Chunk 1)

### 14.1) Where `google-ads.yaml` should live
- ✅ **Real credentials file** goes here (local only, never committed):
  - `secrets/google-ads.yaml`
- ✅ Repo-safe template goes here (committed):
  - `configs/google-ads.example.yaml`

This keeps “client config” (`configs/client_001.yaml`, etc.) separate from “secrets”.

### 14.2) Confirm secrets are NOT committed
**Software: PowerShell** (from repo root)

```powershell
git ls-files | Select-String -Pattern "secrets|google-ads.yaml"
```

Expected: **no output** (meaning Git is not tracking your secrets file).

If anything shows up:
- remove it from tracking (does not delete the file):
```powershell
git rm --cached secrets/google-ads.yaml
git commit -m "chore: stop tracking secrets"
git push
```

### 14.3) GitHub push auth fix (what happened + why it’s OK)
You hit this error:
- `remote: Invalid username or password... Password authentication is not supported`

That’s expected (GitHub removed password auth for Git over HTTPS). Fix was:
- `gh auth login`
- `gh auth setup-git`
Then pushing works normally.

### 14.4) Line endings (CRLF/LF warnings)
You may see:
- `warning: in the working copy of 'X', LF will be replaced by CRLF...`

This is usually harmless. If you want to standardise:
- keep `.gitattributes` committed
- optionally set one of these (pick one policy and stick to it):
```powershell
# option A: keep LF in repo, convert on commit
git config --global core.autocrlf input

# option B: keep exact line endings (no conversion)
git config --global core.autocrlf false
```

---

## 15) Chunk 1 completion checklist (current status)

### 15.1) Steps 1–6 (the “finish Chunk 1” list)
1) ✅ `.gitignore` updated (Python venv, DuckDB files, env, secrets ignored)
2) ✅ `.gitattributes` added (optional but recommended)
3) ✅ Git repo initialised + committed
4) ✅ GitHub repo created + pushed to `main` using GitHub CLI auth
5) ✅ Repo documentation + templates committed:
   - `README.md`
   - `SECURITY.md`
   - `configs/google-ads.example.yaml`
6) ✅ Final verification run: `check_health.ps1` and `refresh_readonly.ps1` both run clean (PASS).
   - run health checks
   - refresh readonly DB
   - run `run-v1 test` against your test account

### 15.2) Final verification commands (PowerShell)
```powershell
cd C:\Users\User\Desktop\gads-data-layer
.\.venv\Scripts\Activate.ps1
```

```powershell
.\tools\check_health.ps1
```

```powershell
.\tools\refresh_readonly.ps1
```

```powershell
python -m gads_pipeline.cli run-v1 test .\configs\client_001.yaml --lookback-days 1
```

Success criteria:
- `check_health.ps1` shows green/OK checks
- `run-v1 test` completes without GoogleAdsException
- `warehouse_readonly.duckdb` opens in DBeaver and `analytics.campaign_daily` exists

---


---

## 16) Known Gaps / Next Milestones (Chunk 1.1 backlog)

### 16.1) Production mode (Basic Access) — checklist (short)

**Goal:** Pull from a *real* (non-test) Google Ads customer into DuckDB using the same `analytics.campaign_daily` contract.

1) In your **MCC**: `Admin → API center → Access level → Apply for Basic Access`  
2) Ensure **Developer details** are filled in and the MCC has real client accounts linked.  
3) Wait until **Access level** shows **Basic** (not “Test Account”).  
4) Implement production runner in code (new CLI mode, e.g. `run-v1 prod`), plus a `configs/client_prod.yaml`.  
5) Run first prod pull (see checklist in Section 17) and confirm rows exist.

### 16.2) Additional datasets (minimum next)

Pick **one** to implement next (both are valid):

- `analytics.search_terms_daily` (Search term / query-level reporting), or  
- `analytics.keyword_daily` (Keyword-level reporting)

Minimum contract expectation (draft):
- `customer_id`, `segments_date`, `campaign_id`, plus the entity keys for that dataset (e.g., `search_term` or `keyword_id`) and standard metrics (`clicks`, `impressions`, `cost_micros`, conversions fields).

---

## 17) Production Access checklist (step-by-step)

### 17.1) Where to request Basic Access
1) In the **MCC account** (not the client sub-account):  
   `Admin → API center → Access level → Apply for Basic Access`

### 17.2) What changes in credentials / configs
- Keep **real credentials** in: `secrets/google-ads.yaml` (ignored by git)  
- Keep a template in: `configs/google-ads.example.yaml` (safe to commit)

In `secrets/google-ads.yaml`, confirm:
- `developer_token` = your token (now Basic Access)  
- `client_id`, `client_secret`, `refresh_token` = OAuth values  
- `login_customer_id` = your MCC customer ID (digits only)

Create a prod client config (example name):
- `configs/client_prod.yaml` with the real `customer_id` (digits only, no dashes)

### 17.3) Exact command we’ll run for first prod pull (after prod mode exists)
> **Planned command for Chunk 1.1:**  
`python -m gads_pipeline.cli run-v1 prod .\configs\client_prod.yaml --lookback-days 1`

### 17.4) Proof SQL query (confirm prod pull wrote rows)
Run against `warehouse.duckdb` or `warehouse_readonly.duckdb`:

```sql
SELECT
  segments_date,
  COUNT(*) AS rows
FROM analytics.campaign_daily
WHERE customer_id = '<PROD_CUSTOMER_ID>'
  AND segments_date >= CURRENT_DATE - 1
GROUP BY 1
ORDER BY 1;
```

You should see **rows > 0** for at least one date.
