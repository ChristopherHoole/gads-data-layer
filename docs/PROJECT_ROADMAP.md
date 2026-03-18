# PROJECT ROADMAP - Ads Control Tower (A.C.T.)

**Last Updated:** 2026-03-18
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

---

## CHATS 97-100 — RECOMMENDATIONS ENGINE TESTING + FIXES

**Commits:** 30decda, 61002f3

**Chat 97 — UI Fixes:**
- Accept goes to Monitoring correctly — _load_monitoring_days reads cooldown_days from DB
- Action labels + value labels correct — second pass after action_type is populated
- Rule name column wraps; Human confirm badge stacked above action text
- Status rules expand row shows "Enabled → Paused"

**Chat 99 — Engine Fixes:**
- CPC/CPA/cost: 4th tuple element (1_000_000 divisor) in metric maps
- Rules 19 & 20: op=None fixed
- impression_share_lost_rank: fallback to (1 - search_impression_share) * 100

**Chat 100 — Date Fix:**
- Engine loads only most recent valid snapshot date — MAX(snapshot_date) WHERE name IS NOT NULL

---

## NEXT PRIORITIES — Master Chat 12 (in progress)

**DASHBOARD — ACT**
1. Test budget rules — enable all 18 budget rules, run engine, verify recs
2. Test flags — enable all 30 flags, run engine, verify flag behaviour
3. Fix Keywords search terms — DATE/VARCHAR mismatch in keywords.py line 187
4. Fix Shopping page query — table alias s not found in shopping.py line 108
5. Fix trigger summary label — rule 19 shows ROAS not CPA
6. Rules strategic review — thresholds, cooldowns, conditions for all 24 rules
7. Radar / monitoring — post-acceptance monitoring, rollback triggers
8. Real data ingestion — blocked on API Basic Access
9. Conversion tracking checkup on account 487-268-1731
10. Smart alerts, automated report generator, Memurai install, unit tests update
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
- Rules: 24 (18 Budget, 6 Bid) — all enabled
- Flags: 30 (16 Performance, 8 Anomaly, 6 Technical) — all enabled
- Templates: 3
- Total rows: 57

**Recommendations:** 0 (cleared for testing)

**Tests:** 620 tests, 0 failures, 80% coverage

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

**Clear recommendations and changes:**
```powershell
python -c "import duckdb; conn = duckdb.connect('warehouse.duckdb'); conn.execute('DELETE FROM recommendations'); conn.execute('DELETE FROM changes'); print('Cleared'); conn.close()"
```

**Git (ACT):** `git push origin main`
**Claude Code:** Code tab in Claude Desktop App only — NOT PowerShell.
**Briefs:** Always save as downloadable files to /docs/ — never inline in chat.

---

**Version:** 8.0 | **Last Updated:** 2026-03-18
