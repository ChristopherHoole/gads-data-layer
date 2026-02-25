# CHAT 32: WEBSITE CONTACT FORM BACKEND

**Estimated Time:** 2-4 hours  
**Dependencies:** Marketing website live at christopherhoole.online  
**Priority:** HIGH (completes website integration)

---

## CONTEXT

### What's Been Done

The marketing website (christopherhoole.online) is live with a fully functional contact form frontend:
- **Location:** Section S12 (Contact Form)
- **Layout:** 2-column (form + "What Happens Next")
- **Fields:** 6 inputs (Name, Company, Role, Looking for, Email, Phone)
- **Frontend:** Complete with validation
- **Current State:** Form submits but has no backend endpoint

### Why This Task Is Needed

Currently, form submissions have nowhere to go. Users fill out the form but nothing happens. This task creates the backend API endpoint to:
1. Receive form submissions from the website
2. Store leads in the A.C.T dashboard database
3. Enable lead management and follow-up
4. Complete the website → dashboard integration

### How It Fits Into the Bigger Picture

This bridges the marketing website (lead generation) with the A.C.T dashboard (client management):
- **Marketing Website:** Generates leads via contact form
- **A.C.T Dashboard:** Stores and manages leads
- **Future:** Display leads in dashboard, send automated follow-ups, track lead status

---

## OBJECTIVE

Create a production-ready API endpoint that receives contact form submissions from christopherhoole.online, validates the data, stores leads in warehouse.duckdb, and returns appropriate success/error responses.

---

## REQUIREMENTS

### 1. Database Schema

**File:** `act_dashboard/warehouse_duckdb.py`

Create `leads` table in warehouse.duckdb:

```sql
CREATE TABLE IF NOT EXISTS leads (
    lead_id INTEGER PRIMARY KEY,
    name VARCHAR NOT NULL,
    company VARCHAR,
    role VARCHAR,
    looking_for VARCHAR,
    email VARCHAR NOT NULL,
    phone VARCHAR,
    source VARCHAR DEFAULT 'website',
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR,
    user_agent VARCHAR,
    status VARCHAR DEFAULT 'new',
    notes TEXT
);
```

**Key Fields:**
- `lead_id`: Auto-increment primary key
- `name`, `email`: Required (NOT NULL)
- `company`, `role`, `looking_for`, `phone`: Optional
- `source`: Default 'website' (future: could be 'referral', 'linkedin', etc.)
- `submitted_at`: Automatic timestamp
- `ip_address`: Track for spam prevention
- `user_agent`: Browser info for analytics
- `status`: 'new', 'contacted', 'qualified', 'converted', 'lost'
- `notes`: For manual annotations

---

### 2. Flask Route

**File:** `act_dashboard/routes/api.py` (or new `leads.py` blueprint)

**Route:** `POST /api/leads`

**Request Format:**
```json
{
  "name": "John Smith",
  "company": "Acme Corp",
  "role": "Marketing Director",
  "looking_for": "PPC management",
  "email": "john.smith@example.com",
  "phone": "+44 20 1234 5678"
}
```

**Response Format (Success):**
```json
{
  "success": true,
  "message": "Thank you! We'll be in touch soon.",
  "lead_id": 123
}
```

**Response Format (Error):**
```json
{
  "success": false,
  "message": "Invalid email address",
  "errors": {
    "email": "Must be a valid email format"
  }
}
```

---

### 3. Validation Rules

**Required Fields:**
- `name`: 2-100 characters
- `email`: Valid email format (regex: `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)

**Optional Fields:**
- `company`: 0-100 characters
- `role`: 0-100 characters
- `looking_for`: 0-500 characters (could be long description)
- `phone`: 0-50 characters (flexible format, international support)

**Sanitization:**
- Strip leading/trailing whitespace
- Remove HTML tags (prevent XSS)
- Escape special characters

---

### 4. CORS Configuration

**File:** `act_dashboard/app.py` (or route file)

Must allow requests from:
- `https://www.christopherhoole.online`
- `https://christopherhoole.online`
- `http://localhost:3000` (for local testing)

**Headers Required:**
```python
Access-Control-Allow-Origin: https://www.christopherhoole.online
Access-Control-Allow-Methods: POST, OPTIONS
Access-Control-Allow-Headers: Content-Type
```

**Handle preflight OPTIONS request** (browser sends this before POST)

---

### 5. Rate Limiting

**Purpose:** Prevent spam submissions

**Strategy:** IP-based rate limiting
- **Limit:** 3 submissions per IP per hour
- **Storage:** In-memory dict or Redis (if available)
- **Response:** HTTP 429 (Too Many Requests) if exceeded

**Implementation:**
```python
# Simple in-memory rate limiter
from collections import defaultdict
from datetime import datetime, timedelta

rate_limit_tracker = defaultdict(list)

def check_rate_limit(ip_address, limit=3, window_hours=1):
    now = datetime.now()
    window_start = now - timedelta(hours=window_hours)
    
    # Remove old entries
    rate_limit_tracker[ip_address] = [
        timestamp for timestamp in rate_limit_tracker[ip_address]
        if timestamp > window_start
    ]
    
    # Check limit
    if len(rate_limit_tracker[ip_address]) >= limit:
        return False
    
    # Add new entry
    rate_limit_tracker[ip_address].append(now)
    return True
```

---

### 6. Email Notification (Optional)

**Purpose:** Notify Christopher when new lead submitted

**Configuration:**
- **From:** A.C.T Dashboard <noreply@christopherhoole.online>
- **To:** chrishoole101@gmail.com
- **Subject:** "New Lead: {name} from {company}"
- **Body:** Plain text with all lead details

**SMTP Setup:**
- Use existing email config from dashboard (if configured)
- **Fallback:** Skip email if not configured (don't block submission)
- Log email send success/failure

**Template:**
```
New Lead Submission

Name: {name}
Company: {company}
Role: {role}
Email: {email}
Phone: {phone}
Looking for: {looking_for}

Submitted: {submitted_at}
IP: {ip_address}
Lead ID: {lead_id}

View in dashboard: http://localhost:5000/leads/{lead_id}
```

---

### 7. Logging

**Log Every Submission:**
- Request received (IP, user agent, timestamp)
- Validation success/failure
- Database insert success/failure
- Email send success/failure (if enabled)
- Rate limit hits

**Example:**
```python
import logging

logger = logging.getLogger(__name__)

logger.info(f"Lead submission received from {ip_address}")
logger.info(f"Lead {lead_id} created: {name} <{email}>")
logger.error(f"Lead submission failed: {error_message}")
```

---

---

## 🔄 MANDATORY WORKFLOW (CHAT_WORKING_RULES.md)

### STEP 1: Read Project Files from Project Knowledge

**Christopher uploads:** ONLY this brief (CHAT_32_BRIEF.md)

**Worker chat reads these files from Project Knowledge:**
- `/mnt/project/PROJECT_ROADMAP.md`
- `/mnt/project/MASTER_KNOWLEDGE_BASE.md`
- `/mnt/project/DETAILED_WORK_LIST.md`
- `/mnt/project/CHAT_WORKING_RULES.md`
- `/mnt/project/WORKFLOW_GUIDE.md`
- `/mnt/project/WORKFLOW_TEMPLATES.md`
- `/mnt/project/DASHBOARD_PROJECT_PLAN.md`

**Worker MUST confirm understanding:**
```
I have read all 7 project files from Project Knowledge:
✅ PROJECT_ROADMAP.md - Current status: 99% complete, M9 complete
✅ MASTER_KNOWLEDGE_BASE.md - Full project history and lessons learned
✅ DETAILED_WORK_LIST.md - Work priorities and estimates
✅ CHAT_WORKING_RULES.md - All 12 mandatory rules understood
✅ WORKFLOW_GUIDE.md - Master + Worker patterns
✅ WORKFLOW_TEMPLATES.md - Brief and handoff templates
✅ DASHBOARD_PROJECT_PLAN.md - Dashboard 3.0 complete

I understand:
- The current project state (99% complete, Dashboard 3.0 done)
- Working rules (especially Rule 2: request current files before editing)
- One step at a time workflow with confirmation at each stage
- 5 Questions + Build Plan workflow before implementation
- No multiple files at once - always wait for confirmation

Ready to proceed to 5 questions.
```

**ONLY after this confirmation**, worker proceeds to STEP 2.

---

### STEP 2: 5 Clarifying Questions (MANDATORY - Rule 5)

Worker MUST:

1. **Write exactly 5 questions** (no more, no less)
2. **Send to user** with header: `"5 QUESTIONS FOR MASTER CHAT"`
3. **STOP - Wait for answers**

**Question Format:**
```
5 QUESTIONS FOR MASTER CHAT

Q1. [CATEGORY] Question text here?
Q2. [CATEGORY] Question text here?
Q3. [CATEGORY] Question text here?
Q4. [CATEGORY] Question text here?
Q5. [CATEGORY] Question text here?

Waiting for Master Chat answers before proceeding.
```

**Categories:** [DATABASE], [ROUTE], [CORS], [EMAIL], [DEPLOYMENT], [TESTING], [SECURITY]

**Flow:**
- User copies questions → pastes in Master Chat
- Master provides answers
- User pastes answers back to worker

---

### STEP 3: Detailed Build Plan (MANDATORY - Rule 5)

After receiving answers, worker MUST:

1. **Create detailed build plan**
2. **Send to user** with header: `"DETAILED BUILD PLAN FOR MASTER CHAT REVIEW"`
3. **STOP - Wait for approval**

**Build Plan Format:**
```
DETAILED BUILD PLAN FOR MASTER CHAT REVIEW

Files to create/modify:
- [Full Windows path] — [what changes]

Step-by-step implementation:
STEP A: Database Schema (~15 min)
  - Request current warehouse_duckdb.py
  - Add leads table creation
  - Test table creation
  - Wait for confirmation

STEP B: Flask Route (~30 min)
  - Request current routes/api.py (or create new leads.py)
  - Add POST /api/leads route
  - Add validation logic
  - Test route responds
  - Wait for confirmation

STEP C: CORS Configuration (~20 min)
  - Request current app.py
  - Add CORS headers
  - Test preflight request
  - Wait for confirmation

[etc...]

Total estimated time: X minutes
Risks / unknowns: [Any remaining concerns]

Waiting for Master Chat approval before starting.
```

**Flow:**
- User copies build plan → pastes in Master Chat
- Master reviews and approves (or requests changes)
- User pastes approval back to worker

---

### STEP 4: Implementation (ONE STEP AT A TIME)

**CRITICAL WORKFLOW RULE:**
- Execute ONE step from build plan
- WAIT for Christopher's confirmation
- Only then proceed to next step

**Example Step Execution:**

```
STEP A STARTING: Database Schema

I need the current version of warehouse_duckdb.py to add the leads table.

Please upload:
- File: warehouse_duckdb.py
- Location: C:\Users\User\Desktop\gads-data-layer\act_dashboard\warehouse_duckdb.py

After upload, I will:
1. Add leads table creation code
2. Provide complete updated file
3. Wait for your confirmation before moving to STEP B
```

**After each step:**
```
STEP A COMPLETE ✅

Deliverable: Updated warehouse_duckdb.py with leads table
[Provides download link]

Test this step:
[Specific test command]

Reply "Confirmed" to proceed to STEP B, or report any issues.

[STOP - WAIT FOR CONFIRMATION]
```

**NEVER:**
- ❌ Do multiple steps in one response
- ❌ Proceed without confirmation
- ❌ Assume files haven't changed
- ❌ Use cached versions of files

**ALWAYS:**
- ✅ Request current file before editing
- ✅ Complete ONE full file (not snippets)
- ✅ Wait for confirmation
- ✅ Test each step before proceeding

---

### STEP 5: Completion & Documentation

After all steps confirmed working:

1. Create CHAT_32_SUMMARY.md (150-200 lines)
2. Create CHAT_32_HANDOFF.md (500-800 lines)
3. Send both to Master Chat for review
4. After approval, prepare git commit message
5. Master Chat updates project documentation

---

## WORKER CHAT CONFIRMATION REQUIRED

**Before starting ANY work, worker chat MUST explicitly confirm:**

```
✅ WORKFLOW UNDERSTOOD:

1. I will read all 7 project files from Project Knowledge
2. I will confirm I've read and understood them
3. I will write 5 questions and STOP
4. I will wait for answers from Master Chat
5. I will write detailed build plan and STOP
6. I will wait for approval from Master Chat
7. I will execute ONE step at a time
8. I will request current file versions before editing
9. I will provide complete files (not snippets)
10. I will WAIT for confirmation after each step
11. I will NEVER proceed without confirmation
12. I will create comprehensive documentation at end

I understand this is a multi-step process with multiple STOP points.
I will not rush ahead or combine steps.

Ready to begin by reading Project Knowledge files.
```

---

## REFERENCE FILES

**Similar Work:**
- `act_dashboard/routes/recommendations.py` - Example POST routes with validation
- `act_dashboard/routes/keywords.py` - POST routes from Chat 30b (recent example)
- `act_dashboard/warehouse_duckdb.py` - Database table creation patterns

**CORS Examples:**
- Flask-CORS library (if installed)
- Manual CORS headers (if not installed)

**Validation Patterns:**
- Check existing routes for validation helpers
- Python `re` module for email regex
- `bleach` library for HTML sanitization (if available)

---

## SUCCESS CRITERIA

All 12 criteria must pass:

- [ ] 1. `leads` table created in warehouse.duckdb with correct schema
- [ ] 2. POST /api/leads route responds to requests
- [ ] 3. CORS headers allow requests from christopherhoole.online
- [ ] 4. Required field validation works (name, email)
- [ ] 5. Email format validation rejects invalid emails
- [ ] 6. Valid submission stores lead in database
- [ ] 7. Database returns lead_id on successful insert
- [ ] 8. Success response returns JSON with lead_id
- [ ] 9. Error response returns JSON with clear error messages
- [ ] 10. Rate limiting blocks excessive submissions (3/hour per IP)
- [ ] 11. All submissions logged to console
- [ ] 12. OPTIONS preflight request handled correctly

**Bonus (Optional):**
- [ ] 13. Email notification sent to Christopher
- [ ] 14. Duplicate email detection (warn if email exists)
- [ ] 15. Lead status tracking (new → contacted → qualified)

---

## TESTING INSTRUCTIONS

### Phase 1: Local API Testing (curl/Postman)

**Test 1: Valid Submission**
```bash
curl -X POST http://localhost:5000/api/leads \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "company": "Test Company",
    "role": "Marketing Manager",
    "looking_for": "PPC management services",
    "email": "test@example.com",
    "phone": "+44 20 1234 5678"
  }'
```

**Expected:** HTTP 200, JSON `{"success": true, "lead_id": 1}`

**Test 2: Missing Required Field**
```bash
curl -X POST http://localhost:5000/api/leads \
  -H "Content-Type: application/json" \
  -d '{
    "company": "Test Company",
    "email": "test@example.com"
  }'
```

**Expected:** HTTP 400, JSON `{"success": false, "errors": {"name": "Required field"}}`

**Test 3: Invalid Email**
```bash
curl -X POST http://localhost:5000/api/leads \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "not-an-email"
  }'
```

**Expected:** HTTP 400, JSON `{"success": false, "errors": {"email": "Invalid email format"}}`

**Test 4: Rate Limiting**
```bash
# Run same curl 4 times rapidly
```

**Expected:** First 3 succeed, 4th returns HTTP 429

**Test 5: CORS Preflight**
```bash
curl -X OPTIONS http://localhost:5000/api/leads \
  -H "Origin: https://www.christopherhoole.online" \
  -H "Access-Control-Request-Method: POST"
```

**Expected:** HTTP 200 with CORS headers

---

### Phase 2: Database Verification

**Check table created:**
```python
import duckdb
conn = duckdb.connect('warehouse.duckdb')
result = conn.execute("SELECT * FROM leads").fetchall()
print(result)
conn.close()
```

**Expected:** Table exists, contains test submissions

---

### Phase 3: Website Integration Testing

**Update Frontend (Next.js):**

File: `act-website/components/ContactForm.tsx`

Change:
```typescript
// FROM:
const response = await fetch('/api/contact', { ... });

// TO:
const response = await fetch('http://localhost:5000/api/leads', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(formData)
});
```

**Test from Website:**
1. Open http://localhost:3000 (Next.js dev server)
2. Fill out contact form
3. Click submit
4. **Expected:** Success message, lead appears in database

**Test from Production:**
1. Open https://www.christopherhoole.online/contact
2. Fill out contact form with real data
3. Click submit
4. **Expected:** Success message, lead appears in database

---

### Phase 4: Production Deployment

**Update Website Environment Variables:**

File: `.env.production` (or Vercel settings)

```
NEXT_PUBLIC_API_URL=https://your-act-dashboard-url.com
```

Update fetch URL:
```typescript
const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/leads`, ...);
```

**Deploy A.C.T Dashboard:**
- Ensure /api/leads is accessible publicly
- Update CORS to allow production domain
- Test submission from live website

---

## POTENTIAL ISSUES

### Issue 1: CORS Blocked
**Symptoms:** Browser console shows "CORS policy" error  
**Cause:** Missing/incorrect CORS headers  
**Fix:** Add proper headers, handle OPTIONS preflight  
**Test:** Check browser Network tab for preflight request

### Issue 2: Rate Limit Too Strict
**Symptoms:** Legitimate users blocked  
**Cause:** Rate limit window too short  
**Fix:** Increase to 5 submissions per hour, or extend window to 24 hours  
**Alternative:** Cookie-based tracking instead of IP

### Issue 3: Email Validation Too Strict
**Symptoms:** Valid emails rejected (e.g., `user+tag@example.com`)  
**Cause:** Regex doesn't handle all valid formats  
**Fix:** Use more permissive regex: `^[^\s@]+@[^\s@]+\.[^\s@]+$`  
**Alternative:** Use `email-validator` library

### Issue 4: Database Connection Error
**Symptoms:** "Unable to open database" error  
**Cause:** warehouse.duckdb locked by another process  
**Fix:** Close existing connections, use read-write mode  
**Prevention:** Connection pooling or close connections promptly

### Issue 5: Spam Submissions
**Symptoms:** Dozens of fake leads  
**Cause:** Bot found the endpoint  
**Fix:** Add honeypot field, reCAPTCHA, or stricter rate limiting  
**Future:** Implement reCAPTCHA on frontend

---

## HANDOFF REQUIREMENTS

**Documentation:**
- Create CHAT_32_SUMMARY.md (150-200 lines)
- Create CHAT_32_HANDOFF.md (500-800 lines)
- Include all testing results
- Document any issues encountered

**Git Commit:**
```
feat(api): Add contact form backend endpoint

Contact Form Backend - Complete

Features:
- POST /api/leads endpoint
- Lead validation (name, email required)
- CORS support for christopherhoole.online
- Rate limiting (3/hour per IP)
- Database storage in leads table
- Email notifications (optional)

Files:
- warehouse_duckdb.py: Added leads table
- routes/leads.py: New blueprint (or routes/api.py updated)
- app.py: CORS configuration

Testing:
- All 12 success criteria passing
- curl testing complete
- Website integration tested
- Production deployment tested

Time: X hours
Chat: 32
Status: Complete
```

**Files to Commit:**
- `act_dashboard/warehouse_duckdb.py` (or migration script)
- `act_dashboard/routes/leads.py` (or api.py)
- `act_dashboard/routes/__init__.py` (if new blueprint)
- `act_dashboard/app.py` (CORS config)
- `docs/CHAT_32_SUMMARY.md`
- `docs/CHAT_32_HANDOFF.md`

---

## ESTIMATED TIME BREAKDOWN

- Database schema: 15 min
- Flask route creation: 30 min
- Validation logic: 30 min
- CORS configuration: 20 min
- Rate limiting: 30 min
- Testing (local): 30 min
- Email notification (optional): 30 min
- Website integration: 20 min
- Testing (production): 15 min
- Documentation: 20 min

**Total: 2-4 hours** (depends on optional email feature)

---

## DEPLOYMENT NOTES

**Local Development:**
- Flask app runs on localhost:5000
- Website runs on localhost:3000
- CORS must allow localhost:3000

**Production:**
- A.C.T dashboard needs public URL (current: localhost only?)
- CORS must allow christopherhoole.online
- Consider HTTPS requirement
- Database must be writable by web server

**Security:**
- Never expose database credentials in frontend
- Validate all inputs server-side (never trust client)
- Rate limit aggressively if spam becomes issue
- Consider adding CAPTCHA in future

---

## FUTURE ENHANCEMENTS

**Short-term:**
- Lead management UI in dashboard (view, edit, status)
- Automated follow-up emails (drip campaign)
- Lead scoring (based on company size, role)

**Medium-term:**
- Integration with CRM (HubSpot, Salesforce)
- Lead activity tracking (pages viewed, time on site)
- A/B testing different form fields

**Long-term:**
- Multi-step form (progressive disclosure)
- Calendar integration (book consultation)
- Live chat fallback

---

**Ready to start?**

**Christopher uploads:** ONLY `CHAT_32_BRIEF.md` (this file) to new worker chat

**Worker chat will:**
1. Read all 7 project files from Project Knowledge
2. Confirm understanding of all files and workflow
3. Write 5 clarifying questions → send to Master Chat
4. Wait for answers
5. Write detailed build plan → send to Master Chat for review
6. Wait for approval
7. Execute implementation ONE STEP AT A TIME with confirmation at each stage
8. Request specific code files as needed (never use cached versions)
9. Create comprehensive documentation at end

**Key Success Factors:**
- Worker confirms it has read and understood all project files
- Worker confirms it understands the one-step-at-a-time workflow
- Worker STOPS at every checkpoint and waits for confirmation
- Worker requests current file versions before any edits
- Worker provides complete files (never snippets)

**Time Estimate:** 2-4 hours (with proper step-by-step execution)
