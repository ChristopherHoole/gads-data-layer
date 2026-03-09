# CLAUDE CODE BRIEF STRUCTURE - DEFINITIVE TEMPLATE

**Purpose:** Defines the EXACT structure Master Chat must use when creating Claude Code briefs
**Architecture:** 2-Tier (Master Chat → Claude Code). Worker Chats are eliminated.
**Last Updated:** 2026-03-09
**Template Version:** 4.0

---

## 🚨 CRITICAL RULES (NEVER VIOLATE THESE)

### RULE 1: BRIEF LENGTH
❌ **NEVER write briefs longer than 2 pages (approx 150 lines)**
- Claude Code reads the codebase directly — it doesn't need project history in the brief
- Long briefs waste context window and dilute the task

✅ **Briefs are SHORT and TASK-FOCUSED:**
- What to build
- Exact file paths
- Key constraints
- Success criteria

### RULE 2: NO QUESTIONS/BUILD PLAN STAGES
❌ **NEVER include a "5 questions stage" in Claude Code briefs**
❌ **NEVER include a "build plan stage" in Claude Code briefs**
❌ **NEVER ask Claude Code to wait for approval before starting**

✅ **Claude Code executes autonomously — brief → implement → test → report back**

### RULE 3: CHRISTOPHER NEVER EDITS CODE
❌ **NEVER say "edit line X" or "replace function Y"**
❌ **NEVER give partial snippets and expect Christopher to merge them**

✅ **Claude Code edits files directly in the codebase**
✅ **Complete files are returned only if Christopher needs to download them**

### RULE 4: FULL WINDOWS PATHS ALWAYS
❌ **NEVER use partial paths:** `routes/outreach.py`
✅ **ALWAYS use full paths:** `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\outreach.py`

### RULE 5: GIT COMMITS ARE MASTER CHAT'S JOB
❌ **NEVER ask Claude Code to run git commands**
❌ **NEVER send git commands to Claude Code**

✅ **Git commits happen in Master Chat via PowerShell — AFTER Christopher confirms in Opera**

### RULE 6: POWERSHELL COMMANDS ARE MASTER CHAT'S JOB
❌ **NEVER send Flask start commands to Claude Code**
❌ **NEVER send taskkill commands to Claude Code**

✅ **All PowerShell commands come from Master Chat**
✅ **Always include fresh-start PowerShell commands:**
```powershell
taskkill /IM python.exe /F
cd C:\Users\User\Desktop\gads-data-layer
.\.venv\Scripts\Activate.ps1
python act_dashboard/app.py
```

### RULE 7: QUICK FIXES STAY IN MASTER CHAT
❌ **NEVER send Claude Code a brief for a 1–3 file fix with a clear, well-defined change**

✅ **Quick fixes (single file edits, CSS tweaks, route bug fixes) are handled directly in Master Chat:**
- Christopher uploads the current file(s)
- Master Chat edits and returns the complete fixed file(s)
- Christopher saves and restarts Flask

✅ **Only send to Claude Code when the task requires:**
- 4+ files to be modified
- New routes, blueprints, or database tables
- Significant new logic or features

---

## 📋 MANDATORY BRIEF STRUCTURE

Every Claude Code brief must contain these sections in order:

---

### SECTION 1: HEADER

```markdown
# CHAT [NUMBER]: [TASK NAME]

**Date:** YYYY-MM-DD
**Estimated Time:** X–Y hours
**Priority:** HIGH / MEDIUM / LOW
**Dependencies:** [What must be complete first, or "None"]
```

---

### SECTION 2: CONTEXT (3–5 sentences MAX)

What was done before this, and why this task is needed. Nothing more.

```markdown
## CONTEXT

[2–3 sentence summary of relevant prior work]
[1–2 sentences on why this task is needed now]
```

---

### SECTION 3: OBJECTIVE (1 sentence)

```markdown
## OBJECTIVE

[Single clear sentence describing the goal]
```

---

### SECTION 4: DELIVERABLES

Full Windows paths for every file to create or modify. Be explicit about what changes.

```markdown
## DELIVERABLES

1. `C:\Users\User\Desktop\gads-data-layer\[path]\file.ext` — CREATE/MODIFY
   - [What it does / what changes]

2. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_[N]_HANDOFF.md` — CREATE
   - Technical handoff document

3. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_[N]_SUMMARY.md` — CREATE
   - Executive summary
```

---

### SECTION 5: REQUIREMENTS

Specific technical requirements. Be explicit — Claude Code does not guess.

```markdown
## REQUIREMENTS

### Technical
- [Specific requirement 1]
- [Specific requirement 2]
- [Database table / column names if relevant]
- [API endpoint names if relevant]

### Design (if UI work)
- Bootstrap 5 components only
- Extend base_bootstrap.html
- [Color / layout specs]

### Constraints
- [Known pitfalls to avoid]
- [Patterns already established in codebase]
```

---

### SECTION 6: SUCCESS CRITERIA

Specific, testable. Christopher verifies these manually in Opera.

```markdown
## SUCCESS CRITERIA

- [ ] [Specific visual or functional test]
- [ ] [Specific visual or functional test]
- [ ] [All items from the confirmed "not yet live" list are working]
- [ ] No console errors
- [ ] Flask starts cleanly

ALL must pass before reporting complete.
```

---

### SECTION 7: REFERENCE FILES

Files Claude Code should read before starting.

```markdown
## REFERENCE FILES

- `C:\Users\User\Desktop\gads-data-layer\[path]\similar_file.py` — Shows [pattern]
- `C:\Users\User\Desktop\gads-data-layer\[path]\related_template.html` — Shows [pattern]
```

---

### SECTION 8: TESTING INSTRUCTIONS

What to test and how. Claude Code runs these after implementing.

```markdown
## TESTING

1. [Specific test step]
2. [Specific test step]
3. Confirm no console errors in Flask terminal
4. Report exact Flask log output for any sends/writes
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
- [ ] No code snippets for Christopher to manually apply

---

## 📝 EXAMPLE BRIEF (SHORT)

```markdown
# CHAT 69: EMAIL SIGNATURE

**Date:** 2026-03-08
**Estimated Time:** 1–2 hours
**Priority:** HIGH
**Dependencies:** Chat 68 complete

---

## CONTEXT

Chat 68 built live email sending via Gmail SMTP. Emails currently send without any signature block. All outgoing emails need a consistent HTML signature appended.

## OBJECTIVE

Append a formatted HTML signature to every email sent from queue_send().

---

## DELIVERABLES

1. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\email_sender.py` — MODIFY
   - Add `get_signature_html()` function that returns formatted HTML signature block
   - Append signature to body_html in send_email() or expose as utility

2. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\outreach.py` — MODIFY
   - In queue_send(), append signature to body_html before calling send_email()

3. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_69_HANDOFF.md` — CREATE
4. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_69_SUMMARY.md` — CREATE

---

## REQUIREMENTS

### Signature content
- Name: Christopher Hoole
- Title: Google Ads Specialist | 16 Years Experience
- Email: chris@christopherhoole.com
- Website: https://christopherhoole.com
- Styled with a top border separator, grey text, Arial font

### Technical
- Signature appended after body content, separated by `<br><br><hr style='...'>`
- Must not break existing body_html wrapping div
- UTF-8 safe

---

## SUCCESS CRITERIA

- [ ] Email arrives at chrishoole101@gmail.com with visible signature below body
- [ ] Signature has name, title, email, website
- [ ] Separator line between body and signature
- [ ] Special characters render correctly (no mojibake)
- [ ] Flask log shows [EMAIL] OK Sent

---

## REFERENCE FILES

- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\email_sender.py` — Current send_email() implementation
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\outreach.py` — Current queue_send() at line ~671

---

## TESTING

1. Run `python tools/reseed_queue.py`
2. Start Flask
3. Send one email from Queue page
4. Check chrishoole101@gmail.com — confirm signature present and formatted
5. Paste Flask [EMAIL] OK log line
```

---

## 🔧 MASTER CHAT POWERSHELL COMMANDS

**Always provide these in Master Chat when Flask testing is needed:**

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

**Document Version:** 4.0
**Last Updated:** 2026-03-09
**Replaces:** WORKER_BRIEF_STRUCTURE.md v3.0
