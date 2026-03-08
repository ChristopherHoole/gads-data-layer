# CHAT 77: REPLY COMPOSER FIXES — SUMMARY

**Date:** 2026-03-08
**Status:** COMPLETE

---

## What Was Done

Fixed 4 issues introduced or missed in Chat 76's slidein redesign.

### Fix 1 — Nav Unread Badge

**File:** `act_dashboard/routes/outreach.py`

The `inject_outreach_badge_counts()` context processor was querying the wrong table:

```python
# BEFORE (wrong table):
"SELECT COUNT(*) FROM outreach_emails WHERE reply_received = true AND reply_read = false"

# AFTER (correct table):
"SELECT COUNT(DISTINCT lead_id) FROM email_replies WHERE read = false"
```

The badge markup in `base_bootstrap.html` was already correct — it was just receiving a stale count of 0 because the query hit `outreach_emails` instead of `email_replies`.

### Fix 2 — Send Reply on Leads and Sent Slideins

**Files:** `leads.html`, `sent.html`

Both pages had a `siSendReply()` stub that showed a "coming soon" toast. Replaced with the real implementation from `replies.html` that:
- POSTs to `/outreach/replies/<lead_id>/send-reply`
- Passes `body` and `attach_cv` in the JSON body
- Clears the textarea on success
- Shows a success toast and re-renders the thread

### Fix 3 — CV Attach Toggle

**Files:** `leads.html`, `replies.html`, `sent.html` (HTML + JS), `routes/outreach.py`

Added a CV attach toggle row below the toolbar in all 3 composers:
- `siLoadCvStatus()` calls `/outreach/cv/status` on panel open
- If CV is uploaded: checkbox enabled, auto-checked, label shows filename on hover
- If no CV: checkbox disabled, label at 50% opacity with "No CV uploaded" tooltip
- `attach_cv: true` is passed in the `send-reply` POST when checkbox is checked

Updated `replies_send_reply` route to:
- Read `attach_cv` from the request JSON
- Resolve the CV file path from `_CV_DIR` when `attach_cv` is true
- Pass `attachment_path` to `send_email()`

### Fix 4 — Signature Toggle Visual Feedback

**Files:** `leads.html`, `replies.html`, `sent.html`

- Added `onclick="siToggleSignature()"` to the `<label class="si-sig-toggle">` element
- `siToggleSignature()` toggles the `.off` CSS class on `#siSigPip` (green ↔ gray)
- Added `#siSigPreview` div below the toolbar showing the signature content
- Preview shown by default (sig ON), hidden when toggled off
- Composer reset on panel open restores sig to ON state

---

## Files Modified

| File | Changes |
|------|---------|
| `act_dashboard/routes/outreach.py` | Fix nav badge query; add `attach_cv` handling in `replies_send_reply` |
| `act_dashboard/templates/outreach/leads.html` | CV toggle, sig toggle+preview, real `siSendReply()` |
| `act_dashboard/templates/outreach/replies.html` | CV toggle, sig toggle+preview, `attach_cv` in `siSendReply` |
| `act_dashboard/templates/outreach/sent.html` | CV toggle, sig toggle+preview, real `siSendReply()` |

No CSS changes needed — `.si-toggle-pip` and `.si-toggle-pip.off` were already defined in `outreach-slidein.css`.
