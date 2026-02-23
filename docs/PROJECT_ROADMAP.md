# PROJECT ROADMAP - Google Ads Data Layer (ACT Dashboard)

**Last Updated:** 2026-02-23
**Current Phase:** Marketing Website ✅ COMPLETE | Dashboard 3.0 M8 ✅ COMPLETE | M9 next
**Overall Completion:** ~98% (Foundation + Polish + Website + Dashboard 3.0 M1–M8 complete)
**Mode:** Ready for next development phase

---

## 🎯 PROJECT VISION

**Mission:** Build a production-ready, automated Google Ads management dashboard that generates, approves, and executes bid/budget recommendations across Keywords, Ads, and Shopping campaigns.

**Core Features:**
- Multi-client support
- Real-time recommendation generation
- Approval workflows
- Automated execution (dry-run + live)
- Change tracking and rollback
- Email reporting and alerts
- **Google Ads-inspired UI** (familiar to millions of users)
- **Professional marketing website** (christopherhoole.online)

---

## ✅ COMPLETED WORK

### **Phase 0: Foundation (Chats 1-17)** ✅
- Chats 1-11: Flask app, DuckDB, auth, multi-client YAML
- Chats 12-16: Shopping module, execution API, dry-run + live, change tracking, Google Ads API
- Chat 17: Architecture refactor — unified recommendation system

### **Phase 1: Code Cleanup & Foundation Hardening** ✅
- 16/16 routes → 8 modular blueprints
- Input validation, rate limiting, logging, cache expiration, error handling

### **Phase 2: Polish & Refactoring** ✅
- DRY helpers, function refactoring, type hints, config validation

### **Marketing Website** ✅ (Complete)
**Tech Stack:** Next.js 14, Tailwind CSS, Framer Motion, shadcn/ui, Three.js WebGL
**Deployment:** Vercel (https://www.christopherhoole.online)
**Repository:** https://github.com/ChristopherHoole/act-website

**Completed Sections (11/13):**
1. ✅ S1: Hero (Three.js interactive shader, 20px h1, scroll indicator)
2. ✅ S2: About Me (4 paragraphs, blue highlights, bullet points)
3. ✅ S3: The Problem (3-column card grid)
4. ✅ S4: The Difference (3 paragraphs with blue highlights)
5. ✅ S5: Work History (vertical timeline, 7 positions)
6. ✅ S6: Skills & Platforms (4-column grid, 8 cards)
7. ✅ S7: What A.C.T Does (4 modules + capabilities box)
8. ❌ S8: How I Work (removed)
9. ❌ S9: What You Get Each Week (removed)
10. ✅ S10: Why I'm Different (16 USP cards)
11. ✅ S11: FAQ (10 collapsible questions)
12. ✅ S12: Contact Form (2-column layout, form + 3 steps)
13. ✅ S13: Footer (18px pure white, LinkedIn + email links)
14. ✅ Navigation (logo + name, reordered links, 14px CTA button)

**Key Deliverables:**
- Chat 31: Wireframe creation (13 sections designed, 306KB base64 images)
- Master Chat 4.0: Full rebuild (11 sections implemented)
- All components mobile responsive
- Collapsible FAQ with smooth transitions
- Contact form (frontend ready, backend pending)
- Custom domain configured (GoDaddy DNS → Vercel)
- Git repository created and pushed to GitHub
- Production deployment complete

### **Dashboard 3.0** ✅ (M1–M8 complete)
- Chat 22 M1: Date picker (Flatpickr, session persistence)
- Chat 23 M2: Metrics cards (Jinja2 macros, all 6 pages)
- Chat 24 M3: Chart overhaul (dual-axis, 4 toggleable metrics)
- Chat 25 M4: Table overhaul (full Google Ads column sets, server-side sort)
- Chat 26 M5: Card-based Rules tab (CRUD, rules_config.json, rules_api.py)
- Chat 27 M6: Recommendations engine + UI (global page + campaigns tab)
- Chat 28 M7: Accept/Decline/Modify wiring + 4-tab recommendations UI
- Chat 29 M8: Changes page + Radar monitoring ✅ COMPLETE

---

## 📊 PROGRESS METRICS

| Phase | Completion | Status |
|-------|------------|--------|
| Foundation (0) | 100% ✅ | Complete |
| Code Cleanup (1) | 100% ✅ | Complete |
| Polish (2) | 100% ✅ | Complete |
| Marketing Website | 100% ✅ | Complete |
| Dashboard 3.0 (M1–M8) | 100% ✅ | Complete |
| Future-Proofing (3) | 0% 📋 | Planned |
| Features (30+) | 0% 📋 | Planned |

---

## 🎯 NEXT MILESTONES

### **Completed:**
- ✅ Chat 22: M1 Date Picker
- ✅ Chat 23: M2 Metrics Cards
- ✅ Chat 24: M3 Chart Overhaul
- ✅ Chat 25: M4 Table Overhaul
- ✅ Chat 26: M5 Rules Tab
- ✅ Chat 27: M6 Recommendations Engine + UI
- ✅ Chat 28: M7 Accept/Decline/Modify + 4-tab UI
- ✅ Chat 29: M8 Changes + Radar Monitoring
- ✅ Chat 31: Marketing Website Wireframe
- ✅ Master Chat 4.0: Marketing Website Rebuild + Deployment

### **Short-term:**
- 🎯 Chat 30: M9 Search Terms / Keywords recommendations — NEXT
- 📋 Website: Connect contact form to /api/leads endpoint
- 📋 Website: Optional SEO improvements (meta tags, sitemap)
- 📋 System Changes tab → cards (currently table, deferred from Chat 29)
- 📋 M5 Rules tab rollout to Ad Groups, Keywords, Ads, Shopping
- 📋 Live Google Ads API execution on accept/modify routes

### **Medium-term:**
- 📋 Phase 3: Future-Proofing (unit tests, job queue, DB indexes, CSRF)
- 📋 Email Reports
- 📋 Smart Alerts

---

## 🔄 CHANGELOG

### **2026-02-23 (Master Chat 4.0 — Marketing Website Deployment)**

**Completed:**
- ✅ Complete website rebuild (11/13 sections, S8/S9 removed)
- ✅ All components created: Hero, AboutMe, TheProblem, TheDifference, WorkHistory, Skills, WhatACTDoes, WhyDifferent, FAQ, ContactForm, Footer, Navigation
- ✅ Typography standardized (18-20px pure white on dark, 16-20px black on light)
- ✅ Navigation: A.C.T logo added, links reordered (About - Experience - A.C.T), sentence case
- ✅ FAQ: Collapsible accordion with smooth transitions
- ✅ Contact form: Frontend complete with validation
- ✅ Three.js Hero: Fixed colorSpace compatibility issue
- ✅ Built for production (Next.js build successful)
- ✅ Deployed to Vercel: https://act-website-fawn.vercel.app
- ✅ Custom domain configured: https://www.christopherhoole.online (DNS propagated)
- ✅ Root domain: https://christopherhoole.online (DNS propagating)
- ✅ GitHub repository created: https://github.com/ChristopherHoole/act-website
- ✅ Git commit + push complete (35 files changed, 3,299 insertions)
- ✅ GoDaddy DNS configured (A record + CNAME)

**Files delivered:**
- 12 component files (Hero.tsx through Navigation.tsx)
- page.tsx (updated, HowIWork and WeeklyDeliverables removed)
- globals.css (text-body-dark and text-body-light classes)
- act_logo.svg + favicon.ico
- All files mobile responsive

**Key decisions:**
- Removed S8 (How I Work) and S9 (What You Get Each Week) for cleaner initial launch
- Navigation links sentence case (not uppercase) for better readability
- FAQ accordion style (one open at a time, all closed by default)
- Contact form frontend ready, backend deferred to post-deployment
- Three.js colorSpace line removed for r128 compatibility

### **2026-02-23 (Chat 29 — M8 Changes + Radar Monitoring)**

**Completed:**
- ✅ Radar background job (`act_autopilot/radar.py`) — 60s daemon thread
- ✅ Radar evaluates ROAS/CVR degradation (≥15% drop → auto-revert)
- ✅ `monitoring_minutes` field added to all 13 rules (fast-test mode)
- ✅ `changes.py` blueprint created — `/changes` route moved from `recommendations.py`
- ✅ Changes page Bootstrap 5 rewrite — summary strip + 2-tab UI
- ✅ My Actions tab — card grid (same M6/M7 format), filter bar
- ✅ System Changes tab — table from `ro.analytics.change_log` (cards deferred)
- ✅ 5th Reverted tab added to `/recommendations` and `/campaigns`
- ✅ Reverted card variant — red top bar, red outcome block, revert_reason
- ✅ Summary strip updated to 5 counts on both recommendation pages
- ✅ `last_run` bug fixed in `_get_summary()`
- ✅ `/recommendations/cards` extended to return `reverted` array
- DuckDB pattern established: open `warehouse.duckdb` read-write + ATTACH readonly
- 8 files created/modified
- **Docs:** `CHAT_29_DETAILED_SUMMARY.md` + `CHAT_29_HANDOFF.md`
- **Wireframe:** `M8_WIREFRAME.html`

### **2026-02-22 (Chat 28 — M7 Accept/Decline/Modify + 4-Tab UI)**
- ✅ Accept/Decline/Modify POST routes — fully wired
- ✅ `changes` audit table created in warehouse.duckdb
- ✅ 4-tab UI: Pending / Monitoring / Successful / Declined
- ✅ Card animations, badge decrements, toast confirmations
- 4 files changed

### **2026-02-22 (Chat 27 — M6 Recommendations Engine + UI)**
- ✅ recommendations table + engine + global page + campaigns tab
- ✅ 48 pending recs generated, duplicate prevention working
- 5 files total

### **2026-02-22 (Chat 26 — M5 Card-Based Rules Tab)**
- ✅ rules_config.json (13 rules), rules_api.py (6 routes), full CRUD
- ✅ Card UI, slide-in drawer, campaign picker
- 6 files created/modified

---

**Last Updated:** 2026-02-23
**Next Step:** Chat 30 — M9 Search Terms / Keywords recommendations
