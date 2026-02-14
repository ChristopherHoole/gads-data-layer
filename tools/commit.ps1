# Simple GitHub Commit Script
# Commits all changes and pushes to GitHub

Write-Host "Committing to GitHub..." -ForegroundColor Cyan

# Add all files
git add .

# Commit with message
git commit -m "feat: Chat 7 complete - Web dashboard MVP

- Flask web interface for non-technical users
- Login page (admin/admin123)
- Dashboard home (stats, charts, recent activity)
- Recommendations page (approve/reject with color-coded risk)
- Change History page (filter/search)
- Settings page (edit client config via form)
- Responsive design (desktop/tablet/mobile)
- Real-time data from DuckDB
- 11 files total (5 Python, 6 HTML templates, 1 launch script)"

# Push to GitHub
git push

Write-Host ""
Write-Host "Done! Changes pushed to GitHub." -ForegroundColor Green
