"""
CLI for sending email alerts.
"""

import argparse
import yaml
from datetime import date, timedelta

from .email_sender import (
    send_daily_summary,
    send_rollback_alert,
    send_performance_alert,
)


def load_config(config_path: str) -> dict:
    """Load client configuration from YAML."""
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def cmd_send_daily_summary(args):
    """Send daily summary email."""
    config = load_config(args.config)

    # Use specified date or yesterday
    if args.date:
        snapshot_date = date.fromisoformat(args.date)
    else:
        snapshot_date = date.today() - timedelta(days=1)

    print(f"Sending daily summary for {config.get('client_name')}...")
    print(f"Date: {snapshot_date}")

    success = send_daily_summary(
        config=config,
        customer_id=str(config["google_ads"]["customer_id"]),
        snapshot_date=snapshot_date,
        db_path=args.db_path,
        dashboard_url=args.dashboard_url,
    )

    if success:
        print("✅ Email sent successfully!")
        return 0
    else:
        print("❌ Failed to send email. Check logs for details.")
        return 1


def cmd_send_test_rollback(args):
    """Send test rollback alert."""
    config = load_config(args.config)

    change_details = {
        "lever": "budget",
        "old_value": 100.0,
        "new_value": 150.0,
        "change_date": "2026-02-14",
    }

    performance_data = {
        "before": {"cpa": 25.50, "roas": 4.2},
        "after": {"cpa": 45.80, "roas": 2.1},
    }

    success = send_rollback_alert(
        config=config,
        campaign_id="12345",
        campaign_name="Test Campaign",
        change_details=change_details,
        rollback_reason="CPA increased 20% AND conversions dropped 10%",
        performance_data=performance_data,
        dashboard_url=args.dashboard_url,
    )

    if success:
        print("✅ Email sent successfully!")
        return 0
    else:
        print("❌ Failed to send email. Check logs for details.")
        return 1


def cmd_send_test_performance(args):
    """Send test performance alert."""
    config = load_config(args.config)

    success = send_performance_alert(
        config=config,
        metric_name="CPA",
        threshold=30.0,
        current_value=42.5,
        threshold_type="above",
        recommended_action="Review budget allocation and consider pausing underperforming campaigns. Check for recent quality score drops.",
        dashboard_url=args.dashboard_url,
    )

    if success:
        print("✅ Email sent successfully!")
        return 0
    else:
        print("❌ Failed to send email. Check logs for details.")
        return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Email Alerts CLI")

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Send daily summary
    daily_parser = subparsers.add_parser(
        "send-daily-summary", help="Send daily summary email"
    )
    daily_parser.add_argument("config", help="Path to client config YAML")
    daily_parser.add_argument(
        "--date", help="Date for summary (YYYY-MM-DD, default: yesterday)"
    )
    daily_parser.add_argument(
        "--db-path", default="warehouse.duckdb", help="Database path"
    )
    daily_parser.add_argument(
        "--dashboard-url", default="http://localhost:5000", help="Dashboard URL"
    )
    daily_parser.set_defaults(func=cmd_send_daily_summary)

    rollback_parser = subparsers.add_parser(
        "send-test-rollback", help="Send test rollback alert"
    )
    rollback_parser.add_argument("config", help="Path to client config YAML")
    rollback_parser.add_argument(
        "--dashboard-url", default="http://localhost:5000", help="Dashboard URL"
    )
    rollback_parser.set_defaults(func=cmd_send_test_rollback)

    perf_parser = subparsers.add_parser(
        "send-test-performance", help="Send test performance alert"
    )
    perf_parser.add_argument("config", help="Path to client config YAML")
    perf_parser.add_argument(
        "--dashboard-url", default="http://localhost:5000", help="Dashboard URL"
    )
    perf_parser.set_defaults(func=cmd_send_test_performance)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
