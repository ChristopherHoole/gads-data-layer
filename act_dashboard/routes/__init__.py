"""
Routes package - modular Blueprint-based routes.

Phase 1a: Auth routes [OK]
Phase 1b: API routes [OK]
Phase 1c: Page routes [OK]
Phase 1d: Final routes [OK] (NEW - COMPLETE!)

ALL 16 ROUTES MIGRATED TO BLUEPRINTS
Chat 22: Shared utility routes [OK]
Chat 29 (M8): Changes blueprint [OK]
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

    # Chat 59: Outreach system — Leads page + AJAX endpoints
    from act_dashboard.routes import outreach
    app.register_blueprint(outreach.bp)

    # Chat 115: Jobs Tracker — job hunting system
    from act_dashboard.routes import jobs
    app.register_blueprint(jobs.bp)

    # Session A3: ACT v2 Client Configuration
    from act_dashboard.routes.v2_config import v2_config_bp
    app.register_blueprint(v2_config_bp)

    # Session B2: ACT v2 Account Level + Shared API
    from act_dashboard.routes.v2_account import v2_account_bp
    from act_dashboard.routes.v2_api import v2_api_bp
    app.register_blueprint(v2_account_bp)
    app.register_blueprint(v2_api_bp)

    print("[OK] [Phase 1a] Registered auth blueprint (login, logout, switch-client)")
    print("[OK] [Phase 1b] Registered api blueprint (execute, batch, status, approve, reject)")
    print("[OK] [Phase 1c] Registered page blueprints (keywords, ads, shopping)")
    print("[OK] [Phase 1d] Registered final blueprints (dashboard, recommendations, settings)")
    print("[OK] [Chat 21c] Registered campaigns blueprint")
    print("[OK] [Chat 21e] Registered ad_groups blueprint")
    print("[OK] [Chat 22] Registered shared blueprint (set-date-range)")
    print("[OK] [Chat 26 M5] Registered rules_api blueprint (GET/POST/PUT/DELETE /api/rules)")
    print("[OK] [Chat 29 M8] Registered changes blueprint (/changes)")
    print("[OK] [Chat 59] Registered outreach blueprint (/outreach/leads)")
    print("[OK] [Chat 115] Registered jobs blueprint (/jobs)")
    print("[OK] [A3] Registered v2_config blueprint (/v2/config)")
    print("[OK] [B2] Registered v2_account blueprint (/v2/account)")
    print("[OK] [B2] Registered v2_api blueprint (/v2/api)")
