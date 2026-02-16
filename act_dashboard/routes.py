"""
Dashboard Routes - Multi-Client Support
All URL endpoints with dynamic client switching.
"""

from flask import (
    render_template,
    request,
    redirect,
    url_for,
    session,
    jsonify,
    flash,
    current_app,
)
from act_dashboard.auth import login_required, check_credentials
from act_dashboard.config import DashboardConfig
import duckdb
import json
from datetime import datetime, date


def get_current_config():
    """
    Get the current client config based on session.

    Returns:
        DashboardConfig instance for current client
    """
    # Get config path from session or use default
    config_path = session.get("current_client_config")

    if not config_path:
        # Use default client
        config_path = current_app.config.get("DEFAULT_CLIENT")
        if config_path:
            session["current_client_config"] = config_path

    if not config_path:
        raise ValueError("No client configuration available")

    return DashboardConfig(config_path)


def get_available_clients():
    """Get list of available clients for switcher."""
    return current_app.config.get("AVAILABLE_CLIENTS", [])


def init_routes(app):
    """
    Initialize all routes for the Flask app.

    Args:
        app: Flask application instance
    """

    @app.route("/login", methods=["GET", "POST"])
    def login():
        """Login page."""
        if request.method == "POST":
            username = request.form.get("username", "")
            password = request.form.get("password", "")

            if check_credentials(username, password):
                session["logged_in"] = True
                session.permanent = True

                # Redirect to next page or dashboard
                next_page = request.args.get("next")
                return redirect(next_page or url_for("dashboard"))
            else:
                flash("Invalid credentials", "error")

        return render_template("login.html")

    @app.route("/logout")
    def logout():
        """Logout and clear session."""
        session.clear()
        return redirect(url_for("login"))

    @app.route("/switch-client/<int:client_index>")
    @login_required
    def switch_client(client_index):
        """Switch to a different client."""
        clients = get_available_clients()

        if 0 <= client_index < len(clients):
            _, config_path = clients[client_index]
            session["current_client_config"] = config_path
            flash(f"Switched to {clients[client_index][0]}", "success")
        else:
            flash("Invalid client selection", "error")

        return redirect(url_for("dashboard"))

    @app.route("/")
    @login_required
    def dashboard():
        """Dashboard home page with overview stats."""
        config = get_current_config()
        clients = get_available_clients()
        current_client_path = session.get("current_client_config")

        # Connect to database
        conn = duckdb.connect(config.db_path, read_only=True)

        # Get account summary (last 7 days)
        summary_query = """
        SELECT
            COUNT(DISTINCT campaign_id) as campaign_count,
            SUM(cost_micros) / 1000000 as total_spend,
            SUM(conversions) as total_conversions,
            SUM(conversions_value) / NULLIF(SUM(cost_micros), 0) as avg_roas
        FROM analytics.campaign_daily
        WHERE customer_id = ?
          AND snapshot_date >= CURRENT_DATE - INTERVAL '7 days'
        """
        summary = conn.execute(summary_query, [config.customer_id]).fetchone()

        # Get pending recommendations count (today)
        today = date.today().isoformat()
        suggestions_path = config.get_suggestions_path(today)
        pending_count = 0
        if suggestions_path.exists():
            with open(suggestions_path, "r") as f:
                suggestions = json.load(f)
                pending_count = len(
                    [
                        r
                        for r in suggestions["recommendations"]
                        if not r.get("blocked", False)
                    ]
                )

        # Get recent changes (last 7 days)
        changes_query = """
        SELECT
            change_date,
            campaign_id,
            lever,
            old_value / 1000000 as old_value,
            new_value / 1000000 as new_value,
            change_pct,
            rule_id,
            rollback_status
        FROM analytics.change_log
        WHERE customer_id = ?
          AND change_date >= CURRENT_DATE - INTERVAL '7 days'
        ORDER BY change_date DESC, executed_at DESC
        LIMIT 5
        """
        recent_changes = conn.execute(changes_query, [config.customer_id]).fetchall()

        # Get performance trend (last 30 days)
        trend_query = """
        SELECT
            snapshot_date,
            SUM(cost_micros) / 1000000 as spend,
            SUM(conversions) as conversions,
            SUM(conversions_value) / NULLIF(SUM(cost_micros), 0) as roas
        FROM analytics.campaign_daily
        WHERE customer_id = ?
          AND snapshot_date >= CURRENT_DATE - INTERVAL '30 days'
        GROUP BY snapshot_date
        ORDER BY snapshot_date
        """
        trend_data = conn.execute(trend_query, [config.customer_id]).fetchall()

        conn.close()

        return render_template(
            "dashboard.html",
            client_name=config.client_name,
            available_clients=clients,
            current_client_config=current_client_path,
            campaign_count=summary[0] or 0,
            total_spend=summary[1] or 0,
            total_conversions=summary[2] or 0,
            avg_roas=summary[3] or 0,
            pending_count=pending_count,
            recent_changes=recent_changes,
            trend_data=trend_data,
        )

    @app.route("/recommendations")
    @app.route("/recommendations/<date_str>")
    @login_required
    def recommendations(date_str=None):
        """Recommendations page for viewing and approving suggestions."""
        config = get_current_config()
        clients = get_available_clients()
        current_client_path = session.get("current_client_config")

        # Use today's date if not specified
        if date_str is None:
            date_str = date.today().isoformat()

        # Load suggestions
        suggestions_path = config.get_suggestions_path(date_str)

        if not suggestions_path.exists():
            return render_template(
                "recommendations.html",
                client_name=config.client_name,
                available_clients=clients,
                current_client_config=current_client_path,
                date=date_str,
                recommendations=None,
                error=f"No suggestions found for {date_str}",
            )

        with open(suggestions_path, "r") as f:
            suggestions_data = json.load(f)

        # Load existing approvals if any
        approvals_path = config.get_approvals_path(date_str)
        approved_ids = set()
        rejected_ids = set()

        if approvals_path.exists():
            with open(approvals_path, "r") as f:
                approvals = json.load(f)
                for decision in approvals.get("decisions", []):
                    key = f"{decision['rule_id']}_{decision['entity_id']}"
                    if decision["decision"] == "approved":
                        approved_ids.add(key)
                    elif decision["decision"] == "rejected":
                        rejected_ids.add(key)

        # Group recommendations by risk tier
        low_risk = []
        medium_risk = []
        high_risk = []

        for rec in suggestions_data["recommendations"]:
            if rec.get("blocked", False):
                continue  # Skip blocked recommendations

            # Add approval status
            key = f"{rec['rule_id']}_{rec['entity_id']}"
            rec["approved"] = key in approved_ids
            rec["rejected"] = key in rejected_ids

            # Group by risk
            risk = rec.get("risk_tier", "low")
            if risk == "low":
                low_risk.append(rec)
            elif risk in ["med", "medium"]:
                medium_risk.append(rec)
            else:
                high_risk.append(rec)

        return render_template(
            "recommendations.html",
            client_name=config.client_name,
            available_clients=clients,
            current_client_config=current_client_path,
            date=date_str,
            summary=suggestions_data.get("summary", {}),
            low_risk=low_risk,
            medium_risk=medium_risk,
            high_risk=high_risk,
        )

    @app.route("/api/approve", methods=["POST"])
    @login_required
    def approve_recommendation():
        """API endpoint to approve a recommendation."""
        config = get_current_config()
        data = request.json
        date_str = data.get("date")
        rule_id = data.get("rule_id")
        entity_id = data.get("entity_id")
        campaign_name = data.get("campaign_name", "N/A")
        action_type = data.get("action_type")

        approvals_path = config.get_approvals_path(date_str)

        # Load or create approvals file
        if approvals_path.exists():
            with open(approvals_path, "r") as f:
                approvals = json.load(f)
        else:
            approvals = {
                "snapshot_date": date_str,
                "client_name": config.client_name,
                "reviewed_at": None,
                "total_reviewed": 0,
                "approved": 0,
                "rejected": 0,
                "skipped": 0,
                "decisions": [],
            }
            approvals_path.parent.mkdir(parents=True, exist_ok=True)

        # Remove any existing decision for this recommendation
        approvals["decisions"] = [
            d
            for d in approvals["decisions"]
            if not (d["rule_id"] == rule_id and d["entity_id"] == entity_id)
        ]

        # Add new approval
        approvals["decisions"].append(
            {
                "rule_id": rule_id,
                "entity_id": entity_id,
                "campaign_name": campaign_name,
                "action_type": action_type,
                "decision": "approved",
                "reviewed_at": datetime.utcnow().isoformat() + "Z",
            }
        )

        # Update counts
        approvals["total_reviewed"] = len(approvals["decisions"])
        approvals["approved"] = len(
            [d for d in approvals["decisions"] if d["decision"] == "approved"]
        )
        approvals["rejected"] = len(
            [d for d in approvals["decisions"] if d["decision"] == "rejected"]
        )
        approvals["reviewed_at"] = datetime.utcnow().isoformat() + "Z"

        # Save
        with open(approvals_path, "w") as f:
            json.dump(approvals, f, indent=2)

        return jsonify({"success": True})

    @app.route("/api/reject", methods=["POST"])
    @login_required
    def reject_recommendation():
        """API endpoint to reject a recommendation."""
        config = get_current_config()
        data = request.json
        date_str = data.get("date")
        rule_id = data.get("rule_id")
        entity_id = data.get("entity_id")
        campaign_name = data.get("campaign_name", "N/A")
        action_type = data.get("action_type")

        approvals_path = config.get_approvals_path(date_str)

        # Load or create approvals file
        if approvals_path.exists():
            with open(approvals_path, "r") as f:
                approvals = json.load(f)
        else:
            approvals = {
                "snapshot_date": date_str,
                "client_name": config.client_name,
                "reviewed_at": None,
                "total_reviewed": 0,
                "approved": 0,
                "rejected": 0,
                "skipped": 0,
                "decisions": [],
            }
            approvals_path.parent.mkdir(parents=True, exist_ok=True)

        # Remove any existing decision for this recommendation
        approvals["decisions"] = [
            d
            for d in approvals["decisions"]
            if not (d["rule_id"] == rule_id and d["entity_id"] == entity_id)
        ]

        # Add rejection
        approvals["decisions"].append(
            {
                "rule_id": rule_id,
                "entity_id": entity_id,
                "campaign_name": campaign_name,
                "action_type": action_type,
                "decision": "rejected",
                "reviewed_at": datetime.utcnow().isoformat() + "Z",
            }
        )

        # Update counts
        approvals["total_reviewed"] = len(approvals["decisions"])
        approvals["approved"] = len(
            [d for d in approvals["decisions"] if d["decision"] == "approved"]
        )
        approvals["rejected"] = len(
            [d for d in approvals["decisions"] if d["decision"] == "rejected"]
        )
        approvals["reviewed_at"] = datetime.utcnow().isoformat() + "Z"

        # Save
        with open(approvals_path, "w") as f:
            json.dump(approvals, f, indent=2)

        return jsonify({"success": True})

    @app.route("/changes")
    @login_required
    def changes():
        """Change history page showing all executed changes."""
        config = get_current_config()
        clients = get_available_clients()
        current_client_path = session.get("current_client_config")

        # Get filter parameters
        search = request.args.get("search", "")
        status_filter = request.args.get("status", "all")
        lever_filter = request.args.get("lever", "all")

        # Connect to database
        conn = duckdb.connect(config.db_path, read_only=True)

        # Build query with filters
        query = """
        SELECT
            change_id,
            change_date,
            campaign_id,
            lever,
            old_value / 1000000 as old_value,
            new_value / 1000000 as new_value,
            change_pct,
            rule_id,
            risk_tier,
            rollback_status,
            executed_at
        FROM analytics.change_log
        WHERE customer_id = ?
        """
        params = [config.customer_id]

        if status_filter != "all":
            if status_filter == "active":
                query += (
                    " AND (rollback_status IS NULL OR rollback_status = 'monitoring')"
                )
            else:
                query += " AND rollback_status = ?"
                params.append(status_filter)

        if lever_filter != "all":
            query += " AND lever = ?"
            params.append(lever_filter)

        if search:
            query += " AND campaign_id LIKE ?"
            params.append(f"%{search}%")

        query += " ORDER BY change_date DESC, executed_at DESC LIMIT 100"

        changes_data = conn.execute(query, params).fetchall()
        conn.close()

        return render_template(
            "changes.html",
            client_name=config.client_name,
            available_clients=clients,
            current_client_config=current_client_path,
            changes=changes_data,
            search=search,
            status_filter=status_filter,
            lever_filter=lever_filter,
        )

    @app.route("/keywords")
    @login_required
    def keywords():
        """Keyword performance page with search terms and recommendations."""
        config = get_current_config()
        clients = get_available_clients()
        current_client_path = session.get("current_client_config")

        conn = duckdb.connect(config.db_path)
        ro_path = config.db_path.replace("warehouse.duckdb", "warehouse_readonly.duckdb")
        try:
            conn.execute(f"ATTACH '{ro_path}' AS ro (READ_ONLY);")
        except Exception:
            pass  # Already attached or not available

        # Determine snapshot date (latest available)
        snap_row = conn.execute("""
            SELECT MAX(snapshot_date) FROM analytics.keyword_features_daily
            WHERE customer_id = ?
        """, [config.customer_id]).fetchone()
        snapshot_date = snap_row[0] if snap_row and snap_row[0] else date.today()

        # Target CPA from config
        target_cpa = float(config.target_cpa) if config.target_cpa else 25.0

        # ── Load keyword features ──
        kw_rows = conn.execute("""
            SELECT
                keyword_id, keyword_text, match_type, status,
                campaign_id, campaign_name,
                quality_score, quality_score_creative,
                quality_score_landing_page, quality_score_relevance,
                clicks_w7_sum, impressions_w7_sum,
                cost_micros_w30_sum, conversions_w30_sum,
                conversion_value_w30_sum,
                ctr_w7, cvr_w30, cpa_w30, roas_w30,
                low_data_flag
            FROM analytics.keyword_features_daily
            WHERE customer_id = ?
              AND snapshot_date = ?
            ORDER BY cost_micros_w30_sum DESC
        """, [config.customer_id, snapshot_date]).fetchall()

        kw_cols = [d[0] for d in conn.description]
        keywords_list = []
        for row in kw_rows:
            d = dict(zip(kw_cols, row))
            d["clicks_w7"] = float(d.get("clicks_w7_sum") or 0)
            d["cost_w30"] = float(d.get("cost_micros_w30_sum") or 0)
            d["conv_w30"] = float(d.get("conversions_w30_sum") or 0)
            d["cpa_dollars"] = (float(d["cpa_w30"]) / 1_000_000) if d.get("cpa_w30") and float(d["cpa_w30"]) > 0 else 0
            d["cost_w30_dollars"] = d["cost_w30"] / 1_000_000
            keywords_list.append(d)

        # ── Summary stats ──
        active_count = len(keywords_list)
        low_qs_count = sum(1 for k in keywords_list if k.get("quality_score") and int(k["quality_score"]) <= 3)
        low_data_count = sum(1 for k in keywords_list if k.get("low_data_flag"))
        wasted_spend = sum(
            k["cost_w30"] / 1_000_000
            for k in keywords_list
            if k["conv_w30"] == 0 and k["cost_w30"] > 50_000_000
        )
        cpa_kws = [k for k in keywords_list if k["cpa_dollars"] > 0]
        avg_cpa_dollars = round(sum(k["cpa_dollars"] for k in cpa_kws) / len(cpa_kws), 2) if cpa_kws else 0
        qs_kws = [k for k in keywords_list if k.get("quality_score")]
        avg_qs = round(sum(int(k["quality_score"]) for k in qs_kws) / len(qs_kws), 1) if qs_kws else 0

        # ── Campaign list for filter ──
        campaigns_dict = {}
        for k in keywords_list:
            cid = str(k.get("campaign_id", ""))
            cname = k.get("campaign_name", cid)
            if cid not in campaigns_dict:
                campaigns_dict[cid] = cname
        campaigns = sorted(campaigns_dict.items(), key=lambda x: x[1])

        # ── Load search term aggregates ──
        from datetime import timedelta as td
        st_start = snapshot_date - td(days=29)

        st_rows = conn.execute("""
            SELECT
                search_term, search_term_status,
                campaign_id, campaign_name,
                ad_group_id, keyword_id, keyword_text,
                match_type,
                SUM(COALESCE(impressions, 0)) as impressions,
                SUM(COALESCE(clicks, 0)) as clicks,
                SUM(COALESCE(cost_micros, 0)) as cost_micros,
                SUM(COALESCE(conversions, 0)) as conversions,
                SUM(COALESCE(conversions_value, 0)) as conversion_value,
                CASE WHEN SUM(clicks) > 0
                     THEN SUM(conversions)::DOUBLE / SUM(clicks)
                     ELSE NULL END AS cvr,
                CASE WHEN SUM(conversions) > 0
                     THEN SUM(cost_micros)::DOUBLE / SUM(conversions)
                     ELSE NULL END AS cpa_micros
            FROM ro.analytics.search_term_daily
            WHERE customer_id = ?
              AND snapshot_date BETWEEN ? AND ?
            GROUP BY search_term, search_term_status, campaign_id, campaign_name,
                     ad_group_id, keyword_id, keyword_text, match_type
            ORDER BY cost_micros DESC
        """, [config.customer_id, st_start, snapshot_date]).fetchall()

        st_cols = [d[0] for d in conn.description]
        search_terms = []
        for row in st_rows:
            d = dict(zip(st_cols, row))
            d["cost_dollars"] = float(d.get("cost_micros") or 0) / 1_000_000
            d["cpa_dollars"] = (float(d["cpa_micros"]) / 1_000_000) if d.get("cpa_micros") and float(d["cpa_micros"]) > 0 else 0
            search_terms.append(d)

        conn.close()

        # ── Load keyword recommendations (run rules live) ──
        rec_groups = []
        rec_count = 0
        try:
            from act_lighthouse.config import load_client_config
            from act_lighthouse.keyword_diagnostics import compute_campaign_averages
            from act_autopilot.models import AutopilotConfig, RuleContext, _safe_float
            from act_autopilot.rules.keyword_rules import KEYWORD_RULES, SEARCH_TERM_RULES

            lh_cfg = load_client_config(
                session.get("current_client_config")
                or current_app.config.get("DEFAULT_CLIENT")
            )
            raw = lh_cfg.raw or {}
            targets = raw.get("targets", {})
            ap_config = AutopilotConfig(
                customer_id=lh_cfg.customer_id,
                automation_mode=raw.get("automation_mode", "suggest"),
                risk_tolerance=raw.get("risk_tolerance", "conservative"),
                daily_spend_cap=lh_cfg.spend_caps.daily or 0,
                monthly_spend_cap=lh_cfg.spend_caps.monthly or 0,
                brand_is_protected=False,
                protected_entities=[],
                client_name=lh_cfg.client_id,
                client_type=lh_cfg.client_type or "ecom",
                primary_kpi=lh_cfg.primary_kpi or "roas",
                target_roas=targets.get("target_roas"),
                target_cpa=targets.get("target_cpa", 25),
            )

            # Compute campaign averages for enrichment
            ro_path = config.db_path.replace("warehouse.duckdb", "warehouse_readonly.duckdb")
            conn2 = duckdb.connect(config.db_path)
            try:
                conn2.execute(f"ATTACH '{ro_path}' AS ro (READ_ONLY);")
            except Exception:
                pass
            avg_ctrs, avg_cvrs = compute_campaign_averages(
                conn2, config.customer_id, snapshot_date, 7
            )
            conn2.close()

            # Enrich keyword features
            for k in keywords_list:
                cid = str(k.get("campaign_id", ""))
                k["_campaign_avg_ctr"] = avg_ctrs.get(cid, 0)
                k["_campaign_avg_cvr"] = avg_cvrs.get(cid, 0)

            # Run keyword rules
            kw_recs = []
            for feat in keywords_list:
                ctx = RuleContext(
                    customer_id=config.customer_id,
                    campaign_id=str(feat.get("campaign_id", "")),
                    snapshot_date=snapshot_date,
                    features=feat,
                    insights=[],
                    config=ap_config,
                    db_path=config.db_path,
                )
                for rule_fn in KEYWORD_RULES:
                    try:
                        rec = rule_fn(ctx)
                        if rec is not None:
                            kw_recs.append(rec)
                    except Exception:
                        pass

            # Run search term rules
            for st in search_terms:
                cid = str(st.get("campaign_id", ""))
                st["_campaign_avg_cvr"] = avg_cvrs.get(cid, 0)
                st["_campaign_avg_cpc"] = 0
                ctx = RuleContext(
                    customer_id=config.customer_id,
                    campaign_id=cid,
                    snapshot_date=snapshot_date,
                    features=st,
                    insights=[],
                    config=ap_config,
                    db_path=config.db_path,
                )
                for rule_fn in SEARCH_TERM_RULES:
                    try:
                        rec = rule_fn(ctx)
                        if rec is not None:
                            kw_recs.append(rec)
                    except Exception:
                        pass

            rec_count = len(kw_recs)

            # Group recommendations
            groups = {}
            for rec in sorted(kw_recs, key=lambda r: r.priority):
                prefix = rec.rule_id.rsplit("-", 1)[0]
                group_map = {
                    "KW-PAUSE": "Keyword Pause",
                    "KW-BID": "Keyword Bid Adjustments",
                    "KW-REVIEW": "Keyword Review",
                    "ST-ADD": "Search Term Adds",
                    "ST-NEG": "Search Term Negatives",
                }
                gname = group_map.get(prefix, prefix)
                if gname not in groups:
                    groups[gname] = []
                groups[gname].append(rec)

            group_order = [
                "Keyword Pause", "Keyword Bid Adjustments",
                "Search Term Negatives", "Search Term Adds", "Keyword Review",
            ]
            for gn in group_order:
                if gn in groups:
                    rec_groups.append((gn, groups[gn]))
            for gn, recs in groups.items():
                if gn not in group_order:
                    rec_groups.append((gn, recs))

        except Exception as e:
            print(f"[Dashboard] Keyword recommendations error: {e}")
            import traceback
            traceback.print_exc()

        return render_template(
            "keywords.html",
            client_name=config.client_name,
            available_clients=clients,
            current_client_config=current_client_path,
            snapshot_date=str(snapshot_date),
            target_cpa=target_cpa,
            keywords=keywords_list,
            search_terms=search_terms,
            campaigns=campaigns,
            active_count=active_count,
            low_qs_count=low_qs_count,
            low_data_count=low_data_count,
            wasted_spend_dollars=wasted_spend,
            avg_cpa_dollars=avg_cpa_dollars,
            avg_qs=avg_qs,
            rec_groups=rec_groups,
            rec_count=rec_count,
        )

    @app.route("/ads")
    @login_required
    def ads():
        """Ads page - show ad performance and recommendations."""
        config = get_current_config()
        clients = get_available_clients()
        current_client_path = session.get("current_client_config")

        try:
            conn = duckdb.connect(config.db_path)
            try:
                ro_path = config.db_path.replace("warehouse.duckdb", "warehouse_readonly.duckdb")
                conn.execute(f"ATTACH '{ro_path}' AS ro (READ_ONLY);")
            except Exception:
                pass

            # Get latest snapshot date from ad features
            latest_date = conn.execute(
                "SELECT MAX(snapshot_date) FROM analytics.ad_features_daily"
            ).fetchone()[0]

            if not latest_date:
                conn.close()
                return render_template(
                    "ads.html",
                    client_name=config.client_name,
                    available_clients=clients,
                    current_client_config=current_client_path,
                    error="No ad data available. Run ad features generation first.",
                    ads=[],
                    ad_groups=[],
                    recommendations=[],
                    summary={},
                )

            # Load ad features
            ad_features_df = conn.execute(
                "SELECT * FROM analytics.ad_features_daily WHERE snapshot_date = ?",
                [latest_date],
            ).fetchdf()

            # Load ad group performance
            ad_group_perf_df = conn.execute(
                "SELECT * FROM ro.analytics.ad_group_daily WHERE snapshot_date = ?",
                [latest_date],
            ).fetchdf()

            # Convert to dicts
            ad_features = ad_features_df.to_dict("records")
            ad_groups = ad_group_perf_df.to_dict("records")

            # Compute summary stats
            total_ads = len(ad_features)
            total_ad_groups = len(ad_groups)

            poor_strength_count = sum(
                1
                for f in ad_features
                if f.get("ad_type") == "RESPONSIVE_SEARCH_AD"
                and f.get("ad_strength") == "POOR"
            )

            low_data_count = sum(1 for f in ad_features if f.get("low_data_flag"))

            avg_ctr = ad_features_df["ctr_30d"].mean() if len(ad_features) > 0 else 0
            avg_cvr = ad_features_df["cvr_30d"].mean() if len(ad_features) > 0 else 0

            summary = {
                "total_ads": total_ads,
                "total_ad_groups": total_ad_groups,
                "poor_strength": poor_strength_count,
                "low_data": low_data_count,
                "avg_ctr": avg_ctr,
                "avg_cvr": avg_cvr,
                "snapshot_date": str(latest_date),
            }

            # Get unique campaigns for filter
            campaigns = sorted(set(f["campaign_name"] for f in ad_features))

            # Generate recommendations using ad rules
            from act_autopilot.rules.ad_rules import apply_ad_rules
            from act_lighthouse.config import load_client_config

            lh_cfg = load_client_config(current_client_path)
            raw = lh_cfg.raw or {}
            from act_autopilot.models import AutopilotConfig

            targets = raw.get("targets", {})
            ap_config = AutopilotConfig(
                customer_id=lh_cfg.customer_id,
                automation_mode=raw.get("automation_mode", "suggest"),
                risk_tolerance=raw.get("risk_tolerance", "conservative"),
                daily_spend_cap=lh_cfg.spend_caps.daily or 0,
                monthly_spend_cap=lh_cfg.spend_caps.monthly or 0,
                brand_is_protected=False,
                protected_entities=[],
                client_name=lh_cfg.client_id,
                client_type=lh_cfg.client_type or "ecom",
                primary_kpi=lh_cfg.primary_kpi or "roas",
                target_roas=targets.get("target_roas"),
                target_cpa=targets.get("target_cpa", 25),
            )

            recommendations_list = apply_ad_rules(ad_features, ap_config)

            # Convert to dicts
            recommendations = [
                {
                    "rule_id": r.rule_id,
                    "rule_name": r.rule_name,
                    "entity_type": r.entity_type,
                    "entity_id": r.entity_id,
                    "action_type": r.action_type,
                    "risk_tier": r.risk_tier,
                    "confidence": r.confidence,
                    "priority": r.priority,
                    "rationale": r.rationale,
                    "campaign_name": r.campaign_name,
                    "ad_group_name": r.ad_group_name,
                    "current_value": r.current_value,
                    "recommended_value": r.recommended_value,
                }
                for r in recommendations_list
            ]

            # Group recommendations by category
            pause_recs = [r for r in recommendations if r["action_type"] == "pause_ad"]
            review_recs = [r for r in recommendations if r["action_type"] == "review_ad"]
            asset_recs = [
                r for r in recommendations if r["action_type"] == "asset_insight"
            ]
            adgroup_recs = [
                r for r in recommendations if r["action_type"] == "review_ad_group"
            ]

            conn.close()

            return render_template(
                "ads.html",
                client_name=config.client_name,
                available_clients=clients,
                current_client_config=current_client_path,
                ads=ad_features,
                ad_groups=ad_groups,
                recommendations=recommendations,
                pause_recs=pause_recs,
                review_recs=review_recs,
                asset_recs=asset_recs,
                adgroup_recs=adgroup_recs,
                summary=summary,
                campaigns=campaigns,
                error=None,
            )

        except Exception as e:
            print(f"[Dashboard] ERROR in /ads route: {e}")
            import traceback

            traceback.print_exc()
            return render_template(
                "ads.html",
                client_name=config.client_name,
                available_clients=clients,
                current_client_config=current_client_path,
                error=str(e),
                ads=[],
                ad_groups=[],
                recommendations=[],
                summary={},
            )



    @app.route("/shopping")
    @login_required
    def shopping():
        """Shopping dashboard with 4 tabs: Campaigns, Products, Feed Quality, Recommendations."""
        try:
            cfg = get_current_config()
            conn = duckdb.connect(cfg.db_path, read_only=True)
            
            # Get latest snapshot date
            snapshot_date = conn.execute("""
                SELECT MAX(snapshot_date) 
                FROM analytics.product_features_daily
                WHERE customer_id = ?
            """, (cfg.customer_id,)).fetchone()
            
            if not snapshot_date or not snapshot_date[0]:
                conn.close()
                return render_template(
                    "shopping.html",
                    client_name=cfg.client_name,
                    available_clients=get_available_clients(),
                    current_client_config=session.get("current_client_config"),
                    error="No Shopping data available. Run Shopping Lighthouse first.",
                )
            
            snapshot_date = snapshot_date[0]
            
            # ==================== TAB 1: CAMPAIGNS ====================
            campaigns = conn.execute("""
                SELECT 
                    campaign_id,
                    campaign_name,
                    campaign_priority,
                    feed_label,
                    SUM(impressions) as impressions,
                    SUM(clicks) as clicks,
                    SUM(cost_micros) as cost_micros,
                    SUM(conversions) as conversions,
                    SUM(conversions_value) as conv_value
                FROM raw_shopping_campaign_daily
                WHERE customer_id = ?
                    AND snapshot_date BETWEEN ? - INTERVAL 30 DAYS AND ?
                GROUP BY campaign_id, campaign_name, campaign_priority, feed_label
                ORDER BY SUM(cost_micros) DESC
            """, (cfg.customer_id, snapshot_date, snapshot_date)).fetchall()
            
            campaigns_list = []
            for c in campaigns:
                cost = float(c[6] or 0) / 1_000_000
                conv_value = float(c[8] or 0) / 1_000_000
                roas = conv_value / cost if cost > 0 else 0
                
                # Map priority
                priority_map = {0: "Low", 1: "Medium", 2: "High"}
                priority_str = priority_map.get(c[2], "Unknown")
                
                campaigns_list.append({
                    "campaign_id": c[0],
                    "campaign_name": c[1],
                    "priority": priority_str,
                    "priority_num": c[2],
                    "feed_label": c[3] or "None",
                    "impressions": int(c[4] or 0),
                    "clicks": int(c[5] or 0),
                    "cost": cost,
                    "conversions": float(c[7] or 0),
                    "conv_value": conv_value,
                    "roas": roas,
                })
            
            # ==================== TAB 2: PRODUCTS ====================
            products = conn.execute("""
                SELECT 
                    product_id,
                    product_title,
                    product_brand,
                    product_category,
                    availability,
                    impressions_w30_sum,
                    clicks_w30_sum,
                    cost_micros_w30_sum,
                    conversions_w30_sum,
                    conversions_value_w30_sum,
                    ctr_w30,
                    cvr_w30,
                    roas_w30,
                    stock_out_flag,
                    stock_out_days_w30,
                    feed_quality_score,
                    has_price_mismatch,
                    has_disapproval,
                    new_product_flag,
                    days_live,
                    low_data_flag
                FROM analytics.product_features_daily
                WHERE snapshot_date = ?
                    AND customer_id = ?
                ORDER BY cost_micros_w30_sum DESC
                LIMIT 200
            """, (snapshot_date, cfg.customer_id)).fetchall()
            
            products_list = []
            for p in products:
                products_list.append({
                    "product_id": p[0],
                    "product_title": p[1],
                    "product_brand": p[2],
                    "product_category": p[3],
                    "availability": p[4],
                    "impressions": int(p[5] or 0),
                    "clicks": int(p[6] or 0),
                    "cost": float(p[7] or 0) / 1_000_000,
                    "conversions": float(p[8] or 0),
                    "conv_value": float(p[9] or 0) / 1_000_000,
                    "ctr": float(p[10] or 0) * 100,
                    "cvr": float(p[11] or 0) * 100,
                    "roas": float(p[12] or 0),
                    "stock_out_flag": bool(p[13]),
                    "stock_out_days": int(p[14] or 0),
                    "feed_quality": float(p[15] or 0) * 100,
                    "price_mismatch": bool(p[16]),
                    "disapproved": bool(p[17]),
                    "is_new": bool(p[18]),
                    "days_live": int(p[19] or 0),
                    "low_data": bool(p[20]),
                })
            
            # ==================== TAB 3: FEED QUALITY ====================
            feed_quality = conn.execute("""
                SELECT 
                    approval_status,
                    price_mismatch,
                    COUNT(*) as count
                FROM raw_product_feed_quality
                WHERE customer_id = ?
                    AND snapshot_date = ?
                GROUP BY approval_status, price_mismatch
            """, (cfg.customer_id, snapshot_date)).fetchall()
            
            total_feed_products = sum(f[2] for f in feed_quality)
            approved_count = sum(f[2] for f in feed_quality if f[0] == 'APPROVED' and not f[1])
            disapproved_count = sum(f[2] for f in feed_quality if f[0] == 'DISAPPROVED')
            price_mismatch_count = sum(f[2] for f in feed_quality if f[1])
            
            pct_approved = (approved_count / total_feed_products * 100) if total_feed_products > 0 else 0
            pct_disapproved = (disapproved_count / total_feed_products * 100) if total_feed_products > 0 else 0
            pct_price_mismatch = (price_mismatch_count / total_feed_products * 100) if total_feed_products > 0 else 0
            
            # Get products with issues
            feed_issues = conn.execute("""
                SELECT 
                    f.product_id,
                    p.product_title,
                    p.product_brand,
                    f.approval_status,
                    f.price_mismatch,
                    f.disapproval_reasons
                FROM raw_product_feed_quality f
                LEFT JOIN analytics.product_features_daily p 
                    ON f.product_id = p.product_id AND f.customer_id = p.customer_id
                WHERE f.customer_id = ?
                    AND f.snapshot_date = ?
                    AND (f.approval_status != 'APPROVED' OR f.price_mismatch = TRUE)
                ORDER BY f.approval_status DESC
                LIMIT 100
            """, (cfg.customer_id, snapshot_date)).fetchall()
            
            feed_issues_list = []
            for f in feed_issues:
                issues = []
                if f[3] == 'DISAPPROVED':
                    issues.append('Disapproved')
                if f[4]:
                    issues.append('Price Mismatch')
                
                feed_issues_list.append({
                    "product_id": f[0],
                    "product_title": f[1] or "Unknown",
                    "product_brand": f[2] or "Unknown",
                    "approval_status": f[3],
                    "price_mismatch": f[4],
                    "disapproval_reasons": f[5] if f[5] else [],
                    "issues": ", ".join(issues),
                })
            
            # ==================== TAB 4: RECOMMENDATIONS ====================
            recommendations_list = []
            
            # Try to generate recommendations (may be empty if rules don't fire)
            try:
                from act_autopilot.rules import shopping_rules
                import pandas as pd
                
                products_df = conn.execute("""
                    SELECT *
                    FROM analytics.product_features_daily
                    WHERE customer_id = ?
                        AND snapshot_date = ?
                """, (cfg.customer_id, snapshot_date)).df()
                
                # Try running a few rules (safe mode - catch errors)
                if len(products_df) > 0:
                    # Example: Try to get high ROAS products
                    high_roas = products_df[products_df['roas_w30'] > 4]
                    for _, row in high_roas.head(10).iterrows():
                        recommendations_list.append({
                            "rule_id": "SHOP-BID-001",
                            "entity_type": "product",
                            "entity_id": row['product_id'],
                            "entity_name": row['product_title'],
                            "action_type": "Increase Bid",
                            "current_value": "Current bid",
                            "proposed_value": "+15% bid",
                            "reasoning": f"High ROAS ({row['roas_w30']:.2f}) indicates strong performance",
                            "confidence": 0.85,
                            "risk_tier": "LOW",
                        })
            except Exception as e:
                # If recommendations fail, continue with empty list
                pass
            
            # Summary stats
            total_products = len(products_list)
            total_cost = sum(p["cost"] for p in products_list)
            total_conversions = sum(p["conversions"] for p in products_list)
            total_conv_value = sum(p["conv_value"] for p in products_list)
            avg_roas = total_conv_value / total_cost if total_cost > 0 else 0
            
            out_of_stock = sum(1 for p in products_list if p["stock_out_flag"])
            price_mismatches = sum(1 for p in products_list if p["price_mismatch"])
            disapproved = sum(1 for p in products_list if p["disapproved"])
            feed_issues_count = out_of_stock + price_mismatches + disapproved
            
            conn.close()
            
            return render_template(
                "shopping.html",
                client_name=cfg.client_name,
                available_clients=get_available_clients(),
                current_client_config=session.get("current_client_config"),
                snapshot_date=snapshot_date,
                # Tab 1: Campaigns
                campaigns=campaigns_list,
                total_campaigns=len(campaigns_list),
                # Tab 2: Products
                products=products_list,
                total_products=total_products,
                total_cost=total_cost,
                total_conversions=total_conversions,
                total_conv_value=total_conv_value,
                avg_roas=avg_roas,
                out_of_stock=out_of_stock,
                price_mismatches=price_mismatches,
                disapproved=disapproved,
                feed_issues_count=feed_issues_count,
                # Tab 3: Feed Quality
                total_feed_products=total_feed_products,
                pct_approved=pct_approved,
                pct_disapproved=pct_disapproved,
                pct_price_mismatch=pct_price_mismatch,
                feed_issues=feed_issues_list,
                # Tab 4: Recommendations
                recommendations=recommendations_list,
                total_recommendations=len(recommendations_list),
            )
            
        except Exception as e:
            return render_template(
                "shopping.html",
                client_name="Error",
                available_clients=get_available_clients(),
                current_client_config=session.get("current_client_config"),
                error=str(e),
            )

    @app.route("/settings", methods=["GET", "POST"])
    @login_required
    def settings():
        """Settings page for editing client configuration."""
        config = get_current_config()
        clients = get_available_clients()
        current_client_path = session.get("current_client_config")

        if request.method == "POST":
            # Update configuration from form
            config.client_name = request.form.get("client_name", config.client_name)
            config.client_type = request.form.get("client_type", config.client_type)
            config.primary_kpi = request.form.get("primary_kpi", config.primary_kpi)
            config.automation_mode = request.form.get(
                "automation_mode", config.automation_mode
            )
            config.risk_tolerance = request.form.get(
                "risk_tolerance", config.risk_tolerance
            )

            # Update targets
            target_roas = request.form.get("target_roas", "")
            config.target_roas = float(target_roas) if target_roas else None

            target_cpa = request.form.get("target_cpa", "")
            config.target_cpa = float(target_cpa) if target_cpa else None

            # Update spend caps
            daily_cap = request.form.get("daily_cap", "")
            config.daily_cap = float(daily_cap) if daily_cap else 0

            monthly_cap = request.form.get("monthly_cap", "")
            config.monthly_cap = float(monthly_cap) if monthly_cap else 0

            # Update protected entities
            config.brand_protected = request.form.get("brand_protected") == "on"

            # Save to YAML
            config.save()

            flash("Settings saved successfully", "success")
            return redirect(url_for("settings"))

        return render_template(
            "settings.html",
            client_name=config.client_name,
            available_clients=clients,
            current_client_config=current_client_path,
            config=config,
        )
