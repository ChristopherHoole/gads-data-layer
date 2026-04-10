# Client Pitch Reports Brief — Dental by Design (Inserta Dental / Prodent Group)

## Workflow — IMPORTANT

**Build one report at a time.** Do NOT start the next report until the user has reviewed and signed off the current one.

1. Build Report 1 (Waste Spend) → deliver → wait for user feedback → iterate until approved
2. Build Report 2 (Account Structure & Issues) → deliver → wait for user feedback → iterate until approved
3. Build Report 3 (Restructure) → deliver → wait for user feedback → iterate until approved

Each report is a separate PowerPoint file. Between reports, apply any lessons learned from the user's feedback to improve the next one.

---

## Context

**Client:** Tommaso Grassi (Commercial Director), Giulio (Marketing)
**Recruitment contact:** Ellie Carvell (Recruitment Specialist, ellie@inserta-dental.com)
**Company:** Prodent Group — comprising Dental by Design (flagship London clinic), Vivo Dental Lab, Inserta (implant manufacturer), and a network of partner clinics across the UK
**Website:** dentalbydesign.co.uk
**Business:** Premium dental implant clinic + cosmetic dentistry + general dentistry + emergency dental care
**Key services:** Dental implants (£1,695-£15,990+), Vivo Bridge (permanent teeth in 48 hours), veneers, teeth whitening, smile makeovers
**Monthly spend:** Unknown until data is reviewed — likely significantly higher than £1,500/month given the competitive London market
**Campaign types:** Google Ads (Search-led) + Meta (based on job spec)
**Conversion goal:** Lead gen — patient enquiry forms, phone calls, online booking
**Competitive landscape:** High CPCs (£5-15+ for dental implant keywords in London), intense competition (Harley Street clinics, NHS alternatives, dental tourism to Turkey)

**Our goal:** Win this role by delivering three outstanding reports that demonstrate deep expertise, identify clear problems and opportunities, and present a credible restructure/growth plan. The tone is constructive and professional — we are positioning ourselves as the expert they need to hire. These reports are the final step in the interview process.

**Author branding:** Christopher Hoole — Google Ads Specialist (christopherhoole.com)

**Previous context:** This session already built an interview presentation for Dental by Design (Christopher_Hoole_Dental_by_Design_Presentation_v4.pptx). That presentation has been delivered and the interview went well — resulting in read-only access being granted. These reports are the follow-up that will seal the deal.

---

## IMPORTANT: Use the OE Reports as Your Visual Template

Christopher has already delivered reports to another client that won him the business. These are your visual and structural reference. Read them before building anything:

**Reference reports (READ ALL OF THESE FIRST):**
- `potential_clients/slide deck examples/ObjectionExperts.com - Waste Spend Report.pptx`
- `potential_clients/slide deck examples/ObjectionExperts.com - Account Structure Report.pptx`
- `potential_clients/slide deck examples/ObjectionExperts.com - Restructure Report.pptx`

Match the visual quality, layout patterns, colour scheme, branding, and slide structure of these reports. The OE reports use:
- Dark navy title slides with large hero stat numbers
- Clean white content slides with data tables, charts, and commentary
- ACT logo branding
- Consistent footer: "Christopher Hoole | christopherhoole.com | Confidential"
- Charts embedded as images (matplotlib/plotly → PNG → embedded)
- Colour coding: green = good, red = waste/problems, amber = warning, blue = neutral

**The Dental by Design reports must look like they come from the same author as the OE reports.** Same design language, same quality level, same professionalism.

---

## Data Location

All data files are in: `potential_clients/Inserta Dental/data/`

### File Naming Convention

The user will download data from Google Ads following the same convention as the OE reports:

```
01_campaign_weekly.csv
02_adgroup_weekly.csv
03_keywords_weekly.csv
04_search_terms_weekly.csv
05_ad_copy_weekly.csv
07_geographic.csv
08_device.csv
09_hour_of_day.csv
10_day_of_week.csv
11_bid_strategy.csv
12_negative_keywords.csv
13_audiences.csv
14_ad_schedule.csv
15_location_targeting.csv
16_conversion_actions.csv
Change history report.csv
```

There may also be additional files. Read whatever is in the `/data/` folder.

### Critical Parsing Notes
1. **ALL Google Ads export files typically have 2 header rows** before column headers (row 1 = report title, row 2 = date range). Check each file and skip header rows as needed.
2. Some files may be **UTF-16 encoded TSV** despite having .csv extension (typically keywords and negative keywords files). If parsing fails with UTF-8, try `encoding='utf-16'` and `sep='\t'`.
3. Numeric columns often use comma formatting within quotes (e.g., `"1,314"`). Parse with `thousands=','`.
4. Currency is GBP throughout.
5. **Read every file in the data folder first** before starting any analysis. Understand what data you have, the column structures, date ranges, and any encoding issues. Document any files that fail to parse and flag them.

---

## Report 1: Waste Spend Report

### Purpose
Show the client exactly where money is being wasted right now. Tangible, actionable, and immediately demonstrates value. This is the "quick win" report.

### Analysis to Perform (adapt based on actual data found)

1. **Search Term Waste** — Parse search terms report. Aggregate by search term across all weeks. Find terms with clicks but 0 conversions, or terms clearly irrelevant to dental services. Calculate total spend on non-converting/irrelevant search terms. Group into categories (e.g., "dental jobs/careers", "NHS dentist", "dental tourism", "DIY/home remedies", "wrong location", "competitor names", "informational queries").

2. **Negative Keyword Gaps** — Parse negative keywords. Cross-reference with wasteful search terms. Identify what should be blocked but isn't. Note match type distribution (exact vs phrase vs broad). Identify if negatives are too narrow (exact only) leaving variations through.

3. **Zero-Conversion Ad Groups/Campaigns** — Parse ad group and campaign reports. Find any with spend but 0 conversions. Calculate total waste.

4. **Time-of-Day Waste** — Parse hour of day report. Find hours with spend but 0 or very few conversions. Identify dead zones.

5. **Day-of-Week Waste** — Parse day of week report. Compare CPA across days. Identify worst-performing days with no bid adjustments.

6. **Device Waste** — Parse device report. Compare CPA, conversion rate, and spend across mobile/desktop/tablet. Check current bid adjustments.

7. **Geographic Waste** — Parse geographic report. Find locations with significant spend but 0 conversions. This is especially important for a London-based clinic — are they getting irrelevant clicks from outside their service area?

8. **Total Waste Summary** — Sum all waste categories. Present as total £ and % of total spend.

### Slides to Build

#### Slide 1: Title Slide
- "Waste Spend Analysis"
- Dental by Design | Prodent Group
- Big headline waste number (calculate from data)
- Key stats: total spend analysed, waste identified, % wasted
- Prepared by Christopher Hoole
- christopherhoole.com

#### Slide 2: Executive Summary
- Total spend analysed
- Waste identified (£ and %)
- Total conversions
- 4-5 key findings (one line each)
- One-line recommendation with estimated monthly savings

#### Slides 3-10: One Slide Per Waste Category
For each waste category identified, create a slide with:
- Chart or data table showing the waste
- Key insight (1-2 sentences)
- Specific recommendation
- £ amount of waste in this category

The exact number and content of slides depends on what the data reveals. Use the OE Waste Spend Report as your structural guide — it had 12 slides covering search terms, categories, negative keywords, ad groups, time of day, day of week, device, geographic, total summary, and quick wins.

#### Final Slide: Quick Wins
- Numbered list of immediate actions
- Estimated monthly savings per action
- Total estimated monthly/annual savings
- "What's Next? Report 2: Account Structure & Issues"

---

## Report 2: Account Structure & Issues Report

### Purpose
Diagnose the structural and strategic issues in the account. This is the "here's what needs fixing" report.

### Analysis to Perform (adapt based on actual data found)

1. **Performance Trends** — Plot CPA, conversion rate, spend over time (weekly). Look for trends, spikes, deterioration. If there's a clear before/after story (like OE had with the agency change), highlight it.

2. **Bid Strategy Analysis** — What bid strategies are in use? Are target CPAs/ROAS set? Are they appropriate? Is auto-apply enabled? Are there guardrails?

3. **Conversion Tracking Audit** — What conversion actions exist? Are they all legitimate leads? Are micro-conversions (email clicks, phone number clicks) being counted as primary? Calculate true CPA vs reported CPA.

4. **Quality Score Analysis** — Distribution of Quality Scores across keywords. Calculate the QS tax (premium being paid for low QS keywords).

5. **Account Structure Overview** — Map the campaign → ad group → keyword → ad hierarchy. Identify structural issues (fragmentation, dormant elements, imbalanced spend).

6. **Ad Copy Audit** — How many RSAs per ad group? Is there ad testing? Pinning strategy? Keyword insertion usage? Ad copy quality.

7. **Landing Page Assessment** — Where are ads sending traffic? Is it the right page for each service? Fetch dentalbydesign.co.uk and assess from a lead gen perspective.

8. **Change History Analysis** — Parse change history. Who's making changes? How often? What kind of changes? Any problematic patterns (same-day reversals, auto-apply incidents, bid strategy changes)?

9. **Audience Setup** — What audiences are applied? Observation vs targeting? Are they relevant to dental services?

### Slides to Build

Follow the OE Account Structure Report pattern (15 slides). Adapt based on what the data reveals. Key slides:
- Executive Summary
- Performance trend over time (the headline slide)
- CPA trend with annotations
- Conversion rate trend
- Bid strategy analysis
- Conversion tracking issues (if any)
- Quality Score distribution
- Account structure overview
- Ad copy audit
- Landing page assessment
- Change history timeline (if revealing)
- Audience setup
- Issues summary (prioritised: Critical / Important / Minor)

---

## Report 3: Restructure Report

### Purpose
Show what Christopher would do differently. This is the "hire me" report. Forward-looking, confident, and specific.

### Slides to Build

Follow the OE Restructure Report pattern (14 slides). Key slides:
- Executive Summary with projected results
- Proposed campaign structure (by treatment type: implants, cosmetic, general, emergency + by clinic for multi-clinic)
- Keyword strategy (keep/pause/add based on data)
- Bid strategy recommendation (with specific target CPA/ROAS based on data)
- Conversion tracking fix (if needed)
- Negative keyword framework (the 9-list system)
- Ad copy testing plan (treatment-specific messaging angles)
- Schedule & device optimisation (data-driven adjustments)
- Quality Score improvement plan
- Multi-clinic management approach (flagship → partner clinics, separate campaigns, shared learnings, performance-based budgets)
- Projected results (conservative: CPA reduction %, conversion volume increase, monthly savings)
- Implementation timeline (Week 1, Month 1-3)
- Why Christopher Hoole (brief — the reports are the proof)
- Next Steps ("Grant me editor access and I'll implement the quick wins in week 1")

---

## Visual Design Specifications

**MUST match the OE reports exactly.** Read them and replicate the design system:

### Colour Palette
- Primary: Deep navy (#1B2A4A)
- Secondary: Teal/cyan accent (#00B4D8)
- Success/positive: Green (#2ECC71)
- Warning/waste: Red/coral (#E74C3C)
- Neutral backgrounds: Light grey (#F5F6FA)
- Text: Dark charcoal (#2C3E50)
- White: (#FFFFFF) for slide backgrounds

### Typography
- Headlines: Bold, clean sans-serif
- Body: Regular weight, same family
- Data tables: Consistent column widths, alternating row colours where appropriate

### Chart Styling
- Clean, minimal charts (no 3D effects, no gradients)
- Green = good performance, Red = waste/problems, Blue = neutral data
- Always label axes and include data labels on key points
- Annotations on line charts for important events

### Slide Layout
- Max 3-4 key points per slide
- Every data slide: chart/visual + 2-3 bullet commentary + one headline finding
- Footer on every slide: "Christopher Hoole | christopherhoole.com | Confidential"
- Page numbers on all slides
- ACT logo on every slide

### PowerPoint Technical Notes
- Use python-pptx or pptxgenjs (whichever was used for the OE reports — check the reference files)
- Slide size: Widescreen 16:9
- Save to: `potential_clients/Inserta Dental/reports/`
  - `01_waste_spend_report.pptx`
  - `02_account_structure_report.pptx`
  - `03_restructure_report.pptx`

---

## Tone & Messaging Guidelines

1. **Constructive, not destructive.** Never trash whoever is currently managing the account. Frame as "optimisation opportunities" not "mistakes."

2. **Data-first.** Every claim backed by specific numbers from the data. No vague statements.

3. **Confidence without arrogance.** "Here's what I recommend based on the data" — not "here's what any idiot would have done."

4. **Client-centric language.** Frame everything in terms of patient enquiries and bookings, not PPC jargon.

5. **Dental-market aware.** Reference the competitive dynamics (high CPCs, long patient decision cycle, price sensitivity vs quality). Show you understand this market.

6. **Multi-clinic aware.** Where relevant, reference how findings/recommendations scale across the partner clinic network. This is what makes this role unique.

7. **Commercial thinking.** Tommaso is a Commercial Director. He cares about revenue, not CTR. Frame results in terms of patient bookings and cost per patient.

8. **Leverage their competitive advantages.** Their integrated model (clinic + lab + manufacturer), "up to 60% less" pricing, Vivo Bridge 48-hour turnaround, 4.8 stars / 399+ reviews. Reference these as ad copy and landing page assets wherever relevant.

---

## Key Differences from the OE Reports

| Aspect | Objection Experts | Dental by Design |
|--------|------------------|-----------------|
| Market | Planning objections (niche) | Dental implants London (ultra-competitive) |
| Budget | ~£1,500/month | Likely much higher |
| Campaigns | 1 main campaign | Multiple (unknown until data reviewed) |
| Services | Single service | Multiple (implants, cosmetic, general, emergency) |
| Clinics | 1 business | Flagship + partner network |
| Platforms | Google Ads only | Google Ads + Meta |
| Context | Client complaining about rising costs | Interview process — proving expertise |
| Tone | "Here's what's wrong and how I'd fix it" | "Here's the opportunity and what I'd do for you" |

The Dental by Design reports should feel slightly more aspirational than the OE reports. OE was about diagnosing problems for a frustrated client. Dental by Design is about showing a Commercial Director the growth opportunity if they hire you.

---

**END OF BRIEF**
