"""
Ads page route - ad performance and recommendations.
Refactored into smaller, focused functions.
"""

from flask import Blueprint, render_template
from act_dashboard.auth import login_required
from act_dashboard.routes.shared import (
    get_page_context,
    get_db_connection,
    build_autopilot_config,
    recommendation_to_dict,
    cache_recommendations
)
from typing import List, Dict, Any, Tuple
import pandas as pd

bp = Blueprint('ads', __name__)


def load_ad_features(conn, latest_date: str) -> Tuple[List[Dict], List[Dict]]:
    """
    Load ad features and ad group performance.
    
    Args:
        conn: Database connection
        latest_date: Latest snapshot date
        
    Returns:
        Tuple of (ad_features, ad_groups)
    """
    # Load ad features
    ad_features_df = conn.execute(
        "SELECT * FROM analytics.ad_features_daily WHERE snapshot_date = ?",
        [latest_date],
    ).fetchdf()

    # Load ad group performance
    ad_group_perf_df = conn.execute(
        "SELECT * FROM ro.analytics.ad_group_daily WHERE snapshot_date = ?",
        [latest_date],
    ).fetchdf()

    ad_features = ad_features_df.to_dict("records")
    ad_groups = ad_group_perf_df.to_dict("records")
    
    return ad_features, ad_groups


def compute_ad_summary(ad_features: List[Dict], ad_groups: List[Dict], ad_features_df: pd.DataFrame, latest_date: str) -> Dict[str, Any]:
    """
    Compute summary statistics for ads.
    
    Args:
        ad_features: List of ad feature dictionaries
        ad_groups: List of ad group dictionaries
        ad_features_df: DataFrame of ad features (for mean calculations)
        latest_date: Snapshot date
        
    Returns:
        Dictionary of summary stats
    """
    total_ads = len(ad_features)
    total_ad_groups = len(ad_groups)

    poor_strength_count = sum(
        1
        for f in ad_features
        if f.get("ad_type") == "RESPONSIVE_SEARCH_AD"
        and f.get("ad_strength") == "POOR"
    )

    low_data_count = sum(1 for f in ad_features if f.get("low_data_flag"))

    avg_ctr = ad_features_df["ctr_30d"].mean() if len(ad_features) > 0 else 0
    avg_cvr = ad_features_df["cvr_30d"].mean() if len(ad_features) > 0 else 0

    return {
        "total_ads": total_ads,
        "total_ad_groups": total_ad_groups,
        "poor_strength": poor_strength_count,
        "low_data": low_data_count,
        "avg_ctr": avg_ctr,
        "avg_cvr": avg_cvr,
        "snapshot_date": str(latest_date),
    }


def extract_campaigns_from_ads(ad_features: List[Dict]) -> List[str]:
    """
    Extract unique campaign names for filter.
    
    Args:
        ad_features: List of ad feature dictionaries
        
    Returns:
        Sorted list of campaign names
    """
    return sorted(set(f["campaign_name"] for f in ad_features))


def generate_ad_recommendations(ad_features: List[Dict], current_client_path: str) -> List[Dict[str, Any]]:
    """
    Generate ad recommendations using ad rules.
    
    Args:
        ad_features: List of ad feature dictionaries
        current_client_path: Path to client config
        
    Returns:
        List of recommendation dictionaries
    """
    from act_autopilot.rules.ad_rules import apply_ad_rules

    # Build AutopilotConfig
    ap_config = build_autopilot_config(current_client_path)

    recommendations_list = apply_ad_rules(ad_features, ap_config)

    # Convert to dicts using helper
    recommendations = [
        recommendation_to_dict(r, index=i)
        for i, r in enumerate(recommendations_list)
    ]
    
    return recommendations


def group_ad_recommendations(recommendations: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Group recommendations by action type.
    
    Args:
        recommendations: List of recommendation dictionaries
        
    Returns:
        Dictionary of grouped recommendations
    """
    return {
        'pause_recs': [r for r in recommendations if r["action_type"] == "pause_ad"],
        'review_recs': [r for r in recommendations if r["action_type"] == "review_ad"],
        'asset_recs': [r for r in recommendations if r["action_type"] == "asset_insight"],
        'adgroup_recs': [r for r in recommendations if r["action_type"] == "review_ad_group"],
    }


@bp.route("/ads")
@login_required
def ads():
    """
    Ads page - show ad performance and recommendations.
    
    Main coordinator function - delegates to helper functions.
    """
    # Get common page context
    config, clients, current_client_path = get_page_context()

    try:
        # Get database connection
        conn = get_db_connection(config)

        # Get latest snapshot date from ad features
        latest_date = conn.execute(
            "SELECT MAX(snapshot_date) FROM analytics.ad_features_daily"
        ).fetchone()[0]

        if not latest_date:
            conn.close()
            return render_template(
                "ads.html",
                client_name=config.client_name,
                available_clients=clients,
                current_client_config=current_client_path,
                error="No ad data available. Run ad features generation first.",
                ads=[],
                ad_groups=[],
                recommendations=[],
                summary={},
            )

        # Load ad data
        ad_features, ad_groups = load_ad_features(conn, latest_date)
        
        # Need DataFrame for summary calculations
        ad_features_df = conn.execute(
            "SELECT * FROM analytics.ad_features_daily WHERE snapshot_date = ?",
            [latest_date],
        ).fetchdf()
        
        conn.close()

        # Compute summary stats
        summary = compute_ad_summary(ad_features, ad_groups, ad_features_df, latest_date)

        # Get unique campaigns for filter
        campaigns = extract_campaigns_from_ads(ad_features)

        # Generate recommendations
        recommendations = generate_ad_recommendations(ad_features, current_client_path)
        
        # Store in cache
        cache_recommendations('ads', recommendations)

        # Group recommendations by category
        grouped = group_ad_recommendations(recommendations)

        return render_template(
            "ads.html",
            client_name=config.client_name,
            available_clients=clients,
            current_client_config=current_client_path,
            ads=ad_features,
            ad_groups=ad_groups,
            recommendations=recommendations,
            pause_recs=grouped['pause_recs'],
            review_recs=grouped['review_recs'],
            asset_recs=grouped['asset_recs'],
            adgroup_recs=grouped['adgroup_recs'],
            summary=summary,
            campaigns=campaigns,
            error=None,
        )

    except Exception as e:
        print(f"[Dashboard] ERROR in /ads route: {e}")
        import traceback
        traceback.print_exc()
        
        return render_template(
            "ads.html",
            client_name=config.client_name,
            available_clients=clients,
            current_client_config=current_client_path,
            error=str(e),
            ads=[],
            ad_groups=[],
            recommendations=[],
            summary={},
        )
