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

from flask import Blueprint, render_template, request
from act_dashboard.auth import login_required
from act_dashboard.routes.shared import (
    get_page_context,
    get_db_connection,
    get_date_range_from_session,
    get_metrics_collapsed,
)
from act_dashboard.routes.rule_helpers import get_rules_for_page, count_rules_by_category
from typing import List, Dict, Any, Tuple
import duckdb

bp = Blueprint('ads', __name__)


def load_ad_data(
    conn: duckdb.DuckDBPyConnection,
    customer_id: str,
    days: int
) -> List[Dict[str, Any]]:
    """
    Load ad data from ro.analytics.ad_features_daily.

    Uses latest snapshot date only (pre-aggregated features table).
    Reads the correct windowed columns based on the days parameter.

    Table confirmed columns:
        ad_status, ad_type, ad_strength, headlines (VARCHAR[]),
        descriptions (VARCHAR[]), final_url,
        impressions_7d/30d/90d, clicks_7d/30d/90d,
        cost_micros_7d/30d/90d, conversions_7d/30d/90d

    Args:
        conn: Database connection
        customer_id: Customer ID
        days: Date window — 7, 30, or 90

    Returns:
        List of ad dictionaries
    """
    # Map days to column suffix
    if days == 7:
        suffix = '7d'
    elif days == 90:
        suffix = '90d'
    else:
        suffix = '30d'  # default

    query = f"""
        SELECT
            ad_id,
            campaign_id,
            ad_group_id,
            campaign_name,
            ad_group_name,
            ad_status,
            ad_type,
            ad_strength,
            array_length(headlines)    AS headlines_count,
            array_length(descriptions) AS descriptions_count,
            final_url,
            impressions_{suffix}       AS impressions,
            clicks_{suffix}            AS clicks,
            cost_micros_{suffix}       AS cost_micros,
            conversions_{suffix}       AS conversions
        FROM analytics.ad_features_daily
        WHERE customer_id = ?
          AND snapshot_date = (
              SELECT MAX(snapshot_date)
              FROM analytics.ad_features_daily
              WHERE customer_id = ?
          )
        ORDER BY cost_micros_{suffix} DESC NULLS LAST
    """

    try:
        rows = conn.execute(query, [customer_id, customer_id]).fetchall()
        cols = [d[0] for d in conn.description]

        ads = []
        for row in rows:
            d = dict(zip(cols, row))

            # Calculate cost, CTR, CPA in Python from raw values
            cost_micros = int(d.get('cost_micros') or 0)
            impressions = int(d.get('impressions') or 0)
            clicks      = int(d.get('clicks')      or 0)
            conversions = float(d.get('conversions') or 0)
            cost        = cost_micros / 1000000.0
            ctr         = (clicks / impressions * 100) if impressions > 0 else 0.0
            cpa         = (cost / conversions)         if conversions  > 0 else 0.0

            # Safe type conversions — use confirmed column names
            d['ad_id']              = str(d.get('ad_id', ''))
            d['campaign_id']        = str(d.get('campaign_id', ''))
            d['ad_group_id']        = str(d.get('ad_group_id', ''))
            d['campaign_name']      = str(d.get('campaign_name')  or 'Unknown')
            d['ad_group_name']      = str(d.get('ad_group_name')  or 'Unknown')
            d['status']             = str(d.get('ad_status')      or 'UNKNOWN')
            d['ad_type']            = str(d.get('ad_type')        or 'UNKNOWN')
            d['ad_strength']        = d.get('ad_strength')        # keep None — handled in template
            d['headlines_count']    = int(d.get('headlines_count')    or 0)
            d['descriptions_count'] = int(d.get('descriptions_count') or 0)
            d['final_url']          = str(d.get('final_url')      or '')
            d['impressions']        = impressions
            d['clicks']             = clicks
            d['cost']               = cost
            d['conversions']        = conversions
            d['ctr']                = ctr
            d['cpa']                = cpa

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


def _card_ads(label, value, sparkline, fmt, invert=False, card_type='financial', sub_label=None):
    """Ads cards have no prev period — change_pct always None (dash)."""
    return {
        'label': label,
        'value_display': _fmt_ads(value, fmt),
        'change_pct': None,
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


def load_ads_metrics_cards(conn, customer_id, days, all_ads):
    """
    Build financial_cards and actions_cards for Ads page.

    Uses pre-computed all_ads list for summary values (already loaded).
    Sparklines from ad_features_daily won't be available — pass None/empty.

    Financial (8): Cost | Revenue | ROAS | Ad Strength | Conversions | CPA | Conv Rate | BLANK
    Actions  (8): Impressions | Clicks | Avg CPC | Avg CTR | 4 blanks (no IS at ad level)
    """
    if not all_ads:
        return [_blank_ads('financial')] * 8, [_blank_ads('actions')] * 8

    suffix = '7d' if days == 7 else ('90d' if days == 90 else '30d')

    total_cost        = sum(a['cost']        for a in all_ads)
    total_revenue     = sum(a.get('conversions_value', 0) or 0 for a in all_ads)
    total_conversions = sum(a['conversions'] for a in all_ads)
    total_impressions = sum(a['impressions'] for a in all_ads)
    total_clicks      = sum(a['clicks']      for a in all_ads)

    roas     = (total_revenue / total_cost)                  if total_cost > 0        else None
    cpa      = (total_cost / total_conversions)              if total_conversions > 0  else None
    cvr      = (total_conversions / total_clicks * 100)      if total_clicks > 0       else None
    cpc      = (total_cost / total_clicks)                   if total_clicks > 0       else None
    ctr      = (total_clicks / total_impressions * 100)      if total_impressions > 0  else None

    good_strength  = sum(1 for a in all_ads if a.get('ad_strength') in ('GOOD', 'EXCELLENT'))
    poor_strength  = sum(1 for a in all_ads if a.get('ad_strength') == 'POOR')
    total_ads      = len(all_ads)
    strength_label = f"{good_strength}/{total_ads}"
    strength_sub   = f"{poor_strength} Poor" if poor_strength > 0 else "Good/Excellent"

    financial_cards = [
        _card_ads('Cost',          total_cost,        None, 'currency',     invert=True),
        _card_ads('Revenue',       total_revenue,     None, 'currency'),
        _card_ads('ROAS',          roas,              None, 'ratio'),
        _blank_ads('financial'),
        _card_ads('Conversions',   total_conversions, None, 'number'),
        _card_ads('Cost / Conv',   cpa,               None, 'currency',     invert=True),
        _card_ads('Conv Rate',     cvr,               None, 'percentage'),
        _blank_ads('financial'),
    ]
    actions_cards = [
        _card_ads('Impressions',   total_impressions, None, 'number',       card_type='actions'),
        _card_ads('Clicks',        total_clicks,      None, 'number',       card_type='actions'),
        _card_ads('Avg CPC',       cpc,               None, 'currency',     card_type='actions'),
        _card_ads('Avg CTR',       ctr,               None, 'percentage',   card_type='actions'),
        _card_ads('Ad Strength',   strength_label,    None, 'ad_strength',  card_type='actions', sub_label=strength_sub),
        _blank_ads('actions'),
        _blank_ads('actions'),
        _blank_ads('actions'),
    ]
    return financial_cards, actions_cards


@bp.route("/ads")
@login_required
def ads():
    """
    Ads page - Bootstrap 5 redesign (Chat 21f).

    URL Parameters:
        days:     Date window 7/30/90 (default: 30)
        page:     Page number (default: 1)
        per_page: Rows per page 10/25/50/100 (default: 25)
        status:   'all', 'enabled', 'paused' (default: 'all')
    """
    # Get date range from session.
    # Ads uses pre-aggregated windowed columns (_7d/_30d/_90d).
    # Custom date ranges are not supported by the schema — fall back to 30d.
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

    # Validate parameters
    if per_page not in [10, 25, 50, 100]:            per_page = 25
    if page     < 1:                                 page     = 1
    if status   not in ['all', 'enabled', 'paused']: status   = 'all'

    # Get common page context
    config, clients, current_client_path = get_page_context()

    # Get database connection
    conn = get_db_connection(config)

    # Load all ad data for selected window
    all_ads = load_ad_data(conn, config.customer_id, days)

    # M2: Metrics cards (pass all_ads before status filter for totals)
    financial_cards, actions_cards = load_ads_metrics_cards(
        conn, config.customer_id, days, all_ads
    )

    conn.close()

    # Apply status filter (Python-side)
    filtered_ads = apply_status_filter(all_ads, status)

    # Compute metrics bar from filtered list
    metrics = compute_metrics(filtered_ads)

    # Apply pagination
    ads_paginated, total_ads, total_pages = apply_pagination(filtered_ads, page, per_page)

    # Load rules for this page
    try:
        rules       = get_rules_for_page('ad', customer_id=config.customer_id)
        rule_counts = count_rules_by_category(rules)
    except Exception as e:
        print(f"[Ads] Rules load error: {e}")
        import traceback
        traceback.print_exc()
        rules       = []
        rule_counts = {}

    print(f"[Ads] {len(all_ads)} ads loaded, {len(filtered_ads)} after filter, {len(rules)} rules")

    return render_template(
        'ads_new.html',
        # Client context
        client_name=config.client_name,
        available_clients=clients,
        current_client_config=current_client_path,
        # Ad data
        ads=ads_paginated,
        total_ads=total_ads,
        # Metrics
        metrics=metrics,
        # Pagination
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        # Filters
        days=days,
        active_days=active_days,
        date_from=date_from,
        date_to=date_to,
        status=status,
        # Rules
        rules=rules,
        rule_counts=rule_counts,
        # Error
        error=None,
        # M2: Metrics cards
        financial_cards=financial_cards,
        actions_cards=actions_cards,
        metrics_collapsed=get_metrics_collapsed('ads'),
    )
