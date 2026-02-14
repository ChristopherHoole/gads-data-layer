"""
Radar Module: Rollback Triggers
Decision logic for when to rollback changes based on performance regression.

Constitution Reference: Section 8 (Monitoring, Rollback & Anti-Oscillation)
- CPA clients: Rollback if CPA worsens >20% AND conversions fall >10%
- ROAS clients: Rollback if ROAS worsens >15% OR value falls >15%
- Minimum wait: max(72 hours, median lag)
- Anti-oscillation: No lever reversal within 14 days
"""

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Dict, Optional
import duckdb


@dataclass
class RollbackDecision:
    """Decision on whether to rollback a change."""

    should_rollback: bool
    reason: str
    trigger: str  # 'CPA_REGRESSION', 'ROAS_REGRESSION', 'VALUE_REGRESSION', 'NONE'
    confidence: float  # 0.0 to 1.0
    evidence: Dict


def check_cpa_regression(
    delta: Dict,
    cpa_threshold: float = 0.20,  # 20% worsening
    conv_threshold: float = 0.10,  # 10% drop
) -> Optional[RollbackDecision]:
    """
    Check for CPA regression.

    Constitution Rule: Rollback if CPA worsens >20% AND conversions fall >10%

    Args:
        delta: Performance delta dict from ChangeMonitor
        cpa_threshold: CPA increase threshold (default 20%)
        conv_threshold: Conversion drop threshold (default 10%)

    Returns:
        RollbackDecision if regression detected, None otherwise
    """
    cpa_change_pct = delta.get("cpa_change_pct", 0.0)
    conv_change_pct = delta.get("conversions_change_pct", 0.0)

    # Check both conditions (AND)
    cpa_worsened = cpa_change_pct > cpa_threshold
    conv_dropped = conv_change_pct < -conv_threshold

    if cpa_worsened and conv_dropped:
        # Calculate confidence based on magnitude
        cpa_severity = min(cpa_change_pct / cpa_threshold, 2.0)  # Cap at 2x
        conv_severity = min(abs(conv_change_pct) / conv_threshold, 2.0)
        confidence = min(
            (cpa_severity + conv_severity) / 4, 0.95
        )  # Average, cap at 0.95

        reason = (
            f"CPA increased {cpa_change_pct:.1%} (>{cpa_threshold:.0%} threshold) "
            f"AND conversions dropped {conv_change_pct:.1%} (>{conv_threshold:.0%} threshold)"
        )

        evidence = {
            "cpa_before": delta.get("baseline_cpa", 0),
            "cpa_after": delta.get("current_cpa", 0),
            "cpa_change_pct": cpa_change_pct,
            "cpa_threshold": cpa_threshold,
            "conversions_before": delta.get("baseline_conversions", 0),
            "conversions_after": delta.get("current_conversions", 0),
            "conversions_change_pct": conv_change_pct,
            "conv_threshold": conv_threshold,
        }

        return RollbackDecision(
            should_rollback=True,
            reason=reason,
            trigger="CPA_REGRESSION",
            confidence=confidence,
            evidence=evidence,
        )

    return None


def check_roas_regression(
    delta: Dict,
    roas_threshold: float = 0.15,  # 15% worsening
    value_threshold: float = 0.15,  # 15% drop
) -> Optional[RollbackDecision]:
    """
    Check for ROAS regression.

    Constitution Rule: Rollback if ROAS worsens >15% OR value falls >15%

    Args:
        delta: Performance delta dict from ChangeMonitor
        roas_threshold: ROAS decrease threshold (default 15%)
        value_threshold: Value drop threshold (default 15%)

    Returns:
        RollbackDecision if regression detected, None otherwise
    """
    roas_change_pct = delta.get("roas_change_pct", 0.0)
    value_change_pct = delta.get("value_change_pct", 0.0)

    # Check either condition (OR)
    roas_worsened = roas_change_pct < -roas_threshold
    value_dropped = value_change_pct < -value_threshold

    if roas_worsened or value_dropped:
        # Determine primary trigger
        if roas_worsened and value_dropped:
            trigger = "ROAS_AND_VALUE_REGRESSION"
            reason = (
                f"ROAS decreased {roas_change_pct:.1%} (>{roas_threshold:.0%} threshold) "
                f"AND conversion value dropped {value_change_pct:.1%} (>{value_threshold:.0%} threshold)"
            )
            # Higher confidence when both conditions met
            confidence = 0.90
        elif roas_worsened:
            trigger = "ROAS_REGRESSION"
            reason = f"ROAS decreased {roas_change_pct:.1%} (>{roas_threshold:.0%} threshold)"
            confidence = min(abs(roas_change_pct) / roas_threshold * 0.8, 0.85)
        else:  # value_dropped
            trigger = "VALUE_REGRESSION"
            reason = f"Conversion value dropped {value_change_pct:.1%} (>{value_threshold:.0%} threshold)"
            confidence = min(abs(value_change_pct) / value_threshold * 0.8, 0.85)

        evidence = {
            "roas_before": delta.get("baseline_roas", 0),
            "roas_after": delta.get("current_roas", 0),
            "roas_change_pct": roas_change_pct,
            "roas_threshold": roas_threshold,
            "value_before": delta.get("baseline_conversion_value", 0),
            "value_after": delta.get("current_conversion_value", 0),
            "value_change_pct": value_change_pct,
            "value_threshold": value_threshold,
            "cost_before": delta.get("baseline_cost", 0),
            "cost_after": delta.get("current_cost", 0),
        }

        return RollbackDecision(
            should_rollback=True,
            reason=reason,
            trigger=trigger,
            confidence=confidence,
            evidence=evidence,
        )

    return None


def check_anti_oscillation(
    customer_id: str,
    campaign_id: str,
    lever: str,
    change_date: date,
    db_path: str = "warehouse.duckdb",
) -> bool:
    """
    Check for anti-oscillation violations.

    Constitution Rule: No lever reversal within 14 days.

    Returns:
        True if oscillation detected (BLOCK rollback), False if safe to rollback
    """
    conn = duckdb.connect(db_path, read_only=True)

    # Look for opposite lever changes in the past 14 days
    cutoff_date = change_date - timedelta(days=14)

    # Determine opposite lever
    opposite_lever = None
    if lever == "budget":
        opposite_lever = "bid"
    elif lever == "bid":
        opposite_lever = "budget"

    if opposite_lever:
        query = """
        SELECT COUNT(*) as recent_opposite_changes
        FROM analytics.change_log
        WHERE customer_id = ?
        AND campaign_id = ?
        AND lever = ?
        AND change_date >= ?
        AND change_date < ?
        """

        count = conn.execute(
            query, [customer_id, campaign_id, opposite_lever, cutoff_date, change_date]
        ).fetchone()[0]

        conn.close()

        if count > 0:
            return True  # Oscillation detected - BLOCK rollback
    else:
        conn.close()

    return False  # Safe to rollback


def should_rollback(
    change: "MonitoredChange", config: Dict, db_path: str = "warehouse.duckdb"
) -> RollbackDecision:
    """
    Main rollback decision function.

    Applies Constitution rules based on client's primary KPI.

    Args:
        change: MonitoredChange with baseline, current, and delta populated
        config: Client configuration dict with primary_kpi, targets, etc.
        db_path: Path to DuckDB database

    Returns:
        RollbackDecision with should_rollback=True/False and evidence
    """
    # Must have delta to make decision
    if not change.delta:
        return RollbackDecision(
            should_rollback=False,
            reason="Insufficient data - monitoring window not complete",
            trigger="INSUFFICIENT_DATA",
            confidence=0.0,
            evidence={},
        )

    primary_kpi = config.get("primary_kpi", "roas").lower()

    # Check anti-oscillation first (blocks rollback if violated)
    if check_anti_oscillation(
        change.customer_id,
        change.campaign_id,
        change.lever,
        change.change_date,
        db_path,
    ):
        return RollbackDecision(
            should_rollback=False,
            reason="Anti-oscillation rule: Opposite lever changed within 14 days",
            trigger="ANTI_OSCILLATION_BLOCK",
            confidence=0.0,
            evidence={
                "lever": change.lever,
                "change_date": str(change.change_date),
            },
        )

    # Apply appropriate regression check based on primary KPI
    decision = None

    if primary_kpi in ["cpa", "cost_per_acquisition", "cost_per_lead"]:
        # CPA clients: Check CPA regression
        decision = check_cpa_regression(
            change.delta,
            cpa_threshold=0.20,  # Constitution: 20%
            conv_threshold=0.10,  # Constitution: 10%
        )

    elif primary_kpi in ["roas", "return_on_ad_spend", "value"]:
        # ROAS clients: Check ROAS regression
        decision = check_roas_regression(
            change.delta,
            roas_threshold=0.15,  # Constitution: 15%
            value_threshold=0.15,  # Constitution: 15%
        )

    else:
        # Unknown KPI - default to ROAS rules
        decision = check_roas_regression(change.delta)

    # If regression detected, return the decision
    if decision:
        # Add change metadata to evidence
        decision.evidence.update(
            {
                "change_id": change.change_id,
                "campaign_id": change.campaign_id,
                "campaign_name": change.campaign_name,
                "change_date": str(change.change_date),
                "lever": change.lever,
                "old_value": change.old_value,
                "new_value": change.new_value,
                "change_pct": change.change_pct,
                "rule_id": change.rule_id,
                "primary_kpi": primary_kpi,
            }
        )
        return decision

    # No regression detected - change is performing OK
    return RollbackDecision(
        should_rollback=False,
        reason="Performance within acceptable thresholds",
        trigger="NONE",
        confidence=0.0,
        evidence={
            "change_id": change.change_id,
            "campaign_id": change.campaign_id,
            "cpa_change_pct": change.delta.get("cpa_change_pct", 0),
            "roas_change_pct": change.delta.get("roas_change_pct", 0),
            "conversions_change_pct": change.delta.get("conversions_change_pct", 0),
        },
    )


def format_rollback_decision(decision: RollbackDecision) -> str:
    """Format a rollback decision for human-readable output."""
    lines = []

    if decision.should_rollback:
        lines.append(f"🚨 ROLLBACK RECOMMENDED")
        lines.append(f"Trigger: {decision.trigger}")
        lines.append(f"Confidence: {decision.confidence:.0%}")
    else:
        lines.append(f"✅ NO ROLLBACK NEEDED")
        lines.append(f"Status: {decision.trigger}")

    lines.append(f"Reason: {decision.reason}")

    if decision.evidence:
        lines.append("\nEvidence:")
        for key, value in decision.evidence.items():
            if isinstance(value, float):
                if "pct" in key or "change" in key:
                    lines.append(f"  {key}: {value:+.1%}")
                else:
                    lines.append(f"  {key}: {value:.2f}")
            else:
                lines.append(f"  {key}: {value}")

    return "\n".join(lines)
