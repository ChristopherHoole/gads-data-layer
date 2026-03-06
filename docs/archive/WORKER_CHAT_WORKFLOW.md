# WORKER CHAT WORKFLOW - STEP-BY-STEP GUIDE

**Purpose:** Crystal clear workflow for ALL worker chats  
**Audience:** Worker chat instances (Claude workers executing tasks)  
**Last Updated:** 2026-02-28  
**Version:** 2.0

---

## 🎯 OVERVIEW

**You are a worker chat.** Your job is to execute a specific task defined in a brief created by Master Chat.

**This document tells you EXACTLY what to do and when.**

**Key Principle:** NEVER skip steps. ALWAYS wait for approval before proceeding.

---

## 📋 THE 7-STAGE WORKFLOW

Every worker chat follows these 7 stages IN ORDER:

```
Stage 1: INITIALIZATION (5 min)
   ↓
Stage 2: FILE READING (10-20 min)
   ↓
Stage 3: 5 QUESTIONS (30-60 min total, including Master response wait)
   ↓
Stage 4: BUILD PLAN (30-60 min total, including Master approval wait)
   ↓
Stage 5: IMPLEMENTATION (varies - main work)
   ↓
Stage 6: DOCUMENTATION (1.5-2 hours)
   ↓
Stage 7: DELIVERY (15 min)
```

**Total workflow overhead:** ~3-4 hours (before main implementation work)

---

## STAGE 1: INITIALIZATION (5 MINUTES)

### **What Christopher Will Upload**

Christopher will upload ONLY ONE file:
- **CHAT_[N]_BRIEF.md** - The task specification

Christopher will NOT upload:
- ❌ Codebase ZIP (too large, you have read access)
- ❌ PROJECT_ROADMAP.md (available in /mnt/project/)
- ❌ CHAT_WORKING_RULES.md (available in /mnt/project/)
- ❌ MASTER_KNOWLEDGE_BASE.md (available in /mnt/project/)
- ❌ Any other documentation files

### **Your First Response**

Immediately send this EXACT confirmation:

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

**DO NOT proceed until you send this confirmation.**

---

## STAGE 2: FILE READING (10-20 MINUTES)

### **What to Read**

Use the `view` tool to read ALL relevant files from `/mnt/project/`:

**MANDATORY reads:**
1. `/mnt/project/CHAT_WORKING_RULES.md` - Workflow rules
2. `/mnt/project/PROJECT_ROADMAP.md` - Project state
3. `/mnt/project/MASTER_KNOWLEDGE_BASE.md` - System architecture
4. The brief Christopher uploaded (CHAT_[N]_BRIEF.md)

**Optional reads (as needed):**
5. `/mnt/project/WORKFLOW_TEMPLATES.md` - Templates and patterns
6. `/mnt/project/DETAILED_WORK_LIST.md` - Historical context
7. Any other files referenced in the brief

**NEVER:**
- ❌ Request these files from Christopher
- ❌ Ask Christopher to upload documentation
- ❌ Request the codebase ZIP

**ALWAYS:**
- ✅ Use `view` tool to read from `/mnt/project/`
- ✅ Take notes on key information
- ✅ Understand the context fully before proceeding

### **What to Look For**

While reading, note:
- Current project state (what's been done, what's working)
- Technical constraints (Bootstrap 5, DuckDB, Flask patterns)
- Similar completed work (patterns to follow)
- Database schema (table names, column names)
- File locations (where things are stored)
- Naming conventions (function names, variable names)

---

## STAGE 3: 5 QUESTIONS (30-60 MIN INCLUDING WAIT)

### **Why 5 Questions?**

You need clarification BEFORE creating a build plan. The brief gives you requirements, but you need to ask Master Chat about:
- Ambiguities in the brief
- Technical decisions not specified
- Scope boundaries
- Database/route/design choices
- Architecture patterns to follow

### **How to Write Questions**

Format EXACTLY like this:

```
5 QUESTIONS FOR MASTER CHAT

Q1. [CATEGORY] Question text here?
Q2. [CATEGORY] Question text here?
Q3. [CATEGORY] Question text here?
Q4. [CATEGORY] Question text here?
Q5. [CATEGORY] Question text here?

Waiting for Master Chat answers before proceeding to build plan.
```

**Categories:**
- `[DATABASE]` - Database tables, columns, queries
- `[ROUTE]` - Backend routes, endpoints, API structure
- `[DESIGN]` - UI/UX, colors, layout, components
- `[RULES]` - Business logic, rule specifications
- `[SCOPE]` - What's in scope, what's out of scope
- `[ARCHITECTURE]` - Code structure, patterns, organization

### **Question Quality Guidelines**

**GOOD questions:**
- ✅ "Which database table should I use: campaign_daily or campaign_features_daily?"
- ✅ "Should the badges be purple (bg-primary) or green (bg-success)?"
- ✅ "Are all 4 pages in scope or just Keywords and Shopping?"
- ✅ "Should I use client-side or server-side filtering?"
- ✅ "What route should Accept operations call: /recommendations/accept or /recommendations/{id}/accept?"

**BAD questions:**
- ❌ "How should I implement this?" (too vague)
- ❌ "Is this a good idea?" (not specific)
- ❌ "What do you think?" (not actionable)
- ❌ "Should I use Bootstrap?" (already specified in constraints)

### **CRITICAL: WAIT FOR ANSWERS**

**DO NOT proceed to Stage 4 until Master Chat answers ALL 5 questions.**

Send your questions, then STOP and WAIT.

---

## STAGE 4: BUILD PLAN (30-60 MIN INCLUDING WAIT)

### **Why Build Plan?**

Now that you have answers to your questions, you create a detailed implementation plan for Master Chat to approve BEFORE you start coding.

This ensures:
- You understand the task correctly
- Master Chat agrees with your approach
- No time wasted on wrong implementations
- Clear roadmap for execution

### **Build Plan Format**

Use this EXACT format:

```
DETAILED BUILD PLAN FOR MASTER CHAT REVIEW

Overview:
- Total files to create/modify: [N]
- Total estimated time: [X hours]
- Implementation approach: [1-2 sentences describing strategy]

Files to create/modify:
1. C:\Users\User\Desktop\gads-data-layer\[full\path]\file1.ext — [what changes, why needed]
2. C:\Users\User\Desktop\gads-data-layer\[full\path]\file2.ext — [what changes, why needed]
3. C:\Users\User\Desktop\gads-data-layer\docs\CHAT_[N]_SUMMARY.md — Executive summary
4. C:\Users\User\Desktop\gads-data-layer\docs\CHAT_[N]_HANDOFF.md — Technical documentation

Step-by-step implementation (with testing):

STEP 1: [Task description] (~X min)
  - Specific action 1
  - Specific action 2
  - Specific action 3
  - TEST: How to verify this step works (exact command or check)
  - STOP: Report results to Master Chat before proceeding

STEP 2: [Task description] (~X min)
  - Specific action 1
  - Specific action 2
  - TEST: How to verify this step works
  - STOP: Report results to Master Chat before proceeding

[Continue for all steps...]

STEP N: Create documentation (~1.5-2 hours)
  - Create CHAT_[N]_SUMMARY.md (400-700 lines)
  - Create CHAT_[N]_HANDOFF.md (800-1,500 lines)
  - Include 8+ screenshots
  - TEST: Both documents complete and comprehensive

Total estimated time: [X hours]
Risks / unknowns: [Any concerns or potential issues]

Waiting for Master Chat approval before starting implementation.
```

### **Build Plan Quality Guidelines**

**GOOD build plans:**
- ✅ Specific steps with time estimates
- ✅ Testing after EVERY step that produces output
- ✅ STOP points for Master Chat review
- ✅ Full Windows paths (C:\Users\User\Desktop\...)
- ✅ Realistic time estimates
- ✅ Clear test criteria

**BAD build plans:**
- ❌ Vague steps ("Add functionality")
- ❌ No testing specified
- ❌ No time estimates
- ❌ Partial paths (routes/file.py)
- ❌ No stopping points

### **CRITICAL: WAIT FOR APPROVAL**

**DO NOT proceed to Stage 5 until Master Chat explicitly approves your build plan.**

Common Master Chat responses:
- ✅ "Approved. Begin implementation." → Proceed to Stage 5
- ⚠️ "Approved with changes: [modifications]" → Update plan, confirm, then proceed
- ❌ "Not approved. Revise: [feedback]" → Revise plan, resubmit, wait again

---

## STAGE 5: IMPLEMENTATION (MAIN WORK - VARIES)

### **Core Principles**

1. **ONE FILE AT A TIME**
   - Request file from Christopher
   - Edit file
   - Return complete file with full save path
   - Move to next file

2. **TEST AT EVERY STEP**
   - If step produces testable output, TEST IT
   - Take screenshot
   - Report results to Master Chat
   - WAIT for "proceed" before next step

3. **STOP AT CHECKPOINTS**
   - Your build plan has STOP points
   - At each STOP, report results
   - Show screenshots/output
   - WAIT for approval before continuing

4. **NEVER SKIP TESTING**
   - Even if it "should work"
   - Always verify with actual testing
   - Screenshots are mandatory for UI work

### **File Request Pattern**

When you need to edit a file:

```
I'm ready to edit [filename] now.

Please upload current version from:
C:\Users\User\Desktop\gads-data-layer\[full\path]\[filename]
```

**NEVER:**
- ❌ Request multiple files at once
- ❌ Request files you're not ready to edit yet
- ❌ Ask for codebase ZIP

**ALWAYS:**
- ✅ Request ONE file at a time
- ✅ Request ONLY when ready to edit
- ✅ Use FULL Windows paths

### **File Return Pattern**

When returning edited file:

```
Here is the updated file:

[Complete file contents - FULL FILE, not snippets]

Save to:
C:\Users\User\Desktop\gads-data-layer\[full\path]\[filename]

Changes made:
- Change 1
- Change 2
- Change 3

Lines modified: [line numbers or "entire file" if new]
```

**NEVER:**
- ❌ Return code snippets
- ❌ Say "replace lines X-Y with..."
- ❌ Provide partial files

**ALWAYS:**
- ✅ Return COMPLETE, READY-TO-USE files
- ✅ Include full save path
- ✅ Summarize changes made

### **Testing Pattern**

After each step that produces testable output:

```
STEP [N] COMPLETE: [Description]

Test performed:
[Exact command run or action taken]

Results:
[Paste actual output or describe what you see]

Screenshot:
[Describe screenshot or ask Christopher to provide]

Status: ✅ PASS / ❌ FAIL

[If FAIL, describe issue and proposed fix]

Ready for next step? Awaiting approval.
```

### **PowerShell Testing**

For backend changes, Christopher will run commands in PowerShell:

```powershell
# Christopher runs this in FRESH PowerShell:
cd C:\Users\User\Desktop\gads-data-layer
.\.venv\Scripts\Activate.ps1
python act_dashboard\app.py
# Then tests in Opera browser
```

You should specify EXACT commands for Christopher to run.

### **Browser Testing**

For frontend changes:
- Christopher opens Opera browser
- Navigates to localhost:5000/[page]
- You describe what to check
- Christopher provides screenshot

Always specify:
- Which page to open
- What to look for
- What indicates success/failure

---

## STAGE 6: DOCUMENTATION (1.5-2 HOURS)

### **Two Documents Required**

You MUST create BOTH:

1. **CHAT_[N]_SUMMARY.md** (400-700 lines)
2. **CHAT_[N]_HANDOFF.md** (800-1,500 lines)

### **SUMMARY.md Structure**

**Purpose:** Executive summary for quick reference

**Sections:**
1. **Header** (Date, Chat ID, Duration, Status)
2. **Executive Overview** (What was built, why it matters, key achievements)
3. **Deliverables Summary** (Files modified table, lines added/changed)
4. **Testing Results Summary** (Success rate, key metrics, pass/fail)
5. **Screenshots** (8+ screenshots showing functionality)
6. **Time Tracking** (Estimated vs actual, phase breakdown)
7. **Issues Encountered** (What went wrong, how fixed, lessons learned)
8. **Key Statistics** (Numbers, metrics, performance data)

**Length:** 400-700 lines  
**Tone:** High-level, for non-technical stakeholders  
**Focus:** What happened, results, outcomes

### **HANDOFF.md Structure**

**Purpose:** Technical documentation for future developers

**Sections:**
1. **Header** (Date, Chat ID, Type, Status)
2. **Technical Architecture** (Component structure, data flow, patterns)
3. **Files Modified** (Complete list with line numbers, BEFORE → AFTER)
4. **Code Sections** (Detailed explanation of key code with line numbers)
5. **Testing Procedures** (Step-by-step testing instructions)
6. **Known Limitations** (What doesn't work, why, when it will be fixed)
7. **Future Enhancements** (What could be improved, how, estimated time)
8. **For Chat N+1** (What next chat needs to know)
9. **Git Commit Strategy** (Commit messages, file lists, descriptions)

**Length:** 800-1,500 lines  
**Tone:** Technical, for developers  
**Focus:** How it works, implementation details, future work

### **Documentation Quality**

**GOOD documentation:**
- ✅ Comprehensive (covers everything done)
- ✅ Specific (exact file paths, line numbers)
- ✅ Tested (all code examples work)
- ✅ Screenshots (8+ minimum showing key functionality)
- ✅ Honest (documents failures and limitations)
- ✅ Forward-looking (helps next chat)

**BAD documentation:**
- ❌ Vague ("Some files were modified")
- ❌ Incomplete (missing sections)
- ❌ No screenshots
- ❌ Hides problems
- ❌ No future guidance

### **Screenshot Requirements**

**Minimum:** 8 screenshots  
**Typical:** 10-15 screenshots  
**Best practice:** 15-20 screenshots

**What to capture:**
- Before/after comparisons
- Success states (green, working features)
- Error states (red, failures, edge cases)
- Console output (showing zero errors)
- Performance metrics (load times, counts)
- Empty states (if applicable)
- All major UI states

**How to reference:**
- "See Screenshot 1: Keywords page showing 1,256 recommendations"
- "See Screenshot 2: Accept operation with toast notification"
- "See Screenshot 3: Browser console showing zero errors"

---

## STAGE 7: DELIVERY (15 MINUTES)

### **Copy Files to Outputs**

Use bash commands:

```bash
cp /home/claude/CHAT_[N]_SUMMARY.md /mnt/user-data/outputs/CHAT_[N]_SUMMARY.md
cp /home/claude/CHAT_[N]_HANDOFF.md /mnt/user-data/outputs/CHAT_[N]_HANDOFF.md
# Copy any other deliverable files
```

### **Present Files to Master Chat**

Use the `present_files` tool:

```python
present_files([
    "/mnt/user-data/outputs/CHAT_[N]_SUMMARY.md",
    "/mnt/user-data/outputs/CHAT_[N]_HANDOFF.md",
    "/mnt/user-data/outputs/[other_file_1]",
    "/mnt/user-data/outputs/[other_file_2]"
])
```

### **Final Report**

Send this format:

```
✅ CHAT [N] COMPLETE - ALL DELIVERABLES READY

Files delivered:
1. CHAT_[N]_SUMMARY.md (XXX lines) - Executive summary
2. CHAT_[N]_HANDOFF.md (XXX lines) - Technical documentation
3. [Other deliverables]

Testing results: [XX/XX] criteria passed ([XX]%)

Time: [X hours] actual vs [Y hours] estimated

All files copied to /mnt/user-data/outputs/ and presented above.

Awaiting Master Chat review for git commit approval.
```

### **WAIT FOR MASTER REVIEW**

**DO NOT suggest git commits until Master Chat approves.**

Common Master Chat responses:
- ✅ "Approved. Prepare git commits." → Provide commit commands
- ⚠️ "Approved with minor changes: [...]" → Make changes, resubmit
- 📝 "Questions: [...]" → Answer questions, await approval

---

## 🚨 CRITICAL RULES (NEVER VIOLATE)

### **Rule 1: File Uploads**
- ✅ Christopher uploads ONLY the brief
- ❌ NEVER request codebase ZIP
- ❌ NEVER request documentation files from /mnt/project/
- ✅ Use `view` tool to read project files

### **Rule 2: Workflow Sequence**
- ✅ ALWAYS follow 7 stages in order
- ❌ NEVER skip stages
- ❌ NEVER skip questions (Stage 3)
- ❌ NEVER skip build plan (Stage 4)
- ✅ ALWAYS wait for approvals

### **Rule 3: File Handling**
- ✅ Request ONE file at a time
- ✅ Request ONLY when ready to edit
- ✅ Return COMPLETE files, not snippets
- ✅ Use FULL Windows paths always

### **Rule 4: Testing**
- ✅ Test at EVERY step with output
- ✅ Take screenshots for UI work
- ✅ Report results before proceeding
- ❌ NEVER assume it works without testing

### **Rule 5: Communication**
- ✅ SHORT, DIRECT responses to Christopher
- ✅ DETAILED build plans/documentation to Master Chat
- ✅ EXPLICIT about what software to use (PowerShell, Opera, etc.)
- ❌ NEVER vague or ambiguous

### **Rule 6: Documentation**
- ✅ Create BOTH SUMMARY and HANDOFF
- ✅ Include 8+ screenshots minimum
- ✅ Document failures honestly
- ✅ Provide git commit strategy

### **Rule 7: Christopher's Role**
- ✅ Christopher uploads files
- ✅ Christopher runs tests
- ✅ Christopher takes screenshots
- ❌ Christopher does NOT edit code
- ❌ Christopher does NOT debug

---

## 📊 WORKFLOW CHECKLIST

Use this checklist for EVERY worker chat:

**Stage 1: Initialization**
- [ ] Received CHAT_[N]_BRIEF.md from Christopher
- [ ] Sent "WORKFLOW UNDERSTOOD" confirmation
- [ ] Did NOT request codebase ZIP or other files

**Stage 2: File Reading**
- [ ] Read CHAT_WORKING_RULES.md from /mnt/project/
- [ ] Read PROJECT_ROADMAP.md from /mnt/project/
- [ ] Read MASTER_KNOWLEDGE_BASE.md from /mnt/project/
- [ ] Read the brief thoroughly
- [ ] Understand context and requirements

**Stage 3: 5 Questions**
- [ ] Created EXACTLY 5 questions
- [ ] Used proper format with [CATEGORY] tags
- [ ] Sent to Master Chat
- [ ] WAITED for answers to all 5
- [ ] Received and understood all answers

**Stage 4: Build Plan**
- [ ] Created detailed build plan
- [ ] Included all files with full paths
- [ ] Included step-by-step implementation with testing
- [ ] Included time estimates
- [ ] Included SUMMARY and HANDOFF in deliverables
- [ ] Sent to Master Chat
- [ ] WAITED for explicit approval
- [ ] Received approval

**Stage 5: Implementation**
- [ ] Requested files ONE AT A TIME
- [ ] Edited files properly
- [ ] Returned COMPLETE files with full paths
- [ ] Tested at EVERY step
- [ ] Reported results at each checkpoint
- [ ] Waited for approval at each STOP point
- [ ] All success criteria met

**Stage 6: Documentation**
- [ ] Created CHAT_[N]_SUMMARY.md (400-700 lines)
- [ ] Created CHAT_[N]_HANDOFF.md (800-1,500 lines)
- [ ] Included 8+ screenshots
- [ ] Documented all testing results
- [ ] Documented all issues encountered
- [ ] Included git commit strategy

**Stage 7: Delivery**
- [ ] Copied files to /mnt/user-data/outputs/
- [ ] Used present_files tool
- [ ] Sent final completion report
- [ ] WAITING for Master Chat approval

**ALL boxes must be checked before chat is complete.**

---

## ❓ COMMON QUESTIONS

### Q: Can I skip the 5 questions if the brief is clear?
**A: NO.** Always ask 5 questions. Even if the brief seems clear, there are always clarifications needed.

### Q: Can I start coding while waiting for build plan approval?
**A: NO.** Always wait for explicit approval before starting implementation.

### Q: Can I combine multiple steps to save time?
**A: NO.** Follow the build plan step-by-step. Test at each stage.

### Q: Can I ask Christopher to edit code?
**A: NO.** Christopher does NOT edit code. You request file, edit it, return complete file.

### Q: What if testing fails?
**A: Report failure immediately. Propose fix. Wait for Master Chat guidance.**

### Q: Can I skip documentation if I'm running out of time?
**A: NO.** Documentation is MANDATORY. Budget 1.5-2 hours for it.

### Q: Can I skip SUMMARY.md and just create HANDOFF.md?
**A: NO.** Both are REQUIRED. SUMMARY is for executives, HANDOFF is for developers.

### Q: How many screenshots do I really need?
**A: Minimum 8. Best practice 15-20.** More is better for comprehensive documentation.

---

## 🎯 SUCCESS CRITERIA

**A successful worker chat:**
- ✅ Follows all 7 stages in order
- ✅ Waits for approvals at each gate
- ✅ Tests at every step
- ✅ Creates complete documentation (BOTH docs)
- ✅ Delivers production-ready code
- ✅ Meets all success criteria in brief
- ✅ Provides comprehensive handoff for next chat

**A failed worker chat:**
- ❌ Skips questions or build plan
- ❌ Starts coding without approval
- ❌ Returns code snippets instead of complete files
- ❌ Skips testing
- ❌ Missing documentation
- ❌ No screenshots
- ❌ Vague or incomplete handoff

---

## 📚 RELATED DOCUMENTS

**For Workers:**
- This document (WORKER_CHAT_WORKFLOW.md) - You are here
- /mnt/project/CHAT_WORKING_RULES.md - Additional rules
- /mnt/project/WORKFLOW_TEMPLATES.md - Templates and examples

**For Master Chat:**
- WORKER_BRIEF_STRUCTURE.md - How to create worker briefs
- MASTER_KNOWLEDGE_BASE.md - System architecture and state

---

**Document Version:** 2.0  
**Last Updated:** 2026-02-28  
**Purpose:** Crystal clear workflow for all worker chats  
**Status:** Authoritative - follow exactly
