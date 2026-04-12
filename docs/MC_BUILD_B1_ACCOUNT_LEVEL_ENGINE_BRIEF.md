# MC Build B1 — Account Level Engine
**Session:** MC Build B1 — Account Level Engine
**Date:** 2026-04-13
**Objective:** Build the Account Level optimization engine — the first level of ACT's decision logic. This engine reads real Google Ads data, evaluates performance, and generates budget allocation recommendations.

---

## CONTEXT

Sessions A1-A3 are complete:
- 13 `act_v2_*` tables with 71 settings seeded for Objection Experts
- 90 days of real Google Ads data in `act_v2_snapshots` (campaigns, ad groups, keywords, ads, search terms, segments)
- Client Configuration page live at `/v2/config` with Save/Reset working
- Level states all set to 'off' — engine should respect this

**This session builds the Account Level optimization engine — engine logic ONLY, no UI.**

The engine:
1. Reads snapshot data from `act_v2_snapshots`
2. Reads client settings from `act_v2_client_settings` and `act_v2_clients`
3. Reads level state from `act_v2_client_level_state`
4. Evaluates performance using signal decomposition and weighted scoring
5. Generates budget allocation recommendations
6. Writes results to `act_v2_recommendations` (with `mode='monitor_only'` initially)

**Source of truth for the logic:**
- `docs/ACT_OPTIMIZATION_ARCHITECTURE_v54.html` — Account Level section (read it thoroughly)
- `docs/ACT_OPTIMIZATION_ARCHITECTURE_SUMMARY.md` — quick reference
- `act_v2_checks` table — check `account_budget_allocation` (check_id, cooldown_hours=72, auto_execute=true)

---

## CRITICAL RULES

1. **Engine only — NO UI, NO Flask routes.** This session builds a standalone Python module that can be run from the command line. The UI comes in Session B2.

2. **Monitor Only mode first.** All recommendations generated in this session use `mode='monitor_only'`. The engine does NOT call the Google Ads API to make changes. It only analyses data and logs what it WOULD do.

3. **Respect level state.** Before running any checks, read `act_v2_client_level_state` for the Account level. If state is:
   - `'off'` → skip entirely, log "Account level is OFF, skipping"
   - `'monitor_only'` → run checks, write recommendations with `mode='monitor_only'`
   - `'active'` → run checks, write recommendations with `mode='active'` (but don't execute yet — execution comes later)

4. **Read real data.** All calculations use data from `act_v2_snapshots` for the client, NOT hardcoded or synthetic values.

5. **Read real settings.** All thresholds, cooldowns, weights, and bands come from `act_v2_client_settings` for the client, NOT hardcoded defaults.

6. **Do NOT modify existing files.** Create new files in `act_dashboard/engine/`.

7. **Idempotency.** Running the engine twice should not create duplicate recommendations. Delete existing PENDING recommendations for this client+level before generating new ones (approved/executed/declined recommendations are preserved).

---

## TASK 1: Read the Architecture

Before writing any code, read the Account Level section of `docs/ACT_OPTIMIZATION_ARCHITECTURE_v54.html` thoroughly. Understand:

1. **Two personas:** Lead Gen (CPA) and Ecommerce (ROAS) — determines what metrics matter
2. **Campaign roles:** BD, CP, RT, PR, TS — each has budget allocation bands
3. **Signal decomposition:** CPC (7d window) + CVR (14d window) for Lead Gen; CPC + CVR + AOV (30d window) for Ecommerce
4. **Performance scoring:** 7d 50% + 14d 30% + 30d 20% weighted blend
5. **Budget allocation logic:** compare campaign performance scores, shift budget from underperformers to outperformers
6. **Guardrails:** max 10% overnight move, 72hr cooldown per campaign, budget bands per role
7. **Decision flow:** what triggers a recommendation, what auto-executes vs what needs approval

Also read:
- `act_v2_checks` row for `account_budget_allocation` — confirm check_id, cooldown, auto_execute values
- `act_v2_client_settings` for Objection Experts — confirm all Account-level settings and their current values
- `act_v2_snapshots` — understand the `metrics_json` structure for campaign-level data

Confirm what you understand before writing code.

---

## TASK 2: Create the Engine Module Structure

Create `act_dashboard/engine/` directory with:

```
act_dashboard/engine/
    __init__.py
    account_level.py    ← Account Level check logic
    base.py             ← Base engine class (shared by all levels)
    run_engine.py       ← CLI runner
```

### `act_dashboard/engine/base.py`

Base class for all level engines:

```python
class BaseLevelEngine:
    def __init__(self, client_id: str):
        self.client_id = client_id
        self.db = self._connect_db()
        self.client = self._load_client()
        self.settings = self._load_settings()
        self.level_state = self._load_level_state()
    
    def _connect_db(self):
        """Connect to warehouse.duckdb"""
    
    def _load_client(self) -> dict:
        """Load client from act_v2_clients"""
    
    def _load_settings(self) -> dict:
        """Load all settings from act_v2_client_settings for this client"""
    
    def _load_level_state(self) -> dict:
        """Load all level states from act_v2_client_level_state for this client"""
    
    def get_setting(self, key: str, default=None):
        """Get a setting value, with type conversion based on setting_type"""
    
    def get_snapshots(self, level: str, date: str, days_back: int = 30) -> list:
        """Get snapshot data for a date range.
        Queries: SELECT * FROM act_v2_snapshots WHERE client_id=? AND level=? 
                 AND snapshot_date BETWEEN (date - days_back) AND date
        Returns list of dicts with parsed metrics_json.
        NOTE: For Account Level engine, pass level='campaign' to get individual campaign data,
        NOT level='account' (which returns the aggregated account-level row)."""
    
    def write_recommendation(self, check_id, entity_id, entity_name, parent_entity_id,
                             action_category, risk_level, summary, recommendation_text,
                             estimated_impact, decision_tree, current_value, proposed_value):
        """Write a recommendation to act_v2_recommendations.
        Automatically sets mode based on level_state (monitor_only or active)."""
    
    def check_cooldown(self, check_id: str, entity_id: str) -> bool:
        """Check if a cooldown is active for this check+entity.
        Returns True if cooldown is active (should NOT act), False if ready."""
    
    def clear_old_recommendations(self, level: str):
        """Delete existing PENDING recommendations for this client+level to ensure idempotency.
        Only deletes recommendations with status='pending' — approved/executed/declined are preserved.
        Uses: DELETE FROM act_v2_recommendations WHERE client_id=? AND level=? AND status='pending'"""
```

### `act_dashboard/engine/account_level.py`

The Account Level engine:

```python
from act_dashboard.engine.base import BaseLevelEngine

class AccountLevelEngine(BaseLevelEngine):
    LEVEL = 'account'
    CHECK_ID = 'account_budget_allocation'
    
    def run(self, evaluation_date: str):
        """Run all Account Level checks for a given date."""
        # 1. Check if account level is enabled
        if self.level_state.get('account') == 'off':
            print(f"Account level is OFF for {self.client_id}, skipping")
            return
        
        # 2. Clear old pending recommendations for idempotency
        self.clear_old_recommendations(self.LEVEL)
        
        # 3. Load campaign data
        campaigns = self._get_campaign_data(evaluation_date)
        
        # 4. Detect campaign roles
        roles = self._get_campaign_roles()
        
        # 5. Calculate performance scores
        scored_campaigns = self._score_campaigns(campaigns, evaluation_date)
        
        # 6. Generate budget allocation recommendations
        self._evaluate_budget_allocation(scored_campaigns, roles, evaluation_date)
    
    def _get_campaign_data(self, date: str) -> list:
        """Get list of campaigns with their current-day metrics.
        Uses get_snapshots(level='campaign', date=date, days_back=0) for the single day.
        IMPORTANT: Filter to only ENABLED campaigns (check metrics_json.campaign_status).
        Paused campaigns should NOT be considered for budget allocation."""
    
    def _get_campaign_roles(self) -> dict:
        """Get campaign role assignments from act_v2_campaign_roles.
        Returns dict: {campaign_id: role_code}.
        If a campaign has no role assigned, it cannot participate in band-constrained
        budget allocation — log a warning and treat it as unconstrained."""
    
    def _score_campaigns(self, campaigns: list, date: str) -> list:
        """Calculate performance score for each campaign using weighted blend.
        
        For each campaign, query snapshots for 3 windows:
        - 7d: get_snapshots(level='campaign', date=date, days_back=7) → filter to this campaign → sum cost, sum conversions → calculate CPA
        - 14d: same with days_back=14
        - 30d: same with days_back=30
        (Or query once with days_back=30 and compute all 3 windows from the same data)
        
        For Lead Gen (CPA persona):
        - For each window, CPA = sum(cost) / sum(conversions)
        - Score = (target_cpa - actual_cpa) / target_cpa × 100 (positive = outperforming)
        - Final score = weighted blend of 3 window scores
        
        For Ecommerce (ROAS persona):
        - For each window, ROAS = sum(conversion_value) / sum(cost)
        - Score = (actual_roas - target_roas) / target_roas × 100 (positive = outperforming)
        - Same weighted blend approach as CPA
        
        Read the weights from settings:
        - performance_scoring_weight_7d (default 50)
        - performance_scoring_weight_14d (default 30)
        - performance_scoring_weight_30d (default 20)
        
        Note on signal windows vs scoring windows:
        - The SCORING windows (7d, 14d, 30d) are the three time horizons for the weighted CPA/ROAS blend. Weights come from performance_scoring_weight_7d/14d/30d.
        - The SIGNAL windows (signal_window_cpc_days=7, signal_window_cvr_days=14, signal_window_aov_days=30) are for DECOMPOSING why the CPA/ROAS changed (CPC trend vs CVR trend). These are supplementary context for the decision tree reasoning, NOT the main scoring inputs.
        - For this implementation: use the 7d/14d/30d scoring windows for the main score. Optionally add signal decomposition context to the decision tree (e.g., "CPA increased because CPC rose 15% while CVR held steady").
        """
    
    def _evaluate_budget_allocation(self, scored_campaigns: list, roles: dict, date: str):
        """Evaluate whether budget should be shifted between campaigns.
        
        Pre-checks:
        0. If fewer than 2 ENABLED campaigns → log "not enough campaigns", return
        0b. Check budget_allocation_mode setting — if 'manual', ALL shifts need approval (action_category='investigate'), never auto-execute
        
        Logic from v54:
        1. Compare each campaign's performance score to the account average
        2. Identify outperformers (score significantly above average) and underperformers
        3. Check if budget shift would stay within the role's budget bands (skip band check if campaign has no role assigned)
        4. Check cooldown (72hr per campaign) — NOTE: on first run, no cooldowns exist in act_v2_monitoring so all campaigns are "ready"
        5. Check max overnight move (default 10% of daily budget)
        6. Generate recommendation:
           - If budget_allocation_mode == 'automatic':
             - Tightening (reducing underperformer budget) → action_category='act' (auto-execute eligible)
             - Loosening (increasing outperformer budget) → action_category='investigate' (needs approval)
           - If budget_allocation_mode == 'manual':
             - ALL shifts → action_category='investigate' (needs approval)
        7. Include decision tree reasoning (Check, Signal, Rule, Cooldown, Risk)
        
        Read guardrails from settings:
        - budget_allocation_mode (default 'automatic')
        - max_overnight_budget_move_pct (default 10)
        - budget_shift_cooldown_hours (default 72)
        - budget_band_XX_min_pct / budget_band_XX_max_pct per role
        - deviation_threshold_pct (default 10)
        """
```

---

## TASK 3: Build the CLI Runner

Create `act_dashboard/engine/run_engine.py`:

```python
"""
ACT v2 Engine Runner

Runs optimization checks for a client.

Usage (from project root):
    # Run Account Level for yesterday:
    python -m act_dashboard.engine.run_engine --client oe001 --level account
    
    # Run Account Level for a specific date:
    python -m act_dashboard.engine.run_engine --client oe001 --level account --date 2026-04-11
    
    # Run all levels:
    python -m act_dashboard.engine.run_engine --client oe001 --level all

Prerequisites:
    - Flask app must be stopped (DuckDB lock)
    - Data must be ingested (Session A2) for the evaluation date
"""
```

Requirements:
1. Parse `--client` (required), `--level` (default 'account'), `--date` (default yesterday)
2. Look up client in `act_v2_clients`
3. Instantiate the appropriate engine class
4. Call `engine.run(date)`
5. Print summary of recommendations generated
6. Log to `act_dashboard/engine/engine.log` (append mode)

---

## TASK 4: Implement the Engine Logic

Build out the `AccountLevelEngine` methods with real logic from v54.

### Performance Scoring Detail

For each campaign, calculate a performance score:

```
For Lead Gen (CPA):
    # Get metrics for each window
    cpa_7d = sum(cost_7d) / sum(conversions_7d)  # handle div by zero
    cpa_14d = sum(cost_14d) / sum(conversions_14d)
    cpa_30d = sum(cost_30d) / sum(conversions_30d)
    
    target_cpa = client.target_cpa  # from act_v2_clients
    
    # Score = % below target (positive = good, negative = bad)
    score_7d = (target_cpa - cpa_7d) / target_cpa * 100
    score_14d = (target_cpa - cpa_14d) / target_cpa * 100
    score_30d = (target_cpa - cpa_30d) / target_cpa * 100
    
    # Weighted blend
    weights = {7: 0.50, 14: 0.30, 30: 0.20}  # from settings
    final_score = (score_7d * weights[7]) + (score_14d * weights[14]) + (score_30d * weights[30])
```

### Budget Allocation Decision

```
Strategy: Rank campaigns by score. Shift budget from the LOWEST scorer to the HIGHEST scorer.
Only ONE shift recommendation per overnight cycle (keep it simple and predictable).

Steps:
    1. Rank campaigns by final_score (highest = best performer)
    2. best = highest scoring campaign, worst = lowest scoring campaign
    3. Is the score difference > deviation_threshold_pct? If not → no action needed, all campaigns performing similarly
    4. Is the best campaign's current budget share < its role's max band? If at max → can't increase, skip
    5. Is the worst campaign's current budget share > its role's min band? If at min → can't decrease, skip
    6. Is either campaign in cooldown? If yes → skip
    7. Calculate proposed shift (capped at max_overnight_budget_move_pct of total daily budget)
    8. Generate ONE recommendation with full decision tree reasoning

If the best/worst pair can't be shifted (band/cooldown constraints), try the next best/worst pair.
```

### Decision Tree (for each recommendation)

```python
decision_tree = {
    "check": "Account-level budget allocation (runs daily)",
    "signal": f"Campaign '{campaign_name}' CPA is {score}% {'below' if score > 0 else 'above'} target over weighted 7d/14d/30d blend",
    "rule": f"Budget shift of {shift_pct}% from '{from_campaign}' to '{to_campaign}'. Within role bands and overnight move cap.",
    "cooldown": f"{cooldown_hours}hr cooldown after execution. Next eligible: {next_eligible_date}",
    "risk": f"{'Low' if abs(shift_pct) <= 5 else 'Medium'} — {'within normal optimization range' if abs(shift_pct) <= 5 else 'larger shift, verify campaign health'}"
}
```

### Estimated Impact

```python
estimated_impact = f"Estimated saving: £{estimated_saving:.2f}/week based on CPA differential"
```

---

## TASK 5: Run the Engine and Verify

### Step 1: Set Account level to 'monitor_only'

Before running the engine, update the level state:
```sql
UPDATE act_v2_client_level_state 
SET state = 'monitor_only', updated_at = CURRENT_TIMESTAMP 
WHERE client_id = 'oe001' AND level = 'account';
```

Or use the Client Config page to toggle it.

### Step 2: Run the engine

```
python -m act_dashboard.engine.run_engine --client oe001 --level account --date 2026-04-11
```

### Step 3: Verify recommendations were created

```sql
SELECT recommendation_id, entity_name, action_category, risk_level, 
       summary, mode, status, identified_at
FROM act_v2_recommendations 
WHERE client_id = 'oe001' AND level = 'account'
ORDER BY identified_at DESC;
```

Expected: at least 1 recommendation (or 0 if all campaigns are performing equally — which is possible for a 1-campaign account like Objection Experts).

### Step 4: Handle the 1-campaign edge case

Objection Experts only has 1 active campaign (GLO Campaign). Budget allocation between campaigns requires 2+ campaigns. The engine should handle this gracefully:
- If only 1 campaign exists → log "Only 1 campaign, no budget allocation possible" → write 0 recommendations
- This is NOT an error — it's a valid outcome

To test the engine with meaningful output, you can either:
- Note that the engine correctly identifies "nothing to do" for a 1-campaign account
- Or create test data with multiple campaigns for verification (but don't modify real data)

### Step 5: Verify idempotency

Run the engine again for the same date. Count recommendations before and after — should be the same:
```sql
-- Before second run:
SELECT COUNT(*) FROM act_v2_recommendations WHERE client_id = 'oe001' AND level = 'account';

-- Run engine again

-- After second run (should be same count):
SELECT COUNT(*) FROM act_v2_recommendations WHERE client_id = 'oe001' AND level = 'account';
```

---

## TASK 6: Write Unit Tests

Create `act_dashboard/engine/tests/test_account_level.py`:

Test cases:
1. **Single campaign account** — engine runs, generates 0 recommendations, no errors
2. **Level state OFF** — engine skips entirely
3. **Level state MONITOR_ONLY** — recommendations written with `mode='monitor_only'`
4. **Performance scoring** — given known snapshot data, verify the score calculation is correct
5. **Cooldown check** — if a campaign was shifted recently, it should be skipped
6. **Budget bands** — shift should not exceed the role's min/max band
7. **Max overnight move** — shift should not exceed max_overnight_budget_move_pct
8. **Idempotency** — running twice produces the same number of recommendations (not double)

Use the real `warehouse.duckdb` with Objection Experts data for integration tests. For unit tests, mock the database responses.

---

## TASK 7: Commit

Git commit with clear message.

---

## DELIVERABLES

1. `act_dashboard/engine/__init__.py`
2. `act_dashboard/engine/base.py` — base engine class
3. `act_dashboard/engine/account_level.py` — Account Level engine
4. `act_dashboard/engine/run_engine.py` — CLI runner
5. `act_dashboard/engine/tests/__init__.py`
6. `act_dashboard/engine/tests/test_account_level.py` — unit tests
7. Recommendations in `act_v2_recommendations` (if any generated)
8. Engine log at `act_dashboard/engine/engine.log`
9. Git commit

---

## EXECUTION ORDER

1. Read v54 Account Level architecture + database tables
2. Create engine module structure (base.py, account_level.py)
3. Build CLI runner
4. Implement engine logic (scoring, budget allocation, decision trees)
5. Set Account level to monitor_only, run the engine
6. Verify recommendations in database
7. Write unit tests
8. Commit

---

## VERIFICATION CHECKLIST

- [ ] Engine module exists at `act_dashboard/engine/`
- [ ] `run_engine.py` runs without errors from command line
- [ ] Engine respects level state (OFF = skip, MONITOR_ONLY = log)
- [ ] Engine reads real snapshot data from `act_v2_snapshots`
- [ ] Engine reads real settings from `act_v2_client_settings`
- [ ] Performance scoring uses correct weighted blend (50/30/20)
- [ ] Budget allocation logic matches v54 architecture
- [ ] Recommendations written to `act_v2_recommendations` with correct fields
- [ ] Decision tree JSON is populated with Check/Signal/Rule/Cooldown/Risk
- [ ] Cooldown checking works (reads from `act_v2_monitoring`)
- [ ] Idempotency — running twice produces same results, not duplicates
- [ ] 1-campaign edge case handled gracefully
- [ ] Unit tests pass
- [ ] Engine log file created with clear output
- [ ] Git commit created

---

## IMPORTANT NOTES

- **Objection Experts has only 1 active campaign** — budget allocation needs 2+ campaigns to produce recommendations. The engine should handle this gracefully (0 recommendations is a valid result).
- Stop Flask before running the engine script (DuckDB lock)
- The engine does NOT call the Google Ads API — it only analyses data and writes recommendations
- For TESTING in this session, the level state will be set to 'monitor_only', so all recommendations will have `mode='monitor_only'`. No active execution. But the code must support both modes.
- The `BaseLevelEngine` class is designed to be extended by Campaign, Ad Group, Keyword, Ad, and Shopping level engines in future sessions
- Signal decomposition windows (CPC 7d, CVR 14d, AOV 30d) are read from settings, not hardcoded
- Performance scoring weights (50/30/20) are read from settings, not hardcoded
- The `metrics_json` in snapshots stores campaign metrics — parse with `json.loads()`
- For multi-day aggregations (7d, 14d, 30d), sum the daily values from snapshots for the relevant date range
- **Division by zero handling:** 0 conversions with spend → CPA is infinite → assign worst possible score (e.g., -100). 0 conversions with 0 spend → campaign had no activity in that window → exclude from scoring for that window. 0 cost → ROAS is undefined → exclude from scoring. Always check denominators before dividing.
- **Paused campaigns:** Snapshots include data for paused campaigns, but budget allocation should only consider ENABLED campaigns. Check `metrics_json.campaign_status` to filter. Objection Experts has 1 ENABLED + 3 PAUSED = only 1 eligible campaign → 0 recommendations.
- **Campaign roles:** If a campaign has no role assigned in `act_v2_campaign_roles`, it cannot be checked against budget bands. Log a warning but still include it in scoring — just skip the band constraint check for that campaign.
- **Budget allocation mode:** Check `budget_allocation_mode` setting. If 'manual', ALL budget shifts need approval (action_category='investigate'). If 'automatic', tightening auto-executes and loosening needs approval.
- **Cooldowns on first run:** The `act_v2_monitoring` table is empty on the first run, so `check_cooldown` will always return False (no active cooldowns). This is expected.
- **Entity ID for budget allocation recommendations:** Generate ONE recommendation per budget shift pair. Use `entity_id` = the outperformer campaign ID (the one receiving budget). The `current_value_json` should capture both campaigns' current daily budgets. The `proposed_value_json` should capture both campaigns' proposed daily budgets.
- **Mode is derived from level state, not hardcoded.** The `write_recommendation` method should set `mode = self.level_state.get(self.LEVEL)`. For this testing session the level will be set to 'monitor_only', but the CODE should support 'active' mode too — don't hardcode 'monitor_only'.
- **ROAS scoring formula:** For Ecommerce clients: `ROAS = sum(conversion_value) / sum(cost)`. Score = `(actual_roas - target_roas) / target_roas × 100`.

---

**END OF BRIEF**
