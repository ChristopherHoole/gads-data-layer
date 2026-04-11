# MC ACT Prototype — Page 6: Keyword Level
**Session:** MC ACT Prototype (continued)
**Date:** 2026-04-09
**Objective:** Build an interactive HTML prototype of the Keyword Level page. This is the highest daily-impact level — where ACT does the most work: bid adjustments, search term mining, negative keyword management, pause recommendations, Quality Score monitoring.

---

## IMPORTANT: FOLLOW EXISTING STANDARDS

Read `docs/ACT_PROTOTYPE_STANDARDS.md` before starting. All patterns from Pages 1-5 must be followed exactly.

Key standards:
- Level Page Structure (hybrid: data table + ACT intelligence)
- Combined Chart + Table Section pattern
- Performance Timeline Chart pattern (dual axes, straight lines, metric dropdowns)
- Table Alignment: all left-aligned
- No all-caps
- v54 colour system (Keyword level colour = purple #8b5cf6)
- Slide-in detail pattern (800px, follow Campaign Level v10 and Ad Group Level v3)
- Word-for-word text consistency between main page and slide-in

---

## Context

Read the Keyword Level section in `docs/ACT_OPTIMIZATION_ARCHITECTURE_v54.html` — source of truth.

Key points from v54 for Keyword Level:

**7 independent checks + Manual CPC bid management:**
1. **Keyword Performance Monitoring** — auto-pause at 1x target spend with 0 conversions for 14+ days (AUTO-EXECUTE)
2. **Search Term Mining — Negatives** — auto-add [exact] match negatives to 9-list structure (AUTO-EXECUTE)
3. **Search Term Mining — Keyword Discovery** — add promising search terms as new keywords (APPROVAL)
4. **Quality Score Monitoring** — weekly scan, flag keywords below QS 4 (FLAG)
5. **Keyword Status Monitoring** — below first page bid, rarely shown (FLAG)
6. **Keyword Conflicts & Cannibalisation** — same ad group different match = OK, different ad groups/campaigns = flag (FLAG)
7. **Keyword Pause Recommendations** — dead 60d+, zero-converting 1x target 14d+ (APPROVAL)

**Plus: Keyword Bid Management (Manual CPC only)** — 10% per cycle, 72hr cooldown, 30% 7-day cap (AUTO-EXECUTE)

**9 standardised negative keyword lists** — ACT only adds [exact] match, phrase match is human-managed.

**10 guardrails** at keyword level.

---

## Page Structure

Follow the same hybrid structure as previous level pages.

### Main Page:

1. **Page header** — purple (#8b5cf6) level accent, title "Keyword Level", subtitle "Performance, Bids, Search Terms & Quality"
2. **Health summary cards** — 4 cards for keyword-level health
3. **Keyword Performance (combined section)** — summary metric cards + timeline chart + keywords data table
4. **Keyword-Level Review sections** — Awaiting Approval, Actions Executed, Currently Monitoring, Recent Alerts (filtered to keyword-level items only). Grouped by campaign name.
5. **Guardrails** — keyword level guardrails

### Slide-in Panel (800px) — opens when clicking a keyword:

1. **Keyword header** — keyword text, match type badge, campaign + ad group badges, status
2. **Health cards** — 4 cards (Cost, CPA with zone badge, Conversions, Quality Score)
3. **Awaiting Approval** (expanded) — this keyword's flags
4. **Actions Executed Overnight** (collapsed) — bid changes, status changes affecting this keyword
5. **Currently Monitoring** (collapsed) — items in monitoring state
6. **Recent Alerts** (collapsed) — historical alerts
7. **Bid History** (collapsed) — last 10 bid changes with dates, old → new, reason
8. **Search Term Analysis** (collapsed) — top 10 search terms that triggered this keyword with cost, conversions, CPA
9. **Quality Score Breakdown** (collapsed) — Expected CTR, Ad Relevance, Landing Page Experience scores

All sections collapsible. Only Awaiting Approval expanded by default.

---

## Section Details

### Health Summary Cards (Main Page)

| Card | Content |
|------|---------|
| Total Keywords | 142 (across all campaigns) |
| Avg CPA | £19.80 |
| Avg Quality Score | 6.2 / 10 |
| Flagged Keywords | 12 (across 4 check types) |

### Keyword Performance Combined Section (Main Page)

**Header:** "Keyword Performance — 142 keywords, 30 days" with date range pills and status filters (All/Enabled/Paused).

**Summary metric cards:** Cost, Impressions, Clicks, Avg CPC, CTR, Conversions, Cost/Conv, Conv Rate.

**Timeline chart:** Dual axis, metric dropdowns, straight lines. Metric 1 colour: purple #8b5cf6 (keyword level). Metric 2: green #10b981.

**Data table — Keywords:**

Columns:
- Status (dot)
- Keyword text (clickable → opens slide-in)
- Match type (badge: Broad / Phrase / Exact)
- Campaign (badge)
- Ad Group (badge)
- Max CPC (bid)
- Quality Score (small badge coloured by score — red for <4, amber 4-6, green 7+)
- Cost
- Impressions
- Clicks
- Avg CPC
- CTR
- Conversions
- Cost/Conv
- Conv Rate
- Flag badges (if any — coloured by type like Ad Group Level)

Sortable, left-aligned, totals/averages row at bottom.

### Sample Data

Create realistic dental keyword data. 142 keywords is too many to render as distinct rows — show the top 15-20 with realistic diversity, and paginate the rest.

Core keywords to include (based on Objection Experts dental sample data):
- "planning objection" — Exact, QS 8, healthy
- "planning objections" — Exact, QS 7, healthy
- "dental implants london" — Phrase, QS 6, healthy
- "cosmetic dentist" — Exact, QS 7, healthy
- "veneers near me" — Phrase, QS 5, flagged (approaching pause threshold)
- "tooth replacement cost" — Exact, QS 3, flagged (low QS)
- "emergency dentist" — Exact, QS 8, healthy
- "teeth whitening" — Broad, QS 6, healthy
- "full mouth restoration" — Exact, QS 7, healthy
- "dental implant cost" — Phrase, QS 5, healthy
- "best dentist london" — Exact, QS 4, flagged (low QS)
- "planning permission objection" — Exact, QS 8, healthy
- "dentist near me" — Phrase, QS 6, healthy
- "invisalign braces" — Exact, QS 7, healthy
- "dental consultation free" — Phrase, QS 2, flagged (very low QS, pause candidate)
- "smile makeover" — Exact, QS 5, healthy
- "tooth pain emergency" — Exact, QS 8, healthy
- "white fillings" — Phrase, QS 6, healthy
- "crown dental cost" — Exact, QS 4, flagged (low QS)
- "wisdom tooth removal" — Exact, QS 7, healthy

Show realistic metrics — high CPCs for competitive terms (£5-12), lower for long-tail (£1-3).

### Keyword-Level Review Sections (Main Page)

**Awaiting Approval (6 items):**

1. **Keyword Discovery — Search Term Mining**: Add "dental implant clinic london" as phrase match to "Dental Implants" ad group. Discovered from search terms with 8 conversions at £18 CPA. (Low Risk)

2. **Keyword Discovery — Search Term Mining**: Add "emergency dental care" as phrase match to "Emergency Dental" ad group. Discovered from search terms with 5 conversions at £22 CPA. (Low Risk)

3. **Keyword Pause — Dead 60+ days**: Pause "dental consultation free" — 0 conversions in 72 days despite £125 spend. (Medium Risk)

4. **Keyword Pause — Zero Converting**: Pause "crown dental cost" — 0 conversions in 18 days at £68 spend (1.5x target CPA). (Medium Risk)

5. **Keyword Conflict**: "dental implants" in 2 different ad groups — Dental Implants and Cosmetic Dentistry. Cannibalising impressions. (Medium Risk)

6. **Quality Score Investigation**: "tooth replacement cost" QS dropped from 6 to 3 in 7 days. Investigate ad relevance and landing page. (Medium Risk)

**Actions Executed Overnight (8 items):**

1. Added "dental veneers price uk" to negative keyword list "3 WORDS [exact]" — search term mining, 0 conversions, £15 spend
2. Added "how to become a dentist" to negative keyword list "5+ WORDS [exact]" — search term mining, irrelevant intent
3. Added "nhs dentist free" to negative keyword list "3 WORDS [exact]" — search term mining, wrong service
4. Paused keyword "dental school london" — 0 conversions in 14 days, £48 spend
5. Paused keyword "oral hygiene products" — 0 conversions in 16 days, £32 spend
6. Reduced bid on "cosmetic dentist london" from £4.80 to £4.32 (-10%) — 72hr cooldown applies
7. Increased bid on "planning objection expert" from £3.20 to £3.52 (+10%) — outperforming, 72hr cooldown
8. Added "dental phobia" to negative keyword list "2 WORDS [exact]" — irrelevant intent

**Currently Monitoring (3 items):**

1. Bid cooldown: "cosmetic dentist london" reduced from £4.80 to £4.32. 66h remaining of 72h cooldown. Healthy.
2. Bid cooldown: "planning objection expert" increased from £3.20 to £3.52. 66h remaining of 72h cooldown. Healthy.
3. Pause watch: "veneers near me" approaching pause threshold. 11 days zero conversions. 3 days remaining until threshold. Trending down.

**Recent Alerts (2 items):**

1. Keyword cannibalisation detected: "dental implants" running in 2 ad groups. Flagged 2 Apr. Under review.
2. QS drop alert: "best dentist london" QS dropped to 4. Flagged 3 Apr. Acknowledged.

### Slide-in Detail

Use 4 unique slide-in variants:

1. **"dental consultation free"** (Pause Candidate — Medium Risk) — default
2. **"dental implant clinic london"** (Keyword Discovery — Low Risk)
3. **"dental implants"** (Conflict/Cannibalisation — Medium Risk)
4. **"tooth replacement cost"** (Low QS Investigation — Medium Risk)

Other keywords show a generic default slide-in.

**Example: "dental consultation free" slide-in:**

- **Header**: "dental consultation free" · Phrase match badge · Testing — New Keywords campaign badge · Cosmetic Dentistry ad group badge · Paused status
- **Health cards**:
  - Cost (MTD): £125
  - CPA: — (no conversions, with red "No conversions in 72 days" zone badge)
  - Conversions (MTD): 0
  - Quality Score: 2 / 10 (red)
- **Awaiting Approval**: 
  - Badges: Keyword, Investigate, Medium Risk, Pause Candidate, clock "Identified 2 hours ago", impact "Saves £52/month"
  - Summary: "Pause this keyword — 0 conversions in 72 days despite £125 spend"
  - ACT recommends: "Pause and consolidate budget to performing keywords in this ad group"
  - Cooldown: "No cooldown — pause action"
- **Bid History** (collapsed): last 10 bid changes on this keyword
- **Search Term Analysis** (collapsed): top 10 search terms this keyword matched with their performance
- **Quality Score Breakdown** (collapsed):
  - Expected CTR: Below Average
  - Ad Relevance: Below Average
  - Landing Page Experience: Below Average
  - Overall: 2/10

### Guardrails (Main Page)

From v54 Keyword Level:
- Auto-pause spend threshold: 1x target CPA
- Auto-pause days threshold: 14 days zero conversions
- Keyword bid adjustment per cycle: 10%
- Keyword bid cooldown: 72 hours
- Keyword bid 7-day cap: 30%
- Quality Score alert threshold: QS < 4
- Negative keyword structure: 9 lists by word count + match type
- Negative keyword match type: [exact] only (phrase is human-managed)
- Dead keyword threshold: 60 days zero conversions
- Conflict detection: same ad group different match OK, different ad groups flagged

Ordered logically (thresholds first, then cooldowns, then structure rules).

---

## Interactive Behaviours

1. **Keyword name click** — opens slide-in
2. **Flag badge click** — opens slide-in
3. **See Details on Awaiting Approval** — inline expand (NOT slide-in)
4. **Slide-in See Details** — inline expand with Hide Details toggle
5. **Chart date range** — controls both chart and table
6. **Table sort and filters** — standard behaviour
7. **Match type badges** — small pill badges (Broad/Phrase/Exact)
8. **Quality Score badges** — colour-coded (red <4, amber 4-6, green 7+)

---

## Key Differences from Ad Group Level

- **Has bid management** — keyword bids are at this level (Manual CPC only per v54)
- **Auto-execution exists** — search term mining (negatives), bid adjustments, dead keyword pauses all auto-execute
- **Search Term Analysis section** — unique to this level (shows which search terms triggered each keyword)
- **Quality Score Breakdown section** — unique to this level
- **Bid History section** — unique to this level
- **More actions executed overnight** — keyword level does the most automated work
- **Match type display** — every keyword row shows match type
- **Negative keyword management** — 9-list structure referenced in actions

---

## Browser Verification

1. Test keyword name click → slide-in opens with correct keyword
2. Test 4 unique slide-in variants (different flag types)
3. Test chart date ranges
4. Test table sort on all columns
5. Test See Details inline expand (main page)
6. Test See Details / Hide Details toggle in slide-in
7. Test flag badge click
8. Check dark mode
9. Save screenshots

---

## Deliverables

1. `act_dashboard/prototypes/keyword-level.html`
2. Updated `docs/ACT_PROTOTYPE_STANDARDS.md` with new patterns (bid history, search term analysis, QS breakdown, match type badges)
3. Screenshots

---

**END OF BRIEF**
