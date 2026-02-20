# MASTER KNOWLEDGE BASE - ADS CONTROL TOWER (A.C.T)

**Version:** 3.0  
**Created:** 2026-02-19  
**Updated:** 2026-02-20  
**Purpose:** Complete project context for Master Chat coordination

---

## EXECUTIVE SUMMARY

### Current State (Feb 20, 2026)
- **Overall Completion:** ~85%
- **Phase:** Dashboard 3.0 — M2 complete ✅, M3 (Chart Overhauls) NEXT
- **Active Development:** Dashboard 3.0 modular improvements

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

## SYSTEM ARCHITECTURE

### Directory Structure
```
gads-data-layer/
├── act_dashboard/
│   ├── app.py
│   ├── warehouse_duckdb.py
│   ├── routes/
│   │   ├── shared.py          (get_metrics_collapsed, get_date_range)
│   │   ├── dashboard.py
│   │   ├── campaigns.py
│   │   ├── ad_groups.py
│   │   ├── keywords.py
│   │   ├── ads.py
│   │   └── shopping.py
│   └── templates/
│       ├── base_bootstrap.html     ← ALWAYS USE THIS (never base.html)
│       ├── macros/
│       │   └── metrics_cards.html  ← M2 macro
│       └── components/
│           ├── rules_sidebar.html
│           ├── rules_tab.html
│           └── rules_card.html
├── src/act_autopilot/
│   ├── executor.py
│   └── constitution.py
├── warehouse.duckdb
└── generate_synthetic_data_v2.py
```

### Customer IDs
- Real: 7372844356
- Synthetic test: 9999999999

---

## DATABASE SCHEMA

CRITICAL: Always use ro.analytics.* prefix in dashboard queries.

### analytics.campaign_daily
snapshot_date, customer_id, campaign_id, campaign_name, campaign_type, status,
budget_micros, target_cpa_micros, target_roas, clicks, impressions, cost_micros,
conversions, conversions_value, rolling windows (w7/w14/w30/w90)
+ IS columns (added Chat 23): search_impression_share, search_top_impression_share,
  search_absolute_top_impression_share, click_share

### analytics.keyword_daily
keyword_text, match_type, max_cpc_micros, quality_score (1-10),
quality_score_landing_page, quality_score_ad_relevance, quality_score_expected_ctr

### analytics.ad_daily
ad_type, ad_strength (POOR/AVERAGE/GOOD/EXCELLENT), headlines_count, final_url

### analytics.ad_group_daily
ad_group_name, campaign_name, cpc_bid_micros, target_cpa_micros

### analytics.shopping_campaign_daily, product_features_daily (76 features), feed_quality_daily
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
| M3: Chart Overhauls | 24 | 📋 NEXT |
| M4: Table Improvements | 25 | 📋 PLANNED |
| M5: Rules Panel Upgrades | 26 | 📋 PLANNED |
| M6: Action Buttons | 27 | 📋 PLANNED |

---

## COMMON PROBLEMS & SOLUTIONS

| Problem | Fix |
|---------|-----|
| Template CSS missing | Must extend base_bootstrap.html, not base.html |
| DB query fails | Use ro.analytics.* not analytics.* |
| Route replacement fails | Match exact quote style of @bp.route decorator |
| Shopping metrics missing | Add total_clicks to compute_campaign_metrics() |
| Ad Strength in wrong row | Actions row ONLY |
| Collapse state lost | POST to /set-metrics-collapse |
| Rules showing 0 | Use r'_\d{3}(?:_|$)' regex |
| Ad group table empty | Use cpc_bid_micros not bid_micros |

---

## CURRENT STATUS

### Overall: ~85% Complete

What's working:
- All 6 dashboard pages with real/synthetic data
- Metrics cards: Financial + Actions on every page
- Sparklines + change indicators on date-range pages
- IS metrics in Actions row
- Ad Strength on Ads page
- Shopping: two independent metric sections
- Session-based date picker
- Rules visibility system
- Authentication + client switching
- Constitution execution engine

Pending:
- Chat 23 git commit (approved, 17 files)
- Ads Revenue fix (future chat)
- 404.html (future chat)
- Chat 15 deferred work (executor compatibility)

---

## FUTURE ROADMAP

Immediate (Dashboard 3.0):
- Chat 24: M3 Chart Overhauls
- Chat 25: M4 Table Improvements
- Chat 26: M5 Rules Panel
- Chat 27: M6 Action Buttons

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

---

**Version:** 3.0 | **Last Updated:** 2026-02-20  
**Next Step:** Chat 24 — M3 Chart Overhauls
