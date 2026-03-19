# PROJECT ROADMAP - Ads Control Tower (A.C.T.)

**Last Updated:** 2026-03-19
**Overall Completion:** ~99.9%
**Architecture:** 2-Tier (Master Chat → Claude Code)
**Local:** `C:\Users\User\Desktop\gads-data-layer`
**Primary Website:** https://christopherhoole.com (always — never christopherhoole.online)

---

## COMPLETED PHASES

| Phase | Chats | Status |
|-------|-------|--------|
| Foundation (Flask, DuckDB, auth, multi-client) | 1–17 | Complete |
| Code Cleanup (blueprints, validation, logging) | 18–21 | Complete |
| Dashboard 3.0 M1–M9 | 22–30b | Complete |
| Marketing Website | 31 + Master 4.0 | Complete |
| Rules Creation | 41–46 | Complete |
| Multi-Entity Recommendations | 47–49 | Complete |
| Dashboard Design Upgrade | 57–58 | Complete |
| Cold Outreach System | 59–64 | Complete |
| Real Data Ingestion Pipeline | 67 | Complete (blocked on API) |
| Live Email Sending | 68 | Complete |
| Outreach Functions + UI Polish | 69–80 | Complete |
| UI Cleanup | 81–83 | Complete |
| Website + CV Polish | 84–87 | Complete |
| ad_daily Table + Database Indexes | 88 | Complete |
| Unit Tests (pytest 80%+, 620 tests) | 89 | Complete |
| Celery + Redis Background Job Queue | 90 | Complete |
| Rules & Flags UI Overhaul | 91 | Complete |
| Impression Share Pipeline + CAMPAIGN_METRIC_MAP | 92 | Complete |
| Templates Tab | 93 | Complete |
| Recommendations Engine Testing + Fixes | 97–100 | Complete |
| Flags System (engine, routes, UI, fixes) | 101 + Master Chat 12 | Complete |

---

## CHAT 101 + MASTER CHAT 12 — FLAGS SYSTEM ✅

**What was built:**
- `flags` table in warehouse.duckdb
- `_run_flag_engine()` in recommendations_engine.py — evaluates flag rules after main engine, same metric maps and duplicate prevention
- `/flags/cards` GET — returns active/snoozed/history groups, lazy snooze expiry check
- `/flags/<id>/acknowledge` POST — moves to snoozed using rule's cooldown_days
- `/flags/<id>/ignore` POST — moves to snoozed with 7/14/30 day options
- Flags tab on main Recommendations page — entity filter pills, active table, collapsible Snoozed + History sections
- Flags subtab on all 5 entity pages (Campaigns, Ad Groups, Keywords, Ads, Shopping) — active table + collapsible Snoozed + History sections
- Expand rows on all flag tables — Why triggered / Flag details / Rule details

**Bugs found and fixed during testing:**
- All 15 `vs_prev_pct` flag conditions had whole-number values (e.g. -30) instead of decimal ratios (-0.30) — fixed via `fix_all_flag_conditions.py`
- 8 flags had `op=None` — fixed with correct operators in same script
- Bootstrap dropdowns on dynamically rendered rows required event delegation (not reinit)
- Functions inside IIFE not accessible from inline onclick — exposed via `window.fnName`
- `stopPropagation()` on snoozed/history rows was silently killing dropdown clicks — removed
- Snoozed/History sections initially missing from entity page Flags subtabs — added to all 5 pages

---

## NEXT PRIORITIES — Master Chat 13

**DASHBOARD — ACT**
1. Fix Keywords search terms — custom date range (non-preset) causes DATE/VARCHAR mismatch in `keywords.py` line 187. Preset 7d/30d/90d buttons work fine.
2. Fix Shopping page query — table alias `s` not found in `shopping.py` line 108
3. Fix trigger summary label — rule 19 shows ROAS label instead of CPA
4. Rules strategic review — thresholds, cooldowns, conditions for all rules
5. Test all flags with real data — synthetic data swings too small for most thresholds
6. Radar / monitoring — post-acceptance monitoring, rollback triggers
7. Conversion tracking checkup on account 487-268-1731
8. Memurai install — required for Celery background jobs to run
9. Unit tests update — 620 tests written pre-flags, need updating
10. Smart alerts and automated report generator
11. Campaign type expansion (PMax, Display, Video, Demand Gen)
12. Multi-user support, API endpoints, ACT deployment

**OUTREACH**
1. Apollo.io lead import
2. Automated email reports (weekly/monthly)
3. Indeed job listing connector

**WEBSITE**
1. Website design upgrade / Hero upgrade
2. Mobile performance optimisation
3. Contact form backend

**GOOGLE ADS — EXTERNAL (monitor only)**
1. API Basic Access — Case 21767540705
2. Advertiser verification — Appeal ID 6448619522, account 487-268-1731

**ADMIN**
1. Handoff docs produced at end of each Master Chat session

---

## CURRENT SYSTEM STATE

**Rules & Flags (Campaign entity):**
- Rules: 19 (13 Budget, 6 Bid) — all enabled
- Flags: 30 (16 Performance, 8 Anomaly, 6 Technical) — all enabled
- Templates: 3
- flags table: 0 rows (cleared after testing)
- Recommendations: 0 (cleared after testing)
- Changes: 0 (cleared after testing)

**Tests:** 620 tests, 80% coverage (pre-flags — needs update)
**Background Jobs:** Celery + Redis (requires Memurai install)

**Google Ads:**
- Account 487-268-1731 — suspended, appeal in review (ID 6448619522)
- Account 125-489-5944 — active
- API: Explorer Access, Basic Access pending (Case 21767540705)

---

## DEVELOPMENT WORKFLOW

**Flask:**
```powershell
taskkill /IM python.exe /F
cd C:\Users\User\Desktop\gads-data-layer
.\.venv\Scripts\Activate.ps1
python act_dashboard/app.py
```

**Clear all:**
```powershell
python -c "import duckdb; conn = duckdb.connect('warehouse.duckdb'); conn.execute('DELETE FROM recommendations'); conn.execute('DELETE FROM changes'); conn.execute('DELETE FROM flags'); print('Cleared'); conn.close()"
```

**Git:** `git push origin main`
**Claude Code:** Code tab in Claude Desktop App only — NOT PowerShell.
**Briefs:** Always save as downloadable files to /docs/ — never inline in chat.

---

**Version:** 9.0 | **Last Updated:** 2026-03-19
