# ACT Prototype — Design Standards

**Created:** 2026-04-06 (Morning Review, Page 1)
**Updated:** 2026-04-08 (Page 4: Campaign Level added — campaign selector, lever cards, strategy panel)
**Status:** Living document — updated with each new page

---

## Text Casing Standard (v2, Change 1)

**Rule: No all-caps anywhere in the UI.** All text uses Title Case or sentence case.
- Badge labels: "Campaign", "Investigate", "Low Risk" (not CAMPAIGN, INVESTIGATE)
- Status card labels: "Actions Executed", "Awaiting Approval" (not ACTIONS EXECUTED)
- Section headings: "Awaiting Approval", "Actions Executed Overnight"
- **Exception:** Sidebar section labels (REVIEW, OPTIMIZATION, SETTINGS) remain uppercase at 12px as a structural wayfinding device.

This standard applies to all future pages.

---

## Table Alignment Standard (v7)

**Rule: ALL table content is LEFT-ALIGNED.** No right-alignment in any table, anywhere in the prototype. This applies to headers (`<th>`) and data cells (`<td>`) for both text and numeric columns.

**Equal-width columns:** Use `table-layout: fixed; width: 100%` with explicit percentage widths on `th`/`td`:
- Signal Decomposition: 8 columns at `width: 12.5%` each (`.data-table--sig`)
- Budget Shift History: 4 columns at `width: 25%` each (`.data-table--hist`)

**No `overflow-x: auto` wrapper** on tables using `table-layout: fixed` — the overflow wrapper creates a new block formatting context that can collapse the table to zero width when the parent section is toggled.

This standard applies to all existing and future tables across the entire prototype.

---

## Date/Time Formats (v6)

| Context | Format | Example |
|---------|--------|---------|
| Actions Executed timestamp | `D Mon, HH:MM AM` | `6 Apr, 05:14 AM` |
| Monitoring start date | `Started: D Mon YYYY, HH:MM AM` | `Started: 4 Apr 2026, 05:10 AM` |
| Recent Alerts timestamp | `D Mon YYYY` | `2 Apr 2026` |
| Time waiting (approval) | Relative | `Identified 3 hours ago`, `Waiting 2 days` |
| Cooldown remaining | Relative | `48h remaining of 72h cooldown` |

**Rules:**
- Executed items include the date because the log may span multiple days
- Monitoring items show the full start date+time so there's no ambiguity about when monitoring began
- Alerts use date-only (time is less relevant for historical items)
- All times use 12-hour format with AM/PM

---

## Font Scale (v3, Change 4)

**Rule: Exactly 5 font sizes. Nothing below 12px.**

| Size | Usage |
|------|-------|
| **28px** | Status card numbers only |
| **20px** | Material Symbols icons in sidebar nav |
| **16px** | Section headings, slide-in panel title, page title |
| **14px** | Body text, summaries, recommendations, item descriptions, nav items, date, client switcher, toasts |
| **12px** | Badges (level, action, risk, resolution, health), buttons, timestamps, labels, before/after pills, group headers, cooldown text, nav section labels, "ACT last ran" pill |

Everything previously at 9px, 10px, 11px is now 12px. Everything at 13px, 15px is now 14px. This standard applies to all future pages.

---

## Colour Rules (v3, Change 5)

**Rule: No grey text colours anywhere.** Every piece of text is either:
- `#000000` (light mode) / `#ffffff` (dark mode) for all text
- A v54 brand colour (blue `#3b82f6`, green `#10b981`, red `#ef4444`, amber `#f59e0b`) for coloured elements

The CSS variables `--act-text-secondary` and `--act-text-muted` have been removed. All text uses `--act-text` which is `#000000` in light mode and `#ffffff` in dark mode. Where reduced emphasis is needed, use `opacity` (e.g., nav labels at `opacity: 0.5`), not grey colours.

This standard applies to all future pages.

---

## Colour Palette

### Core (v5 — v54 Design System, no grey text)
| Token | Value (Light) | Value (Dark) | Usage |
|-------|---------------|--------------|-------|
| `--act-primary` | `#3b82f6` | `#3b82f6` | Primary blue, active states, links |
| `--act-primary-bg` | `#dbeafe` | `#1e3a5f` | Active item backgrounds |
| `--act-text` | `#000000` | `#ffffff` | All text (no grey) |
| `--act-border` | `#dadce0` | `#1e293b` | Primary borders |
| `--act-border-light` | `#e8eaed` | `#1e293b` | Card/section borders |
| `--act-surface` | `#ffffff` | `#111827` | Cards, sidebar, top bar |
| `--act-page-bg` | `#f8f9fa` | `#0a0e17` | Page background |
| `--act-hover-bg` | `#f1f3f4` | `#1e293b` | Hover states |
| `--act-rec-bg` | `#dbeafe` | `rgba(59,130,246,0.2)` | Recommendation highlight bg |
| `--act-rec-text` | `#000000` | `#ffffff` | Recommendation text |

### Action Categories (v5 — v54 Design System)
| Category | Base Colour | Badge BG | Badge Text | Border | Dark BG |
|----------|-------------|----------|------------|--------|---------|
| **Act** (auto-executed) | `#10b981` | `#d1fae5` | `#065f46` | `#a7f3d0` | `rgba(16,185,129,0.12)` |
| **Monitor** (watching) | `#3b82f6` | `#dbeafe` | `#1e40af` | `#bfdbfe` | `rgba(59,130,246,0.15)` |
| **Investigate** (approval) | `#f59e0b` | `#fef3c7` | `#92400e` | `#fde68a` | `rgba(245,158,11,0.12)` |
| **Alert** (urgent) | `#ef4444` | `#fee2e2` | `#991b1b` | `#fecaca` | `rgba(239,68,68,0.12)` |

**Banned legacy colours (must never appear in CSS):** `#34a853`, `#137333`, `#1a73e8`, `#1967d2`, `#f9ab00`, `#b06000`, `#ea4335`, `#c5221f`, `#2d9249`, `#1666d0`, `#e37400`

### Risk Badges (v4, Change 3 — Low is grey, not green)
| Level | Background (Light) | Text (Light) | Background (Dark) | Text (Dark) |
|-------|-------------------|-------------|------------------|------------|
| Low | `#f3f4f6` | `#6b7280` | `#374151` | `#9ca3af` |
| Medium | `#fef3c7` | `#f59e0b` | (amber-bg) | `#f59e0b` |
| High | `#fee2e2` | `#ef4444` | (red-bg) | `#ef4444` |

### Level Badges (v4, Change 2 — v54 architecture colours)
| Level | Background | Text |
|-------|-----------|------|
| Account | `#dbeafe` | `#3b82f6` (blue) |
| Campaign | `#d1fae5` | `#10b981` (green) |
| Ad Group | `#fef3c7` | `#f59e0b` (amber) |
| Keyword | `#ede9fe` | `#8b5cf6` (purple) |
| Ad | `#fce7f3` | `#ec4899` (pink) |
| Shopping | `#ccfbf1` | `#14b8a6` (teal) |

---

## Typography

| Element | Font | Size | Weight | Colour |
|---------|------|------|--------|--------|
| Body text | System stack | 14px | 400 | `--act-text` |
| Page title (topbar) | System stack | 16px | 600 | `--act-text` |
| Section title | System stack | 14px | 600 | `--act-text` |
| Item summary | System stack | 13px | 400 | `--act-text` |
| Recommendation | System stack | 12px | 400 | `--act-text-secondary` |
| Badge text | System stack | 10px | 600-700 | Per-category |
| Nav item | System stack | 13px | 500 | `--act-text-secondary` |
| Nav section label | System stack | 10px | 600 | `--act-text-muted` |
| Timestamp | System stack | 11px | 400 | `--act-text-muted` |
| Time waiting | System stack | 10px | 400 | `--act-text-muted` |
| Code/values | DM Mono | 12px | 400-500 | varies |
| Status card count | System stack | 28px | 700 | Per-category |
| Status card label | System stack | 12px | 600 | `--act-text-secondary` |
| Detail grid label | System stack | 11px | 700 | `--act-text-muted` |
| Detail grid value | System stack | 12px | 400 | `--act-text-secondary` |
| Health label | System stack | 9px | 600 | Per-status |

**System font stack:** `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif`

---

## Spacing System

| Token | Value | Usage |
|-------|-------|-------|
| Content padding | 24px | Main content area padding |
| Card gap | 16px | Between status cards |
| Section margin-bottom | 20px | Between section panels |
| Item padding | 14px 20px | Inside each action item |
| Section header padding | 14px 20px | Section header |
| Group header padding | 10px 20px | Entity-level group header |
| Nav item padding | 8px 12px | Sidebar nav items |
| Badge padding | 2px 8px | All badges |
| Button padding | 5px 14px | Standard buttons |
| Slide-in body padding | 24px | Slide-in panel content |
| Detail grid gap | 8px rows | Between key-value pairs |

---

## Layout

| Element | Dimension |
|---------|-----------|
| Sidebar width | 220px |
| Top bar height | 52px |
| Main content offset | margin-left: 220px, margin-top: 52px |
| Slide-in panel width | 520px |
| Card border-radius | 8px |
| Badge border-radius | 4px |
| Button border-radius | 6px |
| Nav item border-radius | 6px |

**Status cards:** CSS Grid, `repeat(4, 1fr)`, collapses to 2-col at 1024px, 1-col at 480px.

---

## Component Patterns

### Status Card (v4, Change 4 — reordered)
- **Card order (left to right):** Awaiting Approval (amber) → Alerts (red) → Actions Executed (green) → Monitoring (blue)
- White background, 8px radius, 1px `--act-border-light` border
- 4px left colour stripe (green/amber/blue/red)
- Shadow: `0 1px 3px rgba(60,64,67,0.12), 0 1px 2px rgba(60,64,67,0.08)`
- Clickable — filters sections to matching category
- Hover: slight lift (`translateY(-1px)`) + deeper shadow

### Section Panel
- White card with collapsible header
- Header: section icon + title + count badge + chevron toggle
- Header hover: `--act-hover-bg`
- Chevron rotates -90deg when collapsed
- Body hidden when collapsed
- **Default state (v2, Change 4):** Only "Awaiting Approval" expanded; all others collapsed

### Entity-Level Groups (v2, Change 2; v3, Change 2)
- Items within every section grouped by entity level
- Group header: chevron + level badge + count pill
- Groups are independently collapsible
- **Approval section ordering (v2, Change 3):** Alert groups first (most urgent), then Investigate groups
- **v3:** Group header background is barely visible — `rgba(0,0,0,0.015)` in light mode, `rgba(255,255,255,0.02)` in dark mode. Headers serve as passive separators, not action elements.

### Action Item
- Horizontal layout: checkbox (approval only) | content | action buttons
- Content: top row (badges + risk + time waiting) → summary → recommendation
- Bottom border between items, none on last
- Hover: subtle `#fafbfc` background
- **Approve/Decline (v3, Change 6):** Item gets `actioned` class (opacity 0.55), Approve/Decline buttons hide, "Approved"/"Declined" status badge appears. **View Details stays clickable** so the user can still review the decision tree reasoning after acting.
- **Alert items (v2 Change 7; v3 Change 1):** 3px red left border only. No background tint — the border alone provides sufficient visual distinction.

### Action Item Badge Row (v2 Changes 5-6; v3 Change 7)
Order: Level badge → Action badge → Risk badge → Time waiting indicator → Cooldown (if applicable)
- **Risk badge:** Low (green), Medium (amber), High (red) — always visible, no expand needed
- **Time waiting:** clock icon + "Identified 3 hours ago" or "Waiting 2 days"
- **Cooldown (v3, Change 7):** timer icon + "14-day cooldown after approval". Only shown when the action has a defined cooldown period. Cooldowns from the ACT architecture doc:
  - tCPA/tROAS changes: 14-day cooldown
  - Budget shifts: 72-hour cooldown
  - Device bids: 7-day cooldown
  - Geo/Schedule: 30-day cooldown
  - Keyword bids: 72-hour cooldown
  - Product bids: 72-hour cooldown
  - Keyword discovery, Ad Group alerts, Ad flagging: No cooldown (approval-only actions)

### ACT Recommendation Line (v3 Change 3; v4 Change 1)
- Appears below the item summary (problem first, then solution)
- Font size: 14px (body size, not smaller)
- Text colour: `#000000` in light mode, `#ffffff` in dark mode (no grey)
- Background: light blue tint (`--act-rec-bg`) — `#e8f0fe` light, `rgba(30,58,95,0.4)` dark
- **Padding: 4px 6px** (halved in v4 from 8px 12px), border-radius 6px
- Lightbulb icon in `--act-primary` blue
- The recommendation should always be readable without expanding details

### Estimated Impact Line (v6, Change 3)
- Appears below the recommendation line on approval items
- Font size: 12px, opacity 0.7 (supplementary info, not primary content)
- Green trending_up icon prefix
- Realistic estimates: savings in pounds/week, conversion estimates, CPC/CTR percentages
- Not shown on monitoring or executed items (impact is already measured there)

### Monitoring Start Date (v6, Change 1)
- Shown on every monitoring item below the summary
- Format: "Started: D Mon YYYY, HH:MM AM" with calendar_today icon
- Font size: 12px, opacity 0.7

### Consecutive Days Streak (v6, Change 4)
- Shown alongside the health label on monitoring items
- Format: "for N consecutive days"
- Font size: 12px, opacity 0.7
- Only shown when a health status has been stable (Healthy or Trending Down) for 2+ days
- Not shown for "Too early to assess" items

### Overnight Impact Summary (v6, Change 5)
- Single line below the status cards, above the first section
- Green tint background (`--act-green-bg`) with border, 8px radius
- savings icon + summary text
- Format: "ACT saved an estimated £X.XX overnight across Y actions — [breakdown]"
- Calculated from the sum of estimated savings in executed actions

### Empty States (v6, Changes 6-7)
- Shown when a section has zero active (non-actioned) items
- Centered layout: 28px icon (opacity 0.4) + 14px text
- Padding: 40px top/bottom for visual breathing room
- Per-section messages:
  - **Awaiting Approval:** green check_circle icon (full opacity) + "All clear — no actions need your review today"
  - **Actions Executed:** bedtime icon + "No actions were executed overnight."
  - **Currently Monitoring:** visibility_off icon + "Nothing is currently being monitored."
  - **Recent Alerts:** notifications_none icon + "No alerts in the last 7 days."
- Empty state appears dynamically when all approval items are actioned (JS checks after each approve/decline)
- Bulk bar is hidden when empty state is showing

### Before/After Value Pills (v2, Change 8)
- Old value: grey pill (`#e8eaed` bg, muted text)
- New value: coloured pill based on direction
  - Positive/gain: green pill
  - Negative/reduction: red pill
  - Neutral (e.g., "Added as [exact]"): blue pill
- Arrow separator between pills

### Badges
- **Level badges:** Title Case, 10px, 600 weight, 4px radius, pastel bg + dark text
- **Action badges:** Title Case, 10px, 700 weight, 4px radius, pastel bg + 1px border
- **Risk badges:** Title Case, 10px, 600 weight, 4px radius, same colours as action categories
- **Resolution badges:** same sizing, specific colours for Approved/Declined/Auto-resolved
- **Health labels:** 9px, 600 weight, 8px radius pill

### Progress Bars — Health Colour Coded (v2, Change 9)
- 4px height, 160px max-width
- Grey track (`--act-border-light`)
- Fill colour by health status:
  - Healthy: green (`--act-green`)
  - Trending Down: amber (`--act-amber`)
  - Too early to assess: grey (`#9aa0a6`)
- Health label pill alongside (green/amber/grey)
- Optional trend icon (trending_down)

### Buttons
- `btn-act--approve`: solid green (#34a853), white text
- `btn-act--decline`: white bg, border, grey text
- `btn-act--undo`: smaller, white bg, border
- `btn-act--details`: no bg, blue text, hover adds blue bg
- `btn-act--bulk`: solid blue (#1a73e8), white text
  - **Risk breakdown (v2, Change 11):** Shows "Approve Selected (4 low-risk, 1 medium-risk)" instead of just a count

### Slide-in Panel (v2, Change 13)
- Fixed right, 520px wide, full viewport height
- Replaces inline "View Details" expand
- Header: title + close button (X icon)
- Body: scrollable, contains item summary + recommendation + decision tree
- Footer: Approve/Decline buttons (for approval items)
- Overlay: `rgba(32,33,36,0.45)` — click to close
- ESC key closes
- Matches existing ACT flow-slide pattern from `rules.css`

### Decision Tree Key-Value Grid (v2, Change 12)
- CSS Grid: `80px` label column + `1fr` value column
- Labels: 11px, 700 weight, muted colour, capitalize
- Values: 12px, normal weight, secondary colour
- Row dividers: 1px `--act-border-light`
- Fields: Check, Signal, Rule, Cooldown, Risk

### Toast Notifications
- Fixed bottom-right, 8px radius
- Slides up with opacity transition (300ms)
- Auto-dismiss after 3s
- Colour matches type: success/info/warning/error

---

## Page 2: Client Configuration — New Patterns

### Settings Page Layout
- **Page header:** Title + subtitle + "Save Changes" (green) + "Reset to Defaults" (outline) + last-saved timestamp
- **Vertical tabs + content:** 200px tab nav on the left within the content card, content panel on the right
- Tab labels use v54 level colour as left-border accent when active
- Tabs: Account, Campaign, Keyword, Ad Group, Ad, Shopping, Onboarding

### Setting Row
- Two-column grid: info (1fr) + control (280px)
- Setting name: 14px, 600 weight
- Setting description: 14px, opacity 0.7
- Bottom border between rows, none on last
- Responsive: collapses to single column at 768px

### Form Inputs
- **Text/number input:** 14px font, 6px 12px padding, 6px radius, `var(--act-border)` border, `var(--act-surface)` bg
- **Input with suffix:** Input + attached suffix label (e.g., "£", "%", "days", "hours"). Suffix has `var(--act-hover-bg)` background
- **Select dropdown:** Same sizing as input, 200px default width
- **Toggle switch:** 44x24px, `var(--act-border)` off, `var(--act-green)` on. 20px white knob with slide animation
- **Multi-input row:** Flex layout with labels, for grouped inputs (scoring weights, signal windows, extension minimums)

### Validation Messages
- 12px text, 4px 8px padding, 4px radius
- Error: `var(--act-red-bg)` bg, `#991b1b` text
- Success: `var(--act-green-bg)` bg, `#065f46` text
- Hidden by default, shown with `.show` class

### Modifier Caps Table
- Full-width table within the Campaign settings panel
- Headers: 12px, 600 weight
- Cells: inline input groups (70px wide inputs)
- Rows: Device, Geo, Ad Schedule with Min Cap, Max Cap, Cooldown columns

### Onboarding Checklist
- Items: icon circle (24px) + title + status + optional expandable details
- Done icon: green tint bg (`var(--act-green-bg)`), `#065f46` text, check icon
- Pending icon: amber tint bg (`var(--act-amber-bg)`), `#92400e` text, pending icon
- Details panel: `var(--act-hover-bg)` bg, 6px radius, status dots (green/amber) before each sub-item
- "Run Onboarding" button: primary blue, rocket_launch icon

### Confirmation Dialog
- Centered overlay with `rgba(32,33,36,0.45)` backdrop
- Dialog: `var(--act-surface)` bg, 12px radius, 24px padding, shadow
- Title (16px, 600) + description (14px) + Cancel/Confirm buttons
- Confirm button uses `var(--act-red)` bg for destructive actions (reset)

---

## Page 3: Account Level — New Patterns

### Level Page Header
- 3px top border in the level's v54 colour (Account = `#3b82f6`)
- Title + subtitle + persona badge + key metrics row
- Reusable pattern for all level pages (Campaign, Ad Group, Keyword, Ad, Shopping)

### Health Summary Cards
- 4-column grid (collapses at breakpoints)
- Same card style as status cards but without left stripe
- 28px value, 12px label, 12px detail
- Optional progress bar (6px height, `var(--act-border-light)` track)
- Zone badge inline: Outperforming (green), On Target (blue), Underperforming (red)

### Data Tables (sortable)
- Full-width, 14px body text, 12px headers (600 weight)
- Click column headers to sort (unfold_more icon hint)
- Numeric columns right-aligned with `font-family: var(--act-font-mono)`, 12px
- Row hover: `rgba(0,0,0,0.015)` light / `rgba(255,255,255,0.03)` dark
- Expandable rows: hidden `score-breakdown-row` toggled by clicking score values

### Role Badges
- Same sizing as level badges (12px, 600 weight, 2px 8px padding, 4px radius)
- Colours match v54 level colours for the role's primary association:
  - BD (Brand Defence): `#dbeafe` / `#3b82f6` (blue)
  - CP (Core Performance): `#d1fae5` / `#10b981` (green)
  - RT (Retargeting): `#fce7f3` / `#ec4899` (pink)
  - PR (Prospecting): `#ede9fe` / `#8b5cf6` (purple)
  - TS (Testing): `#fef3c7` / `#f59e0b` (amber)

### Budget Share Bar (inline)
- Flex row: percentage text + 80px track (6px height) with coloured fill
- Fill colour matches performance: green (high score), red (low score)

### Stacked Budget Bar (visualisation)
- Horizontal bar, 32px height, rounded 6px, segments sized by budget share
- Segment colours: role colours (CP green, RT pink, BD blue, TS red for underperforming)
- Hover: tooltip with details (campaign name, daily budget, score)
- Legend below with colour dots

### Score Display
- Monospace, 14px, 700 weight
- Colour-coded: `#10b981` (high/good), `#f59e0b` (mid), `#ef4444` (low/bad)
- Clickable to expand scoring breakdown

### Score Breakdown (expandable)
- Hidden row below the data row, toggled on score click
- Shows 7d / 14d / 30d components with mini progress bars and point values
- `var(--act-hover-bg)` background, 6px radius

### Zone Badges
- Outperforming: `var(--act-green-bg)` / `#065f46`
- On Target: `var(--act-blue-bg)` / `#1e40af`
- Underperforming: `var(--act-red-bg)` / `#991b1b`

### Cooldown Badges
- Ready: `var(--act-green-bg)` / `#065f46`
- Active: `var(--act-amber-bg)` / `#92400e` + time remaining

### Trend Arrows
- Good trend: `#10b981` (CPC down or CVR up)
- Bad trend: `#ef4444` (CPC up or CVR down)
- Flat: `var(--act-text)` at opacity 0.5
- Direction meaning is context-dependent (down CPC = good, down CVR = bad)

### Guardrails List
- `<ul>` with icon + label + right-aligned value
- Icons: Material Symbols 18px in `var(--act-amber)`
- Values: monospace 12px, 600 weight, right-aligned

### Recommendation Box (reusable)
- `var(--act-rec-bg)` background, 6px radius, 12px 16px padding
- Lightbulb icon + text + Approve/Decline buttons (right-aligned)
- Same approve/decline pattern as Morning Review

### Level Page Structure (v9 — established on Account Level)
Every level page follows this structure top-to-bottom:
1. **Page header** — level colour accent, title, subtitle, persona badge, key metrics, "ACT last ran" green pill (required on every level page)
2. **ACT health cards** — level-specific health summary (4-column grid)
3. **Combined Performance section** (collapsible) — single section containing:
   - Summary metric cards (7-column grid, 28px values)
   - Performance timeline chart (Chart.js, dual Y-axis)
   - Familiar data table (Google Ads columns + ACT additions)
   - Date range pills in section header control both chart and table
   - Header context note: "[Section Name] — [count] [items], [N] days"
4. **Level-specific review sections** — same 4 Morning Review sections (Approval, Executed, Monitoring, Alerts) filtered to that level only. Uses exact same component patterns from Morning Review.
5. **ACT intelligence sections** (collapsed by default) — level-specific analysis (budget allocation, signal decomposition, guardrails etc.)

This hybrid approach makes the page useful to both ACT users (review sections, intelligence) and Google Ads users (familiar campaign data).

### Summary Metric Cards (inside combined section)
- 7-column grid (collapses at breakpoints)
- 28px value (same size as health cards), 12px label
- Change indicator: `summary-card__change--up` (green), `--down` (red), `--flat` (neutral)
- Shows period-over-period comparison (arrow + percentage)

### Table Toolbar (date range + filters)
- Sits in section header, right-aligned
- **Pill button groups:** `pill-group` container with `pill-btn` buttons
  - Active pill: `var(--act-surface)` bg + subtle shadow
  - Hover: `rgba(0,0,0,0.05)` / `rgba(255,255,255,0.05)` dark
  - Font: 12px, 600 weight
- Date range: 7d / 30d / 90d
- Status filter: All / Enabled / Paused

### Status Dots
- 8px circle, inline in table
- Enabled: `#10b981` (green)
- Paused: `#9ca3af` (grey)

### Pagination
- `table-pagination` bar below table
- Left: "Showing X-Y of Z campaigns"
- Right: page buttons with active state using `var(--act-primary)`

### Section Dividers
- Title Case label (14px, 600 weight, 0.5 opacity) with bottom border
- Separates major page areas: "Account-Level Review", "Budget Allocation"
- No uppercase (fixed in v4)

---

## Performance Timeline Chart (v8-v10)

### Chart Component
- **Library:** Chart.js 4.4 (CDN, already in ACT stack)
- **Type:** Line chart, `tension: 0` (straight lines between points, no bezier curves — matches Google Ads style)
- **Dual Y-axes:** Left axis for metric 1, right axis for metric 2
- **Two dropdown selectors** above the chart, each with a colour dot indicator
- **Metric options** (in this exact order):
  1. Cost
  2. Impressions
  3. Clicks
  4. Avg CPC
  5. CTR
  6. Conversions
  7. CPA (Cost/Conv)
  8. Conv Rate
  9. Performance Score
  10. Budget Utilisation %
- **Default selection:** Metric 1 = Cost, Metric 2 = Conversions
- **Line colours:** Metric 1 = level colour (e.g., `#3b82f6` for Account Level). Metric 2 = `#10b981` (green)
- **Visual:** Light fill under each line, data point markers (radius 3, hover radius 5), clean grid lines
- **Tooltips:** `interaction.mode: 'index'` — hover shows both metrics. Title = date, body = "Metric: £value" or "Metric: value%"
- **Axis labels:** Left Y-axis title = metric 1 name (coloured to match line), right Y-axis title = metric 2 name
- **Chart height:** 280px container, full content width
- **Dark mode:** Auto-rebuilds on theme toggle. White ticks/text, `rgba(255,255,255,0.06)` grid, `#1e293b` tooltip bg

### Chart Date Range Intervals
Date range pills control the chart's X-axis intervals:

| Range | Interval | Data Points | Aggregation |
|-------|----------|-------------|-------------|
| 7d | Daily | 7 | Raw daily values |
| 30d (default) | Daily | 30 | Raw daily values |
| 90d | Weekly | ~13 | SUM for volume metrics (Cost, Impressions, Clicks, Conversions). AVERAGE for rate metrics (CPC, CTR, CPA, Conv Rate, Score, Budget Util %) |

X-axis labels: "D Mon" format (e.g., "15 Mar"). `maxRotation: 0` with `autoSkipPadding: 12` for clean horizontal labels.

### Combined Chart + Table Section Pattern
A single collapsible section containing summary cards, chart, and data table:
- **Section header:** `[Section Name] — [count] [items], [N] days` with date range pills and status filter pills right-aligned
- **Header context note:** Updates dynamically when date range changes (e.g., "4 campaigns, 30 days" → "4 campaigns, 7 days")
- **Date range pills** control BOTH chart and table — switching range rebuilds the chart AND updates all table cell values + totals row + summary cards
- **Contents (in order):**
  1. Summary metric cards (inside `perf-inner` padding wrapper)
  2. Chart with metric selectors
  3. Data table with sortable columns
  4. Totals/averages row at bottom of table
  5. Pagination bar
- **Table data per range:** 7d shows ~1/4 of 30d values. 90d shows ~3x of 30d values. Totals row recalculates.

---

## Page 4: Campaign Level — New Patterns

### Campaign Selector
- Dropdown in page header showing all campaigns in the account
- `font-size: 14px; font-weight: 600;` styled as a form select
- Focus border uses level colour (`#10b981` for Campaign)
- Switching campaigns updates the entire page (prototype shows toast)

### Campaign Info Row
- Below the campaign selector in the page header
- Shows: strategy badge, status dot, daily budget, campaign role badge
- Flex row with 12px gap, wraps on small screens

### Strategy Badge
- `font-size: 12px; font-weight: 600; padding: 3px 10px; border-radius: 4px`
- Blue tint: `var(--act-blue-bg)` / `#1e40af`
- Shows bid strategy + target: "Maximise Conversions — tCPA £25"

### Universal Lever Cards
- One card per lever (Negative Keywords, Device, Geo, Schedule, Match Types)
- Collapsible with expand/collapse toggle — **collapsed by default**
- Header: icon (green `#10b981`) + lever name + summary text + chevron
- Body: detail table or visualisation + cooldown info note
- Tables inside lever cards use `.lever-table` (same left-alignment rules)

### Lever Detail Tables
- Used inside lever cards for device/geo/schedule modifiers
- Columns: name, modifier value, last changed date, cooldown status badge
- Same `cooldown-badge--ready` (green) and `cooldown-badge--active` (amber) patterns

### Match Type Distribution Bar
- Horizontal stacked bar: Broad (red `#ef4444`), Phrase (amber `#f59e0b`), Exact (green `#10b981`)
- 24px height, 4px radius, with legend below

### Strategy Panel
- Shows inside a collapsible section for the active bid strategy
- Current target value (28px), zone badge, last adjustment, next review date
- Adjustment history table (date, change, reason)
- Supported strategies list: 7 pill badges, active one highlighted with green tint
- Guardrails note at bottom

### Strategy List Pills
- Flex row of small pill badges (12px, 3px 10px padding, 4px radius)
- Default: `var(--act-border-light)` border
- Active: `var(--act-green-bg)` + `#065f46` text + `var(--act-green-border)` border + bold

---

## Top Bar Components

### ACT Last Ran (v2 Change 10; v4 Change 7 — required on all pages)
- Green pill with check_circle icon
- Text: "ACT last ran: Today at 05:17 AM"
- Positioned in top bar left area, after date
- **Required on every level page** (Account, Campaign, Ad Group, Keyword, Ad, Shopping) and Morning Review
- Background: `--act-green-bg`, border: `--act-green-border`

### Theme Toggle (v2, Change 14)
- 48x24px toggle with animated sun/moon
- Sky gradient background, stars appear in dark mode
- Moon has crater details (::before, ::after pseudo-elements)
- 400ms delay before page theme switches (toggle leads visually)
- Horizon glow during transition
- Positioned in top bar right area, between client switcher and user avatar

---

## Dark Theme (v2, Change 14)

Activated via `data-theme="dark"` on `<html>`. All colours use CSS custom properties, so the theme switch is automatic.

Key dark values:
- Page bg: `#0a0e17` (deep navy)
- Surface: `#111827` (dark slate)
- Text: `#f1f5f9` (near-white)
- Borders: `#1e293b` (subtle)
- Category backgrounds: semi-transparent versions of light theme colours

---

## Sidebar Navigation

- Grouped by section labels (REVIEW, OPTIMIZATION, SETTINGS — uppercase exception)
- Dividers between groups
- Active state: `--act-primary-bg` + `--act-primary` text
- Icons: Material Symbols Outlined, 20px
- Existing pages (Jobs, Outreach, Changes) included as nav links only

---

## Icons

Using **Google Material Symbols Outlined** throughout:
- Sidebar nav: 20px
- Section headers: 18px
- Inline (recommendations, toasts): 14-18px
- Time waiting: 12px
- Health labels: 12px
- Key icons: `wb_sunny`, `pending_actions`, `check_circle`, `visibility`, `notifications_active`, `lightbulb`, `expand_more`, `trending_down`, `schedule`, `close`

---

## Client Switcher

- Top bar, right-aligned
- Green dot + client name + expand_more chevron
- Dropdown: standard Bootstrap-style, right-aligned
- Active client marked
- Switching shows toast confirmation

---

## Interactive Behaviours

| Interaction | Behaviour |
|-------------|-----------|
| Status card click | Filters page to show only matching section; click again to show all |
| Section header click | Toggle collapse/expand |
| Group header click | Toggle group collapse/expand (v2) |
| View Details | Opens slide-in panel from right with full decision tree (v2) |
| Approve | Fades item, decrements counter, closes slide-in, shows success toast |
| Decline | Fades item, decrements counter, closes slide-in, shows info toast |
| Undo | Fades item, shows warning toast |
| Bulk select all | Checks all approval items, updates risk breakdown in button |
| Bulk approve | Fades all checked items, shows count in toast |
| Client switcher | Swaps client name in button, shows info toast |
| Theme toggle | Animated sun→moon or moon→sun, 400ms delay before page theme switch |
| Slide-in close | Click overlay, click X, or press ESC |

---

## Responsive Breakpoints

| Breakpoint | Changes |
|------------|---------|
| ≤ 1024px | Status cards → 2 columns |
| ≤ 768px | Sidebar slides off-screen, main content full width, slide-in → full width |
| ≤ 480px | Status cards → 1 column, action buttons wrap |

---

## File Structure

```
act_dashboard/prototypes/
  index.html              Morning Review v1
  index-v2.html           Morning Review v2 (14 changes)
  index-v3.html           Morning Review v3 (7 further changes)
  index-v4.html           Morning Review v4 (5 further changes, expanded data)
  index-v5.html           Morning Review v5 (full v54 colour alignment)
  index-v6.html           Morning Review v6 (date/time, impact, empty states)
  client-config.html      Client Configuration (Page 2)
  account-level.html      Account Level v1 (Page 3)
  account-level-v2.html   Account Level v2 (review sections + campaigns table)
  account-level-v3.html   Account Level v3 (reordered, score breakdowns, impact/started)
  account-level-v4.html   Account Level v4 (system font, alignment, totals, title case)
  account-level-v5.html   Account Level v5 (even column widths)
  account-level-v6.html   Account Level v6 (equal-width sig/hist tables)
  account-level-v7.html   Account Level v7 (left-aligned tables, CPA Trend column)
  account-level-v8.html   Account Level v8 (performance timeline chart)
  account-level-v9.html   Account Level v9 (combined section, straight lines, shared date range)
  account-level-v10.html  Account Level v10 (table data per range, 90d weekly aggregates)
  campaign-level.html     Campaign Level (Page 4)
  table-test.html         Standalone table alignment test page
  screenshots/            Browser screenshots
  css/
    prototype.css         v1 styles
    prototype-v2.css      v2 styles
    prototype-v3.css      v3 styles
    prototype-v4.css      v4 styles
    prototype-v5.css      v5 styles
    prototype-v6.css      v6 styles (impact, started, streak, empty state CSS)
    prototype-v7.css      v7 styles (base for config page)
    client-config.css     Client Configuration page styles
    account-level.css     Account Level v1 styles
    account-level-v2.css  Account Level v2 styles
    account-level-v3.css  through v10 (incremental changes per version)
    campaign-level.css    Campaign Level styles (lever cards, strategy panel, match bar)
  js/
    prototype.js          v1 interactions
    prototype-v2.js       v2 interactions
    prototype-v3.js       v3 interactions
    prototype-v4.js       v4 interactions
    prototype-v5.js       v5 interactions
    prototype-v6.js       v6 interactions (empty state logic + checkEmptyStates)
    prototype-v7.js       v7 interactions
    client-config.js      Client Configuration interactions
    account-level.js      Account Level v1 interactions
    account-level-v2.js   through v10 (incremental changes per version)
    campaign-level.js     Campaign Level interactions (campaign selector, chart, levers)
```

---

## Dependencies

- Bootstrap 5.3.2 (CDN) — grid, utilities, dropdown
- Material Symbols Outlined (Google Fonts CDN) — icons
- DM Mono (Google Fonts CDN) — monospace values

---

## Design Decisions Log

1. **Sidebar width: 220px** (vs 110px in existing app) — the optimization levels have longer labels that benefit from a wider sidebar with horizontal text layout rather than stacked icon-only nav.
2. **Section labels in sidebar** (REVIEW, OPTIMIZATION, SETTINGS) — groups related nav items, makes the hierarchy clear at a glance.
3. **4px left colour stripe on status cards** — subtle but immediately communicates category.
4. **Collapsible sections with chevron** — keeps the page scannable.
5. **Bulk approve in a fixed bar** — stays visible at top of approval section.
6. **Before→After values in monospace** — makes numerical changes instantly scannable.
7. **Recommendation line with lightbulb icon** — separates "what happened" from "what ACT suggests".
8. **Toast notifications instead of modals** — non-blocking feedback, auto-dismiss.
9. **No framework (vanilla JS)** — prototype simplicity, easy to port to Flask templates later.
10. **CSS custom properties for all colours** — single source of truth, easy to theme or adjust.
11. **(v2) No all-caps** — Title Case throughout for readability. Uppercase felt aggressive and less professional.
12. **(v2) Entity-level grouping** — reduces visual noise by clustering related items. Collapsible so users can focus on what matters.
13. **(v2) Alert-first ordering** — most urgent items at the top where they'll be seen first.
14. **(v2) Only Awaiting Approval expanded** — the morning review should focus attention on what needs action. Other sections are one click away.
15. **(v2) Risk badge always visible** — the user shouldn't need to expand details just to see risk level. Reduces clicks for the common case.
16. **(v2) Red tint on Alert items** — visual urgency without being overbearing. The faint red bg makes alerts scannable even in a long list.
17. **(v2) Value pills instead of strikethrough** — the grey/coloured pill pattern is more scannable than strikethrough text, and the colour indicates whether the change was positive or negative.
18. **(v2) Health-coded progress bars** — green/amber/grey is immediately readable. Blue was too neutral and didn't convey status.
19. **(v2) Slide-in panel for details** — keeps the approval list compact. Users can review details without losing their scroll position. Matches the existing ACT pattern from rules.css.
20. **(v2) Key-value grid for reasoning** — two-column layout is faster to scan than paragraphs. Labels on left, values on right.
21. **(v2) Dark mode** — matches the ACT architecture document's theme toggle. Important for late-night account reviews and user preference.
22. **(v2) Risk breakdown in bulk approve** — "4 low-risk, 1 medium-risk" is more informative than "5" and helps users make confident bulk decisions.
23. **(v3) No red background on Alert items** — the 3px red left border is sufficient visual distinction. The background tint competed with the recommendation highlight and made the item feel "broken".
24. **(v3) Nearly-invisible group headers** — at `rgba(0,0,0,0.015)`, group headers separate without competing. They're structural dividers, not action elements.
25. **(v3) Prominent recommendation line** — 14px body-size text on a light blue background makes the "what to do" immediately scannable. Problem (summary) first, then solution (recommendation).
26. **(v3) 5-value font scale** — eliminates visual noise from inconsistent sizing. Nothing below 12px ensures readability. The 5 sizes (28/20/16/14/12) create clear hierarchy without ambiguity.
27. **(v3) No grey text** — pure black/white with brand colours only. Grey text creates a hierarchy problem where important information (timestamps, labels) becomes invisible. Black/white + opacity is more accessible.
28. **(v3) View Details stays clickable after action** — the user might approve then want to double-check reasoning, or need to reference the decision tree when explaining to a client. Hiding it after action felt punitive.
29. **(v3) Cooldown info on approval items** — shows the commitment being made. "14-day cooldown after approval" helps the user weigh whether now is the right time to act. Only shown when a cooldown exists (approval-only actions like keyword discovery have none).
30. **(v4) Halved recommendation padding** — `4px 6px` instead of `8px 12px`. The blue background already provides visual separation; the extra padding was wasting vertical space, especially with 13+ approval items.
31. **(v4) v54 architecture level colours** — Account (blue #3b82f6), Campaign (green #10b981), Ad Group (amber #f59e0b), Keyword (purple #8b5cf6), Ad (pink #ec4899), Shopping (teal #14b8a6). Each level now has a distinct colour that matches the finalised architecture document.
32. **(v4) Grey Low Risk badge** — green was creating false urgency (green = "Act" in our system). Low Risk is neutral information, so grey (#6b7280 light, #9ca3af dark) is the right signal. Medium stays amber, High stays red.
33. **(v4) Status card reorder** — Awaiting Approval first (needs action), then Alerts (urgent awareness), then Actions Executed (review), then Monitoring (passive). Left-to-right priority matches the user's morning review workflow.
34. **(v4) Medium-account scale data** — 13 approval items, 18 executed, 9 monitoring, 5 alerts. This tests how the page feels with real-world volume and validates that grouping, collapsing, and bulk actions work at scale.
35. **(v5) Full v54 Design System colour alignment** — replaced all Google Material colours with v54 hex codes. Zero legacy hex codes remain after grep verification.
36. **(v6) Monitoring start dates** — "Started: 4 Apr 2026, 05:10 AM" removes ambiguity about when a cooldown began. Without this, "48h remaining" doesn't tell you when the 72h started.
37. **(v6) Dates on executed timestamps** — "6 Apr, 05:14 AM" instead of just "05:14 AM". The log may span multiple days in future, and the date provides context even for overnight-only runs.
38. **(v6) Estimated impact on approval items** — "Estimated saving: £75/month" or "Estimated: +3 conversions/month" gives the user a reason to act. Abstract recommendations like "review structure" are harder to prioritise without knowing the potential payoff.
39. **(v6) Consecutive days streaks** — "Healthy for 2 consecutive days" shows trend momentum. A keyword that's been trending down for 5 days is more concerning than one trending down for 1 day. Only shown for 2+ day streaks, not for "Too early to assess" items.
40. **(v6) Overnight impact summary** — "ACT saved an estimated £18.40 overnight across 18 actions" reinforces the value of ACT every single morning. It's the first thing the user reads after the status cards — a daily proof of ROI.
41. **(v6) Empty states** — "All clear — no actions need your review today" with a green checkmark is the best possible outcome for a morning review. Empty states also prevent confusing blank sections and provide positive reinforcement when the account is running well.
42. **(Page 2) Vertical tabs for settings** — 7 sections with 40+ settings is too much for a single scrollable page. Vertical tabs keep the sidebar nav visible while providing a secondary nav within the content area. Tab labels use v54 level colours as accents.
43. **(Page 2) Two-column setting layout** — name+description on the left, control on the right. This keeps settings scannable and prevents the eye from jumping between description and input. Grid collapses to single column on mobile.
44. **(Page 2) Input groups with suffixes** — "72 hours", "10 %", "£25" — the suffix removes ambiguity about the unit. Attached visually to the input so they read as one element.
45. **(Page 2) Persona-dependent fields** — changing persona hides/shows Target CPA vs Target ROAS. This prevents confusion about which field applies and reduces visual clutter for the wrong persona.
46. **(Page 2) Onboarding checklist** — not a settings section, but a setup status tracker. Done/Pending icons provide instant visual status. The "Run Onboarding" button is a one-click setup for new clients.
47. **(Page 3) Level colour accent on page header** — 3px top border in the level's v54 colour instantly tells the user which level they're on. Reusable across all 6 level pages.
48. **(Page 3) Sortable data tables** — click any column header to sort. Essential for a 4-campaign table, critical when accounts have 10+ campaigns. Sort icons hint at interactivity.
49. **(Page 3) Inline score breakdown** — clicking a score expands the calculation (7d/14d/30d) in a hidden row. Keeps the table compact while making the scoring transparent.
50. **(Page 3) Stacked budget bar** — horizontal segments sized by budget share, coloured by role. Hover tooltips show exact values. This is the visual centrepiece — the user sees the budget split at a glance.
51. **(Page 3) Budget recommendation with Approve/Decline** — same pattern as Morning Review. The recommendation originates here (Account Level) and surfaces in the Morning Review as an approval item. Consistency across pages.
52. **(Page 3) Context-dependent trend arrows** — down CPC is green (good), down CVR is red (bad). The arrow colour reflects whether the direction is beneficial, not just the direction itself.
53. **(Page 3 v2) Hybrid page structure** — ACT intelligence (review sections, budget allocation, signals) alongside familiar Google Ads data (campaigns table with standard columns). Google Ads users see what they expect; ACT adds Role, Budget Share, and Performance Score as additions, not replacements.
54. **(Page 3 v2) Level-filtered review sections** — same 4 Morning Review sections but filtered to Account Level items only. This means the user can see both the global picture (Morning Review) and the level-specific picture (Account Level page) using identical components.
55. **(Page 3 v2) Summary metric cards above campaigns table** — Total Cost, Impressions, Clicks, Avg CPC, Conversions, Avg CPA, Conv Rate. Period-over-period change indicators. Matches the Google Ads overview pattern users are familiar with.
56. **(Page 3 v2) Date range + status filter pills** — 7d/30d/90d date range and All/Enabled/Paused status filter. Compact pill groups in the table header. Immediately recognisable to Google Ads users.
