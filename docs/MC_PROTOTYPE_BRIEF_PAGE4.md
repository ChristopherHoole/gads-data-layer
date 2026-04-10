# MC ACT Prototype — Page 4: Campaign Level
**Session:** MC ACT Prototype (continued)
**Date:** 2026-04-08
**Objective:** Build an interactive HTML prototype of the Campaign Level page. This is the most complex level page — it covers universal levers (device, geo, schedule, negatives, match types) and 7 strategy-specific bid optimization rule sets.

---

## IMPORTANT: FOLLOW EXISTING STANDARDS

Read `docs/ACT_PROTOTYPE_STANDARDS.md` before starting. All patterns from Pages 1-3 must be followed exactly. Pay particular attention to:
- Level Page Structure standard (v9 pattern)
- Combined Chart + Table Section pattern
- Performance Timeline Chart pattern
- Table Alignment standard (all left-aligned)
- No all-caps
- v54 colour system

---

## Context

Read the Campaign Level section in `docs/ACT_OPTIMIZATION_ARCHITECTURE_v54.html` — this is your source of truth for everything on this page. Read the full section carefully — it's the longest level page with 5 universal levers and 7 strategy-specific lever rule sets.

Reuse the app shell from previous pages (sidebar with Campaign Level highlighted, top bar, client switcher, dark/light toggle, "ACT last ran" timestamp).

---

## Page Structure (following the Level Page Structure standard)

The Campaign Level page follows the same hybrid structure established on Account Level:

1. **Page header** — green (#10b981) level accent, title, subtitle
2. **Health summary cards** — campaign-level health metrics
3. **Campaign Performance section** — combined: summary metric cards + timeline chart + ad groups data table
4. **Campaign-Level Review sections** — Awaiting Approval, Actions Executed, Monitoring, Alerts (filtered to Campaign Level only)
5. **Universal Levers section** — device, geo, schedule, negatives, match types
6. **Strategy-Specific section** — showing the active bid strategy and its lever status
7. **Guardrails section** — campaign-level guardrails

---

## Important: This Page Shows ONE Campaign at a Time

Unlike the Account Level page which shows all campaigns in a table, the Campaign Level page shows the detail for ONE selected campaign. The user selects which campaign to view.

Add a **campaign selector** in the page header — a dropdown showing all campaigns from the account. Default to the first active campaign.

Example: "GLO Campaign — Core ▼" with dropdown showing all 4 campaigns.

When the user switches campaigns, the entire page updates with that campaign's data (health cards, chart, table, review sections, levers, strategy).

---

## Section 1: Page Header

- Level colour accent: green (#10b981) — 3px top border
- Page title: "Campaign Level"
- Subtitle: "Optimization Within Each Campaign"
- Campaign selector dropdown: "GLO Campaign — Core ▼"
- Campaign info row: Bid Strategy badge (e.g., "Maximise Conversions — tCPA £25"), Status (Enabled), Daily Budget (£30), Campaign Role badge (CP)

---

## Section 2: Health Summary Cards

4 cards showing this campaign's current state:

| Card | Content | Detail |
|------|---------|--------|
| Campaign Cost (MTD) | £487 | Daily avg: £16.23 |
| Campaign CPA | £18.50 | Target: £25 (26% below — Outperforming) |
| Conversions (MTD) | 26 | vs 22 last period (+18%) |
| Quality Score Avg | 6.2 | Across all keywords in this campaign |

Use the same zone badge pattern (Outperforming/On Target/Underperforming).

---

## Section 3: Campaign Performance (Combined Section)

Follow the Combined Chart + Table Section pattern from Account Level.

**Header:** "Campaign Performance — 5 ad groups, 30 days" with date range pills (7d/30d/90d) and status filters (All/Enabled/Paused).

**Summary metric cards:** Cost, Impressions, Clicks, Avg CPC, CTR, Conversions, CPA, Conv Rate — for this campaign only.

**Timeline chart:** Same as Account Level — dual axis, metric dropdowns, straight lines, hover tooltips. Chart line 1 colour: #10b981 (campaign green). Date range controls chart + table.

**Data table:** Ad Groups table (not campaigns — we're inside a campaign now). Columns:
- Status (dot)
- Ad Group name
- Cost
- Impressions
- Clicks
- Avg CPC
- CTR
- Conversions
- Cost/Conv
- Conv Rate
- Ads (count of active ads)
- Keywords (count of active keywords)

Sortable, with totals/averages row. Left-aligned throughout.

**Sample data:** 5 ad groups within GLO Campaign — Core:
- Dental Implants (main volume)
- Cosmetic Dentistry
- General Dentistry
- Emergency Dental
- Veneers & Whitening

Use realistic metrics — dental implants should have the highest CPC (£8-12) and the most spend.

---

## Section 4: Campaign-Level Review Sections

Same 4 sections as Morning Review, filtered to Campaign Level items only. Use the exact same component patterns.

**Sample data — create 3-4 approval items, 4-5 executed actions, 2-3 monitoring items, 1-2 alerts. All campaign-level actions from v54:**

Approval items (Investigate/Alert):
- "Loosen tCPA target from £25 to £27.50 — CPA is 26% below target for 14 consecutive days"
- "Reduce Scotland geo modifier from +0% to -15% — CPA 45% above target over 30 days"
- "Increase Monday ad schedule bid from +0% to +15% — Monday CPA £14.20 vs £22.50 avg"

Executed items (Act):
- "Reduced Sunday ad schedule modifier from +0% to -20% — Sunday CPA £34.50 vs £22.50 avg"
- "Reduced tablet device modifier from -20% to -35% — tablet CPA 40% above target over 7 days"
- "Added 4 negative keywords from search term mining"
- "Mobile device modifier confirmed at +10% — mobile CPA on target"

Monitoring items:
- "tCPA adjustment cooldown — changed from £23 to £25. 10 days remaining of 14-day cooldown"
- "Device bid cooldown (tablet) — 5 days remaining of 7-day cooldown"

Alerts:
- "Geo modifier cap reached — Scotland at -50% (maximum cap). Investigate if this location should be excluded entirely"

---

## Section 5: Universal Levers

This section shows the status of the 5 universal levers that apply to all campaign types (except PMax which only uses negatives).

**Layout:** 5 cards/panels, one per lever. Each shows:
- Lever name with icon
- Current status (active adjustments or "No adjustments")
- Last modified date
- Cooldown status (if applicable)
- Quick summary of current settings

### 5.1 Negative Keywords
- Count of negative keywords applied to this campaign
- Last added date
- Link to Keyword Level for full management
- Summary: "142 negative keywords across 9 lists"

### 5.2 Device Modifiers
- Table showing current modifiers: Mobile (+10%), Desktop (+0%), Tablet (-35%)
- Current caps: Min -60%, Max +30%
- Cooldown: 7-day per device type
- Last changed: date per device

### 5.3 Geographic Modifiers
- Table showing current geo modifiers (top 5 locations)
- Current caps: Min -50%, Max +30%
- Cooldown: 30-day per location
- Last changed: date

### 5.4 Ad Schedule Modifiers
- Table/grid showing day + time block modifiers (like Google Ads ad schedule view)
- Current caps: Min -50%, Max +25%
- Cooldown: 30-day per time slot
- Last changed: date

### 5.5 Match Type Distribution
- Bar or pill display showing match type breakdown: Broad (X%), Phrase (Y%), Exact (Z%)
- Link to Keyword Level for full management

**Interactive:** Each lever card is expandable to show full details. Collapsed by default — show just the summary line.

---

## Section 6: Strategy-Specific Lever

This section shows the bid strategy specific to this campaign and its current optimization status.

**The content of this section changes depending on the campaign's bid strategy.** Show a strategy badge at the top, then the relevant content.

For the prototype, show the **tCPA strategy** (since GLO Campaign uses Maximise Conversions with tCPA):

### tCPA Strategy Panel
- Current target CPA: £25
- ACT's assessment: "On target — CPA is 26% below target"
- Last adjustment: "Raised from £23 to £25 on 1 Apr 2026"
- Next review eligible: "15 Apr 2026 (14-day cooldown)"
- Adjustment history (last 5 changes): date, old → new, reason
- Guardrails: max single move 10%, loosening requires approval, tightening auto-executes

**Also show a small note listing all 7 strategies ACT supports:** Manual CPC, tCPA, tROAS, Maximize Conversions, Max Clicks, PMax, Standard Shopping — with the active one highlighted. This shows the user that ACT adapts to whatever strategy is in use.

---

## Section 7: Guardrails

Campaign-level guardrails from v54. Show as a list matching the Account Level guardrails pattern:

- Device modifier caps: -60% / +30%
- Geo modifier caps: -50% / +30%
- Schedule modifier caps: -50% / +25%
- tCPA max single move: 10%
- tCPA cooldown: 14 days
- Device bid cooldown: 7 days
- Geo bid cooldown: 30 days
- Schedule bid cooldown: 30 days
- Match type migration: enabled/disabled
- Search Partners opt-out check: enabled/disabled

Collapsible, collapsed by default.

---

## Interactive Behaviours

1. **Campaign selector dropdown** — switches all page data to the selected campaign
2. **Combined performance section** — chart + table share date range, collapsible
3. **Review sections** — same as Morning Review (approve/decline, slide-in details, bulk approve)
4. **Universal lever cards** — expand/collapse to show details
5. **Strategy section** — adjustment history expandable
6. **All sections collapsible** — only Campaign Performance and Review (Awaiting Approval) expanded by default

---

## Sample Data

Use "GLO Campaign — Core" as the default campaign with:
- Bid strategy: Maximise Conversions with tCPA £25
- Role: CP (Core Performance)
- Daily budget: £30
- 5 ad groups (Dental Implants, Cosmetic, General, Emergency, Veneers)
- Dental market-realistic metrics (high CPCs £5-12, competitive conv rates 3-8%)

---

## Browser Verification

1. Test campaign selector switching
2. Test chart with all 3 date ranges
3. Test ad groups table sorting
4. Test review section interactions (approve, decline, slide-in)
5. Test universal lever cards expand/collapse
6. Check dark mode
7. Save screenshots to `act_dashboard/prototypes/screenshots/`

---

## Deliverables

1. `act_dashboard/prototypes/campaign-level.html` — working interactive Campaign Level page
2. Updated `docs/ACT_PROTOTYPE_STANDARDS.md` with any new patterns (campaign selector, lever cards, strategy panel)
3. Screenshots saved to folder

---

**END OF BRIEF**
