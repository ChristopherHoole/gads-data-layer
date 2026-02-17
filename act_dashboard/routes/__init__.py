"""
Routes package - modular Blueprint-based routes.

Phase 1a: Auth routes only
Future phases will add: API, dashboard, recommendations, keywords, ads, shopping, settings
"""

from flask import Flask


def register_blueprints(app: Flask):
    """
    Register route blueprints.
    
    This is called from app.py to register all modular routes.
    During migration, this runs alongside the old routes.py init_routes().
    """
    
    # Phase 1a: Auth routes only
    from act_dashboard.routes import auth
    
    app.register_blueprint(auth.bp)
    
    print("✅ [Phase 1a] Registered auth blueprint (login, logout, switch-client)")
    
    # Future phases will add more blueprints here:
    # Phase 1b: API routes
    # Phase 1c: Page routes (keywords, ads, shopping)
    # Phase 1d: Remaining routes (dashboard, recommendations, settings)
