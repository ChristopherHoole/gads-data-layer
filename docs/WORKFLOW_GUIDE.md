# WORKFLOW GUIDE - MASTER & WORKER CHAT OPERATIONS

**Version:** 1.1  
**Created:** 2026-02-19  
**Updated:** 2026-02-19  
**Purpose:** Define systematic processes for Master + Worker chat coordination  
**Audience:** Master Chat (primary), Worker Chats (reference)

---

## 📋 TABLE OF CONTENTS

1. [Overview](#overview)
2. [Master Chat Responsibilities](#master-chat-responsibilities)
3. [Worker Chat Lifecycle](#worker-chat-lifecycle)
4. [Handoff Process](#handoff-process)
5. [Review Checklist](#review-checklist)
6. [Escalation Triggers](#escalation-triggers)
7. [Debugging Playbook](#debugging-playbook)
8. [Success Criteria](#success-criteria)
9. [Templates](#templates)
10. [Common Scenarios](#common-scenarios)

---

## 🎯 OVERVIEW

### **The Master + Worker Pattern**

**Master Chat:**
- Coordinates all development work
- Reviews completed work
- Diagnoses complex problems
- Makes architectural decisions
- Writes briefs for worker chats
- Updates documentation
- Tracks overall progress

**Worker Chats:**
- Execute specific, well-defined tasks
- Focus on one module/page/feature
- Follow instructions from brief
- Produce deliverables (code, files, docs)
- Test their own work
- Report completion to Master

---

### **Why This Pattern Works**

**Problem Without It:**
- Single chat becomes slow (browser lag)
- Context becomes overwhelming
- Hard to focus on specific tasks
- Difficult to parallelize work

**Solution With It:**
- Master stays fast (coordinating, not coding)
- Workers stay focused (single task only)
- Clean separation of concerns
- Can work on multiple features simultaneously
- Easy to restart worker if issues arise

---

### **Key Principles**

1. **Master Never Codes** - Master coordinates, workers execute
2. **One Worker = One Task** - Don't expand scope mid-chat
3. **Clear Handoffs** - Master writes comprehensive briefs
4. **Thorough Testing** - Workers test before reporting complete
5. **Documentation First** - Update docs before starting new work
6. **Escalate Early** - Don't waste >1 hour debugging alone

---

## 👑 MASTER CHAT RESPONSIBILITIES

### **1. Project Coordination** ⭐

**What Master Does:**
- Maintains big-picture view of project
- Tracks what's complete vs in-progress vs planned
- Prioritizes work (what comes next?)
- Identifies dependencies (what blocks what?)
- Allocates tasks to worker chats

**Daily Questions Master Answers:**
- "Where are we in the project?"
- "What should I work on next?"
- "Are we on track?"
- "What's blocking progress?"

**Tools Master Uses:**
- PROJECT_ROADMAP.md - Overall status
- DASHBOARD_PROJECT_PLAN.md - Chat 21 specific
- Recent handoff docs - Context on completed work

**Example Master Coordination:**
```
User: "I'm back, ready to work. What's next?"

Master:
Current Status: 5/8 dashboard pages complete (62.5%)
Last Completed: Chat 21e (Ad Groups View)
Next Up: Chat 21f (Ads View redesign)

Recommendation: Start Chat 21f
- Estimated time: 70 minutes
- Dependencies: None (can start immediately)
- Success criteria: 8 items (see brief)

I'll write the comprehensive brief now.
```

---

### **2. Brief Writing** ⭐⭐⭐

**What Master Does:**
- Writes detailed task briefs for worker chats
- Includes context, requirements, success criteria
- Provides reference files and examples
- Anticipates common issues
- Sets clear expectations

**Brief Template Structure:**
```markdown
# CHAT [NUMBER]: [TASK NAME]

## Context
- What's been done already
- Why this task is needed
- How it fits into bigger picture

## Objective
- Clear, single-sentence goal
- Measurable success criteria (8-10 items)

## Requirements
- Specific deliverables (files to create/modify)
- Technical constraints
- Design specifications
- Testing requirements

## Reference Files
- Existing files to examine
- Similar completed work to model
- Documentation to consult

## Success Criteria (Checklist)
- [ ] Criterion 1
- [ ] Criterion 2
- ... (8-10 total)

## Testing Instructions
- How to verify it works
- What to check manually
- What edge cases to test

## Estimated Time
- Realistic estimate based on past work
- Note if uncertain

## Potential Issues
- Common pitfalls to avoid
- Things to watch out for
- Known gotchas

## Handoff Requirements
- What documentation to create
- What to report back
- What to commit to git
```

**Good Brief Characteristics:**
- ✅ **Comprehensive** - Worker doesn't need to ask basic questions
- ✅ **Specific** - Clear acceptance criteria
- ✅ **Referenced** - Points to existing examples
- ✅ **Realistic** - Scoped appropriately
- ✅ **Testable** - Clear way to verify success

**Example Brief (Abbreviated):**
```markdown
# CHAT 21F: ADS VIEW REDESIGN

## Context
You're redesigning the existing ads.py route and ads.html template 
with Bootstrap 5. This is page 6/8 in the dashboard UI overhaul.
Campaigns (21c), Ad Groups (21e), and Keywords (21d) are complete 
and working - use them as reference.

## Objective
Redesign ads page with Bootstrap 5, maintaining all existing 
functionality while adding professional styling and rules integration.

## Requirements
1. Update routes/ads.py - Load ad rules
2. Create templates/ads_new.html - Bootstrap 5 redesign
3. 7 metrics cards (Total, Clicks, Cost, Conv., CTR, Ad Strength)
4. 13-column table with expandable asset performance
5. Ad strength progress bars (POOR=red, AVERAGE=yellow, GOOD=green)
6. Rules integration (sidebar, tab, card)
7. Pagination (10/25/50/100)
8. Filters (date, status, ad type)

## Reference Files
- routes/campaigns.py - Similar structure
- templates/campaigns.html - Bootstrap 5 patterns
- routes/keywords.py - Rules integration example
- templates/keywords_new.html - Expandable rows

## Success Criteria
- [ ] 7 metrics cards display correct aggregated data
- [ ] 13-column table renders without stacking
- [ ] Ad strength shows as colored progress bars
- [ ] Asset performance expands on row click
- [ ] 11 ad rules display in sidebar/tab/card
- [ ] Pagination works (10/25/50/100)
- [ ] Filters work (date, status, ad type)
- [ ] Page loads in <2 seconds

## Estimated Time: 70 minutes

## Potential Issues
- Asset performance expansion needs careful JavaScript
- Ad strength calculation may have NULL values
- Rules display should show 11 rules (AD-* pattern)
```

---

### **3. Work Review** ⭐⭐

**What Master Does:**
- Reviews completed work from workers
- Verifies success criteria met
- Tests functionality manually
- Checks code quality
- Identifies issues/bugs
- Approves or requests changes

**Review Checklist (Use This Every Time):**

**Functional Review:**
- [ ] All success criteria checked off
- [ ] Manual testing performed by worker
- [ ] Edge cases tested
- [ ] Error handling works
- [ ] No console errors
- [ ] Performance acceptable (<2s load)

**Code Review:**
- [ ] Files created in correct locations
- [ ] Code follows project patterns
- [ ] No obvious bugs or issues
- [ ] Comments where needed
- [ ] No hardcoded values (use config)

**Documentation Review:**
- [ ] Handoff document created
- [ ] Key decisions documented
- [ ] Issues encountered noted
- [ ] Git commit message prepared
- [ ] Roadmap updated (if applicable)

**Integration Review:**
- [ ] Works with existing code
- [ ] Doesn't break other pages
- [ ] Database queries efficient
- [ ] No schema conflicts

**Example Review (Approving):**
```
Master reviewing Chat 21e (Ad Groups):

✅ Functional: All 8 criteria passing
✅ Code: Clean, follows campaigns.py pattern
✅ Docs: CHAT_21E_HANDOFF.md excellent
✅ Integration: No conflicts with existing pages

APPROVED ✅

Action items:
1. Commit code to git
2. Update PROJECT_ROADMAP.md (done)
3. Move to Chat 21f (Ads View)
```

**Example Review (Requesting Changes):**
```
Master reviewing hypothetical Chat:

❌ Functional: Success criterion #3 failing (table stacks vertically)
✅ Code: Structure good
⚠️ Docs: Missing troubleshooting section
✅ Integration: No conflicts

NOT APPROVED - Needs fixes:

Issue 1: Table rendering
- Root cause: Wrong base template (base.html vs base_bootstrap.html)
- Fix: Line 1 of template, change extends
- Estimated fix time: 2 minutes

Issue 2: Documentation
- Add troubleshooting section to handoff
- Document the template inheritance issue
- Estimated fix time: 10 minutes

Please fix and resubmit.
```

---

### **4. Problem Diagnosis** ⭐⭐⭐

**What Master Does:**
- Investigates issues workers get stuck on
- Identifies root causes quickly
- Provides clear solutions
- Prevents circular debugging
- Updates troubleshooting docs

**Diagnosis Process:**

**Step 1: Gather Information (5 min)**
```
Questions to ask:
- What were you trying to do?
- What did you expect to happen?
- What actually happened?
- What have you tried already?
- Show me the exact error message
- Show me the relevant code
```

**Step 2: Reproduce Locally (5 min)**
```
Actions:
- Review the uploaded codebase
- Examine the specific file(s)
- Check related files for context
- Look at similar working examples
```

**Step 3: Form Hypothesis (10 min)**
```
Check common issues first:
1. Template inheritance (base.html vs base_bootstrap.html)
2. Database table names (analytics vs ro.analytics)
3. Missing imports
4. Typos in variable names
5. Wrong file paths
6. NULL handling in queries
7. JavaScript errors
8. CSS conflicts
```

**Step 4: Validate & Fix (10 min)**
```
- Test the hypothesis
- Provide exact fix (not just guidance)
- Explain why it failed
- Provide updated file if needed
```

**Time Limit:** 30 minutes max per issue
- If not solved in 30 min → Escalate to user
- Don't waste time on circular debugging

**Example Diagnosis (Chat 21e):**
```
Worker: "Table rendering vertically, all columns stacked"

Master Investigation:
1. Gather info: Screenshot shows vertical stack
2. Reproduce: View ad_groups.html line 1
3. Hypothesis: Wrong base template (similar to past issue)
4. Validate: Line 1 says "extends base.html"

ROOT CAUSE: Template inheritance
- ad_groups.html extends base.html (no Bootstrap)
- Should extend base_bootstrap.html (has Bootstrap 5)

FIX: Change line 1 to {% extends "base_bootstrap.html" %}

DIAGNOSIS TIME: 2 minutes (knew from past experience)
```

---

### **5. Documentation Maintenance** ⭐

**What Master Does:**
- Updates PROJECT_ROADMAP.md after each chat
- Updates DASHBOARD_PROJECT_PLAN.md for Chat 21 work
- Reviews handoff documents
- Maintains this WORKFLOW_GUIDE.md
- Archives old master chat transcripts

**After Each Worker Chat:**
```
1. Review handoff doc from worker
2. Update PROJECT_ROADMAP.md:
   - Mark chat complete
   - Update completion percentage
   - Note actual time vs estimate
   - Add commit hash
3. Update DASHBOARD_PROJECT_PLAN.md (if Chat 21):
   - Check off completed items
   - Update progress tracking
4. Commit documentation updates to git
```

**Weekly:**
```
1. Review all handoff docs from week
2. Extract common issues → Add to troubleshooting
3. Update LESSONS_LEARNED section
4. Archive master chat transcript (if rolling to new master)
```

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
- [x] Ad strength bars show correct colors
- [x] Asset rows expand on click
- [x] 11 ad rules display in sidebar
- [x] Pagination works (10/25/50/100)
- [x] Filters work (date, status, type)
- [x] Page loads in <2 seconds

Edge Cases:
- [x] Handles ads with no assets
- [x] Handles NULL ad_strength values
- [x] Handles 0 conversions (no divide by zero)

Browser Console:
- [x] No JavaScript errors
- [x] No 404s (all resources load)

Responsive:
- [x] Desktop 1920x1080 - working
- [x] Mobile 375x667 - table scrolls horizontally

Performance:
- [x] Initial load: 1.2 seconds
- [x] Table render: 0.3 seconds
```

**If ANY test fails:**
- Don't report complete
- Fix the issue
- Re-test
- Then report

---

### **PHASE 6: DOCUMENTATION (15-20 min)**

**Objective:** Create comprehensive handoff document

**Worker Actions:**
1. Create CHAT_[NUMBER]_HANDOFF.md
2. Document all deliverables
3. Explain key decisions
4. Note issues encountered + solutions
5. Provide testing evidence
6. Create git commit message
7. Note future enhancements

**Handoff Document Template:**
```markdown
# CHAT [NUMBER]: [TASK NAME] - COMPLETE HANDOFF

**Time:** [actual] vs [estimated]  
**Status:** ✅ COMPLETE  
**Commit:** [hash if committed, or PENDING]

## Summary
[2-3 sentences: what was built]

## Deliverables
**Files Created:**
- path/to/file1.py (X lines) - Purpose
- path/to/file2.html (Y lines) - Purpose

**Files Modified:**
- path/to/file3.py (Z lines added) - What changed

## Success Criteria Results
- [x] Criterion 1 - PASS (evidence: screenshot/log)
- [x] Criterion 2 - PASS
... (all criteria)

## Key Decisions
1. Decision 1: Why we chose X over Y
2. Decision 2: How we handled Z edge case

## Issues Encountered
### Issue 1: [Brief description]
**Problem:** [What went wrong]
**Root Cause:** [Why it failed]
**Solution:** [How we fixed it]
**Time Lost:** [X minutes]

## Testing Results
[Copy from Phase 5 testing checklist]

## Git Commit Message
```
[Prepared commit message matching template]
```

## Future Enhancements
- Enhancement 1: [Description] (Low priority)
- Enhancement 2: [Description] (Medium priority)

## Notes for Master
- Anything Master should know
- Dependencies for next work
- Recommendations
```

**Documentation Quality Matters:**
- Future you (or others) will read this
- Master needs it for review
- Other workers may reference it
- It's part of the deliverable

---

### **PHASE 7: DELIVERY (5 min)**

**Objective:** Report completion and hand off to Master

**Worker Actions:**
1. Copy deliverable files to /mnt/user-data/outputs/
2. Present files to user
3. Summarize completion
4. Note any caveats
5. Await Master review

**Example Delivery:**
```
Worker: "Chat 21f (Ads View redesign) COMPLETE ✅

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

## 🚨 ESCALATION TRIGGERS

### **When Worker Should Escalate to Master**

**Immediate Escalation (Don't Try to Fix Yourself):**
1. **Architecture Decision Needed**
   - "Should we use X pattern or Y pattern?"
   - "This requires database schema change - is that okay?"
   - "Found security vulnerability - how to proceed?"

2. **Scope Confusion**
   - "Brief says X but existing code does Y - which is correct?"
   - "Success criteria seem contradictory"
   - "Task seems much larger than estimated"

3. **Breaking Changes**
   - "This fix would break existing functionality"
   - "Need to modify files outside my scope"
   - "Database migration required"

**Escalate After 1 Hour (Don't Debug Forever):**
1. **Stuck on Bug**
   - Tried 3+ approaches, none work
   - Root cause unclear
   - Circular debugging

2. **Missing Information**
   - Reference files don't exist
   - Documentation unclear
   - Can't find examples

3. **Tool/Environment Issues**
   - Code works locally but fails in user environment
   - Library version mismatch
   - Dependency conflicts

**Example Escalation:**
```
Worker to Master:

"Stuck on ad strength progress bar rendering. Tried 3 approaches:

1. CSS width: Doesn't animate
2. Bootstrap progress bar: Wrong colors
3. Custom div: Positioning issues

Root cause unclear. Been debugging 1 hour.

Request Master assistance for diagnosis.

Context:
- File: templates/ads_new.html line 145
- Expected: Colored progress bar (POOR=red, GOOD=green)
- Actual: Gray bar with no color
- Reference: keywords.py has similar but for Quality Score
```

**What NOT to Escalate:**
- Simple typos (fix yourself)
- Minor styling tweaks (iterate yourself)
- Documentation formatting (fix yourself)
- Questions answered in brief (re-read brief)

---

### **When Master Should Escalate to User**

**Immediate Escalation:**
1. **Needs User Decision**
   - Multiple valid approaches, user preference needed
   - Budget/timeline concerns
   - Strategic direction

2. **Permission Required**
   - Breaking changes to production code
   - Database schema modifications
   - Third-party service integration

3. **Blocking Issues**
   - Can't access required resources
   - Credentials needed
   - Environment-specific problem

**Escalate After 30 Minutes:**
1. **Diagnosis Failure**
   - Can't reproduce issue
   - Root cause unclear after thorough investigation
   - Multiple hypotheses, none confirm

2. **Resource Constraints**
   - Need access to files/systems
   - Missing documentation
   - Unclear requirements

**Example Escalation:**
```
Master to User:

"Chat 21f blocked on execution API integration.

Issue: routes/api.py expects JSON files for recommendations
But: ads.py generates recommendations live (no JSON)

Options:
A) Modify API to accept recommendations as payload (1 hr work)
B) Save live recommendations to temp JSON (30 min work)
C) Create separate execution endpoint for live recs (2 hr work)

Need your decision on approach before proceeding.

Recommendation: Option B (fastest, least risk)
```

---

## 🔍 DEBUGGING PLAYBOOK

### **For Master: Systematic Problem Diagnosis**

When a worker escalates a problem, use this systematic approach:

---

### **Step 1: Gather Context (5 minutes)**

**Questions to Ask:**
```
1. What were you trying to do?
2. What did you expect to happen?
3. What actually happened?
4. What's the exact error message? (copy/paste)
5. What have you already tried?
6. When did it last work correctly?
7. What changed since it last worked?
```

**Information to Request:**
```
1. Exact error output (terminal or browser console)
2. Relevant code snippet (10-20 lines)
3. Screenshot (if UI issue)
4. File version (request current file if needed)
5. Steps to reproduce
```

---

### **Step 2: Check Common Issues First (10 minutes)**

**Go through this list in order:**

**UI/Template Issues:**
- [ ] Template inheritance (base.html vs base_bootstrap.html) ⭐ **#1 cause**
- [ ] Missing Bootstrap CSS link
- [ ] Typo in template syntax ({% vs {{)
- [ ] Missing {% endblock %}
- [ ] Wrong file path in route (render_template)

**Database Issues:**
- [ ] Table name wrong (analytics vs ro.analytics) ⭐ **#2 cause**
- [ ] Column name typo
- [ ] Missing NULL handling
- [ ] Wrong date format
- [ ] Connection not closed

**Python/Logic Issues:**
- [ ] Import error (missing import)
- [ ] Variable name typo
- [ ] Indentation error
- [ ] Division by zero (check denominators)
- [ ] Dict vs object attribute (rec['x'] vs rec.x)

**JavaScript Issues:**
- [ ] Console errors (check browser console)
- [ ] Missing event handler
- [ ] Incorrect selector (getElementById)
- [ ] Async/await issues

**Configuration Issues:**
- [ ] Wrong config file loaded
- [ ] Missing required field
- [ ] Enum value typo
- [ ] Path separator wrong (Windows \ vs Linux /)

---

### **Step 3: Reproduce and Diagnose (10 minutes)**

**If Issue Not in Common List:**

**For Code Issues:**
```python
# Add debug logging
print(f"DEBUG: variable = {variable}")
print(f"DEBUG: type = {type(variable)}")

# Check for None
if variable is None:
    print("DEBUG: variable is None!")

# Log query results
print(f"DEBUG: query returned {len(results)} rows")
```

**For Template Issues:**
```html
<!-- Add debug output -->
<p>DEBUG: campaigns = {{ campaigns }}</p>
<p>DEBUG: campaigns length = {{ campaigns|length }}</p>
<p>DEBUG: first campaign = {{ campaigns[0] if campaigns else 'EMPTY' }}</p>
```

**For Database Issues:**
```sql
-- Run query manually in DuckDB
SELECT * FROM analytics.campaign_daily LIMIT 1;

-- Check table exists
SHOW TABLES;

-- Check column names
DESCRIBE analytics.campaign_daily;
```

---

### **Step 4: Form Hypothesis (5 minutes)**

**Ask Yourself:**
- What's the simplest explanation?
- Have we seen this before? (check past handoffs)
- What would cause these exact symptoms?
- What changed recently?

**Hypothesis Template:**
```
HYPOTHESIS: [What I think is wrong]
EVIDENCE: [Why I think this]
TEST: [How to confirm]
FIX: [How to resolve if confirmed]
```

**Example:**
```
HYPOTHESIS: Template extending wrong base (no Bootstrap)
EVIDENCE: Table columns stacking (no grid system), plain styling
TEST: Check line 1 of ad_groups.html for {% extends %}
FIX: Change to {% extends "base_bootstrap.html" %}
```

---

### **Step 5: Test and Fix (10 minutes)**

**Test Hypothesis:**
- Implement minimal test case
- Confirm root cause
- Verify fix works

**Provide Solution:**
```
Master to Worker:

"ROOT CAUSE IDENTIFIED: [Clear explanation]

WHY IT FAILED: [Technical reason]

FIX: [Step-by-step solution]

UPDATED FILE: [Provide complete fixed file if needed]

TEST: [How to verify fix works]

ESTIMATED FIX TIME: [X minutes]
```

---

### **Step 6: Document for Future (5 minutes)**

**If New Issue:**
- Add to MASTER_KNOWLEDGE_BASE.md "Common Problems" section
- Update worker brief template with warning
- Add to CHAT_WORKING_RULES.md if applicable

**Example Documentation:**
```markdown
### Problem 9: Ad Strength NULL Crashes

**Symptoms:**
- Page loads but crashes on specific ads
- Error: "Cannot read property 'ad_strength' of null"

**Root Cause:**
- Some ads don't have ad_strength value
- Template doesn't handle NULL

**Solution:**
```html
<!-- WRONG: -->
<span>{{ ad.ad_strength }}</span>

<!-- CORRECT: -->
<span>{{ ad.ad_strength or 'UNKNOWN' }}</span>
```

**Time to Fix:** 2 minutes
```

---

### **Debugging Time Limits**

**Maximum Time Per Issue:**
- Simple issues: 10 minutes
- Medium issues: 20 minutes
- Complex issues: 30 minutes

**If Exceeds Time Limit:**
- Escalate to user
- Don't keep trying approaches that don't work
- Admit when stumped

---

## 🎯 SUCCESS CRITERIA

### **For Worker Chats**

**A successful worker chat:**
- ✅ Completes assigned task (all success criteria met)
- ✅ Stays within scope (doesn't expand mission)
- ✅ Produces high-quality deliverables (tested and working)
- ✅ Creates comprehensive documentation (handoff doc)
- ✅ Finishes within reasonable time (actual ≤ 2X estimate)
- ✅ Requires minimal Master intervention (<3 escalations)
- ✅ Integrates cleanly (no conflicts with existing code)

**Red Flags (Worker Needs Help):**
- ❌ Scope creep (task expanding beyond brief)
- ❌ Circular debugging (>1 hour on same issue)
- ❌ Multiple false starts (rewriting same section)
- ❌ Confusion about requirements
- ❌ Success criteria can't be tested
- ❌ Poor code quality (not following patterns)

---

### **For Master Chat**

**A successful master chat:**
- ✅ Coordinates efficiently (clear priorities, no confusion)
- ✅ Writes comprehensive briefs (workers rarely need clarification)
- ✅ Reviews thoroughly (catches issues before git commit)
- ✅ Diagnoses quickly (most problems solved <30 min)
- ✅ Maintains documentation (roadmap always current)
- ✅ Manages scope (prevents feature creep)
- ✅ Facilitates progress (unblocks workers promptly)

**Red Flags (Master Needs Improvement):**
- ❌ Vague briefs (workers confused about requirements)
- ❌ Slow reviews (workers waiting >1 hour)
- ❌ Missed issues (bugs found after commit)
- ❌ Outdated documentation (roadmap doesn't match reality)
- ❌ Lost context (asking questions already answered)
- ❌ Poor prioritization (working on low-value tasks)

---

### **For Overall Process**

**The Master + Worker pattern is working when:**
- ✅ Steady progress (completing 1-2 chats per day)
- ✅ High quality (few bugs, clean code)
- ✅ Good documentation (comprehensive handoffs)
- ✅ Minimal rework (first implementation usually correct)
- ✅ Fast Master response (browser stays responsive)
- ✅ Clear communication (everyone knows what's happening)
- ✅ User satisfaction (user feels in control, informed)

---

## 📋 TEMPLATES

### **Template 1: Worker Chat Brief**

```markdown
# CHAT [NUMBER]: [TASK NAME]

**Estimated Time:** [X minutes/hours]  
**Dependencies:** [List any prerequisites]  
**Priority:** [HIGH/MEDIUM/LOW]

---

## CONTEXT

[2-3 paragraphs explaining:
- What's been done already
- Why this task is needed
- How it fits into the bigger picture]

---

## OBJECTIVE

[Single clear sentence describing the goal]

---

## REQUIREMENTS

### Deliverables
1. File 1: path/to/file1.ext (create/modify)
   - Purpose: [What it does]
   - Key features: [List 3-5 main features]

2. File 2: path/to/file2.ext (create/modify)
   - Purpose: [What it does]
   - Key features: [List 3-5 main features]

### Technical Constraints
- Constraint 1
- Constraint 2
- Constraint 3

### Design Specifications
- Bootstrap 5 components
- Color palette: [Specify]
- Layout: [Describe structure]

---

## REFERENCE FILES

**Similar Completed Work:**
- path/to/similar1.ext - Shows [pattern X]
- path/to/similar2.ext - Shows [pattern Y]

**Documentation to Consult:**
- docs/DOCUMENT1.md - Section on [topic]
- docs/DOCUMENT2.md - Examples of [pattern]

**Database Tables:**
- analytics.table_name - Contains [data]

---

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

---

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

---

## POTENTIAL ISSUES

### Common Pitfalls to Avoid
1. Issue 1: [Description + how to avoid]
2. Issue 2: [Description + how to avoid]
3. Issue 3: [Description + how to avoid]

### Known Gotchas
- Gotcha 1: [What + why]
- Gotcha 2: [What + why]

---

## HANDOFF REQUIREMENTS

**Documentation:**
- Create CHAT_[NUMBER]_HANDOFF.md (use template)
- Include all testing results
- Document any issues encountered

**Git:**
- Prepare commit message (use template)
- List all files to commit

**Delivery:**
- Copy files to /mnt/user-data/outputs/
- Use present_files tool
- Await Master review

---

## ESTIMATED TIME BREAKDOWN

- Setup: [X min]
- Implementation: [Y min]
- Testing: [Z min]
- Documentation: [W min]
**Total: [X+Y+Z+W min]**

---

Ready to start? Upload codebase first (CHAT_WORKING_RULES.md Rule 1).
```

---

### **Template 2: Handoff Document**

```markdown
# CHAT [NUMBER]: [TASK NAME] - COMPLETE HANDOFF

**Date:** [YYYY-MM-DD]  
**Worker:** [Chat name/number]  
**Time:** [Actual] vs [Estimated]  
**Status:** ✅ COMPLETE / ⚠️ PARTIAL / ❌ BLOCKED  
**Commit:** [hash] / PENDING

---

## EXECUTIVE SUMMARY

[2-3 sentences: What was built and why it matters]

---

## DELIVERABLES

### Files Created
- `path/to/file1.ext` ([X lines]) - [Purpose]
- `path/to/file2.ext` ([Y lines]) - [Purpose]

### Files Modified
- `path/to/file3.ext` ([Z lines added/changed]) - [What changed]

### Other Outputs
- [Documentation, configs, etc.]

---

## SUCCESS CRITERIA RESULTS

- [x] Criterion 1 - PASS ✅
  - Evidence: [Screenshot/log/description]
- [x] Criterion 2 - PASS ✅
  - Evidence: [Screenshot/log/description]
[... all criteria listed with pass/fail]

**Summary: [X/Y] criteria passing**

---

## IMPLEMENTATION DETAILS

### Approach
[Paragraph explaining overall approach taken]

### Key Decisions
1. **Decision 1:** [What was decided]
   - Why: [Rationale]
   - Alternatives considered: [A, B, C]
   
2. **Decision 2:** [What was decided]
   - Why: [Rationale]

### Code Patterns Used
- Pattern 1: [Description + where applied]
- Pattern 2: [Description + where applied]

---

## ISSUES ENCOUNTERED

### Issue 1: [Brief description]
**Problem:** [What went wrong]  
**Root Cause:** [Why it failed]  
**Solution:** [How we fixed it]  
**Time Lost:** [X minutes]  
**Prevention:** [How to avoid in future]

[Repeat for each issue]

---

## TESTING RESULTS

### Manual Testing Checklist
- [x] Test 1 description - PASS
- [x] Test 2 description - PASS
[... all tests]

### Edge Cases Tested
- [x] Empty data - Handled correctly
- [x] NULL values - Handled correctly
- [x] Large dataset (100+ items) - Performance OK

### Performance Metrics
- Initial page load: [X.X seconds] (target: <2s)
- Table render: [X.X seconds] (target: <0.5s)
- Memory usage: [OK/ISSUE]

### Browser Console
- [x] No JavaScript errors
- [x] No 404s
- [x] No warnings

---

## DATABASE QUERIES

### New Queries Added
```sql
-- Query 1 description
SELECT ...
FROM ...
WHERE ...
```

### Query Performance
- Query 1: [X.X seconds] on [Y rows]
- Indexes used: [list]

---

## TECHNICAL DEBT

### Created (Intentional)
1. [Description] - Why deferred: [Reason]
2. [Description] - Why deferred: [Reason]

### Resolved
1. [Description] - How resolved: [Solution]

---

## GIT COMMIT MESSAGE

```
[Type]: [Brief description]

[Component] - [Detailed description]

Deliverables:
- File 1 description
- File 2 description

Testing:
- All X success criteria passing
- Edge cases handled
- Performance acceptable

Issues resolved:
- Issue 1
- Issue 2

Time: [X minutes]
Commit: [PENDING]
```

---

## FUTURE ENHANCEMENTS

### Immediate (Next Chat)
- Enhancement 1: [Description + impact]

### Short-term (This Phase)
- Enhancement 2: [Description + impact]

### Long-term (Backlog)
- Enhancement 3: [Description + impact]

---

## NOTES FOR MASTER

**Review Priority:**
- [ ] Functional review (all criteria)
- [ ] Code quality review
- [ ] Integration testing
- [ ] Documentation completeness

**Special Attention:**
- Area 1: [Why it needs attention]
- Area 2: [Why it needs attention]

**Dependencies:**
- Blocks: [What this blocks]
- Blocked by: [What blocks this]

**Recommendations:**
- Recommendation 1
- Recommendation 2

---

**Handoff complete. Ready for Master review.**
```

---

### **Template 3: Git Commit Message**

```
[TYPE]: [Brief description in <50 chars]

[Component/Module] - [Detailed description in 1-2 sentences]

Features:
- Feature 1: Description
- Feature 2: Description
- Feature 3: Description

Files Created:
- path/to/file1.ext ([X lines]) - Purpose
- path/to/file2.ext ([Y lines]) - Purpose

Files Modified:
- path/to/file3.ext ([Z lines changed]) - What changed

Testing:
- All [X] success criteria passing
- Edge cases: [list key ones]
- Performance: [metrics]
- Manual testing: [hours spent]

Issues Resolved:
- Issue 1: Description + fix
- Issue 2: Description + fix

Time: [X hours/minutes] ([actual] vs [estimated])
Status: Production-ready / Needs follow-up
Chat: [Number]
```

**TYPE options:**
- `feat:` New feature
- `fix:` Bug fix
- `refactor:` Code restructure
- `docs:` Documentation only
- `style:` CSS/UI changes
- `test:` Test additions
- `chore:` Maintenance

---

### **Template 4: Master Chat Initialization**

```markdown
You are the Master Chat for the ACT Dashboard project. Your role:

RESPONSIBILITIES:
- Coordinate all worker chats (21f-21h and beyond)
- Review worker output and diagnose problems  
- Write briefs for new worker chats
- Make architectural decisions
- Update project documentation

CURRENT STATUS:
- Project: Chat 21 (Dashboard UI Overhaul with Bootstrap 5)
- Progress: [X/8] pages complete ([Y]%)
- Completed: Chats 21a ([Component]), 21b ([Component]), ...
- Next: Chat [NUMBER] ([Task]) - needs brief written
- Remaining: [List remaining]

CONTEXT AVAILABLE:
- All project files are uploaded to Project Knowledge
- You can reference any worker chat in this project
- MASTER_KNOWLEDGE_BASE.md has full project history
- PROJECT_ROADMAP.md has current status
- DASHBOARD_PROJECT_PLAN.md has Chat 21 details

WORKING RULES:
- Always use WORKFLOW_GUIDE.md patterns
- Write comprehensive briefs before starting workers
- Review thoroughly using checklist
- Diagnose problems systematically
- Update documentation after each chat
- Escalate to user if stuck >30 min

Ready to coordinate. What do you need?
```

---

## 🎭 COMMON SCENARIOS

### **Scenario 1: Starting Fresh Worker Chat**

**User:** "I'm ready to work on the next page."

**Master:**
```
Current Status: 5/8 dashboard pages complete
Next: Chat 21f (Ads View redesign)

I'll write the comprehensive brief now. Give me 5 minutes...

[Master writes detailed brief using template]

Brief ready: CHAT_21F_BRIEF.md

Please:
1. Start new worker chat in ACT project
2. Paste this brief in first message
3. Worker will request codebase upload
4. Then begin implementation

Estimated time: 70 minutes
Ready?
```

---

### **Scenario 2: Worker Stuck on Bug**

**Worker:** "Been debugging table rendering issue for 45 min. Columns stack vertically but should be horizontal. Tried 3 approaches, none work. Need Master help."

**Master:**
```
Escalation received. Investigating...

Please provide:
1. Screenshot of issue
2. Current file: templates/ads_new.html
3. Line 1 of template ({% extends ... %})

[Worker provides info]

ROOT CAUSE IDENTIFIED: Template inheritance

Your template extends base.html (no Bootstrap)
Should extend base_bootstrap.html (has Bootstrap 5 CSS)

FIX:
Line 1: Change to {% extends "base_bootstrap.html" %}

This is Problem #3 in our common issues (Chat 21e had same issue)

DIAGNOSIS TIME: 3 minutes
FIX TIME: 30 seconds

Try it and report back.
```

---

### **Scenario 3: Worker Exceeds Time Estimate**

**Worker:** "Implementation taking longer than estimated. At 90 minutes vs 70 estimated. Should I continue or stop?"

**Master:**
```
Status check:

How much is left? [Worker answers: ~30 min]
Quality of work so far? [Worker: Good, all tested]
Any blockers? [Worker: No, just taking longer]

Decision: CONTINUE

Revised estimate: 120 minutes total
This happens - complex UI work often takes 1.5-2X estimate

Please update handoff doc with:
- Actual time: 120 min
- Why it took longer: [Your explanation]

Finish the work properly rather than rush.
```

---

### **Scenario 4: User Changes Requirements Mid-Chat**

**User:** "Actually, can we add a feature where users can export to CSV?"

**Master:**
```
Scope change request received.

Current Chat 21f scope: Ads View redesign (8 success criteria)
New request: Add CSV export feature

Analysis:
- New feature adds ~30-45 min work
- Worker already 60 min into current task
- Original estimate: 70 min → New estimate: 115 min

Options:
A) Add to current chat (finish in one go)
B) Complete current chat, add export in Chat 21f-2
C) Defer to Chat 21h (Polish phase)

Recommendation: Option C (defer to polish)
- Don't expand worker scope mid-task
- CSV export is enhancement, not core
- Better to complete 8 criteria first

Your decision?
```

---

### **Scenario 5: Multiple Workers Running Simultaneously**

**User:** "Can I have two workers running at same time? One on Ads (21f), one on Shopping (21g)?"

**Master:**
```
Yes, BUT with careful coordination:

Requirements:
1. No overlapping files (different .py and .html files)
2. Clear naming (Chat 21f, Chat 21g)
3. Stagger testing (don't test both at once)
4. Separate commits (don't mix changes)

Risk: Integration conflicts
- If both modify __init__.py → merge carefully
- If both modify base_bootstrap.html → coordinate

Recommendation: Finish 21f first, then 21g
- Cleaner workflow
- Lower risk
- Easier review

But if you want parallel work, I can coordinate.
Your call?
```

---

### **Scenario 6: Worker Delivers Low Quality**

**Master Review Finds:**
- 3 success criteria failing
- No error handling
- Hardcoded values
- Poor documentation

**Master:**
```
Chat [NUM] review: CHANGES REQUIRED

Quality Issues Found:

PRIORITY 1 (Blocking):
- Success criteria 2, 4, 7 failing
- No NULL handling in database queries
- Hardcoded customer_id (should use config)

PRIORITY 2 (Recommended):
- Missing error handling (try/catch)
- Handoff doc incomplete (no testing section)
- Comments needed in complex functions

This needs substantial rework before approval.

Recommendation: 
Rather than iterate here, let's start fresh worker chat
with improved brief addressing these issues.

OR continue fixing here if you prefer (est. 45 min fixes).

Your preference?
```

---

### **Scenario 7: Browser Lag Returns**

**User:** "Master chat getting slow again. 10-minute waits."

**Master:**
```
Browser UI lag detected (again).

Diagnosis:
- Current chat: [X] messages
- Files uploaded: [Y]
- DOM size: Large

Solution: Roll to new Master

Process:
1. I'll create MASTER_HANDOFF.md right now
2. You start new Master Chat in ACT project
3. New Master reads handoff + knowledge base
4. Continue from there

This old Master chat:
- Keep open for reference (separate tab)
- Don't delete (has valuable history)
- Just don't use for new work

Creating handoff now...
```

---

## 🎓 LESSONS & BEST PRACTICES

### **For Master Chats**

**DO:**
- ✅ Write comprehensive briefs (save time later)
- ✅ Use review checklist every time
- ✅ Diagnose systematically (don't guess)
- ✅ Update docs after each chat
- ✅ Catch issues before git commit
- ✅ Maintain project knowledge base
- ✅ Roll to new Master when laggy

**DON'T:**
- ❌ Write vague briefs ("just make it better")
- ❌ Skip review steps (causes bugs)
- ❌ Let workers struggle >1 hour
- ❌ Approve incomplete work
- ❌ Forget to update roadmap
- ❌ Let documentation fall behind

---

### **For Worker Chats**

**DO:**
- ✅ Read brief thoroughly first
- ✅ Upload codebase before starting
- ✅ Follow reference examples closely
- ✅ Test incrementally (don't wait till end)
- ✅ Handle edge cases (NULL, empty, errors)
- ✅ Create comprehensive handoff doc
- ✅ Escalate early if stuck

**DON'T:**
- ❌ Expand scope beyond brief
- ❌ Skip codebase upload (Rule 1!)
- ❌ Assume data exists (always check NULL)
- ❌ Test at the end only
- ❌ Ship half-working code
- ❌ Debug in circles >1 hour
- ❌ Forget documentation

---

### **For Both**

**Communication:**
- Be explicit (don't assume understanding)
- Provide evidence (screenshots, logs)
- Ask clarifying questions
- Confirm decisions
- Document everything

**Quality:**
- Test thoroughly
- Handle errors
- Follow patterns
- Write clean code
- Document decisions

**Efficiency:**
- Don't waste time
- Escalate when stuck
- Use templates
- Learn from past issues
- Improve processes

---

**END OF WORKFLOW GUIDE**

**This document version:** 1.0  
**Created:** 2026-02-19  
**For:** Master Chat 2.0 + all Worker Chats  
**Total length:** ~6,500 lines

**Next:** Use these workflows to maintain high quality and steady progress! 🚀
