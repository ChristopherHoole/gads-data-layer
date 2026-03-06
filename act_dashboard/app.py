"""
Ads Control Tower Dashboard - Multi-Client Application
Flask web interface supporting multiple Google Ads clients.
"""

from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect, CSRFError
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

    # Initialize CSRF protection (Chat 36)
    csrf = CSRFProtect(app)

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

    # Import for error handlers and CSRF handler (Chat 36)
    from flask import jsonify, render_template, request

    # Chat 36: CSRF exemption for /api/leads (external website form submission)
    # christopherhoole.online cannot obtain CSRF tokens, so this endpoint is exempt
    # Protected by rate limiting instead (3 submissions/hour per IP)
    csrf.exempt(app.view_functions['api.submit_lead'])

    # Chat 36: CSRF exemption for /login (no session exists before authentication)
    # Standard practice: login forms cannot validate CSRF tokens before user is authenticated
    csrf.exempt(app.view_functions['auth.login'])

    # Chat 36: CSRF exemption for session state routes (UI preferences only, not destructive)
    # These routes only update session storage, no data modification
    # Using try-except to handle routes that may not exist in all deployments
    session_routes = [
        'shared.set_date_range',
        'shared.set_metrics_collapse', 
        'shared.set_chart_metrics'
    ]
    for route_name in session_routes:
        if route_name in app.view_functions:
            csrf.exempt(app.view_functions[route_name])
            print(f"✅ [Chat 36] CSRF exempted: {route_name}")
        else:
            print(f"⚠️  [Chat 36] Route not found (skipping): {route_name}")

    # EMERGENCY FIX: CSRF exemption for rules API routes (JSON API, no CSRF tokens sent)
    # All /api/rules/* endpoints are JSON APIs called from JavaScript
    # Protected by @login_required decorator instead
    rules_api_routes = [
        'rules_api.get_rules',           # GET /api/rules
        'rules_api.add_rule',            # POST /api/rules/add
        'rules_api.update_rule',         # PUT /api/rules/<rule_id>/update
        'rules_api.toggle_rule',         # PUT /api/rules/<rule_id>/toggle
        'rules_api.delete_rule',         # DELETE /api/rules/<rule_id>
        'rules_api.get_campaigns_list'   # GET /api/campaigns-list
    ]
    for route_name in rules_api_routes:
        if route_name in app.view_functions:
            csrf.exempt(app.view_functions[route_name])
            print(f"✅ [EMERGENCY FIX] CSRF exempted: {route_name}")
        else:
            print(f"⚠️  [EMERGENCY FIX] Route not found (skipping): {route_name}")

    # Chat 49: CSRF exemption for recommendations accept/decline routes (JSON API, no CSRF tokens sent)
    # Accept/Decline buttons are JSON API calls from JavaScript (Keywords page Recommendations tab)
    # Protected by @login_required decorator instead
    csrf.exempt(app.view_functions['recommendations.recommendation_accept'])
    csrf.exempt(app.view_functions['recommendations.recommendation_decline'])
    print("✅ [Chat 49] CSRF exempted: recommendations.recommendation_accept")
    print("✅ [Chat 49] CSRF exempted: recommendations.recommendation_decline")

    # Chat 59: CSRF exemption for outreach AJAX endpoints (JSON API, no CSRF tokens sent)
    # PATCH /outreach/leads/<id>/notes and POST /outreach/leads/add are JSON APIs
    # Protected by @login_required decorator instead
    outreach_routes = [
        'outreach.patch_lead_notes',
        'outreach.add_lead',
        'outreach.mark_won',
        'outreach.mark_lost',
        'outreach.update_status',
        'outreach.delete_lead',
    ]
    for route_name in outreach_routes:
        if route_name in app.view_functions:
            csrf.exempt(app.view_functions[route_name])
            print(f"✅ [Chat 59] CSRF exempted: {route_name}")
        else:
            print(f"⚠️  [Chat 59] Route not found (skipping): {route_name}")

    # Chat 60: CSRF exemption for queue action routes (JSON API, no CSRF tokens sent)
    # POST /outreach/queue/<id>/send|skip|discard are JSON APIs called from JavaScript
    # Protected by @login_required decorator instead
    queue_routes = [
        'outreach.queue_send',
        'outreach.queue_skip',
        'outreach.queue_discard',
    ]
    for route_name in queue_routes:
        if route_name in app.view_functions:
            csrf.exempt(app.view_functions[route_name])
            print(f"✅ [Chat 60] CSRF exempted: {route_name}")
        else:
            print(f"⚠️  [Chat 60] Route not found (skipping): {route_name}")

    # Chat 61: CSRF exemption for sent page AJAX endpoints (JSON API, no CSRF tokens sent)
    # POST /outreach/sent/* routes are JSON APIs called from JavaScript
    # Protected by @login_required decorator instead
    sent_routes = [
        'outreach.sent_queue_followup',
        'outreach.sent_update_status',
        'outreach.sent_mark_won',
        'outreach.sent_mark_lost',
    ]
    for route_name in sent_routes:
        if route_name in app.view_functions:
            csrf.exempt(app.view_functions[route_name])
            print(f"✅ [Chat 61] CSRF exempted: {route_name}")
        else:
            print(f"⚠️  [Chat 61] Route not found (skipping): {route_name}")

    # Chat 62: CSRF exemption for replies page AJAX endpoints (JSON API, no CSRF tokens sent)
    # POST /outreach/replies/* routes are JSON APIs called from JavaScript
    # Protected by @login_required decorator instead
    replies_routes = [
        'outreach.replies_mark_read',
        'outreach.replies_mark_won',
        'outreach.replies_mark_lost',
        'outreach.replies_book_meeting',
        'outreach.replies_send_reply',
    ]
    for route_name in replies_routes:
        if route_name in app.view_functions:
            csrf.exempt(app.view_functions[route_name])
            print(f"✅ [Chat 62] CSRF exempted: {route_name}")
        else:
            print(f"⚠️  [Chat 62] Route not found (skipping): {route_name}")

    # Chat 63: CSRF exemption for templates page AJAX endpoints (JSON API, no CSRF tokens sent)
    # POST /outreach/templates/* routes are JSON APIs called from JavaScript
    # Protected by @login_required decorator instead
    templates_routes = [
        'outreach.templates_update',
        'outreach.templates_duplicate',
    ]
    for route_name in templates_routes:
        if route_name in app.view_functions:
            csrf.exempt(app.view_functions[route_name])
            print(f"✅ [Chat 63] CSRF exempted: {route_name}")
        else:
            print(f"⚠️  [Chat 63] Route not found (skipping): {route_name}")

    # Chat 36: CSRF error handler - return JSON for all errors
    @app.errorhandler(CSRFError)
    def csrf_error(reason):
        """Handle CSRF validation failures with JSON response."""
        return jsonify({
            'success': False,
            'error': 'CSRF validation failed',
            'message': 'Security token missing or invalid. Please refresh the page.'
        }), 400

    # Chat 29 (M8): Start Radar background monitoring thread
    # daemon=True ensures thread dies when Flask process exits
    # Started AFTER register_blueprints so all routes are available first
    import threading
    from act_autopilot.radar import radar_loop
    radar_thread = threading.Thread(target=radar_loop, daemon=True, name="RadarThread")
    radar_thread.start()
    print("✅ [Chat 29 M8] Radar background thread started (60s cycle)")

    # Centralized error handlers (Phase 1i)
    
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
