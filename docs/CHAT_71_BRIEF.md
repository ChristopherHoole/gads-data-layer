# CHAT 71: CV UPLOAD & ATTACH

**Date:** 2026-03-08
**Estimated Time:** 4–6 hours
**Priority:** HIGH
**Dependencies:** Chat 70 complete

---

## 🚨 BEFORE STARTING
- **Deselect worktree** in Claude Code session options — all work must be done directly on main branch
- Do NOT create any branches or worktrees
- Do NOT send any test emails — all email testing is done manually by Christopher

---

## CONTEXT

The Queue page has a CV attachment toggle on each email card — it exists in the UI but never attaches anything. The Templates page has placeholder CV UI but no upload endpoint. This chat builds both: CV file management on Templates page and real PDF attachment on send from Queue page.

## OBJECTIVE

Enable Christopher to upload his CV on the Templates page and have it automatically attached to emails where the CV toggle is enabled on the Queue page.

---

## DELIVERABLES

1. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\outreach.py` — MODIFY
   - Add `POST /outreach/cv/upload` — accepts PDF, saves to `act_dashboard/static/uploads/cv/`
   - Add `POST /outreach/cv/remove` — deletes CV file
   - Add `GET /outreach/cv/status` — returns `{uploaded: bool, filename: str}`
   - Add `POST /outreach/queue/<email_id>/toggle-cv` — toggles `cv_attached` boolean on `outreach_emails` row

2. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\outreach.py` — MODIFY `queue_send()`
   - If `cv_attached=True` and CV file exists on disk → pass path to `send_email()`
   - If `cv_attached=True` but file missing → log warning, send without attachment

3. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\email_sender.py` — MODIFY
   - Upgrade to `MIMEMultipart('mixed')` to support attachments
   - Add optional `attachment_path=None` parameter to `send_email()`
   - If provided, attach file as `application/pdf`
   - Must be fully backward compatible — existing calls with no attachment_path must work unchanged

4. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\outreach\templates.html` — MODIFY
   - Replace placeholder CV UI with working upload form
   - Show filename + file size when uploaded
   - Preview link (opens PDF in new tab)
   - Replace and Remove buttons

5. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\outreach\queue.html` — MODIFY
   - Wire CV toggle "+" button to `POST /outreach/queue/<email_id>/toggle-cv`
   - Show attached/not attached state clearly on card (green when attached)
   - Load `cv_attached` state from DB on page load

6. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\app.py` — MODIFY
   - Add CSRF exemptions for: `outreach.cv_upload`, `outreach.cv_remove`, `outreach.cv_status`, `outreach.queue_toggle_cv`
   - Label them `✅ [Chat 71] CSRF exempted:`

7. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_71_HANDOFF.md` — CREATE
8. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_71_SUMMARY.md` — CREATE

---

## REQUIREMENTS

### Technical
- CV storage: `act_dashboard/static/uploads/cv/` — create directory if not exists
- Only one CV at a time — new upload replaces existing
- Store CV path in `warehouse.duckdb` using `system_config` table:
  `CREATE TABLE IF NOT EXISTS system_config (key VARCHAR PRIMARY KEY, value VARCHAR)`
  Insert/update: `key='cv_path', value='<full path>'`
- Add `cv_attached BOOLEAN DEFAULT FALSE` column to `outreach_emails`:
  `ALTER TABLE outreach_emails ADD COLUMN IF NOT EXISTS cv_attached BOOLEAN DEFAULT FALSE`
- PDF only, 5MB max
- `send_email()` change must be backward compatible — `attachment_path` defaults to None

### Constraints
- 🚨 Claude Code must NOT send any test emails
- 🚨 All email testing done manually by Christopher using `python tools/reseed_queue.py` then sending from Queue page in Opera
- 🚨 All changes must be on main branch — no worktrees, no branches
- Jinja/JS brace conflict: never use `{{ }}` in JavaScript strings

---

## SUCCESS CRITERIA

- [ ] Flask starts cleanly with exactly these 4 lines visible:
  - `✅ [Chat 71] CSRF exempted: outreach.cv_upload`
  - `✅ [Chat 71] CSRF exempted: outreach.cv_remove`
  - `✅ [Chat 71] CSRF exempted: outreach.cv_status`
  - `✅ [Chat 71] CSRF exempted: outreach.queue_toggle_cv`
- [ ] `GET /outreach/cv/status` returns `{"uploaded": false}` when no CV present
- [ ] `system_config` table exists in warehouse.duckdb
- [ ] `cv_attached` column exists in `outreach_emails`
- [ ] Templates page CV section renders with upload button
- [ ] Queue page CV toggle wired to `/toggle-cv` route
- [ ] No console errors

Christopher will manually test upload, toggle and send after Flask confirms clean startup.

---

## REFERENCE FILES

- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\email_sender.py` — current `send_email()` to upgrade
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\outreach.py` — current `queue_send()` and route patterns
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\outreach\templates.html` — placeholder CV UI to replace
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\outreach\queue.html` — current CV toggle UI
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\app.py` — CSRF exemption pattern

---

## TESTING (Claude Code — DB and log checks only, no email sends)

1. Confirm Flask starts with all 4 `[Chat 71] CSRF exempted` lines
2. Run: `GET /outreach/cv/status` — confirm `{"uploaded": false}`
3. Check DB: `SELECT * FROM system_config` — confirm table exists
4. Check DB: `SELECT cv_attached FROM outreach_emails LIMIT 3` — confirm column exists
5. Paste Flask startup log showing all 4 Chat 71 CSRF lines
6. Report complete — Christopher will do all remaining manual testing in Opera
