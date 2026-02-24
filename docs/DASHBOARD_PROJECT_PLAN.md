# DASHBOARD UI OVERHAUL - Complete Project Plan

**Project:** Chat 21 - Google Ads-Inspired Dashboard
**Timeline:** 20 hours / 3 days
**Framework:** Bootstrap 5
**Icons:** Bootstrap Icons
**Chat 21 Status:** ✅ COMPLETE - 8/8 (100%) 🏆
**Dashboard 3.0 Status:** ✅ COMPLETE — M1 ✅ M2 ✅ M3 ✅ M4 ✅ M5 ✅ M6 ✅ M7 ✅ M8 ✅ M9 Phase 1 ✅ M9 Phase 2 ✅ COMPLETE
**Started:** February 18, 2026
**Updated:** 2026-02-24
**Mode:** Dashboard 3.0 complete, ready for Phase 3 Future-Proofing
**Location:** `C:\Users\User\Desktop\gads-data-layer\docs\DASHBOARD_PROJECT_PLAN.md`

---

## 🎯 PROJECT GOALS

### **Primary Objective:**
Create a professional, Google Ads-inspired dashboard that feels familiar to millions of Google Ads users while maintaining ACT's unique AI-powered features.

### **Success Criteria:**
- ✅ All 8 main pages redesigned (including Ad Groups)
- ✅ Responsive (desktop + mobile)
- ✅ Professional appearance
- ✅ Fast loading (<2 seconds)
- ✅ Intuitive navigation
- ✅ AI insights integrated seamlessly
- ✅ Pagination on all tables (10, 25, 50, 100 rows)
- ✅ Search terms stay within Keywords page

---

## 📋 PAGES STATUS

| # | Page | Status |
|---|------|--------|
| 1 | Main Dashboard | ✅ Complete |
| 2 | Campaigns | ✅ Complete |
| 3 | Ad Groups | ✅ Complete |
| 4 | Keywords | ✅ Complete |
| 5 | Ads | ✅ Complete |
| 6 | Shopping | ✅ Complete |
| 7 | Recommendations | ✅ Complete (5-tab: Pending/Monitoring/Successful/Reverted/Declined) |
| 8 | Changes | ✅ Complete (2-tab: My Actions cards / System Changes table) |
| 9 | Settings | 📋 Minor polish pending |

---

## DASHBOARD 3.0 PLAN

**Decision:** 2026-02-19. Full modular overhaul of all 6 dashboard pages.
**Architecture:** Jinja2 Macros for reusable components.
**Workflow:** Build on Campaigns (pilot) → test → roll out to all pages → close chat → next module.

---

### PHASE 1 — UI Overhaul

#### Chat 22: M1 — Date Picker ✅ COMPLETE
**Date:** 2026-02-19 | **Commits:** a644fdd + 25c7af5
- Flatpickr + session persistence + 7d/30d/90d presets
- 19 files changed

#### Chat 23: M2 — Metrics Cards ✅ COMPLETE
**Date:** 2026-02-20
- Financial row (8) + collapsible Actions row (8) on all 6 pages
- Jinja2 macro system, sparklines, change %, session-persisted collapse
- 14 files modified

#### Chat 24: M3 — Chart Overhaul ✅ COMPLETE
**Date:** 2026-02-20
- Reusable performance_chart.html macro on all 6 pages
- Dual Y-axis, 4 toggleable slots, session-persisted
- 10 files modified

#### Chat 25: M4 — Table Overhaul ✅ COMPLETE
**Date:** 2026-02-21
- Full Google Ads column sets on all 5 pages
- Server-side sort, sticky first column, ALLOWED_*_SORT whitelists
- 16 files modified

---

### PHASE 2 — Rules + Actions

#### Chat 26: M5 — Rules Section Upgrade ✅ COMPLETE
**Date:** 2026-02-22 | **Commit:** 025986a
**Summary:** `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_26_DETAILED_SUMMARY.md`
**Handoff:** `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_26_HANDOFF.md`
**Wireframe:** `C:\Users\User\Desktop\gads-data-layer\docs\M5_WIREFRAME_v3.html`

- Card-based Rules tab (Campaigns pilot)
- 13 rules, full CRUD, slide-in drawer, campaign picker
- rules_config.json + rules_api.py
- Dual-layer: JSON (UI config) / Python (execution, untouched)

#### Chat 27: M6 — Recommendations Engine + UI ✅ COMPLETE
**Date:** 2026-02-22
**Summary:** `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_27_DETAILED_SUMMARY.md`
**Handoff:** `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_27_HANDOFF.md`
**Wireframe:** `C:\Users\User\Desktop\gads-data-layer\docs\M6_WIREFRAME_v5.html`

- recommendations table in warehouse.duckdb (19 cols) + 22 historical rows seeded
- recommendations_engine.py: rules_config.json → campaign_features_daily → pending recs
- /recommendations/cards JSON endpoint
- Global /recommendations page + Campaigns → Recommendations tab

#### Chat 28: M7 — Accept/Decline/Modify Wiring + 4-Tab UI ✅ COMPLETE
**Date:** 2026-02-22
**Summary:** `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_28_DETAILED_SUMMARY.md`
**Handoff:** `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_28_HANDOFF.md`
**Wireframe:** `C:\Users\User\Desktop\gads-data-layer\docs\M7_4TAB_WIREFRAME.html`

- Accept/Decline/Modify POST routes — live
- changes audit table in warehouse.duckdb
- 4-tab UI: Pending / Monitoring / Successful / Declined
- Card animations, badge decrements, toast confirmations
- Both /recommendations and /campaigns updated

#### Chat 29: M8 — Changes + Radar Monitoring ✅ COMPLETE
**Date:** 2026-02-23
**Summary:** `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_29_DETAILED_SUMMARY.md`
**Handoff:** `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_29_HANDOFF.md`
**Wireframe:** `C:\Users\User\Desktop\gads-data-layer\docs\M8_WIREFRAME.html`

**Delivered:**
- `act_autopilot/radar.py` — Radar background daemon thread (60s cycle)
  - Evaluates all `monitoring` status recommendations on expiry
  - KPI check: ROAS/CVR ≥15% drop → `reverted`; held → `successful`
  - Writes `radar_revert` or `radar_resolved` to changes table
  - DB-only in this chat — no live Google Ads API rollback yet
- `act_dashboard/routes/changes.py` — new blueprint, `/changes` route
- `changes.html` — full Bootstrap 5 rewrite
  - Summary strip: 4 stat cards (Total / Accepted / Modified / Declined)
  - My Actions tab: card grid (same M6/M7 format), filter bar
  - System Changes tab: table from ro.analytics.change_log (cards deferred to future chat)
- `monitoring_minutes` field added to all 13 rules in rules_config.json
- 5th Reverted tab added to both `/recommendations` and `/campaigns`
- Reverted card: red top bar, red outcome block, revert_reason shown
- `last_run` bug fixed in `_get_summary()`
- `/recommendations/cards` extended to return `reverted` array
- 8 files created/modified

**Known deferred items from Chat 29:**
- System Changes tab → card grid (currently table, future chat)
- Live Google Ads API rollback on revert

---

### PHASE 3 — Search Terms + Keywords (next)

#### Chat 30a: M9 Phase 1 — Search Terms Table + Negative Keyword Suggestions ✅ COMPLETE
**Date:** 2026-02-24
**Summary:** `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_30A_SUMMARY.md`
**Handoff:** `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_30A_HANDOFF.md`

- Search Terms tab on Keywords page (16-column data table)
- Advanced filtering (campaign, status, match type) + client-side search
- Server-side pagination (10/25/50/100)
- Negative keyword flagging logic (3 criteria)
- Row-level + bulk "Add as Negative" actions (UI only, execution in Phase 2)
- All 16 success criteria passing
- 431 lines modified in keywords.py, 216 lines added in keywords_new.html

#### Chat 30b: M9 Phase 2 — Live Execution + Keyword Expansion ✅ COMPLETE
**Date:** 2026-02-24
**Summary:** `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_30B_SUMMARY.md`
**Handoff:** `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_30B_HANDOFF.md`
**Time:** 4 hours actual vs 7-9 hours estimated (53% efficiency)

- Live Google Ads API execution for negative keyword blocking
- Campaign-level + ad-group-level support
- Keyword expansion opportunities flagging (CVR ≥5%, ROAS ≥4.0x, Conv. ≥10)
- "Add as Keyword" functionality with match type + bid suggestions
- Dry-run mode for safe testing
- Changes table audit logging
- Bulk selection support
- All 16 success criteria passing (dry-run validated)
- 84 lines added in google_ads_api.py
- 456 lines added in keywords.py
- ~400 lines modified in keywords_new.html

**Key deliverables:**
- `add_adgroup_negative_keyword()` function
- `check_keyword_exists()` helper (duplicate prevention)
- `flag_expansion_opportunities()` helper (4-criteria flagging)
- `/keywords/add-negative` POST route
- `/keywords/add-keyword` POST route
- Negative keyword modal + expansion modal
- JavaScript execution handlers

---

### Dashboard 3.0 Wireframe Reference
- Wireframe provided by Christopher on 2026-02-19
- Page structure (top to bottom):
  1. Page title + tabs — top left
  2. Date picker + 7d/30d/90d — top right ← M1
  3. Financial Metrics row (always visible) ← M2
  4. Actions Metrics row (collapsible) ← M2
  5. Chart with 4 selectable mini-stats above ← M3
  6. Data table with full column set ← M4

---

**Last Updated:** 2026-02-24
**Status:** Dashboard 3.0 — M1 ✅ M2 ✅ M3 ✅ M4 ✅ M5 ✅ M6 ✅ M7 ✅ M8 ✅ M9 ✅ COMPLETE
**Next Step:** Phase 3 Future-Proofing (unit tests, job queue, CSRF)
