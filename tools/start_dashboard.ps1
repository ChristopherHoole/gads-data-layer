# Ads Control Tower - Dashboard Launcher
# Starts the Flask web interface

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "ADS CONTROL TOWER - Dashboard Launcher" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment is activated
if (-not $env:VIRTUAL_ENV) {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & .\.venv\Scripts\Activate.ps1
}

# Check if Flask is installed
Write-Host "Checking Flask installation..." -ForegroundColor Cyan
try {
    python -c "import flask" 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Flask not found"
    }
    Write-Host "Flask installed" -ForegroundColor Green
} catch {
    Write-Host "Flask not installed" -ForegroundColor Red
    Write-Host ""
    Write-Host "Installing Flask..." -ForegroundColor Yellow
    pip install flask --break-system-packages
    Write-Host ""
}

# Get config path (default to synthetic client)
$ConfigPath = "configs/client_synthetic.yaml"
if ($args.Count -gt 0) {
    $ConfigPath = $args[0]
}

Write-Host ""
Write-Host "Starting dashboard..." -ForegroundColor Cyan
Write-Host "Config: $ConfigPath" -ForegroundColor Gray
Write-Host ""
Write-Host "Dashboard will open at: http://localhost:5000" -ForegroundColor Green
Write-Host ""
Write-Host "Login credentials:" -ForegroundColor Yellow
Write-Host "  Username: admin" -ForegroundColor White
Write-Host "  Password: admin123" -ForegroundColor White
Write-Host ""
Write-Host "Press CTRL+C to stop the dashboard" -ForegroundColor Gray
Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Run Flask app
python -m act_dashboard.app $ConfigPath
