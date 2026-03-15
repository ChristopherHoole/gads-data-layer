# MASTER CHAT 11.0 HANDOFF

**From:** Master Chat 11.0
**To:** Master Chat 12.0
**Date:** 2026-03-15
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

## WHAT MASTER CHAT 11.0 COMPLETED

### Chat 91 — Rules & Flags UI Overhaul ✅
**Commits:** 86d0eb6, 4bae83d
- `rules_flow_builder.html` — complete 5-step modal with all 38 metrics, sidebar, condition/action dropdowns
- `rules_flags_tab.html` — Rules table, Flags table with direction labels (Positive/Negative), plain English, condition text, badge colours
- `rules.css` — complete styling
- Fixed: unescaped apostrophes in JS causing SyntaxError on page load
- Fixed: direction-aware FLAG_COND_LABELS (ROAS Spike now shows "ROAS increased" not "ROAS declined")

### Chat 92 — Impression Share Pipeline + CAMPAIGN_METRIC_MAP ✅
**Commit:** 060fe2a
- `act_lighthouse/features.py` — `impression_share_lost_rank` column added (7d rolling avg)
- `scripts/add_impression_share_col.py` — migration script
- `act_autopilot/recommendations_engine.py` — CAMPAIGN_METRIC_MAP expanded from 9 → 38 entries

### Chat 93 — Templates Tab ✅
**Commit:** 342c8d8
- `scripts/add_is_template_col.py` — adds `is_template BOOLEAN DEFAULT FALSE` to rules table
- `act_dashboard/routes/campaigns.py` — save-as-template route, duplicate detection (type + action_type + condition_1_metric)
- `rules_flags_tab.html` — Templates table (live data, grouped), bookmark button on every rule/flag row, Edit template button
- `rules_flow_builder.html` — Edit template mode, Use template footer button, Save template button text, template name label
- **DB cleaned:** 54 total rows (24 rules + 30 flags, test duplicates removed)

**Key bugs found and fixed in Chat 93:**
1. `JSON_EXTRACT` returns quoted values → switch to `json_extract_string`
2. `conn = _get_warehouse()` placed AFTER duplicate check → silent NameError → check never ran
3. State variables (`_rfbIsTemplate` etc.) set before `rfbResetForm()` → wiped on form reset → set them AFTER
4. `rfEditTemplate()` called in HTML but never defined in JS → button did nothing
5. Duplicate detection included `campaign_type_lock` in match → too restrictive, blocked differently-named variants

### Google Ads API Application ✅
- Replied to Google compliance team with detailed 3-question response + ACT Design Document PDF
- API centre Company URL updated from .online to .com
- Access upgraded: Test Account → **Explorer Access** (read production accounts, no writes)
- Basic Access Case 21767540705 — reply sent, awaiting decision

### Google Ads Account Suspension (monitor only)
- Appeal ID 6448619522 — "Your appeal is in review"
- Do NOT submit another appeal. Monitor chris@christopherhoole.com.

### Documentation ✅
- MASTER_KNOWLEDGE_BASE.md → v19.0
- PROJECT_ROADMAP.md → v7.0
- LESSONS_LEARNED.md → v5.0 (76 lessons, 11 new)
- KNOWN_PITFALLS.md → v5.0 (59 pitfalls, 8 new)
- WORKER_BRIEF_STRUCTURE.md → v5.0 (added roadmap format template)
- MASTER_CHAT_11_HANDOFF.md → this file

---

## IMMEDIATE PRIORITIES FOR MASTER CHAT 12

### 1. Rules Strategic Review ← PRIMARY TASK
Go through all 24 rules and review:
- Thresholds — are the values correct for real accounts?
- Cooldown periods — 7d/14d/30d appropriate per rule type?
- Conditions — are condition 1 + condition 2 combinations correct?
- Logic — does the plain English description match the actual condition?
- Missing rules — anything important not covered?

**How it will run:** Design discussion in Master Chat 12 → review rule by rule → agree changes → Claude Code brief to implement updates

### 2. Google Ads API Basic Access (monitor only)
- Case 21767540705 — no action needed, waiting on Google
- When approved → run `tools/run_ingestion.py` then `scripts/copy_all_to_readonly.py`

### 3. Google Ads Account Suspension (monitor only)
- Appeal ID 6448619522 — no action needed
- When Google replies to chris@christopherhoole.com, bring the email to Master Chat 12

---

## CURRENT DB STATE

```
Rules:     24 (18 Budget, 6 Bid) — all enabled
Flags:     30 (16 Performance, 8 Anomaly, 6 Technical) — all enabled
Templates: 0 (clean slate)
Total:     54 rows
```

**Note:** Status rules (Pause rules) are IDs 22-24. They exist in the rules table but aren't showing in the count because the status type only has 3 rows. This is correct.

---

## DIAGNOSTIC SCRIPTS (project root)

Run these to verify DB state before any test session:
```powershell
python C:\Users\User\Desktop\gads-data-layer\full_audit.py
python C:\Users\User\Desktop\gads-data-layer\check_state.py
```

Cleanup scripts (use if junk rows exist):
```powershell
python C:\Users\User\Desktop\gads-data-layer\cleanup_all_templates.py
python C:\Users\User\Desktop\gads-data-layer\cleanup_junk.py
```

---

## GOOGLE ADS ACCOUNT DETAILS

| Field | Value |
|-------|-------|
| Primary account | 487-268-1731 (chris@christopherhoole.com) — active |
| Test account | 125-489-5944 (joicemoura1001@gmail.com) — active |
| MCC | 152-796-4125 |
| Developer token | oDANZ-BXQprTm7_Sg4rjDg |
| API Case ID | 21767540705 |
| Appeal ID | 6448619522 |
| API Access Level | Explorer (upgraded from Test, March 2026) |

---

## CRITICAL TECHNICAL CONTEXT

### Claude Code
Accessed via the **Code tab in the Claude Desktop App** — NOT PowerShell.

### Brief Delivery Rule
Always save Claude Code briefs as downloadable files to `/docs/` — never inline in chat.

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

### Roadmap Format
When asked for the full roadmap, ALWAYS use the format defined in WORKER_BRIEF_STRUCTURE.md:
- Sections: DASHBOARD, OUTREACH, WEBSITE, GOOGLE ADS EXTERNAL, ADMIN
- Each section has its own numbered list starting from 1
- One item per line, no paragraphs

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
| 342c8d8 | Chat 93: Templates tab — table view, save/edit/use template, duplicate detection |
| 4bae83d | Chat 91: Flags sub-tab UI overhaul — direction labels, plain English, condition text |
| 060fe2a | Chat 92: impression_share_lost_rank pipeline + CAMPAIGN_METRIC_MAP 38 entries |
| a932ee7 | Chat 90: Replace daemon threads with Celery + Redis job queue |
| 51e79c6 | Chat 89: Add pytest test suite — 620 tests, 80% coverage |
| 088317d | Chat 88: Add ad_daily table + seed data + database indexes |

---

**Handoff complete. Master Chat 12.0 is ready to start.**
**Primary task: Rules strategic review — start with design discussion, rule by rule.**
