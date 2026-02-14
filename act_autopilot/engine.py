"""
Autopilot Engine - Rule orchestration and conflict resolution.

This module coordinates the execution of all Autopilot rules,
resolves conflicts when multiple rules could apply to the same campaign,
and generates the final recommendation report.
"""

import yaml
from typing import List, Dict, Any
from datetime import date
from act_autopilot.models import AutopilotConfig, Recommendation, RuleContext
from act_autopilot.guardrails import run_all_guardrails
from act_autopilot.rules.budget_rules import (
    budget_001_increase_high_roas,
    budget_002_decrease_low_roas,
    budget_003_emergency_cost_spike,
    budget_004_recovery_cost_drop,
    budget_005_pacing_reduction,
    budget_006_hold_volatile,
)
from act_autopilot.rules.bid_rules import (
    bid_001_tighten_troas,
    bid_002_loosen_troas,
    bid_003_hold_cvr_drop,
    bid_004_hold_low_data,
)
from act_autopilot.rules.account_rules import (
    acct_001_pacing_alert,
    acct_002_portfolio_rebalance,
    acct_003_low_data_warning,
)
from act_autopilot.rules.status_rules import (
    status_001_flag_underperformer,
    status_002_ctr_crisis,
    status_003_healthy,
)


def load_autopilot_config(config_path: str) -> AutopilotConfig:
    """
    Load Autopilot configuration from YAML file.

    Args:
        config_path: Path to client config YAML

    Returns:
        AutopilotConfig object
    """
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    # Handle nested customer_id structure
    if "customer_id" in config:
        customer_id = config["customer_id"]
    elif "google_ads" in config and "customer_id" in config["google_ads"]:
        customer_id = config["google_ads"]["customer_id"]
    else:
        customer_id = "UNKNOWN"

    return AutopilotConfig(
        customer_id=customer_id,
        automation_mode=config.get("automation_mode", "insights"),
        risk_tolerance=config.get("risk_tolerance", "conservative"),
        daily_spend_cap=config.get("spend_caps", {}).get("daily", 0.0),
        monthly_spend_cap=config.get("spend_caps", {}).get("monthly", 0.0),
        brand_is_protected=config.get("protected_entities", {}).get(
            "brand_is_protected", False
        ),
        protected_entities=config.get("protected_entities", {}).get("entities", []),
        client_name=config.get("client_name", "UNKNOWN"),
        client_type=config.get("client_type", "ecom"),
        primary_kpi=config.get("primary_kpi", "roas"),
        target_roas=config.get("targets", {}).get("target_roas"),
        target_cpa=config.get("targets", {}).get("target_cpa"),
    )


def run_rules(
    config: AutopilotConfig,
    insights: List[Dict],
    features: List[Dict],
    snapshot_date: date,
    db_path: str = "warehouse.duckdb",
) -> List[Recommendation]:
    """
    Execute all Autopilot rules and return recommendations.

    Args:
        config: Autopilot configuration
        insights: Lighthouse insights for this snapshot date
        features: Campaign features for this snapshot date
        snapshot_date: Date being analyzed
        db_path: Path to DuckDB database

    Returns:
        List of Recommendation objects
    """
    recommendations = []

    # Campaign-level rules (run per campaign)
    for feat in features:
        ctx = RuleContext(
            config=config,
            customer_id=config.customer_id,
            campaign_id=feat.get("campaign_id", "UNKNOWN"),
            snapshot_date=snapshot_date,
            features=feat,
            insights=insights,
            all_features=features,
            all_insights=insights,
            db_path=db_path,
        )

        # Budget rules
        campaign_recs = []
        campaign_recs.extend(
            _safe_call(
                budget_001_increase_high_roas, ctx, "budget_001_increase_high_roas"
            )
        )
        campaign_recs.extend(
            _safe_call(
                budget_002_decrease_low_roas, ctx, "budget_002_decrease_low_roas"
            )
        )
        campaign_recs.extend(
            _safe_call(
                budget_003_emergency_cost_spike, ctx, "budget_003_emergency_cost_spike"
            )
        )
        campaign_recs.extend(
            _safe_call(
                budget_004_recovery_cost_drop, ctx, "budget_004_recovery_cost_drop"
            )
        )
        campaign_recs.extend(
            _safe_call(budget_005_pacing_reduction, ctx, "budget_005_pacing_reduction")
        )
        campaign_recs.extend(
            _safe_call(budget_006_hold_volatile, ctx, "budget_006_hold_volatile")
        )

        # Bid rules
        campaign_recs.extend(
            _safe_call(bid_001_tighten_troas, ctx, "bid_001_tighten_troas")
        )
        campaign_recs.extend(
            _safe_call(bid_002_loosen_troas, ctx, "bid_002_loosen_troas")
        )
        campaign_recs.extend(
            _safe_call(bid_003_hold_cvr_drop, ctx, "bid_003_hold_cvr_drop")
        )
        campaign_recs.extend(
            _safe_call(bid_004_hold_low_data, ctx, "bid_004_hold_low_data")
        )

        # Status rules
        campaign_recs.extend(
            _safe_call(
                status_001_flag_underperformer, ctx, "status_001_flag_underperformer"
            )
        )
        campaign_recs.extend(
            _safe_call(status_002_ctr_crisis, ctx, "status_002_ctr_crisis")
        )
        campaign_recs.extend(_safe_call(status_003_healthy, ctx, "status_003_healthy"))

        recommendations.extend(campaign_recs)

    # Account-level rules (run once per account)
    if features:
        # Use first campaign's context for account-level context
        account_ctx = RuleContext(
            config=config,
            customer_id=config.customer_id,
            campaign_id="ACCOUNT",
            snapshot_date=snapshot_date,
            features=features[0] if features else {},
            insights=insights,
            all_features=features,
            all_insights=insights,
            db_path=db_path,
        )

        recommendations.extend(
            _safe_call(acct_001_pacing_alert, account_ctx, "acct_001_pacing_alert")
        )
        recommendations.extend(
            _safe_call(
                acct_002_portfolio_rebalance,
                account_ctx,
                "acct_002_portfolio_rebalance",
            )
        )
        recommendations.extend(
            _safe_call(
                acct_003_low_data_warning, account_ctx, "acct_003_low_data_warning"
            )
        )

    # Apply guardrails to all recommendations
    for rec in recommendations:
        rec.blocked, rec.block_reason, rec.guardrails_checked = run_all_guardrails(
            rec=rec,
            config=config,
            customer_id=config.customer_id,
            snapshot_date=snapshot_date,
            db_path=db_path,
        )

    # Resolve conflicts
    recommendations = resolve_conflicts(recommendations)

    return recommendations


def _safe_call(rule_func, ctx: RuleContext, rule_name: str) -> List[Recommendation]:
    """
    Safely call a rule function with error handling.

    Args:
        rule_func: Rule function to call
        ctx: RuleContext object
        rule_name: Name of rule (for logging)

    Returns:
        List of recommendations (empty if error)
    """
    try:
        result = rule_func(ctx)
        if result is None:
            return []
        elif isinstance(result, list):
            return result
        else:
            return [result]
    except Exception as e:
        print(
            f"[Autopilot] WARN: Rule {rule_name} failed on campaign {ctx.features.get('campaign_id', 'UNKNOWN')}: {str(e)}"
        )
        return []


def resolve_conflicts(recommendations: List[Recommendation]) -> List[Recommendation]:
    """
    Resolve conflicts when multiple rules apply to the same campaign.

    Conflict resolution logic:
    1. Group by entity_id
    2. Within each entity, select highest priority recommendation
    3. If tied on priority, select lowest risk tier
    4. If still tied, select first recommendation

    Args:
        recommendations: List of recommendations

    Returns:
        Deduplicated list of recommendations
    """
    # Group by entity_id
    by_entity: Dict[str, List[Recommendation]] = {}
    for rec in recommendations:
        entity_id = rec.entity_id
        if entity_id not in by_entity:
            by_entity[entity_id] = []
        by_entity[entity_id].append(rec)

    # Resolve conflicts within each entity
    resolved = []
    for entity_id, entity_recs in by_entity.items():
        if len(entity_recs) == 1:
            resolved.append(entity_recs[0])
        else:
            # Sort by priority (desc), then risk tier (asc: low < med < high)
            risk_order = {"low": 1, "medium": 2, "high": 3}
            sorted_recs = sorted(
                entity_recs,
                key=lambda r: (-r.priority, risk_order.get(r.risk_tier, 999)),
            )
            resolved.append(sorted_recs[0])

    return resolved


def generate_report(
    config: AutopilotConfig, recommendations: List[Recommendation], snapshot_date: date
) -> Dict[str, Any]:
    """
    Generate final recommendation report.

    Args:
        config: Autopilot configuration
        recommendations: List of recommendations
        snapshot_date: Date analyzed

    Returns:
        Report dictionary (JSON-serializable)
    """
    # Count by risk tier
    low_risk = [r for r in recommendations if r.risk_tier == "low"]
    medium_risk = [r for r in recommendations if r.risk_tier == "medium"]
    high_risk = [r for r in recommendations if r.risk_tier == "high"]
    blocked = [r for r in recommendations if r.blocked]
    executable = [r for r in recommendations if not r.blocked]

    return {
        "customer_id": config.customer_id,
        "snapshot_date": snapshot_date.isoformat(),
        "client_name": config.client_name,
        "automation_mode": config.automation_mode,
        "summary": {
            "total_recommendations": len(recommendations),
            "low_risk": len(low_risk),
            "medium_risk": len(medium_risk),
            "high_risk": len(high_risk),
            "blocked": len(blocked),
            "executable": len(executable),
        },
        "recommendations": [
            {
                "rule_id": r.rule_id,
                "rule_name": r.rule_name,
                "entity_type": r.entity_type,
                "entity_id": r.entity_id,
                "campaign_name": r.campaign_name,
                "action_type": r.action_type,
                "risk_tier": r.risk_tier,
                "confidence": r.confidence,
                "current_value": r.current_value,
                "recommended_value": r.recommended_value,
                "change_pct": r.change_pct,
                "rationale": r.rationale,
                "expected_impact": r.expected_impact,
                "blocked": r.blocked,
                "block_reason": r.block_reason,
                "priority": r.priority,
                "constitution_refs": r.constitution_refs,
                "guardrails_checked": r.guardrails_checked,
                "evidence": r.evidence,
                "triggering_diagnosis": r.triggering_diagnosis,
                "triggering_confidence": r.triggering_confidence,
            }
            for r in recommendations
        ],
    }
