"""
Ads page route - ad performance and recommendations.
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

bp = Blueprint('ads', __name__)


@bp.route("/ads")
@login_required
def ads():
    """Ads page - show ad performance and recommendations."""
    # Get common page context (replaces 3 lines)
    config, clients, current_client_path = get_page_context()

    try:
        # Get database connection (replaces 5 lines)
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

        # Convert to dicts
        ad_features = ad_features_df.to_dict("records")
        ad_groups = ad_group_perf_df.to_dict("records")

        # Compute summary stats
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

        summary = {
            "total_ads": total_ads,
            "total_ad_groups": total_ad_groups,
            "poor_strength": poor_strength_count,
            "low_data": low_data_count,
            "avg_ctr": avg_ctr,
            "avg_cvr": avg_cvr,
            "snapshot_date": str(latest_date),
        }

        # Get unique campaigns for filter
        campaigns = sorted(set(f["campaign_name"] for f in ad_features))

        # Generate recommendations using ad rules
        from act_autopilot.rules.ad_rules import apply_ad_rules

        # Build AutopilotConfig (replaces 20+ lines)
        ap_config = build_autopilot_config(current_client_path)

        recommendations_list = apply_ad_rules(ad_features, ap_config)

        # Convert to dicts using helper (replaces 15+ lines)
        recommendations = [
            recommendation_to_dict(r, index=i)
            for i, r in enumerate(recommendations_list)
        ]
        
        # Store in cache using helper (replaces 1 line)
        cache_recommendations('ads', recommendations)

        # Group recommendations by category
        pause_recs = [r for r in recommendations if r["action_type"] == "pause_ad"]
        review_recs = [r for r in recommendations if r["action_type"] == "review_ad"]
        asset_recs = [
            r for r in recommendations if r["action_type"] == "asset_insight"
        ]
        adgroup_recs = [
            r for r in recommendations if r["action_type"] == "review_ad_group"
        ]

        conn.close()

        return render_template(
            "ads.html",
            client_name=config.client_name,
            available_clients=clients,
            current_client_config=current_client_path,
            ads=ad_features,
            ad_groups=ad_groups,
            recommendations=recommendations,
            pause_recs=pause_recs,
            review_recs=review_recs,
            asset_recs=asset_recs,
            adgroup_recs=adgroup_recs,
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
