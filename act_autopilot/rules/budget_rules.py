"""
Budget Rules — Campaign-level budget optimization.

Rules:
  BUDGET-001: Increase budget (high ROAS + sufficient data)
  BUDGET-002: Decrease budget (low ROAS)
  BUDGET-003: Emergency budget cut (cost spike)
  BUDGET-004: Recovery budget increase (cost drop + good efficiency)
  BUDGET-005: Pacing reduction (monthly cap at risk)
  BUDGET-006: Stabilise budget (volatile campaign — hold steady)
"""
from __future__ import annotations

from typing import List, Optional

from ..models import Recommendation, RuleContext, _safe_float
from ..guardrails import run_all_guardrails


# ─────────────────────────────────────────────────────────────
# BUDGET-001: Increase Budget — High ROAS + Sufficient Data
# ─────────────────────────────────────────────────────────────
def budget_001_increase_high_roas(ctx: RuleContext) -> Optional[Recommendation]:
    """
    Trigger: Campaign ROAS (7d) > target_roas * 1.15 AND clicks_w7 >= 30
    Action:  +5% budget (conservative) / +10% (balanced/aggressive)
    Risk:    low
    """
    if ctx.config.primary_kpi != "roas" or ctx.config.target_roas is None:
        return None

    roas_w7 = _safe_float(ctx.features.get("roas_w7_mean"))
    clicks_w7 = _safe_float(ctx.features.get("clicks_w7_sum"))
    cost_w7 = _safe_float(ctx.features.get("cost_micros_w7_sum"))
    conv_value_w7 = _safe_float(ctx.features.get("conversion_value_w7_sum"))

    target = ctx.config.target_roas
    threshold = target * 1.15

    if roas_w7 <= threshold:
        return None
    if clicks_w7 < 30:
        return None
    if cost_w7 <= 0:
        return None

    # Determine insight confidence (use highest matching insight)
    confidence = _best_insight_confidence(ctx, ["NEEDS_REVIEW", "COST_DROP"])
    if confidence is None:
        confidence = 0.60  # default if no insight found

    change_pct = 0.05 if ctx.config.risk_tolerance == "conservative" else 0.10
    campaign_id = str(ctx.features.get("campaign_id"))

    # Estimate current daily budget from 7d average cost
    current_daily_budget_micros = cost_w7 / 7.0
    new_daily_budget_micros = current_daily_budget_micros * (1 + change_pct)

    passed, block_reason, checked = run_all_guardrails(
        ctx, "budget_increase", "low", campaign_id, change_pct, confidence,
        new_value_micros=new_daily_budget_micros,
    )

    return Recommendation(
        rule_id="BUDGET-001",
        rule_name="Increase Budget — High ROAS",
        entity_type="CAMPAIGN",
        entity_id=campaign_id,
        action_type="budget_increase",
        risk_tier="low",
        confidence=confidence,
        current_value=current_daily_budget_micros,
        recommended_value=new_daily_budget_micros,
        change_pct=change_pct,
        rationale=f"ROAS {roas_w7:.2f} exceeds target {target:.2f} by {((roas_w7/target)-1)*100:.0f}%. "
                  f"Increasing budget by {change_pct:.0%} to capture additional conversions.",
        evidence={
            "roas_w7": roas_w7,
            "target_roas": target,
            "threshold": threshold,
            "clicks_w7": clicks_w7,
            "cost_w7_micros": cost_w7,
            "conv_value_w7": conv_value_w7,
        },
        constitution_refs=["CONSTITUTION-5-1", "CONSTITUTION-5-5", "CONSTITUTION-A-4"],
        guardrails_checked=checked,
        triggering_diagnosis="HIGH_ROAS_OPPORTUNITY",
        triggering_confidence=confidence,
        blocked=not passed,
        block_reason=block_reason,
        priority=20,
    )


# ─────────────────────────────────────────────────────────────
# BUDGET-002: Decrease Budget — Low ROAS
# ─────────────────────────────────────────────────────────────
def budget_002_decrease_low_roas(ctx: RuleContext) -> Optional[Recommendation]:
    """
    Trigger: Campaign ROAS (7d) < target_roas * 0.75 AND clicks_w7 >= 30 AND conversions_w30 >= 15
    Action:  -5% budget (conservative) / -10% (balanced/aggressive)
    Risk:    low
    """
    if ctx.config.primary_kpi != "roas" or ctx.config.target_roas is None:
        return None

    roas_w7 = _safe_float(ctx.features.get("roas_w7_mean"))
    clicks_w7 = _safe_float(ctx.features.get("clicks_w7_sum"))
    conv_w30 = _safe_float(ctx.features.get("conversions_w30_sum"))
    cost_w7 = _safe_float(ctx.features.get("cost_micros_w7_sum"))

    target = ctx.config.target_roas
    threshold = target * 0.75

    if roas_w7 >= threshold or roas_w7 <= 0:
        return None
    if clicks_w7 < 30 or conv_w30 < 15:
        return None

    confidence = _best_insight_confidence(ctx, ["CVR_DROP", "NEEDS_REVIEW"])
    if confidence is None:
        confidence = 0.65

    change_pct = -0.05 if ctx.config.risk_tolerance == "conservative" else -0.10
    campaign_id = str(ctx.features.get("campaign_id"))
    current_daily_budget_micros = cost_w7 / 7.0
    new_daily_budget_micros = current_daily_budget_micros * (1 + change_pct)

    passed, block_reason, checked = run_all_guardrails(
        ctx, "budget_decrease", "low", campaign_id, change_pct, confidence,
        new_value_micros=new_daily_budget_micros,
    )

    return Recommendation(
        rule_id="BUDGET-002",
        rule_name="Decrease Budget — Low ROAS",
        entity_type="CAMPAIGN",
        entity_id=campaign_id,
        action_type="budget_decrease",
        risk_tier="low",
        confidence=confidence,
        current_value=current_daily_budget_micros,
        recommended_value=new_daily_budget_micros,
        change_pct=change_pct,
        rationale=f"ROAS {roas_w7:.2f} is {((1-(roas_w7/target))*100):.0f}% below target {target:.2f}. "
                  f"Reducing budget by {abs(change_pct):.0%} to limit waste.",
        evidence={
            "roas_w7": roas_w7,
            "target_roas": target,
            "threshold": threshold,
            "clicks_w7": clicks_w7,
            "conversions_w30": conv_w30,
        },
        constitution_refs=["CONSTITUTION-5-1", "CONSTITUTION-A-4"],
        guardrails_checked=checked,
        triggering_diagnosis="LOW_ROAS",
        triggering_confidence=confidence,
        blocked=not passed,
        block_reason=block_reason,
        priority=15,
    )


# ─────────────────────────────────────────────────────────────
# BUDGET-003: Emergency Budget Cut — Cost Spike
# ─────────────────────────────────────────────────────────────
def budget_003_emergency_cost_spike(ctx: RuleContext) -> Optional[Recommendation]:
    """
    Trigger: Lighthouse COST_SPIKE diagnosis + confidence >= 0.6
    Action:  -10% budget (immediate, conservative still -5%)
    Risk:    med (requires attention)
    """
    insight = _find_insight(ctx, "COST_SPIKE")
    if insight is None:
        return None
    if insight["confidence"] < 0.6:
        return None

    cost_w1_pct = _safe_float(insight["evidence"].get("cost_micros_w1_vs_prev_pct"))
    campaign_id = str(ctx.features.get("campaign_id"))
    cost_w7 = _safe_float(ctx.features.get("cost_micros_w7_sum"))

    change_pct = -0.05 if ctx.config.risk_tolerance == "conservative" else -0.10
    current_daily_budget_micros = cost_w7 / 7.0
    new_daily_budget_micros = current_daily_budget_micros * (1 + change_pct)

    passed, block_reason, checked = run_all_guardrails(
        ctx, "budget_decrease", "med", campaign_id, change_pct, insight["confidence"],
        new_value_micros=new_daily_budget_micros,
    )

    return Recommendation(
        rule_id="BUDGET-003",
        rule_name="Emergency Budget Cut — Cost Spike",
        entity_type="CAMPAIGN",
        entity_id=campaign_id,
        action_type="budget_decrease",
        risk_tier="med",
        confidence=insight["confidence"],
        current_value=current_daily_budget_micros,
        recommended_value=new_daily_budget_micros,
        change_pct=change_pct,
        rationale=f"Cost spiked {cost_w1_pct:+.0%} day-over-day. "
                  f"Cutting budget by {abs(change_pct):.0%} to contain overspend pending investigation.",
        evidence={
            "cost_spike_pct": cost_w1_pct,
            "lighthouse_confidence": insight["confidence"],
            "cost_w7_micros": cost_w7,
        },
        constitution_refs=["CONSTITUTION-5-1", "CONSTITUTION-5-8"],
        guardrails_checked=checked,
        triggering_diagnosis="COST_SPIKE",
        triggering_confidence=insight["confidence"],
        blocked=not passed,
        block_reason=block_reason,
        priority=5,  # high priority
    )


# ─────────────────────────────────────────────────────────────
# BUDGET-004: Recovery Budget Increase — Cost Drop + Good Efficiency
# ─────────────────────────────────────────────────────────────
def budget_004_recovery_cost_drop(ctx: RuleContext) -> Optional[Recommendation]:
    """
    Trigger: Lighthouse COST_DROP + ROAS (7d) >= target_roas
    Action:  +5% budget to recover lost volume
    Risk:    low
    """
    insight = _find_insight(ctx, "COST_DROP")
    if insight is None:
        return None
    if ctx.config.target_roas is None:
        return None

    roas_w7 = _safe_float(ctx.features.get("roas_w7_mean"))
    clicks_w7 = _safe_float(ctx.features.get("clicks_w7_sum"))
    cost_w7 = _safe_float(ctx.features.get("cost_micros_w7_sum"))

    if roas_w7 < ctx.config.target_roas:
        return None
    if clicks_w7 < 30:
        return None

    change_pct = 0.05
    campaign_id = str(ctx.features.get("campaign_id"))
    current_daily_budget_micros = cost_w7 / 7.0
    new_daily_budget_micros = current_daily_budget_micros * (1 + change_pct)

    passed, block_reason, checked = run_all_guardrails(
        ctx, "budget_recovery", "low", campaign_id, change_pct, insight["confidence"],
        new_value_micros=new_daily_budget_micros,
    )

    return Recommendation(
        rule_id="BUDGET-004",
        rule_name="Recovery Budget Increase — Cost Drop",
        entity_type="CAMPAIGN",
        entity_id=campaign_id,
        action_type="budget_increase",
        risk_tier="low",
        confidence=insight["confidence"],
        current_value=current_daily_budget_micros,
        recommended_value=new_daily_budget_micros,
        change_pct=change_pct,
        rationale=f"Cost dropped significantly but ROAS {roas_w7:.2f} is still above target {ctx.config.target_roas:.2f}. "
                  f"Increasing budget by {change_pct:.0%} to recover lost volume.",
        evidence={
            "cost_drop_pct": _safe_float(insight["evidence"].get("cost_micros_w1_vs_prev_pct")),
            "roas_w7": roas_w7,
            "target_roas": ctx.config.target_roas,
            "clicks_w7": clicks_w7,
        },
        constitution_refs=["CONSTITUTION-5-1", "CONSTITUTION-5-5"],
        guardrails_checked=checked,
        triggering_diagnosis="COST_DROP",
        triggering_confidence=insight["confidence"],
        blocked=not passed,
        block_reason=block_reason,
        priority=25,
    )


# ─────────────────────────────────────────────────────────────
# BUDGET-005: Pacing Reduction — Monthly Cap at Risk
# ─────────────────────────────────────────────────────────────
def budget_005_pacing_reduction(ctx: RuleContext) -> Optional[Recommendation]:
    """
    Trigger: Lighthouse PACE_OVER_CAP at ACCOUNT level
    Action:  -10% budget on highest-cost campaign
    Risk:    high (account-level impact)
    
    NOTE: This rule only fires for the highest-spend campaign per account.
    """
    insight = _find_account_insight(ctx, "PACE_OVER_CAP")
    if insight is None:
        return None

    # Only fire for the single highest-cost campaign
    campaign_id = str(ctx.features.get("campaign_id"))
    cost_w7 = _safe_float(ctx.features.get("cost_micros_w7_sum"))

    highest_cost_campaign = max(
        ctx.all_features,
        key=lambda f: _safe_float(f.get("cost_micros_w7_sum")),
    )
    if str(highest_cost_campaign.get("campaign_id")) != campaign_id:
        return None

    pacing_pct = _safe_float(insight["evidence"].get("acct_pacing_vs_cap_pct"))
    change_pct = -0.10
    current_daily_budget_micros = cost_w7 / 7.0
    new_daily_budget_micros = current_daily_budget_micros * (1 + change_pct)

    passed, block_reason, checked = run_all_guardrails(
        ctx, "budget_decrease", "high", campaign_id, change_pct, insight["confidence"],
        new_value_micros=new_daily_budget_micros,
    )

    return Recommendation(
        rule_id="BUDGET-005",
        rule_name="Pacing Reduction — Monthly Cap at Risk",
        entity_type="CAMPAIGN",
        entity_id=campaign_id,
        action_type="pacing_cut",
        risk_tier="high",
        confidence=insight["confidence"],
        current_value=current_daily_budget_micros,
        recommended_value=new_daily_budget_micros,
        change_pct=change_pct,
        rationale=f"Account pacing {pacing_pct:+.1%} over monthly cap. "
                  f"Cutting highest-spend campaign budget by {abs(change_pct):.0%}.",
        evidence={
            "pacing_over_cap_pct": pacing_pct,
            "projected_monthly_micros": insight["evidence"].get("acct_projected_month_cost_micros"),
            "monthly_cap_micros": insight["evidence"].get("acct_monthly_cap_micros"),
            "campaign_cost_w7": cost_w7,
        },
        constitution_refs=["CONSTITUTION-5-5", "CONSTITUTION-5-8"],
        guardrails_checked=checked,
        triggering_diagnosis="PACE_OVER_CAP",
        triggering_confidence=insight["confidence"],
        blocked=not passed,
        block_reason=block_reason,
        priority=3,  # very high priority
    )


# ─────────────────────────────────────────────────────────────
# BUDGET-006: Hold Budget — Volatile Campaign
# ─────────────────────────────────────────────────────────────
def budget_006_hold_volatile(ctx: RuleContext) -> Optional[Recommendation]:
    """
    Trigger: Lighthouse VOLATILE diagnosis + confidence >= 0.5
             OR cost_w14_cv > 0.60 from features directly
    Action:  No change (explicit hold recommendation)
    Risk:    low (it's a "do nothing" recommendation)
    """
    insight = _find_insight(ctx, "VOLATILE")
    cost_cv = _safe_float(ctx.features.get("cost_w14_cv"))

    # Try Lighthouse insight first
    if insight is not None and insight["confidence"] >= 0.5:
        confidence = insight["confidence"]
        source = "lighthouse"
    elif cost_cv > 0.35:
        # Fallback: check features directly
        confidence = 0.60
        source = "features"
    else:
        return None

    campaign_id = str(ctx.features.get("campaign_id"))

    return Recommendation(
        rule_id="BUDGET-006",
        rule_name="Hold Budget — Volatile Campaign",
        entity_type="CAMPAIGN",
        entity_id=campaign_id,
        action_type="budget_hold",
        risk_tier="low",
        confidence=insight["confidence"],
        current_value=None,
        recommended_value=None,
        change_pct=0.0,
        rationale=f"Campaign is volatile (cost CV={cost_cv:.2f}). "
                  f"Holding budget steady until variance stabilises below 0.60.",
        evidence={
            "cost_w14_cv": cost_cv,
            "volatile_threshold": 0.60,
            "lighthouse_confidence": insight["confidence"],
        },
        constitution_refs=["CONSTITUTION-5-3"],
        guardrails_checked=["volatility_check"],
        triggering_diagnosis="VOLATILE",
        triggering_confidence=insight["confidence"],
        blocked=False,
        block_reason=None,
        priority=40,
    )


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────
def _find_insight(ctx: RuleContext, diagnosis_code: str) -> Optional[dict]:
    """Find a Lighthouse insight for this campaign by diagnosis code."""
    campaign_id = str(ctx.features.get("campaign_id"))
    for ins in ctx.insights:
        if ins.get("diagnosis_code") == diagnosis_code and str(ins.get("entity_id")) == campaign_id:
            return ins
    return None


def _find_account_insight(ctx: RuleContext, diagnosis_code: str) -> Optional[dict]:
    """Find an ACCOUNT-level Lighthouse insight."""
    for ins in ctx.all_insights:
        if ins.get("diagnosis_code") == diagnosis_code and ins.get("entity_type") == "ACCOUNT":
            return ins
    return None


def _best_insight_confidence(ctx: RuleContext, codes: List[str]) -> Optional[float]:
    """Return highest confidence from matching insights for this campaign."""
    campaign_id = str(ctx.features.get("campaign_id"))
    best = None
    for ins in ctx.insights:
        if str(ins.get("entity_id")) == campaign_id and ins.get("diagnosis_code") in codes:
            c = _safe_float(ins.get("confidence"))
            if best is None or c > best:
                best = c
    return best


# Registry of all budget rules (order = evaluation order)
BUDGET_RULES = [
    budget_005_pacing_reduction,    # highest priority
    budget_003_emergency_cost_spike,
    budget_002_decrease_low_roas,
    budget_001_increase_high_roas,
    budget_004_recovery_cost_drop,
    budget_006_hold_volatile,
]
