# CHAT 44: AD RULES CREATION

**Estimated Time:** 4-6 hours  
**Dependencies:** Chat 43 (Ad Group Rules) complete  
**Priority:** HIGH

---

## 🚨 CRITICAL: READ THIS FIRST - MANDATORY WORKFLOW

### **NO FILE UPLOADS REQUIRED - NO CODEBASE ZIP**

**⚠️ IMPORTANT: DO NOT ASK FOR CODEBASE ZIP UPLOAD ⚠️**

The codebase is too large to upload as a ZIP file. You already have access to ALL project files through the Claude Project system.

**You have access to ALL project files in `/mnt/project/`**

Use the `view` tool to read:
- `/mnt/project/MASTER_CHAT_5_0_HANDOFF.md`
- `/mnt/project/WORKFLOW_TEMPLATES.md`
- `/mnt/project/CHAT_WORKING_RULES.md`
- `/mnt/project/PROJECT_ROADMAP.md`
- `/mnt/project/MASTER_KNOWLEDGE_BASE.md`
- `/mnt/project/DETAILED_WORK_LIST.md`
- `/mnt/project/WORKFLOW_GUIDE.md`
- `/mnt/project/DASHBOARD_PROJECT_PLAN.md`

**You can also access the current rules_config.json through project knowledge:**
- Location in knowledge base: Referenced in MASTER_KNOWLEDGE_BASE.md
- Contains 23 existing rules (13 campaign + 6 keyword + 4 ad_group)
- Study the structure from previous chats (Chat 42, Chat 43)

**Christopher will ONLY upload this brief (CHAT_44_BRIEF.md). Everything else is already in your context.**

**When you're ready to EDIT rules_config.json (after build plan approval), THEN request the current version for editing.**

---

### **MANDATORY 3-STEP WORKFLOW (NON-NEGOTIABLE)**

**⚠️ YOU MUST CONFIRM YOU UNDERSTAND THESE RULES BEFORE PROCEEDING ⚠️**

**STEP 1: Read all project files using view tool**
- Read ALL 8 files listed above from `/mnt/project/`
- Study existing rules_config.json structure from knowledge base
- Review Chat 42 and Chat 43 patterns (successful precedents)

**STEP 2: Send EXACTLY 5 questions to Master Chat**
- Format: "5 QUESTIONS FOR MASTER CHAT"
- Must be specific, answerable questions
- Cannot be answered by reading the brief
- **STOP AND WAIT for Master's answers**
- Do NOT proceed until you receive answers

**STEP 3: Create detailed build plan**
- Format: "DETAILED BUILD PLAN FOR MASTER CHAT REVIEW"
- Include exact JSON structure for all rules
- Specify column names, operators, values
- Show implementation order (2 rules at a time)
- Testing approach at each step
- **STOP AND WAIT for Master's approval**
- Do NOT implement until Master approves

**STEP 4: Only after approval → Request rules_config.json upload**
- **DO NOT request this until build plan is approved**
- At this point, Christopher will upload the current rules_config.json for editing
- Then implement ONE rule at a time
- Test after EACH rule
- Get user validation before proceeding

**WHY THIS ORDER:** You need to study the existing structure first (from project files), create your build plan, get it approved, THEN get the current file for editing. Don't ask for it upfront.

---

### **CONFIRM YOUR UNDERSTANDING**

**Before you read ANY project files, respond with:**

```
✅ WORKFLOW UNDERSTOOD

I confirm I will:
1. Read all 8 project files from /mnt/project/ (NO codebase ZIP needed)
2. Send EXACTLY 5 questions and WAIT for Master answers
3. Create detailed build plan and WAIT for Master approval
4. Only AFTER approval: request rules_config.json (not before)
5. Implement incrementally with testing after each rule

I will NOT ask for codebase ZIP upload (files already in project).
I will NOT skip any steps.
I will NOT proceed without Master approval at Steps 2 and 3.

Ready to begin STEP 1.
```

**Only after confirming will you proceed to read project files.**

---

## CONTEXT

**What's been done:**
- Chat 26 (M5): Created 13 campaign rules in rules_config.json
- Chat 42: Added 6 keyword rules
- Chat 43: Added 4 ad group rules
- **Current total: 23 rules** (13 campaign + 6 keyword + 4 ad_group)
- Git commit 4a9cdbe (Chat 43 complete)

**Why this task is needed:**
Ads are the final user touchpoint before conversion. Poor-performing ads waste budget on low CTR (expensive clicks), weak messaging (low CVR), or poor ad strength (Quality Score penalty). Ad-level rules enable automated creative optimization and quality enforcement.

**How it fits into the bigger picture:**
This completes the third of four rule types needed:
1. ✅ Campaign rules (13) - Chat 26
2. ✅ Keyword rules (6) - Chat 42
3. ✅ Ad Group rules (4) - Chat 43
4. 🎯 **Ad rules (3-5) - THIS CHAT**
5. 📋 Shopping rules (14) - Chat 45

After all rules created → extend recommendations_engine.py → add Rules tabs to all pages → recommendations tabs to all pages → live Google Ads connection.

---

## OBJECTIVE

Create 3-5 ad optimization rules in `rules_config.json` based on Christopher's 16 years of Google Ads expertise, focusing on pausing poor performers, scaling high performers, and enforcing ad quality standards.

---

## REQUIREMENTS

### Deliverables

**1. rules_config.json (modify)**
- Location: `C:\Users\User\Desktop\gads-data-layer\act_autopilot\rules_config.json`
- Add 3-5 ad rules (ad_1 through ad_5)
- All 24 required fields per rule
- Constitution-compliant (cooldowns ≥7, monitoring ≥7, magnitude within limits)
- Total rules after completion: 26-28 (13 campaign + 6 keyword + 4 ad_group + 3-5 ad)

**2. CHAT_44_SUMMARY.md (create)**
- Location: `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_44_SUMMARY.md`
- Executive summary of rules created
- Constitution compliance verification
- Testing results

**3. CHAT_44_HANDOFF.md (create)**
- Location: `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_44_HANDOFF.md`
- Complete technical details
- Implementation decisions
- Future enhancements

---

### Technical Constraints

**Rule Structure (24 required fields):**
```json
{
  "rule_id": "ad_1",
  "rule_type": "ad",
  "rule_number": 1,
  "display_name": "Short name for UI",
  "name": "AD-001: Full descriptive name",
  "scope": "blanket",
  "campaign_id": null,
  "condition_metric": "ctr",
  "condition_operator": "lt",
  "condition_value": 1.0,
  "condition_unit": "percentage",
  "condition_2_metric": "impressions",
  "condition_2_operator": "gte",
  "condition_2_value": 500.0,
  "condition_2_unit": "count",
  "action_direction": "pause",
  "action_magnitude": null,
  "risk_level": "low",
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
  - Decreases: ≤-30%
  - Pause/flag actions: null
- `enabled`: true (all rules active)
- `scope`: "blanket" (all campaigns) or "specific" (single campaign)

**Valid Operators:**
- "gte" (≥), "gt" (>), "lte" (≤), "lt" (<), "eq" (=)

**Valid Action Directions for Ads:**
- "pause", "flag"
- **NOTE:** Ads don't have bids (keywords do), so NO increase_bid/decrease_bid

**Valid Risk Levels:**
- "low", "medium", "high"

---

### Ad Optimization Scenarios

**Based on Christopher's 16 years of expertise, here are 8 potential scenarios. Select 3-5 for implementation:**

**Scenario 1: Pause Low CTR Ads**
- Logic: CTR <1% AND impressions ≥500
- Action: pause
- Rationale: Low CTR wastes budget on expensive clicks, signals poor relevance
- Risk: Low (clear underperformer)

**Scenario 2: Pause Poor Ad Strength**
- Logic: ad_strength = 'POOR' AND impressions ≥1000
- Action: pause
- Rationale: Google flags as POOR - needs rewrite
- Risk: Low (Google's own quality signal)

**Scenario 3: Flag Average Ad Strength**
- Logic: ad_strength = 'AVERAGE' AND impressions ≥1000
- Action: flag for improvement
- Rationale: Room for improvement without being destructive
- Risk: Low (non-destructive flag)

**Scenario 4: Pause Zero-Conversion High-Impression Ads**
- Logic: conversions = 0 AND impressions ≥2000
- Action: pause
- Rationale: High visibility but no conversion value
- Risk: Low (no conversion value to protect)

**Scenario 5: Flag Low CVR Ads**
- Logic: CVR <1% AND clicks ≥100
- Action: flag for review
- Rationale: Getting clicks but not converting
- Risk: Medium (may need messaging/landing page review)

**Scenario 6: Pause High CPC Low CTR Ads**
- Logic: CPC >£5 AND CTR <0.5% AND clicks ≥50
- Action: pause
- Rationale: Expensive clicks + poor engagement = budget waste
- Risk: Low (clear inefficiency)

**Scenario 7: Flag ROAS Underperformers**
- Logic: ROAS <2.0 AND conversions ≥10
- Action: flag for review
- Rationale: Consistent underperformance (50% of 4.0 target)
- Risk: Medium (may have strategic value)

**Scenario 8: Pause Disapproved/Limited Ads**
- Logic: ad_status IN ('DISAPPROVED', 'LIMITED')
- Action: pause (already non-serving)
- Rationale: Clean up non-serving ads automatically
- Risk: Low (already not serving)

**Your task: Select 3-5 scenarios in 5 Questions stage with Master approval.**

**Recommended starting point (pending Master approval):**
- 2 pause rules (clear underperformers)
- 2 flag rules (needs review)
- 1 quality enforcement rule

---

### Design Specifications

**Recommended Rule Count: 4 rules**
- 2 pause rules (budget protection)
- 1 flag rule (strategic review)
- 1 quality rule (ad strength)

**Suggested Selection (pending Master approval in 5 Questions):**
- Scenario 1: Pause Low CTR (clear underperformer)
- Scenario 2: Pause Poor Ad Strength (Google quality signal)
- Scenario 3: Flag Average Ad Strength (improvement opportunity)
- Scenario 7: Flag ROAS Underperformers (strategic review)

**But defer final selection to 5 Questions stage - get Master approval first.**

---

## REFERENCE FILES

**Similar Completed Work:**
- `act_autopilot/rules_config.json` - Contains 23 existing rules
  - Study ad_group rules (ad_group_1 through ad_group_4) for recent pattern
  - Study keyword rules (keyword_1 through keyword_6) for structure
  - All have proper Constitution compliance, timestamps
- `docs/CHAT_43_SUMMARY.md` - Successful ad group rules implementation
- `docs/CHAT_43_HANDOFF.md` - Complete technical details from Chat 43
- `docs/CHAT_42_SUMMARY.md` - Successful keyword rules implementation

**Documentation to Consult:**
- `docs/CHAT_WORKING_RULES.md` - Mandatory workflow rules
- `docs/PROJECT_ROADMAP.md` - Overall project status
- `docs/MASTER_KNOWLEDGE_BASE.md` - Lessons learned, architecture

**Database Tables:**
- `ro.analytics.ad_daily` - Contains ad performance data
  - Likely columns: ctr, cvr, cpc, cost, conversions, impressions, clicks, ad_strength
  - Use DESCRIBE or trust column names from brief
  - **IMPORTANT:** Verify ad_strength column exists and values in 5 Questions

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
- [ ] 10. All rule_id values unique (ad_1, ad_2, ad_3, etc.)
- [ ] 11. All rule_type = "ad"
- [ ] 12. All scope = "blanket" (unless Master approves campaign-specific)

---

## TESTING INSTRUCTIONS

### Step-by-Step Testing

**Test A: JSON Validation (after EACH rule added)**
```powershell
cd C:\Users\User\Desktop\gads-data-layer
.\.venv\Scripts\Activate.ps1
python -c "import json; data = json.load(open('act_autopilot/rules_config.json')); print('Total rules:', len(data)); ad_rules = [r for r in data if r['rule_type'] == 'ad']; print('Ad rules:', len(ad_rules))"
```

**Expected progression:**
- After ad_1: Total rules: 24, Ad rules: 1
- After ad_2: Total rules: 25, Ad rules: 2
- After ad_3: Total rules: 26, Ad rules: 3
- After ad_4: Total rules: 27, Ad rules: 4
- (If creating 5): After ad_5: Total rules: 28, Ad rules: 5

**Test B: Constitution Validation**
Run validation script (create one similar to Chat 43) checking:
- All cooldown_days ≥7
- All monitoring_days ≥7
- All action_magnitude = null (pause/flag only)
- All risk_level valid

**Test C: Dashboard Integration**
```powershell
python -m act_dashboard.app
```
- Navigate to Ads page
- Click Rules tab
- Verify tab label shows "Rules (X)" where X = number of ad rules
- Note: Rules won't display yet (need ad_rules_tab.html component later)
- **Expected:** Tab label correct, tab content blank

**Test D: Flask Startup**
- Verify Flask starts without errors
- No JSON parsing errors

---

## POTENTIAL ISSUES

### Common Pitfalls to Avoid

**Issue 1: Column Name - ad_strength**
- **Problem:** ad_strength column may not exist in current schema
- **Solution:** Ask in 5 Questions if ad_strength column exists
- **Alternative:** If not exists, defer Scenarios 2 and 3 to future schema update

**Issue 2: ad_status vs approval_status**
- **Problem:** Column name for ad status may vary
- **Solution:** Verify in 5 Questions what the actual column name is
- **Prevention:** Don't implement Scenario 8 without confirming column exists

**Issue 3: Ads Don't Have Bids**
- **Problem:** Accidentally using increase_bid/decrease_bid
- **Solution:** Ads can ONLY be paused or flagged
- **Prevention:** action_direction must be "pause" or "flag" (never increase_bid/decrease_bid)

**Issue 4: CTR/CVR Threshold Selection**
- **Problem:** Thresholds may be too aggressive or too lenient
- **Solution:** Get Master approval on exact thresholds in build plan
- **Prevention:** Use conservative thresholds (CTR <1%, CVR <1%) to avoid false positives

**Issue 5: Two-Condition Logic**
- **Problem:** Forgetting minimum impression/click thresholds
- **Solution:** All rules need condition_2 for statistical significance
- **Prevention:** Single metric + minimum data requirement (e.g., "CTR <1% AND impressions ≥500")

### Known Gotchas

**Gotcha 1: Ad Strength Values**
- Values: 'POOR', 'AVERAGE', 'GOOD', 'EXCELLENT', NULL
- String comparison: use "eq" operator
- Example: condition_operator: "eq", condition_value: "POOR"

**Gotcha 2: Ad Status Values**
- May include: 'ENABLED', 'PAUSED', 'REMOVED', 'DISAPPROVED', 'LIMITED'
- If Scenario 8 selected, verify exact string values

**Gotcha 3: CVR vs CTR**
- CVR = conversions / clicks (post-click metric)
- CTR = clicks / impressions (pre-click metric)
- Different thresholds: CVR typically <5%, CTR typically <2%

---

## HANDOFF REQUIREMENTS

### Documentation

**Create CHAT_44_SUMMARY.md:**
- Executive summary
- All 3-5 rules with specifications
- Constitution compliance results
- Testing summary
- Time breakdown

**Create CHAT_44_HANDOFF.md:**
- Complete technical details
- All rule specifications (full JSON)
- Key decisions made
- Issues encountered + solutions
- Testing results (all tests)
- Git commit message (prepared)
- Future enhancements

### Git

**Prepare commit message** (use template from Chat 43)

### Delivery

**Copy files to /mnt/user-data/outputs/:**
- rules_config.json (updated)
- CHAT_44_SUMMARY.md
- CHAT_44_HANDOFF.md

**Use present_files tool** to deliver all 3 files

**Await Master review** before git commit

---

## ESTIMATED TIME BREAKDOWN

- Setup & reading project files: 20 min
- 5 Questions to Master: 10 min
- Build plan creation: 15 min
- Master approval wait: 5 min
- Rule creation (3-5 rules): 90-120 min
- Testing (step-by-step): 20 min
- Documentation (2 files): 45-60 min
- **Total: 3h 25min - 4h 30min**

**Estimate: 4-6 hours** (includes buffer)

---

## MANDATORY WORKFLOW CONFIRMATION (REPEAT)

**Before you do ANYTHING:**

**Confirm you understand by responding:**
```
✅ WORKFLOW UNDERSTOOD

I confirm I will:
1. Read all 8 project files from /mnt/project/ using view tool (NO codebase ZIP)
2. Send EXACTLY 5 questions and WAIT for Master answers
3. Create detailed build plan and WAIT for Master approval
4. Only AFTER approval: request rules_config.json and implement

I will NOT ask for codebase ZIP (already in project).
I will NOT skip steps.
I will NOT proceed without Master approval.

Ready to begin STEP 1: Reading project files.
```

**Only after this confirmation will you proceed.**

---

## READY TO START

**Your first action must be:**
1. ✅ Confirm workflow understanding (above)
2. Read all 8 files from `/mnt/project/` using view tool
3. Review existing rules in knowledge base
4. Write exactly 5 clarifying questions for Master
5. STOP and send questions
6. Wait for answers
7. Create detailed build plan
8. STOP and send build plan
9. Wait for approval
10. Request rules_config.json upload
11. Begin implementation

**This is Chat 44. Time estimate: 4-6 hours. Let's build production-ready ad rules.**

**NO FILE UPLOADS NEEDED EXCEPT THIS BRIEF - EVERYTHING ELSE IS IN /mnt/project/**
