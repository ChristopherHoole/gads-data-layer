"""
act_dashboard/celery_app.py

Celery application — Chat 90.
Replaces three daemon threads with Celery periodic tasks backed by Redis.

Tasks:
  - run_outreach_poller  — every 120 seconds  (was outreach_poller._poll_loop)
  - run_queue_scheduler  — every 300 seconds  (was QueueScheduler.run)
  - run_radar            — every 60 seconds   (was radar_loop)

Start Celery (from project root, in .venv):
  celery -A act_dashboard.celery_app worker --beat --loglevel=info
"""

from celery import Celery

celery_app = Celery(
    "act_dashboard",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=[
        "act_dashboard.outreach_poller",
        "act_dashboard.queue_scheduler",
        "act_autopilot.radar",
    ],
)

celery_app.conf.beat_schedule = {
    "run-outreach-poller": {
        "task": "act_dashboard.outreach_poller.run_outreach_poller",
        "schedule": 120.0,
    },
    "run-queue-scheduler": {
        "task": "act_dashboard.queue_scheduler.run_queue_scheduler",
        "schedule": 300.0,
    },
    "run-radar": {
        "task": "act_autopilot.radar.run_radar",
        "schedule": 60.0,
    },
}

celery_app.conf.timezone = "UTC"
