# CHAT 64 BRIEF — Outreach Analytics Page

**Date:** 2026-03-06
**Session:** Claude Code
**Scope:** Outreach Analytics page only
**Estimate:** 4–6 hours
**Depends on:** Chats 59–63 (all outreach data + CSS)

---

## CONTEXT

Building the Analytics page — the final outreach page. This completes the 6-page outreach section (Leads, Queue, Sent, Replies, Templates, Analytics).

**Project location:** `C:\Users\User\Desktop\gads-data-layer`
**App entry point:** `act_dashboard/app.py`
**Wireframe:** `docs/wireframes/wireframe_analytics.html`

---

## WHAT EXISTS ALREADY

- `act_dashboard/routes/outreach.py` — existing file, add routes here
- `act_dashboard/static/css/outreach.css` — existing file, append Analytics CSS here
- `act_dashboard/templates/outreach/` — existing folder, add `analytics.html` here
- `act_dashboard/templates/base_bootstrap.html` — nav already has Analytics link (points to `#`)
- Chart.js already loaded in `base_bootstrap.html`

---

## WHAT TO BUILD

### Step 1: Route — GET /outreach/analytics

Add to `outreach.py`. All queries from `warehouse.duckdb` (read + write connection pattern).

**Date range filter:** Accept `?days=30` query param (default 30). Options: 7, 14, 30, 90.

**Queries to run:**

**KPI cards (8 values):**
- `total_sent` — COUNT of outreach_emails with status='sent' in period
- `total_opened` — COUNT where opened=true in period
- `open_rate` — total_opened / total_sent * 100
- `links_clicked` — COUNT where clicked=true in period
- `click_rate` — links_clicked / total_sent * 100
- `cv_opens` — COUNT where cv_opened=true in period (approximate: emails with cv_attached=true AND clicked=true)
- `cv_open_rate` — cv_opens / total_sent * 100
- `total_replies` — COUNT of outreach_leads with status in ('replied','meeting','won')
- `reply_rate` — total_replies / total_sent * 100
- `meetings_booked` — COUNT of outreach_leads with status='meeting'
- `opened_no_reply` — COUNT leads where at least one email opened but status NOT in ('replied','meeting','won','lost')
- `avg_days_to_reply` — AVG days between first email sent and reply_received_at (approximate using updated_at for replied leads)

**Engagement funnel (6 steps):**
- Leads added (total outreach_leads COUNT)
- Emails sent (total_sent)
- Opened (total_opened)
- Links clicked (links_clicked)
- Replied (total_replies)
- Meeting booked (meetings_booked)
- Each step: count + percentage of sent (or percentage of leads for first step)

**Daily activity chart (last N days):**
- For each day in period: sent count, opened count, clicked count, replied count
- Return as 4 parallel arrays + labels array
- Labels: "5 Jan", "6 Jan" etc.

**Reply rate by day of week:**
- Group by day of week (Mon–Sun)
- For each DOW: open_rate, click_rate, reply_rate
- Return as 3 arrays indexed Mon=0 to Sun=6

**Performance by track (table):**
Group outreach_emails JOIN outreach_leads by track field:
- track name, sent count, opens + open_pct, clicks + click_pct, cv_opens + cv_pct, replies + reply_pct, meetings count + meeting_pct

**Performance by template step (table):**
Group by email_type (initial, follow_up_1, follow_up_2, follow_up_3):
- step label (Step 1–4), template name, sent, opens + open_pct, clicks + click_pct, cv_opens + cv_pct, replies + reply_pct

**Emails sent by day of week:**
- COUNT of sent emails grouped by DOW
- Return as 7-element array [Mon, Tue, Wed, Thu, Fri, Sat, Sun]

**Status distribution (donut):**
- COUNT of outreach_leads grouped by status
- Return as labels + values arrays

**Link clicks breakdown (donut):**
- Approximate from clicked=true emails:
  - CV opened: cv_attached=true AND clicked=true
  - Website: clicked=true AND cv_attached=false (rough proxy)
  - Other: remainder
- Keep simple — 3 categories is fine

**Pass to template:** Single `data` dict with all computed values as JSON-serialisable Python dicts/lists.

---

### Step 2: CSS — append to outreach.css

Append Analytics-specific styles only. Check existing styles first to avoid duplicates.

**New styles needed:**
- `.analytics-content` — content wrapper, padding 20px 24px
- `.caveat-banner` — yellow warning banner (background:#fff8e1, border:#ffe082)
- `.caveat-banner-icon` — amber info icon
- `.stats-row-8` — 8-column KPI grid
- `.stat-card` — white card, border, border-radius, padding (check if already exists)
- `.stat-val` — 22px bold value
- `.stat-lbl` — 11px grey label
- `.stat-delta.up` — green delta
- `.stat-delta.down` — red delta
- `.stat-delta.neutral` — grey delta
- `.stat-caveat` — 10px italic grey note
- `.eng-funnel` — flex row for funnel steps
- `.eng-step` — flex:1, text-center, padding, border
- `.eng-step-val` — 20px bold
- `.eng-step-lbl` — 11px grey
- `.eng-step-pct` — 11px bold coloured
- `.eng-arrow` — arrow between steps
- `.charts-row` — 2fr 1fr grid
- `.charts-row-2` — 1fr 1fr grid
- `.charts-row-3` — 1fr 1fr 1fr grid
- `.chart-card` — white card, border, border-radius, padding
- `.chart-title` — 14px bold
- `.chart-sub` — 11px grey
- `.data-table` — full width, border-collapse
- `.data-table th` — 11px grey header
- `.data-table td` — 12px, padding, border-bottom
- `.pill-step` — blue pill for step number
- `.prog-bar-wrap` — 8px height, grey background track, 60px wide, inline-block
- `.prog-bar-fill` — height 100% !important, display block !important
- `.fill-orange` — background-color: #e65100 !important
- `.fill-purple` — background-color: #6d28d9 !important
- `.fill-blue` — background-color: #1a73e8 !important
- `.fill-green` — background-color: #34a853 !important

---

### Step 3: Template — analytics.html

Create `act_dashboard/templates/outreach/analytics.html`.

**Extend:** `base_bootstrap.html`

**Layout (top to bottom):**

#### Top navbar extras
Date range selector (7d / 14d / 30d / 90d) — GET param, reloads page with `?days=N`

#### Caveat banner
Yellow info banner: "Open tracking note: Apple Mail Privacy Protection (iOS 15+) pre-fetches tracking pixels, which can inflate open counts for Apple Mail users. Open rates are a directional signal only. Click tracking is significantly more reliable — if they clicked your website or CV link, that's a strong intent signal."

#### KPI cards (8 cards, single row)
1. Total sent (black) + "↑ N vs prev" delta
2. Opened (orange #e65100) + "X% open rate" + italic caveat "Incl. Apple pre-fetch"
3. Links clicked (blue) + "X% click rate"
4. CV opens (purple) + "X% of sent"
5. Replies (green) + "X% reply rate"
6. Meetings booked (teal #00897b) + delta
7. Opened, no reply (orange) + "Warm leads" label
8. Avg days to reply (black) + "↓ Xd (faster)" or "↑ Xd (slower)"

#### Full engagement funnel (full width card)
6 coloured steps connected by arrows:
1. Blue: Leads added + "100%"
2. White: Emails sent + "X% of leads"
3. Orange tint: Opened + "X% of sent"
4. Purple tint: Links clicked + "X% of sent"
5. Green tint: Replied + "X% of sent"
6. Dark green tint: Meeting booked + "X% of sent"

#### Daily activity chart (2/3 width) + Reply rate by DOW (1/3 width)
- Daily activity: grouped bar chart, 4 series (Sent/Opened/Clicked/Replied), colours: blue/orange/purple/green
- Reply rate by DOW: grouped bar chart, 3 series (Open%/Click%/Reply%), Mon–Sun x-axis

#### Performance by track (left) + Performance by template step (right)
**Track table columns:** Track | Sent | Opens | Clicks | CV opens | Replies | Meetings
**Each metric cell (except Track, Sent, Meetings):** `N · X%` + coloured progress bar below
- Opens bar: orange `.fill-orange`
- Clicks bar: purple `.fill-purple`
- CV opens bar: blue `.fill-blue`
- Replies bar: green `.fill-green`
- Meetings: just `N · X%` (no bar)

**Template step table columns:** Template | Sent | Opens | Clicks | CV opens | Replies
- Same `N · X%` + bar pattern
- Reply % coloured by performance: ≥20% green, 10–20% blue, 5–10% yellow, <5% grey

#### Bottom row (3 equal columns)
- Emails sent by day of week: bar chart, Tue/Wed/Thu highlighted blue, others grey
- Status distribution: doughnut chart, 7 statuses with colour gradient
- Link clicks breakdown: doughnut chart, 3–4 categories

**All charts use Chart.js.** Pass data from Flask as `{{ data | tojson }}` — never hardcode values in JS.

---

### Step 4: Nav update

In `base_bootstrap.html`, update the Analytics nav link from `href="#"` to `href="/outreach/analytics"`.

---

## DATA NOTES

**outreach_emails columns:** `email_id`, `lead_id`, `email_type`, `status`, `sent_at`, `opened`, `clicked`, `cv_attached`, `subject`, `body`

**outreach_leads columns:** `lead_id`, `name`, `company`, `track`, `status`, `reply_received_at`, `updated_at`

**Email type → step mapping:**
- `initial` → Step 1
- `follow_up_1` → Step 2
- `follow_up_2` → Step 3
- `follow_up_3` → Step 4

**Period filter:** Use `sent_at >= CURRENT_DATE - INTERVAL (days) DAY` for email queries. Lead counts are total (not date-filtered) except where noted.

**NULL handling:** All division must guard against zero denominator — use `CASE WHEN denominator = 0 THEN 0 ELSE ... END`.

**cv_opened approximation:** No dedicated column exists. Use `cv_attached = true AND clicked = true` as a proxy. Note this in a comment.

---

## CONSTRAINTS

- Bootstrap 5 only — no Tailwind
- Extend `base_bootstrap.html`
- No inline styles — all CSS in `outreach.css`
- No `<style>` blocks in template
- Use writable `warehouse.duckdb` connection (read-only queries but use standard connection pattern)
- No CSRF needed (GET only, no POST routes)
- All chart data from Flask via `{{ data | tojson }}` — zero hardcoded values in JS
- Progress bar colours use CSS classes `.fill-orange`, `.fill-purple`, `.fill-blue`, `.fill-green` with `!important` (Bootstrap overrides inline styles)

---

## SUCCESS CRITERIA

1. GET /outreach/analytics returns 200
2. Date range selector changes data on reload
3. Caveat banner renders correctly
4. 8 KPI cards render with correct values and colours
5. Engagement funnel shows 6 steps with correct counts and percentages
6. Daily activity chart renders with 4 series
7. Reply rate by DOW chart renders with 3 series
8. Performance by track table shows all 4 tracks with N · X% + bars
9. Progress bars are coloured (not grey) — orange/purple/blue/green
10. Performance by template step table shows 4 steps with N · X% + bars
11. Reply % in template table is colour-coded by performance
12. Emails sent by DOW chart renders
13. Status distribution donut renders
14. Link clicks breakdown donut renders
15. Nav Analytics link updated and active state correct
16. Zero console errors
17. No inline styles in template

---

## READING ORDER

Before writing any code, read:
1. `docs/wireframes/wireframe_analytics.html` — full layout reference
2. `act_dashboard/routes/outreach.py` — existing connection pattern and route structure
3. `act_dashboard/static/css/outreach.css` — existing styles (don't duplicate)
4. `act_dashboard/templates/base_bootstrap.html` — nav structure + Chart.js inclusion

---

## CHECKPOINTS

**Checkpoint 1:** Route working, all data queries returning values — confirm in terminal
**Checkpoint 2:** KPI cards + funnel render correctly — screenshot
**Checkpoint 3:** All 4 charts render with real data — screenshot
**Checkpoint 4:** Both performance tables render with coloured bars — screenshot
