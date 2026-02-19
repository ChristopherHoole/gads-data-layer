"""
Shopping optimization rules — full implementation.

Rules (14 total):

  SHOP-BID-001: High ROAS bid increase (ROAS > 5.0, clicks > 50)
  SHOP-BID-002: Low ROAS bid decrease (ROAS < 1.5, cost > $20)
  SHOP-BID-003: Very low ROAS bid decrease (ROAS < 0.5, cost > $30) — conservative action
  SHOP-BID-004: Low visibility bid increase (cost > $100, impressions < 500)
  SHOP-BID-005: Insufficient data hold (clicks < 10)

  SHOP-PAUSE-006: Zero conversions high spend pause (zero conv, cost > $50, clicks > 100)
  SHOP-PAUSE-007: Very low ROAS pause (ROAS < 0.5, cost > $30) — aggressive action
  SHOP-PAUSE-008: Out of stock still spending pause

  SHOP-FEED-009: Disapproved product flag
  SHOP-FEED-010: Price mismatch flag
  SHOP-FEED-011: Stuck in pending approval flag
  SHOP-FEED-012: Low feed quality score flag

  SHOP-REVIEW-013: Out of stock receiving clicks review
  SHOP-REVIEW-014: Disapproved product still spending review

Note on SHOP-BID-003 and SHOP-PAUSE-007:
  Both trigger on ROAS < 0.5 AND cost > $30. This is intentional — the rules engine
  generates both recommendations and the user chooses which to action. BID-003 is the
  conservative option (reduce bid), PAUSE-007 is the aggressive option (pause entirely).

Data sources:
  - BID/PAUSE/REVIEW rules: product: Dict from analytics.product_features_daily
  - FEED rules: product: Dict from raw_product_feed_quality
  - apply_rules() accepts both datasets and routes accordingly
"""

from typing import List, Dict, Optional
from act_autopilot.models import Recommendation, _safe_float


# =============================================================================
# SHOP-BID RULES (1–5)
# =============================================================================

def shop_bid_001_high_roas_increase(product: Dict) -> Optional[Recommendation]:
    """
    SHOP-BID-001: High ROAS Product Bid Increase.

    Trigger: ROAS > 5.0 AND clicks > 50 in last 30 days
    Action:  Increase product bid by 15%
    Risk:    low
    """
    roas      = _safe_float(product.get('roas_w30'))
    clicks    = _safe_float(product.get('clicks_w30_sum'))
    cost_mic  = _safe_float(product.get('cost_micros_w30_sum'))
    conv      = _safe_float(product.get('conversions_w30_sum'))

    if roas <= 5.0:
        return None
    if clicks <= 50:
        return None
    if cost_mic <= 0:
        return None

    avg_cpc   = (cost_mic / clicks) / 1_000_000
    new_bid   = avg_cpc * 1.15
    product_id = str(product.get('product_id', 'unknown'))

    return Recommendation(
        rule_id='SHOP-BID-001',
        rule_name='High ROAS Product Bid Increase',
        entity_type='product',
        entity_id=product_id,
        action_type='update_product_bid',
        risk_tier='low',
        confidence=0.85,
        current_value=avg_cpc,
        recommended_value=new_bid,
        change_pct=0.15,
        rationale=(
            f"Strong ROAS of {roas:.2f}x with {int(clicks)} clicks confirms high-value product. "
            f"Recommend +15% bid increase to capture more impression share."
        ),
        priority=40,
        evidence={
            'product_id': product_id,
            'product_title': product.get('product_title', ''),
            'roas_w30': roas,
            'clicks_w30': int(clicks),
            'conversions_w30': int(conv),
            'cost_w30': cost_mic / 1_000_000,
            'avg_cpc_dollars': avg_cpc,
        },
        triggering_diagnosis='HIGH_ROAS_PRODUCT',
        triggering_confidence=0.85,
        expected_impact=f"Increase visibility for high-performing product (ROAS: {roas:.2f}x)",
    )


def shop_bid_002_low_roas_decrease(product: Dict) -> Optional[Recommendation]:
    """
    SHOP-BID-002: Low ROAS Bid Decrease.

    Trigger: ROAS < 1.5 AND cost > $20 in last 30 days
    Action:  Decrease product bid by 15%
    Risk:    low
    """
    roas     = _safe_float(product.get('roas_w30'))
    cost_mic = _safe_float(product.get('cost_micros_w30_sum'))
    clicks   = _safe_float(product.get('clicks_w30_sum'))
    conv     = _safe_float(product.get('conversions_w30_sum'))

    cost_dollars = cost_mic / 1_000_000

    if roas >= 1.5:
        return None
    if cost_dollars < 20:
        return None
    if clicks <= 0:
        return None

    avg_cpc  = (cost_mic / clicks) / 1_000_000
    new_bid  = avg_cpc * 0.85
    product_id = str(product.get('product_id', 'unknown'))

    return Recommendation(
        rule_id='SHOP-BID-002',
        rule_name='Low ROAS Bid Decrease',
        entity_type='product',
        entity_id=product_id,
        action_type='update_product_bid',
        risk_tier='low',
        confidence=0.75,
        current_value=avg_cpc,
        recommended_value=new_bid,
        change_pct=-0.15,
        rationale=(
            f"ROAS of {roas:.2f}x is below 1.5x threshold with ${cost_dollars:.2f} spent. "
            f"Recommend -15% bid decrease to improve efficiency."
        ),
        priority=50,
        evidence={
            'product_id': product_id,
            'product_title': product.get('product_title', ''),
            'roas_w30': roas,
            'cost_w30': cost_dollars,
            'clicks_w30': int(clicks),
            'conversions_w30': int(conv),
            'avg_cpc_dollars': avg_cpc,
        },
        triggering_diagnosis='LOW_ROAS_PRODUCT',
        triggering_confidence=0.75,
        expected_impact=f"Improve ad spend efficiency for underperforming product (ROAS: {roas:.2f}x)",
    )


def shop_bid_003_very_low_roas_decrease(product: Dict) -> Optional[Recommendation]:
    """
    SHOP-BID-003: Very Low ROAS Aggressive Bid Decrease.

    Trigger: ROAS < 0.5 AND cost > $30 in last 30 days
    Action:  Decrease product bid by 25% (conservative option — see also SHOP-PAUSE-007)
    Risk:    medium

    Note: SHOP-PAUSE-007 fires on the same trigger with a pause recommendation.
    This rule is the conservative action — reduce bid rather than pause entirely.
    The user decides which recommendation to action.
    """
    roas     = _safe_float(product.get('roas_w30'))
    cost_mic = _safe_float(product.get('cost_micros_w30_sum'))
    clicks   = _safe_float(product.get('clicks_w30_sum'))
    conv     = _safe_float(product.get('conversions_w30_sum'))

    cost_dollars = cost_mic / 1_000_000

    if roas >= 0.5:
        return None
    if cost_dollars < 30:
        return None
    if clicks <= 0:
        return None

    avg_cpc  = (cost_mic / clicks) / 1_000_000
    new_bid  = avg_cpc * 0.75
    product_id = str(product.get('product_id', 'unknown'))

    return Recommendation(
        rule_id='SHOP-BID-003',
        rule_name='Very Low ROAS Aggressive Bid Decrease',
        entity_type='product',
        entity_id=product_id,
        action_type='update_product_bid',
        risk_tier='medium',
        confidence=0.80,
        current_value=avg_cpc,
        recommended_value=new_bid,
        change_pct=-0.25,
        rationale=(
            f"Very poor ROAS of {roas:.2f}x with ${cost_dollars:.2f} spent. "
            f"Conservative action: -25% bid decrease. "
            f"A pause recommendation (SHOP-PAUSE-007) has also been generated — "
            f"action whichever is appropriate."
        ),
        priority=30,
        evidence={
            'product_id': product_id,
            'product_title': product.get('product_title', ''),
            'roas_w30': roas,
            'cost_w30': cost_dollars,
            'clicks_w30': int(clicks),
            'conversions_w30': int(conv),
            'avg_cpc_dollars': avg_cpc,
        },
        triggering_diagnosis='VERY_LOW_ROAS_PRODUCT',
        triggering_confidence=0.80,
        expected_impact=f"Reduce wasted spend on very low ROAS product ({roas:.2f}x) — conservative option",
    )


def shop_bid_004_low_visibility_increase(product: Dict) -> Optional[Recommendation]:
    """
    SHOP-BID-004: Low Visibility Bid Increase.

    Trigger: cost > $100 AND impressions < 500 in last 30 days
    Action:  Increase product bid by 10% to improve visibility
    Risk:    low
    """
    cost_mic     = _safe_float(product.get('cost_micros_w30_sum'))
    impressions  = _safe_float(product.get('impressions_w30_sum'))
    clicks       = _safe_float(product.get('clicks_w30_sum'))

    cost_dollars = cost_mic / 1_000_000

    if cost_dollars <= 100:
        return None
    if impressions >= 500:
        return None
    if clicks <= 0:
        return None

    avg_cpc  = (cost_mic / clicks) / 1_000_000
    new_bid  = avg_cpc * 1.10
    product_id = str(product.get('product_id', 'unknown'))

    return Recommendation(
        rule_id='SHOP-BID-004',
        rule_name='Low Visibility Bid Increase',
        entity_type='product',
        entity_id=product_id,
        action_type='update_product_bid',
        risk_tier='low',
        confidence=0.70,
        current_value=avg_cpc,
        recommended_value=new_bid,
        change_pct=0.10,
        rationale=(
            f"Product spent ${cost_dollars:.2f} but achieved only {int(impressions)} impressions, "
            f"suggesting low auction visibility. Recommend +10% bid increase to improve reach."
        ),
        priority=60,
        evidence={
            'product_id': product_id,
            'product_title': product.get('product_title', ''),
            'cost_w30': cost_dollars,
            'impressions_w30': int(impressions),
            'clicks_w30': int(clicks),
            'avg_cpc_dollars': avg_cpc,
        },
        triggering_diagnosis='LOW_IMPRESSION_SHARE',
        triggering_confidence=0.70,
        expected_impact=f"Increase auction visibility for product with {int(impressions)} impressions on ${cost_dollars:.2f} spend",
    )


def shop_bid_005_insufficient_data_hold(product: Dict) -> Optional[Recommendation]:
    """
    SHOP-BID-005: Insufficient Data — Hold Bid.

    Trigger: clicks < 10 in last 30 days
    Action:  Hold — flag as low data, no bid change recommended
    Risk:    low
    """
    clicks   = _safe_float(product.get('clicks_w30_sum'))
    cost_mic = _safe_float(product.get('cost_micros_w30_sum'))

    if clicks >= 10:
        return None
    if cost_mic <= 0:
        return None

    product_id = str(product.get('product_id', 'unknown'))

    return Recommendation(
        rule_id='SHOP-BID-005',
        rule_name='Insufficient Data — Hold Bid',
        entity_type='product',
        entity_id=product_id,
        action_type='hold',
        risk_tier='low',
        confidence=0.95,
        current_value=None,
        recommended_value=None,
        change_pct=0.0,
        rationale=(
            f"Only {int(clicks)} clicks in 30 days — insufficient data to make a reliable bid decision. "
            f"Hold current bid and monitor until data threshold is reached."
        ),
        priority=90,
        evidence={
            'product_id': product_id,
            'product_title': product.get('product_title', ''),
            'clicks_w30': int(clicks),
            'cost_w30': cost_mic / 1_000_000,
        },
        triggering_diagnosis='LOW_DATA_PRODUCT',
        triggering_confidence=0.95,
        expected_impact="No change — monitoring only until sufficient data is available",
    )


# =============================================================================
# SHOP-PAUSE RULES (6–8)
# =============================================================================

def shop_pause_006_zero_conv_high_spend(product: Dict) -> Optional[Recommendation]:
    """
    SHOP-PAUSE-006: Zero Conversions High Spend Pause.

    Trigger: zero conversions AND cost > $50 AND clicks > 100 in last 30 days
    Action:  Pause product
    Risk:    low
    """
    conv     = _safe_float(product.get('conversions_w30_sum'))
    cost_mic = _safe_float(product.get('cost_micros_w30_sum'))
    clicks   = _safe_float(product.get('clicks_w30_sum'))

    cost_dollars = cost_mic / 1_000_000

    if conv > 0:
        return None
    if cost_dollars < 50:
        return None
    if clicks <= 100:
        return None

    product_id = str(product.get('product_id', 'unknown'))

    return Recommendation(
        rule_id='SHOP-PAUSE-006',
        rule_name='Zero Conversions High Spend Pause',
        entity_type='product',
        entity_id=product_id,
        action_type='pause_product',
        risk_tier='low',
        confidence=0.90,
        current_value=None,
        recommended_value=None,
        change_pct=None,
        rationale=(
            f"Zero conversions from {int(clicks)} clicks and ${cost_dollars:.2f} spend in 30 days. "
            f"Product is consuming budget with no return. Recommend pausing."
        ),
        priority=20,
        evidence={
            'product_id': product_id,
            'product_title': product.get('product_title', ''),
            'conversions_w30': 0,
            'clicks_w30': int(clicks),
            'cost_w30': cost_dollars,
        },
        triggering_diagnosis='ZERO_CONV_HIGH_SPEND',
        triggering_confidence=0.90,
        expected_impact=f"Stop ${cost_dollars:.2f}/30d wasted spend on zero-conversion product",
    )


def shop_pause_007_very_low_roas_pause(product: Dict) -> Optional[Recommendation]:
    """
    SHOP-PAUSE-007: Very Low ROAS Pause.

    Trigger: ROAS < 0.5 AND cost > $30 in last 30 days
    Action:  Pause product (aggressive option — see also SHOP-BID-003)
    Risk:    medium

    Note: SHOP-BID-003 fires on the same trigger with a bid decrease recommendation.
    This rule is the aggressive action — pause the product entirely.
    The user decides which recommendation to action.
    """
    roas     = _safe_float(product.get('roas_w30'))
    cost_mic = _safe_float(product.get('cost_micros_w30_sum'))
    conv     = _safe_float(product.get('conversions_w30_sum'))
    clicks   = _safe_float(product.get('clicks_w30_sum'))

    cost_dollars = cost_mic / 1_000_000

    if roas >= 0.5:
        return None
    if cost_dollars < 30:
        return None

    product_id = str(product.get('product_id', 'unknown'))

    return Recommendation(
        rule_id='SHOP-PAUSE-007',
        rule_name='Very Low ROAS Pause',
        entity_type='product',
        entity_id=product_id,
        action_type='pause_product',
        risk_tier='medium',
        confidence=0.75,
        current_value=None,
        recommended_value=None,
        change_pct=None,
        rationale=(
            f"Very poor ROAS of {roas:.2f}x with ${cost_dollars:.2f} spent. "
            f"Aggressive action: pause product entirely. "
            f"A bid decrease recommendation (SHOP-BID-003) has also been generated — "
            f"action whichever is appropriate."
        ),
        priority=25,
        evidence={
            'product_id': product_id,
            'product_title': product.get('product_title', ''),
            'roas_w30': roas,
            'cost_w30': cost_dollars,
            'clicks_w30': int(clicks),
            'conversions_w30': int(conv),
        },
        triggering_diagnosis='VERY_LOW_ROAS_PRODUCT',
        triggering_confidence=0.75,
        expected_impact=f"Stop wasted spend on very low ROAS product ({roas:.2f}x) — aggressive option",
    )


def shop_pause_008_out_of_stock_spending(product: Dict) -> Optional[Recommendation]:
    """
    SHOP-PAUSE-008: Out of Stock Product Still Spending.

    Trigger: availability = OUT_OF_STOCK AND clicks_w7 > 0 AND cost_w7 > $0
    Action:  Pause product — out of stock but still spending
    Risk:    low
    """
    availability = str(product.get('availability') or '').upper()
    clicks_w7    = _safe_float(product.get('clicks_w7_sum'))
    cost_mic_w7  = _safe_float(product.get('cost_micros_w7_sum'))

    cost_w7_dollars = cost_mic_w7 / 1_000_000

    if availability != 'OUT_OF_STOCK':
        return None
    if clicks_w7 <= 0:
        return None
    if cost_w7_dollars <= 0:
        return None

    product_id = str(product.get('product_id', 'unknown'))

    return Recommendation(
        rule_id='SHOP-PAUSE-008',
        rule_name='Out of Stock Product Still Spending',
        entity_type='product',
        entity_id=product_id,
        action_type='pause_product',
        risk_tier='low',
        confidence=0.95,
        current_value=None,
        recommended_value=None,
        change_pct=None,
        rationale=(
            f"Product is OUT OF STOCK but received {int(clicks_w7)} clicks and "
            f"spent ${cost_w7_dollars:.2f} in the last 7 days. "
            f"Pausing prevents wasted spend on unavailable inventory."
        ),
        priority=10,
        evidence={
            'product_id': product_id,
            'product_title': product.get('product_title', ''),
            'availability': availability,
            'clicks_w7': int(clicks_w7),
            'cost_w7': cost_w7_dollars,
        },
        triggering_diagnosis='OUT_OF_STOCK_SPENDING',
        triggering_confidence=0.95,
        expected_impact=f"Stop spend on out-of-stock product (${cost_w7_dollars:.2f} last 7 days)",
    )


# =============================================================================
# SHOP-FEED RULES (9–12)
# =============================================================================

def shop_feed_009_disapproved_product(product: Dict) -> Optional[Recommendation]:
    """
    SHOP-FEED-009: Disapproved Product.

    Trigger: approval_status = DISAPPROVED
    Action:  Flag for feed fix — product disapproved and not serving
    Risk:    low
    """
    approval = str(product.get('approval_status') or '').upper()

    if approval != 'DISAPPROVED':
        return None

    product_id = str(product.get('product_id', 'unknown'))
    reasons    = product.get('disapproval_reasons') or []
    reason_str = ', '.join(reasons) if reasons else 'See Merchant Center for details'

    return Recommendation(
        rule_id='SHOP-FEED-009',
        rule_name='Disapproved Product',
        entity_type='product',
        entity_id=product_id,
        action_type='fix_feed',
        risk_tier='low',
        confidence=1.0,
        current_value=None,
        recommended_value=None,
        change_pct=None,
        rationale=(
            f"Product is DISAPPROVED and not serving. "
            f"Disapproval reason(s): {reason_str}. "
            f"Fix the feed issue in Merchant Center to restore serving."
        ),
        priority=15,
        evidence={
            'product_id': product_id,
            'approval_status': approval,
            'disapproval_reasons': reasons,
        },
        triggering_diagnosis='DISAPPROVED_PRODUCT',
        triggering_confidence=1.0,
        expected_impact="Restore product serving by resolving Merchant Center disapproval",
    )


def shop_feed_010_price_mismatch(product: Dict) -> Optional[Recommendation]:
    """
    SHOP-FEED-010: Price Mismatch Detected.

    Trigger: price_mismatch = TRUE
    Action:  Flag for feed fix — price mismatch between feed and landing page
    Risk:    low
    """
    price_mismatch = product.get('price_mismatch')

    if not price_mismatch:
        return None

    product_id = str(product.get('product_id', 'unknown'))

    return Recommendation(
        rule_id='SHOP-FEED-010',
        rule_name='Price Mismatch Detected',
        entity_type='product',
        entity_id=product_id,
        action_type='fix_feed',
        risk_tier='low',
        confidence=1.0,
        current_value=None,
        recommended_value=None,
        change_pct=None,
        rationale=(
            f"Price mismatch detected: the price in the product feed does not match "
            f"the price on the landing page. This can cause disapprovals and poor user experience. "
            f"Update the feed or landing page price to match."
        ),
        priority=20,
        evidence={
            'product_id': product_id,
            'price_mismatch': True,
            'approval_status': str(product.get('approval_status') or ''),
        },
        triggering_diagnosis='PRICE_MISMATCH',
        triggering_confidence=1.0,
        expected_impact="Resolve price mismatch to prevent potential disapproval and improve trust",
    )


def shop_feed_011_pending_approval_stuck(product: Dict) -> Optional[Recommendation]:
    """
    SHOP-FEED-011: Product Stuck in Pending Approval.

    Trigger: approval_status = PENDING AND ingested_at older than 48 hours
    Action:  Flag for review — may indicate a feed processing issue
    Risk:    low
    """
    from datetime import datetime, timezone, timedelta

    approval   = str(product.get('approval_status') or '').upper()
    ingested   = product.get('ingested_at')

    if approval != 'PENDING':
        return None

    # Check if stuck — ingested_at older than 48 hours
    if ingested is not None:
        try:
            if hasattr(ingested, 'tzinfo'):
                if ingested.tzinfo is None:
                    ingested = ingested.replace(tzinfo=timezone.utc)
                age_hours = (datetime.now(timezone.utc) - ingested).total_seconds() / 3600
            else:
                # String — parse it
                ingested_dt = datetime.fromisoformat(str(ingested).replace('Z', '+00:00'))
                age_hours = (datetime.now(timezone.utc) - ingested_dt).total_seconds() / 3600

            if age_hours < 48:
                return None
        except Exception:
            pass  # If we can't parse the date, flag it anyway

    product_id = str(product.get('product_id', 'unknown'))

    return Recommendation(
        rule_id='SHOP-FEED-011',
        rule_name='Product Stuck in Pending Approval',
        entity_type='product',
        entity_id=product_id,
        action_type='review_feed',
        risk_tier='low',
        confidence=0.80,
        current_value=None,
        recommended_value=None,
        change_pct=None,
        rationale=(
            f"Product has been in PENDING approval status for over 48 hours. "
            f"This may indicate a feed processing issue or policy review delay. "
            f"Check Merchant Center for status updates."
        ),
        priority=50,
        evidence={
            'product_id': product_id,
            'approval_status': approval,
            'ingested_at': str(ingested) if ingested else None,
        },
        triggering_diagnosis='PENDING_STUCK',
        triggering_confidence=0.80,
        expected_impact="Identify and resolve feed processing blockage preventing product from serving",
    )


def shop_feed_012_low_quality_score(product: Dict) -> Optional[Recommendation]:
    """
    SHOP-FEED-012: Low Feed Quality Score.

    Trigger: feed_quality_score < 0.70
    Action:  Flag for feed improvement — quality below 70% threshold
    Risk:    low
    """
    quality = _safe_float(product.get('feed_quality_score'))

    # Skip if no quality score (field may be absent from feed quality table)
    if product.get('feed_quality_score') is None:
        return None
    if quality >= 0.70:
        return None

    product_id = str(product.get('product_id', 'unknown'))
    pct        = round(quality * 100, 1)

    return Recommendation(
        rule_id='SHOP-FEED-012',
        rule_name='Low Feed Quality Score',
        entity_type='product',
        entity_id=product_id,
        action_type='improve_feed',
        risk_tier='low',
        confidence=0.85,
        current_value=quality,
        recommended_value=0.70,
        change_pct=None,
        rationale=(
            f"Feed quality score of {pct}% is below the 70% threshold. "
            f"Low feed quality can reduce impression share and increase CPC. "
            f"Improve product title, description, and image quality."
        ),
        priority=55,
        evidence={
            'product_id': product_id,
            'feed_quality_score': quality,
            'threshold': 0.70,
        },
        triggering_diagnosis='LOW_FEED_QUALITY',
        triggering_confidence=0.85,
        expected_impact=f"Improve feed quality from {pct}% to 70%+ to increase auction eligibility",
    )


# =============================================================================
# SHOP-REVIEW RULES (13–14)
# =============================================================================

def shop_review_013_out_of_stock_clicks(product: Dict) -> Optional[Recommendation]:
    """
    SHOP-REVIEW-013: Out of Stock Product Receiving Clicks.

    Trigger: availability = OUT_OF_STOCK AND clicks_w7 > 0
    Action:  Flag for review — user attention required
    Risk:    low
    """
    availability = str(product.get('availability') or '').upper()
    clicks_w7    = _safe_float(product.get('clicks_w7_sum'))

    if availability != 'OUT_OF_STOCK':
        return None
    if clicks_w7 <= 0:
        return None

    product_id = str(product.get('product_id', 'unknown'))

    return Recommendation(
        rule_id='SHOP-REVIEW-013',
        rule_name='Out of Stock Product Receiving Clicks',
        entity_type='product',
        entity_id=product_id,
        action_type='review',
        risk_tier='low',
        confidence=0.95,
        current_value=None,
        recommended_value=None,
        change_pct=None,
        rationale=(
            f"Product is OUT OF STOCK but received {int(clicks_w7)} clicks in the last 7 days. "
            f"Users are clicking through to an unavailable product, creating a poor experience. "
            f"Review whether to pause this product or update availability."
        ),
        priority=35,
        evidence={
            'product_id': product_id,
            'product_title': product.get('product_title', ''),
            'availability': availability,
            'clicks_w7': int(clicks_w7),
        },
        triggering_diagnosis='OUT_OF_STOCK_RECEIVING_CLICKS',
        triggering_confidence=0.95,
        expected_impact="Prevent poor user experience from out-of-stock product receiving clicks",
    )


def shop_review_014_disapproved_spending(product: Dict) -> Optional[Recommendation]:
    """
    SHOP-REVIEW-014: Disapproved Product Still Spending.

    Trigger: approval_status = DISAPPROVED AND cost_w30 > $0
    Action:  Flag for urgent review — disapproved product should not be spending
    Risk:    medium
    """
    approval = str(product.get('approval_status') or '').upper()
    cost_mic = _safe_float(product.get('cost_micros_w30_sum'))

    cost_dollars = cost_mic / 1_000_000

    if approval != 'DISAPPROVED':
        return None
    if cost_dollars <= 0:
        return None

    product_id = str(product.get('product_id', 'unknown'))

    return Recommendation(
        rule_id='SHOP-REVIEW-014',
        rule_name='Disapproved Product Still Spending',
        entity_type='product',
        entity_id=product_id,
        action_type='review',
        risk_tier='medium',
        confidence=0.90,
        current_value=None,
        recommended_value=None,
        change_pct=None,
        rationale=(
            f"Product is DISAPPROVED but shows ${cost_dollars:.2f} spend in the last 30 days. "
            f"A disapproved product should not be serving — this may indicate a data lag or "
            f"a partial disapproval affecting some variants. Urgent review required."
        ),
        priority=10,
        evidence={
            'product_id': product_id,
            'product_title': product.get('product_title', ''),
            'approval_status': approval,
            'cost_w30': cost_dollars,
        },
        triggering_diagnosis='DISAPPROVED_SPENDING',
        triggering_confidence=0.90,
        expected_impact="Identify why a disapproved product is still accruing spend",
    )


# =============================================================================
# EXECUTION ENTRY POINT
# =============================================================================

def apply_rules(
    product_features: List[Dict],
    feed_quality_data: Optional[List[Dict]] = None,
    ctx=None,
) -> List[Recommendation]:
    """
    Apply all shopping rules to product data.

    Args:
        product_features:  List of product dicts from analytics.product_features_daily
        feed_quality_data: List of product dicts from raw_product_feed_quality (optional)
        ctx:               Rule context (unused — kept for interface consistency)

    Returns:
        List of Recommendation objects
    """
    recommendations = []

    # BID + PAUSE + REVIEW rules — operate on product_features
    bid_pause_review_rules = [
        shop_bid_001_high_roas_increase,
        shop_bid_002_low_roas_decrease,
        shop_bid_003_very_low_roas_decrease,
        shop_bid_004_low_visibility_increase,
        shop_bid_005_insufficient_data_hold,
        shop_pause_006_zero_conv_high_spend,
        shop_pause_007_very_low_roas_pause,
        shop_pause_008_out_of_stock_spending,
        shop_review_013_out_of_stock_clicks,
        shop_review_014_disapproved_spending,
    ]

    for product in (product_features or []):
        for rule_fn in bid_pause_review_rules:
            try:
                rec = rule_fn(product)
                if rec:
                    recommendations.append(rec)
            except Exception as e:
                print(f"[shopping_rules] Error in {rule_fn.__name__} for {product.get('product_id')}: {e}")

    # FEED rules — operate on feed_quality_data
    feed_rules = [
        shop_feed_009_disapproved_product,
        shop_feed_010_price_mismatch,
        shop_feed_011_pending_approval_stuck,
        shop_feed_012_low_quality_score,
    ]

    for product in (feed_quality_data or []):
        for rule_fn in feed_rules:
            try:
                rec = rule_fn(product)
                if rec:
                    recommendations.append(rec)
            except Exception as e:
                print(f"[shopping_rules] Error in {rule_fn.__name__} for {product.get('product_id')}: {e}")

    return recommendations
