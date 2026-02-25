"""
Ad Groups page route - ad group performance and optimization.

Chat 21e: New ad groups page with Bootstrap 5 and rule visibility.
M4: SQL-side sort, filter, pagination. Full 26-column spec per wireframe.
Chat 41: M5 Rules tab rollout - using campaigns.py pattern (get_rules_for_page + count_rules_by_category)
"""

from flask import Blueprint, render_template, request
from act_dashboard.auth import login_required
from act_dashboard.routes.shared import get_page_context, get_db_connection, get_date_range_from_session, get_metrics_collapsed, get_chart_metrics
from act_dashboard.routes.rule_helpers import get_rules_for_page, count_rules_by_category
from act_dashboard.routes.rules_api import load_rules
from datetime import date, timedelta
from typing import List, Dict, Any, Tuple, Optional
import duckdb

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

def load_ad_group_metrics_cards(conn, customer_id: str, date_filter: str, prev_filter: str):
    """
    Build financial_cards and actions_cards for M2 metrics_section macro on Ad Groups page.
    Uses ro.analytics.ad_group_daily (account-level totals).
    Includes sparklines and change indicators.
    """
    _empty_fin = [
        {'label':'Cost',         'value':'£0',     'change_pct':None,'sparkline':[],'card_type':'financial'},
        {'label':'Revenue',      'value':'£0',     'change_pct':None,'sparkline':[],'card_type':'financial'},
        {'label':'ROAS',         'value':'0.00',   'change_pct':None,'sparkline':[],'card_type':'financial'},
        {'label':'Wasted Spend', 'value':'£0',     'change_pct':None,'sparkline':[],'card_type':'financial'},
        {'label':'Conv.',        'value':'0',      'change_pct':None,'sparkline':[],'card_type':'financial'},
        {'label':'CPA',          'value':'£0',     'change_pct':None,'sparkline':[],'card_type':'financial'},
        {'label':'CVR',          'value':'0.00%',  'change_pct':None,'sparkline':[],'card_type':'financial'},
        {'label':'',             'value':'',       'change_pct':None,'sparkline':[],'card_type':'financial'},
    ]
    _empty_act = [
        {'label':'Impr.',              'value':'0',     'change_pct':None,'sparkline':[],'card_type':'actions'},
        {'label':'Clicks',             'value':'0',     'change_pct':None,'sparkline':[],'card_type':'actions'},
        {'label':'CPC',                'value':'£0',    'change_pct':None,'sparkline':[],'card_type':'actions'},
        {'label':'CTR',                'value':'0.00%', 'change_pct':None,'sparkline':[],'card_type':'actions'},
        {'label':'Search IS',          'value':'—',     'change_pct':None,'sparkline':[],'card_type':'actions'},
        {'label':'Top IS',             'value':'—',     'change_pct':None,'sparkline':[],'card_type':'actions'},
        {'label':'Abs Top IS',         'value':'—',     'change_pct':None,'sparkline':[],'card_type':'actions'},
        {'label':'Click Share',        'value':'—',     'change_pct':None,'sparkline':[],'card_type':'actions'},
    ]
    q_cur = f"""
        SELECT
            SUM(cost_micros)/1000000.0,
            SUM(conversions_value),
            SUM(conversions),
            SUM(impressions),
            SUM(clicks),
            AVG(search_impression_share),
            AVG(search_top_impression_share),
            AVG(search_absolute_top_impression_share),
            AVG(click_share)
        FROM ro.analytics.ad_group_daily
        WHERE customer_id = ? {date_filter}
    """
    q_prv = q_cur.replace(date_filter, prev_filter)
    q_sparkline = f"""
        SELECT snapshot_date,
               SUM(cost_micros)/1000000.0               AS cost,
               SUM(conversions_value)                   AS conv_value,
               SUM(conversions)                         AS conv,
               SUM(impressions)                         AS impr,
               SUM(clicks)                              AS clicks,
               AVG(search_impression_share)             AS search_is,
               AVG(search_top_impression_share)         AS top_is,
               AVG(search_absolute_top_impression_share) AS abs_top_is,
               AVG(click_share)                         AS click_sh,
               (SUM(cost_micros)/1000000.0)/NULLIF(SUM(clicks),0)        AS avg_cpc,
               SUM(clicks)::DOUBLE/NULLIF(SUM(impressions),0)           AS ctr,
               SUM(conversions)::DOUBLE/NULLIF(SUM(clicks),0)*100       AS cvr
        FROM ro.analytics.ad_group_daily
        WHERE customer_id = ? {date_filter}
        GROUP BY snapshot_date ORDER BY snapshot_date ASC
    """
    try:
        c=conn.execute(q_cur,[customer_id]).fetchone()
        p=conn.execute(q_prv,[customer_id]).fetchone()
        sp_rows=conn.execute(q_sparkline,[customer_id]).fetchall()
    except Exception as e:
        print(f"[AdGroups M2] error: {e}")
        return _empty_fin, _empty_act
    def _f(r,i): return float(r[i]) if r and r[i] is not None else None
    def _chg(cur,prv): return ((cur-prv)/prv*100) if cur is not None and prv else None
    def pct(v): return f"{v*100:.1f}%" if v is not None else "—"
    def _spark(col_idx,scale=1.0):
        return [float((r[col_idx] or 0)*scale) for r in sp_rows]
    c_cost=_f(c,0); c_revenue=_f(c,1); c_conv=_f(c,2); c_impr=_f(c,3); c_clicks=_f(c,4)
    c_is=_f(c,5); c_top_is=_f(c,6); c_abs_top_is=_f(c,7); c_click_sh=_f(c,8)
    p_cost=_f(p,0); p_revenue=_f(p,1); p_conv=_f(p,2); p_impr=_f(p,3); p_clicks=_f(p,4)
    p_is=_f(p,5); p_top_is=_f(p,6); p_abs_top_is=_f(p,7); p_click_sh=_f(p,8)
    c_roas=(c_revenue/c_cost) if c_cost else None
    p_roas=(p_revenue/p_cost) if p_cost else None
    c_cpa=(c_cost/c_conv) if c_conv else None
    p_cpa=(p_cost/p_conv) if p_conv else None
    c_cvr=(c_conv/c_clicks) if c_clicks else None
    p_cvr=(p_conv/p_clicks) if p_clicks else None
    c_cpc=(c_cost/c_clicks) if c_clicks else None
    p_cpc=(p_cost/p_clicks) if p_clicks else None
    c_ctr=(c_clicks/c_impr) if c_impr else None
    p_ctr=(p_clicks/p_impr) if p_impr else None
    wasted=0.0
    def _card_ag(label,value,change,spark,val_type='currency',card_type='financial'):
        return {'label':label,'value':value,'change_pct':change,'sparkline':spark,'value_type':val_type,'card_type':card_type}
    financial_cards=[
        _card_ag('Cost',         f"£{c_cost:,.0f}" if c_cost else '£0',     _chg(c_cost,p_cost),     _spark(1), 'currency'),
        _card_ag('Revenue',      f"£{c_revenue:,.0f}" if c_revenue else '£0', _chg(c_revenue,p_revenue), _spark(2), 'currency'),
        _card_ag('ROAS',         f"{c_roas:.2f}" if c_roas else '0.00',     _chg(c_roas,p_roas),     _spark(1), 'ratio'),
        _card_ag('Wasted Spend', f"£{wasted:,.0f}",                          None,                    [],        'currency'),
        _card_ag('Conv.',        f"{c_conv:,.0f}" if c_conv else '0',       _chg(c_conv,p_conv),     _spark(3), 'number'),
        _card_ag('CPA',          f"£{c_cpa:,.2f}" if c_cpa else '£0',       _chg(c_cpa,p_cpa),       _spark(10),'currency'),
        _card_ag('CVR',          f"{c_cvr*100:.2f}%" if c_cvr else '0.00%', _chg(c_cvr,p_cvr),       _spark(12),'percentage'),
        _card_ag('',             '',                                         None,                    [],        'currency'),
    ]
    actions_cards=[
        _card_ag('Impr.',        f"{c_impr:,.0f}" if c_impr else '0',       _chg(c_impr,p_impr),     _spark(4), 'number', card_type='actions'),
        _card_ag('Clicks',       f"{c_clicks:,.0f}" if c_clicks else '0',   _chg(c_clicks,p_clicks), _spark(5), 'number', card_type='actions'),
        _card_ag('CPC',          f"£{c_cpc:.2f}" if c_cpc else '£0',        _chg(c_cpc,p_cpc),       _spark(10),'currency',card_type='actions'),
        _card_ag('CTR',          f"{c_ctr*100:.2f}%" if c_ctr else '0.00%', _chg(c_ctr,p_ctr),       _spark(11,100.0),'percentage',card_type='actions'),
        _card_ag('Search Impr Share', pct(c_is),     _chg(c_is,p_is),       _spark(6,100.0), 'percentage', card_type='actions'),
        _card_ag('Search Top IS',     pct(c_top_is), _chg(c_top_is,p_top_is), _spark(7,100.0), 'percentage', card_type='actions'),
        _card_ag('Search Abs Top IS', pct(c_abs_top_is), _chg(c_abs_top_is,p_abs_top_is), _spark(8,100.0), 'percentage', card_type='actions'),
        _card_ag('Click Share',       pct(c_click_sh),   _chg(c_click_sh,p_click_sh),     _spark(9,100.0), 'percentage', card_type='actions'),
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
        conn, config.customer_id, _date_filter, _prev_filter
    )

    # M3: Chart data
    chart_data = _build_ag_chart_data(conn, config.customer_id, _date_filter, _prev_filter)

    conn.close()

    # M5: Rules tab - use campaigns.py pattern
    rules = get_rules_for_page('ad_group', config.customer_id)
    rule_counts = count_rules_by_category(rules)
    rules_config = load_rules()

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
    )
