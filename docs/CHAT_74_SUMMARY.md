# CHAT 74 SUMMARY: Reply Inbox Polling

**Date:** 2026-03-08
**Status:** Complete

---

## What Was Built

### 1. `act_dashboard/outreach_poller.py` — NEW
IMAP polling daemon. Every 120 seconds it:
- Connects to Gmail IMAP (`imap.gmail.com`) using credentials from `email_config.yaml`
- Searches for all UNSEEN messages in INBOX
- For each unread message, checks `email_replies.message_id` for deduplication
- Strips Re:/Fwd: prefixes and matches subject against `outreach_emails.subject WHERE status='sent'`
- On match: inserts into `email_replies`, sets `outreach_emails.reply_received=true`, sets `outreach_leads.status='replied'`
- On no match: logs warning and skips
- Does NOT mark emails as read during polling — read state managed by UI only

Schema migration runs at startup:
```sql
ALTER TABLE email_replies ADD COLUMN IF NOT EXISTS message_id VARCHAR;
ALTER TABLE email_replies ADD COLUMN IF NOT EXISTS gmail_message_uid VARCHAR;
```

### 2. `act_dashboard/routes/outreach.py` — MODIFIED
- Added `import imaplib` at top
- Added `get_imap_connection()` helper (uses `load_email_config()` from email_sender)
- Upgraded `replies_mark_read`: after DB update, also updates `email_replies.read=true` and marks as seen in Gmail via IMAP
- Added new `replies_mark_unread` route: `POST /outreach/replies/<reply_id>/mark-unread` — updates `email_replies.read=false` and marks as unseen in Gmail
- Updated replies page query to look up `reply_id` from `email_replies` per lead (needed for Mark as Unread button)

### 3. `act_dashboard/app.py` — MODIFIED
- Starts outreach poller thread after Radar thread
- Logs: `✅ [Chat 74] Outreach poller thread started (120s cycle)`
- Adds CSRF exemption for `outreach.replies_mark_unread`
- Logs: `✅ [Chat 74] CSRF exempted: outreach.replies_mark_unread`

### 4. `act_dashboard/templates/outreach/replies.html` — MODIFIED
- "Mark as Unread" button added to reply card action area
- Only visible when card is read (`!r.unread`) AND has a `reply_id` (poller-imported reply)
- On click: POSTs to `/outreach/replies/{reply_id}/mark-unread`, updates card UI to unread state
- Added `markUnread(replyId, leadId)` JS function

---

## Key Design Decisions

- **No read during polling**: The poller imports replies but never marks them as read — preserving Gmail unread state until the user explicitly opens the card
- **message_id deduplication**: Every poll cycle checks existing `message_id` values to avoid double-imports
- **IMAP failures are non-fatal**: All IMAP operations are wrapped in try/except — failures log a warning but never crash threads or routes
- **reply_id lookup is fail-safe**: The email_replies JOIN for reply_ids is wrapped in try/except — if email_replies doesn't have the expected schema, the replies page still loads

---

## Files Changed

| File | Change |
|------|--------|
| `act_dashboard/outreach_poller.py` | Created |
| `act_dashboard/routes/outreach.py` | Modified |
| `act_dashboard/app.py` | Modified |
| `act_dashboard/templates/outreach/replies.html` | Modified |
