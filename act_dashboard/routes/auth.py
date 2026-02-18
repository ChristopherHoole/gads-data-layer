"""
Authentication routes - login, logout, client switching.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, Response
from act_dashboard.auth import login_required, check_credentials
from act_dashboard.routes.shared import get_available_clients
from typing import Union

bp = Blueprint('auth', __name__)


@bp.route("/login", methods=["GET", "POST"])
def login() -> Union[str, Response]:
    """
    Login page.
    
    Returns:
        Rendered login template or redirect to dashboard
    """
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if check_credentials(username, password):
            session["logged_in"] = True
            session.permanent = True

            # Redirect to next page or dashboard
            next_page = request.args.get("next")
            return redirect(next_page or url_for("dashboard.home"))
        else:
            flash("Invalid credentials", "error")

    return render_template("login.html")


@bp.route("/logout")
def logout() -> Response:
    """
    Logout and clear session.
    
    Returns:
        Redirect to login page
    """
    session.clear()
    return redirect(url_for("auth.login"))


@bp.route("/switch-client/<int:client_index>")
@login_required
def switch_client(client_index: int) -> Response:
    """
    Switch to a different client.
    
    Args:
        client_index: Index of client in available clients list
        
    Returns:
        Redirect to dashboard
    """
    clients = get_available_clients()

    if 0 <= client_index < len(clients):
        _, config_path = clients[client_index]
        session["current_client_config"] = config_path
        flash(f"Switched to {clients[client_index][0]}", "success")
    else:
        flash("Invalid client selection", "error")

    return redirect(url_for("dashboard.home"))
