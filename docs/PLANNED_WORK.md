# PLANNED WORK - Ads Control Tower (A.C.T.)

**Last Updated:** 2026-02-28  
**Current Status:** 99.7% complete (foundation, dashboard 3.0, rules, multi-entity recommendations complete)  
**Total Planned Items:** 20  
**Total Estimated Time:** 200-270 hours  

---

## 📊 PRIORITY OVERVIEW

| Priority | Items | Estimated Time |
|----------|-------|----------------|
| **HIGH (Next 6-7 chats)** | 7 items | 50-90 hours |
| **MEDIUM (Phase 3 + Features)** | 9 items | 65-90 hours |
| **LONG-TERM (Major expansions)** | 6 items | 85-90 hours |

---

## 🔥 HIGH PRIORITY (NEXT 6-7 CHATS)

### **1. Dashboard Design Upgrade** (TBD hours)
**Status:** PLANNED  
**Priority:** CRITICAL (NEXT)  
**Dependencies:** Chat 49 complete ✅

**Scope:** ⚠️ **TO BE DEFINED**

**Potential Areas:**
- Visual redesign (colors, spacing, typography)
- Component updates (cards, tables, charts)
- Navigation improvements
- Layout modernization
- Inspiration from modern SaaS dashboards
- Google Ads-style improvements

**Questions to Answer:**
1. Which pages to upgrade? (All 8 pages or specific pages?)
2. Visual only or functional improvements too?
3. What's the design inspiration/direction?
4. Estimated time commitment?

**Placeholder Deliverables:**
- Updated UI components
- Modernized color palette
- Improved spacing/typography
- Enhanced user experience
- Design system documentation

---

### **2. Website Design Upgrade (christopherhoole.online)** (TBD hours)
**Status:** PLANNED  
**Priority:** CRITICAL  
**Dependencies:** None (can run parallel to dashboard work)

**Current Website:** https://christopherhoole.online  
**Tech Stack:** Next.js 14, Tailwind CSS, Framer Motion, Three.js  
**Current Status:** Fully functional, deployed on Vercel

**Scope:** ⚠️ **TO BE DEFINED**

**Potential Areas:**
- Visual refinements (spacing, typography, colors)
- Component updates (cards, animations, transitions)
- Three.js hero animation improvements
- Mobile responsiveness enhancements
- New sections or content
- Performance optimizations

**Questions to Answer:**
1. What specifically needs upgrading? (visual, functional, content)
2. Which sections? (Hero, About, FAQ, Contact, all?)
3. New features or just polish?
4. Estimated time commitment?

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

**Placeholder Deliverables:**
- Updated design elements
- Improved animations/transitions
- Enhanced mobile experience
- Performance improvements
- Updated content (if needed)

---

### **3. M9 Live Validation** (4-6 hours)
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

### **4. Cold Outreach System** (15-20 hours)
**Status:** PLANNED (moved up from long-term)  
**Priority:** HIGH  
**Dependencies:** None (standalone system)

**Scope:**
Build automated lead generation system targeting digital marketing agencies in English-speaking countries.

**Target Markets:**
- United Kingdom
- United States
- Canada
- Australia
- New Zealand

**Features:**
- Agency database scraping/integration
- Email sequence automation
- Personalization engine
- Response tracking
- CRM integration (HubSpot/Pipedrive)
- Follow-up scheduling

**Email Sequences:**
1. Introduction email (value proposition)
2. Case study email (proof of results)
3. Demo offer email (book a call)
4. Final follow-up (last chance)

**Targeting Criteria:**
- Agencies with Google Ads clients
- 5-50 employees (mid-sized)
- Active on LinkedIn
- Website has contact form

**Deliverables:**
- Lead database
- Email automation system
- Response tracking
- Meeting scheduler integration
- Performance analytics

---

### **5. Finalise Shopping Campaigns** (TBD hours)
**Status:** PLANNED  
**Priority:** HIGH  
**Dependencies:** Dashboard design upgrade complete

**Scope:** Shopping-specific dashboard improvements

**Current Status:**
- 14 shopping rules active and working
- Shopping page exists with basic functionality
- 126 shopping recommendations generating

**Potential Improvements:**
- Enhanced shopping campaign dashboard page
- Product-level performance breakdown
- Feed quality metrics visualization
- Shopping-specific chart improvements
- Enhanced product group tables
- Shopping performance analytics
- Better visualization of feed errors, out-of-stock, impression share

**Questions to Answer:**
1. What specific shopping dashboard features needed?
2. Which metrics/charts should be prioritized?
3. Product-level vs campaign-level focus?
4. Estimated time commitment?

**Placeholder Deliverables:**
- Improved shopping dashboard page
- Enhanced product performance views
- Better feed quality visualization
- Shopping-specific optimizations

---

### **6. Performance Max Campaigns** (20-30 hours)
**Status:** PLANNED  
**Priority:** HIGH (moved up from long-term)  
**Dependencies:** Dashboard design upgrade complete

**Scope:**
Performance Max is Google's newest automated campaign type combining Search, Display, YouTube, Discover, Gmail into one campaign. This is a major expansion requiring:

**Database Layer:**
- New table: `analytics.pmax_asset_group_daily`
- Asset group performance metrics
- Asset-level performance data
- Audience signal effectiveness

**Rules Engine:**
- Asset group performance rules (10-15 rules estimated)
- Budget optimization rules
- ROAS/CPA target adjustments
- Audience signal expansion/contraction
- Asset performance evaluation

**Dashboard Pages:**
- New "Performance Max" page in navigation
- Asset group table view
- Asset performance breakdown
- Audience signals tab
- Recommendations tab (following Chat 49 pattern)
- Rules tab

**Recommendations System:**
- Extend multi-entity engine to support `entity_type: 'pmax_asset_group'`
- Asset group-specific recommendations
- Multi-surface optimization (YouTube + Display + Search combined)

**Testing:**
- Synthetic data generation for Performance Max campaigns
- Test with real Performance Max campaigns (if available)
- Full recommendations workflow (generate → accept → monitor → rollback)

**Challenges:**
- Performance Max has less granular data than Search campaigns
- Google provides aggregated metrics across surfaces
- Asset group optimization is more complex than keyword optimization
- Limited control vs manual campaigns

**Estimated Breakdown:**
- Database + data pipeline: 5-8 hours
- Rules creation (10-15 rules): 8-10 hours
- Dashboard pages (table + tabs): 6-8 hours
- Recommendations integration: 3-4 hours
- Testing + documentation: 3-4 hours
- **Total: 20-30 hours**

**Success Criteria:**
- Performance Max campaigns visible in dashboard
- Asset group performance tracking
- 10-15 optimization rules active
- Recommendations generating and executable
- Full audit trail and rollback capability

---

### **7. Chat 50: Testing & Polish** (6-8 hours)
**Status:** PLANNED (moved back from position 1)  
**Priority:** HIGH  
**Dependencies:** Dashboard design upgrade complete

**Scope:**
- Cross-page integration testing for recommendations UI (4 entity pages) AFTER dashboard redesign
- Performance optimization if needed
- UI polish and refinements based on new dashboard design
- Edge case handling
- Final validation before considering recommendations UI 100% complete

**Rationale for Moving Back:**
Testing and polishing the recommendations UI now would be pointless if the dashboard is about to be redesigned. All tests would need to be redone after the redesign. Better to complete the dashboard upgrade first, THEN do comprehensive testing on the final design.

**Deliverables:**
- Comprehensive testing report (post-redesign)
- Any bug fixes identified
- Performance benchmarks on new design
- Documentation updates

**Success Criteria:**
- All 4 entity pages working seamlessly together with new dashboard design
- No cross-contamination between entity types
- Performance targets met (<5s page loads)
- Zero console errors across all pages
- Visual consistency with new dashboard design

---

### **4. Website Design Upgrade (christopherhoole.online)** (TBD hours)
**Status:** PLANNED  
**Priority:** HIGH (new item)  
**Dependencies:** None (can run parallel to dashboard work)

**Current Website:** https://christopherhoole.online  
**Tech Stack:** Next.js 14, Tailwind CSS, Framer Motion, Three.js  
**Current Status:** Fully functional, deployed on Vercel

**Scope:** ⚠️ **TO BE DEFINED**

**Potential Areas:**
- Visual refinements (spacing, typography, colors)
- Component updates (cards, animations, transitions)
- Three.js hero animation improvements
- Mobile responsiveness enhancements
- New sections or content
- Performance optimizations

**Questions to Answer:**
1. What specifically needs upgrading? (visual, functional, content)
2. Which sections? (Hero, About, FAQ, Contact, all?)
3. New features or just polish?
4. Estimated time commitment?

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

**Placeholder Deliverables:**
- Updated design elements
- Improved animations/transitions
- Enhanced mobile experience
- Performance improvements
- Updated content (if needed)

---

## 📋 MEDIUM PRIORITY (AFTER HIGH PRIORITY COMPLETE)

### **8. Website: Contact Form Backend** (2-3 hours)
**Status:** PLANNED  
**Dependencies:** None (frontend complete)

**Scope:**
- Create `/api/leads` endpoint
- Email notification when form submitted
- Store leads in database (new table or external service)
- Anti-spam protection (reCAPTCHA or similar)
- Response email to submitter

**Deliverables:**
- Backend API endpoint
- Email integration
- Lead storage system
- Admin notification system

---

### **9. Website: SEO Improvements** (3-4 hours)
**Status:** PLANNED  
**Dependencies:** None

**Scope:**
- Meta tags (title, description, keywords)
- Open Graph tags (social media sharing)
- Twitter Card tags
- Sitemap.xml generation
- Robots.txt configuration
- Schema.org markup (Person, Organization)
- Page speed optimization

**Deliverables:**
- Complete meta tag implementation
- Sitemap.xml
- Improved search engine visibility
- Social media preview optimization

---

### **10. System Changes Tab → Cards** (4-6 hours)
**Status:** PLANNED (deferred from Chat 29)  
**Dependencies:** None

**Scope:**
Currently the "System Changes" tab in `/changes` page shows a table. Convert to card-based UI matching the "My Actions" tab and recommendations pages.

**Deliverables:**
- Card-based UI for system changes
- Same visual style as recommendations cards
- Improved readability
- Consistent design language

---

### **11. Unit Tests** (10-15 hours)
**Status:** PLANNED (Phase 3: Future-Proofing)  
**Dependencies:** None

**Scope:**
- Test coverage for all routes (recommendations, rules, campaigns, keywords, etc.)
- Test coverage for recommendations engine
- Test coverage for Google Ads API integrations
- Automated test suite (pytest)
- CI/CD integration (GitHub Actions)

**Target Coverage:** 80%+

**Deliverables:**
- Comprehensive test suite
- CI/CD pipeline
- Test documentation
- Coverage reports

---

### **12. Background Job Queue** (8-10 hours)
**Status:** PLANNED (Phase 3: Future-Proofing)  
**Dependencies:** None

**Scope:**
Replace current daemon threads with proper job queue system for:
- Recommendations engine (scheduled runs)
- Radar monitoring (continuous evaluation)
- Email reports (scheduled delivery)
- Data refresh jobs

**Technology:** Celery + Redis or similar

**Deliverables:**
- Job queue infrastructure
- Scheduled task management
- Better reliability and scaling
- Job monitoring dashboard

---

### **13. Database Indexes** (3-5 hours)
**Status:** PLANNED (Phase 3: Future-Proofing)  
**Dependencies:** None

**Scope:**
- Analyze slow queries (EXPLAIN QUERY PLAN)
- Add indexes to frequently queried columns
- Optimize JOIN operations
- Performance benchmarking

**Tables to Optimize:**
- recommendations table
- changes table
- campaign_features_daily
- keyword_daily
- shopping_campaign_daily

**Deliverables:**
- Index creation scripts
- Query performance improvements
- Documentation of optimization decisions

---

### **14. CSRF Protection** (2-3 hours)
**Status:** PLANNED (Phase 3: Future-Proofing)  
**Dependencies:** None

**Scope:**
- Full Flask-WTF implementation
- Remove current CSRF exemptions (from Chat 49)
- Proper token generation and validation
- Update all POST routes
- Update all forms and AJAX calls

**Current Exemptions to Remove:**
- `/recommendations/accept`
- `/recommendations/decline`
- Other API routes

**Deliverables:**
- Complete CSRF protection
- No security exemptions
- All routes properly protected

---

### **15. Email Reports** (15-20 hours)
**Status:** PLANNED (Features)  
**Dependencies:** Background job queue

**Scope:**
- Automated weekly reports (every Monday)
- Automated monthly reports (1st of month)
- Performance summaries (spend, conversions, ROAS)
- Recommendation highlights (accepted, monitoring, successful)
- Email template design (HTML emails)
- PDF attachment option
- Configurable recipients per client

**Report Sections:**
1. Executive Summary (key metrics)
2. Performance Overview (charts)
3. Recommendations Activity (actions taken)
4. Upcoming Recommendations (pending review)
5. Budget Pacing (on track / overspend / underspend)

**Deliverables:**
- Email report system
- Beautiful HTML email templates
- PDF generation
- Scheduling system
- Report customization options

---

### **16. Smart Alerts** (10-15 hours)
**Status:** PLANNED (Features)  
**Dependencies:** None

**Scope:**
Real-time alerts for critical events:

**Alert Types:**
1. Performance degradation (ROAS drop ≥20%, CVR drop ≥15%)
2. Budget pacing (90% spent with 50%+ of month remaining)
3. High-value opportunities (ROAS ≥10.0x campaigns underinvesting)
4. Budget overspend warnings (approaching daily limit)
5. Recommendation failures (API errors, execution failures)
6. System health (Radar offline, engine not running)

**Delivery Methods:**
- Email (immediate)
- Dashboard banner (persistent until dismissed)
- SMS (critical alerts only, optional)

**Configuration:**
- Per-client alert thresholds
- Alert muting (temporarily disable)
- Alert history/log

**Deliverables:**
- Alert detection system
- Multi-channel delivery
- Alert management UI
- Configuration options

---

## 🚀 LONG-TERM (MAJOR EXPANSIONS)

### **17. Display Campaigns** (15-20 hours)
**Status:** PLANNED (Campaign Type Expansion)  
**Dependencies:** Performance Max complete

**Scope:**
Extend ACT to support Google Display Network campaigns.

**Database Layer:**
- New table: `analytics.display_campaign_daily`
- Placement performance data
- Audience performance data
- Creative performance data

**Rules Engine:**
- Placement optimization (10-12 rules)
- Audience targeting rules
- Creative performance rules
- Budget/bid management
- Impression share optimization

**Dashboard Pages:**
- New "Display" page in navigation
- Placements tab
- Audiences tab
- Creatives tab
- Recommendations tab
- Rules tab

**Challenges:**
- Display has different metrics than Search (impressions, viewability, engagement)
- Less direct conversion tracking
- Placement-level optimization complexity

**Deliverables:**
- Full Display campaign support
- 10-12 optimization rules
- Complete dashboard integration
- Recommendations workflow

---

### **18. Video Campaigns (YouTube)** (15-20 hours)
**Status:** PLANNED (Campaign Type Expansion)  
**Dependencies:** Display complete

**Scope:**
Extend ACT to support YouTube advertising campaigns.

**Database Layer:**
- New table: `analytics.video_campaign_daily`
- Video creative performance
- Audience performance
- Placement performance (channels, videos)

**Rules Engine:**
- Video creative performance rules (10-12 rules)
- Audience targeting optimization
- View rate optimization
- CPV (cost per view) management
- Ad format rules (skippable, non-skippable, bumper)

**Dashboard Pages:**
- New "Video" page in navigation
- Video creatives tab
- Audiences tab
- Placements tab
- Recommendations tab
- Rules tab

**Challenges:**
- Video-specific metrics (view rate, watch time, completion rate)
- Creative quality assessment
- Different conversion attribution

**Deliverables:**
- Full YouTube campaign support
- 10-12 optimization rules
- Complete dashboard integration
- Video performance analytics

---

### **19. Demand Gen Campaigns** (15-20 hours)
**Status:** PLANNED (Campaign Type Expansion)  
**Dependencies:** Video complete

**Scope:**
Extend ACT to support Demand Gen campaigns (multi-surface: YouTube, Discover, Gmail).

**Database Layer:**
- New table: `analytics.demand_gen_campaign_daily`
- Multi-surface performance data
- Creative performance across surfaces
- Audience performance

**Rules Engine:**
- Multi-surface optimization rules (10-12 rules)
- Creative performance by surface
- Audience expansion rules
- Conversion optimization
- Budget allocation across surfaces

**Dashboard Pages:**
- New "Demand Gen" page in navigation
- Surface performance breakdown
- Creatives tab
- Audiences tab
- Recommendations tab
- Rules tab

**Challenges:**
- Multi-surface complexity (different user intents)
- Surface-specific creative requirements
- Cross-surface optimization trade-offs

**Deliverables:**
- Full Demand Gen campaign support
- 10-12 optimization rules
- Multi-surface analytics
- Complete dashboard integration

---

### **20. Automated Report Generator** (20-25 hours)
**Status:** PLANNED (Advanced Features)  
**Dependencies:** Email reports complete

**Scope:**
Build AI-powered report generator similar to Markifact, creating monthly slide-based presentations with insights.

**Features:**
- Automated slide generation (PowerPoint/Google Slides)
- AI-generated insights and commentary
- Performance trend analysis
- Actionable recommendations
- Executive-ready formatting
- Custom branding per client

**Report Structure:**
1. Executive Summary (1 slide)
2. Month-over-Month Performance (2-3 slides)
3. Campaign Performance Breakdown (3-4 slides)
4. Top Performers & Opportunities (2 slides)
5. Recommendations Executed (2 slides)
6. Next Month Outlook (1 slide)

**AI Integration:**
- GPT-4 or similar for insights generation
- Trend detection and explanation
- Natural language summaries
- Anomaly highlighting

**Deliverables:**
- Report generation engine
- Slide template system
- AI insights integration
- Scheduled delivery system
- Client-ready monthly reports

---

### **21. Multi-User Support** (12-15 hours)
**Status:** PLANNED (Advanced Features)  
**Dependencies:** None

**Scope:**
Extend ACT from single-user to multi-user system with roles and permissions.

**User Roles:**
1. **Admin:** Full access (Christopher)
2. **Manager:** Can approve recommendations, modify rules
3. **Analyst:** Read-only + recommendation suggestions
4. **Client:** Limited view (their account only)

**Features:**
- User registration and authentication
- Role-based access control (RBAC)
- Activity logging (who did what, when)
- User management interface
- Team collaboration features
- Client portal (limited view)

**Permissions Matrix:**
| Action | Admin | Manager | Analyst | Client |
|--------|-------|---------|---------|--------|
| View data | ✅ | ✅ | ✅ | ✅ (own only) |
| Accept recommendations | ✅ | ✅ | ❌ | ❌ |
| Create rules | ✅ | ✅ | ❌ | ❌ |
| Modify rules | ✅ | ✅ | ❌ | ❌ |
| Add users | ✅ | ❌ | ❌ | ❌ |
| View all clients | ✅ | ✅ | ✅ | ❌ |

**Deliverables:**
- User management system
- Role-based permissions
- Activity audit trail
- Team collaboration features
- Client portal

---

### **22. API Endpoints** (10-12 hours)
**Status:** PLANNED (Advanced Features)  
**Dependencies:** Multi-user support (for authentication)

**Scope:**
Build public API for external integrations.

**Endpoints:**
- GET `/api/v1/recommendations` - List recommendations
- POST `/api/v1/recommendations/{id}/accept` - Accept recommendation
- POST `/api/v1/recommendations/{id}/decline` - Decline recommendation
- GET `/api/v1/campaigns` - List campaigns with performance
- GET `/api/v1/rules` - List active rules
- POST `/api/v1/rules` - Create new rule
- GET `/api/v1/changes` - List change history

**Features:**
- RESTful API design
- API key authentication
- Rate limiting (100 requests/hour)
- Webhook support (for events)
- API documentation (Swagger/OpenAPI)
- SDK generation (Python, JavaScript)

**Use Cases:**
- Custom reporting dashboards
- Third-party integrations
- Mobile app development
- Automation workflows

**Deliverables:**
- Public API endpoints
- Authentication system
- API documentation
- Rate limiting
- Webhook system

---

## 📊 SUMMARY STATISTICS

**Total Planned Items:** 22  
**Total Estimated Time:** 200-270 hours

**Breakdown by Category:**
- **High Priority (Next 6-7 chats):** 7 items, 50-90 hours
  - Dashboard Design Upgrade (TBD)
  - Website Design Upgrade (TBD)
  - M9 Live Validation (4-6h)
  - Cold Outreach System (15-20h)
  - Finalise Shopping Campaigns (TBD)
  - Performance Max Campaigns (20-30h)
  - Testing & Polish (6-8h)
- **Medium Priority (Future-proofing + Features):** 9 items, 65-90 hours
- **Long-Term Priority (Major expansions):** 6 items, 85-90 hours

**Priority Breakdown:**
- **HIGH:** 7 items (items 1-7)
- **MEDIUM:** 9 items (items 8-16)
- **LONG-TERM:** 6 items (items 17-22)

---

## 🎯 NEXT STEPS

1. **Define scope for Dashboard Design Upgrade** (item #1)
2. **Define scope for Website Design Upgrade** (item #2)
3. **Define scope for Finalise Shopping Campaigns** (item #5)
4. **Begin Dashboard Design Upgrade** (NEXT CHAT)

---

**Document Version:** 1.0  
**Last Updated:** 2026-02-28  
**Next Review:** After Chat 50 complete
