# PROJECT ROADMAP - Ads Control Tower (A.C.T.)

**Last Updated:** 2026-03-12
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
| Rules Creation (41 rules across 5 entity types) | 41–46 | ✅ Complete |
| Multi-Entity Recommendations (1,492 active) | 47–49 | ✅ Complete |
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

---

## ✅ CHAT 88 — AD_DAILY TABLE + DATABASE INDEXES

**Commit:** 088317d

- `tools/seed_ad_daily.py` — populates ad_daily with 90 days synthetic data
- `scripts/copy_all_to_readonly.py` — updated to include ad_daily (6 tables total)
- `scripts/add_indexes.py` — indexes on all 6 analytics tables in warehouse_readonly.duckdb
- **Result:** 23 Ad recommendations now generating (was 0). 983 ads, 12 rules active.

---

## ✅ CHAT 89 — UNIT TESTS (pytest 80%+)

**Commit:** 51e79c6

- `tests/` folder — 19 test files, 620 tests, 0 failures
- Coverage: campaigns 85%, ads 85%, changes 94%, rule_helpers 94%, shared 86%, recommendations 80%
- **Note:** ~30-40% of rule-specific tests will need updating after Rules & Recommendations overhaul

---

## ✅ CHAT 90 — CELERY + REDIS BACKGROUND JOB QUEUE

**Commit:** a932ee7

- `act_dashboard/celery_app.py` — Celery instance, Redis broker, 3 periodic tasks
- `outreach_poller.py`, `queue_scheduler.py`, `radar.py` — converted to Celery tasks
- Daemon thread starts removed from `app.py`
- `requirements.txt` — celery 5.6.2 + redis 7.3.0 added
- `docs/CELERY_STARTUP.md` — full startup instructions

**Manual prerequisite:** Install Memurai (Windows Redis) from https://www.memurai.com/

**Startup sequence (3 terminals):**
```
Terminal 1: memurai
Terminal 2: celery -A act_dashboard.celery_app worker --beat --loglevel=info
Terminal 3: python act_dashboard/app.py
```

---

## 🎯 NEXT PRIORITIES

### IMMEDIATE — Master Chat 11

**Rules & Recommendations Overhaul** (major — multiple Claude Code chats)
- Deep design discussion in Master Chat 11 — wireframes required before any build
- Review all 41 rules — thresholds, conditions, cooldowns
- Review recommendation generation logic — entity-specific scoring
- Note: ~30-40% of Chat 89 unit tests will need updating after this overhaul

**Google Ads Account Suspension** (waiting on Google)
- Appeal ID: 6448619522 — submitted 12 Mar 2026
- Check chris@christopherhoole.com (1–10 days). Do NOT submit another appeal.

**Google Ads API Basic Access** (waiting on Google)
- Case 24460840136 — submitted 4 Mar 2026
- Once approved → run `tools/run_ingestion.py`

**Conversion Tracking** — verify "Enviar formulário de lead" count > 0 in Google Ads Goals

### MEDIUM

- Apollo.io lead import (8-15 hrs)
- M9 Live Validation — blocked on API Basic Access
- Automated email reports (weekly/monthly)
- Smart alerts (ROAS drop, budget pacing)
- Website design upgrade / Hero upgrade
- Mobile performance optimisation
- Contact form backend (currently manual)
- Install Memurai for Celery

### LONG-TERM

- Performance Max Campaigns (20-30 hrs)
- Display Campaigns (15-20 hrs)
- Video/YouTube Campaigns (15-20 hrs)
- Demand Gen Campaigns (15-20 hrs)
- Automated Report Generator (20-25 hrs)
- Multi-User Support (12-15 hrs)
- API Endpoints (10-12 hrs)
- Indeed job listing connector
- ACT deployment (Railway/Render — security hardening first)
- Custom domain for ACT (app.christopherhoole.com)

---

## 📊 CURRENT SYSTEM STATE

**Rules:** 41 active (13 campaign + 6 keyword + 4 ad_group + 4 ad + 14 shopping)

**Recommendations:**
- Campaigns: 110 | Keywords: 1,256 | Shopping: 126 | Ads: 23 | Ad Groups: 0
- **Total: 1,515 active**

**Tests:** 620 tests, 0 failures, 80% coverage

**Background Jobs:** Celery + Redis (requires Memurai install)
- outreach_poller 120s | queue_scheduler 300s | radar 60s

**Google Ads:**
- Account 487-268-1731 — suspended, appeal in review (ID 6448619522)
- Account 125-489-5944 — active, Campaign 1 running, Manual CPC £3, England
- API: Test Access only, Basic Access pending (Case 24460840136)

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

**Version:** 6.0 | **Last Updated:** 2026-03-12
