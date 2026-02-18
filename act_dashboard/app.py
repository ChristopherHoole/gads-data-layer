"""
Ads Control Tower Dashboard - Multi-Client Application
Flask web interface supporting multiple Google Ads clients.
"""

from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import timedelta
import os
import sys
from pathlib import Path
import glob
import logging
from logging.handlers import RotatingFileHandler

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from act_dashboard.routes import register_blueprints
from act_dashboard.auth import init_auth
from act_dashboard.cache import ExpiringCache
from act_dashboard.config_validator import validate_all_configs, print_validation_errors


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

    # Validate all client configs on startup (Phase 2d)
    config_dir = Path("configs")
    is_valid, errors = validate_all_configs(config_dir)
    
    if not is_valid:
        print_validation_errors(errors)
        print("\n⚠️  WARNING: Some configs have errors. App will start but those clients may not work.\n")
        # Uncomment next line to prevent startup with invalid configs:
        # raise ValueError("Invalid client configurations detected")

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

    # Configure logging (Phase 1g)
    if not app.debug:
        # Create logs directory if it doesn't exist
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        # File handler with rotation
        file_handler = RotatingFileHandler(
            'logs/dashboard.log',
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Dashboard startup')

    # Initialize authentication
    init_auth(app)

    # Initialize recommendations cache with expiration (Phase 1h)
    # Recommendations expire after 1 hour to prevent stale data
    # Using ExpiringCache instead of plain dict to prevent memory leaks
    app.config['RECOMMENDATIONS_CACHE'] = ExpiringCache(default_ttl=3600)  # 1 hour TTL

    # Initialize rate limiter (Phase 1f)
    # Default: 200 requests per day, 50 per hour
    # Execution endpoints have stricter limits (10 per minute)
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://",
    )
    app.config['LIMITER'] = limiter

    # Register all route blueprints (Phase 1 complete - all 16 routes migrated)
    register_blueprints(app)

    # Centralized error handlers (Phase 1i)
    from flask import jsonify, render_template, request
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 errors."""
        if request.path.startswith('/api/'):
            return jsonify({
                'success': False,
                'error': 'Not found',
                'message': f'Endpoint {request.path} does not exist'
            }), 404
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        app.logger.error(f'Server Error: {error}')
        if request.path.startswith('/api/'):
            return jsonify({
                'success': False,
                'error': 'Internal server error',
                'message': 'An unexpected error occurred. Please try again.'
            }), 500
        return render_template('500.html'), 500
    
    @app.errorhandler(429)
    def ratelimit_error(error):
        """Handle rate limit errors."""
        if request.path.startswith('/api/'):
            return jsonify({
                'success': False,
                'error': 'Rate limit exceeded',
                'message': 'Too many requests. Please slow down.'
            }), 429
        return jsonify({
            'success': False,
            'error': 'Rate limit exceeded',
            'message': 'Too many requests. Please slow down.'
        }), 429

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
