# Interactive GitHub Commit Script
# Prompts for commit message, then commits and pushes
# Automatically excludes secret files to prevent leaks

Write-Host ""
Write-Host "=== Git Commit & Push ===" -ForegroundColor Cyan
Write-Host ""

# Secret files that must never be committed
$secrets = @(
    "google-ads.yaml",
    "google-credentials.json",
    "act_dashboard/secrets/google-credentials.json",
    "act_dashboard/secrets/email_config.yaml"
)

# Ensure each secret is in .gitignore and removed from staging
foreach ($secret in $secrets) {
    $gitignoreContent = Get-Content .gitignore -Raw -ErrorAction SilentlyContinue
    $basename = Split-Path $secret -Leaf
    if ($gitignoreContent -notmatch [regex]::Escape($basename)) {
        Write-Host "Adding $basename to .gitignore..." -ForegroundColor Yellow
        Add-Content .gitignore "`n$basename"
    }
    git rm --cached $secret 2>$null
}

# Prompt for commit message
$message = Read-Host "Enter commit message"

if ([string]::IsNullOrWhiteSpace($message)) {
    Write-Host "Error: Commit message cannot be empty" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Committing to GitHub..." -ForegroundColor Yellow

# Add all files (secrets already ignored/unstaged)
git add .

# Safety check: abort if any secret file is staged
$staged = git diff --cached --name-only
foreach ($secret in $secrets) {
    if ($staged -contains $secret) {
        Write-Host "ERROR: $secret is staged — aborting to protect secrets!" -ForegroundColor Red
        git reset HEAD $secret 2>$null
        exit 1
    }
}

# Commit
git commit -m $message

# Push
git push

Write-Host ""
Write-Host "Done! Changes pushed to GitHub." -ForegroundColor Green
Write-Host ""
