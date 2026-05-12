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

## Section 2 — TBD (table restyle)
_To be specified once Chris shares the Account page table screenshot for visual reference._

## Section 3 — TBD (top cards review)
_To be specified — decide keep / cut / merge for the 5 status cards (Pending / Approved to Block / Didn't Block / Pushed to Neg Lists / Expired)._

## Section 4 — TBD ("All" cascade reset)
_To be specified — when "All" clicked on a top filter row, downstream filter rows reset to All._

## Section 5 — TBD (button audit + remove redundant)
_To be specified — walk through every button on Search Terms pages, mark each as keep/cut/merge._

## Section 6 — TBD (rename Pass 1/2 and Pass 3)
_To be specified — agree commercial-sounding names. Affects tab labels, headings, telemetry, docs, prompt files._

## Section 7 — TBD (auto-trigger Pass 3 after PMax ingest)
_To be specified — hook Pass 3 AI run to fire ~1-2 min after daily PMax CSV ingest completes._

## Section 8 — TBD (general visual polish)
_Catch-all for items spotted as we work through the rest._

---

## Coordination notes
- Build sequence: Section 1 first (smallest, fully specified). Then sections 2-7 as each is locked in the PM session.
- Each section is independently mergeable.
- Sections 2-3 require additional screenshots — flag if Build 2 starts those before screenshots land.
- Pre-build verification: Build 2 should open both reference templates and confirm the actual file paths/lines listed above are current. If anything has moved since this brief, grep for `pill-group`/`pill-btn`/`st-filter-bar` to relocate.
- After Section 1 ships, capture before/after screenshots in `act_dashboard/Screenshots/` for the PM to verify visually.
