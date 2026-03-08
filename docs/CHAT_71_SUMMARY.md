# Chat 71 Summary — CV Upload & Attach

**Date:** 2026-03-08
**Status:** Complete — all automated checks passed; awaiting manual send test by Christopher

---

## What Was Built

Full CV file management on the Templates page and real PDF attachment on send from the Queue page.

### Files Modified

| File | Change |
|------|--------|
| `act_dashboard/routes/outreach.py` | Added 4 new routes + updated `queue_send()` |
| `act_dashboard/email_sender.py` | Fixed MIME structure for attachments |
| `act_dashboard/templates/outreach/templates.html` | Replaced placeholder CV UI |
| `act_dashboard/templates/outreach/queue.html` | Wired CV toggle to backend |
| `act_dashboard/app.py` | Added CSRF exemptions for 4 new routes |
| `act_dashboard/static/uploads/cv/` | Created directory (empty) |

---

## New Routes

| Method | URL | Function | Purpose |
|--------|-----|----------|---------|
| GET | `/outreach/cv/status` | `cv_status` | Returns filename + size_kb if CV on disk |
| POST | `/outreach/cv/upload` | `cv_upload` | Accepts PDF, saves to `static/uploads/cv/` |
| POST | `/outreach/cv/remove` | `cv_remove` | Deletes CV file, clears system_config |
| POST | `/outreach/queue/<email_id>/toggle-cv` | `queue_toggle_cv` | Toggles `cv_attached` on outreach_emails row |

---

## DB Schema

- **`system_config`** table auto-created on first request:
  ```sql
  CREATE TABLE IF NOT EXISTS system_config (key VARCHAR PRIMARY KEY, value VARCHAR)
  ```
  Stores `cv_path` = absolute path to current CV file.

- **`cv_attached BOOLEAN DEFAULT FALSE`** on `outreach_emails` — already existed in schema.

- `_ensure_cv_schema()` helper called in every new route and in `queue_send()` — idempotent, safe to call repeatedly.

---

## Email Attachment Logic

`email_sender.py::send_email()` now uses proper MIME structure:
- **With attachment**: `MIMEMultipart('mixed')` → `MIMEMultipart('alternative')` (HTML) + `MIMEBase` (PDF)
- **Without attachment**: `MIMEMultipart('alternative')` → `MIMEText` (HTML only)

`queue_send()` reads `cv_attached` from DB, looks up `cv_path` from `system_config`, and passes the path to `send_email()`. If file is missing on disk, logs a warning and sends without attachment.

---

## Templates Page CV UI

- Shows **uploaded state** (filename, size, Preview / Replace / Remove buttons) when a CV is on disk
- Shows **upload area** (click to upload) when no CV is present
- Status loaded via AJAX on `DOMContentLoaded`
- Replace uses a hidden `<input type="file">` wired to the same `uploadCV()` function

---

## Queue Page CV Toggle

- `toggleAttachment(emailId)` now POSTs to `/outreach/queue/<email_id>/toggle-cv`
- UI updates from server response (`cv_attached: true/false`)
- `cvAttached` JS map still initialised from server-rendered Jinja data for accurate initial state

---

## Testing Checklist (for Christopher to verify manually)

- [ ] Templates page shows CV section on load (either uploaded or upload area)
- [ ] Upload a PDF → filename + size appear, preview link opens PDF
- [ ] Remove → upload area reappears
- [ ] Queue card CV badge shows correct attached/not-attached state on load
- [ ] Click badge → toggle persists (refresh page and verify state)
- [ ] Send email with `cv_attached=True` → Flask log shows `attachment=True`
- [ ] Send test email to chrishoole101@gmail.com → CV arrives as PDF attachment
- [ ] Send email with `cv_attached=False` → no attachment in email
