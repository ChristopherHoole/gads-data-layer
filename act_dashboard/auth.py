"""
Simple Authentication
Basic password protection for dashboard (NOT production-grade security).
"""

from flask import session, redirect, url_for, request
from functools import wraps
import os

# Simple credentials (NOT production secure - just basic protection)
DASHBOARD_USERNAME = os.environ.get("DASHBOARD_USERNAME", "admin")
DASHBOARD_PASSWORD = os.environ.get("DASHBOARD_PASSWORD", "admin123")


def login_required(f):
    """
    Decorator to require login for routes.
    Redirects to login page if not authenticated.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login", next=request.url))
        return f(*args, **kwargs)

    return decorated_function


def check_credentials(username: str, password: str) -> bool:
    """
    Check if credentials are valid.

    Args:
        username: Entered username
        password: Entered password

    Returns:
        True if valid, False otherwise
    """
    return username == DASHBOARD_USERNAME and password == DASHBOARD_PASSWORD


def init_auth(app):
    """
    Initialize authentication for Flask app.

    Args:
        app: Flask application instance
    """
    # Make login_required available in all routes
    app.jinja_env.globals.update(login_required=login_required)
