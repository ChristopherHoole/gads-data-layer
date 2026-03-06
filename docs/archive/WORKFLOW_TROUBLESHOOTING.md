# WORKFLOW TROUBLESHOOTING - Escalation & Problem Resolution

**Version:** 2.0 (Split from WORKFLOW_GUIDE v1.2)
**Created:** 2026-02-26  
**Purpose:** Escalation triggers, debugging playbook, success criteria  
**Audience:** Master Chat (primary), Worker Chats (reference)

---

## 📋 WORKFLOW DOCUMENTATION SUITE

This is **Part 3 of 3** in the workflow documentation:

1. **WORKFLOW_CORE.md** - Overview, 15-step process, Master responsibilities
2. **WORKFLOW_EXECUTION.md** - Worker lifecycle, handoff process, review checklist
3. **WORKFLOW_TROUBLESHOOTING.md** (this file) - Escalation triggers, debugging, problem resolution

**Related documents:**
- **CHAT_WORKING_RULES.md** - Mandatory rules for all chats (v2.0)
- **WORKFLOW_TEMPLATES.md** - Brief and handoff templates

---

## 📋 TABLE OF CONTENTS

1. [Escalation Triggers](#escalation-triggers)
2. [Debugging Playbook](#debugging-playbook)
3. [Success Criteria](#success-criteria)

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

**Version:** 2.0 | **Last Updated:** 2026-02-26
**Complete:** See WORKFLOW_CORE.md and WORKFLOW_EXECUTION.md for full workflow documentation
