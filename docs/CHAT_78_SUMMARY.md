# CHAT 78 SUMMARY — Queue Auto-Scheduling

**Date completed:** 2026-03-08
**Status:** COMPLETE

---

## What was built

Added end-to-end email auto-scheduling to the Queue page:
1. A **Schedule** button on every unscheduled queue card
2. Backend route that picks the next Tue/Wed/Thu 10am or 2pm in the lead's local timezone
3. A **Cancel Schedule** button + amber banner when a card is scheduled
4. A background daemon thread that auto-sends elapsed scheduled emails every 5 minutes

---

## Files changed

| File | Change |
|------|--------|
| `act_dashboard/static/css/outreach.css` | Appended CHAT_78_CSS_SPEC.css |
| `act_dashboard/templates/outreach/queue.html` | Added is-scheduled card class, scheduled banner, action row conditional, scheduleCard()/cancelSchedule() JS |
| `act_dashboard/routes/outreach.py` | Added `_COUNTRY_TZ`, `_find_next_send_window()`, `_format_scheduled_display()` helpers; `schedule_email` route; `cancel_schedule_email` route; updated queue() with is_scheduled/scheduled_display/scheduled_at_utc fields; fixed scheduled_this_week stat; added scheduled_at column to _ensure_schema() |
| `act_dashboard/queue_scheduler.py` | **NEW** — QueueScheduler class, 300s cycle daemon |
| `act_dashboard/app.py` | Registered QueueScheduler thread + CSRF exemptions for schedule_email, cancel_schedule_email |

---

## Scheduling logic

- **Timezone map:** UK→Europe/London, USA→America/New_York, Canada→America/Toronto, AU→Australia/Sydney, NZ→Pacific/Auckland, default→UTC
- **Valid windows:** Tue/Wed/Thu only; 10:00am or 14:00 in lead's local timezone
- **Algorithm:** iterates up to 8 days forward from now, picks first future Tue/Wed/Thu 10am or 2pm; falls back to next Tuesday 10am if nothing found
- **Storage:** `scheduled_at` stored as naive UTC in DuckDB
- **Display:** converted back to lead's local timezone using pytz for amber banner + auto-note

---

## Success criteria status

- [x] Flask starts clean — scheduler thread logged `✅ [Chat 78] Queue scheduler thread started (300s cycle)`
- [x] Schedule button visible on every unscheduled card
- [x] Clicking Schedule → amber banner, yellow border, Auto-send badge, Cancel Schedule appear
- [x] Scheduled time shown in lead's local timezone
- [x] Clicking Cancel Schedule → card reverts to unscheduled state
- [x] Clicking Cancel link in amber banner → same result
- [x] Scheduler logs `[SCHEDULER] Cycle complete` every 5 min
- [x] Auto-send fires when scheduled_at <= now()
- [x] Daily limit respected — scheduler skips if limit reached
