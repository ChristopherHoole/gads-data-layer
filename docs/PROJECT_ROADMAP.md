# PROJECT ROADMAP - Ads Control Tower (A.C.T.)

**Last Updated:** 2026-03-07
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

## 🔴 OUTREACH SYSTEM — FUNCTIONS NOT YET LIVE

The following are confirmed incomplete as of Chat 68. Master Chat 8.0 tackles these before moving on.

| # | Function | Location | Status |
|---|----------|----------|--------|
| 1 | Email signature | All outgoing emails | ❌ Not built |
| 2 | CV upload & file storage | Templates page | ❌ Placeholder UI only |
| 3 | CV attachment on send | Queue page | ❌ Toggle exists, never attaches |
| 4 | Open/click tracking pixel | Analytics | ❌ Integer columns seeded only |
| 5 | Reply inbox polling | Replies page | ❌ No Gmail polling |
| 6 | Send reply | Replies page | ❌ "Coming soon" toast |
| 7 | Edit this email | Queue page ✏ button | ❌ "Coming soon" toast |
| 8 | Regenerate with AI | Queue page 🔄 button | ❌ "Coming soon" toast |
| 9 | Switch template | Queue page 📋 button | ❌ "Coming soon" toast |
| 10 | Queue auto-scheduling | Queue page | ❌ All sends are manual |

---

## 🎯 NEXT PRIORITIES

### IMMEDIATE — Master Chat 8.0 (Outreach completion)

Complete the 10 outstanding outreach functions listed above. Suggested grouping for Claude Code briefs:

**Brief A — Email Signature** (1-2 hours)
- HTML signature block appended to every outgoing email
- Configurable in email_config.yaml

**Brief B — Queue Actions** (3-4 hours)
- ✏ Edit this email — inline edit modal
- 📋 Switch template — template picker modal
- 🔄 Regenerate with AI — Claude API call to rewrite body

**Brief C — CV Upload & Attach** (4-6 hours)
- File upload endpoint → `/static/uploads/cv/`
- Templates page: upload, preview, replace, remove
- Queue page: CV attachment on send (real file, not toast)

**Brief D — Reply Send** (2-3 hours)
- Replies page "Send Reply" button → live SMTP send
- Saves reply to `outreach_emails` table

**Brief E — Open/Click Tracking** (6-8 hours)
- Tracking pixel: `/outreach/track/open/<email_id>`
- Link redirect: `/outreach/track/click/<email_id>`
- CV open: `/outreach/track/cv/<email_id>`
- Auto-inject pixel + wrapped links on send
- Writes to `opened_at`, `clicked_at`, `cv_opened_at` timestamp columns

**Brief F — Reply Inbox Polling** (6-8 hours)
- Gmail API (or IMAP) polling for replies to `chris@christopherhoole.com`
- Match reply to `outreach_emails` record by thread/subject
- Write to `outreach_emails`: `reply_received=true`, `reply_text`, `replied_at`
- Replies page auto-updates

**Brief G — Queue Auto-Scheduling** (3-4 hours)
- Background scheduler (APScheduler or daemon thread)
- Check `scheduled_at` every 5 minutes
- Auto-send emails whose `scheduled_at` has passed
- Skip if daily limit reached

### NEXT — After Outreach Complete

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
- 10 functions still not live (see table above)

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

**Version:** 4.0 | **Last Updated:** 2026-03-07
