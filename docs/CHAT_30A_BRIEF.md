# CHAT 30A: SEARCH TERMS TABLE + NEGATIVE KEYWORD SUGGESTIONS

**Estimated Time:** 8-10 hours  
**Dependencies:** Keywords page (Chat 21d), analytics.search_term_daily table  
**Priority:** HIGH (Dashboard 3.0 M9 Phase 1)

---

## 🚨 MANDATORY WORKFLOW (BEFORE ANY CODING)

### **STEP 1: Confirm Context + Required Uploads**

**A. Confirm Project Files Read (Available in Project Knowledge)**

State clearly: "I confirm I have read all 8 project files available in Project Knowledge:"

- [ ] PROJECT_ROADMAP.md
- [ ] MASTER_KNOWLEDGE_BASE.md
- [ ] CHAT_WORKING_RULES.md
- [ ] DASHBOARD_PROJECT_PLAN.md
- [ ] WORKFLOW_GUIDE.md
- [ ] WORKFLOW_TEMPLATES.md
- [ ] DETAILED_WORK_LIST.md
- [ ] MASTER_CHAT_5.0_HANDOFF.md

**B. Request Required Uploads (2 Files Only)**

```
Before starting, I need 2 uploads:

1. Codebase ZIP
   Location: C:\Users\User\Desktop\gads-data-layer
   (Create ZIP of entire folder and upload here)

2. CHAT_30A_BRIEF.md (this brief)
   Location: C:\Users\User\Desktop\gads-data-layer\docs\CHAT_30A_BRIEF.md

Upload both now before proceeding.
```

**After uploads received:**
1. Extract ZIP and explore project structure
2. Read CHAT_30A_BRIEF.md in full
3. Confirm understanding of all 8 project files
4. Proceed to STEP 2

---

### **STEP 2: 5 Questions for Master Chat (MANDATORY)**

Per CHAT_WORKING_RULES.md Rule 5 — after reading all documents and understanding the brief, you MUST write exactly 5 clarifying questions.

**Question Format:**
```
5 QUESTIONS FOR MASTER CHAT

Before building, I reviewed the brief, codebase, and all project files. Here are my 5 questions:

Q1. [CATEGORY] Question text here?

Q2. [CATEGORY] Question text here?

Q3. [CATEGORY] Question text here?

Q4. [CATEGORY] Question text here?

Q5. [CATEGORY] Question text here?

Waiting for Master Chat answers before proceeding.
```

**Categories:** [DATABASE], [ROUTE], [DESIGN], [SCOPE], [TESTING]

**Question Quality:**
- ✅ Ask about things NOT clear from brief or codebase
- ✅ Ask about real ambiguities affecting implementation
- ✅ Ask about DB schema, edge cases, design decisions
- ❌ Do NOT ask things answerable by reading the brief
- ❌ Do NOT ask generic questions

**🚨 STOP HERE — Wait for Christopher to paste answers from Master Chat 🚨**

---

### **STEP 3: Build Plan Review (MANDATORY)**

After receiving answers from Master Chat, create a detailed build plan.

**Build Plan Format:**
```
DETAILED BUILD PLAN FOR MASTER CHAT REVIEW

Files to create/modify:
- C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\keywords.py — [what changes]
- C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\keywords.html — [what changes]

Step-by-step implementation:
STEP A: [Task description] (~X min)
  - [Specific action 1]
  - [Specific action 2]
  
STEP B: [Task description] (~X min)
  - [Specific action 1]
  - [Specific action 2]

STEP C: Testing (~X min)
  - [Test 1]
  - [Test 2]

STEP D: Documentation (~X min)

Total estimated time: X minutes
Risks / unknowns: [Any remaining concerns]

Waiting for Master Chat approval before starting.
```

**🚨 STOP HERE — Wait for Christopher to paste approval from Master Chat 🚨**

---

### **STEP 4: Implementation Begins**

Only after BOTH Stage 2 (5 Questions answered) AND Stage 3 (Build Plan approved) are complete, proceed to coding.

Follow the approved build plan step-by-step, requesting current file versions before editing (CHAT_WORKING_RULES.md Rule 2).

---

## CONTEXT

The Keywords page was built in Chat 21d with keyword-level performance data and optimization rules. Search terms data exists in `analytics.search_term_daily` but is not yet exposed in the UI.

Search terms are the actual queries users typed that triggered ads. Analyzing search terms is critical for:
- Finding wasted spend (irrelevant queries)
- Discovering negative keyword opportunities
- Improving targeting precision

This chat adds a **Search Terms tab** to the Keywords page (similar to Shopping's 4-tab structure). Phase 1 focuses on displaying search terms data and flagging negative keyword opportunities with manual actions. Keyword expansion and match type analysis are deferred to Chat 30b.

**Database verification complete:** `analytics.search_term_daily` exists with 23 columns including search_term, keyword_text, match_type, search_term_status, and full performance metrics.

**Schema Confirmed:**
```
search_term                    VARCHAR
keyword_text                   VARCHAR
match_type                     VARCHAR
search_term_status             VARCHAR
impressions                    BIGINT
clicks                         BIGINT
cost_micros                    BIGINT
cost                           DOUBLE
conversions                    DOUBLE
conversions_value              DOUBLE
ctr                            DOUBLE
cpc                            DOUBLE
cpa                            DOUBLE
roas                           DOUBLE
(+ metadata: run_id, ingested_at, customer_id, snapshot_date, campaign_id, campaign_name, ad_group_id, ad_group_name, keyword_id)
```

---

## OBJECTIVE

Add a Search Terms tab to the Keywords page with a comprehensive data table, filters, pagination, negative keyword flagging logic, and manual action buttons (row-level + bulk).

---

## REQUIREMENTS

### Deliverables

**1. File:** `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\keywords.py` (MODIFY)
- Add search terms data query from `ro.analytics.search_term_daily`
- Implement negative keyword flagging logic (3 criteria)
- Add filters: date range, campaign, status, match type
- Add pagination (10/25/50/100)
- Return data for search terms table
- Respect session-based date range from M1 date picker

**2. File:** `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\keywords.html` (MODIFY)
- Add "Search Terms" as 2nd tab (after Keywords tab)
- 15+ column table with search terms data
- Filter bar (campaign dropdown, status dropdown, match type dropdown)
- Search input (client-side filter by search term text)
- Pagination controls
- Negative keyword flag badge/indicator per row
- Row-level "Add as Negative" button
- Bulk select checkboxes + "Add Selected as Negatives" button
- Match existing Keywords page styling (Bootstrap 5)

**3. Negative Keyword Logic**
Flag search terms meeting **ANY** of these criteria:
- **Criterion 1:** 0% CVR + ≥10 clicks
- **Criterion 2:** ≥£50 cost + 0 conversions
- **Criterion 3:** CTR <1% + ≥20 impressions

Display flagged terms with visual indicator (e.g., red badge "Negative Opportunity").

**4. Manual Actions (UI Only - No Live Execution)**
- Row-level: "Add as Negative" button per search term
- Bulk: Checkboxes + "Add Selected as Negatives" button
- Actions show confirmation modal (dummy for now - execution in future chat)
- Modal displays: search term text, reason for flagging, affected campaign/ad group

### Technical Constraints

- **Template:** MUST extend `base_bootstrap.html`
- **Framework:** Bootstrap 5 components only
- **Database:** Query `ro.analytics.search_term_daily` (readonly)
- **Tab Switching:** Use JavaScript show/hide pattern (reference Shopping page)
- **Filters:** Server-side filtering (query parameters) for campaign/status/match type
- **Search:** Client-side filtering for search term text (JavaScript)
- **Pagination:** Server-side (SQL LIMIT/OFFSET)
- **Date Range:** Respect session date range from M1 (same as Keywords tab)
- **Client Filter:** Respect session client_id (same as Keywords tab)
- **No Live Execution:** Action buttons show modals only (no Google Ads API calls yet)

### Design Specifications

**Table Columns (16):**
1. Checkbox (bulk select)
2. Search Term (text, left-aligned, max-width with ellipsis)
3. Keyword (mapped keyword text)
4. Match Type (EXACT/PHRASE/BROAD badge)
5. Status (ADDED/EXCLUDED/NONE badge)
6. Negative Flag (red badge if flagged, show criteria)
7. Impressions
8. Clicks
9. CTR
10. Cost
11. CPC
12. Conversions
13. CVR
14. CPA
15. ROAS
16. Actions (Add as Negative button)

**Column Styling:**
- Metrics (Impr, Clicks, Cost, Conv): Right-aligned, monospace font
- Percentages (CTR, CVR): Right-aligned, formatted as "12.5%"
- Currency (Cost, CPC, CPA): Right-aligned, formatted as "£12.34"
- ROAS: Right-aligned, formatted as "3.45x"
- Text (Search Term, Keyword): Left-aligned, truncate long text with tooltip

**Filter Bar (Above Table):**
- Campaign dropdown (all campaigns in current client, sorted alphabetically)
- Status dropdown (All / ADDED / EXCLUDED / NONE)
- Match Type dropdown (All / EXACT / PHRASE / BROAD)
- Search input (placeholder: "Filter by search term...", client-side)
- Clear Filters button (resets all filters)

**Pagination:**
- Options: 10, 25, 50, 100 rows per page (dropdown)
- Default: 25
- Show: "Showing X-Y of Z search terms"
- Navigation: Previous / 1 2 3 ... / Next buttons
- Disable Previous on page 1, disable Next on last page

**Tab Structure:**
```
┌────────────┬──────────────┐
│ Keywords   │ Search Terms │
└────────────┴──────────────┘
```
- Keywords tab: Existing content (unchanged)
- Search Terms tab: New content (this chat)
- Active tab: Blue bottom border, bold text
- Inactive tab: Gray text, hover effect

**Negative Flag Badge:**
- Red background (#dc3545)
- White text
- Text: "⚠ Negative Opportunity"
- Tooltip on hover shows which criteria triggered:
  - "0% CVR with 15 clicks"
  - "£65 cost with 0 conversions"
  - "0.8% CTR with 25 impressions"

**Action Buttons:**
- Row-level: Small red button "Add as Negative"
- Bulk: Primary blue button "Add Selected as Negatives (X)" where X = count
- Modal on click:
  - Title: "Add Negative Keywords"
  - Body: List of search terms to be added
  - Footer: "Cancel" / "Confirm" buttons
  - Note: "This action will be available in a future update"

---

## REFERENCE FILES

**Similar Tab Structure:**
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\shopping.py` — 4-tab route logic
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\shopping.html` — Tab switching JavaScript

**Existing Keywords Page:**
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\keywords.py` — Current route structure
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\keywords.html` — Current UI (Bootstrap 5)

**Table Patterns:**
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\campaigns.py` — Pagination + filtering logic
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\campaigns.html` — Filter bar + table structure

**Session Management:**
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\shared.py` — get_date_range(), get_client_id()

**Database Schema Reference:**
```sql
-- Confirmed via PowerShell DESCRIBE command
TABLE: analytics.search_term_daily
COLUMNS: 23 (see CONTEXT section for full list)
```

---

## SUCCESS CRITERIA

- [ ] 1. Search Terms tab visible and clickable on Keywords page
- [ ] 2. Tab switching works (Keywords ↔ Search Terms, no page reload)
- [ ] 3. Table displays 16 columns with correct data from `ro.analytics.search_term_daily`
- [ ] 4. Campaign filter working (dropdown populated from current client, filters data)
- [ ] 5. Status filter working (All/ADDED/EXCLUDED/NONE)
- [ ] 6. Match Type filter working (All/EXACT/PHRASE/BROAD)
- [ ] 7. Search input working (client-side filter, case-insensitive)
- [ ] 8. Pagination working (10/25/50/100 options, page navigation, correct counts)
- [ ] 9. Negative keyword flags shown correctly (red badge for terms meeting any of 3 criteria)
- [ ] 10. Row-level "Add as Negative" button shows modal with search term details
- [ ] 11. Bulk select working (checkboxes, select all, count updates in button)
- [ ] 12. "Add Selected as Negatives" button shows modal with selected count
- [ ] 13. Date range from M1 date picker respected (same as Keywords tab)
- [ ] 14. Client switching respected (search terms filtered by session client_id)
- [ ] 15. No JavaScript console errors
- [ ] 16. Page loads in <2 seconds, filters apply in <1 second

**ALL 16 must pass for approval.**

---

## TESTING INSTRUCTIONS

### Manual Testing

**Test 1: Tab Switching**
```
1. Navigate to /keywords page
2. Verify Keywords tab is active by default
3. Click "Search Terms" tab
4. Verify: Search Terms table loads, no console errors
5. Verify: Tab shows blue bottom border (active state)
6. Click "Keywords" tab
7. Verify: Returns to keywords view
8. Click "Search Terms" again
9. Verify: Loads correctly on second click (no JS errors)
```

**Test 2: Filters - Campaign**
```
1. Note initial row count
2. Select specific campaign from dropdown
3. Verify: Table updates, only search terms from that campaign shown
4. Verify: All rows show correct campaign name
5. Select different campaign
6. Verify: Table updates again
7. Select "All Campaigns"
8. Verify: Returns to full dataset
```

**Test 3: Filters - Status**
```
1. Select "EXCLUDED" status
2. Verify: Only search terms with status "EXCLUDED" shown
3. Select "ADDED"
4. Verify: Only "ADDED" terms shown
5. Select "NONE"
6. Verify: Only "NONE" terms shown
7. Select "All"
8. Verify: All statuses shown
```

**Test 4: Filters - Match Type**
```
1. Select "EXACT"
2. Verify: Only exact match search terms shown
3. Verify: Match Type column shows only "EXACT"
4. Select "PHRASE"
5. Verify: Only phrase match shown
6. Select "BROAD"
7. Verify: Only broad match shown
8. Select "All"
9. Verify: All match types shown
```

**Test 5: Search Input (Client-Side)**
```
1. Type "shoes" in search input
2. Verify: Only search terms containing "shoes" displayed
3. Verify: Case-insensitive ("Shoes", "SHOES", "shoes" all match)
4. Clear search input
5. Verify: Full dataset returns
6. Type partial term "run"
7. Verify: Matches "running", "run", "runner", etc.
```

**Test 6: Pagination**
```
1. Set to 10 rows
2. Verify: Exactly 10 rows shown
3. Verify: Shows "Showing 1-10 of X search terms"
4. Click page 2
5. Verify: Shows "Showing 11-20 of X search terms"
6. Verify: Different 10 rows displayed
7. Set to 100 rows
8. Verify: Up to 100 rows shown
9. Verify: Pagination buttons update correctly
10. Click "Previous" on page 2
11. Verify: Returns to page 1
```

**Test 7: Negative Keyword Logic**
```
1. Find search term with 0 conversions and ≥10 clicks
2. Calculate CVR manually (0%)
3. Verify: Red "⚠ Negative Opportunity" badge shown
4. Hover over badge
5. Verify: Tooltip shows "0% CVR with [X] clicks"

6. Find search term with ≥£50 cost and 0 conversions
7. Verify: Red badge shown
8. Hover over badge
9. Verify: Tooltip shows "£[X] cost with 0 conversions"

10. Find search term with CTR <1% and ≥20 impressions
11. Calculate CTR manually (clicks / impressions * 100)
12. Verify: Red badge shown
13. Hover over badge
14. Verify: Tooltip shows "[X]% CTR with [Y] impressions"

15. Find search term NOT meeting any criteria
16. Verify: NO badge shown
```

**Test 8: Row-Level Actions**
```
1. Click "Add as Negative" button on any row
2. Verify: Modal appears
3. Verify: Modal shows search term text
4. Verify: Modal shows campaign and ad group
5. Verify: Modal has "Cancel" and "Confirm" buttons
6. Click "Cancel"
7. Verify: Modal closes, no changes
8. Click "Add as Negative" again
9. Click "Confirm"
10. Verify: Modal shows "This action will be available in a future update"
11. Verify: Modal closes
```

**Test 9: Bulk Select**
```
1. Check checkbox on 3 individual rows
2. Verify: Checkboxes visually checked
3. Verify: Button text updates to "Add Selected as Negatives (3)"
4. Uncheck 1 row
5. Verify: Button text updates to "(2)"
6. Click "Select All" checkbox in header
7. Verify: All visible rows checked
8. Verify: Button shows count of ALL rows on current page
9. Click "Select All" again
10. Verify: All checkboxes unchecked
11. Verify: Button disabled or shows "(0)"
```

**Test 10: Bulk Actions**
```
1. Check 5 rows
2. Click "Add Selected as Negatives (5)"
3. Verify: Modal appears
4. Verify: Modal lists all 5 search terms
5. Verify: Modal shows total count
6. Click "Confirm"
7. Verify: Modal shows "This action will be available in a future update"
8. Verify: Modal closes
```

**Test 11: Date Range Integration**
```
1. Note current date range in date picker (e.g., "Last 7 days")
2. Switch to Search Terms tab
3. Verify: Data respects same date range
4. Click Keywords tab
5. Change date range to "Last 30 days"
6. Switch back to Search Terms tab
7. Verify: Data updates to 30-day range
8. Verify: More/different search terms shown
```

**Test 12: Client Switching**
```
1. Note current client name in session
2. Verify: Search terms shown belong to this client
3. Switch to different client (if multi-client setup available)
4. Navigate to Keywords → Search Terms tab
5. Verify: Different search terms shown (from new client)
6. Verify: Campaign dropdown shows campaigns from new client
```

### Edge Cases to Test

**1. Empty Data**
```
- Select campaign with 0 search terms
- Verify: Table shows "No search terms found for this campaign"
- Verify: No JavaScript errors
```

**2. NULL Metrics**
```
- Find search term with NULL CTR (0 clicks, >0 impressions)
- Verify: Displays as "0%" or "—"
- Verify: Does not trigger negative keyword flag
```

**3. NULL Conversions**
```
- Find search term with NULL conversions
- Verify: Displays as "0" or "—"
- Verify: CVR displays as "0%" or "—"
```

**4. Large Dataset**
```
- View client with 1000+ search terms
- Verify: Pagination handles correctly
- Verify: Page load time <2 seconds
- Verify: Filter application time <1 second
```

**5. Long Search Terms**
```
- Find search term with >100 characters
- Verify: Text truncates with ellipsis
- Verify: Full text visible on hover (tooltip)
```

**6. All Filters Active**
```
- Set Campaign, Status, Match Type filters simultaneously
- Type in Search input
- Verify: All filters apply correctly (AND logic)
- Verify: Correct subset of data shown
- Click "Clear Filters"
- Verify: All filters reset to defaults
```

**7. Zero Results**
```
- Apply filter combination that yields 0 results
- Verify: Shows "No search terms match your filters"
- Verify: Table doesn't break
- Verify: Can clear filters to restore data
```

### Performance Testing

```
- Initial Search Terms tab load: <2 seconds
- Filter application (campaign/status/match type): <1 second
- Pagination (page change): <500ms
- Client-side search: <100ms (instant)
- Tab switching: <200ms
```

### Browser Console Check

```
1. Open browser DevTools (F12)
2. Go to Console tab
3. Navigate through all features (tabs, filters, pagination, actions)
4. Verify: Zero errors (red text)
5. Verify: Zero warnings (yellow text) related to this code
6. Check Network tab
7. Verify: All requests return 200 status
8. Verify: No 404s or 500s
```

---

## POTENTIAL ISSUES

### Common Pitfalls to Avoid

**1. Issue: search_term_status Values Mismatch**
- **Problem:** Database may use different values than expected (e.g., "added" vs "ADDED")
- **How to check:** Run `SELECT DISTINCT search_term_status FROM analytics.search_term_daily` during Step 2
- **Solution:** Use actual values from database, handle case-insensitivity
- **Prevention:** Verify actual enum values before hardcoding filter options

**2. Issue: NULL Handling in Calculated Metrics**
- **Problem:** CTR, CVR, ROAS may be NULL for low-volume terms or 0-denominator cases
- **Where it breaks:** Negative keyword logic (comparing to thresholds), table display
- **Solution:** Use SQL `COALESCE(metric, 0)` or Jinja `{{ value or '—' }}`
- **Prevention:** Test with NULL-heavy dataset before reporting complete

**3. Issue: Division by Zero in Negative Keyword Logic**
- **Problem:** CVR calculation when impressions = 0 or clicks = 0
- **Where it breaks:** Criterion 1 (0% CVR) and Criterion 3 (CTR <1%)
- **Solution:** Add guards in SQL: `WHERE clicks > 0 AND impressions > 0`
- **Prevention:** Always check denominator >0 before any percentage calculation

**4. Issue: Tab Switching JavaScript Conflicts**
- **Problem:** Existing Keywords page JS may interfere with new Search Terms tab JS
- **Where it breaks:** Click events, DOM selectors, global variables
- **Solution:** Use namespaced event handlers (`searchTermsTab.init()`), avoid global vars
- **Prevention:** Review keywords.html existing JS before adding new code

**5. Issue: Cost Column Confusion**
- **Problem:** Database has both `cost_micros` (BIGINT) and `cost` (DOUBLE) columns
- **Which to use:** Use `cost` column (already converted to currency, DOUBLE type)
- **Why:** Avoids manual /1,000,000 conversion and currency symbol handling
- **Prevention:** Reference schema carefully, test with known cost values

**6. Issue: Date Range Session Variable Not Found**
- **Problem:** Search Terms route may not correctly read M1 date picker session variable
- **Where it breaks:** Initial page load shows wrong date range, inconsistent with Keywords tab
- **Solution:** Import and use `get_date_range()` from shared.py (same as Keywords tab)
- **Prevention:** Copy exact session handling pattern from keywords.py

**7. Issue: Client ID Session Variable Not Found**
- **Problem:** Search Terms query may not filter by current session client
- **Where it breaks:** Shows search terms from ALL clients (data leak)
- **Solution:** Import and use `get_client_id()` from shared.py
- **Prevention:** ALWAYS filter by client_id in SQL WHERE clause

**8. Issue: Pagination Count Mismatch**
- **Problem:** Total count shows 500, but only 300 rows exist after filters
- **Where it breaks:** Count query doesn't match data query (different WHERE clauses)
- **Solution:** Run SAME query with COUNT(*) and with SELECT *, ensure identical WHERE
- **Prevention:** Use single SQL query for both count and data, or carefully sync WHERE clauses

**9. Issue: Bulk Select Across Pages**
- **Problem:** User checks 5 rows on page 1, navigates to page 2, checks 3 more
- **Expected:** Button shows "(8)"
- **Common mistake:** Button only shows "(3)" (current page only)
- **Solution:** Use JavaScript array to track ALL selected IDs across pages
- **Prevention:** Test bulk select → change page → verify selection persists

**10. Issue: Long Search Terms Break Layout**
- **Problem:** Search term "buy nike air max 270 white mens size 10 running shoes..." overflows table cell
- **Where it breaks:** Table becomes horizontally scrollable, hard to read
- **Solution:** CSS `max-width: 300px; overflow: hidden; text-overflow: ellipsis;` + tooltip on hover
- **Prevention:** Test with real search terms data (often 50-100+ characters)

### Known Gotchas

**Date Range Handling:**
- Keywords page has session-based date picker from M1
- Search Terms tab MUST respect same date range
- Use `get_date_range()` from shared.py
- If date range spans >90 days, consider adding warning (large dataset)

**Client Switching:**
- ALWAYS filter by `session['client_id']`
- Use `get_client_id()` from shared.py
- If client_id not in session, redirect to client selector
- Never show cross-client data (critical for multi-client setups)

**Search Term Status Values:**
- Database uses uppercase: "ADDED", "EXCLUDED", "NONE"
- Display can be Title Case: "Added", "Excluded", "None"
- Filter dropdown should use database values for querying

**Match Type Display:**
- Store as uppercase: "EXACT", "PHRASE", "BROAD"
- Display as Title Case: "Exact", "Phrase", "Broad"
- Use badge styling (blue for EXACT, green for PHRASE, gray for BROAD)

**Negative Keyword Thresholds:**
- 0% CVR + ≥10 clicks: Threshold chosen to ensure sufficient data
- ≥£50 cost + 0 conversions: Assumes client is UK-based (adjust currency if needed)
- CTR <1% + ≥20 impressions: Industry benchmark for low relevance
- These are hardcoded for Phase 1, will move to rules_config.json in future

**Modal Behavior:**
- "Add as Negative" actions are UI-only in Phase 1
- Modal should clearly state "This action will be available in a future update"
- Do NOT call any API endpoints from modal
- Do NOT modify database on confirmation click

**Performance Considerations:**
- `search_term_daily` table can have 10,000+ rows per client
- ALWAYS use pagination (never load all rows)
- ALWAYS use indexes on campaign_id, customer_id, snapshot_date
- Consider adding loading spinner during filter application

---

## HANDOFF REQUIREMENTS

**Documentation:**
Create comprehensive handoff document:

**File:** `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_30A_HANDOFF.md`

**Required Sections:**
1. **Executive Summary** (2-3 sentences: what was built)
2. **Deliverables** (files created/modified with line counts)
3. **Success Criteria Results** (16/16 with evidence: screenshots, logs)
4. **Implementation Details** (approach, key decisions, code patterns)
5. **Issues Encountered** (problems + root causes + solutions + time lost)
6. **Testing Results** (all 12 manual tests + 7 edge cases)
7. **Database Queries** (SQL with performance metrics)
8. **Technical Debt** (intentional shortcuts + deferred items)
9. **Git Commit Message** (use template below)
10. **Future Enhancements** (Phase 2 scope: keyword expansion, match type analysis)
11. **Notes for Master** (review priorities, special attention areas, dependencies)

**Git Commit Message Template:**
```
feat: Add Search Terms tab to Keywords page (M9 Phase 1)

Keywords - Search Terms analysis and negative keyword suggestions

Features:
- Search Terms tab with 16-column data table
- Campaign, status, match type filters + client-side search
- Pagination (10/25/50/100)
- Negative keyword flagging (3 criteria: CVR/cost/CTR)
- Row-level + bulk "Add as Negative" actions (UI only)

Files Modified:
- routes/keywords.py (XXX lines added) - search terms query, flagging logic
- templates/keywords.html (XXX lines added) - new tab, table, filters, actions

Database:
- Queries ro.analytics.search_term_daily (23 columns)
- Respects session date range and client_id

Testing:
- All 16 success criteria passing
- 12 manual tests + 7 edge cases verified
- Performance: <2s load, <1s filter, zero JS errors

Issues Resolved:
- [Issue 1]
- [Issue 2]

Time: [X hours] ([actual] vs 8-10 estimated)
Chat: 30a
Status: Phase 1 complete, Phase 2 (keyword expansion) deferred to Chat 30b
```

**Delivery Process:**
1. Copy both files to `/mnt/user-data/outputs/`:
   - `keywords.py`
   - `keywords.html`
   - `CHAT_30A_HANDOFF.md`
2. Use `present_files` tool with all 3 files
3. Provide brief summary of completion
4. Await Master Chat review

---

## ESTIMATED TIME BREAKDOWN

- **Setup:** 10 min (confirm files, extract ZIP, environment check)
- **Step 2: 5 Questions:** 15 min (formulate, send, wait for answers)
- **Step 3: Build Plan:** 20 min (detailed plan, send, wait for approval)
- **Database query development:** 60 min (search terms query, filters, pagination SQL, flagging logic)
- **Negative keyword logic:** 90 min (3 criteria implementation, edge cases, NULL handling, testing)
- **Route modifications:** 60 min (keywords.py updates, new endpoints, session integration)
- **Template modifications:** 120 min (tab structure, table, filter bar, pagination UI, action buttons)
- **JavaScript:** 60 min (tab switching, bulk select, client-side search, modal triggers)
- **Testing:** 90 min (16 success criteria, 12 manual tests, 7 edge cases, performance checks)
- **Documentation:** 45 min (comprehensive handoff doc)

**Subtotal: 570 minutes (9.5 hours)**

**Total with buffer: 8-10 hours**

**Escalation Trigger:** If exceeds 6 hours with <50% completion (4/8 criteria passing), escalate to Master Chat for guidance.

---

## ADDITIONAL NOTES

**Negative Keyword Criteria Rationale:**
- **Criterion 1 (0% CVR + ≥10 clicks):** Sufficient data to determine search term is irrelevant or low-intent
- **Criterion 2 (≥£50 cost + 0 conversions):** Clear wasted spend threshold that justifies immediate action
- **Criterion 3 (CTR <1% + ≥20 impressions):** Industry benchmark for low relevance/poor ad-to-query match

These thresholds are:
- Hardcoded in Phase 1 for simplicity
- Configurable in future (move to `rules_config.json` or client settings)
- Based on typical e-commerce client performance
- Adjust for different industries/client goals in Phase 2

**Future Enhancements (Chat 30b Scope):**
- **Keyword Expansion:** Identify high-performing search terms (CVR >5%, ROAS >4x) not yet added as keywords
- **Match Type Effectiveness:** Analyze which match types perform best per keyword
- **"Add as Keyword" Actions:** UI + execution for adding search terms as new keywords
- **Search Term Clustering:** Group similar search terms for bulk negative keyword actions
- **Historical Trends:** Compare search term performance week-over-week
- **Automated Rules:** Create rules in `rules_config.json` for auto-suggesting negatives

**Known Limitations:**
- Phase 1 is display + manual actions only (no live Google Ads API execution)
- Negative keyword suggestions are based on performance only (not intent/brand safety)
- Bulk actions limited to current page (cross-page selection in Phase 2)
- No export to CSV functionality (add in future if requested)

**Database Performance Notes:**
- `search_term_daily` can have 10,000-50,000 rows per client
- Pagination is REQUIRED (never load all rows)
- Indexes assumed on: customer_id, campaign_id, snapshot_date
- If query >2 seconds, escalate to Master Chat for index optimization

**Client-Side Search Notes:**
- Search input filters VISIBLE rows only (current page)
- Does NOT search across ALL pages (would require re-querying database)
- Case-insensitive matching using JavaScript `.toLowerCase()`
- Matches substring anywhere in search term (not just start)

---

**Ready to start? Confirm you have read all 8 project files, then request the 2 uploads (codebase ZIP + this brief).**
