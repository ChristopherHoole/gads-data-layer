"""
Email sender with SMTP integration.
Supports HTML emails with plain text fallback.
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from datetime import datetime, date
from typing import Dict, Any
from jinja2 import Environment, FileSystemLoader
import duckdb

logger = logging.getLogger(__name__)


class EmailSender:
    """
    SMTP email sender with template support.

    Supports:
    - HTML emails with Jinja2 templates
    - Plain text fallback
    - Gmail SMTP (smtp.gmail.com)
    - Error handling and logging
    """

    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        smtp_user: str,
        smtp_password: str,
        from_email: str = None,
    ):
        """
        Initialize email sender.

        Args:
            smtp_host: SMTP server hostname (e.g., smtp.gmail.com)
            smtp_port: SMTP port (587 for TLS, 465 for SSL)
            smtp_user: SMTP username/email
            smtp_password: SMTP password or app password
            from_email: From email address (defaults to smtp_user)
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.from_email = from_email or smtp_user

        template_dir = Path(__file__).parent / "templates"
        self.jinja_env = Environment(loader=FileSystemLoader(str(template_dir)))

        logger.info(f"EmailSender initialized: {smtp_host}:{smtp_port}")

    def send_email(
        self, to_email: str, subject: str, html_body: str, plain_body: str = None
    ) -> bool:
        """
        Send an email.

        Args:
            to_email: Recipient email address
            subject: Email subject line
            html_body: HTML email body
            plain_body: Plain text fallback (optional)

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.from_email
            msg["To"] = to_email
            msg["Date"] = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")

            # Add plain text part (if provided)
            if plain_body:
                msg.attach(MIMEText(plain_body, "plain"))

            # Add HTML part
            msg.attach(MIMEText(html_body, "html"))

            # Connect to SMTP server and send
            logger.info(f"Connecting to {self.smtp_host}:{self.smtp_port}")

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()  # Enable TLS
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Email sent successfully to {to_email}: {subject}")
            return True

        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failed: {e}")
            return False

        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {e}")
            return False

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Render Jinja2 template with context.

        Args:
            template_name: Template filename (e.g., 'daily_summary.html')
            context: Template variables

        Returns:
            Rendered HTML string
        """
        template = self.jinja_env.get_template(template_name)
        return template.render(**context)


def send_daily_summary(
    config: dict,
    customer_id: str,
    snapshot_date: date,
    db_path: str = "warehouse.duckdb",
    dashboard_url: str = "http://localhost:5000",
) -> bool:
    """
    Send daily summary email.

    Args:
        config: Client config dict with email_alerts section
        customer_id: Google Ads customer ID
        snapshot_date: Date for summary
        db_path: Path to DuckDB database
        dashboard_url: URL to dashboard

    Returns:
        True if sent successfully
    """
    email_config = config.get("email_alerts", {})

    if not email_config.get("enabled", False):
        logger.info("Email alerts disabled in config")
        return False

    # Get data from database
    conn = duckdb.connect(db_path, read_only=True)

    # Yesterday's performance
    yesterday_query = """
    SELECT
        SUM(cost_micros) / 1000000 as spend,
        SUM(conversions) as conversions,
        SUM(conversions_value) / NULLIF(SUM(cost_micros), 0) as roas
    FROM analytics.campaign_daily
    WHERE customer_id = ?
      AND snapshot_date = ?
    """
    yesterday_data = conn.execute(
        yesterday_query, [customer_id, snapshot_date]
    ).fetchone()

    # Pending recommendations
    client_name = config.get("client_name", "Unknown")
    suggestions_path = Path(f"reports/suggestions/{client_name}/{snapshot_date}.json")
    pending_count = 0
    if suggestions_path.exists():
        import json

        with open(suggestions_path, "r") as f:
            suggestions = json.load(f)
            pending_count = len(
                [
                    r
                    for r in suggestions["recommendations"]
                    if not r.get("blocked", False)
                ]
            )

    # Recent changes (last 7 days)
    changes_query = """
    SELECT
        change_date,
        campaign_id,
        lever,
        old_value / 1000000 as old_value,
        new_value / 1000000 as new_value,
        change_pct,
        rule_id
    FROM analytics.change_log
    WHERE customer_id = ?
      AND change_date >= ? - INTERVAL '7 days'
    ORDER BY change_date DESC, executed_at DESC
    LIMIT 10
    """
    recent_changes = conn.execute(
        changes_query, [customer_id, snapshot_date]
    ).fetchall()

    conn.close()

    context = {
        "client_name": client_name,
        "date": snapshot_date.strftime("%A, %B %d, %Y"),
        "spend": yesterday_data[0] or 0,
        "conversions": yesterday_data[1] or 0,
        "roas": yesterday_data[2] or 0,
        "pending_count": pending_count,
        "recent_changes": recent_changes,
        "dashboard_url": dashboard_url,
    }

    # Create email sender
    sender = EmailSender(
        smtp_host=email_config["smtp_host"],
        smtp_port=email_config["smtp_port"],
        smtp_user=email_config["smtp_user"],
        smtp_password=email_config["smtp_password"],
        from_email=email_config.get("from_email", email_config["smtp_user"]),
    )

    html_body = sender.render_template("daily_summary.html", context)

    # Plain text fallback
    plain_body = f"""
Ads Control Tower - Daily Summary
{client_name}
{snapshot_date.strftime('%A, %B %d, %Y')}

YESTERDAY'S PERFORMANCE:
- Spend: £{context['spend']:.2f}
- Conversions: {context['conversions']}
- ROAS: {context['roas']:.2f}

PENDING RECOMMENDATIONS: {pending_count}

RECENT CHANGES: {len(recent_changes)} in last 7 days

View dashboard: {dashboard_url}
    """.strip()

    # Send email
    subject = f"Daily Summary - {client_name} - {snapshot_date.strftime('%Y-%m-%d')}"
    return sender.send_email(
        to_email=email_config["recipient"],
        subject=subject,
        html_body=html_body,
        plain_body=plain_body,
    )


def send_rollback_alert(
    config: dict,
    campaign_id: str,
    campaign_name: str,
    change_details: dict,
    rollback_reason: str,
    performance_data: dict,
    dashboard_url: str = "http://localhost:5000",
) -> bool:
    """
    Send rollback alert email.

    Args:
        config: Client config dict
        campaign_id: Campaign ID
        campaign_name: Campaign name
        change_details: Original change (old_value, new_value, lever, etc)
        rollback_reason: Why rollback triggered
        performance_data: Before/after metrics
        dashboard_url: URL to dashboard

    Returns:
        True if sent successfully
    """
    email_config = config.get("email_alerts", {})

    if not email_config.get("enabled", False):
        return False

    client_name = config.get("client_name", "Unknown")

    context = {
        "client_name": client_name,
        "campaign_id": campaign_id,
        "campaign_name": campaign_name or "Unknown",
        "lever": change_details.get("lever", "unknown"),
        "old_value": change_details.get("old_value", 0),
        "new_value": change_details.get("new_value", 0),
        "change_date": change_details.get("change_date", "Unknown"),
        "rollback_reason": rollback_reason,
        "before_metrics": performance_data.get("before", {}),
        "after_metrics": performance_data.get("after", {}),
        "dashboard_url": dashboard_url,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    # Create email sender
    sender = EmailSender(
        smtp_host=email_config["smtp_host"],
        smtp_port=email_config["smtp_port"],
        smtp_user=email_config["smtp_user"],
        smtp_password=email_config["smtp_password"],
    )

    html_body = sender.render_template("rollback_alert.html", context)

    # Plain text fallback
    plain_body = f"""
⚠️ ROLLBACK ALERT - Ads Control Tower

Campaign: {campaign_name} ({campaign_id})
Change Rolled Back: {change_details.get('lever')} change from {change_details.get('old_value')} to {change_details.get('new_value')}

Reason: {rollback_reason}

Performance Impact:
Before: CPA ${performance_data.get('before', {}).get('cpa', 0):.2f}, ROAS {performance_data.get('before', {}).get('roas', 0):.2f}
After:  CPA ${performance_data.get('after', {}).get('cpa', 0):.2f}, ROAS {performance_data.get('after', {}).get('roas', 0):.2f}

View details: {dashboard_url}/changes

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """.strip()

    # Send email
    subject = f"⚠️ Rollback Alert - {campaign_name} - {client_name}"
    return sender.send_email(
        to_email=email_config["recipient"],
        subject=subject,
        html_body=html_body,
        plain_body=plain_body,
    )


def send_performance_alert(
    config: dict,
    metric_name: str,
    threshold: float,
    current_value: float,
    threshold_type: str,  # 'above' or 'below'
    recommended_action: str,
    dashboard_url: str = "http://localhost:5000",
) -> bool:
    """
    Send performance alert email.

    Args:
        config: Client config dict
        metric_name: Metric that breached (e.g., 'CPA', 'ROAS')
        threshold: Threshold value
        current_value: Current metric value
        threshold_type: 'above' or 'below'
        recommended_action: What to do about it
        dashboard_url: URL to dashboard

    Returns:
        True if sent successfully
    """
    email_config = config.get("email_alerts", {})

    if not email_config.get("enabled", False):
        return False

    client_name = config.get("client_name", "Unknown")

    context = {
        "client_name": client_name,
        "metric_name": metric_name,
        "threshold": threshold,
        "current_value": current_value,
        "threshold_type": threshold_type,
        "recommended_action": recommended_action,
        "dashboard_url": dashboard_url,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "severity": (
            "HIGH" if abs(current_value - threshold) / threshold > 0.2 else "MEDIUM"
        ),
    }

    # Create email sender
    sender = EmailSender(
        smtp_host=email_config["smtp_host"],
        smtp_port=email_config["smtp_port"],
        smtp_user=email_config["smtp_user"],
        smtp_password=email_config["smtp_password"],
    )

    html_body = sender.render_template("performance_alert.html", context)

    # Plain text fallback
    plain_body = f"""
⚠️ PERFORMANCE ALERT - Ads Control Tower

{client_name}

Metric: {metric_name}
Threshold: {threshold_type.title()} {threshold}
Current Value: {current_value}

Recommended Action:
{recommended_action}

View dashboard: {dashboard_url}

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """.strip()

    # Send email
    subject = f"⚠️ Performance Alert - {metric_name} - {client_name}"
    return sender.send_email(
        to_email=email_config["recipient"],
        subject=subject,
        html_body=html_body,
        plain_body=plain_body,
    )
