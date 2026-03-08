# CHAT 77: REPLY COMPOSER FIXES

**Date:** 2026-03-08
**Estimated Time:** 2–3 hours
**Priority:** HIGH
**Dependencies:** Chat 76 complete

---

## CONTEXT

Chat 76 rebuilt all 3 slideins (Leads, Replies, Sent) with a unified design. Testing revealed 4 issues: the nav unread badge stopped updating, the reply composer on Leads and Sent pages doesn't actually send, the CV attach option was dropped from the composer, and the signature toggle has no visual feedback.

## OBJECTIVE

Fix all 4 reply composer issues across Leads, Replies, and Sent slideins.

---

## DELIVERABLES

1. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\outreach\leads.html` — MODIFY
2. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\outreach\replies.html` — MODIFY
3. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\outreach\sent.html` — MODIFY
4. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\base_bootstrap.html` — MODIFY (nav badge)
5. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_77_HANDOFF.md` — CREATE
6. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_77_SUMMARY.md` — CREATE

---

## REQUIREMENTS

### Fix 1 — Nav unread badge
- The Replies nav link must show a red badge with unread reply count
- Count = rows in `email_replies` WHERE `is_read = false`
- Badge must be populated server-side on every page load (injected into base_bootstrap.html nav via a context variable or direct query)
- Badge disappears when count = 0
- Read the existing nav in base_bootstrap.html first — there may already be badge markup that just isn't being populated

### Fix 2 — Reply composer Send button on Leads and Sent pages
- The Send Reply button in the composer on Leads and Sent slideins must POST to `/outreach/replies/<lead_id>/send-reply` — same route used by the Replies page
- Currently does nothing. Wire it up identically to the Replies page implementation
- On success: clear the textarea, show a success toast, reload the slidein thread

### Fix 3 — CV attach in reply composer
- All 3 composer sections (Leads, Replies, Sent) must have a CV attach toggle below the textarea
- Same pattern as the Queue page CV toggle: checkbox/toggle labelled "Attach CV"
- If CV is uploaded (check `/outreach/cv-status`), show the toggle enabled
- If no CV uploaded, show toggle greyed out with tooltip "No CV uploaded"
- When toggled on, pass `attach_cv: true` in the send-reply POST body
- The existing `send-reply` route must honour `attach_cv` and attach the file if present

### Fix 4 — Signature toggle visual feedback
- The `+ Signature` toggle must visually switch on/off when clicked (Bootstrap form-check or toggle pill)
- When ON: show a live preview of the signature HTML below the textarea (greyed out, not editable)
- When OFF: preview hidden
- Signature content: read from `email_sender.py` `get_signature_html()` or hardcode the same content
- State does not need to persist between page loads — default ON

---

## SUCCESS CRITERIA

- [ ] Replies nav link shows red unread count badge when there are unread replies
- [ ] Badge disappears when all replies are marked read
- [ ] Send Reply works from Leads slidein — `[EMAIL] OK Sent` appears in Flask log
- [ ] Send Reply works from Sent slidein — `[EMAIL] OK Sent` appears in Flask log
- [ ] CV attach toggle visible in all 3 composers
- [ ] Toggle greyed out when no CV uploaded
- [ ] Signature toggle switches on/off visually
- [ ] Signature preview appears below textarea when toggled on
- [ ] No console errors

---

## REFERENCE FILES

- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\outreach\replies.html` — working Send Reply implementation to copy
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\outreach\queue.html` — existing CV toggle pattern
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\email_sender.py` — `get_signature_html()`
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\base_bootstrap.html` — nav markup
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\outreach.py` — `send_reply` route + `replies_send_reply`

---

## TESTING

1. Start Flask — confirm clean startup
2. Open Replies page — confirm unread badge shows on nav
3. Mark all replies as read — confirm badge disappears
4. Open Leads slidein — type a reply, click Send Reply — confirm `[EMAIL] OK Sent` in Flask log
5. Open Sent slidein — type a reply, click Send Reply — confirm `[EMAIL] OK Sent` in Flask log
6. Check CV toggle visible in all 3 composers
7. Click Signature toggle — confirm pip switches and preview appears/disappears
8. Report any Flask errors
