"""
Keywords page route - keyword performance and recommendations.
"""

from flask import Blueprint, render_template, session, current_app
from act_dashboard.auth import login_required
from act_dashboard.routes.shared import get_current_config, get_available_clients
import duckdb
from datetime import date, timedelta

bp = Blueprint('keywords', __name__)


@bp.route("/keywords")
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
    st_start = snapshot_date - timedelta(days=29)

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
        
        # Map dashboard action types to executor-compatible types
        action_type_map = {
            'keyword_pause': 'pause_keyword',
            'keyword_bid_decrease': 'update_keyword_bid',
            'keyword_bid_increase': 'update_keyword_bid',
            'keyword_bid_hold': 'update_keyword_bid',
            'add_keyword_exact': 'add_keyword',
            'add_keyword_phrase': 'add_keyword',
            'add_negative_exact': 'add_negative_keyword',
        }
        
        # Build explicit dict mapping (avoids asdict() serialization issues)
        # Use None-safe defaults to prevent JavaScript/sorting errors
        keywords_cache = []
        for idx, rec in enumerate(kw_recs):
            # Map action type
            mapped_action_type = action_type_map.get(rec.action_type, rec.action_type)
            
            keywords_cache.append({
                'id': idx,
                'rule_id': rec.rule_id,
                'rule_name': rec.rule_name,
                'entity_type': rec.entity_type,
                'entity_id': rec.entity_id,
                'action_type': mapped_action_type,
                'risk_tier': rec.risk_tier,
                'confidence': rec.confidence or 0.0,
                'current_value': rec.current_value,  # Can be None - handled by template
                'recommended_value': rec.recommended_value,  # Can be None - handled by template
                'change_pct': rec.change_pct,  # Can be None - handled by template
                'rationale': rec.rationale or '',
                'campaign_name': rec.campaign_name or '',
                'blocked': rec.blocked or False,
                'block_reason': rec.block_reason or '',
                'priority': rec.priority if rec.priority is not None else 50,
                'constitution_refs': rec.constitution_refs or [],
                'guardrails_checked': rec.guardrails_checked or [],
                'evidence': rec.evidence if rec.evidence else {},
                'triggering_diagnosis': rec.triggering_diagnosis or '',
                'triggering_confidence': rec.triggering_confidence or 0.0,
                'expected_impact': rec.expected_impact or '',
            })
        
        # Store in cache for execution API (live recommendations)
        # Using server-side cache instead of session cookies (no size limit!)
        current_app.config['RECOMMENDATIONS_CACHE']['keywords'] = keywords_cache

        # Group recommendations using cache dicts (which have 'id' field for template)
        groups = {}
        for rec_dict in sorted(keywords_cache, key=lambda r: r['priority']):
            prefix = rec_dict['rule_id'].rsplit("-", 1)[0]
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
            groups[gname].append(rec_dict)

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
