# tools/refresh_readonly.ps1
# Purpose:
# 1) Run the data pipeline (writes warehouse.duckdb)
# 2) Apply analytics views (analytics.campaign_daily, etc.)
# 3) Refresh warehouse_readonly.duckdb for safe DBeaver usage

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "==> Starting refresh_readonly pipeline" -ForegroundColor Cyan
Write-Host ""

# -------------------------------------------------------------------
# Resolve repo root
# -------------------------------------------------------------------
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $repoRoot
Write-Host "==> Repo root: $repoRoot" -ForegroundColor DarkGray

# -------------------------------------------------------------------
# Resolve Python executable
# -------------------------------------------------------------------
$venvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"

if (Test-Path $venvPython) {
    $pythonExe = $venvPython
    Write-Host "==> Using venv python: $pythonExe" -ForegroundColor DarkGray
} else {
    $pythonExe = "python"
    Write-Host "==> Using system python" -ForegroundColor DarkGray
}

# -------------------------------------------------------------------
# Ensure Postgres (Docker) is running
# -------------------------------------------------------------------
Write-Host ""
Write-Host "==> Ensuring Postgres is running (Docker)" -ForegroundColor Cyan

$pgContainer = docker ps --filter "name=gads_postgres" --format "{{.Names}}"
if (-not $pgContainer) {
    throw "Postgres container 'gads_postgres' is not running"
}

Write-Host "Container gads_postgres running" -ForegroundColor Green

# -------------------------------------------------------------------
# Run pipeline (writes warehouse.duckdb)
# -------------------------------------------------------------------
Write-Host ""
Write-Host "==> Running pipeline (writes to warehouse.duckdb)" -ForegroundColor Cyan

& $pythonExe ".\tools\run_pipeline.py"
if ($LASTEXITCODE -ne 0) {
    throw "run_pipeline.py failed"
}

Write-Host "SUCCESS: pipeline complete" -ForegroundColor Green

# -------------------------------------------------------------------
# Apply analytics views (analytics schema)
# -------------------------------------------------------------------
Write-Host ""
Write-Host "==> Applying analytics views to warehouse.duckdb" -ForegroundColor Cyan

& $pythonExe ".\tools\apply_analytics.py"
if ($LASTEXITCODE -ne 0) {
    throw "apply_analytics.py failed"
}

Write-Host "SUCCESS: analytics views applied" -ForegroundColor Green

# -------------------------------------------------------------------
# Refresh readonly DuckDB
# -------------------------------------------------------------------
Write-Host ""
Write-Host "==> Refreshing warehouse_readonly.duckdb" -ForegroundColor Cyan

$srcDb  = Join-Path $repoRoot "warehouse.duckdb"
$destDb = Join-Path $repoRoot "warehouse_readonly.duckdb"

if (-not (Test-Path $srcDb)) {
    throw "Source DuckDB not found: $srcDb"
}

Copy-Item -Path $srcDb -Destination $destDb -Force

Write-Host "SUCCESS: refreshed warehouse_readonly.duckdb" -ForegroundColor Green

Write-Host ""
Write-Host "==> refresh_readonly COMPLETE" -ForegroundColor Green
Write-Host ""
