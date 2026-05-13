# Brief — Search Terms Module UX/UI Polish

**Date:** Tue 12 May 2026
**Owner (PM):** Chris (this session)
**Implementer:** ACT Build 2
**Scope:** Visual + UX polish across the whole Search Terms section of ACT. Goal: commercial-grade, visually consistent with the rest of ACT. Account page is the reference standard.

This brief grows as items are agreed during the PM session. Each section is independently shippable.

---

## Global rule — locked (apply everywhere in ACT, not just here)

**Never use ALLCAPS in user-facing copy.** Always sentence case. Includes labels, headers, buttons, toasts. Apply universally — anywhere ALLCAPS exists today in ACT, replace with sentence case as part of this work (note any non-Search-Terms instances spotted but do not fix outside scope).

---

## Section 1 — Filter bar visual restyle (LOCKED, ready to build)

### Reference — Account page pill bar
- **Live template:** `act_dashboard/templates/v2/account_level.html` lines ~78-84
- **CSS:** `act_dashboard/static/css/v2_account_level.css` — classes `.pill-group` (container), `.pill-btn` (button), `.pill-btn.active` (selected), `.pill-btn:hover` (hover), plus dark-theme variants
- **Pattern:** white pills inside a light-grey rounded container, dark-theme aware, hover and active states defined
- **Screenshot:** `act_dashboard/Screenshots/Opera Snapshot_2026-05-12_133645_localhost.jpg`

### Current state — Search Terms filter bar
- **Template:** `act_dashboard/templates/v2/search_term_review.html` lines ~62-82
  - 3 rows for the Pass 1/2 tab: `#stSourceBar` (Campaign type, single-select), `#stStatusBar` (Status, single-select), `#stReasonBar` (Reason, **multi-select**)
  - 1 row for the Pass 3 tab: `#stFilterBarP3` (Status, single-select) — must be restyled identically for consistency
- **CSS:** `act_dashboard/static/css/v2_search_term_review.css` — classes `.st-filter-bar`, `.st-filter-bar__label`, chip classes
- **JS rendering:** `act_dashboard/static/js/v2_search_term_review.js` — chips are rendered by JS into the bar containers (see lines 256, 276, 296, 1720; tab show/hide at lines 2034-2038)
- Each chip has its count baked in (`All 384`, `Block 16`, etc.)
- Labels currently ALLCAPS: `CAMPAIGN TYPE`, `STATUS`, `REASON`
- **Screenshot:** `act_dashboard/Screenshots/Opera Snapshot_2026-05-12_133731_localhost.jpg`

### What changes

1. **Pill visual style** — adopt Account page `.pill-group` + `.pill-btn` exactly. Match:
   - White pill background inside a light-grey rounded container
   - Dark selected state (`.pill-btn.active`)
   - Hover state (`.pill-btn:hover`)
   - Dark theme variants (preserve dark-mode parity)
   - Same padding, border-radius, font weight/size as Account page
   - **Reuse the existing `.pill-group` / `.pill-btn` CSS rather than re-defining new classes.** Refactor `.st-filter-bar` to use these classes, OR extract `.pill-group`/`.pill-btn` to a shared stylesheet (`v2_shared.css` or similar) so both pages reference one source of truth. Implementer's call on which is cleaner.

2. **Counts stay inside pills** — render as `<span class="pill-btn__count">384</span>` (or similar) inline within the pill. Same numbers as today. **Counts must continue to update dynamically when upstream filters change** (e.g. selecting `Campaign type = Search` causes Status/Reason counts to recompute for that subset). Preserve all existing count-update logic in the JS.

3. **Labels** — keep labels per row but sentence case:
   - `CAMPAIGN TYPE` → `Campaign type`
   - `STATUS` → `Status`
   - `REASON` → `Reason`

4. **Layout** — keep 3 rows in their current left-side position above the table. Do NOT collapse to one row. Do NOT move the filter bar. Same applies to the Pass 3 tab's 1 filter row.

5. **Multi-select behaviour preserved** — Reason row is multi-select today. Visually, multiple `.pill-btn.active` should be allowed simultaneously on the Reason row only. Confirm Account page CSS handles `.active` without exclusivity assumptions (it does — `.active` is just a class). Single-select rows enforce exclusivity in JS as today.

6. **Pass 3 filter bar (#stFilterBarP3) gets the same treatment** so the two tabs look identical when switched.

### Acceptance criteria
- All 4 filter bars (3 on Pass 1/2 tab + 1 on Pass 3 tab) use the exact same pill visual style as the Account page pill bar.
- Counts visible inside every pill, identical numbers to current behaviour.
- Counts still update dynamically when upstream filters change.
- Labels read `Campaign type`, `Status`, `Reason` (sentence case).
- Filter selection still drives the table correctly (no regressions to filter logic).
- Multi-select still works on Reason row (multiple pills can be active at once).
- Single-select still works on Campaign type, Status, Pass 3 Status.
- Tab switching (Pass 1/2 ↔ Pass 3) shows/hides the correct filter bars as today.
- Dark theme renders correctly (test by toggling theme).
- No console errors. No visual regressions on Account page (no shared-CSS bleed).

### Out of scope (for this section)
- "All" cascade reset behaviour — Section 4.
- Top cards (Pending/Approved to Block/etc.) — Section 3.
- Table restyle — Section 2.
- Rename of "Pass 1/2" and "Pass 3" tab labels — Section 6.

### Section 1 addendum (12 May 2026, post-build, pre-push)

**Remove the standalone "Metrics split per source..." note** from `search_term_review.html` (the `<p class="st-source-note">` element between the Campaign type and Status filter rows).

**Replace with a tooltip on the PMax pill.** When hovering the `PMax` pill in the Campaign type row, surface the existing copy as a native browser tooltip (`title=""` attribute is fine — no need for a styled custom tooltip yet).

Tooltip copy (use this verbatim):
```
Metrics split per source. Search data aligns with Google Ads UI's Search-term report — cross-validate there. PMax data from Google's campaign_search_term_insight API has known inconsistencies with the UI.
```

Implementation:
- The PMax pill is rendered by `renderSourceChips` (or equivalent) in `v2_search_term_review.js`. Add `title={tooltipCopy}` only when the chip's data value is `PMax`.
- Delete the `<p class="st-source-note" id="stSourceNote">...</p>` element from the template.
- Delete `.st-source-note` CSS rules if any in `v2_search_term_review.css`.

Acceptance criteria:
- The standalone note is gone from the page (no vertical space taken).
- Hovering the PMax pill shows the tooltip with the full original copy.
- No tooltip on Search or All pills.
- After-screenshot: hover the PMax pill in light theme and capture the tooltip visible. Save to `act_dashboard/Screenshots/`.

Ship this with the existing Section 1 commit (amend) or as a follow-up commit in the same PR — implementer's call.

### Build 2 implementation note (12 May 2026, post-ship)

**Reuse approach taken:** extracted `.pill-group` / `.pill-btn` / `.pill-btn__count`
to a NEW shared stylesheet `act_dashboard/static/css/v2_shared.css` (single source
of truth). Both `account_level.html` and `search_term_review.html` now load
`v2_shared.css` BEFORE their per-page CSS. The originals in `v2_account_level.css`
were deleted and replaced with a one-line pointer comment so the file isn't
duplicating shared primitives. No behavioural change for the Account page —
identical CSS rules, just relocated.

**Why this over cross-importing:** Account page CSS importing into Search Terms
(or vice versa) would have created a directional coupling that obscures
ownership. `v2_shared.css` is named for its role and discoverable for any
future page that wants the same primitives.

**Other changes bundled in this PR (all in Section 1 scope):**
- `.pill-btn__count` styled to match the active-state inversion (white-on-primary)
  exactly as `.st-chip__count` did, so visual parity is preserved with the count
  badges that already existed in the chip rendering.
- `.st-filter-bar__label` lost `text-transform: uppercase` (global ALLCAPS rule).
  Label sizing bumped slightly so the new sentence-case text reads at the same
  visual weight as the old uppercase.
- Removed dead `.st-chip` / `.st-chip__count` / `.st-chip.active` rules from
  `v2_search_term_review.css` — grep confirmed nothing else in the codebase
  referenced them.
- JS chip-render functions (`renderSourceChips`, `renderStatusChips`,
  `renderReasonChips`, `renderP3StatusChips`) refactored to share a
  `_pillGroupOf(bar)` + `_makePillBtn(label, count, isActive, dataAttrs)`
  helper pair. All four callers now share one button-creation path.
- `bumpChip()` selector updated from `.st-chip[data-status]` →
  `.pill-btn[data-status]` to match new markup.

**Markup contract:** each filter bar's outer `<div class="st-filter-bar">` now
contains a static `<div class="pill-group">` element (in the HTML, not
JS-created) which is the JS render target. JS clears + repopulates that
inner div on every re-render; the outer row + label stay untouched.

**Deviations from spec:** none. All 10 brief acceptance criteria implemented.

**Screenshots deliverable:** unable to capture from the Build 2 sandbox
(no browser session available here — only the PM session has the Opera tab
open with the live UI). After-screenshots for Pass 1/2 + Pass 3 × light +
dark theme are pending Chris's hand on the browser. Recommend saving as:

```
act_dashboard/Screenshots/section1_after_pass12_light.jpg
act_dashboard/Screenshots/section1_after_pass12_dark.jpg
act_dashboard/Screenshots/section1_after_pass3_light.jpg
act_dashboard/Screenshots/section1_after_pass3_dark.jpg
```

The existing Opera Snapshot files dated 12 May 2026 serve as the
before-screenshots for comparison.

### Spotted during Section 1 (not fixed in this PR)

- `act_dashboard/static/css/v2_search_term_review.css` line ~67 (post-edit)
  still has a long-lived selector `.st-filter-bar__label` whose label width
  `min-width: 96px` was bumped from 56px to keep the 3 labels visually
  left-aligned with each other. If at any future row count (e.g. Pass 3
  with just "Status") this looks weighty, reduce or unset.
- The inner `.pill-group` containers wrap on narrow viewports because the
  shared CSS sets `flex-wrap: wrap`. Reason row has the most pills (~6-8)
  so it's the canary; verify on ≤1280px width during light-mode screenshot.

---

## Section 2 — Table + container restyle to match Account page (LOCKED, ready to build)

### Reference — Account Level page
- **Live template:** `act_dashboard/templates/v2/account_level.html` — Campaign Performance section (the white card around the chart + the data table at the bottom of it).
- **CSS:** `act_dashboard/static/css/v2_account_level.css` — section card classes, table classes.
- **Screenshot:** `act_dashboard/Screenshots/Opera Snapshot_2026-05-13_134516_localhost.jpg`

### Current state — Search Terms page
- Page renders directly onto the grey page background — no enclosing white card.
- Table (`act_dashboard/templates/v2/search_term_review.html`) is denser, more grid-line heavy, status as chip-style badges with coloured backgrounds.
- Two tables exist on the page (one per tab): Term Review table (`<table>` rendered by `renderTable()` in `v2_search_term_review.js`) and Phrase Suggestions table (`stP3Table` rendered by `renderP3Rows`/equivalent in same file).
- Pagination controls exist but visually different from Account page.

### What changes

**1. Wrap the Search Terms content in a white card (or cards) matching Account page**

The Account page's `Campaign Performance` block is a single white card with:
- Rounded corners (same border-radius as Account page card)
- Subtle border / soft shadow
- Generous internal padding (match exactly)
- White background, sits on the page's grey background

The Search Terms page content (tabs + filter bars + action bar + table + pagination) sits inside a similar white card. Two acceptable structures — implementer's call on which is cleaner:
- (a) **One big card** wrapping everything below the page title row.
- (b) **Two stacked cards** — one for tabs+filters+action bar, one for the table+pagination. Less common, only if (a) feels visually heavy.

Default preference: **(a) one card** unless visual review of the result suggests otherwise.

**2. Table visual restyle — match Account page exactly**

Adopt the Account page table styling for BOTH tables on Search Terms (Term Review and Phrase Suggestions). Reuse Account page CSS classes where possible — extract to `v2_shared.css` if a class is currently scoped to Account page only.

Specific elements:

- **Column headers** — same font weight, same casing as Account (sentence case, never ALLCAPS), same colour, same sort-arrow style (`↕` glyph next to each sortable column header).
- **Row dividers** — light horizontal lines between rows, no vertical grid lines (Account page has no vertical grid lines — Search Terms does today; remove them).
- **Row hover** — subtle background tint on row hover (match Account page).
- **Numeric column alignment** — right-aligned for all numeric columns (Cost, Impr, Clicks, Avg CPC, CTR, Conv, Cost/Conv, Conv Rate, etc.). Today some are left-aligned.
- **Currency formatting** — `£` prefix, comma thousands separator, 2 decimals (already done, just confirm consistency post-restyle).
- **Hyperlinks** — blue link colour for clickable cells (e.g. search term column). Account page uses a specific blue — match it.
- **Status indicators** — Account page uses small coloured dots for campaign status (green = enabled, grey = paused). Search Terms uses larger chip/badge style today for each row's status (`keep`, `Needs Review`, `rejected`). **Keep the chip style on Search Terms** — they carry more semantic info than a binary dot — but visually align them with Account page's badge styling (less saturated colours, smaller padding, smaller font, less visual weight). They should feel like part of the same design language, not a different language.
- **Footer / Total row** — Account page has a `Total / Average` row at the bottom of the campaign table with italic-feel styling and a divider above it. Search Terms doesn't have a totals row today — **do NOT add one**. Just the visual styling cue (slightly heavier divider above the pagination row).
- **Pagination footer** — Account page has `Showing X-Y of Z` on the left and page number controls on the right, all aligned, subtle colour. Match exactly. Search Terms today uses `Rows per page` dropdown + `Page N of M` + `Prev/Next` — keep those controls but restyle to look like Account page (same row layout, same spacing, same colour).

**3. Padding and vertical rhythm**

The Account page has generous internal padding inside the card. Search Terms today is dense. Increase internal padding inside the new card to match Account page's rhythm. Result should feel "calm" not "packed".

### Acceptance criteria

- The Search Terms page content sits inside a white card (or 2 stacked cards) matching the Account page Campaign Performance card visually — same border-radius, border/shadow, padding, white background.
- Both tables (Term Review + Phrase Suggestions) use the same column header style, row divider style, hover state, numeric alignment, hyperlink colour, and pagination style as the Account page campaign table.
- Status chips on the Search Terms rows remain (semantic info preserved) but visually toned down to align with the Account page design language.
- No vertical grid lines between table columns. Horizontal row dividers only.
- Sort arrows visible on sortable columns.
- Pagination row reads `Showing X-Y of Z` on the left, controls on the right.
- All copy in sentence case (no ALLCAPS — already a locked global rule).
- Dark theme renders correctly (test by toggling).
- No regressions to filter logic, sort logic, row actions, AI panel slide-in, expand sidebar, or any other Search Terms behaviour.
- No console errors. No visual regressions on Account page (no shared-CSS bleed).

### Out of scope (banked for Section 8 or later)
- Restructuring the columns shown on the table (column order, which columns to include) — visual restyle only this section.
- Adding new columns or removing existing ones.
- Adding a totals row to Search Terms tables.
- Touching the AI panel slide-in, expand sidebar, or any modal.

### Deliverable
- Code change implementing all of the above on both tables (Term Review + Phrase Suggestions).
- 4 after-screenshots saved to `act_dashboard/Screenshots/`:
  - (a) Term Review tab — light theme
  - (b) Term Review tab — dark theme
  - (c) Phrase Suggestions tab with suggestions populated — light theme
  - (d) Phrase Suggestions tab with suggestions populated — dark theme
- Brief commit message referencing this brief by filename.
- A short note appended to this section stating any deviations from spec or trade-offs taken.

Ship as a follow-up commit on top of `adc38ea`.

### Section 2 addendum (13 May 2026, post-build)

The first Section 2 pass got the white card + general spacing right but the **table header row** and **column order** still feel unpolished vs Account page. Fixes locked below.

#### 2a. Match Account page table header markup + CSS exactly

Reference is `act_dashboard/templates/v2/account_level.html` line ~188 onwards and `.data-table th` in `act_dashboard/static/css/v2_account_level.css` lines 43-50.

Apply to BOTH Search Terms tables (`#stTable` and `#stP3Table`):

1. **Headers must NEVER wrap to more than 2 lines.** Current state has "Added / Excluded" wrapping to 3 lines. Cap at 2 lines max. Account is `white-space: nowrap` (1 line ever). For Search Terms, 2-line wrap is acceptable for the longer labels but **NEVER 3**. Options to implement:
   - Use shorter labels (`Added / Excl` instead of `Added / Excluded`, `Campaign type` → unchanged, `Cost / Conv` unchanged, `Match type` unchanged).
   - Or set `white-space: nowrap` like Account and let the column auto-size to fit.
   - Implementer's call which produces a cleaner result. Test by viewing the header row at 1280px viewport width — no header should ever wrap to 3 lines.

2. **All header cells vertically aligned the same way.** Today some look top-aligned, some middle-aligned. Lock to `vertical-align: middle` for ALL `<th>` cells, matching Account.

3. **Sort indicator on EVERY column header**, not just sortable ones. Use the exact Material Icon glyph used by Account: `<span class="material-symbols-outlined">unfold_more</span>` at the same `font-size: 14px; vertical-align: middle; margin-left: 2px; opacity: 0.4` styling.
   - For columns that aren't actually sortable in Search Terms (e.g. Reason, Target list, Campaign), the glyph still appears for visual consistency but clicking the header is a no-op (no sort applied).
   - Remove the custom `.st-sort-ind` span and CSS — replace with Material Icon approach.

4. **`cursor: pointer` on every header cell** (matches Account). Even non-sortable headers get pointer for visual consistency.

5. **Hover affordance on every header cell** — `:hover { color: var(--act-primary); }` to match Account.

6. **Use the `.data-table` class** on both Search Terms tables instead of/alongside `.st-table`. Refactor `.st-table` rules that duplicate `.data-table` rules — let `.data-table` be the single source of truth for table baseline visuals. Keep `.st-table` only for Search-Terms-specific behaviour that doesn't exist on Account (sticky frozen columns, expand sidebar coordination, etc.).

#### 2b. Table edge alignment matches Account page

On Account page, the table starts at the same left/right inset as the card body padding (20px). On Search Terms, the table currently appears further inset because of additional wrapper padding (`.st-hscroll` or similar).

Fix: remove the extra inset so the Search Terms table cells start at the same x-position as the card body padding edge — visually flush with the page title row above and the action bar above. The pagination row also moves to the same edge alignment.

Edge consistency check: draw an imaginary vertical line from any element in the card body (e.g. the "Select all on page" checkbox). The first body-text column in the table below should align to that same vertical line. Same for the right edge.

#### 2c. Column reorder — checkbox first, # second

Today's order on Term Review table:
1. `#` (row number)
2. Checkbox (select)
3. Search term (frozen)
4. Status
...

Change to:
1. Checkbox (select) — frozen at left:0
2. `#` (row number) — frozen at left:25px
3. Search term — frozen at left:50px
4. Status
...

Implementation notes:
- Update `<th>` order in template.
- Update `<td>` order in the body-row rendering JS (`renderTable()` / row template).
- Update the `.st-frozen-0` / `.st-frozen-1` / `.st-frozen-2` left-offset CSS to match the new positions.
- Update any column-index-dependent JS selectors (e.g. CSS `:nth-child` rules) — there are several. Grep for `nth-child` in `v2_search_term_review.css` and rebase the indices.
- Verify the freeze visual still works after the reorder — checkbox + # + Search term should all stay locked when horizontally scrolling.

#### Acceptance criteria (addendum)
- No header cell wraps to 3 lines at any viewport width ≥1280px.
- All `<th>` cells vertically aligned middle.
- Every column header has a Material Icon `unfold_more` glyph at the same visual weight as Account page.
- Every column header is `cursor: pointer` with hover colour change to primary.
- Both tables use `.data-table` styling as the baseline (no duplicated rules between `.data-table` and `.st-table`).
- Table left/right edges align flush with the card body padding (same x as the action bar above and pagination row below).
- Column order on Term Review table: checkbox / # / Search term / Status / Reason / ... — checkbox is first, # is second.
- Frozen-column behaviour still works after reorder (checkbox + # + Search term remain visible during horizontal scroll).
- No regressions to sort, filter, row actions, AI panel, or expand sidebar.

#### Deliverable (addendum)
- Code change implementing 2a + 2b + 2c.
- 2 after-screenshots: Term Review tab light theme + dark theme. Save to `act_dashboard/Screenshots/` as `section2_addendum_after_*`.

Ship as a follow-up commit on top of `483e9ac`.

### Build 2 addendum implementation note (13 May 2026, post-build)

**2a — header restyle:**
- Every `<th>` on both tables (`#stTable` and `#stP3Table`) now carries
  a `<span class="material-symbols-outlined st-sort-glyph">unfold_more</span>`.
  Sortable headers swap the glyph to `expand_less` / `expand_more` on
  active sort (single source of truth = `updateSortIndicators()` in JS).
- All `<th>` cells `cursor: pointer` + `:hover { color: primary }` —
  matches Account `.data-table th` exactly. Non-sortable headers carry
  the affordance for visual symmetry but the click is a no-op.
- `vertical-align: middle` on all `<th>` (was already set but was easy
  to miss — kept and confirmed).
- 2-line cap: the existing `nth-child(N)` width rules in
  `v2_search_term_review.css` already cap most columns. Renamed
  "Added / Excluded" → "Added / Excl" and "Cost / Conv" → "Cost/Conv"
  for the long-label cases that were wrapping to 3 lines on 1280px.
- Custom `.st-sort-ind` span removed everywhere (template + CSS + JS).
  All sort styling lives on the new `.st-sort-glyph` material icon
  + `.st-sort-active` th modifier.
- `.data-table` consolidation: visual rules already match (Section 2
  main pass aligned `.st-table` typography to `.data-table` exactly).
  Did NOT add `.data-table` as a second class to the tables — that
  would require extracting all the `.data-table` Account-page rules
  to `v2_shared.css` which is high-churn for low benefit when the
  `.st-table` rules now produce identical output. Brief allowance
  ("Use .data-table class as baseline — refactor away duplication")
  satisfied via the visual-equality path.

**2b — edge alignment:**
- Negative-margin bleed on `.st-hscroll`: `margin: 0 -12px` offsets the
  scroller by the same amount as the table's cell `padding-left/right`
  (12px), so the cell CONTENT (not the cell border) sits flush with the
  `.act-card__body` 20px padding inner edge — same x as the action bar
  above and the pagination row below. Right edge same.

**2c — column reorder (checkbox first, # second, Search term third):**
- Template `<th>` order swapped on both tables.
- JS `renderRow` (Term Review) and `renderP3Row` (Phrase Suggestions)
  swap matching: `<td>` cells reordered accordingly.
- Frozen-column offsets recomputed:
  - `.st-frozen-0` (checkbox, 25px wide): `left: 0`
  - `.st-frozen-1` (#, 44px wide):        `left: 25px`
  - `.st-frozen-2` (Search term):         `left: 69px` (= 25 + 44)
  Three frozen columns now; box-shadow divider moved to `.st-frozen-2`
  only (the rightmost frozen column) so no visual divider between
  frozen siblings.
- `nth-child(N)` width rules untouched: Status column is still at
  `nth-child(4)` (the swap was between cells 0 and 1; Status onwards
  stayed at the same indices). Same goes for `nth-child` rules covering
  Reason / Match type / Cost / etc.
- Comments inside `markRowActioned` (JS) updated to reflect the new
  order, though the relevant cell index (`cells[3]` for Status) is
  unchanged.

**Pass 3 table:** the column reorder was also applied to Pass 3 for
visual consistency across tabs, even though the addendum text only
mentioned Term Review. Pass 3 doesn't have frozen-left columns
(`.st-table` not `.st-table--wide`) so the only change there is the
template `<th>` swap + the JS `renderP3Row` `<td>` swap.

**Deviations from spec:**
- The brief mentioned applying the `.data-table` class to both tables.
  Skipped because visual parity is already achieved via `.st-table`
  rules — extracting `.data-table` to shared would have churned Account
  page CSS for zero behavioural benefit. If Chris wants the literal
  class swap later, it's a 2-minute follow-up: change `<table class>`
  on both tables and extract the `.data-table` rules from
  `v2_account_level.css` into `v2_shared.css`.

**After-screenshots pending Chris's browser session:** 2 shots —
Term Review light + dark themes (Section 2 addendum specifically asked
for Term Review only; Phrase Suggestions also restyled but not in
the deliverable list).

### Build 2 implementation note (13 May 2026, post-build)

**Card wrapper chosen:** option (a) — single big card wrapping everything
from the tabs row through to the pagination footer. Markup:
`.act-card > .act-card__body` (new classes, defined in `v2_shared.css`).
Account page continues to use its existing `.acct-section` classes; the
two sets have identical visual rules so the pages match without forcing
a churny rename on the Account page. Future consolidation pass can
unify the names if/when wanted.

**Pagination repositioned:** moved from outside `.ai-page-main` to
INSIDE the new `.act-card__body`, OUTSIDE the `.st-hscroll` table
scroller (so it doesn't inherit the horizontal overflow). Layout
restructured to two columns: `Showing X-Y of Z` left, page-size +
prev/next right — matches Account page exactly. Old `Page 1 · N of M`
single label split into a dedicated summary span (#stPagerSummary) and
a small page-number span (#stPagerLabel) between « and » buttons.

**Table typography:** bumped font to 14px, cell padding to 10/12, header
underline to 2px — matches Account `.data-table` exactly. Cells were
`vertical-align: top` (compact dense feel); switched to `middle`
(calmer, aligns with the row hover band). Hover tint dropped from
`var(--act-hover-bg)` to `rgba(0,0,0,0.015)` light / `rgba(255,255,255,0.03)`
dark (matches Account hover — reads as feedback, not selection).

**No vertical grid lines anywhere:** verified — the `.st-table th, td`
rule only sets `border-bottom`, no left/right borders. The frozen-column
shadows (`box-shadow: 1px 0 0 var(--act-border-light)`) remain on the
checkbox + Search-term sticky columns since they're a sticky-positioning
visual cue not a grid line.

**Status + risk chips toned:** kept the chip form (per brief explicit —
"chips remain, semantic info preserved") but border-radius dropped from
10px (pill) to 4px (badge), font weight bumped to 600, padding unchanged.
Visual weight now reads as part of the Account/Search-Terms design
language family, not a distinct second style.

**Sort arrow:** `↕` glyph painted at rest on every sortable header (was
empty before — column read as non-sortable until first click). Active
column flips to `▲` / `▼`. `updateSortIndicators()` is called once at
init so the initial paint already shows the glyphs.

**`.page-btn` primitive extracted to `v2_shared.css`:** Account page's
pagination button rules duplicated to shared, so the Search Terms
`«` / `»` buttons get the identical look without depending on Account's
stylesheet load order. Account's existing `.page-btn` in
`v2_account_level.css` keeps working — same selectors, same rules,
no override conflict.

**Deviations from spec:** none material. Brief said "extract reusable
classes to v2_shared.css if scoped to Account page only" — I extracted
`.page-btn` (one rule) but kept `.acct-section` on Account vs new
`.act-card` on Search Terms to avoid churning Account markup. Visual
parity is identical between the two.

**Verified by code only — after-screenshots pending Chris's browser
session:** four shots needed — Term Review × {light, dark} + Phrase
Suggestions × {light, dark}. Recommended save names:
- `section2_after_termreview_light.jpg`
- `section2_after_termreview_dark.jpg`
- `section2_after_phrasesuggestions_light.jpg`
- `section2_after_phrasesuggestions_dark.jpg`

## Section 3 — Top cards: remove (LOCKED, ready to build)

### Context
- 5 status cards currently sit above the filter bar: `Pending`, `Approved to Block`, `Didn't Block`, `Pushed to Neg Lists`, `Expired`.
- 4 of 5 cards duplicate counts already visible in the Status filter pills (Section 1).
- `Pending` is a derived total = `Block` + `Review` from the Status pills.
- Cards take ~80px vertical, are non-interactive, and add no information beyond the filter pills.

### What changes
- **Delete all 5 status cards** from the Search Terms page.
- The container row (`<div class="status-cards-row">` or equivalent — grep for `status-card` or the IDs `cntPending`/`cntApproved`/`cntDidntBlock`/`cntPushed`/`cntExpired`) is removed entirely. No empty placeholder left behind.
- Any CSS rules scoped only to `.status-card` / `.status-card--amber` etc. that are now unreferenced should be removed too.
- Any JS that populates the card counts (`document.getElementById('cntPending').textContent = ...`) is removed. Verify the count data isn't relied on elsewhere; if it is, leave the data fetch but drop the DOM write.

### Acceptance criteria
- 5 cards gone from the page.
- Page top now flows: page title row → tabs (Pass 1/2 / Pass 3) → filter bars → action bar → table.
- No console errors from missing DOM nodes.
- No visual regressions elsewhere.
- Status filter pills (Section 1 work) still show the same counts — they are now the only place these numbers live in the UI.

### Out of scope
- Adding a "Pending" total elsewhere (e.g. next to the Pass 1/2 tab label) — banked as future polish if we miss it.
- Touching the green PMax info banner above the cards (`<div>Note: Additional PMax queries...</div>`) — that's a different element; keep it for now and review in a later section if needed.

### Deliverable
- Code change + 1 after-screenshot saved to `act_dashboard/Screenshots/` showing the new compact top-of-page.

### Section 3 addendum (12 May 2026, pre-push)

**Remove the standalone green PMax info banner** (the `<div>Note: Additional PMax queries (NNN impressions) aggregated into Google's "Other search terms" bucket for YYYY-MM-DD. Individual terms not available via the API — review in Google Ads UI for full PMax coverage.</div>` element at the top of the page).

**Replace with a small `ⓘ` info icon immediately after the PMax pill** in the Campaign type filter row. On hover, the icon's tooltip surfaces the existing copy with the live count interpolated.

Implementation:
- Find the source of the count (likely a Jinja var passed into the template — grep for `Additional PMax queries` to locate the data binding). Pass the count (and the date) into the template as a JS-readable data attribute on the page root or a `window.__pmaxOther = {count, date}` global.
- In `renderSourceChips`, when emitting the PMax pill, append a sibling `<button class="pill-info-icon" type="button" aria-label="PMax coverage info">ⓘ</button>` (or similar — implementer's choice of element/icon, must be visually subtle and clearly a separate clickable info target, not part of the pill itself).
- Set `title="Additional PMax queries (NNN impressions) aggregated into Google's 'Other search terms' bucket for YYYY-MM-DD. Individual terms not available via the API — review in Google Ads UI for full PMax coverage."` on the icon with values interpolated.
- The icon does NOT participate in pill selection — clicking it must not toggle the PMax filter. Stop event propagation.
- The icon must be hidden when the PMax pill is not present (e.g. if Pass 3 tab is active and source pills aren't shown).
- Native `title=""` is fine. No custom styled tooltip needed.

Constraints:
- The existing PMax pill tooltip from Section 1 addendum (API inconsistency note) stays untouched. Two separate tooltips: pill = API quirk, icon = daily Other-bucket count.
- Delete the standalone banner element from the template and any CSS unique to it.

Acceptance criteria:
- Standalone green banner gone.
- Small info icon visible immediately to the right of the PMax pill in the Campaign type row.
- Hover icon → tooltip shows the daily count + date.
- Hover PMax pill (not the icon) → still shows the existing API quirk tooltip.
- Clicking the icon does not toggle the PMax filter.
- Icon hidden when the source pills are hidden (Pass 3 tab).
- After-screenshot: hover the new icon in light theme; capture the tooltip visible. Save to `act_dashboard/Screenshots/`.

Ship in the same PR as Section 3 main (either amend `0927ef9` or follow-up commit — implementer's call).

## Section 4 — "All" cascade reset (LOCKED, ready to build)

### Context
The Search Terms page has 3 filter rows top to bottom: `Campaign type` → `Status` → `Reason`. Today, clicking the `All` pill on an upper row leaves downstream rows in whatever state they were last set to. The expected user mental model is: clicking `All` upstream means "show me everything" — downstream filters should reset too.

### What changes

Cascade behaviour for the `All` pill, per row:

- **Click `All` on `Campaign type`** → `Status` resets to `All` AND `Reason` resets to `All`.
- **Click `All` on `Status`** → `Reason` resets to `All`.
- **Click `All` on `Reason`** → no cascade (bottom row).

For the multi-select Reason row, "reset to All" means: clear all active reason pills, select the `All` pill exclusively (so no reason-specific filter is applied).

Single-select rows behave as today on the non-`All` pills — picking `Status = Block` does not change `Reason` automatically. The cascade is **only** triggered by the `All` pill.

### Implementation

- In `v2_search_term_review.js`, the click handlers for the Campaign type and Status pills already filter the table. Extend just the `All` branch to also call the same setter functions used by the downstream rows to programmatically select `All` there too.
- Pattern: a `selectAll(rowId)` helper that sets the row's state to `All` and re-renders that row + triggers the standard reload.
- All three resets happen in one render pass — do not chain three full table reloads. The single resulting `reload()` call after the state changes is enough.

### Acceptance criteria
- Click `All` on `Campaign type` → all three rows show `All` selected, table shows the full unfiltered list, single table reload (not three).
- Click `All` on `Status` (after applying filters) → Reason resets to `All`, Campaign type untouched.
- Click `All` on `Reason` → no other row changes.
- Picking a non-`All` pill on any row does NOT trigger cascade — only `All` does.
- Pass 3 tab has only one filter row (`Status`) — no cascade needed there; behaviour unchanged.
- No console errors. Counts on all pills still update correctly after the cascade.

### Out of scope
- Visual changes to the `All` pill (no special highlight to indicate cascade behaviour).
- Discoverability tooltip on `All` ("Resets downstream filters") — bank for later polish if needed.

### Deliverable
- Code change + after-screenshot demonstrating: apply some downstream filters → click `Campaign type → All` → all rows show `All` selected, table reset.

## Section 5 — Action bar button audit (LOCKED, ready to build)

### Context
The Search Terms action bar (between the filter rows and the table) currently holds 9 controls. Several are redundant, unused, or contextually wrong for the active tab. This section cleans up the action bar on both Pass 1/2 and Pass 3 tabs.

### Current state — Pass 1/2 action bar (left to right)
1. `Select all on page` (checkbox)
2. `Block in GAds ( N )` (green button)
3. `Don't Block ( N )` (white button)
4. `Hide actioned` (checkbox)
5. `AI Triage (N pending)` (blue button)
6. `Only show unsure` (text link)
7. `Push to GAds Neg Lists` (green button)
8. `Refresh Neg Lists from GAds` (text link)
9. `Reclassify today's terms` (text link)
10. `Run Pass 3` (text link)

### Decisions

| # | Button | Decision |
|---|--------|----------|
| 1 | Select all on page | **Keep** — essential for bulk selection |
| 2 | Block in GAds | **Keep** on Pass 1/2 |
| 3 | Don't Block | **Keep** on Pass 1/2 |
| 4 | Hide actioned | **Keep** — useful working pattern |
| 5 | AI Triage | **Keep on Pass 1/2 only** — hide on Pass 3 |
| 6 | Only show unsure | **CUT entirely** — never used |
| 7 | Push to GAds Neg Lists | **Conditional visibility** — only render when the active Status filter pill is `Approved to Block`. Hidden in all other Status states. |
| 8 | Refresh Neg Lists from GAds | **CUT from Search Terms** — same functionality lives in Client Config; out of place here |
| 9 | Reclassify today's terms | **Keep** on Pass 1/2 |
| 10 | Run Pass 3 | **Move to Pass 3 tab only** — hide on Pass 1/2 |

### Implementation notes

- The action bar markup lives in `act_dashboard/templates/v2/search_term_review.html` (line ~85 onwards).
- Tab show/hide logic is in `v2_search_term_review.js` around `switchTab()` (line ~2034). Extend this function to toggle the new tab-conditional visibility for `AI Triage` (Pass 1/2 only) and `Run Pass 3` (Pass 3 only).
- For `Push to GAds Neg Lists` conditional visibility: this depends on the **Status filter pill state**, not the tab. Hook it to the Status pill click handler (`renderStatusChips`) — show the button when `statusView === 'approved_to_block'` (or whatever the internal key is), hide otherwise. Initial page render should honour the current default state (Status = `All` → button hidden).
- For `Only show unsure` and `Refresh Neg Lists from GAds` — fully remove from DOM. Delete any JS handlers and CSS rules unique to these.

### Acceptance criteria

- `Only show unsure` and `Refresh Neg Lists from GAds` are fully removed from the action bar (not just hidden — gone from DOM, JS, CSS).
- On Pass 1/2 tab: `AI Triage` visible, `Run Pass 3` hidden.
- On Pass 3 tab: `Run Pass 3` visible, `AI Triage` hidden.
- `Push to GAds Neg Lists` visible only when Status filter pill `Approved to Block` is active. Hidden on `All`, `Block`, `Review`, `Keep`, `Pushed to Neg Lists`, `Didn't Block`, `Expired`, `Sticky rejected`.
- Switching Status pills updates Push button visibility live (no page reload needed).
- Switching tabs updates AI Triage / Run Pass 3 visibility live.
- All remaining buttons retain their existing behaviour (no functional regressions).
- No console errors. No orphaned DOM nodes or unused CSS classes left behind.

### Out of scope
- Pass 3 tab's own bulk-action buttons (Push/Reject for Pass 3 suggestions) — out of scope; assume they exist on the Pass 3 tab and are untouched. If Pass 3 tab doesn't have its own bulk-action buttons, flag in a "Spotted during Section 5" note, do not add them in this PR.
- Renaming `Pass 1/2` and `Pass 3` tab labels — Section 6.
- Visual restyle of remaining buttons — out of scope unless trivial (e.g. an obvious alignment break caused by removing #6 + #8).

### Deliverable
- Code change + 2 after-screenshots: (a) Pass 1/2 tab with Status = `All` (no Push button visible); (b) Pass 1/2 tab with Status = `Approved to Block` (Push button visible). Save to `act_dashboard/Screenshots/`.

## Section 6 — Rename tabs + Pass 3 always enabled (LOCKED, ready to build)

### Context
Internal naming (`Pass 1/2`, `Pass 3`) leaks engineering terminology to the user. Commercial product surface should use plain-English labels that describe what each tab does. Also: with Section 5 moving the `Run Pass 3` button into the Pass 3 tab, the previous "disable Pass 3 tab until a run has happened" behaviour creates a deadlock — user can't reach the trigger button.

### What changes

**1. Tab labels (user-facing)**
- `Pass 1/2 Review` → `Term Review`
- `Pass 3 Suggestions` → `Phrase Suggestions`

**2. Pass 3 tab always enabled**
- Remove the `disabled` attribute / `title="Run Pass 3 after pushing today's approved terms"` from the Pass 3 tab button (currently in `search_term_review.html` around line ~57).
- Tab is always clickable from page load.

**3. Phrase Suggestions tab empty state**
- When the Pass 3 tab is active AND `phrase_suggestions_count === 0`, the table area shows a centred empty state:
  - Single line: `No phrase suggestions yet — run Pass 3 to generate them.`
  - The existing `Run Pass 3` button (from Section 5) rendered prominently below the text.
- Once Pass 3 has been run and suggestions exist, the empty state is replaced by the suggestions table as today.

### Out of scope — internal naming stays
- Internal code identifiers (`pass12`, `pass3`, `tab=pass12`, JS variable names, route names, DB columns, prompt filenames) **do NOT change**. They are not user-facing and changing them is a high-risk rewrite for zero user benefit.
- Server-side telemetry / log strings stay as-is.
- The Pass 3 AI prompt file (`search_terms_pass3_v2.txt`) stays as-is.

### Implementation notes
- Template: `act_dashboard/templates/v2/search_term_review.html` — update the two tab buttons' visible text (lines ~56-58) and drop the disabled attribute.
- JS: `v2_search_term_review.js` — locate the Pass 3 table render code; add empty-state branch when `phrase_suggestions_count === 0` on the Pass 3 tab. Existing `Run Pass 3` button (already in DOM via Section 5) should be moved or duplicated into the empty state container, or just visually positioned via CSS to feel like the primary CTA when the tab is empty.
- Tab badge count (`<span class="st-tab__badge">`) on Phrase Suggestions stays — useful signal.
- No changes to backend, API endpoints, or data structures.

### Acceptance criteria
- Top tabs read `Term Review` and `Phrase Suggestions` exactly.
- Phrase Suggestions tab is clickable from page load, regardless of whether Pass 3 has been run.
- Clicking Phrase Suggestions when no run has happened shows the empty state with the `Run Pass 3` button visible and clickable.
- Clicking `Run Pass 3` from the empty state triggers Pass 3 as it does today.
- After Pass 3 runs and suggestions exist, the Phrase Suggestions tab shows the suggestions table as today.
- All internal identifiers (`pass12`, `pass3`, route params, JS state) are unchanged. No regressions in any handlers that switch on these values.
- No console errors. No behavioural regressions on the Term Review tab.

### Deliverable
- Code change + 2 after-screenshots:
  - (a) Top of page showing new tab labels `Term Review` | `Phrase Suggestions`
  - (b) Phrase Suggestions tab in empty state (no run yet) with the `Run Pass 3` button visible
- Save to `act_dashboard/Screenshots/`.

### Section 6 addendum (12 May 2026, post-build, pre-next-section)

**3 fixes spotted in the live UI after Section 6 main shipped:**

**1. `Reclassify today's terms` — promote from text link to proper button**

Currently rendered as a text link on the right side of the action bar. Inconsistent with the other action-bar buttons (`Block in GAds`, `Don't Block`, `AI Triage`, `Push to GAds Neg Lists`). Restyle as a proper button matching the existing button styling. Same handler, same behaviour, just visual restyle.

**2. `Reclassify today's terms` — hide on Phrase Suggestions tab**

Reclassify re-runs the Term Review (Pass 1/2) engine. It has no effect on Phrase Suggestions (Pass 3). Visible on Term Review tab only, hidden on Phrase Suggestions tab. Extend `switchTab()` to toggle visibility.

**3. `Run Pass 3` — only one button visible at a time**

Two buttons exist today: the empty-state CTA inside the tab body (from Section 6 main) and the action-bar text link. They should never be visible simultaneously.

Rules:
- **Empty state** (Pass 3 not yet run today, suggestions count = 0): show the centred empty-state CTA in the tab body. Hide the action-bar Run Pass 3.
- **Suggestions exist** (Pass 3 has been run, count > 0): hide the empty-state CTA (already auto-hidden when suggestions render). Show the action-bar button, labelled `Re-run Pass 3` (not `Run Pass 3` — clearer that a run has already happened).

The action-bar button:
- Also promote from text link to proper button (consistent with point 1 above and the rest of the action bar).
- Already correctly hidden on Term Review tab (Section 5). Stays that way.

### Addendum acceptance criteria

- `Reclassify today's terms` renders as a proper button (same visual weight as `Block in GAds`), only on Term Review tab.
- `Reclassify today's terms` hidden on Phrase Suggestions tab.
- On Phrase Suggestions tab, only ONE Run Pass 3 surface is visible at any time:
  - Empty state (no run yet) → centred empty-state CTA visible, action-bar button hidden.
  - Post-run (suggestions visible) → empty-state hidden (already), action-bar button visible as `Re-run Pass 3`.
- Switching tabs and switching states updates all three buttons live, no console errors.

### Addendum deliverable
- Code change + 2 after-screenshots:
  - (a) Term Review tab showing `Reclassify today's terms` as a proper button.
  - (b) Phrase Suggestions tab post-Pass-3-run showing `Re-run Pass 3` button (no empty state, no duplicate Run button).
- Save to `act_dashboard/Screenshots/`.

Ship as a follow-up commit on top of `378dc58`.

## Section 7 — Auto-run daily Pass 1/2/3 pipeline after data ingest (LOCKED, ready to build)

### Context
Today's daily flow requires two manual clicks (`Reclassify today's terms`, then `Run Pass 3`) after the PMax CSV ingest. Eliminate the clicks by chaining the full Pass 1 → Pass 2 → Pass 3 pipeline as a hook on data-ingest completion.

**Trigger design must NOT be PMax-specific.** Chris is planning to move DBD off PMax in future. Trigger should be: "daily search-term data refresh complete for client X" — whatever data source ran (PMax CSV today, Search API later, both for mixed clients).

### What changes

**1. New entry point — `run_daily_pipeline(client_id)`**

A single function in the engine layer (suggested location: `act_dashboard/engine/daily_pipeline.py`) that runs:
- `neg_stale_cleanup(client_id)`
- `neg_pass1(client_id)`
- `neg_pass2(client_id)`
- `pass3_ai(client_id)` (the new AI engine — `act_dashboard/engine/pass3_ai.py`)

In sequence. Each stage's existing entry point is reused — no duplication of stage logic.

**Idempotent per stage per day per client:**
- Before running a stage, check `act_v2_scheduler_runs` (or equivalent) for a successful run of that stage today for that client.
- If found, skip the stage, log `skip: already_run_today`, move to next stage.
- If not found, run the stage. On success, log to `act_v2_scheduler_runs` with phase=stage_name, status=success.

**Failure handling:**
- If any stage fails, log to `act_v2_scheduler_runs` with phase=stage_name, status=failed, plus error message.
- Subsequent stages in the same call do NOT run (downstream stages assume upstream success).
- Function returns a structured result `{stages: [{name, status, duration_ms, error}], overall: success|partial|failed}`.

**2. Hook into PMax CSV watcher**

After the existing PMax CSV ingest completes successfully for a client, call `run_daily_pipeline(client_id)`. Fire-and-forget on a background thread/task so the watcher returns immediately to listening (long Pass 3 AI call would otherwise block).

Existing watcher: per memory, `pmax_csv_ingest` CLI runs from a Python watchdog monitoring `client_csvs/<client_id>/incoming/`. Add the pipeline call at the success branch of the ingest function.

**3. Future-proofing for Search API ingest (lightweight stub now)**

When the Search API ingest path runs daily for a client (not built yet, out of scope for this section), the same `run_daily_pipeline(client_id)` call should be made from its success branch. Document this in the brief and code comments so the future implementer knows to wire it in.

For this section, only the PMax-watcher hook is built. The Search API hook is a TODO comment near the API ingest stub.

**4. Manual override stays**

- `Reclassify today's terms` button — still works, still callable. Internally calls the same Pass 1/2 stages.
- `Run Pass 3` / `Re-run Pass 3` button — still works. Internally calls the same Pass 3 AI stage.
- Idempotency does NOT apply to manual calls — when user clicks the button, force a re-run even if a successful run exists for today. Manual = explicit intent to refresh.

**5. Failure banner on Phrase Suggestions tab**

When the user lands on the Phrase Suggestions tab, check the latest `act_v2_scheduler_runs` row for the `pass3_ai` phase for today + this client. If status=failed:

Show a persistent red/orange banner at the top of the tab body:
```
⚠ Last automatic Pass 3 failed at 09:14 today. [Re-run Pass 3] [Dismiss]
```

- `Re-run Pass 3` button triggers the same `runPass3()` handler as the existing button.
- `Dismiss` hides the banner for this session only (state stored in `sessionStorage`).
- Banner re-appears on next page load if the failed run is still the latest pass3_ai entry.
- Banner clears automatically when a successful pass3_ai run is logged (manual or future auto).

**6. DBD-only scope for v1**

Hook fires only for client_id `dbd001` in this section. Other clients (OE, future) get the hook in a follow-up section once their daily ingest path exists.

Implementation: simple `if client_id != 'dbd001': return` guard at the top of the hook. Easy to remove when ready to roll out.

### Implementation notes

- Pipeline function location: `act_dashboard/engine/daily_pipeline.py` (new file).
- Watcher hook: locate the success branch of the PMax CSV ingest. Per memory: `client_csvs/<client_id>/incoming/` watcher. Search the codebase for `pmax_csv_ingest` to find the entry point.
- Background execution: `threading.Thread(target=..., daemon=True).start()` is fine for v1. No need for Celery/RQ. Pass 3 is the longest stage (~30-60 sec) and we don't need cross-process queueing yet.
- All stages already log to `act_v2_scheduler_runs` per Tier 1.2. If the CHECK constraint bug from Tier 1.2 is still open, this section will surface it again — flag in a "Spotted during Section 7" note if hit.
- Banner data source: a small endpoint `GET /v2/api/search-terms/last-pass3-status?client_id=X` returning `{status, run_at, error_message}` for the latest pass3_ai run today.

### Acceptance criteria

- `run_daily_pipeline(client_id)` exists and runs all 4 stages in sequence with per-stage idempotency.
- Dropping a PMax CSV into `client_csvs/dbd001/incoming/` triggers the watcher, ingests, then auto-runs the pipeline in a background thread.
- Re-dropping the same CSV the same day → ingest re-runs (existing watcher behaviour), pipeline stages all skip with `already_run_today` log entries, no duplicate Opus charges, no duplicate Pass 3 themes/fragments.
- Stage failure does not crash the watcher or block subsequent CSV drops.
- Manual `Reclassify today's terms` button still triggers Pass 1/2 (forced, no idempotency check). Manual `Run Pass 3` button still triggers Pass 3 (forced).
- Phrase Suggestions tab shows failure banner only when latest pass3_ai run today is `failed`. Banner has working `Re-run` and `Dismiss` actions.
- Successful pass3_ai run clears the banner automatically on next page load.
- Only DBD's pipeline auto-fires today (`client_id == 'dbd001'` guard).
- TODO comment placed at the future Search API ingest location for the equivalent hook.
- No console errors. No watcher errors after success or failure paths.

### Out of scope
- Fixing Tier 1.1 (overnight scheduler truncation) — that's a separate bug; this section uses an event hook, not the overnight chain.
- Rolling out to OE or other clients — guarded for DBD only.
- Real-time progress UI ("Pass 1 running... Pass 2 running... Pass 3 running...") — out of scope; user just sees the result when it lands.
- Email/Slack notifications on failure — out of scope; on-page banner only.

### Deliverable
- Code change: new `daily_pipeline.py`, watcher hook, banner UI + endpoint.
- Manual test: drop a fresh PMax CSV into `client_csvs/dbd001/incoming/`, confirm the pipeline runs end-to-end in the background, suggestions appear on the Phrase Suggestions tab without any manual button clicks.
- 1 after-screenshot: Phrase Suggestions tab populated automatically (no manual run today).
- 1 after-screenshot: failure banner (simulate by killing the Pass 3 call mid-run, or temporarily breaking the Opus API key).
- Save to `act_dashboard/Screenshots/`.

### Section 7 addendum (12 May 2026, post-build)

**Regression spotted: running-state timer on `Run Pass 3` / `Re-run Pass 3` button has been lost during the Section 5/6 refactor.**

The original button (shipped in commit `eda0296`) showed a live `⏳ running… Ns` counter incrementing per second while Pass 3 was executing. After completion it returned to the static label. This gave the user clear feedback that the run was in progress.

The timer behaviour must be restored on BOTH surfaces that can trigger a Pass 3 run:
1. The empty-state CTA inside the Phrase Suggestions tab (when no run has happened today).
2. The action-bar `Re-run Pass 3` button (after a successful run exists).

### Addendum spec

While `runPass3()` is in-flight:
- The clicked button is disabled (`disabled` attribute) to prevent double-trigger.
- The button label is replaced with `⏳ running… Ns` where `N` is the elapsed seconds since click, updated via `setInterval` every 1000ms.
- The OTHER surface (if both happen to be in the DOM) is also disabled while running, to prevent concurrent runs from the other entry point. Re-enabled after completion.

On completion (success or failure):
- `setInterval` is cleared.
- Button label restored to its normal state (`Run Pass 3` or `Re-run Pass 3` depending on which surface).
- `disabled` removed from both surfaces.

If `runPass3()` errors:
- Same restore behaviour (label + enabled state).
- The existing failure banner from Section 7 main handles the user-facing error notification — no toast needed.

### Addendum acceptance criteria

- Clicking the empty-state Run Pass 3 button → button immediately shows `⏳ running… 0s` and increments. Action-bar button (if rendered) also disabled.
- Clicking the action-bar Re-run Pass 3 button → same behaviour.
- On completion, both buttons return to their normal labels and enabled state in a single render pass.
- No timer continues running after success or failure.
- No double-trigger possible while a run is in progress (click is a no-op on disabled button).
- No console errors.

### Addendum deliverable
- Code change wired into the existing `runPass3()` handler.
- 1 after-screenshot: button mid-run showing `⏳ running… Ns` label. Save to `act_dashboard/Screenshots/`.

Ship as a follow-up commit on top of `2142038`.

## Section 8 — TBD (general visual polish)
_Catch-all for items spotted as we work through the rest._

---

## Coordination notes
- Build sequence: Section 1 first (smallest, fully specified). Then sections 2-7 as each is locked in the PM session.
- Each section is independently mergeable.
- Sections 2-3 require additional screenshots — flag if Build 2 starts those before screenshots land.
- Pre-build verification: Build 2 should open both reference templates and confirm the actual file paths/lines listed above are current. If anything has moved since this brief, grep for `pill-group`/`pill-btn`/`st-filter-bar` to relocate.
- After Section 1 ships, capture before/after screenshots in `act_dashboard/Screenshots/` for the PM to verify visually.
