# CHAT 97: Fix Recommendations Table Display — Rule Name Wrapping + Action Layout

**Date:** 2026-03-17
**Priority:** HIGH
**Estimated Time:** 20 minutes
**Dependencies:** None

---

## CONTEXT

The recommendations table has two display issues identified during testing.

---

## OBJECTIVE

Fix two display issues in the recommendations table on both the Campaigns page and the full Recommendations page.

---

## ISSUE 1: Rule Name Column Not Wrapping

The Rule name column is truncating long rule names like "Decrease Max CPC Cap – High CPC Low CTR". Text needs to wrap within the column.

**Fix:** In `act_dashboard/static/css/recommendations.css`, find the rule name column CSS and ensure it has `white-space: normal; word-break: break-word;`. Read the file first to find the exact selector being used for the rule name column width.

---

## ISSUE 2: Human Confirm Pill + Action Text on Same Line

For High risk recommendations, the "Human confirm" badge pill and the action text (e.g. "Pause campaign") are on the same line. They need to be stacked vertically — pill on top, action text below.

**Fix:** In the `actionCell()` JavaScript function in both:
- `act_dashboard/templates/campaigns.html`
- `act_dashboard/templates/recommendations.html`

Find where the human confirm badge is rendered alongside the action text and add a `<br>` or wrap in a `<div>` so they stack vertically.

Read both files before editing to find the exact `actionCell` function.

---

## DELIVERABLES

1. `act_dashboard/static/css/recommendations.css` — MODIFY (rule name column wrapping)
2. `act_dashboard/templates/campaigns.html` — MODIFY (actionCell stacking)
3. `act_dashboard/templates/recommendations.html` — MODIFY (actionCell stacking)

---

## REQUIREMENTS

- Read each file before editing
- Do not touch any Python files
- Do not touch any other CSS or HTML files
- Verify changes by reading back the modified sections

---

## SUCCESS CRITERIA

- [ ] Rule name column wraps long text instead of truncating
- [ ] Human confirm badge appears on its own line above the action text
- [ ] Flask starts cleanly
- [ ] No other layout is broken
