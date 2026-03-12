"""
act_dashboard/queue_scheduler.py

Background thread — Chat 78.
Every 300 s (5 min): finds queued emails whose scheduled_at has passed,
respects the daily sending limit, and auto-sends each one via Gmail SMTP.
"""

import threading
import time
from datetime import datetime
from pathlib import Path

import duckdb

_WAREHOUSE_PATH = str(
    (Path(__file__).parent.parent / "warehouse.duckdb").resolve()
)

# CV upload directory (same path as used in queue_send route)
_CV_DIR = Path(__file__).parent / "static" / "uploads" / "cv"

CYCLE_SECONDS = 300  # 5 minutes


class QueueScheduler:
    def __init__(self, app):
        self.app = app

    def run(self):
        """Infinite daemon loop — sleeps CYCLE_SECONDS between cycles."""
        while True:
            try:
                with self.app.app_context():
                    self._run_cycle()
            except Exception as e:
                print(f"[SCHEDULER] Unhandled cycle error: {e}")
            time.sleep(CYCLE_SECONDS)

    def _run_cycle(self):
        """Core logic: find elapsed scheduled emails, send up to daily limit."""
        from act_dashboard.email_sender import (
            send_email,
            check_daily_limit,
            get_signature_html,
            load_email_config,
        )
        from act_dashboard.routes.outreach import inject_tracking

        conn = duckdb.connect(_WAREHOUSE_PATH)
        try:
            # Find queued emails whose scheduled_at has arrived
            rows = conn.execute("""
                SELECT e.email_id, e.lead_id, e.subject, e.body, e.cv_attached,
                       l.email, l.first_name, l.full_name, l.company
                FROM outreach_emails e
                JOIN outreach_leads l ON e.lead_id = l.lead_id
                WHERE e.status = 'queued'
                  AND e.scheduled_at IS NOT NULL
                  AND e.scheduled_at <= CURRENT_TIMESTAMP
                ORDER BY e.scheduled_at ASC
            """).fetchall()

            if not rows:
                print(f"[SCHEDULER] Cycle complete — 0 auto-sent")
                return

            # Check daily limit
            limit_info = check_daily_limit(conn)
            remaining = limit_info["remaining"]
            if remaining <= 0:
                print(
                    f"[SCHEDULER] Daily limit reached "
                    f"({limit_info['sent_today']}/{limit_info['limit']}) — skipping cycle"
                )
                return

            email_config = load_email_config()
            base_url = email_config.get("base_url", "http://localhost:5000")

            auto_sent = 0
            for row in rows:
                if auto_sent >= remaining:
                    print(f"[SCHEDULER] Daily limit hit mid-cycle — stopping at {auto_sent} sent")
                    break

                (email_id, lead_id, subject, body, cv_attached,
                 to_email, first_name, full_name, company) = row

                # Substitute template placeholders
                _vars = {
                    "first_name": first_name or (full_name.split()[0] if full_name else ""),
                    "full_name":  full_name or "",
                    "company":    company or "",
                }
                for key, val in _vars.items():
                    subject = subject.replace("{" + key + "}", val)
                    body    = body.replace("{" + key + "}", val)

                # Build HTML body
                body_html = (
                    "<div style='font-family:Arial,sans-serif;font-size:14px;"
                    "line-height:1.6;color:#333;'>"
                    + (body or "").replace("\n", "<br>")
                    + "</div>"
                    + get_signature_html()
                )

                # CV attachment
                attachment_path = None
                if cv_attached:
                    cv_files = [f for f in _CV_DIR.iterdir() if f.is_file()] if _CV_DIR.exists() else []
                    if cv_files:
                        attachment_path = str(cv_files[0])
                    else:
                        print(f"[SCHEDULER] WARNING: cv_attached=True for {email_id} but no CV file found")

                # Inject tracking
                has_cv = bool(cv_attached and attachment_path)
                body_html = inject_tracking(body_html, email_id, base_url, has_cv=has_cv)

                # Send
                result = send_email(
                    to_email=to_email,
                    subject=subject,
                    body_html=body_html,
                    attachment_path=attachment_path,
                )

                if result["success"]:
                    now = datetime.now()
                    conn.execute(
                        "UPDATE outreach_emails "
                        "SET status = 'sent', sent_at = ?, scheduled_at = NULL "
                        "WHERE email_id = ?",
                        [now, email_id],
                    )
                    conn.execute(
                        "UPDATE outreach_leads "
                        "SET status = 'contacted', progress_stage = 3, last_activity = ? "
                        "WHERE lead_id = ? AND status IN ('cold', 'queued')",
                        [now, lead_id],
                    )
                    print(f"[SCHEDULER] Auto-sent email_id={email_id} to {to_email}")
                    auto_sent += 1
                else:
                    print(
                        f"[SCHEDULER] FAIL email_id={email_id} to {to_email}: "
                        f"{result.get('error', 'unknown error')} — will retry next cycle"
                    )

            print(f"[SCHEDULER] Cycle complete — {auto_sent} auto-sent")
        finally:
            conn.close()


# ── Celery task (Chat 90) ─────────────────────────────────────────────────────

from act_dashboard.celery_app import celery_app  # noqa: E402


@celery_app.task(name="act_dashboard.queue_scheduler.run_queue_scheduler")
def run_queue_scheduler():
    """Celery periodic task — replaces QueueScheduler daemon thread. Every 300s."""
    from act_dashboard.app import create_app
    app = create_app()
    scheduler = QueueScheduler(app)
    with app.app_context():
        scheduler._run_cycle()
