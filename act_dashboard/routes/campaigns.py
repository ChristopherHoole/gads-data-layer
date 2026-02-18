"""
Campaigns page route - campaign performance and optimization.

Chat 21c: New campaigns page with Bootstrap 5 and rule visibility.
"""

from flask import Blueprint, render_template, request
from act_dashboard.auth import login_required
from act_dashboard.routes.shared import get_page_context, get_db_connection
from act_dashboard.routes.rule_helpers import get_rules_for_page, count_rules_by_category
from datetime import date, timedelta
from typing import List, Dict, Any, Tuple
import duckdb

bp = Blueprint('campaigns', __name__)


def load_campaign_data(conn: duckdb.DuckDBPyConnection, customer_id: str, days: int) -> List[Dict[str, Any]]:
    """
    Load campaign data from analytics.campaign_daily.
    
    Args:
        conn: Database connection
        customer_id: Customer ID
        days: Number of days to look back (7/30/90)
        
    Returns:
        List of campaign dictionaries with aggregated metrics
    """
    # Validate days parameter
    if days not in [7, 30, 90]:
        days = 7
    
    query = f"""
        SELECT 
            campaign_id,
            campaign_name,
            campaign_status,
            channel_type,
            SUM(cost_micros) / 1000000.0 as spend,
            SUM(clicks) as clicks,
            SUM(impressions) as impressions,
            CASE WHEN SUM(impressions) > 0 
                 THEN (SUM(clicks)::DOUBLE / SUM(impressions)) * 100
                 ELSE 0 END as ctr,
            SUM(conversions) as conversions,
            SUM(conversions_value) as conversion_value,
            CASE WHEN SUM(cost_micros) > 0
                 THEN SUM(conversions_value) / (SUM(cost_micros) / 1000000.0)
                 ELSE 0 END as roas,
            CASE WHEN SUM(conversions) > 0
                 THEN (SUM(cost_micros) / 1000000.0) / SUM(conversions)
                 ELSE 0 END as cpa,
            COUNT(DISTINCT snapshot_date) as days_in_period
        FROM analytics.campaign_daily
        WHERE customer_id = ?
          AND snapshot_date >= CURRENT_DATE - INTERVAL '{days} days'
        GROUP BY campaign_id, campaign_name, campaign_status, channel_type
        ORDER BY spend DESC
    """
    
    try:
        rows = conn.execute(query, [customer_id]).fetchall()
        cols = [d[0] for d in conn.description]
        
        campaigns = []
        for row in rows:
            campaign_dict = dict(zip(cols, row))
            
            # Convert to safe types
            campaign_dict['campaign_id'] = str(campaign_dict.get('campaign_id', ''))
            campaign_dict['campaign_name'] = str(campaign_dict.get('campaign_name', 'Unknown'))
            campaign_dict['campaign_status'] = str(campaign_dict.get('campaign_status', 'UNKNOWN'))
            campaign_dict['channel_type'] = str(campaign_dict.get('channel_type', 'UNKNOWN'))
            campaign_dict['spend'] = float(campaign_dict.get('spend') or 0)
            campaign_dict['clicks'] = int(campaign_dict.get('clicks') or 0)
            campaign_dict['impressions'] = int(campaign_dict.get('impressions') or 0)
            campaign_dict['ctr'] = float(campaign_dict.get('ctr') or 0)
            campaign_dict['conversions'] = float(campaign_dict.get('conversions') or 0)
            campaign_dict['conversion_value'] = float(campaign_dict.get('conversion_value') or 0)
            campaign_dict['roas'] = float(campaign_dict.get('roas') or 0)
            campaign_dict['cpa'] = float(campaign_dict.get('cpa') or 0)
            
            # Calculate daily_budget as average daily spend
            days_in_period = int(campaign_dict.get('days_in_period') or 1)
            campaign_dict['daily_budget'] = campaign_dict['spend'] / days_in_period if days_in_period > 0 else 0
            
            campaigns.append(campaign_dict)
        
        return campaigns
        
    except Exception as e:
        print(f"[Campaigns] Error loading campaign data: {e}")
        import traceback
        traceback.print_exc()
        return []


def compute_metrics_bar(campaigns: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate aggregated metrics for metrics bar.
    
    Args:
        campaigns: List of campaign dictionaries
        
    Returns:
        Dictionary of aggregated metrics
    """
    if not campaigns:
        return {
            'total_campaigns': 0,
            'total_spend': 0.0,
            'total_clicks': 0,
            'total_impressions': 0,
            'total_conversions': 0.0,
            'total_conversion_value': 0.0,
            'avg_ctr': 0.0,
            'overall_roas': 0.0,
            'overall_cpa': 0.0,
        }
    
    total_spend = sum(c['spend'] for c in campaigns)
    total_clicks = sum(c['clicks'] for c in campaigns)
    total_impressions = sum(c['impressions'] for c in campaigns)
    total_conversions = sum(c['conversions'] for c in campaigns)
    total_conversion_value = sum(c['conversion_value'] for c in campaigns)
    
    avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
    overall_roas = (total_conversion_value / total_spend) if total_spend > 0 else 0
    overall_cpa = (total_spend / total_conversions) if total_conversions > 0 else 0
    
    return {
        'total_campaigns': len(campaigns),
        'total_spend': total_spend,
        'total_clicks': total_clicks,
        'total_impressions': total_impressions,
        'total_conversions': total_conversions,
        'total_conversion_value': total_conversion_value,
        'avg_ctr': avg_ctr,
        'overall_roas': overall_roas,
        'overall_cpa': overall_cpa,
    }


def apply_pagination(
    campaigns: List[Dict[str, Any]], 
    page: int, 
    per_page: int
) -> Tuple[List[Dict[str, Any]], int, int]:
    """
    Apply pagination to campaigns list.
    
    Args:
        campaigns: Full list of campaigns
        page: Current page number (1-indexed)
        per_page: Items per page
        
    Returns:
        Tuple of (paginated_campaigns, total_count, total_pages)
    """
    total_count = len(campaigns)
    
    # Calculate total pages (at least 1)
    total_pages = max(1, (total_count + per_page - 1) // per_page)
    
    # Clamp page to valid range
    page = max(1, min(page, total_pages))
    
    # Calculate slice indices
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    # Slice campaigns
    paginated = campaigns[start_idx:end_idx]
    
    return paginated, total_count, total_pages


@bp.route("/campaigns")
@login_required
def campaigns():
    """
    Campaigns page - campaign performance with rule visibility.
    
    URL Parameters:
        days: Date range (7/30/90, default 7)
        page: Page number (default 1)
        per_page: Items per page (10/25/50/100, default 25)
    """
    # Get common page context
    config, clients, current_client_path = get_page_context()
    
    # Get URL parameters
    days = request.args.get('days', 7, type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 25, type=int)
    
    # Validate parameters
    if days not in [7, 30, 90]:
        days = 7
    if per_page not in [10, 25, 50, 100]:
        per_page = 25
    if page < 1:
        page = 1
    
    # Get database connection
    conn = get_db_connection(config)
    
    # Load campaign data
    all_campaigns = load_campaign_data(conn, config.customer_id, days)
    
    conn.close()
    
    # Calculate metrics bar (for all campaigns)
    metrics = compute_metrics_bar(all_campaigns)
    
    # Apply pagination
    campaigns_paginated, total_campaigns, total_pages = apply_pagination(
        all_campaigns, page, per_page
    )
    
    # Get campaign rules
    rules = get_rules_for_page('campaign', config.customer_id)
    rule_counts = count_rules_by_category(rules)
    
    # Count campaigns by status
    active_campaigns = sum(1 for c in all_campaigns if c['campaign_status'] == 'ENABLED')
    paused_campaigns = sum(1 for c in all_campaigns if c['campaign_status'] == 'PAUSED')
    
    # Count campaigns by type
    search_campaigns = sum(1 for c in all_campaigns if c['channel_type'] == 'SEARCH')
    shopping_campaigns = sum(1 for c in all_campaigns if c['channel_type'] == 'SHOPPING')
    display_campaigns = sum(1 for c in all_campaigns if c['channel_type'] == 'DISPLAY')
    
    return render_template(
        "campaigns.html",
        # Client context
        client_name=config.client_name,
        available_clients=clients,
        current_client_config=current_client_path,
        # Campaign data
        campaigns=campaigns_paginated,
        total_campaigns=total_campaigns,
        # Metrics
        metrics=metrics,
        # Pagination
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        # Filters
        days=days,
        # Campaign counts
        active_campaigns=active_campaigns,
        paused_campaigns=paused_campaigns,
        search_campaigns=search_campaigns,
        shopping_campaigns=shopping_campaigns,
        display_campaigns=display_campaigns,
        # Rules
        rules=rules,
        rule_counts=rule_counts,
    )
