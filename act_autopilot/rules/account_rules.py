"""
Account-Level Rules — Cross-campaign and account-wide optimization.

Rules:
  ACCT-001: Monthly pacing alert (soft warning)
  ACCT-002: Portfolio rebalance suggestion (shift budget from worst to best)
  ACCT-003: Account-wide low data warning
"""
from __future__ import annotations

from typing import List, Optional

from ..models import Recommendation, RuleContext, _safe_float


# ─────────────────────────────────────────────────────────────
# ACCT-001: Monthly Pacing Alert
# ─────────────────────────────────────────────────────────────
def acct_001_pacing_alert(ctx: RuleContext) -> Optional[Recommendation]:
    """
    Trigger: PACE_OVER_CAP insight exists but pacing between 100-105%
             (i.e. approaching cap but not yet breached)
    Action:  Alert — suggest reviewing expansion plans
    Risk:    med
    
    NOTE: If pacing is >105%, BUDGET-005 handles the hard cut. This is the early warning.
    """
    # Check account-level pacing from features
    pacing_pct = _safe_float(ctx.features.get("acct_pacing_vs_cap_pct"))
    monthly_cap = _safe_float(ctx.features.get("acct_monthly_cap_micros"))

    if monthly_cap <= 0:
        return None

    # Alert zone: projected 100-105% of cap (not yet at the hard >105% flag)
    if pacing_pct < 0.0 or pacing_pct >= 0.05:
        return None  # either under cap or already in BUDGET-005 territory

    projected = _safe_float(ctx.features.get("acct_projected_month_cost_micros"))

    return Recommendation(
        rule_id="ACCT-001",
        rule_name="Monthly Pacing Alert — Approaching Cap",
        entity_type="ACCOUNT",
        entity_id=None,
        action_type="review",
        risk_tier="med",
        confidence=0.70,
        current_value=projected,
        recommended_value=monthly_cap,
        change_pct=pacing_pct,
        rationale=f"Account is pacing {pacing_pct:+.1%} over monthly cap. "
                  f"Not critical yet, but review planned expansions and pause any non-essential increases.",
        evidence={
            "acct_pacing_vs_cap_pct": pacing_pct,
            "acct_projected_month_cost_micros": projected,
            "acct_monthly_cap_micros": monthly_cap,
        },
        constitution_refs=["CONSTITUTION-5-5"],
        guardrails_checked=["monthly_pacing_check"],
        triggering_diagnosis="PACING_APPROACHING_CAP",
        triggering_confidence=0.70,
        blocked=False,
        block_reason=None,
        priority=10,
    )


# ─────────────────────────────────────────────────────────────
# ACCT-002: Portfolio Rebalance Suggestion
# ─────────────────────────────────────────────────────────────
def acct_002_portfolio_rebalance(ctx: RuleContext) -> Optional[Recommendation]:
    """
    Trigger: ≥2 campaigns with sufficient data AND significant ROAS spread
             (best campaign ROAS > 2x worst campaign ROAS)
    Action:  Suggest shifting budget from worst to best
    Risk:    med (cross-campaign, judgment required)
    
    This rule fires ONCE per account (on the worst-performing campaign).
    """
    if ctx.config.primary_kpi != "roas" or ctx.config.target_roas is None:
        return None

    # Collect campaigns with sufficient data
    eligible: List[dict] = []
    for f in ctx.all_features:
        clicks = _safe_float(f.get("clicks_w7_sum"))
        conv = _safe_float(f.get("conversions_w30_sum"))
        roas = _safe_float(f.get("roas_w7_mean"))
        if clicks >= 30 and conv >= 15 and roas > 0:
            eligible.append(f)

    if len(eligible) < 2:
        return None

    # Sort by ROAS
    eligible.sort(key=lambda f: _safe_float(f.get("roas_w7_mean")))
    worst = eligible[0]
    best = eligible[-1]

    worst_roas = _safe_float(worst.get("roas_w7_mean"))
    best_roas = _safe_float(best.get("roas_w7_mean"))

    # Only fire if meaningful spread (best > 2x worst)
    if best_roas < worst_roas * 2.0:
        return None

    # Only fire on the worst campaign
    campaign_id = str(ctx.features.get("campaign_id"))
    worst_id = str(worst.get("campaign_id"))
    if campaign_id != worst_id:
        return None

    worst_cost = _safe_float(worst.get("cost_micros_w7_sum"))
    best_cost = _safe_float(best.get("cost_micros_w7_sum"))

    return Recommendation(
        rule_id="ACCT-002",
        rule_name="Portfolio Rebalance — Shift Budget to Top Performer",
        entity_type="ACCOUNT",
        entity_id=None,
        action_type="review",
        risk_tier="med",
        confidence=0.55,
        current_value=None,
        recommended_value=None,
        change_pct=None,
        rationale=f"ROAS spread: best campaign ({str(best.get('campaign_id'))}) at {best_roas:.2f} vs "
                  f"worst campaign ({worst_id}) at {worst_roas:.2f} (ratio {best_roas/worst_roas:.1f}x). "
                  f"Consider shifting budget from worst to best.",
        evidence={
            "best_campaign_id": str(best.get("campaign_id")),
            "best_roas_w7": best_roas,
            "best_cost_w7_micros": best_cost,
            "worst_campaign_id": worst_id,
            "worst_roas_w7": worst_roas,
            "worst_cost_w7_micros": worst_cost,
            "roas_ratio": best_roas / worst_roas if worst_roas > 0 else None,
            "eligible_campaigns": len(eligible),
        },
        constitution_refs=["CONSTITUTION-4", "CONSTITUTION-5-4"],
        guardrails_checked=["cross_campaign_review"],
        triggering_diagnosis="PORTFOLIO_IMBALANCE",
        triggering_confidence=0.55,
        blocked=False,
        block_reason=None,
        priority=50,
    )


# ─────────────────────────────────────────────────────────────
# ACCT-003: Account-Wide Low Data Warning
# ─────────────────────────────────────────────────────────────
def acct_003_low_data_warning(ctx: RuleContext) -> Optional[Recommendation]:
    """
    Trigger: >50% of campaigns have low_data_flag=True
    Action:  Warning — account needs more data before meaningful optimization
    Risk:    low
    
    Only fires once (on first campaign processed).
    """
    if not ctx.all_features:
        return None

    # Only fire once — check if this is first campaign by ID
    campaign_id = str(ctx.features.get("campaign_id"))
    first_id = str(ctx.all_features[0].get("campaign_id"))
    if campaign_id != first_id:
        return None

    total = len(ctx.all_features)
    low_data_count = sum(1 for f in ctx.all_features if f.get("low_data_flag") is True)

    if total == 0 or (low_data_count / total) <= 0.50:
        return None

    return Recommendation(
        rule_id="ACCT-003",
        rule_name="Account-Wide Low Data Warning",
        entity_type="ACCOUNT",
        entity_id=None,
        action_type="review",
        risk_tier="low",
        confidence=0.80,
        current_value=None,
        recommended_value=None,
        change_pct=None,
        rationale=f"{low_data_count}/{total} campaigns ({low_data_count/total:.0%}) have low data. "
                  f"Account-wide optimization is limited until more data accumulates.",
        evidence={
            "total_campaigns": total,
            "low_data_campaigns": low_data_count,
            "low_data_pct": low_data_count / total,
        },
        constitution_refs=["CONSTITUTION-5-2", "CONSTITUTION-A-4"],
        guardrails_checked=["low_data_assessment"],
        triggering_diagnosis="ACCOUNT_LOW_DATA",
        triggering_confidence=0.80,
        blocked=False,
        block_reason=None,
        priority=55,
    )


# Registry
ACCOUNT_RULES = [
    acct_001_pacing_alert,
    acct_002_portfolio_rebalance,
    acct_003_low_data_warning,
]
