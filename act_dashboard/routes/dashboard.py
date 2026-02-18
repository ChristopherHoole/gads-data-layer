"""
Dashboard home page route - overview stats.
"""

from flask import Blueprint, render_template, session
from act_dashboard.auth import login_required
from act_dashboard.routes.shared import get_current_config, get_available_clients
import duckdb
import json
from datetime import date

bp = Blueprint('dashboard', __name__)


@bp.route("/")
@login_required
def home():
    """Dashboard home page with overview stats."""
    config = get_current_config()
    clients = get_available_clients()
    current_client_path = session.get("current_client_config")

    # Connect to database
    conn = duckdb.connect(config.db_path, read_only=True)

    # Get account summary (last 7 days)
    summary_query = """
    SELECT
        COUNT(DISTINCT campaign_id) as campaign_count,
        SUM(cost_micros) / 1000000 as total_spend,
        SUM(conversions) as total_conversions,
        SUM(conversions_value) / NULLIF(SUM(cost_micros), 0) as avg_roas
    FROM analytics.campaign_daily
    WHERE customer_id = ?
      AND snapshot_date >= CURRENT_DATE - INTERVAL '7 days'
    """
    summary = conn.execute(summary_query, [config.customer_id]).fetchone()

    # Get pending recommendations count (today)
    today = date.today().isoformat()
    suggestions_path = config.get_suggestions_path(today)
    pending_count = 0
    if suggestions_path.exists():
        with open(suggestions_path, "r") as f:
            suggestions = json.load(f)
            pending_count = len(
                [
                    r
                    for r in suggestions["recommendations"]
                    if not r.get("blocked", False)
                ]
            )

    # Get recent changes (last 7 days)
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

    # Get performance trend (last 30 days)
    trend_query = """
    SELECT
        snapshot_date,
        SUM(cost_micros) / 1000000 as spend,
        SUM(conversions) as conversions,
        SUM(conversions_value) / NULLIF(SUM(cost_micros), 0) as roas
    FROM analytics.campaign_daily
    WHERE customer_id = ?
      AND snapshot_date >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY snapshot_date
    ORDER BY snapshot_date
    """
    trend_data = conn.execute(trend_query, [config.customer_id]).fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        client_name=config.client_name,
        available_clients=clients,
        current_client_config=current_client_path,
        campaign_count=summary[0] or 0,
        total_spend=summary[1] or 0,
        total_conversions=summary[2] or 0,
        avg_roas=summary[3] or 0,
        pending_count=pending_count,
        recent_changes=recent_changes,
        trend_data=trend_data,
    )
