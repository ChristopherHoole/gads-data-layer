"""
Shopping & Product Rules — Product-level optimization.

Rules (14 total):
  SHOP-BID-001:     Increase bids for high-ROAS products
  SHOP-BID-002:     Decrease bids for low-ROAS products
  SHOP-PAUSE-001:   Pause/exclude low-ROAS products
  SHOP-SCALE-001:   Increase campaign budget for winners

  SHOP-FEED-001:    Fix out-of-stock products
  SHOP-FEED-002:    Fix price mismatches
  SHOP-FEED-003:    Fix disapproved products
  SHOP-FEED-004:    Add missing attributes

  SHOP-PRODUCT-001: Identify best sellers
  SHOP-PRODUCT-002: Flag seasonal products
  SHOP-PRODUCT-003: New product launch monitoring
  SHOP-PRIORITY-001: Campaign priority conflicts

  SHOP-NEG-001:     Exclude chronic underperformers
  SHOP-NEG-002:     Exclude out-of-stock products automatically

Constitution references:
  CONSTITUTION-5-2:  Low data gates
  CONSTITUTION-SHOP-1: Stock status check
  CONSTITUTION-SHOP-2: Feed quality gate
"""

from __future__ import annotations

from typing import Dict, Any, List, Optional

from ..models import Recommendation, RuleContext, _safe_float


def _target_roas(config) -> float:
    """Get target ROAS from config (e.g., 3.0)"""
    raw = _safe_float(config.target_roas)
    return raw if raw > 0 else 0.0


# ═══════════════════════════════════════════════════════════════
# SHOPPING BID & BUDGET RULES
# ═══════════════════════════════════════════════════════════════

def shop_bid_001_high_roas_scale(ctx: RuleContext) -> Optional[Recommendation]:
    """
    Trigger: ROAS >1.5x target AND lost impression share >20%
    Action:  Recommend +15% bid at product group level
    Risk:    low
    """
    target_roas = _target_roas(ctx.config)
    if target_roas <= 0:
        return None

    roas_w30 = _safe_float(ctx.features.get("roas_w30"))
    conv_w30 = _safe_float(ctx.features.get("conversions_w30_sum"))
    cost_w30 = _safe_float(ctx.features.get("cost_micros_w30_sum"))
    
    if roas_w30 <= 0 or conv_w30 < 5:
        return None

    roas_ratio = roas_w30 / target_roas
    
    if roas_ratio <= 1.5:
        return None

    # Higher confidence with more conversions
    confidence = min(1.0, 0.60 + 0.20 * min(1.0, conv_w30 / 20))

    product_id = str(ctx.features.get("product_id"))
    product_title = ctx.features.get("product_title", "")
    
    return Recommendation(
        rule_id="SHOP-BID-001",
        rule_name="Increase Bids — High ROAS Product",
        entity_type="PRODUCT",
        entity_id=product_id,
        action_type="product_bid_increase",
        risk_tier="low",
        confidence=confidence,
        current_value=None,
        recommended_value="+15%",
        change_pct=15.0,
        rationale=(
            f"Product '{product_title}' has ROAS of {roas_w30:.2f} "
            f"({roas_ratio:.1f}x target). Strong performer - increase bids to capture more volume."
        ),
        evidence={
            "product_id": product_id,
            "product_title": product_title,
            "roas_w30": round(roas_w30, 2),
            "target_roas": target_roas,
            "roas_ratio": round(roas_ratio, 2),
            "conversions_w30": conv_w30,
            "cost_w30_dollars": cost_w30 / 1_000_000,
        },
        constitution_refs=["CONSTITUTION-5-2"],
        guardrails_checked=[],
        triggering_diagnosis="SHOPPING_WINNER",
        triggering_confidence=confidence,
        blocked=False,
        block_reason=None,
        priority=20,
    )


def shop_bid_002_low_roas_reduce(ctx: RuleContext) -> Optional[Recommendation]:
    """
    Trigger: ROAS <0.5x target AND >=20 conversions (30d)
    Action:  Recommend -15% bid
    Risk:    low
    """
    target_roas = _target_roas(ctx.config)
    if target_roas <= 0:
        return None

    roas_w30 = _safe_float(ctx.features.get("roas_w30"))
    conv_w30 = _safe_float(ctx.features.get("conversions_w30_sum"))
    cost_w30 = _safe_float(ctx.features.get("cost_micros_w30_sum"))
    
    if roas_w30 <= 0 or conv_w30 < 20:
        return None

    roas_ratio = roas_w30 / target_roas
    
    if roas_ratio >= 0.5:
        return None

    confidence = min(1.0, 0.65 + 0.20 * min(1.0, conv_w30 / 50))

    product_id = str(ctx.features.get("product_id"))
    product_title = ctx.features.get("product_title", "")
    
    return Recommendation(
        rule_id="SHOP-BID-002",
        rule_name="Decrease Bids — Low ROAS Product",
        entity_type="PRODUCT",
        entity_id=product_id,
        action_type="product_bid_decrease",
        risk_tier="low",
        confidence=confidence,
        current_value=None,
        recommended_value="-15%",
        change_pct=-15.0,
        rationale=(
            f"Product '{product_title}' has ROAS of {roas_w30:.2f} "
            f"({roas_ratio:.1%} of target). Reduce bids to improve efficiency."
        ),
        evidence={
            "product_id": product_id,
            "product_title": product_title,
            "roas_w30": round(roas_w30, 2),
            "target_roas": target_roas,
            "roas_ratio": round(roas_ratio, 2),
            "conversions_w30": conv_w30,
            "cost_w30_dollars": cost_w30 / 1_000_000,
        },
        constitution_refs=["CONSTITUTION-5-2"],
        guardrails_checked=[],
        triggering_diagnosis="SHOPPING_LOW_ROAS",
        triggering_confidence=confidence,
        blocked=False,
        block_reason=None,
        priority=15,
    )


def shop_pause_001_extreme_underperformer(ctx: RuleContext) -> Optional[Recommendation]:
    """
    Trigger: ROAS <0.3x target AND cost >$100 (30d)
    Action:  Exclude product from campaign
    Risk:    med
    """
    target_roas = _target_roas(ctx.config)
    if target_roas <= 0:
        return None

    roas_w30 = _safe_float(ctx.features.get("roas_w30"))
    cost_w30 = _safe_float(ctx.features.get("cost_micros_w30_sum"))
    conv_w30 = _safe_float(ctx.features.get("conversions_w30_sum"))
    
    cost_w30_dollars = cost_w30 / 1_000_000
    
    if cost_w30_dollars < 100:
        return None
    
    if roas_w30 <= 0:
        return None

    roas_ratio = roas_w30 / target_roas
    
    if roas_ratio >= 0.3:
        return None

    confidence = min(1.0, 0.70 + 0.15 * min(1.0, cost_w30_dollars / 500))

    product_id = str(ctx.features.get("product_id"))
    product_title = ctx.features.get("product_title", "")
    
    return Recommendation(
        rule_id="SHOP-PAUSE-001",
        rule_name="Exclude Product — Extreme Underperformer",
        entity_type="PRODUCT",
        entity_id=product_id,
        action_type="product_exclude",
        risk_tier="med",
        confidence=confidence,
        current_value=None,
        recommended_value="EXCLUDED",
        change_pct=None,
        rationale=(
            f"Product '{product_title}' has ROAS of {roas_w30:.2f} "
            f"({roas_ratio:.1%} of target) with ${cost_w30_dollars:.0f} spent in 30d. "
            f"Extreme underperformer - exclude from campaign."
        ),
        evidence={
            "product_id": product_id,
            "product_title": product_title,
            "roas_w30": round(roas_w30, 2),
            "target_roas": target_roas,
            "roas_ratio": round(roas_ratio, 2),
            "conversions_w30": conv_w30,
            "cost_w30_dollars": round(cost_w30_dollars, 2),
        },
        constitution_refs=["CONSTITUTION-5-2"],
        guardrails_checked=[],
        triggering_diagnosis="SHOPPING_LOW_ROAS",
        triggering_confidence=confidence,
        blocked=False,
        block_reason=None,
        priority=25,
    )


def shop_scale_001_campaign_budget_increase(ctx: RuleContext) -> Optional[Recommendation]:
    """
    Trigger: Campaign ROAS >1.3x target AND lost IS budget >15%
    Action:  +10% campaign budget
    Risk:    low
    """
    target_roas = _target_roas(ctx.config)
    if target_roas <= 0:
        return None

    # This would need campaign-level aggregation
    # For now, flag high-performing products for campaign-level review
    roas_w30 = _safe_float(ctx.features.get("roas_w30"))
    conv_w30 = _safe_float(ctx.features.get("conversions_w30_sum"))
    
    if roas_w30 <= 0 or conv_w30 < 10:
        return None

    roas_ratio = roas_w30 / target_roas
    
    if roas_ratio <= 1.3:
        return None

    # This is informational - actual budget increase needs campaign-level data
    confidence = 0.50

    product_id = str(ctx.features.get("product_id"))
    campaign_id = str(ctx.features.get("campaign_id"))
    
    return Recommendation(
        rule_id="SHOP-SCALE-001",
        rule_name="Flag for Budget Increase — Campaign Winner",
        entity_type="CAMPAIGN",
        entity_id=campaign_id,
        action_type="campaign_budget_increase",
        risk_tier="low",
        confidence=confidence,
        current_value=None,
        recommended_value="+10%",
        change_pct=10.0,
        rationale=(
            f"Product performing at {roas_ratio:.1f}x target ROAS. "
            f"Review campaign for budget increase opportunity."
        ),
        evidence={
            "campaign_id": campaign_id,
            "product_id": product_id,
            "roas_w30": round(roas_w30, 2),
            "conversions_w30": conv_w30,
        },
        constitution_refs=[],
        guardrails_checked=[],
        triggering_diagnosis="SHOPPING_WINNER",
        triggering_confidence=confidence,
        blocked=False,
        block_reason=None,
        priority=10,
    )


# ═══════════════════════════════════════════════════════════════
# FEED QUALITY RULES
# ═══════════════════════════════════════════════════════════════

def shop_feed_001_fix_out_of_stock(ctx: RuleContext) -> Optional[Recommendation]:
    """
    Trigger: Product out of stock, still getting clicks
    Action:  Flag to update feed or pause product
    Risk:    high (revenue impact)
    """
    stock_out_flag = ctx.features.get("stock_out_flag", False)
    clicks_w30 = _safe_float(ctx.features.get("clicks_w30_sum"))
    cost_w30 = _safe_float(ctx.features.get("cost_micros_w30_sum"))
    stock_out_days = _safe_float(ctx.features.get("stock_out_days_w30"))
    
    if not stock_out_flag or clicks_w30 < 5:
        return None

    confidence = min(1.0, 0.85 + 0.10 * min(1.0, stock_out_days / 14))

    product_id = str(ctx.features.get("product_id"))
    product_title = ctx.features.get("product_title", "")
    
    return Recommendation(
        rule_id="SHOP-FEED-001",
        rule_name="Fix Feed — Out of Stock Product",
        entity_type="PRODUCT",
        entity_id=product_id,
        action_type="feed_fix_stock",
        risk_tier="high",
        confidence=confidence,
        current_value="OUT_OF_STOCK",
        recommended_value="Update feed or pause",
        change_pct=None,
        rationale=(
            f"Product '{product_title}' is out of stock but still receiving clicks. "
            f"Out of stock for {stock_out_days:.0f} days in last 30d. "
            f"Wasting ${cost_w30 / 1_000_000:.0f} on clicks that can't convert."
        ),
        evidence={
            "product_id": product_id,
            "product_title": product_title,
            "stock_out_days_w30": stock_out_days,
            "clicks_w30": clicks_w30,
            "cost_w30_dollars": cost_w30 / 1_000_000,
        },
        constitution_refs=["CONSTITUTION-SHOP-1"],
        guardrails_checked=["stock_status"],
        triggering_diagnosis="SHOPPING_OUT_OF_STOCK",
        triggering_confidence=confidence,
        blocked=False,
        block_reason=None,
        priority=50,
    )


def shop_feed_002_fix_price_mismatch(ctx: RuleContext) -> Optional[Recommendation]:
    """
    Trigger: Feed price ≠ landing page (detected by Google)
    Action:  Flag for feed correction
    Risk:    high (policy violation)
    """
    has_price_mismatch = ctx.features.get("has_price_mismatch", False)
    cost_w30 = _safe_float(ctx.features.get("cost_micros_w30_sum"))
    
    if not has_price_mismatch or cost_w30 <= 0:
        return None

    confidence = 0.95  # Google detected it - very high confidence

    product_id = str(ctx.features.get("product_id"))
    product_title = ctx.features.get("product_title", "")
    
    return Recommendation(
        rule_id="SHOP-FEED-002",
        rule_name="Fix Feed — Price Mismatch",
        entity_type="PRODUCT",
        entity_id=product_id,
        action_type="feed_fix_price",
        risk_tier="high",
        confidence=confidence,
        current_value="PRICE_MISMATCH",
        recommended_value="Fix feed price",
        change_pct=None,
        rationale=(
            f"Product '{product_title}' has price mismatch between feed and landing page. "
            f"CRITICAL: Policy violation can lead to account suspension. Fix immediately."
        ),
        evidence={
            "product_id": product_id,
            "product_title": product_title,
            "has_price_mismatch": True,
            "cost_w30_dollars": cost_w30 / 1_000_000,
        },
        constitution_refs=["CONSTITUTION-SHOP-2"],
        guardrails_checked=["feed_quality"],
        triggering_diagnosis="SHOPPING_PRICE_MISMATCH",
        triggering_confidence=confidence,
        blocked=False,
        block_reason=None,
        priority=100,
    )


def shop_feed_003_fix_disapproved(ctx: RuleContext) -> Optional[Recommendation]:
    """
    Trigger: Product disapproved in Merchant Center
    Action:  Review disapproval reason, fix attribute
    Risk:    high
    """
    has_disapproval = ctx.features.get("has_disapproval", False)
    
    if not has_disapproval:
        return None

    confidence = 0.95

    product_id = str(ctx.features.get("product_id"))
    product_title = ctx.features.get("product_title", "")
    
    return Recommendation(
        rule_id="SHOP-FEED-003",
        rule_name="Fix Feed — Disapproved Product",
        entity_type="PRODUCT",
        entity_id=product_id,
        action_type="feed_fix_disapproval",
        risk_tier="high",
        confidence=confidence,
        current_value="DISAPPROVED",
        recommended_value="Review & fix in Merchant Center",
        change_pct=None,
        rationale=(
            f"Product '{product_title}' is disapproved in Merchant Center. "
            f"Review disapproval reasons and fix feed issues immediately."
        ),
        evidence={
            "product_id": product_id,
            "product_title": product_title,
            "has_disapproval": True,
        },
        constitution_refs=["CONSTITUTION-SHOP-2"],
        guardrails_checked=["feed_quality"],
        triggering_diagnosis="SHOPPING_DISAPPROVED",
        triggering_confidence=confidence,
        blocked=False,
        block_reason=None,
        priority=95,
    )


def shop_feed_004_add_missing_attrs(ctx: RuleContext) -> Optional[Recommendation]:
    """
    Trigger: Product approved but missing optional attributes (GTIN, brand)
    Action:  Enhance feed quality
    Risk:    low
    """
    feed_quality_score = _safe_float(ctx.features.get("feed_quality_score"))
    has_disapproval = ctx.features.get("has_disapproval", False)
    
    if has_disapproval or feed_quality_score >= 0.8:
        return None

    confidence = 0.60

    product_id = str(ctx.features.get("product_id"))
    product_title = ctx.features.get("product_title", "")
    
    return Recommendation(
        rule_id="SHOP-FEED-004",
        rule_name="Enhance Feed — Missing Attributes",
        entity_type="PRODUCT",
        entity_id=product_id,
        action_type="feed_enhance",
        risk_tier="low",
        confidence=confidence,
        current_value=f"{feed_quality_score:.0%}",
        recommended_value="Add optional attributes",
        change_pct=None,
        rationale=(
            f"Product '{product_title}' has feed quality score of {feed_quality_score:.0%}. "
            f"Add optional attributes (GTIN, brand, MPN) to improve performance."
        ),
        evidence={
            "product_id": product_id,
            "product_title": product_title,
            "feed_quality_score": round(feed_quality_score, 2),
        },
        constitution_refs=[],
        guardrails_checked=[],
        triggering_diagnosis="SHOPPING_MISSING_ATTRS",
        triggering_confidence=confidence,
        blocked=False,
        block_reason=None,
        priority=5,
    )


# ═══════════════════════════════════════════════════════════════
# PRODUCT STRATEGY RULES
# ═══════════════════════════════════════════════════════════════

def shop_product_001_best_sellers(ctx: RuleContext) -> Optional[Recommendation]:
    """
    Trigger: Product ROAS >campaign avg × 1.5, high volume
    Action:  Flag for inventory increase, more budget
    Risk:    low (informational)
    """
    roas_w30 = _safe_float(ctx.features.get("roas_w30"))
    conv_w30 = _safe_float(ctx.features.get("conversions_w30_sum"))
    target_roas = _target_roas(ctx.config)
    
    if target_roas <= 0 or roas_w30 <= 0 or conv_w30 < 15:
        return None

    roas_ratio = roas_w30 / target_roas
    
    if roas_ratio <= 1.8:
        return None

    confidence = 0.55

    product_id = str(ctx.features.get("product_id"))
    product_title = ctx.features.get("product_title", "")
    
    return Recommendation(
        rule_id="SHOP-PRODUCT-001",
        rule_name="Best Seller — Scale Opportunity",
        entity_type="PRODUCT",
        entity_id=product_id,
        action_type="product_review",
        risk_tier="low",
        confidence=confidence,
        current_value=f"{roas_w30:.2f}",
        recommended_value="Increase inventory/budget",
        change_pct=None,
        rationale=(
            f"Product '{product_title}' is a top performer with ROAS of {roas_w30:.2f} "
            f"({roas_ratio:.1f}x target). Consider increasing inventory and budget allocation."
        ),
        evidence={
            "product_id": product_id,
            "product_title": product_title,
            "roas_w30": round(roas_w30, 2),
            "conversions_w30": conv_w30,
        },
        constitution_refs=[],
        guardrails_checked=[],
        triggering_diagnosis="SHOPPING_WINNER",
        triggering_confidence=confidence,
        blocked=False,
        block_reason=None,
        priority=8,
    )


def shop_product_002_seasonal(ctx: RuleContext) -> Optional[Recommendation]:
    """
    Trigger: Product shows clear seasonal pattern (placeholder)
    Action:  Adjust bids based on season
    Risk:    low
    """
    # This would require time-series analysis - placeholder for now
    return None


def shop_product_003_new_product_monitoring(ctx: RuleContext) -> Optional[Recommendation]:
    """
    Trigger: Product <30 days old
    Action:  Monitor closely, report early performance
    Risk:    low (review only)
    """
    new_product_flag = ctx.features.get("new_product_flag", False)
    days_live = _safe_float(ctx.features.get("days_live"))
    
    if not new_product_flag or days_live > 30:
        return None

    roas_w7 = _safe_float(ctx.features.get("roas_w7"))
    conv_w7 = _safe_float(ctx.features.get("conversions_w7_sum"))
    
    confidence = 0.45

    product_id = str(ctx.features.get("product_id"))
    product_title = ctx.features.get("product_title", "")
    
    return Recommendation(
        rule_id="SHOP-PRODUCT-003",
        rule_name="New Product — Monitor Performance",
        entity_type="PRODUCT",
        entity_id=product_id,
        action_type="product_review",
        risk_tier="low",
        confidence=confidence,
        current_value=f"{days_live:.0f} days live",
        recommended_value="Monitor closely",
        change_pct=None,
        rationale=(
            f"Product '{product_title}' is new ({days_live:.0f} days live). "
            f"Early performance: ROAS {roas_w7:.2f}, {conv_w7:.0f} conversions in 7d."
        ),
        evidence={
            "product_id": product_id,
            "product_title": product_title,
            "days_live": days_live,
            "roas_w7": round(roas_w7, 2),
            "conversions_w7": conv_w7,
        },
        constitution_refs=[],
        guardrails_checked=[],
        triggering_diagnosis=None,
        triggering_confidence=confidence,
        blocked=False,
        block_reason=None,
        priority=3,
    )


def shop_priority_001_campaign_priority_conflicts(ctx: RuleContext) -> Optional[Recommendation]:
    """
    Trigger: Multiple campaigns targeting same products with wrong priorities
    Action:  Recommend priority adjustment
    Risk:    med (placeholder - needs multi-campaign analysis)
    """
    # This requires cross-campaign analysis - placeholder
    return None


# ═══════════════════════════════════════════════════════════════
# NEGATIVE PRODUCT RULES
# ═══════════════════════════════════════════════════════════════

def shop_neg_001_chronic_underperformer(ctx: RuleContext) -> Optional[Recommendation]:
    """
    Trigger: Product ROAS <0.5 for 90+ days, cost >$200
    Action:  Permanently exclude product
    Risk:    med
    """
    roas_w90 = _safe_float(ctx.features.get("roas_w90"))
    cost_w90 = _safe_float(ctx.features.get("cost_micros_w90_sum"))
    target_roas = _target_roas(ctx.config)
    
    if target_roas <= 0 or roas_w90 <= 0:
        return None

    cost_w90_dollars = cost_w90 / 1_000_000
    
    if cost_w90_dollars < 200:
        return None

    roas_ratio = roas_w90 / target_roas
    
    if roas_ratio >= 0.5:
        return None

    confidence = min(1.0, 0.75 + 0.15 * min(1.0, cost_w90_dollars / 1000))

    product_id = str(ctx.features.get("product_id"))
    product_title = ctx.features.get("product_title", "")
    
    return Recommendation(
        rule_id="SHOP-NEG-001",
        rule_name="Exclude Product — Chronic Underperformer",
        entity_type="PRODUCT",
        entity_id=product_id,
        action_type="product_exclude",
        risk_tier="med",
        confidence=confidence,
        current_value=f"{roas_w90:.2f}",
        recommended_value="EXCLUDED",
        change_pct=None,
        rationale=(
            f"Product '{product_title}' has ROAS of {roas_w90:.2f} "
            f"({roas_ratio:.1%} of target) over 90 days with ${cost_w90_dollars:.0f} spent. "
            f"Chronic underperformer - permanently exclude."
        ),
        evidence={
            "product_id": product_id,
            "product_title": product_title,
            "roas_w90": round(roas_w90, 2),
            "target_roas": target_roas,
            "cost_w90_dollars": round(cost_w90_dollars, 2),
        },
        constitution_refs=["CONSTITUTION-5-2"],
        guardrails_checked=[],
        triggering_diagnosis="SHOPPING_LOW_ROAS",
        triggering_confidence=confidence,
        blocked=False,
        block_reason=None,
        priority=30,
    )


def shop_neg_002_auto_exclude_oos(ctx: RuleContext) -> Optional[Recommendation]:
    """
    Trigger: Product out of stock >14 days
    Action:  Exclude until back in stock
    Risk:    low
    """
    stock_out_days = _safe_float(ctx.features.get("stock_out_days_w30"))
    
    if stock_out_days < 14:
        return None

    confidence = 0.90

    product_id = str(ctx.features.get("product_id"))
    product_title = ctx.features.get("product_title", "")
    
    return Recommendation(
        rule_id="SHOP-NEG-002",
        rule_name="Auto-Exclude — Extended Out of Stock",
        entity_type="PRODUCT",
        entity_id=product_id,
        action_type="product_exclude",
        risk_tier="low",
        confidence=confidence,
        current_value=f"{stock_out_days:.0f} days OOS",
        recommended_value="EXCLUDED (auto-resume when in stock)",
        change_pct=None,
        rationale=(
            f"Product '{product_title}' has been out of stock for {stock_out_days:.0f} days. "
            f"Automatically exclude until inventory restored."
        ),
        evidence={
            "product_id": product_id,
            "product_title": product_title,
            "stock_out_days_w30": stock_out_days,
        },
        constitution_refs=["CONSTITUTION-SHOP-1"],
        guardrails_checked=["stock_status"],
        triggering_diagnosis="SHOPPING_OUT_OF_STOCK",
        triggering_confidence=confidence,
        blocked=False,
        block_reason=None,
        priority=40,
    )


# ═══════════════════════════════════════════════════════════════
# MAIN RULE RUNNER
# ═══════════════════════════════════════════════════════════════

def generate_shopping_recommendations(ctx: RuleContext) -> List[Recommendation]:
    """Generate all Shopping recommendations for a product"""
    
    rules = [
        shop_bid_001_high_roas_scale,
        shop_bid_002_low_roas_reduce,
        shop_pause_001_extreme_underperformer,
        shop_scale_001_campaign_budget_increase,
        shop_feed_001_fix_out_of_stock,
        shop_feed_002_fix_price_mismatch,
        shop_feed_003_fix_disapproved,
        shop_feed_004_add_missing_attrs,
        shop_product_001_best_sellers,
        shop_product_003_new_product_monitoring,
        shop_neg_001_chronic_underperformer,
        shop_neg_002_auto_exclude_oos,
    ]
    
    recommendations = []
    for rule_func in rules:
        rec = rule_func(ctx)
        if rec:
            recommendations.append(rec)
    
    return recommendations
