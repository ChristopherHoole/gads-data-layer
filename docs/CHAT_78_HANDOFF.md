# CHAT 78 HANDOFF — Queue Auto-Scheduling

**Date:** 2026-03-08

---

## How to test

### 1. Start Flask
```
python run.py
```
Confirm in terminal:
```
✅ [Chat 78] Queue scheduler thread started (300s cycle)
✅ [Chat 78] CSRF exempted: outreach.schedule_email
✅ [Chat 78] CSRF exempted: outreach.cancel_schedule_email
```

### 2. Queue page
- Open http://localhost:5000/outreach/queue
- Confirm **Schedule** button visible next to Send Now on each card
- Hint text: "Best time: Tue–Thu, 10am or 2pm (recipient local time)"

### 3. Click Schedule
- Amber banner appears between card header and subject bar
- Yellow left border on card
- "⚡ Auto-send" badge in card meta row
- Action row shows "Cancel Schedule" + green "Will auto-send …" note

### 4. Click Cancel (banner or button)
- Card reverts to unscheduled state (Send Now + Schedule buttons restored)

### 5. Test auto-send timing
In PowerShell (from project root):
```powershell
python -c "import duckdb; c=duckdb.connect('warehouse.duckdb'); c.execute(\"UPDATE outreach_emails SET scheduled_at=datetime('now','-1 minute') WHERE status='queued' LIMIT 1\"); c.close(); print('Done')"
```
Wait up to 5 minutes — check Flask terminal for:
```
[SCHEDULER] Auto-sent email_id=<id> to <email>
[SCHEDULER] Cycle complete — 1 auto-sent
```
Verify DB: `status` changed to `'sent'`, `sent_at` populated, `scheduled_at` cleared.

---

## Key architecture notes

- `scheduled_at` in DB is **UTC naive datetime**
- Display conversion (local timezone) done in `_format_scheduled_display()` using pytz
- Scheduler thread uses its own DuckDB connection per cycle (not Flask's connection pool)
- Daily limit is read from `email_config.yaml` → `daily_limit` key
- Scheduler thread is `daemon=True` — dies automatically when Flask exits
- test_mode in email_config.yaml still applies — scheduler sends redirect to test address

---

## Next chat suggestions

- Snooze / reschedule: allow moving a scheduled card to a different time slot
- Bulk scheduling: "Schedule all" button for the entire queue
- Schedule time display on collapsed cards (currently only shown when expanded)
