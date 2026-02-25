# CHAT 41: M5 RULES ROLLOUT - COMPLETE (4 PAGES)

**Estimated Time:** 8-9 hours
**Dependencies:** Chat 26 complete (Campaigns Rules tab pilot)
**Priority:** HIGH (Complete M5 milestone)
**Pages:** Ad Groups, Keywords, Ads, Shopping

---

## 🚨 MANDATORY WORKFLOW - READ THIS FIRST

This chat follows the **15-step worker chat workflow** from WORKFLOW_GUIDE.md.

**You MUST complete these steps in order:**

### **STEP 1: Read Project Knowledge + Confirm Understanding**

1. Read all 8 files from `/mnt/project/`:
   - MASTER_CHAT_5.0_HANDOFF.md
   - WORKFLOW_TEMPLATES.md
   - CHAT_WORKING_RULES.md
   - PROJECT_ROADMAP.md
   - MASTER_KNOWLEDGE_BASE.md
   - DETAILED_WORK_LIST.md
   - WORKFLOW_GUIDE.md
   - DASHBOARD_PROJECT_PLAN.md

2. Confirm you have read each file explicitly

3. Confirm understanding of:
   - Chat 26 pattern (Campaigns Rules tab is the reference)
   - Rule 2 (CRITICAL): Always request current file version before editing
   - One step at a time workflow with confirmation
   - Complete files only (never snippets)
   - Full Windows paths: `C:\Users\User\Desktop\gads-data-layer\...`
   - This chat covers 4 pages sequentially in one chat

**Template confirmation message:**
```
CONFIRMATION: ALL PROJECT FILES READ

I have read all 8 project files from Project Knowledge:
✅ MASTER_CHAT_5.0_HANDOFF.md
✅ WORKFLOW_TEMPLATES.md
✅ CHAT_WORKING_RULES.md
✅ PROJECT_ROADMAP.md
✅ MASTER_KNOWLEDGE_BASE.md
✅ DETAILED_WORK_LIST.md
✅ WORKFLOW_GUIDE.md
✅ DASHBOARD_PROJECT_PLAN.md

I understand:
* Current state: M5 Rules tab complete on Campaigns page (Chat 26)
* Task: Roll out same Rules tab pattern to 4 remaining pages
* Pages: Ad Groups (2 rules), Keywords (3 rules), Ads (2 rules), Shopping (6 rules)
* Pattern: Exact same CRUD, drawer, campaign picker as Chat 26
* Rule 2: Always request current file before editing
* Sequential execution: Ad Groups → Keywords → Ads → Shopping
* One step at a time with confirmation
* Complete files only, full Windows paths
* Estimated 8-9 hours total

Ready to proceed to 5 questions for Master Chat.
```

---

### **STEP 2: 5 Clarifying Questions**

After reading all project files, write exactly **5 questions** for Master Chat.

**Question categories:**
- `[REFERENCE]` - Chat 26 reference files
- `[RULES]` - Which rules for each page
- `[PATTERN]` - Exact pattern to follow
- `[TESTING]` - How to test each page
- `[SCOPE]` - Anything page-specific

**Format:**
```
5 QUESTIONS FOR MASTER CHAT

Q1. [CATEGORY] Question text here?
Q2. [CATEGORY] Question text here?
Q3. [CATEGORY] Question text here?
Q4. [CATEGORY] Question text here?
Q5. [CATEGORY] Question text here?

Waiting for Master Chat answers before proceeding.
```

**⚠️ STOP HERE - Wait for Master Chat answers**

---

### **STEP 3: Detailed Build Plan**

After receiving answers, create a detailed build plan with sequential steps.

**Format:**
```
DETAILED BUILD PLAN FOR MASTER CHAT REVIEW

Files to create/modify:

**Ad Groups:**
- C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\ad_groups.py — Add Rules tab
- C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\ad_groups_new.html — Add Rules tab UI

**Keywords:**
- C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\keywords.py — Add Rules tab
- C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\keywords_new.html — Add Rules tab UI

**Ads:**
- C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\ads.py — Add Rules tab
- C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\ads_new.html — Add Rules tab UI

**Shopping:**
- C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\shopping.py — Add Rules tab
- C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\shopping.html — Add Rules tab UI

Step-by-step implementation:

PART 1: AD GROUPS (2 hours)
STEP A: Review campaigns.py pattern (~10 min)
STEP B: Update ad_groups.py route (~30 min)
STEP C: Update ad_groups_new.html template (~40 min)
STEP D: Test Ad Groups Rules tab (~20 min)
STEP E: Confirm working before proceeding (~20 min)

PART 2: KEYWORDS (2 hours)
STEP F: Update keywords.py route (~30 min)
STEP G: Update keywords_new.html template (~40 min)
STEP H: Test Keywords Rules tab (~20 min)
STEP I: Confirm working before proceeding (~30 min)

PART 3: ADS (2 hours)
STEP J: Update ads.py route (~30 min)
STEP K: Update ads_new.html template (~40 min)
STEP L: Test Ads Rules tab (~20 min)
STEP M: Confirm working before proceeding (~30 min)

PART 4: SHOPPING (2-3 hours)
STEP N: Update shopping.py route (~40 min)
STEP O: Update shopping.html template (~60 min - more complex)
STEP P: Test Shopping Rules tab (~30 min)
STEP Q: Final comprehensive test all 4 pages (~30 min)

STEP R: Documentation (~45 min)

Total estimated time: 8-9 hours
Risks / unknowns: [Any concerns]

Waiting for Master Chat approval before starting implementation.
```

**⚠️ STOP HERE - Wait for Master Chat approval**

---

### **STEP 4: Implementation (ONE STEP AT A TIME)**

After Master Chat approves build plan, execute **ONE STEP AT A TIME**.

**For each step:**

1. **Request current file version:**
```
STEP A STARTING: Review campaigns.py pattern

I need campaigns.py and campaigns.html to understand the Rules tab pattern.

Please upload:
- File 1: campaigns.py
- Location: C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\campaigns.py

- File 2: campaigns.html
- Location: C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\campaigns.html

After upload, I will identify the exact pattern to replicate.

[STOP - WAIT FOR UPLOAD]
```

2. **After upload, analyze and proceed:**
```
STEP A COMPLETE ✅

Pattern identified:
- Rules loaded via get_rules_for_page() helper
- Rules tab uses Jinja2 macros: {% include 'components/rules_sidebar.html' %}
- Campaign picker uses /api/campaigns-list endpoint
- CRUD operations use rules_api.py routes

Ready for STEP B: Update ad_groups.py

Reply "Proceed" to continue.

[STOP - WAIT FOR CONFIRMATION]
```

3. **Wait for "Proceed" before next step**

**CRITICAL RULES:**
- ❌ NEVER provide multiple files in one response
- ❌ NEVER proceed without confirmation
- ❌ NEVER use code snippets (always complete files)
- ✅ ALWAYS request current file version first
- ✅ ALWAYS wait for confirmation after each step
- ✅ ALWAYS provide full Windows paths

---

### **STEP 5: Documentation**

After all implementation and testing complete:

1. Create `CHAT_41_SUMMARY.md` (300-400 lines)
2. Create `CHAT_41_HANDOFF.md` (1500-2000 lines)
3. Send both to Master Chat for review

**Do NOT commit to git - Master Chat handles commits.**

---

## CONTEXT

### **What Was Already Done (Chat 26)**

**Chat 26: M5 Rules Tab on Campaigns Page (Pilot)**
- Card-based Rules UI (replaced dense table)
- 13 budget/bid/status rules
- Full CRUD functionality:
  - Add rule (slide-in drawer)
  - Edit rule (same drawer)
  - Toggle enabled/disabled
  - Delete rule
- Campaign picker for specific-scope rules
- Dual-layer architecture:
  - `rules_config.json` - UI config (CRUD via rules_api.py)
  - `act_autopilot/rules/*.py` - Execution layer (Python functions, untouched)

**Files created in Chat 26:**
- `act_autopilot/rules_config.json` - Contains all 13 campaign rules
- `act_dashboard/routes/rules_api.py` - 6 routes for CRUD operations
- Updated `act_dashboard/routes/campaigns.py` - Load rules
- Updated `act_dashboard/templates/campaigns.html` - Rules tab UI

**Pattern to replicate:** Exact same UI/UX across all 4 pages.

---

### **What Needs to Be Done (Chat 41)**

**Rollout the same Rules tab pattern to 4 remaining pages:**

1. **Ad Groups page** - 2 rules (Ad Group CPA, Ad Group ROAS)
2. **Keywords page** - 3 rules (Keyword CPA, Keyword ROAS, Keyword QS)
3. **Ads page** - 2 rules (Ad CTR, Ad CVR)
4. **Shopping page** - 6 rules (Shopping Budget 1/2, Shopping Bid 1/2, Shopping Status 1/2)

**Same components for each page:**
- Rules tab (alongside existing tabs)
- Card grid layout (3 columns)
- Slide-in drawer (add/edit)
- Campaign picker (specific-scope rules)
- Enable/disable toggle
- Delete confirmation

**All 4 pages will use:**
- Same `rules_config.json` file (already has all rules)
- Same `rules_api.py` routes (already created)
- Same Jinja2 macros from Chat 26

---

## OBJECTIVE

Add card-based Rules tab to Ad Groups, Keywords, Ads, and Shopping pages using the exact pattern established in Chat 26 (Campaigns page pilot).

---

## REQUIREMENTS

### **Deliverables**

**4 pages updated with Rules tab:**

**1. Ad Groups Page**
- File: `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\ad_groups.py`
- File: `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\ad_groups_new.html`
- Rules: 2 (Ad Group CPA, Ad Group ROAS)
- Pattern: Exact copy of Campaigns page Rules tab

**2. Keywords Page**
- File: `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\keywords.py`
- File: `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\keywords_new.html`
- Rules: 3 (Keyword CPA, Keyword ROAS, Keyword QS)
- Pattern: Exact copy of Campaigns page Rules tab

**3. Ads Page**
- File: `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\ads.py`
- File: `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\ads_new.html`
- Rules: 2 (Ad CTR, Ad CVR)
- Pattern: Exact copy of Campaigns page Rules tab

**4. Shopping Page**
- File: `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\shopping.py`
- File: `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\shopping.html`
- Rules: 6 (Shopping Budget 1/2, Shopping Bid 1/2, Shopping Status 1/2)
- Pattern: Exact copy of Campaigns page Rules tab
- Note: Shopping has subcategory tabs (Campaigns, Products, Product Groups, Segments)

---

### **Pattern to Follow (From Chat 26)**

**Python Route Changes:**

```python
from act_dashboard.helpers.shared import get_rules_for_page

@bp.route('/ad-groups')
def ad_groups():
    # ... existing code ...
    
    # Add this for Rules tab
    rules = get_rules_for_page('ad_group')  # page_type: 'ad_group'
    
    return render_template('ad_groups_new.html', 
                         # ... existing context ...
                         rules=rules)
```

**Template Changes:**

Add Rules tab to navigation:
```html
<ul class="nav nav-tabs">
  <li class="nav-item"><a class="nav-link active" data-tab="overview">Overview</a></li>
  <li class="nav-item"><a class="nav-link" data-tab="table">Data</a></li>
  <li class="nav-item"><a class="nav-link" data-tab="rules">Rules</a></li>
</ul>
```

Add Rules tab content:
```html
<div id="rules-tab" class="tab-pane" style="display: none;">
  {% include 'components/rules_sidebar.html' %}
  {% include 'components/rules_tab.html' %}
  {% include 'components/rules_card.html' %}
</div>
```

**JavaScript for tab switching:**
```javascript
document.querySelectorAll('[data-tab]').forEach(tab => {
  tab.addEventListener('click', function(e) {
    e.preventDefault();
    const tabName = this.dataset.tab;
    
    // Hide all tabs
    document.querySelectorAll('.tab-pane').forEach(pane => {
      pane.style.display = 'none';
    });
    
    // Show selected tab
    document.getElementById(tabName + '-tab').style.display = 'block';
    
    // Update active state
    document.querySelectorAll('.nav-link').forEach(link => {
      link.classList.remove('active');
    });
    this.classList.add('active');
  });
});
```

---

### **Technical Constraints**

**Must maintain:**
- ✅ All existing page functionality (tables, charts, metrics)
- ✅ All existing tabs (Overview, Data, etc.)
- ✅ Bootstrap 5 styling
- ✅ Responsive design

**Must add:**
- ✅ Rules tab (new tab in navigation)
- ✅ Card grid (3 columns, responsive)
- ✅ Slide-in drawer (add/edit rules)
- ✅ Campaign picker (specific-scope rules)
- ✅ Enable/disable toggle (per rule)
- ✅ Delete functionality (with confirmation)

**Must NOT:**
- ❌ Break existing tabs
- ❌ Modify rules_config.json structure (already correct)
- ❌ Modify rules_api.py (already correct)
- ❌ Change Python execution files in act_autopilot/rules/

---

### **Page-Specific Notes**

**Ad Groups:**
- `page_type = 'ad_group'` in get_rules_for_page()
- 2 rules: ADGROUP-001, ADGROUP-002

**Keywords:**
- `page_type = 'keyword'` in get_rules_for_page()
- 3 rules: KEYWORD-001, KEYWORD-002, KEYWORD-003

**Ads:**
- `page_type = 'ad'` in get_rules_for_page()
- 2 rules: AD-001, AD-002

**Shopping:**
- `page_type = 'shopping'` in get_rules_for_page()
- 6 rules: SHOP-001 through SHOP-006
- Shopping page has 4 sub-tabs, Rules tab should be at root level (not inside sub-tabs)

---

## SUCCESS CRITERIA

**All 32 criteria must pass for approval (8 per page):**

### **Ad Groups Page (8 criteria)**
- [ ] 1. Rules tab appears in navigation
- [ ] 2. Rules tab shows 2 ad group rules as cards
- [ ] 3. "Add Rule" button opens slide-in drawer
- [ ] 4. Editing rule opens drawer with pre-filled data
- [ ] 5. Enable/disable toggle works for each rule
- [ ] 6. Delete button removes rule (with confirmation)
- [ ] 7. Campaign picker shows for specific-scope rules
- [ ] 8. All changes persist (refresh page, changes remain)

### **Keywords Page (8 criteria)**
- [ ] 9. Rules tab appears in navigation
- [ ] 10. Rules tab shows 3 keyword rules as cards
- [ ] 11. "Add Rule" button opens slide-in drawer
- [ ] 12. Editing rule opens drawer with pre-filled data
- [ ] 13. Enable/disable toggle works for each rule
- [ ] 14. Delete button removes rule (with confirmation)
- [ ] 15. Campaign picker shows for specific-scope rules
- [ ] 16. All changes persist (refresh page, changes remain)

### **Ads Page (8 criteria)**
- [ ] 17. Rules tab appears in navigation
- [ ] 18. Rules tab shows 2 ad rules as cards
- [ ] 19. "Add Rule" button opens slide-in drawer
- [ ] 20. Editing rule opens drawer with pre-filled data
- [ ] 21. Enable/disable toggle works for each rule
- [ ] 22. Delete button removes rule (with confirmation)
- [ ] 23. Campaign picker shows for specific-scope rules
- [ ] 24. All changes persist (refresh page, changes remain)

### **Shopping Page (8 criteria)**
- [ ] 25. Rules tab appears in navigation (root level, not inside sub-tabs)
- [ ] 26. Rules tab shows 6 shopping rules as cards
- [ ] 27. "Add Rule" button opens slide-in drawer
- [ ] 28. Editing rule opens drawer with pre-filled data
- [ ] 29. Enable/disable toggle works for each rule
- [ ] 30. Delete button removes rule (with confirmation)
- [ ] 31. Campaign picker shows for specific-scope rules
- [ ] 32. All changes persist (refresh page, changes remain)

**ALL 32 must pass.**

---

## TESTING INSTRUCTIONS

### **Phase 1: Ad Groups Page Testing**

**Test 1: Navigate to Rules tab**
```powershell
cd C:\Users\User\Desktop\gads-data-layer
.\.venv\Scripts\Activate.ps1
python -m act_dashboard.app
```
- Open: http://localhost:5000/ad-groups
- Click "Rules" tab
- **Expected:** Rules tab appears, shows 2 ad group rule cards

**Test 2: Add rule**
- Click "Add Rule"
- **Expected:** Slide-in drawer opens with form

**Test 3: Edit rule**
- Click edit icon on any card
- **Expected:** Drawer opens with rule data pre-filled

**Test 4: Toggle enabled**
- Click toggle switch
- **Expected:** Toggle changes state, badge updates

**Test 5: Delete rule**
- Click delete icon
- **Expected:** Confirmation modal appears
- Confirm delete
- **Expected:** Rule removed from list

**Test 6: Campaign picker (specific-scope rule)**
- Edit rule, change scope to "Specific campaigns"
- **Expected:** Campaign picker appears
- Select campaign
- **Expected:** Campaign name shown, save works

**Test 7: Persistence**
- Make changes (add, edit, toggle, delete)
- Refresh page
- **Expected:** Changes persist

---

### **Phase 2: Keywords Page Testing**

Repeat all 7 tests above for Keywords page:
- URL: http://localhost:5000/keywords
- Expected: 3 keyword rule cards
- Same CRUD functionality

---

### **Phase 3: Ads Page Testing**

Repeat all 7 tests above for Ads page:
- URL: http://localhost:5000/ads
- Expected: 2 ad rule cards
- Same CRUD functionality

---

### **Phase 4: Shopping Page Testing**

Repeat all 7 tests above for Shopping page:
- URL: http://localhost:5000/shopping
- Expected: 6 shopping rule cards
- Same CRUD functionality
- **Special:** Verify Rules tab is at root level (not inside Campaigns/Products/etc sub-tabs)

---

### **Phase 5: Cross-Page Verification**

**Test: Rules shared across pages**
- Add a new budget rule on Campaigns page
- Navigate to Ad Groups page
- **Expected:** New rule does NOT appear (rules are filtered by page_type)

**Test: Rules API still working**
- Use browser dev tools Network tab
- Edit a rule on any page
- **Expected:** See POST to /api/rules/<id>/update
- **Expected:** Response 200 OK

---

### **Edge Cases to Test**

**Test: Empty state**
- Delete all rules on a page
- **Expected:** Empty state message: "No rules configured"

**Test: Many rules (>6)**
- Add 10+ rules on one page
- **Expected:** Card grid wraps properly, no layout break

**Test: Long rule names**
- Edit rule, set very long display_name (100+ chars)
- **Expected:** Text truncates or wraps, no overflow

**Test: Browser console**
- Open console on each page
- **Expected:** No JavaScript errors

---

## POTENTIAL ISSUES

### **Common Pitfalls to Avoid**

**1. Wrong page_type in get_rules_for_page()**
- **Issue:** Passing wrong string, no rules load
- **Fix:** 
  - Ad Groups: `page_type='ad_group'`
  - Keywords: `page_type='keyword'`
  - Ads: `page_type='ad'`
  - Shopping: `page_type='shopping'`

**2. Tab JavaScript conflicts**
- **Issue:** Existing tab JS conflicts with Rules tab
- **Fix:** Use unique IDs, check for existing tab switcher code

**3. Template path wrong**
- **Issue:** {% include 'components/rules_tab.html' %} not found
- **Fix:** Verify components folder exists, paths are correct

**4. Shopping page subcategory tab structure**
- **Issue:** Rules tab appears inside Products tab instead of root
- **Fix:** Add Rules tab at same level as Campaigns/Products/etc tabs, not nested

**5. Rules not filtering by page**
- **Issue:** All 13 campaign rules showing on Keywords page
- **Fix:** Verify get_rules_for_page() is called with correct page_type

---

### **Known Gotchas**

**Gotcha 1: rules_config.json already has all rules**
- Don't recreate rules, they already exist
- Just load and display them with correct filter

**Gotcha 2: Campaigns page pattern has minor variations**
- Copy the pattern exactly
- Don't try to "improve" it (consistency > perfection)

**Gotcha 3: Template includes must be in correct order**
- rules_sidebar.html FIRST (drawer UI)
- rules_tab.html SECOND (card grid)
- rules_card.html THIRD (individual cards)

**Gotcha 4: Shopping page has different template name**
- Other pages: `*_new.html` (e.g., ad_groups_new.html)
- Shopping: `shopping.html` (no "_new" suffix)

---

## HANDOFF REQUIREMENTS

### **Documentation**

**Create 2 files:**

**1. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_41_SUMMARY.md`**
- 300-400 lines
- What was changed on each page
- All 32 success criteria results
- Testing results per page

**2. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_41_HANDOFF.md`**
- 1500-2000 lines
- Complete technical details per page
- Code changes before/after (all 4 pages)
- All testing results
- Issues encountered + solutions
- Performance notes

### **Git**

**Prepare commit message (Master Chat will execute):**

```
feat(dashboard): Roll out Rules tab to 4 remaining pages

M5 Rules Rollout - Complete (Chat 41)

Added card-based Rules tab to Ad Groups, Keywords, Ads, and Shopping
pages following the pattern established in Chat 26 (Campaigns pilot).

Files Modified:
- routes/ad_groups.py: Added Rules tab integration
- templates/ad_groups_new.html: Added Rules tab UI
- routes/keywords.py: Added Rules tab integration
- templates/keywords_new.html: Added Rules tab UI
- routes/ads.py: Added Rules tab integration
- templates/ads_new.html: Added Rules tab UI
- routes/shopping.py: Added Rules tab integration
- templates/shopping.html: Added Rules tab UI

Changes per page:
- Ad Groups: 2 rules (ADGROUP-001, ADGROUP-002)
- Keywords: 3 rules (KEYWORD-001, KEYWORD-002, KEYWORD-003)
- Ads: 2 rules (AD-001, AD-002)
- Shopping: 6 rules (SHOP-001 through SHOP-006)

Features:
- Card grid layout (3 columns, responsive)
- Slide-in drawer (add/edit rules)
- Campaign picker (specific-scope rules)
- Enable/disable toggle per rule
- Delete functionality with confirmation
- Full CRUD operations via rules_api.py
- Consistent UI/UX across all 5 dashboard pages

Testing:
- All 32 success criteria passing (8 per page)
- CRUD operations tested on all 4 pages
- Cross-page verification (rules filtered correctly)
- Edge cases tested (empty state, many rules, long names)
- No JavaScript errors
- All changes persist correctly

Result: M5 Rules milestone complete across all dashboard pages

Time: [X hours]
Chat: 41
Status: Production ready
```

### **Delivery**

1. Copy files to `/mnt/user-data/outputs/`
2. Use `present_files` tool
3. Provide screenshots of each page's Rules tab
4. Await Master Chat review

---

## ESTIMATED TIME BREAKDOWN

**Part 1: Ad Groups (2h)**
- Review pattern: 10 min
- Update route: 30 min
- Update template: 40 min
- Test: 20 min
- Confirm: 20 min

**Part 2: Keywords (2h)**
- Update route: 30 min
- Update template: 40 min
- Test: 20 min
- Confirm: 30 min

**Part 3: Ads (2h)**
- Update route: 30 min
- Update template: 40 min
- Test: 20 min
- Confirm: 30 min

**Part 4: Shopping (2-3h)**
- Update route: 40 min
- Update template: 60 min (more complex, sub-tabs)
- Test: 30 min
- Final comprehensive test: 30 min

**Documentation (45 min)**
- Summary: 20 min
- Handoff: 25 min

**Total: 8-9 hours**

**Breakdown:**
- Implementation: 5.5-6.5 hours (4 pages)
- Testing: 2 hours (all pages)
- Documentation: 45 min

---

## SEQUENTIAL EXECUTION STRATEGY

**This chat works on 4 pages SEQUENTIALLY:**

1. **Ad Groups** → Test → Confirm working → Proceed
2. **Keywords** → Test → Confirm working → Proceed
3. **Ads** → Test → Confirm working → Proceed
4. **Shopping** → Test → Confirm working → Final comprehensive test

**After each page:**
- Test all CRUD operations
- Verify no JavaScript errors
- Confirm changes persist
- Get confirmation from Christopher before proceeding to next page

**Why sequential?**
- Easier to debug (isolate issues to one page)
- Can roll back individual pages if needed
- Christopher can verify incrementally
- Reduces risk of breaking multiple pages

---

## FINAL REMINDERS

**Before starting:**
1. ✅ Read all 8 project files from `/mnt/project/`
2. ✅ Confirm understanding explicitly
3. ✅ Write exactly 5 questions
4. ✅ STOP and wait for answers
5. ✅ Write detailed build plan
6. ✅ STOP and wait for approval
7. ✅ Execute ONE page at a time
8. ✅ Test EACH page before proceeding to next
9. ✅ WAIT for confirmation after each page
10. ✅ Never provide code snippets (complete files only)

**This completes the M5 Rules milestone across all 5 dashboard pages.**

---

**Ready to start? Upload this brief to the new worker chat.**
