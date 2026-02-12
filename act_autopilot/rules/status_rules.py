"""
Campaign Status Rules — Pause/enable/flag decisions.

Rules:
  STATUS-001: Flag underperformer for review (persistent low ROAS)
  STATUS-002: CTR crisis — recommend review (significant creative decline)
  STATUS-003: Healthy campaign — no action needed
"""
from __future__ import annotations

from typing import Optional

from ..models import Recommendation, RuleContext, _safe_float


# ─────────────────────────────────────────────────────────────
# STATUS-001: Flag Underperformer for Review
# ─────────────────────────────────────────────────────────────
def status_001_flag_underperformer(ctx: RuleContext) -> Optional[Recommendation]:
    """
    Trigger: ROAS (30d) < target * 0.50 AND conversions_w30 >= 15 AND cost is significant
    Action:  Flag for human review — potential pause candidate
    Risk:    high (pausing campaigns is always high risk)
    
    This does NOT auto-pause. It flags for human review per Constitution.
    """
    if ctx.config.primary_kpi != "roas" or ctx.config.target_roas is None:
        return None

    roas_w30 = _safe_float(ctx.features.get("roas_w30_mean"))
    conv_w30 = _safe_float(ctx.features.get("conversions_w30_sum"))
    clicks_w7 = _safe_float(ctx.features.get("clicks_w7_sum"))
    cost_w30 = _safe_float(ctx.features.get("cost_micros_w30_sum"))
    campaign_status = str(ctx.features.get("campaign_status") or "")

    target = ctx.config.target_roas

    if roas_w30 >= target * 0.50 or roas_w30 <= 0:
        return None
    if conv_w30 < 15 or clicks_w7 < 30:
        return None
    if campaign_status != "ENABLED":
        return None

    campaign_id = str(ctx.features.get("campaign_id"))
    campaign_name = str(ctx.features.get("campaign_name") or campaign_id)

    return Recommendation(
        rule_id="STATUS-001",
        rule_name="Flag Underperformer for Review",
        entity_type="CAMPAIGN",
        entity_id=campaign_id,
        action_type="review",
        risk_tier="high",
        confidence=0.75,
        current_value=roas_w30,
        recommended_value=target,
        change_pct=None,
        rationale=f"Campaign '{campaign_name}' ROAS (30d) is {roas_w30:.2f} — "
                  f"{((1-(roas_w30/target))*100):.0f}% below target {target:.2f}. "
                  f"Spent {cost_w30/1e6:.2f} (30d). Consider pausing or restructuring.",
        evidence={
            "roas_w30": roas_w30,
            "target_roas": target,
            "deficit_pct": (1 - (roas_w30 / target)),
            "cost_w30_micros": cost_w30,
            "conversions_w30": conv_w30,
            "campaign_status": campaign_status,
        },
        constitution_refs=["CONSTITUTION-4", "CONSTITUTION-5-6"],
        guardrails_checked=["underperformer_review"],
        triggering_diagnosis="PERSISTENT_UNDERPERFORMER",
        triggering_confidence=0.75,
        blocked=False,
        block_reason=None,
        priority=8,
    )


# ─────────────────────────────────────────────────────────────
# STATUS-002: CTR Crisis — Recommend Creative Review
# ─────────────────────────────────────────────────────────────
def status_002_ctr_crisis(ctx: RuleContext) -> Optional[Recommendation]:
    """
    Trigger: Lighthouse CTR_DROP + CTR (7d) < 1% absolute
    Action:  Flag for creative/relevance review
    Risk:    med
    """
    insight = _find_insight(ctx, "CTR_DROP")
    if insight is None:
        return None

    ctr_w7 = _safe_float(ctx.features.get("ctr_w7_mean"))
    ctr_drop_pct = _safe_float(insight["evidence"].get("ctr_w7_vs_prev_pct"))
    campaign_id = str(ctx.features.get("campaign_id"))

    # Only flag if absolute CTR is also concerning
    if ctr_w7 >= 0.01:  # 1%
        return None

    return Recommendation(
        rule_id="STATUS-002",
        rule_name="CTR Crisis — Creative/Relevance Review",
        entity_type="CAMPAIGN",
        entity_id=campaign_id,
        action_type="review",
        risk_tier="med",
        confidence=insight["confidence"],
        current_value=ctr_w7,
        recommended_value=None,
        change_pct=None,
        rationale=f"CTR dropped {ctr_drop_pct:.0%} AND absolute CTR is {ctr_w7:.2%} (<1%). "
                  f"Review ad copy relevance, keyword-to-ad alignment, and landing page.",
        evidence={
            "ctr_w7": ctr_w7,
            "ctr_drop_pct": ctr_drop_pct,
            "lighthouse_confidence": insight["confidence"],
        },
        constitution_refs=["CONSTITUTION-5-2"],
        guardrails_checked=["ctr_assessment"],
        triggering_diagnosis="CTR_DROP",
        triggering_confidence=insight["confidence"],
        blocked=False,
        block_reason=None,
        priority=15,
    )


# ─────────────────────────────────────────────────────────────
# STATUS-003: Healthy Campaign — No Action
# ─────────────────────────────────────────────────────────────
def status_003_healthy(ctx: RuleContext) -> Optional[Recommendation]:
    """
    Trigger: No Lighthouse diagnosis codes fired (only NEEDS_REVIEW filler)
             AND campaign has sufficient data AND ROAS within ±15% of target
    Action:  Explicit "healthy" status — no intervention needed
    Risk:    low
    """
    if ctx.config.target_roas is None:
        return None

    campaign_id = str(ctx.features.get("campaign_id"))

    # Check no real diagnosis codes (only NEEDS_REVIEW fillers)
    real_codes = {"COST_SPIKE", "COST_DROP", "CTR_DROP", "CVR_DROP", "VOLATILE", "LOW_DATA", "PACE_OVER_CAP"}
    has_real = any(
        ins.get("diagnosis_code") in real_codes and str(ins.get("entity_id")) == campaign_id
        for ins in ctx.insights
    )
    if has_real:
        return None

    # Must have sufficient data
    clicks_w7 = _safe_float(ctx.features.get("clicks_w7_sum"))
    conv_w30 = _safe_float(ctx.features.get("conversions_w30_sum"))
    if clicks_w7 < 30 or conv_w30 < 15:
        return None

    # ROAS within ±15% of target
    roas_w7 = _safe_float(ctx.features.get("roas_w7_mean"))
    target = ctx.config.target_roas
    if roas_w7 <= 0 or abs((roas_w7 / target) - 1.0) > 0.15:
        return None

    return Recommendation(
        rule_id="STATUS-003",
        rule_name="Healthy Campaign — No Action Needed",
        entity_type="CAMPAIGN",
        entity_id=campaign_id,
        action_type="no_action",
        risk_tier="low",
        confidence=0.80,
        current_value=roas_w7,
        recommended_value=target,
        change_pct=None,
        rationale=f"Campaign is healthy: ROAS {roas_w7:.2f} within ±15% of target {target:.2f}, "
                  f"no diagnosis codes, sufficient data. No intervention needed.",
        evidence={
            "roas_w7": roas_w7,
            "target_roas": target,
            "roas_deviation_pct": (roas_w7 / target) - 1.0,
            "clicks_w7": clicks_w7,
            "conversions_w30": conv_w30,
        },
        constitution_refs=[],
        guardrails_checked=["health_assessment"],
        triggering_diagnosis="HEALTHY",
        triggering_confidence=0.80,
        blocked=False,
        block_reason=None,
        priority=90,  # low priority — informational
    )


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────
def _find_insight(ctx: RuleContext, diagnosis_code: str) -> Optional[dict]:
    campaign_id = str(ctx.features.get("campaign_id"))
    for ins in ctx.insights:
        if ins.get("diagnosis_code") == diagnosis_code and str(ins.get("entity_id")) == campaign_id:
            return ins
    return None


# Registry
STATUS_RULES = [
    status_001_flag_underperformer,
    status_002_ctr_crisis,
    status_003_healthy,
]
