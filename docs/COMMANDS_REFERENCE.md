# Ads Control Tower - Quick Command Reference

**Project Location:** `C:\Users\User\Desktop\gads-data-layer`

---

## 🚀 DAILY WORKFLOW COMMANDS

### 1. Navigate to Project
```powershell
cd C:\Users\User\Desktop\gads-data-layer
```

### 2. Activate Python Virtual Environment
```powershell
.\.venv\Scripts\Activate.ps1
```

You'll see `(.venv)` appear in your prompt.

### 3. Start Docker (if needed for PostgreSQL)
```powershell
docker compose up -d
```

---

## 📊 DATA INGESTION COMMANDS

### Run Mock Mode (Fake Data - No Credentials Needed)
```powershell
python -m gads_pipeline.cli run-v1 mock .\configs\client_001.yaml --lookback-days 7
```

**When to use:** Testing without Google Ads API, offline development

### Run Test Mode (Real Google Ads API - Test Account)
```powershell
python -m gads_pipeline.cli run-v1 test .\configs\client_001.yaml --lookback-days 7
```

**When to use:** Pulling real data from test account (207-792-3976)

### Run Production Mode (NOT IMPLEMENTED YET)
```powershell
# Will be available after Basic Access approval
python -m gads_pipeline.cli run-v1 prod .\configs\client_prod.yaml --lookback-days 7
```

### Change Lookback Days
```powershell
# Last 1 day
--lookback-days 1

# Last 7 days
--lookback-days 7

# Last 30 days
--lookback-days 30
```

---

## 🔦 LIGHTHOUSE COMMANDS

### Run Lighthouse Insights
```powershell
python -m act_lighthouse.cli run-v0 configs/client_001.yaml --snapshot-date 2026-02-09
```

### Change Snapshot Date
```powershell
# Use today's date
--snapshot-date 2026-02-11

# Use yesterday
--snapshot-date 2026-02-10

# Use last week
--snapshot-date 2026-02-04
```

### Specify Number of Insights
```powershell
# Get 10 insights instead of default 5
python -m act_lighthouse.cli run-v0 configs/client_001.yaml --snapshot-date 2026-02-09 --max-insights 10
```

### Specify Database Paths
```powershell
python -m act_lighthouse.cli run-v0 configs/client_001.yaml \
  --snapshot-date 2026-02-09 \
  --build-db warehouse.duckdb \
  --readonly-db warehouse_readonly.duckdb
```

---

## 🗄️ DATABASE COMMANDS

### Refresh Readonly Database (CRITICAL - Do Before Browsing)
```powershell
.\tools\refresh_readonly.ps1
```

**IMPORTANT:** Always disconnect DBeaver first!
1. DBeaver → Right-click `warehouse_readonly.duckdb` → Disconnect
2. Run refresh script
3. Reconnect in DBeaver

### Run Health Check
```powershell
.\tools\check_health.ps1
```

**Success:** Should show `OVERALL: PASS`

### Apply Analytics Views
```powershell
python .\tools\apply_analytics.py
```

### Check Database Size
```powershell
# PowerShell
Get-ChildItem -Path . -Filter *.duckdb | Select-Object Name, @{Name="Size(MB)";Expression={[math]::Round($_.Length/1MB, 2)}}
```

---

## 🐳 DOCKER COMMANDS

### Start PostgreSQL
```powershell
docker compose up -d
```

### Stop PostgreSQL
```powershell
docker compose down
```

### View Logs
```powershell
docker compose logs postgres
```

### Check Status
```powershell
docker compose ps
```

### Restart PostgreSQL
```powershell
docker compose restart postgres
```

---

## 📦 PYTHON PACKAGE MANAGEMENT

### Install/Update Requirements
```powershell
pip install -r requirements.txt --break-system-packages
```

### Install Specific Package
```powershell
pip install google-ads==24.1.0 --break-system-packages
```

### Install Package in Editable Mode (For Development)
```powershell
pip install -e . --break-system-packages
```

### List Installed Packages
```powershell
pip list
```

### Check Python Version
```powershell
python --version
```

---

## 🔐 GOOGLE ADS API SETUP

### Generate OAuth Refresh Token
```powershell
python .\scripts\google_ads_oauth.py --client-secret secrets/google_ads_client_secret.json
```

### Test API Connection
```powershell
# Run test mode to verify credentials work
python -m gads_pipeline.cli run-v1 test .\configs\client_001.yaml --lookback-days 1
```

---

## 🗂️ GIT COMMANDS

### Check Status
```powershell
git status
```

### Add All Changes
```powershell
git add .
```

### Commit Changes
```powershell
git commit -m "Your commit message here"
```

### Push to GitHub
```powershell
git push origin main
```

### Pull Latest Changes
```powershell
git pull origin main
```

### Create New Branch
```powershell
git checkout -b feature/your-feature-name
```

### View Commit History
```powershell
git log --oneline
```

### Discard Local Changes
```powershell
# Discard changes to specific file
git checkout -- filename

# Discard ALL local changes (CAREFUL!)
git reset --hard HEAD
```

---

## 🔍 DBEAVER QUERIES

### Query Campaign Daily Data
```sql
SELECT * 
FROM analytics.campaign_daily 
WHERE snapshot_date >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY snapshot_date DESC, cost DESC
LIMIT 100;
```

### Check Latest Data Date
```sql
SELECT 
  MAX(snapshot_date) AS latest_date,
  COUNT(*) AS total_rows
FROM analytics.campaign_daily;
```

### Campaign Performance Summary
```sql
SELECT 
  campaign_name,
  SUM(impressions) AS total_impressions,
  SUM(clicks) AS total_clicks,
  SUM(cost) AS total_cost,
  SUM(conversions) AS total_conversions,
  AVG(ctr) AS avg_ctr,
  AVG(cpc) AS avg_cpc,
  AVG(roas) AS avg_roas
FROM analytics.campaign_daily
WHERE snapshot_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY campaign_name
ORDER BY total_cost DESC;
```

### Check Feature Engineering Output
```sql
SELECT 
  campaign_id,
  campaign_name,
  snapshot_date,
  clicks_w7_sum,
  cost_w7_sum,
  conversions_w7_sum,
  roas_w7_mean
FROM analytics.campaign_features_daily
WHERE snapshot_date = '2026-02-09'
ORDER BY cost_w7_sum DESC;
```

### View Lighthouse Insights
```sql
SELECT 
  rank,
  entity_type,
  entity_id,
  diagnosis_code,
  confidence,
  risk_tier,
  recommended_action
FROM analytics.lighthouse_insights_daily
WHERE snapshot_date = '2026-02-09'
ORDER BY rank;
```

---

## 🧪 TESTING COMMANDS

### Run Python Tests (When Created)
```powershell
pytest tests/
```

### Test Specific Module
```powershell
pytest tests/test_lighthouse.py
```

### Validate YAML Config
```powershell
python -c "import yaml; yaml.safe_load(open('configs/client_001.yaml'))"
```

### Check Import Works
```powershell
python -c "from act_lighthouse import cli; print('✓ Import successful')"
```

---

## 📝 COMMON FILE OPERATIONS

### View File Contents
```powershell
Get-Content filename.txt
```

### Search for Text in Files
```powershell
Select-String -Path .\src\*.py -Pattern "search_term"
```

### Count Lines of Code
```powershell
(Get-Content .\src\gads_pipeline\*.py | Measure-Object -Line).Lines
```

### Find Large Files
```powershell
Get-ChildItem -Recurse | Where-Object {$_.Length -gt 1MB} | Select-Object FullName, @{Name="Size(MB)";Expression={[math]::Round($_.Length/1MB, 2)}}
```

---

## 🚨 TROUBLESHOOTING COMMANDS

### If DBeaver Says "Database Locked"
```powershell
# 1. Disconnect in DBeaver
# 2. Close all query tabs
# 3. Wait 5 seconds
# 4. Try refresh_readonly.ps1 again
```

### If Python Module Not Found
```powershell
# Reinstall in editable mode
pip install -e . --break-system-packages
```

### If Google Ads API Error
```powershell
# Check credentials exist
Test-Path secrets/google-ads.yaml

# Regenerate refresh token
python .\scripts\google_ads_oauth.py --client-secret secrets/google_ads_client_secret.json
```

### If Docker Won't Start
```powershell
# Check Docker Desktop is running
# Restart Docker Desktop
# Try again
docker compose up -d
```

### Clear Python Cache
```powershell
# Remove all __pycache__ directories
Get-ChildItem -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force
```

---

## 📊 MONITORING COMMANDS

### Watch Live Changes to File
```powershell
Get-Content -Path "filename.log" -Wait -Tail 50
```

### Monitor Database Size
```powershell
# Run periodically to track growth
Get-ChildItem *.duckdb | Select-Object Name, @{Name="Size(MB)";Expression={[math]::Round($_.Length/1MB, 2)}}
```

---

## 🎯 QUICK START CHECKLIST

**Every morning / coding session:**

```powershell
# 1. Navigate to project
cd C:\Users\User\Desktop\gads-data-layer

# 2. Activate virtual environment
.\.venv\Scripts\Activate.ps1

# 3. Pull latest changes (if working across machines)
git pull origin main

# 4. Start Docker (if needed)
docker compose up -d

# 5. Run health check
.\tools\check_health.ps1

# 6. Pull fresh data
python -m gads_pipeline.cli run-v1 test .\configs\client_001.yaml --lookback-days 1

# 7. Refresh readonly DB
.\tools\refresh_readonly.ps1

# Ready to work!
```

---

## 💡 PRO TIPS

### PowerShell Aliases (Add to Profile)
```powershell
# Edit profile
notepad $PROFILE

# Add these aliases:
function gads-mock { python -m gads_pipeline.cli run-v1 mock .\configs\client_001.yaml --lookback-days 7 }
function gads-test { python -m gads_pipeline.cli run-v1 test .\configs\client_001.yaml --lookback-days 7 }
function gads-health { .\tools\check_health.ps1 }
function gads-refresh { .\tools\refresh_readonly.ps1 }
function gads-lighthouse { python -m act_lighthouse.cli run-v0 configs/client_001.yaml --snapshot-date (Get-Date -Format 'yyyy-MM-dd') }

# Then just type: gads-mock, gads-test, etc.
```

### Quick Date in PowerShell
```powershell
# Today's date in YYYY-MM-DD format
Get-Date -Format 'yyyy-MM-dd'

# Yesterday
(Get-Date).AddDays(-1).ToString('yyyy-MM-dd')

# 7 days ago
(Get-Date).AddDays(-7).ToString('yyyy-MM-dd')
```

---

**Quick Reference Card:**

| Action | Command |
|--------|---------|
| Activate venv | `.\.venv\Scripts\Activate.ps1` |
| Mock data | `python -m gads_pipeline.cli run-v1 mock .\configs\client_001.yaml --lookback-days 7` |
| Real data | `python -m gads_pipeline.cli run-v1 test .\configs\client_001.yaml --lookback-days 7` |
| Lighthouse | `python -m act_lighthouse.cli run-v0 configs/client_001.yaml --snapshot-date 2026-02-09` |
| Refresh DB | `.\tools\refresh_readonly.ps1` |
| Health check | `.\tools\check_health.ps1` |
| Git push | `git add . && git commit -m "msg" && git push origin main` |
| Start Docker | `docker compose up -d` |
