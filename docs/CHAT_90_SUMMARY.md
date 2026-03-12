# Chat 90 Summary — Background Job Queue (Celery + Redis)

**Date:** 2026-03-12

---

## What changed

Replaced three fragile daemon threads with Celery periodic tasks backed by Redis. The underlying logic in each daemon file is untouched — only the scheduling mechanism changed.

| Old (daemon thread) | New (Celery task) | Schedule |
|---------------------|-------------------|----------|
| `radar_loop()` thread | `run_radar` task | 60s |
| `_poll_loop()` thread | `run_outreach_poller` task | 120s |
| `QueueScheduler.run()` thread | `run_queue_scheduler` task | 300s |

---

## Files created

- `act_dashboard/celery_app.py` — Celery instance, Redis broker config, beat schedule
- `docs/CELERY_STARTUP.md` — Full startup instructions for Redis + Celery + Flask
- `docs/CHAT_90_HANDOFF.md` — Detailed handoff with prerequisites and architecture notes

## Files modified

- `act_dashboard/outreach_poller.py` — Added `run_outreach_poller` Celery task
- `act_dashboard/queue_scheduler.py` — Added `run_queue_scheduler` Celery task
- `act_autopilot/radar.py` — Added `run_radar` Celery task
- `act_dashboard/app.py` — Removed daemon thread starts; added Chat 90 comment
- `requirements.txt` — Added `celery==5.6.2`, `redis==7.3.0`

---

## Manual prerequisite

**Memurai (Windows Redis) must be installed before Celery can run.**
Download: https://www.memurai.com/

Redis was not found on this machine during this chat. Flask starts without it — background tasks simply won't fire until Redis + Celery are running.

---

## Why Celery

Daemon threads die silently on crash with no way to monitor, alert, or restart them without restarting Flask. Celery provides:
- Restartable without restarting Flask
- Visible task history and failure logs via Celery logs
- Standard beat scheduler (no custom `time.sleep` loops)
- Required for production deployment
