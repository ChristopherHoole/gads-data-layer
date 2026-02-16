"""
Ad Optimization Rules - Chat 11
12 rules for ad-level optimization decisions.

Categories:
- Pause Ads (4 rules): Low CTR, Low CVR, Poor RSA strength, Duplicates
- Review/Flag (4 rules): Creative refresh, RSA optimization, A/B test, CTR/CVR mismatch
- Asset Performance (3 rules): Winning headlines, winning descriptions, low-performing assets
- Ad Group (1 rule): Too few ads

All rules follow Constitution guardrails:
- Data thresholds enforced
- Max 5 ads paused per ad group per day
- Never pause if <2 active ads remain
- Review over pause when uncertain
"""

from typing import Optional, List, Dict
from dataclasses import dataclass


@dataclass
class RuleContext:
    """Context passed to each rule."""
    features: Dict  # Ad feature dict
    config: object  # Client config
    ad_group_ad_count: int  # Total active ads in ad group
    paused_today_count: int  # Ads already paused today in this ad group


@dataclass
class Recommendation:
    """Rule recommendation output."""
    rule_id: str
    rule_name: str
    entity_type: str  # 'ad', 'ad_group'
    entity_id: int
    action_type: str  # 'pause_ad', 'review_ad', 'asset_insight', 'review_ad_group'
    risk_tier: str  # 'low', 'med', 'high'
    confidence: float  # 0.0 to 1.0
    change_pct: Optional[float]  # None for non-numeric changes
    priority: int  # 1-100, higher = more important
    rationale: str
    evidence: Dict
    campaign_name: Optional[str] = None
    ad_group_name: Optional[str] = None
    current_value: Optional[str] = None
    recommended_value: Optional[str] = None


def _safe_len(arr) -> int:
    """Safely get length of array (handles None and numpy arrays)."""
    if arr is None:
        return 0
    try:
        return len(arr)
    except:
        return 0


# ============================================================================
# PAUSE ADS RULES (4)
# ============================================================================

def rule_ad_pause_001_low_ctr(ctx: RuleContext) -> Optional[Recommendation]:
    """
    AD-PAUSE-001: Pause ads with low CTR
    
    Trigger: CTR < ad group avg - 30%, ≥1000 impressions (30d)
    Risk: Low (clear underperformer)
    """
    f = ctx.features
    
    # Data gates
    if f['impressions_30d'] < 1000:
        return None  # Insufficient data
    
    if f['low_data_flag']:
        return None
    
    # Constitution: Never pause if <2 active ads would remain
    if ctx.ad_group_ad_count <= 2:
        return None
    
    # Constitution: Max 5 ads paused per ad group per day
    if ctx.paused_today_count >= 5:
        return None
    
    # Check CTR vs ad group average
    ctr_vs_group = f['ctr_vs_ad_group']
    
    if ctr_vs_group >= 0.7:  # Not low enough
        return None
    
    # Calculate gap
    ctr_gap = (1 - ctr_vs_group) * 100  # % below average
    ag_avg_ctr = f['_ad_group_avg_ctr_30d']
    
    # Confidence: Higher gap = higher confidence
    confidence = min(0.9, 0.5 + (ctr_gap / 100))
    
    return Recommendation(
        rule_id='AD-PAUSE-001',
        rule_name='Pause Low CTR Ad',
        entity_type='ad',
        entity_id=f['ad_id'],
        action_type='pause_ad',
        risk_tier='low',
        confidence=confidence,
        change_pct=None,
        priority=70,
        rationale=f"Ad CTR {f['ctr_30d']:.2%} is {ctr_gap:.0f}% below ad group average {ag_avg_ctr:.2%}. Pausing underperforming ad.",
        evidence={
            'ad_ctr_30d': f['ctr_30d'],
            'ad_group_avg_ctr': ag_avg_ctr,
            'ctr_ratio': ctr_vs_group,
            'impressions_30d': f['impressions_30d'],
            'clicks_30d': f['clicks_30d'],
        },
        campaign_name=f['campaign_name'],
        ad_group_name=f['ad_group_name'],
        current_value='ENABLED',
        recommended_value='PAUSED',
    )


def rule_ad_pause_002_low_cvr(ctx: RuleContext) -> Optional[Recommendation]:
    """
    AD-PAUSE-002: Pause ads with low CVR
    
    Trigger: CVR < ad group avg - 20%, ≥100 clicks (30d)
    Risk: Medium (could be landing page issue, not ad)
    """
    f = ctx.features
    
    # Data gates
    if f['clicks_30d'] < 100:
        return None
    
    if f['low_data_flag']:
        return None
    
    # Constitution: Never pause if <2 active ads would remain
    if ctx.ad_group_ad_count <= 2:
        return None
    
    # Constitution: Max 5 ads paused per ad group per day
    if ctx.paused_today_count >= 5:
        return None
    
    # Check CVR vs ad group average
    cvr_vs_group = f['cvr_vs_ad_group']
    
    if cvr_vs_group >= 0.8:  # Not low enough
        return None
    
    # Calculate gap
    cvr_gap = (1 - cvr_vs_group) * 100
    ag_avg_cvr = f['_ad_group_avg_cvr_30d']
    
    # Confidence: Lower than CTR rule because could be landing page
    confidence = min(0.8, 0.4 + (cvr_gap / 100))
    
    return Recommendation(
        rule_id='AD-PAUSE-002',
        rule_name='Pause Low CVR Ad',
        entity_type='ad',
        entity_id=f['ad_id'],
        action_type='pause_ad',
        risk_tier='med',  # Medium because might be landing page issue
        confidence=confidence,
        change_pct=None,
        priority=60,
        rationale=f"Ad CVR {f['cvr_30d']:.2%} is {cvr_gap:.0f}% below ad group average {ag_avg_cvr:.2%}. Consider pausing or reviewing landing page.",
        evidence={
            'ad_cvr_30d': f['cvr_30d'],
            'ad_group_avg_cvr': ag_avg_cvr,
            'cvr_ratio': cvr_vs_group,
            'clicks_30d': f['clicks_30d'],
            'conversions_30d': f['conversions_30d'],
        },
        campaign_name=f['campaign_name'],
        ad_group_name=f['ad_group_name'],
        current_value='ENABLED',
        recommended_value='PAUSED',
    )


def rule_ad_pause_003_poor_rsa_strength(ctx: RuleContext) -> Optional[Recommendation]:
    """
    AD-PAUSE-003: Pause RSA ads with POOR strength
    
    Trigger: Ad strength = POOR, ≥500 impressions (30d)
    Risk: Low (Google provides this metric)
    """
    f = ctx.features
    
    # Only for RSA
    if f['ad_type'] != 'RESPONSIVE_SEARCH_AD':
        return None
    
    # Check ad strength
    if f['ad_strength'] != 'POOR':
        return None
    
    # Data gate
    if f['impressions_30d'] < 500:
        return None
    
    # Constitution: Never pause if <2 active ads would remain
    if ctx.ad_group_ad_count <= 2:
        return None
    
    # Constitution: Max 5 ads paused per ad group per day
    if ctx.paused_today_count >= 5:
        return None
    
    headlines_count = _safe_len(f.get('headlines'))
    descriptions_count = _safe_len(f.get('descriptions'))
    
    return Recommendation(
        rule_id='AD-PAUSE-003',
        rule_name='Pause POOR RSA Strength',
        entity_type='ad',
        entity_id=f['ad_id'],
        action_type='pause_ad',
        risk_tier='low',
        confidence=0.9,  # High confidence - Google provides this
        change_pct=None,
        priority=65,
        rationale=f"RSA has POOR ad strength with {headlines_count} headlines and {descriptions_count} descriptions. Google recommends improvement.",
        evidence={
            'ad_strength': 'POOR',
            'ad_type': 'RESPONSIVE_SEARCH_AD',
            'impressions_30d': f['impressions_30d'],
            'headlines_count': headlines_count,
            'descriptions_count': descriptions_count,
        },
        campaign_name=f['campaign_name'],
        ad_group_name=f['ad_group_name'],
        current_value='ENABLED',
        recommended_value='PAUSED',
    )


def rule_ad_pause_004_duplicate(ctx: RuleContext) -> Optional[Recommendation]:
    """
    AD-PAUSE-004: Pause duplicate/similar ads
    
    Trigger: Multiple ads in ad group with identical headlines (RSA only)
    Risk: Low (duplicate testing not valuable)
    
    Note: This requires comparing ads in the same ad group.
    For simplicity, we'll flag RSAs with generic/duplicate headlines.
    Full implementation would require loading all ads in ad group.
    """
    f = ctx.features
    
    # Only for RSA
    if f['ad_type'] != 'RESPONSIVE_SEARCH_AD':
        return None
    
    # Check if headlines are too generic (simplified duplicate detection)
    # In real implementation, would compare against other ads in ad group
    headlines = f.get('headlines')
    if headlines is None or _safe_len(headlines) == 0:
        return None
    
    # For now, skip this rule - requires cross-ad comparison
    # Would implement in full system by loading all ad group ads
    return None


# ============================================================================
# REVIEW/FLAG ADS RULES (4)
# ============================================================================

def rule_ad_review_001_creative_refresh(ctx: RuleContext) -> Optional[Recommendation]:
    """
    AD-REVIEW-001: Flag ads for creative refresh
    
    Trigger: Ad age > 180 days, CTR declining
    Risk: Low (review only, no execution)
    """
    f = ctx.features
    
    # Check age
    if f['days_since_creation'] < 180:
        return None
    
    # Check if CTR is declining
    ctr_trend = f['ctr_trend_7d_vs_30d']
    is_declining = ctr_trend < -0.005  # Dropped >0.5 percentage points
    
    if is_declining:
        confidence = 0.7
        rationale = f"Ad is {f['days_since_creation']} days old with declining CTR (trend: {ctr_trend:.2%}). Consider creative refresh."
    else:
        confidence = 0.5
        rationale = f"Ad is {f['days_since_creation']} days old. Consider creative refresh even with stable performance."
    
    return Recommendation(
        rule_id='AD-REVIEW-001',
        rule_name='Flag for Creative Refresh',
        entity_type='ad',
        entity_id=f['ad_id'],
        action_type='review_ad',
        risk_tier='low',
        confidence=confidence,
        change_pct=None,
        priority=40,
        rationale=rationale,
        evidence={
            'days_since_creation': f['days_since_creation'],
            'ctr_trend': ctr_trend,
            'ctr_7d': f['ctr_7d'],
            'ctr_30d': f['ctr_30d'],
        },
        campaign_name=f['campaign_name'],
        ad_group_name=f['ad_group_name'],
        current_value=None,
        recommended_value='Review for refresh',
    )


def rule_ad_review_002_rsa_optimization(ctx: RuleContext) -> Optional[Recommendation]:
    """
    AD-REVIEW-002: Flag RSA for asset optimization
    
    Trigger: Ad strength = AVERAGE, ≥1000 impressions
    Risk: Low (review only)
    """
    f = ctx.features
    
    # Only for RSA
    if f['ad_type'] != 'RESPONSIVE_SEARCH_AD':
        return None
    
    # Check ad strength
    if f['ad_strength'] != 'AVERAGE':
        return None
    
    # Data gate
    if f['impressions_30d'] < 1000:
        return None
    
    headlines_count = _safe_len(f.get('headlines'))
    descriptions_count = _safe_len(f.get('descriptions'))
    
    return Recommendation(
        rule_id='AD-REVIEW-002',
        rule_name='Flag RSA for Asset Optimization',
        entity_type='ad',
        entity_id=f['ad_id'],
        action_type='review_ad',
        risk_tier='low',
        confidence=0.7,
        change_pct=None,
        priority=50,
        rationale=f"RSA has AVERAGE ad strength. Consider adding more diverse headlines/descriptions to reach GOOD or EXCELLENT.",
        evidence={
            'ad_strength': 'AVERAGE',
            'impressions_30d': f['impressions_30d'],
            'headlines_count': headlines_count,
            'descriptions_count': descriptions_count,
            'ctr_30d': f['ctr_30d'],
        },
        campaign_name=f['campaign_name'],
        ad_group_name=f['ad_group_name'],
        current_value=f'AVERAGE ({headlines_count}H, {descriptions_count}D)',
        recommended_value='Optimize to GOOD/EXCELLENT',
    )


def rule_ad_review_003_ab_test_opportunity(ctx: RuleContext) -> Optional[Recommendation]:
    """
    AD-REVIEW-003: Flag ad group for A/B testing
    
    Trigger: < 3 ads in ad group, good performance
    Risk: Low (suggestion only)
    """
    f = ctx.features
    
    # Check ad count in ad group
    if ctx.ad_group_ad_count >= 3:
        return None
    
    # Check if current ads are performing well
    if f['ctr_vs_ad_group'] < 0.9 or f['cvr_vs_ad_group'] < 0.9:
        return None  # Current ads not performing well
    
    # Need sufficient data
    if f['impressions_30d'] < 1000:
        return None
    
    return Recommendation(
        rule_id='AD-REVIEW-003',
        rule_name='Flag for A/B Test Opportunity',
        entity_type='ad_group',
        entity_id=f['ad_group_id'],
        action_type='review_ad_group',
        risk_tier='low',
        confidence=0.6,
        change_pct=None,
        priority=30,
        rationale=f"Ad group has only {ctx.ad_group_ad_count} active ads. Consider creating variations to test different messaging.",
        evidence={
            'ad_group_ad_count': ctx.ad_group_ad_count,
            'current_ad_ctr': f['ctr_30d'],
            'current_ad_cvr': f['cvr_30d'],
        },
        campaign_name=f['campaign_name'],
        ad_group_name=f['ad_group_name'],
        current_value=f'{ctx.ad_group_ad_count} ads',
        recommended_value='Add test variations',
    )


def rule_ad_review_004_ctr_cvr_mismatch(ctx: RuleContext) -> Optional[Recommendation]:
    """
    AD-REVIEW-004: Flag CTR/CVR mismatch (landing page issue)
    
    Trigger: High CTR but low CVR (landing page problem, not ad problem)
    Risk: Low (informational)
    """
    f = ctx.features
    
    # Need sufficient data
    if f['clicks_30d'] < 100:
        return None
    
    # Check for high CTR, low CVR
    high_ctr = f['ctr_vs_ad_group'] > 1.2  # 20% above avg
    low_cvr = f['cvr_vs_ad_group'] < 0.8   # 20% below avg
    
    if not (high_ctr and low_cvr):
        return None
    
    return Recommendation(
        rule_id='AD-REVIEW-004',
        rule_name='Flag CTR/CVR Mismatch',
        entity_type='ad',
        entity_id=f['ad_id'],
        action_type='review_ad',
        risk_tier='low',
        confidence=0.8,
        change_pct=None,
        priority=55,
        rationale=f"Ad has high CTR ({f['ctr_30d']:.2%}) but low CVR ({f['cvr_30d']:.2%}). Issue likely with landing page, not ad creative.",
        evidence={
            'ctr_30d': f['ctr_30d'],
            'cvr_30d': f['cvr_30d'],
            'ctr_vs_group': f['ctr_vs_ad_group'],
            'cvr_vs_group': f['cvr_vs_ad_group'],
            'clicks_30d': f['clicks_30d'],
            'conversions_30d': f['conversions_30d'],
        },
        campaign_name=f['campaign_name'],
        ad_group_name=f['ad_group_name'],
        current_value=f"CTR {f['ctr_30d']:.2%}, CVR {f['cvr_30d']:.2%}",
        recommended_value='Review landing page',
    )


# ============================================================================
# ASSET PERFORMANCE RULES (3)
# ============================================================================

def rule_ad_asset_001_winning_headlines(ctx: RuleContext) -> Optional[Recommendation]:
    """
    AD-ASSET-001: Identify winning headlines (RSA)
    
    Trigger: RSA with high CTR, sufficient impressions
    Risk: Low (informational)
    
    Note: Individual asset performance requires ad_group_ad_asset_view query.
    For now, this flags high-performing RSAs for asset analysis.
    """
    f = ctx.features
    
    # Only for RSA
    if f['ad_type'] != 'RESPONSIVE_SEARCH_AD':
        return None
    
    # Check if high performer
    if f['ctr_vs_ad_group'] <= 1.2:  # Not 20% above average
        return None
    
    # Need sufficient data
    if f['impressions_30d'] < 2000:
        return None
    
    headlines = f.get('headlines')
    
    return Recommendation(
        rule_id='AD-ASSET-001',
        rule_name='Analyze Winning Headlines',
        entity_type='ad',
        entity_id=f['ad_id'],
        action_type='asset_insight',
        risk_tier='low',
        confidence=0.7,
        change_pct=None,
        priority=25,
        rationale=f"RSA has high CTR ({f['ctr_30d']:.2%}). Analyze which headlines drive performance for use in other ads.",
        evidence={
            'ctr_30d': f['ctr_30d'],
            'ctr_vs_group': f['ctr_vs_ad_group'],
            'impressions_30d': f['impressions_30d'],
            'headlines_count': _safe_len(headlines),
        },
        campaign_name=f['campaign_name'],
        ad_group_name=f['ad_group_name'],
        current_value=None,
        recommended_value='Review asset report',
    )


def rule_ad_asset_002_winning_descriptions(ctx: RuleContext) -> Optional[Recommendation]:
    """
    AD-ASSET-002: Identify winning descriptions (RSA)
    
    Trigger: RSA with high CVR, sufficient clicks
    Risk: Low (informational)
    """
    f = ctx.features
    
    # Only for RSA
    if f['ad_type'] != 'RESPONSIVE_SEARCH_AD':
        return None
    
    # Check if high CVR
    if f['cvr_vs_ad_group'] <= 1.2:  # Not 20% above average
        return None
    
    # Need sufficient data
    if f['clicks_30d'] < 200:
        return None
    
    descriptions = f.get('descriptions')
    
    return Recommendation(
        rule_id='AD-ASSET-002',
        rule_name='Analyze Winning Descriptions',
        entity_type='ad',
        entity_id=f['ad_id'],
        action_type='asset_insight',
        risk_tier='low',
        confidence=0.7,
        change_pct=None,
        priority=25,
        rationale=f"RSA has high CVR ({f['cvr_30d']:.2%}). Analyze which descriptions drive conversions for use in other ads.",
        evidence={
            'cvr_30d': f['cvr_30d'],
            'cvr_vs_group': f['cvr_vs_ad_group'],
            'clicks_30d': f['clicks_30d'],
            'conversions_30d': f['conversions_30d'],
            'descriptions_count': _safe_len(descriptions),
        },
        campaign_name=f['campaign_name'],
        ad_group_name=f['ad_group_name'],
        current_value=None,
        recommended_value='Review asset report',
    )


def rule_ad_asset_003_low_performing_assets(ctx: RuleContext) -> Optional[Recommendation]:
    """
    AD-ASSET-003: Flag RSA with low-performing assets
    
    Trigger: RSA with low CTR/CVR, sufficient data
    Risk: Low (review asset performance)
    
    Note: Full implementation requires asset-level data.
    For now, flags underperforming RSAs for asset review.
    """
    f = ctx.features
    
    # Only for RSA
    if f['ad_type'] != 'RESPONSIVE_SEARCH_AD':
        return None
    
    # Check if underperforming
    if f['ctr_vs_ad_group'] >= 0.8 and f['cvr_vs_ad_group'] >= 0.8:
        return None  # Not underperforming enough
    
    # Need sufficient data
    if f['impressions_30d'] < 1000:
        return None
    
    return Recommendation(
        rule_id='AD-ASSET-003',
        rule_name='Flag Low-Performing Assets',
        entity_type='ad',
        entity_id=f['ad_id'],
        action_type='asset_insight',
        risk_tier='low',
        confidence=0.6,
        change_pct=None,
        priority=35,
        rationale=f"RSA underperforming (CTR {f['ctr_vs_ad_group']:.0%} of group, CVR {f['cvr_vs_ad_group']:.0%} of group). Review asset performance for improvements.",
        evidence={
            'ctr_30d': f['ctr_30d'],
            'cvr_30d': f['cvr_30d'],
            'ctr_vs_group': f['ctr_vs_ad_group'],
            'cvr_vs_group': f['cvr_vs_ad_group'],
            'impressions_30d': f['impressions_30d'],
        },
        campaign_name=f['campaign_name'],
        ad_group_name=f['ad_group_name'],
        current_value=None,
        recommended_value='Review asset report',
    )


# ============================================================================
# AD GROUP RULES (1)
# ============================================================================

def rule_adgroup_review_001_too_few_ads(ctx: RuleContext) -> Optional[Recommendation]:
    """
    ADGROUP-REVIEW-001: Flag ad groups with too few ads
    
    Trigger: < 3 ads in ad group
    Risk: Low (suggestion only)
    """
    f = ctx.features
    
    # Check ad count
    if ctx.ad_group_ad_count >= 3:
        return None
    
    return Recommendation(
        rule_id='ADGROUP-REVIEW-001',
        rule_name='Flag Ad Group with Too Few Ads',
        entity_type='ad_group',
        entity_id=f['ad_group_id'],
        action_type='review_ad_group',
        risk_tier='low',
        confidence=0.8,
        change_pct=None,
        priority=45,
        rationale=f"Ad group has only {ctx.ad_group_ad_count} active ads. Google recommends 3+ ads per ad group for optimal rotation and testing.",
        evidence={
            'ad_group_ad_count': ctx.ad_group_ad_count,
        },
        campaign_name=f['campaign_name'],
        ad_group_name=f['ad_group_name'],
        current_value=f'{ctx.ad_group_ad_count} ads',
        recommended_value='Add more ad variations',
    )


# ============================================================================
# RULE REGISTRY
# ============================================================================

AD_RULES = [
    # Pause ads (4)
    rule_ad_pause_001_low_ctr,
    rule_ad_pause_002_low_cvr,
    rule_ad_pause_003_poor_rsa_strength,
    # rule_ad_pause_004_duplicate,  # Skipped - requires cross-ad comparison
    
    # Review/Flag (4)
    rule_ad_review_001_creative_refresh,
    rule_ad_review_002_rsa_optimization,
    rule_ad_review_003_ab_test_opportunity,
    rule_ad_review_004_ctr_cvr_mismatch,
    
    # Asset performance (3)
    rule_ad_asset_001_winning_headlines,
    rule_ad_asset_002_winning_descriptions,
    rule_ad_asset_003_low_performing_assets,
    
    # Ad group (1)
    rule_adgroup_review_001_too_few_ads,
]


def apply_ad_rules(features: List[Dict], config: object) -> List[Recommendation]:
    """
    Apply all ad rules to a list of ad features.
    
    Args:
        features: List of ad feature dicts
        config: Client config object
    
    Returns:
        List of recommendations
    """
    print(f"[AdRules] Applying {len(AD_RULES)} rules to {len(features)} ads...")
    
    # Group ads by ad group for counting
    ad_group_counts = {}
    for f in features:
        ag_id = f['ad_group_id']
        ad_group_counts[ag_id] = ad_group_counts.get(ag_id, 0) + 1
    
    # Track paused today (simplified - in real system would query change_log)
    paused_today = {}
    
    recommendations = []
    
    for feature in features:
        ag_id = feature['ad_group_id']
        
        # Build context
        ctx = RuleContext(
            features=feature,
            config=config,
            ad_group_ad_count=ad_group_counts.get(ag_id, 1),
            paused_today_count=paused_today.get(ag_id, 0)
        )
        
        # Apply each rule
        for rule_func in AD_RULES:
            rec = rule_func(ctx)
            if rec:
                recommendations.append(rec)
                
                # Track if pause action
                if rec.action_type == 'pause_ad':
                    paused_today[ag_id] = paused_today.get(ag_id, 0) + 1
    
    # Print summary
    print(f"[AdRules] Generated {len(recommendations)} recommendations")
    
    # Count by rule
    rule_counts = {}
    for rec in recommendations:
        rule_counts[rec.rule_id] = rule_counts.get(rec.rule_id, 0) + 1
    
    print("\n[AdRules] Recommendations by rule:")
    for rule_id in sorted(rule_counts.keys()):
        print(f"  {rule_id}: {rule_counts[rule_id]}")
    
    return recommendations


if __name__ == '__main__':
    # Test with dummy features
    print("✅ Ad rules module loaded successfully")
    print(f"✅ {len(AD_RULES)} rules registered")
