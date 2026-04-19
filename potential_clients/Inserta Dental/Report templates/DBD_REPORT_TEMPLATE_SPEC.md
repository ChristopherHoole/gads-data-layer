# DBD Report — Template & Design Spec (v2)

**Status:** Authoritative specification for the DBD weekly report template.
**Source of truth:** This document + `build_template.py` + `DBD_WEEKLY_REPORT_TEMPLATE.pptx`.
**Change control:** Any change to the visual system must be reflected in all three artefacts.

---

# PART 1 — GLOBAL DESIGN TOKENS

## 1.1 Slide dimensions

- **Aspect ratio:** 16:9 widescreen
- **Slide size:** 13.33" × 7.50" (12,192,000 × 6,858,000 EMU)
- **Safe area (content margins):** 0.50" from left (inside the 0.30" left colour strip, so content effectively starts at x=0.80" on light slides), 0.50" from right, 0.40" from top, 0.40" from bottom
- **Left colour strip:** 0.30" wide vertical bar at x=0, y=0, height=7.50", only on light content slides

## 1.2 Typography

**Font family:** Calibri (exclusively — no display font, no pairings). Calibri is a system font on every Windows machine with Office and renders identically everywhere. Using three weights gives us hierarchy without font dependencies.

| Role | Font | Size | Weight | Line-height |
|------|------|------|--------|-------------|
| Slide title (content slides) | Calibri | 32pt | Bold | 1.1 |
| Slide title (title/closer slides) | Calibri | 54pt | Bold | 1.1 |
| Section header (within slide) | Calibri | 22pt | Bold | 1.15 |
| Stat callout — big number | Calibri | 42pt | Bold | 1.0 |
| Stat callout — title-slide big number | Calibri | 48pt | Bold | 1.0 |
| Stat callout — label | Calibri | 13pt | Regular | 1.2 |
| Stat callout — sub-label | Calibri | 11pt | Regular | 1.2 |
| Body copy | Calibri | 13pt | Regular | 1.35 |
| Table header | Calibri | 12pt | Bold | 1.2 |
| Table body | Calibri | 11pt | Regular | 1.3 |
| Chart axis labels | Calibri | 10pt | Regular | 1.0 |
| Chart data labels | Calibri | 10pt | Bold | 1.0 |
| Footer text | Calibri | 10pt | Regular | 1.0 |
| Context / subtitle line | Calibri | 14pt | Italic | 1.2 |
| Small caps label ("KEY FINDING", "RECOMMENDATION") | Calibri | 11pt | Bold | 1.0 — uppercase |

## 1.3 Colour palette

**Primary palette (use these and ONLY these in content):**

| Name | Hex | Role |
|------|-----|------|
| Navy | `#1A237E` | Primary — titles, headers, dark slide backgrounds, section icons, left strip, 60-70% visual weight |
| Google Blue | `#4285F4` | Secondary — subtitles, accent lines, links, primary data lines, Key Finding labels |
| Google Green | `#34A853` | Positive indicator — good metric changes, positive status pills, positive stat values |
| Google Red | `#EA4335` | Negative indicator — bad metric changes, alerts |
| Google Yellow / Amber | `#FBBC05` | Warning indicator — caution metrics, amber status pills, "Flagged for Week N" labels |
| Body Dark | `#1A1A1A` | All body text (never pure black) |
| Muted Grey | `#666666` | Footer text, captions, sub-labels, secondary text |

**Neutrals (for backgrounds and shading):**

| Name | Hex | Role |
|------|-----|------|
| White | `#FFFFFF` | Default light-slide background, text on dark slides |
| Off-white | `#F7F7F7` | Subtle zebra striping for table alternating rows |
| Border light | `#E0E0E0` | Chart gridlines, table cell borders |
| Border mid | `#D0D0D0` | Table outer borders |

**Colour-use rules:**
- **Dominance:** Navy dominates (≥60% of coloured visual weight in the deck). Google blue is secondary (~25%). Traffic accents are for specific moments only (~15% combined).
- **Traffic-light semantics:**
  - Positive change for "up-good" metrics (conversions, impression share, CTR) → Google Green
  - Negative change for "up-good" metrics → Google Red
  - Positive change for "down-good" metrics (CPC, CPA, cost) → Google Green (arrow is ↓, colour is green)
  - Negative change for "down-good" metrics → Google Red (arrow is ↑, colour is red)
  - Rationale: colour conveys "is this good or bad" regardless of direction
- **Never** use pure black text. Use `#1A1A1A`.
- **Never** use light grey text on light backgrounds. Minimum `#666666` on white.
- **Never** use a colour outside this palette without explicit approval and a spec update.

## 1.4 Visual motif (signature design element)

Two repeating visual elements across every content slide:

### 1.4.1 Left colour strip
- Every **content slide** (2, 3, 4, 5, 6, 7, 8, 9, 10) has a **0.30" wide vertical strip** on the left edge
- Fill: `#1A237E` navy (always — does not vary by section)
- Height: full slide (7.50")
- Position: x=0, y=0
- **Title slide (1)** and **Closer slide (11)** do NOT have a left strip — they have full navy backgrounds instead

### 1.4.2 Section icon in coloured circle
- Every **content slide** has a section icon next to the title
- Icon: Unicode glyph (chosen per slide — see Slide Specs)
- Icon size: 22pt
- Icon colour: WHITE
- Circle: 0.45" diameter, filled navy `#1A237E`
- Positioned at x=0.80", y=0.35"
- Title text starts at x=1.45" (0.20" right of the circle)

**Why Unicode glyphs?** Avoids font dependencies. A future upgrade could swap for Material Symbols if font embedding becomes feasible.

## 1.5 Dark/light slide structure (sandwich)

| Slide | Background | Text convention |
|-------|-----------|-----------------|
| 1 (Title) | Dark navy `#1A237E` fill | White titles, Google blue accents, white big numbers |
| 2–10 (Content) | White fill, 0.30" navy left strip | Navy titles, dark body text, Google blue secondary |
| 11 (Closer) | Dark navy `#1A237E` fill | White text, Google blue accents |

## 1.6 Footer (content slides 2–10 only)

**Position:** y=7.10", height 0.30"

| Zone | Position | Content | Style |
|------|----------|---------|-------|
| Left | x=0.80, width 0.35 | ACT logo | 0.25" tall image |
| Centre | x=1.25, width 9.50 | "Christopher Hoole  |  christopherhoole.com  |  Confidential" | Calibri Regular 10pt `#666666`, centred within its box |
| Right | x=12.30, width 0.50 | Page number | Calibri Regular 10pt `#666666`, right-aligned |

Title slide (1) and Closer slide (11) do NOT have the standard footer.

## 1.7 Logo (ACT)

Path: `potential_clients/Inserta Dental/act_logo_official.png`

| Placement | Size | Position |
|-----------|------|----------|
| Title slide (top) | 0.60" tall | Centred horizontally, y=0.40" |
| Content slide footer | 0.25" tall | x=0.80", y=7.10" |
| Closer slide | 0.70" tall | Centred horizontally, y=6.30" |

## 1.8 Chart specifications (locked)

### 1.8.1 Line charts
- Line weight: 2.5pt
- Line colour: `#4285F4` primary series, `#34A853` secondary series, `#EA4335` tertiary series
- Line style: straight segments (smoothing OFF)
- Markers: filled circles, 5pt diameter, same colour as line
- Gridlines: horizontal only, `#E0E0E0`, 0.75pt
- Vertical gridlines: OFF
- Chart title: OFF (slide title serves as chart title)
- Legend: OFF if single series, ON if multi-series (bottom, 10pt Calibri)
- Axis labels: `#666666`, Calibri 10pt
- Data labels (values above markers): `#1A1A1A`, Calibri Bold 10pt

### 1.8.2 Bar / column charts
- Bar colour: `#4285F4` default; per-bar colouring when traffic-light semantics apply
- Bar width: 60% of slot width
- Gridlines: horizontal only, `#E0E0E0`, 0.75pt
- Data labels on top of bars: `#1A1A1A`, Calibri Bold 10pt
- Other settings same as line charts

### 1.8.3 Tables
- Outer border: 0.75pt `#D0D0D0`
- Header row background: `#1A237E` navy, text `#FFFFFF` Calibri Bold 12pt
- Header row height: 0.40"
- Body rows: alternating `#FFFFFF` and `#F7F7F7`
- Body row height: 0.35"
- Body text: Calibri Regular 11pt `#1A1A1A`
- Cell padding: 6pt all sides
- Column alignment: text columns left-aligned, numeric columns right-aligned, date columns left-aligned
- Numeric values: comma thousands separator, currency prefix £
- Vertical borders between columns: OFF
- Horizontal borders between rows: OFF (zebra striping provides separation)

### 1.8.4 Funnel visual (Slide 7)
- 5 stages as trapezoid shapes, horizontal flow left-to-right
- Each shape: 2.20" × 1.40"
- Widths gradually narrow: 2.30, 2.20, 2.10, 2.00, 1.90 (visual funnel effect; keeps text readable)
- Gap between stages: 0.12"
- Fill: gradient navy to Google blue across stages (stage 1 `#1A237E`, stage 5 `#4285F4`, interpolated)
- Text inside each trapezoid (centred, vertical-aligned middle):
  - Big number: Calibri Bold 26pt `#FFFFFF`
  - Label: Calibri Regular 11pt `#FFFFFF` with opacity 0.85
- Minimum shape width ensures no text wrapping mid-word

## 1.9 Status pill (Slide 2)

- Rounded rectangle, corner radius 6pt
- Dimensions: height 0.55"
- Fill: `#34A853` (green) or `#FBBC05` (amber) or `#EA4335` (red) per status
- Text: Calibri Bold 14pt `#FFFFFF`, centred horizontally and vertically

## 1.10 Stat callout (reusable component)

Used on Slide 1 (title), Slide 2 (exec summary), Slides 4/5/6 (campaign headers).

**Anatomy:**
- Number text box:
  - Size: 2.88" × 0.80"
  - Font: Calibri Bold (48pt on title slide, 42pt on content slides)
  - Colour: contextual (see slide specs); defaults to `#1A237E` navy
  - Alignment: left
- Label text box (positioned BELOW the number):
  - Size: 2.88" × 0.30"
  - **Top-Y must equal (number top-Y + number height + 0.05" gap)**
  - Font: Calibri Regular 13pt
  - Colour: `#1A1A1A` (on light slides) or `#4285F4` (on dark slides)
  - Alignment: left
- Optional sub-label below label:
  - Size: 2.88" × 0.25"
  - Font: Calibri Regular 11pt
  - Colour: `#666666`

**Critical spacing rule:** Number box and label box must NOT overlap. Validate in the builder script.

## 1.11 "Key Finding" and "Recommendation" boxes

- Label (uppercase): Calibri Bold 11pt `#4285F4`, height 0.25"
- Body: Calibri Regular 12pt `#1A1A1A`, max 1.40" height (~4-5 lines of 12pt)
- Top-Y of body = label Y + 0.30"
- Stack spacing between two blocks: 0.35"

---

# PART 2 — SLIDE-BY-SLIDE SPECS

All dimensions in inches. Coordinate origin is top-left (0, 0).

## Slide 1 — Title (DARK)

**Background:** `#1A237E` navy, full slide.
**No left strip, no footer.**

| Element | Position (x, y) | Size (w × h) | Style | Content |
|---------|----------------|-------------|-------|---------|
| ACT logo | centred, y=0.40 | 0.60" tall | PNG | `act_logo_official.png` |
| Main title | centred, y=2.60 | 12.30 × 0.90 | Calibri Bold 54pt `#FFFFFF`, centred | "Week {{WEEK_NUMBER}} Report" |
| Accent line | centred, y=3.55 | 3.00 × 0.03 | Rectangle fill `#4285F4` | — |
| Subtitle | centred, y=3.70 | 12.30 × 0.50 | Calibri Regular 24pt `#4285F4`, centred | "{{DATE_RANGE}}" |
| Descriptor | centred, y=4.40 | 12.30 × 0.45 | Calibri Regular 18pt `#FFFFFF` 85% opacity, centred | "{{WEEK_DESCRIPTOR}}" |
| Stat 1 number | x=0.90, y=5.55 | 2.88 × 0.80 | Calibri Bold 48pt `#FFFFFF`, left | "{{STAT_1_NUMBER}}" |
| Stat 1 label | x=0.90, y=6.40 | 2.88 × 0.30 | Calibri Regular 13pt `#4285F4`, left | "{{STAT_1_LABEL}}" |
| Stat 2 number | x=3.98, y=5.55 | 2.88 × 0.80 | Calibri Bold 48pt `#FFFFFF`, left | "{{STAT_2_NUMBER}}" |
| Stat 2 label | x=3.98, y=6.40 | 2.88 × 0.30 | Calibri Regular 13pt `#4285F4`, left | "{{STAT_2_LABEL}}" |
| Stat 3 number | x=7.05, y=5.55 | 2.88 × 0.80 | Calibri Bold 48pt `#FFFFFF`, left | "{{STAT_3_NUMBER}}" |
| Stat 3 label | x=7.05, y=6.40 | 2.88 × 0.30 | Calibri Regular 13pt `#4285F4`, left | "{{STAT_3_LABEL}}" |
| Stat 4 number | x=10.13, y=5.55 | 2.88 × 0.80 | Calibri Bold 48pt `#FFFFFF`, left | "{{STAT_4_NUMBER}}" |
| Stat 4 label | x=10.13, y=6.40 | 2.88 × 0.30 | Calibri Regular 13pt `#4285F4`, left | "{{STAT_4_LABEL}}" |
| Client block line 1 | x=0.50, y=6.95 | 7.00 × 0.25 | Calibri Bold 14pt `#FFFFFF` | "Dental by Design  |  Prodent Group" |
| Client block line 2 | x=0.50, y=7.20 | 7.00 × 0.22 | Calibri Regular 11pt `#4285F4` | "Christopher Hoole  ·  Google Ads Specialist  ·  christopherhoole.com" |

**Placeholders:**
- `{{WEEK_NUMBER}}`, `{{DATE_RANGE}}`, `{{WEEK_DESCRIPTOR}}`
- `{{STAT_1..4_NUMBER}}`, `{{STAT_1..4_LABEL}}`

## Slide 2 — Executive Summary (LIGHT + LEFT STRIP)

**Background:** white. **Left strip:** 0.30" navy `#1A237E`. **Footer:** standard, page "2".

### Header block

| Element | Position | Size | Style | Content |
|---------|----------|------|-------|---------|
| Icon circle | x=0.80, y=0.35 | 0.45 × 0.45 | Oval fill `#1A237E` | — |
| Icon glyph | x=0.80, y=0.35 | 0.45 × 0.45 | Calibri Bold 22pt `#FFFFFF`, centred | "▣" |
| Title | x=1.45, y=0.35 | 11.30 × 0.55 | Calibri Bold 32pt `#1A237E` | "Executive Summary" |
| Context | x=1.45, y=0.98 | 11.30 × 0.30 | Calibri Italic 14pt `#4285F4` | "Week {{WEEK_NUMBER}}: {{DATE_RANGE}}" |
| Intro | x=1.45, y=1.32 | 11.30 × 0.30 | Calibri Regular 13pt `#1A1A1A` | "{{EXEC_INTRO_LINE}}" |

### Stat callouts row (y=1.85)

4 stats at x=0.80 / 3.88 / 6.95 / 10.03 (w=2.88 each, h=0.80 for numbers, labels below per spec 1.10).

### Status pills row (y=3.40)

3 pills at x=0.80 / 4.88 / 8.95 (w=3.88 × h=0.55 each).

### Core Insight block (y=4.20)

| Element | Position | Size | Style | Content |
|---------|----------|------|-------|---------|
| Label | x=0.80, y=4.20 | 12.00 × 0.25 | Calibri Bold 11pt `#4285F4` uppercase | "CORE INSIGHT" |
| Body | x=0.80, y=4.50 | 12.00 × 2.30 | Calibri Regular 13pt `#1A1A1A` | "{{CORE_INSIGHT_TEXT}}" |

## Slide 3 — Work Delivered (LIGHT + LEFT STRIP)

**Header block:** icon "▸", title "Work Delivered", context "Week {{WEEK_NUMBER}}: {{DATE_RANGE}} · {{WORK_DAYS}} working days", intro "{{WORK_INTRO_LINE}}".

### Horizontal timeline (y=2.30)

Connector line x=1.30, y=2.54, w=10.65, h=0.02, fill `#4285F4`.

Column x-positions: 0.80 / 3.80 / 6.80 / 9.80 (4-column mode for Week 1; 5 columns for full weeks use 0.80 / 3.20 / 5.60 / 8.00 / 10.40 with w=2.32).

Per column N:
- Circle at col_x+0.40, y=2.30, dia 0.50" — fill `#4285F4`
- Circle number: Calibri Bold 20pt `#FFFFFF`, centred
- Day label at col_x, y=2.95, 2.85×0.30, Calibri Bold 13pt `#1A237E` — "{{DAY_N_DATE}}"
- Section label at col_x, y=3.30, 2.85×0.35, Calibri Bold 15pt `#4285F4` — "{{DAY_N_TITLE}}"
- Body at col_x, y=3.75, 2.85×2.40, Calibri Regular 11pt `#1A1A1A` — "{{DAY_N_BODY}}" (~50 words max)

### Key Finding strip (y=6.30)

Label + body full width (0.80 to 12.80).

## Slide 4 — Brand Campaign (LIGHT + LEFT STRIP)

Icon "◆", title "Brand Campaign", context "Week {{WEEK_NUMBER}}: {{DATE_RANGE}}", intro "{{BRAND_INTRO_LINE}}".

### Stat callouts row (y=1.85, same positions as Slide 2)

4 stats: `{{BRAND_STAT_1..4_NUMBER}}` / `{{BRAND_STAT_1..4_LABEL}}`. Stat 4 may include sub-label.

### Main body split (y=3.40)

**Left 60% — Chart area:**
- Chart at x=0.80, y=3.40, w=7.30, h=3.35 — line chart per spec 1.8.1
- Series: `{{BRAND_CPC_DATA}}` (8 floats), categories `{{WEEK_CATEGORIES_8WK}}`

**Right 40% — Insight blocks:**
- KF label at x=8.50, y=3.40 — "KEY FINDING"
- KF body at x=8.50, y=3.70, w=4.30, h=1.40 — "{{BRAND_KEY_FINDING}}"
- REC label at x=8.50, y=5.25 — "RECOMMENDATION"
- REC body at x=8.50, y=5.55, w=4.30, h=1.40 — "{{BRAND_RECOMMENDATION}}"

## Slide 5 — Performance Max (LIGHT + LEFT STRIP)

Same layout pattern as Slide 4.

Icon "◆", title "Performance Max", context + intro per placeholders.

Stat callouts: 4 stats `{{PMAX_STAT_1..4}}` with consistent pattern (recommend: Spend / Primary conv / Cost/conv / Avg CPC — matching Slide 4).

**Main body split:**
- **Left chart (x=0.80, y=3.40, w=7.30, h=3.35):** bar chart per spec 1.8.2 — daily PMax CPA
  - Data: `{{PMAX_DAILY_CPA}}` (5 values for Mon-Fri)
  - Categories: `{{DAILY_CATEGORIES}}` (5 day labels)
  - Per-bar colouring: red for pre-switch days (above target), amber for transitional, green for post-switch (on/below target)
  - Vertical dashed annotation line at the mid-week switch point
  - Annotation text "Target CPA applied {{SWITCH_DATE}}" below chart
- **Right insights:** KF + Flagged-for-Week-N blocks (note: use "FLAGGED FOR WEEK N" with `#FBBC05` amber label when flagging issues)

## Slide 6 — Dental Implants Intent (LIGHT + LEFT STRIP)

Same layout pattern. Icon "◆", title "Dental Implants Intent".

**Main body split:**
- **Left 60% — Structural transformation visual:**
  - Instead of a mis-scaled bar chart, use a clean "before → after" diagrammatic layout
  - Left column (x=0.80, y=3.40): "BEFORE" heading Calibri Bold 12pt `#666666`, followed by 4 stat rows each 0.55" tall:
    - "Ad groups" label + value + small grey indicator
  - Arrow in middle (custom shape or Unicode "→")
  - Right column: "AFTER" heading in navy, same 4 stat rows with coloured values
  - Clean comparison, consistent sizing, no misleading proportional bars

- **Right 40% — Insight blocks:** KF + RECOMMENDATION (or RECOMMENDATION replaced with "NEXT REVIEW" block if appropriate)

## Slide 7 — The Numbers That Matter (LIGHT + LEFT STRIP)

Icon "●", title "The Numbers That Matter", context "Business-level outcomes — Week {{WEEK_NUMBER}}", intro "{{NUMBERS_INTRO_LINE}}".

### Funnel visual (y=2.00)

5 trapezoid shapes, x=0.80 to 12.80, y=2.00, each h=1.40.

| Stage | x | w (trapezoid widest point) | Fill colour |
|-------|---|---|-------------|
| 1 | 0.80 | 2.30 | `#1A237E` |
| 2 | 3.22 | 2.20 | `#1F2D94` (interpolated) |
| 3 | 5.54 | 2.10 | `#2A4CB0` (interpolated) |
| 4 | 7.76 | 2.00 | `#326BCC` (interpolated) |
| 5 | 9.88 | 1.90 | `#4285F4` |

Inside each trapezoid (centred):
- Big number: Calibri Bold 26pt `#FFFFFF`
- Label: Calibri Regular 11pt `#FFFFFF` (85% opacity)

### Note below funnel (y=3.60)

Italic note: "{{FUNNEL_NOTE}}" — Calibri Italic 11pt `#666666`, full width.

### Campaign breakdown table (y=4.20)

Heading at y=4.20: "Dengro Offline Leads — by campaign" Calibri Bold 13pt `#1A237E`.

Table at y=4.55, 4 columns × 5 rows (header + 3 campaigns + TOTAL):

| Column | Width | Align |
|--------|-------|-------|
| Campaign | 4.50" | Left |
| Spend | 2.50" | Right |
| Dengro Leads | 2.50" | Right |
| Spend per Lead | 2.50" | Right |

Total row: bold text `#1A237E`, light navy tint background `#E8EAF6`.

## Slide 8 — 8-Week Context (LIGHT + LEFT STRIP)

Icon "◑", title "8-Week Context", context "{{EIGHT_WEEK_DATE_RANGE}}", intro "{{CONTEXT_INTRO_LINE}}".

### Two charts side-by-side (y=1.90)

**Left chart:** Weekly spend (£) — x=0.80, y=1.90, w=5.90, h=3.80
- Line chart, single series `#4285F4`
- Data `{{WEEKLY_SPEND_DATA}}`, categories `{{WEEK_CATEGORIES_8WK}}`
- Y-axis prefix "£", formatting thousands with k (e.g. "£17k")

**Right chart:** Weekly primary conversions — x=7.10, y=1.90, w=5.70, h=3.80
- Line chart, single series `#34A853` green
- Data `{{WEEKLY_CONVERSIONS_DATA}}`, same 8 categories

### Key Finding strip (y=6.00)

Full-width, as Slide 3. Label + body.

**Important:** Keep Key Finding body to 2 lines max to avoid bottom-edge overflow. Text frame height 0.80" MAXIMUM.

## Slide 9 — Client Clarifications & Actions (LIGHT + LEFT STRIP)

Icon "◉", title "Client Clarifications & Actions", context "{{CLIENT_REPLY_CONTEXT}}" (e.g. "Giulio's replies — Fri 17 April 16:47").

### Table (y=1.80)

2-column wide table, x=0.80, y=1.80, w=12.00, h=5.00 max.

| Column | Width | Align | Header |
|--------|-------|-------|--------|
| 1 | 6.00" | Left | "Giulio confirmed" |
| 2 | 6.00" | Left | "Action taken / scheduled" |

Alternating row shading, 0.35" row height. Body font Calibri Regular 11pt `#1A1A1A`.

For weeks with no client reply: this slide becomes "Decisions Needed" with table columns "Decision" / "Impact" / "Options".

## Slide 10 — Week N+1 Plan (LIGHT + LEFT STRIP)

Icon "▶", title "Week {{NEXT_WEEK_NUMBER}} Plan", context "{{NEXT_WEEK_DATE_RANGE}}", intro "{{PLAN_INTRO_LINE}}".

### Table (y=1.80)

3-column table, x=0.80, y=1.80, w=12.00, h=5.00 max.

| Column | Width | Align | Header |
|--------|-------|-------|--------|
| 1 | 1.80" | Left | "Day" |
| 2 | 3.20" | Left | "Focus" |
| 3 | 7.00" | Left | "Expected output" |

Day column uses Calibri Bold 11pt `#1A237E`. Focus column uses Calibri Bold 12pt `#4285F4`. Output column regular Calibri 11pt `#1A1A1A`.

5 rows for Mon-Fri.

## Slide 11 — Closer (DARK)

**Background:** `#1A237E` navy, full slide. **No left strip, no footer.**

| Element | Position | Size | Style | Content |
|---------|----------|------|-------|---------|
| "Questions?" | centred, y=2.50 | 12.30 × 0.90 | Calibri Bold 44pt `#FFFFFF`, centred | "Questions?" |
| Accent line | centred, y=3.50 | 2.00 × 0.03 | Rectangle fill `#4285F4` | — |
| Subtitle | centred, y=3.70 | 12.30 × 0.50 | Calibri Italic 16pt `#4285F4`, centred | "Happy to walk through any section of this report or align on Week {{NEXT_WEEK_NUMBER}} priorities over a call." |
| Contact name | centred, y=5.10 | 12.30 × 0.35 | Calibri Bold 14pt `#FFFFFF`, centred | "Christopher Hoole  ·  Google Ads Specialist" |
| Contact details | centred, y=5.55 | 12.30 × 0.30 | Calibri Regular 12pt `#4285F4`, centred | "christopherhoole.com  ·  chrishoole101@gmail.com  ·  +44 7451 252857" |
| ACT logo | centred, y=6.30 | 0.70" tall | PNG | `act_logo_official.png` |

---

# PART 3 — PLACEHOLDERS MASTER LIST

All placeholders the session must substitute when generating a weekly report:

## Global
- `{{WEEK_NUMBER}}` — e.g. "1"
- `{{NEXT_WEEK_NUMBER}}` — e.g. "2"
- `{{DATE_RANGE}}` — e.g. "13–17 April 2026"
- `{{START_DATE}}` — e.g. "13 April 2026"
- `{{END_DATE}}` — e.g. "17 April 2026"
- `{{NEXT_WEEK_DATE_RANGE}}` — e.g. "20 – 24 April 2026"
- `{{EIGHT_WEEK_DATE_RANGE}}` — e.g. "23 February – 17 April 2026"
- `{{WEEK_DESCRIPTOR}}` — e.g. "Account Overhaul — Foundation Week"

## Slide 1
- `{{TITLE_STAT_1..4_NUMBER}}` / `{{TITLE_STAT_1..4_LABEL}}`

## Slide 2
- `{{EXEC_INTRO_LINE}}`
- `{{EXEC_STAT_1..4_NUMBER}}` / `{{EXEC_STAT_1..4_LABEL}}` / `{{EXEC_STAT_1..4_COLOUR}}`
- `{{PILL_1..3_TEXT}}` / `{{PILL_1..3_COLOUR}}` (hex)
- `{{CORE_INSIGHT_TEXT}}`

## Slide 3
- `{{WORK_DAYS}}` (integer)
- `{{WORK_INTRO_LINE}}`
- For N=1..4 (or 1..5 if full week): `{{DAY_N_DATE}}`, `{{DAY_N_TITLE}}`, `{{DAY_N_BODY}}`
- `{{WORK_KEY_FINDING}}`

## Slides 4 / 5 / 6 (per campaign)
- `{{BRAND_INTRO_LINE}}` / `{{PMAX_INTRO_LINE}}` / `{{DII_INTRO_LINE}}`
- `{{CAMP_STAT_1..4_NUMBER/LABEL}}` per campaign
- For Slide 4: `{{BRAND_CPC_DATA}}` (8 floats)
- For Slide 5: `{{PMAX_DAILY_CPA}}` (5 floats), `{{DAILY_CATEGORIES}}`, `{{SWITCH_DATE}}`
- For Slide 6: before/after values for ad groups/keywords/RSAs (integers)
- KF / REC / FLAG text per campaign

## Slide 7
- `{{WEEKLY_SPEND_DATA}}` (same as below — or remove)
- `{{NUMBERS_INTRO_LINE}}`
- `{{FUNNEL_STAGE_1..5_NUMBER}}` / `{{FUNNEL_STAGE_1..5_LABEL}}`
- `{{FUNNEL_NOTE}}`
- Campaign table rows (3 campaigns + total): `[campaign_name, spend, leads, spend_per_lead]`

## Slide 8
- `{{CONTEXT_INTRO_LINE}}`
- `{{WEEK_CATEGORIES_8WK}}` (list of 8 strings)
- `{{WEEKLY_SPEND_DATA}}` (8 floats)
- `{{WEEKLY_CONVERSIONS_DATA}}` (8 floats)
- `{{EIGHT_WEEK_KEY_FINDING}}`

## Slide 9
- `{{CLIENT_REPLY_CONTEXT}}` or `{{DECISIONS_CONTEXT}}`
- Table rows: list of `[clarification_text, action_text]` (or `[decision, impact, options]` if no-reply variant)

## Slide 10
- `{{PLAN_INTRO_LINE}}`
- 5 rows: `[day, focus, expected_output]`

## Slide 11
- `{{NEXT_WEEK_NUMBER}}` (already defined globally)

---

# PART 4 — QA CHECKLIST (applied to every generated report)

Before declaring a weekly report complete, verify:

## Content accuracy
- [ ] All numbers trace back to source data CSVs or session summaries
- [ ] All dates match the calendar (Monday date for the reporting week is correct)
- [ ] No banned claims (99.12%, Save 60%, Top 10 Europe, Best Clinic) appear in any ad copy reference
- [ ] Client reply incorporated accurately if email received during the week

## Visual consistency
- [ ] All slide titles use Calibri Bold 32pt navy `#1A237E` (content slides) or 54pt white (title/closer)
- [ ] Every content slide (2-10) has 0.30" navy left strip at x=0
- [ ] Every content slide has section icon in navy circle at x=0.80, y=0.35
- [ ] Title (1) and Closer (11) slides have full navy backgrounds
- [ ] All fonts are Calibri
- [ ] Only approved palette colours used
- [ ] All stat callouts have labels BELOW numbers with 0.05" gap (no overlap)
- [ ] Footer on every content slide: logo + name + page number
- [ ] No footer on title or closer slides

## Layout
- [ ] No text overflow beyond slide boundaries (especially Key Finding blocks)
- [ ] No text running into or beneath other elements
- [ ] Charts have horizontal gridlines only
- [ ] Tables use zebra striping, no vertical borders, navy header
- [ ] Funnel text fits inside shapes (no mid-word wrapping)

## Data visualisation
- [ ] Line chart colours: primary `#4285F4`, secondary `#34A853`
- [ ] Bar charts: traffic-light colouring where applicable
- [ ] Annotations (e.g. bid-strategy switch dashed line) visible on charts
- [ ] 8-week chart uses full 8 data points

## File naming
- [ ] Saved to `potential_clients/Inserta Dental/End-of-week reports/`
- [ ] Filename format: `DentalByDesign.co.uk - Week N Report DD-DD MMMM YYYY-v1.pptx`
