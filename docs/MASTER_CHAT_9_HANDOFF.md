# MASTER CHAT 9.0 HANDOFF

**From:** Master Chat 8.0 (Chats 69–83 + Google Ads setup)
**To:** Master Chat 9.0
**Date:** 2026-03-10
**Status:** Ready for handoff

---

## ⚠️ FIRST THING TO DO

Read ALL of the following project files before doing anything else. They contain the full project history, current state, next priorities, known pitfalls, and lessons learned:

- `MASTER_KNOWLEDGE_BASE.md`
- `PROJECT_ROADMAP.md`
- `LESSONS_LEARNED.md`
- `KNOWN_PITFALLS.md`
- `WORKER_BRIEF_STRUCTURE.md`

These are available in the Claude Project files panel. Read them all, then confirm you've read them before proceeding.

---

## WHAT MASTER CHAT 8.0 COMPLETED

### Chats 69–80 — All 10 Outreach Functions Now Live ✅
| Chat | Feature |
|------|---------|
| 69 | Email signature on all outgoing emails |
| 70 | CV upload & file storage (Templates page) |
| 71 | CV attachment on send (Queue page) |
| 72 | Open/click/CV tracking pixels + auto-inject on send |
| 73 | Reply inbox polling (Gmail IMAP, 120s daemon) |
| 74 | Send reply from Replies page |
| 75 | Edit this email (Queue ✏ button) |
| 76 | Universal slidein design across all outreach pages |
| 77 | Switch template (Queue 📋 button) |
| 78 | Queue auto-scheduling (daemon thread, 300s) |
| 79 | Google Ads-style date picker (replaces Flatpickr) |
| 80 | Remove rules slidein from entity pages |

### Chats 81–83 — UI Cleanup ✅
- Chat 81: Fixed white box layout gap on all 5 entity pages (table-styles.css)
- Chat 82: Removed duplicate client selector from all 6 outreach pages, fixed navbar text hidden, fixed client_name blank on Templates/Analytics
- Chat 83: Removed rules summary card from Campaigns and Shopping pages

### Docs Updated ✅
All 5 knowledge base docs updated (v17.0/5.0/4.0) — committed 1c585e1

### Google Ads Account — Live ✅
Account: **125-489-5944** (joicemoura1001@gmail.com / Joice de Moura)
- Campaign running, Manual CPC £3.00, targeting England
- Impressions now coming through after keyword and ad overhaul
- **Keywords paused:** wrong-intent terms (google ads tag, ai google ads, performance max optimization, etc.)
- **Keywords added:** hiring-intent terms (google ads consultant, ppc specialist, paid search consultant, etc.)
- **Ad copy improved:** removed weak headlines (Learn More, Custom AI Engine, Global Reach Local Results etc.), added hiring-intent headlines and 4 new descriptions

---

## IMMEDIATE PRIORITIES FOR MASTER CHAT 9.0

### 1. Verify Conversion Tracking ⚠️ CHECK FIRST
**Status:** Test submission made just before handoff — result unknown.

In Google Ads → Goals → Conversions, two actions exist:
- **"Enviar formulário de lead"** (Portuguese — set up via Joice account) — Website, 30-day click window
- **"Lead form - Submit"** — Google hosted lead form

Check if the test submission registered. If count > 0 → tracking working.
If still 0 after 30 min → need to debug the tag on christopherhoole.online.

**To debug if not working:**
- Install Chrome/Opera extension **Tag Assistant**
- Visit christopherhoole.online, submit form, check if Google Ads conversion tag fires
- If tag missing → need to add Google Ads conversion tag to the Next.js site

**Note:** "Enviar formulário de lead" was created by the Joice de Moura account — may need to recreate a clean conversion action under Christopher's name once advertiser verification is sorted.

### 2. Google Ads API Basic Access
**Status:** Still on Test Account Access. Application submitted via Case 24460840136.
- No visible progress tracker — Google emails when approved
- "Apply for Basic Access" in API Centre links to the same form (case already open)
- **Nothing to do except wait** — check email for approval notification
- Once approved → run `tools/run_ingestion.py` to pull live data into ACT

### 3. Google Ads Campaign Build (Claude Code brief needed)
Now that the account is live and getting impressions, build a proper campaign structure:

**Recommended structure:**
- **Ad Group 1:** Consultant/Expert (google ads consultant, google ads expert, ppc consultant, paid search consultant)
- **Ad Group 2:** Specialist/Freelancer (google ads specialist, google ads freelancer, ppc specialist, ppc freelancer)
- **Ad Group 3:** Agency/Management (google ads management agency, google ads campaign management, ppc management)

Each ad group needs:
- Tightly themed keywords (phrase + exact, drop most broad once data exists)
- 2 RSAs with keyword-matching headlines
- Relevant display path (/google-ads-consultant, /ppc-specialist etc.)

**Current ad issues to fix:**
- Advertiser name showing as "JOICE DE MOURA" — needs advertiser verification completed for Christopher Hoole / ChristopherHoole.online
- Single ad group with all keywords mixed — needs splitting into themed groups
- Ad strength currently "Average" — target "Excellent"

### 4. Rules & Recommendations Overhaul (after live data flows)
Once Basic Access approved and live data in ACT:
- Review all 41 rules — confirm logic matches how Christopher actually wants to optimise
- Review recommendation generation — thresholds, conditions, cooldowns
- Priority: Campaign budget and bid rules first, then keywords

---

## GOOGLE ADS ACCOUNT DETAILS

| Field | Value |
|-------|-------|
| Account ID | 125-489-5944 |
| MCC | 443-437-9827 |
| Account owner email | joicemoura1001@gmail.com |
| API contact email | chrishoole101@gmail.com |
| Developer token | qAJz1YTgID7c7Jd2PDA1QA |
| Access level | Test Account (Basic Access pending) |
| API Case ID | 24460840136 |
| Campaign | Campaign 1, Manual CPC £3, England, Search |
| Landing page | https://www.christopherhoole.online |

---

## ACT SYSTEM STATE

**What's working:** Full dashboard, all outreach functions, 41 rules, 1,492 recommendations (synthetic data)
**What's blocked:** Live data ingestion — waiting on API Basic Access approval
**Next data step:** Once Basic Access approved → `tools/run_ingestion.py` → `scripts/copy_all_to_readonly.py`

---

## CRITICAL TECHNICAL CONTEXT

### Claude Code
Access via the **Code tab in the Claude Desktop App** — not PowerShell.

### Fresh PowerShell Start
```powershell
taskkill /IM python.exe /F
cd C:\Users\User\Desktop\gads-data-layer
.\.venv\Scripts\Activate.ps1
python act_dashboard/app.py
```

### Git Commit
```powershell
taskkill /IM python.exe /F
cd C:\Users\User\Desktop\gads-data-layer
git add .
git commit -m "Chat XX: description"
git push origin main
```

### SMTP Credentials (email_config.yaml — gitignored)
```yaml
smtp_host: smtp.gmail.com
smtp_port: 587
smtp_username: chris@christopherhoole.com
smtp_password: iflslbdfppfoehqz
daily_limit: 100
```

---

## LATEST COMMITS
| Commit | Description |
|--------|-------------|
| 1c585e1 | Docs: Update all 5 knowledge base docs to reflect Chats 69-83 |
| f531bd8 | Chat 83: Remove Active Optimization Rules card from Campaigns and Shopping |
| 9ee01fb | Chat 82: Remove duplicate client selector from all 6 outreach pages |
| 8968d64 | Chat 81: Fix table-styles.css layout gap on all entity pages |

---

**Handoff complete. Master Chat 9.0 is ready to start.**
