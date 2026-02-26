# CHAT 45: SHOPPING RULES CREATION (MIGRATION FROM PYTHON TO JSON)

**Estimated Time:** 6-10 hours  
**Dependencies:** Chat 44 (Ad Rules) complete  
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
- Contains 27 existing rules (13 campaign + 6 keyword + 4 ad_group + 4 ad)
- Study the structure from previous chats (Chat 42, 43, 44)

**Christopher will ONLY upload this brief (CHAT_45_BRIEF.md). Everything else is already in your context.**

**When you're ready to EDIT rules_config.json (after build plan approval), THEN request the current version for editing.**

---

### **MANDATORY 3-STEP WORKFLOW (NON-NEGOTIABLE)**

**⚠️ YOU MUST CONFIRM YOU UNDERSTAND THESE RULES BEFORE PROCEEDING ⚠️**

**STEP 1: Read all project files using view tool**
- Read ALL 8 files listed above from `/mnt/project/`
- Study existing rules_config.json structure from knowledge base
- Review Chat 42, 43, 44 patterns (successful precedents)
- **CRITICAL:** Review Chat 12 documentation about existing Shopping rules

**STEP 2: Send EXACTLY 5 questions to Master Chat**
- Format: "5 QUESTIONS FOR MASTER CHAT"
- Must be specific, answerable questions
- Cannot be answered by reading the brief
- **STOP AND WAIT for Master's answers**
- Do NOT proceed until you receive answers

**STEP 3: Create detailed build plan**
- Format: "DETAILED BUILD PLAN FOR MASTER CHAT REVIEW"
- Include exact JSON structure for ALL ~14 rules
- Specify column names, operators, values
- Show implementation order (2-3 rules at a time)
- Testing approach at each step
- **STOP AND WAIT for Master's approval**
- Do NOT implement until Master approves

**STEP 4: Only after approval → Request rules_config.json upload**
- **DO NOT request this until build plan is approved**
- At this point, Christopher will upload the current rules_config.json for editing
- Then implement 2-3 rules at a time
- Test after EACH batch
- Get user validation before proceeding

**WHY THIS ORDER:** You need to study the existing structure first (from project files), understand the Chat 12 Shopping rules, create your migration plan, get it approved, THEN get the current file for editing. Don't ask for it upfront.

---

### **CONFIRM YOUR UNDERSTANDING**

**Before you read ANY project files, respond with:**

```
✅ WORKFLOW UNDERSTOOD

I confirm I will:
1. Read all 8 project files from /mnt/project/ (NO codebase ZIP needed)
2. Review Chat 12 Shopping rules documentation
3. Send EXACTLY 5 questions and WAIT for Master answers
4. Create detailed build plan for ALL ~14 rules and WAIT for Master approval
5. Only AFTER approval: request rules_config.json (not before)
6. Implement 2-3 rules at a time with testing after each batch

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
- Chat 43: Added 4 ad_group rules
- Chat 44: Added 4 ad rules
- **Current total: 27 rules**
- Git commit 52b042e (Chat 44 complete)

**Chat 12 - Existing Shopping Module (CRITICAL CONTEXT):**
- **Location:** `act_dashboard/routes/shopping.py` (from Chat 12)
- **Size:** 3,800 lines of Python code
- **Rules:** 14 Shopping-specific optimization rules implemented as Python functions
- **UI:** 4-tab interface (Campaigns, Products, Product Groups, Recommendations)
- **Status:** Fully functional but rules NOT in rules_config.json format

**Why this task is needed:**
The Shopping module (Chat 12) was built BEFORE the unified rules_config.json system (Chat 26 M5). Shopping rules are currently hardcoded in Python functions. This chat migrates those 14 rules from Python → JSON format to:
1. Unify all rules in one configuration file
2. Enable dynamic rule editing via Rules tab UI
3. Integrate with recommendations_engine.py workflow
4. Follow Constitution framework consistently

**This is a MIGRATION task, not new rule creation.**

---

## OBJECTIVE

Migrate 14 existing Shopping optimization rules from Python functions (shopping.py) to JSON format (rules_config.json), preserving all existing logic while ensuring Constitution compliance.

---

## REQUIREMENTS

### Deliverables

**1. rules_config.json (modify)**
- Location: `C:\Users\User\Desktop\gads-data-layer\act_autopilot\rules_config.json`
- Add ~14 shopping rules (shopping_1 through shopping_14)
- All 24 required fields per rule
- Constitution-compliant (cooldowns ≥7, monitoring ≥7, magnitude within limits)
- Total rules after completion: ~41 (13 campaign + 6 keyword + 4 ad_group + 4 ad + 14 shopping)

**2. CHAT_45_SUMMARY.md (create)**
- Location: `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_45_SUMMARY.md`
- Executive summary of migration
- All ~14 rules with specifications
- Constitution compliance verification
- Testing results

**3. CHAT_45_HANDOFF.md (create)**
- Location: `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_45_HANDOFF.md`
- Complete technical details
- Migration decisions
- Python → JSON mapping documentation
- Future enhancements

---

### Technical Constraints

**Rule Structure (24 required fields):**
```json
{
  "rule_id": "shopping_1",
  "rule_type": "shopping",
  "rule_number": 1,
  "display_name": "Short name for UI",
  "name": "SHOPPING-001: Full descriptive name",
  "scope": "blanket",
  "campaign_id": null,
  "condition_metric": "roas",
  "condition_operator": "lt",
  "condition_value": 2.0,
  "condition_unit": "ratio",
  "condition_2_metric": "conversions",
  "condition_2_operator": "gte",
  "condition_2_value": 10.0,
  "condition_2_unit": "count",
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
  - Decreases: ≤-30%
  - Pause/flag actions: null
- `enabled`: true (all rules active)
- `scope`: "blanket" (all campaigns) or "specific" (single campaign)

**Valid Operators:**
- "gte" (≥), "gt" (>), "lte" (≤), "lt" (<), "eq" (=)

**Valid Action Directions for Shopping:**
- "pause", "flag", "increase", "decrease"
- **Shopping can have budget/bid adjustments at campaign level**

**Valid Risk Levels:**
- "low", "medium", "high"

---

### Chat 12 Shopping Rules (TO BE MIGRATED)

**From MASTER_KNOWLEDGE_BASE.md and PROJECT_ROADMAP.md, Chat 12 created 14 Shopping rules:**

These rules are currently Python functions. You need to convert them to JSON format. The exact logic is in `act_dashboard/routes/shopping.py` but here are the 14 rule categories:

**BUDGET RULES (2-3 rules):**
1. Increase budget for high ROAS Shopping campaigns
2. Decrease budget for low ROAS Shopping campaigns
3. Pause budget-wasting campaigns (high cost, zero conversions)

**PRODUCT PERFORMANCE RULES (3-4 rules):**
4. Pause low ROAS products
5. Flag underperforming product groups
6. Pause products with high cost and zero conversions
7. Flag products with declining ROAS trend

**FEED ERROR RULES (2-3 rules):**
8. Flag campaigns with high feed error count
9. Pause products with critical feed errors
10. Alert on out-of-stock products with active campaigns

**IMPRESSION SHARE RULES (2-3 rules):**
11. Flag campaigns losing impression share to budget
12. Flag campaigns with low search impression share
13. Recommend budget increase for IS-constrained campaigns

**OPTIMIZATION SCORE RULES (1-2 rules):**
14. Flag campaigns with low optimization score

**IMPORTANT:** The exact conditions, thresholds, and actions are in the Python code. You'll need to translate Python logic → JSON conditions in your build plan.

---

### Design Specifications

**Recommended Rule Count: 12-14 rules**
- Start with core rules (budget, ROAS, feed errors)
- Add IS and optimization rules if time permits
- Prioritize rules that protect budget and flag issues

**Migration Strategy:**
1. Review Python functions in shopping.py (if accessible)
2. Extract condition logic (if X > Y then action Z)
3. Map to JSON condition_metric + operator + value
4. Preserve thresholds from Python code
5. Add Constitution-compliant cooldowns/monitoring

**Defer final rule count to 5 Questions stage - get Master approval.**

---

## REFERENCE FILES

**Critical Reference:**
- `docs/CHAT_12_SUMMARY.md` or `docs/CHAT_12_HANDOFF.md` (if exists in knowledge base)
  - Contains details of 14 Shopping rules
  - May have exact thresholds and conditions
  - Check MASTER_KNOWLEDGE_BASE.md for Chat 12 details

**Similar Completed Work:**
- `act_autopilot/rules_config.json` - Contains 27 existing rules
  - Study campaign rules (budget/bid patterns)
  - Study ad_group/keyword/ad rules (pause/flag patterns)
  - All have proper Constitution compliance
- `docs/CHAT_44_SUMMARY.md` - Most recent rule creation
- `docs/CHAT_43_HANDOFF.md` - Ad group rules pattern

**Documentation to Consult:**
- `docs/CHAT_WORKING_RULES.md` - Mandatory workflow rules
- `docs/PROJECT_ROADMAP.md` - Chat 12 Shopping module details
- `docs/MASTER_KNOWLEDGE_BASE.md` - Chat 12 Shopping rules, lessons learned

**Database Tables:**
- `ro.analytics.shopping_campaign_daily` - Shopping campaign performance
- `ro.analytics.shopping_product_daily` - Product-level performance
- Likely columns: roas, cost, conversions, impressions, clicks, feed_errors, out_of_stock, search_impression_share, optimization_score
- **IMPORTANT:** Verify exact column names in 5 Questions

---

## SUCCESS CRITERIA

All 12 criteria must pass for approval (same as Chats 42-44):

### JSON Structure & Validity
- [ ] 1. Valid JSON format (no syntax errors)
- [ ] 2. All 24 required fields present per rule
- [ ] 3. Correct data types (strings, numbers, booleans, null)
- [ ] 4. Proper operator format ("gte", "lt", "gt", "eq")
- [ ] 5. ISO 8601 timestamp format (YYYY-MM-DDTHH:MM:SS)

### Constitution Compliance
- [ ] 6. All cooldown_days ≥7 (range: 7-14 days)
- [ ] 7. All monitoring_days ≥7 (range: 7-14 days)
- [ ] 8. Action magnitudes within limits (≤+20% increase, ≤-30% decrease, null for pause/flag)
- [ ] 9. All risk_level values valid ("low", "medium", "high")

### Implementation Correctness
- [ ] 10. All rule_id values unique (shopping_1, shopping_2, etc.)
- [ ] 11. All rule_type = "shopping"
- [ ] 12. All scope = "blanket" (unless Master approves campaign-specific)

---

## TESTING INSTRUCTIONS

### Step-by-Step Testing (After EACH batch of 2-3 rules)

**Test A: JSON Validation**
```powershell
cd C:\Users\User\Desktop\gads-data-layer
.\.venv\Scripts\Activate.ps1
python -c "import json; data = json.load(open('act_autopilot/rules_config.json')); print('Total rules:', len(data)); shopping_rules = [r for r in data if r['rule_type'] == 'shopping']; print('Shopping rules:', len(shopping_rules))"
```

**Expected progression:**
- After batch 1 (3 rules): Total rules: 30, Shopping rules: 3
- After batch 2 (3 rules): Total rules: 33, Shopping rules: 6
- After batch 3 (3 rules): Total rules: 36, Shopping rules: 9
- After batch 4 (3 rules): Total rules: 39, Shopping rules: 12
- After batch 5 (2 rules): Total rules: 41, Shopping rules: 14

**Test B: Constitution Validation**
Run validation script checking:
- All cooldown_days ≥7
- All monitoring_days ≥7
- All action_magnitude within limits
- All risk_level valid

**Test C: Dashboard Integration**
```powershell
python -m act_dashboard.app
```
- Navigate to Shopping page
- Click Rules tab
- Verify tab label shows "Rules (X)" where X = number of shopping rules
- Note: Rules won't display yet (need shopping_rules_tab.html component later)

**Test D: Flask Startup**
- Verify Flask starts without errors
- No JSON parsing errors

---

## POTENTIAL ISSUES

### Common Pitfalls to Avoid

**Issue 1: Python Logic → JSON Conditions**
- **Problem:** Python code may have complex if/else logic
- **Solution:** Simplify to primary condition + secondary data threshold
- **Example:** Python `if roas < 2.0 and conversions >= 10 and cost > 100` → JSON uses condition_1 (roas <2.0) + condition_2 (conversions ≥10), document cost threshold separately

**Issue 2: Shopping-Specific Columns**
- **Problem:** Column names may differ from campaign/keyword/ad tables
- **Solution:** Verify column names in 5 Questions (feed_errors, out_of_stock, optimization_score)
- **Prevention:** Don't assume column names - ask Master

**Issue 3: Feed Error Thresholds**
- **Problem:** "High feed error count" is subjective
- **Solution:** Get Master approval on exact threshold (e.g., feed_errors ≥10)
- **Prevention:** Include threshold decisions in build plan

**Issue 4: Product vs Campaign Rules**
- **Problem:** Some rules apply to products, some to campaigns
- **Solution:** All rules in rules_config.json are campaign-level (apply to Shopping campaigns)
  - Product-level optimizations are handled within campaign optimization
  - Rule scope is campaign, not individual products

**Issue 5: Rule Overlap with Campaign Rules**
- **Problem:** Budget rules may duplicate campaign budget_1/budget_2
- **Solution:** Shopping-specific thresholds or additional conditions
- **Example:** Shopping budget rules may key off ROAS + feed_errors (Shopping-specific)

### Known Gotchas

**Gotcha 1: Shopping Campaign Types**
- Standard Shopping vs Smart Shopping vs Performance Max (Shopping)
- Rules may need to distinguish between types
- Ask in 5 Questions if type filtering needed

**Gotcha 2: Out of Stock Handling**
- Out of stock is a product-level metric
- Campaign-level rule: "If out_of_stock_count > X% of products"
- Get threshold from Master

**Gotcha 3: Optimization Score**
- Google-provided score (0-100%)
- Low score indicates missed optimization opportunities
- Threshold ~60-70% for flagging

---

## HANDOFF REQUIREMENTS

### Documentation

**Create CHAT_45_SUMMARY.md:**
- Executive summary of migration
- All 12-14 rules with specifications
- Python → JSON mapping table
- Constitution compliance results
- Testing summary
- Time breakdown

**Create CHAT_45_HANDOFF.md:**
- Complete technical details
- All rule specifications (full JSON)
- Migration decisions (how Python logic translated to JSON)
- Issues encountered + solutions
- Testing results (all tests)
- Git commit message (prepared)
- Future enhancements

### Git

**Prepare commit message** (use template from Chats 42-44)

### Delivery

**Copy files to /mnt/user-data/outputs/:**
- rules_config.json (updated)
- CHAT_45_SUMMARY.md
- CHAT_45_HANDOFF.md

**Use present_files tool** to deliver all 3 files

**Await Master review** before git commit

---

## ESTIMATED TIME BREAKDOWN

- Setup & reading project files: 30 min
- Review Chat 12 Shopping documentation: 20 min
- 5 Questions to Master: 15 min
- Build plan creation (14 rules): 30 min
- Master approval wait: 5 min
- Rule migration (14 rules, 2-3 at a time): 180-240 min
- Testing (5 batches): 30 min
- Documentation (2 files): 60-90 min
- **Total: 6h 10min - 8h 30min**

**Estimate: 6-10 hours** (includes buffer for complex migration)

---

## MANDATORY WORKFLOW CONFIRMATION (REPEAT)

**Before you do ANYTHING:**

**Confirm you understand by responding:**
```
✅ WORKFLOW UNDERSTOOD

I confirm I will:
1. Read all 8 project files from /mnt/project/ using view tool (NO codebase ZIP)
2. Review Chat 12 Shopping rules documentation thoroughly
3. Send EXACTLY 5 questions and WAIT for Master answers
4. Create detailed build plan for ALL ~14 rules and WAIT for Master approval
5. Only AFTER approval: request rules_config.json and implement

I will NOT ask for codebase ZIP (already in project).
I will NOT skip steps.
I will NOT proceed without Master approval.

Ready to begin STEP 1: Reading project files and reviewing Chat 12.
```

**Only after this confirmation will you proceed.**

---

## READY TO START

**Your first action must be:**
1. ✅ Confirm workflow understanding (above)
2. Read all 8 files from `/mnt/project/` using view tool
3. **Review Chat 12 documentation** (MASTER_KNOWLEDGE_BASE.md, PROJECT_ROADMAP.md)
4. Study existing Shopping rules in Python (if accessible)
5. Write exactly 5 clarifying questions for Master about:
   - Column names in Shopping tables
   - Exact thresholds from Chat 12 rules
   - Rule count approval (12 vs 14)
   - Any Shopping-specific Constitution considerations
   - Priority order for migration
6. STOP and send questions
7. Wait for answers
8. Create detailed build plan for ALL rules
9. STOP and send build plan
10. Wait for approval
11. Request rules_config.json upload
12. Begin implementation (2-3 rules at a time)

**This is Chat 45. Time estimate: 6-10 hours. Let's migrate Shopping rules to unified JSON format.**

**NO FILE UPLOADS NEEDED EXCEPT THIS BRIEF - EVERYTHING ELSE IS IN /mnt/project/**
