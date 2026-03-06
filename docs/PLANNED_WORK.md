# PLANNED WORK - Ads Control Tower (A.C.T.)

**Last Updated:** 2026-03-06
**Current Status:** Dashboard redesign + Cold Outreach System complete. Website, M9 validation, and outreach enhancements next.
**Total Planned Items:** 26
**Total Estimated Time:** 210-300 hours

---

## 📊 PRIORITY OVERVIEW

| Priority | Items | Estimated Time |
|----------|-------|----------------|
| **COMPLETE** | 2 items | ~35 hours spent |
| **HIGH (Next 10-12 chats)** | 12 items | 80-130 hours |
| **MEDIUM (Phase 3 + Features)** | 8 items | 55-75 hours |
| **LONG-TERM (Major expansions)** | 6 items | 85-90 hours |

---

## ✅ COMPLETE

### **Dashboard Design Upgrade (Module 4)**
**Completed:** Chat 57-58 — March 3, 2026
**Commits:** 6f9fafa, 0bcee06, ef93abc, 86e01ed, 72407bf

- Google Ads-style table redesign across all 5 entity pages (Campaigns, Ad Groups, Ads, Keywords, Shopping)
- Control bar, column selector modal, session persistence, status dots, ROAS color coding
- Shared table-styles.css for consistent design language

---

### **Cold Outreach System**
**Completed:** Chats 59-64 — March 2026
**Commits:** (see chat history)

6-page outreach section built end-to-end:
- **Leads** — lead database, add/edit/delete, track assignment, notes panel
- **Queue** — email composition, variable substitution, send/skip/discard
- **Sent** — sent email history, follow-up triggers, status management
- **Replies** — inbox, reply compose, real-time unread tracking, won/lost/meeting actions
- **Templates** — sequence flow diagram, template editor, variable chips, edit modal
- **Analytics** — 8 KPI cards, engagement funnel, 4 charts, performance tables by track and template step

---

## 🔥 HIGH PRIORITY (NEXT 10-12 CHATS)

### **1. Website Design Upgrade (christopherhoole.online)** (TBD hours)
**Status:** PLANNED — scope TBD
**Priority:** CRITICAL (NEXT)
**Dependencies:** None

**Current Website:** https://christopherhoole.online
**Tech Stack:** Next.js 14, Tailwind CSS, Framer Motion, Three.js
**Current Status:** Fully functional, deployed on Vercel

**Scope:** ⚠️ TO BE DEFINED

**Current Sections (11 total):**
1. Hero (Three.js shader animation)
2. About Me
3. The Problem
4. The Difference
5. Work History
6. Skills & Platforms
7. What A.C.T Does
8. Why I'm Different (16 USP cards)
9. FAQ (10 questions)
10. Contact Form
11. Footer + Navigation

**Potential Areas:**
- Visual refinements (spacing, typography, colors)
- Component updates (cards, animations, transitions)
- Three.js hero animation improvements
- Mobile responsiveness enhancements
- New sections or content updates

---

### **2. M9 Live Validation** (4-6 hours)
**Status:** PLANNED
**Priority:** HIGH
**Dependencies:** Real Google Ads account access

**Scope:**
- Test negative keyword blocking with live Google Ads API (not synthetic data)
- Test keyword expansion with live API
- Validate dry-run → live execution flow
- Confirm changes write to Google Ads correctly
- Verify audit trail accuracy

**Deliverables:**
- Live API test results
- Any bug fixes needed
- Production-ready confirmation
- Updated documentation

---

### **3. Website: Contact Form Backend** (2-3 hours)
**Status:** PLANNED
**Priority:** HIGH
**Dependencies:** None (frontend complete)

**Scope:**
- Create `/api/leads` endpoint on Vercel serverless function
- Email notification to Christopher when form submitted
- Store leads (Google Sheets via gspread, consistent with existing lead capture)
- Anti-spam protection (honeypot or reCAPTCHA)
- Response email to submitter

**Deliverables:**
- Vercel serverless function for form submission
- Email notification system
- Lead storage in Google Sheets
- Confirmation email to submitter

---

### **4. Outreach: CV Upload/Replace** (4-6 hours)
**Status:** PLANNED
**Priority:** HIGH
**Dependencies:** None

**Current State:** Templates page has CV attachment UI but all buttons (Preview, Replace, Remove, Upload) show placeholder toasts only.

**Scope:**
- File upload endpoint for CV (PDF)
- Store CV in `/static/uploads/` or similar
- Preview — open PDF in new tab
- Replace — upload new file, update DB reference
- Remove — delete file reference
- CV filename shown on Templates page attachment card
- CV linked correctly when sending emails via Queue

**Deliverables:**
- Working CV file management on Templates page
- CV attached to emails when `cv_attached = true` in queue

---

### **5. Outreach: Live Email Sending** (8-12 hours)
**Status:** PLANNED
**Priority:** HIGH
**Dependencies:** CV upload (item 4) recommended first

**Current State:** Queue "Send" button writes to DB but doesn't actually send emails.

**Scope:**
- SMTP or SendGrid integration
- Send email on Queue "Send" button click
- CV attachment support (if cv_attached = true)
- HTML email templates using existing template bodies
- Variable substitution ({{first_name}}, {{company}}, {{track}}, {{role}})
- Error handling (bounce, auth failure, rate limits)
- Dry-run mode for testing without sending
- Config: sender email, SMTP credentials stored in client YAML or .env

**Deliverables:**
- Working email send from Queue page
- CV attachment support
- HTML email rendering
- Error handling and logging
- Dry-run mode

---

### **6. Outreach: Real Open/Click Tracking** (6-10 hours)
**Status:** PLANNED
**Priority:** HIGH
**Dependencies:** Live email sending (item 5)

**Current State:** `opened_at`, `clicked_at`, `cv_opened_at` columns exist but are never written. Analytics uses `open_count`, `click_count`, `cv_open_count` integer columns populated by seed script only.

**Scope:**
- Tracking pixel endpoint (`/outreach/track/open/<email_id>`) — 1x1 transparent GIF, increments `open_count` + writes `opened_at`
- Link redirect endpoint (`/outreach/track/click/<email_id>`) — increments `click_count` + writes `clicked_at`, redirects to actual URL
- CV redirect endpoint (`/outreach/track/cv/<email_id>`) — increments `cv_open_count` + writes `cv_opened_at`
- Embed tracking pixel + wrapped links automatically when sending emails
- Analytics page automatically reflects real data

**Deliverables:**
- 3 tracking endpoints
- Automatic pixel/link injection on send
- Real open/click/CV data in Analytics

---

### **7. Outreach: Apollo.io Data Partner Integration** (8-15 hours)
**Status:** PLANNED
**Priority:** HIGH
**Dependencies:** None (can run parallel)

**Scope:**
Build bulk lead import from Apollo.io API directly into `outreach_leads` table.

**Features:**
- Apollo.io API authentication (API key in config)
- Search/filter leads at import time: country, company size, industry (digital marketing agencies)
- Field mapping: Apollo fields → ACT schema (name, company, role, track, email, website, linkedin_url)
- Deduplication on email address before insert
- Import history log (when, how many imported, filters used)
- UI on Leads page: "Import from Apollo" button → modal with filter options → preview → confirm import
- Scheduled sync option (daily/weekly auto-import)

**Target criteria:**
- Industry: Digital marketing / advertising agencies
- Countries: UK, US, CA, AU, NZ
- Company size: 5-50 employees
- Has Google Ads clients (inferred from job titles / keywords)

**Deliverables:**
- Apollo.io API integration
- Bulk import with deduplication
- Filter UI on Leads page
- Import history log
- Optional scheduled sync

---

### **8. Outreach: LinkedIn Integration** (TBD hours)
**Status:** PLANNED — scope TBD
**Priority:** HIGH
**Dependencies:** None

**Scope:** ⚠️ TO BE DEFINED

**Potential areas:**
- LinkedIn Sales Navigator API or scraping for lead sourcing
- LinkedIn message outreach alongside email sequences
- LinkedIn connection tracking in lead status
- Profile URL stored per lead (already have `linkedin_url` field in leads)

**Questions to answer:**
1. Outreach via LinkedIn messages or just sourcing leads from LinkedIn?
2. Use LinkedIn API (limited) or third-party tool integration (Phantombuster, Expandi)?
3. Track LinkedIn activity within ACT or in external tool?

---

### **9. Website: WhatsApp Button** (1-2 hours)
**Status:** PLANNED
**Priority:** HIGH
**Dependencies:** None

**Scope:**
- Floating WhatsApp button on christopherhoole.online
- Clicking opens `https://wa.me/[number]` — works on mobile (opens WhatsApp app) and desktop (opens WhatsApp Web)
- Pre-filled message: "Hi Christopher, I found your website and wanted to get in touch."
- Positioned bottom-right, above any other floating elements
- Green WhatsApp icon, subtle animation (pulse or hover lift)
- Optional: also add WhatsApp link to footer alongside LinkedIn/email

**Deliverables:**
- Floating WhatsApp button component
- Pre-filled message URL
- Mobile + desktop compatible

---

### **10. Performance Max Campaigns** (20-30 hours)
**Status:** PLANNED
**Priority:** HIGH
**Dependencies:** None

**Scope:**
Performance Max is Google's newest automated campaign type combining Search, Display, YouTube, Discover, Gmail.

**Database Layer:**
- New table: `analytics.pmax_asset_group_daily`
- Asset group performance metrics, asset-level data, audience signal effectiveness

**Rules Engine:**
- 10-15 rules: budget optimisation, ROAS/CPA targets, audience signals, asset performance

**Dashboard:**
- New "Performance Max" page in navigation
- Asset group table, asset performance tab, audience signals tab
- Recommendations tab (following Chat 49 pattern)
- Rules tab

**Estimated Breakdown:**
- Database + data pipeline: 5-8h
- Rules creation (10-15 rules): 8-10h
- Dashboard pages: 6-8h
- Recommendations integration: 3-4h
- Testing + documentation: 3-4h

---

### **11. Testing & Polish** (6-8 hours)
**Status:** PLANNED
**Priority:** HIGH
**Dependencies:** All high-priority items above complete

**Scope:**
Comprehensive end-to-end testing across entire platform after all high-priority work:
- Dashboard entity pages (campaigns, keywords, ad groups, ads, shopping)
- Recommendations UI across all 4 entity pages
- All 6 outreach pages
- Performance benchmarks (<5s page loads)
- Zero console errors across all pages
- Visual consistency check

**Deliverables:**
- Comprehensive testing report
- Bug fixes
- Performance benchmarks
- Documentation updates

---

### **12. Finalise Shopping Campaigns** (TBD hours)
**Status:** PLANNED — scope TBD
**Priority:** HIGH
**Dependencies:** None

**Current State:**
- 14 shopping rules active, 126 recommendations generating
- Shopping page has full Module 4 table redesign

**Potential enhancements (to define):**
- Product-level performance breakdown (separate tab)
- Feed quality metrics visualisation
- Out-of-stock tracking improvements
- Shopping-specific chart improvements
- Enhanced product group tables

---

## 📋 MEDIUM PRIORITY

### **13. Website: SEO Improvements** (3-4 hours)
**Status:** PLANNED
**Dependencies:** None

**Scope:** Meta tags, Open Graph, Twitter Cards, sitemap.xml, robots.txt, Schema.org markup (Person, Organisation), page speed optimisation.

---

### **14. System Changes Tab → Cards** (4-6 hours)
**Status:** PLANNED (deferred from Chat 29)
**Dependencies:** None

**Scope:** Convert "System Changes" tab on `/changes` page from table to card-based UI matching "My Actions" tab.

---

### **15. Unit Tests** (10-15 hours)
**Status:** PLANNED (Phase 3: Future-Proofing)
**Dependencies:** None

**Scope:** pytest coverage for all routes, recommendations engine, Google Ads API integrations. Target 80%+ coverage. CI/CD via GitHub Actions.

---

### **16. Background Job Queue** (8-10 hours)
**Status:** PLANNED (Phase 3: Future-Proofing)
**Dependencies:** None

**Scope:** Replace daemon threads with Celery + Redis job queue for recommendations engine, Radar monitoring, email reports, data refresh.

---

### **17. Database Indexes** (3-5 hours)
**Status:** PLANNED (Phase 3: Future-Proofing)
**Dependencies:** None

**Scope:** EXPLAIN QUERY PLAN analysis, indexes on frequently queried columns across recommendations, changes, campaign_features_daily, keyword_daily, shopping_campaign_daily.

---

### **18. CSRF Protection** (2-3 hours)
**Status:** PLANNED (Phase 3: Future-Proofing)
**Dependencies:** None

**Scope:** Full Flask-WTF implementation, remove all current CSRF exemptions, proper token generation across all POST routes, forms, and AJAX calls.

---

### **19. Email Reports** (15-20 hours)
**Status:** PLANNED
**Dependencies:** Background job queue

**Scope:** Automated weekly + monthly reports. Sections: executive summary, performance overview, recommendations activity, upcoming recommendations, budget pacing. HTML email templates + PDF attachment option.

---

### **20. Smart Alerts** (10-15 hours)
**Status:** PLANNED
**Dependencies:** None

**Scope:** Real-time alerts for performance degradation (ROAS drop ≥20%, CVR drop ≥15%), budget pacing, high-value opportunities, recommendation failures, system health. Delivery via email + dashboard banner.

---

## 🚀 LONG-TERM (MAJOR EXPANSIONS)

### **21. Display Campaigns** (15-20 hours)
**Status:** PLANNED
**Dependencies:** Performance Max complete

Extend ACT to support Google Display Network campaigns. New DB table, 10-12 placement/audience/creative optimisation rules, new dashboard page with placements/audiences/creatives/recommendations/rules tabs.

---

### **22. Video Campaigns (YouTube)** (15-20 hours)
**Status:** PLANNED
**Dependencies:** Display complete

Extend ACT to support YouTube advertising. New DB table, 10-12 rules (view rate, CPV, ad format, audience), new dashboard page.

---

### **23. Demand Gen Campaigns** (15-20 hours)
**Status:** PLANNED
**Dependencies:** Video complete

Extend ACT to support Demand Gen (YouTube + Discover + Gmail). New DB table, 10-12 multi-surface optimisation rules, new dashboard page.

---

### **24. Automated Report Generator** (20-25 hours)
**Status:** PLANNED
**Dependencies:** Email reports complete

AI-powered monthly slide deck generator (PowerPoint/Google Slides). Sections: executive summary, MoM performance, campaign breakdown, top performers, recommendations executed, next month outlook. AI-generated insights via LLM.

---

### **25. Multi-User Support** (12-15 hours)
**Status:** PLANNED
**Dependencies:** None

Extend ACT from single-user to multi-user with RBAC (Admin / Manager / Analyst / Client roles). User registration, activity logging, team collaboration, client portal.

---

### **26. API Endpoints** (10-12 hours)
**Status:** PLANNED
**Dependencies:** Multi-user support

Public REST API: recommendations (list/accept/decline), campaigns, rules (list/create), changes. API key auth, rate limiting (100 req/hr), webhook support, Swagger docs.

---

## 📊 SUMMARY STATISTICS

**Total Planned Items:** 26 (2 complete, 24 remaining)
**Total Estimated Time Remaining:** 210-300 hours

| Category | Items | Estimated Hours |
|----------|-------|----------------|
| Complete | 2 | ~35h spent |
| High Priority | 12 | 80-130h |
| Medium Priority | 8 | 55-75h |
| Long-Term | 6 | 85-90h |

---

## 🎯 NEXT 3 CHATS

1. **Website Design Upgrade** — define scope, then build
2. **M9 Live Validation** — real Google Ads API testing
3. **Website: Contact Form Backend** — Vercel serverless + Google Sheets

---

**Document Version:** 3.0
**Last Updated:** 2026-03-06
**Next Review:** After Website Design Upgrade + M9 Live Validation complete
