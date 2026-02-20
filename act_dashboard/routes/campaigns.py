"""
Campaigns page route - campaign performance and optimization.

Chat 21c: New campaigns page with Bootstrap 5 and rule visibility.
Chat 22: Session-based date range, custom date support, ro. prefix fix.
Chat 23 M2: Added metrics cards data (financial_cards, actions_cards, sparklines).
"""

from flask import Blueprint, render_template, request
from act_dashboard.auth import login_required
from act_dashboard.routes.shared import (
    get_page_context, get_db_connection, get_date_range_from_session,
    get_metrics_collapsed, get_chart_metrics,
)
from act_dashboard.routes.rule_helpers import get_rules_for_page, count_rules_by_category
from datetime import date, timedelta, datetime
from typing import List, Dict, Any, Tuple, Optional
import duckdb

bp = Blueprint('campaigns', __name__)


# ==================== Existing helpers (unchanged) ====================

def load_campaign_data(
    conn: duckdb.DuckDBPyConnection,
    customer_id: str,
    days: int = 30,
    date_from: str = None,
    date_to: str = None,
) -> List[Dict[str, Any]]:
    """
    Load campaign data from ro.analytics.campaign_daily.
    """
    if date_from and date_to:
        date_filter = f"AND snapshot_date >= '{date_from}' AND snapshot_date <= '{date_to}'"
    else:
        if days not in [7, 30, 90]:
            days = 30
        date_filter = f"AND snapshot_date >= CURRENT_DATE - INTERVAL '{days} days'"

    query = f"""
        SELECT
            campaign_id,
            campaign_name,
            campaign_status,
            channel_type,
            SUM(cost_micros) / 1000000.0 as spend,
            SUM(clicks) as clicks,
            SUM(impressions) as impressions,
            CASE WHEN SUM(impressions) > 0
                 THEN (SUM(clicks)::DOUBLE / SUM(impressions)) * 100
                 ELSE 0 END as ctr,
            SUM(conversions) as conversions,
            SUM(conversions_value) as conversion_value,
            CASE WHEN SUM(cost_micros) > 0
                 THEN SUM(conversions_value) / (SUM(cost_micros) / 1000000.0)
                 ELSE 0 END as roas,
            CASE WHEN SUM(conversions) > 0
                 THEN (SUM(cost_micros) / 1000000.0) / SUM(conversions)
                 ELSE 0 END as cpa,
            COUNT(DISTINCT snapshot_date) as days_in_period
        FROM ro.analytics.campaign_daily
        WHERE customer_id = ?
          {date_filter}
        GROUP BY campaign_id, campaign_name, campaign_status, channel_type
        ORDER BY spend DESC
    """

    try:
        rows = conn.execute(query, [customer_id]).fetchall()
        cols = [d[0] for d in conn.description]

        campaigns = []
        for row in rows:
            campaign_dict = dict(zip(cols, row))
            campaign_dict['campaign_id'] = str(campaign_dict.get('campaign_id', ''))
            campaign_dict['campaign_name'] = str(campaign_dict.get('campaign_name', 'Unknown'))
            campaign_dict['campaign_status'] = str(campaign_dict.get('campaign_status', 'UNKNOWN'))
            campaign_dict['channel_type'] = str(campaign_dict.get('channel_type', 'UNKNOWN'))
            campaign_dict['spend'] = float(campaign_dict.get('spend') or 0)
            campaign_dict['clicks'] = int(campaign_dict.get('clicks') or 0)
            campaign_dict['impressions'] = int(campaign_dict.get('impressions') or 0)
            campaign_dict['ctr'] = float(campaign_dict.get('ctr') or 0)
            campaign_dict['conversions'] = float(campaign_dict.get('conversions') or 0)
            campaign_dict['conversion_value'] = float(campaign_dict.get('conversion_value') or 0)
            campaign_dict['roas'] = float(campaign_dict.get('roas') or 0)
            campaign_dict['cpa'] = float(campaign_dict.get('cpa') or 0)
            days_in_period = int(campaign_dict.get('days_in_period') or 1)
            campaign_dict['daily_budget'] = campaign_dict['spend'] / days_in_period if days_in_period > 0 else 0
            campaigns.append(campaign_dict)

        return campaigns

    except Exception as e:
        print(f"[Campaigns] Error loading campaign data: {e}")
        import traceback
        traceback.print_exc()
        return []


def compute_metrics_bar(campaigns: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate aggregated metrics for metrics bar."""
    if not campaigns:
        return {
            'total_campaigns': 0,
            'total_spend': 0.0,
            'total_clicks': 0,
            'total_impressions': 0,
            'total_conversions': 0.0,
            'total_conversion_value': 0.0,
            'avg_ctr': 0.0,
            'overall_roas': 0.0,
            'overall_cpa': 0.0,
        }

    total_spend = sum(c['spend'] for c in campaigns)
    total_clicks = sum(c['clicks'] for c in campaigns)
    total_impressions = sum(c['impressions'] for c in campaigns)
    total_conversions = sum(c['conversions'] for c in campaigns)
    total_conversion_value = sum(c['conversion_value'] for c in campaigns)
    avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
    overall_roas = (total_conversion_value / total_spend) if total_spend > 0 else 0
    overall_cpa = (total_spend / total_conversions) if total_conversions > 0 else 0

    return {
        'total_campaigns': len(campaigns),
        'total_spend': total_spend,
        'total_clicks': total_clicks,
        'total_impressions': total_impressions,
        'total_conversions': total_conversions,
        'total_conversion_value': total_conversion_value,
        'avg_ctr': avg_ctr,
        'overall_roas': overall_roas,
        'overall_cpa': overall_cpa,
    }


def apply_pagination(
    campaigns: List[Dict[str, Any]],
    page: int,
    per_page: int
) -> Tuple[List[Dict[str, Any]], int, int]:
    """Apply pagination to campaigns list."""
    total_count = len(campaigns)
    total_pages = max(1, (total_count + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    return campaigns[start_idx:end_idx], total_count, total_pages


# ==================== Chat 23 M2: Metrics Cards Helpers ====================

def _build_date_filters(active_days: int, date_from: Optional[str], date_to: Optional[str]) -> Tuple[str, str]:
    """
    Build SQL date filter strings for current and previous period.

    Returns:
        Tuple of (current_filter, prev_filter) — both are WHERE clause fragments
        starting with AND.
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


def _calculate_change_pct(current: Optional[float], previous: Optional[float]) -> Optional[float]:
    """
    Calculate % change. Returns None (show dash) when no previous data.
    Never returns 0% to mask missing data — per A3.
    """
    if previous is None or previous == 0:
        return None
    if current is None:
        return -100.0
    return ((current - previous) / previous) * 100.0


def _fmt(value: Optional[float], fmt: str) -> str:
    """
    Format a metric value for display.

    fmt options:
      'currency'   — $1.2k / $1.2M / $0.80
      'number'     — 1,234 / 1.2k / 1.2M
      'percentage' — 42.1%
      'ratio'      — 3.13x
      'rate'       — 8.14% (same as percentage)
    """
    if value is None:
        return '—'
    v = float(value)
    if fmt == 'currency':
        if v >= 1_000_000:
            return f'${v / 1_000_000:.1f}M'
        if v >= 1_000:
            return f'${v / 1_000:.1f}k'
        return f'${v:,.2f}'
    if fmt in ('percentage', 'rate'):
        return f'{v:.1f}%'
    if fmt == 'ratio':
        return f'{v:.2f}x'
    if fmt == 'number':
        if v >= 1_000_000:
            return f'{v / 1_000_000:.2f}M'
        if v >= 1_000:
            return f'{v / 1_000:.1f}k'
        return f'{v:,.0f}'
    return str(v)


def _card(label: str, value: Optional[float], prev: Optional[float],
          sparkline: List[float], fmt: str, invert: bool = False,
          card_type: str = 'financial') -> Dict[str, Any]:
    """Build a single card dict."""
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


def _blank_card(card_type: str = 'financial') -> Dict[str, Any]:
    """Build a blank placeholder card."""
    return {
        'label': '',
        'value_display': '',
        'change_pct': None,
        'sparkline_data': None,
        'format_type': 'blank',
        'invert_colours': False,
        'card_type': card_type,
        'sub_label': None,
    }


def load_metrics_cards_data(
    conn: duckdb.DuckDBPyConnection,
    customer_id: str,
    active_days: int,
    date_from: Optional[str],
    date_to: Optional[str],
) -> Tuple[List[Dict], List[Dict]]:
    """
    Build financial_cards and actions_cards lists for the Campaigns page.

    Financial (8):  Cost | Revenue | ROAS | BLANK | Conversions | CPA | Conv Rate | BLANK
    Actions (8):    Impressions | Clicks | Avg CPC | Avg CTR |
                    Search IS | Search Top IS | Search Abs Top IS | Click Share

    Returns:
        Tuple of (financial_cards, actions_cards)
    """
    current_filter, prev_filter = _build_date_filters(active_days, date_from, date_to)

    # ── Query 1: Current period summary ──────────────────────────────────────
    q_current = f"""
        SELECT
            SUM(cost_micros) / 1000000.0                                      AS cost,
            SUM(conversions_value)                                             AS revenue,
            SUM(conversions_value) / NULLIF(SUM(cost_micros) / 1000000.0, 0)  AS roas,
            SUM(conversions)                                                   AS conversions,
            (SUM(cost_micros) / 1000000.0) / NULLIF(SUM(conversions), 0)      AS cpa,
            SUM(clicks) * 1.0 / NULLIF(SUM(impressions), 0)                   AS conv_rate_proxy,
            SUM(impressions)                                                   AS impressions,
            SUM(clicks)                                                        AS clicks,
            (SUM(cost_micros) / 1000000.0) / NULLIF(SUM(clicks), 0)           AS cpc,
            SUM(clicks) * 1.0 / NULLIF(SUM(impressions), 0)                   AS ctr,
            AVG(search_impression_share)                                       AS search_is,
            AVG(search_top_impression_share)                                   AS search_top_is,
            AVG(search_absolute_top_impression_share)                          AS search_abs_top_is,
            AVG(click_share)                                                   AS click_share
        FROM ro.analytics.campaign_daily
        WHERE customer_id = ?
          {current_filter}
    """

    # ── Query 2: Previous period summary ─────────────────────────────────────
    q_prev = f"""
        SELECT
            SUM(cost_micros) / 1000000.0                                      AS cost,
            SUM(conversions_value)                                             AS revenue,
            SUM(conversions_value) / NULLIF(SUM(cost_micros) / 1000000.0, 0)  AS roas,
            SUM(conversions)                                                   AS conversions,
            (SUM(cost_micros) / 1000000.0) / NULLIF(SUM(conversions), 0)      AS cpa,
            SUM(clicks) * 1.0 / NULLIF(SUM(impressions), 0)                   AS conv_rate_proxy,
            SUM(impressions)                                                   AS impressions,
            SUM(clicks)                                                        AS clicks,
            (SUM(cost_micros) / 1000000.0) / NULLIF(SUM(clicks), 0)           AS cpc,
            SUM(clicks) * 1.0 / NULLIF(SUM(impressions), 0)                   AS ctr,
            AVG(search_impression_share)                                       AS search_is,
            AVG(search_top_impression_share)                                   AS search_top_is,
            AVG(search_absolute_top_impression_share)                          AS search_abs_top_is,
            AVG(click_share)                                                   AS click_share
        FROM ro.analytics.campaign_daily
        WHERE customer_id = ?
          {prev_filter}
    """

    # ── Query 3: Daily sparkline data ─────────────────────────────────────────
    q_spark = f"""
        SELECT
            snapshot_date,
            SUM(cost_micros) / 1000000.0                                      AS cost,
            SUM(conversions_value)                                             AS revenue,
            SUM(conversions_value) / NULLIF(SUM(cost_micros) / 1000000.0, 0)  AS roas,
            SUM(conversions)                                                   AS conversions,
            (SUM(cost_micros) / 1000000.0) / NULLIF(SUM(conversions), 0)      AS cpa,
            SUM(clicks) * 1.0 / NULLIF(SUM(impressions), 0)                   AS conv_rate,
            SUM(impressions)                                                   AS impressions,
            SUM(clicks)                                                        AS clicks,
            (SUM(cost_micros) / 1000000.0) / NULLIF(SUM(clicks), 0)           AS cpc,
            SUM(clicks) * 1.0 / NULLIF(SUM(impressions), 0)                   AS ctr,
            AVG(search_impression_share)                                       AS search_is,
            AVG(search_top_impression_share)                                   AS search_top_is,
            AVG(search_absolute_top_impression_share)                          AS search_abs_top_is,
            AVG(click_share)                                                   AS click_share
        FROM ro.analytics.campaign_daily
        WHERE customer_id = ?
          {current_filter}
        GROUP BY snapshot_date
        ORDER BY snapshot_date ASC
    """

    try:
        cur = conn.execute(q_current, [customer_id]).fetchone()
        prv = conn.execute(q_prev,    [customer_id]).fetchone()
        spark_rows = conn.execute(q_spark, [customer_id]).fetchall()
    except Exception as e:
        print(f"[Campaigns M2] Error loading metrics cards data: {e}")
        import traceback
        traceback.print_exc()
        return _empty_cards()

    # Safe extraction helpers
    def _c(row, i): return float(row[i]) if row and row[i] is not None else None
    def _p(row, i): return float(row[i]) if row and row[i] is not None else None

    # Current values
    c_cost      = _c(cur, 0)
    c_revenue   = _c(cur, 1)
    c_roas      = _c(cur, 2)
    c_convs     = _c(cur, 3)
    c_cpa       = _c(cur, 4)
    c_cvr       = _c(cur, 5)
    c_impr      = _c(cur, 6)
    c_clicks    = _c(cur, 7)
    c_cpc       = _c(cur, 8)
    c_ctr       = _c(cur, 9)
    c_sis       = _c(cur, 10)
    c_topis     = _c(cur, 11)
    c_absis     = _c(cur, 12)
    c_cs        = _c(cur, 13)

    # Previous values
    p_cost      = _p(prv, 0)
    p_revenue   = _p(prv, 1)
    p_roas      = _p(prv, 2)
    p_convs     = _p(prv, 3)
    p_cpa       = _p(prv, 4)
    p_cvr       = _p(prv, 5)
    p_impr      = _p(prv, 6)
    p_clicks    = _p(prv, 7)
    p_cpc       = _p(prv, 8)
    p_ctr       = _p(prv, 9)
    p_sis       = _p(prv, 10)
    p_topis     = _p(prv, 11)
    p_absis     = _p(prv, 12)
    p_cs        = _p(prv, 13)

    # Conv rate as percentage (query returns 0–1 ratio)
    c_cvr_pct = (c_cvr * 100) if c_cvr is not None else None
    p_cvr_pct = (p_cvr * 100) if p_cvr is not None else None
    c_ctr_pct = (c_ctr * 100) if c_ctr is not None else None
    p_ctr_pct = (p_ctr * 100) if p_ctr is not None else None
    c_sis_pct       = (c_sis   * 100) if c_sis   is not None else None
    p_sis_pct       = (p_sis   * 100) if p_sis   is not None else None
    c_topis_pct     = (c_topis * 100) if c_topis is not None else None
    p_topis_pct     = (p_topis * 100) if p_topis is not None else None
    c_absis_pct     = (c_absis * 100) if c_absis is not None else None
    p_absis_pct     = (p_absis * 100) if p_absis is not None else None
    c_cs_pct        = (c_cs    * 100) if c_cs    is not None else None
    p_cs_pct        = (p_cs    * 100) if p_cs    is not None else None

    # Build sparkline lists (ordered oldest → newest)
    def _spark(col_idx, scale=1.0):
        return [
            float(row[col_idx]) * scale if row[col_idx] is not None else 0.0
            for row in spark_rows
        ]

    sp_cost    = _spark(1)
    sp_revenue = _spark(2)
    sp_roas    = _spark(3)
    sp_convs   = _spark(4)
    sp_cpa     = _spark(5)
    sp_cvr     = _spark(6, 100.0)   # convert 0–1 → percentage
    sp_impr    = _spark(7)
    sp_clicks  = _spark(8)
    sp_cpc     = _spark(9)
    sp_ctr     = _spark(10, 100.0)  # convert 0–1 → percentage
    sp_sis     = _spark(11, 100.0)
    sp_topis   = _spark(12, 100.0)
    sp_absis   = _spark(13, 100.0)
    sp_cs      = _spark(14, 100.0)

    # ── Financial cards (8) ───────────────────────────────────────────────────
    financial_cards = [
        _card('Cost',         c_cost,    p_cost,    sp_cost,    'currency',    invert=True),
        _card('Revenue',      c_revenue, p_revenue, sp_revenue, 'currency'),
        _card('ROAS',         c_roas,    p_roas,    sp_roas,    'ratio'),
        _blank_card('financial'),
        _card('Conversions',  c_convs,   p_convs,   sp_convs,   'number'),
        _card('Cost / Conv',  c_cpa,     p_cpa,     sp_cpa,     'currency',    invert=True),
        _card('Conv Rate',    c_cvr_pct, p_cvr_pct, sp_cvr,     'percentage'),
        _blank_card('financial'),
    ]

    # ── Actions cards (8) ─────────────────────────────────────────────────────
    actions_cards = [
        _card('Impressions',       c_impr,    p_impr,    sp_impr,  'number',     card_type='actions'),
        _card('Clicks',            c_clicks,  p_clicks,  sp_clicks,'number',     card_type='actions'),
        _card('Avg CPC',           c_cpc,     p_cpc,     sp_cpc,   'currency',   card_type='actions'),
        _card('Avg CTR',           c_ctr_pct, p_ctr_pct, sp_ctr,   'percentage', card_type='actions'),
        _card('Search Impr Share', c_sis_pct, p_sis_pct, sp_sis,   'percentage', card_type='actions'),
        _card('Search Top IS',     c_topis_pct, p_topis_pct, sp_topis, 'percentage', card_type='actions'),
        _card('Search Abs Top IS', c_absis_pct, p_absis_pct, sp_absis, 'percentage', card_type='actions'),
        _card('Click Share',       c_cs_pct,  p_cs_pct,  sp_cs,    'percentage', card_type='actions'),
    ]

    return financial_cards, actions_cards


def _empty_cards() -> Tuple[List[Dict], List[Dict]]:
    """Return blank card lists on error."""
    fin = [_blank_card('financial')] * 8
    act = [_blank_card('actions')] * 8
    return fin, act


# ==================== Chat 24 M3: Chart Data Builder ====================

def build_chart_data(
    conn: duckdb.DuckDBPyConnection,
    customer_id: str,
    active_days: int,
    date_from: Optional[str],
    date_to: Optional[str],
) -> Dict[str, Any]:
    """
    Build chart_data dict for the M3 performance_chart macro.

    Queries ro.analytics.campaign_daily for daily cost/impressions/clicks
    and derives avg_cpc per day. Computes period totals and change_pct
    vs previous period for all 4 metrics.

    avg_cpc total = total_cost / total_clicks (never sum of daily values).

    Returns:
        chart_data dict with keys: dates, cost, impressions, clicks, avg_cpc
    """
    current_filter, prev_filter = _build_date_filters(active_days, date_from, date_to)

    _empty = {
        'dates': [],
        'cost':        {'values': [], 'total': None, 'change_pct': None, 'axis': 'y1'},
        'impressions': {'values': [], 'total': None, 'change_pct': None, 'axis': 'y2'},
        'clicks':      {'values': [], 'total': None, 'change_pct': None, 'axis': 'y2'},
        'avg_cpc':     {'values': [], 'total': None, 'change_pct': None, 'axis': 'y1'},
    }

    # ── Daily values (current period) ────────────────────────────────────────
    q_daily = f"""
        SELECT
            snapshot_date,
            SUM(cost_micros) / 1000000.0                                    AS cost,
            SUM(impressions)                                                 AS impressions,
            SUM(clicks)                                                      AS clicks,
            (SUM(cost_micros) / 1000000.0) / NULLIF(SUM(clicks), 0)        AS avg_cpc
        FROM ro.analytics.campaign_daily
        WHERE customer_id = ?
          {current_filter}
        GROUP BY snapshot_date
        ORDER BY snapshot_date ASC
    """

    # ── Current period totals ─────────────────────────────────────────────────
    q_current = f"""
        SELECT
            SUM(cost_micros) / 1000000.0                                    AS cost,
            SUM(impressions)                                                 AS impressions,
            SUM(clicks)                                                      AS clicks
        FROM ro.analytics.campaign_daily
        WHERE customer_id = ?
          {current_filter}
    """

    # ── Previous period totals ────────────────────────────────────────────────
    q_prev = f"""
        SELECT
            SUM(cost_micros) / 1000000.0                                    AS cost,
            SUM(impressions)                                                 AS impressions,
            SUM(clicks)                                                      AS clicks
        FROM ro.analytics.campaign_daily
        WHERE customer_id = ?
          {prev_filter}
    """

    try:
        daily_rows = conn.execute(q_daily,   [customer_id]).fetchall()
        cur        = conn.execute(q_current, [customer_id]).fetchone()
        prv        = conn.execute(q_prev,    [customer_id]).fetchone()
    except Exception as e:
        print(f"[Campaigns M3] Error building chart data: {e}")
        import traceback
        traceback.print_exc()
        return _empty

    def _f(row, i): return float(row[i]) if row and row[i] is not None else None

    # Current / previous totals
    c_cost  = _f(cur, 0)
    c_impr  = _f(cur, 1)
    c_clicks= _f(cur, 2)
    p_cost  = _f(prv, 0)
    p_impr  = _f(prv, 1)
    p_clicks= _f(prv, 2)

    # avg_cpc totals: total_cost / total_clicks
    c_cpc = (c_cost / c_clicks) if c_cost and c_clicks else None
    p_cpc = (p_cost / p_clicks) if p_cost and p_clicks else None

    # Daily series
    dates      = [str(row[0]) for row in daily_rows]
    cost_vals  = [float(row[1]) if row[1] is not None else 0.0 for row in daily_rows]
    impr_vals  = [float(row[2]) if row[2] is not None else 0.0 for row in daily_rows]
    click_vals = [float(row[3]) if row[3] is not None else 0.0 for row in daily_rows]
    cpc_vals   = [float(row[4]) if row[4] is not None else 0.0 for row in daily_rows]

    return {
        'dates': dates,
        'cost': {
            'values':     cost_vals,
            'total':      c_cost,
            'change_pct': _calculate_change_pct(c_cost,   p_cost),
            'axis':       'y1',
        },
        'impressions': {
            'values':     impr_vals,
            'total':      c_impr,
            'change_pct': _calculate_change_pct(c_impr,   p_impr),
            'axis':       'y2',
        },
        'clicks': {
            'values':     click_vals,
            'total':      c_clicks,
            'change_pct': _calculate_change_pct(c_clicks, p_clicks),
            'axis':       'y2',
        },
        'avg_cpc': {
            'values':     cpc_vals,
            'total':      c_cpc,
            'change_pct': _calculate_change_pct(c_cpc,    p_cpc),
            'axis':       'y1',
        },
    }


# ==================== Main route ====================

@bp.route("/campaigns")
@login_required
def campaigns():
    """
    Campaigns page - campaign performance with rule visibility.

    Chat 23 M2: Now passes financial_cards, actions_cards, metrics_collapsed
    to template for the standardised metrics cards component.
    """
    config, clients, current_client_path = get_page_context()

    active_days, date_from, date_to = get_date_range_from_session()
    if active_days == 30 and date_from is None and 'days' in request.args:
        url_days = request.args.get('days', 30, type=int)
        if url_days in [7, 90]:
            active_days = url_days

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 25, type=int)

    if per_page not in [10, 25, 50, 100]:
        per_page = 25
    if page < 1:
        page = 1

    conn = get_db_connection(config)

    # Existing campaign table data
    all_campaigns = load_campaign_data(conn, config.customer_id, active_days, date_from, date_to)

    # M2: Metrics cards data
    financial_cards, actions_cards = load_metrics_cards_data(
        conn, config.customer_id, active_days, date_from, date_to
    )

    # M3: Chart data
    chart_data = build_chart_data(conn, config.customer_id, active_days, date_from, date_to)

    conn.close()

    metrics = compute_metrics_bar(all_campaigns)

    campaigns_paginated, total_campaigns, total_pages = apply_pagination(
        all_campaigns, page, per_page
    )

    rules = get_rules_for_page('campaign', config.customer_id)
    rule_counts = count_rules_by_category(rules)

    active_campaigns  = sum(1 for c in all_campaigns if c['campaign_status'] == 'ENABLED')
    paused_campaigns  = sum(1 for c in all_campaigns if c['campaign_status'] == 'PAUSED')
    search_campaigns  = sum(1 for c in all_campaigns if c['channel_type'] == 'SEARCH')
    shopping_campaigns = sum(1 for c in all_campaigns if c['channel_type'] == 'SHOPPING')
    display_campaigns = sum(1 for c in all_campaigns if c['channel_type'] == 'DISPLAY')

    return render_template(
        "campaigns.html",
        # Client context
        client_name=config.client_name,
        available_clients=clients,
        current_client_config=current_client_path,
        # Campaign data
        campaigns=campaigns_paginated,
        total_campaigns=total_campaigns,
        # Metrics bar (legacy)
        metrics=metrics,
        # M2: Metrics cards
        financial_cards=financial_cards,
        actions_cards=actions_cards,
        metrics_collapsed=get_metrics_collapsed('campaigns'),
        # Pagination
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        # Date filter
        days=active_days,
        active_days=active_days,
        date_from=date_from,
        date_to=date_to,
        # Campaign counts
        active_campaigns=active_campaigns,
        paused_campaigns=paused_campaigns,
        search_campaigns=search_campaigns,
        shopping_campaigns=shopping_campaigns,
        display_campaigns=display_campaigns,
        # Rules
        rules=rules,
        rule_counts=rule_counts,
        # M3: Chart
        chart_data=chart_data,
        active_metrics=get_chart_metrics('campaigns'),
    )
