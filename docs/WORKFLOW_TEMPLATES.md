# WORKFLOW TEMPLATES - CHAT BRIEFS & HANDOFFS

**Version:** 1.2
**Created:** 2026-02-19
**Updated:** 2026-02-23
**Purpose:** Template structures for chat briefs, handoffs, and common scenarios
**Parent Doc:** WORKFLOW_GUIDE.md

---

## 📋 TABLE OF CONTENTS

1. [CHAT_XX_BRIEF Template](#chat-brief-template)
2. [CHAT_XX_HANDOFF Template](#chat-handoff-template)
3. [Common Scenarios](#common-scenarios)
4. [Lessons & Best Practices](#lessons-best-practices)

---

## 📋 TEMPLATES

### **Template 1: Worker Chat Brief**

```markdown
# CHAT [NUMBER]: [TASK NAME]

**Estimated Time:** [X minutes/hours]  
**Dependencies:** [List any prerequisites]  
**Priority:** [HIGH/MEDIUM/LOW]

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
1. File 1: C:\Users\User\Desktop\gads-data-layer\[path]\file1.ext (create/modify)
   - Purpose: [What it does]
   - Key features: [List 3-5 main features]

2. File 2: C:\Users\User\Desktop\gads-data-layer\[path]\file2.ext (create/modify)
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
- Read from /mnt/project/ or project codebase
- path/to/similar1.ext - Shows [pattern X]
- path/to/similar2.ext - Shows [pattern Y]

**Documentation to Consult:**
- /mnt/project/DOCUMENT1.md - Section on [topic]
- /mnt/project/DOCUMENT2.md - Examples of [pattern]

**Database Tables:**
- ro.analytics.table_name - Contains [data]

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

- 5 Questions + Build Plan: [X min]
- Implementation: [Y min]
- Testing (at each step): [Z min]
- Documentation: [W min]
**Total: [X+Y+Z+W min]**

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
