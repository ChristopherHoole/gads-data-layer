# CHAT 47: Recommendations Engine Extension - Database + Engine Foundation

**Date:** 2026-02-26  
**Type:** Worker Chat (Foundation - Architectural Refactor)  
**Estimated Time:** 11-14 hours (includes mandatory Master Chat checkpoints)  
**Complexity:** HIGH  
**Risk:** MEDIUM

---

## 🎯 OBJECTIVE

Extend the recommendations engine from campaign-only to support all 5 entity types: campaigns (existing), keywords, ads, ad groups, and shopping products. This includes database schema changes, engine logic for 5 data sources, route updates, and comprehensive testing.

**Success Definition:** All 41 rules generate recommendations for their respective entity types. Campaigns continue working (no regression). Keywords generate recommendations that can be accepted/declined via existing UI.

---

## 🚨 CRITICAL: MANDATORY MASTER CHAT REVIEW AT EVERY STEP

**This chat is HIGH RISK and HIGH COMPLEXITY. Standard workflow is insufficient.**

**WORKER MUST STOP and REPORT TO MASTER after EVERY major step.**

### **8 Mandatory Checkpoints**

After completing each step below, worker MUST:
1. ✋ **STOP work completely**
2. 📋 **Report to Master Chat** (via Christopher)
3. ⏳ **WAIT for Master approval**
4. ✅ **Only then proceed to next step**

**Checkpoints:**
1. ✋ Migration script created → Report to Master
2. ✋ Migration tested on backup → Report to Master
3. ✋ Engine extended (all 5 entity types) → Report to Master
4. ✋ Engine tested (recommendations generated) → Report to Master
5. ✋ Routes updated (Accept/Decline/Modify) → Report to Master
6. ✋ Routes tested (accept working) → Report to Master
7. ✋ Test script created → Report to Master
8. ✋ Full testing complete → Report to Master

### **Report Format**

**Worker sends to Christopher (who pastes to Master Chat):**
```
STEP [N] COMPLETE - REPORTING TO MASTER

What was done: [1-2 sentences]
Files changed: [list with full paths]
Testing results: [pass/fail with details]
Issues encountered: [problems + solutions]
Screenshots: [if UI testing]
Next step: [what comes next]

Waiting for Master approval before proceeding.
```

**Master Chat responds (Christopher pastes back to worker):**
```
STEP [N] APPROVED ✅ - Proceed to Step [N+1]

[or if issues found:]

STEP [N] NEEDS CHANGES ⚠️
- Issue 1: [what to fix]
- Issue 2: [what to fix]
Fix and resubmit before proceeding.
```

### **Why This Is Mandatory**

1. **Database changes** - One wrong migration = corrupted data
2. **5 data sources** - Each could fail differently
3. **41 rules** - High chance of edge cases
4. **10-12 hours** - Too long to debug at the end
5. **Foundation chat** - Chats 48-50 depend on this working perfectly

**DO NOT skip checkpoints. DO NOT proceed without approval.**

---

## 📋 CONTEXT

### **Current State (Campaign-Only)**

**What Works:**
- ✅ 13 campaign rules (budget/bid/status) generate recommendations
- ✅ Recommendations engine queries `campaign_features_daily`
- ✅ Global `/recommendations` page with 4-tab UI
- ✅ Campaigns page has inline recommendations tab
- ✅ Accept/Decline/Modify routes work for campaigns
- ✅ Database schema: `campaign_id`, `campaign_name`

**What Doesn't Work:**
- ❌ 28 non-campaign rules (keyword/ad/ad_group/shopping) generate nothing
- ❌ Engine only queries campaign data
- ❌ Database schema cannot store non-campaign recommendations
- ❌ Routes assume campaign_id always present
- ❌ No recommendations tabs on keywords/ads/ad_groups/shopping pages

### **Rules Breakdown (from rules_config.json)**

**Campaign Rules (13 total, 13 enabled) - ✅ WORKING**
- budget: 6 rules
- bid: 4 rules  
- status: 3 rules

**Non-Campaign Rules (28 total, 27 enabled) - ❌ NOT WORKING**
- keyword: 6/6 enabled
- ad_group: 4/4 enabled
- ad: 3/4 enabled
- shopping: 13/14 enabled

### **Architecture Issues Identified**

**Database Schema:**
- Current: `campaign_id BIGINT NOT NULL, campaign_name VARCHAR`
- Problem: Cannot represent keywords/ads/ad_groups/products
- Solution: Add `entity_type VARCHAR, entity_id BIGINT, entity_name VARCHAR`

**Engine Logic:**
- Current: Queries only `ro.analytics.campaign_features_daily`
- Problem: Keywords/ads/etc. not in this table
- Solution: Query 5 different tables based on rule_type

**Route Logic:**
- Current: Filters by `campaign_id`
- Problem: Non-campaign recommendations invisible
- Solution: Filter by `entity_type` + `entity_id`

---

## 📦 DELIVERABLES

### **1. Database Schema Migration**

**File:** `tools/migrations/migrate_recommendations_schema.py` (NEW)

**Requirements:**
- Backup existing recommendations table
- Add 3 new columns: `entity_type`, `entity_id`, `entity_name`
- Migrate existing rows: `entity_type='campaign'`, `entity_id=campaign_id`, `entity_name=campaign_name`
- Keep `campaign_id`/`campaign_name` for backward compatibility (mark deprecated)
- Create indexes on `entity_type` + `entity_id`
- Rollback capability if migration fails

**Full Path:**
```
C:\Users\User\Desktop\gads-data-layer\tools\migrations\migrate_recommendations_schema.py
```

### **2. Extended Recommendations Engine**

**File:** `act_autopilot/recommendations_engine.py` (MODIFIED)

**Requirements:**
- Detect rule_type and query appropriate data source:
  - campaign → `ro.analytics.campaign_features_daily` (existing)
  - keyword → `ro.analytics.keyword_daily` (NEW)
  - ad_group → `ro.analytics.ad_group_daily` (NEW)
  - ad → `ro.analytics.ad_daily` (NEW)
  - shopping → `ro.analytics.shopping_campaign_daily` or `ro.analytics.product_daily` (NEW - check which exists)
- Extract entity_id and entity_name from each data source
- Map metrics for each entity type (keywords have QS, ads have ad_strength, etc.)
- Handle entity-specific current_value logic
- Populate entity_type/entity_id/entity_name in recommendations
- Maintain backward compatibility (campaign rules still work)

**Full Path:**
```
C:\Users\User\Desktop\gads-data-layer\act_autopilot\recommendations_engine.py
```

### **3. Updated Routes**

**File:** `act_dashboard/routes/recommendations.py` (MODIFIED)

**Requirements:**
- Update `/recommendations` route: Query by entity_type
- Update `/recommendations/cards` route: Group by entity_type
- Update Accept/Decline/Modify routes: Use entity_id not campaign_id
- Update changes table inserts: Record entity_type + entity_id
- Add backward compatibility checks (handle old campaign_id-only rows)
- No UI changes (global page already works, just needs entity-aware data)

**Full Path:**
```
C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\recommendations.py
```

### **4. Testing & Validation**

**File:** `tools/testing/test_recommendations_all_entities.py` (NEW)

**Requirements:**
- Run engine for synthetic customer (9999999999)
- Verify campaigns generate recommendations (regression test)
- Verify keywords generate recommendations (NEW)
- Verify ads generate recommendations (NEW)
- Verify ad_groups generate recommendations (NEW)
- Verify shopping generates recommendations (NEW)
- Check database has entity_type populated correctly
- Verify Accept/Decline work for non-campaign entities

**Full Path:**
```
C:\Users\User\Desktop\gads-data-layer\tools\testing\test_recommendations_all_entities.py
```

### **5. Documentation**

**Files:** (BOTH required)
- `docs/CHAT_47_SUMMARY.md` (NEW)
- `docs/CHAT_47_HANDOFF.md` (NEW)

**Full Paths:**
```
C:\Users\User\Desktop\gads-data-layer\docs\CHAT_47_SUMMARY.md
C:\Users\User\Desktop\gads-data-layer\docs\CHAT_47_HANDOFF.md
```

---

## 🔧 TECHNICAL CONSTRAINTS

### **Database**

**CRITICAL:**
- Write to `warehouse.duckdb` ONLY
- NEVER write to `ro.analytics.*` (readonly)
- Test migration on synthetic data first
- Provide rollback script in case of issues
- Keep campaign_id/campaign_name for backward compatibility (don't delete)

**Schema Changes:**
```sql
-- Add to recommendations table
ALTER TABLE recommendations ADD COLUMN entity_type VARCHAR;
ALTER TABLE recommendations ADD COLUMN entity_id BIGINT;
ALTER TABLE recommendations ADD COLUMN entity_name VARCHAR;

-- Migrate existing data
UPDATE recommendations 
SET entity_type = 'campaign',
    entity_id = campaign_id,
    entity_name = campaign_name
WHERE entity_type IS NULL;

-- Create indexes
CREATE INDEX idx_recommendations_entity ON recommendations(entity_type, entity_id);
```

### **Data Source Mapping**

**You MUST verify these tables exist before querying:**

```python
DATA_SOURCE_MAP = {
    "campaign":  "ro.analytics.campaign_features_daily",  # VERIFIED EXISTS
    "keyword":   "ro.analytics.keyword_daily",            # CHECK IF EXISTS
    "ad_group":  "ro.analytics.ad_group_daily",           # CHECK IF EXISTS  
    "ad":        "ro.analytics.ad_daily",                 # CHECK IF EXISTS
    "shopping":  "ro.analytics.shopping_campaign_daily",  # CHECK IF EXISTS (or product_daily)
}
```

**If a table doesn't exist:**
- Log warning
- Skip rules for that entity type
- Document in handoff which tables are missing

### **Metric Mapping Per Entity Type**

**Campaign metrics** (existing):
- roas_7d, clicks_7d, conversions_30d, cost_spike_confidence, etc.

**Keyword metrics** (NEW - check column availability):
- quality_score, ctr, cvr, cost, conversions
- May need to map: `quality_score` → `qs` or similar

**Ad metrics** (NEW - check column availability):
- ad_strength, ctr, cvr, cost, conversions
- String comparison: ad_strength "eq" "POOR"

**Ad Group metrics** (NEW - check column availability):
- ctr, cvr, cost, conversions, quality_score_avg

**Shopping metrics** (NEW - check column availability):
- roas, cost, conversions, feed_error_count, out_of_stock_count, impression_share

**Action Required:**
1. Run DESCRIBE on each table to see available columns
2. Create metric mapping dict for each entity type
3. Handle missing columns gracefully (skip rule if metric unavailable)

### **Entity-Specific Current Value Logic**

```python
# Campaign
if rule_type == "budget":
    current_value = budget_value  # from cost_micros_w7_mean
elif rule_type == "bid":
    current_value = target_roas   # fallback 4.0

# Keyword
if rule_type == "keyword":
    current_value = keyword_bid_micros / 1_000_000  # or max_cpc

# Ad
if rule_type == "ad":
    current_value = None  # ads don't have numeric value (status/strength only)

# Ad Group
if rule_type == "ad_group":
    current_value = ad_group_bid_micros / 1_000_000

# Shopping
if rule_type == "shopping":
    current_value = campaign_budget_micros / 1_000_000  # similar to campaign
```

### **Backward Compatibility**

**CRITICAL - Do NOT break existing functionality:**
- Campaign recommendations must still work
- Global `/recommendations` page must still load campaigns
- Campaigns page recommendations tab must still work
- Existing Accept/Decline routes must still work for old campaign-only rows

**How to ensure:**
1. Keep campaign_id/campaign_name columns
2. In routes, check if entity_type is NULL → treat as campaign
3. Test campaigns thoroughly before testing other entities
4. Provide regression test suite

---

## 📚 REFERENCE FILES

### **Critical Files to Study**

**1. Current Engine (Campaign-Only)**
```
C:\Users\User\Desktop\gads-data-layer\act_autopilot\recommendations_engine.py
```
- Study lines 274-616 (main engine function)
- Understand how campaigns are processed
- Note metric mapping (lines 50-66)
- See condition evaluation (lines 84-99)

**2. Current Routes**
```
C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\recommendations.py
```
- Study Accept/Decline/Modify routes (lines 200-400)
- Understand how status updates work
- See changes table structure (lines 44-65)
- Note monitoring_days logic (lines 68-86)

**3. Rules Configuration**
```
C:\Users\User\Desktop\gads-data-layer\act_autopilot\rules_config.json
```
- See all 41 rules
- Understand rule_type field
- Note which rules are enabled
- Study different condition metrics per entity type

**4. Chat 27 Handoff (Original Implementation)**
```
C:\Users\User\Desktop\gads-data-layer\docs\CHAT_27_HANDOFF.md
```
- Understand original architecture decisions
- See what Chat 28 added (Accept/Decline)
- Note monitoring period implementation

**5. Database Schema**
```
Inspect: warehouse.duckdb → recommendations table
Inspect: warehouse_readonly.duckdb → analytics.* tables
```
Use: `DESCRIBE recommendations;` and `SHOW TABLES;`

---

## ✅ SUCCESS CRITERIA (18 items)

### **Database Migration (5 items)**
- [ ] 1. Migration script created with rollback capability
- [ ] 2. entity_type/entity_id/entity_name columns added
- [ ] 3. Existing campaign rows migrated (entity_type='campaign')
- [ ] 4. Indexes created on entity_type + entity_id
- [ ] 5. Migration tested on synthetic database

### **Engine Extension (6 items)**
- [ ] 6. Engine queries 5 data sources based on rule_type
- [ ] 7. Campaign rules still generate recommendations (no regression)
- [ ] 8. Keyword rules generate recommendations (NEW)
- [ ] 9. Ad rules generate recommendations (NEW)
- [ ] 10. Ad Group rules generate recommendations (NEW)
- [ ] 11. Shopping rules generate recommendations (NEW)
- [ ] 12. entity_type/entity_id/entity_name populated correctly

### **Routes Extension (3 items)**
- [ ] 13. Accept/Decline/Modify work for all entity types
- [ ] 14. Cards endpoint returns recommendations for all entity types
- [ ] 15. Changes table records entity_type + entity_id

### **Testing & Validation (4 items)**
- [ ] 16. Test script runs successfully for all entity types
- [ ] 17. Database has recommendations for all 5 entity types
- [ ] 18. Global `/recommendations` page shows all entity types (can test manually)

---

## 🧪 TESTING INSTRUCTIONS

### **Phase 1: Database Migration (15 min)**

**1. Backup existing database**
```powershell
cd C:\Users\User\Desktop\gads-data-layer
copy warehouse.duckdb warehouse_backup_pre_chat47.duckdb
```

**2. Run migration script**
```powershell
python tools/migrations/migrate_recommendations_schema.py
```

**Expected output:**
```
[MIGRATION] Starting schema migration...
[MIGRATION] Backing up recommendations table...
[MIGRATION] Adding entity_type, entity_id, entity_name columns...
[MIGRATION] Migrating existing campaign recommendations...
[MIGRATION] Creating indexes...
[MIGRATION] Migration complete: X rows migrated
```

**3. Verify schema**
```powershell
python -c "import duckdb; conn = duckdb.connect('warehouse.duckdb'); print(conn.execute('DESCRIBE recommendations').fetchall())"
```

**Expected:** Should see entity_type, entity_id, entity_name columns

### **Phase 2: Engine Extension Testing (30 min)**

**1. Check available data sources**
```powershell
python -c "import duckdb; conn = duckdb.connect('warehouse_readonly.duckdb'); print(conn.execute('SHOW TABLES FROM analytics').fetchall())"
```

**Expected:** List of tables (verify keyword_daily, ad_daily, etc. exist)

**2. Run extended engine**
```powershell
cd C:\Users\User\Desktop\gads-data-layer
python -m act_autopilot.recommendations_engine --customer-id 9999999999
```

**Expected output:**
```
[ENGINE] Starting recommendations engine for customer 9999999999
[ENGINE] Loaded 41 rules (40 enabled)
[ENGINE] Processing campaigns... [X recommendations generated]
[ENGINE] Processing keywords... [X recommendations generated]
[ENGINE] Processing ad_groups... [X recommendations generated]
[ENGINE] Processing ads... [X recommendations generated]
[ENGINE] Processing shopping... [X recommendations generated]
[ENGINE] Total: X generated, Y skipped_duplicate, Z skipped_no_data
```

**3. Verify database has all entity types**
```powershell
python -c "import duckdb; conn = duckdb.connect('warehouse.duckdb'); print(conn.execute('SELECT entity_type, COUNT(*) FROM recommendations GROUP BY entity_type').fetchall())"
```

**Expected:** List showing counts for campaign, keyword, ad, ad_group, shopping

### **Phase 3: Routes Testing (20 min)**

**1. Start Flask**
```powershell
cd C:\Users\User\Desktop\gads-data-layer
.\.venv\Scripts\Activate.ps1
python -m act_dashboard.app
```

**2. Test global recommendations page**
- Navigate to: http://127.0.0.1:5000/recommendations
- Verify Pending tab shows recommendations
- Check if entity types are displayed (may need to add entity_type label to cards later)
- Take screenshot

**3. Test Accept for keyword recommendation (if any exist)**
- Click Accept on any keyword recommendation
- Verify no errors
- Check database: `SELECT * FROM recommendations WHERE entity_type='keyword' AND status='accepted'`

### **Phase 4: Full Validation (15 min)**

**Run comprehensive test script**
```powershell
python tools/testing/test_recommendations_all_entities.py
```

**Expected output:**
```
[TEST] Testing recommendations engine for all entity types...
[TEST] ✓ Database schema migration successful
[TEST] ✓ Campaign recommendations: X generated
[TEST] ✓ Keyword recommendations: X generated
[TEST] ✓ Ad recommendations: X generated
[TEST] ✓ Ad Group recommendations: X generated
[TEST] ✓ Shopping recommendations: X generated
[TEST] ✓ Accept/Decline working for all entity types
[TEST] All tests passed!
```

### **Edge Cases to Test**

**1. Missing Data Source:**
- If a table doesn't exist (e.g., ad_daily), engine should log warning and continue
- Should NOT crash

**2. NULL Values:**
- Some entities may have NULL for certain metrics
- Engine should skip rule if metric is NULL (existing behavior)

**3. Backward Compatibility:**
- Old campaign-only recommendations still work
- Can accept/decline old rows

**4. Metric Mapping:**
- Keyword-specific metrics (quality_score) work
- Ad-specific metrics (ad_strength) work
- Shopping-specific metrics (feed_error_count) work

---

## ⚠️ POTENTIAL ISSUES

### **Issue 1: Data Tables Don't Exist**

**Symptom:** Error "Table analytics.keyword_daily not found"

**Root Cause:** Data source not created yet in warehouse_readonly.duckdb

**Solution:**
- Check which tables exist using SHOW TABLES
- Skip rules for missing entity types
- Document in handoff which entities are blocked by missing data
- User can add data tables later

**Workaround:**
```python
def _table_exists(conn, table_name):
    try:
        conn.execute(f"SELECT 1 FROM {table_name} LIMIT 1")
        return True
    except:
        return False

# Only query if table exists
if _table_exists(conn, "ro.analytics.keyword_daily"):
    # Process keyword rules
else:
    print(f"[ENGINE] Skipping keyword rules - data table not found")
```

### **Issue 2: Metric Column Name Mismatches**

**Symptom:** Rule expects "quality_score" but column is "qs"

**Root Cause:** Database column names differ from rules_config.json metric names

**Solution:**
- Run DESCRIBE on each table first
- Create entity-specific metric mappings
- Add fallback logic if column doesn't exist

**Example:**
```python
KEYWORD_METRIC_MAP = {
    "quality_score": "qs",           # Map rule metric → DB column
    "ctr": "ctr",
    "cost": "cost_micros",           # Remember micros conversion
}
```

### **Issue 3: Current Value Calculation**

**Symptom:** proposed_value is wrong for keywords/ads

**Root Cause:** current_value logic is campaign-specific

**Solution:**
- Implement entity-specific current_value functions
- For keywords: Use max_cpc or bid
- For ads: Use NULL (ads don't have numeric values for most rules)
- For ad_groups: Use default_cpc
- For shopping: Use campaign_budget

### **Issue 4: String Comparison for Ad Strength**

**Symptom:** Ad rule `condition_operator: "eq"` with `condition_value: "POOR"` doesn't work

**Root Cause:** Engine expects numeric comparisons

**Solution:**
- Extend `_evaluate()` function to handle string comparisons
- Check if threshold is string, use string equality
- Already partially implemented (line 93-96 in current engine)

### **Issue 5: Migration Fails Midway**

**Symptom:** Migration adds columns but fails on UPDATE

**Root Cause:** Existing data corrupt or unexpected NULL values

**Solution:**
- Wrap migration in transaction (BEGIN/COMMIT/ROLLBACK)
- Test on backup first
- Provide rollback script that drops new columns
- Document manual rollback steps in handoff

---

## 📖 HANDOFF REQUIREMENTS

### **CHAT_47_SUMMARY.md Must Include:**

**Executive Summary** (3-4 sentences)
- What was built (database + engine extension)
- What now works (all 5 entity types)
- Key decisions made
- Time actual vs estimated

**Deliverables List** (5 files)
- Migration script path
- Extended engine path
- Updated routes path
- Test script path
- Documentation paths

**Key Achievements**
- Schema extended without breaking campaigns
- Engine processes 5 entity types
- All X rules now generate recommendations (specify number)

**Known Limitations**
- Which data tables are missing (if any)
- Which entity types couldn't be tested (if any)
- What's needed for Chats 48-50 (UI tabs)

### **CHAT_47_HANDOFF.md Must Include:**

**Complete Technical Details:**
- Database schema changes (before/after)
- Engine architecture (5 data source queries)
- Metric mapping for each entity type
- Current value logic per entity type
- Route changes (entity-aware filtering)

**Testing Results:**
- Migration success (rows migrated)
- Engine execution (recommendations per entity type)
- Route testing (accept/decline for each type)
- Edge cases tested

**Issues Encountered + Solutions:**
- Any data tables missing
- Any metric mapping issues
- Any migration problems
- How each was resolved

**Critical Code Sections:**
- Where entity_type logic is added (line numbers)
- Where data source selection happens
- Where backward compatibility is maintained
- Where to add new entity types in future

**For Chats 48-50 (Next Steps):**
- Where to add UI tabs (which templates)
- How to wire up entity-specific cards
- What testing is needed for each page
- Estimated time for each remaining chat

---

## 🎯 ESTIMATED TIME BREAKDOWN

**Total: 11-14 hours** (includes mandatory Master Chat coordination)

**Phase 1: Analysis & Planning (1.5 hours)**
- Study existing code (30 min)
- Verify data sources exist (30 min)
- Create metric mappings (30 min)

**Phase 2: Database Migration (1.5 hours + 15 min Master review)**
- Write migration script (45 min)
- ✋ **CHECKPOINT 1** → Report to Master (10 min)
- Test on backup (30 min)
- ✋ **CHECKPOINT 2** → Report to Master (10 min)
- Create rollback script (15 min)

**Phase 3: Engine Extension (4-5 hours + 30 min Master review)**
- Add entity_type detection (30 min)
- Implement 5 data source queries (90 min)
- Add metric mapping per entity (90 min)
- ✋ **CHECKPOINT 3** → Report to Master (15 min)
- Test each entity type (60 min)
- ✋ **CHECKPOINT 4** → Report to Master (15 min)

**Phase 4: Routes Extension (2-2.5 hours + 30 min Master review)**
- Update Accept/Decline/Modify (60 min)
- Update cards endpoint (45 min)
- Update changes table (30 min)
- ✋ **CHECKPOINT 5** → Report to Master (15 min)
- Test routes (30 min)
- ✋ **CHECKPOINT 6** → Report to Master (15 min)

**Phase 5: Testing & Validation (1.5-2 hours + 30 min Master review)**
- Write test script (45 min)
- ✋ **CHECKPOINT 7** → Report to Master (15 min)
- Run full test suite (45 min)
- Edge case testing (30 min)
- ✋ **CHECKPOINT 8** → Report to Master (15 min)

**Phase 6: Documentation (1-1.5 hours)**
- CHAT_47_SUMMARY.md (30 min)
- CHAT_47_HANDOFF.md (45 min)

**Master Chat Coordination Time:**
- 8 checkpoints × 10-15 minutes = 80-120 minutes
- Worth it for risk mitigation on critical foundation chat

---

## 🔄 WORKFLOW REMINDER

**This chat follows CHAT_WORKING_RULES.md v2.0 + MANDATORY MASTER CHECKPOINTS:**

**Phase 1: Upfront Planning**
1. ✅ Christopher uploads ONLY this brief
2. ✅ Worker reads ALL project files from /mnt/project/
3. ✅ Worker sends 5 QUESTIONS → waits for Master answers
4. ✅ Worker sends DETAILED BUILD PLAN → waits for Master approval

**Phase 2: Step-by-Step Execution (8 MANDATORY CHECKPOINTS)**
5. ✅ Worker implements Step 1 → ✋ STOP → Report to Master → Wait for approval
6. ✅ Worker implements Step 2 → ✋ STOP → Report to Master → Wait for approval
7. ✅ Worker implements Step 3 → ✋ STOP → Report to Master → Wait for approval
8. ✅ Worker implements Step 4 → ✋ STOP → Report to Master → Wait for approval
9. ✅ Worker implements Step 5 → ✋ STOP → Report to Master → Wait for approval
10. ✅ Worker implements Step 6 → ✋ STOP → Report to Master → Wait for approval
11. ✅ Worker implements Step 7 → ✋ STOP → Report to Master → Wait for approval
12. ✅ Worker implements Step 8 → ✋ STOP → Report to Master → Wait for approval

**Phase 3: Final Documentation**
13. ✅ Worker creates SUMMARY.md + HANDOFF.md → Final report to Master
14. ✅ Master reviews → Approves for git commit

**Total Master Chat Interactions: 10** (2 upfront + 8 checkpoints)

**Christopher's role:**
- Upload files when requested
- Save files when provided (worker edits, not Christopher)
- **CRITICAL:** Act as messenger between worker and Master Chat for all 8 checkpoints

**Ready to start Chat 47?**

Upload this brief to new worker chat in ACT project to begin.

---

**End of Brief**
