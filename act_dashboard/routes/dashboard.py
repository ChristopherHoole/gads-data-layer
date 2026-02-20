"""
Dashboard home page route - overview stats.
"""

from flask import Blueprint, render_template, session, request
from act_dashboard.auth import login_required
from act_dashboard.routes.shared import get_current_config, get_available_clients, get_date_range_from_session, get_metrics_collapsed
import duckdb
import json
from datetime import date, datetime
from typing import Any

bp = Blueprint('dashboard', __name__)


def calculate_change_pct(current: float, previous: float) -> float:
    """
    Calculate percentage change between current and previous values.
    
    Args:
        current: Current period value
        previous: Previous period value
        
    Returns:
        Percentage change (e.g., 12.5 for +12.5%)
    """
    if previous is None or previous == 0:
        return 0 if (current is None or current == 0) else 100
    if current is None:
        return -100
    return ((current - previous) / previous) * 100




# ==================== Chat 23 M2: Metrics Cards ====================

def _fmt_dash(value, fmt):
    """Format a metric value for display."""
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


def _chg(current, previous):
    """Change % — returns None (dash) when no previous data."""
    if previous is None or previous == 0:
        return None
    if current is None:
        return -100.0
    return ((float(current) - float(previous)) / float(previous)) * 100.0


def _card_d(label, value, prev, sparkline, fmt, invert=False, card_type='financial'):
    return {
        'label': label,
        'value_display': _fmt_dash(value, fmt),
        'change_pct': _chg(value, prev),
        'sparkline_data': sparkline,
        'format_type': fmt,
        'invert_colours': invert,
        'card_type': card_type,
        'sub_label': None,
    }


def _blank_d(card_type='financial'):
    return {
        'label': '', 'value_display': '', 'change_pct': None,
        'sparkline_data': None, 'format_type': 'blank',
        'invert_colours': False, 'card_type': card_type, 'sub_label': None,
    }


def load_dashboard_metrics_cards(conn, customer_id, date_filter, prev_filter):
    """
    Build financial_cards and actions_cards for the Dashboard page.
    Uses the already-built date_filter and prev_filter strings from the route.

    Financial (8): Cost | Revenue | ROAS | BLANK | Conversions | CPA | Conv Rate | BLANK
    Actions (8):   Impressions | Clicks | Avg CPC | Avg CTR |
                   Search IS | Search Top IS | Search Abs Top IS | Click Share
    """
    q_cur = f"""
        SELECT
            SUM(cost_micros) / 1000000.0                                      AS cost,
            SUM(conversions_value)                                             AS revenue,
            SUM(conversions_value) / NULLIF(SUM(cost_micros) / 1000000.0, 0)  AS roas,
            SUM(conversions)                                                   AS conversions,
            (SUM(cost_micros) / 1000000.0) / NULLIF(SUM(conversions), 0)      AS cpa,
            SUM(clicks) * 1.0 / NULLIF(SUM(impressions), 0)                   AS cvr,
            SUM(impressions)                                                   AS impressions,
            SUM(clicks)                                                        AS clicks,
            (SUM(cost_micros) / 1000000.0) / NULLIF(SUM(clicks), 0)           AS cpc,
            SUM(clicks) * 1.0 / NULLIF(SUM(impressions), 0)                   AS ctr,
            AVG(search_impression_share)                                       AS search_is,
            AVG(search_top_impression_share)                                   AS search_top_is,
            AVG(search_absolute_top_impression_share)                          AS search_abs_top_is,
            AVG(click_share)                                                   AS click_share
        FROM analytics.campaign_daily
        WHERE customer_id = ?
          {date_filter}
          AND snapshot_date < CURRENT_DATE
    """
    q_prv = f"""
        SELECT
            SUM(cost_micros) / 1000000.0                                      AS cost,
            SUM(conversions_value)                                             AS revenue,
            SUM(conversions_value) / NULLIF(SUM(cost_micros) / 1000000.0, 0)  AS roas,
            SUM(conversions)                                                   AS conversions,
            (SUM(cost_micros) / 1000000.0) / NULLIF(SUM(conversions), 0)      AS cpa,
            SUM(clicks) * 1.0 / NULLIF(SUM(impressions), 0)                   AS cvr,
            SUM(impressions)                                                   AS impressions,
            SUM(clicks)                                                        AS clicks,
            (SUM(cost_micros) / 1000000.0) / NULLIF(SUM(clicks), 0)           AS cpc,
            SUM(clicks) * 1.0 / NULLIF(SUM(impressions), 0)                   AS ctr,
            AVG(search_impression_share)                                       AS search_is,
            AVG(search_top_impression_share)                                   AS search_top_is,
            AVG(search_absolute_top_impression_share)                          AS search_abs_top_is,
            AVG(click_share)                                                   AS click_share
        FROM analytics.campaign_daily
        WHERE customer_id = ?
          {prev_filter}
    """
    q_spark = f"""
        SELECT
            snapshot_date,
            SUM(cost_micros) / 1000000.0                                      AS cost,
            SUM(conversions_value)                                             AS revenue,
            SUM(conversions_value) / NULLIF(SUM(cost_micros) / 1000000.0, 0)  AS roas,
            SUM(conversions)                                                   AS conversions,
            (SUM(cost_micros) / 1000000.0) / NULLIF(SUM(conversions), 0)      AS cpa,
            SUM(clicks) * 1.0 / NULLIF(SUM(impressions), 0)                   AS cvr,
            SUM(impressions)                                                   AS impressions,
            SUM(clicks)                                                        AS clicks,
            (SUM(cost_micros) / 1000000.0) / NULLIF(SUM(clicks), 0)           AS cpc,
            SUM(clicks) * 1.0 / NULLIF(SUM(impressions), 0)                   AS ctr,
            AVG(search_impression_share)                                       AS search_is,
            AVG(search_top_impression_share)                                   AS search_top_is,
            AVG(search_absolute_top_impression_share)                          AS search_abs_top_is,
            AVG(click_share)                                                   AS click_share
        FROM analytics.campaign_daily
        WHERE customer_id = ?
          {date_filter}
          AND snapshot_date < CURRENT_DATE
        GROUP BY snapshot_date
        ORDER BY snapshot_date ASC
    """

    try:
        cur = conn.execute(q_cur, [customer_id]).fetchone()
        prv = conn.execute(q_prv, [customer_id]).fetchone()
        spark_rows = conn.execute(q_spark, [customer_id]).fetchall()
    except Exception as e:
        print(f"[Dashboard M2] Error loading metrics cards: {e}")
        return [_blank_d('financial')] * 8, [_blank_d('actions')] * 8

    def _v(row, i): return float(row[i]) if row and row[i] is not None else None

    c = [_v(cur, i) for i in range(14)]
    p = [_v(prv, i) for i in range(14)]

    # Convert ratios to percentages
    def pct(val): return val * 100 if val is not None else None

    def _spark(col_idx, scale=1.0):
        return [float(r[col_idx]) * scale if r[col_idx] is not None else 0.0 for r in spark_rows]

    sp_cost    = _spark(1)
    sp_revenue = _spark(2)
    sp_roas    = _spark(3)
    sp_convs   = _spark(4)
    sp_cpa     = _spark(5)
    sp_cvr     = _spark(6, 100.0)
    sp_impr    = _spark(7)
    sp_clicks  = _spark(8)
    sp_cpc     = _spark(9)
    sp_ctr     = _spark(10, 100.0)
    sp_sis     = _spark(11, 100.0)
    sp_topis   = _spark(12, 100.0)
    sp_absis   = _spark(13, 100.0)
    sp_cs      = _spark(14, 100.0)

    financial_cards = [
        _card_d('Cost',        c[0],       p[0],       sp_cost,    'currency',   invert=True),
        _card_d('Revenue',     c[1],       p[1],       sp_revenue, 'currency'),
        _card_d('ROAS',        c[2],       p[2],       sp_roas,    'ratio'),
        _blank_d('financial'),
        _card_d('Conversions', c[3],       p[3],       sp_convs,   'number'),
        _card_d('Cost / Conv', c[4],       p[4],       sp_cpa,     'currency',   invert=True),
        _card_d('Conv Rate',   pct(c[5]),  pct(p[5]),  sp_cvr,     'percentage'),
        _blank_d('financial'),
    ]
    actions_cards = [
        _card_d('Impressions',       c[6],          p[6],          sp_impr,  'number',     card_type='actions'),
        _card_d('Clicks',            c[7],          p[7],          sp_clicks,'number',     card_type='actions'),
        _card_d('Avg CPC',           c[8],          p[8],          sp_cpc,   'currency',   card_type='actions'),
        _card_d('Avg CTR',           pct(c[9]),     pct(p[9]),     sp_ctr,   'percentage', card_type='actions'),
        _card_d('Search Impr Share', pct(c[10]),    pct(p[10]),    sp_sis,   'percentage', card_type='actions'),
        _card_d('Search Top IS',     pct(c[11]),    pct(p[11]),    sp_topis, 'percentage', card_type='actions'),
        _card_d('Search Abs Top IS', pct(c[12]),    pct(p[12]),    sp_absis, 'percentage', card_type='actions'),
        _card_d('Click Share',       pct(c[13]),    pct(p[13]),    sp_cs,    'percentage', card_type='actions'),
    ]
    return financial_cards, actions_cards


@bp.route("/")
@login_required
def home() -> str:
    """
    Dashboard home page with overview stats.
    
    Returns:
        Rendered dashboard template
    """
    config = get_current_config()
    clients = get_available_clients()
    current_client_path = session.get("current_client_config")
    
    # Get date range from session (default 30d).
    # Fall back to URL param only if session has no preference yet.
    active_days, date_from, date_to = get_date_range_from_session()
    if active_days == 30 and date_from is None and 'days' in request.args:
        url_days = request.args.get('days', 30, type=int)
        if url_days in [7, 90]:
            active_days = url_days

    # Build date filter clauses for all queries.
    if date_from and date_to:
        date_filter = f"AND snapshot_date >= '{date_from}' AND snapshot_date <= '{date_to}'"
        from datetime import timedelta as _td
        from datetime import datetime as _dt
        _df = _dt.strptime(date_from, '%Y-%m-%d').date()
        _dt2 = _dt.strptime(date_to, '%Y-%m-%d').date()
        _span = (_dt2 - _df).days + 1
        _prev_to = (_df - _td(days=1)).isoformat()
        _prev_from = (_df - _td(days=_span)).isoformat()
        prev_filter = f"AND snapshot_date >= '{_prev_from}' AND snapshot_date <= '{_prev_to}'"
        days = 0
    else:
        days = active_days
        date_filter = f"AND snapshot_date >= CURRENT_DATE - INTERVAL '{days} days'"
        prev_filter = f"AND snapshot_date >= CURRENT_DATE - INTERVAL '{days * 2} days' AND snapshot_date < CURRENT_DATE - INTERVAL '{days} days'"

    # Connect to database
    conn = duckdb.connect(config.db_path, read_only=True)

    # Query 1: Current period metrics
    # Note: Using f-string for INTERVAL because DuckDB doesn't support ? in INTERVAL
    current_query = f"""
    SELECT
        SUM(clicks) as clicks,
        SUM(impressions) as impressions,
        SUM(cost_micros) / 1000000 as cost,
        SUM(conversions) as conversions,
        SUM(conversions_value) / NULLIF(SUM(cost_micros) / 1000000, 0) as roas,
        SUM(cost_micros) / 1000000 / NULLIF(SUM(conversions), 0) as cpa
    FROM analytics.campaign_daily
    WHERE customer_id = ?
      {date_filter}
      AND snapshot_date < CURRENT_DATE
    """
    current = conn.execute(current_query, [config.customer_id]).fetchone()
    
    # Query 2: Previous period metrics (for change % calculation)
    previous_query = f"""
    SELECT
        SUM(clicks) as clicks,
        SUM(impressions) as impressions,
        SUM(cost_micros) / 1000000 as cost,
        SUM(conversions) as conversions,
        SUM(conversions_value) / NULLIF(SUM(cost_micros) / 1000000, 0) as roas,
        SUM(cost_micros) / 1000000 / NULLIF(SUM(conversions), 0) as cpa
    FROM analytics.campaign_daily
    WHERE customer_id = ?
      {prev_filter}
    """
    previous = conn.execute(previous_query, [config.customer_id]).fetchone()
    
    # Calculate metrics with change percentages
    metrics = {
        'clicks': int(current[0] or 0),
        'clicks_change': calculate_change_pct(current[0], previous[0]),
        'impressions': int(current[1] or 0),
        'impressions_change': calculate_change_pct(current[1], previous[1]),
        'cost': float(current[2] or 0),
        'cost_change': calculate_change_pct(current[2], previous[2]),
        'conversions': int(current[3] or 0),
        'conversions_change': calculate_change_pct(current[3], previous[3]),
        'roas': float(current[4] or 0),
        'roas_change': calculate_change_pct(current[4], previous[4]),
        'cpa': float(current[5] or 0),
        'cpa_change': calculate_change_pct(current[5], previous[5]),
    }

    # Query 3: Daily performance trend (for chart)
    trend_query = f"""
    SELECT
        snapshot_date,
        SUM(cost_micros) / 1000000 as cost,
        SUM(conversions) as conversions,
        SUM(conversions_value) / NULLIF(SUM(cost_micros) / 1000000, 0) as roas
    FROM analytics.campaign_daily
    WHERE customer_id = ?
      {date_filter}
    GROUP BY snapshot_date
    ORDER BY snapshot_date
    """
    trend_raw = conn.execute(trend_query, [config.customer_id]).fetchall()
    
    # Format trend data with readable dates
    trend_data = [
        {
            'date': row[0].strftime('%b %d') if isinstance(row[0], (date, datetime)) else str(row[0]),
            'cost': float(row[1] or 0),
            'conversions': int(row[2] or 0),
            'roas': float(row[3] or 0)
        }
        for row in trend_raw
    ]

    # Query 4: Top 5 campaigns by spend
    top_campaigns_query = f"""
    SELECT
        campaign_id,
        campaign_name,
        campaign_status,
        channel_type,
        SUM(cost_micros) / 1000000 as spend,
        SUM(clicks) as clicks,
        SUM(conversions) as conversions,
        SUM(conversions_value) / NULLIF(SUM(cost_micros) / 1000000, 0) as roas
    FROM analytics.campaign_daily
    WHERE customer_id = ?
      {date_filter}
    GROUP BY campaign_id, campaign_name, campaign_status, channel_type
    ORDER BY spend DESC
    LIMIT 5
    """
    top_campaigns = conn.execute(top_campaigns_query, [config.customer_id]).fetchall()

    # Query 5: Campaign status counts
    status_query = """
    SELECT
        campaign_status,
        COUNT(DISTINCT campaign_id) as count
    FROM (
        SELECT DISTINCT campaign_id, campaign_status
        FROM analytics.campaign_daily
        WHERE customer_id = ?
          AND snapshot_date >= CURRENT_DATE - INTERVAL '7 days'
    )
    GROUP BY campaign_status
    """
    status_counts = conn.execute(status_query, [config.customer_id]).fetchall()
    
    # Parse status counts
    active_campaigns_count = 0
    paused_campaigns_count = 0
    for status, count in status_counts:
        if status and 'ENABLED' in status.upper():
            active_campaigns_count = count
        elif status and 'PAUSED' in status.upper():
            paused_campaigns_count = count

    # Query 6: Recent changes (last 5)
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

    # Query 7: Last sync time (most recent snapshot_date)
    last_sync_query = """
    SELECT MAX(snapshot_date)
    FROM analytics.campaign_daily
    WHERE customer_id = ?
    """
    last_sync_result = conn.execute(last_sync_query, [config.customer_id]).fetchone()
    last_sync_time = "Never"
    if last_sync_result and last_sync_result[0]:
        last_sync_date = last_sync_result[0]
        if isinstance(last_sync_date, (date, datetime)):
            days_ago = (date.today() - last_sync_date).days
            if days_ago == 0:
                last_sync_time = "Today"
            elif days_ago == 1:
                last_sync_time = "Yesterday"
            else:
                last_sync_time = f"{days_ago} days ago"

    # M2: Metrics cards — uses same conn before close
    financial_cards, actions_cards = load_dashboard_metrics_cards(
        conn, config.customer_id, date_filter, prev_filter
    )

    conn.close()

    # Load and sort recommendations by predicted_lift
    today = date.today().isoformat()
    suggestions_path = config.get_suggestions_path(today)
    recommendations_count = 0
    top_recommendations = []
    
    if suggestions_path.exists():
        with open(suggestions_path, "r") as f:
            suggestions_data = json.load(f)
            all_recommendations = [
                r for r in suggestions_data.get("recommendations", [])
                if not r.get("blocked", False)
            ]
            recommendations_count = len(all_recommendations)
            
            # Sort by predicted_lift (descending) and take top 3
            sorted_recommendations = sorted(
                all_recommendations,
                key=lambda x: x.get('predicted_lift', 0),
                reverse=True
            )
            top_recommendations = sorted_recommendations[:3]

    return render_template(
        "dashboard_new.html",
        client_name=config.client_name,
        available_clients=clients,
        current_client_config=current_client_path,
        days=active_days,
        active_days=active_days,
        date_from=date_from,
        date_to=date_to,
        metrics=metrics,
        trend_data=trend_data,
        top_campaigns=top_campaigns,
        recommendations_count=recommendations_count,
        top_recommendations=top_recommendations,
        recent_changes=recent_changes,
        active_campaigns_count=active_campaigns_count,
        paused_campaigns_count=paused_campaigns_count,
        last_sync_time=last_sync_time,
        # M2: Metrics cards
        financial_cards=financial_cards,
        actions_cards=actions_cards,
        metrics_collapsed=get_metrics_collapsed('dashboard'),
    )
