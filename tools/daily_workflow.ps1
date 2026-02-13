# Daily Workflow - Run complete pipeline
# Usage: .\tools\daily_workflow.ps1 <config_path> <snapshot_date>
# Example: .\tools\daily_workflow.ps1 configs/client_synthetic.yaml 2026-02-10

param(
    [Parameter(Mandatory=$true)]
    [string]$ConfigPath,
    
    [Parameter(Mandatory=$true)]
    [string]$SnapshotDate
)

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "DAILY WORKFLOW - $SnapshotDate" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Lighthouse
Write-Host "Step 1/2: Running Lighthouse analysis..." -ForegroundColor Yellow
Write-Host "--------------------------------------------------------------------------------"
python -m act_lighthouse.cli run-v0 $ConfigPath --snapshot-date $SnapshotDate

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Lighthouse failed" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Lighthouse complete" -ForegroundColor Green
Write-Host ""

# Step 2: Suggestions
Write-Host "Step 2/2: Generating recommendations..." -ForegroundColor Yellow
Write-Host "--------------------------------------------------------------------------------"
python -m act_autopilot.suggest_engine $ConfigPath $SnapshotDate

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Suggestions failed" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "WORKFLOW COMPLETE" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  Review: python -m act_autopilot.approval_cli reports/suggestions/Synthetic_Test_Client/$SnapshotDate.json"
Write-Host ""