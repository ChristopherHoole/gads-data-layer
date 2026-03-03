# WORKER BRIEF STRUCTURE - DEFINITIVE TEMPLATE

**Purpose:** This document defines the EXACT structure Master Chat must use when creating worker chat briefs  
**Problem:** Master Chat keeps violating workflow rules by asking workers to upload files, writing questions/plans for workers  
**Solution:** Follow this template EXACTLY with NO deviations  

**Last Updated:** 2026-02-28  
**Template Version:** 2.0 (based on WORKFLOW_TEMPLATES.md v1.2)

---

## 🚨 CRITICAL RULES (NEVER VIOLATE THESE)

### **RULE 1: FILE UPLOADS**
❌ **NEVER ask worker to upload:**
- Codebase ZIP (too large, workers have read access)
- PROJECT_ROADMAP.md (available in /mnt/project/)
- CHAT_WORKING_RULES.md (available in /mnt/project/)
- MASTER_KNOWLEDGE_BASE.md (available in /mnt/project/)
- Any other documentation files

✅ **Workers read files using `view` tool from /mnt/project/**

✅ **Workers request individual files ONLY when ready to edit them:**
- Example: "I'm ready to edit keywords_new.html now. Please upload current version from C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\keywords_new.html"

### **RULE 2: QUESTIONS AND BUILD PLANS**
❌ **NEVER write the 5 questions in the brief** - Worker creates them
❌ **NEVER write the build plan in the brief** - Worker creates it
❌ **NEVER write detailed implementation steps in the brief** - Worker creates them

✅ **Brief INSTRUCTS worker to create 5 questions**
✅ **Brief INSTRUCTS worker to create build plan**
✅ **Brief provides requirements, worker figures out how**

### **RULE 3: CHRISTOPHER ONLY UPLOADS THE BRIEF**
❌ **NEVER say:** "Christopher will upload 3 files..."
❌ **NEVER say:** "Request codebase ZIP before starting..."

✅ **ALWAYS say:** "Christopher will ONLY upload this brief (CHAT_XX_BRIEF.md)"

---

## 📋 MANDATORY BRIEF STRUCTURE

### **SECTION 1: HEADER (REQUIRED)**

```markdown
# CHAT [NUMBER]: [TASK NAME]

**Estimated Time:** [X hours]  
**Dependencies:** [List prerequisites]  
**Priority:** [HIGH/MEDIUM/LOW]
```

**Example:**
```markdown
# CHAT 50: TESTING & POLISH - RECOMMENDATIONS UI

**Estimated Time:** 6-8 hours  
**Dependencies:** Chat 49 complete, Dashboard redesign complete  
**Priority:** HIGH
```

---

### **SECTION 2: CRITICAL WORKFLOW RULES (REQUIRED)**

**This section is MANDATORY and MUST use this EXACT template:**

```markdown
---

## 🚨 CRITICAL WORKFLOW RULES

**Christopher will ONLY upload this brief (CHAT_[N]_BRIEF.md). Everything else is in `/mnt/project/`.**

**YOUR FIRST STEP:**
```
✅ WORKFLOW UNDERSTOOD

I confirm:
1. Christopher will ONLY upload the brief (CHAT_[N]_BRIEF.md)
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
```

**⚠️ DO NOT MODIFY THIS SECTION - Copy it exactly as shown above**

---

### **SECTION 3: CONTEXT (REQUIRED)**

**What to include:**
- 2-3 paragraphs explaining:
  - What's been done already (previous chats)
  - Why this task is needed
  - How it fits into the bigger picture

**Example:**
```markdown
## CONTEXT

### What's Been Done

Chat 48 added entity filtering to the global /recommendations page. Users can now filter by Campaign, Keyword, Shopping, or Ad Group. All 1,492 recommendations are accessible with color-coded badges and entity-specific content.

Chat 49 extended this to entity-specific pages, adding Recommendations tabs to Keywords, Shopping, Ad Groups, and Ads pages. Each page shows only its relevant recommendations with appropriate empty states.

### Why This Task Is Needed

The dashboard design is about to undergo a major redesign. Testing and polishing the current recommendations UI now would be wasted effort, as all tests would need to be redone after the redesign. However, we need to ensure the recommendations system works perfectly with the NEW design once it's complete.

### How It Fits

This is the final validation step for the multi-entity recommendations system (Chats 47-49). After the dashboard redesign, this chat will verify all 4 entity pages work seamlessly together with the new visual design, consistent behavior, and zero bugs.
```

---

### **SECTION 4: OBJECTIVE (REQUIRED)**

**Single clear sentence describing the goal**

**Example:**
```markdown
## OBJECTIVE

Conduct comprehensive cross-page testing of the recommendations UI after dashboard redesign to ensure all 4 entity pages work seamlessly with consistent behavior and zero bugs.
```

---

### **SECTION 5: REQUIREMENTS (REQUIRED)**

**Must include:**

#### **Deliverables** (numbered list with full paths)
```markdown
### Deliverables

1. File 1: C:\Users\User\Desktop\gads-data-layer\[path]\file1.ext (create/modify)
   - Purpose: [What it does]
   - Key features: [List 3-5 main features]

2. File 2: C:\Users\User\Desktop\gads-data-layer\[path]\file2.ext (create/modify)
   - Purpose: [What it does]
   - Key features: [List 3-5 main features]

3. CHAT_[N]_SUMMARY.md: C:\Users\User\Desktop\gads-data-layer\docs\CHAT_[N]_SUMMARY.md (create)
   - Purpose: Executive summary for quick reference
   - Key sections: Overview, deliverables, testing, statistics, screenshots

4. CHAT_[N]_HANDOFF.md: C:\Users\User\Desktop\gads-data-layer\docs\CHAT_[N]_HANDOFF.md (create)
   - Purpose: Technical documentation for future work
   - Key sections: Architecture, code details, testing procedures, git strategy
```

#### **Technical Constraints** (bulleted list)
```markdown
### Technical Constraints

- Constraint 1
- Constraint 2
- Constraint 3
```

#### **Design Specifications** (if applicable)
```markdown
### Design Specifications

- Bootstrap 5 components
- Color palette: [Specify]
- Layout: [Describe structure]
```

---

### **SECTION 6: REFERENCE FILES (REQUIRED)**

**What to include:**

```markdown
## REFERENCE FILES

**Similar Completed Work:**
- Read from /mnt/project/ or project codebase
- path/to/similar1.ext - Shows [pattern X]
- path/to/similar2.ext - Shows [pattern Y]

**Documentation to Consult:**
- /mnt/project/DOCUMENT1.md - Section on [topic]
- /mnt/project/DOCUMENT2.md - Examples of [pattern]

**Database Tables:**
- ro.analytics.table_name - Contains [data]
```

**⚠️ ALWAYS reference /mnt/project/ for documentation, NEVER ask worker to upload**

---

### **SECTION 7: SUCCESS CRITERIA (REQUIRED)**

**Checklist format, ALL must pass:**

```markdown
## SUCCESS CRITERIA

- [ ] 1. [Specific, testable criterion]
- [ ] 2. [Specific, testable criterion]
- [ ] 3. [Specific, testable criterion]
- [ ] 4. [Specific, testable criterion]
- [ ] 5. [Specific, testable criterion]
- [ ] 6. [Specific, testable criterion]
- [ ] 7. [Specific, testable criterion]
- [ ] 8. [Specific, testable criterion]

**ALL must pass for approval.**
```

**Minimum:** 5 criteria  
**Maximum:** 30 criteria  
**Typical:** 10-20 criteria

---

### **SECTION 8: 5 QUESTIONS STAGE (REQUIRED)**

**This section INSTRUCTS worker to create questions - DO NOT write the questions yourself**

```markdown
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
```

**❌ WRONG - Writing the questions:**
```markdown
Q1. [DATABASE] Should I use ro.analytics.campaign_daily or campaign_features_daily?
Q2. [SCOPE] Are all 4 pages in scope or just keywords?
```

**✅ CORRECT - Instructing worker to create questions:**
```markdown
**After reading all project files, you MUST write EXACTLY 5 questions and send them to Master Chat.**
```

---

### **SECTION 9: BUILD PLAN STAGE (REQUIRED)**

**This section INSTRUCTS worker to create build plan - DO NOT write the plan yourself**

```markdown
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
```

**❌ WRONG - Writing the build plan:**
```markdown
STEP 1: Request keywords_new.html (~30 min)
  - Copy from /mnt/project/
  - Add tab structure
  - TEST: Tab renders
```

**✅ CORRECT - Instructing worker to create build plan:**
```markdown
**After receiving answers to 5 questions, you MUST create a detailed build plan and send it to Master Chat for approval.**
```

---

### **SECTION 10: TESTING INSTRUCTIONS (REQUIRED)**

**Manual testing procedures:**

```markdown
## TESTING INSTRUCTIONS

### Manual Testing
1. Test scenario 1
2. Test scenario 2
3. Test scenario 3

### Edge Cases to Test
1. Empty data
2. NULL values
3. Large datasets (100+ items)
4. Error conditions

### Performance
- Initial page load: <2 seconds
- Table render: <500ms
- No JavaScript errors in console

**IMPORTANT:** Test AT EVERY STEP if the step produces testable output.
```

---

### **SECTION 11: POTENTIAL ISSUES (OPTIONAL)**

**Common pitfalls and known gotchas:**

```markdown
## POTENTIAL ISSUES

### Common Pitfalls to Avoid
1. Issue 1: [Description + how to avoid]
2. Issue 2: [Description + how to avoid]
3. Issue 3: [Description + how to avoid]

### Known Gotchas
- Gotcha 1: [What + why]
- Gotcha 2: [What + why]
```

---

### **SECTION 12: HANDOFF REQUIREMENTS (REQUIRED)**

**Documentation and delivery:**

```markdown
## HANDOFF REQUIREMENTS

**Documentation (BOTH required):**

1. **CHAT_[NUMBER]_SUMMARY.md** (400-700 lines)
   - Executive overview (what was built, why it matters, key achievements)
   - Deliverables summary (files modified, code added)
   - Testing results summary (success rate, key metrics)
   - 8+ screenshots showing functionality
   - Time tracking (estimated vs actual)
   - Issues encountered summary (what went wrong, how fixed)
   - Key statistics (numbers, metrics, performance)

2. **CHAT_[NUMBER]_HANDOFF.md** (800-1,500 lines)
   - Technical architecture (component structure, data flow)
   - Files modified with line numbers (BEFORE → AFTER)
   - Code sections with detailed explanations
   - Testing procedures (detailed step-by-step)
   - Known limitations (what doesn't work, why)
   - Future enhancements (what could be improved)
   - For next chat notes (what Chat N+1 needs to know)
   - Git commit strategy (commit messages ready)

**Git:**
- Prepare commit message(s) using project template
- List all files to commit
- Include commit descriptions

**Delivery:**
- Copy BOTH documents to /mnt/user-data/outputs/
- Copy any other deliverable files to /mnt/user-data/outputs/
- Use present_files tool to share with Master Chat
- Await Master review before git commits
```

**Note:** Both documents are MANDATORY. SUMMARY is for quick reference, HANDOFF is for technical details and future work.

---

### **SECTION 13: ESTIMATED TIME BREAKDOWN (REQUIRED)**

**Time estimates for each phase:**

```markdown
## ESTIMATED TIME BREAKDOWN

- 5 Questions + Build Plan: [X min]
- Implementation: [Y min]
- Testing (at each step): [Z min]
- Documentation (SUMMARY + HANDOFF): [W min]
**Total: [X+Y+Z+W min]**

**Note:** Documentation time should account for creating BOTH CHAT_[N]_SUMMARY.md (400-700 lines) AND CHAT_[N]_HANDOFF.md (800-1,500 lines). Typically 1.5-2 hours total for both documents.
```

---

### **SECTION 14: WORKFLOW REMINDER (REQUIRED - EXACT COPY)**

**This MUST be at the end of every brief:**

```markdown
---

**WORKFLOW REMINDER:**
1. Confirm you understand workflow (see top of brief)
2. Read all files from /mnt/project/ using view tool
3. Send 5 QUESTIONS → WAIT for answers
4. Send DETAILED BUILD PLAN → WAIT for approval
5. Implement step-by-step, ONE FILE AT A TIME, testing at each stage
6. Create handoff documentation
7. Await Master review
```

---

## ❌ COMMON MISTAKES TO AVOID

### **Mistake 1: Asking for file uploads**

❌ **WRONG:**
```markdown
Worker must request 3 files from Christopher:
1. Complete Codebase ZIP
2. PROJECT_ROADMAP.md
3. CHAT_WORKING_RULES.md
```

✅ **CORRECT:**
```markdown
Christopher will ONLY upload this brief (CHAT_XX_BRIEF.md).
Worker uses view tool to read project files from /mnt/project/
```

---

### **Mistake 2: Writing questions for worker**

❌ **WRONG:**
```markdown
5 QUESTIONS FOR MASTER CHAT

Q1. [DATABASE] Should I use campaign_daily or campaign_features_daily?
Q2. [SCOPE] Are all 4 pages in scope?
Q3. [DESIGN] What color should the badges be?
Q4. [ROUTE] Which route should I use for Accept?
Q5. [ARCHITECTURE] Client-side or server-side filtering?

[Worker sends these to Master Chat]
```

✅ **CORRECT:**
```markdown
**After reading all project files, you MUST write EXACTLY 5 questions and send them to Master Chat.**

[Worker creates their own questions based on the brief]
```

---

### **Mistake 3: Writing build plan for worker**

❌ **WRONG:**
```markdown
DETAILED BUILD PLAN

STEP 1: Request keywords_new.html (~30 min)
  - Locate existing tabs
  - Add 4th Recommendations tab
  - TEST: Tab renders correctly

STEP 2: Add CSS styling (~20 min)
  - Copy from recommendations.html
  - TEST: Styles apply

[100 more lines of detailed steps...]
```

✅ **CORRECT:**
```markdown
**After receiving answers to 5 questions, you MUST create a detailed build plan and send it to Master Chat for approval.**

[Worker creates their own build plan based on brief requirements]
```

---

### **Mistake 4: File request instructions**

❌ **WRONG:**
```markdown
Request current version of:
- keywords_new.html
- shopping_new.html  
- ad_groups.html
- ads_new.html

Christopher will upload all 4 files.
```

✅ **CORRECT:**
```markdown
Request files ONE AT A TIME only when ready to edit them.

Example: "I'm ready to edit keywords_new.html now. Please upload current version from C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\keywords_new.html"
```

---

### **Mistake 5: Including actual implementation details**

❌ **WRONG:**
```markdown
Add this code to keywords_new.html line 45:
```html
<li class="nav-item">
  <a class="nav-link" data-bs-toggle="tab" href="#recommendations-tab">
    Recommendations (<span id="kw-total-count">0</span>)
  </a>
</li>
```
```

✅ **CORRECT:**
```markdown
**Deliverables:**
1. keywords_new.html - Add Recommendations tab (4th tab position)
   - Purpose: Display keyword recommendations
   - Key features: Tab structure, count display, Bootstrap 5 styling

[Worker figures out HOW to implement based on requirements]
```

---

## ✅ COMPLETE EXAMPLE BRIEF (CORRECT)

```markdown
# CHAT 50: TESTING & POLISH - RECOMMENDATIONS UI

**Estimated Time:** 6-8 hours  
**Dependencies:** Chat 49 complete, Dashboard redesign complete  
**Priority:** HIGH

---

## 🚨 CRITICAL WORKFLOW RULES

**Christopher will ONLY upload this brief (CHAT_50_BRIEF.md). Everything else is in `/mnt/project/`.**

**YOUR FIRST STEP:**
```
✅ WORKFLOW UNDERSTOOD

I confirm:
1. Christopher will ONLY upload the brief (CHAT_50_BRIEF.md)
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

Chat 49 completed the entity-specific recommendations pages (Keywords, Shopping, Ad Groups, Ads). All 4 pages have Recommendations tabs showing filtered recommendations. However, the dashboard is about to undergo a major redesign.

Testing now would be premature - all tests would need redoing after the redesign. This chat will validate the recommendations UI AFTER the dashboard redesign is complete, ensuring seamless integration with the new design.

This is the final validation step for the multi-entity recommendations system.

---

## OBJECTIVE

Conduct comprehensive cross-page testing of recommendations UI after dashboard redesign to ensure all 4 entity pages work seamlessly with consistent behavior and zero bugs.

---

## REQUIREMENTS

### Deliverables

1. Testing Report: C:\Users\User\Desktop\gads-data-layer\docs\CHAT_50_TESTING_REPORT.md
   - Purpose: Document all testing results
   - Key features: Test results for all 4 pages, performance metrics, bug reports, screenshots

2. Bug Fixes: [Files to be determined based on testing]
   - Purpose: Fix any issues discovered during testing
   - Key features: Clean code, zero console errors, performance optimizations

3. CHAT_50_SUMMARY.md: C:\Users\User\Desktop\gads-data-layer\docs\CHAT_50_SUMMARY.md
   - Purpose: Executive summary for quick reference
   - Key sections: Overview, deliverables, testing summary, statistics, 8+ screenshots

4. CHAT_50_HANDOFF.md: C:\Users\User\Desktop\gads-data-layer\docs\CHAT_50_HANDOFF.md
   - Purpose: Technical documentation for future work
   - Key sections: Architecture, testing procedures, known limitations, git strategy

### Technical Constraints

- All tests must pass on new dashboard design
- Performance targets: <5s page loads, <500ms filter response
- Zero console errors across all 4 pages
- Visual consistency with new dashboard design

### Design Specifications

- Match new dashboard color palette
- Match new dashboard spacing/typography
- Consistent with new dashboard component styling

---

## REFERENCE FILES

**Similar Completed Work:**
- /mnt/project/CHAT_49_HANDOFF.md - Testing procedures from Chat 49
- act_dashboard/templates/recommendations.html - Global page pattern

**Documentation to Consult:**
- /mnt/project/MASTER_KNOWLEDGE_BASE.md - System architecture
- /mnt/project/PROJECT_ROADMAP.md - Current project state

**Database Tables:**
- ro.analytics.recommendations - All recommendations data

---

## SUCCESS CRITERIA

- [ ] 1. Keywords page: All 1,256 recommendations display correctly
- [ ] 2. Keywords page: Load More pattern works (20 cards per load)
- [ ] 3. Keywords page: Accept/Decline operations functional
- [ ] 4. Shopping page: All 126 recommendations display correctly
- [ ] 5. Shopping page: Accept/Decline operations functional
- [ ] 6. Ad Groups page: Empty state displays correctly
- [ ] 7. Ad Groups page: Run Engine button works
- [ ] 8. Ads page: Warning empty state displays correctly
- [ ] 9. Cross-page: No entity type contamination
- [ ] 10. Cross-page: Visual consistency with new dashboard
- [ ] 11. Performance: All pages load in <5 seconds
- [ ] 12. Performance: Filter responses <500ms
- [ ] 13. Console: Zero JavaScript errors on all pages
- [ ] 14. Mobile: Responsive design works on all pages
- [ ] 15. Documentation: Complete testing report delivered

**ALL 15 must pass for approval.**

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

### Manual Testing
1. Test Keywords page: Tab structure, recommendations display, Load More, Accept/Decline
2. Test Shopping page: Tab structure, recommendations display, Accept/Decline
3. Test Ad Groups page: Empty state, Run button
4. Test Ads page: Warning empty state
5. Test cross-page behavior: Switch between all 4 pages, verify no contamination

### Edge Cases to Test
1. Empty states (Ad Groups, Ads)
2. Large datasets (Keywords: 1,256 recommendations)
3. Accept/Decline with network errors
4. Browser console errors

### Performance
- Page load: <5 seconds (all pages)
- Filter response: <500ms
- Load More: Instant (<100ms)
- No JavaScript errors in console

**IMPORTANT:** Test AT EVERY STEP.

---

## POTENTIAL ISSUES

### Common Pitfalls to Avoid
1. New dashboard CSS conflicts: Check for styling conflicts with new design
2. JavaScript errors from redesign: Verify all event handlers still work
3. Performance regression: Ensure redesign didn't slow down page loads

### Known Gotchas
- Entity filter: Must use exact entity_type match ('keyword', 'shopping_product', 'ad_group', 'ad')
- Action labels: Use action_label filter, not hardcoded text

---

## HANDOFF REQUIREMENTS

**Documentation (BOTH required):**

1. **CHAT_50_SUMMARY.md** (400-700 lines)
   - Executive overview
   - Deliverables summary
   - Testing results summary
   - 8+ screenshots
   - Time tracking
   - Issues encountered summary
   - Key statistics

2. **CHAT_50_HANDOFF.md** (800-1,500 lines)
   - Technical architecture
   - Files modified with line numbers
   - Code sections with explanations
   - Testing procedures (detailed)
   - Known limitations
   - Future enhancements
   - Git commit strategy

**Git:**
- Prepare commit message for any bug fixes
- List all files modified

**Delivery:**
- Copy BOTH documents to /mnt/user-data/outputs/
- Copy testing report to /mnt/user-data/outputs/
- Use present_files tool
- Await Master review

---

## ESTIMATED TIME BREAKDOWN

- 5 Questions + Build Plan: 30 min
- Testing Phase 1 (Keywords): 2 hours
- Testing Phase 2 (Shopping): 1 hour
- Testing Phase 3 (Ad Groups): 1 hour
- Testing Phase 4 (Ads): 1 hour
- Bug Fixes: 1-2 hours
- Documentation (SUMMARY + HANDOFF): 1.5-2 hours
**Total: 7.5-9.5 hours**

---

**WORKFLOW REMINDER:**
1. Confirm you understand workflow (see top of brief)
2. Read all files from /mnt/project/ using view tool
3. Send 5 QUESTIONS → WAIT for answers
4. Send DETAILED BUILD PLAN → WAIT for approval
5. Implement step-by-step, ONE FILE AT A TIME, testing at each stage
6. Create handoff documentation
7. Await Master review
```

---

## 📊 CHECKLIST FOR MASTER CHAT

**Before finalizing any worker brief, verify:**

- [ ] ✅ Section 2 (Critical Workflow Rules) copied EXACTLY as shown
- [ ] ✅ NO requests for codebase ZIP upload
- [ ] ✅ NO requests for documentation file uploads
- [ ] ✅ References to /mnt/project/ for reading files
- [ ] ✅ Section 8 (5 Questions) INSTRUCTS worker, doesn't write questions
- [ ] ✅ Section 9 (Build Plan) INSTRUCTS worker, doesn't write plan
- [ ] ✅ File request pattern: "ONE AT A TIME, only when editing"
- [ ] ✅ Section 14 (Workflow Reminder) copied EXACTLY
- [ ] ✅ All Windows paths are FULL paths (C:\Users\User\Desktop\...)
- [ ] ✅ Success criteria are specific and testable
- [ ] ✅ Testing instructions are clear
- [ ] ✅ Time estimates are provided

**If ANY checkbox fails → FIX THE BRIEF before sending to worker**

---

**Document Version:** 2.0  
**Last Updated:** 2026-02-28  
**Based On:** WORKFLOW_TEMPLATES.md v1.2  
**Purpose:** Prevent recurring workflow violations in worker briefs
