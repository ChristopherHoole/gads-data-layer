# Autopilot Rule Catalog (v0)

**Module:** `act_autopilot/`
**Total rules:** 16
**Date:** 2026-02-12

---

## Rule Summary Table

| Rule ID    | Name                                    | Category | Risk | Action Type         | Trigger                                       |
|------------|----------------------------------------|----------|------|---------------------|-----------------------------------------------|
| BUDGET-001 | Increase Budget — High ROAS            | Budget   | low  | budget_increase     | ROAS (7d) > target×1.15 + clicks≥30          |
| BUDGET-002 | Decrease Budget — Low ROAS             | Budget   | low  | budget_decrease     | ROAS (7d) < target×0.75 + conv≥15            |
| BUDGET-003 | Emergency Budget Cut — Cost Spike      | Budget   | med  | budget_decrease     | Lighthouse COST_SPIKE + conf≥0.6             |
| BUDGET-004 | Recovery Budget Increase — Cost Drop   | Budget   | low  | budget_increase     | Lighthouse COST_DROP + ROAS ≥ target         |
| BUDGET-005 | Pacing Reduction — Monthly Cap at Risk | Budget   | high | pacing_cut          | Lighthouse PACE_OVER_CAP (highest-cost camp) |
| BUDGET-006 | Hold Budget — Volatile Campaign        | Budget   | low  | budget_hold         | Lighthouse VOLATILE + conf≥0.5               |
| BID-001    | Tighten tROAS — Beating Goal           | Bid      | med  | bid_target_increase | ROAS (30d) > target×1.25 + conv≥15 + stable |
| BID-002    | Loosen tROAS — Missing Goal            | Bid      | med  | bid_target_decrease | ROAS (30d) < target×0.85 + conv≥15 + stable |
| BID-003    | Hold Bid — CVR Drop Investigation      | Bid      | med  | bid_hold            | Lighthouse CVR_DROP                          |
| BID-004    | Hold Bid — Low Data                    | Bid      | low  | bid_hold            | Lighthouse LOW_DATA or conv<15               |
| ACCT-001   | Monthly Pacing Alert                   | Account  | med  | review              | Pacing 100-105% of monthly cap               |
| ACCT-002   | Portfolio Rebalance Suggestion         | Account  | med  | review              | Best ROAS > 2× worst ROAS (≥2 eligible)     |
| ACCT-003   | Account-Wide Low Data Warning          | Account  | low  | review              | >50% campaigns have low_data_flag            |
| STATUS-001 | Flag Underperformer for Review         | Status   | high | review              | ROAS (30d) < target×0.50 + conv≥15          |
| STATUS-002 | CTR Crisis — Creative Review           | Status   | med  | review              | Lighthouse CTR_DROP + absolute CTR <1%       |
| STATUS-003 | Healthy Campaign — No Action           | Status   | low  | no_action           | No diagnoses + ROAS ±15% of target + data OK |

---

## Rule Categories

### Budget Rules (6)
| Priority | Rule ID    | When it fires                              | What it does              |
|----------|------------|-------------------------------------------|---------------------------|
| 3        | BUDGET-005 | Monthly pacing >105% cap                  | -10% on highest-cost camp |
| 5        | BUDGET-003 | COST_SPIKE detected                       | -5%/-10% emergency cut    |
| 15       | BUDGET-002 | ROAS 25%+ below target                    | -5%/-10% budget           |
| 20       | BUDGET-001 | ROAS 15%+ above target                    | +5%/+10% budget           |
| 25       | BUDGET-004 | Cost dropped + ROAS still good            | +5% recovery              |
| 40       | BUDGET-006 | Volatile (CV>0.60)                        | Hold — no changes         |

### Bid Rules (4)
| Priority | Rule ID  | When it fires                              | What it does              |
|----------|----------|-------------------------------------------|---------------------------|
| 10       | BID-003  | CVR dropping                              | Hold — investigate first  |
| 35       | BID-001  | ROAS 25%+ above target (30d, stable)      | Tighten tROAS +5%/+10%   |
| 35       | BID-002  | ROAS 15%+ below target (30d, stable)      | Loosen tROAS -5%          |
| 45       | BID-004  | Low data (<15 conv/30d)                   | Hold — collect data       |

### Account Rules (3)
| Priority | Rule ID   | When it fires                             | What it does              |
|----------|-----------|------------------------------------------|---------------------------|
| 10       | ACCT-001  | Pacing 100-105% cap                      | Early warning alert       |
| 50       | ACCT-002  | ROAS spread >2x across campaigns         | Suggest rebalance         |
| 55       | ACCT-003  | >50% campaigns low data                  | Data collection warning   |

### Status Rules (3)
| Priority | Rule ID    | When it fires                             | What it does              |
|----------|------------|------------------------------------------|---------------------------|
| 8        | STATUS-001 | ROAS <50% of target (30d, with data)     | Flag for human review     |
| 15       | STATUS-002 | CTR dropped + absolute CTR <1%           | Creative/relevance review |
| 90       | STATUS-003 | Everything healthy                       | Explicit "no action"      |

---

## Constitution Compliance

### Guardrails Applied to Every Recommendation

| Guardrail              | Constitution Ref    | What it checks                                    |
|------------------------|--------------------|----------------------------------------------------|
| low_data_block         | CONSTITUTION-A-4   | clicks_w7 ≥ 30                                    |
| low_conv_bid_block     | CONSTITUTION-A-4   | conversions_w30 ≥ 15 (bid rules only)             |
| protected_entity       | CONSTITUTION-5-6   | Campaign not in protected list, not brand          |
| confidence_threshold   | —                  | Confidence ≥ 0.5                                   |
| cooldown               | CONSTITUTION-5-3   | No same-lever change on entity within 7d          |
| one_lever_rule         | CONSTITUTION-5-4   | No budget+bid on same campaign within 7d          |
| budget_change_cap      | CONSTITUTION-5-1   | ±5% (conservative) / ±10% (balanced) / ±15% (aggressive) / ±20% absolute |
| bid_change_cap         | CONSTITUTION-5-1   | ±5%/±10%/±15% max                                 |
| daily_spend_cap        | CONSTITUTION-5-5   | New budget < daily cap                            |
| monthly_pacing         | CONSTITUTION-5-5   | No expansion if pacing >105%                      |

### Change Limits Respected

| Limit                    | Value              | Rule                    |
|--------------------------|-------------------|--------------------------|
| Budget change (conservative) | ±5%           | CONSTITUTION-5-1         |
| Budget change (balanced)     | ±10%          | CONSTITUTION-5-1         |
| Budget change (aggressive)   | ±15%          | CONSTITUTION-5-1         |
| Budget absolute max          | ±20%          | CONSTITUTION-5-1         |
| Bid target change max        | ±15%          | CONSTITUTION-5-1         |
| Cooldown same lever          | 7 days        | CONSTITUTION-5-3         |
| One lever at a time          | 7 days        | CONSTITUTION-5-4         |

---

## Expected Scenario Outcomes

| Campaign | Scenario    | Expected Rules           | Not Expected                  |
|----------|------------|--------------------------|-------------------------------|
| 2001     | STABLE_A   | STATUS-003 (healthy)     | BUDGET-003, BUDGET-005       |
| 2002     | STABLE_B   | STATUS-003 (healthy)     | BUDGET-003, BUDGET-005       |
| 2003     | COST_SPIKE | BUDGET-003 (emergency)   | BUDGET-001, BUDGET-004       |
| 2004     | COST_DROP  | BUDGET-004 (recovery)    | BUDGET-003                   |
| 2005     | CTR_DROP   | BID-003 (hold)           | BUDGET-001                   |
| 2006     | CVR_DROP   | BID-003 (hold CVR)       | BID-001, BID-002             |
| 2007     | VOLATILE   | BUDGET-006 (hold)        | BUDGET-001, BUDGET-002       |
| 2008     | LOW_DATA   | BID-004 (hold low data)  | BUDGET-001/002, BID-001/002  |

---

## File Structure

```
act_autopilot/
├── __init__.py
├── __main__.py
├── models.py          # AutopilotConfig, Recommendation, RuleContext
├── guardrails.py      # All Constitution guardrail checks
├── engine.py          # Rule orchestration, conflict resolution, reporting
├── cli.py             # CLI entrypoint
└── rules/
    ├── __init__.py
    ├── budget_rules.py    # BUDGET-001 through BUDGET-006
    ├── bid_rules.py       # BID-001 through BID-004
    ├── account_rules.py   # ACCT-001 through ACCT-003
    └── status_rules.py    # STATUS-001 through STATUS-003
```

---

## How to Run

### Run Autopilot (after Lighthouse has run)

```powershell
cd C:\Users\User\Desktop\gads-data-layer
.\.venv\Scripts\Activate.ps1
python -m act_autopilot.cli run-v0 configs/client_synthetic.yaml --snapshot-date 2026-02-11
```

### Run Tests

```powershell
python tools/testing/test_autopilot_rules.py
```

### Output Locations

- Autopilot report: `reports/autopilot/<client_id>/<date>.json`
- Test results: `reports/autopilot/<client_id>/test_results_<date>.json`
