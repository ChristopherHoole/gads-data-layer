"""
Keyword & Search Term Rules — Keyword-level optimization.

Rules (14 total):
  KW-PAUSE-001: Pause wasted spend keyword (>$50/30d, zero conversions)
  KW-PAUSE-002: Pause chronic underperformer (CPA >2x target, 90d data)
  KW-PAUSE-003: Pause low QS + high CPA (QS<=3 AND CPA>1.5x target) — hard rule

  KW-BID-001:   Reduce bid — high CPA (CPA 1.3-2x target)
  KW-BID-002:   Increase bid — low CPA, high efficiency
  KW-BID-003:   Hold bid — low data

  ST-ADD-001:   Add search term as EXACT keyword (>=5 conv, high CVR)
  ST-ADD-002:   Add search term as PHRASE keyword (>=10 conv, good CVR)

  ST-NEG-001:   Negative — wasted spend (>$50/30d, zero conv)
  ST-NEG-002:   Negative — high CPC low CVR (likely competitor/irrelevant)
  ST-NEG-003:   Negative — low relevance (>$20/30d, zero conv, CTR<1%)

  KW-REVIEW-001: Review low QS (QS<=3, not triggering pause)
  KW-REVIEW-002: Review low CTR (CTR <70% campaign avg)
  KW-REVIEW-003: Review match type tightening (BROAD with good perf)

Constitution references:
  CONSTITUTION-5-2:  Low data gates
  CONSTITUTION-5-3:  Cooldown (14 days for keyword bid changes)
  CONSTITUTION-A-4:  Low data appendix
"""

from __future__ import annotations

from typing import Dict, Any, List, Optional

from ..models import Recommendation, RuleContext, _safe_float


def _target_cpa_micros(config) -> float:
    """
    Get target CPA in micros from config.
    Config stores target_cpa in DOLLARS (e.g. 25.0 = $25).
    Features store CPA in MICROS (e.g. 25_000_000 = $25).
    This function always returns micros.
    """
    raw = _safe_float(config.target_cpa)
    if raw <= 0:
        return 0.0
    # If value looks like dollars (< 100,000), convert to micros
    # If already micros (>= 100,000), use as-is
    if raw < 100_000:
        return raw * 1_000_000
    return raw


# ═══════════════════════════════════════════════════════════════
# KEYWORD PAUSE RULES (use keyword_features_daily via RuleContext)
# ═══════════════════════════════════════════════════════════════


def kw_pause_001_wasted_spend(ctx: RuleContext) -> Optional[Recommendation]:
    """
    Trigger: Cost >$50 in 30d AND zero conversions AND >=10 clicks
    Action:  Pause keyword
    Risk:    low (zero conversions = no value being lost)
    """
    cost_w30 = _safe_float(ctx.features.get("cost_micros_w30_sum"))
    conv_w30 = _safe_float(ctx.features.get("conversions_w30_sum"))
    clicks_w30 = _safe_float(ctx.features.get("clicks_w30_sum"))
    cost_w90 = _safe_float(ctx.features.get("cost_micros_w90_sum"))
    conv_w90 = _safe_float(ctx.features.get("conversions_w90_sum"))

    cost_30d_dollars = cost_w30 / 1_000_000
    cost_90d_dollars = cost_w90 / 1_000_000

    if cost_30d_dollars < 50:
        return None
    if conv_w30 > 0:
        return None
    if clicks_w30 < 10:
        return None

    # Higher confidence with more spend and longer zero-conv streak
    confidence = min(1.0, 0.50 + 0.25 * min(1.0, cost_30d_dollars / 200)
                     + 0.25 * (1.0 if conv_w90 == 0 else 0.0))

    keyword_id = str(ctx.features.get("keyword_id"))
    keyword_text = ctx.features.get("keyword_text", "")
    match_type = ctx.features.get("match_type", "")
    campaign_id = str(ctx.features.get("campaign_id"))

    return Recommendation(
        rule_id="KW-PAUSE-001",
        rule_name="Pause Keyword — Wasted Spend",
        entity_type="KEYWORD",
        entity_id=keyword_id,
        action_type="keyword_pause",
        risk_tier="low",
        confidence=confidence,
        current_value=None,
        recommended_value=None,
        change_pct=None,
        rationale=(
            f"Keyword '{keyword_text}' [{match_type}] spent ${cost_30d_dollars:.0f} "
            f"in 30d with zero conversions ({clicks_w30:.0f} clicks). "
            f"90d total: ${cost_90d_dollars:.0f} spent, {conv_w90:.0f} conversions. "
            f"Strong pause candidate."
        ),
        evidence={
            "keyword_text": keyword_text,
            "match_type": match_type,
            "campaign_id": campaign_id,
            "campaign_name": ctx.features.get("campaign_name", "Unknown"),
            "cost_w30_dollars": round(cost_30d_dollars, 2),
            "cost_w90_dollars": round(cost_90d_dollars, 2),
            "clicks_w30": clicks_w30,
            "conversions_w30": conv_w30,
            "conversions_w90": conv_w90,
            "expected_impact": f"Save ${cost_30d_dollars:.0f}/month with zero conversion loss",
        },
        constitution_refs=["CONSTITUTION-5-2", "CONSTITUTION-A-4"],
        guardrails_checked=[],
        triggering_diagnosis="KEYWORD_WASTED_SPEND",
        triggering_confidence=confidence,
        blocked=False,
        block_reason=None,
        priority=10,
    )


def kw_pause_002_chronic_underperformer(ctx: RuleContext) -> Optional[Recommendation]:
    """
    Trigger: CPA >2x target over 90 days AND >=50 clicks in 90d
    Action:  Pause keyword
    Risk:    med (has SOME conversions, just very expensive)
    """
    target_cpa_micros = _target_cpa_micros(ctx.config)
    if target_cpa_micros <= 0:
        return None

    cost_w90 = _safe_float(ctx.features.get("cost_micros_w90_sum"))
    conv_w90 = _safe_float(ctx.features.get("conversions_w90_sum"))
    clicks_w30 = _safe_float(ctx.features.get("clicks_w30_sum"))

    if conv_w90 <= 0 or cost_w90 <= 0:
        return None  # Handled by KW-PAUSE-001

    cpa_w90_micros = cost_w90 / conv_w90
    cpa_ratio = cpa_w90_micros / target_cpa_micros

    # Need 90d clicks proxy: use 30d × 3
    est_clicks_90d = clicks_w30 * 3
    if est_clicks_90d < 50:
        return None

    if cpa_ratio <= 2.0:
        return None

    confidence = min(1.0, 0.50 + 0.25 * min(1.0, (cpa_ratio - 2.0) / 2.0)
                     + 0.25 * min(1.0, conv_w90 / 10))

    keyword_id = str(ctx.features.get("keyword_id"))
    keyword_text = ctx.features.get("keyword_text", "")
    match_type = ctx.features.get("match_type", "")
    campaign_id = str(ctx.features.get("campaign_id"))
    cpa_dollars = cpa_w90_micros / 1_000_000
    target_dollars = target_cpa_micros / 1_000_000

    return Recommendation(
        rule_id="KW-PAUSE-002",
        rule_name="Pause Keyword — Chronic Underperformer",
        entity_type="KEYWORD",
        entity_id=keyword_id,
        action_type="keyword_pause",
        risk_tier="med",
        confidence=confidence,
        current_value=cpa_w90_micros,
        recommended_value=None,
        change_pct=None,
        rationale=(
            f"Keyword '{keyword_text}' [{match_type}] has 90d CPA ${cpa_dollars:.2f} "
            f"which is {cpa_ratio:.1f}x target ${target_dollars:.2f}. "
            f"Persistent underperformance over 90 days — pause recommended."
        ),
        evidence={
            "keyword_text": keyword_text,
            "match_type": match_type,
            "campaign_id": campaign_id,
            "campaign_name": ctx.features.get("campaign_name", "Unknown"),
            "cpa_w90_dollars": round(cpa_dollars, 2),
            "target_cpa_dollars": round(target_dollars, 2),
            "cpa_ratio": round(cpa_ratio, 2),
            "conversions_w90": conv_w90,
            "cost_w90_dollars": round(cost_w90 / 1_000_000, 2),
            "expected_impact": f"Reallocate ${cost_w90 / 1_000_000 / 3:.0f}/month to better performers",
        },
        constitution_refs=["CONSTITUTION-5-2", "CONSTITUTION-A-4"],
        guardrails_checked=[],
        triggering_diagnosis="KEYWORD_HIGH_CPA",
        triggering_confidence=confidence,
        blocked=False,
        block_reason=None,
        priority=8,
    )


def kw_pause_003_low_qs_high_cpa(ctx: RuleContext) -> Optional[Recommendation]:
    """
    Trigger: QS <= 3 AND CPA > 1.5x target (hard rule from Constitution)
    Action:  Pause keyword
    Risk:    med
    """
    quality_score = ctx.features.get("quality_score")
    if quality_score is None or int(quality_score) > 3:
        return None

    target_cpa_micros = _target_cpa_micros(ctx.config)
    if target_cpa_micros <= 0:
        return None

    cpa_w30 = _safe_float(ctx.features.get("cpa_w30"))
    if cpa_w30 <= 0:
        return None

    cpa_ratio = cpa_w30 / target_cpa_micros
    if cpa_ratio <= 1.5:
        return None

    clicks_w30 = _safe_float(ctx.features.get("clicks_w30_sum"))
    if clicks_w30 < 15:
        return None  # Need minimum data

    qs = int(quality_score)
    confidence = min(1.0, 0.60 + 0.20 * min(1.0, (cpa_ratio - 1.5) / 1.0)
                     + 0.20 * (1.0 - qs / 10.0))

    keyword_id = str(ctx.features.get("keyword_id"))
    keyword_text = ctx.features.get("keyword_text", "")
    match_type = ctx.features.get("match_type", "")
    campaign_id = str(ctx.features.get("campaign_id"))
    cpa_dollars = cpa_w30 / 1_000_000
    target_dollars = target_cpa_micros / 1_000_000

    return Recommendation(
        rule_id="KW-PAUSE-003",
        rule_name="Pause Keyword — Low QS + High CPA",
        entity_type="KEYWORD",
        entity_id=keyword_id,
        action_type="keyword_pause",
        risk_tier="med",
        confidence=confidence,
        current_value=cpa_w30,
        recommended_value=None,
        change_pct=None,
        rationale=(
            f"Keyword '{keyword_text}' [{match_type}] has QS={qs} AND CPA ${cpa_dollars:.2f} "
            f"({cpa_ratio:.1f}x target). Both quality and economics are poor — "
            f"pause and reallocate spend."
        ),
        evidence={
            "keyword_text": keyword_text,
            "match_type": match_type,
            "campaign_id": campaign_id,
            "campaign_name": ctx.features.get("campaign_name", "Unknown"),
            "quality_score": qs,
            "qs_creative": ctx.features.get("quality_score_creative"),
            "qs_landing_page": ctx.features.get("quality_score_landing_page"),
            "qs_relevance": ctx.features.get("quality_score_relevance"),
            "cpa_w30_dollars": round(cpa_dollars, 2),
            "target_cpa_dollars": round(target_dollars, 2),
            "cpa_ratio": round(cpa_ratio, 2),
            "expected_impact": f"Stop bleeding on QS={qs} keyword with {cpa_ratio:.1f}x CPA",
        },
        constitution_refs=["CONSTITUTION-5-2"],
        guardrails_checked=[],
        triggering_diagnosis="KEYWORD_LOW_QS",
        triggering_confidence=confidence,
        blocked=False,
        block_reason=None,
        priority=7,
    )


# ═══════════════════════════════════════════════════════════════
# KEYWORD BID RULES
# ═══════════════════════════════════════════════════════════════


def kw_bid_001_reduce_high_cpa(ctx: RuleContext) -> Optional[Recommendation]:
    """
    Trigger: CPA 1.3-2x target AND >=30 clicks/30d (not severe enough to pause)
    Action:  Reduce bid by 15% (max ±20% per Constitution)
    Risk:    med
    Cooldown: 14 days
    """
    target_cpa_micros = _target_cpa_micros(ctx.config)
    if target_cpa_micros <= 0:
        return None

    cpa_w30 = _safe_float(ctx.features.get("cpa_w30"))
    clicks_w30 = _safe_float(ctx.features.get("clicks_w30_sum"))
    conv_w30 = _safe_float(ctx.features.get("conversions_w30_sum"))
    bid_micros = _safe_float(ctx.features.get("bid_micros"))

    if cpa_w30 <= 0 or clicks_w30 < 30 or conv_w30 < 1:
        return None

    cpa_ratio = cpa_w30 / target_cpa_micros
    if cpa_ratio <= 1.3 or cpa_ratio > 2.0:
        return None  # <1.3 = fine, >2.0 = pause candidate

    low_data = bool(ctx.features.get("low_data_flag", False))
    if low_data:
        return None  # Handled by KW-BID-003

    change_pct = -0.15
    new_bid = bid_micros * (1 + change_pct) if bid_micros > 0 else None
    confidence = min(1.0, 0.45 + 0.30 * min(1.0, (cpa_ratio - 1.3) / 0.7)
                     + 0.25 * min(1.0, conv_w30 / 15))

    keyword_id = str(ctx.features.get("keyword_id"))
    keyword_text = ctx.features.get("keyword_text", "")
    match_type = ctx.features.get("match_type", "")
    cpa_dollars = cpa_w30 / 1_000_000
    target_dollars = target_cpa_micros / 1_000_000

    return Recommendation(
        rule_id="KW-BID-001",
        rule_name="Reduce Bid — High CPA Keyword",
        entity_type="KEYWORD",
        entity_id=keyword_id,
        action_type="keyword_bid_decrease",
        risk_tier="med",
        confidence=confidence,
        current_value=bid_micros,
        recommended_value=new_bid,
        change_pct=change_pct,
        rationale=(
            f"Keyword '{keyword_text}' CPA ${cpa_dollars:.2f} is {cpa_ratio:.1f}x target "
            f"${target_dollars:.2f}. Reducing bid by {abs(change_pct):.0%} to improve efficiency."
        ),
        evidence={
            "keyword_text": keyword_text,
            "match_type": match_type,
            "campaign_id": str(ctx.features.get("campaign_id")),
            "campaign_name": ctx.features.get("campaign_name", "Unknown"),
            "cpa_w30_dollars": round(cpa_dollars, 2),
            "target_cpa_dollars": round(target_dollars, 2),
            "cpa_ratio": round(cpa_ratio, 2),
            "bid_micros": bid_micros,
            "new_bid_micros": new_bid,
            "clicks_w30": clicks_w30,
            "conversions_w30": conv_w30,
            "expected_impact": f"Bring CPA closer to ${target_dollars:.2f} target",
        },
        constitution_refs=["CONSTITUTION-5-3"],
        guardrails_checked=["cooldown_14d", "max_change_20pct"],
        triggering_diagnosis="KEYWORD_HIGH_CPA",
        triggering_confidence=confidence,
        blocked=False,
        block_reason=None,
        priority=15,
    )


def kw_bid_002_increase_low_cpa(ctx: RuleContext) -> Optional[Recommendation]:
    """
    Trigger: CPA < 0.7x target AND >=30 clicks/30d AND conversions > 5
    Action:  Increase bid by 15% to capture more volume
    Risk:    low
    Cooldown: 14 days
    """
    target_cpa_micros = _target_cpa_micros(ctx.config)
    if target_cpa_micros <= 0:
        return None

    cpa_w30 = _safe_float(ctx.features.get("cpa_w30"))
    clicks_w30 = _safe_float(ctx.features.get("clicks_w30_sum"))
    conv_w30 = _safe_float(ctx.features.get("conversions_w30_sum"))
    bid_micros = _safe_float(ctx.features.get("bid_micros"))

    if cpa_w30 <= 0 or clicks_w30 < 30 or conv_w30 < 5:
        return None

    cpa_ratio = cpa_w30 / target_cpa_micros
    if cpa_ratio >= 0.7:
        return None

    low_data = bool(ctx.features.get("low_data_flag", False))
    if low_data:
        return None

    change_pct = 0.15
    new_bid = bid_micros * (1 + change_pct) if bid_micros > 0 else None
    confidence = min(1.0, 0.50 + 0.30 * min(1.0, (0.7 - cpa_ratio) / 0.4)
                     + 0.20 * min(1.0, conv_w30 / 20))

    keyword_id = str(ctx.features.get("keyword_id"))
    keyword_text = ctx.features.get("keyword_text", "")
    cpa_dollars = cpa_w30 / 1_000_000
    target_dollars = target_cpa_micros / 1_000_000

    return Recommendation(
        rule_id="KW-BID-002",
        rule_name="Increase Bid — Low CPA Keyword",
        entity_type="KEYWORD",
        entity_id=keyword_id,
        action_type="keyword_bid_increase",
        risk_tier="low",
        confidence=confidence,
        current_value=bid_micros,
        recommended_value=new_bid,
        change_pct=change_pct,
        rationale=(
            f"Keyword '{keyword_text}' CPA ${cpa_dollars:.2f} is well below target "
            f"${target_dollars:.2f} ({cpa_ratio:.1f}x). Increasing bid by {change_pct:.0%} "
            f"to capture more volume at profitable CPA."
        ),
        evidence={
            "keyword_text": keyword_text,
            "match_type": ctx.features.get("match_type", ""),
            "campaign_id": str(ctx.features.get("campaign_id")),
            "campaign_name": ctx.features.get("campaign_name", "Unknown"),
            "cpa_w30_dollars": round(cpa_dollars, 2),
            "target_cpa_dollars": round(target_dollars, 2),
            "cpa_ratio": round(cpa_ratio, 2),
            "bid_micros": bid_micros,
            "new_bid_micros": new_bid,
            "conversions_w30": conv_w30,
            "expected_impact": f"Capture more volume at ${cpa_dollars:.2f} CPA",
        },
        constitution_refs=["CONSTITUTION-5-3"],
        guardrails_checked=["cooldown_14d", "max_change_20pct"],
        triggering_diagnosis="LOW_CPA_OPPORTUNITY",
        triggering_confidence=confidence,
        blocked=False,
        block_reason=None,
        priority=20,
    )


def kw_bid_003_hold_low_data(ctx: RuleContext) -> Optional[Recommendation]:
    """
    Trigger: Low data flag (clicks_7d < 30 OR conversions_30d < 15)
    Action:  Hold bid — explicit "do nothing" recommendation
    Risk:    low
    """
    low_data = bool(ctx.features.get("low_data_flag", False))
    if not low_data:
        return None

    # Skip paused/zero-activity keywords
    clicks_w7 = _safe_float(ctx.features.get("clicks_w7_sum"))
    if clicks_w7 == 0:
        return None

    keyword_id = str(ctx.features.get("keyword_id"))
    keyword_text = ctx.features.get("keyword_text", "")

    return Recommendation(
        rule_id="KW-BID-003",
        rule_name="Hold Bid — Low Data Keyword",
        entity_type="KEYWORD",
        entity_id=keyword_id,
        action_type="keyword_bid_hold",
        risk_tier="low",
        confidence=0.80,
        current_value=None,
        recommended_value=None,
        change_pct=0.0,
        rationale=(
            f"Keyword '{keyword_text}' has insufficient data for bid changes. "
            f"Holding bid until more data accumulates."
        ),
        evidence={
            "keyword_text": keyword_text,
            "match_type": ctx.features.get("match_type", ""),
            "campaign_id": str(ctx.features.get("campaign_id")),
            "campaign_name": ctx.features.get("campaign_name", "Unknown"),
            "clicks_w7": clicks_w7,
            "conversions_w30": _safe_float(ctx.features.get("conversions_w30_sum")),
            "low_data_clicks_7d": ctx.features.get("low_data_clicks_7d"),
            "low_data_conversions_30d": ctx.features.get("low_data_conversions_30d"),
            "expected_impact": "Avoid premature bid changes on insufficient data",
        },
        constitution_refs=["CONSTITUTION-5-2", "CONSTITUTION-A-4"],
        guardrails_checked=["low_data_gate"],
        triggering_diagnosis="LOW_DATA",
        triggering_confidence=0.80,
        blocked=False,
        block_reason=None,
        priority=50,
    )


# ═══════════════════════════════════════════════════════════════
# SEARCH TERM ADD RULES
# ═══════════════════════════════════════════════════════════════


def st_add_001_add_exact(ctx: RuleContext) -> Optional[Recommendation]:
    """
    Trigger: >=5 conversions AND CVR > campaign avg × 1.2 AND not yet ADDED
    Action:  Add search term as EXACT match keyword
    Risk:    low
    """
    st_status = str(ctx.features.get("search_term_status", ""))
    if st_status == "ADDED":
        return None

    conversions = _safe_float(ctx.features.get("conversions_sum"))
    if conversions < 5:
        return None

    cvr = ctx.features.get("cvr")
    if cvr is None:
        return None
    cvr = float(cvr)

    campaign_avg_cvr = _safe_float(ctx.features.get("_campaign_avg_cvr"))
    cvr_threshold = campaign_avg_cvr * 1.2 if campaign_avg_cvr > 0 else 0.05

    if cvr <= cvr_threshold:
        return None

    search_term = str(ctx.features.get("search_term", ""))
    clicks = _safe_float(ctx.features.get("clicks_sum"))
    cost_dollars = _safe_float(ctx.features.get("cost_micros_sum")) / 1_000_000
    conv_value = _safe_float(ctx.features.get("conversion_value_sum"))

    confidence = min(1.0, 0.40 + 0.30 * min(1.0, conversions / 15)
                     + 0.30 * min(1.0, (cvr - cvr_threshold) / cvr_threshold if cvr_threshold > 0 else 0))

    return Recommendation(
        rule_id="ST-ADD-001",
        rule_name="Add Search Term as EXACT Keyword",
        entity_type="SEARCH_TERM",
        entity_id=search_term,
        action_type="add_keyword_exact",
        risk_tier="low",
        confidence=confidence,
        current_value=None,
        recommended_value=None,
        change_pct=None,
        rationale=(
            f"Search term '{search_term}' has {conversions:.0f} conversions at "
            f"CVR {cvr:.2%} (campaign avg {campaign_avg_cvr:.2%}). "
            f"Add as EXACT match keyword to lock in this traffic."
        ),
        evidence={
            "search_term": search_term,
            "campaign_id": str(ctx.features.get("campaign_id")),
            "campaign_name": ctx.features.get("campaign_name", "Unknown"),
            "ad_group_id": str(ctx.features.get("ad_group_id")),
            "triggering_keyword": ctx.features.get("keyword_text", ""),
            "cvr": round(cvr, 4),
            "campaign_avg_cvr": round(campaign_avg_cvr, 4),
            "conversions": conversions,
            "clicks": clicks,
            "cost_dollars": round(cost_dollars, 2),
            "conversion_value": round(conv_value, 2),
            "recommended_match_type": "EXACT",
            "expected_impact": f"Lock in {conversions:.0f} conversions at {cvr:.2%} CVR",
        },
        constitution_refs=[],
        guardrails_checked=[],
        triggering_diagnosis="SEARCH_TERM_WINNER",
        triggering_confidence=confidence,
        blocked=False,
        block_reason=None,
        priority=12,
    )


def st_add_002_add_phrase(ctx: RuleContext) -> Optional[Recommendation]:
    """
    Trigger: >=10 conversions AND CVR > campaign avg AND not yet ADDED
    Action:  Add search term as PHRASE match keyword (broader capture)
    Risk:    low
    Note:    Only fires if ST-ADD-001 did NOT fire (CVR not high enough for EXACT)
    """
    st_status = str(ctx.features.get("search_term_status", ""))
    if st_status == "ADDED":
        return None

    conversions = _safe_float(ctx.features.get("conversions_sum"))
    if conversions < 10:
        return None

    cvr = ctx.features.get("cvr")
    if cvr is None:
        return None
    cvr = float(cvr)

    campaign_avg_cvr = _safe_float(ctx.features.get("_campaign_avg_cvr"))

    # Must be above campaign avg but NOT above 1.2x (that's EXACT territory)
    if campaign_avg_cvr > 0:
        if cvr <= campaign_avg_cvr:
            return None
        if cvr > campaign_avg_cvr * 1.2:
            return None  # ST-ADD-001 handles this
    else:
        if cvr <= 0.03:
            return None

    search_term = str(ctx.features.get("search_term", ""))
    clicks = _safe_float(ctx.features.get("clicks_sum"))
    cost_dollars = _safe_float(ctx.features.get("cost_micros_sum")) / 1_000_000

    confidence = min(1.0, 0.35 + 0.35 * min(1.0, conversions / 20)
                     + 0.30 * min(1.0, cvr / 0.10))

    return Recommendation(
        rule_id="ST-ADD-002",
        rule_name="Add Search Term as PHRASE Keyword",
        entity_type="SEARCH_TERM",
        entity_id=search_term,
        action_type="add_keyword_phrase",
        risk_tier="low",
        confidence=confidence,
        current_value=None,
        recommended_value=None,
        change_pct=None,
        rationale=(
            f"Search term '{search_term}' has {conversions:.0f} conversions at "
            f"CVR {cvr:.2%}. Add as PHRASE match to capture similar variations."
        ),
        evidence={
            "search_term": search_term,
            "campaign_id": str(ctx.features.get("campaign_id")),
            "campaign_name": ctx.features.get("campaign_name", "Unknown"),
            "ad_group_id": str(ctx.features.get("ad_group_id")),
            "triggering_keyword": ctx.features.get("keyword_text", ""),
            "cvr": round(cvr, 4),
            "campaign_avg_cvr": round(campaign_avg_cvr, 4),
            "conversions": conversions,
            "clicks": clicks,
            "cost_dollars": round(cost_dollars, 2),
            "recommended_match_type": "PHRASE",
            "expected_impact": f"Capture variations of {conversions:.0f}-converting term",
        },
        constitution_refs=[],
        guardrails_checked=[],
        triggering_diagnosis="SEARCH_TERM_WINNER",
        triggering_confidence=confidence,
        blocked=False,
        block_reason=None,
        priority=18,
    )


# ═══════════════════════════════════════════════════════════════
# SEARCH TERM NEGATIVE RULES
# ═══════════════════════════════════════════════════════════════


def st_neg_001_wasted_spend(ctx: RuleContext) -> Optional[Recommendation]:
    """
    Trigger: >$50 spend in 30d AND zero conversions AND >=5 clicks
    Action:  Add as campaign-level negative keyword (EXACT)
    Risk:    low
    """
    cost_micros = _safe_float(ctx.features.get("cost_micros_sum"))
    conversions = _safe_float(ctx.features.get("conversions_sum"))
    clicks = _safe_float(ctx.features.get("clicks_sum"))

    cost_dollars = cost_micros / 1_000_000

    if cost_dollars < 50:
        return None
    if conversions > 0:
        return None
    if clicks < 5:
        return None

    search_term = str(ctx.features.get("search_term", ""))
    confidence = min(1.0, 0.55 + 0.25 * min(1.0, cost_dollars / 200)
                     + 0.20 * min(1.0, clicks / 30))

    return Recommendation(
        rule_id="ST-NEG-001",
        rule_name="Negative Keyword — Wasted Spend",
        entity_type="SEARCH_TERM",
        entity_id=search_term,
        action_type="add_negative_exact",
        risk_tier="low",
        confidence=confidence,
        current_value=None,
        recommended_value=None,
        change_pct=None,
        rationale=(
            f"Search term '{search_term}' spent ${cost_dollars:.0f} in 30d with "
            f"zero conversions ({clicks:.0f} clicks). Add as negative keyword."
        ),
        evidence={
            "search_term": search_term,
            "campaign_id": str(ctx.features.get("campaign_id")),
            "campaign_name": ctx.features.get("campaign_name", "Unknown"),
            "ad_group_id": str(ctx.features.get("ad_group_id")),
            "triggering_keyword": ctx.features.get("keyword_text", ""),
            "cost_dollars": round(cost_dollars, 2),
            "clicks": clicks,
            "conversions": conversions,
            "negative_level": "CAMPAIGN",
            "negative_match_type": "EXACT",
            "expected_impact": f"Save ${cost_dollars:.0f}/month",
        },
        constitution_refs=[],
        guardrails_checked=[],
        triggering_diagnosis="SEARCH_TERM_NEGATIVE",
        triggering_confidence=confidence,
        blocked=False,
        block_reason=None,
        priority=9,
    )


def st_neg_002_high_cpc_low_cvr(ctx: RuleContext) -> Optional[Recommendation]:
    """
    Trigger: CPC > 2x campaign avg CPC AND CVR < 1% AND >=10 clicks AND <=1 conversion
    Action:  Add as campaign-level negative keyword (EXACT)
    Risk:    low
    Note:    Catches competitor brand terms, expensive irrelevant terms
    """
    clicks = _safe_float(ctx.features.get("clicks_sum"))
    conversions = _safe_float(ctx.features.get("conversions_sum"))
    cost_micros = _safe_float(ctx.features.get("cost_micros_sum"))

    if clicks < 10 or conversions > 1:
        return None

    cvr = ctx.features.get("cvr")
    if cvr is not None and float(cvr) >= 0.01:
        return None

    # CPC check vs campaign avg
    cpc = cost_micros / clicks if clicks > 0 else 0
    campaign_avg_cpc = _safe_float(ctx.features.get("_campaign_avg_cpc"))
    if campaign_avg_cpc <= 0:
        return None
    if cpc < campaign_avg_cpc * 2.0:
        return None

    search_term = str(ctx.features.get("search_term", ""))
    cost_dollars = cost_micros / 1_000_000
    cpc_dollars = cpc / 1_000_000

    confidence = min(1.0, 0.50 + 0.25 * min(1.0, cost_dollars / 100)
                     + 0.25 * min(1.0, (cpc / campaign_avg_cpc - 2.0) / 2.0))

    return Recommendation(
        rule_id="ST-NEG-002",
        rule_name="Negative Keyword — High CPC Low CVR",
        entity_type="SEARCH_TERM",
        entity_id=search_term,
        action_type="add_negative_exact",
        risk_tier="low",
        confidence=confidence,
        current_value=None,
        recommended_value=None,
        change_pct=None,
        rationale=(
            f"Search term '{search_term}' has high CPC ${cpc_dollars:.2f} "
            f"(2x+ campaign avg) with CVR <1%. Likely competitor or irrelevant term."
        ),
        evidence={
            "search_term": search_term,
            "campaign_id": str(ctx.features.get("campaign_id")),
            "campaign_name": ctx.features.get("campaign_name", "Unknown"),
            "cpc_micros": cpc,
            "campaign_avg_cpc_micros": campaign_avg_cpc,
            "cpc_ratio": round(cpc / campaign_avg_cpc, 2),
            "cvr": float(cvr) if cvr else 0,
            "clicks": clicks,
            "conversions": conversions,
            "cost_dollars": round(cost_dollars, 2),
            "negative_level": "CAMPAIGN",
            "negative_match_type": "EXACT",
            "expected_impact": f"Block expensive low-quality traffic",
        },
        constitution_refs=[],
        guardrails_checked=[],
        triggering_diagnosis="SEARCH_TERM_NEGATIVE",
        triggering_confidence=confidence,
        blocked=False,
        block_reason=None,
        priority=11,
    )


def st_neg_003_low_relevance(ctx: RuleContext) -> Optional[Recommendation]:
    """
    Trigger: >$20 spend in 30d AND zero conversions AND CTR < 1%
    Action:  Add as campaign-level negative keyword (EXACT)
    Risk:    low
    Note:    Lower spend threshold but combined with low CTR = clearly irrelevant
    """
    cost_micros = _safe_float(ctx.features.get("cost_micros_sum"))
    conversions = _safe_float(ctx.features.get("conversions_sum"))
    clicks = _safe_float(ctx.features.get("clicks_sum"))
    impressions = _safe_float(ctx.features.get("impressions_sum"))

    cost_dollars = cost_micros / 1_000_000

    if cost_dollars < 20:
        return None
    if conversions > 0:
        return None
    if impressions < 100:
        return None

    ctr = clicks / impressions if impressions > 0 else 0
    if ctr >= 0.01:
        return None

    # Don't double-fire with ST-NEG-001 (that has $50 threshold)
    if cost_dollars >= 50 and clicks >= 5:
        return None

    search_term = str(ctx.features.get("search_term", ""))
    confidence = min(1.0, 0.45 + 0.30 * min(1.0, cost_dollars / 100)
                     + 0.25 * (1.0 - ctr / 0.01))

    return Recommendation(
        rule_id="ST-NEG-003",
        rule_name="Negative Keyword — Low Relevance",
        entity_type="SEARCH_TERM",
        entity_id=search_term,
        action_type="add_negative_exact",
        risk_tier="low",
        confidence=confidence,
        current_value=None,
        recommended_value=None,
        change_pct=None,
        rationale=(
            f"Search term '{search_term}' has CTR {ctr:.2%} with zero conversions "
            f"and ${cost_dollars:.0f} spend. Low relevance — add as negative."
        ),
        evidence={
            "search_term": search_term,
            "campaign_id": str(ctx.features.get("campaign_id")),
            "campaign_name": ctx.features.get("campaign_name", "Unknown"),
            "ctr": round(ctr, 4),
            "impressions": impressions,
            "clicks": clicks,
            "conversions": conversions,
            "cost_dollars": round(cost_dollars, 2),
            "negative_level": "CAMPAIGN",
            "negative_match_type": "EXACT",
            "expected_impact": f"Block irrelevant traffic (CTR {ctr:.2%})",
        },
        constitution_refs=[],
        guardrails_checked=[],
        triggering_diagnosis="SEARCH_TERM_NEGATIVE",
        triggering_confidence=confidence,
        blocked=False,
        block_reason=None,
        priority=14,
    )


# ═══════════════════════════════════════════════════════════════
# KEYWORD REVIEW RULES (flag for human review, no automated action)
# ═══════════════════════════════════════════════════════════════


def kw_review_001_low_qs(ctx: RuleContext) -> Optional[Recommendation]:
    """
    Trigger: QS <= 3 AND NOT triggering KW-PAUSE-003 (i.e., CPA is acceptable)
    Action:  Flag for review (ad copy, landing page, keyword relevance)
    Risk:    low (review only)
    """
    quality_score = ctx.features.get("quality_score")
    if quality_score is None or int(quality_score) > 3:
        return None

    qs = int(quality_score)

    # Skip if this would be caught by KW-PAUSE-003 (QS<=3 + CPA>1.5x)
    target_cpa_micros = _target_cpa_micros(ctx.config)
    if target_cpa_micros > 0:
        cpa_w30 = _safe_float(ctx.features.get("cpa_w30"))
        if cpa_w30 > 0 and cpa_w30 / target_cpa_micros > 1.5:
            clicks_w30 = _safe_float(ctx.features.get("clicks_w30_sum"))
            if clicks_w30 >= 15:
                return None  # KW-PAUSE-003 handles this

    keyword_id = str(ctx.features.get("keyword_id"))
    keyword_text = ctx.features.get("keyword_text", "")

    return Recommendation(
        rule_id="KW-REVIEW-001",
        rule_name="Review Keyword — Low Quality Score",
        entity_type="KEYWORD",
        entity_id=keyword_id,
        action_type="keyword_review",
        risk_tier="low",
        confidence=0.55,
        current_value=None,
        recommended_value=None,
        change_pct=None,
        rationale=(
            f"Keyword '{keyword_text}' has QS={qs}. Review ad relevance, "
            f"landing page experience, and keyword-to-ad alignment."
        ),
        evidence={
            "keyword_text": keyword_text,
            "match_type": ctx.features.get("match_type", ""),
            "campaign_id": str(ctx.features.get("campaign_id")),
            "campaign_name": ctx.features.get("campaign_name", "Unknown"),
            "quality_score": qs,
            "qs_creative": ctx.features.get("quality_score_creative"),
            "qs_landing_page": ctx.features.get("quality_score_landing_page"),
            "qs_relevance": ctx.features.get("quality_score_relevance"),
            "expected_impact": "Improve QS to reduce CPC and improve ad rank",
        },
        constitution_refs=[],
        guardrails_checked=[],
        triggering_diagnosis="KEYWORD_LOW_QS",
        triggering_confidence=0.55,
        blocked=False,
        block_reason=None,
        priority=40,
    )


def kw_review_002_low_ctr(ctx: RuleContext) -> Optional[Recommendation]:
    """
    Trigger: CTR (7d) < 70% of campaign avg CTR AND >=500 impressions
    Action:  Flag for review (ad copy, keyword relevance)
    Risk:    low (review only)
    """
    ctr_w7 = _safe_float(ctx.features.get("ctr_w7"))
    impr_w7 = _safe_float(ctx.features.get("impressions_w7_sum"))
    campaign_avg_ctr = _safe_float(ctx.features.get("_campaign_avg_ctr"))

    if ctr_w7 <= 0 or impr_w7 < 500 or campaign_avg_ctr <= 0:
        return None

    threshold = campaign_avg_ctr * 0.70
    if ctr_w7 >= threshold:
        return None

    ctr_gap_pct = (campaign_avg_ctr - ctr_w7) / campaign_avg_ctr

    keyword_id = str(ctx.features.get("keyword_id"))
    keyword_text = ctx.features.get("keyword_text", "")

    return Recommendation(
        rule_id="KW-REVIEW-002",
        rule_name="Review Keyword — Low CTR",
        entity_type="KEYWORD",
        entity_id=keyword_id,
        action_type="keyword_review",
        risk_tier="low",
        confidence=min(1.0, 0.40 + 0.30 * min(1.0, ctr_gap_pct / 0.50)
                       + 0.30 * min(1.0, impr_w7 / 2000)),
        current_value=None,
        recommended_value=None,
        change_pct=None,
        rationale=(
            f"Keyword '{keyword_text}' CTR {ctr_w7:.2%} is {ctr_gap_pct:.0%} below "
            f"campaign average {campaign_avg_ctr:.2%}. Review ad copy relevance."
        ),
        evidence={
            "keyword_text": keyword_text,
            "match_type": ctx.features.get("match_type", ""),
            "campaign_id": str(ctx.features.get("campaign_id")),
            "campaign_name": ctx.features.get("campaign_name", "Unknown"),
            "ctr_w7": round(ctr_w7, 4),
            "campaign_avg_ctr": round(campaign_avg_ctr, 4),
            "ctr_gap_pct": round(ctr_gap_pct, 2),
            "impressions_w7": impr_w7,
            "expected_impact": "Improve CTR to campaign average or better",
        },
        constitution_refs=[],
        guardrails_checked=[],
        triggering_diagnosis="KEYWORD_LOW_CTR",
        triggering_confidence=0.50,
        blocked=False,
        block_reason=None,
        priority=45,
    )


def kw_review_003_match_type_tighten(ctx: RuleContext) -> Optional[Recommendation]:
    """
    Trigger: BROAD match keyword with good performance (CVR > campaign avg,
             >=30 clicks/30d, >=5 conversions/30d)
    Action:  Flag for review — consider tightening to PHRASE or EXACT
    Risk:    med (match type changes require human judgment)
    """
    match_type = str(ctx.features.get("match_type", ""))
    if match_type != "BROAD":
        return None

    clicks_w30 = _safe_float(ctx.features.get("clicks_w30_sum"))
    conv_w30 = _safe_float(ctx.features.get("conversions_w30_sum"))
    cvr_w30 = _safe_float(ctx.features.get("cvr_w30"))
    campaign_avg_cvr = _safe_float(ctx.features.get("_campaign_avg_cvr"))

    if clicks_w30 < 30 or conv_w30 < 5:
        return None
    if cvr_w30 <= 0 or campaign_avg_cvr <= 0:
        return None
    if cvr_w30 < campaign_avg_cvr:
        return None

    keyword_id = str(ctx.features.get("keyword_id"))
    keyword_text = ctx.features.get("keyword_text", "")

    return Recommendation(
        rule_id="KW-REVIEW-003",
        rule_name="Review Match Type — Consider Tightening",
        entity_type="KEYWORD",
        entity_id=keyword_id,
        action_type="keyword_review_match_type",
        risk_tier="med",
        confidence=0.50,
        current_value=None,
        recommended_value=None,
        change_pct=None,
        rationale=(
            f"BROAD keyword '{keyword_text}' is performing well "
            f"(CVR {cvr_w30:.2%} vs campaign avg {campaign_avg_cvr:.2%}). "
            f"Consider tightening to PHRASE or EXACT to reduce irrelevant matches."
        ),
        evidence={
            "keyword_text": keyword_text,
            "match_type": match_type,
            "campaign_id": str(ctx.features.get("campaign_id")),
            "campaign_name": ctx.features.get("campaign_name", "Unknown"),
            "cvr_w30": round(cvr_w30, 4),
            "campaign_avg_cvr": round(campaign_avg_cvr, 4),
            "clicks_w30": clicks_w30,
            "conversions_w30": conv_w30,
            "expected_impact": "Reduce wasted clicks while preserving conversions",
        },
        constitution_refs=[],
        guardrails_checked=[],
        triggering_diagnosis="MATCH_TYPE_REVIEW",
        triggering_confidence=0.50,
        blocked=False,
        block_reason=None,
        priority=45,
    )


# ═══════════════════════════════════════════════════════════════
# Rule registries
# ═══════════════════════════════════════════════════════════════

KEYWORD_RULES = [
    kw_pause_003_low_qs_high_cpa,   # highest priority (hard rule)
    kw_pause_001_wasted_spend,
    kw_pause_002_chronic_underperformer,
    kw_bid_001_reduce_high_cpa,
    kw_bid_002_increase_low_cpa,
    kw_bid_003_hold_low_data,
    kw_review_001_low_qs,
    kw_review_002_low_ctr,
    kw_review_003_match_type_tighten,
]

SEARCH_TERM_RULES = [
    st_neg_001_wasted_spend,
    st_neg_002_high_cpc_low_cvr,
    st_neg_003_low_relevance,
    st_add_001_add_exact,
    st_add_002_add_phrase,
]

ALL_KEYWORD_RULES = KEYWORD_RULES + SEARCH_TERM_RULES
