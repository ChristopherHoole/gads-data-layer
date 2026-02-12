"""
Guardrails — Constitution compliance checks applied to every recommendation.

Each check returns (passed: bool, reason: str).
If passed=False, the recommendation is blocked with the reason.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from .models import AutopilotConfig, RuleContext, _safe_float


def check_low_data_block(ctx: RuleContext) -> Tuple[bool, str]:
    """CONSTITUTION-5-2 / CONSTITUTION-A-4: No execution if <30 clicks (7d)."""
    clicks_w7 = _safe_float(ctx.features.get("clicks_w7_sum"))
    if clicks_w7 < 30:
        return False, f"Low data block: clicks_w7={clicks_w7:.0f} < 30 (CONSTITUTION-A-4)"
    return True, ""


def check_low_conversions_for_bid(ctx: RuleContext, action_type: str) -> Tuple[bool, str]:
    """CONSTITUTION-A-4: No bid target changes if <15 conversions (30d)."""
    if "bid" not in action_type:
        return True, ""
    conv_w30 = _safe_float(ctx.features.get("conversions_w30_sum"))
    if conv_w30 < 15:
        return False, f"Low conversion block for bid change: conversions_w30={conv_w30:.1f} < 15 (CONSTITUTION-A-4)"
    return True, ""


def check_protected_entity(ctx: RuleContext, campaign_id: Optional[str], action_type: str) -> Tuple[bool, str]:
    """CONSTITUTION-5-6: Protected entities are immutable unless explicit override."""
    if campaign_id is None:
        return True, ""
    # Check if campaign is in protected list
    if campaign_id in ctx.config.protected_campaign_ids:
        return False, f"Protected entity: campaign {campaign_id} is in protected list (CONSTITUTION-5-6)"
    # Check brand protection by campaign name
    if ctx.config.brand_is_protected:
        cname = str(ctx.features.get("campaign_name") or "").lower()
        if "brand" in cname:
            return False, f"Brand protected: campaign '{cname}' contains 'brand' (CONSTITUTION-5-6)"
    return True, ""


def check_budget_change_cap(change_pct: float, risk_tolerance: str) -> Tuple[bool, str]:
    """CONSTITUTION-5-1: Budget change caps per risk tolerance."""
    caps = {"conservative": 0.05, "balanced": 0.10, "aggressive": 0.15}
    cap = caps.get(risk_tolerance, 0.10)
    absolute_cap = 0.20

    if abs(change_pct) > absolute_cap:
        return False, f"Budget change {change_pct:+.1%} exceeds absolute cap ±20% (CONSTITUTION-5-1)"
    if abs(change_pct) > cap:
        return False, f"Budget change {change_pct:+.1%} exceeds {risk_tolerance} cap ±{cap:.0%} (CONSTITUTION-5-1)"
    return True, ""


def check_bid_change_cap(change_pct: float, risk_tolerance: str) -> Tuple[bool, str]:
    """CONSTITUTION-5-1: Bid/target change caps per risk tolerance."""
    caps = {"conservative": 0.05, "balanced": 0.10, "aggressive": 0.15}
    cap = caps.get(risk_tolerance, 0.10)

    if abs(change_pct) > 0.15:
        return False, f"Bid change {change_pct:+.1%} exceeds max ±15% (CONSTITUTION-5-1)"
    if abs(change_pct) > cap:
        return False, f"Bid change {change_pct:+.1%} exceeds {risk_tolerance} cap ±{cap:.0%} (CONSTITUTION-5-1)"
    return True, ""


def check_daily_spend_cap(ctx: RuleContext, new_budget_micros: Optional[float]) -> Tuple[bool, str]:
    """CONSTITUTION-5-5: Daily spend cap enforcement."""
    if ctx.config.daily_cap is None or new_budget_micros is None:
        return True, ""
    daily_cap_micros = ctx.config.daily_cap * 1_000_000
    # Sum of all campaign budgets shouldn't exceed daily cap
    # For now: check if this single campaign's new budget exceeds daily cap
    if new_budget_micros > daily_cap_micros:
        return False, f"New budget {new_budget_micros/1e6:.2f} exceeds daily cap {ctx.config.daily_cap:.2f} (CONSTITUTION-5-5)"
    return True, ""


def check_monthly_pacing(ctx: RuleContext) -> Tuple[bool, str]:
    """CONSTITUTION-5-5: Block expansions if pacing >105% of monthly cap."""
    pacing_flag = ctx.features.get("pacing_flag_over_105")
    if pacing_flag is True:
        return False, "Monthly pacing >105% of cap — no expansions allowed (CONSTITUTION-5-5)"
    return True, ""


def check_confidence_threshold(confidence: float, min_confidence: float = 0.5) -> Tuple[bool, str]:
    """Block if confidence too low."""
    if confidence < min_confidence:
        return False, f"Confidence {confidence:.2f} < minimum {min_confidence:.2f}"
    return True, ""


def check_automation_mode(ctx: RuleContext, risk_tier: str) -> Tuple[bool, str]:
    """CONSTITUTION-6: Check if automation_mode allows this risk tier."""
    mode = ctx.config.automation_mode
    if mode == "insights":
        return False, f"automation_mode=insights — no execution allowed (CONSTITUTION-6)"
    if mode == "suggest":
        # suggest mode: recommendations are generated but not executed
        # We don't block — we just mark them as suggestions
        return True, ""
    if mode == "auto_low_risk":
        if risk_tier != "low":
            return False, f"automation_mode=auto_low_risk — {risk_tier} risk not auto-executable (CONSTITUTION-6)"
    if mode == "auto_expanded":
        if risk_tier == "high":
            return False, f"automation_mode=auto_expanded — high risk always requires approval (CONSTITUTION-6)"
    return True, ""


def check_one_lever_rule(ctx: RuleContext, campaign_id: Optional[str], lever: str) -> Tuple[bool, str]:
    """CONSTITUTION-5-4: One lever at a time — no budget+bid on same campaign within 7d."""
    if campaign_id is None:
        return True, ""
    opposite = "bid" if "budget" in lever else "budget"
    for change in ctx.recent_changes:
        if str(change.get("entity_id")) == campaign_id and opposite in str(change.get("lever", "")):
            return False, f"One-lever rule: {opposite} change exists on campaign {campaign_id} within 7d (CONSTITUTION-5-4)"
    return True, ""


def check_cooldown(ctx: RuleContext, campaign_id: Optional[str], lever: str) -> Tuple[bool, str]:
    """CONSTITUTION-5-3: 7-day cooldown on same entity+lever."""
    if campaign_id is None:
        return True, ""
    for change in ctx.recent_changes:
        if str(change.get("entity_id")) == campaign_id and lever in str(change.get("lever", "")):
            return False, f"Cooldown: {lever} change on campaign {campaign_id} within 7d (CONSTITUTION-5-3)"
    return True, ""


def run_all_guardrails(
    ctx: RuleContext,
    action_type: str,
    risk_tier: str,
    campaign_id: Optional[str],
    change_pct: Optional[float],
    confidence: float,
    new_value_micros: Optional[float] = None,
    min_confidence: float = 0.5,
) -> Tuple[bool, Optional[str], List[str]]:
    """
    Run all applicable guardrails. Returns (passed, block_reason, guardrails_checked).
    """
    checked: List[str] = []
    lever = "budget" if "budget" in action_type else "bid" if "bid" in action_type else "other"

    checks = [
        ("low_data_block", lambda: check_low_data_block(ctx)),
        ("low_conv_bid_block", lambda: check_low_conversions_for_bid(ctx, action_type)),
        ("protected_entity", lambda: check_protected_entity(ctx, campaign_id, action_type)),
        ("confidence_threshold", lambda: check_confidence_threshold(confidence, min_confidence)),
        ("cooldown", lambda: check_cooldown(ctx, campaign_id, lever)),
        ("one_lever_rule", lambda: check_one_lever_rule(ctx, campaign_id, lever)),
    ]

    # Budget-specific checks
    if "budget" in action_type and change_pct is not None:
        checks.append(("budget_change_cap", lambda: check_budget_change_cap(change_pct, ctx.config.risk_tolerance)))
        checks.append(("daily_spend_cap", lambda: check_daily_spend_cap(ctx, new_value_micros)))
    if "increase" in action_type or "expand" in action_type:
        checks.append(("monthly_pacing", lambda: check_monthly_pacing(ctx)))

    # Bid-specific checks
    if "bid" in action_type and change_pct is not None:
        checks.append(("bid_change_cap", lambda: check_bid_change_cap(change_pct, ctx.config.risk_tolerance)))

    for name, check_fn in checks:
        passed, reason = check_fn()
        checked.append(name)
        if not passed:
            return False, reason, checked

    return True, None, checked
