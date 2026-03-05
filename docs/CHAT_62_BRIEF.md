# CHAT 62 BRIEF — Outreach Replies Page

**Date:** 2026-03-05
**Session:** Claude Code
**Scope:** Outreach Replies page only
**Estimate:** 4–5 hours
**Depends on:** Chat 59 (outreach data + CSS) + Chat 60 (Queue) + Chat 61 (Sent)

---

## CONTEXT

Building the Replies page for the ACT Outreach system. This is the 4th outreach page after Leads, Queue, and Sent.

**Project location:** `C:\Users\User\Desktop\gads-data-layer`
**App entry point:** `act_dashboard/app.py`
**Wireframe:** `docs/wireframes/wireframe_replies.html`

---

## WHAT EXISTS ALREADY

- `act_dashboard/routes/outreach.py` — existing file, add routes here
- `act_dashboard/static/css/outreach.css` — existing file, append Replies CSS here
- `act_dashboard/templates/outreach/` — existing folder, add `replies.html` here
- `act_dashboard/templates/base_bootstrap.html` — nav already has Replies link (points to `#`)
- Database tables already exist: `outreach_leads`, `outreach_emails`, `outreach_tracking_events`, `outreach_templates`

---

## WHAT TO BUILD

### Step 1: Route — GET /outreach/replies

Add to `outreach.py`. Query from `warehouse.duckdb`.

**Query logic:**
- JOIN `outreach_leads` + `outreach_emails` on `lead_id`
- Filter: `outreach_leads.status IN ('replied', 'meeting', 'won')`
- For each lead, get their most recent sent email (for email_type display)
- Include: lead name, company, email, track, status, reply_received (bool), reply_text, replied_at (from tracking_events or emails), email_type of most recent email
- Order by: most recent reply first

**Unread logic:**
- Add `reply_read` boolean column to `outreach_leads` if it doesn't exist (ALTER TABLE, safe to run idempotently)
- Unread = reply_received = true AND reply_read = false
- When panel is opened → POST to mark-read route

**Stats to compute:**
1. Total replies = COUNT leads with status IN ('replied', 'meeting', 'won')
2. Unread = COUNT where reply_read = false AND reply_received = true
3. Meetings booked = COUNT where status = 'meeting'
4. Awaiting your reply = COUNT where status = 'replied' (replied but not yet meeting/won)

**Pass to template:** `replies` list, `stats` dict

---

### Step 2: Routes — POST actions

Add these routes to `outreach.py`:

| Route | Method | Action |
|-------|--------|--------|
| `/outreach/replies/<lead_id>/mark-read` | POST | Set `reply_read = true`. Return `{"success": true}` |
| `/outreach/replies/<lead_id>/mark-won` | POST | Set `outreach_leads.status = 'won'`. Return `{"success": true}` |
| `/outreach/replies/<lead_id>/mark-lost` | POST | Set `outreach_leads.status = 'lost'`. Return `{"success": true}` |
| `/outreach/replies/<lead_id>/book-meeting` | POST | Set `outreach_leads.status = 'meeting'`. Return `{"success": true}` |
| `/outreach/replies/<lead_id>/send-reply` | POST | Placeholder — return `{"success": true, "message": "Reply sending coming soon"}` |

Add CSRF exemptions for all 5 in `app.py`.

---

### Step 3: CSS — append to outreach.css

Append Replies-specific styles to bottom of `outreach.css`. No inline styles, no `<style>` blocks in template.

**Check first** — many styles already exist (track badges, status pills, panel styles, pagination, reply bubble). Only add what's missing:

- `.reply-card` — card row with border-bottom, padding, hover state
- `.reply-card.unread` — blue left border `3px solid #1a73e8`
- `.reply-card.unread .prospect-name` — font-weight 700
- `.card-top`, `.card-top-left`, `.card-top-right` — flex layout for card header
- `.reply-date` — grey timestamp text
- `.reply-snippet` — truncated preview text, ellipsis overflow
- `.card-bottom` — flex row for badges and actions
- `.card-actions` — button group, margin-left auto
- `.btn-small` — small action button (border, padding, hover)
- `.btn-small.primary` — blue variant
- `.unread-dot` — 8px blue circle
- `.compose-area`, `.compose-toolbar`, `.compose-toolbar-btn` — reply compose box
- `.compose-textarea` — textarea styling
- `.compose-footer` — footer row with send + attachment
- `.btn-send-reply` — blue send button
- `.compose-hint` — grey helper text
- `.reply-bubble-panel` — green reply bubble (may already exist as `.reply-bubble`, check)
- `.reply-meta`, `.reply-from-label`, `.reply-from-name`, `.reply-time`
- `.thread-item`, `.thread-header`, `.thread-type`, `.thread-date`, `.thread-subject`, `.thread-body`

---

### Step 4: Template — replies.html

Create `act_dashboard/templates/outreach/replies.html`.

**Extend:** `base_bootstrap.html`

**Layout (top to bottom):**

#### Stats row (4 cards)
```
Total replies (green) | Unread (blue) | Meetings booked (teal) | Awaiting your reply (grey)
```

#### Control bar
- Filter tabs: All | Unread | Needs action | Meeting booked | Won
- Rows per page selector (10/25/50)
- Spacer
- Search input (placeholder: "Search company or contact…")
- Track filter dropdown (All tracks / Job / Recruiter / Agency / Direct)

#### Reply cards (NOT a table)

Each card contains:
- **Top row:** Name (bold if unread) + company (grey, small) on left | Track badge + status pill + unread dot (if unread) + reply date on right
- **NO avatar circles** — name only, consistent with Leads/Sent pages
- **Snippet row:** Truncated reply text preview (single line, ellipsis)
- **Bottom row:** Email type pill | Action buttons on right: "Queue follow-up" (secondary) + "Mark as won" (primary green)
- **Unread:** Blue left border on card + bold name + blue dot in top right

**Card click:** Opens slide panel

#### Pagination
- Google Ads style: Prev / page numbers / Next
- Info text: "1–10 of 11 replies"

#### Slide panel (right side, 540px)

**Panel header:** Name · Company, email · track

**Panel body sections:**

1. **Their reply** — section title shows date+time. Green bubble with:
   - Reply meta row: "Reply" badge (green) + contact name + timestamp (right)
   - Full reply text

2. **Your reply** — compose area:
   - Toolbar: Bold, Italic, Link, + Signature, AI draft (all placeholder toasts except + Signature which inserts text)
   - Textarea (placeholder: "Write your reply…")
   - Footer: "Send reply" button (POST send-reply, show toast "Reply sending coming soon") + CV toggle badge + hint text "Sending from chrishoole101@gmail.com"

3. **Email thread** — collapsible items showing sent emails to this lead (same pattern as Sent page). Start collapsed.

**Panel footer actions:**
- Mark as won (green/success)
- Book meeting (secondary)
- Update status (secondary)
- Mark as lost (danger red text)

---

### Step 5: Nav update

In `base_bootstrap.html`, update the Replies nav link from `href="#"` to `href="/outreach/replies"`. Add unread badge count (dynamic from stats).

---

## DATA NOTES

**reply_read column:**
- May not exist yet — add with `ALTER TABLE outreach_leads ADD COLUMN IF NOT EXISTS reply_read BOOLEAN DEFAULT false`
- Leads with `reply_received = true` that were created before this column existed should default to `false` (unread)

**replied_at timestamp:**
- Check `outreach_tracking_events` for event_type = 'reply_received'
- Fallback: use `updated_at` from `outreach_leads`

**For email thread in panel:**
- Query ALL sent emails for the lead ordered by `sent_at ASC`
- Display most recent first (reverse in template)

**Synthetic data:**
- Run `python tools/generate_outreach_data.py` after adding `reply_read` column to ensure clean data
- Expect ~7-11 leads with replied/meeting/won status

---

## CONSTRAINTS

- Bootstrap 5 only
- Extend `base_bootstrap.html`
- No inline styles — all CSS in `outreach.css`
- No `<style>` blocks in template
- No avatar circles — removed by design decision
- Use writable `warehouse.duckdb` connection
- CSRF exemptions required for all POST routes
- Send reply = placeholder toast (not live email sending)
- AI draft = placeholder toast
- Mark won/lost/meeting must write to database

---

## SUCCESS CRITERIA

1. GET /outreach/replies returns 200
2. Stats row shows 4 cards with correct counts
3. Reply cards render (not a table)
4. Unread cards have blue left border + bold name + blue dot
5. Reply snippet shows truncated preview
6. Filter tabs work (All/Unread/Needs action/Meeting booked/Won)
7. Search filters by name/company
8. Track dropdown filters correctly
9. Pagination works
10. Card click opens slide panel
11. Panel shows green reply bubble with full text
12. Compose area renders with toolbar + textarea + footer
13. + Signature inserts signature text into textarea
14. Send reply shows toast
15. Email thread shows collapsible items
16. Panel footer: Mark as won updates DB
17. Panel footer: Book meeting updates DB
18. Panel footer: Mark as lost updates DB
19. mark-read POST fires when panel opens (unread → read)
20. Nav Replies link updated + badge shows unread count
21. Zero console errors
22. No inline styles in template

---

## READING ORDER

Before writing any code, read:
1. `docs/wireframes/wireframe_replies.html` — layout reference
2. `act_dashboard/routes/outreach.py` — existing routes and connection pattern
3. `act_dashboard/static/css/outreach.css` — existing styles (don't duplicate)
4. `act_dashboard/templates/outreach/sent.html` — panel + thread pattern reference
5. `act_dashboard/templates/base_bootstrap.html` — nav structure

---

## CHECKPOINTS

**Checkpoint 1:** Route working, reply count in terminal log
**Checkpoint 2:** Cards render with unread styling — screenshot
**Checkpoint 3:** Filter tabs and search working
**Checkpoint 4:** Slide panel opens with reply bubble + compose area — screenshot
**Checkpoint 5:** Mark won/lost/meeting write to DB — confirm via query
