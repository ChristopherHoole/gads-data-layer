# Interactive GitHub Commit Script
# Prompts for commit message, then commits and pushes

Write-Host ""
Write-Host "=== Git Commit & Push ===" -ForegroundColor Cyan
Write-Host ""

# Prompt for commit message
$message = Read-Host "Enter commit message"

if ([string]::IsNullOrWhiteSpace($message)) {
    Write-Host "Error: Commit message cannot be empty" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Committing to GitHub..." -ForegroundColor Yellow

# Add all files
git add .

# Commit
git commit -m $message

# Push
git push

Write-Host ""
Write-Host "Done! Changes pushed to GitHub." -ForegroundColor Green
Write-Host ""