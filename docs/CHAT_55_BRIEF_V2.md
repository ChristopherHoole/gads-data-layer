# CHAT 55: MODULE 3 - GOOGLE ADS CHART DESIGN IMPLEMENTATION

**Estimated Time:** 5-7 hours  
**Dependencies:** Backend routes fix complete (Chat 54), Wireframe approved  
**Priority:** HIGH

---

## 🚨 CRITICAL WORKFLOW RULES

**Christopher will ONLY upload this brief (CHAT_55_BRIEF.md). Everything else is in `/mnt/project/`.**

**YOUR FIRST STEP:**
```
✅ WORKFLOW UNDERSTOOD

I confirm:
1. Christopher will ONLY upload the brief (CHAT_55_BRIEF.md)
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

Chat 52 fixed a critical routing issue where the Dashboard Overview page was loading entity-specific templates instead of the dashboard template. This was resolved by implementing a centralized template selection system in the base route decorator.

Chat 53 completed the Backend Routes Fix for all 6 pages (Dashboard, Campaigns, Keywords, Ad Groups, Ads, Shopping), ensuring each page loads the correct template with proper data. All routes now use the centralized get_performance_data() function.

Chat 54 conducted comprehensive testing across all 6 pages with the new routing system, verifying template loading, data display, and performance metrics. All pages are now functional with the correct templates and entity-specific data.

### Why This Task Is Needed

The current chart design uses outdated colors, has scaling issues where metrics with different ranges appear as flat lines, and lacks the clean Google Ads aesthetic. The A.C.T. platform needs a modern, professional chart visualization that matches the Google Ads interface while incorporating the A.C.T. brand colors from the logo.

A comprehensive wireframe session (Module 3 specification) has been completed with full approval from Christopher. The wireframe demonstrates all required functionality including dynamic metric selection, normalization for different scales, date interval logic, and ACT logo color integration.

### How It Fits

This is Module 3 of the dashboard redesign initiative. It transforms the performance charts across all 6 pages from basic visualizations to professional, Google Ads-style analytics displays. This provides users with clear, readable performance trends regardless of metric scale differences, establishing visual consistency with the A.C.T. brand.

**CRITICAL:** Each of the 6 pages must display its OWN entity-specific data (Dashboard shows account totals, Keywords shows keyword totals, etc.) while using the SAME chart macro and visual design.

---

## OBJECTIVE

Implement Google Ads-style chart design with ACT logo colors, dynamic metric selection, intelligent normalization, and date interval logic across all 6 dashboard pages, ensuring each page displays its entity-specific performance data.

---

## DATA FLOW ARCHITECTURE

### How Data Flows to Charts (CRITICAL TO UNDERSTAND)

**The chart macro is SHARED across all 6 pages but receives DIFFERENT data from each page's route:**

```
┌─────────────────────────────────────────────────────────┐
│ BACKEND ROUTE (routes/campaigns.py, keywords.py, etc.) │
│                                                         │
│ 1. Calls get_performance_data()                        │
│ 2. Aggregates entity-specific metrics                  │
│ 3. Passes data to template                             │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│ PAGE TEMPLATE (campaigns.html, keywords.html, etc.)    │
│                                                         │
│ Calls: {{ performance_chart(data, ...) }}              │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│ CHART MACRO (macros/performance_chart.html)            │
│                                                         │
│ - SAME code for all pages                              │
│ - DIFFERENT data per page                              │
│ - Renders chart with provided entity-specific data     │
└─────────────────────────────────────────────────────────┘
```

### Per-Page Data Sources

| Page       | Database Table                      | Entity Type        | Aggregation                    |
|------------|-------------------------------------|--------------------|--------------------------------|
| Dashboard  | ro.analytics.campaign_performance   | campaign           | Account-level totals           |
| Campaigns  | ro.analytics.campaign_performance   | campaign           | All campaigns summed           |
| Keywords   | ro.analytics.keyword_performance    | keyword            | All keywords summed            |
| Ad Groups  | ro.analytics.ad_group_performance   | ad_group           | All ad groups summed           |
| Ads        | ro.analytics.ad_performance         | ad                 | All ads summed                 |
| Shopping   | ro.analytics.shopping_performance   | shopping_product   | All shopping products summed   |

### Data Structure Passed to Macro

**The macro receives this structure from EVERY page (content differs per page):**

```python
{
    'dates': ['Feb 1', 'Feb 2', 'Feb 3', ...],  # Date labels (daily/weekly/monthly)
    'metrics': {
        'cost': [45000, 47000, 49000, ...],
        'impressions': [1800000, 1950000, 2100000, ...],
        'clicks': [58000, 60000, 63000, ...],
        'avg_cpc': [0.77, 0.78, 0.78, ...],
        'conversions': [580, 600, 630, ...],
        'conv_value': [17400, 18000, 18900, ...],
        'cost_per_conv': [77.59, 78.33, 77.78, ...],
        'conv_rate': [1.0, 1.0, 1.0, ...],
        'ctr': [3.2, 3.1, 3.0, ...],
        'roas': [0.39, 0.38, 0.39, ...]
    }
}
```

**Example:** Keywords page passes keyword-aggregated data, Shopping page passes shopping product-aggregated data, but BOTH use the same macro with the same visual design.

---

## REQUIREMENTS

### Deliverables

1. File: C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\macros\performance_chart.html (modify)
   - Purpose: Replace current chart macro with Google Ads-style design
   - Key features:
     * Uses data structure passed from page route (entity-specific)
     * Two-state metric system (selectedMetrics for cards, visibleMetrics for chart)
     * Normalization to 0-95% range for 3+ metrics (prevents flat lines)
     * Axes hide completely when 3+ metrics (normalized mode)
     * Tooltip shows lines instead of squares, displays real values
     * No grid lines when 1-2 metrics, grid lines when 3+ metrics
     * Metric cards only show selected metrics (dynamic 1-4 count)
     * Links to chart-styles.css for all styling

2. File: C:\Users\User\Desktop\gads-data-layer\act_dashboard\static\css\chart-styles.css (create)
   - Purpose: Centralized styles for charts across all 6 pages
   - **COMPLETE FILE PROVIDED IN THIS BRIEF** (copy exactly as-is)
   - Key features:
     * ACT logo color palette
     * Metric card styling (active/inactive states)
     * Chart container (fixed 300px height)
     * Metrics selector modal
     * Responsive breakpoints (1200px max-width, mobile support)

3. File: C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\base.py (modify if needed)
   - Purpose: Add date interval calculation for chart data
   - Key features:
     * getDateInterval() function (daily ≤30 days, weekly ≤180 days, monthly >180 days)
     * Generate dates array based on interval
     * Pass date labels to chart template
     * Works for ALL entity types (campaign, keyword, ad_group, ad, shopping_product)

4. File: C:\Users\User\Desktop\gads-data-layer\act_dashboard\static\js\chart-config.js (create)
   - Purpose: Centralized Chart.js configuration and logic
   - Key features:
     * ACT color palette constants
     * Normalization logic for 3+ metrics (0-95% ceiling)
     * Tooltip configuration with line indicators
     * Reusable chart initialization function
     * Two-state metric system (selectedMetrics vs visibleMetrics)

5. CHAT_55_SUMMARY.md: C:\Users\User\Desktop\gads-data-layer\docs\CHAT_55_SUMMARY.md (create)
   - Purpose: Executive summary for quick reference
   - Key sections: Overview, deliverables, testing, 10+ screenshots, statistics

6. CHAT_55_HANDOFF.md: C:\Users\User\Desktop\gads-data-layer\docs\CHAT_55_HANDOFF.md (create)
   - Purpose: Technical documentation for future work
   - Key sections: Architecture, code details, testing procedures, git strategy

### Technical Constraints

- Must work across all 6 pages with DIFFERENT entity-specific data
- Chart.js library already loaded (version 4.4.0)
- Bootstrap 5 for UI components (already loaded)
- Database queries use ro.analytics.* prefix
- No external dependencies beyond Chart.js
- All changes must be backward compatible with existing session-based metric selection
- Performance: Chart must render in <500ms for 30-day range
- Each page must display its OWN entity data (no cross-contamination)

### Design Specifications

**Color Palette (ACT Logo Colors - EXACT VALUES):**
- 1st metric: Green (#34A853)
- 2nd metric: Yellow (#FBBC05)
- 3rd metric: Red (#EA4335)
- 4th metric: Blue (#4285F4)

**Metric Card Styling:**
- Active: Solid color background (from palette), white text
- Inactive: White background (#ffffff), black text (#212529), 1px #e0e0e0 border
- Padding: 12px 16px
- Value font: 22px
- Border radius: 6px
- Height: ~82px total
- Transition: all 0.2s ease

**Chart Styling:**
- Height: 300px (fixed, no vertical expansion)
- Container padding: 24px
- Border radius: 8px
- Background: white
- No border on container

**Axes Behavior:**
- 1-2 metrics: Axes visible with labels, NO grid lines
- 3-4 metrics: Axes completely hidden (display: false), grid lines visible (#e0e0e0 dashed)

**Tooltip:**
- White background (#ffffff)
- Border: 1px solid #e0e0e0
- Line indicators (not squares) - requires pointStyle: 'line' and usePointStyle: true
- Shows real values (even when normalized)

**Header Row:**
- Max-width: 1200px
- Centered on wide screens
- Metrics button on same row as cards
- Responsive grid for mobile

---

## REFERENCE FILES

**Similar Completed Work:**
- act_dashboard/templates/macros/performance_chart.html - Current implementation to replace
- act_dashboard/templates/dashboard_new.html - Shows how macro is called (Dashboard page)
- act_dashboard/templates/campaigns.html - Shows how macro is called (Campaigns page)
- act_dashboard/templates/keywords_new.html - Shows how macro is called (Keywords page)
- act_dashboard/templates/shopping_new.html - Shows how macro is called (Shopping page)

**Documentation to Consult:**
- /mnt/project/MASTER_KNOWLEDGE_BASE.md - System architecture, Chart.js patterns
- /mnt/project/PROJECT_ROADMAP.md - Current project state
- /mnt/project/KNOWN_PITFALLS.md - Common Chart.js issues

**Approved Wireframe:**
- MODULE_3_WIREFRAME_FINAL.html (provided separately) - Complete working demo with all functionality

**Backend Route Pattern:**
- act_dashboard/routes/campaigns.py - Shows get_performance_data() usage for campaigns
- act_dashboard/routes/keywords.py - Shows get_performance_data() usage for keywords
- act_dashboard/routes/shopping.py - Shows get_performance_data() usage for shopping
- act_dashboard/routes/base.py - Contains shared get_performance_data() function

**Database Tables:**
- ro.analytics.campaign_performance - Campaign daily metrics
- ro.analytics.keyword_performance - Keyword daily metrics
- ro.analytics.ad_group_performance - Ad group daily metrics
- ro.analytics.ad_performance - Ad daily metrics
- ro.analytics.shopping_performance - Shopping product daily metrics

---

## SUCCESS CRITERIA

### Chart Functionality (All 6 Pages)
- [ ] 1. Chart uses ACT logo colors (Green, Yellow, Red, Blue) in correct order
- [ ] 2. Metric cards show only selected metrics (1-4 cards dynamically)
- [ ] 3. Card click toggles visibility (not selection) - cards stay visible when inactive
- [ ] 4. Metrics modal changes which metrics are loaded (selectedMetrics)
- [ ] 5. Inactive cards are white background with black text (not dimmed colors)
- [ ] 6. Chart height fixed at 300px (no vertical expansion)
- [ ] 7. Cards row max-width 1200px (centered on wide screens)
- [ ] 8. Metric card height ~82px (reduced padding and font)

### Axes and Grid Behavior
- [ ] 9. When 1-2 metrics: Axes visible with labels, NO grid lines
- [ ] 10. When 3-4 metrics: Axes completely hidden (display: false), grid lines visible
- [ ] 11. Normalization: 3+ metrics scaled to 0-95% (prevents flat lines at top)
- [ ] 12. All metrics use full chart height when 3+ selected (no flat lines at bottom)

### Tooltip and Interaction
- [ ] 13. Tooltip shows line indicators (not colored squares)
- [ ] 14. Tooltip displays real values (even when normalized)
- [ ] 15. Hover shows all visible metrics for that date

### Date Intervals
- [ ] 16. Date intervals: ≤30 days = daily, ≤180 days = weekly, >180 days = monthly
- [ ] 17. Date labels update based on selected date range
- [ ] 18. Chart renders correctly for 7-day, 30-day, 90-day, 365-day ranges

### Entity-Specific Data (CRITICAL)
- [ ] 19. Dashboard page shows account-level aggregated data
- [ ] 20. Campaigns page shows campaigns-only aggregated data
- [ ] 21. Keywords page shows keywords-only aggregated data
- [ ] 22. Ad Groups page shows ad-groups-only aggregated data
- [ ] 23. Ads page shows ads-only aggregated data
- [ ] 24. Shopping page shows shopping-products-only aggregated data
- [ ] 25. NO cross-contamination (Keywords page doesn't show campaign data, etc.)

### Session and Performance
- [ ] 26. Session persistence: Selected metrics saved across page refreshes
- [ ] 27. Metrics selector modal enforces 4-metric limit
- [ ] 28. Chart renders in <500ms for 30-day range
- [ ] 29. Zero JavaScript console errors on any page
- [ ] 30. Responsive design works on mobile (cards stack, modal adapts)

**ALL 30 must pass for approval.**

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

Total estimated time: X hours
Risks / unknowns: [Any remaining concerns]

Waiting for Master Chat approval before starting implementation.
```

**ONLY AFTER Master Chat explicitly approves your build plan can you begin implementation.**

---

## TESTING INSTRUCTIONS

### Manual Testing (All 6 Pages)

**Test EVERY page in this exact order:**
1. Dashboard
2. Campaigns
3. Keywords
4. Ad Groups
5. Ads
6. Shopping

**For Each Page:**

**STEP 1: Entity Data Verification (CRITICAL)**
- Load page
- Open browser DevTools → Network tab
- Reload page
- Check performance data endpoint response
- Verify: Data matches entity type (Keywords page has keyword data, not campaign data)
- Verify: Metric totals match entity aggregation

**STEP 2: Metric Card Behavior**
- Open page → See default 2 metrics (Cost, Impressions)
- Click Metrics button → Select 4 different metrics → Click Apply
- Verify: 4 colored cards appear (Green, Yellow, Red, Blue)
- Verify: Cards show entity-specific values (not mixed entities)
- Click one card → Verify: Turns white/inactive, chart hides that metric
- Click white card again → Verify: Turns colored/active, chart shows that metric
- Refresh page → Verify: Selected metrics persist

**STEP 3: Chart Visualization (1-2 Metrics)**
- Select 1 metric only
- Verify: Left axis visible with labels
- Verify: NO grid lines
- Verify: Chart uses full 300px height
- Verify: Line shows entity-specific trend
- Select 2 metrics (1 currency, 1 count)
- Verify: Left axis (currency) and right axis (count) visible
- Verify: NO grid lines
- Verify: Both lines show entity-specific trends

**STEP 4: Chart Visualization (3-4 Metrics)**
- Select 3 metrics with vastly different scales
- Verify: ALL 3 lines use full chart height (not flat at bottom)
- Verify: NO axes visible (completely hidden)
- Verify: Grid lines visible (light grey dashed)
- Hover chart → Verify: Tooltips show REAL entity-specific values (not normalized)
- Verify: Tooltip shows line indicators (not squares)
- Verify: All values are entity-specific (not mixed)

**STEP 5: Date Range Testing**
- Change date range to 7 days → Verify: Daily intervals (7 labels)
- Verify: Entity-specific data for all 7 days
- Change to 30 days → Verify: Daily intervals (30 labels)
- Change to 90 days → Verify: Weekly intervals (~13 labels)
- Change to 365 days → Verify: Monthly intervals (~12 labels)

**STEP 6: Color Consistency**
- Select ANY 4 metrics in ANY order
- Verify: Colors ALWAYS Green, Yellow, Red, Blue (based on visible position)
- Hide 2nd metric → Verify: Remaining 3 stay same colors, no reordering

**STEP 7: Cross-Page Contamination Check**
- Open Keywords page → Note a specific metric value (e.g., Cost = $X)
- Open Campaigns page → Check same date range
- Verify: Cost value is DIFFERENT (campaigns ≠ keywords)
- Repeat for all page pairs
- **CRITICAL:** Ensure no page shows another entity's data

### Edge Cases to Test

1. **Single Metric:**
   - Select only Cost on each page
   - Verify: 1 green card, chart shows 1 line, left axis visible
   - Verify: Each page shows different Cost value (entity-specific)

2. **All Metrics Same Scale:**
   - Select 4 currency metrics (Cost, Conv Value, Cost/Conv, Avg CPC)
   - Verify: Normalization still works, no flat lines

3. **Quick Toggle:**
   - Rapidly click card on/off 5 times on each page
   - Verify: Chart updates smoothly, no errors, data stays entity-specific

4. **Modal Cancel:**
   - Change metrics in modal → Click Cancel
   - Verify: Cards don't change
   - Verify: Chart still shows original entity-specific data

5. **Page Switching:**
   - Select 4 metrics on Keywords page
   - Switch to Shopping page
   - Verify: Same 4 metrics selected (session persists)
   - Verify: VALUES are different (shopping data, not keyword data)

### Performance Benchmarks

- Page load: <3 seconds (including chart render)
- Chart render: <500ms for 30-day range
- Metric toggle: <100ms response
- Modal open: <200ms
- Date range change: <1 second
- Entity data fetch: <500ms

### Browser Console

- Zero JavaScript errors on all 6 pages
- Zero warnings related to chart code
- No duplicate event listeners
- No data leakage between pages

**IMPORTANT:** Test AT EVERY STEP. Do not proceed if entity data contamination is detected.

---

## POTENTIAL ISSUES

### Common Pitfalls to Avoid

1. **Entity Data Contamination (CRITICAL):**
   - Problem: Keywords page showing campaign data or mixed data
   - Solution: Verify each route passes correct entity_type to get_performance_data()
   - Test: Compare metric totals across pages - they MUST be different

2. **Color Binding Issue:**
   - Problem: Colors assigned to metric type instead of position
   - Solution: Always use visibleMetrics.indexOf() for color assignment

3. **Normalization Flat Lines:**
   - Problem: Using 0-100% causes flat lines at top
   - Solution: Use 0-95% ceiling (leaves headroom)

4. **Grid Toggle Bug:**
   - Problem: Grid lines persist when switching from 3+ to 1-2 metrics
   - Solution: Explicitly set grid.display = false in else branch

5. **Tooltip Real Values:**
   - Problem: Tooltip shows normalized values instead of real
   - Solution: Store originalData separately, use in tooltip callback

6. **Session Persistence:**
   - Problem: Selected metrics lost on refresh
   - Solution: Use /set-chart-metrics endpoint (already exists)

### Known Gotchas

- Chart.js pointStyle 'line' requires usePointStyle: true in tooltip config
- Normalization must happen AFTER cloning raw data (don't mutate original)
- Axes must be explicitly hidden (display: false) not just ticks
- Bootstrap 5 uses different grid classes than Bootstrap 4
- Date interval logic must account for inclusive/exclusive ranges
- get_performance_data() entity_type parameter is case-sensitive

### Entity-Specific Data Gotchas

- Dashboard aggregates ALL campaigns (not just one)
- Keywords page aggregates ALL keywords (can be 1000+)
- Shopping page uses 'shopping_product' entity type (not 'shopping')
- Ad Groups use 'ad_group' entity type (underscore, not hyphen)
- Each entity table has different column names - verify in database

### Testing Gotchas

- Opera browser (Christopher's primary): Test there first
- PowerShell terminal: Use for Flask app, verify output shows no errors
- Screenshots: Capture at 1920x1080 for documentation
- Clear browser cache between major changes to avoid stale JS
- Test with REAL synthetic data (not hardcoded sample data)

---

## HANDOFF REQUIREMENTS

**Documentation (BOTH required):**

1. **CHAT_55_SUMMARY.md** (400-700 lines)
   - Executive overview of Module 3 implementation
   - Deliverables summary with file paths
   - Testing results (all 30 success criteria with ✅/❌)
   - 10+ screenshots:
     * Before/After comparison
     * All 6 pages with charts (verify different data per page)
     * 1-2 metrics (axes visible, no grid)
     * 3-4 metrics (axes hidden, grid visible, all lines use full height)
     * Tooltip with line indicators showing real values
     * Inactive card (white background)
     * Modal with metrics selection
     * Date range comparison (daily vs weekly vs monthly)
     * Responsive layout (wide screen with 1200px limit)
     * Entity data verification (DevTools showing different data per page)
   - Time tracking breakdown
   - Issues encountered and resolutions
   - Key statistics (files modified, lines changed, functions added)

2. **CHAT_55_HANDOFF.md** (800-1,500 lines)
   - **Architecture Section:**
     * Data flow diagram (route → template → macro)
     * Two-state metric system (selectedMetrics vs visibleMetrics)
     * Normalization algorithm explanation
     * Date interval logic flow
     * Color assignment strategy
     * Per-page data isolation mechanism
   - **Code Details:**
     * performance_chart.html: Line-by-line changes with before/after
     * chart-styles.css: Complete file with annotations
     * chart-config.js: JavaScript functions with explanations
     * base.py: Date interval function implementation
     * Database queries: Entity-specific aggregation logic
   - **Testing Procedures:**
     * Manual test steps for all 6 pages
     * Entity data verification method
     * Edge case scenarios
     * Performance benchmarks
     * Browser console verification
   - **Known Limitations:**
     * Chart.js version dependency
     * Browser compatibility (tested in Opera/Chrome)
     * Maximum metrics limit (4)
     * Entity types supported
   - **Future Enhancements:**
     * Additional metrics beyond current 10
     * Export chart as image
     * Custom date ranges
     * Chart annotations
     * Comparison mode (compare two date ranges)
   - **Git Commit Strategy:**
     * Suggested commit message
     * Files to include in commit
     * Testing checklist before commit

**Git:**
- Prepare commit message: "Module 3: Google Ads chart design with ACT colors, normalization, entity-specific data, and dynamic metrics"
- List all modified/created files:
  * performance_chart.html
  * chart-styles.css
  * chart-config.js
  * base.py (if modified)
  * All 6 page templates (if modified)
- Note dependencies: Chart.js 4.4.0

**Delivery:**
- Copy CHAT_55_SUMMARY.md to /mnt/user-data/outputs/
- Copy CHAT_55_HANDOFF.md to /mnt/user-data/outputs/
- Copy chart-styles.css to /mnt/user-data/outputs/ (for reference)
- Use present_files tool for all documents
- Await Master review before git commit

---

## ESTIMATED TIME BREAKDOWN

- 5 Questions + Build Plan: 30-45 min
- Read wireframe and understand requirements: 20-30 min
- Create chart-styles.css: **SKIP (provided complete in brief)**
- Modify performance_chart.html macro: 1.5-2 hours
- Create chart-config.js with normalization logic: 45-60 min
- Add date interval logic to base.py: 30-45 min
- Test on Dashboard page (with entity verification): 30-40 min
- Test on Campaigns page (with entity verification): 20-30 min
- Test on Keywords page (with entity verification): 20-30 min
- Test on Ad Groups page (with entity verification): 20-30 min
- Test on Ads page (with entity verification): 20-30 min
- Test on Shopping page (with entity verification): 20-30 min
- Cross-page contamination testing: 30-45 min
- Edge case testing: 30-45 min
- Performance testing: 15-20 min
- Bug fixes and polish: 45-90 min
- Documentation (SUMMARY): 1-1.5 hours
- Documentation (HANDOFF): 1.5-2 hours

**Total: 5.5-7 hours**

---

**WORKFLOW REMINDER:**
1. Confirm you understand workflow (see top of brief)
2. Read all files from /mnt/project/ using view tool
3. Send 5 QUESTIONS → WAIT for answers
4. Send DETAILED BUILD PLAN → WAIT for approval
5. Implement step-by-step, ONE FILE AT A TIME, testing at each stage
6. Create handoff documentation
7. Await Master review

---

## COMPLETE CSS FILE (COPY EXACTLY AS-IS)

**Save this to: C:\Users\User\Desktop\gads-data-layer\act_dashboard\static\css\chart-styles.css**

```css
/* ============================================================================
   ACT DASHBOARD - CHART STYLES
   Module 3: Google Ads Chart Design
   
   Purpose: Styling for performance charts across all 6 pages
   Pages: Dashboard, Campaigns, Keywords, Ad Groups, Ads, Shopping
   
   Colors: ACT Logo Palette
   - Green: #34A853 (1st metric)
   - Yellow: #FBBC05 (2nd metric)
   - Red: #EA4335 (3rd metric)
   - Blue: #4285F4 (4th metric)
   ============================================================================ */

/* HEADER ROW (Metric Cards + Metrics Button) */
.chart-header-row {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 16px;
    max-width: 1200px;
    margin-left: auto;
    margin-right: auto;
}

/* METRIC BOXES CONTAINER */
.metric-boxes {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    flex: 1;
}

/* INDIVIDUAL METRIC BOX */
.metric-box {
    border-radius: 6px;
    padding: 12px 16px;
    cursor: pointer;
    transition: all 0.2s ease;
    user-select: none;
}

.metric-box .label {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
}

.metric-box .value {
    font-size: 22px;
    font-weight: 700;
    line-height: 1.2;
    margin-bottom: 6px;
}

.metric-box .change {
    font-size: 12px;
    font-weight: 500;
}

/* ACTIVE/INACTIVE STATES */
.metric-box.active {
    /* Color set via inline JavaScript */
    color: white;
}

.metric-box.inactive {
    background: white;
    color: #212529;
    border: 1px solid #e0e0e0;
}

.metric-box.active .change {
    color: rgba(255, 255, 255, 0.9);
}

.metric-box.inactive .change {
    color: #616161;
}

/* METRICS BUTTON */
.metrics-btn {
    background: white;
    border: 1px solid #d0d0d0;
    padding: 8px 16px;
    border-radius: 4px;
    font-size: 13px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 6px;
    transition: all 0.15s;
    white-space: nowrap;
    height: fit-content;
}

.metrics-btn:hover {
    background: #f5f5f5;
    border-color: #b0b0b0;
}

/* CHART CONTAINER */
.chart-container {
    background: white;
    border-radius: 8px;
    padding: 24px;
    height: 340px;
    position: relative;
}

.chart-canvas {
    height: 300px !important;
    max-height: 300px !important;
}

/* METRICS SELECTOR MODAL */
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    z-index: 9998;
    display: none;
}

.modal-overlay.show {
    display: block;
}

.metrics-modal {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: white;
    border-radius: 8px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    width: 700px;
    max-height: 600px;
    z-index: 9999;
    display: none;
}

.metrics-modal.show {
    display: block;
}

/* MODAL HEADER */
.modal-header {
    padding: 20px;
    border-bottom: 1px solid #e0e0e0;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.modal-header h3 {
    margin: 0;
    font-size: 18px;
    font-weight: 500;
}

.modal-close {
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
    color: #616161;
    line-height: 1;
    padding: 0;
    width: 24px;
    height: 24px;
}

.modal-close:hover {
    color: #212121;
}

/* MODAL BODY */
.modal-body {
    display: grid;
    grid-template-columns: 1fr 1fr;
    height: 400px;
}

.metrics-available {
    padding: 20px;
    border-right: 1px solid #e0e0e0;
    overflow-y: auto;
}

.metrics-selected {
    padding: 20px;
    overflow-y: auto;
}

.modal-section-title {
    font-size: 13px;
    margin-bottom: 12px;
    color: #616161;
    font-weight: 500;
}

/* METRIC CHECKBOXES */
.metric-checkbox {
    display: block;
    padding: 8px 0;
    font-size: 14px;
    cursor: pointer;
}

.metric-checkbox input {
    margin-right: 8px;
    cursor: pointer;
}

.metric-checkbox:hover {
    background: #f5f5f5;
}

/* SELECTED METRICS LIST */
.selected-metric {
    display: flex;
    align-items: center;
    padding: 8px;
    background: #f5f5f5;
    border-radius: 4px;
    margin-bottom: 8px;
}

.selected-metric .drag-handle {
    margin-right: 8px;
    color: #9e9e9e;
    cursor: move;
}

.selected-metric .name {
    flex: 1;
    font-size: 14px;
}

.selected-metric .remove {
    background: none;
    border: none;
    color: #9e9e9e;
    cursor: pointer;
    font-size: 18px;
    line-height: 1;
    padding: 0;
    width: 20px;
    height: 20px;
}

.selected-metric .remove:hover {
    color: #EA4335;
}

/* MODAL FOOTER */
.modal-footer {
    padding: 16px 20px;
    border-top: 1px solid #e0e0e0;
    display: flex;
    justify-content: flex-end;
    gap: 12px;
}

.btn {
    padding: 8px 20px;
    border-radius: 4px;
    border: 1px solid #d0d0d0;
    background: white;
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
}

.btn:hover {
    background: #f5f5f5;
}

.btn-primary {
    background: #1a73e8;
    color: white;
    border-color: #1a73e8;
}

.btn-primary:hover {
    background: #1557b0;
}

/* LIMIT WARNING */
.limit-warning {
    background: #fff3cd;
    border: 1px solid #ffc107;
    color: #856404;
    padding: 12px;
    border-radius: 4px;
    margin-top: 12px;
    font-size: 13px;
    display: none;
}

.limit-warning.show {
    display: block;
}

/* RESPONSIVE BREAKPOINTS */
@media (max-width: 1200px) {
    .chart-header-row {
        max-width: 100%;
        padding: 0 20px;
    }
}

@media (max-width: 768px) {
    .metric-boxes {
        grid-template-columns: repeat(2, 1fr);
    }
    
    .metrics-modal {
        width: 90%;
        max-width: 500px;
    }
    
    .modal-body {
        grid-template-columns: 1fr;
        height: auto;
        max-height: 500px;
    }
    
    .metrics-available {
        border-right: none;
        border-bottom: 1px solid #e0e0e0;
    }
}

@media (max-width: 480px) {
    .metric-boxes {
        grid-template-columns: 1fr;
    }
    
    .metric-box .value {
        font-size: 20px;
    }
}
```

---

## CRITICAL IMPLEMENTATION NOTES

### ACT Color Palette (EXACT VALUES)

```javascript
const FIXED_COLORS = [
    '#34A853',  // 1st metric: Green (from logo inner circle)
    '#FBBC05',  // 2nd metric: Yellow (from logo middle ring)
    '#EA4335',  // 3rd metric: Red (from logo outer ring)
    '#4285F4'   // 4th metric: Blue (from logo outermost ring)
];
```

### Normalization Algorithm (EXACT FORMULA)

```javascript
// For 3+ metrics only
const min = Math.min(...rawData);
const max = Math.max(...rawData);
const range = max - min;

if (range > 0) {
    normalizedData = rawData.map(v => ((v - min) / range) * 95);  // 95% ceiling
} else {
    normalizedData = rawData.map(() => 47.5);  // All same = middle
}
```

### Date Interval Logic (EXACT THRESHOLDS)

```python
def get_date_interval(total_days):
    if total_days <= 30:
        return 1      # Daily
    elif total_days <= 180:
        return 7      # Weekly
    else:
        return 30     # Monthly
```

### Two-State System (CRITICAL)

```javascript
let selectedMetrics = [];  // Which metrics are in cards (from modal)
let visibleMetrics = [];   // Which metrics shown in chart (toggled by cards)

// Modal Apply button updates BOTH
// Card click toggles ONLY visibleMetrics
```

### Entity Data Flow (CRITICAL)

```python
# Each route MUST pass correct entity_type
data = get_performance_data(
    customer_id=customer_id,
    start_date=start_date,
    end_date=end_date,
    entity_type='keyword'  # MUST match page entity
)

# Macro receives entity-specific data
# Same macro code, different data per page
```

**These are non-negotiable specifications from the approved wireframe.**

---

**END OF BRIEF**
