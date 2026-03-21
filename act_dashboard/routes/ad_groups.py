"""
Ad Groups page route - ad group performance and optimization.

Chat 21e: New ad groups page with Bootstrap 5 and rule visibility.
M4: SQL-side sort, filter, pagination. Full 26-column spec per wireframe.
Chat 41: M5 Rules tab rollout - using campaigns.py pattern (get_rules_for_page + count_rules_by_category)
"""

from flask import Blueprint, render_template, request, session, jsonify
from act_dashboard.auth import login_required
from act_dashboard.routes.shared import get_page_context, get_db_connection, get_date_range_from_session, get_metrics_collapsed, get_chart_metrics, get_performance_data
from act_dashboard.routes.rule_helpers import get_rules_for_page, count_rules_by_category
from act_dashboard.routes.rules_api import load_rules
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path as _Path
import duckdb
import json as _json

bp = Blueprint('ad_groups', __name__)


# Whitelisted sort columns
ALLOWED_SORT_COLS = {
    'ad_group_name', 'campaign_name', 'target_cpa',
    'cost', 'conversions_value', 'conversions',
    'conv_value_per_cost', 'cost_per_conv', 'conv_rate',
    'all_conversions', 'cost_per_all_conv', 'all_conv_rate',
    'all_conversions_value', 'all_conv_value_per_cost',
    'impressions', 'clicks', 'avg_cpc', 'ctr',
    'search_impression_share', 'search_top_impression_share',
    'search_absolute_top_impression_share', 'click_share',
    'optimization_score',
}


def load_ad_groups_m4(
    conn: duckdb.DuckDBPyConnection,
    customer_id: str,
    date_from: Optional[str],
    date_to: Optional[str],
    active_days: int,
    sort_by: str = 'cost',
    sort_dir: str = 'desc',
    page: int = 1,
    per_page: int = 25,
    status: str = 'all',
) -> Tuple[List[Dict[str, Any]], int, int]:
    """M4: SQL-side sort/filter/paginate for ad groups. Returns (page, total, total_pages)."""
    if sort_by not in ALLOWED_SORT_COLS:
        sort_by = 'cost'
    sort_dir = 'asc' if sort_dir == 'asc' else 'desc'

    if date_from and date_to:
        date_filter = f"AND snapshot_date >= '{date_from}' AND snapshot_date <= '{date_to}'"
    else:
        days = active_days if active_days in [7, 30, 90] else 30
        date_filter = f"AND snapshot_date >= CURRENT_DATE - INTERVAL '{days} days'"

    if status == 'enabled':
        status_filter = "AND ad_group_status = 'ENABLED'"
    elif status == 'paused':
        status_filter = "AND ad_group_status = 'PAUSED'"
    else:
        status_filter = ""

    offset = (page - 1) * per_page

    base_query = f"""
        WITH agg AS (
            SELECT
                ad_group_id,
                ad_group_name,
                campaign_id,
                campaign_name,
                ad_group_status,
                ANY_VALUE(ad_group_type)                                             AS ad_group_type,
                ANY_VALUE(optimization_score)                                        AS optimization_score,
                ANY_VALUE(bid_strategy_type)                                         AS bid_strategy_type,
                MAX(target_cpa_micros) / 1000000.0                                  AS target_cpa,
                SUM(cost_micros) / 1000000.0                                        AS cost,
                SUM(conversions_value)                                               AS conversions_value,
                SUM(conversions)                                                     AS conversions,
                SUM(all_conversions)                                                 AS all_conversions,
                SUM(all_conversions_value)                                           AS all_conversions_value,
                SUM(impressions)                                                     AS impressions,
                SUM(clicks)                                                          AS clicks,
                CASE WHEN SUM(impressions) > 0
                     THEN SUM(clicks)::DOUBLE / SUM(impressions) ELSE NULL END       AS ctr,
                CASE WHEN SUM(clicks) > 0
                     THEN (SUM(cost_micros)/1000000.0) / SUM(clicks) ELSE NULL END  AS avg_cpc,
                CASE WHEN SUM(cost_micros) > 0
                     THEN SUM(conversions_value) / (SUM(cost_micros)/1000000.0)
                     ELSE NULL END                                                   AS conv_value_per_cost,
                CASE WHEN SUM(conversions) > 0
                     THEN (SUM(cost_micros)/1000000.0) / SUM(conversions)
                     ELSE NULL END                                                   AS cost_per_conv,
                CASE WHEN SUM(clicks) > 0
                     THEN SUM(conversions) / SUM(clicks) ELSE NULL END               AS conv_rate,
                CASE WHEN SUM(all_conversions) > 0
                     THEN (SUM(cost_micros)/1000000.0) / SUM(all_conversions)
                     ELSE NULL END                                                   AS cost_per_all_conv,
                CASE WHEN SUM(clicks) > 0
                     THEN SUM(all_conversions) / SUM(clicks) ELSE NULL END           AS all_conv_rate,
                CASE WHEN SUM(cost_micros) > 0
                     THEN SUM(all_conversions_value) / (SUM(cost_micros)/1000000.0)
                     ELSE NULL END                                                   AS all_conv_value_per_cost,
                AVG(search_impression_share)                                         AS search_impression_share,
                AVG(search_top_impression_share)                                     AS search_top_impression_share,
                AVG(search_absolute_top_impression_share)                            AS search_absolute_top_impression_share,
                AVG(click_share)                                                     AS click_share
            FROM ro.analytics.ad_group_daily
            WHERE customer_id = ?
              {date_filter}
              {status_filter}
            GROUP BY ad_group_id, ad_group_name, campaign_id, campaign_name, ad_group_status
        )
    """

    count_query = base_query + "SELECT COUNT(*) FROM agg"
    data_query  = base_query + f"""
        SELECT * FROM agg
        ORDER BY {sort_by} {sort_dir} NULLS LAST
        LIMIT {per_page} OFFSET {offset}
    """

    try:
        total_count = conn.execute(count_query, [customer_id]).fetchone()[0]
        total_pages = max(1, (total_count + per_page - 1) // per_page)
        rows = conn.execute(data_query, [customer_id]).fetchall()
        cols = [d[0] for d in conn.description]

        result = []
        for row in rows:
            d = dict(zip(cols, row))
            d['ad_group_id']     = str(d.get('ad_group_id', ''))
            d['ad_group_name']   = str(d.get('ad_group_name', 'Unknown'))
            d['campaign_id']     = str(d.get('campaign_id', ''))
            d['campaign_name']   = str(d.get('campaign_name', 'Unknown'))
            d['ad_group_status'] = str(d.get('ad_group_status', 'UNKNOWN'))
            d['ad_group_type']   = str(d.get('ad_group_type') or '—')
            d['bid_strategy_type'] = str(d.get('bid_strategy_type') or '—')
            for f in ['target_cpa', 'cost', 'conversions_value', 'conversions',
                      'all_conversions', 'all_conversions_value', 'impressions', 'clicks',
                      'ctr', 'avg_cpc', 'conv_value_per_cost', 'cost_per_conv', 'conv_rate',
                      'cost_per_all_conv', 'all_conv_rate', 'all_conv_value_per_cost',
                      'search_impression_share', 'search_top_impression_share',
                      'search_absolute_top_impression_share', 'click_share',
                      'optimization_score']:
                val = d.get(f)
                d[f] = float(val) if val is not None else None
            result.append(d)

        return result, total_count, total_pages

    except Exception as e:
        print(f"[Ad Groups M4] Error: {e}")
        import traceback; traceback.print_exc()
        return [], 0, 1




def compute_metrics_bar(ad_groups: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate aggregated metrics for metrics bar (M4: uses 'cost' not 'spend')."""
    if not ad_groups:
        return {
            'total_ad_groups': 0, 'active_count': 0, 'paused_count': 0,
            'total_clicks': 0, 'total_cost': 0.0,
            'total_conversions': 0.0, 'overall_cpa': 0.0, 'overall_ctr': 0.0,
        }
    total_clicks      = sum(ag.get('clicks') or 0 for ag in ad_groups)
    total_impressions = sum(ag.get('impressions') or 0 for ag in ad_groups)
    total_cost        = sum(ag.get('cost') or 0 for ag in ad_groups)
    total_conversions = sum(ag.get('conversions') or 0 for ag in ad_groups)
    overall_cpa = total_cost / total_conversions if total_conversions else 0
    overall_ctr = total_clicks / total_impressions if total_impressions else 0
    active_count = sum(1 for ag in ad_groups if ag.get('ad_group_status') == 'ENABLED')
    paused_count = sum(1 for ag in ad_groups if ag.get('ad_group_status') == 'PAUSED')
    return {
        'total_ad_groups': len(ad_groups),
        'active_count': active_count,
        'paused_count': paused_count,
        'total_clicks': total_clicks,
        'total_cost': total_cost,
        'total_conversions': total_conversions,
        'overall_cpa': overall_cpa,
        'overall_ctr': overall_ctr * 100,
    }


# ==================== Chat 23 M2: Metrics Cards Data Loader ====================

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


def _fmt(value, fmt):
    """Format values for display."""
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


def _card(label, value, prev, sparkline, fmt, invert=False, card_type='financial'):
    """Build a metrics card with period-over-period comparison."""
    return {
        'label': label,
        'value_display': _fmt(value, fmt),
        'change_pct': _calculate_change_pct(value, prev),
        'sparkline_data': sparkline,
        'format_type': fmt,
        'invert_colours': invert,
        'card_type': card_type,
        'sub_label': None,
    }


def _blank_card(card_type='financial'):
    """Build a blank placeholder card."""
    return {
        'label': '', 'value_display': '', 'change_pct': None,
        'sparkline_data': None, 'format_type': 'blank',
        'invert_colours': False, 'card_type': card_type, 'sub_label': None,
    }


def load_ad_group_metrics_cards(conn, customer_id: str, active_days: int, date_from=None, date_to=None):
    """
    Build financial_cards and actions_cards for Ad Groups page.
    
    Uses ro.analytics.ad_group_daily for all queries (current, previous, sparklines).
    Compares current period vs previous period for change percentages.
    
    Financial (8): Cost | Revenue | ROAS | Wasted Spend | Conv | CPA | CVR | BLANK
    Actions  (8): Impressions | Clicks | CPC | CTR | Search IS | Top IS | Abs Top IS | Click Share
    """
    # Build date filters for current and previous periods
    current_filter, prev_filter = _build_date_filters(active_days, date_from, date_to)
    
    # ── Query 1: Current period summary from ad_group_daily ──
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
                -- Wasted spend: sum cost for ad groups with 0 conversions
                SUM(CASE WHEN conversions = 0 AND cost_micros > 0
                    THEN cost_micros / 1000000.0 ELSE 0 END)                       AS wasted_spend
            FROM ro.analytics.ad_group_daily
            WHERE customer_id = ?
              {current_filter}
        """, [customer_id]).fetchone()
    except Exception as e:
        print(f"[AdGroups M2] Current period query error: {e}")
        summary = None
    
    # ── Query 2: Previous period summary from ad_group_daily ──
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
            FROM ro.analytics.ad_group_daily
            WHERE customer_id = ?
              {prev_filter}
        """, [customer_id]).fetchone()
    except Exception as e:
        print(f"[AdGroups M2] Previous period query error: {e}")
        prev_summary = None
    
    # ── Query 3: Daily sparkline data from ad_group_daily ──
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
            FROM ro.analytics.ad_group_daily
            WHERE customer_id = ?
              {current_filter}
            GROUP BY snapshot_date
            ORDER BY snapshot_date ASC
        """, [customer_id]).fetchall()
    except Exception as e:
        print(f"[AdGroups M2] Sparkline query error: {e}")
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
        _card('Cost',          c[0],        p[0],        _spark(1),        'currency',   invert=True),
        _card('Revenue',       c[1],        p[1],        _spark(2),        'currency'),
        _card('ROAS',          c[2],        p[2],        _spark(3),        'ratio'),
        _card('Wasted Spend',  c[14],       p[14],       _spark(1),        'currency',   invert=True),
        _card('Conversions',   c[3],        p[3],        _spark(4),        'number'),
        _card('Cost / Conv',   c[4],        p[4],        _spark(5),        'currency',   invert=True),
        _card('Conv Rate',     pct(c[5]),   pct(p[5]),   _spark(6, 100.0), 'percentage'),
        _blank_card('financial'),
    ]
    
    actions_cards = [
        _card('Impressions',       c[6],        p[6],        _spark(7),         'number',     card_type='actions'),
        _card('Clicks',            c[7],        p[7],        _spark(8),         'number',     card_type='actions'),
        _card('Avg CPC',           c[8],        p[8],        _spark(9),         'currency',   card_type='actions'),
        _card('Avg CTR',           pct(c[9]),   pct(p[9]),   _spark(10, 100.0), 'percentage', card_type='actions'),
        _card('Search Impr Share', pct(c[10]),  pct(p[10]),  _spark(11, 100.0), 'percentage', card_type='actions'),
        _card('Search Top IS',     pct(c[11]),  pct(p[11]),  _spark(12, 100.0), 'percentage', card_type='actions'),
        _card('Search Abs Top IS', pct(c[12]),  pct(p[12]),  _spark(13, 100.0), 'percentage', card_type='actions'),
        _card('Click Share',       pct(c[13]),  pct(p[13]),  _spark(14, 100.0), 'percentage', card_type='actions'),
    ]
    
    return financial_cards, actions_cards


# ==================== Chat 24 M3: Chart Data Builder ====================

def _build_ag_chart_data(conn, customer_id: str, date_filter: str, prev_filter: str) -> dict:
    """
    Build chart_data dict for M3 performance_chart macro on Ad Groups page.
    Uses ro.analytics.ad_group_daily (account-level totals per day).
    avg_cpc total = total_cost / total_clicks.
    """
    _empty = {
        'dates': [],
        'cost':        {'values': [], 'total': None, 'change_pct': None, 'axis': 'y1'},
        'impressions': {'values': [], 'total': None, 'change_pct': None, 'axis': 'y2'},
        'clicks':      {'values': [], 'total': None, 'change_pct': None, 'axis': 'y2'},
        'avg_cpc':     {'values': [], 'total': None, 'change_pct': None, 'axis': 'y1'},
    }
    q_daily = f"""
        SELECT snapshot_date,
               SUM(cost_micros)/1000000.0 AS cost,
               SUM(impressions)           AS impressions,
               SUM(clicks)                AS clicks,
               (SUM(cost_micros)/1000000.0)/NULLIF(SUM(clicks),0) AS avg_cpc
        FROM ro.analytics.ad_group_daily
        WHERE customer_id = ? {date_filter}
        GROUP BY snapshot_date ORDER BY snapshot_date ASC
    """
    q_cur = f"""
        SELECT SUM(cost_micros)/1000000.0, SUM(impressions), SUM(clicks)
        FROM ro.analytics.ad_group_daily
        WHERE customer_id = ? {date_filter}
    """
    q_prv = f"""
        SELECT SUM(cost_micros)/1000000.0, SUM(impressions), SUM(clicks)
        FROM ro.analytics.ad_group_daily
        WHERE customer_id = ? {prev_filter}
    """
    try:
        rows = conn.execute(q_daily, [customer_id]).fetchall()
        cur  = conn.execute(q_cur,   [customer_id]).fetchone()
        prv  = conn.execute(q_prv,   [customer_id]).fetchone()
    except Exception as e:
        print(f"[AdGroups M3] chart data error: {e}")
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


@bp.route("/ad-groups")
@login_required
def ad_groups():
    """
    Ad Groups page - ad group performance with rule visibility.
    
    URL Parameters:
        days: Date range (7/30/90, default 7)
        page: Page number (default 1)
        per_page: Items per page (10/25/50/100, default 25)
        status: Status filter ('all', 'active', 'paused', default 'all')
    """
    # Get common page context
    config, clients, current_client_path = get_page_context()
    
    # Get date range from session (default 30d).
    active_days, date_from, date_to = get_date_range_from_session()
    if active_days == 30 and date_from is None and 'days' in request.args:
        url_days = request.args.get('days', 30, type=int)
        if url_days in [7, 90]:
            active_days = url_days

    page     = request.args.get('page',     1,      type=int)
    per_page = request.args.get('per_page', 25,     type=int)
    status   = request.args.get('status',   'all',  type=str)
    sort_by  = request.args.get('sort_by',  'cost', type=str)
    sort_dir = request.args.get('sort_dir', 'desc', type=str)

    if per_page not in [10, 25, 50, 100]:
        per_page = 25
    if page < 1:
        page = 1
    if status not in ['all', 'enabled', 'paused']:
        status = 'all'
    if sort_by not in ALLOWED_SORT_COLS:
        sort_by = 'cost'
    if sort_dir not in ['asc', 'desc']:
        sort_dir = 'desc'

    # Build date filter strings for metrics cards
    if date_from and date_to:
        from datetime import timedelta as _td, datetime as _dt2
        _df = _dt2.strptime(date_from, '%Y-%m-%d').date()
        _dt2v = _dt2.strptime(date_to, '%Y-%m-%d').date()
        _span = (_dt2v - _df).days + 1
        _prev_to = (_df - _td(days=1)).isoformat()
        _prev_from = (_df - _td(days=_span)).isoformat()
        _date_filter = f"AND snapshot_date >= '{date_from}' AND snapshot_date <= '{date_to}'"
        _prev_filter = f"AND snapshot_date >= '{_prev_from}' AND snapshot_date <= '{_prev_to}'"
    else:
        _d = active_days
        _date_filter = f"AND snapshot_date >= CURRENT_DATE - INTERVAL '{_d} days'"
        _prev_filter = f"AND snapshot_date >= CURRENT_DATE - INTERVAL '{_d * 2} days' AND snapshot_date < CURRENT_DATE - INTERVAL '{_d} days'"

    # Get database connection
    conn = get_db_connection(config)

    # M4: SQL-side sort/filter/paginate
    ad_groups_paginated, total_ad_groups, total_pages = load_ad_groups_m4(
        conn, config.customer_id, date_from, date_to, active_days,
        sort_by=sort_by, sort_dir=sort_dir, page=page, per_page=per_page, status=status,
    )

    # Metrics bar
    metrics = compute_metrics_bar(ad_groups_paginated)

    # M2: Metrics cards
    financial_cards, actions_cards = load_ad_group_metrics_cards(
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
        entity_type='ad_group'
    )

    conn.close()

    # M5: Rules tab - use campaigns.py pattern
    rules = get_rules_for_page('ad_group', config.customer_id)
    rule_counts = count_rules_by_category(rules)
    rules_config = load_rules()

    # Chat 107: pre-sanitised ad group list for the flow builder (id + name only)
    rfb_ad_groups = [
        {
            'id':   str(ag.get('ad_group_id', '') or ''),
            'name': str(ag.get('ad_group_name', '') or ''),
        }
        for ag in (ad_groups_paginated or [])
    ]

    return render_template(
        "ad_groups.html",
        client_name=config.client_name,
        available_clients=clients,
        current_client_config=current_client_path,
        ad_groups=ad_groups_paginated,
        total_ad_groups=total_ad_groups,
        metrics=metrics,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        days=active_days,
        active_days=active_days,
        date_from=date_from,
        date_to=date_to,
        status=status,
        sort_by=sort_by,
        sort_dir=sort_dir,
        rules=rules,
        rule_counts=rule_counts,
        rules_config=rules_config,
        financial_cards=financial_cards,
        actions_cards=actions_cards,
        metrics_collapsed=get_metrics_collapsed('ad_groups'),
        chart_data=chart_data,
        active_metrics=get_chart_metrics('ad_groups'),
        # M4: Saved column visibility
        saved_columns=session.get('ad_groups_columns', None),
        # Chat 107: ad group list for flow builder
        rfb_ad_groups=rfb_ad_groups,
    )


@bp.route("/ad-groups/save-columns", methods=['POST'])
@login_required
def save_columns():
    """
    POST /ad-groups/save-columns
    Body JSON: { visible: ["cost", "conv-value", ...] }
    Stores visible column list in session['ad_groups_columns'].
    """
    data = request.get_json(silent=True) or {}
    visible = data.get('visible', [])

    if not isinstance(visible, list):
        return jsonify({'success': False, 'error': 'visible must be a list'}), 400

    session['ad_groups_columns'] = visible
    return jsonify({'success': True, 'columns': visible})


# ══════════════════════════════════════════════════════════════════════════════
# Chat 107: Ad Group Rules & Flags CRUD routes
# Pattern: Copied from campaigns.py (Chat 91), adapted for entity_type='ad_group'
# ══════════════════════════════════════════════════════════════════════════════

_WAREHOUSE_PATH = _Path(__file__).parent.parent.parent / 'warehouse.duckdb'


def _ag_get_warehouse():
    """Open warehouse.duckdb writable."""
    return duckdb.connect(str(_WAREHOUSE_PATH))


def _ag_client_cfg_name():
    """Return the client config stem from the session path."""
    path = session.get("current_client_config")
    if not path:
        return None
    return _Path(path).stem


def _ag_serialize_rule(row, cols):
    """Convert a DB row to a JSON-serialisable dict."""
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


@bp.route("/ad_groups/rules", methods=['GET'])
@login_required
def ag_list_rules():
    """GET /ad_groups/rules — return all ad group rules + flags for client."""
    client_config = _ag_client_cfg_name()
    if not client_config:
        return jsonify({'success': False, 'error': 'No client selected'}), 400

    conn = _ag_get_warehouse()
    try:
        result = conn.execute(
            "SELECT * FROM rules WHERE client_config = ? AND entity_type = 'ad_group' ORDER BY type, id",
            [client_config]
        )
        cols = [d[0] for d in result.description]
        rows = [_ag_serialize_rule(row, cols) for row in result.fetchall()]
        return jsonify({'success': True, 'data': rows})
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()


@bp.route("/ad_groups/rules", methods=['POST'])
@login_required
def ag_create_rule():
    """POST /ad_groups/rules — insert new ad group rule/flag."""
    client_config = _ag_client_cfg_name()
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

    conn = _ag_get_warehouse()

    # Duplicate detection (includes entity_type filter)
    if not is_template:
        try:
            c1_metric = conditions[0].get('metric', '') if conditions else ''
            dup = conn.execute("""
                SELECT name FROM rules
                WHERE client_config = ?
                  AND entity_type = 'ad_group'
                  AND type = ?
                  AND action_type = ?
                  AND is_template = FALSE
                  AND json_extract_string(conditions, '$[0].metric') = ?
            """, [client_config, data.get('type'), data.get('action_type'), c1_metric]).fetchone()
            if dup:
                return jsonify({'success': False, 'error': f'A similar rule already exists: "{dup[0]}"'}), 409
        except Exception as e:
            print(f"[Chat 107] Duplicate check error: {e}")

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
            ) VALUES (
                ?, ?, 'ad_group', ?,
                ?, ?, ?,
                ?, ?,
                ?, ?,
                ?, ?, TRUE,
                ?, NOW(), NOW()
            )
        """, [
            next_id,
            client_config,
            data['name'],
            data['rule_or_flag'],
            data['type'],
            data.get('campaign_type_lock'),
            _json.dumps(entity_scope) if isinstance(entity_scope, (dict, list)) else entity_scope,
            _json.dumps(conditions),
            data.get('action_type'),
            data.get('action_magnitude'),
            data.get('cooldown_days', 7),
            data.get('risk_level'),
            is_template,
        ])
        conn.commit()

        result = conn.execute("SELECT * FROM rules WHERE id = ?", [next_id])
        cols = [d[0] for d in result.description]
        new_row = _ag_serialize_rule(result.fetchone(), cols)
        print(f"[Chat 107] Created ad_group rule id={next_id} name='{data['name']}'")
        return jsonify({'success': True, 'data': new_row})
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()


@bp.route("/ad_groups/rules/<int:rule_id>", methods=['PUT'])
@login_required
def ag_update_rule(rule_id):
    """PUT /ad_groups/rules/<rule_id> — full replace of mutable columns."""
    client_config = _ag_client_cfg_name()
    if not client_config:
        return jsonify({'success': False, 'error': 'No client selected'}), 400

    data = request.get_json(silent=True) or {}

    conn = _ag_get_warehouse()
    try:
        existing = conn.execute(
            "SELECT id FROM rules WHERE id = ? AND client_config = ?",
            [rule_id, client_config]
        ).fetchone()
        if not existing:
            return jsonify({'success': False, 'error': 'Rule not found'}), 404

        conditions = data.get('conditions', [])
        entity_scope = data.get('entity_scope', {'scope': 'all'})
        is_template = bool(data.get('is_template', False))

        conn.execute("""
            UPDATE rules SET
                name = ?,
                rule_or_flag = ?,
                type = ?,
                campaign_type_lock = ?,
                entity_scope = ?,
                conditions = ?,
                action_type = ?,
                action_magnitude = ?,
                cooldown_days = ?,
                risk_level = ?,
                is_template = ?,
                updated_at = NOW()
            WHERE id = ? AND client_config = ?
        """, [
            data.get('name'),
            data.get('rule_or_flag'),
            data.get('type'),
            data.get('campaign_type_lock'),
            _json.dumps(entity_scope) if isinstance(entity_scope, (dict, list)) else entity_scope,
            _json.dumps(conditions) if isinstance(conditions, list) else conditions,
            data.get('action_type'),
            data.get('action_magnitude'),
            data.get('cooldown_days', 7),
            data.get('risk_level'),
            is_template,
            rule_id,
            client_config,
        ])
        conn.commit()

        result = conn.execute("SELECT * FROM rules WHERE id = ?", [rule_id])
        cols = [d[0] for d in result.description]
        updated = _ag_serialize_rule(result.fetchone(), cols)
        print(f"[Chat 107] Updated ad_group rule id={rule_id}")
        return jsonify({'success': True, 'data': updated})
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()


@bp.route("/ad_groups/rules/<int:rule_id>", methods=['DELETE'])
@login_required
def ag_delete_rule(rule_id):
    """DELETE /ad_groups/rules/<rule_id> — delete by id."""
    client_config = _ag_client_cfg_name()
    if not client_config:
        return jsonify({'success': False, 'error': 'No client selected'}), 400

    conn = _ag_get_warehouse()
    try:
        existing = conn.execute(
            "SELECT id FROM rules WHERE id = ? AND client_config = ?",
            [rule_id, client_config]
        ).fetchone()
        if not existing:
            return jsonify({'success': False, 'error': 'Rule not found'}), 404

        conn.execute(
            "DELETE FROM rules WHERE id = ? AND client_config = ?",
            [rule_id, client_config]
        )
        conn.commit()
        print(f"[Chat 107] Deleted ad_group rule id={rule_id}")
        return jsonify({'success': True, 'data': {'id': rule_id}})
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()


@bp.route("/ad_groups/rules/<int:rule_id>/toggle", methods=['POST'])
@login_required
def ag_toggle_rule(rule_id):
    """POST /ad_groups/rules/<rule_id>/toggle — flip enabled boolean."""
    client_config = _ag_client_cfg_name()
    if not client_config:
        return jsonify({'success': False, 'error': 'No client selected'}), 400

    conn = _ag_get_warehouse()
    try:
        existing = conn.execute(
            "SELECT id, enabled FROM rules WHERE id = ? AND client_config = ?",
            [rule_id, client_config]
        ).fetchone()
        if not existing:
            return jsonify({'success': False, 'error': 'Rule not found'}), 404

        new_enabled = not bool(existing[1])
        conn.execute(
            "UPDATE rules SET enabled = ?, updated_at = NOW() WHERE id = ? AND client_config = ?",
            [new_enabled, rule_id, client_config]
        )
        conn.commit()
        print(f"[Chat 107] Toggled ad_group rule id={rule_id} enabled={new_enabled}")
        return jsonify({'success': True, 'data': {'id': rule_id, 'enabled': new_enabled}})
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()


@bp.route("/ad_groups/rules/<int:rule_id>/save-as-template", methods=['POST'])
@login_required
def ag_save_as_template(rule_id):
    """POST /ad_groups/rules/<rule_id>/save-as-template — duplicate as template."""
    client_config = _ag_client_cfg_name()
    if not client_config:
        return jsonify({'success': False, 'error': 'No client selected'}), 400

    conn = _ag_get_warehouse()
    try:
        result = conn.execute(
            "SELECT * FROM rules WHERE id = ? AND client_config = ?",
            [rule_id, client_config]
        )
        cols = [d[0] for d in result.description]
        orig = result.fetchone()
        if not orig:
            return jsonify({'success': False, 'error': 'Rule not found'}), 404

        orig_dict = dict(zip(cols, orig))

        orig_name = orig_dict.get('name', '')
        new_name = orig_name if orig_name.endswith(' (template)') else orig_name + ' (template)'

        next_id = conn.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM rules").fetchone()[0]

        conn.execute("""
            INSERT INTO rules (
                id, client_config, entity_type, name,
                rule_or_flag, type, campaign_type_lock,
                entity_scope, conditions,
                action_type, action_magnitude,
                cooldown_days, risk_level, enabled,
                is_template, plain_english,
                created_at, updated_at
            ) VALUES (
                ?, ?, 'ad_group', ?,
                ?, ?, ?,
                ?, ?,
                ?, ?,
                ?, ?, FALSE,
                TRUE, ?,
                NOW(), NOW()
            )
        """, [
            next_id,
            client_config,
            new_name,
            orig_dict.get('rule_or_flag'),
            orig_dict.get('type'),
            orig_dict.get('campaign_type_lock'),
            orig_dict.get('entity_scope') if isinstance(orig_dict.get('entity_scope'), str) else _json.dumps(orig_dict.get('entity_scope', {'scope': 'all'})),
            orig_dict.get('conditions') if isinstance(orig_dict.get('conditions'), str) else _json.dumps(orig_dict.get('conditions', [])),
            orig_dict.get('action_type'),
            orig_dict.get('action_magnitude'),
            orig_dict.get('cooldown_days', 7),
            orig_dict.get('risk_level'),
            orig_dict.get('plain_english'),
        ])
        conn.commit()

        result = conn.execute("SELECT * FROM rules WHERE id = ?", [next_id])
        cols = [d[0] for d in result.description]
        new_row = _ag_serialize_rule(result.fetchone(), cols)
        print(f"[Chat 107] Saved ad_group rule id={rule_id} as template id={next_id}")
        return jsonify({'success': True, 'data': new_row})
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()
