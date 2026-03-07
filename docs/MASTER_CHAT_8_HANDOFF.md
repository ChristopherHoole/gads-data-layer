# MASTER CHAT 8.0 HANDOFF

**From:** Master Chat 7.0 (Chats 65–68)
**To:** Master Chat 8.0
**Date:** 2026-03-07
**Status:** Ready for handoff

---

## WHAT MASTER CHAT 7.0 COMPLETED

### Chat 65 — Google Sheets → A.C.T Sync ✅
Contact form leads from christopherhoole.online automatically sync to outreach_leads via `/outreach/sync-from-sheets`.

### Chat 66 — Add Client Modal + Config Validator ✅
- Christopher Hoole account added: customer_id 1254895944, MCC 4434379827
- Config YAML validator bug fixed

### Chat 67 — Real Data Ingestion Pipeline ✅ (blocked on API access)
- `src/gads_pipeline/v1_runner.py` — fixed DB write path
- `scripts/copy_all_to_readonly.py` — copies all 5 analytics tables
- `tools/run_ingestion.py` — orchestration script
- **Blocker:** Google Ads API Basic Access pending. Case ID 24460840136. Check ads.google.com → Tools → API Centre.

### Chat 68 — Live Email Sending ✅
- Domain: christopherhoole.com (Namecheap)
- Email: chris@christopherhoole.com (Google Workspace, DKIM/SPF ✅)
- Gmail App Password: `iflslbdfppfoehqz` (stored in `act_dashboard/secrets/email_config.yaml` — gitignored)
- `act_dashboard/email_sender.py` — SMTP module built
- `act_dashboard/routes/outreach.py` — `queue_send()` upgraded to live send
- Confirmed working: emails deliver with correct HTML formatting, UTF-8 characters render correctly, green toast on send

**3 bugs found and fixed post-initial commit:**
1. MIMEText missing `"utf-8"` third arg → garbled special chars
2. `\n → <br>` conversion missing from `queue_send()` → plain text emails
3. `showToast` missing from success branch of `sendCard()` → no toast

**Current git HEAD:** Commits include `fe4a0d7` + subsequent bug fixes. All on `main`. Need to confirm final commit hash after this session's fixes.

---

## IMMEDIATE PRIORITY FOR MASTER CHAT 8.0

### The 10 Outreach Functions Not Yet Live

Before moving to any other work, complete these 10 items. They are confirmed broken as of Chat 68.

| # | Function | Location | Notes |
|---|----------|----------|-------|
| 1 | Email signature | All outgoing emails | Append to body_html in queue_send() |
| 2 | CV upload & file storage | Templates page | No upload endpoint exists |
| 3 | CV attachment on send | Queue page | Toggle UI exists, never attaches |
| 4 | Open/click tracking pixel | Analytics | Integer columns seeded; no pixel endpoint |
| 5 | Reply inbox polling | Replies page | No Gmail inbox polling |
| 6 | Send reply | Replies page | "Coming soon" toast only |
| 7 | Edit this email | Queue page ✏ | "Coming soon" toast only |
| 8 | Regenerate with AI | Queue page 🔄 | "Coming soon" toast only |
| 9 | Switch template | Queue page 📋 | "Coming soon" toast only |
| 10 | Queue auto-scheduling | Queue page | All sends currently manual |

### Suggested Brief Groupings

**Brief A — Email Signature** (~1-2 hrs)
Append HTML signature block to every outgoing email. Configurable name/title/email/website.

**Brief B — Queue Actions** (~3-4 hrs)
Wire up ✏ Edit email (inline edit modal), 📋 Switch template (picker modal), 🔄 Regenerate with AI (Claude API call).

**Brief C — CV Upload & Attach** (~4-6 hrs)
File upload endpoint → `/static/uploads/cv/`. Templates page: upload/preview/replace/remove. Queue page: real CV attachment on send.

**Brief D — Send Reply** (~2-3 hrs)
Replies page "Send Reply" → live SMTP send via email_sender.py. Save to outreach_emails table.

**Brief E — Open/Click Tracking** (~6-8 hrs)
Tracking pixel `/outreach/track/open/<id>`, link redirect `/outreach/track/click/<id>`, CV open `/outreach/track/cv/<id>`. Auto-inject on send. Write timestamp columns.

**Brief F — Reply Inbox Polling** (~6-8 hrs)
Gmail API or IMAP polling for replies. Match to outreach_emails by thread. Write reply_received, reply_text, replied_at. Replies page auto-updates.

**Brief G — Queue Auto-Scheduling** (~3-4 hrs)
APScheduler or daemon thread. Check scheduled_at every 5 min. Auto-send. Skip if daily limit reached.

---

## AFTER OUTREACH COMPLETE

Once all 10 outreach functions are live and tested:

1. **Apollo.io Lead Import** — account needed first (not yet created)
2. **M9 Live Validation** — blocked on Google Ads API Basic Access (Case 24460840136)
3. **Website Design Upgrade** — scope TBD
4. **Testing & Polish** — comprehensive pass across dashboard + outreach
5. **Website Contact Form Backend** — Google Sheets integration

---

## CRITICAL TECHNICAL CONTEXT

### Email Architecture
```
email_sender.py         ← receives ready HTML, sends via SMTP
outreach.py queue_send() ← converts body, builds body_html, calls send_email()
secrets/email_config.yaml ← SMTP credentials, gitignored, local only
```

**SMTP credentials (for rebuilding email_config.yaml if needed):**
```yaml
smtp_host: smtp.gmail.com
smtp_port: 587
smtp_username: chris@christopherhoole.com
smtp_password: iflslbdfppfoehqz
from_name: Christopher Hoole
from_email: chris@christopherhoole.com
daily_limit: 100
```

### Key Patterns

**Body HTML conversion (queue_send, outreach.py ~line 671):**
```python
body_html = (
    "<div style='font-family:Arial,sans-serif;font-size:14px;line-height:1.6;color:#333;'>"
    + (body or "").replace("\n", "<br>")
    + "</div>"
)
```

**MIMEText — always all 3 args:**
```python
msg.attach(MIMEText(body_html, "html", "utf-8"))
```

**Toast — always add to success branch:**
```javascript
if (data.success) {
    showToast('Action successful!', 'success');
    // then other actions
}
```

### Database
- Outreach tables all in `warehouse.duckdb`
- Connection: `duckdb.connect(_WAREHOUSE_PATH)` — no ATTACH needed for outreach-only operations
- Table names: `outreach_leads`, `outreach_emails`, `email_templates`
- Integer tracking cols: `open_count`, `click_count`, `cv_open_count`
- Timestamp tracking cols (not yet populated): `opened_at`, `clicked_at`, `cv_opened_at`

### Reseed Tool
`tools/reseed_queue.py` — resets sent emails back to queued for testing. Use before every send test.

### Claude Code Start
```powershell
cd C:\Users\User\Desktop\gads-data-layer
npx @anthropic-ai/claude-code
```

### Flask Test
```powershell
taskkill /IM python.exe /F
cd C:\Users\User\Desktop\gads-data-layer
.\.venv\Scripts\Activate.ps1
python act_dashboard/app.py
```

### Git Commit (Master Chat only, after Christopher confirms in Opera)
```powershell
taskkill /IM python.exe /F
cd C:\Users\User\Desktop\gads-data-layer
git add .
git commit -m "Chat XX: [Description]"
git push origin main
```

---

## OUTSTANDING COMMITS NEEDED

The bug fixes from this session (MIMEText utf-8, body_html conversion, toast success branch) need to be committed. First confirm Flask works cleanly, then:

```powershell
taskkill /IM python.exe /F
cd C:\Users\User\Desktop\gads-data-layer
git add .
git commit -m "Chat 68: Fix email formatting, UTF-8 charset, send toast"
git push origin main
```

---

## DOCS UPDATED THIS SESSION

All saved to `C:\Users\User\Desktop\gads-data-layer\docs\`:

| File | Version | Key Changes |
|------|---------|-------------|
| MASTER_KNOWLEDGE_BASE.md | 16.0 | Chats 67-68, email infra, 10-item incomplete list |
| PROJECT_ROADMAP.md | 4.0 | Chat 67-68 complete, christopherhoole.com added, brief groupings |
| LESSONS_LEARNED.md | 3.0 | Lessons 45-55 (email sending, toast, debug method) |
| KNOWN_PITFALLS.md | 3.0 | New section: Email Sending Issues (pitfalls 44-47) |
| WORKER_BRIEF_STRUCTURE.md | 3.0 | Completely rewritten for 2-tier Claude Code workflow |

---

**Handoff complete. Master Chat 8.0 is ready to start.**
