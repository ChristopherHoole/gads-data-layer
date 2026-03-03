"""
Shopping page route - Bootstrap 5 redesign.

Chat 21g: Full redesign matching campaigns/ad_groups/keywords/ads pattern.

Tabs:
  1. Campaigns  — raw_shopping_campaign_daily LEFT JOIN analytics.campaign_daily
  2. Products   — analytics.product_features_daily (windowed cols), fallback to
                  raw_product_performance_daily if features table is empty
  3. Feed Quality — raw_product_feed_quality with graceful empty state
  4. Rules      — get_rules_for_page('shopping') — will show empty state (0 rules)

Key decisions (from Master Chat answers):
  - Campaign status: JOIN analytics.campaign_daily on campaign_id
  - Products date filter: windowed columns (_w7/_w30/_w90), NOT row filtering
  - Products fallback: raw_product_performance_daily when features table empty
  - Feed freshness: MAX(ingested_at) from raw_product_feed_quality
  - Rules: empty state expected (no public shopping rule functions yet)
"""

from flask import Blueprint, render_template, request, session, jsonify
from act_dashboard.auth import login_required
from act_dashboard.routes.shared import get_page_context, get_db_connection, get_date_range_from_session, get_metrics_collapsed, get_chart_metrics, get_performance_data
from act_dashboard.routes.rule_helpers import get_rules_for_page, count_rules_by_category
from act_dashboard.routes.rules_api import load_rules
from datetime import date, datetime, timedelta, timezone
from typing import List, Dict, Any, Tuple, Optional
import duckdb

bp = Blueprint('shopping', __name__)


# =============================================================================
# TAB 1: CAMPAIGNS
# =============================================================================

ALLOWED_SHOPPING_SORT = {
    'campaign_name', 'cost', 'conversions_value', 'conversions',
    'conv_value_per_cost', 'cost_per_conv', 'conv_rate',
    'all_conversions', 'all_conversions_value',
    'impressions', 'clicks', 'avg_cpc', 'ctr',
    'search_impression_share', 'search_top_impression_share',
    'search_absolute_top_impression_share', 'click_share',
    'optimization_score',
}


def load_shopping_campaigns(
    conn: duckdb.DuckDBPyConnection,
    customer_id: str,
    days: int,
    status_filter: str,
    date_filter: str = None,
    sort_by: str = 'cost',
    sort_dir: str = 'desc',
) -> List[Dict[str, Any]]:
    """
    Load shopping campaign data from ro.analytics.shopping_campaign_daily.
    24-column set matching Campaigns page. Columns not yet in schema → NULL.
    """
    _date_clause = date_filter if date_filter else f"AND snapshot_date >= CURRENT_DATE - INTERVAL '{days} days'"

    query = f"""
        SELECT
            campaign_id,
            campaign_name,
            campaign_status,
            'SHOPPING'                                                        AS channel_type,
            SUM(cost_micros) / 1000000.0                                      AS cost,
            SUM(conversions_value)                                            AS conversions_value,
            SUM(conversions)                                                  AS conversions,
            CASE WHEN SUM(cost_micros) > 0
                 THEN SUM(conversions_value) / (SUM(cost_micros) / 1000000.0)
                 ELSE NULL END                                                AS conv_value_per_cost,
            CASE WHEN SUM(conversions) > 0
                 THEN (SUM(cost_micros) / 1000000.0) / SUM(conversions)
                 ELSE NULL END                                                AS cost_per_conv,
            CASE WHEN SUM(clicks) > 0
                 THEN SUM(conversions) * 1.0 / SUM(clicks)
                 ELSE NULL END                                                AS conv_rate,
            NULL                                                              AS all_conversions,
            NULL                                                              AS cost_per_all_conv,
            NULL                                                              AS all_conv_rate,
            NULL                                                              AS all_conversions_value,
            NULL                                                              AS all_conv_value_per_cost,
            SUM(impressions)                                                  AS impressions,
            SUM(clicks)                                                       AS clicks,
            CASE WHEN SUM(clicks) > 0
                 THEN (SUM(cost_micros) / 1000000.0) / SUM(clicks)
                 ELSE NULL END                                                AS avg_cpc,
            CASE WHEN SUM(impressions) > 0
                 THEN SUM(clicks) * 1.0 / SUM(impressions)
                 ELSE NULL END                                                AS ctr,
            NULL                                                              AS search_impression_share,
            NULL                                                              AS search_top_impression_share,
            NULL                                                              AS search_absolute_top_impression_share,
            NULL                                                              AS click_share,
            NULL                                                              AS optimization_score,
            NULL                                                              AS bid_strategy_type
        FROM ro.analytics.shopping_campaign_daily
        WHERE customer_id = ?
          {_date_clause}
        GROUP BY campaign_id, campaign_name, campaign_status
        ORDER BY {sort_by} {sort_dir} NULLS LAST
    """

    try:
        rows = conn.execute(query, [customer_id]).fetchall()
        cols = [d[0] for d in conn.description]
    except Exception as e:
        print(f"[Shopping Campaigns] Query error: {e}")
        import traceback; traceback.print_exc()
        return []

    campaigns = []
    for row in rows:
        d = dict(zip(cols, row))
        status_raw = str(d.get('campaign_status') or 'UNKNOWN').upper()

        # Python-side status filter
        if status_filter == 'enabled' and status_raw != 'ENABLED':
            continue
        if status_filter == 'paused' and status_raw != 'PAUSED':
            continue

        for f in ['cost', 'conversions_value', 'conversions', 'conv_value_per_cost',
                  'cost_per_conv', 'conv_rate', 'all_conversions', 'cost_per_all_conv',
                  'all_conv_rate', 'all_conversions_value', 'all_conv_value_per_cost',
                  'impressions', 'clicks', 'avg_cpc', 'ctr',
                  'search_impression_share', 'search_top_impression_share',
                  'search_absolute_top_impression_share', 'click_share',
                  'optimization_score']:
            val = d.get(f)
            d[f] = float(val) if val is not None else None

        d['campaign_id']    = str(d.get('campaign_id', ''))
        d['campaign_name']  = str(d.get('campaign_name') or 'Unknown')
        d['status']         = status_raw
        d['channel_type']   = str(d.get('channel_type') or 'SHOPPING')
        d['bid_strategy_type'] = str(d.get('bid_strategy_type') or '') if d.get('bid_strategy_type') else None

        campaigns.append(d)

    return campaigns


def compute_campaign_metrics(campaigns: List[Dict]) -> Dict[str, Any]:
    """6-card metrics bar for Campaigns tab."""
    if not campaigns:
        return {
            'total_campaigns': 0, 'total_cost': 0.0,
            'total_conversions': 0.0, 'overall_roas': 0.0,
            'total_impressions': 0, 'total_conv_value': 0.0,
            'total_clicks': 0,
        }
    total_cost       = sum(c.get('cost') or 0 for c in campaigns)
    total_conv_value = sum(c.get('conversions_value') or 0 for c in campaigns)
    return {
        'total_campaigns':   len(campaigns),
        'total_cost':        total_cost,
        'total_conversions': sum(c.get('conversions') or 0 for c in campaigns),
        'overall_roas':      total_conv_value / total_cost if total_cost > 0 else 0.0,
        'total_impressions': int(sum(c.get('impressions') or 0 for c in campaigns)),
        'total_conv_value':  total_conv_value,
        'total_clicks':      int(sum(c.get('clicks') or 0 for c in campaigns)),
    }


# =============================================================================
# TAB 2: PRODUCTS
# =============================================================================

def load_products_from_features(
    conn: duckdb.DuckDBPyConnection,
    customer_id: str,
    days: int
) -> List[Dict]:
    """Primary: analytics.product_features_daily with windowed columns."""
    suffix = f'w{days}' if days in [7, 30, 90] else 'w30'

    query = f"""
        SELECT
            product_id,
            product_title,
            product_brand,
            product_category,
            availability,
            COALESCE(impressions_{suffix}_sum, 0)        AS impressions,
            COALESCE(clicks_{suffix}_sum, 0)             AS clicks,
            COALESCE(cost_micros_{suffix}_sum, 0)        AS cost_micros,
            COALESCE(conversions_{suffix}_sum, 0)        AS conversions,
            COALESCE(conversions_value_{suffix}_sum, 0)  AS conv_value_micros,
            COALESCE(roas_{suffix}, 0)                   AS roas,
            feed_quality_score,
            stock_out_flag,
            COALESCE(stock_out_days_w30, 0)              AS stock_out_days,
            has_price_mismatch,
            has_disapproval
        FROM analytics.product_features_daily
        WHERE customer_id = ?
          AND snapshot_date = (
              SELECT MAX(snapshot_date)
              FROM analytics.product_features_daily
              WHERE customer_id = ?
          )
        ORDER BY cost_micros_{suffix}_sum DESC NULLS LAST
        LIMIT 200
    """

    try:
        rows = conn.execute(query, [customer_id, customer_id]).fetchall()
        if not rows:
            return []
        cols = [d[0] for d in conn.description]
        products = []
        for row in rows:
            d = dict(zip(cols, row))
            cost_micros      = float(d.get('cost_micros') or 0)
            conv_value_micros = float(d.get('conv_value_micros') or 0)
            fq_raw           = d.get('feed_quality_score')
            products.append({
                'product_id':     str(d.get('product_id', '')),
                'product_title':  str(d.get('product_title') or 'Unknown'),
                'product_brand':  str(d.get('product_brand') or ''),
                'product_category': str(d.get('product_category') or ''),
                'availability':   str(d.get('availability') or 'UNKNOWN').upper(),
                'impressions':    int(d.get('impressions') or 0),
                'clicks':         int(d.get('clicks') or 0),
                'cost':           cost_micros / 1_000_000,
                'conversions':    float(d.get('conversions') or 0),
                'conv_value':     conv_value_micros / 1_000_000,
                'roas':           float(d.get('roas') or 0),
                'feed_quality':   float(fq_raw) * 100 if fq_raw is not None else None,
                'stock_out_flag': bool(d.get('stock_out_flag') or False),
                'stock_out_days': int(d.get('stock_out_days') or 0),
                'price_mismatch': bool(d.get('has_price_mismatch') or False),
                'disapproved':    bool(d.get('has_disapproval') or False),
            })
        return products
    except Exception as e:
        print(f"[Shopping Products] product_features_daily error: {e}")
        return []


def load_products_from_raw(
    conn: duckdb.DuckDBPyConnection,
    customer_id: str,
    days: int
) -> List[Dict]:
    """Fallback: raw_product_performance_daily — no derived columns."""
    query = f"""
        SELECT
            product_id,
            product_title,
            product_brand,
            product_category,
            availability,
            SUM(impressions)                AS impressions,
            SUM(clicks)                     AS clicks,
            SUM(cost_micros) / 1000000.0    AS cost,
            SUM(conversions)                AS conversions,
            SUM(conversions_value)          AS conv_value,
            CASE WHEN SUM(cost_micros) > 0
                 THEN SUM(conversions_value) / (SUM(cost_micros) / 1000000.0)
                 ELSE 0 END                 AS roas
        FROM raw_product_performance_daily
        WHERE customer_id = ?
          AND snapshot_date >= CURRENT_DATE - INTERVAL '{days} days'
        GROUP BY product_id, product_title, product_brand, product_category, availability
        ORDER BY cost DESC
        LIMIT 200
    """
    try:
        rows = conn.execute(query, [customer_id]).fetchall()
        cols = [d[0] for d in conn.description]
        products = []
        for row in rows:
            d = dict(zip(cols, row))
            products.append({
                'product_id':     str(d.get('product_id', '')),
                'product_title':  str(d.get('product_title') or 'Unknown'),
                'product_brand':  str(d.get('product_brand') or ''),
                'product_category': str(d.get('product_category') or ''),
                'availability':   str(d.get('availability') or 'UNKNOWN').upper(),
                'impressions':    int(d.get('impressions') or 0),
                'clicks':         int(d.get('clicks') or 0),
                'cost':           float(d.get('cost') or 0),
                'conversions':    float(d.get('conversions') or 0),
                'conv_value':     float(d.get('conv_value') or 0),
                'roas':           float(d.get('roas') or 0),
                'feed_quality':   None,
                'stock_out_flag': False,
                'stock_out_days': 0,
                'price_mismatch': False,
                'disapproved':    False,
            })
        return products
    except Exception as e:
        print(f"[Shopping Products] raw fallback error: {e}")
        return []


def load_products(
    conn: duckdb.DuckDBPyConnection,
    customer_id: str,
    days: int,
    availability_filter: str
) -> Tuple[List[Dict], bool]:
    """
    Load products — features table first, raw fallback if empty.
    Returns (products, using_fallback).
    """
    products = load_products_from_features(conn, customer_id, days)
    using_fallback = False

    if not products:
        print("[Shopping Products] product_features_daily empty — using raw fallback")
        products = load_products_from_raw(conn, customer_id, days)
        using_fallback = True

    # Availability filter (Python-side)
    if availability_filter == 'in_stock':
        products = [p for p in products if p['availability'] == 'IN_STOCK']
    elif availability_filter == 'out_of_stock':
        products = [p for p in products if p['availability'] == 'OUT_OF_STOCK']
    elif availability_filter == 'preorder':
        products = [p for p in products if p['availability'] == 'PREORDER']

    return products, using_fallback


def compute_product_metrics(products: List[Dict]) -> Dict[str, Any]:
    """6-card metrics bar for Products tab."""
    if not products:
        return {
            'total_products': 0, 'total_cost': 0.0,
            'total_conversions': 0.0, 'overall_roas': 0.0,
            'out_of_stock_count': 0, 'feed_issues_count': 0,
        }
    total_cost       = sum(p['cost'] for p in products)
    total_conv_value = sum(p['conv_value'] for p in products)
    return {
        'total_products':    len(products),
        'total_cost':        total_cost,
        'total_conversions': sum(p['conversions'] for p in products),
        'overall_roas':      total_conv_value / total_cost if total_cost > 0 else 0.0,
        'out_of_stock_count': sum(1 for p in products if p['availability'] == 'OUT_OF_STOCK'),
        'feed_issues_count': sum(1 for p in products if p['price_mismatch'] or p['disapproved']),
    }


# =============================================================================
# TAB 3: FEED QUALITY
# =============================================================================

def load_feed_quality(
    conn: duckdb.DuckDBPyConnection,
    customer_id: str
) -> Tuple[Optional[Dict], List[Dict]]:
    """
    Load feed quality data. Returns (quality_stats or None, issues_list).
    None means no data — template shows clean empty state.
    """
    try:
        count_row = conn.execute(
            "SELECT COUNT(*) FROM raw_product_feed_quality WHERE customer_id = ?",
            [customer_id]
        ).fetchone()

        if not count_row or count_row[0] == 0:
            return None, []

        # Approval status counts
        stats_rows = conn.execute("""
            SELECT approval_status, COUNT(*) AS cnt
            FROM raw_product_feed_quality
            WHERE customer_id = ?
            GROUP BY approval_status
        """, [customer_id]).fetchall()

        status_counts     = {r[0]: r[1] for r in stats_rows}
        total             = sum(status_counts.values())
        approved_count    = status_counts.get('APPROVED', 0)
        disapproved_count = status_counts.get('DISAPPROVED', 0)
        pending_count     = status_counts.get('PENDING', 0)

        # Price mismatch count
        mismatch_row = conn.execute("""
            SELECT COUNT(*) FROM raw_product_feed_quality
            WHERE customer_id = ? AND price_mismatch = TRUE
        """, [customer_id]).fetchone()
        mismatch_count = int(mismatch_row[0]) if mismatch_row else 0

        # Top disapproval reasons
        try:
            reasons_rows = conn.execute("""
                SELECT reason, COUNT(*) AS cnt
                FROM (
                    SELECT UNNEST(disapproval_reasons) AS reason
                    FROM raw_product_feed_quality
                    WHERE customer_id = ?
                      AND approval_status = 'DISAPPROVED'
                      AND disapproval_reasons IS NOT NULL
                )
                GROUP BY reason
                ORDER BY cnt DESC
                LIMIT 5
            """, [customer_id]).fetchall()
            top_reasons = [{'reason': r[0], 'count': r[1]} for r in reasons_rows if r[0]]
        except Exception:
            top_reasons = []

        # Feed freshness — MAX(ingested_at)
        freshness_row = conn.execute(
            "SELECT MAX(ingested_at) FROM raw_product_feed_quality WHERE customer_id = ?",
            [customer_id]
        ).fetchone()

        last_sync        = None
        hours_since_sync = None
        freshness_status = 'unknown'

        if freshness_row and freshness_row[0]:
            raw_dt = freshness_row[0]
            if hasattr(raw_dt, 'tzinfo'):
                last_sync_dt = raw_dt.replace(tzinfo=timezone.utc) if raw_dt.tzinfo is None else raw_dt
            else:
                last_sync_dt = datetime.fromisoformat(str(raw_dt)).replace(tzinfo=timezone.utc)

            now_utc          = datetime.now(timezone.utc)
            hours_since_sync = (now_utc - last_sync_dt).total_seconds() / 3600
            last_sync        = last_sync_dt.strftime('%Y-%m-%d %H:%M UTC')

            if hours_since_sync < 24:
                freshness_status = 'fresh'
            elif hours_since_sync < 48:
                freshness_status = 'stale'
            else:
                freshness_status = 'old'

        quality_stats = {
            'total':             total,
            'approved_count':    approved_count,
            'disapproved_count': disapproved_count,
            'pending_count':     pending_count,
            'pct_approved':      (approved_count / total * 100) if total > 0 else 0,
            'pct_disapproved':   (disapproved_count / total * 100) if total > 0 else 0,
            'mismatch_count':    mismatch_count,
            'pct_mismatch':      (mismatch_count / total * 100) if total > 0 else 0,
            'top_reasons':       top_reasons,
            'last_sync':         last_sync,
            'hours_since_sync':  round(hours_since_sync, 1) if hours_since_sync is not None else None,
            'freshness_status':  freshness_status,
        }

        # Issues table
        issues_rows = conn.execute("""
            SELECT product_id, approval_status, price_mismatch, disapproval_reasons
            FROM raw_product_feed_quality
            WHERE customer_id = ?
              AND (approval_status != 'APPROVED' OR price_mismatch = TRUE)
            ORDER BY approval_status DESC
            LIMIT 100
        """, [customer_id]).fetchall()

        issues_list = []
        for row in issues_rows:
            tags = []
            if row[1] == 'DISAPPROVED':
                tags.append('Disapproved')
            elif row[1] == 'PENDING':
                tags.append('Pending Review')
            if row[2]:
                tags.append('Price Mismatch')
            issues_list.append({
                'product_id':          str(row[0]),
                'approval_status':     str(row[1]),
                'price_mismatch':      bool(row[2]),
                'disapproval_reasons': row[3] if row[3] else [],
                'issue_tags':          tags,
            })

        return quality_stats, issues_list

    except Exception as e:
        print(f"[Shopping Feed Quality] Error: {e}")
        import traceback; traceback.print_exc()
        return None, []


# =============================================================================
# PAGINATION
# =============================================================================

def apply_pagination(
    items: List[Dict],
    page: int,
    per_page: int
) -> Tuple[List[Dict], int, int]:
    """Slice list for current page. Returns (paginated, total, total_pages)."""
    total       = len(items)
    total_pages = max(1, (total + per_page - 1) // per_page)
    page        = max(1, min(page, total_pages))
    start       = (page - 1) * per_page
    return items[start:start + per_page], total, total_pages


# =============================================================================
# ROUTE
# =============================================================================



# ==================== Chat 23 M2: Metrics Cards ====================

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


def _fmt_sh(value, fmt):
    if value is None:
        return '—'
    if fmt == 'count_label':
        return str(value)
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


def _card_sh(label, value, prev, sparkline, fmt, invert=False, card_type='financial', sub_label=None):
    """Shopping cards with period-over-period comparison."""
    return {
        'label': label,
        'value_display': _fmt_sh(value, fmt),
        'change_pct': _calculate_change_pct(value, prev),
        'sparkline_data': sparkline,
        'format_type': fmt,
        'invert_colours': invert,
        'card_type': card_type,
        'sub_label': sub_label,
    }


def _blank_sh(card_type='financial'):
    return {
        'label': '', 'value_display': '', 'change_pct': None,
        'sparkline_data': None, 'format_type': 'blank',
        'invert_colours': False, 'card_type': card_type, 'sub_label': None,
    }


def build_campaign_metrics_cards(
    conn: duckdb.DuckDBPyConnection,
    customer_id: str,
    active_days: int,
    date_from: Optional[str],
    date_to: Optional[str],
) -> Tuple[List[Dict], List[Dict]]:
    """
    Build financial_cards and actions_cards for Shopping Campaigns.
    
    Queries ro.analytics.shopping_campaign_daily for current, previous, and sparkline data.
    Returns tuple of (financial_cards, actions_cards).
    """
    # Build date filters for current and previous periods
    current_filter, prev_filter = _build_date_filters(active_days, date_from, date_to)
    
    # ── Query 1: Current period summary from shopping_campaign_daily ──
    try:
        summary = conn.execute(f"""
            SELECT
                SUM(cost_micros) / 1000000.0                                      AS cost,
                SUM(conversions_value)                                             AS conv_value,
                SUM(conversions_value) / NULLIF(SUM(cost_micros) / 1000000.0, 0)  AS roas,
                SUM(conversions)                                                   AS conversions,
                (SUM(cost_micros) / 1000000.0) / NULLIF(SUM(conversions), 0)      AS cpa,
                SUM(clicks) * 1.0 / NULLIF(SUM(conversions), 0)                   AS cvr,
                SUM(impressions)                                                   AS impressions,
                SUM(clicks)                                                        AS clicks,
                (SUM(cost_micros) / 1000000.0) / NULLIF(SUM(clicks), 0)           AS cpc,
                SUM(clicks) * 1.0 / NULLIF(SUM(impressions), 0)                   AS ctr
            FROM ro.analytics.shopping_campaign_daily
            WHERE customer_id = ?
              {current_filter}
        """, [customer_id]).fetchone()
    except Exception as e:
        print(f"[Shopping M2] Current period query error: {e}")
        summary = None
    
    # ── Query 2: Previous period summary from shopping_campaign_daily ──
    try:
        prev_summary = conn.execute(f"""
            SELECT
                SUM(cost_micros) / 1000000.0                                      AS cost,
                SUM(conversions_value)                                             AS conv_value,
                SUM(conversions_value) / NULLIF(SUM(cost_micros) / 1000000.0, 0)  AS roas,
                SUM(conversions)                                                   AS conversions,
                (SUM(cost_micros) / 1000000.0) / NULLIF(SUM(conversions), 0)      AS cpa,
                SUM(clicks) * 1.0 / NULLIF(SUM(conversions), 0)                   AS cvr,
                SUM(impressions)                                                   AS impressions,
                SUM(clicks)                                                        AS clicks,
                (SUM(cost_micros) / 1000000.0) / NULLIF(SUM(clicks), 0)           AS cpc,
                SUM(clicks) * 1.0 / NULLIF(SUM(impressions), 0)                   AS ctr
            FROM ro.analytics.shopping_campaign_daily
            WHERE customer_id = ?
              {prev_filter}
        """, [customer_id]).fetchone()
    except Exception as e:
        print(f"[Shopping M2] Previous period query error: {e}")
        prev_summary = None
    
    # ── Query 3: Daily sparkline data from shopping_campaign_daily ──
    try:
        spark_rows = conn.execute(f"""
            SELECT
                snapshot_date,
                SUM(cost_micros) / 1000000.0                                      AS cost,
                SUM(conversions_value)                                             AS conv_value,
                SUM(conversions_value) / NULLIF(SUM(cost_micros) / 1000000.0, 0)  AS roas,
                SUM(conversions)                                                   AS conversions,
                (SUM(cost_micros) / 1000000.0) / NULLIF(SUM(conversions), 0)      AS cpa,
                SUM(clicks) * 1.0 / NULLIF(SUM(conversions), 0)                   AS cvr,
                SUM(impressions)                                                   AS impressions,
                SUM(clicks)                                                        AS clicks,
                (SUM(cost_micros) / 1000000.0) / NULLIF(SUM(clicks), 0)           AS cpc,
                SUM(clicks) * 1.0 / NULLIF(SUM(impressions), 0)                   AS ctr
            FROM ro.analytics.shopping_campaign_daily
            WHERE customer_id = ?
              {current_filter}
            GROUP BY snapshot_date
            ORDER BY snapshot_date ASC
        """, [customer_id]).fetchall()
    except Exception as e:
        print(f"[Shopping M2] Sparkline query error: {e}")
        spark_rows = []
    
    def _v(row, i): return float(row[i]) if row and row[i] is not None else None
    def pct(val): return val * 100 if val is not None else None
    
    # Current period values
    c = [_v(summary, i) for i in range(10)] if summary else [None] * 10
    
    # Previous period values
    p = [_v(prev_summary, i) for i in range(10)] if prev_summary else [None] * 10
    
    # Build sparkline arrays
    def _spark(col_idx, scale=1.0):
        return [float(r[col_idx]) * scale if r[col_idx] is not None else 0.0 for r in spark_rows]
    
    financial_cards = [
        _card_sh('Cost',         c[0],        p[0],        _spark(1),        'currency',   invert=True),
        _card_sh('Revenue',      c[1],        p[1],        _spark(2),        'currency'),
        _card_sh('ROAS',         c[2],        p[2],        _spark(3),        'ratio'),
        _blank_sh('financial'),
        _card_sh('Conversions',  c[3],        p[3],        _spark(4),        'number'),
        _card_sh('Cost / Conv',  c[4],        p[4],        _spark(5),        'currency',   invert=True),
        _card_sh('Conv Rate',    pct(c[5]),   pct(p[5]),   _spark(6, 100.0), 'percentage'),
        _blank_sh('financial'),
    ]
    
    actions_cards = [
        _card_sh('Impressions',  c[6],        p[6],        _spark(7),         'number',     card_type='actions'),
        _card_sh('Clicks',       c[7],        p[7],        _spark(8),         'number',     card_type='actions'),
        _card_sh('Avg CPC',      c[8],        p[8],        _spark(9),         'currency',   card_type='actions'),
        _card_sh('Avg CTR',      pct(c[9]),   pct(p[9]),   _spark(10, 100.0), 'percentage', card_type='actions'),
        _blank_sh('actions'),
        _blank_sh('actions'),
        _blank_sh('actions'),
        _blank_sh('actions'),
    ]
    
    return financial_cards, actions_cards


def build_product_metrics_cards(pm):
    """
    Product metrics cards - incomplete (shopping_product_daily table doesn't exist yet).
    Uses None for prev (no period comparison) and [] for sparklines (no daily data).
    """
    total_cost    = pm.get('total_cost', 0) or 0
    total_convs   = pm.get('total_conversions', 0) or 0
    roas          = pm.get('overall_roas', 0) or 0
    oos           = pm.get('out_of_stock_count', 0) or 0
    feed_issues   = pm.get('feed_issues_count', 0) or 0
    total_prods   = pm.get('total_products', 0) or 0
    oos_sub       = 'Needs attention' if oos > 0 else 'All in stock'
    issues_sub    = 'Price mismatch/disapproved' if feed_issues > 0 else 'No issues'
    
    # No prev or sparkline data - product_daily table doesn't exist
    financial_cards = [
        _card_sh('Cost',          total_cost,  None, [], 'currency',  invert=True),
        _card_sh('ROAS',          roas,        None, [], 'ratio'),
        _blank_sh('financial'),
        _card_sh('Out of Stock',  oos,         None, [], 'number',    invert=True, sub_label=oos_sub),
        _card_sh('Conversions',   total_convs, None, [], 'number'),
        _blank_sh('financial'),
        _blank_sh('financial'),
        _blank_sh('financial'),
    ]
    actions_cards = [
        _card_sh('Products',    total_prods,  None, [], 'number',  card_type='actions'),
        _card_sh('Feed Issues', feed_issues,  None, [], 'number',  card_type='actions', invert=True, sub_label=issues_sub),
        _blank_sh('actions'),
        _blank_sh('actions'),
        _blank_sh('actions'),
        _blank_sh('actions'),
        _blank_sh('actions'),
        _blank_sh('actions'),
    ]
    return financial_cards, actions_cards


# ==================== Chat 24 M3: Chart Data Builder ====================

def _build_shopping_chart_data(conn, customer_id: str, active_days: int, date_from=None, date_to=None) -> dict:
    """
    Chart data for Shopping page (Campaigns tab). Uses ro.analytics.campaign_daily (account-level).
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
        print(f"[Shopping M3] chart data error: {e}")
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


@bp.route('/shopping')
@login_required
def shopping():
    """
    Shopping dashboard — Bootstrap 5 redesign (Chat 21g).

    URL Parameters:
        days:         7 / 30 / 90           (default 30)
        page:         page number            (default 1)
        per_page:     10 / 25 / 50 / 100     (default 25)
        status:       all / enabled / paused  (Campaigns tab)
        availability: all / in_stock / out_of_stock / preorder  (Products tab)
        tab:          campaigns / products / feed_quality / rules
    """
    # Get date range from session (default 30d).
    # Campaigns tab supports custom date ranges (raw SQL).
    # Products tab uses windowed columns — custom range falls back to w30.
    active_days, date_from, date_to = get_date_range_from_session()
    if date_from and date_to:
        days = 0  # signals custom range to campaign SQL builder
    elif active_days in [7, 30, 90]:
        days = active_days
    else:
        days = 30

    page         = request.args.get('page',         default=1,     type=int)
    per_page     = request.args.get('per_page',     default=25,    type=int)
    status       = request.args.get('status',       default='all', type=str).lower()
    availability = request.args.get('availability', default='all', type=str).lower()
    active_tab   = request.args.get('tab',          default='campaigns', type=str).lower()
    sort_by      = request.args.get('sort_by',      default='cost', type=str)
    sort_dir     = request.args.get('sort_dir',     default='desc', type=str)

    if per_page not in [10, 25, 50, 100]:                              per_page = 25
    if page     < 1:                                                   page     = 1
    if status   not in ['all', 'enabled', 'paused']:                   status   = 'all'
    if availability not in ['all', 'in_stock', 'out_of_stock', 'preorder']: availability = 'all'
    if active_tab not in ['campaigns', 'products', 'feed_quality', 'rules']: active_tab = 'campaigns'
    if sort_by  not in ALLOWED_SHOPPING_SORT:                          sort_by  = 'cost'
    if sort_dir not in ['asc', 'desc']:                                sort_dir = 'desc'

    # Days value for Products tab (windowed cols only support 7/30/90)
    products_days = days if days in [7, 30, 90] else 30

    _empty_ctx = dict(
        campaigns=[], campaign_metrics=compute_campaign_metrics([]),
        total_campaigns=0, total_pages_campaigns=1,
        products=[], product_metrics=compute_product_metrics([]),
        total_products=0, total_pages_products=1,
        using_fallback=False,
        quality_stats=None, feed_issues=[],
        rules=[], rule_counts={},
        days=days, active_days=active_days, date_from=date_from, date_to=date_to,
        page=page, per_page=per_page,
        status=status, availability=availability, active_tab=active_tab,
        sort_by=sort_by, sort_dir=sort_dir,
        saved_columns=session.get('shopping_columns', None),
    )

    try:
        config, clients, current_client_path = get_page_context()
        conn = get_db_connection(config)
    except Exception as e:
        return render_template(
            'shopping_new.html',
            error=str(e),
            client_name='Error',
            available_clients=[],
            current_client_config=None,
            **_empty_ctx,
        )

    # ── Campaigns ──
    try:
        # Campaigns tab: build date filter (supports custom range)
        if date_from and date_to:
            _camp_days = 30  # placeholder — overridden by date_filter below
            _camp_date_filter = f"AND s.snapshot_date >= '{date_from}' AND s.snapshot_date <= '{date_to}'"
        else:
            _camp_days = days
            _camp_date_filter = None
        all_campaigns    = load_shopping_campaigns(conn, config.customer_id, _camp_days, status, _camp_date_filter, sort_by, sort_dir)
        campaign_metrics = compute_campaign_metrics(all_campaigns)
        campaigns_pg, total_campaigns, total_pages_campaigns = apply_pagination(
            all_campaigns, page, per_page
        )
    except Exception as e:
        print(f"[Shopping] Campaigns error: {e}")
        import traceback; traceback.print_exc()
        all_campaigns, campaigns_pg = [], []
        campaign_metrics = compute_campaign_metrics([])
        total_campaigns, total_pages_campaigns = 0, 1

    # ── Products ──
    try:
        all_products, using_fallback = load_products(
            conn, config.customer_id, products_days, availability
        )
        product_metrics = compute_product_metrics(all_products)
        products_pg, total_products, total_pages_products = apply_pagination(
            all_products, page, per_page
        )
    except Exception as e:
        print(f"[Shopping] Products error: {e}")
        import traceback; traceback.print_exc()
        all_products, products_pg = [], []
        product_metrics = compute_product_metrics([])
        total_products, total_pages_products = 0, 1
        using_fallback = False

    # ── Feed Quality ──
    try:
        quality_stats, feed_issues = load_feed_quality(conn, config.customer_id)
    except Exception as e:
        print(f"[Shopping] Feed quality error: {e}")
        quality_stats, feed_issues = None, []

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
        entity_type='campaign',
        campaign_type='SHOPPING'
    )

    # M2: Build metrics cards (MUST be before conn.close())
    camp_financial_cards, camp_actions_cards = build_campaign_metrics_cards(
        conn, config.customer_id, active_days, date_from, date_to
    )
    prod_financial_cards, prod_actions_cards = build_product_metrics_cards(product_metrics)
    metrics_collapsed = get_metrics_collapsed('shopping')

    conn.close()

    # ── Rules ──
    try:
        rules       = get_rules_for_page('shopping', customer_id=config.customer_id)
        rule_counts = count_rules_by_category(rules)
    except Exception as e:
        print(f"[Shopping] Rules error: {e}")
        rules, rule_counts = [], {}

    print(
        f"[Shopping] campaigns={len(all_campaigns)}, "
        f"products={len(all_products)} (fallback={using_fallback}), "
        f"feed_issues={len(feed_issues)}, rules={len(rules)}"
    )

    return render_template(
        'shopping_new.html',
        client_name=config.client_name,
        available_clients=clients,
        current_client_config=current_client_path,
        error=None,
        # Tab 1
        campaigns=campaigns_pg,
        campaign_metrics=campaign_metrics,
        total_campaigns=total_campaigns,
        total_pages_campaigns=total_pages_campaigns,
        # Tab 2
        products=products_pg,
        product_metrics=product_metrics,
        total_products=total_products,
        total_pages_products=total_pages_products,
        using_fallback=using_fallback,
        # Tab 3
        quality_stats=quality_stats,
        feed_issues=feed_issues,
        # Tab 4
        rules=rules,
        rules_config=load_rules(),
        rule_counts=rule_counts,
        # Filters / state
        days=days,
        active_days=active_days,
        date_from=date_from,
        date_to=date_to,
        page=page,
        per_page=per_page,
        status=status,
        availability=availability,
        active_tab=active_tab,
        sort_by=sort_by,
        sort_dir=sort_dir,
        # M2: Metrics cards
        camp_financial_cards=camp_financial_cards,
        camp_actions_cards=camp_actions_cards,
        prod_financial_cards=prod_financial_cards,
        prod_actions_cards=prod_actions_cards,
        metrics_collapsed=metrics_collapsed,
        # M3: Chart
        chart_data=chart_data,
        active_metrics=get_chart_metrics('shopping'),
        # M4: Column persistence
        saved_columns=session.get('shopping_columns', None),
    )


@bp.route("/shopping/save-columns", methods=['POST'])
@login_required
def save_columns():
    """
    POST /shopping/save-columns
    Body JSON: { visible: ["cost", "conv-value", ...] }
    Stores visible column list in session['shopping_columns'].
    """
    data = request.get_json(silent=True) or {}
    visible = data.get('visible', [])

    if not isinstance(visible, list):
        return jsonify({'success': False, 'error': 'visible must be a list'}), 400

    session['shopping_columns'] = visible
    return jsonify({'success': True, 'columns': visible})
