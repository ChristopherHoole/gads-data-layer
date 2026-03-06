# PROJECT ROADMAP - Ads Control Tower (A.C.T.)

**Last Updated:** 2026-03-06
**Overall Completion:** ~99.9%
**Architecture:** 2-Tier (Master Chat → Claude Code)
**Local:** `C:\Users\User\Desktop\gads-data-layer`
**Marketing Site:** https://christopherhoole.online

---

## ✅ COMPLETED PHASES

| Phase | Chats | Status |
|-------|-------|--------|
| Foundation (Flask, DuckDB, auth, multi-client) | 1–17 | ✅ Complete |
| Code Cleanup (blueprints, validation, logging) | 18–21 | ✅ Complete |
| Dashboard 3.0 M1–M9 (date picker → live keyword execution) | 22–30b | ✅ Complete |
| Marketing Website (Next.js, Vercel, christopherhoole.online) | 31 + Master 4.0 | ✅ Complete |
| Rules Creation (41 rules across 5 entity types) | 41–46 | ✅ Complete |
| Multi-Entity Recommendations (1,492 active) | 47–49 | ✅ Complete |
| Module 4: Dashboard Design Upgrade (Google Ads-style tables) | 57–58 | ✅ Complete |
| Cold Outreach System (6 pages) | 59–64 | ✅ Complete |

---

## ✅ MODULE 4: DASHBOARD DESIGN UPGRADE (Chats 57-58)

**Commits:** 6f9fafa, 0bcee06, ef93abc, 86e01ed, 72407bf

Google Ads-style table redesign across all 5 entity pages:
- Control bar (All/Enabled/Paused filters, rows per page, action buttons)
- Column selector modal (Default / Performance / Additional groups)
- Session-based column persistence per entity
- Status dots: Green (enabled) / Grey (paused)
- ROAS color coding: Green ≥4.0x / Yellow 2.0–4.0x / Red <2.0x
- Actions menus per entity type
- Shared table-styles.css

---

## ✅ COLD OUTREACH SYSTEM (Chats 59-64)

**Commits:** d524448, c0e0eb8, 194ef2c

6 pages under `/outreach/` blueprint:

| Page | Route | Status |
|------|-------|--------|
| Leads | /outreach/leads | ✅ Complete |
| Queue | /outreach/queue | ✅ Complete |
| Sent | /outreach/sent | ✅ Complete |
| Replies | /outreach/replies | ✅ Complete |
| Templates | /outreach/templates | ✅ Complete |
| Analytics | /outreach/analytics | ✅ Complete |

**Analytics page features:** 8 KPI cards, 6-step engagement funnel, 5 charts, performance by track + template step tables.

**What's DB-only (live implementation planned):**
- Email sending (no SMTP/SendGrid yet)
- Open/click tracking (integer columns populated; no tracking pixel yet)
- CV attachment (placeholder toasts; no real file management yet)

---

## 🎯 NEXT PRIORITIES

### HIGH — Next 3-5 Chats

**1. Website Design Upgrade** (TBD hours)
Refinements to christopherhoole.online. Scope to be defined.
- Visual/typography/spacing improvements
- Animation enhancements
- Mobile responsiveness
- Potentially new sections

**2. M9 Live Validation** (4-6 hours)
Test negative keyword blocking and keyword expansion against real Google Ads account.
- Requires real Google Ads API credentials
- Validate dry-run → live execution flow
- Confirm changes write correctly

**3. Website: Contact Form Backend** (2-3 hours)
- POST to /api/leads endpoint
- Store in Google Sheets (consistent with existing lead capture on Vercel)
- Anti-spam protection

**4. Outreach: Live Email Sending** (8-12 hours)
- SMTP or SendGrid integration
- HTML templates with variable substitution
- CV attachment support
- Dry-run mode, error handling

**5. Outreach: CV Upload/Replace** (4-6 hours)
- File upload endpoint
- Store in /static/uploads/
- Preview, replace, remove
- Attach on send from Queue

**6. Outreach: Open/Click Tracking** (6-10 hours)
- Tracking pixel endpoint: /outreach/track/open/<email_id>
- Link redirect: /outreach/track/click/<email_id>
- CV open: /outreach/track/cv/<email_id>
- Auto-inject pixel + wrapped links on send
- Write to opened_at, clicked_at, cv_opened_at timestamp columns

**7. Outreach: Apollo.io Integration** (8-15 hours)
- API authentication
- Search/filter: country (UK/US/CA/AU/NZ), company size (5-50), industry (digital marketing)
- Field mapping: Apollo → ACT schema
- Deduplication on email
- UI: "Import from Apollo" modal with preview + confirm
- Import history log

**8. Testing & Polish** (6-8 hours)
Comprehensive post-redesign testing across dashboard + outreach.

### MEDIUM — Phase 3 + Features

- Website: SEO improvements (meta tags, sitemap, Open Graph)
- Website: LinkedIn integration (messaging or lead sourcing — scope TBD)
- Website: WhatsApp floating button (wa.me link with pre-filled message)
- System Changes tab → card grid (currently table, deferred from Chat 29)
- Unit tests (pytest, 80%+ coverage)
- Background job queue (Celery + Redis — replace daemon threads)
- Database indexes (optimize slow queries)
- CSRF protection (full Flask-WTF, remove current exemptions)
- Email reports (automated weekly/monthly)
- Smart alerts (ROAS drop, budget pacing, budget overspend)

### LONG-TERM — Major Expansions

- Performance Max Campaigns (20-30 hours — asset groups, 10-15 rules, new page)
- Display Campaigns (15-20 hours)
- Video Campaigns / YouTube (15-20 hours)
- Demand Gen Campaigns (15-20 hours)
- Automated Report Generator (AI insights, monthly slide-based — 20-25 hours)
- Multi-User Support (roles, permissions, client portal — 12-15 hours)
- API Endpoints (REST API for external integrations — 10-12 hours)

---

## 📊 CURRENT SYSTEM STATE

**Rules:** 41 active (13 campaign + 6 keyword + 4 ad_group + 4 ad + 14 shopping)

**Recommendations:**
- Campaigns: 110 (13 rules generating)
- Keywords: 1,256 (6 rules generating)
- Shopping: 126 (13 rules generating)
- Ad Groups: 0 (conditions not met with current data — expected)
- Ads: 0 (analytics.ad_daily table missing — known limitation)
- **Total: 1,492 active**

**Outreach:**
- Leads: seeded synthetic data
- Email templates: 4 steps × 4 tracks = 16 templates
- Analytics: open_count/click_count populated via tools/seed_outreach_clicks.py

**Known Database Gap:**
- `analytics.ad_daily` table does not exist → Ads rules cannot generate recommendations

---

## 🔧 DEVELOPMENT WORKFLOW

**Start Claude Code:**
```powershell
cd C:\Users\User\Desktop\gads-data-layer
npx @anthropic-ai/claude-code
```

**Test Flask:**
```powershell
taskkill /IM python.exe /F
cd C:\Users\User\Desktop\gads-data-layer
.\.venv\Scripts\Activate.ps1
python act_dashboard/app.py
```
Test at http://localhost:5000 in Opera.

**Git commit (after Master Chat approval):**
```powershell
git add .
git commit -m "Chat XX: [Description]"
git push origin main
```

**Reference docs:**
- CLAUDE_CODE_WORKFLOW.md — how to work with Claude Code
- MASTER_KNOWLEDGE_BASE.md — full project history and technical detail
- PLANNED_WORK.md — detailed work items with time estimates
- KNOWN_PITFALLS.md — troubleshooting
- LESSONS_LEARNED.md — best practices

---

**Version:** 3.0 | **Last Updated:** 2026-03-06
