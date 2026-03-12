# Celery + Redis Startup Guide

Chat 90 — Background Job Queue

---

## Prerequisites

**Memurai must be installed before starting Celery.**
Download from: https://www.memurai.com/
Memurai is the Windows-native Redis port. Install it once; it runs as a Windows service.

---

## Full Stack Startup (3 terminals)

### Terminal 1 — Redis (Memurai on Windows)

```
memurai
```

Confirm it's running — you should see the Memurai banner. If installed as a service, it may already be running automatically.

To verify: open a new terminal and run:
```
redis-cli ping
```
Expected response: `PONG`

---

### Terminal 2 — Celery worker + beat

```
cd C:\Users\User\Desktop\gads-data-layer
.\.venv\Scripts\Activate.ps1
celery -A act_dashboard.celery_app worker --beat --loglevel=info
```

The worker combines the worker and beat scheduler in one process (suitable for single-server deployments). You should see all 3 tasks registered in the startup output:

```
[tasks]
  . act_dashboard.outreach_poller.run_outreach_poller
  . act_dashboard.queue_scheduler.run_queue_scheduler
  . act_autopilot.radar.run_radar
```

And the beat schedule:
```
beat: Starting...
  . run-outreach-poller -> every 120.0 seconds
  . run-queue-scheduler -> every 300.0 seconds
  . run-radar           -> every 60.0 seconds
```

---

### Terminal 3 — Flask

```
cd C:\Users\User\Desktop\gads-data-layer
.\.venv\Scripts\Activate.ps1
python act_dashboard/app.py
```

Flask starts independently. It does NOT start or depend on Celery.

---

## Task Reference

| Task name | Module | Schedule | Replaces |
|-----------|--------|----------|---------|
| `run_outreach_poller` | `act_dashboard.outreach_poller` | 120s | Chat 74 OutreachPoller thread |
| `run_queue_scheduler` | `act_dashboard.queue_scheduler` | 300s | Chat 78 QueueScheduler thread |
| `run_radar` | `act_autopilot.radar` | 60s | Chat 29 M8 RadarThread |

---

## Shutdown

Stop Celery: `Ctrl+C` in Terminal 2
Stop Flask: `Ctrl+C` in Terminal 3
Stop Memurai: `Ctrl+C` in Terminal 1 (or stop the Windows service)

---

## Notes

- Flask can start and serve the dashboard without Celery running. Background tasks simply won't fire until Celery is started.
- The `--beat` flag embeds the scheduler in the worker. For multi-worker production deployments, run `celery beat` as a separate process.
- Beat schedule state is stored in `celerybeat-schedule` (created automatically at project root).
