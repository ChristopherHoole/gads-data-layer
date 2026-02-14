"""
Radar Module: Alert System
Notifications when rollbacks occur.

Constitution Reference: Section 8 (Monitoring, Rollback & Anti-Oscillation)
"""

from datetime import datetime
from typing import List, Dict
import json


def send_rollback_alert(
    change: Dict, decision: "RollbackDecision", result: "RollbackResult", config: Dict
) -> None:
    """
    Send rollback alert to console (MVP).

    Future: Email, Slack, etc.

    Args:
        change: Original change dict
        decision: RollbackDecision that triggered rollback
        result: RollbackResult from execution
        config: Client configuration
    """
    client_name = config.get("client_name", "Unknown")
    campaign_name = change.get("campaign_name", "Unknown")

    print("\n" + "=" * 80)
    print("🚨 ROLLBACK ALERT")
    print("=" * 80)

    print(f"\nClient: {client_name}")
    print(f"Campaign: {campaign_name} ({change['campaign_id']})")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    print(f"\n📊 CHANGE ROLLED BACK:")
    print(f"  Original Change ID: {change['change_id']}")
    print(f"  Date: {change['change_date']}")
    print(f"  Lever: {change['lever']}")
    print(
        f"  Original Action: {change['old_value']:.2f} → {change['new_value']:.2f} ({change['change_pct']:+.1%})"
    )
    print(f"  Rule: {change['rule_id']} ({change['risk_tier']} risk)")

    print(f"\n⚠️ ROLLBACK REASON:")
    print(f"  Trigger: {decision.trigger}")
    print(f"  Confidence: {decision.confidence:.0%}")
    print(f"  Reason: {decision.reason}")

    print(f"\n📈 PERFORMANCE EVIDENCE:")
    evidence = decision.evidence

    if "cpa_before" in evidence:
        print(
            f"  CPA: ${evidence['cpa_before']:.2f} → ${evidence['cpa_after']:.2f} ({evidence['cpa_change_pct']:+.1%})"
        )
        print(
            f"  Conversions: {evidence['conversions_before']:.1f} → {evidence['conversions_after']:.1f} ({evidence['conversions_change_pct']:+.1%})"
        )

    if "roas_before" in evidence:
        print(
            f"  ROAS: {evidence['roas_before']:.2f} → {evidence['roas_after']:.2f} ({evidence['roas_change_pct']:+.1%})"
        )
        print(
            f"  Conv Value: ${evidence['value_before']:.2f} → ${evidence['value_after']:.2f} ({evidence['value_change_pct']:+.1%})"
        )
        print(f"  Cost: ${evidence['cost_before']:.2f} → ${evidence['cost_after']:.2f}")

    print(f"\n✅ ROLLBACK EXECUTED:")
    if result.dry_run:
        print(f"  Mode: DRY-RUN (simulated only)")
        print(f"  Would revert: {result.old_value:.2f} → {result.new_value:.2f}")
    else:
        print(f"  Mode: LIVE")
        print(f"  Status: {'SUCCESS' if result.success else 'FAILED'}")
        print(f"  Reverted: {result.old_value:.2f} → {result.new_value:.2f}")
        if result.error_message:
            print(f"  Error: {result.error_message}")

    print("\n" + "=" * 80)


def send_monitoring_summary(
    monitored_changes: List["MonitoredChange"],
    rollback_decisions: List["RollbackDecision"],
    config: Dict,
) -> None:
    """
    Send summary of all monitored changes.

    Args:
        monitored_changes: List of all changes being monitored
        rollback_decisions: List of rollback decisions
        config: Client configuration
    """
    client_name = config.get("client_name", "Unknown")

    total = len(monitored_changes)
    needing_rollback = sum(1 for d in rollback_decisions if d.should_rollback)
    confirmed_good = sum(
        1 for d in rollback_decisions if not d.should_rollback and d.trigger == "NONE"
    )
    insufficient_data = sum(
        1 for d in rollback_decisions if d.trigger == "INSUFFICIENT_DATA"
    )

    print("\n" + "=" * 80)
    print("📊 RADAR MONITORING SUMMARY")
    print("=" * 80)

    print(f"\nClient: {client_name}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    print(f"\n📈 CHANGES MONITORED:")
    print(f"  Total: {total}")
    print(f"  🚨 Rollback needed: {needing_rollback}")
    print(f"  ✅ Confirmed good: {confirmed_good}")
    print(f"  ⏳ Insufficient data: {insufficient_data}")

    if needing_rollback > 0:
        print(f"\n⚠️ ACTION REQUIRED:")
        print(f"  {needing_rollback} change(s) need rollback")
        print(f"  Run: python -m act_radar.cli rollback <config> --live")
    else:
        print(f"\n✅ NO ACTION NEEDED")
        print(f"  All monitored changes performing within thresholds")

    print("\n" + "=" * 80)


def generate_rollback_report(
    rollbacks: List[Dict], config: Dict, output_path: str
) -> str:
    """
    Generate detailed rollback report (JSON).

    Args:
        rollbacks: List of rollback events
        config: Client configuration
        output_path: Path to save report

    Returns:
        Path to saved report
    """
    report = {
        "client_name": config.get("client_name", "Unknown"),
        "customer_id": config.get("customer_id", "Unknown"),
        "generated_at": datetime.now().isoformat(),
        "total_rollbacks": len(rollbacks),
        "rollbacks": rollbacks,
    }

    with open(output_path, "w") as f:
        json.dump(report, f, indent=2, default=str)

    return output_path


def log_alert(
    change_id: int, alert_type: str, reason: str, db_path: str = "warehouse.duckdb"
) -> None:
    """
    Log alert to database for audit trail.

    Future: Create alerts table for tracking.

    Args:
        change_id: Change ID that triggered alert
        alert_type: 'rollback', 'monitoring_summary', etc.
        reason: Alert reason
        db_path: Path to DuckDB
    """
    # Future implementation: Insert into alerts table
    # For now, just print to console
    print(f"  [AUDIT] Alert logged: change_id={change_id}, type={alert_type}")


def format_performance_summary(delta: Dict) -> str:
    """
    Format performance delta for readable output.

    Args:
        delta: Performance delta dict from ChangeMonitor

    Returns:
        Formatted string with key metrics
    """
    lines = []

    lines.append("Performance Change:")
    lines.append(
        f"  CPA: ${delta['baseline_cpa']:.2f} → ${delta['current_cpa']:.2f} ({delta['cpa_change_pct']:+.1%})"
    )
    lines.append(
        f"  ROAS: {delta['baseline_roas']:.2f} → {delta['current_roas']:.2f} ({delta['roas_change_pct']:+.1%})"
    )
    lines.append(
        f"  Conversions: {delta['baseline_conversions']:.1f} → {delta['current_conversions']:.1f} ({delta['conversions_change_pct']:+.1%})"
    )
    lines.append(
        f"  Conv Value: ${delta['baseline_conversion_value']:.2f} → ${delta['current_conversion_value']:.2f} ({delta['value_change_pct']:+.1%})"
    )
    lines.append(
        f"  Cost: ${delta['baseline_cost']:.2f} → ${delta['current_cost']:.2f} ({delta['cost_change_pct']:+.1%})"
    )

    return "\n".join(lines)


def send_email_alert(
    subject: str, body: str, recipients: List[str], config: Dict
) -> bool:
    """
    Send email alert (future implementation).

    Args:
        subject: Email subject
        body: Email body (plain text)
        recipients: List of email addresses
        config: Client configuration

    Returns:
        True if sent successfully
    """
    # Future implementation: SMTP or SendGrid
    print(f"  [EMAIL] Would send to: {', '.join(recipients)}")
    print(f"  [EMAIL] Subject: {subject}")
    return False  # Not implemented yet


def send_slack_alert(channel: str, message: str, config: Dict) -> bool:
    """
    Send Slack alert (future implementation).

    Args:
        channel: Slack channel (e.g., '#ads-alerts')
        message: Message text (markdown supported)
        config: Client configuration

    Returns:
        True if sent successfully
    """
    # Future implementation: Slack webhook
    print(f"  [SLACK] Would send to: {channel}")
    return False  # Not implemented yet


# Alert severity levels
ALERT_SEVERITY = {
    "critical": "🚨",  # Rollback executed
    "warning": "⚠️",  # Performance degrading
    "info": "ℹ️",  # Monitoring summary
    "success": "✅",  # Change confirmed good
}


def format_alert_header(severity: str, title: str) -> str:
    """
    Format alert header with severity emoji.

    Args:
        severity: 'critical', 'warning', 'info', or 'success'
        title: Alert title

    Returns:
        Formatted header string
    """
    emoji = ALERT_SEVERITY.get(severity, "📊")
    return f"{emoji} {title}"


def create_alert_payload(
    alert_type: str, severity: str, data: Dict, config: Dict
) -> Dict:
    """
    Create standardized alert payload for any channel.

    Args:
        alert_type: 'rollback', 'monitoring', 'warning', etc.
        severity: Alert severity level
        data: Alert data (change, decision, etc.)
        config: Client configuration

    Returns:
        Standardized alert payload dict
    """
    return {
        "alert_type": alert_type,
        "severity": severity,
        "client_name": config.get("client_name", "Unknown"),
        "customer_id": config.get("customer_id", "Unknown"),
        "timestamp": datetime.now().isoformat(),
        "data": data,
    }
