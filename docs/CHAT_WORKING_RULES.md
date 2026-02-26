# CHAT WORKING RULES - MANDATORY FOR ALL CHATS

**Version:** 2.0
**Last Updated:** 2026-02-26
**Applies to:** All Claude chats working on this project

---

## 🚨 CRITICAL: READ THIS FIRST

These rules are MANDATORY and NON-NEGOTIABLE. Violating these rules causes:
- ❌ Wasted time debugging wrong versions of files
- ❌ Edits to outdated code
- ❌ Circular debugging loops
- ❌ Technical debt accumulation
- ❌ User frustration

**Master Chat will review EVERY action to ensure compliance.**

---

## 📋 RULE 1: READ FROM PROJECT FILES - NO UPLOADS NEEDED

### 🚨 CRITICAL: NO FILE UPLOADS BY USER

**Christopher will ONLY upload the task brief (CHAT_[N]_BRIEF.md). Everything else is already available in the Claude Project system.**

### **The Rule:**

**YOU HAVE ACCESS TO ALL PROJECT FILES via `/mnt/project/` directory.**

**DO NOT REQUEST:**
- ❌ Codebase ZIP (too large, not needed)
- ❌ PROJECT_ROADMAP.md (already in `/mnt/project/`)
- ❌ CHAT_WORKING_RULES.md (already in `/mnt/project/`)
- ❌ MASTER_KNOWLEDGE_BASE.md (already in `/mnt/project/`)
- ❌ DASHBOARD_PROJECT_PLAN.md (already in `/mnt/project/`)
- ❌ WORKFLOW_GUIDE.md (already in `/mnt/project/`)
- ❌ WORKFLOW_TEMPLATES.md (already in `/mnt/project/`)
- ❌ Any other documentation files

### **What YOU WILL Receive:**

Christopher will upload ONLY:
1. **CHAT_[N]_BRIEF.md** - Your task instructions

That's it. ONE file.

### **What YOU MUST Do:**

**STEP 1: Confirm you understand the workflow**
```
✅ WORKFLOW UNDERSTOOD

I confirm:
1. Christopher will ONLY upload the brief (CHAT_[N]_BRIEF.md)
2. I will read ALL project files from /mnt/project/ using view tool
3. I will NOT request codebase ZIP (too large)
4. I will NOT request any documentation files (already available)
5. I will send 5 QUESTIONS to Master Chat and WAIT for answers
6. I will create DETAILED BUILD PLAN and WAIT for Master approval
7. I will implement step-by-step, testing at each stage
8. I will work ONE FILE AT A TIME
9. Christopher does NOT edit code - I request file, he uploads, I edit, I return complete file with full save path

Ready to begin.
```

**STEP 2: Read all project files using `view` tool**

Use the `view` tool to read these files from `/mnt/project/`:
1. `/mnt/project/MASTER_CHAT_5_0_HANDOFF.md` (if exists)
2. `/mnt/project/PROJECT_ROADMAP.md`
3. `/mnt/project/CHAT_WORKING_RULES.md` (this file)
4. `/mnt/project/MASTER_KNOWLEDGE_BASE.md`
5. `/mnt/project/DASHBOARD_PROJECT_PLAN.md`
6. `/mnt/project/WORKFLOW_GUIDE.md`
7. `/mnt/project/WORKFLOW_TEMPLATES.md`
8. `/mnt/project/DETAILED_WORK_LIST.md` (if relevant)

**STEP 3: Read the brief thoroughly**

Study CHAT_[N]_BRIEF.md - understand objective, requirements, success criteria.

**STEP 4: Proceed to Rule 5 (5 Questions)**

Write 5 clarifying questions for Master Chat.

---

## 📋 RULE 2: FILE HANDLING - CHRISTOPHER DOESN'T EDIT CODE

### **The Rule:**
**BEFORE analyzing or editing ANY file, you MUST request the current version from Christopher.**

**Christopher does NOT edit code. Here's how it works:**

1. **Worker:** "I need to edit `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\campaigns.py`"
2. **Worker:** "Please upload the current version"
3. **Christopher:** [uploads campaigns.py]
4. **Worker:** [analyzes, makes edits, returns COMPLETE file]
5. **Worker:** "Save this complete file to: `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\campaigns.py`"
6. **Christopher:** [saves file, confirms]

**Christopher's role:** Upload files when requested, save files when provided
**Worker's role:** Request files, edit files, return complete files with full save paths

### **NEVER Say:**
- ❌ "I already have this file from earlier"
- ❌ "I'll use the version from the ZIP"  
- ❌ "Based on my previous upload..."
- ❌ "Can you make this edit for me?" (Christopher doesn't edit)

### **ALWAYS Say:**
```
I need the current version to ensure accurate editing.

Please upload:
- File: [filename]
- Location: C:\Users\User\Desktop\gads-data-layer\[path]\[filename]

After upload, I will:
1. Analyze current state
2. Make the edits
3. Return COMPLETE file with full save path

Upload now.
```

### **Why This Rule Exists:**
- Christopher may have manually edited since last upload
- Christopher may have reverted changes
- Other processes may have modified files
- Your memory may be wrong
- **Christopher doesn't edit code** - you do all editing

### **Enforcement:**
If you catch yourself about to edit a file, ask:
1. "Do I have the CURRENT version uploaded in the last 2 messages?"
2. If NO → Request upload FIRST
3. If YES → Proceed with edit, return COMPLETE file

**Master Chat will intervene if you violate this.**

---

## 📋 RULE 3: FILE PATHS - ALWAYS USE FULL PATHS

### **The Rule:**
**NEVER use partial file paths. ALWAYS use complete Windows paths.**

### **WRONG:**
- ❌ "Edit routes.py"
- ❌ "Upload keyword_rules.py"
- ❌ "The file is in act_dashboard/"

### **CORRECT:**
- ✅ "Edit `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes.py`"
- ✅ "Upload `C:\Users\User\Desktop\gads-data-layer\act_autopilot\rules\keyword_rules.py`"
- ✅ "The file is in `C:\Users\User\Desktop\gads-data-layer\act_dashboard\`"

### **Format:**
```
C:\Users\User\Desktop\gads-data-layer\[folder]\[subfolder]\[filename]
```

**Use this format in EVERY file reference.**

---

## 📋 RULE 4: WORKFLOW - ONE STEP AT A TIME, ONE FILE AT A TIME

### **The Rule:**
**Complete each step FULLY before proceeding to the next. Work on ONE FILE AT A TIME. Test immediately if possible. Wait for Christopher's confirmation.**

### **NEVER:**
- ❌ Combine multiple steps in one response
- ❌ Edit multiple files simultaneously
- ❌ Proceed without Christopher's confirmation
- ❌ Make assumptions about what Christopher wants next
- ❌ Skip testing if the step is testable

### **ALWAYS:**
```
STEP 1 COMPLETE: [What was done]
- File edited: [filename]
- Changes: [brief summary]
- Testing: [if testable, provide test results]

Next: STEP 2: [What will be done]
- File to edit: [filename]
- Expected outcome: [what this achieves]

Reply "Proceed" to continue, or give different instructions.

[STOP - Wait for confirmation]
```

### **Testing at Every Step:**
If a step produces testable output (e.g., Flask starts, template validates, function works), test it IMMEDIATELY:

**Example (Jinja template):**
```
STEP 3 COMPLETE: Created keywords_rules_tab.html

Testing now:
python -c "from jinja2 import Environment, FileSystemLoader; env = Environment(loader=FileSystemLoader('act_dashboard/templates/components')); env.get_template('keywords_rules_tab.html'); print('Jinja OK')"

Result: ✅ Template validates successfully

Next: STEP 4: Update keywords_new.html to include new component
```

**Example (Flask startup):**
```
STEP 5 COMPLETE: Updated routes/keywords.py

Testing now:
python -m act_dashboard.app

Result: ✅ Flask starts, no errors, keywords page loads

Next: STEP 6: Test keyword rules tab display
```

**ONE FILE AT A TIME means:**
- Edit campaigns.py → test → confirm → THEN edit campaigns.html
- NOT: Edit campaigns.py + campaigns.html + __init__.py all at once

**Christopher will confirm after EACH step before you proceed.**

---

## 📋 RULE 5: 5 QUESTIONS + BUILD PLAN - BOTH MANDATORY BEFORE ANY CODE

### **🚨 CRITICAL: TWO-STAGE APPROVAL PROCESS**

**After reading all docs — BEFORE writing ANY code — you MUST complete BOTH stages:**

**STAGE 1:** Send 5 QUESTIONS to Master Chat → WAIT for answers
**STAGE 2:** Send DETAILED BUILD PLAN to Master Chat → WAIT for approval

**ONLY AFTER BOTH APPROVALS can you begin implementation.**

### **The Full Process:**
```
STEP 1:  Worker reads brief + all 8 project files from /mnt/project/
STEP 2:  Worker writes EXACTLY 5 questions (no more, no less)
STEP 3:  Worker sends questions with header "5 QUESTIONS FOR MASTER CHAT"
STEP 4:  Worker STOPS — waits for answers
STEP 5:  Christopher copies questions → pastes in Master Chat
STEP 6:  Master provides answers
STEP 7:  Christopher pastes answers back into worker chat
STEP 8:  Worker creates DETAILED BUILD PLAN (step-by-step, all files, all changes)
STEP 9:  Worker sends plan with header "DETAILED BUILD PLAN FOR MASTER CHAT REVIEW"
STEP 10: Worker STOPS — waits for Master approval
STEP 11: Christopher copies build plan → pastes in Master Chat
STEP 12: Master Chat reviews build plan and provides feedback/approval
STEP 13: Christopher pastes feedback/approval back into worker chat
STEP 14: Worker begins implementation (ONLY if Master approved)
```

### **5 Questions Format:**
```
5 QUESTIONS FOR MASTER CHAT

Before building, I need clarification on these 5 critical points:

Q1. [CATEGORY] Question text here?
Q2. [CATEGORY] Question text here?
Q3. [CATEGORY] Question text here?
Q4. [CATEGORY] Question text here?
Q5. [CATEGORY] Question text here?

Waiting for Master Chat answers before proceeding to build plan.
```

### **Question Categories:**
- `[DATABASE]` — schema, column names, table existence, query structure
- `[ROUTE]` — existing code, overwrite vs. extend, route patterns
- `[DESIGN]` — UI decisions not clear from brief, layout, styling
- `[RULES]` — rules engine specifics, Constitution compliance
- `[SCOPE]` — what's in vs. out of this chat, priorities
- `[ARCHITECTURE]` — component structure, patterns to follow

### **Build Plan Format:**
```
DETAILED BUILD PLAN FOR MASTER CHAT REVIEW

Overview:
- Total files to create/modify: [N]
- Total estimated time: [X hours]
- Implementation approach: [1-2 sentences]

Files to create/modify:
1. [Full path] — [what changes, why needed]
2. [Full path] — [what changes, why needed]
3. [Full path] — [what changes, why needed]

Step-by-step implementation (with testing):
STEP 1: [Task description] (~X min)
  - [Specific action 1]
  - [Specific action 2]
  - TEST: [How to verify this step works]
  
STEP 2: [Task description] (~X min)
  - [Specific action 1]
  - [Specific action 2]
  - TEST: [How to verify this step works]

STEP 3: Final Testing (~X min)
  - [Test scenario 1]
  - [Test scenario 2]
  - [Success criteria verification]

Total estimated time: X hours
Risks / unknowns: [Any remaining concerns]

Waiting for Master Chat approval before starting implementation.
```

### **NEVER:**
- ❌ Ask questions answerable by reading the brief or project files
- ❌ Ask generic or vague questions ("How should I approach this?")
- ❌ Ask more or fewer than 5 questions (EXACTLY 5)
- ❌ Skip the build plan stage (Master must approve your plan)
- ❌ Begin implementation without Master Chat explicit approval
- ❌ Combine 5 questions + build plan in one message (separate stages)

### **Master Chat Confirmation Required:**

After you send build plan, Master Chat will respond with:
- ✅ "BUILD PLAN APPROVED - Proceed to implementation"
- ⚠️ "BUILD PLAN NEEDS CHANGES - [specific feedback]"
- ❌ "BUILD PLAN REJECTED - [reason + new approach needed]"

**You MUST wait for explicit approval before writing ANY code.**

---

## 📋 RULE 6: SHOW YOUR WORK

**Document findings, explain reasoning, show comparisons BEFORE making changes.**

---

## 📋 RULE 7: TESTING - VERIFY BEFORE REPORTING COMPLETE

**After EVERY code change — mandatory test workflow:**

1. Specify exact test steps with PowerShell commands
2. Define success criteria before testing
3. Report actual results — never "it should work"
4. If tests fail: stop, debug, fix, retest before proceeding

**Jinja Template Validation (mandatory after any template edit):**
```powershell
cd C:\Users\User\Desktop\gads-data-layer
.\.venv\Scripts\Activate.ps1
python -c "from jinja2 import Environment, FileSystemLoader; env = Environment(loader=FileSystemLoader('act_dashboard/templates')); env.get_template('your_template.html'); print('Jinja OK')"
```

**PowerShell restart command:**
```powershell
cd C:\Users\User\Desktop\gads-data-layer
.\.venv\Scripts\Activate.ps1
python -m act_dashboard.app
```

---

## 📋 RULE 8: ERROR HANDLING

Every code change must include: input validation, safe defaults, empty list/dict checks, try/except with specific errors and logging.

---

## 📋 RULE 9: DELIVERABLES - COMPLETE FILES ONLY

**ALL file edits MUST be provided as complete, ready-to-use files. NO code snippets in chat.**

Format:
1. Show summary of changes (bullets)
2. Provide complete file
3. Specify exact save path (full Windows path)
4. Request confirmation after save

---

## 📋 RULE 10: GIT COMMITS

**When to Commit:** After major working milestone, after completing a chat's main goal, before risky changes, when user requests.

**Git Workflow:**
```powershell
cd C:\Users\User\Desktop\gads-data-layer
git add .
git status
git commit -m "[message]"
git push origin main
```

---

## 📋 RULE 11: WHEN TO STOP

**Stop Immediately If:** Going in circles (same error 3+ times), 3+ hours without resolution, user expresses frustration, root cause unclear after debugging.

Then present options: continue debugging / architectural refactor plan / reassess approach.

---

## 📋 RULE 12: COMPLETION WORKFLOW

After all implementation and testing is done:

1. Worker writes completion summary (Step 10)
2. Christopher pastes to Master Chat
3. Master Chat reviews and approves (or sends back for fixes)
4. Worker creates two handoff docs:
   - `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_[N]_DETAILED_SUMMARY.md`
   - `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_[N]_HANDOFF.md`
5. Christopher pastes both to Master Chat
6. Master Chat reviews handoff docs and updates project docs (Steps 14/15)
7. Master Chat instructs git commit

**Worker never commits to git directly — always via Master Chat instruction.**

---

## ✅ COMPLIANCE CHECKLIST

**Before ANY action, verify:**

- [ ] Have all 7 uploads been received and read?
- [ ] Have I requested current file version before editing? (Rule 2)
- [ ] Am I using full Windows file paths? (Rule 3)
- [ ] Am I completing one step at a time and waiting for confirmation? (Rule 4)
- [ ] Have I sent 5 questions to Master Chat and received answers? (Rule 5)
- [ ] Have I sent my build plan to Master Chat and received approval? (Rule 5)
- [ ] Have I shown my analysis before editing? (Rule 6)
- [ ] Have I included error handling in code? (Rule 8)
- [ ] Am I providing complete files (not snippets)? (Rule 9)
- [ ] Have I tested before reporting complete? (Rule 7)
- [ ] Am I stopping if going in circles? (Rule 11)

**Master Chat is watching. Follow these rules.**

---

## KNOWN PITFALLS (Updated Chat 29)

| Problem | Fix |
|---------|-----|
| Blueprint not registered | New blueprints MUST be added to __init__.py — never assume pre-registration |
| Column missing in synthetic data | Verify column existence before building logic — never assume schema matches brief |
| Missing column fallback | Use proxy/fallback + log it — do not error silently |
| Recommendations in wrong DB | Write to writable warehouse.duckdb — never write to ro.analytics.* |
| Inline card rendering | Use /cards JSON endpoint + JS rendering — do not reload full page |
| Duplicate recommendations | Check (campaign_id, rule_id) before insert — engine run 2 must return SkippedDuplicate |
| Flask route decorator broken | Never insert helper functions between @bp.route decorator and its function |
| Brief column names differ from schema | Always verify actual DB column names before writing |
| Tab switching approach mismatch | recommendations.html: server-side Jinja + JS show/hide; campaigns.html: JS fetch from /cards — match pre-existing pattern per page |
| Datetime formatting from DuckDB | Use `\| string \| truncate(10, True, '')` in Jinja to safely extract YYYY-MM-DD |
| NULL dates on old rows | Synthetic data predating new routes has NULL timestamps — handle gracefully |
| Radar "ro catalog does not exist" | Must ATTACH warehouse_readonly.duckdb in Radar connection before querying ro.analytics.* |
| Radar read-write conflict | Never open warehouse.duckdb with read_only=True if writes needed. Same file, different configs = DuckDB error |
| changes JOIN to recommendations | No recommendation_id FK in changes table — JOIN on campaign_id + rule_id + QUALIFY ROW_NUMBER() |
| System Changes tab data | ro.analytics.change_log is empty in synthetic environment — empty state is correct, not a bug |

---

**Version:** 2.0 | **Last Updated:** 2026-02-26
**END OF CHAT WORKING RULES**

**🚨 CRITICAL CHANGES IN VERSION 2.0:**
1. **NO FILE UPLOADS** - Worker reads from `/mnt/project/` (Christopher only uploads brief)
2. **NO CODEBASE ZIP** - Too large, everything in project files
3. **CHRISTOPHER DOESN'T EDIT CODE** - Worker edits, returns complete files
4. **ONE FILE AT A TIME** - Step-by-step, testing at each stage
5. **TESTING MANDATORY** - Test immediately if step is testable
