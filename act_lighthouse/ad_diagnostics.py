"""
Ad Diagnostics Module - Chat 11
Generates diagnosis codes for ad performance issues.

Diagnosis Codes:
1. AD_LOW_CTR - CTR < ad group avg - 30%
2. AD_LOW_CVR - CVR < ad group avg - 20%
3. AD_POOR_STRENGTH - RSA with POOR strength
4. AD_STALE - No changes 180+ days
5. AD_LOW_IMPRESSIONS - <1000 impressions/30d
6. AD_HIGH_PERFORMER - CTR + CVR both above avg
"""

from typing import Dict, List, Optional


class Insight:
    """Represents a diagnostic insight."""
    
    def __init__(self, code: str, severity: str, message: str, confidence: float, evidence: Dict):
        self.code = code
        self.severity = severity  # low, med, high
        self.message = message
        self.confidence = confidence  # 0.0 to 1.0
        self.evidence = evidence
    
    def to_dict(self):
        return {
            'code': self.code,
            'severity': self.severity,
            'message': self.message,
            'confidence': self.confidence,
            'evidence': self.evidence
        }


def run_ad_diagnostics(feature: Dict) -> List[Insight]:
    """
    Run diagnostics on a single ad's features.
    
    Args:
        feature: Feature dict from ad_features.py
    
    Returns:
        List of Insight objects
    """
    insights = []
    
    # Extract key metrics
    ad_id = feature['ad_id']
    ad_type = feature['ad_type']
    ad_strength = feature['ad_strength']
    
    impressions_30d = feature['impressions_30d']
    clicks_30d = feature['clicks_30d']
    ctr_30d = feature['ctr_30d']
    cvr_30d = feature['cvr_30d']
    
    ctr_vs_group = feature['ctr_vs_ad_group']
    cvr_vs_group = feature['cvr_vs_ad_group']
    
    ag_avg_ctr = feature['_ad_group_avg_ctr_30d']
    ag_avg_cvr = feature['_ad_group_avg_cvr_30d']
    
    days_since_creation = feature['days_since_creation']
    low_data_flag = feature['low_data_flag']
    
    # DIAGNOSIS 1: AD_LOW_CTR
    # CTR < ad group avg - 30%, ≥1000 impressions
    if impressions_30d >= 1000 and ctr_vs_group < 0.7:  # <70% of ad group avg
        ctr_gap = (1 - ctr_vs_group) * 100  # % below average
        confidence = min(0.9, 0.5 + (ctr_gap / 100))  # Higher gap = higher confidence
        
        insights.append(Insight(
            code='AD_LOW_CTR',
            severity='low',
            message=f'Ad CTR {ctr_30d:.2%} is {ctr_gap:.0f}% below ad group average {ag_avg_ctr:.2%}',
            confidence=confidence,
            evidence={
                'ad_ctr': ctr_30d,
                'ad_group_avg_ctr': ag_avg_ctr,
                'ctr_ratio': ctr_vs_group,
                'impressions_30d': impressions_30d,
                'clicks_30d': clicks_30d
            }
        ))
    
    # DIAGNOSIS 2: AD_LOW_CVR
    # CVR < ad group avg - 20%, ≥100 clicks
    if clicks_30d >= 100 and cvr_vs_group < 0.8:  # <80% of ad group avg
        cvr_gap = (1 - cvr_vs_group) * 100
        confidence = min(0.8, 0.4 + (cvr_gap / 100))
        
        insights.append(Insight(
            code='AD_LOW_CVR',
            severity='med',  # Medium because could be landing page issue
            message=f'Ad CVR {cvr_30d:.2%} is {cvr_gap:.0f}% below ad group average {ag_avg_cvr:.2%}',
            confidence=confidence,
            evidence={
                'ad_cvr': cvr_30d,
                'ad_group_avg_cvr': ag_avg_cvr,
                'cvr_ratio': cvr_vs_group,
                'clicks_30d': clicks_30d,
                'conversions_30d': feature['conversions_30d']
            }
        ))
    
    # DIAGNOSIS 3: AD_POOR_STRENGTH
    # RSA with POOR ad strength, ≥500 impressions
    if ad_type == 'RESPONSIVE_SEARCH_AD' and ad_strength == 'POOR' and impressions_30d >= 500:
        confidence = 0.9  # High confidence - Google provides this metric
        
        insights.append(Insight(
            code='AD_POOR_STRENGTH',
            severity='low',
            message=f'RSA has POOR ad strength with {impressions_30d} impressions in 30 days',
            confidence=confidence,
            evidence={
                'ad_strength': ad_strength,
                'ad_type': ad_type,
                'impressions_30d': impressions_30d,
                'headlines_count': len(feature['headlines']) if feature['headlines'] else 0,
                'descriptions_count': len(feature['descriptions']) if feature['descriptions'] else 0
            }
        ))
    
    # DIAGNOSIS 4: AD_STALE
    # No changes in 180+ days, CTR declining
    if days_since_creation >= 180:
        ctr_trend = feature['ctr_trend_7d_vs_30d']
        is_declining = ctr_trend < -0.005  # CTR dropped >0.5 percentage points
        
        if is_declining:
            confidence = 0.7
            insights.append(Insight(
                code='AD_STALE',
                severity='low',
                message=f'Ad is {days_since_creation} days old with declining CTR (trend: {ctr_trend:.2%})',
                confidence=confidence,
                evidence={
                    'days_since_creation': days_since_creation,
                    'ctr_trend': ctr_trend,
                    'ctr_7d': feature['ctr_7d'],
                    'ctr_30d': ctr_30d
                }
            ))
        else:
            # Still old but stable performance
            confidence = 0.5
            insights.append(Insight(
                code='AD_STALE',
                severity='low',
                message=f'Ad is {days_since_creation} days old (consider refresh even with stable performance)',
                confidence=confidence,
                evidence={
                    'days_since_creation': days_since_creation,
                    'ctr_trend': ctr_trend,
                    'ctr_30d': ctr_30d
                }
            ))
    
    # DIAGNOSIS 5: AD_LOW_IMPRESSIONS
    # <1000 impressions in 30 days (insufficient data)
    if impressions_30d < 1000:
        confidence = 0.8
        
        insights.append(Insight(
            code='AD_LOW_IMPRESSIONS',
            severity='low',
            message=f'Ad has only {impressions_30d} impressions in 30 days (insufficient data for optimization)',
            confidence=confidence,
            evidence={
                'impressions_30d': impressions_30d,
                'clicks_30d': clicks_30d,
                'days_since_creation': days_since_creation,
                'low_data_flag': low_data_flag
            }
        ))
    
    # DIAGNOSIS 6: AD_HIGH_PERFORMER
    # CTR + CVR both above ad group average
    if ctr_vs_group > 1.0 and cvr_vs_group > 1.0 and impressions_30d >= 1000:
        performance_score = (ctr_vs_group + cvr_vs_group) / 2  # Average of ratios
        confidence = min(0.9, 0.5 + ((performance_score - 1) * 0.5))
        
        insights.append(Insight(
            code='AD_HIGH_PERFORMER',
            severity='low',
            message=f'Ad performing above average: CTR {ctr_vs_group:.0%} of group avg, CVR {cvr_vs_group:.0%} of group avg',
            confidence=confidence,
            evidence={
                'ctr_vs_group': ctr_vs_group,
                'cvr_vs_group': cvr_vs_group,
                'performance_score': performance_score,
                'ad_ctr': ctr_30d,
                'ad_cvr': cvr_30d,
                'impressions_30d': impressions_30d,
                'conversions_30d': feature['conversions_30d']
            }
        ))
    
    return insights


def run_diagnostics_batch(features: List[Dict]) -> Dict[int, List[Insight]]:
    """
    Run diagnostics on multiple ads.
    
    Args:
        features: List of feature dicts
    
    Returns:
        Dict mapping ad_id to list of insights
    """
    print(f"[AdDiagnostics] Running diagnostics on {len(features)} ads...")
    
    results = {}
    total_insights = 0
    
    for feature in features:
        ad_id = feature['ad_id']
        insights = run_ad_diagnostics(feature)
        
        if insights:
            results[ad_id] = insights
            total_insights += len(insights)
    
    print(f"[AdDiagnostics] Generated {total_insights} insights for {len(results)} ads")
    
    # Print summary by code
    code_counts = {}
    for insights in results.values():
        for insight in insights:
            code_counts[insight.code] = code_counts.get(insight.code, 0) + 1
    
    print("\n[AdDiagnostics] Insights by code:")
    for code, count in sorted(code_counts.items()):
        print(f"  {code}: {count}")
    
    return results


if __name__ == '__main__':
    # Test with dummy data
    test_feature = {
        'ad_id': 10001,
        'ad_type': 'RESPONSIVE_SEARCH_AD',
        'ad_strength': 'POOR',
        'impressions_30d': 5000,
        'clicks_30d': 150,
        'ctr_30d': 0.03,
        'cvr_30d': 0.02,
        'ctr_vs_ad_group': 0.6,  # 60% of group avg
        'cvr_vs_ad_group': 0.75,  # 75% of group avg
        '_ad_group_avg_ctr_30d': 0.05,
        '_ad_group_avg_cvr_30d': 0.027,
        'days_since_creation': 200,
        'ctr_trend_7d_vs_30d': -0.01,  # Declining
        'ctr_7d': 0.025,
        'conversions_30d': 3.0,
        'low_data_flag': False,
        'headlines': ['Test 1', 'Test 2', 'Test 3'],
        'descriptions': ['Desc 1', 'Desc 2']
    }
    
    insights = run_ad_diagnostics(test_feature)
    
    print(f"\nTest generated {len(insights)} insights:")
    for insight in insights:
        print(f"  {insight.code}: {insight.message} (confidence: {insight.confidence:.2f})")
    
    print("\n✅ Ad diagnostics test complete")
