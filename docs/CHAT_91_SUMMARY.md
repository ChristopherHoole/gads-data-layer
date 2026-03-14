# Chat 91 Summary — Campaign Rules & Flags

## What changed

Replaced the old `rules_config.json`-backed rules system (41 static rules) with a fully database-backed Campaign Rules & Flags system. Users can now view, toggle, delete, and create rules and flags directly in the dashboard UI.

## Deliverables

| # | Deliverable | Status |
|---|---|---|
| 1 | `tools/migrate_rules_schema.py` | Done |
| 2 | `tools/seed_campaign_rules.py` | Done — 54 rows seeded |
| 3 | `act_dashboard/routes/campaigns.py` — 5 API endpoints | Done |
| 4 | `act_dashboard/app.py` — CSRF exemptions | Done |
| 5 | `act_dashboard/templates/components/rules_flags_tab.html` | Done |
| 6 | `act_dashboard/templates/components/rules_flow_builder.html` | Done |
| 7 | `act_dashboard/templates/campaigns.html` — 4 edits | Done |
| 8 | `act_dashboard/static/css/rules.css` | Done |
| 9 | `docs/CHAT_91_HANDOFF.md` | Done |
| 10 | `docs/CHAT_91_SUMMARY.md` | Done |

## Seed data

54 rows for `client_christopher_hoole`: 24 rules (budget/bid/status) + 30 flags (performance/anomaly/technical).

## What is NOT built yet

The rule **evaluation engine** (the background worker that reads rules, evaluates them against live campaign metrics, and writes to `rule_evaluation_log` + `recommendations`) is a future deliverable.
