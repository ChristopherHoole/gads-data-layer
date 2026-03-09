# CHAT 79 Summary — Google Ads-Style Date Picker

**Date:** 2026-03-09
**Status:** Complete

---

## What was built

Replaced the Flatpickr-based date filter with a Google Ads-style dropdown date picker. The new component has a compact trigger button that opens a panel with a preset list on the left and a calendar on the right.

---

## Files changed

### `act_dashboard/templates/components/date_filter.html` — REPLACED
- Removed Flatpickr CSS/JS dependency entirely
- New HTML: trigger button + quick preset buttons + dropdown panel
- Panel: 10-item preset list (left) + date inputs + calendar + Cancel/Apply footer
- All JavaScript is inline vanilla JS (IIFE, no globals except the IIFE itself)
- Backend wiring is identical: POSTs JSON to `/set-date-range` with `range_type`, `date_from`, `date_to`

### `act_dashboard/static/css/custom.css` — APPENDED
- Added `/* ── Date Picker (Chat 79) ── */` block at end of file
- All classes use `dp-` or `cal-` prefix to avoid conflicts
- No existing CSS was removed or modified

---

## Design decisions

### Preset → backend mapping
| Preset | range_type | Notes |
|--------|-----------|-------|
| Last 7 days | `'7'` | Stored in session as days=7 |
| Last 30 days | `'30'` | Stored in session as days=30 |
| Last 90 days | `'90'` | Stored in session as days=90 |
| Today, Yesterday, 14d, This month, Last month, All time | `'custom'` | Calculated in JS, sent as explicit dates |
| Custom range | `'custom'` | User picks dates, Apply required |

### Trigger label after reload
- 7d/30d/90d presets: "Last 7 days" / "Last 30 days" / "Last 90 days" (detected from active_days)
- Custom/extended presets: formatted date range e.g. "Mar 9 – Mar 9, 2026"
- This is a backend limitation — the session only stores days or explicit dates, not preset names

### Calendar layout
- Monday-first grid (M T W T F S S)
- Range: `range-start` / `in-range` / `range-end` classes with blue pill/band styling
- Single-day selection: `selected` class (full circle)
- Today: bold, blue text (combines cleanly with range classes)

---

## Behaviour notes

- **Quick buttons** (7d/30d/90d): immediate submit, no Apply needed
- **Preset list** (all except Custom range): immediate submit
- **Custom range** preset: clears selection, keeps panel open for manual date pick
- **Calendar clicks**: first click = start, second click = end; clicking end before start swaps them
- **Date inputs**: editable in DD/MM/YYYY format; valid entry updates calendar highlight
- **Cancel**: reverts to last applied state, closes panel
- **Apply**: submits current selFrom/selTo as custom range
- **Outside click**: closes panel

---

## What was NOT changed

- `/set-date-range` route — unchanged
- `get_date_range_from_session()` — unchanged
- Any other route files — unchanged
- Any other template files — unchanged
- Bootstrap Icons (already loaded globally) — no new CDN links needed
