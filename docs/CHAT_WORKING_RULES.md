# CHAT WORKING RULES - MANDATORY FOR ALL CHATS

**Version:** 1.2  
**Last Updated:** 2026-02-21  
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

**MANDATORY FIRST STEP FOR EVERY CHAT — ALL 3 UPLOADS REQUIRED:**

Before doing ANYTHING, request all 3 uploads:
```
Before I begin, I need 3 mandatory uploads:

1. Codebase ZIP
   Location: C:\Users\User\Desktop\gads-data-layer
   (Create ZIP of entire folder and upload here)

2. PROJECT_ROADMAP.md
   Location: C:\Users\User\Desktop\gads-data-layer\docs\PROJECT_ROADMAP.md

3. CHAT_WORKING_RULES.md
   Location: C:\Users\User\Desktop\gads-data-layer\docs\CHAT_WORKING_RULES.md

These allow me to:
✅ See complete project structure (ZIP)
✅ Understand current project status and completed work (ROADMAP)
✅ Follow mandatory working rules for this project (RULES)
✅ Work from current state, not assumptions

Upload all 3 now before I proceed.
```

**After all 3 uploaded:**
1. Extract ZIP
2. Use `view` tool to explore structure
3. Read PROJECT_ROADMAP.md — understand current status
4. Read CHAT_WORKING_RULES.md — confirm rules understood
5. THEN proceed to Phase 2B (5 Questions)

**NEVER skip any of the 3 uploads. NEVER proceed with only 1 or 2.**

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

### **Why This Rule Exists:**
- Prevents ambiguity (multiple files with same name)
- User knows exactly what to upload/save
- No confusion about locations
- Professional communication

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

### **Why This Rule Exists:**
- User can course-correct if needed
- Prevents runaway automation
- Allows user to verify each step
- Reduces waste if direction changes

### **Checkpoints:**
- After analysis/diagnosis
- After creating files
- After testing
- Before major changes

---

## 📋 RULE 5: 5 QUESTIONS + BUILD PLAN REVIEW BEFORE BUILDING

### **The Rule:**
**After uploading and reviewing the codebase, PROJECT_ROADMAP.md, and CHAT_WORKING_RULES.md — BEFORE writing any code — the worker MUST complete a two-stage clarification process: (1) send 5 questions to Master Chat, (2) send a detailed build plan to Master Chat for review. Both must be approved before implementation begins.**

### **Why This Rule Exists:**
- Surfaces unknowns BEFORE they become bugs
- Prevents mid-build assumptions that cost hours to debug
- Ensures worker and Master are fully aligned on approach
- Catches architectural mistakes before any code is written
- Saves time vs. discovering issues mid-implementation

### **The Full Process:**
```
STEP 1:  Worker reviews brief + codebase + docs
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

### **Build Plan Format (after receiving Q&A answers):**
```
DETAILED BUILD PLAN FOR MASTER CHAT REVIEW

Files to create/modify:
- [Full path] — [what changes]
- [Full path] — [what changes]

Step-by-step implementation:
STEP A: [Task] (~X min)
  - [Specific action]
  - [Specific action]
STEP B: [Task] (~X min)
  - [Specific action]
STEP C: Testing (~X min)
  - [Test 1]
  - [Test 2]

Total estimated time: X minutes
Risks / unknowns: [Any remaining concerns]

Waiting for Master Chat approval before starting.
```

### **Question Categories (use in brackets):**
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

### **Enforcement:**
Master Chat will not review completed work from a worker that skipped either stage of this process. Both the Q&A and the build plan review are mandatory checkpoints.

---

## 📋 RULE 6: SHOW YOUR WORK

### **The Rule:**
**Document findings, explain reasoning, show comparisons BEFORE making changes.**

### **Analysis Format:**
```
CURRENT STATE:
- Field X: [current value]
- Field Y: [current value]

PROBLEM IDENTIFIED:
- [Specific issue with evidence]

PROPOSED FIX:
- [Exact change to make]

WHY THIS FIXES IT:
- [Explanation of how fix addresses problem]
```

### **Before/After Format:**
```
BEFORE (Current Code - Line X):
[exact current code]

AFTER (New Code):
[exact new code]

CHANGES MADE:
✅ [Change 1]
✅ [Change 2]
```

### **Comparison Tables:**
```
| Field | Required | Keywords Has | Ads Has | Shopping Has |
|-------|----------|--------------|---------|--------------|
| id    | Yes      | ❌ Missing   | ✅ Yes  | ✅ Yes       |
```

### **Why This Rule Exists:**
- User understands what you're doing
- User can catch errors before they happen
- Builds trust
- Creates documentation trail

---

## 📋 RULE 7: DEBUGGING PROTOCOL

### **When Tests Fail:**

**MANDATORY DEBUG WORKFLOW:**

1. **Add Debug Logging:**
```python
logger.info(f"DEBUG: field_name={field_name}")
logger.info(f"DEBUG: full_object={full_object}")
```

2. **Request Test:**
```
I've added debug logging to see exact values.

Please:
1. Save the file
2. Restart server
3. Test the action
4. Copy ALL debug lines from PowerShell
5. Paste here

This will show us EXACTLY what values are causing the failure.
```

3. **Analyze Debug Output:**
```
DEBUG OUTPUT ANALYSIS:
- Field X = [value] ← PROBLEM: Should be [expected]
- Field Y = [value] ← OK
- Field Z = [value] ← PROBLEM: Is None, should be [type]

ROOT CAUSE: [Specific issue identified]

FIX: [Exact change needed]
```

4. **Fix and Retest:**
- Make targeted fix
- Keep debug logging until confirmed working
- Remove debug logging after success

### **Never:**
- ❌ Guess at the problem without debug output
- ❌ Make changes without seeing actual values
- ❌ Say "it should work" without testing

---

## 📋 RULE 8: ERROR HANDLING

### **Every Code Change Must Include:**

**1. Input Validation:**
```python
if not all([required_field1, required_field2]):
    return {
        "success": False,
        "message": "Missing required fields",
        "error": "Specific field names missing"
    }
```

**2. Safe Defaults:**
```python
value = rec.get('field') or 'safe_default'
count = rec.get('count') if rec.get('count') is not None else 0
```

**3. Empty List/Dict Checks:**
```python
if len(results) == 0:
    return error_response("No results found")

result = results[0]  # Only access after checking length
```

**4. Try/Except with Specific Errors:**
```python
try:
    result = risky_operation()
except KeyError as e:
    logger.error(f"Missing key: {e}")
    return error_response(f"Missing required key: {e}")
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    return error_response(f"Operation failed: {e}")
```

### **Never:**
- ❌ Assume fields exist without checking
- ❌ Access list[0] without checking length
- ❌ Use broad `except Exception` without logging
- ❌ Return generic error messages

---

## 📋 RULE 9: TESTING PROTOCOL

### **After EVERY code change:**

**MANDATORY TEST WORKFLOW:**

1. **Specify Exact Test Steps:**
```
TESTING INSTRUCTIONS:

1. Save file to: C:\Users\User\Desktop\gads-data-layer\[path]\[file]
2. Restart server:
   cd C:\Users\User\Desktop\gads-data-layer
   .\.venv\Scripts\Activate.ps1
   python act_dashboard/app.py
3. Navigate to: http://localhost:5000/[page]
4. Click "Dry-Run" on first 3 recommendations
5. Report:
   - Toast color (green or red)
   - Toast message
   - PowerShell output (last 10 lines)
```

2. **Define Success Criteria:**
```
EXPECTED RESULTS:
✅ Green success toast appears
✅ PowerShell shows: "successful=1, failed=0"
✅ No errors in browser console
```

3. **Handle Failures:**
```
IF TEST FAILS:
1. Do NOT proceed to next step
2. Request debug output
3. Analyze failure
4. Fix issue
5. Retest
6. Only proceed when test passes
```

### **Never:**
- ❌ Skip testing after code changes
- ❌ Proceed if tests fail
- ❌ Say "it should work" without actual test
- ❌ Test only one scenario (test multiple)
- ❌ Deploy a modified Jinja template without first validating syntax

**Jinja Template Validation (mandatory after any template edit):**
```powershell
cd C:\Users\User\Desktop\gads-data-layer
.\.venv\Scripts\Activate.ps1
python -c "from jinja2 import Environment, FileSystemLoader; env = Environment(loader=FileSystemLoader('act_dashboard/templates')); env.get_template('your_template.html'); print('Jinja OK')"
```
If this throws an error, fix the template before proceeding.

---

## 📋 RULE 10: DELIVERABLES - DOWNLOADS ONLY

### **The Rule:**
**ALL file edits MUST be provided as download links. NO code in chat.**

### **WRONG:**
```
Here's the fixed code:
[300 lines of Python code in chat]

Copy this and save it to routes.py
```

### **CORRECT:**
```
CHANGES MADE:
✅ Fixed field validation (line 245)
✅ Added error handling (lines 260-265)

[DOWNLOAD LINK - routes.py]

Save to: C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes.py

After saving, reply "Saved, ready to test"
```

### **Why This Rule Exists:**
- Code in chat is hard to copy
- Formatting breaks
- User can't easily save
- Download = one click
- Download = complete file guaranteed

### **Format:**
1. Show summary of changes (bullets)
2. Provide download link
3. Specify exact save path
4. Request confirmation after save

---

## 📋 RULE 11: GIT COMMITS

### **When to Commit:**
- After major working milestone
- After completing a chat's main goal
- Before attempting risky changes
- When user requests

### **Commit Message Format:**
```
[Chat Number]: [Brief Description]

WORKING:
- [Feature 1]: Description
- [Feature 2]: Description

IN PROGRESS / FIXED:
- [Issue 1]: What was done
- [Issue 2]: What was done

FILES MODIFIED:
- path/to/file1.py (what changed)
- path/to/file2.py (what changed)

FILES CREATED:
- path/to/new_file.py

TEST RESULTS:
- [Test 1]: ✅ / ❌
- [Test 2]: ✅ / ❌

NEXT: [What should be done next]
```

### **Git Workflow:**
```powershell
cd C:\Users\User\Desktop\gads-data-layer
git add .
git status
git commit -m "[message from above]"
git push origin main
```

---

## 📋 RULE 12: WHEN TO STOP

### **Stop Immediately If:**
- Going in circles (same error 3+ times)
- 3+ hours on same issue without resolution
- User expresses frustration
- Unclear what's causing problem even after debugging
- Tactical fixes revealing more issues underneath

### **Then:**
```
⚠️ STOPPING - Tactical approach not working

We've encountered [problem] which suggests deeper architectural issues.

OPTIONS:
A) Continue debugging (est. [time])
B) Stop and create architectural refactor plan
C) Stop and reassess approach

User, what would you like to do?
```

### **Never:**
- ❌ Keep trying same fixes hoping for different results
- ❌ Make changes without understanding root cause
- ❌ Waste user's time on fruitless debugging

---

## 📋 RULE 13: COMMUNICATION

### **Tone:**
- Professional but friendly
- Honest about limitations
- Clear about what you know vs. don't know
- Admit mistakes immediately

### **Explanations:**
- Use simple language
- Explain WHY, not just WHAT
- Provide context
- Break complex topics into steps

### **Questions:**
- Ask specific questions
- Provide options when appropriate
- Don't ask what you should already know from files

### **Updates:**
- Keep user informed of progress
- Explain what you're doing
- Set realistic expectations

---

## ✅ COMPLIANCE CHECKLIST

**Before ANY action, verify:**

- [ ] Have I uploaded codebase ZIP? (if first message)
- [ ] Have I requested current file version?
- [ ] Am I using full file paths?
- [ ] Am I completing one step at a time?
- [ ] Have I sent 5 questions to Master Chat and received answers? (Rule 5)
- [ ] Have I sent my build plan to Master Chat and received approval? (Rule 5)
- [ ] Have I shown my analysis before editing? (Rule 6)
- [ ] Have I included debug logging if testing?
- [ ] Have I included error handling in code?
- [ ] Have I specified exact test steps?
- [ ] Am I providing downloads (not code in chat)?
- [ ] Am I stopping if going in circles?

**Master Chat is watching. Follow these rules.**

---

**END OF CHAT WORKING RULES**