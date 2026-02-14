"""
Ads Control Tower Dashboard - Multi-Client Application
Flask web interface supporting multiple Google Ads clients.
"""

from flask import Flask
from datetime import timedelta
import os
import sys
from pathlib import Path
import glob

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from act_dashboard.routes import init_routes
from act_dashboard.auth import init_auth


def discover_clients():
    """
    Discover all client config files.

    Returns:
        List of (client_name, config_path) tuples
    """
    config_files = glob.glob("configs/client_*.yaml")
    clients = []

    for config_path in sorted(config_files):
        # Extract client name from filename
        filename = Path(config_path).stem  # client_synthetic

        # Load config to get actual client_name
        import yaml

        try:
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)
                client_name = config.get("client_name", filename)
                clients.append((client_name, config_path))
        except Exception as e:
            print(f"Warning: Could not load {config_path}: {e}")

    return clients


def create_app():
    """
    Create and configure Flask application (multi-client).

    Returns:
        Flask app instance
    """
    app = Flask(__name__)

    # Session configuration
    app.secret_key = os.environ.get(
        "DASHBOARD_SECRET_KEY", "dev-secret-key-change-in-production"
    )
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=24)

    # Discover available clients
    clients = discover_clients()
    app.config["AVAILABLE_CLIENTS"] = clients

    # Set default client (first one) if available
    if clients:
        app.config["DEFAULT_CLIENT"] = clients[0][1]  # config_path
    else:
        print("WARNING: No client configs found in configs/client_*.yaml")
        app.config["DEFAULT_CLIENT"] = None

    # Flask settings
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0

    # Initialize authentication
    init_auth(app)

    # Initialize routes
    init_routes(app)

    return app


def main():
    """Run the dashboard server."""
    # Create app
    app = create_app()

    # Display startup info
    clients = app.config["AVAILABLE_CLIENTS"]

    print("=" * 80)
    print("ADS CONTROL TOWER - Multi-Client Dashboard Starting")
    print("=" * 80)
    print(f"Available Clients: {len(clients)}")
    for client_name, config_path in clients:
        print(f"  • {client_name} ({config_path})")
    print()
    print("Dashboard running at: http://localhost:5000")
    print()
    print("Login credentials:")
    print("  Username: admin")
    print("  Password: admin123")
    print()
    print("Press CTRL+C to stop")
    print("=" * 80)
    print()

    # Run development server
    app.run(host="0.0.0.0", port=5000, debug=True)


if __name__ == "__main__":
    main()
