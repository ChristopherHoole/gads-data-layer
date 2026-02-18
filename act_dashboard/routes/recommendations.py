"""
Recommendations and changes history routes.
"""

from flask import Blueprint, render_template, session, request
from act_dashboard.auth import login_required
from act_dashboard.routes.shared import get_current_config, get_available_clients
import duckdb
import json
from datetime import date
from typing import Optional

bp = Blueprint('recommendations', __name__)


@bp.route("/recommendations")
@bp.route("/recommendations/<date_str>")
@login_required
def recommendations(date_str: Optional[str] = None) -> str:
    """
    Recommendations page for viewing and approving suggestions.
    
    Args:
        date_str: Date string in ISO format (YYYY-MM-DD), uses today if None
        
    Returns:
        Rendered recommendations template
    """
    config = get_current_config()
    clients = get_available_clients()
    current_client_path = session.get("current_client_config")

    # Use today's date if not specified
    if date_str is None:
        date_str = date.today().isoformat()

    # Load suggestions
    suggestions_path = config.get_suggestions_path(date_str)

    if not suggestions_path.exists():
        return render_template(
            "recommendations.html",
            client_name=config.client_name,
            available_clients=clients,
            current_client_config=current_client_path,
            date=date_str,
            recommendations=None,
            error=f"No suggestions found for {date_str}",
        )

    with open(suggestions_path, "r") as f:
        suggestions_data = json.load(f)

    # Load existing approvals if any
    approvals_path = config.get_approvals_path(date_str)
    approved_ids = set()
    rejected_ids = set()

    if approvals_path.exists():
        with open(approvals_path, "r") as f:
            approvals = json.load(f)
            for decision in approvals.get("decisions", []):
                key = f"{decision['rule_id']}_{decision['entity_id']}"
                if decision["decision"] == "approved":
                    approved_ids.add(key)
                elif decision["decision"] == "rejected":
                    rejected_ids.add(key)

    # Group recommendations by risk tier
    low_risk = []
    medium_risk = []
    high_risk = []

    for idx, rec in enumerate(suggestions_data["recommendations"]):
        if rec.get("blocked", False):
            continue  # Skip blocked recommendations

        # Add index for execution API
        rec["id"] = idx
        
        # Add approval status
        key = f"{rec['rule_id']}_{rec['entity_id']}"
        rec["approved"] = key in approved_ids
        rec["rejected"] = key in rejected_ids

        # Group by risk
        risk = rec.get("risk_tier", "low")
        if risk == "low":
            low_risk.append(rec)
        elif risk in ["med", "medium"]:
            medium_risk.append(rec)
        else:
            high_risk.append(rec)

    return render_template(
        "recommendations.html",
        client_name=config.client_name,
        available_clients=clients,
        current_client_config=current_client_path,
        date=date_str,
        summary=suggestions_data.get("summary", {}),
        low_risk=low_risk,
        medium_risk=medium_risk,
        high_risk=high_risk,
    )


@bp.route("/changes")
@login_required
def changes() -> str:
    """
    Change history page showing all executed changes.
    
    Returns:
        Rendered changes template
    """
    config = get_current_config()
    clients = get_available_clients()
    current_client_path = session.get("current_client_config")

    # Get filter parameters
    search = request.args.get("search", "")
    status_filter = request.args.get("status", "all")
    lever_filter = request.args.get("lever", "all")

    # Connect to database
    conn = duckdb.connect(config.db_path, read_only=True)

    # Build query with filters
    query = """
    SELECT
        change_id,
        change_date,
        campaign_id,
        lever,
        old_value / 1000000 as old_value,
        new_value / 1000000 as new_value,
        change_pct,
        rule_id,
        risk_tier,
        rollback_status,
        executed_at
    FROM analytics.change_log
    WHERE customer_id = ?
    """
    params = [config.customer_id]

    if status_filter != "all":
        if status_filter == "active":
            query += (
                " AND (rollback_status IS NULL OR rollback_status = 'monitoring')"
            )
        else:
            query += " AND rollback_status = ?"
            params.append(status_filter)

    if lever_filter != "all":
        query += " AND lever = ?"
        params.append(lever_filter)

    if search:
        query += " AND campaign_id LIKE ?"
        params.append(f"%{search}%")

    query += " ORDER BY change_date DESC, executed_at DESC LIMIT 100"

    changes_data = conn.execute(query, params).fetchall()
    conn.close()

    return render_template(
        "changes.html",
        client_name=config.client_name,
        available_clients=clients,
        current_client_config=current_client_path,
        changes=changes_data,
        search=search,
        status_filter=status_filter,
        lever_filter=lever_filter,
    )
