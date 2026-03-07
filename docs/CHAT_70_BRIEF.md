# CHAT 70: QUEUE ACTIONS — EDIT EMAIL + SWITCH TEMPLATE

**Date:** 2026-03-07
**Estimated Time:** 3–4 hours
**Priority:** HIGH
**Dependencies:** Chat 69 complete

---

## CONTEXT

The Queue page has ✏ (Edit) and 📋 (Switch Template) buttons on each email card. Both currently fire a "Coming soon" toast. Chat 68 built live email sending. Chat 69 added the email signature. These two actions need to be fully wired up so users can edit an email's subject/body or swap to a different template before sending.

## OBJECTIVE

Wire up the ✏ Edit and 📋 Switch Template buttons on the Queue page so users can modify queued emails before sending.

---

## DELIVERABLES

1. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\outreach.py` — MODIFY
   - Add `GET /outreach/queue/<email_id>/get` — fetch current subject + body for edit modal
   - Add `POST /outreach/queue/<email_id>/edit` — save updated subject + body to `outreach_emails`
   - Add `GET /outreach/queue/<email_id>/templates` — return templates filtered by lead's track type
   - Add `POST /outreach/queue/<email_id>/switch-template` — apply selected template to `outreach_emails`

2. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\outreach\queue.html` — MODIFY
   - Add single Edit modal (subject field + body textarea, pre-populated via JS fetch)
   - Add single Template Picker modal (list of templates for that lead's track, selectable)
   - Wire ✏ button: fetch GET route → populate modal → open
   - Wire 📋 button: fetch templates GET route → render list → open modal
   - Both modals: on confirm → POST to respective route → close modal → update card subject/body in DOM

3. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\app.py` — MODIFY
   - Add CSRF exemptions for all 4 new routes

4. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_70_HANDOFF.md` — CREATE
5. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_70_SUMMARY.md` — CREATE

---

## REQUIREMENTS

### Technical
- Both routes write to `outreach_emails` WHERE `status='queued'` only — never touch sent emails
- Variable placeholders (e.g. `{{first_name}}`) must be preserved as-is in stored body — substitution happens at send time in `queue_send()`
- Template picker must filter by the lead's track type (Agency / Recruiter / Direct / Job) — fetch track from `outreach_leads` via the lead_id on the email record
- GET route for edit modal returns: `email_id`, `subject`, `body`
- GET route for templates returns: `template_id`, `name`, `step`, `subject`, `body` — filtered by track
- Both modals are shared/single instances in queue.html — not duplicated per card
- On successful save, update the card's displayed subject in the DOM without page reload

### Design
- Bootstrap 5 modal components
- Edit modal: subject input (text), body textarea (min 8 rows), Save + Cancel buttons
- Template picker modal: scrollable list of template cards showing name + step number, Select button per template, Cancel button
- Match existing queue page styling

### Constraints
- Jinja/JS brace conflict: never use `{{ }}` in JavaScript strings — use data attributes or split braces
- CSRF exemptions required for all 4 new routes in app.py
- Read existing `queue_send()` carefully — do not break it

---

## SUCCESS CRITERIA

- [ ] ✏ button opens Edit modal pre-populated with current subject and body
- [ ] Saving edit updates `outreach_emails` and reflects on card without page reload
- [ ] 📋 button opens Template Picker showing templates filtered to correct track type
- [ ] Selecting a template updates `outreach_emails` subject + body
- [ ] Sending the email after edit/switch sends the updated content (not original)
- [ ] Variable placeholders survive the edit/switch without being substituted prematurely
- [ ] No "Coming soon" toasts on either button
- [ ] No console errors, Flask starts cleanly

---

## REFERENCE FILES

- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\outreach.py` — existing queue routes, queue_send() pattern
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\outreach\queue.html` — current queue page with card structure and existing modals
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\app.py` — CSRF exemption pattern (~line where Chat 60 exemptions are added)

---

## TESTING

1. Run `python tools/reseed_queue.py`
2. Start Flask
3. Click ✏ on any queue card — confirm modal opens with correct subject and body pre-filled
4. Edit the subject, save — confirm card subject updates in DOM and Flask logs the update
5. Click 📋 on a queue card — confirm template picker opens showing templates for that lead's track only
6. Select a template — confirm subject/body updated in DB
7. Send the edited email — confirm Flask log shows `[EMAIL] OK Sent` with updated subject
8. Check chrishoole101@gmail.com — confirm edited content arrived (not original template)
9. Confirm no console errors in Flask terminal
