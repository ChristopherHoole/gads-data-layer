# Chat 28 — Handoff Document
## M7: Recommendations Action Buttons + 4-Tab UI

**Date:** 2026-02-22
**Status:** COMPLETE ✅ — Approved by Master Chat
**Next step:** Git commit

---

## What the Next Developer Needs to Know

### What Chat 28 delivered
The recommendations system now has a fully functional UI. Users can:
- Accept, decline, or modify pending recommendations — changes are persisted to the database
- View all 4 recommendation lifecycle stages in dedicated tabs: Pending / Monitoring / Successful / Declined
- See live counts across all stages in both the summary strip and tab badges

This UI is live on two pages: `/recommendations` (dedicated page) and `/campaigns` (inner tab within the Campaigns page).

---

## Current State of the Recommendations System

### Statuses and their meanings
| Status | Description |
|---|---|
| `pending` | Generated, awaiting user action |
| `monitoring` | Accepted, within monitoring window (monitoring_days > 0) |
| `successful` | Completed — either accepted with monitoring_days=0, or monitoring period ended successfully |
| `declined` | Rejected by user |
| `reverted` | Monitoring period ended with ROAS degradation — auto-rollback (not yet implemented, field exists in schema) |

### Current monitoring_days setting
All 13 rules in `rules_config.json` have `monitoring_days: 0`. This means all accepted recommendations go straight to `successful`. The field is wired and ready — set any rule to `monitoring_days: 7` (or any value) to enable the monitoring flow for that rule.

### Changes audit table
A new `changes` table was created in `warehouse.duckdb` by the `_ensure_changes_table()` helper. It records every user action (accept/decline/modify) with before/after values, timestamps, and `executed_by` labels. This is separate from the existing `analytics.change_log` table used by the Changes page.

---

## File Locations

| File | Path |
|---|---|
| Recommendations routes | `act_dashboard/routes/recommendations.py` |
| Recommendations template | `act_dashboard/templates/recommendations.html` |
| Campaigns template | `act_dashboard/templates/campaigns.html` |
| Rules config | `act_autopilot/rules_config.json` |

---

## Route Reference

| Method | Route | Purpose |
|---|---|---|
| GET | `/recommendations` | Renders 4-tab page — passes all 4 status groups server-side |
| POST | `/recommendations/<rec_id>/accept` | Accept pending rec → monitoring or successful |
| POST | `/recommendations/<rec_id>/decline` | Decline pending rec → declined |
| POST | `/recommendations/<rec_id>/modify` | Update proposed_value + accept |
| POST | `/recommendations/run` | Trigger recommendations engine |
| GET | `/recommendations/cards` | JSON — all 4 status groups (used by campaigns.html) |
| GET | `/recommendations/data` | JSON — summary counts (used by sidebar badge) |

---

## Key Implementation Details

### Tab switching — `/recommendations`
Pure JS. All 4 tab content divs are rendered server-side by Jinja. `switchTab(name)` shows the target div and hides the others. No page reloads. Pending is active by default.

### Tab switching — `/campaigns`
Inner tab switcher using `camSwitchTab(name)`. Data is fetched via `GET /recommendations/cards` on outer tab click. Cards are rendered client-side by JS template functions: `renderPendingCards()`, `renderMonitoringCards()`, `renderSuccessfulCards()`, `renderDeclinedCards()`.

### Date handling in templates
Datetime fields from DuckDB can be either Python `datetime` objects or ISO strings depending on context. Templates use `| string | truncate(10, True, '')` to safely extract the date portion (YYYY-MM-DD) in all cases.

### NULL `accepted_at` on old declined rows
Synthetic data rows that predated Chat 28 have NULL `accepted_at`. These show "Declined —" in the footer. All new declines correctly populate this field via the Part 1 POST route. Not a bug.

---

## What Comes Next (for Master Chat to assign)

The recommendations UI is now fully functional. Logical next steps depending on roadmap priority:

1. **Radar / monitoring resolution** — Build the background process that checks monitoring-period recommendations and transitions them to `successful` or `reverted` based on ROAS performance
2. **Enable monitoring_days per rule** — Set non-zero `monitoring_days` on specific rules to test the full monitoring flow end-to-end
3. **Changes page integration** — Consider surfacing the new `changes` table (user actions) alongside the existing `analytics.change_log` (system changes) on the Changes page
4. **Live execution** — Connect the accept/modify routes to the Google Ads API execution engine for real campaign changes

---

## Testing Checklist (for regression testing)

- [ ] `/recommendations` loads without errors — all 4 tabs render
- [ ] Summary strip counts match tab badge counts
- [ ] Pending tab: action buttons functional (accept/decline/modify)
- [ ] Pending tab: card removes from DOM on action, badge decrements
- [ ] Monitoring tab: read-only, no action buttons visible
- [ ] Successful tab: read-only, green cards, correct dates
- [ ] Declined tab: read-only, faded cards, generated/declined dates
- [ ] `/campaigns` Recommendations tab: 4 inner tabs render
- [ ] `/campaigns` inner tabs: all 4 status groups load from `/recommendations/cards`
- [ ] No 500 errors on any route
- [ ] No JS console errors on either page
