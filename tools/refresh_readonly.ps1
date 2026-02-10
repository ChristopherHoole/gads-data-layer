param(
  [int]$LookbackDays = 1,
  [ValidateSet("test","live")]
  [string]$RunMode = "test",
  [string]$ClientConfig = "configs\client_001.yaml"
)

$ErrorActionPreference = "Stop"

# Repo root = parent of /tools
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..") | Select-Object -ExpandProperty Path
Write-Host "=> Repo root: $repoRoot"
Set-Location $repoRoot

# Activate venv (required)
$venvActivate = Join-Path $repoRoot ".venv\Scripts\Activate.ps1"
if (!(Test-Path $venvActivate)) {
  throw "Missing venv activation script at: $venvActivate`nCreate the venv first (see CHUNK_1 handoff)."
}
. $venvActivate
Write-Host "=> Activated venv"

# Always use venv python explicitly (avoid system Python)
$pythonExe = Join-Path $repoRoot ".venv\Scripts\python.exe"
if (!(Test-Path $pythonExe)) {
  throw "Missing venv python at: $pythonExe"
}
Write-Host "=> Using python: $pythonExe"

# Ensure Postgres is running (Docker)
try {
  $null = docker version 2>$null
  Write-Host "=> Ensuring Postgres is running (Docker)"
  try {
    docker compose up -d postgres | Out-Null
  } catch {
    # fallback if service name differs
    docker compose up -d | Out-Null
  }
  $running = docker ps --format '{{.Names}}' | Select-String -SimpleMatch "gads_postgres"
  if ($running) {
    Write-Host "Container gads_postgres Running"
  } else {
    Write-Host "NOTE: gads_postgres container not detected (check docker compose output)."
  }
} catch {
  Write-Host "NOTE: Docker not available; skipping Postgres startup."
}

# Run pipeline -> writes warehouse.duckdb
$cfgPath = Join-Path $repoRoot $ClientConfig
if (!(Test-Path $cfgPath)) {
  throw "Client config not found: $cfgPath"
}

Write-Host "=> Running pipeline ($RunMode) (writes to warehouse.duckdb)"
& $pythonExe -m gads_pipeline.cli run-v1 $RunMode $cfgPath --lookback-days $LookbackDays

# Apply analytics layer (creates analytics.campaign_daily etc)
if (Test-Path (Join-Path $repoRoot "tools\apply_analytics.py")) {
  Write-Host "=> Applying analytics views"
  & $pythonExe (Join-Path $repoRoot "tools\apply_analytics.py")
} else {
  Write-Host "NOTE: tools\apply_analytics.py not found; skipping analytics apply."
}

# Copy -> readonly DB
$src = Join-Path $repoRoot "warehouse.duckdb"
$dst = Join-Path $repoRoot "warehouse_readonly.duckdb"

if (!(Test-Path $src)) {
  throw "Source warehouse DB not found: $src"
}

Write-Host "=> Copying warehouse.duckdb -> warehouse_readonly.duckdb"
try {
  Copy-Item -Force $src $dst
} catch {
  Write-Host "!! FAILED to overwrite warehouse_readonly.duckdb (likely file is open/locked)."
  Write-Host "   Fix: Disconnect warehouse_readonly.duckdb in DBeaver and re-run this script."
  throw
}

Write-Host "DONE: refresh_readonly OK"
