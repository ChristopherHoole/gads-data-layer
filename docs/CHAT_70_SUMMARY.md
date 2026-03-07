# CHAT 70 SUMMARY: Queue Actions — Edit Email + Switch Template

**Date:** 2026-03-07
**Status:** Complete

---

## What Was Built

Wired up the ✏ Edit and 📋 Switch Template buttons on the Queue page so users can modify queued emails before sending.

---

## Files Changed

### `act_dashboard/routes/outreach.py`
Added 4 new routes:
- `GET /outreach/queue/<email_id>/get` — returns `{email_id, subject, body}` for the edit modal
- `POST /outreach/queue/<email_id>/edit` — saves updated subject + body (queued emails only)
- `GET /outreach/queue/<email_id>/templates` — returns templates filtered by the lead's track type
- `POST /outreach/queue/<email_id>/switch-template` — applies a template's subject + body to the queued email

All routes guard with `AND status = 'queued'` so sent emails are never touched.

### `act_dashboard/templates/outreach/queue.html`
- Replaced "coming soon" `onclick` on ✏ button with `openEditModal(emailId)`
- Replaced "coming soon" `onclick` on 📋 button with `openTemplateModal(emailId)`
- Added single **Edit Email Modal** (Bootstrap 5): subject input + 10-row body textarea, pre-populated via GET route
- Added single **Template Picker Modal** (Bootstrap 5): scrollable list of template cards filtered by track, each with a Select button
- Added JS functions: `openEditModal`, `confirmEditEmail`, `openTemplateModal`, `selectTemplate`
- On save/switch: updates card subject bar + email field in DOM without page reload

### `act_dashboard/app.py`
Added Chat 70 CSRF exemptions for all 4 new routes.

---

## Key Design Decisions

- **Single modal instances** — not duplicated per card; `emailId` stored in JS variable
- **No `{{ }}` in JS strings** — used `/outreach/queue/` + emailId string concatenation; template data passed via `data-tmpl-id` attributes
- **Placeholders preserved** — routes store body as-is; `queue_send()` handles substitution at send time (unchanged)
- **Track filtering** — `queue_get_templates` joins `outreach_emails → outreach_leads` to read track, then filters `outreach_templates` by track
