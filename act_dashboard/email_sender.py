"""
act_dashboard/email_sender.py

Email sending module for live Gmail SMTP delivery.
Chat 68.
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path

import yaml


def load_email_config():
    """Load SMTP configuration from act_dashboard/secrets/email_config.yaml."""
    config_path = Path(__file__).parent / "secrets" / "email_config.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def send_email(to_email, subject, body_html, from_name=None, from_email=None, attachment_path=None):
    """
    Send an HTML email via Gmail SMTP (TLS port 587).

    Args:
        to_email:        Recipient email address.
        subject:         Email subject line.
        body_html:       HTML body string.
        from_name:       Sender display name (defaults to config value).
        from_email:      Sender address (defaults to config value).
        attachment_path: Optional path to a file to attach (e.g. CV PDF).

    Returns:
        {'success': True} or {'success': False, 'error': str}
    """
    try:
        config = load_email_config()

        # Test mode: redirect all sends to the safe test address (Chat 73)
        if config.get("test_mode", False):
            original_to = to_email
            to_email = config["test_redirect_email"]
            print(f"[EMAIL] ⚠️ TEST MODE — redirecting to {to_email} (original: {original_to})")

        _from_name  = from_name  or config.get("from_name",  "Christopher Hoole")
        _from_email = from_email or config.get("from_email", config["smtp_username"])

        msg = MIMEMultipart("mixed")
        msg["Subject"] = subject
        msg["From"]    = f"{_from_name} <{_from_email}>"
        msg["To"]      = to_email

        msg.attach(MIMEText(body_html, "html", "utf-8"))

        # Optional file attachment
        if attachment_path:
            attach = Path(attachment_path)
            if attach.exists():
                with open(attach, "rb") as f:
                    part = MIMEBase("application", "pdf")
                    part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f'attachment; filename="{attach.name}"',
                )
                msg.attach(part)
            else:
                print(f"[EMAIL] Attachment not found: {attach}")

        # Connect and send
        with smtplib.SMTP(config["smtp_host"], config["smtp_port"]) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(config["smtp_username"], config["smtp_password"])
            server.sendmail(_from_email, [to_email], msg.as_string())

        print(f"[EMAIL] OK Sent to {to_email}: {subject}")
        return {"success": True}

    except Exception as e:
        print(f"[EMAIL] FAIL Failed to send to {to_email}: {e}")
        return {"success": False, "error": str(e)}


def get_signature_html():
    """Return a formatted HTML email signature block for Christopher Hoole."""
    return (
        "<br><br>"
        "<hr style='border:none;border-top:1px solid #ddd;margin:20px 0;'>"
        "<div style='font-family:Arial,sans-serif;font-size:12px;color:#888;line-height:1.6;'>"
        "<strong style='color:#555;'>Christopher Hoole</strong><br>"
        "Google Ads Specialist | 16 Years Experience<br>"
        "<a href='tel:+447451252857' style='color:#888;text-decoration:none;'>"
        "+44 7451 252857</a><br>"
        "<a href='mailto:chris@christopherhoole.com' style='color:#1a73e8;text-decoration:none;'>"
        "chris@christopherhoole.com</a><br>"
        "<a href='https://christopherhoole.com' style='color:#1a73e8;text-decoration:none;'>"
        "christopherhoole.com</a>"
        "</div>"
    )


def substitute_variables(template_body, lead_dict):
    """
    Replace {contact_name}, {company_name}, {role_title}, {location} etc.
    with actual values from lead_dict. Single-brace format. Returns substituted string.
    """
    result = template_body or ""

    # Derive contact_name from first_name or full_name
    full = lead_dict.get("full_name") or ""
    first_name = lead_dict.get("first_name") or (full.split()[0] if full.strip() else "")

    # Build standard merge field map
    merge_map = {
        "contact_name": first_name,
        "company_name": lead_dict.get("company") or "",
        "role_title":   lead_dict.get("role") or "",
        "location":     lead_dict.get("city_state") or "",
        # Backward compatibility aliases
        "first_name":   first_name,
        "full_name":    full,
        "last_name":    lead_dict.get("last_name") or "",
        "company":      lead_dict.get("company") or "",
        "email":        lead_dict.get("email") or "",
        "role":         lead_dict.get("role") or "",
        "track":        lead_dict.get("track") or "",
    }

    for key, value in merge_map.items():
        if value:
            result = result.replace("{" + key + "}", str(value))

    return result


def check_daily_limit(conn):
    """
    Count emails sent today from outreach_emails table.
    Returns {'limit': N, 'sent_today': N, 'remaining': N}.
    """
    try:
        config = load_email_config()
        daily_limit = config.get("daily_limit", 100)
        sent_today = conn.execute(
            "SELECT COUNT(*) FROM outreach_emails "
            "WHERE status = 'sent' AND sent_at >= CURRENT_DATE"
        ).fetchone()[0]
        return {
            "limit":      daily_limit,
            "sent_today": sent_today,
            "remaining":  max(0, daily_limit - sent_today),
        }
    except Exception as e:
        return {"limit": 100, "sent_today": 0, "remaining": 100, "error": str(e)}
