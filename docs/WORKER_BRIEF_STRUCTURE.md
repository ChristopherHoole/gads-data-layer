# CLAUDE CODE BRIEF STRUCTURE - DEFINITIVE TEMPLATE

**Purpose:** Defines the EXACT structure Master Chat must use when creating Claude Code briefs
**Architecture:** 2-Tier (Master Chat → Claude Code). Worker Chats are eliminated.
**Last Updated:** 2026-03-15
**Template Version:** 5.0

---

## 🚨 CRITICAL RULES (NEVER VIOLATE THESE)

### RULE 1: BRIEF LENGTH
❌ **NEVER write briefs longer than 2 pages (approx 150 lines)**
✅ **Briefs are SHORT and TASK-FOCUSED:** what to build, exact file paths, key constraints, success criteria

### RULE 2: NO QUESTIONS/BUILD PLAN STAGES
❌ **NEVER include a "5 questions stage" or "build plan stage"**
❌ **NEVER ask Claude Code to wait for approval before starting**
✅ **Claude Code executes autonomously — brief → implement → test → report back**

### RULE 3: CHRISTOPHER NEVER EDITS CODE
❌ **NEVER say "edit line X" or "replace function Y"**
✅ **Claude Code edits files directly in the codebase**

### RULE 4: FULL WINDOWS PATHS ALWAYS
❌ **NEVER:** `routes/outreach.py`
✅ **ALWAYS:** `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\outreach.py`

### RULE 5: GIT COMMITS ARE MASTER CHAT'S JOB
❌ **NEVER ask Claude Code to run git commands**
✅ **Git commits happen in Master Chat via PowerShell — AFTER Christopher confirms in Opera**

### RULE 6: POWERSHELL COMMANDS ARE MASTER CHAT'S JOB
❌ **NEVER send Flask start or taskkill commands to Claude Code**
✅ **Always include fresh-start PowerShell commands in Master Chat:**
```powershell
taskkill /IM python.exe /F
cd C:\Users\User\Desktop\gads-data-layer
.\.venv\Scripts\Activate.ps1
python act_dashboard/app.py
```

### RULE 7: QUICK FIXES STAY IN MASTER CHAT
❌ **NEVER send Claude Code a brief for a 1–3 file fix with a clear, well-defined change**
✅ **Quick fixes: Christopher uploads file → Master Chat edits → returns complete file → Christopher saves**
✅ **Only send to Claude Code when task requires 4+ files, new routes, blueprints, or significant logic**

---

## 📋 MANDATORY BRIEF STRUCTURE

### SECTION 1: HEADER
```markdown
# CHAT [NUMBER]: [TASK NAME]
**Date:** YYYY-MM-DD
**Estimated Time:** X–Y hours
**Priority:** HIGH / MEDIUM / LOW
**Dependencies:** [What must be complete first, or "None"]
```

### SECTION 2: CONTEXT (3–5 sentences MAX)
```markdown
## CONTEXT
[2–3 sentence summary of relevant prior work]
[1–2 sentences on why this task is needed now]
```

### SECTION 3: OBJECTIVE (1 sentence)
```markdown
## OBJECTIVE
[Single clear sentence describing the goal]
```

### SECTION 4: DELIVERABLES
```markdown
## DELIVERABLES
1. `C:\Users\User\Desktop\gads-data-layer\[path]\file.ext` — CREATE/MODIFY
   - [What it does / what changes]
2. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_[N]_HANDOFF.md` — CREATE
3. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_[N]_SUMMARY.md` — CREATE
```

### SECTION 5: REQUIREMENTS
```markdown
## REQUIREMENTS
### Technical
- [Specific requirement 1]
- [Database table / column names if relevant]
### Design (if UI work)
- Bootstrap 5 components only
- Extend base_bootstrap.html
### Constraints
- [Known pitfalls to avoid]
```

### SECTION 6: SUCCESS CRITERIA
```markdown
## SUCCESS CRITERIA
- [ ] [Specific visual or functional test]
- [ ] No console errors
- [ ] Flask starts cleanly
ALL must pass before reporting complete.
```

### SECTION 7: REFERENCE FILES
```markdown
## REFERENCE FILES
- `C:\Users\User\Desktop\gads-data-layer\[path]\file.py` — Shows [pattern]
```

### SECTION 8: TESTING INSTRUCTIONS
```markdown
## TESTING
1. [Specific test step]
2. Confirm no console errors in Flask terminal
3. Report exact Flask log output for any writes
```

---

## ✅ CHECKLIST FOR MASTER CHAT

Before finalising any brief, verify:
- [ ] Brief is under 150 lines
- [ ] No "5 questions stage" or "build plan stage"
- [ ] No git commands in brief
- [ ] No PowerShell/Flask commands in brief
- [ ] All file paths are full Windows paths
- [ ] Success criteria are specific and testable
- [ ] Deliverables include CHAT_N_HANDOFF.md and CHAT_N_SUMMARY.md
- [ ] Context is 3–5 sentences max

---

## 📊 ROADMAP FORMAT — MANDATORY TEMPLATE

When Christopher asks for the full project roadmap or work list, ALWAYS use this exact format.
No paragraphs. Each section has its own numbered list starting from 1.

```
**DASHBOARD — ACT**
1. [item]
2. [item]

**OUTREACH**
1. [item]
2. [item]

**WEBSITE**
1. [item]
2. [item]

**GOOGLE ADS — EXTERNAL (monitor only)**
1. [item]
2. [item]

**ADMIN**
1. [item]
```

**Rules:**
- Each section header is bold
- Each section's list starts at 1 (not a continuation of previous section)
- One item per line — no sub-bullets, no descriptions in paragraphs
- Descriptions go on the same line after a dash: `1. Item name — brief context`
- Never use prose paragraphs for roadmap items

---

## 🔧 MASTER CHAT POWERSHELL COMMANDS

**Flask start:**
```powershell
taskkill /IM python.exe /F
cd C:\Users\User\Desktop\gads-data-layer
.\.venv\Scripts\Activate.ps1
python act_dashboard/app.py
```

**Git commit (only after Christopher confirms in Opera):**
```powershell
taskkill /IM python.exe /F
cd C:\Users\User\Desktop\gads-data-layer
git add .
git commit -m "Chat XX: [Description]"
git push origin main
```

**Start Claude Code:**
```powershell
cd C:\Users\User\Desktop\gads-data-layer
npx @anthropic-ai/claude-code
```

---

**Document Version:** 5.0
**Last Updated:** 2026-03-15
