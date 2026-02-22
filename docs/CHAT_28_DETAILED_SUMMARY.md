# Chat 28 — Detailed Summary
## M7: Recommendations Action Buttons + 4-Tab UI

**Date:** 2026-02-22
**Status:** COMPLETE ✅ — Approved by Master Chat
**Scope:** M7 scope addition — wired action buttons + full 4-tab recommendations UI across both `/recommendations` and `/campaigns`

---

## Overview

Chat 28 delivered two distinct pieces of work in a single session:

**Part 1 — Action Buttons (Accept / Decline / Modify)**
Wired the previously disabled action buttons on recommendation cards to live POST routes. Changes are written to both the `recommendations` table (status transition) and a new `changes` audit table in `warehouse.duckdb`.

**Part 2 — 4-Tab Recommendations UI**
Replaced the previous 3-tab server-side routed layout (Pending / Monitoring / History) with a new 4-tab pure-JS interface (Pending / Monitoring / Successful / Declined) on both `/recommendations` and `/campaigns`.

---

## Files Changed

### 1. `act_autopilot/rules_config.json`
- Added `"monitoring_days": 0` to all 13 rules
- All rules currently skip monitoring (go straight to `successful` on accept)
- Field is ready for non-zero values when monitoring is enabled per rule in future

### 2. `act_dashboard/routes/recommendations.py`

**New helpers added (Part 1):**
- `_ensure_changes_table(conn)` — Creates `changes` table + sequence in `warehouse.duckdb` if not present
- `_load_monitoring_days(rule_id)` — Reads `rules_config.json`, returns `monitoring_days` for a given rule
- `_load_rec_by_id(conn, rec_id, customer_id)` — Loads single recommendation row as dict
- `_write_changes_row(conn, rec, executed_by, ...)` — Writes audit row to `changes` table

**New POST routes added (Part 1):**
- `POST /recommendations/<rec_id>/accept` — Transitions `pending` → `monitoring` or `successful` depending on `monitoring_days`
- `POST /recommendations/<rec_id>/decline` — Transitions `pending` → `declined`, sets `accepted_at`
- `POST /recommendations/<rec_id>/modify` — Updates `proposed_value`, then accepts (same status logic as accept)

**Updated (Part 2):**
- `_get_summary()` — Now returns `pending`, `monitoring`, `successful`, `declined` counts. Removed `success_rate` and `last_run`.
- `recommendations()` route — Removed `history_recs`, `history_success_rate`, `history_successful_count`, `history_accepted_count`, `active_tab`. Added `successful_recs` and `declined_recs` queries. Now passes all 4 groups server-side.
- `recommendations_cards()` endpoint — Extended to return `successful` and `declined` arrays in addition to existing `pending` and `monitoring`.

### 3. `act_dashboard/templates/recommendations.html`

**Part 1 changes:**
- Removed `disabled` attribute and `opacity: 0.5` / `cursor: not-allowed` from all 3 action buttons
- Added `onclick` handlers: `acceptRec()`, `declineRec()`, `openModifyModal()`
- Added `data-rec-id`, `data-rec-rule`, `data-rec-campaign`, `data-rec-value` to Modify button
- Added `id="card-{{ rec.rec_id }}"` to each card for DOM targeting
- Added IDs for badge/count updates: `summary-pending`, `tab-badge-pending`, `pending-subhead`
- Added Bootstrap modal `#modifyModal`
- Added toast container `#act-toast-wrap`
- Added JS: `showToast()`, `removeCard()`, `updateBadges()`, `acceptRec()`, `declineRec()`, `openModifyModal()`, `submitModify()`

**Part 2 changes (full rewrite):**
- Summary strip: 4 cards — Pending (blue) / Monitoring (purple) / Successful (green) / Declined (grey). Replaced previous success_rate % and last_run cards.
- Tab bar: 4 pure-JS tabs replacing 3 server-side `<a href>` tabs. Colour-coded badges: default / amber / green / grey.
- History tab: **removed entirely**
- Tab switching: `switchTab(name)` function — hides all 4 divs, shows target, toggles `active` class. Pending is default on page load.
- **Monitoring tab:** Read-only. `card-monitoring` class (blue border), `rt-monitoring` top bar, monitoring-block with purple progress bar, day counter, outcome pills (ROAS holds / ROAS drops), `🔒 Read only` footer label. No action buttons.
- **Successful tab:** Read-only. `card-success` class (green border), `rt-successful` top bar, `ob-success` outcome block (green), "Change completed successfully", "Accepted [date] · Completed [date]" (falls back to "Accepted [date]" only if `resolved_at` is NULL). `✅ Completed` footer label. No action buttons.
- **Declined tab:** Read-only. `card-declined` class (opacity 0.55), `rt-declined` top bar (grey), `cb-grey`/`ciw-grey` change block, `ob-declined` outcome block, "Declined by user", "Generated [date] · Declined [date]" (uses `accepted_at` for declined date). `✖ Declined` footer label. No action buttons.
- **New CSS classes added:** `rt-successful`, `rt-declined`, `card-success`, `card-declined`, `rrt-monitoring`, `rrt-declined`, `sp-successful`, `outcome-block`, `ob-success`, `ob-declined`, `outcome-title`, `ot-success`, `ot-declined`, `outcome-sub`, `cb-grey`, `ciw-grey`, `tab-badge-orange`, `tab-badge-green`, `tab-badge-grey`, `readonly-label`

### 4. `act_dashboard/templates/campaigns.html`

**Part 1 changes:**
- Removed `disabled` + `opacity: 0.5` from all 3 action buttons in `renderPendingCards()`
- Added `onclick` handlers, `data-*` attributes, `id="cam-card-${r.rec_id}"` to pending card template strings
- Added `camShowToast()`, `camRemoveCard()`, `camAcceptRec()`, `camDeclineRec()`, `camOpenModifyModal()`, `camSubmitModify()` functions
- Added Bootstrap modal `#camModifyModal`
- Added toast container `#cam-toast-wrap`

**Part 2 changes:**
- Summary strip: Updated to 4 counts (Pending / Monitoring / Successful / Declined). Removed success-rate and last-run cards. New IDs: `cam-count-pending`, `cam-count-monitoring`, `cam-count-successful`, `cam-count-declined`.
- Inner 4-tab bar added using inline-styled button elements (not Bootstrap nav-tabs, to avoid conflict with outer campaign tabs). IDs: `cam-btn-pending/monitoring/successful/declined`.
- Tab content divs: `cam-tab-pending`, `cam-tab-monitoring`, `cam-tab-successful`, `cam-tab-declined`
- `camSwitchTab(name)` function: shows/hides inner tab divs, updates button colour + border
- Tab activated on outer Recommendations tab click via event listener on `#recommendations-tab-btn`
- Badge IDs: `cam-badge-pending`, `cam-badge-monitoring`, `cam-badge-successful`, `cam-badge-declined`
- `loadRecCards()` updated to call all 4 render functions and populate all 8 count/badge elements
- `renderSuccessfulCards(recs)` added: green border, green top bar, outcome block with accepted/completed dates, `✅ Completed` label, no action buttons
- `renderDeclinedCards(recs)` added: grey/faded cards, grey top bar, outcome block with generated/declined dates, `✖ Declined` label, no action buttons

---

## Database

### `recommendations` table (existing, `warehouse.duckdb`)
Fields used by Chat 28 routes:
- `rec_id`, `rule_id`, `rule_type`, `campaign_id`, `campaign_name`, `customer_id`
- `status` — transitions: `pending` → `monitoring` / `successful` / `declined`
- `accepted_at` — set on accept, modify, and decline
- `monitoring_ends_at` — set on accept when `monitoring_days > 0`
- `resolved_at` — set on accept/modify when `monitoring_days = 0` (direct to successful)
- `updated_at` — always updated on any status change

### `changes` table (new, `warehouse.duckdb`)
Created by `_ensure_changes_table()` on first action. Schema:
```
change_id       INTEGER (sequence)
customer_id     VARCHAR
campaign_id     VARCHAR
campaign_name   VARCHAR
rule_id         VARCHAR
action_type     VARCHAR  (budget_change / bid_change / status_change)
old_value       DOUBLE
new_value       DOUBLE
justification   VARCHAR
executed_by     VARCHAR  (user_accept / user_decline / user_modify)
executed_at     TIMESTAMP
dry_run         BOOLEAN  (always FALSE for user actions)
status          VARCHAR  (always 'completed' for user actions)
```

---

## Architecture Decisions

| Decision | Choice | Reason |
|---|---|---|
| Tab switching method | Pure JS show/hide | Server-side routing would require full page reloads; data volume is small |
| Data passing method | Server-side Jinja (recommendations.html) | Simpler, no extra fetch needed, option (b) approved by Master Chat |
| Data passing method | JS fetch from `/recommendations/cards` (campaigns.html) | Pre-existing pattern on that page, maintained for consistency |
| History tab fate | Removed entirely | Replaced by Successful + Declined card tabs |
| Summary strip | Kept and updated | Provides at-a-glance counts before clicking into tabs |
| Declined date field | `accepted_at` | Set during decline route; no separate `declined_at` field needed |
| Successful "Completed" date | `resolved_at` with NULL fallback | Confirmed in schema; older rows may have NULL, falls back gracefully |

---

## Test Results

| Test | Page | Result |
|---|---|---|
| 4-tab bar renders, Pending default active | /recommendations | ✅ |
| Summary strip: 4 correct counts | /recommendations | ✅ 0/4/54/8 |
| Monitoring tab: cards, progress bars, read-only | /recommendations | ✅ |
| Successful tab: 54 cards, green border, dates | /recommendations | ✅ |
| Declined tab: 8 cards, faded, outcome block | /recommendations | ✅ |
| 4-tab inner switcher | /campaigns | ✅ |
| Summary strip: 4 correct counts | /campaigns | ✅ 0/4/54/8 |
| Monitoring tab: cards, progress bars, read-only | /campaigns | ✅ |
| Successful tab: cards rendering | /campaigns | ✅ |
| Declined tab: cards rendering, faded | /campaigns | ✅ |
| No 500s | Both | ✅ |
| No JS console errors | Both | ✅ |
| NULL `accepted_at` on old declined rows | Both | ✅ Expected — shows "Declined —" |

---

## Known Behaviour (Not a Bug)

Some declined cards show "Declined —" in the footer. This affects synthetic data rows that predate the Part 1 routes and therefore have NULL `accepted_at`. All new declines via the Part 1 routes correctly populate this field.

---

## What Was NOT Changed

- All existing Campaign, Ad Groups, Keywords, Ads, Shopping, Dashboard pages — untouched
- `act_autopilot/recommendations_engine.py` — untouched
- `changes.html` (change history page) — untouched
- The 3 POST action routes from Part 1 — untouched in Part 2
- `base_bootstrap.html` — untouched
