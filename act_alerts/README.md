# Email Alerts Module

Automated email notifications for Ads Control Tower.

## Features

- **Daily Summary Emails**: Account performance, pending recommendations, recent changes
- **Rollback Alerts**: Automatic notifications when changes are rolled back
- **Performance Alerts**: Threshold breach notifications

## Installation

```powershell
# Install dependencies
pip install jinja2
```

## Configuration

Add email_alerts section to your client config:

```yaml
# configs/client_name.yaml

email_alerts:
  enabled: true
  smtp_host: smtp.gmail.com
  smtp_port: 587
  smtp_user: your-email@gmail.com
  smtp_password: your-app-password  # Gmail App Password
  recipient: client@example.com
  daily_summary_time: "08:00"  # When to send daily emails
```

### Gmail App Password Setup

1. Go to Google Account settings
2. Security → 2-Step Verification
3. App passwords → Generate new
4. Select "Mail" and "Other" (Ads Control Tower)
5. Copy generated password to config

## Usage

### Send Daily Summary

```powershell
# Send for yesterday
python -m act_alerts.cli send-daily-summary configs/client_synthetic.yaml

# Send for specific date
python -m act_alerts.cli send-daily-summary configs/client_synthetic.yaml --date 2026-02-14
```

### Send Test Emails

```powershell
# Test rollback alert
python -m act_alerts.cli send-test-rollback configs/client_synthetic.yaml

# Test performance alert
python -m act_alerts.cli send-test-performance configs/client_synthetic.yaml
```

### Programmatic Usage

```python
from act_alerts import send_daily_summary, send_rollback_alert, send_performance_alert
from datetime import date

# Load config
import yaml
with open('configs/client_name.yaml') as f:
    config = yaml.safe_load(f)

# Send daily summary
send_daily_summary(
    config=config,
    customer_id='1234567890',
    snapshot_date=date(2026, 2, 14),
    dashboard_url='https://your-dashboard.com'
)
```

## Email Types

### 1. Daily Summary
- **When**: Scheduled (e.g., 8am daily)
- **To**: Client
- **Contains**:
  - Yesterday's spend, conversions, ROAS
  - Pending recommendations count
  - Recent changes (last 7 days)
  - Link to dashboard

### 2. Rollback Alert
- **When**: Radar triggers rollback
- **To**: Admin + Client
- **Contains**:
  - Campaign details
  - What was rolled back
  - Why (performance regression)
  - Before/after metrics
  - Link to change history

### 3. Performance Alert
- **When**: KPI breaches threshold
- **To**: Admin + Client
- **Contains**:
  - Which metric (CPA, ROAS, etc.)
  - Threshold vs current value
  - Recommended action
  - Link to dashboard

## Scheduling

### Windows Task Scheduler

Create scheduled task:

```powershell
# Daily summary at 8am
$action = New-ScheduledTaskAction -Execute 'python' -Argument '-m act_alerts.cli send-daily-summary configs/client_name.yaml'
$trigger = New-ScheduledTaskTrigger -Daily -At 8am
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "Ads Control Tower - Daily Summary"
```

### Linux Cron

```bash
# Add to crontab
0 8 * * * cd /path/to/gads-data-layer && python -m act_alerts.cli send-daily-summary configs/client_name.yaml
```

## Troubleshooting

### Email Not Sending

1. **Check SMTP credentials**: Verify username/password correct
2. **Check Gmail App Password**: Regular password won't work, must use app password
3. **Check logs**: Look for error messages
4. **Test SMTP connection**:

```python
import smtplib
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login('your-email@gmail.com', 'your-app-password')
print("✅ SMTP connection successful")
server.quit()
```

### Emails in Spam

1. Add sender to contacts
2. Mark as "Not spam"
3. Consider using custom domain email instead of Gmail

### Template Not Found

- Ensure templates/ folder exists in act_alerts/
- Verify template files exist: daily_summary.html, rollback_alert.html, performance_alert.html

## File Structure

```
act_alerts/
├── __init__.py
├── email_sender.py       # Core email sending logic
├── cli.py                # Command-line interface
├── README.md             # This file
└── templates/
    ├── daily_summary.html
    ├── rollback_alert.html
    └── performance_alert.html
```

## Security Notes

- **Never commit SMTP passwords**: Keep configs private
- **Use app passwords**: Don't use main Gmail password
- **Rotate passwords**: Change app passwords periodically
- **Restrict access**: Only authorized users should have config access
