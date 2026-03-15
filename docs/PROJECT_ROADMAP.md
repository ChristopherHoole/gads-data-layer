# PROJECT ROADMAP - Ads Control Tower (A.C.T.)

**Last Updated:** 2026-03-15
**Overall Completion:** ~99.9%
**Architecture:** 2-Tier (Master Chat → Claude Code)
**Local:** `C:\Users\User\Desktop\gads-data-layer`
**Primary Website:** https://christopherhoole.com (always — never christopherhoole.online)

---

## ✅ COMPLETED PHASES

| Phase | Chats | Status |
|-------|-------|--------|
| Foundation (Flask, DuckDB, auth, multi-client) | 1–17 | ✅ Complete |
| Code Cleanup (blueprints, validation, logging) | 18–21 | ✅ Complete |
| Dashboard 3.0 M1–M9 (date picker → live keyword execution) | 22–30b | ✅ Complete |
| Marketing Website (Next.js, Vercel, christopherhoole.com) | 31 + Master 4.0 | ✅ Complete |
| Rules Creation (57 rules/flags across 5 entity types) | 41–46 | ✅ Complete |
| Multi-Entity Recommendations (1,515 active) | 47–49 | ✅ Complete |
| Module 4: Dashboard Design Upgrade (Google Ads-style tables) | 57–58 | ✅ Complete |
| Cold Outreach System — UI (6 pages) | 59–64 | ✅ Complete |
| Real Data Ingestion Pipeline | 67 | ✅ Complete (blocked on API access) |
| Live Email Sending (Gmail SMTP) | 68 | ✅ Complete |
| Outreach Functions + UI Polish | 69–80 | ✅ Complete |
| UI Cleanup (layout gap, client selector, rules card) | 81–83 | ✅ Complete |
| Website + CV Polish (CV download, SEO, WhatsApp, LinkedIn) | 84–87 | ✅ Complete |
| ad_daily Table + Database Indexes | 88 | ✅ Complete |
| Unit Tests (pytest 80%+, 620 tests) | 89 | ✅ Complete |
| Celery + Redis Background Job Queue | 90 | ✅ Complete |
| Rules & Flags UI Overhaul — Chat 91 | 91 | ✅ Complete |
| Impression Share Pipeline + CAMPAIGN_METRIC_MAP — Chat 92 | 92 | ✅ Complete |
| Templates Tab — Chat 93 | 93 | ✅ Complete |

---

## ✅ CHAT 91 — RULES & FLAGS UI OVERHAUL

**Commits:** 86d0eb6, 4bae83d

- `rules_flow_builder.html` — 5-step modal, condition/action dropdowns, sidebar, full metric list
- `rules_flags_tab.html` — Rules table, Flags table (direction labels, plain English, condition text, badge colours)
- `rules.css` — all rules styling
- Schema normalisation: handles both `op`/`ref` and `operator`/`unit` condition schemas
- Fixed: unescaped apostrophes in JS strings causing SyntaxError

---

## ✅ CHAT 92 — IMPRESSION SHARE PIPELINE + METRIC MAP

**Commit:** 060fe2a

- `act_lighthouse/features.py` — added `impression_share_lost_rank` column (7d rolling avg)
- `scripts/add_impression_share_col.py` — migration script
- `act_autopilot/recommendations_engine.py` — `CAMPAIGN_METRIC_MAP` expanded from 9 → 38 entries

---

## ✅ CHAT 93 — TEMPLATES TAB

**Commit:** 342c8d8

- `scripts/add_is_template_col.py` — adds `is_template BOOLEAN DEFAULT FALSE` to rules table
- `act_dashboard/routes/campaigns.py` — save-as-template route, duplicate detection (type + action_type + condition_1_metric)
- `rules_flags_tab.html` — Templates table (live data), save-as-template bookmark button on every row, Edit template button
- `rules_flow_builder.html` — Edit template mode, Use template footer button, template name label, Save template button text
- **DB state:** 24 rules + 30 flags = 54 total rows (cleaned of test duplicates)
- **Key fixes:** conn must open before duplicate check; json_extract_string not JSON_EXTRACT; state vars set after rfbResetForm()

---

## 🎯 NEXT PRIORITIES — Master Chat 12

### DASHBOARD — ACT
1. Rules strategic review — thresholds, cooldowns, conditions, logic for all 24 rules
2. Recommendations UI review — scoring, prioritisation, entity-specific behaviour
3. Radar / monitoring — post-acceptance monitoring, rollback triggers
4. Real data ingestion — blocked on API Basic Access
5. Conversion tracking checkup on account 487-268-1731
6. Smart alerts (ROAS drop, budget pacing)
7. Automated report generator
8. Memurai install for Celery
9. Unit tests update — ~30-40% of rule tests need rewrite after rules review
10. Performance Max campaign support
11. Display campaign support
12. Video/YouTube campaign support
13. Demand Gen campaign support
14. Multi-user support
15. API endpoints
16. ACT deployment (Railway/Render — security hardening first)
17. Custom domain (app.christopherhoole.com)

### OUTREACH
1. Apollo.io lead import
2. Automated email reports (weekly/monthly)
3. Indeed job listing connector

### WEBSITE
1. Website design upgrade / Hero upgrade
2. Mobile performance optimisation
3. Contact form backend (currently manual)

### GOOGLE ADS — EXTERNAL (monitor only)
1. API Basic Access — Case 21767540705
2. Advertiser verification — Appeal ID 6448619522, account 487-268-1731

### ADMIN
1. Handoff docs produced at end of each Master Chat session

---

## 📊 CURRENT SYSTEM STATE

**Rules & Flags (Campaign entity):**
- Rules: 24 (18 Budget, 6 Bid) — all enabled
- Flags: 30 (16 Performance, 8 Anomaly, 6 Technical) — all enabled
- Templates: 0 (clean slate — create via bookmark button on any rule/flag)
- Total rows: 54

**Recommendations:** 1,515 active (1,256 keywords + 126 shopping + 110 campaigns + 23 ads)

**Tests:** 620 tests, 0 failures, 80% coverage

**Background Jobs:** Celery + Redis (requires Memurai install)
- outreach_poller 120s | queue_scheduler 300s | radar 60s

**Google Ads:**
- Account 487-268-1731 — suspended, appeal in review (ID 6448619522)
- Account 125-489-5944 — active, Campaign 1 running, Manual CPC £3, England
- API: Explorer Access (upgraded from Test Account March 2026), Basic Access pending (Case 21767540705)

---

## 🔧 DEVELOPMENT WORKFLOW

**Flask:**
```powershell
taskkill /IM python.exe /F
cd C:\Users\User\Desktop\gads-data-layer
.\.venv\Scripts\Activate.ps1
python act_dashboard/app.py
```

**Git (ACT):** `git push origin main`
**Git (Website):** `git push origin master`

**Claude Code:** Code tab in Claude Desktop App only — NOT PowerShell.
**Briefs:** Always save as downloadable files to `/docs/` — never inline in chat.

---

**Version:** 7.0 | **Last Updated:** 2026-03-15
