"""
Shopping page route - shopping campaigns, products, feed quality, and recommendations.
"""

from flask import Blueprint, render_template, session, current_app
from act_dashboard.auth import login_required
from act_dashboard.routes.shared import get_current_config, get_available_clients
import duckdb

bp = Blueprint('shopping', __name__)


@bp.route("/shopping")
@login_required
def shopping():
    """Shopping dashboard with 4 tabs: Campaigns, Products, Feed Quality, Recommendations."""
    try:
        cfg = get_current_config()
        conn = duckdb.connect(cfg.db_path, read_only=True)
        
        # Get latest snapshot date
        snapshot_date = conn.execute("""
            SELECT MAX(snapshot_date) 
            FROM analytics.product_features_daily
            WHERE customer_id = ?
        """, (cfg.customer_id,)).fetchone()
        
        if not snapshot_date or not snapshot_date[0]:
            conn.close()
            return render_template(
                "shopping.html",
                client_name=cfg.client_name,
                available_clients=get_available_clients(),
                current_client_config=session.get("current_client_config"),
                error="No Shopping data available. Run Shopping Lighthouse first.",
            )
        
        snapshot_date = snapshot_date[0]
        
        # ==================== TAB 1: CAMPAIGNS ====================
        campaigns = conn.execute("""
            SELECT 
                campaign_id,
                campaign_name,
                campaign_priority,
                feed_label,
                SUM(impressions) as impressions,
                SUM(clicks) as clicks,
                SUM(cost_micros) as cost_micros,
                SUM(conversions) as conversions,
                SUM(conversions_value) as conv_value
            FROM raw_shopping_campaign_daily
            WHERE customer_id = ?
                AND snapshot_date BETWEEN ? - INTERVAL 30 DAYS AND ?
            GROUP BY campaign_id, campaign_name, campaign_priority, feed_label
            ORDER BY SUM(cost_micros) DESC
        """, (cfg.customer_id, snapshot_date, snapshot_date)).fetchall()
        
        campaigns_list = []
        for c in campaigns:
            cost = float(c[6] or 0) / 1_000_000
            conv_value = float(c[8] or 0) / 1_000_000
            roas = conv_value / cost if cost > 0 else 0
            
            # Map priority
            priority_map = {0: "Low", 1: "Medium", 2: "High"}
            priority_str = priority_map.get(c[2], "Unknown")
            
            campaigns_list.append({
                "campaign_id": c[0],
                "campaign_name": c[1],
                "priority": priority_str,
                "priority_num": c[2],
                "feed_label": c[3] or "None",
                "impressions": int(c[4] or 0),
                "clicks": int(c[5] or 0),
                "cost": cost,
                "conversions": float(c[7] or 0),
                "conv_value": conv_value,
                "roas": roas,
            })
        
        # ==================== TAB 2: PRODUCTS ====================
        products = conn.execute("""
            SELECT 
                product_id,
                product_title,
                product_brand,
                product_category,
                availability,
                impressions_w30_sum,
                clicks_w30_sum,
                cost_micros_w30_sum,
                conversions_w30_sum,
                conversions_value_w30_sum,
                ctr_w30,
                cvr_w30,
                roas_w30,
                stock_out_flag,
                stock_out_days_w30,
                feed_quality_score,
                has_price_mismatch,
                has_disapproval,
                new_product_flag,
                days_live,
                low_data_flag
            FROM analytics.product_features_daily
            WHERE snapshot_date = ?
                AND customer_id = ?
            ORDER BY cost_micros_w30_sum DESC
            LIMIT 200
        """, (snapshot_date, cfg.customer_id)).fetchall()
        
        products_list = []
        for p in products:
            products_list.append({
                "product_id": p[0],
                "product_title": p[1],
                "product_brand": p[2],
                "product_category": p[3],
                "availability": p[4],
                "impressions": int(p[5] or 0),
                "clicks": int(p[6] or 0),
                "cost": float(p[7] or 0) / 1_000_000,
                "conversions": float(p[8] or 0),
                "conv_value": float(p[9] or 0) / 1_000_000,
                "ctr": float(p[10] or 0) * 100,
                "cvr": float(p[11] or 0) * 100,
                "roas": float(p[12] or 0),
                "stock_out_flag": bool(p[13]),
                "stock_out_days": int(p[14] or 0),
                "feed_quality": float(p[15] or 0) * 100,
                "price_mismatch": bool(p[16]),
                "disapproved": bool(p[17]),
                "is_new": bool(p[18]),
                "days_live": int(p[19] or 0),
                "low_data": bool(p[20]),
            })
        
        # ==================== TAB 3: FEED QUALITY ====================
        feed_quality = conn.execute("""
            SELECT 
                approval_status,
                price_mismatch,
                COUNT(*) as count
            FROM raw_product_feed_quality
            WHERE customer_id = ?
                AND snapshot_date = ?
            GROUP BY approval_status, price_mismatch
        """, (cfg.customer_id, snapshot_date)).fetchall()
        
        total_feed_products = sum(f[2] for f in feed_quality)
        approved_count = sum(f[2] for f in feed_quality if f[0] == 'APPROVED' and not f[1])
        disapproved_count = sum(f[2] for f in feed_quality if f[0] == 'DISAPPROVED')
        price_mismatch_count = sum(f[2] for f in feed_quality if f[1])
        
        pct_approved = (approved_count / total_feed_products * 100) if total_feed_products > 0 else 0
        pct_disapproved = (disapproved_count / total_feed_products * 100) if total_feed_products > 0 else 0
        pct_price_mismatch = (price_mismatch_count / total_feed_products * 100) if total_feed_products > 0 else 0
        
        # Get products with issues
        feed_issues = conn.execute("""
            SELECT 
                f.product_id,
                p.product_title,
                p.product_brand,
                f.approval_status,
                f.price_mismatch,
                f.disapproval_reasons
            FROM raw_product_feed_quality f
            LEFT JOIN analytics.product_features_daily p 
                ON f.product_id = p.product_id AND f.customer_id = p.customer_id
            WHERE f.customer_id = ?
                AND f.snapshot_date = ?
                AND (f.approval_status != 'APPROVED' OR f.price_mismatch = TRUE)
            ORDER BY f.approval_status DESC
            LIMIT 100
        """, (cfg.customer_id, snapshot_date)).fetchall()
        
        feed_issues_list = []
        for f in feed_issues:
            issues = []
            if f[3] == 'DISAPPROVED':
                issues.append('Disapproved')
            if f[4]:
                issues.append('Price Mismatch')
            
            feed_issues_list.append({
                "product_id": f[0],
                "product_title": f[1] or "Unknown",
                "product_brand": f[2] or "Unknown",
                "approval_status": f[3],
                "price_mismatch": f[4],
                "disapproval_reasons": f[5] if f[5] else [],
                "issues": ", ".join(issues),
            })
        
        # ==================== TAB 4: RECOMMENDATIONS ====================
        recommendations_list = []
        
        # Try to generate recommendations (may be empty if rules don't fire)
        try:
            from act_autopilot.rules import shopping_rules
            import pandas as pd
            
            products_df = conn.execute("""
                SELECT *
                FROM analytics.product_features_daily
                WHERE customer_id = ?
                    AND snapshot_date = ?
            """, (cfg.customer_id, snapshot_date)).df()
            
            # Call shopping rules (matches keywords/ads pattern)
            if len(products_df) > 0:
                # Convert DataFrame to list of dicts for rules
                product_list = products_df.to_dict('records')
                
                # Apply rules (returns Recommendation objects)
                shop_recs = shopping_rules.apply_rules(product_list, ctx=None)
                
                # Convert Recommendation objects to dicts for cache
                # (matches keywords pattern - explicit field mapping)
                for idx, rec in enumerate(shop_recs):
                    recommendations_list.append({
                        'id': idx,
                        'rule_id': rec.rule_id,
                        'rule_name': rec.rule_name,
                        'entity_type': rec.entity_type,
                        'entity_id': rec.entity_id,
                        'action_type': rec.action_type,
                        'risk_tier': rec.risk_tier,
                        'confidence': rec.confidence or 0.0,
                        'current_value': rec.current_value,
                        'recommended_value': rec.recommended_value,
                        'change_pct': rec.change_pct,
                        'rationale': rec.rationale or '',
                        'campaign_name': rec.campaign_name or '',
                        'blocked': rec.blocked or False,
                        'block_reason': rec.block_reason or '',
                        'priority': rec.priority if rec.priority is not None else 50,
                        'constitution_refs': rec.constitution_refs or [],
                        'guardrails_checked': rec.guardrails_checked or [],
                        'evidence': rec.evidence if rec.evidence else {},
                        'triggering_diagnosis': rec.triggering_diagnosis or '',
                        'triggering_confidence': rec.triggering_confidence or 0.0,
                        'expected_impact': rec.expected_impact or '',
                    })
        except Exception as e:
            # If recommendations fail, continue with empty list
            pass
        
        # Store in cache for execution API (live recommendations)
        # Using server-side cache instead of session cookies (no size limit!)
        current_app.config['RECOMMENDATIONS_CACHE']['shopping'] = recommendations_list
        
        # Summary stats
        total_products = len(products_list)
        total_cost = sum(p["cost"] for p in products_list)
        total_conversions = sum(p["conversions"] for p in products_list)
        total_conv_value = sum(p["conv_value"] for p in products_list)
        avg_roas = total_conv_value / total_cost if total_cost > 0 else 0
        
        out_of_stock = sum(1 for p in products_list if p["stock_out_flag"])
        price_mismatches = sum(1 for p in products_list if p["price_mismatch"])
        disapproved = sum(1 for p in products_list if p["disapproved"])
        feed_issues_count = out_of_stock + price_mismatches + disapproved
        
        conn.close()
        
        return render_template(
            "shopping.html",
            client_name=cfg.client_name,
            available_clients=get_available_clients(),
            current_client_config=session.get("current_client_config"),
            snapshot_date=snapshot_date,
            # Tab 1: Campaigns
            campaigns=campaigns_list,
            total_campaigns=len(campaigns_list),
            # Tab 2: Products
            products=products_list,
            total_products=total_products,
            total_cost=total_cost,
            total_conversions=total_conversions,
            total_conv_value=total_conv_value,
            avg_roas=avg_roas,
            out_of_stock=out_of_stock,
            price_mismatches=price_mismatches,
            disapproved=disapproved,
            feed_issues_count=feed_issues_count,
            # Tab 3: Feed Quality
            total_feed_products=total_feed_products,
            pct_approved=pct_approved,
            pct_disapproved=pct_disapproved,
            pct_price_mismatch=pct_price_mismatch,
            feed_issues=feed_issues_list,
            # Tab 4: Recommendations
            recommendations=recommendations_list,
            total_recommendations=len(recommendations_list),
        )
        
    except Exception as e:
        return render_template(
            "shopping.html",
            client_name="Error",
            available_clients=get_available_clients(),
            current_client_config=session.get("current_client_config"),
            error=str(e),
        )
