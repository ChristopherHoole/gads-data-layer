# Execution Guide - Ads Control Tower

This guide explains how to execute Google Ads recommendations using the Ads Control Tower execution system.

---

## Table of Contents

1. [Overview](#overview)
2. [CLI Execution Tool](#cli-execution-tool)
3. [Execution Modes](#execution-modes)
4. [Constitution Guardrails](#constitution-guardrails)
5. [Action Types](#action-types)
6. [Examples](#examples)
7. [Troubleshooting](#troubleshooting)

---

## Overview

The Ads Control Tower execution system provides safe, controlled automation for Google Ads optimization with:

- **Dry-run simulation** - Test changes before applying them
- **Constitution guardrails** - Automatic safety checks and limits
- **Comprehensive logging** - Full audit trail of all changes
- **Automatic rollback** - Revert changes if performance degrades
- **Multi-level approval** - Control who can execute what

### Execution Flow

```
1. Generate Recommendations (Autopilot)
   ↓
2. Apply Constitution Guardrails (Validation)
   ↓
3. Execute Changes (Executor)
   ↓
4. Log to Database (Change Log)
   ↓
5. Monitor Performance (Radar)
```

---

## CLI Execution Tool

The CLI execution tool (`tools/execute_recommendations.py`) provides manual execution control.

### Installation

No installation needed - the tool is included in the project.

### Basic Usage

```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# View help
python tools/execute_recommendations.py --help

# Execute in dry-run mode
python tools/execute_recommendations.py --client client_001 --dry-run

# Execute in live mode (with confirmation)
python tools/execute_recommendations.py --client client_001 --live
```

### Command-Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `--client` | Client ID (required) | `--client client_001` |
| `--dry-run` | Simulate execution only | `--dry-run` |
| `--live` | Make actual API changes | `--live` |
| `--risk-tier` | Filter by risk level | `--risk-tier LOW` |
| `--action-type` | Filter by action type | `--action-type pause_keyword` |
| `--campaign` | Filter by campaign name | `--campaign "Brand"` |
| `--include-blocked` | Show blocked recommendations | `--include-blocked` |
| `--no-confirm` | Skip confirmation prompt | `--no-confirm` |
| `--save-log` | Save execution log to file | `--save-log log.json` |
| `--max-display` | Max recommendations to show | `--max-display 20` |

---

## Execution Modes

### Dry-Run Mode

**Purpose:** Test and validate changes before applying them.

**Behavior:**
- Simulates all API calls without making changes
- Validates all guardrails and constraints
- Logs simulated actions to console
- No changes written to database
- No actual Google Ads API calls made

**When to use:**
- Testing new rules or configurations
- Reviewing recommendations before execution
- Training and familiarization
- Debugging and troubleshooting

**Example:**
```powershell
python tools/execute_recommendations.py --client client_001 --dry-run
```

**Output:**
```
DRY-RUN: Would pause keyword 123456789 in ad group 12345
Status: DRY_RUN
```

### Live Mode

**Purpose:** Execute actual changes to Google Ads account.

**Behavior:**
- Makes real API calls to Google Ads
- Applies all changes to live account
- Logs all changes to database
- Triggers monitoring and alerting
- Cannot be undone (except via rollback)

**When to use:**
- After reviewing dry-run results
- When confident in recommendations
- During regular optimization cycles

**Safety features:**
- Requires explicit `--live` flag
- Shows confirmation prompt by default
- Validates all guardrails before execution
- Logs every change with full audit trail

**Example:**
```powershell
python tools/execute_recommendations.py --client client_001 --live
```

**Output:**
```
⚠️  About to execute 5 recommendations in LIVE mode
⚠️  WARNING: This will make LIVE changes to your Google Ads account!

Proceed? (yes/no): yes

LIVE: Executed BUD-001
  Campaign: Brand Search (12345)
  Old Budget: £50.00/day
  New Budget: £60.00/day
  Change: +20.0%
  API Response: SUCCESS
  Status: SUCCESS
```

---

## Constitution Guardrails

The Constitution defines safety rules that are automatically enforced during execution.

### Keyword Guardrails

| Guardrail | Limit | Purpose |
|-----------|-------|---------|
| Daily add limit | Max 10/day per campaign | Prevent keyword stuffing |
| Daily negative limit | Max 20/day per campaign | Prevent over-blocking |
| Bid change magnitude | ±20% max | Prevent bid shocks |
| Cooldown period | 14 days | Prevent rapid changes |
| Data requirement (pause) | ≥30 clicks (30d) | Ensure statistical significance |
| Initial bid requirement | Must specify | Avoid zero-bid keywords |

**Example validation:**
```
✗ BLOCKED: Daily keyword add limit reached (10/day): 10 already added today
✗ BLOCKED: Cooldown violation - keyword changed within 14 days (last: 2026-02-06)
✗ BLOCKED: Insufficient data - need ≥30 clicks, found 25
```

### Ad Guardrails

| Guardrail | Limit | Purpose |
|-----------|-------|---------|
| Daily pause limit | Max 5/day per ad group | Prevent mass pausing |
| Minimum active ads | Always ≥2 active | Maintain ad rotation |
| Cooldown period | 7 days | Prevent rapid changes |
| Data requirement (CTR pause) | ≥1000 impressions (30d) | Ensure statistical significance |
| Data requirement (CVR pause) | ≥100 clicks (30d) | Ensure statistical significance |
| CTR improvement (re-enable) | ≥20% improvement | Verify performance recovery |

**Example validation:**
```
✗ BLOCKED: Daily ad pause limit reached (5/day): 5 already paused today
✗ BLOCKED: Cannot pause - would leave only 1 active ads (min 2 required)
✗ BLOCKED: CTR improvement insufficient - need ≥20%, found 15%
```

### Shopping Guardrails

| Guardrail | Limit | Purpose |
|-----------|-------|---------|
| Daily exclusion limit | Max 10/day per campaign | Prevent over-exclusion |
| Bid change magnitude | ±20% max | Prevent bid shocks |
| Cooldown period | 14 days | Prevent rapid changes |
| Out-of-stock protection | No changes to OOS products | Avoid wasted spend |
| Feed quality protection | No exclusions with feed issues | Fix feed first |
| Category protection | No exclusions if only in category | Maintain coverage |

**Example validation:**
```
✗ BLOCKED: Cannot modify out-of-stock product - fix feed first
✗ BLOCKED: Cannot exclude product with feed quality issues - fix feed first
✗ BLOCKED: Daily product exclusion limit reached (10/day)
```

---

## Action Types

### Budget & Bid Actions (Campaign-level)

| Action Type | Description | Risk Tier |
|-------------|-------------|-----------|
| `update_budget` | Adjust daily budget | LOW-MEDIUM |
| `update_target_cpa` | Adjust target CPA | LOW-MEDIUM |
| `update_target_roas` | Adjust target ROAS | LOW-MEDIUM |
| `pause_campaign` | Pause campaign | MEDIUM-HIGH |
| `enable_campaign` | Enable campaign | MEDIUM |

### Keyword Actions

| Action Type | Description | Risk Tier |
|-------------|-------------|-----------|
| `add_keyword` | Add new keyword with bid | MEDIUM |
| `pause_keyword` | Pause underperforming keyword | LOW |
| `update_keyword_bid` | Adjust keyword CPC bid | LOW |
| `add_negative_keyword` | Add negative keyword (campaign-level) | LOW |

### Ad Actions

| Action Type | Description | Risk Tier |
|-------------|-------------|-----------|
| `pause_ad` | Pause underperforming ad | LOW |
| `enable_ad` | Re-enable paused ad | MEDIUM |

### Shopping Actions

| Action Type | Description | Risk Tier |
|-------------|-------------|-----------|
| `update_product_bid` | Adjust product partition bid | LOW |
| `exclude_product` | Exclude product (campaign-level) | MEDIUM |

---

## Examples

### Example 1: Execute Low-Risk Changes Only

```powershell
python tools/execute_recommendations.py \
  --client client_001 \
  --risk-tier LOW \
  --dry-run
```

**Output:**
```
Filtered: 12 recommendations

By Risk Tier:
  LOW: 12

Recommendation Details:
1. KW-PAUSE-001 - Pause High CPA Keyword
   Risk: LOW | Confidence: 90.0%
   Rationale: CPA £85.50 exceeds target £50.00

2. AD-PAUSE-001 - Pause Low CTR Ad
   Risk: LOW | Confidence: 88.0%
   Rationale: Ad CTR 1.5% below average 3.2%
```

### Example 2: Execute Keyword Changes Only

```powershell
python tools/execute_recommendations.py \
  --client client_001 \
  --action-type pause_keyword \
  --live
```

**Output:**
```
Filtered: 3 recommendations

By Action Type:
  pause_keyword: 3

⚠️  About to execute 3 recommendations in LIVE mode
⚠️  WARNING: This will make LIVE changes to your Google Ads account!

Proceed? (yes/no): yes

Executing 3 Recommendations
✓ All 3 recommendations executed successfully!
```

### Example 3: Execute Changes for Specific Campaign

```powershell
python tools/execute_recommendations.py \
  --client client_001 \
  --campaign "Brand Search" \
  --dry-run
```

**Output:**
```
Filtered: 8 recommendations

Recommendation Details:
1. BUD-001 - Increase High-Performing Campaign Budget
   Entity: Brand Search Campaign (12345)
   Change: £50.00 → £60.00 (+20.0%)
```

### Example 4: Review Blocked Recommendations

```powershell
python tools/execute_recommendations.py \
  --client client_001 \
  --include-blocked \
  --dry-run
```

**Output:**
```
Filtered: 15 recommendations (3 blocked)

5. KW-ADD-002 - Add High-Intent Keyword
   Risk: MEDIUM | Confidence: 85.0%
   ⚠️  BLOCKED: Daily keyword add limit reached (10/day)

6. AD-PAUSE-004 - Pause Low CTR Ad
   Risk: LOW | Confidence: 80.0%
   ⚠️  BLOCKED: Cannot pause - would leave only 1 active ads
```

### Example 5: Save Execution Log

```powershell
python tools/execute_recommendations.py \
  --client client_001 \
  --risk-tier LOW \
  --live \
  --save-log execution_20260216.json
```

**Output:**
```
✓ All 5 recommendations executed successfully!
✓ Execution log saved to: execution_20260216.json
```

**Log file contents:**
```json
{
  "timestamp": "2026-02-16T10:30:00",
  "client_id": "client_001",
  "mode": "live",
  "filters": {
    "risk_tier": "LOW"
  },
  "summary": {
    "total": 5,
    "successful": 5,
    "failed": 0
  },
  "results": [...]
}
```

---

## Troubleshooting

### Issue: "Config file not found"

**Problem:**
```
✗ Error: Config file not found: configs\client_001.yaml
```

**Solution:**
- Check client ID matches config filename exactly
- Config files are in `configs/` directory
- Available clients: `client_001`, `client_001_mcc`, `client_002`, `client_synthetic`

### Issue: "No recommendations found"

**Problem:**
```
✗ No recommendations match filters. Exiting.
```

**Solutions:**
1. Remove filters to see all recommendations
2. Check if filters are too restrictive
3. Verify recommendations were generated
4. Try different client or campaign

### Issue: "Validation failed: Cooldown violation"

**Problem:**
```
✗ BLOCKED: Cooldown violation - keyword changed within 14 days
```

**Solutions:**
- Wait for cooldown period to expire
- This is a safety feature - working as intended
- Review why entity was changed recently
- Check change_log table for history

### Issue: "API call failed"

**Problem:**
```
✗ Execution failed: GoogleAdsException
```

**Solutions:**
1. Check Google Ads API credentials
2. Verify account access permissions
3. Check API rate limits
4. Review error message details
5. Run in dry-run mode first

### Issue: "Insufficient data for action"

**Problem:**
```
✗ BLOCKED: Insufficient data - need ≥30 clicks, found 25
```

**Solutions:**
- This is a safety feature - working as intended
- Wait for more data to accumulate
- Lower data thresholds in Constitution (advanced)
- Verify entity has enough traffic

---

## Best Practices

### 1. Always Start with Dry-Run

```powershell
# GOOD: Test first
python tools/execute_recommendations.py --client client_001 --dry-run
# Review output, then run live if satisfied
python tools/execute_recommendations.py --client client_001 --live

# BAD: Live execution without testing
python tools/execute_recommendations.py --client client_001 --live --no-confirm
```

### 2. Start with Low-Risk Changes

```powershell
# Week 1: Low risk only
python tools/execute_recommendations.py --client client_001 --risk-tier LOW --live

# Week 2: Low + Medium risk
python tools/execute_recommendations.py --client client_001 --live

# Later: All risk tiers (with approval)
```

### 3. Monitor After Execution

- Check change_log table for execution record
- Monitor performance metrics for 7-14 days
- Set up email alerts for anomalies
- Review Radar dashboard regularly

### 4. Keep Execution Logs

```powershell
# Save all live executions
python tools/execute_recommendations.py \
  --client client_001 \
  --live \
  --save-log "logs/execution_$(date +%Y%m%d_%H%M%S).json"
```

### 5. Review Blocked Recommendations

```powershell
# Weekly review of blocked items
python tools/execute_recommendations.py \
  --client client_001 \
  --include-blocked \
  --dry-run
```

---

## Support

For issues or questions:

1. Check this documentation
2. Review test scripts in `tools/testing/`
3. Check change_log table for execution history
4. Review Constitution guardrails
5. Contact support team

---

**Last Updated:** 2026-02-16  
**Version:** 1.0
