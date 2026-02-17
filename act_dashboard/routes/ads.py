"""
Ads page route - ad performance and recommendations.
"""

from flask import Blueprint, render_template, session, current_app
from act_dashboard.auth import login_required
from act_dashboard.routes.shared import get_current_config, get_available_clients
import duckdb

bp = Blueprint('ads', __name__)


@bp.route("/ads")
@login_required
def ads():
    """Ads page - show ad performance and recommendations."""
    config = get_current_config()
    clients = get_available_clients()
    current_client_path = session.get("current_client_config")

    try:
        conn = duckdb.connect(config.db_path)
        try:
            ro_path = config.db_path.replace("warehouse.duckdb", "warehouse_readonly.duckdb")
            conn.execute(f"ATTACH '{ro_path}' AS ro (READ_ONLY);")
        except Exception:
            pass

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
        from act_lighthouse.config import load_client_config

        lh_cfg = load_client_config(current_client_path)
        raw = lh_cfg.raw or {}
        from act_autopilot.models import AutopilotConfig

        targets = raw.get("targets", {})
        ap_config = AutopilotConfig(
            customer_id=lh_cfg.customer_id,
            automation_mode=raw.get("automation_mode", "suggest"),
            risk_tolerance=raw.get("risk_tolerance", "conservative"),
            daily_spend_cap=lh_cfg.spend_caps.daily or 0,
            monthly_spend_cap=lh_cfg.spend_caps.monthly or 0,
            brand_is_protected=False,
            protected_entities=[],
            client_name=lh_cfg.client_id,
            client_type=lh_cfg.client_type or "ecom",
            primary_kpi=lh_cfg.primary_kpi or "roas",
            target_roas=targets.get("target_roas"),
            target_cpa=targets.get("target_cpa", 25),
        )

        recommendations_list = apply_ad_rules(ad_features, ap_config)

        # Convert to dicts
        recommendations = [
            {
                "rule_id": r.rule_id,
                "rule_name": r.rule_name,
                "entity_type": r.entity_type,
                "entity_id": r.entity_id,
                "action_type": r.action_type,
                "risk_tier": r.risk_tier,
                "confidence": r.confidence,
                "priority": r.priority,
                "rationale": r.rationale,
                "campaign_name": r.campaign_name,
                "ad_group_name": r.ad_group_name,
                "current_value": r.current_value,
                "recommended_value": r.recommended_value,
                "evidence": r.evidence if r.evidence else {},
            }
            for r in recommendations_list
        ]
        
        # Add ID enumeration for frontend (needed for execution API)
        for i, rec in enumerate(recommendations):
            rec['id'] = i
        
        # Store in cache for execution API (live recommendations)
        # Using server-side cache instead of session cookies (no size limit!)
        current_app.config['RECOMMENDATIONS_CACHE']['ads'] = recommendations

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
