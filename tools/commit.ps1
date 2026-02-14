# Interactive GitHub Commit Script
# Prompts for commit message, then commits and pushes
# Automatically excludes google-ads.yaml to prevent secret leaks

Write-Host ""
Write-Host "=== Git Commit & Push ===" -ForegroundColor Cyan
Write-Host ""

# Ensure google-ads.yaml is in .gitignore
$gitignoreContent = Get-Content .gitignore -ErrorAction SilentlyContinue
if ($gitignoreContent -notcontains "google-ads.yaml") {
    Write-Host "Adding google-ads.yaml to .gitignore..." -ForegroundColor Yellow
    Add-Content .gitignore "google-ads.yaml"
}

# Remove google-ads.yaml from staging if present
git rm --cached google-ads.yaml 2>$null

# Prompt for commit message
$message = Read-Host "Enter commit message"

if ([string]::IsNullOrWhiteSpace($message)) {
    Write-Host "Error: Commit message cannot be empty" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Committing to GitHub..." -ForegroundColor Yellow

# Add all files (google-ads.yaml already ignored)
git add .

# Commit
git commit -m $message

# Push
git push

Write-Host ""
Write-Host "Done! Changes pushed to GitHub." -ForegroundColor Green
Write-Host ""
