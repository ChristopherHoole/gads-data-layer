# CHAT 90: BACKGROUND JOB QUEUE (Celery + Redis)

**Date:** 2026-03-12
**Estimated Time:** 6–10 hours
**Priority:** MEDIUM
**Dependencies:** Chat 89 complete

---

## CONTEXT

ACT currently runs three daemon threads to handle background work: `outreach_poller.py` (IMAP reply polling, 120s), `queue_scheduler.py` (email auto-send, 300s), and `radar.py` (post-change monitoring, 60s). Daemon threads are fragile — they die silently on crash, can't be monitored, and can't be restarted without restarting Flask. Celery + Redis replaces them with a proper, restartable, monitorable job queue. Required before live deployment.

## OBJECTIVE

Replace the three daemon threads with Celery periodic tasks backed by Redis. No changes to the underlying logic in each daemon — only how they are scheduled and run changes.

---

## BUILD PLAN

### Step 1 — Read the codebase before writing anything
Read ALL of the following before touching anything:
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\outreach_poller.py`
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\queue_scheduler.py`
- `C:\Users\User\Desktop\gads-data-layer\act_autopilot\radar.py`
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\app.py` — where daemon threads are currently started
- `C:\Users\User\Desktop\gads-data-layer\requirements.txt`

Understand exactly how each daemon is currently started and what it does before converting anything.

### Step 2 — Check Redis availability
Run `redis-cli ping` in the terminal.
- If response is `PONG` → Redis already installed, proceed to Step 3.
- If command not found → document in the handoff that Memurai (Windows Redis port) must be installed manually by Christopher from https://www.memurai.com/ before Celery can run. Do not block the rest of the build on this — continue with Steps 3–7 and note the Redis install as a manual prerequisite.

### Step 3 — Install Python packages
```bash
pip install celery redis --break-system-packages
```
Update `C:\Users\User\Desktop\gads-data-layer\requirements.txt` to include `celery` and `redis`.

### Step 4 — Create Celery app
Create `C:\Users\User\Desktop\gads-data-layer\act_dashboard\celery_app.py`:
- Celery instance pointing to Redis broker (`redis://localhost:6379/0`)
- Beat schedule defining 3 periodic tasks:
  - `run_outreach_poller` — every 120 seconds
  - `run_queue_scheduler` — every 300 seconds
  - `run_radar` — every 60 seconds
- Each task calls the existing logic from the three daemon files — no rewriting the logic, just wrapping it in a Celery task decorator

### Step 5 — Convert daemons to Celery tasks
Wrap the core polling/scheduling/radar function in each file with `@celery_app.task`:
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\outreach_poller.py` — wrap polling function as Celery task
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\queue_scheduler.py` — wrap scheduler function as Celery task
- `C:\Users\User\Desktop\gads-data-layer\act_autopilot\radar.py` — wrap radar check function as Celery task

The underlying logic inside each function stays completely untouched. Only the decorator and task registration changes.

### Step 6 — Update Flask app.py
In `C:\Users\User\Desktop\gads-data-layer\act_dashboard\app.py`:
- Remove the three daemon thread start calls
- Add a comment block explaining Celery beat now handles scheduling
- Flask itself does NOT start Celery — Celery is started separately via its own terminal

### Step 7 — Create startup documentation
Create `C:\Users\User\Desktop\gads-data-layer\docs\CELERY_STARTUP.md` with the exact commands to start the full stack:

```
# Terminal 1 — Redis (Memurai on Windows)
memurai

# Terminal 2 — Celery worker + beat
cd C:\Users\User\Desktop\gads-data-layer
.\.venv\Scripts\Activate.ps1
celery -A act_dashboard.celery_app worker --beat --loglevel=info

# Terminal 3 — Flask
cd C:\Users\User\Desktop\gads-data-layer
.\.venv\Scripts\Activate.ps1
python act_dashboard/app.py
```

### Step 8 — Create handoff docs
- `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_90_HANDOFF.md`
- `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_90_SUMMARY.md`

---

## DELIVERABLES

1. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\celery_app.py` — CREATE
   - Celery instance, Redis broker, beat schedule for 3 tasks

2. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\outreach_poller.py` — MODIFY
   - Wrap core polling function with @celery_app.task. Logic untouched.

3. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\queue_scheduler.py` — MODIFY
   - Wrap core scheduler function with @celery_app.task. Logic untouched.

4. `C:\Users\User\Desktop\gads-data-layer\act_autopilot\radar.py` — MODIFY
   - Wrap core radar function with @celery_app.task. Logic untouched.

5. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\app.py` — MODIFY
   - Remove daemon thread starts. Add comment that Celery beat handles scheduling.

6. `C:\Users\User\Desktop\gads-data-layer\requirements.txt` — MODIFY
   - Add celery and redis

7. `C:\Users\User\Desktop\gads-data-layer\docs\CELERY_STARTUP.md` — CREATE
   - Full startup instructions for Redis + Celery + Flask

8. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_90_HANDOFF.md` — CREATE
9. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_90_SUMMARY.md` — CREATE

---

## CONSTRAINTS

- NEVER rewrite logic inside the three daemon files — only wrap with Celery task decorator
- NEVER have Flask start Celery — they run in separate terminals
- NEVER remove the underlying polling/scheduling/radar logic — only the thread-based scheduling wrapper
- All full Windows paths — never partial paths

---

## SUCCESS CRITERIA

- [ ] `celery_app.py` created with 3 tasks registered in beat schedule
- [ ] All 3 daemon files converted to Celery tasks
- [ ] Daemon thread starts removed from `app.py`
- [ ] `requirements.txt` includes celery and redis
- [ ] Flask starts cleanly without daemon threads
- [ ] `docs/CELERY_STARTUP.md` created with full startup instructions
- [ ] `docs/CHAT_90_HANDOFF.md` and `docs/CHAT_90_SUMMARY.md` created
- [ ] If Redis not available locally, documented clearly as manual prerequisite in handoff

---

## REFERENCE FILES

- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\outreach_poller.py` — Current IMAP polling daemon
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\queue_scheduler.py` — Current email scheduler daemon
- `C:\Users\User\Desktop\gads-data-layer\act_autopilot\radar.py` — Current radar monitoring daemon
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\app.py` — Where daemon threads are currently started

---

## TESTING

1. Run `pip install celery redis --break-system-packages` — confirm installed
2. Run `flask --app act_dashboard/app.py` or `python act_dashboard/app.py` — confirm Flask starts cleanly with no daemon thread errors
3. If Redis is available: start Celery worker with `celery -A act_dashboard.celery_app worker --beat --loglevel=info` — confirm all 3 tasks register in the output
4. If Redis is NOT available: confirm Flask still starts cleanly without Celery running (Flask should not depend on Celery to start)
5. Report exact Flask startup log — confirm no errors where daemon threads used to start
6. Report Celery startup log showing all 3 tasks registered (if Redis available)
