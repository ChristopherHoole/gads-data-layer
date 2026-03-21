"""
Ads page route - ad performance with Bootstrap 5 redesign.
Chat 21f: Full redesign matching campaigns/ad_groups/keywords pattern.

- Table: ro.analytics.ad_features_daily
- Date filter: latest snapshot, windowed columns (_7d/_30d/_90d)
- Status filter: Python-side post-query (column: ad_status)
- Pagination: Python-side
- Rules: get_rules_for_page('ad')
- Renders: ads_new.html
"""

from flask import Blueprint, render_template, request, session, jsonify
from act_dashboard.auth import login_required
from act_dashboard.routes.shared import (
    get_page_context,
    get_db_connection,
    get_date_range_from_session,
    get_metrics_collapsed,
    get_chart_metrics,
    get_performance_data,
)
from act_dashboard.routes.rule_helpers import get_rules_for_page, count_rules_by_category
from act_dashboard.routes.rules_api import load_rules
from typing import List, Dict, Any, Tuple
from datetime import date, datetime, timedelta
from pathlib import Path as _Path
import duckdb
import json as _json

bp = Blueprint('ads', __name__)


# ==================== Helper Functions (Chat 54) ====================

def _build_date_filters(active_days, date_from, date_to):
    """
    Build current and previous period date filters for SQL WHERE clauses.
    Returns tuple of (current_filter, prev_filter) starting with AND.
    """
    if date_from and date_to:
        from datetime import datetime, timedelta
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


ALLOWED_ADS_SORT = {
    'final_url', 'campaign_name', 'ad_group_name', 'ad_type', 'ad_strength',
    'cost', 'conversions_value', 'conversions', 'conv_value_per_cost',
    'cpa', 'conv_rate', 'all_conversions', 'all_conversions_value',
    'impressions', 'clicks', 'avg_cpc', 'ctr',
}


def load_ad_data(
    conn: duckdb.DuckDBPyConnection,
    customer_id: str,
    days: int,
    sort_by: str = 'impressions',
    sort_dir: str = 'desc',
) -> List[Dict[str, Any]]:
    """
    Load ad data from ro.analytics.ad_features_daily.
    Uses 30d windowed columns. Sort applied SQL-side.
    """
    # Always use 30d — windowed columns only
    query = f"""
        SELECT
            ad_id,
            ad_name,
            final_url,
            campaign_name,
            ad_group_name,
            ad_status,
            ad_type,
            cost_micros_30d / 1000000.0                                      AS cost,
            conversions_value_30d                                             AS conversions_value,
            conversions_30d                                                   AS conversions,
            CASE WHEN cost_micros_30d > 0
                 THEN conversions_value_30d / (cost_micros_30d / 1000000.0)
                 ELSE NULL END                                                AS conv_value_per_cost,
            cpa_30d / 1000000.0                                              AS cpa,
            cvr_30d                                                           AS conv_rate,
            NULL                                                              AS all_conversions,
            NULL                                                              AS cost_per_all_conv,
            NULL                                                              AS all_conv_rate,
            NULL                                                              AS all_conversions_value,
            NULL                                                              AS all_conv_value_per_cost,
            impressions_30d                                                   AS impressions,
            clicks_30d                                                        AS clicks,
            CASE WHEN clicks_30d > 0
                 THEN (cost_micros_30d / 1000000.0) / clicks_30d
                 ELSE NULL END                                                AS avg_cpc,
            ctr_30d                                                           AS ctr,
            ad_strength
        FROM ro.analytics.ad_features_daily
        WHERE customer_id = ?
          AND snapshot_date = (
              SELECT MAX(snapshot_date)
              FROM ro.analytics.ad_features_daily
              WHERE customer_id = ?
          )
        ORDER BY {sort_by} {sort_dir} NULLS LAST
    """

    try:
        rows = conn.execute(query, [customer_id, customer_id]).fetchall()
        cols = [d[0] for d in conn.description]

        ads = []
        for row in rows:
            d = dict(zip(cols, row))
            d['ad_id']         = str(d.get('ad_id', ''))
            d['final_url']     = str(d.get('final_url')     or '')
            d['campaign_name'] = str(d.get('campaign_name') or 'Unknown')
            d['ad_group_name'] = str(d.get('ad_group_name') or 'Unknown')
            d['status']        = str(d.get('ad_status')     or 'UNKNOWN')
            d['ad_type']       = str(d.get('ad_type')       or 'UNKNOWN')
            d['ad_strength']   = str(d.get('ad_strength')   or '')
            for f in ['cost', 'conversions_value', 'conversions', 'conv_value_per_cost',
                      'cpa', 'conv_rate', 'all_conversions', 'cost_per_all_conv',
                      'all_conv_rate', 'all_conversions_value', 'all_conv_value_per_cost',
                      'impressions', 'clicks', 'avg_cpc', 'ctr']:
                val = d.get(f)
                d[f] = float(val) if val is not None else None
            ads.append(d)

        return ads

    except Exception as e:
        print(f"[Ads] Error loading ad data: {e}")
        import traceback
        traceback.print_exc()
        return []


def apply_status_filter(ads: List[Dict[str, Any]], status: str) -> List[Dict[str, Any]]:
    """
    Apply status filter in Python after SQL query.
    Status values in ad_features_daily: ENABLED, PAUSED, REMOVED.

    Args:
        ads: Full ad list
        status: 'all', 'enabled', or 'paused'

    Returns:
        Filtered list
    """
    if status == 'enabled':
        return [a for a in ads if a['status'] == 'ENABLED']
    elif status == 'paused':
        return [a for a in ads if a['status'] == 'PAUSED']
    return ads  # 'all'


def compute_metrics(ads: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compute summary metrics for the 7 metrics cards bar.

    Args:
        ads: Full filtered ad list

    Returns:
        Dict of metric values
    """
    if not ads:
        return {
            'total_ads':           0,
            'enabled_count':       0,
            'paused_count':        0,
            'total_clicks':        0,
            'total_cost':          0.0,
            'total_conversions':   0.0,
            'overall_ctr':         0.0,
            'overall_cpa':         0.0,
            'poor_strength_count': 0,
            'good_strength_count': 0,
        }

    total_clicks      = sum(a['clicks']      for a in ads)
    total_impressions = sum(a['impressions'] for a in ads)
    total_cost        = sum(a['cost']        for a in ads)
    total_conversions = sum(a['conversions'] for a in ads)
    overall_ctr       = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0.0
    overall_cpa       = (total_cost / total_conversions)         if total_conversions  > 0 else 0.0
    enabled_count     = sum(1 for a in ads if a['status'] == 'ENABLED')
    paused_count      = sum(1 for a in ads if a['status'] == 'PAUSED')
    poor_strength     = sum(1 for a in ads if a['ad_strength'] == 'POOR')
    good_strength     = sum(1 for a in ads if a['ad_strength'] in ('GOOD', 'EXCELLENT'))

    return {
        'total_ads':           len(ads),
        'enabled_count':       enabled_count,
        'paused_count':        paused_count,
        'total_clicks':        total_clicks,
        'total_cost':          total_cost,
        'total_conversions':   total_conversions,
        'overall_ctr':         overall_ctr,
        'overall_cpa':         overall_cpa,
        'poor_strength_count': poor_strength,
        'good_strength_count': good_strength,
    }


def apply_pagination(
    ads: List[Dict[str, Any]],
    page: int,
    per_page: int
) -> Tuple[List[Dict[str, Any]], int, int]:
    """
    Slice ads list for current page.

    Args:
        ads: Full filtered list
        page: Current page (1-based)
        per_page: Items per page

    Returns:
        Tuple of (paginated_list, total_count, total_pages)
    """
    total_count = len(ads)
    total_pages = max(1, (total_count + per_page - 1) // per_page)

    if page > total_pages:
        page = total_pages

    start = (page - 1) * per_page
    end   = start + per_page

    return ads[start:end], total_count, total_pages




# ==================== Chat 23 M2: Metrics Cards ====================

def _fmt_ads(value, fmt):
    if value is None:
        return '—'
    if fmt == 'ad_strength':
        return str(value)  # pre-formatted string e.g. "24/30"
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


def _card_ads(label, value, prev, sparkline, fmt, invert=False, card_type='financial', sub_label=None):
    """Ads cards with period-over-period comparison."""
    return {
        'label': label,
        'value_display': _fmt_ads(value, fmt),
        'change_pct': _calculate_change_pct(value, prev),
        'sparkline_data': sparkline,
        'format_type': fmt,
        'invert_colours': invert,
        'card_type': card_type,
        'sub_label': sub_label,
    }


def _blank_ads(card_type='financial'):
    return {
        'label': '', 'value_display': '', 'change_pct': None,
        'sparkline_data': None, 'format_type': 'blank',
        'invert_colours': False, 'card_type': card_type, 'sub_label': None,
    }


def load_ads_metrics_cards(conn, customer_id: str, active_days: int, date_from=None, date_to=None):
    """
    Build financial_cards and actions_cards for Ads page.
    
    Uses ro.analytics.ad_daily for all queries (current, previous, sparklines).
    Compares current period vs previous period for change percentages.
    
    Financial (8): Cost | Revenue | ROAS | Wasted Spend | Conv | CPA | CVR | BLANK
    Actions  (8): Impressions | Clicks | CPC | CTR | Search IS | Top IS | Abs Top IS | Click Share
    """
    # Build date filters for current and previous periods
    current_filter, prev_filter = _build_date_filters(active_days, date_from, date_to)
    
    # ── Query 1: Current period summary from ad_daily ──
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
                -- Wasted spend: sum cost for ads with 0 conversions
                SUM(CASE WHEN conversions = 0 AND cost_micros > 0
                    THEN cost_micros / 1000000.0 ELSE 0 END)                       AS wasted_spend
            FROM ro.analytics.ad_daily
            WHERE customer_id = ?
              {current_filter}
        """, [customer_id]).fetchone()
    except Exception as e:
        print(f"[Ads M2] Current period query error: {e}")
        summary = None
    
    # ── Query 2: Previous period summary from ad_daily ──
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
            FROM ro.analytics.ad_daily
            WHERE customer_id = ?
              {prev_filter}
        """, [customer_id]).fetchone()
    except Exception as e:
        print(f"[Ads M2] Previous period query error: {e}")
        prev_summary = None
    
    # ── Query 3: Daily sparkline data from ad_daily ──
    try:
        spark_rows = conn.execute(f"""
            SELECT
                snapshot_date,
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
                AVG(click_share)                                                   AS click_share
            FROM ro.analytics.ad_daily
            WHERE customer_id = ?
              {current_filter}
            GROUP BY snapshot_date
            ORDER BY snapshot_date ASC
        """, [customer_id]).fetchall()
    except Exception as e:
        print(f"[Ads M2] Sparkline query error: {e}")
        spark_rows = []
    
    def _v(row, i): return float(row[i]) if row and row[i] is not None else None
    def pct(val): return val * 100 if val is not None else None
    
    # Current period values
    c = [_v(summary, i) for i in range(15)] if summary else [None] * 15
    
    # Previous period values
    p = [_v(prev_summary, i) for i in range(15)] if prev_summary else [None] * 15
    
    # Build sparkline arrays
    def _spark(col_idx, scale=1.0):
        return [float(r[col_idx]) * scale if r[col_idx] is not None else 0.0 for r in spark_rows]
    
    financial_cards = [
        _card_ads('Cost',          c[0],        p[0],        _spark(1),        'currency',   invert=True),
        _card_ads('Revenue',       c[1],        p[1],        _spark(2),        'currency'),
        _card_ads('ROAS',          c[2],        p[2],        _spark(3),        'ratio'),
        _card_ads('Wasted Spend',  c[14],       p[14],       _spark(1),        'currency',   invert=True),
        _card_ads('Conversions',   c[3],        p[3],        _spark(4),        'number'),
        _card_ads('Cost / Conv',   c[4],        p[4],        _spark(5),        'currency',   invert=True),
        _card_ads('Conv Rate',     pct(c[5]),   pct(p[5]),   _spark(6, 100.0), 'percentage'),
        _blank_ads('financial'),
    ]
    
    actions_cards = [
        _card_ads('Impressions',       c[6],        p[6],        _spark(7),         'number',     card_type='actions'),
        _card_ads('Clicks',            c[7],        p[7],        _spark(8),         'number',     card_type='actions'),
        _card_ads('Avg CPC',           c[8],        p[8],        _spark(9),         'currency',   card_type='actions'),
        _card_ads('Avg CTR',           pct(c[9]),   pct(p[9]),   _spark(10, 100.0), 'percentage', card_type='actions'),
        _card_ads('Search Impr Share', pct(c[10]),  pct(p[10]),  _spark(11, 100.0), 'percentage', card_type='actions'),
        _card_ads('Search Top IS',     pct(c[11]),  pct(p[11]),  _spark(12, 100.0), 'percentage', card_type='actions'),
        _card_ads('Search Abs Top IS', pct(c[12]),  pct(p[12]),  _spark(13, 100.0), 'percentage', card_type='actions'),
        _card_ads('Click Share',       pct(c[13]),  pct(p[13]),  _spark(14, 100.0), 'percentage', card_type='actions'),
    ]
    
    return financial_cards, actions_cards


# ==================== Chat 24 M3: Chart Data Builder ====================

def _build_ads_chart_data(conn, customer_id: str, active_days: int, date_from=None, date_to=None) -> dict:
    """
    Chart data for Ads page. Uses ro.analytics.campaign_daily (account-level).
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
        print(f"[Ads M3] chart data error: {e}")
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


@bp.route("/ads")
@login_required
def ads():
    """
    Ads page - Bootstrap 5 redesign (Chat 21f / M4).
    """
    active_days, date_from, date_to = get_date_range_from_session()
    if date_from and date_to:
        days = 30
        print("[Ads] Custom date range selected — using 30d windowed columns as approximation")
    elif active_days in [7, 30, 90]:
        days = active_days
    else:
        days = 30

    page     = request.args.get('page',     default=1,     type=int)
    per_page = request.args.get('per_page', default=25,    type=int)
    status   = request.args.get('status',   default='all', type=str).lower()
    sort_by  = request.args.get('sort_by',  default='impressions', type=str)
    sort_dir = request.args.get('sort_dir', default='desc', type=str)

    if per_page not in [10, 25, 50, 100]:            per_page = 25
    if page     < 1:                                 page     = 1
    if status   not in ['all', 'enabled', 'paused']: status   = 'all'
    if sort_by  not in ALLOWED_ADS_SORT:             sort_by  = 'impressions'
    if sort_dir not in ['asc', 'desc']:              sort_dir = 'desc'

    config, clients, current_client_path = get_page_context()
    conn = get_db_connection(config)

    all_ads = load_ad_data(conn, config.customer_id, days, sort_by, sort_dir)

    financial_cards, actions_cards = load_ads_metrics_cards(
        conn, config.customer_id, active_days, date_from, date_to
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
        entity_type='ad'
    )

    conn.close()

    filtered_ads = apply_status_filter(all_ads, status)
    metrics = compute_metrics(filtered_ads)
    ads_paginated, total_ads, total_pages = apply_pagination(filtered_ads, page, per_page)

    try:
        rules       = get_rules_for_page('ad', customer_id=config.customer_id)
        rule_counts = count_rules_by_category(rules)
    except Exception as e:
        print(f"[Ads] Rules load error: {e}")
        rules       = []
        rule_counts = {}

    print(f"[Ads] {len(all_ads)} ads loaded, {len(filtered_ads)} after filter, {len(rules)} rules")

    return render_template(
        'ads_new.html',
        client_name=config.client_name,
        available_clients=clients,
        current_client_config=current_client_path,
        ads=ads_paginated,
        total_ads=total_ads,
        metrics=metrics,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        days=days,
        active_days=active_days,
        date_from=date_from,
        date_to=date_to,
        status=status,
        sort_by=sort_by,
        sort_dir=sort_dir,
        rules=rules,
        rules_config=load_rules(),
        rule_counts=rule_counts,
        error=None,
        financial_cards=financial_cards,
        actions_cards=actions_cards,
        metrics_collapsed=get_metrics_collapsed('ads'),
        chart_data=chart_data,
        active_metrics=get_chart_metrics('ads'),
        # M4: Saved column visibility
        saved_columns=session.get('ads_columns', None),
        # Chat 109: ad list for flow builder
        rfb_ads=[
            {'id': str(a.get('ad_id', '') or ''), 'name': str(a.get('ad_name', '') or '')}
            for a in (ads_paginated or [])
        ],
    )


@bp.route("/ads/save-columns", methods=['POST'])
@login_required
def save_columns():
    """
    POST /ads/save-columns
    Body JSON: { visible: ["cost", "conv-value", ...] }
    Stores visible column list in session['ads_columns'].
    """
    data = request.get_json(silent=True) or {}
    visible = data.get('visible', [])

    if not isinstance(visible, list):
        return jsonify({'success': False, 'error': 'visible must be a list'}), 400

    session['ads_columns'] = visible
    return jsonify({'success': True, 'columns': visible})


# ══════════════════════════════════════════════════════════════════════════════
# Chat 109: Ad Rules & Flags CRUD routes
# ══════════════════════════════════════════════════════════════════════════════

_AD_WAREHOUSE_PATH = _Path(__file__).parent.parent.parent / 'warehouse.duckdb'


def _ad_get_warehouse():
    return duckdb.connect(str(_AD_WAREHOUSE_PATH))


def _ad_client_cfg_name():
    path = session.get("current_client_config")
    if not path:
        return None
    return _Path(path).stem


def _ad_serialize_rule(row, cols):
    d = dict(zip(cols, row))
    for field in ('conditions', 'entity_scope'):
        val = d.get(field)
        if val and isinstance(val, str):
            try:
                d[field] = _json.loads(val)
            except Exception:
                pass
    for k, v in d.items():
        if isinstance(v, datetime):
            d[k] = v.isoformat()
    return d


@bp.route("/ads/rules", methods=['GET'])
@login_required
def ad_list_rules():
    client_config = _ad_client_cfg_name()
    if not client_config:
        return jsonify({'success': False, 'error': 'No client selected'}), 400
    conn = _ad_get_warehouse()
    try:
        result = conn.execute(
            "SELECT * FROM rules WHERE client_config = ? AND entity_type = 'ad' ORDER BY type, id",
            [client_config]
        )
        cols = [d[0] for d in result.description]
        rows = [_ad_serialize_rule(row, cols) for row in result.fetchall()]
        return jsonify({'success': True, 'data': rows})
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()


@bp.route("/ads/rules", methods=['POST'])
@login_required
def ad_create_rule():
    client_config = _ad_client_cfg_name()
    if not client_config:
        return jsonify({'success': False, 'error': 'No client selected'}), 400
    data = request.get_json(silent=True) or {}
    required = ['name', 'rule_or_flag', 'type']
    for f in required:
        if not data.get(f):
            return jsonify({'success': False, 'error': f'Missing required field: {f}'}), 400
    conditions = data.get('conditions', [])
    if not isinstance(conditions, list):
        return jsonify({'success': False, 'error': 'conditions must be an array'}), 400
    entity_scope = data.get('entity_scope', {'scope': 'all'})
    is_template = bool(data.get('is_template', False))
    conn = _ad_get_warehouse()
    if not is_template:
        try:
            c1_metric = conditions[0].get('metric', '') if conditions else ''
            dup = conn.execute("""
                SELECT name FROM rules
                WHERE client_config = ? AND entity_type = 'ad'
                  AND type = ? AND action_type = ? AND is_template = FALSE
                  AND json_extract_string(conditions, '$[0].metric') = ?
            """, [client_config, data.get('type'), data.get('action_type'), c1_metric]).fetchone()
            if dup:
                return jsonify({'success': False, 'error': f'A similar rule already exists: "{dup[0]}"'}), 409
        except Exception as e:
            print(f"[Chat 109] Duplicate check error: {e}")
    try:
        next_id = conn.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM rules").fetchone()[0]
        conn.execute("""
            INSERT INTO rules (
                id, client_config, entity_type, name,
                rule_or_flag, type, campaign_type_lock,
                entity_scope, conditions,
                action_type, action_magnitude,
                cooldown_days, risk_level, enabled,
                is_template, created_at, updated_at
            ) VALUES (?, ?, 'ad', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, TRUE, ?, NOW(), NOW())
        """, [
            next_id, client_config, data['name'],
            data['rule_or_flag'], data['type'], data.get('campaign_type_lock'),
            _json.dumps(entity_scope) if isinstance(entity_scope, (dict, list)) else entity_scope,
            _json.dumps(conditions),
            data.get('action_type'), data.get('action_magnitude'),
            data.get('cooldown_days', 7), data.get('risk_level'), is_template,
        ])
        conn.commit()
        result = conn.execute("SELECT * FROM rules WHERE id = ?", [next_id])
        cols = [d[0] for d in result.description]
        return jsonify({'success': True, 'data': _ad_serialize_rule(result.fetchone(), cols)})
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()


@bp.route("/ads/rules/<int:rule_id>", methods=['PUT'])
@login_required
def ad_update_rule(rule_id):
    client_config = _ad_client_cfg_name()
    if not client_config:
        return jsonify({'success': False, 'error': 'No client selected'}), 400
    data = request.get_json(silent=True) or {}
    conn = _ad_get_warehouse()
    try:
        existing = conn.execute("SELECT id FROM rules WHERE id = ? AND client_config = ?", [rule_id, client_config]).fetchone()
        if not existing:
            return jsonify({'success': False, 'error': 'Rule not found'}), 404
        conditions = data.get('conditions', [])
        entity_scope = data.get('entity_scope', {'scope': 'all'})
        is_template = bool(data.get('is_template', False))
        conn.execute("""
            UPDATE rules SET name=?, rule_or_flag=?, type=?, campaign_type_lock=?,
                entity_scope=?, conditions=?, action_type=?, action_magnitude=?,
                cooldown_days=?, risk_level=?, is_template=?, updated_at=NOW()
            WHERE id = ? AND client_config = ?
        """, [
            data.get('name'), data.get('rule_or_flag'), data.get('type'), data.get('campaign_type_lock'),
            _json.dumps(entity_scope) if isinstance(entity_scope, (dict, list)) else entity_scope,
            _json.dumps(conditions) if isinstance(conditions, list) else conditions,
            data.get('action_type'), data.get('action_magnitude'),
            data.get('cooldown_days', 7), data.get('risk_level'), is_template, rule_id, client_config,
        ])
        conn.commit()
        result = conn.execute("SELECT * FROM rules WHERE id = ?", [rule_id])
        cols = [d[0] for d in result.description]
        return jsonify({'success': True, 'data': _ad_serialize_rule(result.fetchone(), cols)})
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()


@bp.route("/ads/rules/<int:rule_id>", methods=['DELETE'])
@login_required
def ad_delete_rule(rule_id):
    client_config = _ad_client_cfg_name()
    if not client_config:
        return jsonify({'success': False, 'error': 'No client selected'}), 400
    conn = _ad_get_warehouse()
    try:
        existing = conn.execute("SELECT id FROM rules WHERE id = ? AND client_config = ?", [rule_id, client_config]).fetchone()
        if not existing:
            return jsonify({'success': False, 'error': 'Rule not found'}), 404
        conn.execute("DELETE FROM rules WHERE id = ? AND client_config = ?", [rule_id, client_config])
        conn.commit()
        return jsonify({'success': True, 'data': {'id': rule_id}})
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()


@bp.route("/ads/rules/<int:rule_id>/toggle", methods=['POST'])
@login_required
def ad_toggle_rule(rule_id):
    client_config = _ad_client_cfg_name()
    if not client_config:
        return jsonify({'success': False, 'error': 'No client selected'}), 400
    conn = _ad_get_warehouse()
    try:
        existing = conn.execute("SELECT id, enabled FROM rules WHERE id = ? AND client_config = ?", [rule_id, client_config]).fetchone()
        if not existing:
            return jsonify({'success': False, 'error': 'Rule not found'}), 404
        new_enabled = not bool(existing[1])
        conn.execute("UPDATE rules SET enabled=?, updated_at=NOW() WHERE id=? AND client_config=?", [new_enabled, rule_id, client_config])
        conn.commit()
        return jsonify({'success': True, 'data': {'id': rule_id, 'enabled': new_enabled}})
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()


@bp.route("/ads/rules/<int:rule_id>/save-as-template", methods=['POST'])
@login_required
def ad_save_as_template(rule_id):
    client_config = _ad_client_cfg_name()
    if not client_config:
        return jsonify({'success': False, 'error': 'No client selected'}), 400
    conn = _ad_get_warehouse()
    try:
        result = conn.execute("SELECT * FROM rules WHERE id = ? AND client_config = ?", [rule_id, client_config])
        cols = [d[0] for d in result.description]
        orig = result.fetchone()
        if not orig:
            return jsonify({'success': False, 'error': 'Rule not found'}), 404
        orig_dict = dict(zip(cols, orig))
        orig_name = orig_dict.get('name', '')
        new_name = orig_name if orig_name.endswith(' (template)') else orig_name + ' (template)'
        next_id = conn.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM rules").fetchone()[0]
        conn.execute("""
            INSERT INTO rules (id, client_config, entity_type, name, rule_or_flag, type, campaign_type_lock,
                entity_scope, conditions, action_type, action_magnitude,
                cooldown_days, risk_level, enabled, is_template, plain_english, created_at, updated_at
            ) VALUES (?, ?, 'ad', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, FALSE, TRUE, ?, NOW(), NOW())
        """, [
            next_id, client_config, new_name,
            orig_dict.get('rule_or_flag'), orig_dict.get('type'), orig_dict.get('campaign_type_lock'),
            orig_dict.get('entity_scope') if isinstance(orig_dict.get('entity_scope'), str) else _json.dumps(orig_dict.get('entity_scope', {'scope': 'all'})),
            orig_dict.get('conditions') if isinstance(orig_dict.get('conditions'), str) else _json.dumps(orig_dict.get('conditions', [])),
            orig_dict.get('action_type'), orig_dict.get('action_magnitude'),
            orig_dict.get('cooldown_days', 7), orig_dict.get('risk_level'), orig_dict.get('plain_english'),
        ])
        conn.commit()
        result = conn.execute("SELECT * FROM rules WHERE id = ?", [next_id])
        cols = [d[0] for d in result.description]
        return jsonify({'success': True, 'data': _ad_serialize_rule(result.fetchone(), cols)})
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()


@bp.route("/api/ads-list", methods=['GET'])
@login_required
def ad_api_ads_list():
    client_config = _ad_client_cfg_name()
    if not client_config:
        return jsonify({'success': False, 'error': 'No client selected'}), 400
    conn = _ad_get_warehouse()
    try:
        result = conn.execute(
            "SELECT DISTINCT ad_id, ad_name FROM rules WHERE client_config = ? AND entity_type = 'ad'",
            [client_config]
        )
        return jsonify({'success': True, 'ads': []})
    except Exception:
        return jsonify({'success': True, 'ads': []})
    finally:
        conn.close()
