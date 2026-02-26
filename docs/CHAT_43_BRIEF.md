# CHAT 43: AD GROUP RULES CREATION

**Estimated Time:** 4-6 hours  
**Dependencies:** Chat 42 (Keyword Rules) complete  
**Priority:** HIGH

---

## CONTEXT

**What's been done:**
- Chat 26 (M5): Created rules_config.json with 13 campaign rules
- Chat 42: Added 6 keyword rules to rules_config.json
- Current total: 19 rules (13 campaign + 6 keyword)
- Keywords Rules tab working with keywords_rules_tab.html component

**Why this task is needed:**
Ad groups are a critical optimization layer between campaigns and keywords. Poor-performing ad groups waste budget on broad targeting, while high-performing ad groups deserve more investment. Ad group-level rules enable automated optimization at the middle layer of account structure.

**How it fits into the bigger picture:**
This completes the second of four rule types needed:
1. ✅ Campaign rules (13) - Chat 26
2. ✅ Keyword rules (6) - Chat 42
3. 🎯 Ad Group rules (3-5) - **THIS CHAT**
4. 📋 Ad rules (3-5) - Chat 44
5. 📋 Shopping rules (14) - Chat 45

After all rules created → recommendations engine extension → live Google Ads connection.

---

## OBJECTIVE

Create 3-5 ad group optimization rules in `rules_config.json` based on Christopher's 16 years of Google Ads expertise, focusing on pausing poor performers and scaling winners at the ad group level.

---

## REQUIREMENTS

### Deliverables

**1. rules_config.json (modify)**
- Location: `C:\Users\User\Desktop\gads-data-layer\act_autopilot\rules_config.json`
- Add 3-5 ad group rules (ad_group_1 through ad_group_5)
- All 24 required fields per rule (see structure below)
- Constitution-compliant (cooldowns ≥7, monitoring ≥7, magnitude within limits)
- Total rules after completion: 22-24 (13 campaign + 6 keyword + 3-5 ad_group)

**2. CHAT_43_SUMMARY.md (create)**
- Location: `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_43_SUMMARY.md`
- Executive summary of rules created
- Constitution compliance verification
- Testing results

**3. CHAT_43_HANDOFF.md (create)**
- Location: `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_43_HANDOFF.md`
- Complete technical details
- Implementation decisions
- Future enhancements

---

### Technical Constraints

**Rule Structure (24 required fields):**
```json
{
  "rule_id": "ad_group_1",
  "rule_type": "ad_group",
  "rule_number": 1,
  "display_name": "Short name for UI",
  "name": "AD_GROUP-001: Full descriptive name",
  "scope": "blanket",
  "campaign_id": null,
  "condition_metric": "quality_score",
  "condition_operator": "lt",
  "condition_value": 4.0,
  "condition_unit": "score",
  "condition_2_metric": null,
  "condition_2_operator": null,
  "condition_2_value": null,
  "condition_2_unit": null,
  "action_direction": "pause",
  "action_magnitude": null,
  "risk_level": "medium",
  "cooldown_days": 14,
  "monitoring_days": 14,
  "monitoring_minutes": 0,
  "enabled": true,
  "created_at": "2026-02-26T00:00:00",
  "updated_at": "2026-02-26T00:00:00"
}
```

**Constitution Requirements:**
- `cooldown_days`: ≥7 days (7-14 recommended)
- `monitoring_days`: ≥7 days (7-14 recommended)
- `action_magnitude`: 
  - Increases: ≤+20%
  - Decreases: ≤-30% (expressed as positive number)
  - Pause/flag actions: null
- `enabled`: true (all rules active)
- `scope`: "blanket" (all campaigns) or "specific" (single campaign)

**Valid Operators:**
- "gte" (≥), "gt" (>), "lte" (≤), "lt" (<), "eq" (=)

**Valid Action Directions:**
- "increase_bid", "decrease_bid", "pause", "flag"
- Note: No "increase/decrease" for ad groups (budget/bid are campaign/keyword level)

**Valid Risk Levels:**
- "low", "medium", "high"

---

### Ad Group Optimization Scenarios

**Based on Christopher's 16 years of expertise, here are 8 potential scenarios. Select 3-5 for implementation:**

**Scenario 1: Pause Low Quality Score Ad Groups**
- Logic: Ad groups with QS <4 and ≥20 clicks
- Action: pause
- Rationale: Low QS indicates poor relevance, unlikely to improve
- Risk: Low (clear underperformer)

**Scenario 2: Flag High CPA Ad Groups**
- Logic: CPA >2x target AND ≥10 conversions
- Action: flag for review
- Rationale: Consistent high CPA needs investigation, not automatic pause
- Risk: Medium (may have strategic value)

**Scenario 3: Pause Zero-Conversion High-Spend Ad Groups**
- Logic: Cost ≥£100 AND conversions = 0
- Action: pause
- Rationale: Clear waste of budget
- Risk: Low (no conversion value)

**Scenario 4: Flag Low CTR Ad Groups**
- Logic: CTR <0.5% AND impressions ≥500
- Action: flag for review
- Rationale: Poor ad relevance or targeting
- Risk: Low (non-destructive flag)

**Scenario 5: Flag ROAS Underperformers**
- Logic: ROAS <50% of target AND conversions ≥10
- Action: flag for review
- Rationale: Consistent underperformance needs strategic review
- Risk: Medium (may be building toward goals)

**Scenario 6: Pause Ad Groups in Budget-Constrained Campaigns**
- Logic: Campaign pacing flag = over 105% AND ad group CPA >1.5x target
- Action: pause (lowest performers in constrained campaigns)
- Rationale: Protect budget for better performers
- Risk: Medium (campaign-level dependency)

**Scenario 7: Flag Search Impression Share Loss**
- Logic: Search IS <40% AND IS lost (budget) >30%
- Action: flag for budget increase review
- Rationale: Ad group is competitive but budget-limited
- Risk: Low (flag only, not destructive)

**Scenario 8: Pause Ad Groups with Declining CVR**
- Logic: CVR drop detected ≥30% over 14 days AND conversions ≥10
- Action: pause
- Rationale: Clear performance degradation
- Risk: Medium (may be temporary)

**Your task: Select 3-5 scenarios that are:**
- Highest ROI (protect budget, scale winners)
- Clear decision criteria (not subjective)
- Constitution-compliant
- Representative of ad group optimization best practices

---

### Design Specifications

**Recommended Rule Count: 4 rules**
- 2 pause rules (clear underperformers)
- 1 flag rule (needs review)
- 1 scaling/protection rule

**Suggested Selection:**
- Scenario 1: Pause Low QS (clear underperformer)
- Scenario 3: Pause Zero-Conv High-Spend (budget protection)
- Scenario 5: Flag ROAS Underperformers (strategic review)
- Scenario 7: Flag Search IS Loss (scaling opportunity)

**But defer final selection to 5 Questions stage - get Master approval first.**

---

## REFERENCE FILES

**Similar Completed Work:**
- `act_autopilot/rules_config.json` - Contains 19 existing rules (13 campaign + 6 keyword)
  - Study keyword rules (keyword_1 through keyword_6) for pattern
  - All have proper structure, Constitution compliance, timestamps
- `docs/CHAT_42_SUMMARY.md` - Successful keyword rules implementation
- `docs/CHAT_42_HANDOFF.md` - Complete technical details

**Documentation to Consult:**
- `docs/CHAT_WORKING_RULES.md` - Mandatory workflow rules
- `docs/PROJECT_ROADMAP.md` - Overall project status
- `docs/MASTER_KNOWLEDGE_BASE.md` - Lessons learned, architecture

**Database Tables:**
- `ro.analytics.ad_group_daily` - Contains ad group performance data
  - quality_score, ctr, cpa, roas, cvr, cost, conversions columns
  - Use DESCRIBE to verify exact column names before building rules

---

## SUCCESS CRITERIA

All 12 criteria must pass for approval:

### JSON Structure & Validity
- [ ] 1. Valid JSON format (no syntax errors)
- [ ] 2. All 24 required fields present per rule
- [ ] 3. Correct data types (strings, numbers, booleans, null)
- [ ] 4. Proper operator format ("gte", "lt", "gt", "eq")
- [ ] 5. ISO 8601 timestamp format (YYYY-MM-DDTHH:MM:SS)

### Constitution Compliance
- [ ] 6. All cooldown_days ≥7 (range: 7-14 days)
- [ ] 7. All monitoring_days ≥7 (range: 7-14 days)
- [ ] 8. Action magnitudes within limits (N/A for pause/flag)
- [ ] 9. All risk_level values valid ("low", "medium", "high")

### Implementation Correctness
- [ ] 10. All rule_id values unique (ad_group_1, ad_group_2, etc.)
- [ ] 11. All rule_type = "ad_group"
- [ ] 12. All scope = "blanket" (unless Master approves campaign-specific)

---

## TESTING INSTRUCTIONS

### Step-by-Step Testing

**Test A: JSON Validation (2 min)**
```powershell
cd C:\Users\User\Desktop\gads-data-layer
.\.venv\Scripts\Activate.ps1
python -c "import json; data = json.load(open('act_autopilot/rules_config.json')); print('Total rules:', len(data)); ag = [r for r in data if r['rule_type'] == 'ad_group']; print('Ad group rules:', len(ag))"
```
**Expected output:**
```
Total rules: 22-24
Ad group rules: 3-5
```

**Test B: Constitution Validation (5 min)**
Create and run validation script:
```python
import json

data = json.load(open('act_autopilot/rules_config.json'))
ad_group_rules = [r for r in data if r['rule_type'] == 'ad_group']

print(f"Validating {len(ad_group_rules)} ad group rules...")
violations = []

for rule in ad_group_rules:
    rid = rule['rule_id']
    
    # Check cooldown
    if rule['cooldown_days'] < 7:
        violations.append(f"{rid}: cooldown_days {rule['cooldown_days']} < 7")
    
    # Check monitoring
    if rule['monitoring_days'] < 7:
        violations.append(f"{rid}: monitoring_days {rule['monitoring_days']} < 7")
    
    # Check action magnitude (if applicable)
    if rule['action_direction'] in ['increase_bid', 'decrease_bid']:
        mag = rule['action_magnitude']
        if rule['action_direction'] == 'increase_bid' and mag > 20:
            violations.append(f"{rid}: increase magnitude {mag}% > 20%")
        if rule['action_direction'] == 'decrease_bid' and mag > 30:
            violations.append(f"{rid}: decrease magnitude {mag}% > 30%")

if violations:
    print("❌ VIOLATIONS FOUND:")
    for v in violations:
        print(f"  - {v}")
else:
    print("✅ All rules Constitution-compliant")
```

**Test C: Dashboard Integration (2 min)**
```powershell
python -m act_dashboard.app
```
- Navigate to Ad Groups page
- Click Rules tab
- Verify tab label shows "Rules (3-5)" depending on count
- Note: Rules won't display yet (need ad_group_rules_tab.html component)
- **Expected:** Tab label correct, tab content blank (component not created yet)

**Test D: Flask Startup (1 min)**
- Verify Flask starts without errors
- Check PowerShell output for successful route registration
- No JSON parsing errors

---

## POTENTIAL ISSUES

### Common Pitfalls to Avoid

**Issue 1: Column Name Mismatches**
- **Problem:** Brief uses generic names (quality_score, cpa), actual DB column might differ
- **Solution:** DESCRIBE ro.analytics.ad_group_daily before writing rules
- **Prevention:** Always verify actual column names in database schema

**Issue 2: Ad Group vs Keyword Confusion**
- **Problem:** Ad group rules might accidentally use keyword-level metrics
- **Solution:** Ad groups aggregate keyword performance - use ad group level metrics only
- **Prevention:** Double-check metric availability at ad group level

**Issue 3: Two-Condition Logic**
- **Problem:** Forgetting to set condition_2_* fields to null for single-condition rules
- **Solution:** If only one condition needed, all condition_2_* = null
- **Prevention:** Review keyword rules for pattern

**Issue 4: Timestamp Format**
- **Problem:** Incorrect timestamp format breaks JSON parsing
- **Solution:** Use exact format "2026-02-26T00:00:00" (ISO 8601)
- **Prevention:** Copy timestamp format from existing rules

**Issue 5: Pause vs Bid Adjustment**
- **Problem:** Ad groups don't have bids directly (keywords do)
- **Solution:** Ad groups can only be paused/flagged, not bid-adjusted
- **Prevention:** Use action_direction: "pause" or "flag" only (not increase_bid/decrease_bid)

### Known Gotchas

**Gotcha 1: Quality Score Availability**
- Ad group QS is average of keyword QS
- May be null for new ad groups
- Handle with QS + minimum impressions/clicks requirement

**Gotcha 2: Search Impression Share**
- IS metrics may be null for low-volume ad groups
- Add minimum impressions threshold (e.g., ≥100)

**Gotcha 3: Budget Pacing Flags**
- Campaign-level metric (pace_over_cap_detected)
- Can be used in ad group rules but references campaign data
- Acceptable for Scenario 6 type rules

---

## HANDOFF REQUIREMENTS

### Documentation

**Create CHAT_43_SUMMARY.md:**
- Executive summary
- All 3-5 rules with specifications
- Constitution compliance results
- Testing summary
- Time breakdown

**Create CHAT_43_HANDOFF.md:**
- Complete technical details
- All rule specifications (full JSON)
- Key decisions made
- Issues encountered + solutions
- Testing results (all tests)
- Git commit message (prepared)
- Future enhancements

### Git

**Prepare commit message** (use template):
```
feat: Add 3-5 ad group optimization rules to rules_config.json

Ad Group Rules - Constitution-compliant ad group-level optimizations

Rules Created:
- ad_group_1: [Name] ([conditions], [action])
- ad_group_2: [Name] ([conditions], [action])
- ad_group_3: [Name] ([conditions], [action])
[etc.]

Constitution Compliance:
- All cooldowns ≥7 days (7-14 range)
- All monitoring ≥7 days (7-14 range)
- Action magnitudes within limits (pause/flag only)
- All blanket scope (campaign_id=null)
- Risk levels: X low, Y medium, Z high

Testing:
- JSON validation: PASS (valid format, all fields present)
- Constitution validation: PASS (all rules compliant)
- Dashboard integration: PASS (Ad Groups tab shows "Rules (X)")

Files Modified:
- act_autopilot/rules_config.json (+XXX lines, X rules)

Time: X hours
Chat: 43
```

### Delivery

**Copy files to /mnt/user-data/outputs/:**
- rules_config.json (updated)
- CHAT_43_SUMMARY.md
- CHAT_43_HANDOFF.md

**Use present_files tool** to deliver all 3 files

**Await Master review** before git commit

---

## ESTIMATED TIME BREAKDOWN

- Setup & reading: 15 min
- 5 Questions to Master: 10 min
- Build plan creation: 15 min
- Master approval wait: 5 min
- Rule creation (3-5 rules): 90-120 min
- Testing (4 tests): 15 min
- Documentation (2 files): 45-60 min
- **Total: 3h 15min - 4h 15min**

**Estimate: 4-6 hours** (includes buffer for iterations)

---

## WORKFLOW REMINDER

**MANDATORY STEPS (from CHAT_WORKING_RULES.md):**

**STEP 1:** Read all 6 files from /mnt/project/ using view tool:
- CHAT_43_BRIEF.md (this file)
- PROJECT_ROADMAP.md
- CHAT_WORKING_RULES.md
- MASTER_KNOWLEDGE_BASE.md
- DASHBOARD_PROJECT_PLAN.md
- WORKFLOW_GUIDE.md

**STEP 2:** Send 5 questions to Master Chat (STOP AND WAIT)

**STEP 3:** Send build plan to Master Chat (STOP AND WAIT)

**STEP 4:** Request rules_config.json upload when ready to edit

**STEP 5:** Implement rules incrementally (2 rules at a time)

**STEP 6:** Test after each batch

**STEP 7:** Create handoff docs

**STEP 8:** Deliver to Master for review

**NEVER skip steps. NEVER proceed without Master approval at Steps 2 and 3.**

---

## READY TO START

**Before proceeding:**
1. Read all 6 project files using view tool
2. Review existing rules_config.json structure
3. Write exactly 5 clarifying questions for Master
4. STOP and send questions
5. Wait for Master answers
6. Create detailed build plan
7. STOP and send build plan
8. Wait for Master approval
9. Begin implementation

**This is Chat 43. Time estimate: 4-6 hours. Let's build production-ready ad group rules.**
