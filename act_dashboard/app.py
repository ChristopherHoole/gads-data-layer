"""
Ads Control Tower Dashboard - Main Application
Flask web interface for viewing and approving Google Ads optimization recommendations.
"""

from flask import Flask, session
from datetime import timedelta
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from act_dashboard.config import DashboardConfig
from act_dashboard.routes import init_routes
from act_dashboard.auth import init_auth


def create_app(config_path: str = "configs/client_synthetic.yaml"):
    """
    Create and configure Flask application.
    
    Args:
        config_path: Path to client config YAML file
    
    Returns:
        Flask app instance
    """
    app = Flask(__name__)
    
    # Load dashboard configuration
    dashboard_config = DashboardConfig(config_path)
    app.config.from_object(dashboard_config)
    
    # Store config path for routes to access
    app.config['CONFIG_PATH'] = config_path
    app.config['DASHBOARD_CONFIG'] = dashboard_config
    
    # Session configuration
    app.secret_key = os.environ.get('DASHBOARD_SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
    
    # Initialize authentication
    init_auth(app)
    
    # Initialize routes
    init_routes(app)
    
    return app


def main():
    """Run the dashboard server."""
    # Get config path from command line or use default
    config_path = sys.argv[1] if len(sys.argv) > 1 else "configs/client_synthetic.yaml"
    
    # Create app
    app = create_app(config_path)
    
    # Get client name for display
    client_name = app.config['DASHBOARD_CONFIG'].client_name
    
    print("=" * 80)
    print("ADS CONTROL TOWER - Dashboard Starting")
    print("=" * 80)
    print(f"Client: {client_name}")
    print(f"Config: {config_path}")
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
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )


if __name__ == '__main__':
    main()
