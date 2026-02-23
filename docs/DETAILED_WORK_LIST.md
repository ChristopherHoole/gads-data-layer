# DETAILED WORK LIST - All Planned Work

**Created:** 2026-02-23
**Purpose:** Comprehensive list of all planned work across A.C.T Dashboard and Marketing Website
**Priority:** Ranked 1 (critical) → 5 (nice-to-have)
**Location:** `C:\Users\User\Desktop\gads-data-layer\docs\DETAILED_WORK_LIST.md`

---

## 🎯 IMMEDIATE PRIORITIES (Next 2-4 weeks)

### **Priority 1: CRITICAL - Must Complete**

#### **1. Chat 30: M9 Search Terms / Keywords Recommendations**
**Estimated:** 8-12 hours
**Status:** Brief not yet written
**Description:** Add Search Terms functionality to Keywords page
**Deliverables:**
- Search Terms tab on /keywords page
- Query analysis and negative keyword suggestions
- Integration with existing keyword optimization rules
- Card-based recommendation UI (following M6/M7 pattern)

#### **2. Website: Connect Contact Form to A.C.T Dashboard**
**Estimated:** 2-4 hours
**Status:** Frontend complete, backend needed
**Description:** Create /api/leads endpoint in A.C.T dashboard
**Deliverables:**
- `/api/leads` POST route in Flask
- Store leads in warehouse.duckdb (new `leads` table)
- Email notification on new lead (optional)
- Test form submission from christopherhoole.online
**Technical Notes:**
- Frontend sends: name, company, role, looking_for, email, phone
- Backend validates, stores, returns success/error
- Consider rate limiting (prevent spam)

### **Priority 2: HIGH - Important for Completeness**

#### **3. System Changes Tab → Card Grid**
**Estimated:** 3-5 hours
**Status:** Deferred from Chat 29, currently table format
**Description:** Convert System Changes tab to card grid (match My Actions style)
**Deliverables:**
- Card-based UI for `ro.analytics.change_log` data
- Same card anatomy as My Actions tab
- Filter bar (date range, change type)
**Technical Notes:**
- Currently implemented as table in changes.html
- Will be empty in synthetic environment until Autopilot runs live

#### **4. M5 Rules Tab Rollout**
**Estimated:** 6-8 hours (2 hours per page)
**Status:** Complete on Campaigns, needs rollout
**Description:** Add card-based Rules tab to remaining pages
**Pages:**
- Ad Groups (2 rules)
- Keywords (3 rules)
- Ads (2 rules)
- Shopping (6 rules + subcategory tabs)
**Deliverables:**
- Rules tab on each page with relevant rule cards
- Same CRUD functionality as Campaigns
- Campaign picker (for specific-scope rules)
- Consistent UI/UX across all pages

---

## 🔧 TECHNICAL DEBT & IMPROVEMENTS

### **Priority 3: MEDIUM - Phase 3 Future-Proofing**

#### **5. Unit Test Suite**
**Estimated:** 15-20 hours
**Status:** Not started
**Description:** Comprehensive pytest test suite
**Components:**
- Route tests (all 8 blueprints)
- Database query tests (DuckDB)
- Rules engine tests (recommendations_engine.py)
- Radar monitoring tests (radar.py)
- API endpoint tests (rules_api.py)
- Helper function tests (shared.py)
**Coverage Target:** 80%+

#### **6. Background Job Queue**
**Estimated:** 8-12 hours
**Status:** Not started
**Description:** Celery + Redis for background tasks
**Use Cases:**
- Radar monitoring (currently daemon thread)
- Recommendations engine runs
- Email report generation
- Data sync from Google Ads API
**Benefits:**
- Better scalability
- Retry logic
- Task monitoring
- Scheduled jobs

#### **7. Database Optimization**
**Estimated:** 4-6 hours
**Status:** Not started
**Description:** Indexes, query optimization, schema refinement
**Tasks:**
- Add indexes on frequently queried columns
- Optimize slow queries (campaign_features_daily joins)
- Consider materialized views for common aggregations
- Review warehouse.duckdb vs warehouse_readonly.duckdb separation

#### **8. CSRF Protection**
**Estimated:** 2-3 hours
**Status:** Not started
**Description:** Add Flask-WTF CSRF tokens to all forms
**Scope:**
- All POST/PUT/DELETE routes
- Rules CRUD forms
- Recommendations action buttons
- Settings forms

---

## 🚀 CAMPAIGN TYPE EXPANSION

### **Priority 2: HIGH - Campaign Types Beyond Search**

**Current State:** A.C.T only supports Search campaigns fully. Shopping partially implemented (Chat 12).

**Priority Order (from Master Chat 3.0):**
1. Shopping (complete the implementation)
2. Performance Max (PMAX) - highest priority
3. Video / YouTube
4. Display
5. Demand Gen (lowest priority)

#### **5. Shopping Campaign Completion**
**Estimated:** 12-18 hours
**Status:** Partially complete (Chat 12: 14 rules, 4-tab UI, 3,800 lines)
**Description:** Complete Shopping campaign support
**Deliverables:**
- Full recommendations engine integration
- All 14 rules producing recommendations
- Shopping-specific metrics (Product partition IS, Opt. Score)
- Feed error monitoring
- Product performance analysis
- Shopping tab polish (complete all sub-tabs)
**Technical Notes:**
- Shopping module exists but not fully integrated with M6 recommendations engine
- Need to wire Shopping rules into recommendations flow

#### **6. Performance Max (PMAX) Campaign Support**
**Estimated:** 20-30 hours
**Status:** Not started
**Description:** Add complete PMAX campaign support (highest priority new type)
**Why Priority:** PMAX is now Google's dominant campaign type
**Deliverables:**
- Google Ads API data ingestion (PMAX-specific fields)
- Feature engineering (asset group performance, audience signals)
- PMAX-specific rules (10-15 rules):
  - Budget optimization
  - Asset group performance
  - Audience signal recommendations
  - Final URL expansion suggestions
  - Listing group optimization (for retail)
- Recommendations engine integration
- PMAX dashboard page (similar to Campaigns page)
- Metrics cards (PMAX-specific metrics)
- Performance charts
**Technical Challenges:**
- PMAX has different structure (asset groups vs ad groups)
- Limited transparency into which assets/audiences perform best
- API limitations on granular data

#### **7. Video / YouTube Campaign Support**
**Estimated:** 18-25 hours
**Status:** Not started
**Description:** Add YouTube/Video campaign support
**Deliverables:**
- Video campaign data ingestion
- Video-specific metrics (View rate, CPV, Watch time)
- Video rules (8-12 rules):
  - View rate optimization
  - CPV bidding
  - Audience targeting
  - Placement performance
- Video dashboard page
- Video preview/thumbnail display
**Technical Notes:**
- Need to handle video assets (thumbnails, previews)
- TrueView vs Bumper vs In-stream differences

#### **8. Display Campaign Support**
**Estimated:** 15-22 hours
**Status:** Not started
**Description:** Add Display campaign support
**Deliverables:**
- Display campaign data ingestion
- Display-specific metrics (Viewable impressions, Active View)
- Display rules (8-12 rules):
  - Placement performance
  - Audience targeting
  - Creative rotation
  - Viewability optimization
- Display dashboard page
- Banner/image ad preview
**Technical Notes:**
- Responsive display ads vs uploaded image ads
- Placement exclusions important

#### **9. Demand Gen Campaign Support**
**Estimated:** 12-18 hours
**Status:** Not started (lowest priority)
**Description:** Add Demand Gen campaign support (newest Google Ads type)
**Deliverables:**
- Demand Gen data ingestion
- Similar to Discovery campaigns (visual storytelling)
- Demand Gen rules (6-10 rules)
- Demand Gen dashboard page
**Technical Notes:**
- Newest campaign type, may have limited API maturity
- Consider deferring until more stable

---

## 🚀 FEATURE DEVELOPMENT

### **Priority 3: MEDIUM - Planned Features**

#### **10. Automated Report Generator (Markifact-Style)**
**Estimated:** 25-35 hours
**Status:** Not started
**Priority:** HIGH (saves 2-4 hours per client per month)
**Description:** Monthly slide-based reports with AI-generated insights
**Reference:** https://www.markifact.com/templates/google-ads-monthly-slides-with-ai-insights
**Deliverables:**
- **Monthly Reports:**
  - PowerPoint/Google Slides generation
  - Executive summary slide (AI-generated)
  - Performance trends slides (charts: spend, conversions, ROAS)
  - Top wins slide (best performing campaigns/keywords)
  - Concerns slide (underperformers, issues)
  - Recommendations slide (approved/executed from A.C.T)
  - Next month action plan
  - Client-specific branding (logo, colors)
- **Bi-weekly Update Slides** (lighter version for client calls):
  - 2-week performance snapshot
  - Key metrics
  - Recent changes
  - Quick wins
- **AI Insights Generation:**
  - Claude API integration
  - AI-written commentary per section
  - Explain performance changes in plain English
  - Contextual recommendations
- **Automation:**
  - One-click generation from dashboard
  - Scheduled generation (e.g., 1st of each month)
  - Auto-email to client (optional)
  - Download as PPTX or PDF
**Technical:**
- Use python-pptx or Google Slides API
- Jinja2 templates for slide structure
- Chart.js or Matplotlib for embedded charts
- Claude API for AI commentary
- Background job queue (Celery) for generation
**Goal:** Save 2-4 hours per client per month on manual reporting work

#### **11. Smart Alerts (Anomaly Detection)**
**Estimated:** 12-18 hours
**Status:** Not started
**Description:** Real-time alerts for anomalies and issues
**Alert Types:**
- Budget overspend (>110% of daily target)
- Performance drop (ROAS/CVR <-20%)
- Feed errors (Shopping)
- Tracking breaks (conversion lag >48h)
- Quality Score drops (>2 point decrease)
**Channels:**
- Email (immediate)
- Dashboard badge (in-app)
- Slack webhook (optional)

#### **12. Advanced Visualizations**
**Estimated:** 8-12 hours
**Status:** Not started
**Description:** Enhanced data visualization beyond current Chart.js
**Charts:**
- Heatmaps (day-of-week × hour performance)
- Funnel charts (awareness → consideration → conversion)
- Cohort analysis (campaign performance over time)
- Correlation matrix (metric relationships)
**Library:** Consider Plotly.js or D3.js

---

## 🎯 LEAD GENERATION & CLIENT ACQUISITION

### **Priority 2: HIGH - Cold Outreach System**

**Context (from Master Chat 3.0):**
- Google Ads to drive traffic to marketing website is costly
- Need cheaper lead generation method
- Target: Digital marketing agencies (force multiplier - one agency = multiple clients)
- Geographies: UK, USA, Australia, Dubai (English-speaking countries)

#### **13. Cold Outreach System - Phase 1: Foundation**
**Estimated:** 30-40 hours
**Status:** Not started
**Description:** Build automated cold email outreach system targeting agencies
**Deliverables:**

**A. Agency List Builder (8-12 hours):**
- Scrape/aggregate from multiple sources:
  - Google Maps API (search "digital marketing agency" by location)
  - Clutch.co (API or scraper)
  - Agency Spotter (scraper)
  - LinkedIn Company Search (scraper)
- Store in database: agency_name, website, location, size, services
- Deduplication logic (same agency from multiple sources)
- Export to CSV

**B. Contact Finder (10-15 hours):**
- Website crawler for each agency
- Extract email addresses:
  - Contact page
  - About page
  - Footer
- Email validation (format check, MX record check)
- Prioritize: owner/director emails > info@ emails
- Store: contact_email, source_page, confidence_score

**C. Email Outreach Engine (8-12 hours):**
- Template system (3-5 email templates):
  - Template A: Agency partnership pitch
  - Template B: White-label offering
  - Template C: Referral program
- Personalization tokens: {agency_name}, {first_name}, {location}
- Sequenced campaigns: Email 1 → wait 3 days → Email 2 (if no reply)
- Sending limits (respect SMTP limits, avoid spam)
- Integration with Gmail SMTP or SendGrid API

**D. Tracking & Analytics (4-6 hours):**
- Open rate tracking (pixel)
- Click rate tracking (UTM links)
- Reply detection (email parser)
- Dashboard: campaigns, sent, opened, clicked, replied
- Conversion tracking (form submission from website)

**E. Lead Ingestion to A.C.T (2-3 hours):**
- When agency fills contact form → create lead in A.C.T
- Store full context:
  - Which email campaign
  - Which template
  - Open/click history
  - Source (cold outreach)
- Link to agency record in database

**F. Compliance & Legal (2-4 hours):**
- Unsubscribe mechanism (one-click)
- Suppression list (never email again)
- GDPR/CAN-SPAM/CASL compliance:
  - Physical address in footer
  - Opt-out link in every email
  - "Why am I receiving this" disclosure
- Terms & Privacy Policy for website

**Technical Stack:**
- Scrapers: Selenium or Playwright (headless browser)
- Email: SendGrid API or Gmail SMTP
- Database: DuckDB or PostgreSQL (agencies + contacts + campaigns)
- Scheduler: Celery (background jobs)
- Tracking: Custom pixel + UTM params

**Legal Requirements by Country:**
- **UK:** GDPR + PECR (B2B okay, needs opt-out)
- **USA:** CAN-SPAM (requires opt-out + physical address)
- **Australia:** Spam Act (similar to UK)
- **Canada:** CASL (strictest - requires consent)

**Goal:** Generate 10-20 qualified agency leads per month at <£500 cost

#### **14. Cold Outreach System - Phase 2: Advanced Features**
**Estimated:** 15-25 hours
**Status:** Not started (after Phase 1 validates)
**Description:** Enhanced outreach capabilities
**Features:**
- A/B testing (template variations)
- AI-generated personalization (Claude API)
- Agency firmographic enrichment (company size, revenue)
- LinkedIn integration (InMail alternative)
- CRM integration (HubSpot, Salesforce)
- Automated follow-ups (if opened but no reply)
- Warm-up sequences (build domain reputation)

---

## 🌐 WEBSITE ENHANCEMENTS

### **Priority 4: LOW - Optional Website Improvements**

#### **15. Website SEO Optimization**
**Estimated:** 2-4 hours
**Status:** Not started
**Description:** Improve search engine visibility
**Tasks:**
- Add meta tags (title, description, keywords)
- OpenGraph images (social sharing)
- robots.txt
- sitemap.xml
- Structured data (JSON-LD)
- Page speed optimization

#### **16. Website Analytics Integration**
**Estimated:** 1-2 hours
**Status:** Not started
**Description:** Track visitor behavior
**Tools:**
- Google Analytics 4
- Track: page views, button clicks, form submissions
- Conversion goals (form submit = lead)

#### **17. Website A/B Testing**
**Estimated:** 3-5 hours
**Status:** Not started
**Description:** Test variations of key elements
**Candidates:**
- CTA button text
- Hero headline
- Contact form fields (more/fewer)
- FAQ questions (which 10 to show)
**Tool:** Vercel Edge Config or simple feature flags

---

## 🔐 ENTERPRISE FEATURES

### **Priority 5: NICE-TO-HAVE - Enterprise/Multi-User**

#### **18. Multi-User Support**
**Estimated:** 15-20 hours
**Status:** Not started
**Description:** Role-based access control
**Roles:**
- Admin (full access)
- Manager (approve recommendations, view reports)
- Analyst (read-only, no approve)
- Client (view their account only)
**Features:**
- User management UI
- Login/logout per user
- Permission checks on all routes
- Audit log (who did what)

#### **19. API Endpoints (External Access)**
**Estimated:** 8-12 hours
**Status:** Not started
**Description:** RESTful API for external integrations
**Endpoints:**
- GET /api/v1/campaigns
- GET /api/v1/recommendations
- POST /api/v1/recommendations/{id}/accept
- GET /api/v1/reports/weekly
**Auth:** API keys or OAuth2

#### **20. White-Label Capabilities**
**Estimated:** 6-10 hours
**Status:** Not started (LOW PRIORITY - Christopher wants to keep A.C.T exclusive)
**Description:** Rebrand dashboard for agency use
**Features:**
- Custom logo upload
- Color scheme customization
- Custom domain per agency
- Agency-specific branding
**Use Case:** Agencies using A.C.T for their clients
**Note:** Deferred indefinitely per Christopher's preference

---

## 📚 DOCUMENTATION & ONBOARDING

### **Priority 4: LOW - User Experience**

#### **21. Onboarding Wizard**
**Estimated:** 10-15 hours
**Status:** Not started
**Description:** First-time user setup flow
**Steps:**
1. Connect Google Ads account
2. Select campaigns to manage
3. Set target ROAS/CPA goals
4. Configure notification preferences
5. Run first recommendations engine
**UI:** Multi-step modal with progress indicator

#### **22. In-App Help & Tooltips**
**Estimated:** 4-6 hours
**Status:** Not started
**Description:** Contextual help throughout dashboard
**Features:**
- ? icons next to complex metrics
- Popover explanations
- Video tutorials (embedded YouTube)
- Keyboard shortcuts guide

#### **23. User Documentation**
**Estimated:** 8-12 hours
**Status:** Not started
**Description:** Comprehensive user guide
**Sections:**
- Getting Started
- Understanding Recommendations
- Rules Configuration
- Reading Reports
- Troubleshooting
- FAQ
**Format:** Markdown → static site (Docusaurus or MkDocs)

---

## 🐛 BUG FIXES & POLISH

### **Priority 2: HIGH - Known Issues**

#### **24. Campaign Scope Pill Name Resolution**
**Estimated:** 1-2 hours
**Status:** Known issue
**Description:** Campaign-specific rules show campaign_id instead of name
**Fix:** Fetch campaign name from warehouse when rendering card
**Location:** recommendations card rendering (both pages)

#### **25. All Conversions Pipeline**
**Estimated:** 3-5 hours
**Status:** Incomplete
**Description:** "All Conv." columns exist but not fully wired
**Tasks:**
- Verify data source (Google Ads API field)
- Add to synthetic data generation
- Wire to dashboard tables
- Update metrics cards if needed

#### **26. Shopping Impression Share & Optimization Score**
**Estimated:** 2-4 hours
**Status:** Columns exist but NULL
**Description:** Shopping-specific metrics not populated
**Tasks:**
- Verify API fields exist
- Add to data ingestion
- Populate synthetic data
- Display in Shopping page tables

#### **27. Config YAML Validation Errors**
**Estimated:** 2-3 hours
**Status:** Pre-existing, non-blocking
**Description:** Multi-client YAML config has validation warnings
**Tasks:**
- Review all YAML files in `configs/`
- Fix schema mismatches
- Add schema validation on load
- Document expected structure

---

## 🔄 ONGOING MAINTENANCE

### **Priority 3: MEDIUM - Continuous Improvement**

#### **28. Google Ads API Updates**
**Estimated:** Ongoing (4-8 hours per API version)
**Frequency:** Every 6-12 months
**Description:** Keep up with Google Ads API changes
**Tasks:**
- Monitor API changelog
- Test against new API versions
- Update field mappings
- Deprecate old endpoints

#### **29. Synthetic Data Improvements**
**Estimated:** Ongoing (2-4 hours per improvement)
**Description:** Make synthetic data more realistic
**Ideas:**
- Add seasonality patterns
- Correlation between metrics (high CTR → high CVR)
- Outliers and edge cases
- Multi-month historical data

#### **30. Performance Monitoring**
**Estimated:** Ongoing (1-2 hours per review)
**Frequency:** Monthly
**Description:** Monitor dashboard performance
**Metrics:**
- Page load times
- Database query duration
- Recommendation engine runtime
- Memory usage
**Tools:** Flask-DebugToolbar, cProfile, py-spy

---

## 📊 SUMMARY BY PRIORITY

| Priority | Count | Estimated Hours | Description |
|----------|-------|-----------------|-------------|
| 1 (Critical) | 2 | 10-16 | M9 Keywords, Website form backend |
| 2 (High) | 12 | 159-244 | Campaign types, Reports, Cold outreach, System Changes, Rules rollout, bug fixes |
| 3 (Medium) | 11 | 72-114 | Phase 3, maintenance, features |
| 4 (Low) | 7 | 37-57 | Website SEO, documentation |
| 5 (Nice-to-have) | 3 | 29-42 | Enterprise features (multi-user deferred) |
| **TOTAL** | **35** | **307-473** | **Full roadmap** |

---

## 🎯 RECOMMENDED SEQUENCING

**Week 1-2:**
1. Chat 30: M9 Keywords Search Terms (Priority 1)
2. Website: Contact form backend (Priority 1)
3. System Changes tab → cards (Priority 2)

**Week 3-4:**
4. Shopping campaign completion (Priority 2)
5. Campaign scope pill fix (Priority 2)
6. All Conv. pipeline (Priority 2)

**Month 2:**
7. Automated Report Generator (Priority 2) - HIGH IMPACT
8. M5 Rules tab rollout (Priority 2)
9. PMAX campaign support (Priority 2)

**Month 3:**
10. Cold Outreach System Phase 1 (Priority 2) - LEAD GENERATION
11. Unit test suite (Priority 3)
12. Smart alerts (Priority 3)

**Month 4+:**
- Background job queue
- Database optimization
- Video/Display campaigns
- Documentation & onboarding

---

**Created:** 2026-02-23
**Updated:** 2026-02-23 (added Campaign Types, Automated Reports, Cold Outreach System)
**Total Estimated Work:** 307-473 hours (35 items)
**Next Action:** Chat 30 (M9 Keywords Search Terms)
