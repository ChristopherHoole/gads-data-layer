# CHAT WORKING RULES - MANDATORY FOR ALL CHATS

**Version:** 1.5
**Last Updated:** 2026-02-23
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

## 📋 RULE 1: MANDATORY UPLOADS AT START OF EVERY CHAT

**MANDATORY FIRST STEP FOR EVERY CHAT — ALL 7 UPLOADS REQUIRED:**

Before doing ANYTHING, confirm all 7 uploads received:
```
Before I begin, I need 7 mandatory uploads:

1. Codebase ZIP
   Location: C:\Users\User\Desktop\gads-data-layer

2. CHAT_[N]_BRIEF.md  (the brief for this specific chat)
   Location: C:\Users\User\Desktop\gads-data-layer\docs\CHAT_[N]_BRIEF.md

3. PROJECT_ROADMAP.md
   Location: C:\Users\User\Desktop\gads-data-layer\docs\PROJECT_ROADMAP.md

4. CHAT_WORKING_RULES.md
   Location: C:\Users\User\Desktop\gads-data-layer\docs\CHAT_WORKING_RULES.md

5. MASTER_KNOWLEDGE_BASE.md
   Location: C:\Users\User\Desktop\gads-data-layer\docs\MASTER_KNOWLEDGE_BASE.md

6. DASHBOARD_PROJECT_PLAN.md
   Location: C:\Users\User\Desktop\gads-data-layer\docs\DASHBOARD_PROJECT_PLAN.md

7. WORKFLOW_GUIDE.md
   Location: C:\Users\User\Desktop\gads-data-layer\docs\WORKFLOW_GUIDE.md
```

**After all 7 uploaded:**
1. Extract ZIP, explore structure
2. Read the brief for this chat in full
3. Read PROJECT_ROADMAP.md — understand current status
4. Read CHAT_WORKING_RULES.md — confirm rules understood
5. Read MASTER_KNOWLEDGE_BASE.md — understand architecture and lessons learned
6. THEN proceed to Rule 5 (5 Questions)

**NEVER skip any of the 7 uploads. NEVER proceed with only some.**

---

## 📋 RULE 2: FILE HANDLING - ALWAYS REQUEST CURRENT VERSION

### **The Rule:**
**BEFORE analyzing or editing ANY file, you MUST request the current version from the user.**

### **NEVER Say:**
- ❌ "I already have this file from earlier"
- ❌ "I'll use the version from the ZIP"
- ❌ "Based on my previous upload..."

### **ALWAYS Say:**
```
I need the current version to ensure accurate editing.

Please upload:
- File: [filename]
- Location: C:\Users\User\Desktop\gads-data-layer\[path]\[filename]

After upload, I will:
1. Analyze current state
2. Make the fix
3. Provide download link

Upload now.
```

### **Why This Rule Exists:**
- User may have manually edited since last upload
- User may have reverted changes
- Other processes may have modified files
- ZIP may be outdated
- Your memory may be wrong

### **Enforcement:**
If you catch yourself about to edit a file, ask:
1. "Do I have the CURRENT version uploaded in the last 2 messages?"
2. If NO → Request upload FIRST
3. If YES → Proceed

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

## 📋 RULE 4: WORKFLOW - ONE STEP AT A TIME

### **The Rule:**
**Complete each step FULLY before proceeding to the next. Wait for user confirmation.**

### **NEVER:**
- ❌ Combine multiple steps in one response
- ❌ Proceed without user confirmation
- ❌ Make assumptions about what user wants next

### **ALWAYS:**
```
STEP 1 COMPLETE: [What was done]

Next: STEP 2: [What will be done]

Reply "Proceed" to continue, or give different instructions.

[STOP - Wait for confirmation]
```

---

## 📋 RULE 5: 5 QUESTIONS + BUILD PLAN REVIEW BEFORE BUILDING

### **The Rule:**
**After uploading and reviewing all docs — BEFORE writing any code — the worker MUST complete a two-stage clarification process: (1) send 5 questions to Master Chat, (2) send a detailed build plan to Master Chat for review. Both must be approved before implementation begins.**

### **The Full Process:**
```
STEP 1:  Worker reviews brief + codebase + all 7 docs
STEP 2:  Worker writes exactly 5 questions (no more, no less)
STEP 3:  Worker sends questions with header "5 QUESTIONS FOR MASTER CHAT"
STEP 4:  Worker STOPS — waits for answers
STEP 5:  User copies questions → pastes in Master Chat
STEP 6:  Master provides answers
STEP 7:  User pastes answers back into worker chat
STEP 8:  Worker creates detailed build plan
STEP 9:  Worker STOPS — waits for Master Chat review
STEP 10: User copies detailed build plan → pastes in Master Chat
STEP 11: Master Chat reviews build plan and provides feedback
STEP 12: User pastes feedback back into worker chat
STEP 13: Worker begins implementation
```

### **Question Format:**
```
5 QUESTIONS FOR MASTER CHAT

Q1. [CATEGORY] Question text here?
Q2. [CATEGORY] Question text here?
Q3. [CATEGORY] Question text here?
Q4. [CATEGORY] Question text here?
Q5. [CATEGORY] Question text here?

Waiting for Master Chat answers before proceeding.
```

### **Build Plan Format:**
```
DETAILED BUILD PLAN FOR MASTER CHAT REVIEW

Files to create/modify:
- [Full path] — [what changes]

Step-by-step implementation:
STEP A: [Task] (~X min)
  - [Specific action]
STEP B: [Task] (~X min)
  - [Specific action]
STEP C: Testing (~X min)
  - [Test 1]

Total estimated time: X minutes
Risks / unknowns: [Any remaining concerns]

Waiting for Master Chat approval before starting.
```

### **Question Categories:**
- `[DATABASE]` — schema, column names, table existence
- `[ROUTE]` — existing code, overwrite vs. extend
- `[DESIGN]` — UI decisions not clear from brief
- `[RULES]` — rules engine specifics
- `[SCOPE]` — what's in vs. out of this chat

### **NEVER:**
- ❌ Ask questions answerable by reading the brief
- ❌ Ask generic or vague questions
- ❌ Ask more or fewer than 5 questions
- ❌ Skip the build plan step after receiving Q&A answers
- ❌ Begin implementation without Master Chat approving the build plan

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

**Version:** 1.5 | **Last Updated:** 2026-02-23
**END OF CHAT WORKING RULES**
