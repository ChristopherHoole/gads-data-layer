# CHAT 63 BRIEF — Outreach Templates Page

**Date:** 2026-03-05
**Session:** Claude Code
**Scope:** Outreach Templates page only
**Estimate:** 3–4 hours
**Depends on:** Chat 59 (outreach data + CSS) + existing outreach_templates table

---

## CONTEXT

Building the Templates page for the ACT Outreach system. This is the 5th outreach page after Leads, Queue, Sent, and Replies.

**Project location:** `C:\Users\User\Desktop\gads-data-layer`
**App entry point:** `act_dashboard/app.py`
**Wireframe:** `docs/wireframes/wireframe_templates.html`

---

## WHAT EXISTS ALREADY

- `act_dashboard/routes/outreach.py` — existing file, add routes here
- `act_dashboard/static/css/outreach.css` — existing file, append Templates CSS here
- `act_dashboard/templates/outreach/` — existing folder, add `templates.html` here
- `act_dashboard/templates/base_bootstrap.html` — nav already has Templates link (points to `#`)
- `outreach_templates` table already exists in `warehouse.duckdb`

---

## WHAT TO BUILD

### Step 1: Route — GET /outreach/templates

Add to `outreach.py`. Query from `warehouse.duckdb`.

**Query logic:**
- SELECT all rows from `outreach_templates` ordered by `sequence_step ASC`
- Include: `template_id`, `name`, `email_type`, `subject`, `body`, `cv_attached`, `sequence_step`, `send_delay_days`

**Stats to compute per template (from outreach_emails):**
- `times_sent` = COUNT of emails with this template's email_type and status = 'sent'
- `replies` = COUNT of leads who replied after receiving this email type
- `reply_rate` = replies / times_sent * 100 (0 if times_sent = 0)

**Pass to template:** `templates` list (with stats attached), no pagination needed (max 4 templates)

---

### Step 2: Routes — POST actions

Add these routes to `outreach.py`:

| Route | Method | Action |
|-------|--------|--------|
| `/outreach/templates/<template_id>/update` | POST | Accept JSON: `{name, subject, body, cv_attached, send_delay_days}`. Update `outreach_templates` row. Return `{"success": true}` |
| `/outreach/templates/<template_id>/duplicate` | POST | Placeholder — return `{"success": true, "message": "Duplicate coming soon"}` |

Add CSRF exemptions for both in `app.py`.

**No routes needed for attachments** — Preview/Replace/Remove are all placeholder toasts.

---

### Step 3: CSS — append to outreach.css

Append Templates-specific styles to bottom of `outreach.css`. No inline styles, no `<style>` blocks in template.

**Check first** — track badges, pills, btn-ghost already exist. Only add what's missing:

- `.templates-content-area` — 2-column grid layout, gap 20px, max-width 1200px
- `.attachments-card` — full-width card (grid-column 1/-1), white bg, border, border-radius
- `.attachments-title`, `.attachments-sub`
- `.attachment-row` — flex row with icon, name/meta, spacer, buttons
- `.attachment-icon` — red PDF icon size
- `.attachment-name`, `.attachment-meta`
- `.attachment-spacer` — flex:1
- `.upload-area` — dashed border, hover state (blue border + bg)
- `.sequence-card` — full-width card (grid-column 1/-1)
- `.sequence-flow` — flex row, overflow-x auto
- `.sequence-step`, `.sequence-box`, `.sequence-box.active`
- `.sequence-box-label`, `.sequence-box-title`, `.sequence-box-sub`
- `.sequence-arrow`, `.sequence-delay`
- `.template-card` — white card, border, border-radius, flex column
- `.template-card-header` — grey bg header, flex between
- `.template-card-title`
- `.template-track-row` — track badges row with "Used for:" label
- `.track-label`
- `.template-body`, `.template-field`, `.template-field-label`
- `.template-subject` — read-only subject display box
- `.template-text` — read-only body display box, scrollable, min-height 140px
- `.template-vars`, `.var-chip`
- `.template-footer` — flex row with stats + attach toggle + buttons
- `.template-stats`
- `.attach-toggle`, `.attach-on`, `.attach-off`
- `.template-footer-right`
- `.section-header`, `.section-title`, `.section-sub`
- `.btn-add`
- Edit modal: `.modal-overlay`, `.modal-box`, `.modal-header`, `.modal-body`, `.modal-footer`
- `.form-group`, `.form-label`, `.form-input`, `.form-textarea`, `.form-hint`
- `.var-chips-row`, `.var-chip-insert`
- `.btn-save`, `.btn-cancel`

---

### Step 4: Template — templates.html

Create `act_dashboard/templates/outreach/templates.html`.

**Extend:** `base_bootstrap.html`

**Layout (top to bottom):**

#### Attachments card (full width)
- Title: "Attachments" + subtitle
- Single attachment row: PDF icon (red) + "Christopher_Hoole_CV.pdf" + meta ("Uploaded [date] · [size] · Used in 4 templates") + Preview / Replace / Remove buttons (all placeholder toasts)
- Upload area: dashed border, upload icon, "Click to upload a new attachment · PDF, DOC, DOCX · Max 5MB" (placeholder toast on click)

#### Sequence flow card (full width)
- Title: "Outreach sequence" + subtitle
- Horizontal flow: Step 1 (active) → +7 days → Step 2 → +7 days → Step 3 → +14 days → Step 4 → No reply → Closed (greyed out)
- Each step box shows: step label, template name, day + CV info
- Clicking a step box scrolls to that template card (smooth scroll)
- Active step highlighted in blue

#### Template cards (2×2 grid)
One card per template from DB. Each card:

**Header:** Template name (bold) | Step pill (Step 1 = blue "Initial", Steps 2-4 = orange "+N days")

**Track row:** "Used for:" label + all 4 track badges (Job/Recruiter/Agency/Direct) — same for all templates

**Body:**
- Subject line field (read-only display box)
- Body field (read-only display box, scrollable, max-height 220px)
- Variables row: "Variables:" label + blue chip for each `{{variable}}` detected in body

**Footer:**
- Stats: "Sent X times · Y replies · Z% reply rate"
- CV attach toggle: "CV attached by default" (blue) or "No CV by default" (grey) — display only
- Edit button → opens edit modal
- Duplicate button → placeholder toast

#### Edit modal (centre overlay)
Triggered by Edit button. Fields:
- Template name (text input)
- Subject line (text input)
- Body (textarea, min-height 200px, resizable)
  - Variable insert chips above textarea: `{{first_name}}` `{{company}}` `{{track}}` `{{role}}` — clicking inserts at cursor
  - Hint text below: "Use {{first_name}}, {{company}} etc."
- CV attachment default (select: "Attach CV by default" / "No CV by default")
- Send delay (select: Same day / +3 days / +5 days / +7 days / +10 days / +14 days / +21 days / +30 days)

**Modal footer:** Cancel | Save changes (POST to update route, show toast, close modal, refresh template display)

---

### Step 5: Nav update

In `base_bootstrap.html`, update the Templates nav link from `href="#"` to `href="/outreach/templates"`.

---

## DATA NOTES

**outreach_templates columns (existing):**
- `template_id`, `name`, `email_type` (initial/follow_up_1/follow_up_2/follow_up_3), `subject`, `body`, `cv_attached` (bool), `sequence_step` (1-4), `send_delay_days`

**Stats calculation:**
- Match template to emails by `email_type` field
- `replied` = lead has `reply_received = true` AND their most recent sent email matches this email_type
- Keep it simple — approximate is fine for synthetic data

**Variable detection:**
- Parse `{{...}}` patterns from body text using regex
- Display as blue chips in the Variables row

**Sequence flow timing:**
- Compute cumulative days from `send_delay_days` in each template
- Step 1: Day 1, Step 2: Day 1 + delay, etc.

---

## CONSTRAINTS

- Bootstrap 5 only
- Extend `base_bootstrap.html`
- No inline styles — all CSS in `outreach.css`
- No `<style>` blocks in template
- Use writable `warehouse.duckdb` connection
- CSRF exemptions required for POST routes
- All attachment actions = placeholder toasts
- Duplicate = placeholder toast
- Edit → Save must write to DB and update displayed template without full page reload

---

## SUCCESS CRITERIA

1. GET /outreach/templates returns 200
2. Attachments card renders with CV row + upload area
3. Sequence flow shows 4 steps + Closed end box
4. Clicking a sequence step scrolls to that template card
5. 4 template cards render in 2×2 grid
6. Each card shows correct subject, body, variables
7. Stats show (times sent, replies, reply rate)
8. CV attach toggle displays correctly (on/off)
9. Edit button opens modal with correct data pre-filled
10. Variable insert chips insert at cursor position in textarea
11. Save changes POSTs to DB and updates card display
12. Duplicate shows placeholder toast
13. Attachment Preview/Replace/Remove show placeholder toasts
14. Upload area shows placeholder toast on click
15. Nav Templates link updated and active state correct
16. Zero console errors
17. No inline styles in template

---

## READING ORDER

Before writing any code, read:
1. `docs/wireframes/wireframe_templates.html` — full layout reference
2. `act_dashboard/routes/outreach.py` — existing routes and connection pattern
3. `act_dashboard/static/css/outreach.css` — existing styles (don't duplicate)
4. `act_dashboard/templates/base_bootstrap.html` — nav structure

---

## CHECKPOINTS

**Checkpoint 1:** Route working, 4 templates returned — confirm in terminal log
**Checkpoint 2:** Attachments + sequence flow render correctly — screenshot
**Checkpoint 3:** 4 template cards render with correct content — screenshot
**Checkpoint 4:** Edit modal opens, variable chips work, Save updates DB — confirm
