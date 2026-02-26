# WORKFLOW EXECUTION - Worker Lifecycle & Handoff

**Version:** 2.0 (Split from WORKFLOW_GUIDE v1.2)
**Created:** 2026-02-26  
**Purpose:** Worker chat lifecycle, handoff procedures, review checklist  
**Audience:** Worker Chats (primary), Master Chat (reference)

---

## 📋 WORKFLOW DOCUMENTATION SUITE

This is **Part 2 of 3** in the workflow documentation:

1. **WORKFLOW_CORE.md** - Overview, 15-step process, Master responsibilities
2. **WORKFLOW_EXECUTION.md** (this file) - Worker lifecycle, handoff process, review checklist
3. **WORKFLOW_TROUBLESHOOTING.md** - Escalation triggers, debugging, problem resolution

**Related documents:**
- **CHAT_WORKING_RULES.md** - Mandatory rules for all chats (v2.0)
- **WORKFLOW_TEMPLATES.md** - Brief and handoff templates

---

## 📋 TABLE OF CONTENTS

1. [Worker Chat Lifecycle](#worker-chat-lifecycle)
2. [Handoff Process](#handoff-process)
3. [Review Checklist](#review-checklist)

---

## 🔧 WORKER CHAT LIFECYCLE

### **8 Phases of a Worker Chat**

Every worker chat goes through these phases in order:

---

### **PHASE 1: INITIALIZATION (5-10 min)**

**Objective:** Get context and understand the task

**Worker Actions:**
1. Read the brief from Master (thoroughly!)
2. Ask clarifying questions if needed
3. Confirm understanding
4. Check reference files mentioned
5. Review success criteria
6. Acknowledge time estimate

**Example:**
```
Worker: "I've read the brief for Chat 21f (Ads View redesign).

Understanding:
- Redesign existing ads.py + ads.html with Bootstrap 5
- 7 metrics cards, 13-column table
- Ad strength progress bars
- Rules integration (11 ad rules expected)
- Model after campaigns.py and keywords.py

Questions:
1. Should I create ads_new.html or overwrite ads.html?
2. Do asset performance rows expand on click or hover?

Ready to proceed once clarified."
```

**Master Response:**
```
Answers:
1. Create ads_new.html (keep old as backup)
2. Click to expand (same as keywords.py QS expansion)

Proceed! Start with codebase upload per CHAT_WORKING_RULES.md
```

---

### **PHASE 2: SETUP (5-10 min)**

**Objective:** Get all 3 mandatory uploads before doing anything else.

**Worker Actions:**
1. **MANDATORY:** Request all 3 uploads (CHAT_WORKING_RULES.md Rule 1)
2. Extract ZIP and explore project structure
3. Read PROJECT_ROADMAP.md — understand current status and completed work
4. Read CHAT_WORKING_RULES.md — confirm all rules understood
5. Locate reference files mentioned in brief
6. Note current file versions

**Example:**
```
Worker: "Before starting, I need 3 mandatory uploads:

1. Codebase ZIP
   Location: C:\Users\User\Desktop\gads-data-layer
   (Create ZIP of entire folder and upload here)

2. PROJECT_ROADMAP.md
   Location: C:\Users\User\Desktop\gads-data-layer\docs\PROJECT_ROADMAP.md

3. CHAT_WORKING_RULES.md
   Location: C:\Users\User\Desktop\gads-data-layer\docs\CHAT_WORKING_RULES.md

Upload all 3 now before I proceed."
```

**Critical:** All 3 uploads are required. Never proceed with only 1 or 2. This is Rule 1.

---

### **PHASE 2B: CLARIFICATION + BUILD PLAN REVIEW (15-20 min)**

**Objective:** Two mandatory stages before any code is written. Stage 1: Worker asks 5 questions → Master answers. Stage 2: Worker writes detailed build plan → Master approves. Both stages must complete before implementation begins.

**This phase is MANDATORY. Never skip either stage.**

**Worker Actions:**
1. Review the brief, codebase ZIP, PROJECT_ROADMAP.md, and CHAT_WORKING_RULES.md
2. Identify the 5 most important unknowns or ambiguities
3. Write exactly 5 questions — no more, no less
4. Send questions to user with header: `"5 QUESTIONS FOR MASTER CHAT"`
5. **STOP. Wait for answers.**
6. Receive answers → write detailed build plan
7. Send build plan to user with header: `"DETAILED BUILD PLAN FOR MASTER CHAT REVIEW"`
8. **STOP. Wait for Master approval.**
9. Receive approval → begin implementation (Phase 4)

**Question Quality Rules:**
- ✅ Ask about things NOT clear from the brief or codebase
- ✅ Ask about real ambiguities that would affect implementation
- ✅ Ask about DB schema, edge cases, design decisions
- ❌ Do NOT ask things answerable by reading the brief
- ❌ Do NOT ask generic questions
- ❌ Do NOT proceed without answers

**Worker Example:**
```
5 QUESTIONS FOR MASTER CHAT

Before building, I reviewed the brief, codebase, and reference files. Here are my 5 questions:

Q1. [DATABASE] The brief references an ads table — I can see `ro.analytics.ad_group_daily` but no dedicated ads table. Should I query ad-level data from ad_group_daily, or is there a separate `ads_daily` table I should look for?

Q2. [ASSET EXPANSION] The brief says "expand on row click to show asset-level performance." Does the DB contain headline/description-level performance data, or should the expanded row show the ad's static assets (headline 1, headline 2 etc.) pulled from a separate table?

Q3. [AD STRENGTH] Chat 21d had a column name mismatch (bid_micros vs max_cpc_micros). For ad strength, what is the exact column name in the database — `ad_strength`, `strength`, or something else? Should I run DESCRIBE first?

Q4. [RULES COUNT] The brief says "expect ~11 ad rules." I can see ad_rules.py in the codebase. Should I count them now and confirm, or just load them and whatever number appears is correct?

Q5. [ROUTE CONFLICT] The existing ads.py appears to already have a route registered. Should I overwrite it completely, or preserve the existing route logic and add Bootstrap UI on top?

Waiting for Master Chat answers before proceeding.
```

**User copies these 5 questions to Master Chat. Master answers. User pastes answers back.**

**Master Answer Format:**
```
ANSWERS FOR CHAT 21F WORKER:

A1. [DATABASE] There is no separate ads_daily table. Query ro.analytics.ad_group_daily and join with ad-level data if available. Run DESCRIBE ro.analytics.ad_group_daily first to confirm columns.

A2. [ASSET EXPANSION] No headline-level performance data in DB. Show static asset fields from the ad record (final_url, headline_1, headline_2, description_1, description_2). These exist in the existing ads.py route already.

A3. [AD STRENGTH] Column is `ad_strength` (string). Run DESCRIBE to confirm. Values are: 'POOR', 'AVERAGE', 'GOOD', 'EXCELLENT', NULL. Handle all cases.

A4. [RULES COUNT] Count them now — confirm with DESCRIBE ad_rules.py. Currently 11 rules (AD-001 through AD-011). Whatever loads is correct — don't hardcode the number.

A5. [ROUTE CONFLICT] Overwrite completely. The old route used base.html (not Bootstrap). Start fresh using campaigns.py as the pattern.

Proceed to Stage 2 — write your detailed build plan.
```

**Worker receives answers → writes build plan → sends to user.**

**Build Plan Format:**
```
DETAILED BUILD PLAN FOR MASTER CHAT REVIEW

Files to create/modify:
- C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\ads.py — overwrite with Bootstrap route
- C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\ads_new.html — create new Bootstrap template
- C:\Users\User\Desktop\gads-data-layer\docs\CHAT_21F_HANDOFF.md — create handoff doc

Step-by-step implementation:
STEP A: Update routes/ads.py (~15 min)
  - Import get_rules_for_page helper
  - Query ro.analytics.ad_group_daily (DESCRIBE first)
  - Load ad rules using 'ad' page_type
  - Calculate 7 metrics card aggregations
  - Apply pagination (Python-based, 25 default)

STEP B: Create templates/ads_new.html (~35 min)
  - Extend base_bootstrap.html (line 1 — check first)
  - 7 metrics cards
  - 12-column table with ad strength progress bars
  - Expandable asset rows (JS toggle hidden tr)
  - Rules sidebar/tab/card components

STEP C: Testing (~15 min)
  - All 10 success criteria
  - Browser console check
  - PowerShell output capture

STEP D: Documentation (~10 min)
  - CHAT_21F_HANDOFF.md

Total estimated time: ~75 minutes
Risks: ad_strength NULL values, column name mismatches

Waiting for Master Chat approval before starting.
```

**Master Build Plan Review Format:**
```
BUILD PLAN REVIEW — CHAT 21F:

✅ Files: Correct paths, correct approach
✅ Step A: Good — DESCRIBE first is right
⚠️ Step B: Table should be 13 columns not 12 — add Ad Type column
✅ Step C: Good testing approach
✅ Step D: Good

APPROVED WITH ONE CHANGE:
- Add Ad Type as column 6 in the table

Proceed to implementation.
```

**Worker receives approval → begins Phase 4 (Implementation).**

---

### **PHASE 3: PLANNING (already done in Phase 2B)**

**Note:** The detailed build plan was created and reviewed by Master Chat in Phase 2B. Phase 3 is now complete before Phase 4 begins. Worker should refer back to the approved build plan and follow it exactly.

**If Master requested changes in the build plan review**, update the plan accordingly before proceeding.

**Worker Actions:**
1. Re-read the approved build plan
2. Note any changes Master requested
3. Confirm all reference files are located
4. Begin Phase 4 (Implementation)

---

### **PHASE 4: IMPLEMENTATION (30-60 min)**

**Objective:** Build the actual deliverables

**Worker Actions:**
1. Create/modify files per plan
2. Follow project patterns (reference files)
3. Test incrementally (don't wait till end)
4. Handle edge cases
5. Add comments for complex logic
6. Keep Master informed of progress (optional)

**Best Practices:**
- ✅ Create complete files (not snippets)
- ✅ Follow existing code style
- ✅ Use Bootstrap 5 components (if UI work)
- ✅ Handle NULL values in database queries
- ✅ Add error handling
- ✅ Test each section before moving on

**What to Avoid:**
- ❌ Hardcoding values (use config)
- ❌ Copy-paste without understanding
- ❌ Skipping error handling
- ❌ Assuming data exists (check for NULL)
- ❌ Creating files in wrong directories

**Communication (Optional but Helpful):**
```
Worker progress updates:

"Step 1 complete: routes/ads.py updated (15 min)
- Loaded 11 ad rules successfully
- Metrics calculation working
- Moving to Step 2..."

"Step 2: 50% done - 7 metrics cards complete
- Table structure built
- Working on ad strength progress bars..."
```

---

### **PHASE 5: TESTING (15-30 min)**

**Objective:** Verify everything works before reporting

**Worker Actions:**
1. Test each success criterion individually
2. Test edge cases (empty data, NULLs, large datasets)
3. Test all interactive elements (clicks, filters, pagination)
4. Check browser console (no errors)
5. Test responsive design (mobile + desktop)
6. Performance check (<2 second load)

**Testing Checklist Template:**
```
Manual Testing Results:

Success Criteria:
- [x] 7 metrics cards display correct data
- [x] 13-column table renders horizontally
- [x] Ad strength shows as colored progress bars
- [x] Asset performance expands on click
- [x] 11 ad rules display in sidebar
- [x] Pagination works (10/25/50/100)
- [x] Filters work (date, status, ad type)
- [x] Page loads in <2 seconds

Edge Cases:
- [x] NULL ad strength → shows gray "UNKNOWN"
- [x] Empty dataset → shows "No ads found"
- [x] Large dataset (100+ rows) → pagination works

Browser Console:
- [x] Zero JavaScript errors
- [x] Zero 404 network requests
- [x] Zero warnings

PowerShell Output:
[paste output showing Flask startup, no errors]

Screenshots:
[screenshot showing page working]
```

---

### **PHASE 6: DOCUMENTATION (10-20 min)**

**Objective:** Create comprehensive handoff docs

**Worker Actions:**
1. Create `CHAT_[NUM]_HANDOFF.md`
2. Document what was built
3. Explain key decisions
4. Note issues encountered + solutions
5. List all files changed
6. Provide git commit message

**Handoff Template:**
See `WORKFLOW_TEMPLATES.md` for complete template.

**Key Sections:**
- Summary (what was done)
- Deliverables (files created/modified)
- Success criteria results
- Key decisions (why choices were made)
- Issues encountered (problems + solutions)
- Testing results (comprehensive)
- Git commit message
- Future enhancements

---

### **PHASE 7: COMPLETION (5 min)**

**Objective:** Report completion to Master

**Worker Actions:**
1. Copy all deliverable files to `/mnt/user-data/outputs/`
2. Use `present_files` tool to provide download links
3. Send completion message to Master
4. Wait for review

**Completion Message Template:**
```
Worker: "Chat [NUM] COMPLETE ✅

Summary:
[2-3 sentences describing what was built]

Deliverables:
- routes/ads.py (updated, 287 lines)
- templates/ads_new.html (new, 412 lines)
- CHAT_21F_HANDOFF.md (documentation)

Testing: 8/8 success criteria passing
Time: 75 minutes (vs 70 estimated)

[Links to 3 files]

Ready for Master review."
```

**Then:**
- Worker chat stays available for questions
- Master reviews (may take a few messages)
- If approved → git commit
- If changes needed → worker fixes
- Once committed → worker chat complete

---

### **PHASE 8: ITERATION (if needed)**

**Objective:** Address review feedback

**Worker Actions:**
1. Read Master's review carefully
2. Understand each requested change
3. Fix issues in order of priority
4. Re-test after fixes
5. Update documentation
6. Resubmit

**Example:**
```
Master review: "2 issues found:
1. Ad strength NULL causing crash (high priority)
2. Missing troubleshooting section in handoff (low priority)"

Worker: "Understood. Fixing now:

Fix 1 (Ad strength NULL):
- Added NULL handling in template
- Default to 'UNKNOWN' with gray badge
- Re-tested with synthetic data
- FIXED ✅

Fix 2 (Documentation):
- Added troubleshooting section
- Documented 3 common issues
- FIXED ✅

Updated files:
- templates/ads_new.html (line 145: NULL check added)
- CHAT_21F_HANDOFF.md (new section at line 380)

[Links to updated files]

Ready for re-review."
```

---

## 🤝 HANDOFF PROCESS

### **From Master to Worker (Starting Work)**

**Master Writes Brief:**
```markdown
# CHAT 21F: ADS VIEW REDESIGN

[Complete brief with context, requirements, references, success criteria]

Estimated time: 70 minutes
Ready to start?
```

**Worker Acknowledges:**
```
Worker: "Brief received and understood.

Confirming:
- Task: Redesign ads page with Bootstrap 5
- Deliverables: routes/ads.py (updated), templates/ads_new.html (new)
- Success: 8 criteria listed
- Time: ~70 minutes

Before starting: Please upload complete codebase ZIP:
Location: C:\Users\User\Desktop\gads-data-layer

(Per CHAT_WORKING_RULES.md Rule 1)
```

**User Uploads → Worker Proceeds**

---

### **From Worker to Master (Completing Work)**

**Worker Reports Completion:**
```
Worker: "Chat 21f COMPLETE ✅

[Summary + testing results + file links]

Handoff doc: CHAT_21F_HANDOFF.md (450 lines)
Ready for Master review."
```

**Master Reviews:**
```
Master: "Reviewing Chat 21f...

[5-10 minutes of review]

✅ Functional: 8/8 criteria passing
✅ Code: Clean, follows patterns
✅ Docs: Comprehensive
✅ Integration: No conflicts

APPROVED ✅

Next steps:
1. User commits to git
2. I'll update roadmap
3. Start Chat 21g (Shopping View)
```

**Or if issues:**
```
Master: "Review found 2 issues:

Issue 1: [Description + fix]
Issue 2: [Description + fix]

Please fix and resubmit.
Estimated fix time: 15 minutes
```

**Worker fixes → resubmits → approved → complete**

---

### **From Master to Master (Rolling Chat)**

**Old Master Creates Handoff:**
```markdown
# MASTER CHAT HANDOFF - [Date]

## Status
- Overall: 77% complete
- Chat 21: 62.5% (5/8 pages)
- Last completed: Chat 21e (Ad Groups)
- Next up: Chat 21f (Ads View)

## Active Issues
- Issue 1: [Description + context]
- Issue 2: [Description + context]

## Recent Decisions
- Decision 1: [What + why]
- Decision 2: [What + why]

## Context for Next Master
- Key info new Master needs
- Recent patterns established
- Things to watch out for

## Open Questions
- Question 1: [Needs resolution]
- Question 2: [Needs resolution]

## Files to Review
- MASTER_KNOWLEDGE_BASE.md
- PROJECT_ROADMAP.md
- CHAT_21F_BRIEF.md (ready to go)
```

**New Master Initializes:**
```
New Master: "Master Chat 2.0 initialized.

Context loaded:
✅ MASTER_KNOWLEDGE_BASE.md (2,708 lines)
✅ Handoff from previous Master
✅ PROJECT_ROADMAP.md
✅ All project files in Project Knowledge

Current status understood: 77% complete, 5/8 dashboard pages done

Ready to coordinate. What's the priority?
```

---

## ✅ REVIEW CHECKLIST

### **For Master: Reviewing Worker Output**

**Before Approving ANY Worker Chat:**

**□ Functional Review**
- [ ] All success criteria explicitly checked
- [ ] Manual testing performed by worker (evidence provided)
- [ ] Edge cases tested (NULL values, empty data, errors)
- [ ] No console errors (JavaScript clean)
- [ ] Performance acceptable (<2 seconds initial load)
- [ ] Responsive design tested (mobile + desktop)

**□ Code Quality Review**
- [ ] Files created in correct locations (/home/claude → /mnt/user-data/outputs)
- [ ] Code follows established patterns (reference similar files)
- [ ] No obvious bugs or code smells
- [ ] Comments present for complex logic
- [ ] No hardcoded values (uses config)
- [ ] Error handling present (try/catch, NULL checks)
- [ ] Database queries efficient (no N+1, proper indexes)

**□ Documentation Review**
- [ ] Handoff document created (CHAT_[NUM]_HANDOFF.md)
- [ ] Summary clear and accurate
- [ ] All deliverables listed
- [ ] Key decisions explained
- [ ] Issues encountered documented with solutions
- [ ] Testing results included
- [ ] Git commit message prepared
- [ ] Future enhancements noted

**□ Integration Review**
- [ ] Works with existing code (no conflicts)
- [ ] Doesn't break other pages (regression test)
- [ ] Database schema compatible
- [ ] Templates extend correct base (base_bootstrap.html)
- [ ] Imports don't cause circular dependencies
- [ ] Routes properly registered in __init__.py

**□ Security Review** (where applicable)
- [ ] No SQL injection vulnerabilities
- [ ] Input validation present
- [ ] No exposed credentials
- [ ] CSRF protection (if forms)
- [ ] XSS prevention (template escaping)

**□ User Experience Review**
- [ ] UI is intuitive
- [ ] Error messages are helpful
- [ ] Loading states present (spinners, progress)
- [ ] Confirmation for destructive actions
- [ ] Success feedback (toasts, messages)

**Approval Decision:**

**If all checked → APPROVED ✅**
```
Master: "Chat [NUM] APPROVED ✅

All review criteria passing.
Ready to commit.

Next: [What comes next]"
```

**If issues found → REQUEST CHANGES ⚠️**
```
Master: "Chat [NUM] needs fixes before approval:

Priority 1 Issues (blocking):
- Issue 1: [Clear description + fix]

Priority 2 Issues (non-blocking but recommended):
- Issue 2: [Clear description + fix]

Estimated fix time: [X minutes]
Please fix and resubmit."
```

---

**Version:** 2.0 | **Last Updated:** 2026-02-26
**Next:** See WORKFLOW_TROUBLESHOOTING.md for escalation and debugging
