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

from flask import Blueprint, render_template, request
from act_dashboard.auth import login_required
from act_dashboard.routes.shared import get_page_context, get_db_connection, get_date_range_from_session
from act_dashboard.routes.rule_helpers import get_rules_for_page, count_rules_by_category
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple, Optional
import duckdb

bp = Blueprint('shopping', __name__)


# =============================================================================
# TAB 1: CAMPAIGNS
# =============================================================================

def load_shopping_campaigns(
    conn: duckdb.DuckDBPyConnection,
    customer_id: str,
    days: int,
    status_filter: str,
    date_filter: str = None,
) -> List[Dict[str, Any]]:
    """
    Load shopping campaign data from raw_shopping_campaign_daily.
    LEFT JOINs analytics.campaign_daily to get campaign_status.
    Accepts optional date_filter string for custom date ranges.
    """
    _date_clause = date_filter if date_filter else f"AND s.snapshot_date >= CURRENT_DATE - INTERVAL '{days} days'"
    query = f"""
        SELECT
            s.campaign_id,
            s.campaign_name,
            s.campaign_priority,
            s.feed_label,
            COALESCE(cd.campaign_status, 'UNKNOWN')    AS campaign_status,
            0.0                                         AS daily_budget,
            SUM(s.impressions)                          AS impressions,
            SUM(s.clicks)                               AS clicks,
            SUM(s.cost_micros) / 1000000.0              AS cost,
            SUM(s.conversions)                          AS conversions,
            SUM(s.conversions_value) / 1000000.0        AS conv_value
        FROM raw_shopping_campaign_daily s
        LEFT JOIN (
            SELECT campaign_id, campaign_status
            FROM analytics.campaign_daily
            WHERE customer_id = ?
            QUALIFY ROW_NUMBER() OVER (
                PARTITION BY campaign_id ORDER BY snapshot_date DESC
            ) = 1
        ) cd ON cd.campaign_id = s.campaign_id
        WHERE s.customer_id = ?
          {{_date_clause}}
        GROUP BY
            s.campaign_id, s.campaign_name, s.campaign_priority,
            s.feed_label, cd.campaign_status
        ORDER BY cost DESC
    """.format(_date_clause=_date_clause)

    rows = None
    cols = None

    try:
        rows = conn.execute(query, [customer_id, customer_id]).fetchall()
        cols = [d[0] for d in conn.description]
    except Exception as e:
        print(f"[Shopping Campaigns] JOIN query error: {e} — trying fallback")
        try:
            fallback_query = f"""
                SELECT
                    campaign_id,
                    campaign_name,
                    campaign_priority,
                    feed_label,
                    'UNKNOWN'                           AS campaign_status,
                    0.0                                 AS daily_budget,
                    SUM(impressions)                    AS impressions,
                    SUM(clicks)                         AS clicks,
                    SUM(cost_micros) / 1000000.0        AS cost,
                    SUM(conversions)                    AS conversions,
                    SUM(conversions_value) / 1000000.0  AS conv_value
                FROM raw_shopping_campaign_daily
                WHERE customer_id = ?
                  AND (snapshot_date >= CURRENT_DATE - INTERVAL '30 days')
                GROUP BY campaign_id, campaign_name, campaign_priority, feed_label
                ORDER BY cost DESC
            """
            rows = conn.execute(fallback_query, [customer_id]).fetchall()
            cols = [
                'campaign_id', 'campaign_name', 'campaign_priority', 'feed_label',
                'campaign_status', 'daily_budget',
                'impressions', 'clicks', 'cost', 'conversions', 'conv_value'
            ]
        except Exception as e2:
            print(f"[Shopping Campaigns] Fallback query error: {e2}")
            return []

    if rows is None:
        return []

    priority_map = {0: 'Low', 1: 'Medium', 2: 'High'}

    campaigns = []
    for row in rows:
        d = dict(zip(cols, row))
        cost       = float(d.get('cost') or 0)
        conv_value = float(d.get('conv_value') or 0)
        roas       = conv_value / cost if cost > 0 else 0.0
        priority   = int(d.get('campaign_priority') or 0)
        status_raw = str(d.get('campaign_status') or 'UNKNOWN').upper()

        campaigns.append({
            'campaign_id':   str(d.get('campaign_id', '')),
            'campaign_name': str(d.get('campaign_name') or 'Unknown'),
            'priority':      priority_map.get(priority, 'Unknown'),
            'priority_num':  priority,
            'feed_label':    str(d.get('feed_label') or 'None'),
            'status':        status_raw,
            'daily_budget':  float(d.get('daily_budget') or 0),
            'impressions':   int(d.get('impressions') or 0),
            'clicks':        int(d.get('clicks') or 0),
            'cost':          cost,
            'conversions':   float(d.get('conversions') or 0),
            'conv_value':    conv_value,
            'roas':          roas,
        })

    # Python-side status filter
    if status_filter == 'enabled':
        campaigns = [c for c in campaigns if c['status'] == 'ENABLED']
    elif status_filter == 'paused':
        campaigns = [c for c in campaigns if c['status'] == 'PAUSED']

    return campaigns


def compute_campaign_metrics(campaigns: List[Dict]) -> Dict[str, Any]:
    """6-card metrics bar for Campaigns tab."""
    if not campaigns:
        return {
            'total_campaigns': 0, 'total_cost': 0.0,
            'total_conversions': 0.0, 'overall_roas': 0.0,
            'total_impressions': 0, 'total_conv_value': 0.0,
        }
    total_cost       = sum(c['cost'] for c in campaigns)
    total_conv_value = sum(c['conv_value'] for c in campaigns)
    return {
        'total_campaigns':   len(campaigns),
        'total_cost':        total_cost,
        'total_conversions': sum(c['conversions'] for c in campaigns),
        'overall_roas':      total_conv_value / total_cost if total_cost > 0 else 0.0,
        'total_impressions': sum(c['impressions'] for c in campaigns),
        'total_conv_value':  total_conv_value,
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

    if per_page not in [10, 25, 50, 100]:                              per_page = 25
    if page     < 1:                                                   page     = 1
    if status   not in ['all', 'enabled', 'paused']:                   status   = 'all'
    if availability not in ['all', 'in_stock', 'out_of_stock', 'preorder']: availability = 'all'
    if active_tab not in ['campaigns', 'products', 'feed_quality', 'rules']: active_tab = 'campaigns'

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
        all_campaigns    = load_shopping_campaigns(conn, config.customer_id, _camp_days, status, _camp_date_filter)
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
    )
