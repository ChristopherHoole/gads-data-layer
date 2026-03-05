# CHAT 61 BRIEF — Outreach Sent Page

**Date:** 2026-03-05
**Session:** Claude Code
**Scope:** Outreach Sent page only
**Estimate:** 4–5 hours
**Depends on:** Chat 59 (outreach data + CSS) + Chat 60 (Queue page patterns)

---

## CONTEXT

Building the Sent page for the ACT Outreach system. This is the 3rd outreach page after Leads (Chat 59) and Queue (Chat 60).

**Project location:** `C:\Users\User\Desktop\gads-data-layer`
**App entry point:** `act_dashboard/app.py`
**Wireframe:** `docs/wireframes/wireframe_sent.html`

---

## WHAT EXISTS ALREADY

- `act_dashboard/routes/outreach.py` — existing file, add routes here
- `act_dashboard/static/css/outreach.css` — existing file, append Sent CSS here
- `act_dashboard/templates/outreach/` — existing folder, add `sent.html` here
- `act_dashboard/templates/base_bootstrap.html` — nav already has Sent link (points to `#`)
- Database tables already exist: `outreach_leads`, `outreach_emails`, `outreach_tracking_events`, `outreach_templates`

---

## WHAT TO BUILD

### Step 1: Route — GET /outreach/sent

Add to `outreach.py`. Query data from `warehouse.duckdb` (writable connection, same pattern as leads route).

**Query logic:**
- JOIN `outreach_emails` + `outreach_leads` on `lead_id`
- Filter: `outreach_emails.status = 'sent'`
- Include: lead name, company, email, track, email_type, sent_at, followup_due, lead status
- Order by: `sent_at DESC`

**Follow-up due logic (compute in Python):**
- `followup_due` column in `outreach_emails` — compare to today
- If `followup_due < today` → `overdue`
- If `followup_due = today` → `today`
- If `followup_due > today` → `soon` (show formatted date)
- If `followup_due IS NULL` → `none`

**Stats to compute:**
1. Total sent = COUNT of sent emails
2. Follow-ups overdue = COUNT where followup_due < today
3. Due today = COUNT where followup_due = today
4. Replied = COUNT of leads with status IN ('replied', 'meeting', 'won')
5. No reply / closed = COUNT of leads with status IN ('no_reply', 'lost')

**Pass to template:** `emails` list, `stats` dict, `current_tab` (default 'all')

---

### Step 2: Routes — POST actions

Add 4 action routes to `outreach.py`:

| Route | Method | Action |
|-------|--------|--------|
| `/outreach/sent/<email_id>/queue-followup` | POST | Update `followup_due` to tomorrow + set lead status to `followed_up`. Return `{"success": true}` |
| `/outreach/sent/<lead_id>/update-status` | POST | Accept `status` from JSON body, update `outreach_leads.status`. Return `{"success": true}` |
| `/outreach/sent/<lead_id>/mark-won` | POST | Set `outreach_leads.status = 'won'`. Return `{"success": true}` |
| `/outreach/sent/<lead_id>/mark-lost` | POST | Set `outreach_leads.status = 'lost'`. Return `{"success": true}` |

Add CSRF exemptions for all 4 in `app.py` (same pattern as Chat 59/60).

---

### Step 3: CSS — append to outreach.css

Add Sent-specific styles to the bottom of `outreach.css`. No inline styles, no `<style>` blocks in template.

**Styles needed (extract from wireframe):**
- `.overdue-row` — light red row background `#fff8f8`
- `.followup-overdue` — red text `#ea4335`
- `.followup-today` — orange text `#e65100`
- `.followup-soon` — dark text `#202124`
- `.followup-none` — grey italic text `#9aa0a6`
- `.reply-bubble` — green background reply block
- `.reply-header`, `.reply-label`, `.reply-from`
- `.followup-scheduler` — yellow box with border
- `.followup-scheduler-title`, `.followup-row`, `.btn-schedule`
- `.email-thread-item`, `.thread-item-header`, `.thread-body`, `.thread-body.hidden`
- `.thread-date`, `.thread-subject`
- `.sent-date`, `.sent-time`

**Note:** Many styles already exist in outreach.css (track badges, email-type pills, status dots, panel styles, pagination). Do NOT duplicate — check first, only add what's missing.

---

### Step 4: Template — sent.html

Create `act_dashboard/templates/outreach/sent.html`.

**Extend:** `base_bootstrap.html`
**CSS:** Link `outreach.css` (already linked in base or add to block)

**Layout (top to bottom):**

#### Stats row (5 cards)
```
Total sent | Follow-ups overdue (red) | Due today (orange) | Replied (green) | No reply/closed (grey)
```

#### Control bar
- Filter tabs: All | Overdue | Due today | Replied | Closed
- Rows per page selector (10/25/50/100)
- Spacer
- Search input (placeholder: "Search company or contact…")
- Track filter dropdown (All tracks / Job / Recruiter / Agency / Direct)
- Email type filter dropdown (All email types / Initial email / Follow-up 1 / Follow-up 2 / Follow-up 3)

#### Table (8 columns)
| # | Column | Content |
|---|--------|---------|
| 1 | Prospect | Name (bold) + company (grey, small) |
| 2 | Email | Email address (grey, small) |
| 3 | Track | Colour-coded badge (Job/Recruiter/Agency/Direct) |
| 4 | Email type | Pill (Initial email = blue, Follow-up = orange) |
| 5 | Sent | Date line 1 + time/timezone line 2 |
| 6 | Follow-up due | Colour-coded text (overdue=red, today=orange, soon=dark, none=grey dash) |
| 7 | Status | Dot + label |
| 8 | Actions | Dropdown button |

**Row states:**
- Overdue rows: light red background `overdue-row` class
- Clicking any row (except Actions cell) opens slide panel

**Actions dropdown items:**
1. View email thread (opens slide panel)
2. Queue follow-up (POST queue-followup, show toast)
3. Update status (show status picker modal, POST update-status)
4. --- separator ---
5. Mark as replied (POST update-status with replied)
6. Mark as won (POST mark-won)
7. Mark as lost (POST mark-lost)
8. --- separator ---
9. Delete (placeholder toast "Delete coming soon")

#### Pagination
- Google Ads style: Prev / page numbers / Next
- Info text: "1–10 of 67 emails"

#### Slide panel (right side, 520px)
Slide in from right on row click.

**Panel header:** Name · Company (bold), email address (grey)

**Panel body sections:**
1. **Lead details** — Status (dot+label), Track (badge), Last sent (date+time), Email type (pill)
2. **Their reply** (only if lead status = replied/meeting/won AND reply exists) — green bubble with reply text
3. **Email thread** — collapsible items, most recent first. Each item: pill + date header (clickable to expand), body text when expanded
4. **Follow-up scheduler** (only if followup_due is not none) — yellow box with: due date label, Send on date input, Template dropdown, Attach CV dropdown, "Add to queue" button (placeholder toast)

**Panel footer actions:**
- Queue follow-up (primary blue)
- Update status
- Mark as won
- Mark as lost (danger red text)

---

### Step 5: Nav update

In `base_bootstrap.html`, update the Sent nav link from `href="#"` to `href="/outreach/sent"`.

---

## DATA NOTES

**outreach_emails columns (relevant):**
- `email_id`, `lead_id`, `email_type`, `subject`, `body`, `status`, `sent_at`, `followup_due`, `cv_attached`, `reply_received`, `reply_text`

**outreach_leads columns (relevant):**
- `lead_id`, `first_name`, `last_name`, `company`, `email`, `track`, `status`

**For the email thread in slide panel:**
- Query ALL emails for the lead (not just sent ones) ordered by `sent_at ASC`
- Show each email as a collapsible thread item
- Most recent first (reverse the order in display)

**Sent_at formatting:**
- Display as "5 Mar 2026" + "8:36am EST" (separate lines)
- Use Python to format, pass pre-formatted strings to template

---

## CONSTRAINTS

- Bootstrap 5 only — no other CSS frameworks
- Extend `base_bootstrap.html` — not `base.html`
- No inline styles anywhere — all CSS in `outreach.css`
- No `<style>` blocks in template
- Use writable `warehouse.duckdb` connection (same pattern as leads/queue routes)
- Follow exact connection pattern from `outreach.py` (Chat 59)
- CSRF exemptions required for all POST routes
- Placeholder toasts acceptable for: Delete, Add to queue (follow-up scheduler), Update status modal
- Mark won/lost and Queue follow-up must write to database

---

## SUCCESS CRITERIA

1. GET /outreach/sent returns 200
2. Stats row shows 5 cards with correct counts
3. Table shows sent emails with all 8 columns
4. Overdue rows have red background
5. Follow-up due column colour-coded correctly
6. Filter tabs work (All/Overdue/Due today/Replied/Closed)
7. Search filters by company and contact name
8. Track dropdown filters correctly
9. Email type dropdown filters correctly
10. Pagination works
11. Row click opens slide panel
12. Slide panel shows lead details section
13. Reply bubble shows for replied/meeting/won leads
14. Email thread shows collapsible items
15. Follow-up scheduler shows for leads with due dates
16. Actions dropdown opens on button click
17. Queue follow-up updates database (followup_due + status)
18. Mark won/lost updates database
19. Nav Sent link updated and active state correct
20. Zero console errors
21. No inline styles in template

---

## READING ORDER

Before writing any code, read:
1. `docs/wireframes/wireframe_sent.html` — full layout reference
2. `act_dashboard/routes/outreach.py` — existing routes and connection pattern
3. `act_dashboard/static/css/outreach.css` — existing styles (don't duplicate)
4. `act_dashboard/templates/outreach/leads.html` — panel pattern reference
5. `act_dashboard/templates/base_bootstrap.html` — nav structure

---

## CHECKPOINTS

**Checkpoint 1:** Route + data query working — confirm sent email count in terminal log
**Checkpoint 2:** Table renders with correct columns and row colours — screenshot
**Checkpoint 3:** Filter tabs, search, dropdowns all working — confirm in browser
**Checkpoint 4:** Slide panel opens with all sections — screenshot
**Checkpoint 5:** Actions (queue follow-up, mark won/lost) write to DB — confirm via query
