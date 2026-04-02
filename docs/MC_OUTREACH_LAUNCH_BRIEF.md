# MC Outreach Launch — Master Brief
**Session:** MC Outreach Launch
**Date:** 2026-03-30
**Objective:** Get the cold outreach system fully operational and sending 20 emails/day to UK digital marketing recruiters and agencies by end of week.

---

## CRITICAL: BROWSER VERIFICATION REQUIRED

Every change made during this session MUST be visually verified in the browser before moving on. After each task:
- Run the Flask app and open the relevant page
- Visually confirm the UI renders correctly
- Test all interactions
- Check the browser console for JavaScript errors

---

## CRITICAL: ONE TASK AT A TIME

Complete each task fully and get confirmation before starting the next. Do NOT work on multiple tasks simultaneously.

---

## TASK 1: Outreach System Health Check

Run the entire outreach system end-to-end and document what works and what's broken.

**Test each component:**
- Flask app starts without errors on outreach routes
- Leads page: can create, edit, delete a lead
- Queue page: can compose an email for a lead
- Templates page: can create, edit, select a template
- Email sending: send a real test email from chris@christopherhoole.com via SMTP — confirm it arrives
- Sent page: sent email appears in the list
- Replies page: check if inbox polling picks up a test reply
- Analytics page: loads without errors
- Tracking pixels: open/click tracking functional
- Queue scheduling: scheduled emails fire at correct time

**Output:** A list of what's working and what's broken. Fix critical blockers before moving on. Non-critical issues get noted for later.

**Browser-verify:** Every page loads, every action works.

---

## TASK 2: Email Signature Setup

Configure a professional email signature for chris@christopherhoole.com on all outgoing emails.

**Signature should include:**
- Christopher Hoole
- Google Ads Specialist
- christopherhoole.com (hyperlinked)
- Phone number (if Christopher wants to include)
- Clean, minimal HTML formatting — not an image-heavy signature

**Browser-verify:** Send a test email, confirm signature appears correctly in Gmail/Outlook.

---

## TASK 3: Template System — Add Merge Fields

Upgrade the template system to support merge field placeholders that auto-fill from lead data when composing an email.

**Merge fields to support:**
- `{contact_name}` — lead's first name or full name
- `{company_name}` — company/agency name
- `{role_title}` — job title if known
- `{location}` — lead's location/city

**How it should work:**
1. When creating/editing a template, user can type merge fields directly into the body text
2. A helper showing available merge fields should be visible (small reference list)
3. When a template is selected in the Queue compose view, merge fields auto-replace with the lead's data
4. If a merge field has no matching data, it should highlight/flag so the user can fill it manually before sending
5. Preview should show the merged version before sending

**Browser-verify:** Create a template with merge fields, select it for a lead, confirm fields auto-fill correctly. Test with missing data — confirm it flags the gaps.

---

## TASK 4: Create Recruiter Email Template

Create an email template for cold outreach to UK digital marketing recruiters.

**Audience:** Recruiters who place PPC/Google Ads/digital marketing roles

**Tone:** Professional but approachable. Not desperate. Positioning as a high-value specialist who's available.

**Key messages:**
- Available for all PPC roles (contract, freelance, permanent, on-site, remote)
- 10+ years Google Ads experience
- Specialist in Search, Shopping, Performance Max
- Built ACT (Ads Control Tower) — a proprietary optimization platform with 75 rules, 99 flags
- Currently managing/consulting across multiple accounts
- Based in UK, flexible on working arrangements
- Link to christopherhoole.com for full portfolio

**Template should use merge fields:** `{contact_name}`, `{company_name}`

**Keep it short** — 4-6 sentences max. Recruiters scan emails fast. The goal is to get a conversation started, not tell the whole story.

**Browser-verify:** Template appears in the Templates page, merge fields work when composing.

---

## TASK 5: Create Agency Email Template

Create an email template for cold outreach to UK digital marketing agencies.

**Audience:** Agency owners, directors, or head of PPC at digital marketing agencies

**Tone:** Peer-to-peer professional. Positioning as someone who can add immediate value.

**Key messages:**
- Available for PPC specialist work (overflow, white-label, contract, or full-time)
- Deep specialism in Google Ads (Search, Shopping, PMax)
- Can handle account audits, restructures, ongoing management
- Built a proprietary optimization platform (ACT) — differentiator
- Flexible engagement models (day rate, retainer, project-based)
- Link to christopherhoole.com

**Template should use merge fields:** `{contact_name}`, `{company_name}`

**Keep it short** — 4-6 sentences max. The goal is to start a conversation.

**Browser-verify:** Template appears in the Templates page, merge fields work when composing.

---

## TASK 6: Apollo.io Integration

Connect Apollo.io API to the ACT outreach system for importing leads with verified email addresses.

**Setup:**
- Start with free tier (50 credits/month) to prove the system
- API key stored in config (not hardcoded)
- Integration should work with both free and paid tiers

**Features to build:**
- "Import from Apollo" button on the Leads page
- Search Apollo by: job title, company name, location, industry
- Display results in a list with: name, title, company, email, phone, location
- Select contacts to import → creates leads in the outreach_leads table
- Duplicate detection — don't import leads that already exist (match by email)
- Track Apollo credits used

**Browser-verify:** Search Apollo for "PPC recruiter UK", see results, import a contact, confirm it appears in Leads.

---

## TASK 7: Reply Inbox Polling — Live Test

Test the existing reply inbox polling code with the live chris@christopherhoole.com inbox.

**Test steps:**
1. Send a test outreach email
2. Reply to it from a different email address
3. Confirm the reply appears on the Replies page
4. Test mark read/unread
5. Test sending a reply back

**Fix any issues found.** This is the most critical feature — if you can't catch replies, the whole system is useless.

**Browser-verify:** Reply appears in Replies page, all actions work.

---

## TASK 8: Build Recruiter Lead List (First Batch)

Use Apollo (and manual research if credits run out) to build a list of 50-100 UK digital marketing recruiters.

**Search criteria:**
- Title contains: recruiter, consultant, talent, resourcing
- Industry: staffing, recruitment, digital marketing
- Location: United Kingdom
- Company type: recruitment agencies that place digital/PPC roles

**Examples of target companies:** Harnham, Salt, Forward Role, Digital Waffle, Sphere Digital, Major Players, Propel, Recruit Digital, etc.

**For each lead capture:** Name, title, company, verified email, phone (if available), LinkedIn URL

**Browser-verify:** All leads appear in the Leads page with correct data.

---

## TASK 9: Build Agency Lead List (First Batch)

Use Apollo (and manual research if credits run out) to build a list of 50-100 UK digital marketing agencies.

**Search criteria:**
- Company type: digital marketing agency, PPC agency, performance marketing agency
- Location: United Kingdom
- Contact title: Director, MD, Head of PPC, PPC Manager, Head of Paid Media
- Company size: 5-100 employees (small-medium agencies most likely to need contractor help)

**For each lead capture:** Contact name, title, agency name, verified email, phone, website, LinkedIn URL

**Browser-verify:** All leads appear in the Leads page with correct data.

---

## TASK 10: Queue and Send First Batch

Queue the first 20 emails (10 recruiters + 10 agencies) and send them.

**Steps:**
1. Select 10 recruiters from the lead list → compose using recruiter template → review merged fields → queue
2. Select 10 agencies from the lead list → compose using agency template → review merged fields → queue
3. Review all 20 emails in the Queue before sending
4. Send the first batch
5. Confirm all 20 appear in the Sent page
6. Confirm tracking pixels are embedded
7. Monitor for bounces over the next hour

**Browser-verify:** All 20 emails sent, visible in Sent page, no bounces in first hour.

---

## SESSION SUMMARY

| # | Task | Category |
|---|------|----------|
| 1 | Outreach system health check | Testing |
| 2 | Email signature setup | Config |
| 3 | Template system — merge fields | Feature |
| 4 | Recruiter email template | Content |
| 5 | Agency email template | Content |
| 6 | Apollo.io integration | Feature |
| 7 | Reply inbox polling — live test | Testing |
| 8 | Build recruiter lead list (50-100) | Data |
| 9 | Build agency lead list (50-100) | Data |
| 10 | Queue and send first batch (20) | Execution |

**TOTAL: 10 tasks, executed in order, one at a time.**

**End-of-week target:** 20 outreach emails/day to recruiters and agencies, with working reply detection and professional templates.

---

**END OF BRIEF**
