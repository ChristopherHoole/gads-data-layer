# MASTER CHAT 10.0 HANDOFF

**From:** Master Chat 10.0
**To:** Master Chat 11.0
**Date:** 2026-03-12
**Status:** Ready for handoff

---

## ⚠️ FIRST THING TO DO

Read ALL of the following project files before doing anything else:

- `MASTER_KNOWLEDGE_BASE.md`
- `PROJECT_ROADMAP.md`
- `LESSONS_LEARNED.md`
- `KNOWN_PITFALLS.md`
- `WORKER_BRIEF_STRUCTURE.md`

These are in the Claude Project files panel. Read them all, confirm you've read them before proceeding.

---

## WHAT MASTER CHAT 10.0 COMPLETED

### Chat 88 — ad_daily Table + Database Indexes ✅
**Commit:** 088317d
- Created `analytics.ad_daily` table in both databases
- Seeded with 90 days synthetic data (983 ads)
- Added database indexes across all 6 analytics tables
- **Result:** 23 Ad recommendations now generating (was 0)

### Chat 89 — Unit Tests (pytest 80%+) ✅
**Commit:** 51e79c6
- 19 test files in `tests/` folder
- 620 tests, 0 failures, 80% coverage
- Key coverage: campaigns 85%, ads 85%, changes 94%, rule_helpers 94%
- **Important:** ~30-40% of rule-specific tests will need updating after Rules & Recommendations overhaul

### Chat 90 — Celery + Redis Background Job Queue ✅
**Commit:** a932ee7
- `act_dashboard/celery_app.py` created — 3 periodic Celery tasks
- Daemon threads replaced: outreach_poller (120s), queue_scheduler (300s), radar (60s)
- Flask runs cleanly without Celery — tasks just don't fire until worker started
- **Manual prerequisite:** Install Memurai from https://www.memurai.com/
- Startup instructions in `docs/CELERY_STARTUP.md`

### Google Ads Account Suspension ✅ (appeal submitted)
- Account 487-268-1731 (chris@christopherhoole.com) suspended
- Root cause: UK passport submitted but payments profile registered in Brazil
- RNM document (V770566I) submitted as correct Brazilian ID
- **Appeal ID: 6448619522** — status "Your appeal is in review"
- Do NOT submit another appeal. Check chris@christopherhoole.com for response.

### Changes Tab ✅
- Confirmed already implemented as card grid — no work needed

### Docs Updated ✅
- MASTER_KNOWLEDGE_BASE.md → v18.0
- PROJECT_ROADMAP.md → v6.0
- MASTER_CHAT_10_HANDOFF.md → this file

---

## IMMEDIATE PRIORITIES FOR MASTER CHAT 11.0

### 1. Rules & Recommendations Overhaul ← PRIMARY TASK
This is the main focus of Master Chat 11. Christopher has confirmed this is the next major piece of work.

**How it will run:**
- Deep design discussion between Christopher and Master Chat 11
- Wireframes required before any build begins
- One step at a time — nothing rushed
- Claude Code builds once design is fully agreed

**What's in scope:**
- Review all 41 rules — thresholds, conditions, cooldowns, logic
- Review recommendation generation — entity-specific scoring, prioritisation
- Potentially redesign how rules and recommendations are structured entirely
- UI changes to how recommendations are presented and acted on

**Key constraint:** ~30-40% of the Chat 89 unit tests cover current rule logic. These will need updating after the overhaul — expected and accepted.

### 2. Google Ads Account Suspension (monitor only)
- Check chris@christopherhoole.com for Google's response to appeal ID 6448619522
- Do NOT submit another appeal or contact support again
- When Google replies, bring the email here for next steps

### 3. Google Ads API Basic Access (monitor only)
- Case 24460840136 — no action needed, waiting on Google approval
- Once approved → run `tools/run_ingestion.py` then `scripts/copy_all_to_readonly.py`

---

## GOOGLE ADS ACCOUNT DETAILS

| Field | Value |
|-------|-------|
| Primary account | 487-268-1731 (chris@christopherhoole.com) — SUSPENDED |
| Test account | 125-489-5944 (joicemoura1001@gmail.com) — active |
| MCC | 443-437-9827 |
| Developer token | qAJz1YTgID7c7Jd2PDA1QA |
| API Case ID | 24460840136 |
| Appeal ID | 6448619522 |
| Campaign | Campaign 1, Manual CPC £3, England, Search |
| Landing page | https://www.christopherhoole.com |

---

## ACT SYSTEM STATE

**Recommendations:** 1,515 active (1,256 keywords + 126 shopping + 110 campaigns + 23 ads)
**Rules:** 41 active across 5 entity types
**Tests:** 620 tests, 80% coverage
**Background jobs:** Celery (requires Memurai install to run)
**API:** Test Access only — Basic Access pending

---

## CRITICAL TECHNICAL CONTEXT

### Claude Code
Accessed via the **Code tab in the Claude Desktop App** — NOT PowerShell.

### Brief Delivery Rule
Always save Claude Code briefs as downloadable files to `/docs/` — never inline in chat.

### Fresh PowerShell Start (ACT)
```powershell
taskkill /IM python.exe /F
cd C:\Users\User\Desktop\gads-data-layer
.\.venv\Scripts\Activate.ps1
python act_dashboard/app.py
```

### Git Commit (ACT)
```powershell
taskkill /IM python.exe /F
cd C:\Users\User\Desktop\gads-data-layer
git add .
git commit -m "Chat XX: description"
git push origin main
```

### Website (Next.js)
```powershell
cd C:\Users\User\Desktop\act-website
npm run dev
git push origin master
```

### SMTP Credentials (email_config.yaml — gitignored)
```yaml
smtp_host: smtp.gmail.com
smtp_port: 587
smtp_username: chris@christopherhoole.com
smtp_password: iflslbdfppfoehqz
daily_limit: 100
```

### Primary Website
Always use **christopherhoole.com** — never christopherhoole.online as the primary URL.

---

## LATEST COMMITS

| Commit | Description |
|--------|-------------|
| a932ee7 | Chat 90: Replace daemon threads with Celery + Redis job queue |
| 51e79c6 | Chat 89: Add pytest test suite - 620 tests, 80% coverage |
| 088317d | Chat 88: Add ad_daily table + seed data + database indexes |
| 1c585e1 | Docs: Update all 5 knowledge base docs to reflect Chats 69-83 |

---

**Handoff complete. Master Chat 11.0 is ready to start.**
**Primary task: Rules & Recommendations overhaul — start with design discussion, wireframes first.**
