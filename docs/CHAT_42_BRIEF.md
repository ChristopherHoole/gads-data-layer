# CHAT 42: KEYWORD RULES CREATION - COMPREHENSIVE BRIEF

**Estimated Time:** 10-15 hours  
**Dependencies:** Chat 41 complete (Keywords page has Rules tab ready)  
**Priority:** HIGH  
**Brief Version:** 1.0  
**Created:** 2026-02-25

---

## 🎯 CONTEXT

### What's Been Done

**Chat 41 (Complete):**
- Keywords page now has Rules tab
- Tab shows "Rules (0)" (correct - no keyword rules exist yet)
- Tab opens to empty state with M5 card-based UI
- Ready to display rules when they exist in rules_config.json

**Current State:**
- `rules_config.json` has 13 campaign rules (Budget, Bid, Status)
- Keywords page functional but has 0 keyword-specific rules
- Recommendations engine doesn't evaluate keyword rules (will be Chat 43)
- No keyword recommendations generated (expected - no rules to evaluate)

### Why This Chat Matters

**Christopher has 16 years of Google Ads experience managing:**
- 200+ accounts
- £50+ million in ad spend
- Maximum 4 clients at a time (deep expertise per account)

**This chat translates that keyword optimization expertise into automated rules.**

---

## 🎯 OBJECTIVE

**Define 5-8 keyword optimization rules and add them to rules_config.json.**

Each rule must:
1. Address a real keyword optimization scenario
2. Follow Constitution safety guardrails
3. Use correct rules_config.json structure (18 fields)
4. Be testable with synthetic data
5. Align with Google Ads best practices

**Deliverable:** Updated `rules_config.json` with 5-8 new keyword rules (rule_type: 'keyword')

---

## 📋 KEYWORD OPTIMIZATION SCENARIOS

### **Based on Christopher's expertise, here are common keyword scenarios:**

### Scenario 1: High-Cost, Low-Performance Keywords
**Problem:** Keywords spending >£50 with 0 conversions (wasted spend)  
**Action:** Pause keyword OR reduce bid by 30-50%  
**Constitution:** 7-day data minimum, 14-day cooldown

### Scenario 2: Low Quality Score Keywords  
**Problem:** Keywords with QS <4 (poor relevance, high CPC)  
**Action:** Reduce bid by 20% OR pause if QS <3  
**Constitution:** 14-day data minimum, 14-day cooldown

### Scenario 3: High CPC Keywords (Above Target)
**Problem:** Keywords with CPC >150% of target CPA goal  
**Action:** Reduce bid by 10-20%  
**Constitution:** 7-day data minimum, 7-day cooldown

### Scenario 4: Low CTR Keywords
**Problem:** Keywords with CTR <1% and >100 impressions (poor relevance)  
**Action:** Pause keyword OR add to review list  
**Constitution:** 14-day data minimum, 14-day cooldown

### Scenario 5: High-Performing Keywords (Scale Opportunity)
**Problem:** Keywords with ROAS >6.0x, CVR >5%, low impression share  
**Action:** Increase bid by 10-20% to gain more volume  
**Constitution:** 14-day data minimum, 7-day cooldown, IS <70%

### Scenario 6: Budget-Constrained Keywords
**Problem:** Keywords losing impression share due to budget (IS lost to budget >20%)  
**Action:** Flag for budget increase recommendation at campaign level  
**Constitution:** 7-day data minimum, budget IS loss >20%

### Scenario 7: Match Type Optimization
**Problem:** Broad match keywords with high wasted spend from irrelevant searches  
**Action:** Suggest tightening to Phrase or Exact match  
**Constitution:** 30-day data minimum (need search term history)

### Scenario 8: Seasonal/Trend Keywords
**Problem:** Keywords with declining search volume or CVR trend  
**Action:** Pause temporarily OR reduce bid by 20%  
**Constitution:** 21-day trend data, >30% decline

**Worker should select 5-8 of these scenarios to implement as rules.**

---

## 📋 RULE STRUCTURE (18 REQUIRED FIELDS)

### **From Chat 26 M5 - rules_config.json format:**

```json
{
  "rule_id": "keyword_1",
  "rule_type": "keyword",
  "rule_number": 1,
  "display_name": "Pause High-Cost Zero-Conv Keywords",
  "name": "KEYWORD-001: Pause keywords spending >£50 with 0 conversions",
  
  "scope": "blanket",
  "campaign_id": null,
  
  "condition_metric": "cost",
  "condition_operator": ">=",
  "condition_value": 50.0,
  "condition_unit": "currency",
  
  "condition_2_metric": "conversions",
  "condition_2_operator": "=",
  "condition_2_value": 0,
  "condition_2_unit": "count",
  
  "action_direction": "pause",
  "action_magnitude": null,
  "risk_level": "low",
  "cooldown_days": 14,
  "monitoring_days": 7,
  "monitoring_minutes": 0,
  "enabled": true,
  
  "created_at": "2026-02-25T18:00:00Z",
  "updated_at": "2026-02-25T18:00:00Z"
}
```

### **Field Definitions:**

**Identity (5 fields):**
- `rule_id`: Unique ID (e.g., "keyword_1", "keyword_2")
- `rule_type`: MUST be "keyword" for all rules in this chat
- `rule_number`: Sequential (1, 2, 3, etc.)
- `display_name`: Short title for UI (3-6 words)
- `name`: Full description (starts with "KEYWORD-XXX:")

**Scope (2 fields):**
- `scope`: "blanket" (applies to all keywords) OR "specific" (requires campaign_id)
- `campaign_id`: Campaign ID if scope="specific", null if blanket

**Condition 1 (4 fields):**
- `condition_metric`: cost, conversions, ctr, cpc, quality_score, impressions, etc.
- `condition_operator`: ">", "<", ">=", "<=", "=", "!="
- `condition_value`: Number threshold
- `condition_unit`: "currency", "count", "percent", "score", null

**Condition 2 (4 fields):**
- `condition_2_metric`: Second metric (AND logic with condition 1)
- `condition_2_operator`: Same operators as condition 1
- `condition_2_value`: Number threshold
- `condition_2_unit`: Same units as condition 1

**Action (3 fields):**
- `action_direction`: "increase_bid", "decrease_bid", "pause", "enable", "flag_review"
- `action_magnitude`: Percentage change (e.g., 20 for +20%, -30 for -30%), null for pause/enable
- `risk_level`: "low", "medium", "high"

**Safety (4 fields):**
- `cooldown_days`: Days before same keyword can be changed again (7-14 typical)
- `monitoring_days`: Days to monitor after change before marking successful (7-14 typical)
- `monitoring_minutes`: Fast-test mode override (0 = disabled, use monitoring_days)
- `enabled`: true/false

**Timestamps (2 fields):**
- `created_at`: ISO 8601 timestamp
- `updated_at`: ISO 8601 timestamp

---

## 🛡️ CONSTITUTION COMPLIANCE

### **Mandatory Safety Constraints:**

**1. Data Sufficiency**
- Minimum 7 days data for bid changes
- Minimum 14 days data for pause actions
- Minimum 30 days data for match type changes
- Never act on <100 impressions OR <10 clicks

**2. Change Magnitude Limits**
- Bid increases: Maximum +20% per change
- Bid decreases: Maximum -30% per change
- Never change bid >1 time per cooldown period

**3. Cooldown Periods**
- Bid changes: 7-day minimum cooldown
- Pause/enable: 14-day minimum cooldown
- Match type changes: 30-day minimum cooldown

**4. Monitoring Periods**
- Bid changes: 7-day monitoring minimum
- Status changes: 14-day monitoring minimum
- Monitor ROAS and CVR (±15% drop triggers rollback)

**5. Risk Classification**
- Low risk: Pause high-cost zero-conv, reduce bid on poor performers
- Medium risk: Increase bid on high performers, enable paused keywords
- High risk: Match type changes, large bid swings

**6. Scope Restrictions**
- Prefer "blanket" scope (applies to all keywords globally)
- Use "specific" scope only if rule is campaign-dependent
- Campaign-specific rules require campaign_id validation

---

## 📋 REQUIREMENTS

### **Deliverables**

**1. Updated rules_config.json**
- Location: `C:\Users\User\Desktop\gads-data-layer\act_autopilot\rules_config.json`
- Add 5-8 new keyword rules
- Maintain existing 13 campaign rules (DO NOT MODIFY)
- Total rules after: 18-21 (13 campaign + 5-8 keyword)

**2. Rule Selection Justification**
- Document which 5-8 scenarios chosen from the 8 provided
- Explain why each rule is important
- Note any scenarios deferred for future

**3. Testing Plan**
- How to verify rules load correctly
- How to test with synthetic data
- Edge case handling

### **Technical Constraints**

**1. JSON Format**
- Valid JSON (no syntax errors)
- All 18 fields present for each rule
- Correct data types (strings, numbers, booleans, null)

**2. Field Validation**
- `rule_type`: Must be "keyword" (NOT "campaign", "ad_group", "ad", "shopping")
- `scope`: Must be "blanket" or "specific"
- `campaign_id`: null for blanket, valid campaign ID for specific
- `action_direction`: Must be valid action type
- `risk_level`: Must be "low", "medium", or "high"
- Timestamps: ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)

**3. Consistency**
- Rule IDs sequential: keyword_1, keyword_2, keyword_3, etc.
- Rule numbers sequential: 1, 2, 3, etc.
- Display names concise (3-6 words)
- Names descriptive (start with "KEYWORD-XXX:")

**4. Constitution Alignment**
- All cooldown_days ≥7
- All monitoring_days ≥7
- Action magnitude within limits (bid ±20-30%)
- Risk levels appropriate for actions

### **Google Ads Best Practices**

**1. Keyword Optimization Principles**
- Focus on conversion economics (CPA, ROAS) over vanity metrics
- Quality Score matters but conversions matter more
- High CPC acceptable if ROAS positive
- Pause aggressively, enable conservatively
- Never change multiple variables simultaneously

**2. Data Requirements**
- Low-volume keywords need longer lookback (21-30 days)
- High-volume keywords can act faster (7-14 days)
- Always require minimum clicks/impressions threshold
- Account for conversion lag (24-48 hours typical)

**3. Match Type Hierarchy**
- Broad → Phrase: Tighten if wasted spend evident
- Phrase → Exact: Only if highly specific intent
- Exact → Phrase: Expand if impression share lost
- Never auto-change match type without human approval

**4. Seasonal Considerations**
- Trend-based rules need ≥30 day history
- Account for day-of-week patterns (B2B vs B2C)
- Holiday/event spikes should not trigger pause rules
- Declining trends vs temporary dips (statistical significance)

---

## ✅ SUCCESS CRITERIA

### **All 12 criteria must pass for approval:**

**JSON Validity (3 criteria)**
- [ ] 1. rules_config.json is valid JSON (no syntax errors)
- [ ] 2. All 18 required fields present for each new rule
- [ ] 3. Correct data types (strings, numbers, booleans, null)

**Rule Content (3 criteria)**
- [ ] 4. 5-8 new keyword rules added (rule_type: "keyword")
- [ ] 5. All rule scenarios address real optimization needs
- [ ] 6. Rule names/descriptions clear and actionable

**Constitution Compliance (3 criteria)**
- [ ] 7. All cooldown_days ≥7, monitoring_days ≥7
- [ ] 8. Action magnitudes within limits (±20-30% for bids)
- [ ] 9. Risk levels appropriate (low/medium/high)

**Integration (3 criteria)**
- [ ] 10. Existing 13 campaign rules unchanged
- [ ] 11. Flask loads rules_config.json without errors
- [ ] 12. Keywords page shows "Rules (X)" where X = number of keyword rules

---

## 🧪 TESTING INSTRUCTIONS

### **Step 1: JSON Validation**
```powershell
cd C:\Users\User\Desktop\gads-data-layer
python -c "import json; f=open('act_autopilot/rules_config.json'); json.load(f); print('Valid JSON')"
```
Expected: "Valid JSON"

### **Step 2: Count Rules**
```powershell
python -c "import json; f=open('act_autopilot/rules_config.json'); d=json.load(f); print(f'Total: {len(d)}, Keyword: {len([r for r in d if r[\"rule_type\"]==\"keyword\"])}')"
```
Expected: "Total: 18-21, Keyword: 5-8"

### **Step 3: Flask Startup Test**
```powershell
cd C:\Users\User\Desktop\gads-data-layer
.\.venv\Scripts\Activate.ps1
python -m act_dashboard.app
```
Expected: No errors, server starts

### **Step 4: Keywords Page Test**
- Navigate to http://localhost:5000/keywords
- Click Rules tab
- Verify tab label shows "Rules (X)" where X matches keyword rule count
- Verify rules display in card UI

### **Step 5: Rule Card Display Test**
- Click "View All Rules" button
- Verify each keyword rule displays:
  - Correct display_name
  - Correct condition metrics
  - Correct action description
  - Enable/disable toggle works
- Verify no JavaScript errors in console

---

## 🚨 POTENTIAL ISSUES

### **Common Pitfalls to Avoid**

**Issue 1: JSON Syntax Errors**
- Missing commas between objects
- Trailing comma after last object
- Unquoted field names
- Wrong quote types (use double quotes)
**Prevention:** Use JSON validator before saving

**Issue 2: Incorrect rule_type**
- Using "campaign" instead of "keyword"
- Typo in rule_type field
- Case sensitivity (lowercase "keyword")
**Prevention:** Copy exact field values from campaign rules

**Issue 3: Missing Fields**
- Only 17 fields instead of 18
- Null vs missing field (null is required for some)
- Empty string vs null (different meanings)
**Prevention:** Use campaign rule as template, verify all 18 fields

**Issue 4: Invalid Operators**
- Using ">" when ">=" needed
- Wrong operator for metric type
- Comparing strings to numbers
**Prevention:** Test logic with sample data first

**Issue 5: Constitution Violations**
- cooldown_days <7
- monitoring_days <7
- action_magnitude >30% for decreases or >20% for increases
**Prevention:** Review Constitution limits before setting values

**Issue 6: Unrealistic Thresholds**
- Cost threshold too low (triggers on every keyword)
- CTR threshold too high (never triggers)
- Quality Score threshold impossible (QS 1-10 scale)
**Prevention:** Validate against synthetic data ranges

### **Known Gotchas**

**1. Metric Names**
- Database columns: cost, conversions, clicks, impressions, ctr, cpc
- NOT: spend, conv, click, impr (use exact column names)

**2. Unit Consistency**
- cost: "currency" (£, $, €)
- conversions: "count" (integer)
- ctr: "percent" (0-100, not 0-1)
- quality_score: "score" (1-10)
- cpc: "currency"

**3. Scope Logic**
- "blanket": Applies to all keywords globally (campaign_id must be null)
- "specific": Applies to keywords in one campaign (campaign_id required)
- Cannot mix (either blanket OR specific, not both)

**4. Timestamp Format**
- Must be ISO 8601: "2026-02-25T18:00:00Z"
- Include T separator and Z timezone
- Use current date/time for created_at and updated_at

---

## 📝 HANDOFF REQUIREMENTS

### **Documentation**

**1. Create CHAT_42_SUMMARY.md**
- Which 5-8 scenarios chosen
- Why each rule is important
- Constitution compliance verification
- Testing results

**2. Create CHAT_42_HANDOFF.md**
- Complete technical details
- Rule-by-rule breakdown
- JSON structure explanation
- Future enhancements (scenarios not implemented)

### **Git Commit**

**Prepare commit message:**
```
feat(rules): Add 5-8 keyword optimization rules to rules_config.json

Chat 42 - Keyword rules creation

Rules Added:
- Rule 1: [display_name]
- Rule 2: [display_name]
- Rule 3: [display_name]
- Rule 4: [display_name]
- Rule 5: [display_name]
[... up to 8]

All rules Constitution-compliant:
- Cooldown ≥7 days
- Monitoring ≥7 days
- Action magnitude within limits
- Risk levels appropriate

Testing:
- JSON valid
- Flask loads successfully
- Keywords page shows Rules (X)
- All 12 success criteria passing

Files Modified (1):
- act_autopilot/rules_config.json

Time: [X hours]
Chat: 42
Status: Ready for recommendations engine integration (Chat 43)
```

### **Delivery**

**Copy to /mnt/user-data/outputs/:**
- Updated rules_config.json
- CHAT_42_SUMMARY.md
- CHAT_42_HANDOFF.md

**Use present_files tool to share with Christopher**

**Await Master approval before git commit**

---

## ⏱️ ESTIMATED TIME BREAKDOWN

| Phase | Task | Time |
|-------|------|------|
| 1 | Read brief + docs | 30 min |
| 2 | Select 5-8 scenarios | 30 min |
| 3 | Define rule 1-2 | 2 hours |
| 4 | Define rule 3-4 | 2 hours |
| 5 | Define rule 5-6 | 2 hours |
| 6 | Define rule 7-8 (if doing 8) | 2 hours |
| 7 | Constitution validation | 1 hour |
| 8 | JSON formatting + validation | 1 hour |
| 9 | Testing (all 5 steps) | 1.5 hours |
| 10 | Documentation (2 handoffs) | 1.5 hours |
| **TOTAL** | **10-15 hours** | **(depends on 5 vs 8 rules)** |

---

## 🎯 RECOMMENDED APPROACH

### **Step 1: Select Scenarios (30 min)**
- Review all 8 scenarios provided
- Choose 5-8 based on:
  - Most common in real accounts
  - Highest ROI potential
  - Constitution-compliant
  - Testable with synthetic data

### **Step 2: Define Rules One at a Time (6-8 hours)**
- Start with easiest (e.g., high-cost zero-conv pause)
- Use campaign rule as JSON template
- Validate each rule before moving to next
- Test after every 2 rules

### **Step 3: Validate Compliance (1 hour)**
- Check all cooldowns ≥7
- Check all monitoring ≥7
- Check action magnitudes within limits
- Verify risk levels make sense

### **Step 4: Test Thoroughly (1.5 hours)**
- Run all 5 testing steps
- Fix any issues
- Retest until all pass

### **Step 5: Document (1.5 hours)**
- Write summary (why each rule chosen)
- Write handoff (technical details)
- Prepare git commit message

---

## 🚀 READY TO START

**MANDATORY WORKFLOW - DO NOT SKIP ANY STEP:**

### **STEP 1: Read Project Files (15 minutes)**

**Use `view` tool to read these files from `/mnt/project/`:**

```
view /mnt/project/CHAT_42_BRIEF.md
view /mnt/project/PROJECT_ROADMAP.md
view /mnt/project/CHAT_WORKING_RULES.md
view /mnt/project/MASTER_KNOWLEDGE_BASE.md
view /mnt/project/DASHBOARD_PROJECT_PLAN.md
view /mnt/project/WORKFLOW_GUIDE.md
```

**Read each file thoroughly to understand:**
- Project context and current state
- Working rules and workflows
- Architecture and patterns
- Lessons learned from past chats

---

### **STEP 2: Send 5 Questions to Master Chat (STOP AND WAIT)**

**After reading all docs, send exactly 5 questions:**

Example questions:
- Q1. [SCENARIOS] Which 5-8 scenarios should I prioritize from the 8 provided?
- Q2. [THRESHOLDS] Should Quality Score rules use exact QS values (e.g., <4) or ranges?
- Q3. [ACTIONS] For match type rules, should action be 'flag_review' or 'change_match_type'?
- Q4. [SCOPE] Should all rules be 'blanket' scope or include campaign-specific rules?
- Q5. [VALUES] What cost threshold is realistic for "high-cost" keywords (£50? £100?)?

**Format:**
```
5 QUESTIONS FOR MASTER CHAT

Q1. [CATEGORY] Question text?
Q2. [CATEGORY] Question text?
Q3. [CATEGORY] Question text?
Q4. [CATEGORY] Question text?
Q5. [CATEGORY] Question text?

Waiting for Master Chat answers before proceeding.
```

**STOP. Do not proceed until Master answers.**

---

### **STEP 3: Send Build Plan to Master Chat (STOP AND WAIT)**

**After receiving answers, create detailed build plan:**

```
DETAILED BUILD PLAN FOR MASTER CHAT REVIEW

Based on Master's answers, I will create X keyword rules:

Rule 1: [Scenario name]
- Condition 1: [metric] [operator] [value]
- Condition 2: [metric] [operator] [value]
- Action: [action_direction] [magnitude]
- Risk: [low/medium/high]
- Cooldown: [X days]
- Monitoring: [Y days]

[Repeat for each rule]

Implementation steps:
STEP A: Request upload of rules_config.json from Christopher
STEP B: Add Rule 1-2 (~2h)
STEP C: Add Rule 3-4 (~2h)
STEP D: Add Rule 5-6 (~2h)
STEP E: Add Rule 7-8 if needed (~2h)
STEP F: Validate JSON (~30min)
STEP G: Test all 5 testing steps (~1.5h)
STEP H: Create handoff docs (~1.5h)

Total estimated time: [X hours]

Waiting for Master Chat approval before starting.
```

**STOP. Do not proceed until Master approves.**

---

### **STEP 4: Request Current File**

**After Master approval, request the file you'll edit:**

```
I need the current version of rules_config.json to edit.

Please upload:
- File: rules_config.json
- Location: C:\Users\User\Desktop\gads-data-layer\act_autopilot\rules_config.json

After upload, I will add the keyword rules and return the complete updated file.
```

**WAIT for Christopher to upload before proceeding.**

---

### **STEP 5: Implement Rules**

**Follow your approved build plan.**

**Add rules one at a time.**

**Test after every 2 rules added.**

---

### **STEP 6: Deliver Complete File**

**When finished:**
- Provide complete updated rules_config.json
- Run all 5 testing steps
- Create CHAT_42_SUMMARY.md
- Create CHAT_42_HANDOFF.md
- Report to Master for final approval

---

**Brief complete. Worker Chat 42 may now begin.**

**Estimated completion: 10-15 hours**
