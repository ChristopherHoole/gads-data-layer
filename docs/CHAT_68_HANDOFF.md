# Chat 68 Handoff — Live Email Sending via Gmail SMTP

**Date:** 2026-03-07
**Status:** Complete — live email sending working

---

## State of the System

The Outreach Queue page now sends **real emails** when the Send button is clicked.

### How It Works
1. User clicks "Send now" on a queue card
2. JS calls `POST /outreach/queue/<email_id>/send`
3. Route fetches subject + body from `outreach_emails`, to_email from `outreach_leads`
4. Checks daily limit (100/day)
5. Connects to smtp.gmail.com:587 via TLS
6. Logs in as chris@christopherhoole.com
7. Sends HTML email to the lead's email address
8. Updates `outreach_emails.status = 'sent'`, `outreach_leads.status = 'contacted'`
9. Returns `{success: true}` — card animates out of queue

### Daily Limit
- Set to 100 in `email_config.yaml`
- `check_daily_limit()` counts rows where `status = 'sent' AND sent_at >= CURRENT_DATE`
- If limit exceeded: HTTP 429, error toast shown in UI

---

## Key Files

| File | Purpose |
|---|---|
| `act_dashboard/secrets/email_config.yaml` | SMTP credentials — **gitignored, never commit** |
| `act_dashboard/email_sender.py` | `send_email()`, `check_daily_limit()`, etc. |
| `act_dashboard/routes/outreach.py:641` | `queue_send()` — main send route |

---

## SMTP Credentials
- Stored in: `act_dashboard/secrets/email_config.yaml`
- Gmail App Password: 16-character app password (not the account password)
- From: `Christopher Hoole <chris@christopherhoole.com>`

---

## To Run
```
cd C:\Users\User\Desktop\gads-data-layer
PYTHONUTF8=1 venv\Scripts\python.exe act_dashboard/app.py
```
Then go to http://localhost:5000/outreach/queue and click Send.

---

## What Was NOT Done (Future Work)
- CV attachment — `send_email()` supports `attachment_path` param but it's not wired to the `cv_attached` toggle yet
- Send All button — could loop through all pending queue items
- Email tracking (open/click) — would require tracking pixels and click redirects
- Reply detection — would require IMAP polling
