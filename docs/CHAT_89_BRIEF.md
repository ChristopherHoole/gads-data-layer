# CHAT 89: UNIT TESTS (pytest 80%+)

**Date:** 2026-03-12
**Estimated Time:** 8–12 hours
**Priority:** HIGH
**Dependencies:** Chat 88 complete (ad_daily table exists)

---

## CONTEXT

ACT dashboard is fully built across 6 pages, 41 rules, recommendations engine, email sender, and outreach system. No test suite exists. Unit tests are required before live deployment or client onboarding. The Rules & Recommendations overhaul is planned for later — ~30–40% of rule-specific tests may need updating after that, but everything else will carry over cleanly.

## OBJECTIVE

Write a pytest test suite achieving 80%+ coverage across routes, recommendations engine, rules engine, email sender, and constitution safety guardrails. No changes to existing code — new `tests/` folder only.

---

## BUILD PLAN

### Step 1 — Read the codebase before writing anything
Read ALL of the following before writing a single test:
- All files in `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\`
- `C:\Users\User\Desktop\gads-data-layer\act_autopilot\recommendations_engine.py`
- `C:\Users\User\Desktop\gads-data-layer\act_autopilot\rules_config.json`
- All files in `C:\Users\User\Desktop\gads-data-layer\act_autopilot\rules\`
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\email_sender.py`
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\outreach.py`
- Any constitution or safety guardrail file in `act_autopilot\`

Tests must match actual function signatures, column names, and route paths — no guessing.

### Step 2 — Create test infrastructure
Create `tests/conftest.py` with shared fixtures:
- Flask test client (app in test mode)
- In-memory DuckDB with all required tables seeded (campaign_daily, keyword_daily, ad_group_daily, ad_daily, shopping_daily, recommendations, changes, outreach_leads, outreach_emails)
- Seed data must be realistic enough to trigger rule conditions and generate recommendations
- Mock SMTP client (patches email_sender.send_email) — no real network calls
- Mock Google Ads API client — no real network calls

### Step 3 — Write route tests
Create one test file per entity page:
- `tests/test_routes_campaigns.py` — GET /campaigns returns 200, sort columns, date filter
- `tests/test_routes_keywords.py` — GET /keywords returns 200, search terms tab loads, sort/filter
- `tests/test_routes_ads.py` — GET /ads returns 200, ad_daily data present
- `tests/test_routes_ad_groups.py` — GET /ad-groups returns 200, cpc_bid_micros present
- `tests/test_routes_shopping.py` — GET /shopping returns 200, all 4 tabs load
- `tests/test_routes_recommendations.py` — GET /recommendations 200, Accept POST, Decline POST, entity type filter
- `tests/test_routes_changes.py` — GET /changes 200, all 5 tabs (Pending/Monitoring/Successful/Declined/Reverted)

### Step 4 — Write recommendations engine tests
Create `tests/test_recommendations_engine.py`:
- Engine generates recs for entities with known bad metrics in seeded data
- Duplicate prevention — no second pending rec for same (entity_id, rule_id)
- Entity type strings exactly match: 'campaign', 'keyword', 'ad_group', 'ad', 'shopping_product'
- Cooldown respected — no rec generated within 7 days of last change for same entity

### Step 5 — Write rules engine tests
Create `tests/test_rules_engine.py`:
- Each rule fires when threshold is breached (seeded data deliberately breaches each condition)
- Each rule does NOT fire when threshold is not breached
- rules_config.json loads without KeyError or schema error
- Rule evaluation returns expected action_type

### Step 6 — Write email sender tests
Create `tests/test_email_sender.py`:
- Variable substitution: {{first_name}}, {{company}}, {{sender_name}} replaced correctly
- Daily limit blocks send when limit reached, allows send when under limit
- HTML body conversion: \n correctly replaced with <br>
- MIMEText constructed with all 3 args (type "html" and "utf-8" both present)

### Step 7 — Write constitution / safety guardrail tests
Create `tests/test_constitution.py`:
- Budget change exceeding configured max % is blocked
- Bid change exceeding configured max % is blocked
- Change within 7-day cooldown period is blocked
- Change with insufficient data (below minimum threshold) is blocked
- Valid change within all limits passes all checks

### Step 8 — Run coverage report and hit 80%+
```bash
pip install pytest pytest-cov --break-system-packages
pytest --cov=act_dashboard --cov=act_autopilot --cov-report=term-missing
```
If below 80%, identify uncovered modules from the report and add targeted tests until threshold is met.

### Step 9 — Create handoff docs
- `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_89_HANDOFF.md`
- `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_89_SUMMARY.md`

---

## DELIVERABLES

1. `C:\Users\User\Desktop\gads-data-layer\tests\conftest.py` — CREATE
2. `C:\Users\User\Desktop\gads-data-layer\tests\test_routes_campaigns.py` — CREATE
3. `C:\Users\User\Desktop\gads-data-layer\tests\test_routes_keywords.py` — CREATE
4. `C:\Users\User\Desktop\gads-data-layer\tests\test_routes_ads.py` — CREATE
5. `C:\Users\User\Desktop\gads-data-layer\tests\test_routes_ad_groups.py` — CREATE
6. `C:\Users\User\Desktop\gads-data-layer\tests\test_routes_shopping.py` — CREATE
7. `C:\Users\User\Desktop\gads-data-layer\tests\test_routes_recommendations.py` — CREATE
8. `C:\Users\User\Desktop\gads-data-layer\tests\test_routes_changes.py` — CREATE
9. `C:\Users\User\Desktop\gads-data-layer\tests\test_recommendations_engine.py` — CREATE
10. `C:\Users\User\Desktop\gads-data-layer\tests\test_rules_engine.py` — CREATE
11. `C:\Users\User\Desktop\gads-data-layer\tests\test_email_sender.py` — CREATE
12. `C:\Users\User\Desktop\gads-data-layer\tests\test_constitution.py` — CREATE
13. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_89_HANDOFF.md` — CREATE
14. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_89_SUMMARY.md` — CREATE

---

## CONSTRAINTS

- NEVER modify any existing source files — new files in tests/ only
- NEVER connect to warehouse.duckdb or warehouse_readonly.duckdb in tests
- NEVER make real SMTP or Google Ads API calls in tests
- Use pytest fixtures, not unittest classes
- All full Windows paths — never partial paths

---

## SUCCESS CRITERIA

- [ ] `pytest tests/ -v` runs with zero errors and zero failures
- [ ] Coverage report shows 80%+ across act_dashboard and act_autopilot
- [ ] No real network calls made during test run
- [ ] No modifications to any existing source files
- [ ] Flask starts cleanly after tests complete
- [ ] `docs/CHAT_89_HANDOFF.md` and `docs/CHAT_89_SUMMARY.md` created

---

## REFERENCE FILES

- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\` — All route files
- `C:\Users\User\Desktop\gads-data-layer\act_autopilot\recommendations_engine.py` — Rec generation logic
- `C:\Users\User\Desktop\gads-data-layer\act_autopilot\rules\` — All rule files
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\email_sender.py` — Email sending logic
- `C:\Users\User\Desktop\gads-data-layer\tools\seed_ad_daily.py` — Example seed pattern

---

## TESTING

1. Run `pip install pytest pytest-cov --break-system-packages` — confirm installed
2. Run `pytest tests/ -v` — confirm zero failures
3. Run `pytest --cov=act_dashboard --cov=act_autopilot --cov-report=term-missing` — report exact coverage %
4. If below 80%, add tests and re-run until threshold met
5. Start Flask — confirm starts cleanly
6. Report final coverage % and total test count
