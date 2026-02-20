"""
Ad Groups page route - ad group performance and optimization.

Chat 21e: New ad groups page with Bootstrap 5 and rule visibility.
"""

from flask import Blueprint, render_template, request
from act_dashboard.auth import login_required
from act_dashboard.routes.shared import get_page_context, get_db_connection, get_date_range_from_session
from act_dashboard.routes.rule_helpers import get_rules_for_page, count_rules_by_category
from datetime import date, timedelta
from typing import List, Dict, Any, Tuple
import duckdb

bp = Blueprint('ad_groups', __name__)


def load_ad_group_data(
    conn: duckdb.DuckDBPyConnection,
    customer_id: str,
    days: int = 30,
    status: str = 'all',
    date_from: str = None,
    date_to: str = None,
) -> List[Dict[str, Any]]:
    """
    Load ad group data from ro.analytics.ad_group_daily.

    Args:
        conn: Database connection
        customer_id: Customer ID
        days: Number of days to look back (7/30/90) — used when date_from/date_to are None
        status: Status filter ('all', 'active', 'paused')
        date_from: Start date string (YYYY-MM-DD) for custom date range
        date_to: End date string (YYYY-MM-DD) for custom date range

    Returns:
        List of ad group dictionaries with aggregated metrics
    """
    if date_from and date_to:
        date_filter = f"AND snapshot_date >= '{date_from}' AND snapshot_date <= '{date_to}'"
    else:
        if days not in [7, 30, 90]:
            days = 30
        date_filter = f"AND snapshot_date >= CURRENT_DATE - INTERVAL '{days} days'"

    query = f"""
        SELECT 
            ad_group_id,
            ad_group_name,
            ad_group_status,
            campaign_id,
            campaign_name,
            cpc_bid_micros,
            target_cpa_micros,
            SUM(cost_micros) / 1000000.0 as spend,
            SUM(clicks) as clicks,
            SUM(impressions) as impressions,
            CASE WHEN SUM(impressions) > 0 
                 THEN (SUM(clicks)::DOUBLE / SUM(impressions)) * 100
                 ELSE 0 END as ctr,
            SUM(conversions) as conversions,
            CASE WHEN SUM(conversions) > 0
                 THEN (SUM(cost_micros) / 1000000.0) / SUM(conversions)
                 ELSE 0 END as cpa,
            COUNT(DISTINCT snapshot_date) as days_in_period
        FROM ro.analytics.ad_group_daily
        WHERE customer_id = ?
          {date_filter}
        GROUP BY ad_group_id, ad_group_name, ad_group_status, 
                 campaign_id, campaign_name, cpc_bid_micros, target_cpa_micros
        ORDER BY spend DESC
    """
    
    try:
        rows = conn.execute(query, [customer_id]).fetchall()
        cols = [d[0] for d in conn.description]
        
        ad_groups = []
        for row in rows:
            ad_group_dict = dict(zip(cols, row))
            
            # Convert to safe types
            ad_group_dict['ad_group_id'] = str(ad_group_dict.get('ad_group_id', ''))
            ad_group_dict['ad_group_name'] = str(ad_group_dict.get('ad_group_name', 'Unknown'))
            ad_group_dict['ad_group_status'] = str(ad_group_dict.get('ad_group_status', 'UNKNOWN'))
            ad_group_dict['campaign_id'] = str(ad_group_dict.get('campaign_id', ''))
            ad_group_dict['campaign_name'] = str(ad_group_dict.get('campaign_name', 'Unknown'))
            ad_group_dict['cpc_bid_micros'] = int(ad_group_dict.get('cpc_bid_micros') or 0)
            ad_group_dict['target_cpa_micros'] = int(ad_group_dict.get('target_cpa_micros')) if ad_group_dict.get('target_cpa_micros') is not None else None
            ad_group_dict['spend'] = float(ad_group_dict.get('spend') or 0)
            ad_group_dict['clicks'] = int(ad_group_dict.get('clicks') or 0)
            ad_group_dict['impressions'] = int(ad_group_dict.get('impressions') or 0)
            ad_group_dict['ctr'] = float(ad_group_dict.get('ctr') or 0)
            ad_group_dict['conversions'] = float(ad_group_dict.get('conversions') or 0)
            ad_group_dict['cpa'] = float(ad_group_dict.get('cpa') or 0)
            
            ad_groups.append(ad_group_dict)
        
        # Apply status filter in Python (after SQL query)
        if status == 'active':
            ad_groups = [ag for ag in ad_groups if ag['ad_group_status'] == 'ENABLED']
        elif status == 'paused':
            ad_groups = [ag for ag in ad_groups if ag['ad_group_status'] == 'PAUSED']
        # 'all' requires no filtering
        
        return ad_groups
        
    except Exception as e:
        print(f"[Ad Groups] Error loading ad group data: {e}")
        import traceback
        traceback.print_exc()
        return []


def compute_metrics_bar(ad_groups: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate aggregated metrics for metrics bar.
    
    Args:
        ad_groups: List of ad group dictionaries
        
    Returns:
        Dictionary of aggregated metrics (7 metrics)
    """
    if not ad_groups:
        return {
            'total_ad_groups': 0,
            'active_count': 0,
            'paused_count': 0,
            'total_clicks': 0,
            'total_cost': 0.0,
            'total_conversions': 0.0,
            'overall_cpa': 0.0,
            'overall_ctr': 0.0,
            'avg_bid': 0.0,
        }
    
    total_clicks = sum(ag['clicks'] for ag in ad_groups)
    total_impressions = sum(ag['impressions'] for ag in ad_groups)
    total_cost = sum(ag['spend'] for ag in ad_groups)
    total_conversions = sum(ag['conversions'] for ag in ad_groups)
    
    # Calculate overall CPA
    overall_cpa = (total_cost / total_conversions) if total_conversions > 0 else 0
    
    # Calculate overall CTR
    overall_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
    
    # Calculate average bid (only from ad groups with bid > 0)
    bids = [ag['cpc_bid_micros'] / 1000000.0 for ag in ad_groups if ag.get('cpc_bid_micros', 0) > 0]
    avg_bid = sum(bids) / len(bids) if len(bids) > 0 else 0
    
    # Count by status
    active_count = sum(1 for ag in ad_groups if ag['ad_group_status'] == 'ENABLED')
    paused_count = sum(1 for ag in ad_groups if ag['ad_group_status'] == 'PAUSED')
    
    return {
        'total_ad_groups': len(ad_groups),
        'active_count': active_count,
        'paused_count': paused_count,
        'total_clicks': total_clicks,
        'total_cost': total_cost,
        'total_conversions': total_conversions,
        'overall_cpa': overall_cpa,
        'overall_ctr': overall_ctr,
        'avg_bid': avg_bid,
    }


def apply_pagination(
    ad_groups: List[Dict[str, Any]], 
    page: int, 
    per_page: int
) -> Tuple[List[Dict[str, Any]], int, int]:
    """
    Apply pagination to ad groups list.
    
    Args:
        ad_groups: Full list of ad groups
        page: Current page number (1-indexed)
        per_page: Items per page
        
    Returns:
        Tuple of (paginated_ad_groups, total_count, total_pages)
    """
    total_count = len(ad_groups)
    
    # Calculate total pages (at least 1)
    total_pages = max(1, (total_count + per_page - 1) // per_page)
    
    # Clamp page to valid range
    page = max(1, min(page, total_pages))
    
    # Calculate slice indices
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    # Slice ad groups
    paginated = ad_groups[start_idx:end_idx]
    
    return paginated, total_count, total_pages


@bp.route("/ad-groups")
@login_required
def ad_groups():
    """
    Ad Groups page - ad group performance with rule visibility.
    
    URL Parameters:
        days: Date range (7/30/90, default 7)
        page: Page number (default 1)
        per_page: Items per page (10/25/50/100, default 25)
        status: Status filter ('all', 'active', 'paused', default 'all')
    """
    # Get common page context
    config, clients, current_client_path = get_page_context()
    
    # Get date range from session (default 30d).
    active_days, date_from, date_to = get_date_range_from_session()
    if active_days == 30 and date_from is None and 'days' in request.args:
        url_days = request.args.get('days', 30, type=int)
        if url_days in [7, 90]:
            active_days = url_days

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 25, type=int)
    status = request.args.get('status', 'all', type=str)

    # Validate parameters
    if per_page not in [10, 25, 50, 100]:
        per_page = 25
    if page < 1:
        page = 1
    if status not in ['all', 'active', 'paused']:
        status = 'all'

    # Get database connection
    conn = get_db_connection(config)

    # Load ad group data
    all_ad_groups = load_ad_group_data(conn, config.customer_id, active_days, status, date_from, date_to)
    
    conn.close()
    
    # Calculate metrics bar (for all ad groups after filtering)
    metrics = compute_metrics_bar(all_ad_groups)
    
    # Apply pagination
    ad_groups_paginated, total_ad_groups, total_pages = apply_pagination(
        all_ad_groups, page, per_page
    )
    
    # Get ad group rules
    rules = get_rules_for_page('ad_group', config.customer_id)
    rule_counts = count_rules_by_category(rules)
    
    return render_template(
        "ad_groups.html",
        # Client context
        client_name=config.client_name,
        available_clients=clients,
        current_client_config=current_client_path,
        # Ad group data
        ad_groups=ad_groups_paginated,
        total_ad_groups=total_ad_groups,
        # Metrics
        metrics=metrics,
        # Pagination
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        # Date filter
        days=active_days,
        active_days=active_days,
        date_from=date_from,
        date_to=date_to,
        # Filters
        status=status,
        # Rules
        rules=rules,
        rule_counts=rule_counts,
    )
