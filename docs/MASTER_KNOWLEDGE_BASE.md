# MASTER KNOWLEDGE BASE - ADS CONTROL TOWER (A.C.T)

**Version:** 20.0
**Created:** 2026-02-19
**Updated:** 2026-03-18
**Purpose:** Complete project context for Master Chat coordination

---

## EXECUTIVE SUMMARY

### Current State (March 18, 2026)
- **Overall Completion:** ~99.9%
- **Phase:** Recommendations engine testing — budget rules next, then flags
- **Active Development:** Master Chat 12
- **Primary Website:** https://christopherhoole.com (always use this — never christopherhoole.online)
- **Email:** chris@christopherhoole.com (Google Workspace, live, DKIM/SPF authenticated)
- **Rules:** 24 campaign rules (18 Budget, 6 Bid) — all enabled
- **Flags:** 30 campaign flags (16 Performance, 8 Anomaly, 6 Technical) — all enabled
- **Templates:** 3
- **Total DB rows:** 57
- **Recommendations:** 0 (cleared for testing — re-run engine to regenerate)
- **Tests:** 620 tests, 80% coverage
- **Background jobs:** Celery + Redis (Chat 90)

### Tech Stack

**A.C.T Dashboard:**
- **Backend:** Python 3.11, Flask
- **Database:** DuckDB (warehouse.duckdb + warehouse_readonly.duckdb)
- **API:** Google Ads API (v15) — Explorer Access (upgraded March 2026), Basic Access pending
- **Frontend:** Bootstrap 5.3, Chart.js 4.4, Vanilla JS
- **Templating:** Jinja2 Macros (metrics_section M2 + performance_chart M3)
- **Date Picker:** Custom Google Ads-style dropdown (Chat 79, datepicker.css)
- **Email:** Gmail SMTP (chris@christopherhoole.com, port 587 TLS, App Password)
- **Background Jobs:** Celery 5.6.2 + Redis (Memurai on Windows) — see docs/CELERY_STARTUP.md
- **Tests:** pytest + pytest-cov, 620 tests, 80% coverage

**Marketing Website:**
- **Framework:** Next.js 14, Tailwind CSS, Framer Motion, shadcn/ui
- **Hero:** Three.js WebGL (r128)
- **Hosting:** Vercel
- **Domain:** christopherhoole.com (primary)

### Development Architecture (2-Tier — Current)

```
Master Chat (claude.ai)
 → Quick fixes done directly here (file upload → edit → download)
 → Large builds: creates concise task briefs as downloadable files to /docs/

Claude Code (Code tab in Claude Desktop App)
 → Executes large builds autonomously
 → Reads codebase directly — no file uploads needed
```

**Brief delivery rule:** Always save briefs as downloadable files to `/docs/` — never inline in chat.

---

## COMPLETE CHAT HISTORY

### Phase 0: Foundation (Chats 1-17) ✅
### Phase 1-2: Code Cleanup + Polish ✅
### Chat 21: Dashboard UI Overhaul ✅
### Chats 22-30b: Dashboard M1-M9 ✅
### Marketing Website ✅
### Chats 84-87: Website + CV Polish ✅
### Chats 41-49: Rules + Recommendations ✅
### Chats 57-58: Dashboard Design Upgrade ✅
### Chats 59-80: Cold Outreach System ✅
### Chats 81-83: UI Cleanup ✅
### Chat 88: ad_daily Table + Database Indexes ✅ — Commit: 088317d
### Chat 89: Unit Tests (pytest 80%+) ✅ — Commit: 51e79c6
### Chat 90: Celery + Redis Background Job Queue ✅ — Commit: a932ee7
### Chat 91: Rules & Flags UI Overhaul ✅ — Commits: 86d0eb6, 4bae83d
### Chat 92: Impression Share Pipeline + Metric Map ✅ — Commit: 060fe2a
### Chat 93: Templates Tab ✅ — Commit: 342c8d8

### Chats 97-100: Recommendations Engine Testing + Fixes ✅
**Commits:** 30decda, 61002f3

**Chat 97 — Recommendations UI Fixes:**
- `recommendations.py` — `_load_monitoring_days()` reads `cooldown_days` from DB rules table for `db_campaign_*` rule IDs
- `recommendations.py` — second pass in `recommendations_cards()` re-calculates `action_label` AND `value_label` AFTER `_enrich_with_rule_data()` populates `action_type`
- `recommendations.css` — `.rec-col-rule`: `white-space: normal; word-break: break-word`
- `campaigns.html` + `recommendations.html` — `actionCell()` Human confirm badge stacked above action text
- `campaigns.html` — status rules expand row shows "Enabled → Paused" not "Current: 4 / Proposed: 4"
- `_ACTION_TYPE_TO_RULE_TYPE` — added `decrease_max_cpc` and `increase_max_cpc` entries
- `get_action_label()` — checks `action_type` for max_cpc/tcpa distinction per entity

**Chat 99 — Engine Fixes (micros, broken rules, impression share):**
- `recommendations_engine.py` — 4th tuple element (divisor `1_000_000`) added to `cpc_avg_*`, `cost_*`, `cpa_*` in all metric maps; `_get_metric_value()` applies divisor
- `act_lighthouse/features.py` — `rank_lost_is_expr` falls back to `(1.0 - search_impression_share) * 100.0`
- `scripts/fix_rules_19_20_conditions.py` — fixed `op=None` on rules 19 & 20 (run once, complete)
- `scripts/rebuild_campaign_features.py` — rebuilt `campaign_features_daily` with non-NULL impression share

**Chat 100 — Engine Fix (valid date query):**
- `recommendations_engine.py` — entity data query uses `MAX(snapshot_date) WHERE name IS NOT NULL` subquery → loads 4 rows not 360

### Google Ads API Application (March 2026)
- Access upgraded: Test Account → **Explorer Access** (read production, no writes)
- Basic Access Case: 21767540705 — pending

### Google Ads Account Suspension
- **Appeal ID: 6448619522** — "Your appeal is in review"
- Do NOT submit another appeal. Monitor chris@christopherhoole.com.

---

## CURRENT STATUS

### What's Working
- All 6 dashboard pages with Google Ads-style tables
- 24 campaign rules + 30 flags (all enabled)
- Templates sub-tab — save/edit/use template, duplicate detection
- Recommendations engine — generates correct recs from DB rules
- Accept → Monitoring (correct cooldown from rules table) ✅
- Decline → History ✅
- Accept all low risk bulk action ✅
- Action labels correct for all rule types (budget/bid/status/CPC cap) ✅
- CPC/CPA/cost metrics converted from micros correctly ✅
- Engine loads only most recent valid snapshot date ✅
- impression_share_lost_rank populated (approximate fallback) ✅
- Rules 19 & 20 conditions fixed ✅
- Changes audit trail
- Cold Outreach System — 6 pages, all 10 functions live
- Marketing website live (christopherhoole.com)
- 620 unit tests, 80% coverage
- Celery + Redis job queue (requires Memurai install)

### What's Blocked / Pending
- Rules 16, 17, 18, 20 don't fire — `campaign_type_lock` can't be enforced (NULL `bid_strategy_type` in synthetic data). Will work on real data.
- Google Ads API Basic Access (Case 21767540705)
- Advertiser verification appeal (ID 6448619522)
- Memurai install (for Celery to run)

### Known Bugs (logged, not yet fixed)
- Keywords search terms gone — DATE/VARCHAR type mismatch in `keywords.py` line 187
- Shopping page query error — table alias `s` not found in `shopping.py` line 108
- Trigger summary wrong label — rule 19 shows "ROAS" label instead of "CPA"

---

## RECOMMENDATIONS ENGINE STATE

**Confirmed working on synthetic data:**
- Rule 7 (Decrease Budget – Weak CPA) — fires on all 4 campaigns
- Rule 21 (Decrease Max CPC Cap) — fires on 2 campaigns (CPC > £5 after micros fix)
- Rule 19 (Loosen tCPA Target) — fires on 1 campaign (IS lost rank > 20%)
- Status rules (Pause – Poor ROAS, Pause – High CPA, Pause – High CPC) — all fire correctly

**Rules that skip (expected — synthetic data limitation):**
- Rules 16, 17, 18, 20 — campaign_type_lock (tROAS/tCPA/Max Clicks) can't be enforced when bid_strategy_type is NULL

**Synthetic data:** Christopher Hoole client, customer_id `1254895944`, 4 campaigns
**Last valid snapshot date:** 2026-03-16

---

## DB STATE

| Table | Count |
|-------|-------|
| Rules (campaign, is_template=FALSE) | 24 |
| Flags (campaign, is_template=FALSE) | 30 |
| Templates (is_template=TRUE) | 3 |
| **Total rows** | **57** |

**Diagnostic scripts (project root):**
- `full_audit.py` — full breakdown of all rules/flags/templates
- `check_state.py` — recent rows + template state
- `check_rules.py` — list all rules with enabled status
- `check_bid_rules.py` — bid rule conditions
- `check_bid_rules2.py` — campaign features vs thresholds
- `check_campaign_names.py` — campaign names in features table
- `check_engine_date.py` — most recent valid snapshot date
- `cleanup_junk.py` — delete specific IDs
- `cleanup_all_templates.py` — delete all template rows

---

## KNOWN PITFALLS (Quick Reference)

| Problem | Fix |
|---------|-----|
| Template CSS missing | Must extend base_bootstrap.html |
| DB query fails | Use ro.analytics.* not analytics.* |
| Route replacement fails | Match exact quote style |
| json_extract returns quoted value | Use json_extract_string not JSON_EXTRACT |
| Duplicate check silently failing | conn must be open BEFORE the check query |
| JS state vars wiped | Set _rfbEditId/_rfbIsTemplate AFTER rfbResetForm() |
| onclick function does nothing | Verify function is actually defined in JS |
| Apostrophe breaks JS | Escape as \' in single-quoted strings |
| Flag condition shows wrong direction | Use direction-aware label objects {pos, neg} |
| Recommendations limit=200 truncates | Increase to 5000+ |
| CSRF 400 | Add csrf.exempt() to routes |
| Opened/clicked showing 0 | Use open_count > 0 not opened_at IS NOT NULL |
| Client selector switching | Use session.get() not get_current_config() |
| Email no formatting | Add \n→<br> wrap in queue_send() |
| Email garbled chars | MIMEText needs all 3 args including "utf-8" |
| White box gap on entity pages | table-styles.css had prototype body/container CSS |
| Navbar text hidden | Never define .d-none in custom CSS |
| Celery worker not running | Install Memurai first — see docs/CELERY_STARTUP.md |
| CPC/CPA showing micros in engine | Add 4th tuple element (1_000_000) to metric map entries |
| Accept goes straight to Successful | _load_monitoring_days must query DB rules table for db_campaign_* IDs |
| Action label shows tROAS for CPC cap | Re-run get_action_label() AFTER _enrich_with_rule_data() sets action_type |
| Engine loads 360 rows not 4 | Use MAX(snapshot_date) WHERE name IS NOT NULL subquery |
| Campaign names show as IDs | Synthetic data has NULL names for dates without source data |
| Rules 19/20 never fire | op=None in DB conditions — run fix_rules_19_20_conditions.py |

**See KNOWN_PITFALLS.md for full detail.**

---

## KEY FILE PATHS

| File | Purpose |
|------|---------|
| `act_dashboard/routes/recommendations.py` | Accept/decline/monitoring, action labels, enrichment |
| `act_autopilot/recommendations_engine.py` | Engine — metric map, condition evaluation, micros fix, date query |
| `act_lighthouse/features.py` | Feature engineering — impression_share_lost_rank fallback |
| `act_dashboard/templates/recommendations.html` | Full recommendations page |
| `act_dashboard/templates/campaigns.html` | Campaigns page rec tab |
| `act_dashboard/static/css/recommendations.css` | Column widths, badges, layout |
| `scripts/fix_rules_19_20_conditions.py` | One-time migration — rules 19/20 conditions (already run) |
| `scripts/rebuild_campaign_features.py` | Rebuilds campaign_features_daily |
| `act_dashboard/email_sender.py` | SMTP sending module |
| `act_dashboard/celery_app.py` | Celery instance + beat schedule |
| `act_dashboard/routes/campaigns.py` | Campaign rules CRUD + save-as-template |
| `act_autopilot/rules_config.json` | Rules UI config layer (non-campaign rules) |
| `tests/` | pytest test suite — 620 tests, 80% coverage |
| `docs/CELERY_STARTUP.md` | Celery + Redis startup instructions |

---

## GOOGLE ADS ACCOUNT DETAILS

| Field | Value |
|-------|-------|
| Primary account | 487-268-1731 (chris@christopherhoole.com) — active |
| Test account | 125-489-5944 (joicemoura1001@gmail.com) — active |
| MCC | 152-796-4125 |
| Developer token | oDANZ-BXQprTm7_Sg4rjDg |
| API Case ID | 21767540705 |
| Appeal ID | 6448619522 |
| API Access Level | Explorer (upgraded from Test Account, March 2026) |

---

## LATEST COMMITS

| Commit | Description |
|--------|-------------|
| 61002f3 | Chats 99-100: Engine fixes — micros, rules 19/20, impression share, valid date query |
| 30decda | Chat 97: Recommendations UI fixes — action labels, monitoring, column widths, display polish |
| 342c8d8 | Chat 93: Templates tab |
| 4bae83d | Chat 91: Flags sub-tab UI overhaul |
| 060fe2a | Chat 92: impression_share_lost_rank pipeline + CAMPAIGN_METRIC_MAP |
| a932ee7 | Chat 90: Celery + Redis job queue |

---

**Version:** 20.0 | **Last Updated:** 2026-03-18
**Architecture:** 2-Tier (Master Chat → Claude Code)
**Next Step:** Test budget rules, then flags
