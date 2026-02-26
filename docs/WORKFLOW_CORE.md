# WORKFLOW CORE - Master & Worker Chat Coordination

**Version:** 2.0 (Split from WORKFLOW_GUIDE v1.2)
**Created:** 2026-02-26  
**Purpose:** Core workflow patterns, 15-step process, Master Chat responsibilities  
**Audience:** Master Chat (primary), Worker Chats (reference)

---

## 📋 WORKFLOW DOCUMENTATION SUITE

This is **Part 1 of 3** in the workflow documentation:

1. **WORKFLOW_CORE.md** (this file) - Overview, 15-step process, Master responsibilities
2. **WORKFLOW_EXECUTION.md** - Worker lifecycle, handoff process, review checklist
3. **WORKFLOW_TROUBLESHOOTING.md** - Escalation triggers, debugging, problem resolution

**Related documents:**
- **CHAT_WORKING_RULES.md** - Mandatory rules for all chats (v2.0)
- **WORKFLOW_TEMPLATES.md** - Brief and handoff templates

---

## 📋 TABLE OF CONTENTS

1. [Overview](#overview)
2. [The 15-Step Worker Chat Workflow](#the-15-step-worker-chat-workflow)
3. [Master Chat Responsibilities](#master-chat-responsibilities)

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

## 🔄 THE 15-STEP WORKER CHAT WORKFLOW

This is the MANDATORY workflow for every worker chat. No steps may be skipped.

---

### STEP 1 — Master writes brief
Master Chat produces a comprehensive CHAT_XX_BRIEF.md covering:
- Objective and context
- Full list of deliverables (files to create/modify with full Windows paths)
- Technical constraints and critical rules
- Success criteria checklist
- Estimated time
- Handoff requirements

---

### STEP 2 — Uploads to worker chat
The following are ALL uploaded to the new worker chat before any work begins:
- `CHAT_XX_BRIEF.md` — the task brief
- `PROJECT_ROADMAP.md`
- `CHAT_WORKING_RULES.md`
- `MASTER_KNOWLEDGE_BASE.md`
- `DASHBOARD_PROJECT_PLAN.md`
- Codebase as a ZIP (`C:\Users\User\Desktop\gads-data-layer`)

---

### STEP 3 — Worker reads and produces 5 questions
Worker Chat reads ALL uploaded documents and the brief thoroughly.
Worker identifies gaps, ambiguities, or risks and produces exactly **5 clarifying questions**.
These questions must be specific and answerable — not vague.

---

### STEP 4 — Worker STOPS and sends 5 questions to Master
Worker Chat stops work completely and sends the 5 questions to Master Chat.
Worker does NOT proceed until answers are received.

---

### STEP 5 — Master answers 5 questions
Master Chat reviews the 5 questions and provides clear, direct answers.
Answers are sent back to Worker Chat.

---

### STEP 6 — Worker creates detailed build plan
Worker Chat uses the brief + answers to produce a detailed, step-by-step build plan.
The build plan must specify:
- Every file to be created or edited (full Windows path)
- The order of operations
- How each deliverable satisfies the brief
- Any risks or dependencies called out

---

### STEP 7 — Build plan sent to Master for review
Worker sends the detailed build plan to Master Chat.
Worker does NOT start coding until Master approves.

---

### STEP 8 — Master approves build plan → Worker starts work
Master reviews the build plan. If approved, Worker begins implementation.
If not approved, Master provides feedback and Worker revises.

---

### STEP 9 — Implementation: 1 step at a time, 1 file at a time
Worker implements the build plan one step at a time, one file at a time.

**Rules during implementation:**
- Before editing ANY existing file → Worker asks Christopher to upload the current version
- Worker edits the file and returns the COMPLETE file (never snippets)
- Every file delivered includes its FULL Windows path
- If the step can be tested → Worker provides fresh PowerShell commands
- Worker waits for confirmation before moving to next step

---

### STEP 10 — Worker creates detailed completion summary
Once all work is done and tested, Worker creates a detailed summary covering:
- Every file created or modified (full paths)
- What was built and how it works
- Test results
- Any known issues or deviations from the brief

---

### STEP 11 — Detailed summary sent to Master for review
Worker sends the detailed summary to Master Chat.
Master reviews against the brief and success criteria.

---

### STEP 12 — If approved: Worker creates handoff documents
Master approves summary → Worker creates two documents:
- `CHAT_XX_HANDOFF.md` — comprehensive technical record
- `CHAT_XX_SUMMARY.md` — context for the next worker chat

Both saved to: `C:\Users\User\Desktop\gads-data-layer\docs\`

---

### STEP 13 — Handoff docs sent to Master for approval
Worker sends both handoff documents to Master Chat for review.
Master checks they are complete, accurate, and useful for future chats.

---

### STEP 14 — Master updates project documentation
Master Chat updates ALL 4 project docs to reflect completed work:
- `CHAT_WORKING_RULES.md` — any new lessons or pitfalls
- `DASHBOARD_PROJECT_PLAN.md` — module/chat status updated
- `MASTER_KNOWLEDGE_BASE.md` — architecture, lessons, current state
- `PROJECT_ROADMAP.md` — progress, changelog, next steps

---

### STEP 15 — Git commit
Master instructs Christopher to commit and push.

**Commit message format:**
```
[type]: [brief description]

[Detailed description]

Files changed:
- file1.ext
- file2.ext

Testing: [test results]
Time: [actual vs estimated]
Chat: [number]
```

Christopher runs:
```powershell
cd C:\Users\User\Desktop\gads-data-layer
git add .
git status
git commit -m "[message]"
git push origin main
```

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
- Maintains this WORKFLOW_CORE.md
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

**Version:** 2.0 | **Last Updated:** 2026-02-26
**Next:** See WORKFLOW_EXECUTION.md for worker lifecycle and handoff process
