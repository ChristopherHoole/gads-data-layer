"""
Keywords page route - keyword performance and recommendations.
Refactored into smaller, focused functions.
Chat 21d: Redesigned with Bootstrap 5, pagination, filters, rule visibility
"""

from flask import Blueprint, render_template, request
from act_dashboard.auth import login_required
from act_dashboard.routes.shared import (
    get_page_context,
    get_db_connection,
    get_date_range_from_session,
    build_autopilot_config,
    recommendation_to_dict,
    cache_recommendations
)
from act_dashboard.routes.rule_helpers import get_rules_for_page
from datetime import date, timedelta
from typing import List, Dict, Any, Tuple
import duckdb

bp = Blueprint('keywords', __name__)


def load_keyword_features(conn: duckdb.DuckDBPyConnection, customer_id: str, snapshot_date: date) -> List[Dict[str, Any]]:
    """
    Load keyword features from database.
    
    Args:
        conn: Database connection
        customer_id: Customer ID
        snapshot_date: Snapshot date
        
    Returns:
        List of keyword feature dictionaries
    """
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
    """, [customer_id, snapshot_date]).fetchall()

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
    
    return keywords_list


def compute_keyword_summary(keywords_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compute summary statistics for keywords.
    
    Args:
        keywords_list: List of keyword dictionaries
        
    Returns:
        Dictionary of summary stats
    """
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
    
    return {
        'active_count': active_count,
        'low_qs_count': low_qs_count,
        'low_data_count': low_data_count,
        'wasted_spend_dollars': wasted_spend,
        'avg_cpa_dollars': avg_cpa_dollars,
        'avg_qs': avg_qs,
    }


def extract_campaign_list(keywords_list: List[Dict[str, Any]]) -> List[Tuple[str, str]]:
    """
    Extract unique campaigns for filter dropdown.
    
    Args:
        keywords_list: List of keyword dictionaries
        
    Returns:
        Sorted list of (campaign_id, campaign_name) tuples
    """
    campaigns_dict = {}
    for k in keywords_list:
        cid = str(k.get("campaign_id", ""))
        cname = k.get("campaign_name", cid)
        if cid not in campaigns_dict:
            campaigns_dict[cid] = cname
    return sorted(campaigns_dict.items(), key=lambda x: x[1])


def load_search_terms(conn: duckdb.DuckDBPyConnection, customer_id: str, snapshot_date: date) -> List[Dict[str, Any]]:
    """
    Load search term aggregates for last 30 days.
    
    Args:
        conn: Database connection
        customer_id: Customer ID
        snapshot_date: Snapshot date
        
    Returns:
        List of search term dictionaries
    """
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
    """, [customer_id, st_start, snapshot_date]).fetchall()

    st_cols = [d[0] for d in conn.description]
    search_terms = []
    for row in st_rows:
        d = dict(zip(st_cols, row))
        d["cost_dollars"] = float(d.get("cost_micros") or 0) / 1_000_000
        d["cpa_dollars"] = (float(d["cpa_micros"]) / 1_000_000) if d.get("cpa_micros") and float(d["cpa_micros"]) > 0 else 0
        search_terms.append(d)
    
    return search_terms


def generate_keyword_recommendations(
    keywords_list: List[Dict[str, Any]],
    search_terms: List[Dict[str, Any]],
    config,
    current_client_path: str,
    snapshot_date: date
) -> List[Dict[str, Any]]:
    """
    Generate keyword and search term recommendations.
    
    Args:
        keywords_list: List of keyword dictionaries
        search_terms: List of search term dictionaries
        config: Dashboard config
        current_client_path: Path to client config
        snapshot_date: Snapshot date
        
    Returns:
        List of recommendation dictionaries (with 'id' field)
    """
    from act_lighthouse.keyword_diagnostics import compute_campaign_averages
    from act_autopilot.models import RuleContext
    from act_autopilot.rules.keyword_rules import KEYWORD_RULES, SEARCH_TERM_RULES

    # Build AutopilotConfig
    ap_config = build_autopilot_config(current_client_path)

    # Compute campaign averages for enrichment
    conn2 = get_db_connection(config)
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
    
    # Convert recommendations to dicts
    keywords_cache = []
    for idx, rec in enumerate(kw_recs):
        rec_dict = recommendation_to_dict(rec, index=idx)
        # Map action type
        rec_dict['action_type'] = action_type_map.get(rec.action_type, rec.action_type)
        keywords_cache.append(rec_dict)
    
    return keywords_cache


def group_keyword_recommendations(recommendations: List[Dict[str, Any]]) -> List[Tuple[str, List[Dict]]]:
    """
    Group recommendations by category.
    
    Args:
        recommendations: List of recommendation dictionaries
        
    Returns:
        List of (group_name, recommendations) tuples
    """
    groups = {}
    for rec_dict in sorted(recommendations, key=lambda r: r['priority']):
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

    # Order groups
    group_order = [
        "Keyword Pause", "Keyword Bid Adjustments",
        "Search Term Negatives", "Search Term Adds", "Keyword Review",
    ]
    rec_groups = []
    for gn in group_order:
        if gn in groups:
            rec_groups.append((gn, groups[gn]))
    for gn, recs in groups.items():
        if gn not in group_order:
            rec_groups.append((gn, recs))
    
    return rec_groups


@bp.route("/keywords")
@login_required
def keywords():
    """
    Keywords page with Bootstrap 5, date filtering, pagination, match type filter, and rule visibility.
    
    URL Parameters:
        days: 7, 30, or 90 (default: 7)
        page: Page number (default: 1)
        per_page: Rows per page - 10, 25, 50, 100 (default: 25)
        match_type: 'all', 'exact', 'phrase', 'broad' (default: 'all')
    
    Chat 21d: Complete redesign with search terms integration and rule visibility
    """
    # Get date range from session.
    # Keywords uses pre-aggregated windowed columns (_w7/_w30).
    # Custom date ranges are not supported by the schema — fall back to w30.
    active_days, date_from, date_to = get_date_range_from_session()
    if date_from and date_to:
        # Custom range: use 30d window as closest approximation
        days = 30
        print("[Keywords] Custom date range selected — using w30 windowed columns as approximation")
    elif active_days in [7, 30, 90]:
        days = active_days
    else:
        days = 30

    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=25, type=int)
    match_type = request.args.get('match_type', default='all', type=str).lower()

    # Validate parameters
    if page < 1:
        page = 1
    if per_page not in [10, 25, 50, 100]:
        per_page = 25
    if match_type not in ['all', 'exact', 'phrase', 'broad']:
        match_type = 'all'
    
    # Get common page context
    config, clients, current_client_path = get_page_context()
    
    # Get database connection
    conn = get_db_connection(config)
    
    # Determine snapshot date (latest available)
    snap_row = conn.execute("""
        SELECT MAX(snapshot_date) FROM analytics.keyword_features_daily
        WHERE customer_id = ?
    """, [config.customer_id]).fetchone()
    snapshot_date = snap_row[0] if snap_row and snap_row[0] else date.today()
    
    # Determine which rolling window columns to use based on days
    # For 7 days: use _w7 columns
    # For 30 days: use _w30 columns  
    # For 90 days: use _w30 columns (w90 doesn't exist yet)
    window_suffix = 'w7' if days == 7 else 'w30'
    
    # QUERY 1: Metrics Bar (8 metrics)
    try:
        metrics_row = conn.execute(f"""
            SELECT 
                COUNT(DISTINCT keyword_id) as total_keywords,
                COUNT(DISTINCT CASE WHEN status = 'ENABLED' THEN keyword_id END) as active_keywords,
                COUNT(DISTINCT CASE WHEN status = 'PAUSED' THEN keyword_id END) as paused_keywords,
                SUM(clicks_{window_suffix}_sum) as clicks,
                SUM(cost_micros_{window_suffix}_sum)/1000000 as cost,
                SUM(conversions_{window_suffix}_sum) as conversions,
                SUM(cost_micros_{window_suffix}_sum)/1000000/NULLIF(SUM(conversions_{window_suffix}_sum), 0) as cpa,
                AVG(quality_score) as avg_qs
            FROM analytics.keyword_features_daily
            WHERE customer_id = ?
              AND snapshot_date = ?
        """, [config.customer_id, snapshot_date]).fetchone()
        
        metrics = {
            'total_keywords': int(metrics_row[0] or 0),
            'active_keywords': int(metrics_row[1] or 0),
            'paused_keywords': int(metrics_row[2] or 0),
            'clicks': int(metrics_row[3] or 0),
            'cost': float(metrics_row[4] or 0),
            'conversions': int(metrics_row[5] or 0),
            'cpa': float(metrics_row[6] or 0),
            'avg_qs': float(metrics_row[7] or 0),
        }
    except Exception as e:
        print(f"[Keywords] Metrics query error: {e}")
        metrics = {
            'total_keywords': 0, 'active_keywords': 0, 'paused_keywords': 0,
            'clicks': 0, 'cost': 0, 'conversions': 0, 'cpa': 0, 'avg_qs': 0
        }
    
    # Calculate wasted spend (keywords with 0 conversions but >$0 cost)
    try:
        wasted_row = conn.execute(f"""
            SELECT SUM(cost_micros_{window_suffix}_sum) / 1000000 as wasted
            FROM analytics.keyword_features_daily
            WHERE customer_id = ?
              AND snapshot_date = ?
              AND conversions_{window_suffix}_sum = 0
              AND cost_micros_{window_suffix}_sum > 0
        """, [config.customer_id, snapshot_date]).fetchone()
        wasted_spend = float(wasted_row[0] or 0)
    except Exception as e:
        print(f"[Keywords] Wasted spend query error: {e}")
        wasted_spend = 0
    
    metrics['wasted_spend'] = wasted_spend
    
    # QUERY 2: Total Count (for pagination, with match type filter)
    count_query = """
        SELECT COUNT(DISTINCT keyword_id) as total
        FROM analytics.keyword_features_daily
        WHERE customer_id = ?
          AND snapshot_date = ?
    """
    count_params = [config.customer_id, snapshot_date]
    
    if match_type != 'all':
        count_query += " AND UPPER(match_type) = ?"
        count_params.append(match_type.upper())
    
    try:
        total_count = conn.execute(count_query, count_params).fetchone()[0] or 0
    except Exception as e:
        print(f"[Keywords] Count query error: {e}")
        total_count = 0
    
    # Calculate pagination
    total_pages = max(1, (total_count + per_page - 1) // per_page)
    if page > total_pages:
        page = total_pages
    offset = (page - 1) * per_page
    
    # QUERY 3: Keywords Table (with pagination and match type filter)
    keywords_query = f"""
        SELECT 
            keyword_id,
            keyword_text,
            match_type,
            status,
            campaign_name,
            ad_group_name,
            bid_micros / 1000000 as max_cpc,
            quality_score,
            quality_score_landing_page as landing_page_score,
            quality_score_relevance as ad_relevance_score,
            quality_score_creative as expected_ctr_score,
            clicks_{window_suffix}_sum as clicks,
            cost_micros_{window_suffix}_sum / 1000000 as cost,
            conversions_{window_suffix}_sum as conversions,
            cpa_{window_suffix} / 1000000 as cpa,
            roas_{window_suffix} as roas
        FROM analytics.keyword_features_daily
        WHERE customer_id = ?
          AND snapshot_date = ?
    """
    keywords_params = [config.customer_id, snapshot_date]
    
    if match_type != 'all':
        keywords_query += " AND UPPER(match_type) = ?"
        keywords_params.append(match_type.upper())
    
    keywords_query += f"""
        ORDER BY cost_micros_{window_suffix}_sum DESC
        LIMIT ? OFFSET ?
    """
    keywords_params.extend([per_page, offset])
    
    try:
        keywords = conn.execute(keywords_query, keywords_params).fetchall()
    except Exception as e:
        print(f"[Keywords] Keywords table query error: {e}")
        import traceback
        traceback.print_exc()
        keywords = []
    
    # QUERY 4: QS Distribution (for card)
    try:
        qs_distribution = conn.execute("""
            SELECT 
                CASE 
                    WHEN quality_score >= 8 THEN '8-10'
                    WHEN quality_score >= 5 THEN '5-7'
                    WHEN quality_score >= 1 THEN '1-4'
                    ELSE 'N/A'
                END as qs_range,
                COUNT(DISTINCT keyword_id) as count
            FROM analytics.keyword_features_daily
            WHERE customer_id = ?
              AND snapshot_date = ?
            GROUP BY qs_range
            ORDER BY qs_range DESC
        """, [config.customer_id, snapshot_date]).fetchall()
    except Exception as e:
        print(f"[Keywords] QS distribution query error: {e}")
        qs_distribution = []
    
    # QUERY 5: Low Data Count (for card)
    try:
        low_data_row = conn.execute("""
            SELECT COUNT(DISTINCT keyword_id) as low_data_count
            FROM analytics.keyword_features_daily
            WHERE customer_id = ?
              AND snapshot_date = ?
              AND low_data_flag = true
        """, [config.customer_id, snapshot_date]).fetchone()
        low_data_count = int(low_data_row[0] or 0)
    except Exception as e:
        print(f"[Keywords] Low data count query error: {e}")
        low_data_count = 0
    
    # QUERY 6: Search Terms (collapsible section)
    try:
        search_terms = load_search_terms(conn, config.customer_id, snapshot_date)
    except Exception as e:
        print(f"[Keywords] Search terms query error: {e}")
        search_terms = []
    
    # Close database connection
    conn.close()
    
    # QUERY 7: Get Rules for Keywords Page
    try:
        rules = get_rules_for_page('keyword', customer_id=config.customer_id)
    except Exception as e:
        print(f"[Keywords] Rules query error: {e}")
        import traceback
        traceback.print_exc()
        rules = []
    
    # Render template with new Bootstrap 5 design
    return render_template(
        'keywords_new.html',
        # Client context
        client_name=config.client_name,
        available_clients=clients,
        current_client_config=current_client_path,
        # Filter parameters
        days=days,
        active_days=active_days,
        date_from=date_from,
        date_to=date_to,
        page=page,
        per_page=per_page,
        match_type=match_type,
        total_pages=total_pages,
        # Data
        snapshot_date=str(snapshot_date),
        metrics=metrics,
        keywords=keywords,
        total_keywords=total_count,
        qs_distribution=qs_distribution,
        low_data_count=low_data_count,
        wasted_spend=wasted_spend,
        search_terms=search_terms,
        rules=rules,
    )
