"""
Routes package - modular Blueprint-based routes.

Phase 1a: Auth routes ✅
Phase 1b: API routes ✅
Phase 1c: Page routes ✅ (NEW)
Future phase will add: dashboard, recommendations, settings
"""

from flask import Flask


def register_blueprints(app: Flask):
    """
    Register route blueprints.
    
    This is called from app.py to register all modular routes.
    During migration, this runs alongside the old routes_old.py init_routes().
    """
    
    # Phase 1a: Auth routes
    from act_dashboard.routes import auth
    app.register_blueprint(auth.bp)
    
    # Phase 1b: API routes
    from act_dashboard.routes import api
    app.register_blueprint(api.bp, url_prefix='/api')
    
    # Phase 1c: Page routes (NEW)
    from act_dashboard.routes import keywords, ads, shopping
    app.register_blueprint(keywords.bp)
    app.register_blueprint(ads.bp)
    app.register_blueprint(shopping.bp)
    
    print("✅ [Phase 1a] Registered auth blueprint (login, logout, switch-client)")
    print("✅ [Phase 1b] Registered api blueprint (execute, batch, status, approve, reject)")
    print("✅ [Phase 1c] Registered page blueprints (keywords, ads, shopping)")
    
    # Future phase will add more blueprints here:
    # Phase 1d: Remaining routes (dashboard, recommendations, settings)
