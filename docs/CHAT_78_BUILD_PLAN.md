# CHAT 78 — DETAILED BUILD PLAN
# Queue Auto-Scheduling

---

## FILES TO MODIFY

1. `act_dashboard/static/css/outreach.css` — append new CSS
2. `act_dashboard/templates/outreach/queue.html` — add Schedule button, scheduled banner, Cancel Schedule button
3. `act_dashboard/routes/outreach.py` — add schedule + cancel-schedule routes, update queue page data
4. `act_dashboard/app.py` — register new scheduler background thread

## FILES TO CREATE

5. `act_dashboard/queue_scheduler.py` — background thread that auto-sends elapsed scheduled emails

---

## STEP-BY-STEP BUILD ORDER

---

### STEP 1 — CSS
Append contents of CHAT_78_CSS_SPEC.css to bottom of outreach.css.
No other CSS changes.

---

### STEP 2 — Backend: schedule route

In `act_dashboard/routes/outreach.py`, add:

```
POST /outreach/queue/<email_id>/schedule
```

Logic:
1. Fetch the email record from `outreach_emails` — confirm status='queued' and scheduled_at IS NULL
2. Fetch the lead record to get `country`
3. Map country → timezone using this table:
   - United Kingdom → Europe/London
   - United States → America/New_York
   - Canada → America/Toronto
   - Australia → Australia/Sydney
   - New Zealand → Pacific/Auckland
   - Default/unknown → UTC (log warning)
4. From current UTC time, find the next valid send window:
   - Valid days: Tuesday (1), Wednesday (2), Thursday (3) only
   - Valid windows: 10:00am or 14:00 (2pm) in lead's local timezone
   - Algorithm:
     a. Convert now to lead's local timezone
     b. Check if today is Tue/Wed/Thu AND current local time < 10:00 → use today at 10:00
     c. Else if today is Tue/Wed/Thu AND current local time < 14:00 → use today at 14:00
     d. Else advance to next day and repeat until a valid Tue/Wed/Thu window is found
     e. Cap search at 7 days — if nothing found, default to next Tuesday 10:00
5. Convert chosen local datetime back to UTC
6. UPDATE outreach_emails SET scheduled_at = <utc_datetime> WHERE email_id = <id>
7. Return JSON: { success: true, scheduled_at_utc: "...", scheduled_display: "Tue 10 Mar · 10:00am EST" }

---

### STEP 3 — Backend: cancel-schedule route

In `act_dashboard/routes/outreach.py`, add:

```
POST /outreach/queue/<email_id>/cancel-schedule
```

Logic:
1. UPDATE outreach_emails SET scheduled_at = NULL WHERE email_id = <id>
2. Return JSON: { success: true }

---

### STEP 4 — Backend: update queue page route

In the existing queue page route in `outreach.py`:
- For each email in queued_emails, add these fields to the email dict:
  - `is_scheduled`: True if scheduled_at IS NOT NULL
  - `scheduled_display`: formatted string e.g. "Tue 10 Mar · 10:00am GMT" (if scheduled)
  - `scheduled_at_utc`: raw UTC datetime string (if scheduled)
- Stats dict: `stats.scheduled_this_week` — count of emails with scheduled_at between now and now+7 days

---

### STEP 5 — Frontend: queue.html changes

**5a — Card wrapper:** Add `is-scheduled` class conditionally:
```
class="queue-card collapsed {% if email.is_scheduled %}is-scheduled{% endif %}"
```

**5b — Queue number bubble:** Add `is-scheduled` class conditionally:
```
class="queue-number {% if email.is_scheduled %}is-scheduled{% endif %}"
```

**5c — Auto-send badge:** Add to card meta row when scheduled:
```
{% if email.is_scheduled %}
<span class="auto-send-badge">⚡ Auto-send</span>
{% endif %}
```

**5d — Scheduled banner:** Insert between card header div and subject bar div:
```
{% if email.is_scheduled %}
<div class="scheduled-banner">
  <span class="material-symbols-outlined">calendar_clock</span>
  <span class="sched-banner-label">Scheduled for</span>
  <span class="sched-banner-time">{{ email.scheduled_display }}</span>
  <span class="sched-banner-local">(recipient's local time)</span>
  <button class="sched-banner-cancel"
          onclick="cancelSchedule('{{ email.email_id }}')">Cancel</button>
</div>
{% endif %}
```

**5e — Action row:** Replace Send Now + add Schedule button conditionally:
```
{% if email.is_scheduled %}
  <button class="btn-cancel-schedule"
          onclick="cancelSchedule('{{ email.email_id }}')">
    ✕ Cancel Schedule
  </button>
  <div class="sched-auto-note">
    <span class="material-symbols-outlined">check_circle</span>
    Will auto-send {{ email.scheduled_display }} — no action needed
  </div>
{% else %}
  <button class="btn-send" onclick="sendCard('{{ email.email_id }}')">
    <span class="material-symbols-outlined">send</span>
    Send now
  </button>
  <button class="btn-schedule" onclick="scheduleCard('{{ email.email_id }}')">
    <span class="material-symbols-outlined">calendar_clock</span>
    Schedule
  </button>
  <div class="send-schedule-note">
    <span class="material-symbols-outlined">info</span>
    {{ email.schedule_note }}
  </div>
{% endif %}
<button class="btn-discard" onclick="discardCard('{{ email.email_id }}')">🗑 Discard</button>
```

**5f — JavaScript: scheduleCard():**
```javascript
function scheduleCard(emailId) {
  fetch('/outreach/queue/' + emailId + '/schedule', { method: 'POST' })
    .then(r => r.json())
    .then(data => {
      if (data.success) {
        showToast('Scheduled for ' + data.scheduled_display, 'success');
        setTimeout(() => location.reload(), 800);
      } else {
        showToast(data.message || 'Could not schedule', 'error');
      }
    })
    .catch(() => showToast('Network error', 'error'));
}
```

**5g — JavaScript: cancelSchedule():**
```javascript
function cancelSchedule(emailId) {
  fetch('/outreach/queue/' + emailId + '/cancel-schedule', { method: 'POST' })
    .then(r => r.json())
    .then(data => {
      if (data.success) {
        showToast('Schedule cancelled', 'success');
        setTimeout(() => location.reload(), 800);
      } else {
        showToast(data.message || 'Could not cancel', 'error');
      }
    })
    .catch(() => showToast('Network error', 'error'));
}
```

---

### STEP 6 — Background scheduler thread

Create `act_dashboard/queue_scheduler.py`:

```
Class: QueueScheduler
Method: run() — infinite loop, sleeps 300s (5 min) between cycles
Method: _run_cycle() — core logic per cycle:
  1. Connect to warehouse.duckdb
  2. SELECT email_id, lead_id, scheduled_at FROM outreach_emails
     WHERE status='queued' AND scheduled_at IS NOT NULL
     AND scheduled_at <= now() UTC
  3. Check daily_limit_remaining (count sent today vs limit in email_config.yaml)
  4. For each elapsed email (up to remaining daily limit):
     a. Fetch full email record (to, subject, body, cv_attached)
     b. Build body_html (same \n→<br> pattern as queue_send)
     c. Call send_email() from email_sender.py
     d. On success: UPDATE outreach_emails SET status='sent', sent_at=now(), scheduled_at=NULL
     e. Log: [SCHEDULER] Auto-sent email_id=<id> to <email>
     f. On failure: log error, leave record unchanged for retry next cycle
  5. Log: [SCHEDULER] Cycle complete — <n> auto-sent
```

---

### STEP 7 — Register scheduler in app.py

In `act_dashboard/app.py`, after the existing radar and poller thread starts:

```python
from act_dashboard.queue_scheduler import QueueScheduler
scheduler = QueueScheduler(app)
scheduler_thread = threading.Thread(target=scheduler.run, daemon=True)
scheduler_thread.start()
print("✅ [Chat 78] Queue scheduler thread started (300s cycle)")
```

Add CSRF exemptions for new routes:
```python
csrf.exempt(outreach.schedule_email)
csrf.exempt(outreach.cancel_schedule_email)
```

---

### STEP 8 — CSRF exemptions

In `app.py` CSRF section, add:
```
✅ [Chat 78] CSRF exempted: outreach.schedule_email
✅ [Chat 78] CSRF exempted: outreach.cancel_schedule_email
```

---

## DEPENDENCIES

- `pytz` — for timezone handling. Check if already installed. If not: `pip install pytz --break-system-packages`
- All other dependencies already present

---

## SUCCESS CRITERIA

- [ ] Flask starts clean, scheduler thread logged
- [ ] Schedule button appears on unscheduled cards
- [ ] Clicking Schedule → amber banner appears, yellow border, Auto-send badge, Cancel Schedule button
- [ ] Clicking Cancel Schedule → reverts card to unscheduled state
- [ ] Clicking Cancel on amber banner → same as Cancel Schedule
- [ ] Scheduled card shows correct day/time in lead's local timezone
- [ ] Background scheduler logs [SCHEDULER] Cycle complete every 5 min
- [ ] Auto-send fires when scheduled_at passes (test by setting scheduled_at to now() in DB)
- [ ] Daily limit respected — scheduler skips if limit reached
- [ ] No console errors
