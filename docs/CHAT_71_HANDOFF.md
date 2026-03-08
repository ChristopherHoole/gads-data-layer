# Chat 71 Handoff — CV Upload & Attach

**Date:** 2026-03-08
**Branch:** main
**Depends on:** Chat 70 complete

---

## State at Handoff

### Done ✅
- CV upload/remove/status routes implemented and CSRF-exempted
- `queue_toggle_cv` route persists `cv_attached` to DB
- `queue_send()` reads `cv_attached` and resolves CV path from `system_config`
- `email_sender.py` uses correct `MIMEMultipart('mixed')` structure for PDF attachments
- Templates page has live upload form (replaces placeholder)
- Queue page CV toggle is wired to the backend
- CV uploads directory created: `act_dashboard/static/uploads/cv/`
- All syntax verified; Flask start verified (no import errors)

### Pending — Manual Test Required ⏳
Christopher needs to:
1. Upload a PDF via the Templates page — confirm file appears and preview works
2. Toggle CV on a queue card — confirm badge updates
3. Refresh queue page — confirm toggle state persists from DB
4. Send one test email to `chrishoole101@gmail.com` with `cv_attached=True` — confirm PDF arrives

---

## Known Constraints

- Only one CV file at a time — upload replaces any existing file
- PDF only, 5 MB max — validated server-side
- If CV toggle is ON but file is missing from disk, email sends without attachment (Flask logs a warning)
- `static/uploads/cv/` is served by Flask static file handler — Preview link uses `/static/uploads/cv/<filename>`

---

## Next Chat Suggestions

- Chat 72: Analytics page — real data (open rate, reply rate by template/track)
- Chat 72: Follow-up automation — auto-queue follow-up emails when `followup_due` is reached
- Chat 72: Lead import from CSV
