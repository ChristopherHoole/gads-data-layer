# Client Pitch Reports Brief — Objection Experts

## Workflow — IMPORTANT

**Build one report at a time.** Do NOT start the next report until the user has reviewed and signed off the current one.

1. Build Report 1 (Waste Spend) → deliver → wait for user feedback → iterate until approved
2. Build Report 2 (Account Structure & Issues) → deliver → wait for user feedback → iterate until approved
3. Build Report 3 (Restructure) → deliver → wait for user feedback → iterate until approved

Each report is a separate PowerPoint file. Between reports, apply any lessons learned from the user's feedback to improve the next one.

---

## Context

**Client:** Owen Hoare, Objection Experts (objectionexperts.com)
**Business:** UK planning objection consultancy — helps people formally object to planning applications
**Service price:** From £350+VAT per objection letter
**Monthly spend:** ~£1,500/month Google Ads
**Campaign type:** Search (one main campaign)
**Conversion goal:** Lead gen — free consultation form submissions + phone calls
**Client's pain point:** "Costs have gone insane. A new agency took over in October. Cost per conversion has gone from £20 to £63."

**Our goal:** Win this client by delivering three outstanding reports that demonstrate deep expertise, identify clear problems, and present a credible restructure plan. The tone is constructive — "here's how we make this better" — not trashing the previous agency.

**Author branding:** Christopher Hoole — Google Ads Specialist (christopherhoole.com)

---

## Data Location

All data files are in: `potential_clients/objection_experts/data/`

### File Inventory

| File | Format | Encoding | Content |
|------|--------|----------|---------|
| `01_campaign_weekly.csv` | CSV | UTF-8 | Campaign performance by week |
| `02_adgroup_weekly.csv` | CSV | UTF-8 | Ad group performance by week |
| `03_keywords_weekly.csv` | TSV | **UTF-16** | Keyword performance by week (includes Quality Score) |
| `04_search_terms_weekly.csv` | CSV | UTF-8 | Search term report by week |
| `05_ad_copy_weekly.csv` | CSV | UTF-8 | RSA ad copy + performance by week (59 columns) |
| `07_geographic.csv` | CSV | UTF-8 | Performance by city/region (aggregated) |
| `08_device.csv` | CSV | UTF-8 | Performance by device + bid adjustments |
| `09_hour_of_day.csv` | CSV | UTF-8 | Performance by hour, campaign, ad group |
| `10_day_of_week.csv` | CSV | UTF-8 | Performance by day of week, campaign, ad group |
| `11_bid_strategy.csv` | CSV | UTF-8 | Bid strategy type + performance |
| `12_negative_keywords.csv` | TSV | **UTF-16** | Negative keywords with match types and levels |
| `13_audiences.csv` | CSV | UTF-8 | Audience segment observations |
| `14_ad_schedule.csv` | CSV | UTF-8 | Ad schedule with time blocks + bid adjustments |
| `15_location_targeting.csv` | CSV | UTF-8 | Location targets + radius targets |
| `16_conversion_actions.csv` | CSV | UTF-8 | Conversion actions by campaign/ad group |
| `Negative keyword details report.csv` | CSV | UTF-8 | Separate negative keyword list (broad match) |
| `Change history report.csv` | CSV | UTF-8 | All account changes with timestamps, users, and descriptions |

### Critical Parsing Notes
1. **ALL files have 2 header rows** before column headers (row 1 = report title, row 2 = date range). Skip rows 0-1.
2. Files 03 and 12 are **UTF-16 encoded TSV** despite having .csv extension. Use `encoding='utf-16'` and `sep='\t'`.
3. Numeric columns use comma formatting within quotes (e.g., `"1,314"`). Parse with `thousands=','`.
4. Date range: 1 Jan 2025 – 29 Mar 2026. Weekly segmentation on time-series files.
5. Currency is GBP throughout.

---

## Account Structure (Pre-Analysis Summary)

### Campaigns
| Campaign | Type | Status | Budget | Spend (period) |
|----------|------|--------|--------|----------------|
| GLO Campaign | Search | Active | £50/day | ~£18,300 |
| GLO - Core - PMax | Performance Max | Active | Unknown | Small |
| Planning Objection Letters | Search | Appears dormant | Unknown | Minimal |
| Lead Form Submissions | Unknown | Dormant | Unknown | £0 |

### Ad Groups (within GLO Campaign)
| Ad Group | Spend | Conversions | Notes |
|----------|-------|-------------|-------|
| Planning Objections | ~£17,400 | ~527 | Main ad group, all spend |
| Neighbourhood Objections | £79 | **0** | Pure waste |
| Planning Objection Consultants | Tiny | Tiny | Very small volume |
| Planning Objection Letters | Tiny | Tiny | Very small volume |

### Conversion Actions
| Action | Type | Count | Designation | In Goals? |
|--------|------|-------|-------------|-----------|
| Form Submission | Website form | 484 | Primary | Yes |
| Google Forwarding Number | Phone call | 27 | Primary | Yes |
| Email Click | Email link click | 34 | **Primary** | **Yes — PROBLEM** |
| Phone Number Click | Phone link click | 76 | Secondary | No |

**Key issue:** Email Click is set as Primary and included in account-level goals. This is a micro-conversion (clicking an email link), not an actual lead. It inflates reported conversion numbers and causes the bidding algorithm to optimise toward low-quality actions.

**Real conversions** = 484 + 27 = **511** (forms + calls)
**Reported conversions** = 572 (includes email clicks)
**True cost/conversion** = ~£36 (not the reported ~£32)

### Bid Strategy
- **Maximise Conversions** with **no target CPA set**
- This means the algorithm has no cost guardrails — it will spend whatever it takes to get conversions, which explains the cost volatility the client described

### Quality Scores
- Most keywords show QS of **2-3** (out of 10)
- This is extremely low and means Google is charging a significant premium on every click
- Likely caused by ad relevance and/or landing page experience issues

### Change History Analysis

The change history file (`Change history report.csv`) contains all account modifications from Jan 2025 – Mar 2026. Columns: `Date & time`, `User`, `Campaign`, `Ad group`, `Changes` (free-text, can be multiline).

#### Key Users
| User | Role | Activity Level |
|------|------|----------------|
| theo.atkinson@flex-digital.net | Flex Digital (new agency) | ~120 changes |
| owen@objectionexperts.com | Client (Owen) | ~119 changes |
| mike@generateleads.online | Generate Leads (old agency) | ~65 changes |
| rich@flex-digital.net | Flex Digital | ~19 changes |
| alex@generateleads.online | Generate Leads | ~14 changes |
| Recommendations Auto-Apply | Google system | Automated changes |

#### Agency Transition Timeline
- **Generate Leads** was the previous agency, active Jan–mid Sept 2025. Last meaningful change: 10 Sept 2025.
- **Flex Digital** took over late Sept 2025. First changes: 25 Sept 2025.
- Owen (client) has been actively adding negative keywords throughout both periods — shows he's engaged and watching.

#### What Flex Digital Changed at Takeover (Sept–Oct 2025)
This is critical context for Report 2 (Structure & Issues). The change history shows exactly what happened:

1. **25 Sept:** Created new RSAs, call-only ads, call extension. Bulk-added 101 negative exact match keywords.
2. **3 Oct:** Restructured ad groups — created "Planning Objection Letters", "Planning Objection Consultants", "Neighbourhood Objections" (splitting from the single "Planning Objections" group). Mass-paused ~15 phrase match keywords.
3. **3 Oct:** New ad copy for each ad group — notably contained spelling errors ("Planinng", "Guidence", "Counsil", "Distruptive", "propery", "Obejction", "Neighour") that were later corrected.
4. **7 Oct:** Set Target CPA to £30.
5. **9 Oct:** Turned on Search Partners + Display Network, then reversed the same day.
6. **9 Oct:** Added 6 image extensions, removed 4 the same day.
7. **9 Oct:** Enabled several auto-apply recommendations (including "Bid more efficiently with Maximize conversions" and "Set a target CPA").
8. **13 Oct:** Device bid adjustments: Mobile +30%, Desktop +10%, Tablet -20%.
9. **13 Oct:** Ad schedule bid adjustments: +10% Tue 2-5pm, Wed 5pm-midnight, Fri 9am-12pm; +20% Thu 2-5pm.
10. **21 Oct:** Changed Email Click and Phone Number Click from Primary to Secondary conversions.
11. **30 Oct:** Removed all headline pins from Planning Objections RSA.
12. **30 Oct:** Raised Target CPA from £30 to £38.65.
13. **28 Mar 2026:** Google auto-apply changed bid strategy from Maximise Conversions to Maximise Conversion Value. Rich at Flex Digital reversed it same day and disabled auto-apply.

#### Key Takeaways for Reports
- The restructure into multiple ad groups (3 Oct) fragmented volume — the new ad groups never got enough data to optimise, and "Neighbourhood Objections" produced zero conversions.
- Target CPA was raised from £30 to £38.65 within 3 weeks — the algorithm was given permission to spend more.
- Auto-apply recommendations were enabled, meaning Google itself was making bid strategy changes without human oversight. One such change (28 Mar 2026) switched the entire bid strategy automatically.
- Owen is doing the agency's job for them — he's the one actively adding negative keywords to block irrelevant traffic.
- Spelling errors in ad copy is unprofessional but should be mentioned tactfully.
- The same-day reversals (Search Partners, image extensions) suggest trial-and-error rather than a strategic plan.

**IMPORTANT TONE NOTE:** Present change history findings factually. Don't say "the agency was incompetent." Instead frame as "the change history shows several changes that may have contributed to the cost increase" and let the data speak for itself. The client will draw their own conclusions.

---

## Report 1: Waste Spend Report

### Purpose
Show the client exactly where money is being wasted right now. This is the "quick win" report — tangible, actionable, and immediately demonstrates value.

### Slides to Build

#### Slide 1: Title Slide
- "Waste Spend Analysis"
- Objection Experts
- Prepared by Christopher Hoole
- Date
- christopherhoole.com

#### Slide 2: Executive Summary
- Total spend analysed: £18,521
- Estimated waste identified: £X,XXX (calculate from data)
- Key waste categories with percentages
- One-line recommendation

#### Slide 3: Search Term Waste
- **Analysis:** Parse `04_search_terms_weekly.csv`. Aggregate by search term across all weeks. Find terms with clicks but 0 conversions, or terms that are clearly irrelevant to planning objections.
- **Visuals:** Table of top 20 wasted search terms ranked by cost. Columns: Search Term, Clicks, Cost, Conversions. Highlight rows with £0 return.
- **Commentary:** Calculate total spend on irrelevant/non-converting search terms. Show as % of total spend.

#### Slide 4: Search Term Waste (Categories)
- **Analysis:** Group the irrelevant search terms into categories (e.g., "DIY/template seekers", "wrong service", "geographic irrelevance", "competitor names", "informational queries").
- **Visuals:** Pie chart or horizontal bar chart showing waste by category.
- **Commentary:** Explain which categories should be blocked with negative keywords.

#### Slide 5: Negative Keyword Gaps
- **Analysis:** Parse `12_negative_keywords.csv` and `Negative keyword details report.csv`. Cross-reference with the wasteful search terms from Slides 3-4.
- **Visuals:** Two-column layout: "Currently blocked" (count + examples) vs "Should be blocked" (specific recommendations from search term analysis).
- **Key finding:** Most negatives use **exact match only** — this means slight variations of wasteful terms still get through. Recommendation: use phrase match negatives for broader protection.

#### Slide 6: Zero-Conversion Ad Groups
- **Analysis:** From `02_adgroup_weekly.csv` — identify ad groups with spend but 0 conversions.
- **Visuals:** Table showing ad group, spend, clicks, conversions. "Neighbourhood Objections" = £79, 0 conversions.
- **Commentary:** Recommend pausing or restructuring non-performing ad groups.

#### Slide 7: Time-of-Day Waste
- **Analysis:** From `09_hour_of_day.csv` — aggregate by hour across all campaigns. Find hours with spend but 0 or very low conversions.
- **Visuals:** Heatmap or bar chart showing cost and conversions by hour. Highlight dead zones.
- **Key finding:** Early morning hours (especially Fri/Sat) show zero conversions despite active spending.

#### Slide 8: Day-of-Week Waste
- **Analysis:** From `10_day_of_week.csv` — show performance by day.
- **Visuals:** Bar chart with dual axis (cost vs conversions) by day of week.
- **Key finding:** Sunday has the weakest performance. Monday is strongest. No bid adjustments are in place to capitalise on this.

#### Slide 9: Device Waste
- **Analysis:** From `08_device.csv` — compare device performance for the main campaign.
- **Visuals:** Table or bar chart: Device, Cost, Conversions, CPA, Conv Rate.
- **Commentary:** Note current bid adjustments (+10% mobile, -20% tablet, +10% desktop) and whether they're appropriate given the data.

#### Slide 10: Geographic Waste
- **Analysis:** From `07_geographic.csv` — find locations with significant spend but 0 conversions.
- **Visuals:** Table of top wasting locations by cost. Optional: map visualisation if feasible.
- **Commentary:** Identify geographic areas that consistently waste budget.

#### Slide 11: Total Waste Summary
- **Analysis:** Sum all waste categories identified above.
- **Visuals:** Waterfall chart or stacked bar showing waste breakdown. Big headline number: "£X,XXX of your £18,521 (X%) was wasted on non-converting traffic."
- **Commentary:** Frame constructively: "This isn't about blame — these are normal optimisation opportunities that any proactive manager would address."

#### Slide 12: Quick Wins (Recommendations)
- Numbered list of immediate actions:
  1. Add phrase-match negative keywords for identified waste categories
  2. Pause Neighbourhood Objections ad group
  3. Implement ad schedule bid reductions for dead hours
  4. Review device bid adjustments based on CPA data
  5. Tighten geographic targeting for non-converting areas
- Estimated monthly savings from implementing these changes

---

## Report 2: Account Structure & Issues Report

### Purpose
Diagnose WHY costs went up after October. Show the structural and strategic issues causing poor performance. This is the "here's what's wrong" report.

### Slides to Build

#### Slide 1: Title Slide
- "Account Structure & Performance Analysis"
- Same branding as Report 1

#### Slide 2: Executive Summary
- Overall account health score (create a simple rating system)
- 3-4 headline findings
- Before/after October snapshot

#### Slide 3: The Before & After Story (THE KILLER SLIDE)
- **Analysis:** From `01_campaign_weekly.csv` — split data into pre-October 2025 and post-October 2025 periods. Calculate: avg weekly spend, avg CPC, avg CPA, avg conversion rate for each period.
- **Visuals:** Side-by-side comparison boxes. Or a line chart showing CPA over time with a vertical "Agency Change" marker at October.
- **Commentary:** This directly addresses the client's pain point. Show the performance shift with cold, hard numbers.

#### Slide 4: Cost Per Conversion Trend
- **Analysis:** From `01_campaign_weekly.csv` — plot CPA by week across the full date range.
- **Visuals:** Line chart showing CPA over time. Annotate spikes. Show the volatility the client described ("some weeks are fine, then some weeks the algorithm just goes crazy").
- **Commentary:** The Maximise Conversions strategy without a target CPA explains this volatility.

#### Slide 5: Conversion Rate Trend
- **Analysis:** From `01_campaign_weekly.csv` — plot conversion rate by week.
- **Visuals:** Line chart. Look for the decline pattern post-October.
- **Commentary:** Link to bid strategy and Quality Score issues.

#### Slide 6: Bid Strategy Analysis
- **Analysis:** From `11_bid_strategy.csv` + change history data.
- **Visuals:** Simple infographic explaining what Maximise Conversions does vs what it should do with a target CPA. Include a timeline showing bid strategy changes from the change history:
  - 7 Oct: Target CPA set to £30
  - 30 Oct: Target CPA raised to £38.65
  - 28 Mar 2026: Google auto-apply changed strategy to Maximise Conversion Value (reversed same day)
- **Commentary:** "Without a stable target CPA, Google's algorithm has permission to spend any amount per conversion. The target was raised from £30 to £38.65 within 3 weeks, and auto-apply recommendations were left enabled — meaning Google itself could change the bid strategy without human oversight."

#### Slide 7: What Changed at Takeover
- **Analysis:** From `Change history report.csv` — build a timeline of the key changes made when Flex Digital took over in late Sept/Oct 2025.
- **Visuals:** Clean timeline graphic showing the sequence of changes (see Change History Analysis section above for the full list). Key events:
  - Ad group restructure that fragmented volume
  - Keyword pausing
  - Target CPA set then raised
  - Auto-apply recommendations enabled
  - Headline pins removed
  - Same-day reversals (Search Partners, image extensions)
- **Commentary:** Frame as "These are the changes that coincided with the cost increase. Some are standard onboarding steps. Others — like raising the target CPA and enabling auto-apply — directly contributed to cost volatility." Keep tone factual, not accusatory. Note that Owen (the client) has been actively managing negative keywords himself, adding them almost daily — this shows engagement and suggests the agency wasn't doing this proactively.
- **IMPORTANT:** Do NOT name the agency (Flex Digital) or any individuals in the slides. Refer to them as "the current management" or "the account changes." This keeps it professional and avoids making it personal.

#### Slide 8: Conversion Tracking Issues
- **Analysis:** From `16_conversion_actions.csv` + the conversion screenshot data.
- **Visuals:** Table of all conversion actions showing which are Primary vs Secondary, and which are "real" leads vs micro-conversions.
- **Key finding:** Email Click is a Primary conversion included in goals. The algorithm is optimising toward email link clicks, not just form submissions and calls.
- **Impact:** Reported CPA is artificially low. True CPA based on real leads is higher.

#### Slide 9: Quality Score Analysis
- **Analysis:** From `03_keywords_weekly.csv` — extract Quality Score data for all keywords.
- **Visuals:** Distribution chart (how many keywords at each QS level). Most are 2-3.
- **Commentary:** Explain the QS tax — at QS 2-3, the client is paying 2-4x more per click than a competitor with QS 7-8. Calculate the estimated premium being paid.

#### Slide 10: Account Structure Overview
- **Analysis:** Visual map of the account structure: campaigns → ad groups → keyword count → ad count.
- **Visuals:** Organisational chart or tree diagram showing the hierarchy.
- **Key findings:**
  - Only 1 RSA running (no ad testing)
  - Multiple dormant campaigns/ad groups
  - Simple structure isn't inherently bad for this spend level, but it needs proper optimisation

#### Slide 11: Ad Copy Audit
- **Analysis:** From `05_ad_copy_weekly.csv` — extract all headlines and descriptions.
- **Visuals:** Show the current RSA with all 15 headlines and 4 descriptions. Highlight issues:
  - Only 1 ad (no A/B testing possible)
  - Headline 1 uses {KeyWord:} insertion (can create awkward combinations)
  - Only 1 pin (Headline 13 pinned to position 3)
- **Commentary:** Best practice is 2-3 RSAs per ad group for testing. Having only 1 means no performance comparison is possible.

#### Slide 12: Landing Page Assessment
- **Analysis:** All ads point to the homepage (objectionexperts.com). Assess from a lead gen perspective.
- **Visuals:** Screenshot of the landing page with annotations highlighting strengths and areas for improvement.
- **Commentary:** The homepage is reasonably good as a lead gen page (clear CTA, trust signals with 600+ objections and 60% success rate), but a dedicated landing page could improve Quality Score and conversion rate.

#### Slide 13: Audience Setup
- **Analysis:** From `13_audiences.csv` — show the observation audiences applied.
- **Visuals:** Table of audiences with performance data. Highlight the completely irrelevant ones (GMC cars, horror movies, baseball).
- **Commentary:** Observation mode doesn't waste money, but the audience selection shows a lack of strategic thinking. Proper audiences (property buyers, home movers, legal services seekers) should be applied.

#### Slide 14: Issues Summary
- Prioritised list of all issues found, categorised by impact:
  - Critical: No stable target CPA, conversion tracking inflation, QS 2-3, auto-apply enabled
  - Important: No ad testing, negative keyword gaps, volume fragmentation across ad groups
  - Minor: Irrelevant observation audiences, dormant campaigns

---

## Report 3: Restructure Report

### Purpose
Show what YOU would do differently. This is the pitch — the "hire me" report. It should be forward-looking, confident, and specific.

### Slides to Build

#### Slide 1: Title Slide
- "Restructure & Growth Plan"
- Same branding

#### Slide 2: Executive Summary
- The opportunity: what's achievable with proper management
- Target metrics: projected CPA, conversion volume, monthly savings
- Timeline: quick wins (week 1) vs medium-term improvements (month 1-3)

#### Slide 3: Proposed Campaign Structure
- **Visuals:** Clean organisational chart showing the proposed new structure:
  - Campaign: Objection Experts — Search
    - Ad Group 1: Planning Objections (broad/phrase match, core terms)
    - Ad Group 2: Planning Permission Challenge (related intent)
    - Ad Group 3: [any other identified theme clusters from search term data]
  - Optional: Brand campaign (if competitor bidding is detected in search terms)
- **Commentary:** Explain the logic — tighter theme grouping = better QS = lower CPC. Note: keep it simple for this spend level. Don't over-structure a £1,500/month account.

#### Slide 4: Keyword Strategy
- **Analysis:** From `03_keywords_weekly.csv` and `04_search_terms_weekly.csv` — identify top-performing keywords and promising search terms not currently covered.
- **Visuals:** Table showing proposed keyword list with match types, estimated volume, and rationale.
- **Commentary:** Focus on the winners. Show which current keywords to keep, which to pause, and which new ones to add.

#### Slide 5: Bid Strategy Recommendation
- **Visuals:** Simple before/after comparison:
  - Current: Maximise Conversions (no target) → uncontrolled spending
  - Proposed: Maximise Conversions with Target CPA of £X (calculate from historical best-performing periods)
- **Commentary:** Explain that a target CPA gives the algorithm a guardrail. Base the target on the pre-October performance baseline when CPA was ~£20. Start conservative (e.g., £25-30) and optimise from there.

#### Slide 6: Conversion Tracking Fix
- **Visuals:** Before/after table of conversion actions:
  - Move Email Click from Primary → Secondary (or remove from goals entirely)
  - Review Phone Number Click vs Google Forwarding Number setup
  - Ensure only genuine leads (form submissions + actual calls) are Primary
- **Commentary:** "Clean conversion tracking = better algorithm decisions = lower CPA."

#### Slide 7: Negative Keyword Framework
- **Visuals:** Proposed negative keyword structure:
  - Account-level negatives (universal blockers: jobs, courses, templates, DIY, free)
  - Campaign-level negatives (service-specific exclusions)
  - Ongoing process: weekly search term review
- **Commentary:** Show the shift from reactive exact-match negatives to a proactive phrase/broad-match framework.

#### Slide 8: Ad Copy Testing Plan
- **Visuals:** Show 2-3 proposed RSA variants with different messaging angles:
  - RSA 1: Trust/credibility angle (600+ objections, 60% success rate, RTPI qualified)
  - RSA 2: Speed/urgency angle (5-day turnaround, same-day available)
  - RSA 3: Price/value angle (from £350, free consultation, fixed fee)
- **Commentary:** A/B testing plan — run for 4-6 weeks, then keep the winner and test a new challenger.

#### Slide 9: Schedule & Device Optimisation
- **Visuals:** Proposed ad schedule with bid adjustments based on the data:
  - Increase bids during high-converting hours (e.g., Mon 2-5pm)
  - Reduce bids during dead hours (early morning, late night)
  - Adjust device bids based on actual CPA by device
- **Commentary:** Show the data supporting each adjustment.

#### Slide 10: Quality Score Improvement Plan
- **Visuals:** Roadmap showing how to lift QS from 2-3 to 6-7+:
  1. Tighter ad group themes → better ad relevance
  2. Better ad copy with keyword alignment → better expected CTR
  3. Landing page recommendations → better landing page experience
- **Commentary:** "Every 1-point QS improvement reduces your CPC. Moving from QS 3 to QS 7 could cut click costs by 30-50%."

#### Slide 11: Projected Results
- **Analysis:** Build a conservative projection based on:
  - Current spend: ~£1,500/month
  - Current true CPA: ~£36
  - Target CPA with optimisations: £20-25
  - Projected conversion volume increase: X%
- **Visuals:** Before/after comparison table or chart. Be conservative — underpromise so you can overdeliver.
- **Commentary:** "Based on the waste reduction and optimisation opportunities identified, I project we can reduce your cost per lead from £36 to £20-25 within 8-12 weeks, while increasing lead volume."

#### Slide 12: Implementation Timeline
- **Visuals:** Gantt chart or phased timeline:
  - Week 1: Conversion tracking fix, negative keywords, bid strategy update, pause waste
  - Weeks 2-4: Ad copy testing, schedule optimisation, QS improvements
  - Months 2-3: Ongoing optimisation, potential landing page test, expand keyword coverage
- **Commentary:** Show that improvements start immediately, not in 3 months.

#### Slide 13: Why Christopher Hoole
- Brief credentials (keep short — the reports themselves are the proof)
- Link to christopherhoole.com
- What makes you different: hands-on specialist (not a junior in a big agency), data-driven approach, transparent reporting
- Proposed management fee / engagement model (leave blank or placeholder — you'll fill this in)

#### Slide 14: Next Steps
- Clear call to action
- "Grant me editor access and I'll implement the quick wins in week 1"
- Contact details

---

## Visual Design Specifications

### Colour Palette
Use a professional, modern palette. Suggestion:
- **Primary:** Deep navy (#1B2A4A)
- **Secondary:** Teal/cyan accent (#00B4D8)
- **Success/positive:** Green (#2ECC71)
- **Warning/waste:** Red/coral (#E74C3C)
- **Neutral backgrounds:** Light grey (#F5F6FA)
- **Text:** Dark charcoal (#2C3E50)
- **White:** (#FFFFFF) for slide backgrounds

### Typography
- Headlines: Bold, clean sans-serif (Calibri, Montserrat, or similar)
- Body: Regular weight, same family
- Data tables: Slightly smaller font, consistent column widths

### Chart Styling
- Clean, minimal charts (no 3D effects, no gradients)
- Consistent colour coding across all three reports
- Green = good performance, Red = waste/problems, Blue = neutral data
- Always label axes and include data labels on key points
- Use annotations on line charts to call out important events (e.g., "Agency change — October 2025")

### Slide Layout Principles
- Max 3-4 key points per slide
- Every data slide needs: chart/visual + 2-3 bullet commentary + one headline finding
- Use icons where appropriate (magnifying glass for analysis, warning triangle for issues, checkmark for recommendations)
- Footer on every slide: "Christopher Hoole | christopherhoole.com | Confidential"
- Page numbers on all slides

### PowerPoint Technical Notes
- Use python-pptx library
- Slide size: Widescreen 16:9 (13.333" × 7.5")
- Create reusable functions for consistent slide layouts:
  - `create_title_slide(title, subtitle)`
  - `create_content_slide(title, bullets, chart=None)`
  - `create_chart_slide(title, chart_data, chart_type, commentary)`
  - `create_table_slide(title, dataframe, highlight_column=None)`
  - `create_summary_slide(title, metrics_dict)`
- Save outputs to: `potential_clients/objection_experts/reports/`
  - `01_waste_spend_report.pptx`
  - `02_account_structure_report.pptx`
  - `03_restructure_report.pptx`

---

## Implementation Approach

### Step 1: Data Loading & Cleaning
Build a data loading module that handles:
- Skipping the 2 header rows in all files
- UTF-16 + TSV handling for files 03 and 12
- Comma-formatted number parsing
- Date/week column parsing
- Create clean DataFrames for each file

### Step 2: Analysis Engine
For each report, build analysis functions that:
- Calculate all metrics needed for each slide
- Generate the specific data cuts (before/after October, waste categories, etc.)
- Output structured data ready for chart/table generation

### Step 3: Chart Generation
Use matplotlib or plotly for creating charts, then embed as images in PowerPoint:
- Line charts for trends (CPA over time, conversion rate over time)
- Bar charts for comparisons (day of week, device, hour)
- Pie/donut charts for proportions (waste categories)
- Heatmaps for schedule data
- Tables for detailed data (search terms, keywords)

### Step 4: PowerPoint Assembly
Build each report slide by slide using python-pptx:
- Consistent formatting using the design spec above
- Embed chart images at high resolution
- Format tables with alternating row colours
- Add commentary text boxes with key findings

### Step 5: Quality Check
- Review all three reports for consistency
- Verify all numbers are accurate and add up
- Check that the narrative flows logically across all three reports
- Ensure no data is misrepresented

---

## Tone & Messaging Guidelines

1. **Constructive, not destructive.** Never say "the previous agency was terrible." Instead: "There are several optimisation opportunities that haven't been addressed."

2. **Data-first.** Every claim must be backed by a specific number from the data. No vague statements.

3. **Confidence without arrogance.** Present recommendations as "here's what I recommend based on the data" not "here's what any idiot would have done."

4. **Client-centric language.** Frame everything in terms of the client's goals: more leads, lower cost per lead, better ROI on their £1,500/month.

5. **Avoid jargon overload.** The client may not know PPC terminology deeply. Explain concepts briefly when first introduced (e.g., "Quality Score — Google's rating of your ad relevance, scored 1-10").

6. **The golden thread:** Every slide should connect back to the client's core complaint: "costs went up, conversions went down." Show that you understand the problem and have a clear plan to fix it.
