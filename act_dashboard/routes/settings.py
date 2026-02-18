"""
Settings page route - client configuration.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from act_dashboard.auth import login_required
from act_dashboard.routes.shared import get_current_config, get_available_clients

bp = Blueprint('settings', __name__)


@bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    """Settings page for editing client configuration."""
    config = get_current_config()
    clients = get_available_clients()
    current_client_path = session.get("current_client_config")

    if request.method == "POST":
        # Update configuration from form
        config.client_name = request.form.get("client_name", config.client_name)
        config.client_type = request.form.get("client_type", config.client_type)
        config.primary_kpi = request.form.get("primary_kpi", config.primary_kpi)
        config.automation_mode = request.form.get(
            "automation_mode", config.automation_mode
        )
        config.risk_tolerance = request.form.get(
            "risk_tolerance", config.risk_tolerance
        )

        # Update targets
        target_roas = request.form.get("target_roas", "")
        config.target_roas = float(target_roas) if target_roas else None

        target_cpa = request.form.get("target_cpa", "")
        config.target_cpa = float(target_cpa) if target_cpa else None

        # Update spend caps
        daily_cap = request.form.get("daily_cap", "")
        config.daily_cap = float(daily_cap) if daily_cap else 0

        monthly_cap = request.form.get("monthly_cap", "")
        config.monthly_cap = float(monthly_cap) if monthly_cap else 0

        # Update protected entities
        config.brand_protected = request.form.get("brand_protected") == "on"

        # Save to YAML
        config.save()

        flash("Settings saved successfully", "success")
        return redirect(url_for("settings.settings"))

    return render_template(
        "settings.html",
        client_name=config.client_name,
        available_clients=clients,
        current_client_config=current_client_path,
        config=config,
    )
