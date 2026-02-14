"""
Email Alert System for Ads Control Tower

Sends automated email notifications:
- Daily summary emails
- Rollback alerts
- Performance alerts
"""

__version__ = "1.0.0"

from .email_sender import (
    EmailSender,
    send_daily_summary,
    send_rollback_alert,
    send_performance_alert,
)

__all__ = [
    "EmailSender",
    "send_daily_summary",
    "send_rollback_alert",
    "send_performance_alert",
]
