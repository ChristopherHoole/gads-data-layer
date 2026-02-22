# MASTER KNOWLEDGE BASE - ADS CONTROL TOWER (A.C.T)

**Version:** 5.0  
**Created:** 2026-02-19  
**Updated:** 2026-02-22  
**Purpose:** Complete project context for Master Chat coordination

---

## EXECUTIVE SUMMARY

### Current State (Feb 22, 2026)
- **Overall Completion:** ~92%
- **Phase:** Dashboard 3.0 — M5 complete ✅, M6 Recommendations Tab NEXT
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
| Dashboard/Campaigns/Ad Groups/Keywords | Cost|Revenue|ROAS|Wasted Spend|Conv|CPA|CVR|blank | Impr|Clicks|CPC|CTR|Search IS|Top IS|Abs Top IS|Click Share |
| Ads | Cost|Revenue|ROAS|blank|Conv|CPA|CVR|blank | Impr|Clicks|CPC|CTR|Ad Strength|blank x3 |
| Shopping (Campaigns) | Cost|Conv Value|ROAS|blank|Conv|Cost/Conv|CVR|blank | Impr|Clicks|CPC|CTR|blank x4 |
| Shopping (Products) | Cost|ROAS|blank|Out of Stock|Conv|blank x3 | Products|Feed Issues|blank x6 |

Invert colours (red when rising): Cost, Cost/Conv, Wasted Spend
Ad Strength: Actions row ONLY. Format: "240/983" label, "129 Poor" sub_label.
Shopping: Two independent macro calls (shopping_campaigns, shopping_products).

IS columns added: search_impression_share, search_top_impression_share, search_absolute_top_impression_share, click_share

Data types:
- Date-range (Dashboard/Campaigns/Ad Groups): change indicators + sparklines
- Windowed (Keywords/Ads/Shopping): dash indicators, no sparklines

Files modified (17): warehouse_duckdb.py, generate_synthetic_data_v2.py, base_bootstrap.html, macros/metrics_cards.html, shared.py, all 6 route files, all 6 template files

Known issues (non-blocking):
- Ads Revenue $0.00 — ads-level revenue not aggregated
- 404.html missing — pre-existing

Pending git commit message:
  feat(dashboard): M2 metrics cards rollout - all 6 pages complete
  Chat-23 | Module-M2 | Status: COMPLETE

---

### Chat 26 — M5: Card-Based Rules Tab ✅
**Date:** 2026-02-22 | **Commit:** pending

Replaced dense table-based Rules tab with fully interactive card-based UI on Campaigns page (pilot):

**Architecture — dual-layer (critical — do not break):**
- `act_autopilot/rules_config.json` — UI config layer (CRUD via rules_api.py)
- `act_autopilot/rules/*.py` — execution layer (untouched, Python functions only)
- These layers are intentionally separate. JSON edits never touch Python execution files.

**UI:**
- Card grid (auto-fill, min 340px) per rule type section (Budget / Bid / Status)
- 4px colour-coded top bar: blue=budget, green=bid, red=status
- Rule naming: "Budget 1" / "Bid 1" / "Status 1" (not BUDGET-001)
- Condition block (IF/AND highlighted values) + Action block (gradient, icon, description)
- Campaign-specific cards: blue border + OVERRIDES BLANKET tag
- Toggle switches persist to JSON
- Slide-in drawer (480px): 5-step form (Type→Scope→Condition→Action→Settings) + live preview
- Campaign picker: fetches live from `/api/campaigns-list` → `ro.analytics.campaign_daily`
- Filter bar: All / Budget / Bid / Status / Blanket only / Campaign-specific only / Active only
- Recommendations placeholder tab (Chat 27 scope)
- Inline SVG only — NO Bootstrap Icons CDN

**rules_config.json data model (18 fields per rule):**
```
rule_id, rule_type, rule_number, display_name, name
scope (blanket/specific), campaign_id
condition_metric, condition_operator, condition_value, condition_unit
condition_2_metric, condition_2_operator, condition_2_value, condition_2_unit
action_direction, action_magnitude, risk_level, cooldown_days, enabled
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

**Files created/modified:**
- `act_autopilot/rules_config.json` — CREATED (13 rules seeded from docstrings)
- `act_dashboard/routes/rules_api.py` — CREATED
- `act_dashboard/routes/__init__.py` — MODIFIED
- `act_dashboard/routes/campaigns.py` — MODIFIED (imports load_rules(), passes rules_config)
- `act_dashboard/templates/campaigns.html` — MODIFIED (3-tab: Campaigns/Rules/Recommendations)
- `act_dashboard/templates/components/rules_tab.html` — REPLACED

**Bugs fixed:**
- "budget budget" double word — explicit type→label map: `{budget:'daily budget', bid:'bid target', status:'campaign status'}`
- Drawer visible on page load — `display:none` + `display:flex` conflict; removed flex from inline style
- rules_config.json path — `.parent.parent.parent` needed (routes/ is 3 levels from project root)
- Campaign picker empty — wired to `/api/campaigns-list` fetch on scope card click

**Known states (not bugs):**
- Scope pill shows campaign_id not name — name resolution is Chat 27 scope
- Rule numbering gaps after deletes — cosmetic, rule_id is the true identifier

---

### Chat 25 — M4: Table Overhaul ✅
**Date:** 2026-02-21 | **Commit:** pending

Full Google Ads UI column sets across all 5 pages, server-side sort, sticky first column:
- Campaigns: 24 cols (unchanged, reference standard)
- Ad Groups: 26 cols — `ro.analytics.ad_group_daily`
- Keywords: 17 cols — `ro.analytics.keyword_features_daily` (windowed), match type pill inside keyword col
- Ads: 24 cols — `ro.analytics.ad_features_daily` (30d windowed), ad strength progress bar
- Shopping: 24 cols — migrated from `raw_shopping_campaign_daily` to `ro.analytics.shopping_campaign_daily`

Sort pattern: URL params (sort_by/sort_dir) → ALLOWED_*_SORT whitelist → SQL ORDER BY + LIMIT/OFFSET
Sticky: CSS `position:sticky` on first th/td, no JS library

Database state post-Chat 25:
| Table | Rows | Cols |
|---|---|---|
| analytics.campaign_daily | 7,300 | 21 |
| analytics.ad_group_daily | 23,725 | 30 |
| analytics.keyword_daily | 77,368 | 33 |
| analytics.ad_features_daily | 983 | 51 |
| analytics.shopping_campaign_daily | 7,300 | 26 |

New file: `tools/testing/generate_synthetic_shopping_v2.py`

Key lessons:
- Generators live in `tools/testing/` not `scripts/`
- Always validate Jinja syntax before deploying: `python3 -c "from jinja2 import Environment, FileSystemLoader; env = Environment(loader=FileSystemLoader('.')); env.get_template('template.html'); print('OK')"`
- Column specs vary per page — never assume Campaigns spec applies everywhere

Known expected states (not bugs):
- All Conv. columns show `—` — all_conversions pipeline not yet built
- Shopping IS/Opt. Score/Click Share show `—` — NULL in SQL, pending real data

---

### Chat 24 — M3: Chart Overhaul ✅
**Date:** 2026-02-20 | **Commit:** Pending

Reusable `performance_chart.html` Jinja2 macro on all 6 pages:
- Dual Y-axis: Y1 left ($) = Cost + Avg CPC; Y2 right (count) = Impressions + Clicks
- Each axis auto-hides when all its metrics are inactive
- 4 toggleable slots: click to show/hide line (Google Ads style)
- Default active: Cost + Clicks
- Session key: `chart_metrics_<page_id>` | POST /set-chart-metrics (no reload)
- Empty state shown when 0 metrics active
- Dashboard: replaced legacy Performance Trend chart
- Shopping: Campaigns tab only
- Keywords + Ads: account-level campaign_daily (no per-entity daily table)

Data sources:
| Page | Table |
|------|-------|
| Dashboard | analytics.campaign_daily (no ro. prefix) |
| Campaigns | ro.analytics.campaign_daily |
| Ad Groups | ro.analytics.ad_group_daily |
| Keywords | ro.analytics.campaign_daily (account proxy) |
| Ads | ro.analytics.campaign_daily (account proxy) |
| Shopping | ro.analytics.campaign_daily (account proxy) |

Files modified (10): shared.py + 6 routes + dashboard_new.html + ad_groups.html + keywords_new.html + ads_new.html + shopping_new.html
New file: macros/performance_chart.html

**Critical lesson:** Helper functions MUST be placed BEFORE @bp.route decorator. Inserting between decorator and def registers the helper as the route handler (silent Flask bug).

---

## SYSTEM ARCHITECTURE

### Directory Structure
```
gads-data-layer/
├── act_autopilot/
│   ├── rules/                     ← execution layer (Python, never touched by UI)
│   │   └── *.py
│   └── rules_config.json          ← UI config layer (M5, Chat 26)
├── act_dashboard/
│   ├── app.py
│   ├── warehouse_duckdb.py
│   ├── routes/
│   │   ├── shared.py
│   │   ├── dashboard.py
│   │   ├── campaigns.py
│   │   ├── ad_groups.py
│   │   ├── keywords.py
│   │   ├── ads.py
│   │   ├── shopping.py
│   │   └── rules_api.py           ← CRUD + /api/campaigns-list (M5, Chat 26)
│   └── templates/
│       ├── base_bootstrap.html     ← ALWAYS USE THIS (never base.html)
│       ├── macros/
│       │   ├── metrics_cards.html  ← M2 macro
│       │   └── performance_chart.html ← M3 macro
│       └── components/
│           ├── rules_sidebar.html
│           ├── rules_tab.html      ← REPLACED Chat 26 (M5 card UI)
│           └── rules_card.html
├── warehouse.duckdb
└── tools/testing/
    └── generate_synthetic_*.py
```

### Customer IDs
- Real: 7372844356
- Synthetic test: 9999999999

---

## DATABASE SCHEMA

CRITICAL: Always use ro.analytics.* prefix in dashboard queries.

### analytics.campaign_daily (7,300 rows, 21 cols)
snapshot_date, customer_id, campaign_id, campaign_name, campaign_type, status,
budget_micros, target_cpa_micros, target_roas, clicks, impressions, cost_micros,
conversions, conversions_value, rolling windows (w7/w14/w30/w90)
+ IS columns (added Chat 23): search_impression_share, search_top_impression_share,
  search_absolute_top_impression_share, click_share
+ M4 columns (added Chat 25): optimization_score, bid_strategy_type

### analytics.ad_group_daily (23,725 rows, 30 cols)
ad_group_name, campaign_name, cpc_bid_micros, target_cpa_micros
+ IS columns (added Chat 23): search_impression_share, search_top_impression_share,
  search_absolute_top_impression_share, click_share
+ M4 columns (added Chat 25): ad_group_type, all_conversions, all_conversions_value,
  optimization_score, bid_strategy_type
NOTE: ad_group_daily is a VIEW over snap_ad_group_daily

### analytics.keyword_daily (77,368 rows, 33 cols)
keyword_text, match_type, max_cpc_micros, quality_score (1-10),
quality_score_landing_page, quality_score_creative (= Exp. CTR),
quality_score_relevance (= Ad relevance)
+ M4 columns (added Chat 25): all_conversions_value, bid_strategy_type, final_url
NOTE: Routes use keyword_features_daily (windowed) not keyword_daily (raw)

### analytics.ad_features_daily (983 rows, 51 cols)
ad_type, ad_strength (POOR/AVERAGE/GOOD/EXCELLENT), headlines_count, final_url
campaign_name, ad_group_name (already in table — no JOINs needed)
Windowed 30d: impressions_30d, clicks_30d, cost_micros_30d, conversions_30d,
  conversions_value_30d, ctr_30d, cvr_30d, cpa_30d, roas_30d
+ M4 columns (added Chat 25): all_conversions_30d, all_conversions_value_30d
NOTE: Table is ad_features_daily — ad_daily does NOT exist

### analytics.shopping_campaign_daily (7,300 rows, 26 cols)
Full shopping campaign data — M4 generator built from scratch
+ M4 columns (added Chat 25): campaign_status, channel_type, all_conversions,
  all_conversions_value, search_impression_share, search_top_impression_share,
  search_absolute_top_impression_share, click_share, optimization_score, bid_strategy_type

### analytics.change_log — audit trail

---

## HOW THINGS WORK

### Start Dashboard
```powershell
cd C:\Users\User\Desktop\gads-data-layer
.\.venv\Scripts\Activate.ps1
python -m act_dashboard.app configs/client_synthetic.yaml
```

### M1 Date Flow
User picks date → Flatpickr → POST /set-date-range → session → get_date_range() → SQL

### M2 Metrics Cards Flow
Route queries DB → builds card dicts → get_metrics_collapsed(page_id) → render_template
Template: {{ metrics_section(financial_cards, actions_cards, 'page_id', metrics_collapsed) }}
Toggle → POST /set-metrics-collapse → session updated

### Card Dict Format
```python
{
    'label': 'Cost',
    'value_display': '$199.9k',
    'change_pct': -1.5,        # None = '—'
    'sparkline_data': [1,2,3], # None = no chart
    'format_type': 'currency', # currency|number|percent|roas|ad_strength
    'invert_colours': True,    # red when rising
    'card_type': 'financial',
    'sub_label': None,
}
```

### Constitution Gates
- Min 10 conversions (30d) for bid changes
- Max 30% budget increase, 20% bid change
- 7-day cooldown between changes on same entity
- Protected entities: brand campaigns immutable by default

---

## RULES ENGINE

Rule categories: Budget (4), Bid/Target (6), Campaign Status (2), Keyword (8), Ad (3), Shopping (14)
Total: 30+ rules

Rule detection regex: r'_\d{3}(?:_|$)'
Supports: budget_001_increase AND kw_pause_001

Rule Visibility System (Chat 21c — reusable on all pages):
- rule_helpers.py: extract + categorize rules
- rules_sidebar.html, rules_tab.html, rules_card.html
- Auto-detects: BUDGET/BID/STATUS/KEYWORD/AD/SHOPPING categories

---

## DASHBOARD 3.0 MODULE STATUS

| Module | Chat | Status |
|--------|------|--------|
| M1: Date Range Picker | 22 | ✅ COMPLETE |
| M2: Metrics Cards | 23 | ✅ COMPLETE |
| M3: Chart Overhauls | 24 | ✅ COMPLETE |
| M4: Table Overhaul | 25 | ✅ COMPLETE |
| M5: Rules Tab (Campaigns pilot) | 26 | ✅ COMPLETE |
| M6: Recommendations Tab | 27 | 🚧 NEXT |

---

## COMMON PROBLEMS & SOLUTIONS

| Problem | Fix |
|---------|-----|
| Template CSS missing | Must extend base_bootstrap.html, not base.html |
| DB query fails | Use ro.analytics.* not analytics.* |
| Route replacement fails | Match exact quote style of @bp.route decorator |
| Shopping metrics missing | Add total_clicks to compute_campaign_metrics() |
| Ad Strength in wrong row | Actions row ONLY (M2 cards) |
| Collapse state lost | POST to /set-metrics-collapse |
| Rules showing 0 | Use r'_\d{3}(?:_|$)' regex |
| Ad group table empty | Use cpc_bid_micros not bid_micros |
| Generator scripts not found | They are in tools/testing/ — not scripts/ |
| Sort not working on full dataset | Must be SQL-side ORDER BY, not Python-side |
| New sort column not working | Must add to ALLOWED_*_SORT whitelist in route |
| Jinja template 500 error | Validate: `python3 -c "from jinja2 import Environment, FileSystemLoader; env = Environment(loader=FileSystemLoader('.')); env.get_template('template.html'); print('OK')"` |
| ad_daily table not found | Does not exist — use ad_features_daily |
| Shopping data empty | Check compute_campaign_metrics() key names match schema |
| rules_config.json not found | Path needs `.parent.parent.parent` — routes/ is 3 levels from project root |
| Drawer visible on page load | `display:none` + `display:flex` in same inline style — remove flex, let JS add it |
| Campaign picker empty | Fetch from `/api/campaigns-list` on scope card click — not static HTML |
| "budget budget" double word | Use explicit type→label map: `{budget:'daily budget', bid:'bid target', status:'campaign status'}` |

---

## CURRENT STATUS

### Overall: ~92% Complete

What's working:
- All 6 dashboard pages with real/synthetic data
- Metrics cards: Financial + Actions on every page
- Performance chart: dual-axis, 4 toggleable metrics, session-persisted, all 6 pages
- Sparklines + change indicators on date-range pages
- IS metrics in Actions row
- Ad Strength on Ads page
- Shopping: two independent metric sections
- Session-based date picker
- Rules visibility system (legacy sidebar/tab/card components)
- **M5 card-based Rules tab on Campaigns page** (Chat 26)
- **rules_config.json + rules_api.py CRUD** (Chat 26)
- Authentication + client switching
- Constitution execution engine
- M4 tables: full Google Ads column sets on all 5 pages
- Server-side sort on all sortable columns
- CSS sticky first column on all pages
- Status filter + per-page controls standardised

Pending:
- M6 Recommendations tab (Chat 27)
- M5 Rules tab rollout to Ad Groups, Keywords, Ads, Shopping (future chat)
- Campaign scope pill name resolution (Chat 27)
- All Conv. pipeline (populating all_conversions across all tables)
- Shopping IS/Opt. Score (columns exist but NULL)
- Ads Revenue fix (future chat)
- 404.html template missing (pre-existing)

---

## FUTURE ROADMAP

Immediate (Dashboard 3.0):
- Chat 27: M6 Recommendations Tab
- Chat 28: M6 rollout to remaining pages
- Chat 29: M7 Change History + Monitoring (merged screen)
- Chat 30: Keywords Search Terms tab

Short-term:
- Phase 5: Unit tests, job queue, DB indexes, CSRF
- Email Reports (SMTP)
- Smart Alerts (anomaly detection)

Medium-term:
- Keywords Enhancement
- Onboarding Wizard
- Documentation

---

## LESSONS LEARNED

1. Always extend base_bootstrap.html (never base.html)
2. Always use ro.analytics.* prefix
3. Request current file before editing — never cached
4. Route decorator quote style matters for string replacement
5. Shopping: compute_campaign_metrics() must include total_clicks
6. Session state > URL params for picker/collapse
7. Jinja2 macros: pilot-then-rollout pattern is efficient
8. Mandatory codebase upload saves hours in worker chats
9. Files in routes/ are 3 levels deep from project root — use `.parent.parent.parent`
10. `display:none` + `display:flex` in same inline style — browser uses last one; keep none, let JS add flex
11. Dual-layer architecture: JSON config (UI) and Python functions (execution) must remain separate — never sync them
12. Campaign picker must be wired to real data before declaring campaign-specific scope complete

---

**Version:** 5.0 | **Last Updated:** 2026-02-22  
**Next Step:** Chat 27 — M6 Recommendations Tab (discuss with Master Chat first)
