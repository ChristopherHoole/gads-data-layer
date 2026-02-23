"""
Routes package - modular Blueprint-based routes.

Phase 1a: Auth routes ✅
Phase 1b: API routes ✅
Phase 1c: Page routes ✅
Phase 1d: Final routes ✅ (NEW - COMPLETE!)

ALL 16 ROUTES MIGRATED TO BLUEPRINTS
Chat 21a: Bootstrap test route ✅
Chat 22: Shared utility routes ✅
Chat 29 (M8): Changes blueprint ✅
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
    
    # Chat 21e: Ad Groups page with rule visibility
    from act_dashboard.routes import ad_groups
    app.register_blueprint(ad_groups.bp)

    # Chat 22: Shared utility routes (/set-date-range)
    from act_dashboard.routes import shared
    app.register_blueprint(shared.bp)

    # Chat 26 (M5): Rules API — CRUD for rules_config.json
    from act_dashboard.routes import rules_api
    app.register_blueprint(rules_api.bp)

    # Chat 29 (M8): Changes page — My Actions + System Changes
    from act_dashboard.routes import changes
    app.register_blueprint(changes.bp)

    print("✅ [Phase 1a] Registered auth blueprint (login, logout, switch-client)")
    print("✅ [Phase 1b] Registered api blueprint (execute, batch, status, approve, reject)")
    print("✅ [Phase 1c] Registered page blueprints (keywords, ads, shopping)")
    print("✅ [Phase 1d] Registered final blueprints (dashboard, recommendations, settings)")
    print("✅ [Chat 21a] Registered test blueprint (test-bootstrap)")
    print("✅ [Chat 21c] Registered campaigns blueprint")
    print("✅ [Chat 21e] Registered ad_groups blueprint")
    print("✅ [Chat 22] Registered shared blueprint (set-date-range)")
    print("✅ [Chat 26 M5] Registered rules_api blueprint (GET/POST/PUT/DELETE /api/rules)")
    print("✅ [Chat 29 M8] Registered changes blueprint (/changes)")
    print("🎉 ALL ROUTES REGISTERED - Phase 1 + Bootstrap + Campaigns + Ad Groups + Date Range + Rules API + Changes COMPLETE!")
