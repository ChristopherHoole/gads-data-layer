# CHAT 72: SEND REPLY

**Date:** 2026-03-08
**Estimated Time:** 2–3 hours
**Priority:** HIGH
**Dependencies:** Chat 71 complete

---

## 🚨 BEFORE STARTING
- **Deselect worktree** in Claude Code session options — all work must be done directly on main branch
- Do NOT create any branches or worktrees
- Do NOT send any test emails — all email testing is done manually by Christopher
- Confirm you are on main branch before touching any files

---

## CONTEXT & APPROACH

The Replies page shows inbound reply cards from prospects stored in `email_replies`. The "Send Reply" button currently fires a "Coming soon" toast. This chat wires it up to send a real email via the existing `email_sender.py` SMTP module.

**Approach:**
- New route `POST /outreach/replies/<reply_id>/send-reply` handles the send
- Fetches reply from `email_replies` to get lead_id and original subject
- Fetches lead from `outreach_leads` to get email address and name for variable substitution
- Sends via `send_email()` with signature appended, no CV attachment
- Saves outbound reply as new row in `outreach_emails` with `direction='outbound_reply'`
- Updates lead status to 'in_conversation' in `outreach_leads`
- Frontend: inline compose area (textarea + Send + Cancel) replaces the "Coming soon" toast
- No new modal needed — compose area opens inline below the reply card

---

## OBJECTIVE

Wire up the "Send Reply" button on the Replies page to send a real email via SMTP, save it to the database, and update the lead status.

---

## DELIVERABLES

1. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\outreach.py` — MODIFY
   - Add `POST /outreach/replies/<reply_id>/send-reply` route
   - Fetches `email_replies` row by `reply_id` to get `lead_id` and original subject
   - Fetches `outreach_leads` row by `lead_id` to get recipient email + first_name
   - Builds subject: strip any existing "Re:" prefix, prepend single "Re:"
   - Calls `substitute_variables(body, lead_data)` on the body
   - Appends signature via `get_signature_html()`
   - Calls `send_email(to_email, subject, body_html)` — no attachment_path
   - On success: INSERT into `outreach_emails` (status='sent', direction='outbound_reply', lead_id, subject, body, sent_at=now())
   - On success: UPDATE `outreach_leads` SET status='in_conversation' WHERE id=lead_id
   - Returns `{success: true}` or `{success: false, error: '...'}`

2. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\outreach.py` — MODIFY `replies_send_reply()`
   - This function currently exists but fires "Coming soon" — replace entirely with real implementation above

3. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\outreach\replies.html` — MODIFY
   - Replace "Coming soon" toast trigger on Send Reply button
   - Add inline compose area below each reply card: textarea (min 6 rows, full width), Send button (primary), Cancel button
   - Compose area hidden by default — shown when Send Reply clicked
   - On successful send: show success toast "Reply sent", collapse compose area, update lead status badge if visible
   - On error: show error toast with message
   - Cancel button collapses compose area without sending

4. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\app.py` — MODIFY
   - `outreach.replies_send_reply` is already CSRF exempted (Chat 62) — verify it's there, do not duplicate

5. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_72_HANDOFF.md` — CREATE
6. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_72_SUMMARY.md` — CREATE

---

## REQUIREMENTS

### Database
- Add `direction VARCHAR DEFAULT 'outbound'` column to `outreach_emails`:
  `ALTER TABLE outreach_emails ADD COLUMN IF NOT EXISTS direction VARCHAR DEFAULT 'outbound'`
- All existing rows will default to 'outbound' — no data migration needed
- Outbound replies insert with `direction='outbound_reply'`
- Lead status value to set: `'in_conversation'` (lowercase, underscore) — verify this matches existing status values in `outreach_leads` before using

### Email
- Subject format: single "Re:" prefix only — strip existing Re:/RE:/re: before prepending
- Signature appended via `get_signature_html()` — already in `email_sender.py`
- No CV attachment on replies
- Body HTML conversion: same `\n → <br>` wrap pattern as `queue_send()` — apply before calling `send_email()`

### Frontend
- Bootstrap 5 components only
- Compose area: full width, sits below reply card, smooth show/hide with Bootstrap collapse or simple JS toggle
- Textarea placeholder: "Type your reply..."
- Send button: Bootstrap primary, label "Send Reply"
- Cancel button: Bootstrap secondary/outline, label "Cancel"
- Jinja/JS brace conflict: never use `{{ }}` in JavaScript strings — use data attributes

### Constraints
- 🚨 Claude Code must NOT send any test emails
- 🚨 All email testing done manually by Christopher — `python tools/reseed_queue.py` then test in Opera
- 🚨 All changes on main branch — no worktrees, no branches
- `outreach.replies_send_reply` CSRF exemption already exists — do not add duplicate

---

## SUCCESS CRITERIA

- [ ] Flask starts cleanly — no new errors, existing Chat 62 CSRF exemption for `outreach.replies_send_reply` confirmed present
- [ ] `direction` column exists in `outreach_emails` — verify via DB check
- [ ] Replies page loads without errors
- [ ] Send Reply button reveals inline compose area
- [ ] Cancel button hides compose area
- [ ] After Christopher manually sends a test reply: Flask log shows `[EMAIL] OK Sent`
- [ ] New row in `outreach_emails` with `direction='outbound_reply'` and `status='sent'`
- [ ] Lead status updated to `'in_conversation'` in `outreach_leads`
- [ ] Success toast visible in Opera
- [ ] No console errors

---

## REFERENCE FILES

- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\outreach.py` — existing `replies_send_reply()` (currently "Coming soon"), `queue_send()` for email send pattern
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\outreach\replies.html` — current reply card layout and Send Reply button
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\email_sender.py` — `send_email()`, `get_signature_html()`, `substitute_variables()`
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\app.py` — verify Chat 62 CSRF exemption for `outreach.replies_send_reply`

---

## TESTING (Claude Code — DB and log checks only, no email sends)

1. Confirm Flask starts cleanly with no new errors
2. Confirm `outreach.replies_send_reply` CSRF exemption present (Chat 62 line)
3. Check DB: `ALTER TABLE` ran — `direction` column exists in `outreach_emails`
4. Check DB: `SELECT email_id, status, direction FROM outreach_emails LIMIT 5` — existing rows show `direction='outbound'`
5. Load `/outreach/replies` — confirm page loads, compose area hidden by default
6. Report DB state and Flask startup — Christopher will do all email testing manually in Opera
