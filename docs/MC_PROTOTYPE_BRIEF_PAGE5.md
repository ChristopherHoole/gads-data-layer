# MC ACT Prototype — Page 5: Ad Group Level
**Session:** MC ACT Prototype (continued)
**Date:** 2026-04-09
**Objective:** Build an interactive HTML prototype of the Ad Group Level page. This follows the same pattern as Account Level and Campaign Level — a familiar data table view with ACT's optimization intelligence layered on top.

---

## IMPORTANT: FOLLOW EXISTING STANDARDS

Read `docs/ACT_PROTOTYPE_STANDARDS.md` before starting. All patterns from Pages 1-4 must be followed exactly.

Key standards to follow:
- Level Page Structure (hybrid: data table + ACT intelligence)
- Combined Chart + Table Section pattern
- Performance Timeline Chart pattern (dual axes, straight lines, metric dropdowns)
- Table Alignment: all left-aligned
- No all-caps
- v54 colour system (Ad Group level colour = amber #f59e0b)
- Slide-in detail pattern from Campaign Level Option D v10

---

## Context

Read the Ad Group Level section in `docs/ACT_OPTIMIZATION_ARCHITECTURE_v54.html` — source of truth.

Key points from v54 for Ad Group Level:
- 4 independent checks (run in parallel, all monitoring/flagging only — no auto-execution at this level):
  1. Negative Performance Outliers (30% of campaign spend, 50%+ worse performance than campaign average)
  2. Positive Performance Outliers (40%+ better than campaign average — promote to standalone campaign)
  3. Budget Concentration Alerts (1/2/3+ active ad group context checks)
  4. Pause Recommendations (21+ days zero conversions, 30+ days inactive, 30+ days despite optimizations)
- **All actions at this level require approval** — ACT flags but doesn't auto-execute
- No bid adjustments at this level (those live at Campaign and Keyword levels)

Reuse the app shell from previous pages (sidebar with Ad Group Level highlighted, top bar, client switcher, dark/light toggle, "ACT last ran" timestamp).

---

## Page Structure

Follow the same hybrid structure as Campaign Level (Option D) — Google Ads-style list view with slide-in detail.

### Main Page (always visible):

1. **Page header** — amber (#f59e0b) level accent, title "Ad Group Level", subtitle "Outlier Detection & Structural Health"
2. **Health summary cards** — 4 cards showing account-wide ad group health
3. **Ad Group Performance (combined section)** — summary metric cards + timeline chart + ad groups data table
4. **Ad Group-Level Review sections** — Awaiting Approval, Actions Executed, Currently Monitoring, Recent Alerts (filtered to ad group level items only). Grouped by campaign name.
5. **Guardrails** — ad group level guardrails

### Slide-in Panel (800px, opens when clicking an ad group name):

Shows the full detail for that specific ad group:

1. **Ad group header** — ad group name, campaign badge, status, keyword count, ad count
2. **Health cards** — 4 cards (cost MTD, CPA with zone badge, conversions MTD, QS average) — single row
3. **Awaiting Approval** (expanded by default) — this ad group's flagged items grouped by check type (Negative Outlier, Positive Outlier, Concentration, Pause Candidate)
4. **Actions Executed Overnight** (collapsed) — changes affecting this ad group (e.g., keywords added/paused at keyword level)
5. **Currently Monitoring** (collapsed) — items in monitoring state
6. **Recent Alerts** (collapsed) — historical alerts
7. **Outlier Analysis** (collapsed) — compact analysis showing how this ad group compares to others in the campaign:
   - Cost share of campaign
   - CPA vs campaign average
   - Conversion rate vs campaign average
   - Performance delta
8. **Structural Health** (collapsed) — ad group structural metrics:
   - Keyword count
   - Ad count
   - Average Quality Score
   - Days since last change
   - Days since last conversion

All sections collapsible. Only Awaiting Approval expanded by default.

---

## Section Details

### Health Summary Cards (Main Page)

4 cards showing account-wide ad group health:

| Card | Content |
|------|---------|
| Total Ad Groups | 18 (across 4 campaigns) |
| Avg CPA | £22.10 |
| Flagged Ad Groups | 3 (require review) |
| Concentration Alerts | 1 (1 ad group consumes 95% of campaign spend) |

### Ad Group Performance Combined Section (Main Page)

Follow the Combined Chart + Table Section pattern.

**Header:** "Ad Group Performance — 18 ad groups, 30 days" with date range pills (7d/30d/90d) and status filters (All/Enabled/Paused).

**Summary metric cards:** Total Cost, Impressions, Clicks, Avg CPC, CTR, Conversions, Cost/Conv, Conv Rate (aggregated across all ad groups).

**Timeline chart:** Same pattern as Account and Campaign Level. Dual axis, metric dropdowns, straight lines. Metric 1 colour: amber #f59e0b (ad group level). Metric 2: green #10b981.

**Data table — Ad Groups:**

Columns:
- Status (dot)
- Ad Group name (clickable → opens slide-in)
- Campaign (badge showing parent campaign)
- Keywords (count of active keywords)
- Ads (count of active ads)
- Cost
- Impressions
- Clicks
- Avg CPC
- CTR
- Conversions
- Cost/Conv
- Conv Rate
- Flag count (if any flags — show as small amber badge)

Sortable, left-aligned, totals/averages row at bottom.

### Sample Data (18 ad groups across 4 campaigns)

Create realistic sample data:

**GLO Campaign — Core (5 ad groups):**
- Core Terms (40% of campaign spend, healthy)
- Brand Defence (8% spend, healthy)
- Competitor Terms (15% spend, flagged — 60% worse CPA than campaign avg)
- Long Tail (25% spend, positive outlier — 45% better CPA)
- Retargeting Terms (12% spend, healthy)

**GLO Campaign — Retargeting (3 ad groups):**
- Recent Visitors (50% spend, healthy)
- Cart Abandoners (30% spend, positive outlier — 70% better CPA)
- Past Customers (20% spend, healthy)

**Brand — Objection Experts (4 ad groups):**
- Main Brand Terms (70% spend, healthy — concentration alert trigger)
- Brand + Service (15% spend, healthy)
- Brand + Location (10% spend, healthy)
- Brand Misspellings (5% spend, flagged — 30 days no conversions, pause candidate)

**Testing — New Keywords (6 ad groups):**
- Test Batch 1 (20% spend, underperforming)
- Test Batch 2 (18% spend, healthy)
- Test Batch 3 (15% spend, flagged — 21+ days zero conversions, pause candidate)
- Test Batch 4 (18% spend, healthy)
- Test Batch 5 (15% spend, underperforming)
- Test Batch 6 (14% spend, healthy)

Use realistic dental/professional services metrics based on GLO Campaign data.

### Ad Group-Level Review Sections (Main Page)

**Sample data:**

Awaiting Approval (3 items):
- "Competitor Terms in GLO Campaign — Core: Negative performance outlier. This ad group consumes 15% of campaign spend at £35 CPA vs £22 campaign avg (60% worse)." — Flag type: Negative Outlier
- "Long Tail in GLO Campaign — Core: Positive performance outlier. 45% better CPA than campaign average. Consider promoting to standalone campaign." — Flag type: Positive Outlier
- "Test Batch 3 in Testing — New Keywords: Pause recommendation. 21 days with zero conversions despite £45 spend." — Flag type: Pause Candidate

Actions Executed Overnight (2 items — these are keyword-level actions that affect ad groups):
- "Added 3 negative keywords to Competitor Terms ad group"
- "Paused 2 keywords in Test Batch 3 ad group — 0 conversions in 21 days"

Currently Monitoring (2 items):
- "Brand Misspellings in Brand — Objection Experts: Monitoring for pause candidate status. 25 days zero conversions. 5 days until threshold."
- "Competitor Terms negative outlier flag: Monitoring performance after negative keyword additions. 3 days into 7-day observation."

Recent Alerts (1 item):
- "Main Brand Terms in Brand — Objection Experts: Concentration alert — consumes 70% of campaign spend. Acknowledged 5 Apr."

### Slide-in Detail (when clicking an ad group name)

Use "Competitor Terms in GLO Campaign — Core" as the default example (it has an active flag).

**Ad group header:**
- Name: "Competitor Terms"
- Campaign badge: "GLO Campaign — Core"
- Status: Enabled
- Keywords: 24 active
- Ads: 3 active
- Avg QS: 4.2

**Health cards (4 in a row):**
- Cost (MTD): £248
- CPA: £35.00 (with red zone badge "60% above campaign avg — Underperforming")
- Conversions (MTD): 7
- QS Average: 4.2

**Awaiting Approval (expanded):**
- "Negative performance outlier — this ad group consumes 15% of campaign spend at £35 CPA vs £22 campaign avg (60% worse)"
- ACT recommends: "Investigate keyword selection and ad copy. Consider pausing underperforming keywords or reducing bids."
- Estimated impact: "Potential saving: £80/month"
- Stacked buttons: Approve / Decline / See Details

**Outlier Analysis (collapsed):**
When expanded, show a mini comparison table:

| Metric | This Ad Group | Campaign Average | Delta |
|--------|---------------|------------------|-------|
| Cost Share | 15% | — | — |
| CPA | £35.00 | £22.00 | +59% (worse) |
| Conv Rate | 2.8% | 4.5% | -38% (worse) |
| Avg CPC | £3.20 | £2.80 | +14% (higher) |
| Quality Score | 4.2 | 6.1 | -31% (lower) |

With a note: "This ad group is flagged as a negative outlier because it exceeds the 30% spend + 50% worse CPA thresholds."

**Structural Health (collapsed):**
When expanded, show:
- Keywords: 24 active (3 paused)
- Ads: 3 active (2 RSAs, 1 call-only)
- Average Quality Score: 4.2 / 10
- Days since last change: 12 days
- Days since last conversion: 4 days
- Ad strength: Average

### Guardrails (Main Page)

- Negative outlier spend threshold: 30% of campaign spend
- Negative outlier performance threshold: 50% worse than campaign average
- Positive outlier performance threshold: 40% better than campaign average
- Pause recommendation: zero conversions threshold: 21 days
- Pause recommendation: inactive threshold: 30 days
- Concentration alert: 1 ad group >90% trigger
- Concentration alert: 2 ad groups 1 >80% trigger
- Concentration alert: 3+ ad groups 1 >70% trigger

Ordered logically (thresholds grouped together).

---

## Interactive Behaviours

1. **Ad group name click** — opens slide-in with that ad group's detail
2. **Slide-in close** — X button, ESC, overlay click
3. **Chart date range** — controls both chart and table
4. **Table sort** — click column headers
5. **Status filters** — All / Enabled / Paused
6. **Review section interactions** — same as Campaign Level (approve, decline, see details inline expand in slide-in)
7. **Universal lever rows** — N/A for Ad Group Level (no levers at this level)

---

## Key Differences from Campaign Level

- **No Universal Levers section** — Ad Group Level has no bid levers (bids are at Campaign and Keyword levels)
- **No Bid Strategy section** — same reason
- **All actions require approval** — ACT can't auto-execute at this level (per v54)
- **Different focus** — outlier detection, structural health, pause candidates (not optimization actions)
- **Outlier Analysis section is unique** — shows how the ad group compares to its campaign's average
- **Structural Health section is unique** — keyword/ad counts, QS, activity metrics

---

## Browser Verification

1. Test ad group name click → slide-in opens
2. Test chart with all 3 date ranges
3. Test table sorting and filters
4. Test slide-in section collapse/expand
5. Test approve/decline in slide-in
6. Check dark mode
7. Save screenshots to `act_dashboard/prototypes/screenshots/`

---

## Deliverables

1. `act_dashboard/prototypes/ad-group-level.html` — working interactive Ad Group Level page
2. Updated `docs/ACT_PROTOTYPE_STANDARDS.md` with any new patterns (outlier analysis, structural health)
3. Screenshots saved to folder

---

**END OF BRIEF**
