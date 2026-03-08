# CHAT 74 HANDOFF

**Date:** 2026-03-08
**Next Chat:** 75

---

## Current State

Chat 74 is complete. The outreach reply inbox is now polled automatically.

### What's Working
- Flask starts with `✅ [Chat 74] Outreach poller thread started (120s cycle)`
- Poller logs `[POLLER] Cycle start` every 2 minutes
- `email_replies` table has `message_id` and `gmail_message_uid` columns
- `replies_mark_read` syncs read state to Gmail via IMAP
- `replies_mark_unread` route exists and syncs unread state to Gmail
- "Mark as Unread" button appears on read cards that have a poller-imported reply

### What Still Needs Manual Verification
- Christopher to open a real incoming reply on the Replies page and confirm:
  - Flask log shows `[POLLER] Marked as read in Gmail: uid=...`
  - Gmail shows the email as read
- Christopher to click "Mark as Unread" and confirm:
  - Flask log shows `[POLLER] Marked as unread in Gmail: uid=...`
  - Gmail shows the email as unread again
- Christopher to wait 2 minutes after Flask start and confirm `[POLLER] Cycle start` appears

---

## Architecture Notes

### email_replies table columns (post Chat 74)
| Column | Type | Notes |
|--------|------|-------|
| id | VARCHAR | UUID primary key |
| lead_id | VARCHAR | FK to outreach_leads |
| from_email | VARCHAR | |
| from_name | VARCHAR | |
| subject | VARCHAR | |
| body | TEXT | Plain text, HTML fallback |
| received_at | TIMESTAMP | |
| read | BOOLEAN | false on import |
| message_id | VARCHAR | RFC 2822 Message-ID header |
| gmail_message_uid | VARCHAR | IMAP UID (string) |

### Polling logic (outreach_poller.py)
- `start_poller()` — call once at startup, starts daemon thread
- `_poll_loop()` — runs forever, 120s sleep, calls `_run_poll_cycle()`
- `_run_poll_cycle()` — IMAP connect → SEARCH UNSEEN → process each UID → logout
- `_ensure_schema()` — called once at loop start, adds columns if missing

### IMAP helpers (outreach.py)
- `get_imap_connection()` — returns authenticated `imaplib.IMAP4_SSL` on INBOX
- Used by `replies_mark_read` and `replies_mark_unread`
- Credentials: `email_config.yaml` → `smtp_username` / `smtp_password`

---

## Known Limitations

- The "Mark as Unread" button only appears for replies imported by the poller (those with a `reply_id`). Manually seeded test data without an `email_replies` row won't show the button.
- The replies page view query still reads `reply_text` / `reply_read` from `outreach_emails` — not from `email_replies`. Poller-imported replies don't update `outreach_emails.reply_text`. This may be a future improvement.

---

## Suggested Next Steps (Chat 75)

- Consider migrating the replies view to read from `email_replies` directly instead of `outreach_emails.reply_text`
- Add reply body display in the slide panel for poller-imported replies
- Consider pagination or age limit on IMAP polling (currently scans all UNSEEN)
