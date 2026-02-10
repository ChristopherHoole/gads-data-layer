# tools\check_health.ps1
$ErrorActionPreference = "Stop"

Write-Host "==> Entering repo root: $(Get-Location)" -ForegroundColor Cyan

# 1) Activate venv
if (Test-Path ".\.venv\Scripts\Activate.ps1") {
  Write-Host "==> Activating venv" -ForegroundColor Cyan
  . .\.venv\Scripts\Activate.ps1
} else {
  throw "Missing venv: .\.venv\Scripts\Activate.ps1"
}

# 2) Ensure Postgres is running (Docker)
Write-Host "==> Ensuring Postgres is running (Docker)" -ForegroundColor Cyan
docker compose up -d | Out-Host

# 3) Run pipeline (writes to warehouse.duckdb and Postgres metadata)
Write-Host "==> Running pipeline (mock client_001)" -ForegroundColor Cyan
python -m gads_pipeline.cli run-v1 mock .\configs\client_001.yaml

# 4) DuckDB checks
Write-Host "==> DuckDB checks (warehouse.duckdb)" -ForegroundColor Cyan
python -c @"
import duckdb
con = duckdb.connect('warehouse.duckdb', read_only=True)

tables = [t[0] for t in con.execute('SHOW TABLES').fetchall()]
need = {'raw_campaign_daily','snap_campaign_daily','snap_campaign_config','vw_campaign_daily_latest'}
missing = sorted(list(need - set(tables)))
print('tables_found:', tables)
if missing:
    raise SystemExit('FAIL: missing tables: ' + ', '.join(missing))

raw_cnt = con.execute('select count(*) from raw_campaign_daily').fetchone()[0]
snap_cnt = con.execute('select count(*) from snap_campaign_daily').fetchone()[0]
latest_cnt = con.execute('select count(*) from vw_campaign_daily_latest').fetchone()[0]
max_ingested = con.execute('select max(ingested_at) from snap_campaign_daily').fetchone()[0]

print('raw_campaign_daily:', raw_cnt)
print('snap_campaign_daily:', snap_cnt)
print('vw_campaign_daily_latest:', latest_cnt)
print('max_ingested_at:', max_ingested)

if latest_cnt <= 0:
    raise SystemExit('FAIL: vw_campaign_daily_latest has 0 rows')

print('DuckDB: PASS')
"@

# 5) Postgres validation checks (no failed rows in validation_results for the latest run)
Write-Host "==> Postgres checks (validation_results)" -ForegroundColor Cyan
python -c @"
import sqlalchemy as sa
from gads_pipeline.settings import get_settings
s = get_settings()
engine = sa.create_engine(f'postgresql+psycopg2://{s.meta_db_user}:{s.meta_db_password}@{s.meta_db_host}:{s.meta_db_port}/{s.meta_db_name}')

with engine.connect() as c:
    latest_run = c.execute(sa.text('select run_id from pipeline_runs order by created_at desc limit 1')).scalar()
    if not latest_run:
        raise SystemExit('FAIL: no pipeline_runs found')

    failed = c.execute(sa.text('select count(*) from validation_results where run_id = :rid and passed = false'), {'rid': latest_run}).scalar()
    total = c.execute(sa.text('select count(*) from validation_results where run_id = :rid'), {'rid': latest_run}).scalar()

    print('latest_run_id:', latest_run)
    print('validation_total:', total)
    print('validation_failed:', failed)

    if failed and int(failed) > 0:
        raise SystemExit('FAIL: validations failed for latest run_id')

print('Postgres validations: PASS')
print('OVERALL: PASS')
"@

Write-Host "==> DONE: OVERALL PASS" -ForegroundColor Green
