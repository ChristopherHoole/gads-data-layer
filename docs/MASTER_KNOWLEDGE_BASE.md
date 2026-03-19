# MASTER KNOWLEDGE BASE - ADS CONTROL TOWER (A.C.T)

**Version:** 21.0
**Created:** 2026-02-19
**Updated:** 2026-03-19
**Purpose:** Complete project context for Master Chat coordination

---

## EXECUTIVE SUMMARY

### Current State (March 19, 2026)
- **Overall Completion:** ~99.9%
- **Phase:** Flags system complete — keyword/shopping bug fixes next
- **Active Development:** Master Chat 13 (starting)
- **Primary Website:** https://christopherhoole.com (always use this — never christopherhoole.online)
- **Email:** chris@christopherhoole.com (Google Workspace, live, DKIM/SPF authenticated)
- **Rules:** 19 campaign rules (13 Budget, 6 Bid) — all enabled
- **Flags:** 30 campaign flags (16 Performance, 8 Anomaly, 6 Technical) — all enabled
- **Templates:** 3
- **flags table:** 0 rows (cleared after testing)
- **Recommendations:** 0 (cleared for testing)
- **Changes:** 0 (cleared for testing)
- **Tests:** 620 tests, 80% coverage (pre-flags — needs update)
- **Background jobs:** Celery + Redis (requires Memurai install)

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
- `campaigns.html` — status rules expand row shows "Enabled → Paused"
- `_ACTION_TYPE_TO_RULE_TYPE` — added `decrease_max_cpc` and `increase_max_cpc` entries
- `get_action_label()` — checks `action_type` for max_cpc/tcpa distinction per entity

**Chat 99 — Engine Fixes (micros, broken rules, impression share):**
- `recommendations_engine.py` — 4th tuple element (divisor `1_000_000`) added to `cpc_avg_*`, `cost_*`, `cpa_*` in all metric maps; `_get_metric_value()` applies divisor
- `act_lighthouse/features.py` — `rank_lost_is_expr` falls back to `(1.0 - search_impression_share) * 100.0`
- `scripts/fix_rules_19_20_conditions.py` — fixed `op=None` on rules 19 & 20 (run once, complete)
- `scripts/rebuild_campaign_features.py` — rebuilt `campaign_features_daily` with non-NULL impression share

**Chat 100 — Engine Fix (valid date query):**
- `recommendations_engine.py` — entity data query uses `MAX(snapshot_date) WHERE name IS NOT NULL` subquery → loads 4 rows not 360

### Chat 101 + Master Chat 12: Flags System ✅
**Commits:** b8188fe (pre-build checkpoint) + final commit

**What was built:**
- `flags` DB table in warehouse.duckdb
- `_run_flag_engine()` in recommendations_engine.py — evaluates `rule_or_flag = 'flag'` rules after main engine, uses same CAMPAIGN_METRIC_MAP and `_evaluate_condition()`, correct MAX(snapshot_date) date query, duplicate prevention (skips if active or within snooze window)
- `/flags/cards` GET — returns `{active, snoozed, history}`, lazy snooze expiry check on every call
- `/flags/<id>/acknowledge` POST — sets status=snoozed, snooze_until = NOW() + cooldown_days from rules table
- `/flags/<id>/ignore` POST — sets status=snoozed, snooze_until = NOW() + days (7/14/30)
- All 3 flag routes CSRF exempted
- Flags tab on main Recommendations page — entity filter pills (All/Campaigns/Ad Groups/Keywords/Ads/Shopping), active table, collapsible Snoozed section (Snoozed until column), collapsible History section (Actioned column)
- Flags subtab on all 5 entity pages (Campaigns, Ad Groups, Keywords, Ads, Shopping) — active table + collapsible Snoozed section + collapsible History section
- Expand rows on ALL flag tables across all pages — Why triggered / Flag details / Rule details
- Actions dropdown on ALL flag rows (active, snoozed, history) across all pages

**Bugs found and fixed during testing:**
- All 15 `vs_prev_pct` flag conditions stored as whole numbers (e.g. -30) not decimals (-0.30) — fixed via `fix_all_flag_conditions.py` (already run — do NOT re-run)
- 8 flags had `op=None` — fixed with correct operators (lt/gt) in same script
- Bootstrap dropdowns on dynamically rendered rows — event delegation required, NOT bootstrap.Dropdown reinit
- Functions inside IIFE inaccessible from inline onclick — exposed via `window.fnName`
- `stopPropagation()` on snoozed/history TDs silently blocked event delegation dropdowns — removed
- Snoozed/History sections initially missing from entity page Flags subtabs — added to all 5 pages

**Tested and verified:**
- ✅ Engine generates flags (tested with Conversion Drop id=33 threshold temporarily lowered to -0.05)
- ✅ Duplicate prevention — SkippedDuplicate=1 on second run
- ✅ Expand row on active, snoozed and history rows across all pages
- ✅ Actions dropdown on all rows across all pages
- ✅ Acknowledge moves flag to Snoozed with correct snooze_until (today + cooldown_days)
- ✅ Snoozed section expands with correct columns including Snoozed until date
- ✅ History section renders correctly
- ✅ Flask starts cleanly, no console errors

**Flag 33 threshold restored to -0.30 after testing.**

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
- 19 campaign rules (13 Budget, 6 Bid) — all enabled
- 30 campaign flags (16 Performance, 8 Anomaly, 6 Technical) — all enabled
- Templates sub-tab — save/edit/use template, duplicate detection
- Recommendations engine — generates correct recs from DB rules
- Flags engine — generates flags, duplicate prevention, acknowledge/ignore/snooze
- Accept → Monitoring (correct cooldown from rules table) ✅
- Decline → History ✅
- Accept all low risk bulk action ✅
- Action labels correct for all rule types ✅
- CPC/CPA/cost metrics converted from micros correctly ✅
- Engine loads only most recent valid snapshot date ✅
- Flags tab on Recommendations page — Active / Snoozed / History ✅
- Flags subtab on all 5 entity pages — Active / Snoozed / History ✅
- Changes audit trail
- Cold Outreach System — 6 pages, all 10 functions live
- Marketing website live (christopherhoole.com)
- 620 unit tests, 80% coverage
- Celery + Redis job queue (requires Memurai install)

### What's Blocked / Pending
- Rules 16, 17, 18, 20 don't fire — `campaign_type_lock` can't be enforced (NULL `bid_strategy_type` in synthetic data). Will work on real data.
- Google Ads API Basic Access (Case 21767540705)
- Memurai install (for Celery to run)

### Known Bugs (logged — fix in Master Chat 13)
- Keywords search terms — custom date range causes DATE/VARCHAR mismatch in `keywords.py` line 187. Preset 7d/30d/90d buttons work fine.
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

## FLAGS ENGINE STATE

**vs_prev_pct flags:** All 15 conditions fixed (decimals not whole numbers). All 8 op=None conditions fixed.
**Tested:** Conversion Drop (id=33) — fires on PPC Freelancer with threshold lowered to -0.05. Threshold restored to -0.30.
**Synthetic data limitation:** Max swing is ~10% — none of the flags fire at real-world thresholds on synthetic data. Will test properly with real Google Ads data.

---

## DB STATE

| Table | Count |
|-------|-------|
| Rules (campaign, is_template=FALSE) | 19 |
| Flags (campaign, is_template=FALSE) | 30 |
| Templates (is_template=TRUE) | 3 |
| flags table | 0 (cleared after testing) |
| Recommendations | 0 (cleared) |
| Changes | 0 (cleared) |

**Diagnostic scripts (project root):**
- `full_audit.py` — full breakdown of all rules/flags/templates
- `check_state.py` — recent rows + template state
- `check_rules.py` — list all rules with enabled status
- `check_bid_rules.py` — bid rule conditions
- `check_bid_rules2.py` — campaign features vs thresholds
- `check_campaign_names.py` — campaign names in features table
- `check_engine_date.py` — most recent valid snapshot date
- `check_flag33.py` — flag 33 conditions vs data
- `check_flag_data.py` — all vs_prev_pct values in synthetic data
- `check_absolute_flags.py` — non-percentage flag conditions
- `fix_all_flag_conditions.py` — fixed flag conditions (already run — do NOT re-run)
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
| onclick function does nothing | Expose via window.fnName — IIFE scope issue |
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
| Flag vs_prev_pct never fires | Thresholds must be decimals (-0.30) not whole numbers (-30) |
| Flag op=None never fires | Set correct op: lt for drops, gt for spikes |
| Bootstrap dropdown not opening (dynamic) | Use document event delegation — not bootstrap.Dropdown reinit |
| Dropdown works on active rows not snoozed | stopPropagation on TD kills delegation — remove it |
| Flag row click does nothing | Expose toggle function via window.fnName |

**See KNOWN_PITFALLS.md for full detail.**

---

## KEY FILE PATHS

| File | Purpose |
|------|---------|
| `act_dashboard/routes/recommendations.py` | Accept/decline/monitoring, action labels, flags routes |
| `act_autopilot/recommendations_engine.py` | Engine + flag engine — metric map, condition evaluation, micros fix, date query |
| `act_lighthouse/features.py` | Feature engineering — impression_share_lost_rank fallback |
| `act_dashboard/templates/recommendations.html` | Full recommendations page + Flags tab |
| `act_dashboard/templates/campaigns.html` | Campaigns page rec tab + Flags subtab |
| `act_dashboard/templates/ad_groups.html` | Ad Groups page + Flags subtab |
| `act_dashboard/templates/keywords.html` | Keywords page + Flags subtab |
| `act_dashboard/templates/ads.html` | Ads page + Flags subtab |
| `act_dashboard/templates/shopping.html` | Shopping page + Flags subtab |
| `act_dashboard/static/css/recommendations.css` | Column widths, badges, flag severity styles |
| `act_dashboard/routes/keywords.py` line 187 | Keywords search terms DATE/VARCHAR bug |
| `act_dashboard/routes/shopping.py` line 108 | Shopping query table alias bug |
| `scripts/fix_rules_19_20_conditions.py` | One-time migration — rules 19/20 (already run) |
| `scripts/fix_all_flag_conditions.py` | Fixed flag conditions — already run, do NOT re-run |
| `scripts/rebuild_campaign_features.py` | Rebuilds campaign_features_daily |
| `act_dashboard/email_sender.py` | SMTP sending module |
| `act_dashboard/celery_app.py` | Celery instance + beat schedule |
| `act_dashboard/routes/campaigns.py` | Campaign rules CRUD + save-as-template |
| `act_autopilot/rules_config.json` | Rules UI config layer (non-campaign rules) |
| `tests/` | pytest test suite — 620 tests, 80% coverage |
| `docs/CELERY_STARTUP.md` | Celery + Redis startup instructions |
| `docs/wireframes/flags_wireframe.html` | Approved flags wireframe |

---

## GOOGLE ADS ACCOUNT DETAILS

| Field | Value |
|-------|-------|
| Primary account | 487-268-1731 — active, live campaigns running |
| Test account | 125-489-5944 — not in use |
| MCC | 152-796-4125 |
| Developer token | oDANZ-BXQprTm7_Sg4rjDg |
| API Case ID | 21767540705 — Basic Access pending |
| API Access Level | Explorer (upgraded from Test Account, March 2026) |

---

## LATEST COMMITS

| Commit | Description |
|--------|-------------|
| final (pending) | Chat 101: Flags system complete — engine, routes, UI, all fixes |
| b8188fe | Chat 101: Add flags wireframe and brief — pre-build checkpoint |
| 61002f3 | Chats 99-100: Engine fixes — micros, rules 19/20, impression share, valid date query |
| 30decda | Chat 97: Recommendations UI fixes |
| 342c8d8 | Chat 93: Templates tab |

---

**Version:** 21.0 | **Last Updated:** 2026-03-19
**Architecture:** 2-Tier (Master Chat → Claude Code)
**Next Step:** Master Chat 13 — Keywords search terms fix, Shopping query fix, trigger summary label fix
