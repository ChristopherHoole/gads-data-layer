# PROJECT ROADMAP - Ads Control Tower (A.C.T.)

**Last Updated:** 2026-03-09
**Overall Completion:** ~99.9%
**Architecture:** 2-Tier (Master Chat → Claude Code)
**Local:** `C:\Users\User\Desktop\gads-data-layer`
**Marketing Sites:** https://christopherhoole.online | https://christopherhoole.com

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
| Cold Outreach System — UI (6 pages) | 59–64 | ✅ Complete |
| Real Data Ingestion Pipeline | 67 | ✅ Complete (blocked on API access) |
| Live Email Sending (Gmail SMTP) | 68 | ✅ Complete |
| Outreach Functions + UI Polish | 69–80 | ✅ Complete |
| UI Cleanup (layout gap, client selector, rules card) | 81–83 | ✅ Complete |

---

## ✅ CHAT 67 — REAL DATA INGESTION PIPELINE

**Commit:** e9bcb3f

- `src/gads_pipeline/v1_runner.py` — fixed DB write path to warehouse.duckdb
- `scripts/copy_all_to_readonly.py` — copies all 5 analytics tables to warehouse_readonly
- `tools/run_ingestion.py` — orchestration script (pull + copy + summary)

**Status:** Built and tested with mock data. Live pull blocked on Google Ads API Basic Access approval (Case ID 24460840136 — applied March 4, 2026).

---

## ✅ CHAT 68 — LIVE EMAIL SENDING

**Commit:** fe4a0d7 + subsequent bug fixes

**Infrastructure:**
- Domain: `christopherhoole.com` (Namecheap)
- Email: `chris@christopherhoole.com` (Google Workspace Business Starter)
- DKIM/SPF: ✅ Authenticated
- `act_dashboard/secrets/email_config.yaml` — local only, gitignored

**Files:**
- `act_dashboard/email_sender.py` — `send_email()`, `load_email_config()`, `substitute_variables()`, `check_daily_limit()`
- `act_dashboard/routes/outreach.py` — `queue_send()` upgraded to live SMTP

**Bugs fixed post-commit:**
- MIMEText missing `"utf-8"` third arg — special chars garbled → fixed
- `body_html` conversion (`\n → <br>`) missing from `queue_send()` — emails sent as plain text → fixed
- `showToast` missing from success branch of `sendCard()` — no toast on send → fixed

**Daily limit:** 100 emails/day (configurable in email_config.yaml)

---

## ✅ CHATS 69–80 — OUTREACH FUNCTIONS + UI POLISH

| Chat | Feature |
|------|---------|
| 69 | Email signature appended to all outgoing emails |
| 70 | CV upload & file storage (Templates page) |
| 71 | CV attachment on send (Queue page) |
| 72 | Open/click/CV tracking pixels + auto-inject on send |
| 73 | Reply inbox polling (Gmail IMAP, 120s daemon — outreach_poller.py) |
| 74 | Send reply from Replies page via SMTP |
| 75 | Edit this email (Queue ✏ button) |
| 76 | Universal slidein design across all outreach pages |
| 77 | Switch template (Queue 📋 button) |
| 78 | Queue auto-scheduling (queue_scheduler.py, daemon thread, 300s) |
| 79 | Google Ads-style date picker (replaces Flatpickr, datepicker.css) |
| 80 | Remove rules slidein from Campaigns, Keywords, Ads, Shopping |

---

## ✅ CHAT 81 — TABLE-STYLES.CSS LAYOUT FIX

**Commit:** 8968d64
- `table-styles.css` was originally written as a standalone HTML prototype — contained `body { padding: 20px }` and `.container { background: white; border-radius: 8px; padding: 24px }` which overrode Flask app layout
- Caused a white rounded box with gaps on all 5 entity pages; dashboard unaffected (doesn't load table-styles.css)
- Fix: removed `body` and `.container` blocks entirely

---

## ✅ CHAT 82 — REMOVE DUPLICATE CLIENT SELECTOR FROM OUTREACH

**Commit:** 9ee01fb — three separate bugs:
1. All 6 outreach templates had `<select class="outreach-client-selector">` in their page header — navbar.html already renders a client selector → two pickers visible → removed select from all 6 templates
2. `outreach.css` had `.d-none { display: none !important }` overriding Bootstrap responsive classes → navbar text hidden on all outreach pages → removed the rule
3. Templates and Analytics routes missing `client_name=config.client_name` in `render_template()` → client name blank → added `config = get_current_config()` to analytics route + `client_name=config.client_name` to both render_template calls

---

## ✅ CHAT 83 — REMOVE RULES CARD FROM CAMPAIGNS AND SHOPPING

**Commit:** f531bd8
- Removed `{% include 'components/rules_card.html' %}` from campaigns.html and shopping_new.html
- Rules tab (Rules (41)) preserved on both pages — only the bottom summary block removed

---

## 🎯 NEXT PRIORITIES

### IMMEDIATE

**Apollo.io Lead Import** (8-15 hours)
- API authentication
- Search/filter: country (UK/US/CA/AU/NZ), company size (5-50), industry (digital marketing)
- Field mapping: Apollo → ACT schema
- UI: "Import from Apollo" modal with preview + confirm

**M9 Live Validation** (4-6 hours)
- Test negative keyword blocking and keyword expansion against real Google Ads account
- Requires Basic Access approval (pending)

**Website Design Upgrade** (TBD hours)
- Refinements to christopherhoole.com / christopherhoole.online
- Scope to be defined

**Testing & Polish** (6-8 hours)
- Comprehensive post-outreach testing

### MEDIUM — Phase 3 + Features

- Website: Contact Form Backend (Google Sheets integration)
- Website: SEO improvements (meta tags, sitemap, Open Graph)
- Website: LinkedIn integration
- Website: WhatsApp floating button
- System Changes tab → card grid (deferred from Chat 29)
- Unit tests (pytest, 80%+ coverage)
- Background job queue (Celery + Redis)
- Database indexes
- Email reports (automated weekly/monthly)
- Smart alerts (ROAS drop, budget pacing)

### LONG-TERM — Major Expansions

- Performance Max Campaigns (20-30 hours)
- Display Campaigns (15-20 hours)
- Video/YouTube Campaigns (15-20 hours)
- Demand Gen Campaigns (15-20 hours)
- Automated Report Generator (20-25 hours)
- Multi-User Support (12-15 hours)
- API Endpoints (10-12 hours)
- Indeed job listing connector (planned)

---

## 📊 CURRENT SYSTEM STATE

**Rules:** 41 active (13 campaign + 6 keyword + 4 ad_group + 4 ad + 14 shopping)

**Recommendations:**
- Campaigns: 110 | Keywords: 1,256 | Shopping: 126
- Ad Groups: 0 (conditions not met) | Ads: 0 (ad_daily table missing)
- **Total: 1,492 active**

**Outreach:**
- Live email sending: ✅ Gmail SMTP via chris@christopherhoole.com
- 16 email templates (4 steps × 4 tracks)
- Daily limit: 100 emails/day
- All 10 original outreach functions now live ✅
- Single client selector on all outreach pages ✅

**Known Database Gap:**
- `analytics.ad_daily` table does not exist → Ads rules cannot generate recommendations

**Google Ads API:**
- Test Access only — Basic Access application pending (Case 24460840136)

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

**Git commit (Master Chat only — after Christopher confirms in Opera):**
```powershell
taskkill /IM python.exe /F
cd C:\Users\User\Desktop\gads-data-layer
git add .
git commit -m "Chat XX: [Description]"
git push origin main
```

**Reference docs:**
- MASTER_KNOWLEDGE_BASE.md — full project history and technical detail
- KNOWN_PITFALLS.md — troubleshooting
- LESSONS_LEARNED.md — best practices

---

**Version:** 5.0 | **Last Updated:** 2026-03-09
