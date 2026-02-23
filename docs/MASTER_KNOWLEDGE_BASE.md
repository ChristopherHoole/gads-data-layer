# MASTER KNOWLEDGE BASE - ADS CONTROL TOWER (A.C.T)

**Version:** 8.0
**Created:** 2026-02-19
**Updated:** 2026-02-23
**Purpose:** Complete project context for Master Chat coordination

---

## EXECUTIVE SUMMARY

### Current State (Feb 23, 2026)
- **Overall Completion:** ~97%
- **Phase:** Dashboard 3.0 — M8 complete ✅, M9 Search Terms / Keywords NEXT
- **Active Development:** Dashboard 3.0 modular improvements
- **Templating:** Jinja2 Macros (metrics_section M2 + performance_chart M3)

### Tech Stack
- **Backend:** Python 3.11, Flask
- **Database:** DuckDB (warehouse.duckdb)
- **API:** Google Ads API (v15)
- **Frontend:** Bootstrap 5.3, Chart.js 4.4, Vanilla JS, Flatpickr
- **Templating:** Jinja2 Macros (metrics_section macro from M2)

---

## COMPLETE CHAT HISTORY

### Phase 0: Foundation (Chats 1-17) ✅
- Chats 1-11: Flask app, DuckDB, auth, multi-client YAML
- Chat 12: Shopping module (14 rules, 4-tab UI, 3,800 lines)
- Chat 13.1: Constitution execution engine (safety guardrails, dry-run + live)
- Chat 14: Dashboard execution UI (buttons, toasts, change history)
- Chat 17: Architecture refactor — unified recommendation system

### Phase 1: Code Cleanup ✅
- 16/16 routes → 8 modular blueprints
- Input validation, rate limiting, logging, cache, error handling

### Phase 2: Polish ✅
- DRY helpers, type hints, config validation

### Chat 21: Dashboard UI Overhaul ✅
All 6 pages rebuilt with Bootstrap 5:
- 21a: Bootstrap foundation + base_bootstrap.html (commit 5789628)
- 21b: Main dashboard + Chart.js trend (commit 4976a29)
- 21c: Campaigns + Rule Visibility System (commit 3ab82a2)
- 21d: Keywords + QS distribution (commit f0fbd15)
- 21e: Ad Groups
- 21f: Ads
- 21g: Shopping (4 tabs)
- 21h: Polish

Key outputs: base_bootstrap.html, rule_helpers.py, rules_sidebar/tab/card components, dynamic category detection (regex: r'_\d{3}(?:_|$)')

### Chat 22 — M1: Date Range Picker ✅
**Date:** 2026-02-19 | **Commits:** a644fdd + 25c7af5
- Flatpickr replacing URL-parameter system
- Session-based persistence across all 6 pages
- Preset (7d/30d/90d) + custom date range

### Chat 23 — M2: Metrics Cards ✅
**Date:** 2026-02-20 | **Commit:** Approved, pending push

Jinja2 macro system on all 6 pages:
- Financial row (8 cards) + collapsible Actions row (8 cards)
- Sparklines on date-range pages (Dashboard/Campaigns/Ad Groups)
- Change % vs prior period on date-range pages
- Session-persisted collapse state (7 page IDs)
- IS metrics added to schema (4 new columns)
- Synthetic data to today (dynamic date.today())

Card layouts:
| Page | Financial (8) | Actions (8) |
|------|---------------|-------------|
| Dashboard/Campaigns/Ad Groups/Keywords | Cost\|Revenue\|ROAS\|Wasted Spend\|Conv\|CPA\|CVR\|blank | Impr\|Clicks\|CPC\|CTR\|Search IS\|Top IS\|Abs Top IS\|Click Share |
| Ads | Cost\|Revenue\|ROAS\|blank\|Conv\|CPA\|CVR\|blank | Impr\|Clicks\|CPC\|CTR\|Ad Strength\|blank x3 |
| Shopping (Campaigns) | Cost\|Conv Value\|ROAS\|blank\|Conv\|Cost/Conv\|CVR\|blank | Impr\|Clicks\|CPC\|CTR\|blank x4 |
| Shopping (Products) | Cost\|ROAS\|blank\|Out of Stock\|Conv\|blank x3 | Products\|Feed Issues\|blank x6 |

Invert colours (red when rising): Cost, Cost/Conv, Wasted Spend
Ad Strength: Actions row ONLY. Format: "240/983" label, "129 Poor" sub_label.
Shopping: Two independent macro calls (shopping_campaigns, shopping_products).

IS columns added: search_impression_share, search_top_impression_share, search_absolute_top_impression_share, click_share

Data types:
- Date-range (Dashboard/Campaigns/Ad Groups): change indicators + sparklines
- Windowed (Keywords/Ads/Shopping): dash indicators, no sparklines

Files modified (17): warehouse_duckdb.py, generate_synthetic_data_v2.py, base_bootstrap.html, macros/metrics_cards.html, shared.py, all 6 route files, all 6 template files

### Chat 25 — M4: Table Overhaul ✅
**Date:** 2026-02-21 | **Commit:** pending

Full Google Ads UI column sets across all 5 pages, server-side sort, sticky first column:

Column specs (locked — do not change without Master Chat approval):
| Page | Cols | Sticky |
|---|---|---|
| Campaigns | 24 | Campaign name |
| Ad Groups | 26 | Ad Group name |
| Keywords | 17 | Keyword |
| Ads | 24 | Ad (final_url) |
| Shopping | 24 | Campaign name |

### Chat 26 — M5: Card-Based Rules Tab ✅
**Date:** 2026-02-22 | **Commit:** 025986a

Replaced dense table-based Rules tab with fully interactive card-based UI on Campaigns page (pilot).

**Architecture — dual-layer (critical — do not break):**
- `act_autopilot/rules_config.json` — UI config layer (CRUD via rules_api.py)
- `act_autopilot/rules/*.py` — execution layer (untouched, Python functions only)
- These layers are intentionally separate. JSON edits never touch Python execution files.

**rules_config.json data model (18 fields per rule):**
```
rule_id, rule_type, rule_number, display_name, name
scope (blanket/specific), campaign_id
condition_metric, condition_operator, condition_value, condition_unit
condition_2_metric, condition_2_operator, condition_2_value, condition_2_unit
action_direction, action_magnitude, risk_level, cooldown_days, enabled
monitoring_days, monitoring_minutes
created_at, updated_at
```

**rules_api.py routes:**
| Route | Method | Purpose |
|---|---|---|
| `/api/rules` | GET | Return all rules |
| `/api/rules/add` | POST | Add rule |
| `/api/rules/<id>/update` | PUT | Edit rule |
| `/api/rules/<id>/toggle` | PUT | Toggle enabled |
| `/api/rules/<id>` | DELETE | Delete rule |
| `/api/campaigns-list` | GET | Campaign names from warehouse |

### Chat 27 — M6: Recommendations Engine + UI ✅
**Date:** 2026-02-22

- recommendations table in warehouse.duckdb (19 cols) + 22 historical rows seeded
- recommendations_engine.py: reads rules_config.json, evaluates campaign_features_daily, inserts pending recs
- Duplicate prevention on (campaign_id, rule_id)
- /recommendations/cards JSON endpoint for JS-rendered inline cards
- Global /recommendations page: Pending (48 cards) / Monitoring / History
- Campaigns → Recommendations tab: 2-col card grids

**Engine proxy column mappings:**
| Needed | Proxy |
|---|---|
| target_roas | Fallback 4.0 (column missing) |
| budget_micros | cost_micros_w7_mean |
| cost_spike_confidence | anomaly_cost_z >= 2.0 |
| pace_over_cap_detected | pacing_flag_over_105 |
| ctr_drop_detected | ctr_w7_vs_prev_pct < -20 |
| cvr_drop_detected | cvr_w7_vs_prev_pct < -20 |

**Card anatomy (locked):**
1. 4px coloured top bar (blue=budget, green=bid, red=status)
2. Header: rule tag + campaign name + status pill
3. Change block FIRST (gradient bg by type)
4. Trigger block SECOND (grey bg, "Why this triggered")
5. Footer: confidence badge + source pill + age
6. Action buttons: Modify / Decline / Accept

**Status pills:** Pending=blue / Monitoring=purple / Successful=green / Reverted=red / Declined=grey

### Chat 28 — M7: Accept/Decline/Modify Wiring + 4-Tab UI ✅
**Date:** 2026-02-22

- Accept / Decline / Modify POST routes — fully wired
- `changes` audit table created in warehouse.duckdb
- `monitoring_days: 0` added to all 13 rules in rules_config.json
- Card fade+slide animations, badge decrements, toast confirmations
- 4-tab UI: Pending / Monitoring / Successful / Declined
- Both /recommendations and /campaigns updated

**Architecture decisions:**
- recommendations.html: server-side Jinja passes all groups, JS shows/hides divs
- campaigns.html: JS fetch from /recommendations/cards (pre-existing pattern maintained)

### Chat 29 — M8: Changes + Radar Monitoring ✅
**Date:** 2026-02-23

**Files created:**
- `act_autopilot/radar.py` — background daemon thread (60s cycle), evaluates monitoring recs, auto-resolves to successful or reverted
- `act_dashboard/routes/changes.py` — new blueprint, /changes route

**Files modified:**
- `act_autopilot/rules_config.json` — added `monitoring_minutes` to all 13 rules
- `act_dashboard/routes/recommendations.py` — removed /changes, added reverted_recs, monitoring_minutes support, last_run fix
- `act_dashboard/routes/__init__.py` — registered changes blueprint
- `act_dashboard/templates/recommendations.html` — 5 tabs (added Reverted)
- `act_dashboard/templates/campaigns.html` — 5 inner tabs + 5 summary cards
- `act_dashboard/templates/changes.html` — full Bootstrap 5 rewrite

**Key technical decisions:**
- DuckDB connection pattern for Radar: `duckdb.connect('warehouse.duckdb')` + `ATTACH 'warehouse_readonly.duckdb' AS ro (READ_ONLY)`. **This is now the established pattern for any component needing both read and write access.**
- JOIN strategy for changes → recommendations: no recommendation_id FK exists — use `campaign_id + rule_id` with `QUALIFY ROW_NUMBER() OVER (PARTITION BY campaign_id, rule_id ORDER BY generated_at DESC) = 1`
- System Changes tab is currently a table (ro.analytics.change_log data) — will be converted to cards in a future chat
- Radar revert is DB-only in this chat — no Google Ads API rollback call yet

**executed_by values in changes table:**
| Value | Meaning |
|---|---|
| `user_accept` | User clicked Accept |
| `user_modify` | User modified value then accepted |
| `user_decline` | User clicked Decline |
| `radar_resolved` | Radar: monitoring complete, KPI held |
| `radar_revert` | Radar: KPI degraded, auto-reverted |

**monitoring_minutes:**
All 13 rules now have `monitoring_minutes`. When > 0, takes priority over `monitoring_days`. Default 0 = disabled, uses monitoring_days. Fast-test values: Budget 1→1min, Budget 2→2min, Bid 1→2min, all others→0.

**Test results:** 0 Pending / 1 Monitoring / 57 Successful / 4 Reverted / 8 Declined ✅ All pages confirmed ✅

---

## CURRENT STATUS

### Overall: ~97% Complete

What's working:
- All 6 dashboard pages with real/synthetic data
- Metrics cards: Financial + Actions on every page
- Performance chart: dual-axis, 4 toggleable metrics, session-persisted, all 6 pages
- Sparklines + change indicators on date-range pages
- Session-based date picker
- M5 card-based Rules tab on Campaigns page
- rules_config.json + rules_api.py CRUD
- M6 Recommendations Engine + global page + Campaigns tab
- M7 Accept/Decline/Modify action buttons — live POST routes
- M7 5-tab Recommendations UI on /recommendations + /campaigns (Pending/Monitoring/Successful/Reverted/Declined)
- M8 Radar background job — auto-resolves monitoring recommendations
- M8 Changes page — My Actions card grid + System Changes table
- M8 Reverted tab on both recommendation pages
- changes audit table in warehouse.duckdb
- Authentication + client switching
- Constitution execution engine
- M4 tables: full Google Ads column sets on all 5 pages
- Server-side sort on all sortable columns

Pending:
- M9 Search Terms / Keywords recommendations (Chat 30)
- System Changes tab → card grid (deferred from Chat 29)
- M5 Rules tab rollout to Ad Groups, Keywords, Ads, Shopping
- Live Google Ads API execution on accept/modify/revert routes
- Campaign scope pill name resolution
- All Conv. pipeline
- Shopping IS/Opt. Score (columns exist but NULL)
- Config YAML validation errors (pre-existing, non-blocking)

---

## FUTURE ROADMAP

Immediate (Dashboard 3.0):
- Chat 30: M9 Keywords Search Terms tab
- Future: System Changes tab → card grid

Short-term:
- Phase 3: Unit tests, job queue, DB indexes, CSRF
- Email Reports (SMTP)
- Smart Alerts (anomaly detection)

Medium-term:
- Keywords Enhancement
- Onboarding Wizard
- Documentation

---

## LESSONS LEARNED

1. Always extend base_bootstrap.html (never base.html)
2. Always use ro.analytics.* prefix for read queries
3. Request current file before editing — never cached
4. Route decorator quote style matters for string replacement
5. Shopping: compute_campaign_metrics() must include total_clicks
6. Session state > URL params for picker/collapse
7. Jinja2 macros: pilot-then-rollout pattern is efficient
8. Mandatory codebase upload saves hours in worker chats
9. Files in routes/ are 3 levels deep from project root — use `.parent.parent.parent`
10. `display:none` + `display:flex` in same inline style — browser uses last one; keep none, let JS add flex
11. Dual-layer architecture: JSON config (UI) and Python functions (execution) must remain separate
12. Campaign picker must be wired to real data before declaring campaign-specific scope complete
13. New /recommendations/cards JSON endpoint pattern — JS rendering of inline cards without page reload
14. recommendations table must live in writable warehouse.duckdb — never in readonly analytics DB
15. Engine proxy columns must be logged when used — do not silently substitute
16. Duplicate prevention: always check (campaign_id, rule_id) before insert
17. Verify actual DB column names before writing routes — brief column names may differ from schema
18. Tab switching approach depends on page: recommendations.html uses server-side Jinja + JS show/hide; campaigns.html uses JS fetch from /cards endpoint
19. Datetime fields from DuckDB can be Python datetime objects or ISO strings — use `| string | truncate(10, True, '')` in Jinja
20. NULL dates on old synthetic rows are expected — document clearly
21. DuckDB Radar connection pattern: open warehouse.duckdb as read-write + ATTACH warehouse_readonly.duckdb as ro. Never open with read_only=True if writes are needed. Never open same file twice with different configs.
22. changes table has no recommendation_id FK — JOIN to recommendations using campaign_id + rule_id + QUALIFY ROW_NUMBER()
23. System Changes tab from ro.analytics.change_log — will be empty in synthetic environment until Autopilot runs live

---

## KNOWN PITFALLS

| Problem | Fix |
|---------|-----|
| Template CSS missing | Must extend base_bootstrap.html, not base.html |
| DB query fails | Use ro.analytics.* not analytics.* |
| Route replacement fails | Match exact quote style of @bp.route decorator |
| Shopping metrics missing | Add total_clicks to compute_campaign_metrics() |
| Collapse state lost | POST to /set-metrics-collapse |
| Rules showing 0 | Use r'_\d{3}(?:_|$)' regex |
| Ad group table empty | Use cpc_bid_micros not bid_micros |
| Sort not working on full dataset | Must be SQL-side ORDER BY, not Python-side |
| New sort column not working | Must add to ALLOWED_*_SORT whitelist in route |
| Jinja template 500 error | Validate with jinja2 Environment before deploying |
| rules_config.json not found | Path needs `.parent.parent.parent` — routes/ is 3 levels from project root |
| Drawer visible on page load | Remove flex from inline style, let JS add it |
| Campaign picker empty | Fetch from `/api/campaigns-list` on scope card click |
| "budget budget" double word | Use explicit type→label map |
| Blueprint not registered | New blueprints MUST be added to __init__.py |
| Radar "ro catalog does not exist" | Must ATTACH warehouse_readonly.duckdb in radar connection |
| Radar read-write conflict | Never open warehouse.duckdb with read_only=True if writes needed |
| changes JOIN to recommendations | No recommendation_id — use campaign_id + rule_id + QUALIFY |

---

**Version:** 8.0 | **Last Updated:** 2026-02-23
**Next Step:** Chat 30 — M9 Search Terms / Keywords recommendations
