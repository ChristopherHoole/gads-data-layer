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
    cache_recommendations,
    get_metrics_collapsed,
    get_chart_metrics,
    get_performance_data
)
from act_dashboard.routes.rule_helpers import get_rules_for_page, count_rules_by_category
from act_dashboard.routes.rules_api import load_rules
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Tuple
import duckdb
from flask import jsonify
from act_autopilot.google_ads_api import (
    load_google_ads_client,
    add_negative_keyword,
    add_adgroup_negative_keyword,
    add_keyword as add_keyword_to_adgroup
)
import json
from datetime import datetime

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


def load_search_terms(
    conn: duckdb.DuckDBPyConnection, 
    customer_id: str, 
    date_from: date,
    date_to: date,
    campaign_id: str = None,
    status: str = None,
    match_type: str = None,
    page: int = 1,
    per_page: int = 25
) -> Dict[str, Any]:
    """
    Load search term aggregates with filters and pagination.
    
    Args:
        conn: Database connection
        customer_id: Customer ID
        date_from: Start date from session
        date_to: End date from session
        campaign_id: Optional campaign filter
        status: Optional status filter
        match_type: Optional match type filter
        page: Page number (1-indexed)
        per_page: Results per page
        
    Returns:
        Dict with keys: data (list), total_count, page, per_page
    """
    # Build WHERE clause
    where_clauses = ["customer_id = ?"]
    params = [customer_id]
    
    where_clauses.append("snapshot_date BETWEEN ? AND ?")
    params.extend([date_from, date_to])
    
    if campaign_id and campaign_id != 'all':
        where_clauses.append("campaign_id = ?")
        params.append(campaign_id)
    
    if status and status != 'all':
        where_clauses.append("UPPER(search_term_status) = ?")
        params.append(status.upper())
    
    if match_type and match_type != 'all':
        where_clauses.append("UPPER(match_type) = ?")
        params.append(match_type.upper())
    
    where_clause = " AND ".join(where_clauses)
    
    # Count total matching rows (before pagination)
    count_query = f"""
        SELECT COUNT(DISTINCT search_term || '|' || campaign_id || '|' || keyword_id)
        FROM ro.analytics.search_term_daily
        WHERE {where_clause}
    """
    total_count = conn.execute(count_query, params).fetchone()[0]
    
    # Calculate offset
    offset = (page - 1) * per_page
    
    # Main query with all required columns
    st_rows = conn.execute(f"""
        SELECT
            search_term,
            keyword_text,
            match_type,
            search_term_status,
            campaign_id,
            campaign_name,
            ad_group_id,
            keyword_id,
            SUM(COALESCE(impressions, 0)) as impressions,
            SUM(COALESCE(clicks, 0)) as clicks,
            AVG(COALESCE(ctr, 0)) as ctr,
            SUM(COALESCE(cost, 0)) as cost,
            CASE WHEN SUM(clicks) > 0
                 THEN SUM(cost) / SUM(clicks)
                 ELSE 0 END as cpc,
            SUM(COALESCE(conversions, 0)) as conversions,
            CASE WHEN SUM(clicks) > 0
                 THEN SUM(conversions)::DOUBLE / SUM(clicks)
                 ELSE 0 END as cvr,
            CASE WHEN SUM(conversions) > 0
                 THEN SUM(cost) / SUM(conversions)
                 ELSE 0 END as cpa,
            CASE WHEN SUM(cost) > 0
                 THEN SUM(COALESCE(conversions_value, 0)) / SUM(cost)
                 ELSE 0 END as roas
        FROM ro.analytics.search_term_daily
        WHERE {where_clause}
        GROUP BY search_term, keyword_text, match_type, search_term_status,
                 campaign_id, campaign_name, ad_group_id, keyword_id
        ORDER BY SUM(cost) DESC
        LIMIT ? OFFSET ?
    """, params + [per_page, offset]).fetchall()
    
    st_cols = [d[0] for d in conn.description]
    search_terms = []
    for row in st_rows:
        d = dict(zip(st_cols, row))
        # Ensure numeric types for template
        d['impressions'] = int(d.get('impressions') or 0)
        d['clicks'] = int(d.get('clicks') or 0)
        d['conversions'] = float(d.get('conversions') or 0)
        d['cost'] = float(d.get('cost') or 0)
        d['ctr'] = float(d.get('ctr') or 0)
        d['cpc'] = float(d.get('cpc') or 0)
        d['cvr'] = float(d.get('cvr') or 0)
        d['cpa'] = float(d.get('cpa') or 0)
        d['roas'] = float(d.get('roas') or 0)
        search_terms.append(d)
    
    return {
        'data': search_terms,
        'total_count': total_count,
        'page': page,
        'per_page': per_page
    }


def flag_negative_keywords(search_terms: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Flag search terms as negative keyword opportunities based on 3 criteria.
    
    Criteria:
    1. 0% CVR + ≥10 clicks
    2. ≥£50 cost + 0 conversions  
    3. CTR <1% + ≥20 impressions
    
    Args:
        search_terms: List of search term dictionaries
        
    Returns:
        Same list with negative_flag and flag_reason added to each term
    """
    for st in search_terms:
        flagged = False
        reasons = []
        
        clicks = st.get('clicks', 0)
        conversions = st.get('conversions', 0)
        cost = st.get('cost', 0)
        ctr = st.get('ctr', 0)
        impressions = st.get('impressions', 0)
        
        # Criterion 1: 0% CVR + ≥10 clicks
        if clicks >= 10 and conversions == 0:
            flagged = True
            reasons.append("0% CVR with 10+ clicks")
        
        # Criterion 2: ≥£50 cost + 0 conversions
        if cost >= 50 and conversions == 0:
            flagged = True
            reasons.append("£50+ spend, no conversions")
        
        # Criterion 3: CTR <1% + ≥20 impressions
        if ctr < 0.01 and impressions >= 20:
            flagged = True
            reasons.append("CTR <1% with 20+ impressions")
        
        st['negative_flag'] = flagged
        st['flag_reason'] = " | ".join(reasons) if reasons else ""
    
    return search_terms



def check_keyword_exists(
    conn: duckdb.DuckDBPyConnection,
    customer_id: str,
    ad_group_id: str,
    search_term: str
) -> bool:
    """
    Check if a search term already exists as a keyword in the ad group.
    
    Uses case-insensitive exact text match. If ANY match type exists
    (Exact, Phrase, or Broad), consider it "already added" to prevent
    near-duplicates.
    
    Args:
        conn: Database connection
        customer_id: Customer ID
        ad_group_id: Ad group ID
        search_term: Search term text to check
        
    Returns:
        True if keyword exists, False otherwise
    """
    try:
        result = conn.execute("""
            SELECT COUNT(DISTINCT keyword_text)
            FROM ro.analytics.keyword_daily
            WHERE customer_id = ?
              AND ad_group_id = ?
              AND LOWER(keyword_text) = LOWER(?)
        """, [customer_id, ad_group_id, search_term]).fetchone()
        
        count = result[0] if result else 0
        return count > 0
    except Exception as e:
        print(f"[Keywords] Error checking keyword existence: {e}")
        return False  # Assume doesn't exist on error (allow flagging)


def flag_expansion_opportunities(
    conn: duckdb.DuckDBPyConnection,
    customer_id: str,
    search_terms: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Flag search terms as keyword expansion opportunities based on 4 criteria.
    
    Criteria (ALL must be met):
    1. CVR ≥5% (high conversion rate)
    2. ROAS ≥4.0x (profitable performance)
    3. ≥10 conversions (sufficient data)
    4. Search term NOT already added as keyword
    
    Args:
        conn: Database connection
        customer_id: Customer ID
        search_terms: List of search term dictionaries
        
    Returns:
        Same list with expansion_flag and expansion_reason added to each term
    """
    for st in search_terms:
        flagged = False
        reasons = []
        
        conversions = st.get('conversions', 0)
        cvr = st.get('cvr', 0)
        roas = st.get('roas', 0)
        ad_group_id = st.get('ad_group_id', '')
        search_term = st.get('search_term', '')
        
        # Check all 4 criteria
        meets_cvr = cvr >= 0.05  # 5% = 0.05 decimal
        meets_roas = roas >= 4.0
        meets_conversions = conversions >= 10
        
        # Check if keyword already exists (criterion 4)
        already_exists = check_keyword_exists(
            conn, customer_id, str(ad_group_id), search_term
        )
        
        # Must meet ALL criteria AND not already exist
        if meets_cvr and meets_roas and meets_conversions and not already_exists:
            flagged = True
            reasons.append(f"High CVR ({cvr*100:.1f}%)")
            reasons.append(f"ROAS {roas:.1f}x")
            reasons.append(f"{int(conversions)} conversions")
        
        st['expansion_flag'] = flagged
        st['expansion_reason'] = " | ".join(reasons) if reasons else ""
        
        # Suggest match type based on original search term match
        # EXACT → EXACT, PHRASE → PHRASE, BROAD → PHRASE (tighten)
        match_type = st.get('match_type', '').upper()
        if match_type == 'EXACT':
            st['suggested_match_type'] = 'EXACT'
        elif match_type == 'PHRASE':
            st['suggested_match_type'] = 'PHRASE'
        else:  # BROAD or other
            st['suggested_match_type'] = 'PHRASE'
        
        # Suggest bid based on historical CPC
        cpc = st.get('cpc', 0)
        st['suggested_bid'] = cpc if cpc > 0.10 else 0.10  # Minimum £0.10
    
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




# ==================== Chat 23 M2: Metrics Cards ====================

def _build_date_filters(active_days, date_from, date_to):
    """
    Build current and previous period date filters for SQL WHERE clauses.
    Returns tuple of (current_filter, prev_filter) starting with AND.
    """
    if date_from and date_to:
        _df = datetime.strptime(date_from, '%Y-%m-%d').date()
        _dt = datetime.strptime(date_to, '%Y-%m-%d').date()
        _span = (_dt - _df).days + 1
        _prev_to = (_df - timedelta(days=1)).isoformat()
        _prev_from = (_df - timedelta(days=_span)).isoformat()
        current_filter = f"AND snapshot_date >= '{date_from}' AND snapshot_date <= '{date_to}'"
        prev_filter = f"AND snapshot_date >= '{_prev_from}' AND snapshot_date <= '{_prev_to}'"
    else:
        days = active_days if active_days in [7, 30, 90] else 30
        current_filter = f"AND snapshot_date >= CURRENT_DATE - INTERVAL '{days} days'"
        prev_filter = (
            f"AND snapshot_date >= CURRENT_DATE - INTERVAL '{days * 2} days' "
            f"AND snapshot_date < CURRENT_DATE - INTERVAL '{days} days'"
        )
    return current_filter, prev_filter


def _calculate_change_pct(current, previous):
    """
    Calculate % change. Returns None (show dash) when no previous data.
    Never returns 0% to mask missing data.
    """
    if previous is None or previous == 0:
        return None
    if current is None:
        return -100.0
    return ((current - previous) / previous) * 100.0


def _fmt_kw(value, fmt):
    if value is None:
        return '—'
    v = float(value)
    if fmt == 'currency':
        if v >= 1_000_000: return f'${v/1_000_000:.1f}M'
        if v >= 1_000: return f'${v/1_000:.1f}k'
        return f'${v:,.2f}'
    if fmt in ('percentage', 'rate'): return f'{v:.1f}%'
    if fmt == 'ratio': return f'{v:.2f}x'
    if fmt == 'number':
        if v >= 1_000_000: return f'{v/1_000_000:.2f}M'
        if v >= 1_000: return f'{v/1_000:.1f}k'
        return f'{v:,.0f}'
    return str(v)


def _card_kw(label, value, prev, sparkline, fmt, invert=False, card_type='financial'):
    """Keywords cards with period-over-period comparison."""
    return {
        'label': label,
        'value_display': _fmt_kw(value, fmt),
        'change_pct': _calculate_change_pct(value, prev),
        'sparkline_data': sparkline,
        'format_type': fmt,
        'invert_colours': invert,
        'card_type': card_type,
        'sub_label': None,
    }


def _blank_kw(card_type='financial'):
    return {
        'label': '', 'value_display': '', 'change_pct': None,
        'sparkline_data': None, 'format_type': 'blank',
        'invert_colours': False, 'card_type': card_type, 'sub_label': None,
    }


def load_keyword_metrics_cards(conn, customer_id, window_suffix, snapshot_date, active_days, date_from=None, date_to=None):
    """
    Build financial_cards and actions_cards for Keywords page.

    Uses ro.analytics.keyword_daily for all queries (current, previous, sparklines).
    Compares current period vs previous period for change percentages.

    Financial (8): Cost | Revenue | ROAS | Wasted Spend | Conversions | CPA | Conv Rate | BLANK
    Actions  (8): Impressions | Clicks | Avg CPC | Avg CTR |
                  Search IS | Search Top IS | Search Abs Top IS | Click Share
    """
    # Build date filters for current and previous periods
    current_filter, prev_filter = _build_date_filters(active_days, date_from, date_to)
    
    # ── Query 1: Current period summary from keyword_daily ──────────────────
    try:
        summary = conn.execute(f"""
            SELECT
                SUM(cost_micros) / 1000000.0                                      AS cost,
                SUM(conversions_value)                                             AS revenue,
                SUM(conversions_value) / NULLIF(SUM(cost_micros) / 1000000.0, 0)  AS roas,
                SUM(conversions)                                                   AS conversions,
                (SUM(cost_micros) / 1000000.0) / NULLIF(SUM(conversions), 0)      AS cpa,
                SUM(clicks) * 1.0 / NULLIF(SUM(conversions), 0)                   AS cvr,
                SUM(impressions)                                                   AS impressions,
                SUM(clicks)                                                        AS clicks,
                (SUM(cost_micros) / 1000000.0) / NULLIF(SUM(clicks), 0)           AS cpc,
                SUM(clicks) * 1.0 / NULLIF(SUM(impressions), 0)                   AS ctr,
                AVG(search_impression_share)                                       AS search_is,
                AVG(search_top_impression_share)                                   AS search_top_is,
                AVG(search_absolute_top_impression_share)                          AS search_abs_top_is,
                AVG(click_share)                                                   AS click_share,
                -- Wasted spend: sum cost for keywords with 0 conversions
                SUM(CASE WHEN conversions = 0 AND cost_micros > 0
                    THEN cost_micros / 1000000.0 ELSE 0 END)                       AS wasted_spend
            FROM ro.analytics.keyword_daily
            WHERE customer_id = ?
              {current_filter}
        """, [customer_id]).fetchone()
    except Exception as e:
        print(f"[Keywords M2] Current period query error: {e}")
        summary = None
    
    # ── Query 2: Previous period summary from keyword_daily ─────────────────
    try:
        prev_summary = conn.execute(f"""
            SELECT
                SUM(cost_micros) / 1000000.0                                      AS cost,
                SUM(conversions_value)                                             AS revenue,
                SUM(conversions_value) / NULLIF(SUM(cost_micros) / 1000000.0, 0)  AS roas,
                SUM(conversions)                                                   AS conversions,
                (SUM(cost_micros) / 1000000.0) / NULLIF(SUM(conversions), 0)      AS cpa,
                SUM(clicks) * 1.0 / NULLIF(SUM(conversions), 0)                   AS cvr,
                SUM(impressions)                                                   AS impressions,
                SUM(clicks)                                                        AS clicks,
                (SUM(cost_micros) / 1000000.0) / NULLIF(SUM(clicks), 0)           AS cpc,
                SUM(clicks) * 1.0 / NULLIF(SUM(impressions), 0)                   AS ctr,
                AVG(search_impression_share)                                       AS search_is,
                AVG(search_top_impression_share)                                   AS search_top_is,
                AVG(search_absolute_top_impression_share)                          AS search_abs_top_is,
                AVG(click_share)                                                   AS click_share,
                SUM(CASE WHEN conversions = 0 AND cost_micros > 0
                    THEN cost_micros / 1000000.0 ELSE 0 END)                       AS wasted_spend
            FROM ro.analytics.keyword_daily
            WHERE customer_id = ?
              {prev_filter}
        """, [customer_id]).fetchone()
    except Exception as e:
        print(f"[Keywords M2] Previous period query error: {e}")
        prev_summary = None

    def _v(row, i): return float(row[i]) if row and row[i] is not None else None
    def pct(val): return val * 100 if val is not None else None

    # Current period values
    c = [_v(summary, i) for i in range(15)] if summary else [None] * 15
    
    # Previous period values
    p = [_v(prev_summary, i) for i in range(15)] if prev_summary else [None] * 15

    # ── Query 3: Daily sparkline data from keyword_daily ────────────────────
    try:
        spark_rows = conn.execute(f"""
            SELECT
                snapshot_date,
                SUM(cost_micros) / 1000000.0                                                     AS cost,
                SUM(conversions_value)                                                            AS revenue,
                SUM(conversions_value) / NULLIF(SUM(cost_micros) / 1000000.0, 0)                 AS roas,
                SUM(conversions)                                                                  AS conversions,
                (SUM(cost_micros) / 1000000.0) / NULLIF(SUM(conversions), 0)                     AS cpa,
                SUM(clicks) * 1.0 / NULLIF(SUM(conversions), 0)                                  AS cvr,
                SUM(impressions)                                                                  AS impressions,
                SUM(clicks)                                                                       AS clicks,
                (SUM(cost_micros) / 1000000.0) / NULLIF(SUM(clicks), 0)                          AS cpc,
                SUM(clicks) * 1.0 / NULLIF(SUM(impressions), 0)                                  AS ctr,
                AVG(search_impression_share)                                                      AS search_is,
                AVG(search_top_impression_share)                                                  AS search_top_is,
                AVG(search_absolute_top_impression_share)                                         AS search_abs_top_is,
                AVG(click_share)                                                                  AS click_share
            FROM ro.analytics.keyword_daily
            WHERE customer_id = ?
              {current_filter}
            GROUP BY snapshot_date
            ORDER BY snapshot_date ASC
        """, [customer_id]).fetchall()
    except Exception as e:
        print(f"[Keywords M2] Sparkline query error: {e}")
        spark_rows = []

    def _spark(col_idx, scale=1.0):
        return [float(r[col_idx]) * scale if r[col_idx] is not None else 0.0 for r in spark_rows]

    financial_cards = [
        _card_kw('Cost',          c[0],        p[0],        _spark(1),        'currency',   invert=True),
        _card_kw('Revenue',       c[1],        p[1],        _spark(2),        'currency'),
        _card_kw('ROAS',          c[2],        p[2],        _spark(3),        'ratio'),
        _card_kw('Wasted Spend',  c[14],       p[14],       _spark(1),        'currency',   invert=True),
        _card_kw('Conversions',   c[3],        p[3],        _spark(4),        'number'),
        _card_kw('Cost / Conv',   c[4],        p[4],        _spark(5),        'currency',   invert=True),
        _card_kw('Conv Rate',     pct(c[5]),   pct(p[5]),   _spark(6, 100.0), 'percentage'),
        _blank_kw('financial'),
    ]
    
    # Actions cards - Impression Share values from summary queries
    actions_cards = [
        _card_kw('Impressions',       c[6],        p[6],        _spark(7),         'number',     card_type='actions'),
        _card_kw('Clicks',            c[7],        p[7],        _spark(8),         'number',     card_type='actions'),
        _card_kw('Avg CPC',           c[8],        p[8],        _spark(9),         'currency',   card_type='actions'),
        _card_kw('Avg CTR',           pct(c[9]),   pct(p[9]),   _spark(10, 100.0), 'percentage', card_type='actions'),
        _card_kw('Search Impr Share', pct(c[10]),  pct(p[10]),  _spark(11, 100.0), 'percentage', card_type='actions'),
        _card_kw('Search Top IS',     pct(c[11]),  pct(p[11]),  _spark(12, 100.0), 'percentage', card_type='actions'),
        _card_kw('Search Abs Top IS', pct(c[12]),  pct(p[12]),  _spark(13, 100.0), 'percentage', card_type='actions'),
        _card_kw('Click Share',       pct(c[13]),  pct(p[13]),  _spark(14, 100.0), 'percentage', card_type='actions'),
    ]
    return financial_cards, actions_cards


# ==================== Chat 24 M3: Chart Data Builder ====================

def _build_kw_chart_data(conn, customer_id: str, active_days: int, date_from=None, date_to=None) -> dict:
    """
    Chart data for Keywords page. Uses ro.analytics.campaign_daily (account-level).
    Builds date filter strings from session date params.
    """
    _empty = {
        'dates': [],
        'cost':        {'values': [], 'total': None, 'change_pct': None, 'axis': 'y1'},
        'impressions': {'values': [], 'total': None, 'change_pct': None, 'axis': 'y2'},
        'clicks':      {'values': [], 'total': None, 'change_pct': None, 'axis': 'y2'},
        'avg_cpc':     {'values': [], 'total': None, 'change_pct': None, 'axis': 'y1'},
    }
    from datetime import timedelta as _td, datetime as _dt2
    if date_from and date_to:
        _df = _dt2.strptime(date_from, '%Y-%m-%d').date()
        _dt2v = _dt2.strptime(date_to, '%Y-%m-%d').date()
        _span = (_dt2v - _df).days + 1
        _prev_to = (_df - _td(days=1)).isoformat()
        _prev_from = (_df - _td(days=_span)).isoformat()
        df = f"AND snapshot_date >= '{date_from}' AND snapshot_date <= '{date_to}'"
        pf = f"AND snapshot_date >= '{_prev_from}' AND snapshot_date <= '{_prev_to}'"
    else:
        d = active_days if active_days in [7, 30, 90] else 30
        df = f"AND snapshot_date >= CURRENT_DATE - INTERVAL '{d} days'"
        pf = f"AND snapshot_date >= CURRENT_DATE - INTERVAL '{d*2} days' AND snapshot_date < CURRENT_DATE - INTERVAL '{d} days'"
    q_daily = f"""
        SELECT snapshot_date,
               SUM(cost_micros)/1000000.0 AS cost,
               SUM(impressions) AS impressions,
               SUM(clicks) AS clicks,
               (SUM(cost_micros)/1000000.0)/NULLIF(SUM(clicks),0) AS avg_cpc
        FROM ro.analytics.campaign_daily
        WHERE customer_id = ? {df}
        GROUP BY snapshot_date ORDER BY snapshot_date ASC
    """
    q_cur = f"SELECT SUM(cost_micros)/1000000.0, SUM(impressions), SUM(clicks) FROM ro.analytics.campaign_daily WHERE customer_id = ? {df}"
    q_prv = f"SELECT SUM(cost_micros)/1000000.0, SUM(impressions), SUM(clicks) FROM ro.analytics.campaign_daily WHERE customer_id = ? {pf}"
    try:
        rows = conn.execute(q_daily, [customer_id]).fetchall()
        cur  = conn.execute(q_cur,   [customer_id]).fetchone()
        prv  = conn.execute(q_prv,   [customer_id]).fetchone()
    except Exception as e:
        print(f"[Keywords M3] chart data error: {e}")
        return _empty
    def _f(r, i): return float(r[i]) if r and r[i] is not None else None
    def _chg(c, p): return ((c-p)/p*100) if c is not None and p else None
    c_cost=_f(cur,0); c_impr=_f(cur,1); c_clicks=_f(cur,2)
    p_cost=_f(prv,0); p_impr=_f(prv,1); p_clicks=_f(prv,2)
    c_cpc=(c_cost/c_clicks) if c_cost and c_clicks else None
    p_cpc=(p_cost/p_clicks) if p_cost and p_clicks else None
    return {
        'dates': [str(r[0]) for r in rows],
        'cost':        {'values':[float(r[1] or 0) for r in rows],'total':c_cost,  'change_pct':_chg(c_cost,  p_cost),  'axis':'y1'},
        'impressions': {'values':[float(r[2] or 0) for r in rows],'total':c_impr,  'change_pct':_chg(c_impr,  p_impr),  'axis':'y2'},
        'clicks':      {'values':[float(r[3] or 0) for r in rows],'total':c_clicks,'change_pct':_chg(c_clicks,p_clicks),'axis':'y2'},
        'avg_cpc':     {'values':[float(r[4] or 0) for r in rows],'total':c_cpc,   'change_pct':_chg(c_cpc,   p_cpc),   'axis':'y1'},
    }




# ============================================================================
# CHAT 30B: POST ROUTES FOR LIVE EXECUTION
# ============================================================================

@bp.route('/keywords/add-negative', methods=['POST'])
@login_required
def add_negative_keywords_route():
    """
    Execute negative keyword additions (campaign or ad-group level).
    
    Request JSON:
    {
        "search_terms": [
            {
                "search_term": "text",
                "campaign_id": "123",
                "ad_group_id": "456",
                "ad_group_name": "Ad Group Name",
                "match_type": "EXACT",
                "flag_reason": "..."
            },
            ...
        ],
        "level": "campaign" | "adgroup",
        "dry_run": true | false
    }
    
    Returns:
        JSON with success counts and any failures
    """
    try:
        data = request.get_json()
        search_terms = data.get('search_terms', [])
        level = data.get('level', 'campaign')
        dry_run = data.get('dry_run', False)
        
        if not search_terms:
            return jsonify({'success': False, 'message': 'No search terms provided'}), 400
        
        # Get context
        config, clients, current_client_path = get_page_context()
        customer_id = config.customer_id
        config, clients, current_client_path = get_page_context()
        customer_id = config.customer_id
        
        # DRY-RUN CHECK FIRST - if dry-run, skip Google Ads client loading
        if dry_run:
            # Validate inputs only
            successes = [term.get('search_term', '') for term in search_terms]
            return jsonify({
                'success': True,
                'message': f'Dry-run successful: Would add {len(successes)} negative keyword(s) at {level} level',
                'added': len(successes),
                'failed': 0,
                'failures': []
            }), 200
        
        # Load Google Ads client (only for live execution)
        from pathlib import Path
        project_root = Path(__file__).parent.parent.parent
        google_ads_config_path = project_root / 'google-ads.yaml'
        
        if not google_ads_config_path.exists():
            google_ads_config_path = project_root / 'configs' / 'google-ads.yaml'
        
        if not google_ads_config_path.exists():
            google_ads_config_path = project_root / 'secrets' / 'google-ads.yaml'
        
        if not google_ads_config_path.exists():
            return jsonify({
                'success': False,
                'message': 'Google Ads configuration file not found. Checked: project root, configs/, secrets/'
            }), 500
        
        client = load_google_ads_client(str(google_ads_config_path))
        
        
        # Track results
        successes = []
        failures = []
        
        # Sequential execution
        for item in search_terms:
            search_term = item.get('search_term', '')
            campaign_id = str(item.get('campaign_id', ''))
            ad_group_id = str(item.get('ad_group_id', ''))
            match_type = item.get('match_type', 'EXACT').upper()
            
            try:
                if level == 'adgroup':
                    # Ad-group-level negative
                    result = add_adgroup_negative_keyword(
                        client=client,
                        customer_id=customer_id,
                        ad_group_id=ad_group_id,
                        keyword_text=search_term,
                        match_type=match_type,
                        dry_run=dry_run
                    )
                else:
                    # Campaign-level negative (default)
                    result = add_negative_keyword(
                        client=client,
                        customer_id=customer_id,
                        campaign_id=campaign_id,
                        keyword_text=search_term,
                        match_type=match_type,
                        dry_run=dry_run
                    )
                
                if result.get('status') in ['success', 'dry_run']:
                    successes.append(search_term)
                    
                    # Log to changes table (only if not dry-run)
                    if not dry_run:
                        conn = get_db_connection(config)
                        conn.execute("""
                            INSERT INTO changes (
                                campaign_id, rule_id, executed_by, change_type,
                                entity_type, entity_id, old_value, new_value, reason,
                                executed_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, [
                            int(campaign_id) if campaign_id else None,
                            'SEARCH_TERMS_NEGATIVE',
                            'user_search_terms_negative',
                            'negative_keyword_add',
                            'keyword',
                            ad_group_id if level == 'adgroup' else campaign_id,
                            None,
                            json.dumps({
                                'search_term': search_term,
                                'match_type': match_type,
                                'level': level,
                                'campaign_id': campaign_id,
                                'ad_group_id': ad_group_id
                            }),
                            item.get('flag_reason', 'Manual selection'),
                            datetime.now().isoformat()
                        ])
                        conn.close()
                else:
                    failures.append((search_term, result.get('message', 'Unknown error')))
                    
            except Exception as e:
                error_msg = str(e)
                if 'already exists' in error_msg.lower() or 'duplicate' in error_msg.lower():
                    error_msg = 'Already added as negative'
                failures.append((search_term, error_msg))
        
        # Build response
        if dry_run:
            return jsonify({
                'success': True,
                'message': f'Dry-run successful: {len(successes)} negative keywords validated (not executed)',
                'added': len(successes),
                'failed': len(failures),
                'failures': failures
            })
        elif successes and not failures:
            return jsonify({
                'success': True,
                'message': f'{len(successes)} negative keywords added successfully',
                'added': len(successes),
                'failed': 0,
                'failures': []
            })
        elif successes and failures:
            return jsonify({
                'success': True,
                'message': f'{len(successes)} added, {len(failures)} failed',
                'added': len(successes),
                'failed': len(failures),
                'failures': failures
            })
        else:
            return jsonify({
                'success': False,
                'message': f'All {len(failures)} negative keywords failed',
                'added': 0,
                'failed': len(failures),
                'failures': failures
            }), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/keywords/add-keyword', methods=['POST'])
@login_required
def add_keywords_route():
    """
    Execute keyword expansions (add search terms as keywords).
    
    Request JSON:
    {
        "keywords": [
            {
                "search_term": "text",
                "ad_group_id": "456",
                "campaign_id": "123",
                "match_type": "PHRASE",
                "bid_micros": 1500000,
                "expansion_reason": "..."
            },
            ...
        ],
        "dry_run": true | false
    }
    
    Returns:
        JSON with success counts and any failures
    """
    try:
        data = request.get_json()
        keywords = data.get('keywords', [])
        dry_run = data.get('dry_run', False)
        
        if not keywords:
            return jsonify({'success': False, 'message': 'No keywords provided'}), 400
        
        # Get context
        # Get context
        config, clients, current_client_path = get_page_context()
        customer_id = config.customer_id
        
        # DRY-RUN CHECK FIRST - if dry-run, validate and return
        if dry_run:
            # Validate inputs only
            successes = [kw.get('search_term', '') for kw in keywords]
            return jsonify({
                'success': True,
                'message': f'Dry-run successful: Would add {len(successes)} keyword(s)',
                'added': len(successes),
                'skipped': 0,
                'failed': 0,
                'failures': []
            }), 200
        
        # Load Google Ads client (only for live execution)
        from pathlib import Path
        project_root = Path(__file__).parent.parent.parent
        google_ads_config_path = project_root / 'google-ads.yaml'
        
        if not google_ads_config_path.exists():
            google_ads_config_path = project_root / 'configs' / 'google-ads.yaml'
        
        if not google_ads_config_path.exists():
            google_ads_config_path = project_root / 'secrets' / 'google-ads.yaml'
        
        if not google_ads_config_path.exists():
            return jsonify({
                'success': False,
                'message': 'Google Ads configuration file not found. Checked: project root, configs/, secrets/'
            }), 500
        
        client = load_google_ads_client(str(google_ads_config_path))
        
        
        # Track results
        successes = []
        skipped = []
        failures = []
        
        # Sequential execution with existence check
        conn = get_db_connection(config)
        
        for item in keywords:
            search_term = item.get('search_term', '')
            ad_group_id = str(item.get('ad_group_id', ''))
            campaign_id = str(item.get('campaign_id', ''))
            match_type = item.get('match_type', 'PHRASE').upper()
            bid_micros = int(item.get('bid_micros', 100000))  # Default £0.10
            
            # Check if keyword already exists (skip if so)
            if check_keyword_exists(conn, customer_id, ad_group_id, search_term):
                skipped.append(search_term)
                continue
            
            try:
                result = add_keyword_to_adgroup(
                    client=client,
                    customer_id=customer_id,
                    ad_group_id=ad_group_id,
                    keyword_text=search_term,
                    match_type=match_type,
                    bid_micros=bid_micros,
                    dry_run=dry_run
                )
                
                if result.get('status') in ['success', 'dry_run']:
                    successes.append(search_term)
                    
                    # Log to changes table (only if not dry-run)
                    if not dry_run:
                        conn.execute("""
                            INSERT INTO changes (
                                campaign_id, rule_id, executed_by, change_type,
                                entity_type, entity_id, old_value, new_value, reason,
                                executed_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, [
                            int(campaign_id) if campaign_id else None,
                            'SEARCH_TERMS_EXPANSION',
                            'user_search_terms_expansion',
                            'keyword_add',
                            'keyword',
                            ad_group_id,
                            None,
                            json.dumps({
                                'search_term': search_term,
                                'match_type': match_type,
                                'bid_micros': bid_micros,
                                'ad_group_id': ad_group_id,
                                'campaign_id': campaign_id
                            }),
                            item.get('expansion_reason', 'Manual selection'),
                            datetime.now().isoformat()
                        ])
                else:
                    failures.append((search_term, result.get('message', 'Unknown error')))
                    
            except Exception as e:
                error_msg = str(e)
                if 'already exists' in error_msg.lower() or 'duplicate' in error_msg.lower():
                    skipped.append(search_term)
                else:
                    failures.append((search_term, error_msg))
        
        conn.close()
        
        # Build response
        if dry_run:
            return jsonify({
                'success': True,
                'message': f'Dry-run successful: {len(successes)} keywords validated (not executed)',
                'added': len(successes),
                'skipped': len(skipped),
                'failed': len(failures),
                'failures': failures
            })
        elif successes and not failures:
            msg = f'{len(successes)} keywords added successfully'
            if skipped:
                msg += f' ({len(skipped)} already existed, skipped)'
            return jsonify({
                'success': True,
                'message': msg,
                'added': len(successes),
                'skipped': len(skipped),
                'failed': 0,
                'failures': []
            })
        elif successes and failures:
            return jsonify({
                'success': True,
                'message': f'{len(successes)} added, {len(skipped)} skipped, {len(failures)} failed',
                'added': len(successes),
                'skipped': len(skipped),
                'failed': len(failures),
                'failures': failures
            })
        else:
            return jsonify({
                'success': False,
                'message': f'All keywords failed or skipped ({len(skipped)} existed)',
                'added': 0,
                'skipped': len(skipped),
                'failed': len(failures),
                'failures': failures
            }), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


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
    sort_by  = request.args.get('sort_by',  'cost',  type=str)
    sort_dir = request.args.get('sort_dir', 'desc',  type=str)

    # Validate parameters
    if page < 1:
        page = 1
    if per_page not in [10, 25, 50, 100]:
        per_page = 25
    if match_type not in ['all', 'exact', 'phrase', 'broad']:
        match_type = 'all'

    ALLOWED_KW_SORT = {
        'keyword_text', 'campaign_name', 'ad_group_name', 'status',
        'cost', 'conversions_value', 'conversions', 'conv_value_per_cost',
        'cpa', 'conv_rate',
        'impressions', 'clicks', 'avg_cpc', 'ctr',
        'quality_score', 'expected_ctr_score', 'ad_relevance_score',
    }
    if sort_by not in ALLOWED_KW_SORT:
        sort_by = 'cost'
    if sort_dir not in ['asc', 'desc']:
        sort_dir = 'desc'
    
    # Search Terms tab filter params
    st_page = request.args.get('st_page', default=1, type=int)
    st_per_page = request.args.get('st_per_page', default=25, type=int)
    st_campaign = request.args.get('st_campaign', default='all', type=str)
    st_status = request.args.get('st_status', default='all', type=str)
    st_match_type = request.args.get('st_match_type', default='all', type=str).lower()
    
    # Validate search term params
    if st_page < 1:
        st_page = 1
    if st_per_page not in [10, 25, 50, 100]:
        st_per_page = 25
    if st_status not in ['all', 'added', 'excluded', 'none']:
        st_status = 'all'
    if st_match_type not in ['all', 'exact', 'phrase', 'broad']:
        st_match_type = 'all'
    
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
    
    # QUERY 3: Keywords Table (with pagination, match type filter, and sort)
    keywords_query = f"""
        SELECT
            keyword_id,
            keyword_text,
            match_type,
            campaign_name,
            ad_group_name,
            status,
            cost_micros_{window_suffix}_sum / 1000000.0                         AS cost,
            conversion_value_{window_suffix}_sum                                 AS conversions_value,
            conversions_{window_suffix}_sum                                      AS conversions,
            CASE WHEN cost_micros_{window_suffix}_sum > 0
                 THEN conversion_value_{window_suffix}_sum
                      / (cost_micros_{window_suffix}_sum / 1000000.0)
                 ELSE NULL END                                                   AS conv_value_per_cost,
            cpa_{window_suffix} / 1000000.0                                     AS cpa,
            CASE WHEN clicks_{window_suffix}_sum > 0
                 THEN conversions_{window_suffix}_sum * 1.0 / clicks_{window_suffix}_sum
                 ELSE NULL END                                                   AS conv_rate,
            impressions_{window_suffix}_sum                                      AS impressions,
            clicks_{window_suffix}_sum                                           AS clicks,
            CASE WHEN clicks_{window_suffix}_sum > 0
                 THEN (cost_micros_{window_suffix}_sum / 1000000.0)
                      / clicks_{window_suffix}_sum
                 ELSE NULL END                                                   AS avg_cpc,
            CASE WHEN impressions_{window_suffix}_sum > 0
                 THEN clicks_{window_suffix}_sum * 1.0 / impressions_{window_suffix}_sum
                 ELSE NULL END                                                   AS ctr,
            quality_score,
            quality_score_creative                                               AS expected_ctr_score,
            quality_score_relevance                                              AS ad_relevance_score
        FROM analytics.keyword_features_daily
        WHERE customer_id = ?
          AND snapshot_date = ?
    """
    keywords_params = [config.customer_id, snapshot_date]

    if match_type != 'all':
        keywords_query += " AND UPPER(match_type) = ?"
        keywords_params.append(match_type.upper())

    keywords_query += f"""
        ORDER BY {sort_by} {sort_dir} NULLS LAST
        LIMIT ? OFFSET ?
    """
    keywords_params.extend([per_page, offset])

    try:
        kw_rows = conn.execute(keywords_query, keywords_params).fetchall()
        kw_cols = [d[0] for d in conn.description]
        keywords = []
        for row in kw_rows:
            d = dict(zip(kw_cols, row))
            d['keyword_id']       = str(d.get('keyword_id', ''))
            d['keyword_text']     = str(d.get('keyword_text', ''))
            d['match_type']       = str(d.get('match_type', ''))
            d['status']           = str(d.get('status', ''))
            d['campaign_name']    = str(d.get('campaign_name', ''))
            d['ad_group_name']    = str(d.get('ad_group_name', ''))
            for f in ['cost', 'conversions_value', 'conversions', 'conv_value_per_cost',
                      'cpa', 'conv_rate',
                      'impressions', 'clicks', 'avg_cpc', 'ctr',
                      'quality_score', 'expected_ctr_score', 'ad_relevance_score']:
                val = d.get(f)
                d[f] = float(val) if val is not None else None
            keywords.append(d)
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
    
    # Get campaigns list for search terms filter dropdown
    try:
        campaigns_rows = conn.execute("""
            SELECT DISTINCT campaign_id, campaign_name
            FROM ro.analytics.search_term_daily
            WHERE customer_id = ?
            ORDER BY campaign_name
        """, [config.customer_id]).fetchall()
        st_campaigns = [(row[0], row[1]) for row in campaigns_rows]
    except Exception as e:
        print(f"[Keywords] Campaigns list query error: {e}")
        st_campaigns = []
    
    # QUERY 6: Search Terms with filters, pagination, and negative keyword flagging
    try:
        st_result = load_search_terms(
            conn, 
            config.customer_id,
            date_from if date_from else snapshot_date - timedelta(days=29),
            date_to if date_to else snapshot_date,
            campaign_id=st_campaign,
            status=st_status,
            match_type=st_match_type,
            page=st_page,
            per_page=st_per_page
        )
        search_terms_data = st_result['data']
        search_terms_total = st_result['total_count']
        st_page = st_result['page']
        st_per_page = st_result['per_page']
        
        # Flag negative keyword opportunities
        search_terms_data = flag_negative_keywords(search_terms_data)
        # Flag negative keyword opportunities AND expansion opportunities
        search_terms_data = flag_negative_keywords(search_terms_data)
        search_terms_data = flag_expansion_opportunities(conn, config.customer_id, search_terms_data)
    except Exception as e:
        print(f"[Keywords] Search terms query error: {e}")
        import traceback
        traceback.print_exc()
        search_terms_data = []
        search_terms_total = 0
    
    # Calculate search terms pagination
    st_total_pages = max(1, (search_terms_total + st_per_page - 1) // st_per_page)
    
    # M2: Metrics cards
    financial_cards, actions_cards = load_keyword_metrics_cards(
        conn, config.customer_id, window_suffix, snapshot_date, active_days, date_from, date_to
    )

    # M3: Chart data (Module 3: uses centralized get_performance_data)
    # Calculate actual start/end dates for get_performance_data
    if date_from and date_to:
        chart_start_date = date_from
        chart_end_date = date_to
    else:
        # Preset mode (7d, 30d, 90d) - calculate dates
        end_dt = datetime.now().date()
        start_dt = end_dt - timedelta(days=active_days)
        chart_start_date = start_dt.isoformat()
        chart_end_date = end_dt.isoformat()
    
    chart_data = get_performance_data(
        conn=conn,
        customer_id=config.customer_id,
        start_date=chart_start_date,
        end_date=chart_end_date,
        entity_type='keyword'
    )

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
        sort_by=sort_by,
        sort_dir=sort_dir,
        total_pages=total_pages,
        # Data
        snapshot_date=str(snapshot_date),
        metrics=metrics,
        keywords=keywords,
        total_keywords=total_count,
        qs_distribution=qs_distribution,
        low_data_count=low_data_count,
        wasted_spend=wasted_spend,
        # Search Terms data
        search_terms=search_terms_data,
        search_terms_total=search_terms_total,
        st_page=st_page,
        st_per_page=st_per_page,
        st_total_pages=st_total_pages,
        st_campaign=st_campaign,
        st_status=st_status,
        st_match_type=st_match_type,
        st_campaigns=st_campaigns,
        # M5 Rules
        rules=get_rules_for_page('keyword', config.customer_id),
        rule_counts=count_rules_by_category(get_rules_for_page('keyword', config.customer_id)),
        rules_config=load_rules(),
        # M2: Metrics cards
        financial_cards=financial_cards,
        actions_cards=actions_cards,
        metrics_collapsed=get_metrics_collapsed('keywords'),
        # M3: Chart
        chart_data=chart_data,
        active_metrics=get_chart_metrics('keywords'),
    )
