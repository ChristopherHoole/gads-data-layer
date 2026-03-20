# CHAT 105: Unit Tests Update - Iterative Fixing

**Date:** 2026-03-19
**Estimated Time:** 1-2 hours
**Priority:** HIGH
**Dependencies:** Chat 104 complete (rule changes)

---

## CONTEXT

Unit tests (620 tests, 80% coverage) were written in Chat 89 before several major changes: flags system (Chat 101), templates system (Chat 93), and campaign rules changes (Chat 104). This is an ITERATIVE fix session - Master Chat will run test files one by one, report failures, and Claude Code will fix them in sequence until all 13 test files pass.

---

## OBJECTIVE

Fix all failing unit tests across 13 test files through iterative testing and fixing.

---

## WORKFLOW (ITERATIVE)

**This is NOT a one-shot fix.** This is a collaborative iterative process:

1. Master Chat runs a test file (e.g., `pytest tests/test_X.py -v`)
2. Master Chat reports failures to Claude Code
3. Claude Code fixes those specific failures
4. Master Chat re-runs to verify
5. Move to next test file
6. Repeat until all 13 files pass

**Claude Code should:**
- Wait for Master Chat to report failures
- Fix only what's reported
- Explain each fix clearly
- Confirm when ready for next test run

---

## TEST FILES (13 total)

**Core Engine:**
1. test_recommendations_engine.py ← START HERE
2. test_rules_engine.py
3. test_constitution.py
4. test_rule_helpers.py

**Routes:**
5. test_routes_campaigns.py
6. test_routes_recommendations.py
7. test_routes_keywords.py
8. test_routes_ads.py
9. test_routes_ad_groups.py
10. test_routes_shopping.py
11. test_routes_changes.py
12. test_shared.py

**Other:**
13. test_email_sender.py

---

## FIRST FAILURES (test_recommendations_engine.py)

**2 failures out of 83 tests:**

**Failure 1:** `test_generates_recommendation_when_condition_met`
```
[ENGINE] ERROR querying DB campaign rules: Invalid Input Error: Need a DataFrame with at least one column
[FLAGS ENGINE] ERROR querying flag rules: Catalog Error: Table with name rules does not exist!
```

**Failure 2:** `test_skips_no_table_entities`
- Same error: rules table doesn't exist in test fixtures

**Root cause:** Test fixtures created before rules moved to database (Chat 91). Tests use old rules_config.json approach.

**Fix required:**
- Update test fixtures to create `rules` table
- Insert test rules that should fire
- Handle flags engine gracefully when rules table missing

---

## REQUIREMENTS

### Technical
- Fix test fixtures, not engine code (engine works correctly)
- All fixes must maintain 80%+ coverage
- Tests must be isolated (no shared state between tests)
- Use pytest fixtures for database setup

### Changes from Chat 104
- 4 rules deleted (4, 5, 10, 15)
- 5 rules updated (7, 11, 20, 23, 24)
- Any tests referencing these need updating

### Changes from Chat 101
- Flags system added (30 flags)
- Flags engine runs after main engine
- Tests need flags table + flag rules

### Changes from Chat 93
- Templates system added (is_template flag)
- Tests need to handle template filtering

---

## SUCCESS CRITERIA

- [ ] All 13 test files pass (0 failures)
- [ ] Coverage remains 80%+
- [ ] No broken fixtures
- [ ] All tests run in isolation

---

## REFERENCE FILES

- `C:\Users\User\Desktop\gads-data-layer\tests\` — All test files
- `C:\Users\User\Desktop\gads-data-layer\act_autopilot\recommendations_engine.py` — Engine logic
- `C:\Users\User\Desktop\gads-data-layer\warehouse.duckdb` — Current DB schema

---

## TESTING LOOP

**Master Chat will run:**
```powershell
pytest tests/test_FILE.py -v
```

**Report format to Claude Code:**
"File X: Y failures - [list specific test names and errors]"

**Claude Code fixes, then Master Chat re-runs to verify.**

---

**Brief Version:** 1.0
**Template Version:** 5.0
**Status:** ITERATIVE - waiting for first failure report from Master Chat
