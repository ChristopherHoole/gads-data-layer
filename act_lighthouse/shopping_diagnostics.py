from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Dict, List, Optional

import duckdb

from .config import ClientConfig
from .diagnostics import Insight, _clamp01, _cap_low_data

# Constitution rule IDs
RULE_LOW_DATA_GATES = "CONSTITUTION-5-2"
RULE_LOW_DATA_APPENDIX = "CONSTITUTION-A-4"
RULE_SHOPPING_STOCK_GATE = "CONSTITUTION-SHOP-1"
RULE_SHOPPING_FEED_GATE = "CONSTITUTION-SHOP-2"


# ── Product-level diagnostics ────────────────────────────────────────

def _score_product_volume(clicks_w7: float, conv_w30: float) -> float:
    """Volume confidence score for products."""
    clicks_score = _clamp01((clicks_w7 - 3.0) / 27.0)   # 3->0, 30->1
    conv_score = _clamp01(conv_w30 / 10.0)               # 10 conv -> 1
    return 0.60 * clicks_score + 0.40 * conv_score


def run_product_diagnostics(
    row: Dict[str, Any],
    target_cpa_micros: Optional[float],
    target_roas: Optional[float],
    protected_campaign_ids: List[str],
) -> List[Insight]:
    """
    Generate product-level insights from a product_features_daily row.

    Args:
        row: One row from analytics.product_features_daily
        target_cpa_micros: Client target CPA in micros (e.g., 25_000_000 = $25)
        target_roas: Client target ROAS (e.g., 3.0)
        protected_campaign_ids: List of protected campaign IDs
    """
    insights: List[Insight] = []

    product_id = str(row.get("product_id", ""))
    campaign_id = str(row.get("campaign_id", ""))
    product_title = str(row.get("product_title", ""))
    product_brand = str(row.get("product_brand", ""))
    availability = str(row.get("availability", ""))

    # Skip protected campaigns
    if campaign_id in set(protected_campaign_ids):
        return insights

    low_data_flag = bool(row.get("low_data_flag", False))
    stock_out_flag = bool(row.get("stock_out_flag", False))
    has_disapproval = bool(row.get("has_disapproval", False))
    has_price_mismatch = bool(row.get("has_price_mismatch", False))
    feed_quality_score = float(row.get("feed_quality_score") or 0.5)
    new_product_flag = bool(row.get("new_product_flag", False))

    clicks_w7 = float(row.get("clicks_w7_sum") or 0)
    clicks_w30 = float(row.get("clicks_w30_sum") or 0)
    conv_w30 = float(row.get("conversions_w30_sum") or 0)
    cost_w30 = float(row.get("cost_micros_w30_sum") or 0)
    cost_w90 = float(row.get("cost_micros_w90_sum") or 0)
    conv_w90 = float(row.get("conversions_w90_sum") or 0)
    impr_w7 = float(row.get("impressions_w7_sum") or 0)
    impr_w30 = float(row.get("impressions_w30_sum") or 0)
    stock_out_days = int(row.get("stock_out_days_w30") or 0)

    cpa_w30 = float(row.get("cpa_w30") or 0)
    roas_w30 = float(row.get("roas_w30") or 0)
    roas_w90 = float(row.get("roas_w90") or 0)
    ctr_w30 = float(row.get("ctr_w30") or 0)

    volume = _score_product_volume(clicks_w7, conv_w30)
    base_labels: List[str] = []
    base_guardrails: List[str] = []

    if low_data_flag:
        base_labels.append("LOW_DATA")
        base_guardrails.extend([RULE_LOW_DATA_GATES, RULE_LOW_DATA_APPENDIX])

    if new_product_flag:
        base_labels.append("NEW_PRODUCT")

    # ── SHOPPING_OUT_OF_STOCK ────────────────────────────────────
    # Product out of stock, still spending
    if stock_out_flag and cost_w30 > 0 and clicks_w30 > 5:
        conf = _clamp01(0.80 + 0.10 * min(1.0, stock_out_days / 14.0))
        insights.append(Insight(
            insight_rank=0,
            entity_type="PRODUCT",
            entity_id=product_id,
            diagnosis_code="SHOPPING_OUT_OF_STOCK",
            confidence=conf,
            risk_tier="high",
            labels=sorted(set(base_labels + ["OUT_OF_STOCK", "WASTED_SPEND"])),
            evidence={
                "product_id": product_id,
                "product_title": product_title,
                "product_brand": product_brand,
                "availability": availability,
                "stock_out_days_w30": stock_out_days,
                "cost_w30": cost_w30 / 1_000_000,
                "clicks_w30": clicks_w30,
                "conversions_w30": conv_w30,
            },
            recommended_action=(
                f"Product out of stock for {stock_out_days} days in last 30d. "
                f"Pause or exclude product immediately to stop wasted spend. "
                f"Update feed when back in stock."
            ),
            guardrail_rule_ids=sorted(set(base_guardrails + [RULE_SHOPPING_STOCK_GATE])),
        ))

    # ── SHOPPING_PRICE_MISMATCH ──────────────────────────────────
    # Feed price ≠ landing page price
    if has_price_mismatch and cost_w30 > 0:
        conf = 0.90  # High confidence - Google detected it
        insights.append(Insight(
            insight_rank=0,
            entity_type="PRODUCT",
            entity_id=product_id,
            diagnosis_code="SHOPPING_PRICE_MISMATCH",
            confidence=conf,
            risk_tier="high",
            labels=sorted(set(base_labels + ["PRICE_MISMATCH", "POLICY_RISK"])),
            evidence={
                "product_id": product_id,
                "product_title": product_title,
                "product_brand": product_brand,
                "has_price_mismatch": True,
                "feed_quality_score": feed_quality_score,
            },
            recommended_action=(
                f"Price mismatch detected between feed and landing page. "
                f"Fix feed immediately - policy violation can lead to account suspension."
            ),
            guardrail_rule_ids=sorted(set(base_guardrails + [RULE_SHOPPING_FEED_GATE])),
        ))

    # ── SHOPPING_LOW_ROAS ─────────────────────────────────────────
    # Product ROAS < target
    if target_roas and target_roas > 0 and roas_w30 > 0 and conv_w30 >= 5:
        roas_ratio = roas_w30 / target_roas
        if roas_ratio < 0.7:
            conf = _cap_low_data(
                _clamp01(0.35 + 0.35 * volume + 0.30 * (1.0 - roas_ratio)),
                low_data_flag,
            )
            insights.append(Insight(
                insight_rank=0,
                entity_type="PRODUCT",
                entity_id=product_id,
                diagnosis_code="SHOPPING_LOW_ROAS",
                confidence=conf,
                risk_tier="med",
                labels=sorted(set(base_labels + ["LOW_ROAS", "UNDERPERFORMER"])),
                evidence={
                    "product_id": product_id,
                    "product_title": product_title,
                    "product_brand": product_brand,
                    "roas_w30": round(roas_w30, 2),
                    "target_roas": target_roas,
                    "roas_ratio": round(roas_ratio, 2),
                    "conversions_w30": conv_w30,
                    "cost_w30": cost_w30 / 1_000_000,
                },
                recommended_action=(
                    f"Product ROAS is {roas_ratio:.1%} of target. "
                    f"Consider bid reduction or exclusion if trend continues."
                ),
                guardrail_rule_ids=base_guardrails,
            ))

    # ── SHOPPING_DISAPPROVED ──────────────────────────────────────
    # Product disapproved in Merchant Center
    if has_disapproval:
        conf = 0.95  # Very high confidence - definitive feed issue
        insights.append(Insight(
            insight_rank=0,
            entity_type="PRODUCT",
            entity_id=product_id,
            diagnosis_code="SHOPPING_DISAPPROVED",
            confidence=conf,
            risk_tier="high",
            labels=sorted(set(base_labels + ["DISAPPROVED", "POLICY_VIOLATION"])),
            evidence={
                "product_id": product_id,
                "product_title": product_title,
                "product_brand": product_brand,
                "has_disapproval": True,
                "feed_quality_score": feed_quality_score,
            },
            recommended_action=(
                f"Product disapproved in Merchant Center. "
                f"Review disapproval reasons in Merchant Center and fix feed issues."
            ),
            guardrail_rule_ids=sorted(set(base_guardrails + [RULE_SHOPPING_FEED_GATE])),
        ))

    # ── SHOPPING_MISSING_ATTRS ────────────────────────────────────
    # Required attributes missing
    if feed_quality_score < 0.8 and feed_quality_score >= 0.5 and not has_disapproval:
        conf = 0.60
        insights.append(Insight(
            insight_rank=0,
            entity_type="PRODUCT",
            entity_id=product_id,
            diagnosis_code="SHOPPING_MISSING_ATTRS",
            confidence=conf,
            risk_tier="low",
            labels=sorted(set(base_labels + ["MISSING_ATTRS", "FEED_QUALITY"])),
            evidence={
                "product_id": product_id,
                "product_title": product_title,
                "product_brand": product_brand,
                "feed_quality_score": round(feed_quality_score, 2),
            },
            recommended_action=(
                f"Product feed quality score is {feed_quality_score:.0%}. "
                f"Add missing optional attributes (GTIN, brand, MPN) to improve performance."
            ),
            guardrail_rule_ids=base_guardrails,
        ))

    # ── SHOPPING_WINNER ───────────────────────────────────────────
    # High ROAS, opportunity to scale
    if target_roas and target_roas > 0 and roas_w30 > 0 and conv_w30 >= 5:
        roas_ratio = roas_w30 / target_roas
        if roas_ratio > 1.5 and impr_w30 > 0:
            # Check if losing impression share (simplified - would need API data)
            conf = _cap_low_data(
                _clamp01(0.40 + 0.40 * volume + 0.20 * min(1.0, (roas_ratio - 1.5))),
                low_data_flag,
            )
            insights.append(Insight(
                insight_rank=0,
                entity_type="PRODUCT",
                entity_id=product_id,
                diagnosis_code="SHOPPING_WINNER",
                confidence=conf,
                risk_tier="low",
                labels=sorted(set(base_labels + ["HIGH_ROAS", "SCALE_OPPORTUNITY"])),
                evidence={
                    "product_id": product_id,
                    "product_title": product_title,
                    "product_brand": product_brand,
                    "roas_w30": round(roas_w30, 2),
                    "target_roas": target_roas,
                    "roas_ratio": round(roas_ratio, 2),
                    "conversions_w30": conv_w30,
                    "cost_w30": cost_w30 / 1_000_000,
                },
                recommended_action=(
                    f"Product ROAS is {roas_ratio:.1f}x target - strong performer. "
                    f"Consider increasing bids to capture more volume."
                ),
                guardrail_rule_ids=base_guardrails,
            ))

    # ── SHOPPING_LOW_IMPRESSIONS ──────────────────────────────────
    # Product not showing (feed quality issue)
    if impr_w30 < 50 and cost_w30 > 0 and clicks_w30 < 5:
        # Low impressions but still active - likely feed issue
        if feed_quality_score < 0.8:
            conf = 0.65
            insights.append(Insight(
                insight_rank=0,
                entity_type="PRODUCT",
                entity_id=product_id,
                diagnosis_code="SHOPPING_LOW_IMPRESSIONS",
                confidence=conf,
                risk_tier="med",
                labels=sorted(set(base_labels + ["LOW_IMPRESSIONS", "FEED_QUALITY"])),
                evidence={
                    "product_id": product_id,
                    "product_title": product_title,
                    "product_brand": product_brand,
                    "impressions_w30": impr_w30,
                    "feed_quality_score": round(feed_quality_score, 2),
                },
                recommended_action=(
                    f"Product getting very low impressions ({impr_w30:.0f} in 30d). "
                    f"Feed quality score: {feed_quality_score:.0%}. "
                    f"Review product data quality and category selection."
                ),
                guardrail_rule_ids=sorted(set(base_guardrails + [RULE_SHOPPING_FEED_GATE])),
            ))

    return insights
