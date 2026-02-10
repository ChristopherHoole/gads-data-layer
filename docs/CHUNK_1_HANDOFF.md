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
13.3) Add real Google Ads API connectivity:
- test account mode
- production mode (small live account)
13.4) BigQuery warehouse migration (target architecture)

---
