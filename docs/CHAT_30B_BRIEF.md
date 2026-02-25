# CHAT 30B: SEARCH TERMS LIVE EXECUTION + KEYWORD EXPANSION

**Estimated Time:** 7-9 hours  
**Dependencies:** Chat 30a (Search Terms tab complete), Google Ads API integration  
**Priority:** HIGH (Dashboard 3.0 M9 Phase 2)

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

2. CHAT_30B_BRIEF.md (this brief)
   Location: C:\Users\User\Desktop\gads-data-layer\docs\CHAT_30B_BRIEF.md

Upload both now before proceeding.
```

**After uploads received:**
1. Extract ZIP and explore project structure
2. Read CHAT_30B_BRIEF.md in full
3. Review CHAT_30A_HANDOFF.md (Phase 1 context)
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

**Categories:** [API], [DATABASE], [EXECUTION], [SCOPE], [TESTING]

**🚨 STOP HERE — Wait for Christopher to paste answers from Master Chat 🚨**

---

### **STEP 3: Build Plan Review (MANDATORY)**

After receiving answers from Master Chat, create a detailed build plan.

**Build Plan Format:**
```
DETAILED BUILD PLAN FOR MASTER CHAT REVIEW

Files to create/modify:
- C:\Users\User\Desktop\gads-data-layer\... — [what changes]

Step-by-step implementation:
STEP A: [Task description] (~X min)
  - [Specific action 1]
  - [Specific action 2]

Total estimated time: X minutes
Risks / unknowns: [Any remaining concerns]

Waiting for Master Chat approval before starting.
```

**🚨 STOP HERE — Wait for Christopher to paste approval from Master Chat 🚨**

---

### **STEP 4: Implementation Begins**

Only after BOTH Stage 2 (5 Questions answered) AND Stage 3 (Build Plan approved) are complete, proceed to coding.

---

## CONTEXT

**Phase 1 Complete (Chat 30a):**
- Search Terms tab displays 16-column data table
- Negative keyword flagging logic identifies opportunities (3 criteria)
- Row-level + bulk "Add as Negative" buttons show preview modal
- **No live execution** — modal displays "Available in future update" message

**Phase 2 Goal:**
Complete M9 by adding:
1. **Live Google Ads API execution** for negative keywords
2. **Keyword expansion opportunity flagging** (high-performing search terms)
3. **"Add as Keyword" functionality** with live execution

**Business Value:**
- Negative keyword blocking saves money immediately (prevent wasted clicks)
- Keyword expansion drives growth (capture missed opportunities)
- Audit trail in changes table ensures accountability

---

## OBJECTIVE

Add live Google Ads API execution for both negative keyword blocking and keyword expansion, replacing preview-only modals with actual campaign modifications tracked in the changes table.

---

## REQUIREMENTS

### Deliverables

**1. File:** `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\keywords.py` (MODIFY)
- Add POST route: `/keywords/add-negative` (execute negative keyword addition)
- Add POST route: `/keywords/add-keyword` (execute keyword expansion)
- Google Ads API integration for both routes
- Error handling and validation
- Changes table audit logging

**2. File:** `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\keywords_new.html` (MODIFY)
- Update "Add as Negative" modal (replace preview with execution confirmation)
- Add keyword expansion flagging logic (visual indicators)
- Add "Add as Keyword" buttons (row-level + bulk)
- Add "Add as Keyword" modal (similar to negative keyword modal)
- Update JavaScript for live API calls
- Success/error toast notifications

**3. File:** `C:\Users\User\Desktop\gads-data-layer\act_autopilot\google_ads_client.py` (MODIFY or CREATE)
- Helper functions for negative keyword operations
- Helper functions for keyword creation operations
- Campaign-level vs ad group-level logic
- Match type handling

**4. Keyword Expansion Logic**
Flag search terms as expansion opportunities meeting **ALL** of these criteria:
- **Criterion 1:** CVR ≥5% (high conversion rate)
- **Criterion 2:** ROAS ≥4.0x (profitable performance)
- **Criterion 3:** ≥10 conversions (sufficient data)
- **Criterion 4:** Search term NOT already added as keyword

Display flagged terms with green badge "Expansion Opportunity".

**5. Changes Table Integration**
Log all actions in `warehouse.duckdb` changes table:
- **executed_by:** `user_search_terms_negative` or `user_search_terms_expansion`
- **change_type:** `negative_keyword_add` or `keyword_add`
- **entity_type:** `keyword` or `search_term`
- **entity_id:** campaign_id or ad_group_id
- **old_value:** null
- **new_value:** JSON with search_term, match_type, level (campaign/ad_group)
- **reason:** Flag reason or "Manual selection"

### Technical Constraints

- **Google Ads API:** Use existing client from `google_ads_client.py`
- **Negative Keyword Level:** Campaign-level by default (ad group-level optional in modal)
- **Keyword Match Type:** Suggest based on original search term match (Exact → Exact, Phrase → Phrase, Broad → Phrase)
- **Bid Strategy:** For new keywords, use campaign default bid or suggest based on search term CPC
- **Error Handling:** Graceful failures with user-friendly messages
- **Dry-Run Mode:** Add checkbox in modal for testing without execution
- **Rate Limiting:** Batch API calls if >10 selections (prevent quota issues)

### Design Specifications

**Negative Keyword Modal (Updated):**
- Title: "Add Negative Keywords"
- Body:
  - List of search terms to be added
  - Radio buttons: Campaign-level (default) / Ad group-level
  - Dry-run checkbox: "Test mode (don't execute)"
- Footer:
  - Cancel button
  - "Add Negatives" button (blue, primary)
- After execution:
  - Success: Green toast "X negative keywords added successfully"
  - Error: Red toast with specific error message

**Keyword Expansion Flag:**
- Green badge: "✓ Expansion Opportunity"
- Tooltip: "High CVR (X%), ROAS (Xx), 10+ conversions"

**Add as Keyword Modal (New):**
- Title: "Add as Keywords"
- Body:
  - List of search terms to be added
  - Match type dropdown per term: Exact / Phrase / Broad (default: suggested)
  - Bid input per term (default: search term CPC or campaign default)
  - Dry-run checkbox
- Footer:
  - Cancel button
  - "Add Keywords" button (green, success)
- After execution:
  - Success: Green toast "X keywords added successfully"
  - Error: Red toast with specific error message

---

## REFERENCE FILES

**Phase 1 Work:**
- `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_30A_HANDOFF.md` — Phase 1 context
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\keywords.py` — Current implementation
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\keywords_new.html` — Current UI

**Google Ads API Integration:**
- `C:\Users\User\Desktop\gads-data-layer\act_autopilot\google_ads_client.py` — Existing client
- `C:\Users\User\Desktop\gads-data-layer\act_autopilot\execution\` — Execution patterns

**Changes Table:**
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\recommendations.py` — Similar POST patterns
- `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_28_HANDOFF.md` — Changes table usage

---

## SUCCESS CRITERIA

- [ ] 1. "Add as Negative" button executes live API call (campaign-level default)
- [ ] 2. Negative keywords successfully added to Google Ads campaign
- [ ] 3. Changes table logs negative keyword additions with correct fields
- [ ] 4. Success toast displays after negative keyword execution
- [ ] 5. Error toast displays with specific message on API failure
- [ ] 6. Keyword expansion opportunities flagged (green badge, 4 criteria)
- [ ] 7. "Add as Keyword" buttons visible on expansion opportunities
- [ ] 8. "Add as Keyword" modal opens with suggested match type and bid
- [ ] 9. Keywords successfully added to Google Ads ad group
- [ ] 10. Changes table logs keyword additions
- [ ] 11. Bulk selection works for both negative and expansion actions
- [ ] 12. Dry-run mode prevents actual API execution (test mode)
- [ ] 13. Ad group-level option works for negative keywords
- [ ] 14. Match type override works for keyword additions
- [ ] 15. Bid override works for keyword additions
- [ ] 16. Zero JavaScript errors in browser console

**ALL 16 must pass for approval.**

---

## TESTING INSTRUCTIONS

### Manual Testing

**Test 1: Negative Keyword - Campaign Level (Single)**
```
1. Find search term with negative flag
2. Click "Add as Negative" button
3. Modal opens → verify search term listed
4. Select "Campaign-level" (default)
5. Uncheck dry-run
6. Click "Add Negatives"
7. Verify: Success toast appears
8. Check Google Ads UI: Negative keyword added to campaign
9. Check changes table: New row with change_type=negative_keyword_add
```

**Test 2: Negative Keyword - Ad Group Level (Single)**
```
1. Click "Add as Negative" on different term
2. Modal opens → select "Ad group-level"
3. Click "Add Negatives"
4. Verify: Success toast
5. Check Google Ads UI: Negative added to ad group
6. Check changes table: entity_type=ad_group_id in new_value JSON
```

**Test 3: Negative Keyword - Bulk (5 terms)**
```
1. Check 5 search terms
2. Click "Add Selected as Negatives (5)"
3. Modal lists all 5 terms
4. Click "Add Negatives"
5. Verify: Success toast "5 negative keywords added"
6. Check Google Ads: All 5 added
7. Check changes table: 5 new rows (or 1 batch row)
```

**Test 4: Negative Keyword - Dry Run**
```
1. Click "Add as Negative"
2. Check "Test mode (don't execute)"
3. Click "Add Negatives"
4. Verify: Success toast "Dry-run successful (not executed)"
5. Check Google Ads: NO new negative keyword
6. Check changes table: NO new row
```

**Test 5: Keyword Expansion - Flag Display**
```
1. Find search term with CVR ≥5%, ROAS ≥4x, ≥10 conversions
2. Verify: Green "✓ Expansion Opportunity" badge visible
3. Hover badge → tooltip shows criteria values
4. Find search term NOT meeting criteria
5. Verify: NO expansion badge
```

**Test 6: Keyword Expansion - Add Single**
```
1. Click "Add as Keyword" on expansion opportunity
2. Modal opens → search term listed
3. Suggested match type displayed (e.g., "Phrase")
4. Suggested bid displayed (e.g., "£1.50")
5. Click "Add Keywords"
6. Verify: Success toast
7. Check Google Ads: Keyword added to ad group
8. Check changes table: change_type=keyword_add
```

**Test 7: Keyword Expansion - Override Match Type**
```
1. Click "Add as Keyword"
2. Modal → change match type from Phrase to Exact
3. Click "Add Keywords"
4. Verify: Success toast
5. Check Google Ads: Keyword added as Exact match
```

**Test 8: Keyword Expansion - Override Bid**
```
1. Click "Add as Keyword"
2. Modal → change bid from £1.50 to £2.00
3. Click "Add Keywords"
4. Verify: Success toast
5. Check Google Ads: Keyword max CPC = £2.00
```

**Test 9: Keyword Expansion - Bulk (3 terms)**
```
1. Check 3 expansion opportunities
2. Click "Add Selected as Keywords (3)"
3. Modal lists 3 terms with individual match type + bid
4. Click "Add Keywords"
5. Verify: Success toast "3 keywords added"
6. Check Google Ads: All 3 keywords present
```

**Test 10: API Error Handling**
```
1. Simulate API error (invalid campaign ID or quota exceeded)
2. Click "Add as Negative"
3. Verify: Red error toast with specific message
4. Verify: Modal doesn't close (user can retry)
5. Verify: NO entry in changes table (failed action not logged)
```

**Test 11: Changes Table Audit**
```
1. Execute 1 negative keyword action
2. Execute 1 keyword expansion action
3. Navigate to /changes page
4. My Actions tab → verify 2 new cards
5. Verify: Correct timestamps, entity IDs, new_value JSON
6. Verify: executed_by = user_search_terms_negative / user_search_terms_expansion
```

**Test 12: Search Term Already Added**
```
1. Add search term as keyword
2. Refresh Search Terms tab
3. Verify: Expansion badge REMOVED (no longer qualifies - already added)
4. Verify: "Add as Keyword" button disabled or hidden
```

### Edge Cases

**1. Duplicate Prevention:**
- Search term already exists as negative → Show warning "Already added as negative"
- Search term already exists as keyword → Remove from expansion opportunities

**2. NULL Metrics:**
- Search term with NULL CVR → No expansion flag (doesn't meet criteria)
- Search term with NULL cost → No suggested bid, use campaign default

**3. Large Bulk Selection:**
- User selects 50 terms → Batch API calls (10 per batch)
- Show progress indicator "Adding 1-10 of 50..."

**4. Permissions:**
- User lacks edit access to campaign → API returns permission error
- Show error toast: "Insufficient permissions for campaign X"

**5. Campaign Paused:**
- Campaign not ENABLED → Allow negative keywords (always allowed)
- Keyword expansion → Show warning "Campaign paused - keyword won't serve"

### Performance

- Single negative keyword: <2 seconds (API call + DB write)
- Bulk 10 negatives: <5 seconds (single batch)
- Single keyword expansion: <3 seconds (keyword creation slower than negative)
- Changes table write: <500ms

---

## POTENTIAL ISSUES

### Common Pitfalls

**1. Issue: Google Ads API Authentication**
- **Problem:** Client credentials expired or invalid
- **Solution:** Use existing `google_ads_client.py` auth pattern
- **Prevention:** Test API connection before building execution logic

**2. Issue: Campaign vs Ad Group Level for Negatives**
- **Problem:** Unclear which level to default to
- **Master Chat Decision:** Campaign-level default (broader blocking)
- **User Override:** Modal allows ad group-level selection

**3. Issue: Match Type for New Keywords**
- **Problem:** Original search term was Broad, but add as Exact?
- **Solution:** Suggest conservative match (Exact → Exact, Phrase → Phrase, Broad → Phrase)
- **Prevention:** Show suggested match type in modal, allow override

**4. Issue: Bid Strategy for New Keywords**
- **Problem:** Campaign uses Target ROAS, individual keyword bids ignored
- **Solution:** Check campaign bidding strategy, show warning if tROAS/tCPA
- **Prevention:** Query campaign settings before showing bid input

**5. Issue: Changes Table Schema Mismatch**
- **Problem:** new_value JSON structure differs from recommendations changes
- **Solution:** Follow Chat 28 pattern: {entity_id, campaign_id, old_value, new_value, reason}
- **Prevention:** Review CHAT_28_HANDOFF.md before writing to changes

**6. Issue: Duplicate Negative Keywords**
- **Problem:** User tries to add search term already added as negative
- **Solution:** API will return error "Criterion already exists"
- **Handling:** Catch error, show toast "X already added as negative", succeed for others

**7. Issue: Keyword Already Exists**
- **Problem:** Search term matches existing keyword exactly
- **Solution:** API returns error "Keyword already exists"
- **Handling:** Remove from expansion opportunities if detected, show warning in modal

**8. Issue: Rate Limiting on Bulk Actions**
- **Problem:** Adding 50 keywords at once exceeds API quota
- **Solution:** Batch into groups of 10, sequential execution with progress
- **Prevention:** Warn user if >20 selections "This may take 30-60 seconds"

**9. Issue: Conversion Tracking Not Set Up**
- **Problem:** Client has no conversion actions configured
- **Solution:** Expansion logic requires conversions ≥10, won't flag anything
- **Handling:** Acceptable - expansion opportunities only for conversion-enabled accounts

**10. Issue: Currency Mismatch in Bid Suggestion**
- **Problem:** Template uses £ but client is USD
- **Solution:** Use `cost` column currency (already in client currency from Phase 1)
- **Prevention:** No hardcoded currency symbol in bid input, use campaign currency

### Known Gotchas

**Google Ads API Specifics:**
- Negative keywords use `CampaignCriterionOperation` (campaign) or `AdGroupCriterionOperation` (ad group)
- Match type for negatives: EXACT, PHRASE, BROAD (same as regular keywords)
- Keyword creation requires `ad_group_criterion` with `keyword` and `cpc_bid_micros`
- API returns partial failure: Some operations succeed, others fail (handle individually)

**Changes Table:**
- `executed_by` values must be consistent: `user_search_terms_negative` / `user_search_terms_expansion`
- `change_type` for audit: `negative_keyword_add` / `keyword_add`
- `entity_type` = `keyword` for both (even though negative keywords are criteria)
- `new_value` JSON must include: search_term, match_type, level, campaign_name

**Keyword Expansion Thresholds:**
- CVR ≥5%: Industry average is 2-3%, so 5% is significantly above average
- ROAS ≥4.0x: Indicates profitable performance (4x return on spend)
- ≥10 conversions: Ensures statistical significance
- NOT already added: Check against existing keywords in ad group

**Dry-Run Mode:**
- When checked, execute all logic EXCEPT final API call
- Validate inputs, check duplicates, build API request
- Return success message but don't commit
- Useful for testing without affecting campaigns

---

## HANDOFF REQUIREMENTS

**Documentation:**

**File:** `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_30B_HANDOFF.md`

**Required Sections:**
1. Executive Summary
2. Deliverables (files + line counts)
3. Success Criteria Results (16/16 with evidence)
4. Implementation Details (Google Ads API integration, execution flow)
5. Issues Encountered
6. Testing Results (12 manual tests + 5 edge cases)
7. Google Ads API Calls (request/response examples, rate limits)
8. Technical Debt
9. Git Commit Message
10. Future Enhancements
11. Notes for Master

**Git Commit Message Template:**
```
feat: Add live execution for Search Terms (M9 Phase 2)

Keywords - Live Google Ads API integration for negative keywords and keyword expansion

Features:
- Live "Add as Negative" execution (campaign + ad group level)
- Keyword expansion opportunity flagging (4 criteria: CVR/ROAS/conversions/not added)
- Live "Add as Keyword" execution with match type and bid control
- Dry-run mode for testing without execution
- Changes table audit logging
- Success/error toast notifications

Files Modified:
- routes/keywords.py (XXX lines) - POST routes, API integration
- templates/keywords_new.html (XXX lines) - execution modals, expansion flags
- google_ads_client.py (XXX lines) - helper functions

Google Ads API:
- CampaignCriterionOperation for negative keywords
- AdGroupCriterionOperation for keyword creation
- Batch operations for bulk actions (10 per batch)

Testing:
- All 16 success criteria passing
- 12 manual tests + 5 edge cases verified
- Negative keywords: campaign + ad group level
- Keyword expansion: match type + bid override

Time: [X hours] (7-9 estimated)
Chat: 30b
Status: M9 complete (Phase 1 + Phase 2)
```

---

## ESTIMATED TIME BREAKDOWN

- **Setup:** 10 min
- **Step 2: 5 Questions:** 15 min
- **Step 3: Build Plan:** 20 min
- **Google Ads API research:** 30 min (review existing patterns, test credentials)
- **Negative keyword POST route:** 60 min (API call, error handling, dry-run)
- **Keyword expansion logic:** 45 min (flagging criteria, badge display)
- **Keyword creation POST route:** 75 min (API call, match type + bid handling)
- **Modal updates:** 60 min (execution flow, success/error states)
- **Changes table integration:** 30 min (audit logging for both actions)
- **JavaScript updates:** 45 min (API calls, toast notifications)
- **Testing:** 90 min (16 criteria, 12 manual tests, 5 edge cases)
- **Documentation:** 45 min (handoff doc)

**Subtotal:** 525 minutes (~8.75 hours)

**Total with buffer: 7-9 hours**

**Escalation Trigger:** If exceeds 6 hours with <50% completion (8/16 criteria passing), escalate to Master Chat.

---

## ADDITIONAL NOTES

**Keyword Expansion Criteria Rationale:**
- **CVR ≥5%:** Double the typical e-commerce CVR (2-3%), indicates high intent
- **ROAS ≥4.0x:** Profitable threshold for most businesses (4x return on ad spend)
- **≥10 conversions:** Minimum for statistical significance (not just luck)
- **NOT already added:** Prevents duplicate keyword creation

**Negative Keyword Level Decision:**
- **Campaign-level (default):** Blocks search term across all ad groups (broader)
- **Ad group-level (optional):** Allows term in other ad groups (more granular)
- Most use cases: Campaign-level is safer (prevent waste everywhere)

**Match Type Suggestions:**
- **Exact search term → Exact keyword:** Most relevant, highest intent
- **Phrase search term → Phrase keyword:** Maintain relevance
- **Broad search term → Phrase keyword:** Tighten relevance (Broad too loose)

**Bid Suggestions:**
- **First choice:** Search term CPC (what it cost historically)
- **Fallback:** Campaign default max CPC
- **Minimum:** £0.10 (prevent invalid bids)
- **Maximum:** £50 (prevent accidental overspend)

**Future Enhancements (Post M9):**
- Automated rules for negative keywords (auto-add if criteria met)
- Search term clustering (group similar terms for bulk actions)
- Historical performance tracking (week-over-week trends)
- Intent classification (informational/navigational/transactional)

---

**Ready to start? Confirm you have read all 8 project files, then request the 2 uploads (codebase ZIP + this brief).**
