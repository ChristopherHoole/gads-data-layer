# CHAT 28 — SCOPE ADDITION: 4-Tab Recommendations UI

**Date:** 2026-02-22
**Status:** Approved by Master Chat — implement before writing handoff docs
**Wireframe:** `C:\Users\User\Desktop\gads-data-layer\docs\M7_4TAB_WIREFRAME.html`

---

## Context

During testing of the Accept/Decline/Modify buttons (Chat 28 Part 1), it became clear that once all pending recommendations were actioned, there was no way to see them again. Cards simply disappeared. This is a UX problem — the system feels like a black box.

The fix is to add 4 tabs to the Recommendations UI so every stage of a recommendation lifecycle is visible.

This scope addition must be completed in both `recommendations.html` and `campaigns.html` **before** the handoff docs are written.

---

## Objective

Replace the current single-view card list with a 4-tab UI:

| Tab | Status filter | Action buttons |
|---|---|---|
| **Pending** | `status = 'pending'` | ✅ Modify / Decline / Accept (unchanged) |
| **Monitoring** | `status = 'monitoring'` | 🔒 None — read only |
| **Successful** | `status = 'successful'` | 🔒 None — read only |
| **Declined** | `status = 'declined'` | 🔒 None — read only |

**Pending is the default active tab on page load.**

---

## Wireframe

Open `C:\Users\User\Desktop\gads-data-layer\docs\M7_4TAB_WIREFRAME.html` and follow it exactly. It is built using the actual M6 card CSS — do not deviate from it. It covers:

1. Tab bar with badge counts and colours
2. Pending tab — existing card design, unchanged
3. Monitoring tab — monitoring-block replaces trigger-block, no action buttons
4. Successful tab — outcome-block (green) replaces trigger-block, no action buttons
5. Declined tab — outcome-block (grey), card-declined class (opacity 0.55), no action buttons
6. Empty states — per-tab contextual message + SVG icon
7. Implementation reference table — CSS classes, block types, button rules per tab

---

## Card Design — Critical Notes

**Do not invent new CSS.** All required classes already exist in the M6 stylesheet:

| Element | Class |
|---|---|
| Card grid | `rec-grid-2` — 2 columns, NOT full width |
| Pending top bar | `rt-budget` / `rt-bid` / `rt-status` (per rule type) |
| Monitoring top bar | `rt-monitoring` |
| Successful top bar | `rt-successful` |
| Declined top bar | `rt-declined` |
| Monitoring card border | `card-monitoring` |
| Successful card border | `card-success` |
| Declined opacity | `card-declined` (already sets opacity:0.55) |
| Monitoring block | `monitoring-block` (purple, progress bar, outcome pills) |
| Outcome block (success) | `outcome-block ob-success` |
| Outcome block (declined) | `outcome-block ob-declined` |

**Card structure per tab:**
- **Pending:** `rec-top` → `rec-card-header` → `change-block` → `trigger-block` → `rec-footer` (meta row + action buttons row)
- **Monitoring:** `rec-top` → `rec-card-header` → `change-block` → `monitoring-block` → `rec-footer` (meta row only, no action buttons row)
- **Successful:** `rec-top` → `rec-card-header` → `change-block` → `outcome-block ob-success` → `rec-footer` (meta row only)
- **Declined:** `rec-top` → `rec-card-header` → `change-block` → `outcome-block ob-declined` → `rec-footer` (meta row only)

---

## Tab Bar

- 4 tabs: Pending | Monitoring | Successful | Declined
- Use existing `.page-tab` / `.page-tab.active` classes
- Badge colours: default (Pending) · amber `tab-badge-warning` (Monitoring) · green (Successful) · grey (Declined)
- Pending is default active on page load
- Tab switching is **pure JS** — no page reload

---

## Empty States

Each tab shows a contextual empty state when no cards exist:

| Tab | Icon colour | Message |
|---|---|---|
| Pending | Blue | "No pending recommendations." |
| Monitoring | Purple (#6d28d9) | "No recommendations currently being monitored." |
| Successful | Green (#15803d) | "No successful recommendations yet." |
| Declined | Grey (#6b7280) | "No declined recommendations." |

---

## Backend Check — Do This First

Before editing any template, check `recommendations.py`:

**Open `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\recommendations.py`** and find the `/recommendations/cards` endpoint.

- If it filters to `status = 'pending'` only → update it to return all statuses
- If it already returns all statuses → no backend change needed

Request the current file from Christopher before checking (Rule 2).

---

## Files to Edit

| File | Full Path |
|---|---|
| recommendations.py | `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\recommendations.py` |
| recommendations.html | `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\recommendations.html` |
| campaigns.html | `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\campaigns.html` |

⚠️ Request current versions before editing all files (Rule 2).

---

## Implementation Order

1. Check `/recommendations/cards` in `recommendations.py` — fix if filtering to pending only
2. Edit `recommendations.html` — tab bar, 4 tab sections with correct card structures, empty states, JS tab switching + badge counts
3. Edit `campaigns.html` — same
4. Test all 4 tabs on both pages

---

## Testing Checklist

- [ ] Pending tab is default active, shows pending cards in `rec-grid-2` (2 columns)
- [ ] Monitoring tab shows monitoring cards with `monitoring-block` + progress bar, no action buttons
- [ ] Successful tab shows cards with green `outcome-block`, no action buttons
- [ ] Declined tab shows cards with grey `outcome-block`, `card-declined` opacity, no action buttons
- [ ] All badge counts correct on page load
- [ ] After actioning a pending card: badge decrements correctly
- [ ] Empty state shows correctly when a tab has no cards
- [ ] Cards are 2 columns (`rec-grid-2`) on all tabs — not full width
- [ ] Tab switching has no page reload
- [ ] Works on both `/recommendations` page AND Campaigns → Recommendations tab
- [ ] No HTTP 500s, no JS console errors

---

## Estimated Additional Time

~60 minutes on top of Part 1 work.

---

## Critical Rules

- Use existing M6 CSS classes only — do not create new ones
- `rec-grid-2` (2 columns) on all tabs — never full width
- No action buttons on Monitoring / Successful / Declined tabs
- No new backend routes unless `/recommendations/cards` needs a status filter fix
- Complete files only — never snippets
- Full Windows paths on all deliverables
- Request current file versions before editing (Rule 2)
