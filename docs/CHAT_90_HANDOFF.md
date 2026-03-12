# Chat 90 Handoff

**Date:** 2026-03-12
**Status:** COMPLETE

---

## What was built

Three daemon threads have been replaced with Celery periodic tasks backed by Redis. The underlying polling/scheduling/radar logic is completely unchanged — only how the tasks are scheduled and started has changed.

---

## Manual prerequisite — Redis (MUST DO BEFORE USING CELERY)

`redis-cli ping` returned "command not found" — Redis is not installed on this machine.

**Christopher must install Memurai (Windows Redis port) before Celery can run.**

Download from: https://www.memurai.com/

After installing, start with `memurai` in a terminal. Verify with `redis-cli ping` → should return `PONG`.

Flask starts and serves the dashboard without Celery running. Background tasks simply won't fire until Redis + Celery are started.

---

## Files changed

| File | Change |
|------|--------|
| `act_dashboard/celery_app.py` | NEW — Celery instance, Redis broker, beat schedule for 3 tasks |
| `act_dashboard/outreach_poller.py` | Added `run_outreach_poller` Celery task at end of file |
| `act_dashboard/queue_scheduler.py` | Added `run_queue_scheduler` Celery task at end of file |
| `act_autopilot/radar.py` | Added `run_radar` Celery task at end of file |
| `act_dashboard/app.py` | Removed 3 daemon thread start blocks; added Chat 90 comment |
| `requirements.txt` | Added `celery==5.6.2` and `redis==7.3.0` |
| `docs/CELERY_STARTUP.md` | NEW — full startup instructions |

---

## Architecture

```
Before (Chat 74/78/29):
  Flask create_app()
    → threading.Thread(target=radar_loop)       # 60s
    → threading.Thread(target=_poll_loop)        # 120s
    → threading.Thread(target=scheduler.run)     # 300s

After (Chat 90):
  Flask create_app()
    → prints info message only (no threads)

  Celery worker (separate terminal):
    → run_radar              every 60s
    → run_outreach_poller    every 120s
    → run_queue_scheduler    every 300s
```

---

## How to start

See `docs/CELERY_STARTUP.md` for full instructions.

Short version:
1. Terminal 1: `memurai`
2. Terminal 2: `celery -A act_dashboard.celery_app worker --beat --loglevel=info`
3. Terminal 3: `python act_dashboard/app.py`

---

## Implementation notes

### outreach_poller task
Calls `_ensure_schema()` then `_run_poll_cycle()` directly — same logic as before, minus the `while True` + `time.sleep(120)` loop (Celery beat handles the interval).

### queue_scheduler task
`_run_cycle()` needs a Flask app context. The task calls `create_app()` and wraps `_run_cycle()` with `app.app_context()`, mirroring exactly what `QueueScheduler.run()` did before.

### radar task
Calls `_evaluate_all_monitoring_recs(_DB_PATH, _RO_DB_PATH)` directly — same single-cycle logic as before, minus the `while True` + `time.sleep(60)` loop.

---

## Testing done

- `redis-cli ping` → not available (Memurai not installed — documented above)
- `pip install celery redis` → SUCCESS: celery 5.6.2, redis 7.3.0 installed
- Flask startup → SUCCESS: `create_app()` completes with no daemon thread errors
  - Confirmed: `ℹ️  [Chat 90] Background tasks handled by Celery beat — start separately`
  - No threading imports in app.py
  - No daemon thread starts in app.py
- Celery worker startup not testable without Redis (Memurai prerequisite)

---

## Next chat

No blockers from Chat 90. Once Memurai is installed:
1. Run the 3-terminal startup from `docs/CELERY_STARTUP.md`
2. Verify Celery output shows all 3 tasks registered
3. Verify tasks fire on schedule in Celery logs
