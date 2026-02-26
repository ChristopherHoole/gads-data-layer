# PROJECT ROADMAP - Google Ads Data Layer (ACT Dashboard)

**Last Updated:** 2026-02-26
**Current Phase:** Rules Creation ✅ COMPLETE (41 rules across 5 types) | Marketing Website ✅ COMPLETE | Dashboard 3.0 M9 ✅ COMPLETE
**Overall Completion:** ~99% (Foundation + Polish + Website + Dashboard 3.0 + Rules Creation complete)
**Mode:** Ready for Rules Tab UI Components + Recommendations Engine Extension

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

### **Dashboard 3.0** ✅ (M1–M9 complete)
- Chat 22 M1: Date picker (Flatpickr, session persistence)
- Chat 23 M2: Metrics cards (Jinja2 macros, all 6 pages)
- Chat 24 M3: Chart overhaul (dual-axis, 4 toggleable metrics)
- Chat 25 M4: Table overhaul (full Google Ads column sets, server-side sort)
- Chat 26 M5: Card-based Rules tab (CRUD, rules_config.json, rules_api.py)
- Chat 27 M6: Recommendations engine + UI (global page + campaigns tab)
- Chat 28 M7: Accept/Decline/Modify wiring + 4-tab recommendations UI
- Chat 29 M8: Changes page + Radar monitoring ✅ COMPLETE
- Chat 30a M9 Phase 1: Search Terms tab + Negative Keyword Suggestions ✅ COMPLETE
- Chat 30b M9 Phase 2: Live Execution + Keyword Expansion ✅ COMPLETE

### **Rules Creation Phase** ✅ (41 rules complete - 100%)
- Chat 41: M5 Rules tab rollout (Keywords, Ad Groups, Ads, Shopping pages) - ead441b
- Chat 42: 6 Keyword rules (keyword_1 through keyword_6) - d9d0b33 + 65b6986
- Chat 43: 4 Ad Group rules (ad_group_1 through ad_group_4) - 4a9cdbe
- Chat 44: 4 Ad rules (ad_1 through ad_4) - 52b042e
- Chat 45: 14 Shopping rules (shopping_1 through shopping_14, Chat 12 migration) - 86fc939
- **Total: 41 rules** (13 campaign + 6 keyword + 4 ad_group + 4 ad + 14 shopping)
- All rules Constitution-compliant (cooldowns ≥7 days, monitoring ≥7 days, risk levels appropriate)

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
- ✅ Chat 30a: M9 Phase 1 Search Terms Table
- ✅ Chat 30b: M9 Phase 2 Live Execution + Keyword Expansion
- ✅ Chat 41: M5 Rules tab rollout to 4 pages
- ✅ Chat 42: 6 Keyword rules
- ✅ Chat 43: 4 Ad Group rules
- ✅ Chat 44: 4 Ad rules
- ✅ Chat 45: 14 Shopping rules

### **Short-term:**
- 🎯 Rules Tab UI Components (ad_group, ad, shopping) — NEXT (~3 hours)
- 🎯 Recommendations Engine Extension (all rule types, 15-25 hours)
- 📋 M9 live validation with real Google Ads account
- 📋 Website: Connect contact form to /api/leads endpoint
- 📋 Website: Optional SEO improvements (meta tags, sitemap)
- 📋 System Changes tab → cards (currently table, deferred from Chat 29)

### **Medium-term:**
- 📋 Phase 3: Future-Proofing (unit tests, job queue, DB indexes, CSRF)
- 📋 Email Reports
- 📋 Smart Alerts

---

## 🔄 CHANGELOG

### **2026-02-24 (Chat 30b — M9 Phase 2 Live Execution + Keyword Expansion)**

**Completed:**
- ✅ Live Google Ads API execution for negative keyword blocking
- ✅ Campaign-level and ad-group-level negative keyword support
- ✅ Keyword expansion opportunities flagging (4 criteria)
- ✅ "Add as Keyword" functionality with match type + bid suggestions
- ✅ Dry-run mode for safe testing (both actions)
- ✅ Changes table audit logging (both actions)
- ✅ Bulk selection support (row-level + bulk)
- ✅ Match type override (EXACT/PHRASE/BROAD dropdowns)
- ✅ Bid override (£0.10 minimum, user customizable)
- ✅ Toast notifications (success/error messages)
- ✅ All 16 success criteria passing (dry-run validated)
- 84 lines added in google_ads_api.py (new function)
- 456 lines added in keywords.py (2 routes + 2 helpers)
- ~400 lines modified in keywords_new.html (modals + JavaScript)
- **Docs:** `CHAT_30B_SUMMARY.md` + `CHAT_30B_HANDOFF.md`
- **Time:** 4 hours actual vs 7-9 hours estimated (53% efficiency)

**Key features:**
- `add_adgroup_negative_keyword()` function for ad-group-level blocking
- `check_keyword_exists()` prevents duplicate keyword creation
- `flag_expansion_opportunities()` identifies high-performers (CVR ≥5%, ROAS ≥4.0x, Conv. ≥10)
- `/keywords/add-negative` POST route (campaign or ad-group level)
- `/keywords/add-keyword` POST route (with duplicate checking)
- Dry-run first architecture (enables testing without API credentials)
- Google Ads config detection (3 fallback paths)
- Sequential execution with partial success support

**Expansion criteria (all 4 must be met):**
1. CVR ≥5% (2x typical industry average)
2. ROAS ≥4.0x (highly profitable)
3. Conversions ≥10 (statistical significance)
4. NOT already exists (duplicate prevention)

**Match type suggestions:**
- EXACT → EXACT (maintain precision)
- PHRASE → PHRASE (maintain moderate targeting)
- BROAD → PHRASE (tighten for safety)

**Deferred to production:**
- Live API validation (requires real Google Ads account)
- Batching for >10 items (sequential only for now)
- CSRF protection (Flask-WTF)

### **2026-02-26 (Chat 41 — M5 Rules Tab Rollout to 4 Pages)**

**Completed:**
- ✅ Rules tab structure on Keywords, Ad Groups, Ads, Shopping pages
- ✅ Tab labels show rule counts (6, 4, 4, 14 respectively)
- ✅ rules_api.py extended with rule_type filtering
- ✅ Component files created (placeholder structures)
- ✅ All 4 pages updated with Rules tab integration
- Time: 3.5 hours actual vs 4-6 hours estimated (58-88% efficiency)
- **Commit:** ead441b
- **Docs:** CHAT_41_SUMMARY.md + CHAT_41_HANDOFF.md

**Key features:**
- Systematic tab addition across all 4 pages
- Rule count display (ready for future rule creation)
- Consistent UI pattern across all pages
- Foundation for Chat 42-45 rule creation

### **2026-02-26 (Chat 42 — 6 Keyword Rules Creation)**

**Completed:**
- ✅ 6 Keyword rules migrated to rules_config.json
- ✅ Rules: keyword_1 through keyword_6
- ✅ Constitution compliance verified (all rules 7+ day cooldowns/monitoring)
- ✅ Keywords Rules tab component created
- ✅ Bug fix: Nested tab-pane wrapper removed from keywords_rules_tab.html
- Time: ~4 hours actual vs 4-6 hours estimated
- **Commits:** d9d0b33 (initial) + 65b6986 (bug fix)
- **Docs:** CHAT_42_SUMMARY.md + CHAT_42_HANDOFF.md

**6 Keyword Rules:**
1. keyword_1: Pause High Cost Low Conv (cost ≥£100, 0 conversions, 7-day cooldown)
2. keyword_2: Increase Bid High ROAS (ROAS ≥5.0, +20% bid, 14-day cooldown)
3. keyword_3: Decrease Bid Low ROAS (ROAS <2.0, -20% bid, 14-day cooldown)
4. keyword_4: Pause Low QS High Cost (QS ≤3, cost ≥£50, 7-day cooldown)
5. keyword_5: Flag Low CTR (CTR <1%, 20+ impressions, 7-day cooldown)
6. keyword_6: Flag High Impr Low Click (1,000+ impressions, CTR <0.5%, 7-day cooldown)

**Key technical details:**
- keyword_4: 2 conditions (QS ≤3 AND cost ≥£50, both required)
- keyword_5 & keyword_6: Flag-only rules (medium risk, diagnostic)
- All pause rules: High risk tier

### **2026-02-26 (Chat 43 — 4 Ad Group Rules Creation)**

**Completed:**
- ✅ 4 Ad Group rules migrated to rules_config.json
- ✅ Rules: ad_group_1 through ad_group_4
- ✅ Constitution compliance verified
- ✅ Ad Groups Rules tab component created
- Time: ~3 hours actual vs 4-6 hours estimated (50-75% efficiency)
- **Commit:** 4a9cdbe
- **Docs:** CHAT_43_SUMMARY.md + CHAT_43_HANDOFF.md
- **Total rules:** 23 (13 campaign + 6 keyword + 4 ad_group)

**4 Ad Group Rules:**
1. ad_group_1: Pause High Cost No Conv (cost ≥£150, 0 conversions, 7-day cooldown)
2. ad_group_2: Increase Bid High ROAS (ROAS ≥5.0, +20% bid, 14-day cooldown)
3. ad_group_3: Decrease Bid Low ROAS (ROAS <2.0, -20% bid, 14-day cooldown)
4. ad_group_4: Flag Low CTR (CTR <1.5%, 50+ impressions, 7-day cooldown)

### **2026-02-26 (Chat 44 — 4 Ad Rules Creation)**

**Completed:**
- ✅ 4 Ad rules migrated to rules_config.json
- ✅ Rules: ad_1 through ad_4
- ✅ Constitution compliance verified
- ✅ Ads Rules tab component created
- ✅ String comparison pattern: "eq" operator with "POOR"/"AVERAGE"
- Time: 3h 25min actual vs 4-6 hours estimated (57-85% efficiency)
- **Commit:** 52b042e
- **Docs:** CHAT_44_SUMMARY.md + CHAT_44_HANDOFF.md
- **Total rules:** 27 (13 campaign + 6 keyword + 4 ad_group + 4 ad)

**4 Ad Rules:**
1. ad_1: Pause High Cost No Conv (cost ≥£100, 0 conversions, 7-day cooldown)
2. ad_2: Flag Low CTR (CTR <2%, 100+ impressions, 7-day cooldown)
3. ad_3: Flag Poor Ad Strength (ad_strength "eq" "POOR", 7-day cooldown)
4. ad_4: Flag Average Ad Strength (ad_strength "eq" "AVERAGE", 14-day cooldown)

**Key technical decision:**
- String comparison: condition_operator "eq" + condition_value "POOR" (not enum)
- ad_3: Higher priority (7-day) vs ad_4 (14-day) due to severity

### **2026-02-26 (Chat 45 — 14 Shopping Rules Migration)**

**Completed:**
- ✅ 14 Shopping rules migrated from Chat 12 Python code to rules_config.json
- ✅ Rules: shopping_1 through shopping_14
- ✅ All Constitution compliance verified (cooldowns, monitoring, risk levels)
- ✅ Comprehensive validation script created (validate_ad_rules.py)
- ✅ All 14 rules tested incrementally (5 batches)
- Time: 5.5 hours actual vs 6-10 hours estimated (55-91% efficiency)
- **Commit:** 86fc939
- **Docs:** CHAT_45_SUMMARY.md + CHAT_45_HANDOFF.md + CHAT_45_BRIEF.md
- **Total rules:** 41 (13 campaign + 6 keyword + 4 ad_group + 4 ad + 14 shopping)
- **🎉 RULES CREATION PHASE: 100% COMPLETE**

**14 Shopping Rules:**

**Budget Rules (3):**
1. shopping_1: Increase Budget High ROAS (ROAS ≥4.5, +15%, 7-day cooldown)
2. shopping_2: Decrease Budget Low ROAS (ROAS <2.0, -20%, 7-day cooldown)
3. shopping_3: Pause Budget Wasting (cost ≥£200, 0 conversions, 14-day cooldown, high risk)

**ROAS Performance (3):**
4. shopping_4: Flag Low ROAS (ROAS <2.0, 7-day cooldown, medium risk)
5. shopping_5: Flag Very Low ROAS (ROAS <1.5, 5+ conversions, 7-day cooldown, low risk)
6. shopping_6: Pause Extremely Low ROAS (ROAS <1.0, 14-day cooldown, high risk)

**Feed Errors (3):**
7. shopping_7: Flag High Cost No Conv (cost ≥£100, 0 conversions, 7-day cooldown, low risk)
8. shopping_8: Flag High Feed Errors (feed_error_count ≥20, 7-day cooldown, medium risk)
9. shopping_9: Pause Critical Feed Errors (feed_error_count ≥50, 14-day cooldown, high risk)

**Out-of-Stock + IS (3):**
10. shopping_10: Flag Out-of-Stock Products (out_of_stock_product_count ≥5, 7-day cooldown, low risk)
11. shopping_11: Flag Low Impression Share (search_impression_share <30%, 7-day cooldown, medium risk)
12. shopping_12: Flag IS Lost to Budget (search_impression_share <30%, cost ≥£150, 7-day cooldown, medium risk)

**IS Budget + Opt Score (2):**
13. shopping_13: Increase Budget IS-Constrained (search_impression_share <40%, ROAS ≥3.0, +15%, 7-day cooldown)
14. shopping_14: Flag Low Opt Score (optimization_score <60%, 14-day cooldown, low risk)

**Key Specifications:**
- Campaign-level scope (product performance aggregated)
- Standard Constitution (no Shopping-specific exceptions)
- Thresholds: ROAS (4.5/2.0/1.5/1.0), Feed errors (20/50), IS (30%), Opt score (60%)
- Column NULL handling: Rules created even for unpopulated columns (feed_error_count, out_of_stock_product_count, optimization_score)

**Master-Approved Thresholds:**
- ROAS increase trigger: 4.5x (high-performing campaigns only)
- ROAS decrease trigger: 2.0x (underperforming campaigns)
- ROAS pause triggers: 1.5x (early warning, 5 conv. threshold), 1.0x (critical)
- Feed error flag: 20 errors (monitoring threshold)
- Feed error pause: 50 errors (critical threshold)
- IS thresholds: 30% (flag), 40% (budget increase with ROAS ≥3.0)
- Out-of-stock: 5 products (multiple product issue, not single SKU)
- Optimization score: 60% (Google's "good" threshold)

### **2026-02-24 (Chat 30a — M9 Phase 1 Search Terms Table)**

**Completed:**
- ✅ Search Terms tab on Keywords page (16-column data table)
- ✅ Campaign, status, match type filters + client-side search
- ✅ Server-side pagination (10/25/50/100 per page)
- ✅ Negative keyword flagging logic (3 criteria: CVR/cost/CTR)
- ✅ Row-level + bulk "Add as Negative" actions (UI only)
- ✅ Bootstrap 5 modal for action preview
- ✅ All 16 success criteria passing
- 431 lines modified in keywords.py
- 216 lines added in keywords_new.html
- **Docs:** `CHAT_30A_SUMMARY.md` + `CHAT_30A_HANDOFF.md`

**Key features:**
- Uses `ro.analytics.search_term_daily` (23 columns)
- Respects M1 session date range
- Automated flagging: 0% CVR + ≥10 clicks, ≥£50 cost + 0 conversions, CTR <1% + ≥20 impressions
- Performance: <2s load, <1s filter, zero JS errors

**Deferred to Phase 2 (Chat 30b):**
- Live Google Ads API execution for "Add as Negative"
- Keyword expansion opportunities
- "Add as Keyword" functionality

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

**Last Updated:** 2026-02-26
**Next Step:** Rules Tab UI Components (~3 hours) | Recommendations Engine Extension (15-25 hours)
