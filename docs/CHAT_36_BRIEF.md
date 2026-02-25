# CHAT 36: CSRF PROTECTION (FLASK-WTF)

**Estimated Time:** 2-3 hours
**Dependencies:** None (independent security improvement)
**Priority:** HIGH (security hardening)

---

## 🚨 MANDATORY WORKFLOW - READ THIS FIRST

This chat follows the **15-step worker chat workflow** from WORKFLOW_GUIDE.md.

**You MUST complete these steps in order:**

### **STEP 1: Read Project Knowledge + Confirm Understanding**

1. Read all 7 files from `/mnt/project/`:
   - MASTER_CHAT_5.0_HANDOFF.md
   - WORKFLOW_TEMPLATES.md
   - CHAT_WORKING_RULES.md
   - PROJECT_ROADMAP.md
   - MASTER_KNOWLEDGE_BASE.md
   - DETAILED_WORK_LIST.md
   - WORKFLOW_GUIDE.md
   - DASHBOARD_PROJECT_PLAN.md

2. Confirm you have read each file explicitly

3. Confirm understanding of:
   - Current project state (99% complete, Chats 32 & 35 done)
   - Rule 2 (CRITICAL): Always request current file version before editing
   - One step at a time workflow with confirmation
   - Complete files only (never snippets)
   - Full Windows paths: `C:\Users\User\Desktop\gads-data-layer\...`

**Template confirmation message:**
```
CONFIRMATION: ALL PROJECT FILES READ

I have read all 7 project files from Project Knowledge:
✅ MASTER_CHAT_5.0_HANDOFF.md
✅ WORKFLOW_TEMPLATES.md
✅ CHAT_WORKING_RULES.md
✅ PROJECT_ROADMAP.md
✅ MASTER_KNOWLEDGE_BASE.md
✅ DETAILED_WORK_LIST.md
✅ WORKFLOW_GUIDE.md
✅ DASHBOARD_PROJECT_PLAN.md

I understand:
* Current state: [brief summary]
* Rule 2: Always request current file before editing
* One step at a time with confirmation
* Complete files only, full Windows paths
* Tech stack: Flask, DuckDB, Bootstrap 5

Ready to proceed to 5 questions for Master Chat.
```

---

### **STEP 2: 5 Clarifying Questions**

After reading all project files, write exactly **5 questions** for Master Chat.

**Question categories:**
- `[SCOPE]` - Which forms need protection
- `[IMPLEMENTATION]` - Flask-WTF approach
- `[FORMS]` - Which routes handle POST requests
- `[TESTING]` - How to verify CSRF working
- `[EXISTING]` - Any CSRF already implemented

**Format:**
```
5 QUESTIONS FOR MASTER CHAT

Q1. [CATEGORY] Question text here?
Q2. [CATEGORY] Question text here?
Q3. [CATEGORY] Question text here?
Q4. [CATEGORY] Question text here?
Q5. [CATEGORY] Question text here?

Waiting for Master Chat answers before proceeding.
```

**⚠️ STOP HERE - Wait for Master Chat answers**

---

### **STEP 3: Detailed Build Plan**

After receiving answers, create a detailed build plan with sequential steps.

**Format:**
```
DETAILED BUILD PLAN FOR MASTER CHAT REVIEW

Files to create/modify:
- C:\Users\User\Desktop\gads-data-layer\[path]\[file] — [what changes]

Step-by-step implementation:
STEP A: Install Flask-WTF (~5 min)
  - Add to requirements.txt
  - pip install
  - Test: verify import works

STEP B: Configure CSRF in app.py (~10 min)
  - Import CSRFProtect
  - Initialize with app
  - Set secret key
  - Test: app starts without error

STEP C: Update forms (~X min)
  - Add {{ csrf_token() }} to each form
  - List all forms to update
  - Test: each form submits

STEP D: Test all forms (~X min)
  - Test each POST route
  - Verify CSRF rejection on missing token

STEP E: Documentation (~20 min)

Total estimated time: [X] minutes
Risks / unknowns: [Any concerns]

Waiting for Master Chat approval before starting implementation.
```

**⚠️ STOP HERE - Wait for Master Chat approval**

---

### **STEP 4: Implementation (ONE STEP AT A TIME)**

After Master Chat approves build plan, execute **ONE STEP AT A TIME**.

**For each step:**

1. **Request current file version:**
```
STEP A STARTING: [File name]

I need the current version to [what you'll do].

Please upload:
- File: [filename]
- Location: C:\Users\User\Desktop\gads-data-layer\[path]\[filename]

[STOP - WAIT FOR UPLOAD]
```

2. **After upload, provide complete updated file:**
```
STEP A COMPLETE ✅

Deliverable: Updated [filename]
[Download link to complete file]

Test this step:
```powershell
[PowerShell commands to test]
```

Expected: [What should happen]

Reply "Confirmed" to proceed to STEP B.

[STOP - WAIT FOR CONFIRMATION]
```

3. **Wait for "Confirmed" before next step**

**CRITICAL RULES:**
- ❌ NEVER provide multiple files in one response
- ❌ NEVER proceed without confirmation
- ❌ NEVER use code snippets (always complete files)
- ✅ ALWAYS request current file version first
- ✅ ALWAYS wait for confirmation after each step
- ✅ ALWAYS provide full Windows paths

---

### **STEP 5: Documentation**

After all implementation and testing complete:

1. Create `CHAT_36_SUMMARY.md` (150-200 lines)
2. Create `CHAT_36_HANDOFF.md` (500-800 lines)
3. Send both to Master Chat for review

**Do NOT commit to git - Master Chat handles commits.**

---

## WORKER CHAT CONFIRMATION REQUIRED

Before proceeding, you MUST explicitly confirm:

- [ ] I have read all 7 project files from Project Knowledge
- [ ] I will write exactly 5 questions and STOP
- [ ] I will wait for Master Chat answers before build plan
- [ ] I will create detailed build plan and STOP
- [ ] I will wait for Master Chat approval before implementation
- [ ] I will execute ONE step at a time
- [ ] I will request current file versions before editing
- [ ] I will provide complete files (not snippets)
- [ ] I will WAIT for confirmation after each step
- [ ] I will NEVER proceed without confirmation
- [ ] I will create comprehensive documentation at end
- [ ] I understand Master Chat handles git commits

---

## CONTEXT

### **What Is CSRF?**

**CSRF (Cross-Site Request Forgery):** An attack where a malicious site tricks a user's browser into making unauthorized requests to your application.

**Example attack:**
1. User logs into A.C.T dashboard
2. User visits malicious site (in another tab)
3. Malicious site submits form to A.C.T (e.g., accept all recommendations)
4. Browser sends user's session cookies automatically
5. A.C.T executes the action (user didn't intend this)

**CSRF protection prevents this** by requiring a secret token with each form submission.

---

### **Why This Matters**

A.C.T dashboard has several **state-changing actions:**
- Accept/decline/modify recommendations (changes Google Ads campaigns)
- Create/edit/delete rules (changes automation behavior)
- Execute keyword operations (adds negative keywords, expands keywords)

**Without CSRF protection:** An attacker could trigger these actions without the user's knowledge.

**With CSRF protection:** Forms require a secret token that only the real page can generate, blocking CSRF attacks.

---

## OBJECTIVE

Add Flask-WTF CSRF protection to all forms in the A.C.T dashboard to prevent cross-site request forgery attacks.

---

## REQUIREMENTS

### **Deliverables**

**1. Install Flask-WTF**

**File:** `C:\Users\User\Desktop\gads-data-layer\requirements.txt`

**Changes:**
- Add `Flask-WTF==1.2.1` to dependencies
- Run `pip install Flask-WTF`

---

**2. Configure CSRF in app.py**

**File:** `C:\Users\User\Desktop\gads-data-layer\act_dashboard\app.py`

**Changes:**
```python
from flask_wtf.csrf import CSRFProtect

# After creating Flask app
app = Flask(__name__)
csrf = CSRFProtect(app)

# Ensure SECRET_KEY is set
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
```

**Note:** SECRET_KEY may already exist. If so, just add CSRFProtect initialization.

---

**3. Add CSRF tokens to all forms**

**Forms to protect (likely locations):**

**A. Recommendations actions (recommendations.html)**
- Accept recommendation form
- Decline recommendation form
- Modify recommendation form

**B. Rules CRUD (campaigns.html or rules templates)**
- Add rule form
- Edit rule form
- Delete rule form

**C. Keywords operations (keywords_new.html)**
- Add as negative keyword form
- Add as keyword form

**D. Any other POST forms**
- Settings forms (if exist)
- Other forms identified during implementation

**Template change pattern:**
```html
<!-- OLD (no CSRF) -->
<form method="POST" action="/api/recommendations/123/accept">
  <button type="submit">Accept</button>
</form>

<!-- NEW (with CSRF) -->
<form method="POST" action="/api/recommendations/123/accept">
  {{ csrf_token() }}
  <button type="submit">Accept</button>
</form>
```

**Or for JavaScript/AJAX forms:**
```html
<meta name="csrf-token" content="{{ csrf_token() }}">

<script>
fetch('/api/endpoint', {
  method: 'POST',
  headers: {
    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
  }
})
</script>
```

---

**4. Handle CSRF in API routes (if needed)**

**File:** `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\api.py`

**For /api/leads (external form):**
```python
from flask_wtf.csrf import CSRFProtect, exempt

@bp.route('/api/leads', methods=['POST', 'OPTIONS'])
@csrf.exempt  # External form doesn't have CSRF token
def leads():
    # ... existing code
```

**Reason:** External website form (christopherhoole.online) can't get CSRF token from A.C.T app. Must exempt this endpoint.

**All other API routes:** Require CSRF token (protect from CSRF attacks).

---

### **Technical Constraints**

**Must maintain:**
- ✅ All existing functionality working
- ✅ All forms submitting successfully (with token)
- ✅ External API endpoint (/api/leads) still accepts requests
- ✅ No breaking changes to user experience

**Must NOT:**
- ❌ Break any existing forms
- ❌ Block legitimate requests
- ❌ Require CSRF for OPTIONS requests (CORS preflight)
- ❌ Add CSRF to GET requests (not needed, read-only)

---

### **Design Specifications**

**CSRF token placement:**

**For standard forms:**
```html
<form method="POST" action="/some/route">
  {{ csrf_token() }}
  <!-- form fields -->
</form>
```

**For JavaScript/AJAX:**
```html
<!-- In <head> or base template -->
<meta name="csrf-token" content="{{ csrf_token() }}">

<!-- In JavaScript -->
<script>
const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
fetch(url, {
  method: 'POST',
  headers: {
    'X-CSRFToken': csrfToken,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(data)
});
</script>
```

**For forms using fetch() API:**
- Add CSRF token to headers: `'X-CSRFToken': token`
- Flask-WTF checks both form field and header

---

## REFERENCE FILES

### **Similar Work**

**None in this project** - CSRF is new addition.

**Reference external:**
- Flask-WTF docs: https://flask-wtf.readthedocs.io/
- Flask docs on CSRF: https://flask.palletsprojects.com/patterns/wtforms/

---

### **Files to Review**

**1. Templates with forms:**
```
C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\
  - recommendations.html (accept/decline/modify buttons)
  - campaigns.html (rules CRUD)
  - keywords_new.html (keyword operations)
  - changes.html (any forms?)
  - base_bootstrap.html (add meta tag here if using AJAX)
```

**2. Routes handling POST:**
```
C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\
  - recommendations.py (POST /accept, /decline, /modify)
  - rules_api.py (POST /api/rules/add, PUT /update, DELETE)
  - keywords.py (POST /add-negative, /add-keyword)
  - api.py (POST /api/leads - EXEMPT this)
```

**3. App initialization:**
```
C:\Users\User\Desktop\gads-data-layer\act_dashboard\app.py
  - Add CSRFProtect initialization
```

---

### **Documentation to Consult**

**From Project Knowledge:**
- MASTER_KNOWLEDGE_BASE.md - Current architecture
- CHAT_WORKING_RULES.md - Rule 8 (error handling)

---

## SUCCESS CRITERIA

**All 10 criteria must pass for approval:**

- [ ] 1. Flask-WTF installed (in requirements.txt, pip install successful)
- [ ] 2. CSRFProtect initialized in app.py
- [ ] 3. SECRET_KEY configured (exists or added)
- [ ] 4. All POST forms include {{ csrf_token() }}
- [ ] 5. Forms submit successfully WITH token
- [ ] 6. Forms REJECT submission WITHOUT token (return 400 error)
- [ ] 7. /api/leads endpoint exempted (external form works)
- [ ] 8. AJAX requests include X-CSRFToken header
- [ ] 9. No breaking changes (all existing features work)
- [ ] 10. Browser console shows no CSRF errors

**Bonus criteria (nice-to-have):**
- [ ] 11. CSRF error page friendly (not generic 400)
- [ ] 12. All templates use CSRF meta tag pattern (consistent)

---

## TESTING INSTRUCTIONS

### **Phase 1: Installation & Configuration**

**Test 1: Flask-WTF installed**
```powershell
cd C:\Users\User\Desktop\gads-data-layer
.\.venv\Scripts\Activate.ps1
python -c "from flask_wtf.csrf import CSRFProtect; print('Flask-WTF OK')"
```
**Expected:** "Flask-WTF OK"

**Test 2: App starts**
```powershell
python -m act_dashboard.app
```
**Expected:** App starts without error, CSRF initialized

---

### **Phase 2: Form Testing**

**Test 3: Form WITH token (should succeed)**
1. Navigate to Recommendations page
2. Click "Accept" on a recommendation
3. **Expected:** Action executes successfully
4. Check browser network tab: POST includes csrf_token field

**Test 4: Form WITHOUT token (should fail)**
1. Open browser DevTools → Console
2. Run JavaScript to submit form without token:
```javascript
fetch('/api/recommendations/123/accept', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'}
}).then(r => console.log(r.status))
```
3. **Expected:** HTTP 400 (Bad Request) - CSRF validation failed

**Test 5: /api/leads still works (exempted)**
```powershell
Invoke-RestMethod -Uri http://localhost:5000/api/leads -Method POST -Headers @{"Content-Type"="application/json"} -Body '{"name":"Test","email":"test@example.com"}'
```
**Expected:** HTTP 200, lead saved (CSRF not required for this endpoint)

---

### **Phase 3: Comprehensive Testing**

**Test 6: All forms functional**
- Recommendations: Accept, Decline, Modify
- Rules: Add, Edit, Delete
- Keywords: Add as Negative, Add as Keyword
- Any other POST actions

**For each form:**
1. Submit form normally (with CSRF token)
2. **Expected:** Action succeeds
3. Check network tab: csrf_token present

**Test 7: Browser console**
- Navigate through all pages
- Perform various actions
- **Expected:** Zero CSRF-related errors

**Test 8: AJAX forms**
- If any forms use fetch/AJAX (likely keyword operations)
- **Expected:** X-CSRFToken header present in request
- **Expected:** Action succeeds

---

### **Edge Cases to Test**

**1. Missing token:**
- Submit form without csrf_token field
- **Expected:** HTTP 400 error

**2. Invalid token:**
- Submit form with wrong csrf_token value
- **Expected:** HTTP 400 error

**3. Expired session:**
- Get CSRF token, wait 1+ hour, submit form
- **Expected:** May fail (token tied to session)
- **Acceptable:** User re-authenticates

**4. Multiple tabs:**
- Open dashboard in two tabs
- Submit form in each tab
- **Expected:** Both work (tokens independent per request)

---

### **Performance**

- No performance impact expected (CSRF is fast)
- Forms should submit as quickly as before
- App startup <5 seconds (unchanged)

---

## POTENTIAL ISSUES

### **Common Pitfalls to Avoid**

**1. Forgot to add token to form**
- **Issue:** Form submission returns 400 error
- **Fix:** Add `{{ csrf_token() }}` to form
- **Detection:** Check browser network tab for csrf_token field

**2. AJAX requests missing header**
- **Issue:** fetch() POST returns 400 error
- **Fix:** Add `'X-CSRFToken': token` to headers
- **Pattern:** Get token from meta tag

**3. Exempted wrong endpoint**
- **Issue:** External form (/api/leads) blocked
- **Fix:** Add `@csrf.exempt` decorator to route
- **Why:** External forms can't get CSRF token

**4. SECRET_KEY not set**
- **Issue:** App crashes on startup
- **Fix:** Set `app.config['SECRET_KEY']` in app.py
- **Note:** May already exist, check first

**5. OPTIONS requests blocked**
- **Issue:** CORS preflight fails
- **Fix:** Flask-WTF automatically exempts OPTIONS
- **Verify:** /api/leads OPTIONS still works

---

### **Known Gotchas**

**From MASTER_KNOWLEDGE_BASE.md:**

**Gotcha 1: /api/leads is public API**
- Must exempt from CSRF (external website calls it)
- Use `@csrf.exempt` decorator

**Gotcha 2: Template inheritance**
- If adding meta tag, put in base_bootstrap.html (inherited by all)
- Don't add to every template individually

**Gotcha 3: JavaScript forms**
- Must read CSRF token from meta tag or hidden field
- Must send in X-CSRFToken header (not body)

---

## HANDOFF REQUIREMENTS

### **Documentation**

**Create 2 files:**

**1. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_36_SUMMARY.md`**
- 150-200 lines
- Overview of CSRF implementation
- Success criteria results
- Testing summary
- Forms protected (list)

**2. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_36_HANDOFF.md`**
- 500-800 lines
- Complete technical details
- Code examples (before/after)
- All testing results
- List of every form protected
- Future considerations

### **Git**

**Prepare commit message (Master Chat will execute):**

```
security(csrf): Add Flask-WTF CSRF protection to all forms

CSRF Protection Implementation (Chat 36)

Added Flask-WTF CSRF protection to prevent cross-site request
forgery attacks on all state-changing forms.

Files Modified:
- requirements.txt: Added Flask-WTF==1.2.1
- act_dashboard/app.py: Initialized CSRFProtect
- act_dashboard/routes/api.py: Exempted /api/leads endpoint
- act_dashboard/templates/*.html: Added csrf_token() to [X] forms

Forms Protected:
- Recommendations: Accept, Decline, Modify
- Rules: Add, Edit, Delete
- Keywords: Add as Negative, Add as Keyword
- [Other forms listed]

Testing:
- All 10 success criteria passing
- Forms submit successfully WITH token
- Forms reject submission WITHOUT token
- /api/leads exempted (external form works)
- Zero browser console errors
- All existing functionality preserved

Time: [X hours]
Chat: 36
Status: Production ready
```

### **Delivery**

1. Copy files to `/mnt/user-data/outputs/`
2. Use `present_files` tool
3. Await Master Chat review

---

## ESTIMATED TIME BREAKDOWN

- **STEP 1:** Read project files + confirm (10 min)
- **STEP 2:** Write 5 questions (5 min)
- **STEP 3:** Wait for answers + build plan (10 min)
- **STEP 4:** Wait for approval (0 min, async)
- **STEP 5A:** Install Flask-WTF (5 min)
- **STEP 5B:** Configure app.py (10 min)
- **STEP 5C:** Add tokens to forms (60-90 min)
- **STEP 5D:** Test all forms (30 min)
- **STEP 6:** Documentation (20 min)

**Total: 2-3 hours** (150-180 minutes)

**Breakdown by phase:**
- Planning: 25 min
- Implementation: 75-105 min
- Testing: 30 min
- Documentation: 20 min

---

## FINAL REMINDERS

**Before starting:**
1. ✅ Upload ONLY this brief (NOT codebase ZIP)
2. ✅ Read all 7 project files from `/mnt/project/`
3. ✅ Confirm understanding explicitly
4. ✅ Write exactly 5 questions
5. ✅ STOP and wait for answers
6. ✅ Write detailed build plan
7. ✅ STOP and wait for approval
8. ✅ Execute ONE step at a time
9. ✅ WAIT for confirmation after each step
10. ✅ Never provide code snippets (complete files only)

**This is an important security improvement. Take time to do it right.**

---

**Ready to start? Upload this brief to the new worker chat.**
