# PROJECT ROADMAP - Google Ads Data Layer (ACT Dashboard)

**Last Updated:** 2026-02-23
**Current Phase:** Dashboard 3.0 — M8 ✅ COMPLETE | M9 next
**Overall Completion:** ~97% (Foundation + Polish + Dashboard 3.0 M1–M8 complete)
**Mode:** Dashboard 3.0 Phase 2 in progress 🚧

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

### **Dashboard 3.0** ✅ (M1–M8 complete)
- Chat 22 M1: Date picker (Flatpickr, session persistence)
- Chat 23 M2: Metrics cards (Jinja2 macros, all 6 pages)
- Chat 24 M3: Chart overhaul (dual-axis, 4 toggleable metrics)
- Chat 25 M4: Table overhaul (full Google Ads column sets, server-side sort)
- Chat 26 M5: Card-based Rules tab (CRUD, rules_config.json, rules_api.py)
- Chat 27 M6: Recommendations engine + UI (global page + campaigns tab)
- Chat 28 M7: Accept/Decline/Modify wiring + 4-tab recommendations UI
- Chat 29 M8: Changes page + Radar monitoring ✅ COMPLETE (this chat)

---

## 📊 PROGRESS METRICS

| Phase | Completion | Status |
|-------|------------|--------|
| Foundation (0) | 100% ✅ | Complete |
| Code Cleanup (1) | 100% ✅ | Complete |
| Polish (2) | 100% ✅ | Complete |
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

### **Short-term:**
- 🎯 Chat 30: M9 Search Terms / Keywords recommendations — NEXT
- 📋 System Changes tab → cards (currently table, deferred from Chat 29)
- 📋 M5 Rules tab rollout to Ad Groups, Keywords, Ads, Shopping
- 📋 Live Google Ads API execution on accept/modify routes

### **Medium-term:**
- 📋 Phase 3: Future-Proofing (unit tests, job queue, DB indexes, CSRF)
- 📋 Email Reports
- 📋 Smart Alerts

---

## 🔄 CHANGELOG

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
