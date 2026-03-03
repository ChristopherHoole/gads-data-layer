# CHAT 53: FIX BACKEND ROUTES - METRICS CARDS DATA (KEYWORDS, SHOPPING, AD GROUPS)

**Estimated Time:** 4.5 hours  
**Dependencies:** Chat 52 complete (Metrics Cards UI redesign), Database verification complete  
**Priority:** HIGH

---

## 🚨 CRITICAL WORKFLOW RULES

**Christopher will ONLY upload this brief (CHAT_53_BRIEF.md). Everything else is in `/mnt/project/`.**

**YOUR FIRST STEP:**
```
✅ WORKFLOW UNDERSTOOD

I confirm:
1. Christopher will ONLY upload the brief (CHAT_53_BRIEF.md)
2. I will read ALL project files from /mnt/project/ using view tool
3. I will NOT request codebase ZIP (too large)
4. I will NOT request any documentation files (already available in /mnt/project/)
5. I will send 5 QUESTIONS to Master Chat and WAIT for answers
6. I will create DETAILED BUILD PLAN and WAIT for Master approval
7. I will implement step-by-step, testing at each stage
8. I will work ONE FILE AT A TIME
9. Christopher does NOT edit code - I request file, he uploads, I edit, I return complete file with full save path

Ready to begin.
```

**THEN:**
1. Use `view` tool to read all files from `/mnt/project/`
2. Read this brief thoroughly
3. Proceed to 5 QUESTIONS stage (MANDATORY)

---

## CONTEXT

### What's Been Done

**Chat 52** (Metrics Cards Redesign) successfully updated the visual design of metrics cards across all 6 pages. The new design features white backgrounds, color-coded left borders (green/blue/gray), sentence case labels, and interactive SVG sparklines with hover tooltips.

**Investigation (Feb 28, 2026)** revealed that 3 out of 6 pages have incomplete backend implementations:
- **Keywords:** Has sparkline queries but hardcodes `change_pct = None`
- **Shopping:** Has current period query but missing previous period and sparkline queries
- **Ad Groups:** Returns hardcoded placeholder data, doesn't query database at all

**Dashboard and Campaigns pages work perfectly** because they implement the complete pattern: current period query + previous period query + sparkline query + calculate change percentages.

### Why This Task Is Needed

The metrics cards template (updated in Chat 52) expects three pieces of data:
1. `value_display` - Current metric value (formatted)
2. `change_pct` - Percentage change vs previous period
3. `sparkline_data` - Array of values for sparkline chart

Currently, 3 routes provide incomplete data:
- Keywords: Provides #1 and #3, but hardcodes #2 to None → shows "—" for changes, grey sparklines
- Shopping: Provides #1 only, hardcodes #2 and #3 → shows "—" for changes, no sparklines
- Ad Groups: Hardcodes all three → shows placeholder "£0" values

### How It Fits

This completes the backend implementation to match Chat 52's UI improvements. After this chat:
- 5 out of 6 pages will be fully functional (colored sparklines, change percentages)
- Only Ads page will remain incomplete (blocked by missing `ad_daily` table)

---

## OBJECTIVE

Fix 3 backend routes (Keywords, Shopping, Ad Groups) to provide complete metrics cards data including period-over-period change percentages and sparkline arrays.

---

## REQUIREMENTS

### Deliverables

1. **keywords.py:** C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\keywords.py (modify)
   - Purpose: Add previous period comparison to Keywords route
   - Key changes:
     - Add previous period SQL query
     - Add `_calculate_change_pct()` function
     - Update `_card_kw()` to accept `prev` parameter and calculate change_pct
     - Pass previous values to all card definitions

2. **shopping.py:** C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\shopping.py (modify)
   - Purpose: Add previous period comparison and sparklines to Shopping route
   - Key changes:
     - Add previous period SQL query for campaign metrics
     - Add daily sparkline query for campaign metrics
     - Add `_calculate_change_pct()` function
     - Update `_card_sh()` to accept `prev` and `sparkline` parameters
     - Build sparkline arrays from daily breakdown
     - Pass previous values and sparklines to all card definitions

3. **ad_groups.py:** C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\ad_groups.py (modify)
   - Purpose: Replace hardcoded placeholder with real database queries
   - Key changes:
     - Delete `build_adgroup_metrics_cards()` function (lines 193-217)
     - Create new `load_ad_group_metrics_cards()` function
     - Add current period, previous period, and sparkline SQL queries
     - Add helper functions: `_calculate_change_pct()`, `_card()`, `_blank_card()`, `_fmt()`
     - Build cards dynamically from query results

4. **CHAT_53_SUMMARY.md:** C:\Users\User\Desktop\gads-data-layer\docs\CHAT_53_SUMMARY.md (create)
   - Purpose: Executive summary for quick reference
   - Key sections: Overview, deliverables, testing results, screenshots, statistics

5. **CHAT_53_HANDOFF.md:** C:\Users\User\Desktop\gads-data-layer\docs\CHAT_53_HANDOFF.md (create)
   - Purpose: Technical documentation for future work
   - Key sections: Architecture, code changes, testing procedures, git strategy

### Technical Constraints

- **Database:** Query `warehouse_readonly.duckdb` (Flask attaches as `ro` catalog)
- **Table prefix:** Use `ro.analytics.*` for all queries
- **Customer ID:** 9999999999 (Synthetic Test Client)
- **Date range:** Data available from Feb 22, 2025 to Feb 21, 2026 (365 days)
- **Pattern to follow:** Copy from `campaigns.py` (working reference implementation)
- **Must test:** All 3 routes with PowerShell + browser verification
- **No jQuery:** Use vanilla JavaScript only
- **Browser:** Primary testing in Opera

### Design Specifications

**Working Reference Pattern (from campaigns.py):**

All routes must implement these three components:

**1. Helper Functions:**
- `_calculate_change_pct(current, previous)` - Returns percentage change or None
- `_card(label, value, prev, sparkline, fmt, invert, card_type)` - Builds card dict
- `_blank_card(card_type)` - Builds blank placeholder card
- `_fmt(value, fmt)` - Formats values for display

**2. SQL Queries (3 per route):**
- Current period aggregate (SUM all metrics WHERE date filter)
- Previous period aggregate (SUM all metrics WHERE previous date filter)
- Daily sparklines (GROUP BY snapshot_date, ORDER BY snapshot_date ASC)

**3. Data Flow:**
- Execute 3 queries → Extract current and previous values
- Build sparkline arrays from daily data
- Call `_card(label, current, previous, sparkline, ...)` for each metric
- Return `(financial_cards, actions_cards)` tuple

---

## REFERENCE FILES

**Working Implementation (MUST READ FIRST):**
- `act_dashboard/routes/campaigns.py` (lines 230-520) - COMPLETE pattern to copy
- `act_dashboard/routes/dashboard.py` (lines 62-220) - Alternative working example

**Files to Modify:**
- `act_dashboard/routes/keywords.py` (lines 572-715) - 40% complete, needs prev query
- `act_dashboard/routes/shopping.py` (lines 535-619) - 30% complete, needs prev + sparklines
- `act_dashboard/routes/ad_groups.py` (lines 193-300) - 0% complete, full rewrite needed

**Investigation Documentation:**
- Read from /mnt/project/ or uploaded by Christopher:
  - `INVESTIGATION_SUMMARY.md` - Overview of findings
  - `FINAL_FIX_STRATEGY.md` - Detailed implementation guide with code patterns
  - `BACKEND_ROUTES_DIAGNOSIS.md` - Line-by-line code analysis

**Database Tables:**
- `ro.analytics.keyword_daily` - 77,368 rows (Nov 2025 - Feb 2026)
- `ro.analytics.shopping_campaign_daily` - 7,300 rows (Feb 2025 - Feb 2026)
- `ro.analytics.ad_group_daily` - 23,725 rows (Feb 2025 - Feb 2026)

---

## SUCCESS CRITERIA

**Keywords Route (8 criteria):**
- [ ] 1. Previous period query added (queries `ro.analytics.keyword_daily`)
- [ ] 2. `_calculate_change_pct()` function added
- [ ] 3. `_card_kw()` updated to accept `prev` parameter
- [ ] 4. `_card_kw()` calls `_calculate_change_pct(value, prev)` instead of hardcoding None
- [ ] 5. All financial cards pass previous values
- [ ] 6. All actions cards pass previous values
- [ ] 7. Keywords page loads without errors
- [ ] 8. Change percentages show actual values (not "—")

**Shopping Route (10 criteria):**
- [ ] 9. Previous period query added for campaign metrics
- [ ] 10. Daily sparkline query added for campaign metrics
- [ ] 11. `_calculate_change_pct()` function added
- [ ] 12. `_card_sh()` updated to accept `prev` and `sparkline` parameters
- [ ] 13. `_card_sh()` calls `_calculate_change_pct(value, prev)`
- [ ] 14. Sparkline arrays built from daily data (not empty arrays)
- [ ] 15. All campaign cards pass previous values and sparklines
- [ ] 16. Shopping page loads without errors
- [ ] 17. Change percentages show actual values
- [ ] 18. Sparklines render with colors (not grey)

**Ad Groups Route (12 criteria):**
- [ ] 19. Old `build_adgroup_metrics_cards()` function deleted
- [ ] 20. New `load_ad_group_metrics_cards()` function created with proper parameters
- [ ] 21. Current period query added (queries `ro.analytics.ad_group_daily`)
- [ ] 22. Previous period query added
- [ ] 23. Daily sparkline query added
- [ ] 24. `_calculate_change_pct()` function added
- [ ] 25. `_card()` helper function added
- [ ] 26. `_blank_card()` helper function added
- [ ] 27. `_fmt()` formatting function added
- [ ] 28. Cards built from query results (not hardcoded)
- [ ] 29. Ad Groups page loads without errors
- [ ] 30. Change percentages and sparklines show real data

**Overall (5 criteria):**
- [ ] 31. All 3 routes tested in browser (screenshots captured)
- [ ] 32. Sparklines are colored (green/red/gray based on change)
- [ ] 33. Hover over sparklines shows dot + tooltip
- [ ] 34. No JavaScript console errors on any page
- [ ] 35. Git commit message prepared following project template

**ALL 35 criteria must pass for approval.**

---

## 5 QUESTIONS STAGE (MANDATORY)

**After reading all project files, you MUST write EXACTLY 5 questions and send them to Master Chat.**

Format:
```
5 QUESTIONS FOR MASTER CHAT

Q1. [CATEGORY] Question text here?
Q2. [CATEGORY] Question text here?
Q3. [CATEGORY] Question text here?
Q4. [CATEGORY] Question text here?
Q5. [CATEGORY] Question text here?

Waiting for Master Chat answers before proceeding to build plan.
```

Categories: [DATABASE], [ROUTE], [DESIGN], [RULES], [SCOPE], [ARCHITECTURE]

---

## BUILD PLAN STAGE (MANDATORY)

**After receiving answers to 5 questions, you MUST create a detailed build plan and send it to Master Chat for approval.**

Format:
```
DETAILED BUILD PLAN FOR MASTER CHAT REVIEW

Overview:
- Total files to create/modify: [N]
- Total estimated time: [X hours]
- Implementation approach: [1-2 sentences]

Files to create/modify:
1. [Full Windows path] — [what changes, why needed]
2. [Full Windows path] — [what changes, why needed]

Step-by-step implementation (with testing):
STEP 1: [Task description] (~X min)
  - [Specific action 1]
  - [Specific action 2]
  - TEST: [How to verify this step works]
  
STEP 2: [Task description] (~X min)
  - [Specific action 1]
  - TEST: [How to verify this step works]

Total estimated time: X hours
Risks / unknowns: [Any remaining concerns]

Waiting for Master Chat approval before starting implementation.
```

**ONLY AFTER Master Chat explicitly approves your build plan can you begin implementation.**

---

## TESTING INSTRUCTIONS

### Manual Testing (ALL 3 routes)

**Per Route Testing Protocol:**

1. **Start fresh PowerShell session:**
   ```powershell
   cd C:\Users\User\Desktop\gads-data-layer
   .\.venv\Scripts\Activate.ps1
   python -m flask run
   ```

2. **Navigate to page in Opera browser**

3. **Visual verification:**
   - All metrics cards display values (not "—" or "£0")
   - Change percentages show actual values (e.g., "-9.1%", "+3.4%")
   - Change percentages colored correctly (green for good, red for bad)
   - Sparklines render (not blank spaces)
   - Sparklines colored (green/red/gray, not all grey)

4. **Interactive verification:**
   - Hover over each sparkline
   - Verify dot appears and follows mouse
   - Verify tooltip shows value
   - Test on multiple cards

5. **Console verification:**
   - Open browser DevTools (F12)
   - Check Console tab
   - Verify zero errors

6. **Screenshot capture:**
   - Full page view
   - Close-up of metrics cards
   - Sparkline hover (showing dot + tooltip)
   - Browser console (showing no errors)

### Specific Route Tests

**Keywords Page:**
- Verify 4 Financial cards: Cost, Revenue, ROAS, Wasted Spend
- Verify 3 Leads cards: Conversions, Cost/Conv, Conv Rate
- Verify 8 Actions cards
- Verify "Wasted Spend" metric displays correctly
- Verify all change percentages are NOT "—"

**Shopping Page:**
- Verify Campaign metrics section (3 Financial + 3 Leads)
- Verify sparklines render
- Verify change percentages are NOT "—"
- Note: Product metrics will remain incomplete (expected)

**Ad Groups Page:**
- Verify ALL cards show real data (not "£0" placeholders)
- Verify Financial metrics (Cost, Revenue, ROAS, Wasted Spend, Conv, CPA, CVR)
- Verify Actions metrics (Impressions, Clicks, CPC, CTR, IS metrics)
- Verify change percentages are NOT "—"
- Verify sparklines render

### Edge Cases to Test

1. **Different date ranges:**
   - Default (last 30 days)
   - Custom date range (select dates in UI)
   - Verify queries adapt correctly

2. **Actions toggle:**
   - Collapse Actions section
   - Expand Actions section
   - Verify works on all 3 pages

3. **Page refresh:**
   - Hard refresh (Ctrl+F5)
   - Verify data persists

### Performance Expectations

- Page load: <2 seconds per page
- Query execution: <500ms per query
- Sparkline render: <100ms
- No memory leaks (check DevTools Performance tab)

**IMPORTANT:** Test AT EVERY STEP if the step produces testable output.

---

## POTENTIAL ISSUES

### Common Pitfalls to Avoid

1. **Wrong table prefix:**
   - Issue: Querying `analytics.table_name` instead of `ro.analytics.table_name`
   - Solution: Always use `ro.analytics.*` prefix
   - Verification: Check Flask database connection in shared.py

2. **Incorrect date filter logic:**
   - Issue: Previous period calculation off by one day
   - Solution: Copy date filter logic exactly from campaigns.py
   - Verification: Print date ranges to console during development

3. **Sparkline point ordering:**
   - Issue: Sparklines rendered backwards (newest → oldest instead of oldest → newest)
   - Solution: Always `ORDER BY snapshot_date ASC` in sparkline query
   - Verification: Hover over sparkline and check if values increase/decrease correctly

4. **Missing percentage conversion:**
   - Issue: CTR, Conv Rate showing as 0.03 instead of 3.0%
   - Solution: Multiply by 100 for percentage metrics
   - Verification: Check card displays show "3.0%" not "0.03"

5. **Hardcoded customer ID:**
   - Issue: Using '9999999999' instead of variable customer_id
   - Solution: Use customer_id parameter in WHERE clauses
   - Verification: Check if route accepts customer_id from session

### Known Gotchas

- **PowerShell sessions:** Always use fresh PowerShell window for accurate testing
- **Browser cache:** Hard refresh (Ctrl+F5) required after code changes
- **Database attachment:** Flask attaches warehouse_readonly.duckdb as `ro` catalog
- **Synthetic vs real customer:** Routes show synthetic (9999999999) customer by default
- **Features tables:** Don't use `*_features_daily` tables - they only have 1 day of data

---

## HANDOFF REQUIREMENTS

**Documentation (BOTH required):**

1. **CHAT_53_SUMMARY.md** (400-700 lines)
   - Executive overview (what was fixed, why it matters, key achievements)
   - Deliverables summary (files modified, code added)
   - Testing results (35/35 success criteria passed)
   - 12+ screenshots showing:
     - Keywords page with colored sparklines
     - Shopping page with colored sparklines
     - Ad Groups page with real data
     - Sparkline hover interactions (3 screenshots, one per page)
     - Browser console (no errors)
     - Before/after comparisons
   - Time tracking (estimated vs actual)
   - Issues encountered (if any)
   - Key statistics (queries added, lines of code, completion time)

2. **CHAT_53_HANDOFF.md** (800-1,500 lines)
   - Technical architecture (3 routes, each with 3 queries)
   - Files modified with line numbers (BEFORE → AFTER for each change)
   - Code explanations:
     - Date filter calculation logic
     - Period-over-period comparison algorithm
     - Sparkline data extraction from daily breakdown
     - SQL query patterns (current, previous, sparklines)
   - Testing procedures (detailed step-by-step for future verification)
   - Success criteria verification (all 35 criteria with checkmarks)
   - Known limitations (Ads page still incomplete - no ad_daily table)
   - Future enhancements (fix Ads page when ad_daily table created)
   - For next chat notes (what Module 3 needs to know)
   - Git commit strategy (ready commit message)

**Git:**
- Prepare commit message using project template:
  ```
  feat(backend): Add period comparison and sparklines to Keywords, Shopping, Ad Groups routes
  
  Fixes incomplete backend implementations for 3 routes. All routes now provide:
  - Period-over-period change percentages
  - Daily sparkline data arrays
  - Proper color-coded change indicators
  
  Technical:
  - Keywords: Added previous period query, calculate change_pct
  - Shopping: Added previous/sparkline queries, calculate change_pct
  - Ad Groups: Complete rewrite, queries ad_group_daily table
  - All routes follow campaigns.py pattern
  
  Database:
  - Queries ro.analytics.keyword_daily (77k rows)
  - Queries ro.analytics.shopping_campaign_daily (7.3k rows)
  - Queries ro.analytics.ad_group_daily (23k rows)
  
  Files:
  - modify: act_dashboard/routes/keywords.py (~XXX lines changed)
  - modify: act_dashboard/routes/shopping.py (~YYY lines changed)
  - modify: act_dashboard/routes/ad_groups.py (~ZZZ lines changed)
  
  Testing: 35/35 success criteria passed, 12+ screenshots captured
  
  Known limitation: Ads page remains incomplete (ad_daily table doesn't exist)
  
  Chat: 53 | Time: X.X hours | Commits: 1
  ```

**Delivery:**
- Copy BOTH documents to /mnt/user-data/outputs/
- Use present_files tool to share with Master Chat
- Await Master review before git commits

---

## ESTIMATED TIME BREAKDOWN

- 5 Questions + Build Plan: 30 min
- Keywords route fix: 60 min
- Shopping route fix: 90 min
- Ad Groups route fix: 120 min
- Testing (comprehensive, all 3 routes): 45 min
- Documentation (SUMMARY + HANDOFF): 120 min
**Total: 4 hours 45 min**

**Note:** Documentation time accounts for creating BOTH CHAT_53_SUMMARY.md (400-700 lines) AND CHAT_53_HANDOFF.md (800-1,500 lines), including 12+ screenshots and detailed code explanations for 3 different routes.

---

**WORKFLOW REMINDER:**
1. Confirm you understand workflow (see top of brief)
2. Read all files from /mnt/project/ using view tool
3. Send 5 QUESTIONS → WAIT for answers
4. Send DETAILED BUILD PLAN → WAIT for approval
5. Implement step-by-step, ONE FILE AT A TIME, testing at each stage
6. Create handoff documentation
7. Await Master review
