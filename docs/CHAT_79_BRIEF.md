# CHAT 79: Google Ads-Style Date Picker

**Date:** 2026-03-09
**Estimated Time:** 3–4 hours
**Priority:** MEDIUM
**Dependencies:** None

---

## CONTEXT

The current date picker (`components/date_filter.html`) uses a Flatpickr text input, an Apply button, and three separate 7d/30d/90d quick buttons in a horizontal row. The design is functional but doesn't match the quality of the rest of the dashboard. The replacement is a Google Ads-style date picker: a compact trigger button that opens a dropdown panel with presets on the left and a calendar on the right.

---

## OBJECTIVE

Replace the existing date filter component with a Google Ads-style dropdown date picker — trigger button above quick presets, panel with preset list + calendar, Cancel/Apply footer.

---

## DELIVERABLES

1. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\components\date_filter.html` — REPLACE ENTIRELY
   - New Google Ads-style date picker (no Flatpickr dependency)

2. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\static\css\custom.css` — MODIFY
   - Add all date picker CSS under a `/* ── Date Picker (Chat 79) ── */` comment block
   - Do not remove any existing CSS

3. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_79_HANDOFF.md` — CREATE
4. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_79_SUMMARY.md` — CREATE

---

## BUILD PLAN

### Step 1 — Read current implementation
Read these files before writing a single line:
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\components\date_filter.html` — current component (understand existing session vars, route, form action)
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\dashboard.py` — understand how `date_from`, `date_to`, `date_preset` are read from session/POST
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\static\css\custom.css` — append CSS here, do not create a new file

### Step 2 — Preserve all existing backend wiring
The new component must POST the same fields the backend already expects:
- `date_from` — YYYY-MM-DD format
- `date_to` — YYYY-MM-DD format  
- `date_preset` — string: `'7d'`, `'30d'`, `'90d'`, `'today'`, `'yesterday'`, `'14d'`, `'30d'`, `'this_month'`, `'last_month'`, `'all_time'`, `'custom'`
- Form action and method must match what currently exists

### Step 3 — Build the HTML structure

**Trigger bar layout (stacked, right-aligned):**
```
[ 📅 Mar 3 – Mar 9, 2026  ▾ ]   ← trigger button (top)
[ 7d ]  [ 30d ]  [ 90d ]         ← quick preset buttons (below)
```

**Dropdown panel (opens below trigger, right-aligned):**
```
┌─────────────────┬──────────────────────────────┐
│  Today          │  [03/03/2026] – [03/09/2026]  │
│  Yesterday      │                               │
│  Last 7 days ✓  │  < March 2026 >              │
│  Last 14 days   │  M  T  W  T  F  S  S         │
│  Last 30 days   │  …calendar grid…              │
│  This month     │                               │
│  Last month     │            [Cancel] [Apply]   │
│  Last 90 days   │                               │
│  All time       │                               │
│  Custom range   │                               │
└─────────────────┴──────────────────────────────┘
```

### Step 4 — CSS requirements (append to custom.css)

All classes use `dp-` prefix to avoid conflicts.

| Class | Purpose |
|-------|---------|
| `.dp-wrapper` | Relative positioned container |
| `.dp-trigger` | Trigger button — white bg, border #dadce0, border-radius 4px |
| `.dp-quick-btns` | Row of 7d/30d/90d buttons below trigger |
| `.dp-quick-btn` | Individual quick button |
| `.dp-quick-btn.active` | Active state: bg #1a73e8, white text |
| `.dp-panel` | Dropdown — absolute, right:0, min-width 560px, shadow |
| `.dp-presets` | Left column, 180px, border-right #e8eaed |
| `.dp-preset` | Each preset row, hover bg #f1f3f4 |
| `.dp-preset.active` | Active preset: bg #e8f0fe, text #1a73e8, font-weight 500 |
| `.dp-right` | Right column, padding 16px |
| `.dp-date-inputs` | Row with two date text inputs and a dash separator |
| `.dp-date-input` | Individual date input, focus border #1a73e8 |
| `.cal-nav` | Month navigation row (prev/next arrows + label) |
| `.cal-grid` | 7-column grid, fixed 32px columns, no gap |
| `.cal-dow` | Day-of-week header (M T W T F S S) |
| `.cal-day` | Individual day cell, 32px × 32px, border-radius 50% |
| `.cal-day.today` | Bold, text #1a73e8 |
| `.cal-day.selected` | bg #1a73e8, white text |
| `.cal-day.range-start` | bg #1a73e8, white, border-radius 50% 0 0 50% |
| `.cal-day.range-end` | bg #1a73e8, white, border-radius 0 50% 50% 0 |
| `.cal-day.in-range` | bg #e8f0fe, text #1a73e8, border-radius 0 |
| `.cal-day.other-month` | text #bdc1c6 |
| `.dp-footer` | Right-aligned row, border-top #e8eaed, margin-top 14px |
| `.dp-btn-cancel` | Ghost button |
| `.dp-btn-apply` | Solid blue #1a73e8 button |

### Step 5 — JavaScript behaviour (inline in date_filter.html)

**Open/close:**
- Clicking trigger toggles panel open/closed
- Clicking outside panel closes it
- Chevron rotates when open

**Quick preset buttons (7d / 30d / 90d):**
- Clicking immediately submits the form with the corresponding preset
- No Apply needed
- Sets `.active` class on clicked button

**Preset list (left column):**
- Clicking a preset populates both date inputs and highlights the calendar range
- All presets except "Custom range" submit immediately (no Apply needed)
- "Custom range" leaves panel open for manual date selection

**Calendar:**
- Renders current month on open
- Prev/next arrows navigate months
- First click sets start date, second click sets end date
- Range highlighted between start and end
- After selecting end date, populate the date inputs but do NOT auto-submit — wait for Apply

**Apply button:**
- Submits the form with current date_from, date_to, date_preset=custom

**Cancel button:**
- Closes panel, reverts inputs to last applied values

**Date input fields:**
- Editable — typing a valid date updates calendar highlight
- Format: DD/MM/YYYY for display, converted to YYYY-MM-DD on submit

**Trigger label:**
- Updates to reflect selected range after Apply
- Format: "Mar 3 – Mar 9, 2026" for custom/preset ranges
- Format: "Last 7 days", "Last 30 days" etc for named presets

### Step 6 — Preset date calculations (JavaScript)

All calculated relative to today's date in the browser:

| Preset | date_from | date_to |
|--------|-----------|---------|
| Today | today | today |
| Yesterday | today-1 | today-1 |
| Last 7 days | today-6 | today |
| Last 14 days | today-13 | today |
| Last 30 days | today-29 | today |
| This month | first day of current month | today |
| Last month | first day of last month | last day of last month |
| Last 90 days | today-89 | today |
| All time | 2000-01-01 | today |

### Step 7 — Test

---

## REQUIREMENTS

### Must preserve
- All existing Flask session variables (`date_from`, `date_to`, `date_preset`) — backend does not change
- Form POST action — read from current `date_filter.html` and keep identical
- 7d/30d/90d buttons must still work exactly as before (immediate apply)
- Date picker must work on ALL pages that include it — not just dashboard

### Must not do
- Do not add Flatpickr or any new JS library — vanilla JS only
- Do not modify any route files
- Do not create a new CSS file — append to `custom.css` only
- Do not break any existing CSS

### Browser
- Test in Opera only

---

## SUCCESS CRITERIA

- [ ] Trigger button shows calendar icon + current date range label + chevron
- [ ] Quick 7d/30d/90d buttons sit below trigger, right-aligned
- [ ] Clicking trigger opens dropdown panel
- [ ] Clicking outside panel closes it
- [ ] Preset list on left — clicking any preset (except Custom) applies immediately
- [ ] Calendar renders correct month with range highlighted
- [ ] Prev/next month navigation works
- [ ] Start + end date selection works via calendar clicks
- [ ] Date inputs are editable and sync with calendar
- [ ] Apply submits with correct date_from / date_to in YYYY-MM-DD format
- [ ] Cancel closes panel without applying
- [ ] Trigger label updates after Apply to show new range
- [ ] Works on Campaigns, Keywords, Ad Groups, Ads, Shopping pages (not just dashboard)
- [ ] No console errors
- [ ] Flask starts cleanly

---

## REFERENCE FILES

- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\components\date_filter.html` — READ FIRST (current implementation)
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\dashboard.py` — understand date session handling
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\static\css\custom.css` — append CSS here
- `C:\Users\User\Desktop\gads-data-layer\docs\DATE_PICKER_WIREFRAME.html` — approved visual spec (save this file here before sending brief)

---

## TESTING

1. Start Flask fresh
2. Open Dashboard in Opera — confirm trigger + quick buttons render correctly
3. Click trigger — confirm panel opens, calendar shows correct month
4. Click "Last 30 days" preset — confirm panel closes, page reloads with 30-day data
5. Click trigger → click a start date → click an end date → click Apply — confirm page reloads with correct custom range
6. Click Cancel — confirm panel closes with no change
7. Click 7d quick button — confirm immediate apply
8. Navigate to Campaigns page — confirm date picker renders and works identically
9. Report Flask log output and any console errors

---

**Version:** 1.0 | **Date:** 2026-03-09
