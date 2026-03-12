# Chat 89 Handoff — pytest 80%+ Coverage

**Date:** 2026-03-12
**Status:** COMPLETE — 80% coverage, 620 tests, 0 failures

---

## What to Know Going Forward

### Running Tests

```bash
# From project root, using the .venv python:
.venv/Scripts/python -m pytest tests/ -q
.venv/Scripts/python -m pytest tests/ --cov=act_dashboard --cov=act_autopilot --cov-report=term-missing -q
```

Note: use `.venv/Scripts/python` (not system `python`) — system python doesn't have Flask.

### Test Structure

```
tests/
├── conftest.py                      # Fixtures: app, client, db_conn
├── test_constitution.py             # Guardrails / safety rules
├── test_email_sender.py             # Email sender + DashboardConfig
├── test_recommendations_engine.py   # Rec generation + pure helpers
├── test_rule_helpers.py             # Rule metadata helpers (NEW Chat 89)
├── test_routes_ad_groups.py         # /ad-groups route + helpers
├── test_routes_ads.py               # /ads route + helpers
├── test_routes_campaigns.py         # /campaigns route + helpers
├── test_routes_changes.py           # /changes route + _enrich helpers
├── test_routes_keywords.py          # /keywords route + pure functions
├── test_routes_recommendations.py   # /recommendations route + pure helpers
├── test_routes_shopping.py          # /shopping route + helpers
└── test_shared.py                   # Shared helpers + API endpoints
```

### db_conn Fixture (conftest.py)

The `db_conn` fixture returns an in-memory DuckDB that has:
- An `ro` schema attached with all analytics tables (campaign_daily, ad_group_daily, ad_features_daily, product_features_daily, shopping_campaign_daily)
- A writable main DB schema with raw performance tables

CUSTOMER_ID used throughout tests: `"9999999999"` (matches conftest seed data).

### Coverage Gaps to Address Later

If coverage needs to go higher (85%+), the main targets are:
1. **keywords.py lines 887–1202** (~120 lines) — Performance Max / Smart Shopping loaders. Need `performance_max_daily` and `shopping_campaign_daily` windowed columns in conftest.
2. **shopping.py lines 374–488** (~115 lines) — Shopping route handler tabs. Need session-based tests for each tab.
3. **shopping.py lines 212–239** (~28 lines) — `load_products_from_features`. Need windowed columns (`impressions_w30_sum`, `clicks_w30_sum`, etc.) added to `product_features_daily` in conftest.

### Constraints

- Never modify source files — tests/ only
- Never connect to `warehouse.duckdb` or `warehouse_readonly.duckdb`
- Never make real SMTP/Google Ads API calls
