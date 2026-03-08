# CHAT 72 HANDOFF

**Date:** 2026-03-08
**Branch:** main

---

## What Was Done

Wired up the "Send Reply" button on the Replies page to send real emails via SMTP, record them in the DB, and update lead status.

---

## Files Changed

### `act_dashboard/routes/outreach.py`
- `_ensure_schema()`: added `ALTER TABLE outreach_emails ADD COLUMN IF NOT EXISTS direction VARCHAR DEFAULT 'outbound'`
- `STATUS_DISPLAY`: added `"in_conversation": "In Conversation"`
- `replies_send_reply(lead_id)`: replaced stub with full implementation — fetches lead, builds Re: subject, substitutes variables, converts body to HTML, appends signature, calls `send_email()`, inserts to `outreach_emails` with `direction='outbound_reply'`, updates lead status to `'in_conversation'`

### `act_dashboard/templates/outreach/replies.html`
- `buildCard(r)`: wrapped card + inline compose in `reply-card-wrap` container; changed "Reply" button to "Send Reply" calling `toggleCompose()`; added hidden `inline-compose-{leadId}` div with textarea (6 rows), Send Reply button (Bootstrap primary), Cancel button (Bootstrap outline-secondary)
- `sendReply(leadId)`: updated to read textarea content and include `body` in POST JSON body
- Added `toggleCompose(leadId)`: shows/hides the inline compose area and focuses textarea
- Added `sendInlineReply(leadId)`: POSTs body to `/outreach/replies/<lead_id>/send-reply`, shows toast, collapses compose on success

### `act_dashboard/app.py`
- No changes — `outreach.replies_send_reply` CSRF exemption already present from Chat 62 (line 251)

---

## DB State

- `direction` column added to `outreach_emails` (`VARCHAR DEFAULT 'outbound'`)
- All existing rows now show `direction='outbound'`
- New outbound replies insert with `direction='outbound_reply'`

---

## Testing Checklist for Christopher

1. Run `python tools/reseed_queue.py` if needed to ensure there are leads in 'replied' status
2. Go to `/outreach/replies` in Opera
3. Click "Send Reply" on a reply card — inline compose area should expand below the card
4. Type a reply message
5. Click "Send Reply" (primary button) — should show "Reply sent" toast and collapse compose
6. Check Flask log for `[EMAIL] OK Sent`
7. Verify DB: `SELECT email_id, status, direction FROM outreach_emails WHERE direction='outbound_reply' LIMIT 5`
8. Verify lead status: `SELECT lead_id, status FROM outreach_leads WHERE status='in_conversation' LIMIT 5`
9. Cancel button should collapse compose without sending

---

## Known Behaviour

- After reply, lead status becomes `'in_conversation'` — those leads no longer appear in the replies page filter (`status IN ('replied', 'meeting', 'won')`) until a future chat adds 'in_conversation' to that filter if desired
- The slide panel remains accessible by clicking the card body (not the Send Reply button)
- Panel compose area (`buildComposeSection`) also sends via the same endpoint (now wired up)
