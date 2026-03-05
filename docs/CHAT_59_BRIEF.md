# CHAT 59: OUTREACH SYSTEM — LEADS PAGE

**Estimated Time:** 6-8 hours  
**Priority:** HIGH  
**Dependencies:** Chat 58 complete ✅  
**Location:** `C:\Users\User\Desktop\gads-data-layer`

---

## CONTEXT

The ACT dashboard manages Google Ads optimisation for high-value clients. This chat starts building a cold outreach system inside the existing dashboard. Christopher is a Google Ads specialist actively seeking new clients and opportunities.

This chat covers three things only:
1. Synthetic data (database foundation for all future outreach pages)
2. Shared CSS file (used by all outreach pages going forward)
3. Leads page — fully complete and tested

Nothing else. One page done properly is the goal.

---

## OBJECTIVE

Build the outreach database, shared CSS, and a pixel-perfect Leads page that matches the approved wireframe exactly.

---

## WIREFRAME

The approved wireframe is at:
`C:\Users\User\Desktop\gads-data-layer\docs\wireframes\wireframe_leads_v2.html`

**Read this file in full before writing a single line of code.** It is the source of truth for every layout decision, column, interaction, colour, and spacing detail. Do not deviate from it.

---

## DELIVERABLES

| File | Action | Purpose |
|------|--------|---------|
| `tools/generate_outreach_data.py` | Create | Synthetic data for all outreach tables |
| `act_dashboard/routes/outreach.py` | Create | Outreach blueprint — Leads route only for this chat |
| `act_dashboard/static/css/outreach.css` | Create | Shared styles for all outreach pages — extracted from wireframe |
| `act_dashboard/templates/outreach/leads.html` | Create | Leads page template |
| `act_dashboard/templates/base_bootstrap.html` | Modify | Add Outreach nav section |
| `act_dashboard/routes/__init__.py` | Modify | Register outreach blueprint |
| `act_dashboard/app.py` | Modify | CSRF exemptions if needed |
| `docs/CHAT_59_SUMMARY.md` | Create | Summary doc |
| `docs/CHAT_59_HANDOFF.md` | Create | Technical handoff |

---

## BUILD ORDER

Build in this exact order. Do not skip ahead.

---

### STEP 1 — Synthetic data

Create `tools/generate_outreach_data.py`. Run it. Confirm row counts before moving on.

**Database:** All outreach tables go into the writable `warehouse.duckdb`. Never `warehouse_readonly.duckdb`. Follow the DuckDB connection pattern from `act_dashboard/routes/recommendations.py`.

#### Table: `outreach_leads`

```sql
CREATE TABLE IF NOT EXISTS outreach_leads (
    lead_id         VARCHAR PRIMARY KEY,
    first_name      VARCHAR,
    last_name       VARCHAR,
    full_name       VARCHAR,
    company         VARCHAR,
    role            VARCHAR,
    email           VARCHAR,
    linkedin_url    VARCHAR,
    website         VARCHAR,
    city_state      VARCHAR,
    country         VARCHAR,
    timezone        VARCHAR,
    track           VARCHAR,
    source          VARCHAR,
    lead_type_score INTEGER,
    status          VARCHAR,
    progress_stage  INTEGER,
    notes           TEXT,
    added_date      DATE,
    last_activity   TIMESTAMP,
    sequence_step   INTEGER DEFAULT 0,
    do_not_contact  BOOLEAN DEFAULT false
);
```

**Status values:** `cold` | `queued` | `contacted` | `followed_up` | `replied` | `meeting` | `won` | `lost` | `no_reply`

**Lead type score (1-5):**
- 5 = Agency MD / Director / Head of PPC → label: High
- 4 = Recruiter specialising in PPC/digital → label: High
- 3 = Agency senior manager → label: Medium
- 2 = General digital recruiter → label: Medium
- 1 = Job posting / indirect → label: Low

**Progress stages (1-8):** Added → Queued → Contacted → Followed up → Opened/Engaged → Replied → Meeting → Won/Lost

**Seed: 30 leads** — 15 Agency, 8 Recruiter, 4 Direct, 3 Job. Status distribution: 8 cold, 3 queued, 6 contacted, 5 followed_up, 4 replied, 2 meeting, 1 won, 1 no_reply. Countries: mix of uk, usa, uae, canada, australia. Use realistic company names, email addresses, LinkedIn URLs.

#### Table: `outreach_emails`

```sql
CREATE TABLE IF NOT EXISTS outreach_emails (
    email_id        VARCHAR PRIMARY KEY,
    lead_id         VARCHAR,
    template_id     VARCHAR,
    email_type      VARCHAR,
    subject         VARCHAR,
    body            TEXT,
    status          VARCHAR,
    cv_attached     BOOLEAN DEFAULT false,
    sent_at         TIMESTAMP,
    scheduled_at    TIMESTAMP,
    tracking_id     VARCHAR UNIQUE,
    opened_at       TIMESTAMP,
    open_count      INTEGER DEFAULT 0,
    clicked_at      TIMESTAMP,
    click_count     INTEGER DEFAULT 0,
    cv_opened_at    TIMESTAMP,
    cv_open_count   INTEGER DEFAULT 0,
    reply_received  BOOLEAN DEFAULT false,
    reply_read      BOOLEAN DEFAULT false,
    reply_at        TIMESTAMP,
    reply_text      TEXT,
    followup_due    DATE,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Seed ~40 emails consistent with lead statuses. Leads with status `replied` or `meeting` must have `reply_received = true` and realistic `reply_text`. Use UUID4 for `tracking_id`.

#### Table: `outreach_tracking_events`

```sql
CREATE TABLE IF NOT EXISTS outreach_tracking_events (
    event_id        VARCHAR PRIMARY KEY,
    tracking_id     VARCHAR,
    event_type      VARCHAR,
    event_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address      VARCHAR,
    user_agent      VARCHAR,
    click_url       VARCHAR
);
```

Seed ~60 events consistent with sent email data.

#### Table: `outreach_templates`

```sql
CREATE TABLE IF NOT EXISTS outreach_templates (
    template_id         VARCHAR PRIMARY KEY,
    name                VARCHAR,
    email_type          VARCHAR,
    sequence_step       INTEGER,
    subject             VARCHAR,
    body                TEXT,
    send_delay_days     INTEGER,
    cv_attached_default BOOLEAN,
    times_sent          INTEGER DEFAULT 0,
    times_replied       INTEGER DEFAULT 0,
    active              BOOLEAN DEFAULT true,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Seed 4 templates. Subjects: Step 1 "Google Ads Specialist — 16 Years Experience, Available Now", Steps 2-3 "Re: Google Ads Specialist — 16 Years Experience", Step 4 "Re: Google Ads Specialist — Last message".

**Confirm before moving on:** 30 leads, ~40 emails, ~60 events, 4 templates.

---

### STEP 2 — Shared CSS file

Create `act_dashboard/static/css/outreach.css`. Extract all outreach-specific styles from the wireframe into this single file. Every future outreach page will link this file.

Include styles for: stats row and cards, filter section, table container and controls, filter tabs, status dot colours, track badge colours, score badge, pipeline progress bar, actions dropdown, slide-out panel, panel header, badges row, action buttons, My Notes section, email timeline, Add lead modal, all form elements inside modal.

---

### STEP 3 — Navigation

Modify `act_dashboard/templates/base_bootstrap.html`. Add Outreach nav section matching the wireframe. Sub-items: Leads · Queue · Sent · Replies · Templates · Analytics.

- Queue badge: count of `outreach_emails WHERE status = 'queued'`
- Replies badge: count of `outreach_emails WHERE reply_received = true AND reply_read = false`
- Leads active when on `/outreach/leads`

---

### STEP 4 — Leads page

Route in `act_dashboard/routes/outreach.py`. Template at `act_dashboard/templates/outreach/leads.html`. Extend `base_bootstrap.html`. Link `outreach.css`. No inline styles. No `<style>` block.

#### Top navbar
- Left: "Outreach — Leads"
- Right: client selector + `+ Add lead` button (blue, opens modal)

#### Stats row — 5 cards
Total leads · Contacted · Replies · Hot leads (score ≥ 4) · Won

#### Filter section
Search input + 4 dropdowns (All tracks / All countries / All statuses / All sources) + Reset link. All filtering is client-side JavaScript — no page reload.

"Showing X leads" result count below filters, updates as filters change.

#### Table

**Top controls:** filter tabs (All · Active · Won · No reply) + rows per page (10/25/50) on left. Columns button on right (placeholder — toast "Column selector coming soon").

**Columns (exact order):**

| Column | Detail |
|--------|--------|
| Status | Coloured dot only. Tooltip on hover shows status label. |
| Company & contact | Bold company name + grey contact name + role on second line |
| Email | Plain text, no mailto |
| City / State | e.g. "New York, NY" |
| Country | Flag emoji + country name |
| Track | Coloured badge |
| Source | Plain text |
| Type score | Fire emoji + High/Medium/Low |
| Pipeline progress | 8-segment bar filled to progress_stage |
| Added | Date e.g. "4 Mar 2026" |
| Actions | Dropdown |

**Status dot colours:** cold/no_reply → `#9aa0a6` · queued/contacted → `#1a73e8` · followed_up → `#f9ab00` · replied/meeting → `#34a853` · won → `#137333` · lost → `#ea4335`

**Track badge colours:** Agency=blue · Recruiter=purple · Direct=green · Job=grey

**Actions dropdown:** View prospect · Add lead · Queue email · Update status · Mark won · Mark lost · Delete (confirm dialog)

Clicking anywhere on row (except Actions cell) opens slide panel.

#### Slide-out panel

Right-side panel with semi-transparent overlay. Click overlay to close. Match wireframe exactly.

**Header:** Company name (large bold) · Contact name · Role · City, Country · Local time (🕐 EST UTC-5 · 8:55am) · Close button

**Badges row:** Track · Source · Status · Score

**Pipeline progress bar** (full width, 8 segments)

**Action buttons:** Queue email (blue) · Edit lead (outline) · Mark won (green) · Mark lost (red outline) · Update status (grey)

**My Notes:** Shows notes text or placeholder if empty. Edit button → editable textarea with Save/Cancel. Save posts to `PATCH /outreach/leads/<lead_id>/notes`, updates database.

**Email timeline:** Newest first. Each item: dot + card with type label, date, subject, preview, expand button. Types: Initial sent (↑ grey dot) · Follow-up sent (↑ blue dot) · Reply received (↩ green dot) · Scheduled (⏰ orange dot, with Edit draft / Cancel buttons). Expanding shows full email body.

#### Add lead modal

Fields: Company name (required) · Contact name · Email (required) · Track (required) · Country (required) · Source (required) · City/State (with hint: "⚠ Without this, defaults to EST for USA and GMT for UK") · Notes textarea.

Save posts to `POST /outreach/leads/add`, inserts into `outreach_leads`, closes modal, refreshes table.

#### Pagination
Below table. Previous · page numbers · Next. Match `table-styles.css` pattern.

---

## TECHNICAL CONSTRAINTS

- Bootstrap 5 only — no Tailwind, no jQuery
- Extend `base_bootstrap.html` — never `base.html`
- Link `outreach.css` — no inline styles, no `<style>` block in template
- Outreach tables in `warehouse.duckdb` writable connection — follow `recommendations.py` pattern
- Register blueprint in `act_dashboard/routes/__init__.py` — follow existing pattern exactly
- All table filtering is client-side JavaScript
- Add CSRF exemptions to `app.py` for any AJAX POST/PATCH routes

---

## SUCCESS CRITERIA

- [ ] Synthetic data: 30 leads, ~40 emails, ~60 events, 4 templates confirmed
- [ ] `outreach.css` exists — no inline styles in template
- [ ] Outreach nav section visible, 6 sub-items, Leads active state correct
- [ ] Queue and Replies badges show correct counts
- [ ] `/outreach/leads` loads HTTP 200, zero console errors
- [ ] Stats row shows correct counts for all 5 cards
- [ ] All 4 filter dropdowns populated correctly
- [ ] Search filters client-side without page reload
- [ ] Reset clears all filters
- [ ] Result count updates as filters change
- [ ] Filter tabs work (All / Active / Won / No reply)
- [ ] Rows per page selector works
- [ ] All 11 columns present in correct order
- [ ] Status dots show correct colours per status
- [ ] Track badges show correct colours
- [ ] Type score shows fire emoji + High/Medium/Low
- [ ] Pipeline progress shows correct filled segments
- [ ] Clicking a row opens the slide panel
- [ ] Slide panel shows correct lead data
- [ ] Email timeline items expand/collapse correctly
- [ ] My Notes edit saves to database
- [ ] Actions dropdown items all present and functional
- [ ] Add lead modal opens, all fields present, saves to database
- [ ] Pagination works correctly
- [ ] Page loads under 3 seconds

**All criteria must pass before this chat is marked complete.**

---

## TESTING PROTOCOL

1. Fresh PowerShell session
2. `cd C:\Users\User\Desktop\gads-data-layer`
3. `.\.venv\Scripts\Activate.ps1`
4. `python act_dashboard/app.py`
5. Open Opera → `http://localhost:5000/outreach/leads`
6. F12 → Console — zero errors required
7. Work through each success criterion
8. Report at each checkpoint

---

## CHECKPOINTS

1. ✅ Synthetic data complete — row counts confirmed
2. ✅ `outreach.css` created
3. ✅ Nav updated — Outreach section visible, badges correct
4. ✅ Leads page complete — all success criteria passing

---

## REFERENCE FILES

Read before starting:
- `C:\Users\User\Desktop\gads-data-layer\docs\wireframes\wireframe_leads_v2.html` — approved wireframe (source of truth)
- `/mnt/project/MASTER_KNOWLEDGE.md` — DuckDB patterns, blueprint structure
- `act_dashboard/routes/recommendations.py` — DuckDB connection pattern
- `act_dashboard/routes/__init__.py` — blueprint registration pattern
- `act_dashboard/templates/base_bootstrap.html` — nav structure
- `act_dashboard/static/css/table-styles.css` — existing table styles (pagination, control bar patterns)

---

## DOCUMENTATION

**`docs/CHAT_59_SUMMARY.md`:** What was built, files created/modified, testing results, issues and fixes.

**`docs/CHAT_59_HANDOFF.md`:** Database schema (all 4 tables), blueprint route map, CSS architecture, Notes PATCH endpoint, Add lead POST endpoint, git commit strategy.
