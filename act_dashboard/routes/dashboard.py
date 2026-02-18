"""
Dashboard home page route - overview stats.
"""

from flask import Blueprint, render_template, session, request
from act_dashboard.auth import login_required
from act_dashboard.routes.shared import get_current_config, get_available_clients
import duckdb
import json
from datetime import date, datetime
from typing import Any

bp = Blueprint('dashboard', __name__)


def calculate_change_pct(current: float, previous: float) -> float:
    """
    Calculate percentage change between current and previous values.
    
    Args:
        current: Current period value
        previous: Previous period value
        
    Returns:
        Percentage change (e.g., 12.5 for +12.5%)
    """
    if previous is None or previous == 0:
        return 0 if (current is None or current == 0) else 100
    if current is None:
        return -100
    return ((current - previous) / previous) * 100


@bp.route("/")
@login_required
def home() -> str:
    """
    Dashboard home page with overview stats.
    
    Returns:
        Rendered dashboard template
    """
    config = get_current_config()
    clients = get_available_clients()
    current_client_path = session.get("current_client_config")
    
    # Get date range parameter (default: 7 days)
    days = request.args.get('days', 7, type=int)
    # Ensure valid values (prevents SQL injection)
    if days not in [7, 30, 90]:
        days = 7

    # Connect to database
    conn = duckdb.connect(config.db_path, read_only=True)

    # Query 1: Current period metrics
    # Note: Using f-string for INTERVAL because DuckDB doesn't support ? in INTERVAL
    current_query = f"""
    SELECT
        SUM(clicks) as clicks,
        SUM(impressions) as impressions,
        SUM(cost_micros) / 1000000 as cost,
        SUM(conversions) as conversions,
        SUM(conversions_value) / NULLIF(SUM(cost_micros) / 1000000, 0) as roas,
        SUM(cost_micros) / 1000000 / NULLIF(SUM(conversions), 0) as cpa
    FROM analytics.campaign_daily
    WHERE customer_id = ?
      AND snapshot_date >= CURRENT_DATE - INTERVAL '{days} days'
      AND snapshot_date < CURRENT_DATE
    """
    current = conn.execute(current_query, [config.customer_id]).fetchone()
    
    # Query 2: Previous period metrics (for change % calculation)
    previous_query = f"""
    SELECT
        SUM(clicks) as clicks,
        SUM(impressions) as impressions,
        SUM(cost_micros) / 1000000 as cost,
        SUM(conversions) as conversions,
        SUM(conversions_value) / NULLIF(SUM(cost_micros) / 1000000, 0) as roas,
        SUM(cost_micros) / 1000000 / NULLIF(SUM(conversions), 0) as cpa
    FROM analytics.campaign_daily
    WHERE customer_id = ?
      AND snapshot_date >= CURRENT_DATE - INTERVAL '{days * 2} days'
      AND snapshot_date < CURRENT_DATE - INTERVAL '{days} days'
    """
    previous = conn.execute(previous_query, [config.customer_id]).fetchone()
    
    # Calculate metrics with change percentages
    metrics = {
        'clicks': int(current[0] or 0),
        'clicks_change': calculate_change_pct(current[0], previous[0]),
        'impressions': int(current[1] or 0),
        'impressions_change': calculate_change_pct(current[1], previous[1]),
        'cost': float(current[2] or 0),
        'cost_change': calculate_change_pct(current[2], previous[2]),
        'conversions': int(current[3] or 0),
        'conversions_change': calculate_change_pct(current[3], previous[3]),
        'roas': float(current[4] or 0),
        'roas_change': calculate_change_pct(current[4], previous[4]),
        'cpa': float(current[5] or 0),
        'cpa_change': calculate_change_pct(current[5], previous[5]),
    }

    # Query 3: Daily performance trend (for chart)
    trend_query = f"""
    SELECT
        snapshot_date,
        SUM(cost_micros) / 1000000 as cost,
        SUM(conversions) as conversions,
        SUM(conversions_value) / NULLIF(SUM(cost_micros) / 1000000, 0) as roas
    FROM analytics.campaign_daily
    WHERE customer_id = ?
      AND snapshot_date >= CURRENT_DATE - INTERVAL '{days} days'
    GROUP BY snapshot_date
    ORDER BY snapshot_date
    """
    trend_raw = conn.execute(trend_query, [config.customer_id]).fetchall()
    
    # Format trend data with readable dates
    trend_data = [
        {
            'date': row[0].strftime('%b %d') if isinstance(row[0], (date, datetime)) else str(row[0]),
            'cost': float(row[1] or 0),
            'conversions': int(row[2] or 0),
            'roas': float(row[3] or 0)
        }
        for row in trend_raw
    ]

    # Query 4: Top 5 campaigns by spend
    top_campaigns_query = f"""
    SELECT
        campaign_id,
        campaign_name,
        campaign_status,
        channel_type,
        SUM(cost_micros) / 1000000 as spend,
        SUM(clicks) as clicks,
        SUM(conversions) as conversions,
        SUM(conversions_value) / NULLIF(SUM(cost_micros) / 1000000, 0) as roas
    FROM analytics.campaign_daily
    WHERE customer_id = ?
      AND snapshot_date >= CURRENT_DATE - INTERVAL '{days} days'
    GROUP BY campaign_id, campaign_name, campaign_status, channel_type
    ORDER BY spend DESC
    LIMIT 5
    """
    top_campaigns = conn.execute(top_campaigns_query, [config.customer_id]).fetchall()

    # Query 5: Campaign status counts
    status_query = """
    SELECT
        campaign_status,
        COUNT(DISTINCT campaign_id) as count
    FROM (
        SELECT DISTINCT campaign_id, campaign_status
        FROM analytics.campaign_daily
        WHERE customer_id = ?
          AND snapshot_date >= CURRENT_DATE - INTERVAL '7 days'
    )
    GROUP BY campaign_status
    """
    status_counts = conn.execute(status_query, [config.customer_id]).fetchall()
    
    # Parse status counts
    active_campaigns_count = 0
    paused_campaigns_count = 0
    for status, count in status_counts:
        if status and 'ENABLED' in status.upper():
            active_campaigns_count = count
        elif status and 'PAUSED' in status.upper():
            paused_campaigns_count = count

    # Query 6: Recent changes (last 5)
    changes_query = """
    SELECT
        change_date,
        campaign_id,
        lever,
        old_value / 1000000 as old_value,
        new_value / 1000000 as new_value,
        change_pct,
        rule_id,
        rollback_status
    FROM analytics.change_log
    WHERE customer_id = ?
      AND change_date >= CURRENT_DATE - INTERVAL '7 days'
    ORDER BY change_date DESC, executed_at DESC
    LIMIT 5
    """
    recent_changes = conn.execute(changes_query, [config.customer_id]).fetchall()

    # Query 7: Last sync time (most recent snapshot_date)
    last_sync_query = """
    SELECT MAX(snapshot_date)
    FROM analytics.campaign_daily
    WHERE customer_id = ?
    """
    last_sync_result = conn.execute(last_sync_query, [config.customer_id]).fetchone()
    last_sync_time = "Never"
    if last_sync_result and last_sync_result[0]:
        last_sync_date = last_sync_result[0]
        if isinstance(last_sync_date, (date, datetime)):
            days_ago = (date.today() - last_sync_date).days
            if days_ago == 0:
                last_sync_time = "Today"
            elif days_ago == 1:
                last_sync_time = "Yesterday"
            else:
                last_sync_time = f"{days_ago} days ago"

    conn.close()

    # Load and sort recommendations by predicted_lift
    today = date.today().isoformat()
    suggestions_path = config.get_suggestions_path(today)
    recommendations_count = 0
    top_recommendations = []
    
    if suggestions_path.exists():
        with open(suggestions_path, "r") as f:
            suggestions_data = json.load(f)
            all_recommendations = [
                r for r in suggestions_data.get("recommendations", [])
                if not r.get("blocked", False)
            ]
            recommendations_count = len(all_recommendations)
            
            # Sort by predicted_lift (descending) and take top 3
            sorted_recommendations = sorted(
                all_recommendations,
                key=lambda x: x.get('predicted_lift', 0),
                reverse=True
            )
            top_recommendations = sorted_recommendations[:3]

    return render_template(
        "dashboard_new.html",
        client_name=config.client_name,
        available_clients=clients,
        current_client_config=current_client_path,
        days=days,
        metrics=metrics,
        trend_data=trend_data,
        top_campaigns=top_campaigns,
        recommendations_count=recommendations_count,
        top_recommendations=top_recommendations,
        recent_changes=recent_changes,
        active_campaigns_count=active_campaigns_count,
        paused_campaigns_count=paused_campaigns_count,
        last_sync_time=last_sync_time,
    )
