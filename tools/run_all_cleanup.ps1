# Complete Code Cleanup Script
# Runs all cleanup steps in sequence

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "ADS CONTROL TOWER - CODE CLEANUP (Part 5)" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Install tools
Write-Host "Step 1: Installing cleanup tools..." -ForegroundColor Yellow
pip install black autoflake --quiet
Write-Host "✅ Tools installed" -ForegroundColor Green
Write-Host ""

# Step 2: Run Black formatter
Write-Host "Step 2: Running Black formatter..." -ForegroundColor Yellow
black act_autopilot/ act_dashboard/ act_alerts/ tools/ scripts/ --quiet
Write-Host "✅ Code formatted" -ForegroundColor Green
Write-Host ""

# Step 3: Clean code
Write-Host "Step 3: Cleaning code (removing debug prints, whitespace)..." -ForegroundColor Yellow
python tools/cleanup_code.py act_autopilot --apply
python tools/cleanup_code.py act_dashboard --apply
python tools/cleanup_code.py act_alerts --apply
Write-Host "✅ Code cleaned" -ForegroundColor Green
Write-Host ""

# Step 4: Remove unused imports
Write-Host "Step 4: Removing unused imports..." -ForegroundColor Yellow
autoflake --in-place --remove-all-unused-imports -r act_autopilot/ 2>$null
autoflake --in-place --remove-all-unused-imports -r act_dashboard/ 2>$null
autoflake --in-place --remove-all-unused-imports -r act_alerts/ 2>$null
Write-Host "✅ Unused imports removed" -ForegroundColor Green
Write-Host ""

# Step 5: Update requirements.txt
Write-Host "Step 5: Updating requirements.txt..." -ForegroundColor Yellow
python tools/update_requirements.py
Write-Host "✅ Requirements updated" -ForegroundColor Green
Write-Host ""

# Step 6: Final format
Write-Host "Step 6: Final Black formatting..." -ForegroundColor Yellow
black . --quiet
Write-Host "✅ Final formatting complete" -ForegroundColor Green
Write-Host ""

# Step 7: Verify
Write-Host "Step 7: Verifying imports..." -ForegroundColor Yellow
python -c "import act_autopilot; import act_dashboard; import act_alerts; print('✅ All imports working')"
Write-Host ""

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "CODE CLEANUP COMPLETE!" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Review changes: git diff" -ForegroundColor White
Write-Host "  2. Commit to GitHub: .\tools\commit.ps1" -ForegroundColor White
Write-Host ""
