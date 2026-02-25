# CHAT 39: DEPLOY /API/LEADS ENDPOINT

**Estimated Time:** 2-3 hours
**Dependencies:** Chat 32 complete (backend endpoint exists)
**Priority:** CRITICAL (required before advertising website)

---

## 🚨 MANDATORY WORKFLOW - READ THIS FIRST

This chat follows the **15-step worker chat workflow** from WORKFLOW_GUIDE.md.

**You MUST complete these steps in order:**

### **STEP 1: Read Project Knowledge + Confirm Understanding**

1. Read all 8 files from `/mnt/project/`:
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
   - Current project state (Chat 32: /api/leads endpoint created)
   - Rule 2 (CRITICAL): Always request current file version before editing
   - One step at a time workflow with confirmation
   - Complete files only (never snippets)
   - Full Windows paths: `C:\Users\User\Desktop\gads-data-layer\...`

**Template confirmation message:**
```
CONFIRMATION: ALL PROJECT FILES READ

I have read all 8 project files from Project Knowledge:
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
* Task: Deploy /api/leads endpoint to make it publicly accessible
* Rule 2: Always request current file before editing
* One step at a time with confirmation
* Complete files only, full Windows paths
* Tech stack: Flask, DuckDB, Vercel (website)

Ready to proceed to 5 questions for Master Chat.
```

---

### **STEP 2: 5 Clarifying Questions**

After reading all project files, write exactly **5 questions** for Master Chat.

**Question categories:**
- `[DEPLOYMENT]` - Where to deploy (Vercel Functions vs full hosting)
- `[DATABASE]` - How to handle DuckDB in cloud environment
- `[CORS]` - How to configure cross-origin requests
- `[EXISTING]` - What exists from Chat 32
- `[TESTING]` - How to test before connecting website

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

Deployment approach: [Option A/B/C based on Master answers]

Files to create/modify:
- C:\Users\User\Desktop\gads-data-layer\[path]\[file] — [what changes]

Step-by-step implementation:
STEP A: [Task description] (~X min)
  - [Specific action]
  
STEP B: [Task description] (~X min)
  - [Specific action]

STEP C: Test locally (~X min)
  - [Test command]

STEP D: Deploy to cloud (~X min)
  - [Deployment command]

STEP E: Test live endpoint (~X min)
  - [Test with curl/Postman]

STEP F: Documentation (~X min)

Total estimated time: [X] minutes
Risks / unknowns: [Any concerns]

Waiting for Master Chat approval before starting implementation.
```

**⚠️ STOP HERE - Wait for Master Chat approval**

---

### **STEP 4: Implementation (ONE STEP AT A TIME)**

After Master Chat approves build plan, execute **ONE STEP AT A TIME**.

**For each step:**

1. **Request current file version (if editing existing file):**
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

1. Create `CHAT_39_SUMMARY.md` (200-300 lines)
2. Create `CHAT_39_HANDOFF.md` (800-1200 lines)
3. Send both to Master Chat for review

**Do NOT commit to git - Master Chat handles commits.**

---

## CONTEXT

### **What Is the Problem?**

**Current state:**
- ✅ Website live: https://www.christopherhoole.online
- ✅ Contact form exists on website (frontend)
- ✅ /api/leads endpoint exists in Flask (backend, Chat 32)
- ❌ Flask runs on localhost:5000 (not publicly accessible)
- ❌ Website can't POST to localhost from Vercel

**The gap:**
```
Website (Vercel)          Flask Dashboard (localhost)
    |                              |
    |---> POST to localhost? ----> X (can't reach)
    
PUBLIC INTERNET               PRIVATE LAPTOP
```

**Desired state:**
```
Website (Vercel)          API Endpoint (Cloud)
    |                         |
    |---> POST ✅ --------->  /api/leads
                              (publicly accessible)
```

---

### **Why This Matters**

**Business context:**
- Christopher plans to advertise the website
- Website needs to capture leads
- Without working form, leads are lost
- This blocks all advertising spend

**This is CRITICAL PATH work.**

---

## OBJECTIVE

Deploy the `/api/leads` Flask endpoint to a publicly accessible URL so the website contact form can submit leads.

---

## REQUIREMENTS

### **Functional Requirements**

**1. Public API endpoint**
- URL: `https://[something].com/api/leads`
- Method: POST
- Accepts: JSON payload from contact form
- Returns: JSON success/error response

**2. CORS configuration**
- Allow requests from: `https://christopherhoole.online` and `https://www.christopherhoole.online`
- Allow method: POST
- Allow headers: Content-Type, X-CSRFToken (if needed)

**3. Data storage**
- Write to DuckDB `leads` table
- Handle database in cloud environment

**4. Error handling**
- Rate limiting (prevent spam)
- Validation (all required fields)
- Clear error messages

---

### **Deployment Options**

**Option A: Vercel Serverless Functions (RECOMMENDED)**

**Pros:**
- ✅ Same platform as website (Vercel)
- ✅ Free tier sufficient
- ✅ Automatic HTTPS
- ✅ Fast deployment
- ✅ CORS easy to configure

**Cons:**
- ⚠️ DuckDB file storage tricky (need persistent volume or cloud DB)
- ⚠️ Serverless = stateless (can't use local file)

**Implementation:**
```
/api/leads.py  (Vercel Function)
    ↓
  Store leads in:
  - Supabase (PostgreSQL)
  - PlanetScale (MySQL)
  - Google Sheets (simple)
  - OR Vercel Blob Storage + DuckDB
```

---

**Option B: Railway/Render (Full Flask App)**

**Pros:**
- ✅ Deploy entire Flask app
- ✅ DuckDB works natively (persistent disk)
- ✅ No code changes needed
- ✅ Simple deployment

**Cons:**
- ⚠️ More complex than just /api/leads
- ⚠️ Paid tier may be needed
- ⚠️ Overkill for one endpoint

**Implementation:**
```
Deploy full Flask app to Railway/Render
    ↓
  /api/leads endpoint works as-is
  warehouse.duckdb on persistent disk
```

---

**Option C: AWS Lambda + API Gateway**

**Pros:**
- ✅ Industry standard
- ✅ Free tier generous

**Cons:**
- ❌ Complex setup (IAM, permissions, etc.)
- ❌ Overkill for this use case

**NOT RECOMMENDED for this task.**

---

### **Recommended Approach**

**HYBRID: Vercel Function + Simple Storage**

**Phase 1 (This Chat):**
- Deploy /api/leads as Vercel Function
- Store leads in simple JSON file on Vercel Blob Storage
- OR store leads in Google Sheets (dead simple)

**Phase 2 (Later):**
- Migrate to proper database when needed
- Full dashboard deployment for client access

**Why this works:**
- Gets website operational ASAP
- Minimal complexity
- Easy to test
- Can migrate later

---

## DELIVERABLES

### **Required Files**

**1. Vercel Function: `/api/leads.py` or `/api/leads.js`**

**Location:** `C:\Users\User\Desktop\act-website\api\leads.py`

**Purpose:** Handle POST requests from contact form

**Example structure (Python):**
```python
from http.server import BaseHTTPRequestHandler
import json
import os
from datetime import datetime

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Parse request
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        data = json.loads(body)
        
        # Validate
        required = ['name', 'email', 'company', 'role', 'looking_for', 'phone']
        if not all(k in data for k in required):
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Missing fields'}).encode())
            return
        
        # Store (TODO: implement storage)
        # For now, log to Vercel logs
        print(f"Lead received: {data['email']}")
        
        # Send success
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', 'https://www.christopherhoole.online')
        self.end_headers()
        self.wfile.write(json.dumps({'success': True}).encode())
```

---

**2. Vercel Configuration: `vercel.json`**

**Location:** `C:\Users\User\Desktop\act-website\vercel.json`

**Purpose:** Configure CORS, routes, environment

**Example:**
```json
{
  "headers": [
    {
      "source": "/api/leads",
      "headers": [
        { "key": "Access-Control-Allow-Origin", "value": "https://www.christopherhoole.online" },
        { "key": "Access-Control-Allow-Methods", "value": "POST, OPTIONS" },
        { "key": "Access-Control-Allow-Headers", "value": "Content-Type" }
      ]
    }
  ]
}
```

---

**3. Storage Solution (Choose One)**

**Option A: Vercel Blob Storage**
- Store leads as JSON in Vercel Blob
- Append new leads to blob
- Simple, built into Vercel

**Option B: Google Sheets**
- Use Google Sheets API
- Append row for each lead
- Dead simple, no database needed

**Option C: Supabase (PostgreSQL)**
- Free tier: 500MB database
- SQL queries
- Most robust

**Recommendation:** Start with Google Sheets (simplest), migrate later if needed.

---

### **Technical Constraints**

**Must maintain:**
- ✅ All fields from Chat 32 (name, email, company, role, looking_for, phone)
- ✅ Timestamp on each lead
- ✅ Rate limiting (max 10 submissions per hour per IP)
- ✅ Email validation
- ✅ CORS only from christopherhoole.online

**Must NOT:**
- ❌ Expose API publicly without rate limiting
- ❌ Store sensitive data unencrypted
- ❌ Allow cross-origin requests from anywhere

---

## SUCCESS CRITERIA

**All 10 criteria must pass for approval:**

- [ ] 1. /api/leads endpoint deployed and publicly accessible
- [ ] 2. POST request from Postman/curl returns 200 OK
- [ ] 3. CORS headers allow requests from christopherhoole.online
- [ ] 4. All 6 required fields validated
- [ ] 5. Missing field returns 400 error with clear message
- [ ] 6. Leads stored somewhere retrievable
- [ ] 7. Rate limiting prevents spam (max 10/hour per IP)
- [ ] 8. Invalid email returns 400 error
- [ ] 9. Public URL documented (e.g., https://act-website.vercel.app/api/leads)
- [ ] 10. No errors in Vercel logs

**Bonus criteria (nice-to-have):**
- [ ] 11. Email notification on new lead (SMTP)
- [ ] 12. Honeypot field to catch bots

---

## TESTING INSTRUCTIONS

### **Phase 1: Local Testing (Before Deployment)**

**Test 1: Validate endpoint logic**
```powershell
# If testing locally first
cd C:\Users\User\Desktop\act-website
python api/leads.py
```

**Expected:** No syntax errors

---

### **Phase 2: Deployment Testing**

**Test 2: Deploy to Vercel**
```powershell
cd C:\Users\User\Desktop\act-website
npx vercel --prod
```

**Expected:** 
```
✅ Deployed to production
🔗 https://act-website-fawn.vercel.app
```

---

### **Phase 3: Endpoint Testing**

**Test 3: curl test (valid request)**
```powershell
curl -X POST https://act-website-fawn.vercel.app/api/leads `
  -H "Content-Type: application/json" `
  -d '{\"name\":\"Test User\",\"email\":\"test@example.com\",\"company\":\"Test Co\",\"role\":\"CEO\",\"looking_for\":\"PPC Help\",\"phone\":\"+44 1234 567890\"}'
```

**Expected:**
```json
{"success": true}
```

**Test 4: curl test (missing field)**
```powershell
curl -X POST https://act-website-fawn.vercel.app/api/leads `
  -H "Content-Type: application/json" `
  -d '{\"name\":\"Test User\",\"email\":\"test@example.com\"}'
```

**Expected:**
```json
{"error": "Missing required fields"}
```

**Test 5: curl test (invalid email)**
```powershell
curl -X POST https://act-website-fawn.vercel.app/api/leads `
  -H "Content-Type: application/json" `
  -d '{\"name\":\"Test\",\"email\":\"not-an-email\",\"company\":\"Test\",\"role\":\"CEO\",\"looking_for\":\"Help\",\"phone\":\"123\"}'
```

**Expected:**
```json
{"error": "Invalid email address"}
```

---

### **Phase 4: CORS Testing**

**Test 6: Browser console test**
```javascript
// Open https://www.christopherhoole.online
// Open DevTools Console
// Run:
fetch('https://act-website-fawn.vercel.app/api/leads', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    name: 'Test User',
    email: 'test@example.com',
    company: 'Test Co',
    role: 'CEO',
    looking_for: 'PPC Help',
    phone: '+44 1234 567890'
  })
})
.then(r => r.json())
.then(d => console.log('Success:', d))
.catch(e => console.error('Error:', e));
```

**Expected:** `Success: {success: true}`

**NOT:** CORS error

---

### **Phase 5: Storage Verification**

**Test 7: Verify lead was stored**

**If using Google Sheets:**
- Open sheet
- Verify new row added

**If using Vercel Blob:**
```powershell
# Check Vercel dashboard → Storage → Blob
# Verify file exists
```

**If using Supabase:**
```sql
SELECT * FROM leads ORDER BY created_at DESC LIMIT 5;
```

---

### **Edge Cases to Test**

**1. Rate limiting:**
- Submit 11 requests in 1 hour
- **Expected:** 11th request returns 429 Too Many Requests

**2. Very long input:**
- Submit 1000-character name
- **Expected:** Either truncated or rejected with 400

**3. Special characters:**
- Submit name with emoji: "Test 🚀 User"
- **Expected:** Accepted and stored correctly

**4. Concurrent requests:**
- Submit 5 requests simultaneously
- **Expected:** All processed, no data corruption

---

## POTENTIAL ISSUES

### **Common Pitfalls to Avoid**

**1. CORS misconfiguration**
- **Issue:** Wildcard `Access-Control-Allow-Origin: *` is insecure
- **Fix:** Explicitly allow only christopherhoole.online
- **Detection:** Test from different origin, should fail

**2. DuckDB in serverless**
- **Issue:** Serverless functions are stateless, can't use local file
- **Fix:** Use alternative storage (Google Sheets, Supabase, etc.)
- **Detection:** Data not persisting between requests

**3. Missing CSRF exemption**
- **Issue:** If /api/leads has CSRF protection, external requests fail
- **Fix:** Exempt /api/leads from CSRF (already done in Chat 36)
- **Detection:** 400 error with "CSRF token missing"

**4. Rate limiting too strict**
- **Issue:** Legitimate users blocked
- **Fix:** Set reasonable limit (10/hour is safe)
- **Detection:** Test user can't submit after 10 tries

**5. Email validation too strict**
- **Issue:** Valid emails rejected (e.g., user@company.co.uk)
- **Fix:** Use standard regex or library
- **Detection:** Test with various email formats

---

### **Known Gotchas**

**Gotcha 1: Vercel Functions use different Python version**
- Vercel uses Python 3.9 by default
- Your local env might be 3.11
- Check compatibility

**Gotcha 2: Environment variables**
- If using Supabase/API keys
- Must set in Vercel dashboard → Settings → Environment Variables
- Can't use local .env file

**Gotcha 3: Cold starts**
- First request after idle may take 1-2 seconds
- This is normal for serverless
- Not a bug

**Gotcha 4: File paths in Vercel Functions**
- Can't use absolute paths like `C:\...`
- Must use relative paths or `/tmp/`
- DuckDB file path won't work

---

## HANDOFF REQUIREMENTS

### **Documentation**

**Create 2 files:**

**1. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_39_SUMMARY.md`**
- 200-300 lines
- Deployment approach chosen
- Public URL for API endpoint
- Storage solution used
- All 10 success criteria results
- Testing screenshots

**2. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_39_HANDOFF.md`**
- 800-1200 lines
- Complete technical details
- Deployment commands used
- Vercel configuration
- Storage setup steps
- All testing results with curl outputs
- Issues encountered + solutions
- Next steps (Chat 40: Website form integration)

### **Git**

**Prepare commit message (Master Chat will execute):**

```
feat(api): Deploy /api/leads endpoint to Vercel

Website Contact Form API (Chat 39)

Deployed Flask /api/leads endpoint as Vercel serverless function to
enable website contact form submissions from christopherhoole.online.

Files Created:
- act-website/api/leads.py: Serverless function handler
- act-website/vercel.json: CORS configuration

Changes:
- POST endpoint accepts: name, email, company, role, looking_for, phone
- CORS configured for christopherhoole.online
- Rate limiting: 10 requests/hour per IP
- Storage: [Google Sheets / Vercel Blob / Supabase]
- Email validation with regex
- Error handling for missing/invalid fields

Testing:
- All 10 success criteria passing
- curl tests: valid request ✅, missing field ✅, invalid email ✅
- CORS test from browser console ✅
- Rate limiting verified ✅
- Leads stored and retrievable ✅

Deployment:
- URL: https://act-website-fawn.vercel.app/api/leads
- Method: POST
- Headers: Content-Type: application/json
- CORS: christopherhoole.online only

Next: Chat 40 (update website ContactForm.tsx to use this endpoint)

Time: [X hours]
Chat: 39
Status: Production ready
```

### **Delivery**

1. Copy files to `/mnt/user-data/outputs/`
2. Use `present_files` tool
3. Provide public API URL for testing
4. Await Master Chat review

---

## ESTIMATED TIME BREAKDOWN

**Approach 1: Vercel Function + Google Sheets (SIMPLEST)**
- Setup Google Sheets API: 30 min
- Create Vercel Function: 30 min
- Configure CORS: 15 min
- Deploy to Vercel: 15 min
- Test endpoint: 20 min
- Documentation: 30 min
**Total: 2.5 hours**

**Approach 2: Vercel Function + Supabase (ROBUST)**
- Setup Supabase account: 20 min
- Create table schema: 15 min
- Create Vercel Function: 30 min
- Configure CORS: 15 min
- Deploy to Vercel: 15 min
- Test endpoint: 20 min
- Documentation: 30 min
**Total: 2.5 hours**

**Approach 3: Railway Full Flask Deploy (OVERKILL)**
- Setup Railway account: 15 min
- Configure deployment: 30 min
- Deploy Flask app: 20 min
- Test endpoint: 20 min
- Documentation: 30 min
**Total: 2 hours**

**Recommended: Approach 1 (Google Sheets) - Dead simple, no database setup**

---

## FINAL REMINDERS

**Before starting:**
1. ✅ Read all 8 project files from `/mnt/project/`
2. ✅ Confirm understanding explicitly
3. ✅ Write exactly 5 questions
4. ✅ STOP and wait for answers
5. ✅ Write detailed build plan
6. ✅ STOP and wait for approval
7. ✅ Execute ONE step at a time
8. ✅ WAIT for confirmation after each step
9. ✅ Never provide code snippets (complete files only)

**This enables the website to capture leads before advertising.**

---

**Ready to start? Upload this brief to the new worker chat.**
