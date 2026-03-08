# CHAT 74: REPLY INBOX POLLING

**Date:** 2026-03-08
**Estimated Time:** 4–5 hours
**Priority:** HIGH
**Dependencies:** Chat 73 complete

---

## CONTEXT & APPROACH

Chat 73 completed open/click tracking. The Replies page currently only shows manually seeded test data — no real inbound replies are ever imported. This chat builds a background IMAP polling daemon that checks `chris@christopherhoole.com` every 2 minutes, imports replies into `email_replies`, and syncs read/unread state back to Gmail.

Build order:
1. DB schema: add `message_id` + `gmail_message_uid` columns to `email_replies`
2. Create `act_dashboard/outreach_poller.py` — IMAP polling daemon
3. Modify `replies_mark_read` route — add IMAP mark-as-seen
4. Add new `replies_mark_unread` route — DB + IMAP unread
5. Add "Mark as Unread" button to `replies.html`
6. Start poller thread in `app.py`
7. CSRF exemption for new route in `app.py`

---

## OBJECTIVE

Poll `chris@christopherhoole.com` inbox every 2 minutes via IMAP, auto-import replies into ACT, and sync read/unread state back to Gmail.

---

## DELIVERABLES

1. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\outreach_poller.py` — CREATE
   - IMAP polling daemon (see Requirements)

2. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\outreach.py` — MODIFY
   - Upgrade `replies_mark_read` to also mark as read in Gmail via IMAP
   - Add new `replies_mark_unread` route
   - Add `get_imap_connection()` helper used by both routes

3. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\app.py` — MODIFY
   - Import and start poller thread (same pattern as Radar)
   - Add CSRF exemption for `outreach.replies_mark_unread`
   - Label: `✅ [Chat 74] CSRF exempted: outreach.replies_mark_unread`
   - Label: `✅ [Chat 74] Started outreach poller thread (2min cycle)`

4. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\outreach\replies.html` — MODIFY
   - Add "Mark as Unread" button to reply card (visible when reply is read)

5. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_74_HANDOFF.md` — CREATE
6. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_74_SUMMARY.md` — CREATE

---

## REQUIREMENTS

### DB Schema Migration
Run at startup in `outreach_poller.py` (before polling loop):
```sql
ALTER TABLE email_replies ADD COLUMN IF NOT EXISTS message_id VARCHAR;
ALTER TABLE email_replies ADD COLUMN IF NOT EXISTS gmail_message_uid VARCHAR;
```

### outreach_poller.py — Polling Daemon

```python
def start_poller():
    thread = threading.Thread(target=_poll_loop, daemon=True)
    thread.start()
```

`_poll_loop()`:
- Runs forever, sleeps 120 seconds between cycles
- Calls `_run_poll_cycle()` wrapped in try/except — never crashes the thread
- Logs: `[POLLER] Cycle start` and `[POLLER] Cycle complete — {n} new replies imported`

`_run_poll_cycle()`:
- Load IMAP credentials from `email_config.yaml` (same file as SMTP):
  - `smtp_username` → IMAP username
  - `smtp_password` → App Password
- Connect: `imaplib.IMAP4_SSL('imap.gmail.com')`
- Login, select `INBOX`
- Search for ALL unread messages: `SEARCH UNSEEN`
- For each UID:
  - Fetch headers: `Message-ID`, `Subject`, `From`, `Date`
  - Fetch body (plain text preferred, HTML fallback)
  - Check `email_replies` — skip if `message_id` already exists
  - Strip `Re:`, `Fwd:`, `Re: Re:` prefixes from subject (recursive strip)
  - Match cleaned subject against `outreach_emails.subject` WHERE `status='sent'`
  - If match found:
    - Insert into `email_replies`: `id=uuid4()`, `lead_id`, `from_email`, `from_name`, `subject`, `body`, `received_at`, `read=false`, `message_id`, `gmail_message_uid=str(uid)`
    - UPDATE `outreach_emails` SET `reply_received=true`, `replied_at=now()` WHERE matched id
    - UPDATE `outreach_leads` SET `status='replied'` WHERE matched lead_id
    - Log: `[POLLER] New reply from {from_email} — imported (lead_id={lead_id})`
  - If no match:
    - Log: `[POLLER] Unmatched reply subject: "{subject}" — skipped`
- Logout, close connection

**Important:** Do NOT mark emails as read during polling. Read state is managed by `replies_mark_read` only.

### get_imap_connection() Helper in outreach.py
```python
def get_imap_connection():
    config = load_email_config()
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(config['smtp_username'], config['smtp_password'])
    mail.select('INBOX')
    return mail
```

### replies_mark_read Upgrade
After setting `read=true` in DB, also:
- Get `gmail_message_uid` from `email_replies` row
- If `gmail_message_uid` is not None:
  - Call `get_imap_connection()`
  - `mail.uid('STORE', gmail_message_uid, '+FLAGS', '\\Seen')`
  - `mail.logout()`
  - Log: `[POLLER] Marked as read in Gmail: uid={gmail_message_uid}`
- If IMAP fails: log warning, do not fail the route response

### replies_mark_unread Route (NEW)
```
POST /outreach/replies/<reply_id>/mark-unread
```
- Get `gmail_message_uid` from `email_replies` WHERE `id=reply_id`
- UPDATE `email_replies` SET `read=false` WHERE `id=reply_id`
- If `gmail_message_uid` is not None:
  - Call `get_imap_connection()`
  - `mail.uid('STORE', gmail_message_uid, '-FLAGS', '\\Seen')`
  - `mail.logout()`
  - Log: `[POLLER] Marked as unread in Gmail: uid={gmail_message_uid}`
- Return `{"success": true}`
- If IMAP fails: log warning, still return success (DB update succeeded)

### replies.html — Mark as Unread Button
- Add a "Mark as Unread" button inside the reply card action area
- Only visible when `reply.read == true`
- On click: POST to `/outreach/replies/{reply_id}/mark-unread` via fetch
- On success: update card UI to show unread state (remove read styling)
- Small, secondary button — not prominent

### app.py — Start Poller
Add after Radar thread start:
```python
from act_dashboard.outreach_poller import start_poller
start_poller()
```
Log: `✅ [Chat 74] Outreach poller thread started (120s cycle)`

### Constraints
- 🚨 Deselect worktree — all work on main branch
- 🚨 Do NOT send test emails
- IMAP failures must never crash the poller thread or any route — always try/except with log warning
- `message_id` deduplication prevents double-importing on every poll cycle
- Poller only runs one thread — no concurrent poll cycles
- `email_config.yaml` already has all needed credentials — no new config keys needed

---

## SUCCESS CRITERIA

- [ ] Flask starts cleanly with `✅ [Chat 74] Outreach poller thread started`
- [ ] Poller log shows `[POLLER] Cycle start` within 2 minutes of Flask start
- [ ] `GET /outreach/replies` shows test reply card
- [ ] Clicking reply card auto-marks as read — Flask log shows `[POLLER] Marked as read in Gmail`
- [ ] "Mark as Unread" button visible on read reply card
- [ ] Clicking "Mark as Unread" — Flask log shows `[POLLER] Marked as unread in Gmail`
- [ ] `email_replies` table has `message_id` and `gmail_message_uid` columns
- [ ] No console errors, no Flask errors

Christopher will verify Gmail read/unread state manually after testing.

---

## REFERENCE FILES

- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\outreach.py` — `replies_mark_read` route + `load_email_config()`
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\outreach\replies.html` — reply card structure
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\app.py` — Radar thread start pattern
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\secrets\email_config.yaml` — IMAP credentials (same as SMTP)

---

## TESTING (Claude Code — no email sends)

1. Confirm `email_replies` has `message_id` and `gmail_message_uid` columns
2. Confirm `outreach_poller.py` exists with `start_poller()` and `_poll_loop()`
3. Confirm `replies_mark_unread` route exists in `outreach.py`
4. Confirm CSRF exemption in `app.py`
5. Start Flask — confirm `[Chat 74] Outreach poller thread started` in log
6. Wait up to 2 minutes — confirm `[POLLER] Cycle start` appears in log
7. Report any IMAP errors seen during first cycle
8. Christopher verifies read/unread sync in Opera + Gmail manually
