# CHAT 68 BRIEF — Live Email Sending via Gmail SMTP

**Date:** 2026-03-07
**Objective:** Wire up the Outreach Queue page to send real emails via Gmail SMTP using chris@christopherhoole.com

---

## CRITICAL INSTRUCTION — NO PLACEHOLDERS

**Christopher does not replace placeholders. Every credential must be hardcoded directly into the config/code exactly as shown below. Do not use placeholders like `YOUR_PASSWORD_HERE`. Use the actual values provided.**

---

## SMTP CREDENTIALS

These are real, working credentials. Use them exactly as shown:

- **SMTP server:** `smtp.gmail.com`
- **Port:** `587`
- **Username:** `chris@christopherhoole.com`
- **App password:** `iflslbdfppfoehqz` (spaces removed — 16 characters)

These go into `act_dashboard/secrets/email_config.yaml` (new file — see Task 1).

---

## CONTEXT

The Outreach system has a Queue page (`/outreach/queue`) where emails are scheduled and ready to send. Currently the Send button shows a placeholder toast — no actual email is sent.

The `sent_emails` table exists in `warehouse.duckdb` and already tracks sent emails.
The `email_queue` table exists and holds emails with status `pending`.
Email templates are in the `email_templates` table with variable substitution support (`{{first_name}}`, `{{company}}`, etc.)

---

## TASKS

### Task 1 — Create `act_dashboard/secrets/email_config.yaml`

New file. Content must be exactly:

```yaml
smtp_host: smtp.gmail.com
smtp_port: 587
smtp_username: chris@christopherhoole.com
smtp_password: iflslbdfppfoehqz
from_name: Christopher Hoole
from_email: chris@christopherhoole.com
daily_limit: 100
```

Add `email_config.yaml` to `.gitignore` immediately — same pattern as `google-ads.yaml` and `google-credentials.json`.

---

### Task 2 — Create `act_dashboard/email_sender.py`

New module. Handles all email sending logic.

Functions needed:

**`load_email_config()`**
- Reads `act_dashboard/secrets/email_config.yaml`
- Returns config dict
- Path resolution: `Path(__file__).parent / "secrets" / "email_config.yaml"`

**`send_email(to_email, subject, body_html, from_name=None, from_email=None, attachment_path=None)`**
- Connects to Gmail SMTP via TLS (port 587)
- Sends HTML email
- Supports optional file attachment (for CV later)
- Returns `{'success': True}` or `{'success': False, 'error': str}`
- Logs success/failure with print statements

**`substitute_variables(template_body, lead_dict)`**
- Replaces `{{first_name}}`, `{{company}}`, `{{role}}`, `{{track}}` etc. with actual lead values
- Returns substituted string

**`check_daily_limit(conn)`**
- Counts emails sent today from `sent_emails` table
- Returns `{'limit': 100, 'sent_today': N, 'remaining': 100-N}`

---

### Task 3 — Create `act_dashboard/routes/outreach_send.py`

New blueprint. Route: `POST /outreach/send-email`

Logic:
1. Get `queue_id` from request JSON
2. Load queue item from `email_queue` table
3. Check daily limit — if exceeded, return error
4. Load lead details from `leads` table
5. Load template from `email_templates` table
6. Substitute variables in subject + body
7. Call `send_email()` from email_sender.py
8. On success:
   - Update `email_queue` status to `sent`, set `sent_at = now()`
   - Insert row into `sent_emails` table
   - Write to `changes` audit table: `executed_by = 'user_send'`
9. Return JSON `{'success': True, 'message': 'Email sent'}` or error

Register blueprint in `act_dashboard/routes/__init__.py` and add CSRF exemption in `act_dashboard/app.py`.

---

### Task 4 — Update Queue page to call real send endpoint

File: `act_dashboard/templates/outreach/queue.html`

Find the existing Send button JavaScript. Currently it shows a toast placeholder. 

Replace with a real `fetch()` call to `POST /outreach/send-email` with `{'queue_id': id}`.

On success: update the row status in the UI to "Sent", show success toast.
On error: show error toast with the error message.

Also wire up a **Send All** button (if it exists) to loop through all pending queue items and send them sequentially with a 2-second delay between each to avoid rate limiting.

---

### Task 5 — Test

Send a real test email to `chrishoole101@gmail.com` from the Queue page.

Steps:
1. Start Flask fresh
2. Go to http://localhost:5000/outreach/queue in Opera
3. Click Send on one queue item
4. Confirm the email arrives in chrishoole101@gmail.com inbox
5. Confirm the queue item status updates to Sent
6. Check `sent_emails` table has a new row

Paste the test result in the handoff document.

---

## FILES

**Create:**
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\secrets\email_config.yaml`
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\email_sender.py`
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\outreach_send.py`

**Modify:**
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\outreach\queue.html`
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\__init__.py`
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\app.py`
- `C:\Users\User\Desktop\gads-data-layer\.gitignore`

**Do not touch:**
- `act_dashboard/secrets/google-ads.yaml`
- Any existing outreach templates or routes unrelated to sending

---

## RUN COMMANDS (for Claude Code)

Always start fresh:
```powershell
taskkill /IM python.exe /F
cd C:\Users\User\Desktop\gads-data-layer
.\.venv\Scripts\Activate.ps1
python act_dashboard/app.py
```

Test at http://localhost:5000/outreach/queue in Opera.

---

## DELIVERABLES

1. `email_config.yaml` with real credentials
2. `email_sender.py` working module
3. `outreach_send.py` route
4. Updated `queue.html` with real send functionality
5. Confirmed test email received in chrishoole101@gmail.com
6. `CHAT_68_SUMMARY.md` saved to `docs/`
7. `CHAT_68_HANDOFF.md` saved to `docs/`
8. Git commit: `Chat 68: Live email sending via Gmail SMTP`

**Note:** `email_config.yaml` must NOT be included in the git commit — it must be in `.gitignore` before committing.
