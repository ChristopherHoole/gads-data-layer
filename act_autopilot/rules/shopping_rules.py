"""
Shopping product bid optimization rules.

Follows the same pattern as keyword_rules.py and ad_rules.py.
"""

from typing import List, Dict, Optional
from act_autopilot.models import Recommendation


def _safe_float(value) -> float:
    """Safely convert to float."""
    try:
        return float(value) if value is not None else 0.0
    except (ValueError, TypeError):
        return 0.0


def apply_rules(product_features: List[Dict], ctx) -> List[Recommendation]:
    """
    Apply shopping rules to product features.
    
    Args:
        product_features: List of product feature dicts from analytics.product_features_daily
        ctx: Rule context (not currently used but kept for consistency)
    
    Returns:
        List of Recommendation objects
    """
    recommendations = []
    
    for product in product_features:
        # Rule: High ROAS Product Bid Increase
        rec = _apply_shop_bid_001(product)
        if rec:
            recommendations.append(rec)
    
    return recommendations


def _apply_shop_bid_001(product: Dict) -> Optional[Recommendation]:
    """
    SHOP-BID-001: High ROAS Product Bid Increase
    
    Trigger: ROAS > 1.0 AND has clicks/cost data
    Action: Recommend +15% bid increase
    """
    # Extract data
    roas = _safe_float(product.get('roas_w30'))
    clicks = _safe_float(product.get('clicks_w30_sum'))
    cost_micros = _safe_float(product.get('cost_micros_w30_sum'))
    conversions = _safe_float(product.get('conversions_w30_sum'))
    
    # Rule trigger conditions
    if roas <= 1.0:
        return None
    if clicks <= 0 or cost_micros <= 0:
        return None
    
    # Calculate current bid from avg CPC
    avg_cpc_micros = cost_micros / clicks
    current_bid_dollars = avg_cpc_micros / 1_000_000
    
    # Skip if bid too low (unreliable)
    if current_bid_dollars <= 0:
        return None
    
    # Calculate recommended bid (+15% increase)
    recommended_bid_dollars = current_bid_dollars * 1.15
    
    # Build recommendation
    product_id = str(product.get('product_id', 'unknown'))
    
    return Recommendation(
        rule_id="SHOP-BID-001",
        rule_name="High ROAS Product Bid Increase",
        entity_type="product",
        entity_id=product_id,
        action_type="update_product_bid",
        risk_tier="low",
        confidence=0.85,
        current_value=current_bid_dollars,
        recommended_value=recommended_bid_dollars,
        change_pct=0.15,
        rationale=f"High ROAS ({roas:.2f}) indicates strong performance. Recommend +15% bid increase.",
        campaign_name=None,
        blocked=False,
        block_reason=None,
        priority=50,
        constitution_refs=[],
        guardrails_checked=[],
        evidence={
            "product_id": product_id,
            "product_title": product.get('product_title', ''),
            "ad_group_id": "unknown",  # Placeholder - synthetic data doesn't have this
            "roas_w30": roas,
            "clicks_w30": int(clicks),
            "conversions_w30": int(conversions),
            "cost_w30": cost_micros / 1_000_000,
            "avg_cpc_dollars": current_bid_dollars,
        },
        triggering_diagnosis="HIGH_ROAS_PRODUCT",
        triggering_confidence=0.85,
        expected_impact=f"Increase visibility for high-performing product (ROAS: {roas:.2f})",
    )
