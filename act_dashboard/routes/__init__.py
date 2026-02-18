"""
Routes package - modular Blueprint-based routes.

Phase 1a: Auth routes ✅
Phase 1b: API routes ✅
Phase 1c: Page routes ✅
Phase 1d: Final routes ✅ (NEW - COMPLETE!)

ALL 16 ROUTES MIGRATED TO BLUEPRINTS
Chat 21a: Bootstrap test route ✅
"""

from flask import Flask


def register_blueprints(app: Flask):
    """
    Register route blueprints.
    
    All routes now migrated to modular blueprints.
    The old routes_old.py file can be deleted.
    """
    
    # Phase 1a: Auth routes
    from act_dashboard.routes import auth
    app.register_blueprint(auth.bp)
    
    # Phase 1b: API routes
    from act_dashboard.routes import api
    app.register_blueprint(api.bp, url_prefix='/api')
    
    # Phase 1c: Page routes
    from act_dashboard.routes import keywords, ads, shopping
    app.register_blueprint(keywords.bp)
    app.register_blueprint(ads.bp)
    app.register_blueprint(shopping.bp)
    
    # Phase 1d: Final routes (NEW)
    from act_dashboard.routes import dashboard, recommendations, settings
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(recommendations.bp)
    app.register_blueprint(settings.bp)
    
    # Chat 21a: Test Bootstrap route
    from act_dashboard.routes import test_bootstrap
    app.register_blueprint(test_bootstrap.bp)
    
    # Chat 21c: Campaigns page with rule visibility
    from act_dashboard.routes import campaigns
    app.register_blueprint(campaigns.bp)
    
    print("✅ [Phase 1a] Registered auth blueprint (login, logout, switch-client)")
    print("✅ [Phase 1b] Registered api blueprint (execute, batch, status, approve, reject)")
    print("✅ [Phase 1c] Registered page blueprints (keywords, ads, shopping)")
    print("✅ [Phase 1d] Registered final blueprints (dashboard, recommendations, settings)")
    print("✅ [Chat 21a] Registered test blueprint (test-bootstrap)")
    print("✅ [Chat 21c] Registered campaigns blueprint")
    print("🎉 ALL ROUTES REGISTERED - Phase 1 + Bootstrap test + Campaigns COMPLETE!")
