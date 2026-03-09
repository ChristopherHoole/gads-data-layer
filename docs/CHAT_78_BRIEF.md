# CHAT 78: QUEUE AUTO-SCHEDULING

**Date:** 2026-03-08
**Estimated Time:** 4–6 hours
**Priority:** HIGH
**Dependencies:** Chat 77 complete

---

## CONTEXT

The queue page currently only supports manual sends (Send Now). This chat adds auto-scheduling — Christopher clicks Schedule, the system picks the next optimal send window (Tue/Wed/Thu 9–11am or 2–4pm in the lead's local timezone), and a background thread auto-sends when the time arrives. The wireframe, CSS spec, and build plan are in `docs/`.

## OBJECTIVE

Add a Schedule button to every queue card, implement the scheduling logic backend, and start a background thread that auto-sends elapsed scheduled emails every 5 minutes.

---

## DELIVERABLES

1. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\static\css\outreach.css` — MODIFY (append new CSS from docs/CHAT_78_CSS_SPEC.css)
2. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\outreach\queue.html` — MODIFY
3. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\outreach.py` — MODIFY
4. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\queue_scheduler.py` — CREATE
5. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\app.py` — MODIFY (register scheduler thread + CSRF exemptions)
6. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_78_HANDOFF.md` — CREATE
7. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_78_SUMMARY.md` — CREATE

---

## REQUIREMENTS

Read the full build plan before starting:
`C:\Users\User\Desktop\gads-data-layer\docs\CHAT_78_BUILD_PLAN.md`

Read the CSS spec before touching outreach.css:
`C:\Users\User\Desktop\gads-data-layer\docs\CHAT_78_CSS_SPEC.css`

Read the wireframe to understand the exact visual target:
`C:\Users\User\Desktop\gads-data-layer\docs\CHAT_78_QUEUE_WIREFRAME_v2.html`

### Key constraints
- Follow build plan steps 1–8 in order
- Country → timezone map: UK=Europe/London, US=America/New_York, CA=America/Toronto, AU=Australia/Sydney, NZ=Pacific/Auckland, default=UTC
- Valid send windows: Tue/Wed/Thu only · 10:00am or 14:00 lead local time
- Always wait for optimal window — never compromise to a suboptimal day
- Scheduler thread: 300s (5 min) cycle, daemon=True
- Scheduler must respect daily_limit from email_config.yaml
- Use pytz for timezone handling — check if installed, pip install if not
- Page reloads after Schedule/Cancel (location.reload() after toast)
- NEVER send a real email during testing — use DB manipulation to test scheduler timing

### Scheduled card visual changes (exact)
- Yellow left border: `border-left: 3px solid #FBBC05`
- Amber banner between card header and subject bar
- "⚡ Auto-send" badge in card meta row
- Send Now replaced by Cancel Schedule button
- Queue number bubble turns yellow

---

## SUCCESS CRITERIA

- [ ] Flask starts clean — scheduler thread logged `✅ [Chat 78] Queue scheduler thread started (300s cycle)`
- [ ] Schedule button visible on every unscheduled card
- [ ] Clicking Schedule → amber banner, yellow border, Auto-send badge, Cancel Schedule appear
- [ ] Scheduled time shown in lead's local timezone (e.g. "Tue 10 Mar · 10:00am GMT")
- [ ] Clicking Cancel Schedule → card reverts to unscheduled state
- [ ] Clicking Cancel link in amber banner → same result as Cancel Schedule button
- [ ] Scheduler logs `[SCHEDULER] Cycle complete` every 5 min in Flask terminal
- [ ] Auto-send fires when scheduled_at <= now() — verify by setting scheduled_at to past time in DB and waiting one cycle
- [ ] `[SCHEDULER] Auto-sent email_id=<id>` appears in Flask log
- [ ] Daily limit check works — scheduler skips if limit reached
- [ ] No console errors

---

## REFERENCE FILES

- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\outreach\queue.html` — current queue template
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\outreach.py` — existing queue route and send logic
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\email_sender.py` — send_email(), check_daily_limit()
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\outreach_poller.py` — pattern for background daemon thread
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\app.py` — where to register thread + CSRF exemptions

---

## TESTING

1. Start Flask — confirm `✅ [Chat 78] Queue scheduler thread started` in log
2. Open Queue page — confirm Schedule button visible on cards
3. Click Schedule on a card — confirm amber banner appears with correct day/time, yellow border, Auto-send badge
4. Click Cancel on banner — confirm card reverts
5. Click Cancel Schedule button — confirm card reverts
6. Test scheduler timing: in PowerShell run:
   `python -c "import duckdb; c=duckdb.connect('warehouse.duckdb'); c.execute(\"UPDATE outreach_emails SET scheduled_at=datetime('now','-1 minute') WHERE status='queued' LIMIT 1\"); c.close(); print('Done')"`
7. Wait one scheduler cycle (up to 5 min) — confirm `[SCHEDULER] Auto-sent` in Flask log
8. Confirm that email record status changed to 'sent' in DB
9. Report Flask log output for scheduler cycles
