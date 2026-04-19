# DBD Weekly Report — Session Workflow

**Purpose:** The exact sequence of steps this session follows to produce each weekly report. Do not skip steps. Do not reorder them. Do not start building slides before step 7.

---

## STEP 0 — Orient the session (run this once at the start of every weekly report session)

Before the user's first message about this week's report, read these three files in full:

1. `potential_clients/Inserta Dental/Report templates/DBD_WEEKLY_REPORT_BRIEF.md` — client context, structure, anti-patterns
2. `potential_clients/Inserta Dental/Report templates/DBD_REPORT_TEMPLATE_SPEC.md` — design specification
3. This file — `potential_clients/Inserta Dental/Report templates/DBD_WEEKLY_REPORT_WORKFLOW.md` — the process

After reading, report to the user:
> "I've read the 3 briefing documents. Ready to start the Week N report. Which week are we reporting on?"

---

## STEP 1 — Establish the week being reported

Ask the user:
> "What is the Monday date of the week being reported? (e.g. 13 April 2026 for Week 1)"

Once answered:
- **Calculate and state back:** "Confirming: Week N covers Monday DD Month YYYY to Friday DD Month YYYY."
- **State the current calendar date** (from the system) so there's no date ambiguity
- **Confirm which days the user actually worked** — this may be fewer than 5 for Week 1, but should be all 5 for subsequent weeks. Ask the user if unsure.

**Example for Week 1:**
> "Confirming: Week 1 covers Monday 13 April 2026 to Friday 17 April 2026.
> Current date (system): [today].
> Work delivered days: Tuesday 14 April (afternoon) to Friday 17 April — client signed Tuesday afternoon, so the Work Delivered slide covers 4 days."

**DO NOT PROCEED** until the user confirms these dates.

---

## STEP 2 — List the session summary files

Glob the session summary folder for files whose date falls within the week's range.

Path: `potential_clients/Inserta Dental/Session Summary/`
Filename pattern: `SESSION_SUMMARY_DD-MM-YY[_AM/PM].md`

**Example for Week 1 (13-17 Apr 2026):** Files should include any dated 14-4-26, 15-4-26, 16-4-26, 17-4-26 (Monday the 13th no session — user hadn't started).

**Report back to the user:**
> "Found N session summaries for this week:
> - SESSION_SUMMARY_14-4-26.md (Tue)
> - SESSION_SUMMARY_15-4-26_AM.md (Wed AM)
> - SESSION_SUMMARY_15-4-26_PM.md (Wed PM)
> - SESSION_SUMMARY_16-4-26.md (Thu)
> [and add: no summary found for 17-4-26 if missing]"

Confirm with the user this list is correct before reading them.

---

## STEP 3 — Read the session summaries

Read every session summary file in full. Extract for each day:
- Headline deliverable
- Key numbers (keywords added, campaigns changed, etc.)
- Campaign-specific outcomes
- Open issues / flags for next week
- Key learnings

Build a consolidated day-by-day summary in your working notes. Do not write to disk yet.

---

## STEP 4 — Read the data files

Read the 4 CSV files in `potential_clients/Inserta Dental/data/Data For End-of-Week Reports/`:

1. `All Campaigns Daily - [week dates].csv` — daily breakdown for the week
2. `All Campaigns Past 8 weeks Weekly - [dates].csv` — 8-week rolling trend
3. `All Campaigns split by device - [week dates].csv` — device split
4. `Conversions by conversion action name for this week.csv` — Dengro funnel data

For each file:
- Verify the date range in the file header matches the week being reported
- Flag any anomalies (missing days, zero-cost campaigns that should be running, etc.)

**Compute and have ready:**
- **Week totals per campaign:** cost, impressions, clicks, avg CPC, CTR, conversions (primary), all conversions, cost/conv
- **Week totals account-wide:** same metrics, summed
- **Daily totals account-wide:** for the bar chart
- **8-week trend values** per week: Cost, All Conversions, Primary Conversions
- **Dengro funnel:** Leads, Bookings, Purchases — from conversion action CSV
- **Device split:** Mobile vs Desktop vs Tablet — click/conversion distribution

---

## STEP 5 — Read the reference template

Open the design reference: `potential_clients/Inserta Dental/reports/DentalByDesign.co.uk - Account Structure Report-v5.pptx`

Extract text with: `python -m markitdown "DentalByDesign.co.uk - Account Structure Report-v5.pptx"`

Observe:
- The exact layout pattern used on content slides
- How stat callouts are positioned
- How Key Finding / Recommendation boxes are written
- Footer format
- Tone of voice

**DO NOT skim.** The failed Week 1 drafts failed because they improvised.

---

## STEP 6 — Check for client email replies during the week

Check if there's an email thread file in the client folder:
- `potential_clients/Inserta Dental/EMAIL THREAD*.txt`

If the client has replied during the reporting week, note:
- What they confirmed
- What they clarified
- What remains open

This affects Slide 9 — see Brief section 6 for variants.

---

## STEP 7 — Produce the content outline

Before building any slides, write a complete content outline as a markdown response to the user. Structure:

```
# Week N Report — Content Outline

## Slide 1: Title
- Week N | DD-DD Month YYYY
- 4 headline stats: [X], [Y], [Z], [W]
- [any notes]

## Slide 2: Executive Summary
- 4 big stats: [X], [Y], [Z], [W]
- 3 status pills: [green item], [amber item], [red item]
- Core insight paragraph: "[draft text]"

## Slide 3: Work Delivered
- Timeline visual: [day icons]
- Tue 14 Apr: [output one-liner]
- Wed 15 Apr: [output one-liner]
- Thu 16 Apr: [output one-liner]
- Fri 17 Apr: [output one-liner]

## Slide 4: Brand Campaign
- 4 stats: [X], [Y], [Z], [W]
- Chart: 8-week CPC trend
- Key Finding: "[draft]"
- Recommendation: "[draft]"

[... continue for every slide ...]

## Slide 11: Closer
- Questions? prompt
- Contact details
```

**Present this outline to the user and wait for approval.** Do not proceed to build slides until the user says "proceed" or provides feedback to refine the outline.

---

## STEP 8 — Build the PPTX (slide by slide, verify as you go)

When the user approves the outline:

1. **Use the PPTX skill** (already loaded). For creating from scratch, use `pptxgenjs` or `python-pptx`. For editing a template, use the editing workflow.

2. **Choose approach:** Copy the v5 reference file as the starting template, then replace content slide-by-slide. This preserves layouts, fonts, and footers automatically.

3. **Build slides in order 1→11.** After every 2-3 slides, convert to images and visually inspect.

4. **Verify each slide:**
   - Numbers match the data files
   - Dates are correct (day of week, date, month)
   - Footer is present and identical
   - Colour palette is correct (only the 7 approved colours)
   - No banned elements (page counters in body, bullets in tables, etc.)

5. **Save to:** `potential_clients/Inserta Dental/End-of-week reports/DentalByDesign.co.uk - Week N Report [DD-DD MMMM YYYY]-v1.pptx`

   **Important:** Save to the `End-of-week reports/` folder. **Not** to the old `reports/` folder (that's for historical pitch reports and reference templates only).

---

## STEP 9 — Full visual QA pass

Once all 11 slides are built:

1. Convert to images: `python scripts/office/soffice.py --headless --convert-to pdf [output.pptx] && pdftoppm -jpeg -r 150 output.pdf slide`
2. **Spawn a QA subagent** (per the PPTX skill's instructions). Use this prompt:

```
Visually inspect these 11 slides of a weekly Google Ads report for Dental by Design.

Expected standard: matches DentalByDesign.co.uk - Account Structure Report-v5.pptx in layout, typography (Calibri), and 7-colour palette (#1A237E navy, #4285F4 blue, #EA4335 red, #34A853 green, #FBBC05 yellow, #1A1A1A body, #666666 muted).

For each slide, verify:
1. Title is 44pt navy bold
2. 4 stat callouts on content slides (not title/closer)
3. Chart/table/visual is present (no text-only content slides)
4. Footer: logo + "Christopher Hoole | christopherhoole.com | Confidential | page N"
5. No overlapping elements, no text overflow
6. No banned elements: accent lines under titles, page counters in body, emoji, bullets inside tables
7. Colour palette restricted to the 7 approved colours
8. Layout consistent with v5 reference

Report every issue found, even minor. If zero issues, look harder — first passes almost never find nothing.
```

3. Fix all issues reported. Re-verify affected slides. Repeat until a clean pass.

---

## STEP 10 — Verify against the brief's checklist

Run through the verification checklist in `DBD_WEEKLY_REPORT_BRIEF.md` section 8. Confirm every item is ✓ before declaring the report done.

---

## STEP 11 — Hand off to the user

Report to the user:

> "Week N report complete at:
> `potential_clients/Inserta Dental/End-of-week reports/DentalByDesign.co.uk - Week N Report [dates]-v1.pptx`
>
> 11 slides, verified against design spec and brief checklist. Ready for your review.
>
> Key numbers used:
> - Total spend: £X
> - Qualified leads: N
> - Patient enquiries: N
> - Cost per lead: £X
>
> Flag any issues and I'll produce v2."

Wait for user feedback. If they request revisions, iterate and save as `-v2.pptx` (do not overwrite v1).

---

## RECOVERY: IF YOU ARE MID-REPORT AND SOMETHING SEEMS OFF

If at any step you notice:
- A number doesn't match across sources
- A date doesn't map to the correct day of the week
- The structure is drifting from the 11-slide spec
- You're tempted to skip a step because "it seems fine"

**STOP.** Do not invent data to bridge the gap. Return to the user and say:

> "Pausing — I've noticed [specific issue]. Before continuing I need [specific clarification]."

Consistency over speed. The previous Week 1 drafts failed precisely because they cut corners.
