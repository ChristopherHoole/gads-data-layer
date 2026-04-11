# MC ACT Prototype — Page 7: Ad Level
**Session:** MC ACT Prototype (continued)
**Date:** 2026-04-11
**Objective:** Build an interactive HTML prototype of the Ad Level page. This level focuses on creative performance, ad strength, RSA assets, and ad health monitoring.

---

## IMPORTANT: FOLLOW EXISTING STANDARDS

Read `docs/ACT_PROTOTYPE_STANDARDS.md` before starting. All patterns from Pages 1-6 must be followed exactly.

Key standards:
- Level Page Structure (hybrid: data table + ACT intelligence)
- Combined Chart + Table Section pattern
- Performance Timeline Chart pattern (dual axes, straight lines, metric dropdowns, no vertical gridlines, no fill)
- Table Alignment: all left-aligned
- No all-caps, no coloured pills for metadata columns
- v54 colour system (Ad level colour = pink #ec4899)
- Slide-in detail pattern (800px)
- Word-for-word text consistency between main page and slide-in
- Rows per page dropdown (10/20/50/100/200)
- Coloured flag badges for flag types, grey/neutral for metadata

---

## Context

Read the Ad Level section in `docs/ACT_OPTIMIZATION_ARCHITECTURE_v54.html` — source of truth.

Key points from v54 for Ad Level:

**6 independent checks (all approval-based — ACT cannot write ad copy):**
1. **Ad Strength Monitoring** — flag ads below "Good" rating
2. **RSA Asset Performance** — flag "Low" rated assets after 30+ days
3. **Ad Count per Ad Group** — minimum 3 live ads per ad group
4. **Ad Performance Comparison** — flag ads 30%+ worse than ad group average (after 21+ days live and 100+ impressions)
5. **Ad Disapprovals** — daily scan, flag immediately
6. **Ad Extensions Monitoring** — sitelinks 4+, callouts 4+, snippets 1+, call if tracking

**Key characteristics:**
- Weekly scan (editable), except disapprovals which are daily
- All actions are approval-based — ACT cannot create/edit ad copy or extensions
- 8 guardrails at ad level

---

## Page Structure

Follow the same hybrid structure as previous level pages.

### Main Page:

1. **Page header** — pink (#ec4899) level accent, title "Ad Level", subtitle "Creative Performance & Health"
2. **Health summary cards** — 4 cards
3. **Ad Performance (combined section)** — summary metric cards + timeline chart + ads data table
4. **Ad-Level Review sections** — Awaiting Approval, Actions Executed, Currently Monitoring, Recent Alerts (filtered to ad level items only). Grouped by campaign.
5. **Guardrails** — ad level guardrails

### Slide-in Panel (800px) — opens when clicking an ad:

1. **Ad header** — ad type (RSA/Call-only), campaign + ad group badges, status, ad strength
2. **Health cards** — 4 cards (Impressions, CTR, Conversions, Cost/Conv)
3. **Awaiting Approval** (expanded) — this ad's flagged items
4. **Actions Executed Overnight** (collapsed) — any changes affecting this ad (typically none at this level)
5. **Currently Monitoring** (collapsed)
6. **Recent Alerts** (collapsed)
7. **Ad Preview** (collapsed) — shows the actual ad copy: headlines, descriptions, pinning
8. **Asset Performance** (collapsed) — for RSAs: list of all headlines and descriptions with their performance rating (Best/Good/Low/Learning)
9. **Extensions Status** (collapsed) — sitelinks count, callouts count, snippets count, call extension status — with the guardrail thresholds shown inline

All sections collapsible. Only Awaiting Approval expanded by default.

---

## Section Details

### Health Summary Cards (Main Page)

| Card | Content |
|------|---------|
| Total Ads | 42 (across all ad groups) |
| Avg Ad Strength | Good (with distribution) |
| Flagged Ads | 8 (across 5 check types) |
| Disapprovals | 1 (requires immediate action) |

### Ad Performance Combined Section (Main Page)

**Header:** "Ad Performance — 42 ads, 30 days" with date range pills and status filters.

**Summary metric cards:** Cost, Impressions, Clicks, Avg CPC, CTR, Conversions, Cost/Conv, Conv Rate.

**Timeline chart:** Dual axis, metric dropdowns, straight lines, no vertical gridlines, no fill. Metric 1 colour: pink #ec4899 (ad level). Metric 2: green #10b981.

**Data table — Ads:**

Columns:
- Status (dot)
- Ad name/identifier (clickable → opens slide-in) — for RSAs show first headline, for call-only show "Call Only Ad"
- Ad Type (plain text: RSA / Call Only / etc)
- Ad Strength (coloured badge: Excellent=green, Good=green, Average=amber, Poor=red)
- Campaign (plain text)
- Ad Group (plain text)
- Impressions
- Clicks
- CTR
- Conversions
- Cost/Conv
- Conv Rate
- Days Live
- Flag badges (coloured by flag type)

Sortable, left-aligned, totals/averages row at bottom, rows per page dropdown (10/20/50/100/200).

### Sample Data

Create realistic ad data. 42 ads across ad groups. Show 20 on first page.

Include this mix:
- **Most ads healthy** — Good or Excellent strength, no flags
- **1 RSA flagged for Poor strength** — "Expert Planning Help" with Poor rating (2 headlines rated Low after 30+ days)
- **1 RSA flagged for Low asset performance** — several Low-rated headlines
- **1 Ad Group with only 2 live ads** — triggers "Ad count below minimum" flag
- **1 RSA flagged for underperformance** — 35% worse CTR than ad group avg, 25 days live, 450 impressions
- **1 ad disapproved** — "Fast Planning Results" disapproved for misleading content
- **1 ad with missing extensions** — ad group has only 2 sitelinks, needs 4+
- **A few call-only ads** — low volume, status indicators

Use realistic dental-themed ad copy since Objection Experts sample:
- Headlines like: "Expert Planning Objection Help", "600+ Objections Prepared", "RTPI Qualified Planner", "From £350+VAT", "Free Consultation", "Fast 5-Day Turnaround"
- Descriptions with similar messaging

### Ad-Level Review Sections (Main Page)

**Awaiting Approval (5 items):**

1. **Ad Disapproval — Immediate** (HIGH RISK)
   - "'Fast Planning Results' disapproved for misleading content in Ad Group 'Planning Objections'. Requires headline edit and resubmission."
   - ACT recommends: "Remove or replace headline 4 'Guaranteed Results' which violates misleading content policy"
   - Flag type: Disapproval
   - Badge: Ad · Alert · High Risk · Identified 3 hours ago · Disapproval

2. **Ad Strength — Poor rating** (MEDIUM RISK)
   - "'Expert Planning Help' ad strength is Poor after 35 days live. 2 headlines rated Low."
   - ACT recommends: "Replace headlines 4 and 7 with new variations to improve ad strength"
   - Flag type: Ad Strength
   - Badge: Ad · Investigate · Medium Risk · Identified 1 day ago · Ad Strength

3. **RSA Asset Performance** (LOW RISK)
   - "3 assets in 'Planning Objection Letters' RSA rated Low for 32 days. Consider replacing."
   - ACT recommends: "Replace low-rated headlines to improve asset diversity and performance"
   - Flag type: Asset Performance
   - Badge: Ad · Investigate · Low Risk · Identified 2 days ago · Asset Performance

4. **Ad Count Below Minimum** (MEDIUM RISK)
   - "Ad Group 'Neighbourhood Objections' has only 2 live ads. Minimum is 3 ads per ad group for effective testing."
   - ACT recommends: "Add at least 1 more ad variation to enable proper testing"
   - Flag type: Ad Count
   - Badge: Ad · Investigate · Medium Risk · Identified 4 days ago · Ad Count

5. **Ad Performance Comparison** (LOW RISK)
   - "'Consultation Available' ad is 35% worse CTR than ad group average. 25 days live, 450 impressions."
   - ACT recommends: "Review ad copy or pause to let better performers take more impression share"
   - Flag type: Performance
   - Badge: Ad · Investigate · Low Risk · Identified 2 days ago · Performance

**Actions Executed Overnight (0 items)** — show empty state "No actions were executed overnight" — because ACT cannot auto-execute at Ad Level.

**Currently Monitoring (2 items):**

1. "'New Brand RSA' — Launched 3 days ago, in learning phase. 14 days until full performance evaluation."
2. "'Planning Objection Help' — Ad strength improved from Poor to Average after asset changes 8 Apr. Monitoring 7 more days before resolving flag."

**Recent Alerts (2 items):**

1. "Ad disapproval resolved: 'Fast Planning Results' headline edited and resubmitted. Approved on 7 Apr."
2. "Ad strength alert: 'Expert Planning Help' flagged for Poor rating. Under review since 5 Apr."

### Slide-in Detail

Use 4 unique slide-in variants:

1. **"Fast Planning Results" RSA** (Disapproval — High Risk) — default on page load
2. **"Expert Planning Help" RSA** (Ad Strength Poor — Medium Risk)
3. **"Consultation Available" RSA** (Performance — Low Risk)
4. **"Planning Objections" Ad Group view** (Ad Count flag — Medium Risk) — or alternative: clicking the ad group name shows the ad count issue

**Example: "Fast Planning Results" slide-in:**

- **Header**: "Fast Planning Results" · Disapproved status · RSA · GLO Campaign — Core · Planning Objections · Ad strength: Good (pre-disapproval)
- **Health cards**:
  - Impressions: 0 (disapproved, paused)
  - CTR: —
  - Conversions: 0
  - Cost/Conv: —
- **Awaiting Approval** (expanded):
  - Badges: Ad · Alert · High Risk · Disapproval · Identified 3 hours ago · Impact: Restore ad serving
  - Summary: "'Fast Planning Results' disapproved for misleading content. Requires headline edit and resubmission."
  - ACT recommends: "Remove or replace headline 4 'Guaranteed Results' which violates misleading content policy"
  - Cooldown: "No cooldown — resubmission required"
- **Ad Preview** (collapsed) — shows:
  - Headline 1: "Expert Planning Objections"
  - Headline 2: "RTPI Qualified"
  - Headline 3: "5-Day Turnaround"
  - Headline 4: "Guaranteed Results" — **flagged with red warning icon**
  - Headline 5-15: various
  - Description 1-4: ad copy
  - Pinning indicators
- **Asset Performance** (collapsed):
  - Table of headlines with performance rating
  - Headline 4 "Guaranteed Results" — **Flagged: Policy Violation**
  - Others: Best/Good/Low ratings
- **Extensions Status** (collapsed):
  - Sitelinks: 4 (meets threshold of 4+) ✓
  - Callouts: 6 (meets threshold of 4+) ✓
  - Snippets: 2 (meets threshold of 1+) ✓
  - Call extension: Active ✓

### Ad Preview Component

This is a unique component for the Ad Level. When expanded in the slide-in, it shows a mock ad preview similar to how Google Ads shows RSAs:

- Ad headline preview area
- Display URL
- Description text
- Below: a table/list showing all 15 headlines with their status (active/paused/flagged) and pin position (if pinned)
- Below that: all 4 descriptions with status

Style it to look like a simplified version of the Google Ads RSA preview. No need for a perfect replica — just enough to give the user a sense of what the ad actually contains.

### Asset Performance Component

Table showing all RSA assets:

| Asset | Type | Position | Status | Performance |
|-------|------|----------|--------|-------------|
| Expert Planning Objections | Headline | Any | Active | Best |
| RTPI Qualified | Headline | Pos 2 (pinned) | Active | Good |
| 5-Day Turnaround | Headline | Any | Active | Good |
| Guaranteed Results | Headline | Any | **Disapproved** | Low |
| ... | | | | |

### Extensions Status Component

Simple checklist showing:

- ✓ Sitelinks: 4 of 4+ required
- ✓ Callouts: 6 of 4+ required
- ✓ Snippets: 2 of 1+ required
- ✓ Call extension: Active (tracking enabled)

Each item shows green check if met, red X if not met, with the count and requirement.

### Guardrails (Main Page)

- Ad scan frequency: Weekly
- Disapproval scan frequency: Daily
- Ad strength minimum: Good
- RSA asset low-rated days threshold: 30 days
- Minimum ads per ad group: 3
- Ad performance comparison threshold: 30% worse than ad group average
- Ad minimum days live for comparison: 21 days
- Ad minimum impressions for comparison: 100 impressions
- Extension minimums: Sitelinks 4+, Callouts 4+, Snippets 1+

---

## Interactive Behaviours

1. **Ad name click** — opens slide-in
2. **Flag badge click** — opens slide-in
3. **See Details on main page** — inline expand (NOT slide-in)
4. **See Details in slide-in** — inline expand with Hide Details toggle
5. **Chart date range** — controls both chart and table
6. **Table sort and filters** — standard behaviour
7. **Ad strength badge** — coloured by level
8. **Ad Preview section** — expands to show headlines, descriptions, pinning
9. **Asset Performance** — expands to show all assets with ratings

---

## Key Differences from Keyword Level

- **No auto-execution** — every action at this level requires approval (ACT cannot write ad copy or create extensions)
- **Actions Executed Overnight typically empty** — show empty state
- **Unique sections**: Ad Preview, Asset Performance, Extensions Status
- **Daily disapproval scans** vs weekly for other checks
- **Different flag types**: Disapproval, Ad Strength, Asset Performance, Ad Count, Performance Comparison, Extensions
- **Ad Strength badges** on every ad row
- **Fewer health metrics** — focus on creative performance (CTR, Impressions) rather than bids

---

## Browser Verification

1. Test ad name click → slide-in opens
2. Test 4 unique slide-in variants
3. Test Ad Preview expand
4. Test Asset Performance expand
5. Test Extensions Status expand
6. Test chart date ranges
7. Test rows per page dropdown
8. Check dark mode
9. Save screenshots

---

## Deliverables

1. `act_dashboard/prototypes/ad-level.html`
2. Updated `docs/ACT_PROTOTYPE_STANDARDS.md` with new patterns (Ad Preview, Asset Performance, Extensions Status, Ad Strength badges)
3. Screenshots

---

**END OF BRIEF**
