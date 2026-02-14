"""
Bid Rules — Campaign-level bid target optimization.

Rules:
  BID-001: Tighten tROAS target (beating goal significantly)
  BID-002: Loosen tROAS target (missing goal, but has volume)
  BID-003: Hold bid target (CVR drop — investigate first)
  BID-004: Hold bid target (low data — collect more)
"""
from __future__ import annotations

from typing import Optional

from ..models import Recommendation, RuleContext, _safe_float


# ─────────────────────────────────────────────────────────────
# BID-001: Tighten tROAS — Beating Goal Significantly
# ─────────────────────────────────────────────────────────────
def bid_001_tighten_troas(ctx: RuleContext) -> Optional[Recommendation]:
    """
    Trigger: ROAS (30d) > target_roas * 1.25 AND conversions_w30 >= 15 AND stable (CV < 0.60)
    Action:  Increase tROAS target by +5% (conservative) / +10% (balanced)
    Risk:    med (bid target changes are medium risk)
    
    Rationale: Campaign is significantly outperforming target — tighten to improve efficiency
    or allow Google to find cheaper conversions.
    """
    if ctx.config.primary_kpi != "roas" or ctx.config.target_roas is None:
        return None

    roas_w30 = _safe_float(ctx.features.get("roas_w30_mean"))
    conv_w30 = _safe_float(ctx.features.get("conversions_w30_sum"))
    cost_cv14 = _safe_float(ctx.features.get("cost_w14_cv"), default=1.0)

    target = ctx.config.target_roas
    threshold = target * 1.25

    if roas_w30 <= threshold:
        return None
    if conv_w30 < 15:
        return None
    if cost_cv14 >= 0.60:
        return None  # too volatile

    change_pct = 0.05 if ctx.config.risk_tolerance == "conservative" else 0.10
    new_target_roas = target * (1 + change_pct)
    campaign_id = str(ctx.features.get("campaign_id"))

    passed, block_reason, checked = (True, None, [])

    return Recommendation(
        rule_id="BID-001",
        rule_name="Tighten tROAS Target — Beating Goal",
        entity_type="CAMPAIGN",
        entity_id=campaign_id,
        action_type="bid_target_increase",
        risk_tier="med",
        confidence=0.70,
        current_value=target,
        recommended_value=new_target_roas,
        change_pct=change_pct,
        rationale=f"ROAS (30d) is {roas_w30:.2f}, exceeding target {target:.2f} by {((roas_w30/target)-1)*100:.0f}%. "
                  f"Tightening tROAS target to {new_target_roas:.2f} (+{change_pct:.0%}).",
        evidence={
            "roas_w30": roas_w30,
            "target_roas": target,
            "threshold": threshold,
            "conversions_w30": conv_w30,
            "cost_cv14": cost_cv14,
        },
        constitution_refs=["CONSTITUTION-5-1", "CONSTITUTION-5-2", "CONSTITUTION-A-4"],
        guardrails_checked=checked,
        triggering_diagnosis="HIGH_ROAS_SUSTAINED",
        triggering_confidence=0.70,
        blocked=not passed,
        block_reason=block_reason,
        priority=35,
    )


# ─────────────────────────────────────────────────────────────
# BID-002: Loosen tROAS — Missing Goal with Volume
# ─────────────────────────────────────────────────────────────
def bid_002_loosen_troas(ctx: RuleContext) -> Optional[Recommendation]:
    """
    Trigger: ROAS (30d) < target_roas * 0.85 AND conversions_w30 >= 15 AND stable
    Action:  Decrease tROAS target by -5% to give bidder more room
    Risk:    med
    
    Rationale: Campaign is consistently missing target — loosen to avoid limiting volume too much.
    """
    if ctx.config.primary_kpi != "roas" or ctx.config.target_roas is None:
        return None

    roas_w30 = _safe_float(ctx.features.get("roas_w30_mean"))
    conv_w30 = _safe_float(ctx.features.get("conversions_w30_sum"))
    cost_cv14 = _safe_float(ctx.features.get("cost_w14_cv"), default=1.0)

    target = ctx.config.target_roas
    threshold = target * 0.85

    if roas_w30 >= threshold or roas_w30 <= 0:
        return None
    if conv_w30 < 15:
        return None
    if cost_cv14 >= 0.60:
        return None

    change_pct = -0.05
    new_target_roas = target * (1 + change_pct)
    campaign_id = str(ctx.features.get("campaign_id"))

    passed, block_reason, checked = (True, None, [])

    return Recommendation(
        rule_id="BID-002",
        rule_name="Loosen tROAS Target — Missing Goal",
        entity_type="CAMPAIGN",
        entity_id=campaign_id,
        action_type="bid_target_decrease",
        risk_tier="med",
        confidence=0.65,
        current_value=target,
        recommended_value=new_target_roas,
        change_pct=change_pct,
        rationale=f"ROAS (30d) is {roas_w30:.2f}, {((1-(roas_w30/target))*100):.0f}% below target {target:.2f}. "
                  f"Loosening tROAS to {new_target_roas:.2f} ({change_pct:.0%}) to give smart bidding more room.",
        evidence={
            "roas_w30": roas_w30,
            "target_roas": target,
            "threshold": threshold,
            "conversions_w30": conv_w30,
            "cost_cv14": cost_cv14,
        },
        constitution_refs=["CONSTITUTION-5-1", "CONSTITUTION-5-2", "CONSTITUTION-A-4"],
        guardrails_checked=checked,
        triggering_diagnosis="LOW_ROAS_SUSTAINED",
        triggering_confidence=0.65,
        blocked=not passed,
        block_reason=block_reason,
        priority=35,
    )


# ─────────────────────────────────────────────────────────────
# BID-003: Hold Bid — CVR Drop (Investigate First)
# ─────────────────────────────────────────────────────────────
def bid_003_hold_cvr_drop(ctx: RuleContext) -> Optional[Recommendation]:
    """
    Trigger: Lighthouse CVR_DROP or CTR_DROP diagnosis
    Action:  Explicit HOLD — do not change bids until investigated
    Risk:    med
    """
    insight = _find_insight(ctx, "CVR_DROP")
    label = "CVR"
    if insight is None:
        insight = _find_insight(ctx, "CTR_DROP")
        label = "CTR"
    if insight is None:
        return None

    drop_pct = _safe_float(insight["evidence"].get("cvr_w14_vs_prev_pct") or insight["evidence"].get("ctr_w7_vs_prev_pct"))
    campaign_id = str(ctx.features.get("campaign_id"))

    return Recommendation(
        rule_id="BID-003",
        rule_name=f"Hold Bid Target — {label} Drop Investigation",
        entity_type="CAMPAIGN",
        entity_id=campaign_id,
        action_type="bid_hold",
        risk_tier="med",
        confidence=insight["confidence"],
        current_value=None,
        recommended_value=None,
        change_pct=0.0,
        rationale=f"{label} dropped {drop_pct:.0%}. "
                  f"Hold bid target until root cause identified (landing page, tracking, demand shift, creative).",
        evidence={
            f"{label.lower()}_drop_pct": drop_pct,
            "lighthouse_confidence": insight["confidence"],
            "diagnosis_code": insight["diagnosis_code"],
        },
        constitution_refs=["CONSTITUTION-5-3", "CONSTITUTION-5-7"],
        guardrails_checked=["efficiency_investigation_hold"],
        triggering_diagnosis=insight["diagnosis_code"],
        triggering_confidence=insight["confidence"],
        blocked=False,
        block_reason=None,
        priority=10,
    )


# ─────────────────────────────────────────────────────────────
# BID-004: Hold Bid — Low Data
# ─────────────────────────────────────────────────────────────
def bid_004_hold_low_data(ctx: RuleContext) -> Optional[Recommendation]:
    """
    Trigger: Lighthouse LOW_DATA diagnosis OR conversions_w30 < 15
    Action:  Explicit HOLD — collect more data before bid changes
    Risk:    low
    """
    insight = _find_insight(ctx, "LOW_DATA")
    conv_w30 = _safe_float(ctx.features.get("conversions_w30_sum"))

    if insight is None and conv_w30 >= 15:
        return None

    campaign_id = str(ctx.features.get("campaign_id"))
    clicks_w7 = _safe_float(ctx.features.get("clicks_w7_sum"))

    confidence = 0.35
    if insight is not None:
        confidence = insight["confidence"]

    return Recommendation(
        rule_id="BID-004",
        rule_name="Hold Bid Target — Low Data",
        entity_type="CAMPAIGN",
        entity_id=campaign_id,
        action_type="bid_hold",
        risk_tier="low",
        confidence=confidence,
        current_value=None,
        recommended_value=None,
        change_pct=0.0,
        rationale=f"Low data: {conv_w30:.0f} conversions (30d), {clicks_w7:.0f} clicks (7d). "
                  f"Need ≥15 conversions (30d) before any bid target changes.",
        evidence={
            "conversions_w30": conv_w30,
            "clicks_w7": clicks_w7,
            "conv_threshold": 15,
        },
        constitution_refs=["CONSTITUTION-5-2", "CONSTITUTION-A-4"],
        guardrails_checked=["low_data_block"],
        triggering_diagnosis="LOW_DATA",
        triggering_confidence=confidence,
        blocked=False,
        block_reason=None,
        priority=45,
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
BID_RULES = [
    bid_003_hold_cvr_drop,
    bid_004_hold_low_data,
    bid_001_tighten_troas,
    bid_002_loosen_troas,
]
