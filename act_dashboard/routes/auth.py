"""
Authentication routes - login, logout, client switching.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from act_dashboard.auth import login_required, check_credentials
from act_dashboard.routes.shared import get_available_clients

bp = Blueprint('auth', __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    """Login page."""
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if check_credentials(username, password):
            session["logged_in"] = True
            session.permanent = True

            # Redirect to next page or dashboard
            next_page = request.args.get("next")
            return redirect(next_page or url_for("dashboard"))
        else:
            flash("Invalid credentials", "error")

    return render_template("login.html")


@bp.route("/logout")
def logout():
    """Logout and clear session."""
    session.clear()
    return redirect(url_for("auth.login"))


@bp.route("/switch-client/<int:client_index>")
@login_required
def switch_client(client_index):
    """Switch to a different client."""
    clients = get_available_clients()

    if 0 <= client_index < len(clients):
        _, config_path = clients[client_index]
        session["current_client_config"] = config_path
        flash(f"Switched to {clients[client_index][0]}", "success")
    else:
        flash("Invalid client selection", "error")

    return redirect(url_for("dashboard"))
