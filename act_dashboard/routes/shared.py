"""
Shared helper functions used across dashboard routes.
"""

from flask import session, current_app, request, jsonify, Blueprint
from act_dashboard.config import DashboardConfig
from google.ads.googleads.client import GoogleAdsClient
from pathlib import Path
import duckdb
import re
from typing import Tuple, List, Dict, Any


def get_current_config():
    """
    Get the current client config based on session.

    Returns:
        DashboardConfig instance for current client
    """
    # Get config path from session or use default
    config_path = session.get("current_client_config")

    if not config_path:
        # Use default client
        config_path = current_app.config.get("DEFAULT_CLIENT")
        if config_path:
            session["current_client_config"] = config_path

    if not config_path:
        raise ValueError("No client configuration available")

    return DashboardConfig(config_path)


def get_available_clients():
    """Get list of available clients for switcher."""
    return current_app.config.get("AVAILABLE_CLIENTS", [])


def get_google_ads_client(config):
    """
    Initialize Google Ads API client for the current config.
    
    Args:
        config: DashboardConfig instance
        
    Returns:
        GoogleAdsClient instance
    """
    # Path to google-ads.yaml (in secrets folder)
    google_ads_yaml = Path(__file__).parent.parent / "secrets" / "google-ads.yaml"
    
    if not google_ads_yaml.exists():
        raise FileNotFoundError(f"Google Ads config not found at {google_ads_yaml}")
    
    return GoogleAdsClient.load_from_storage(str(google_ads_yaml))


# ==================== Phase 2a: Extracted Helper Functions ====================


def get_page_context() -> Tuple[DashboardConfig, List, str]:
    """
    Get common page context (config, clients, current_client_path).
    
    Returns:
        Tuple of (config, available_clients, current_client_path)
    """
    config = get_current_config()
    clients = get_available_clients()
    current_client_path = session.get("current_client_config")
    return config, clients, current_client_path


def get_db_connection(config: DashboardConfig, read_only: bool = False):
    """
    Get DuckDB connection with readonly database attached.
    
    Args:
        config: DashboardConfig instance
        read_only: If True, open main DB as read-only
        
    Returns:
        DuckDB connection with readonly DB attached as 'ro'
    """
    conn = duckdb.connect(config.db_path, read_only=read_only)
    
    # Try to attach readonly database
    ro_path = config.db_path.replace("warehouse.duckdb", "warehouse_readonly.duckdb")
    try:
        conn.execute(f"ATTACH '{ro_path}' AS ro (READ_ONLY);")
    except Exception:
        pass  # Already attached or not available
    
    return conn


def build_autopilot_config(current_client_path: str = None):
    """
    Build AutopilotConfig from client config file.
    
    Args:
        current_client_path: Path to client YAML config (uses session default if None)
        
    Returns:
        AutopilotConfig instance
    """
    from act_lighthouse.config import load_client_config
    from act_autopilot.models import AutopilotConfig
    
    if not current_client_path:
        current_client_path = session.get("current_client_config") or current_app.config.get("DEFAULT_CLIENT")
    
    lh_cfg = load_client_config(current_client_path)
    raw = lh_cfg.raw or {}
    targets = raw.get("targets", {})
    
    return AutopilotConfig(
        customer_id=lh_cfg.customer_id,
        automation_mode=raw.get("automation_mode", "suggest"),
        risk_tolerance=raw.get("risk_tolerance", "conservative"),
        daily_spend_cap=lh_cfg.spend_caps.daily or 0,
        monthly_spend_cap=lh_cfg.spend_caps.monthly or 0,
        brand_is_protected=False,
        protected_entities=[],
        client_name=lh_cfg.client_id,
        client_type=lh_cfg.client_type or "ecom",
        primary_kpi=lh_cfg.primary_kpi or "roas",
        target_roas=targets.get("target_roas"),
        target_cpa=targets.get("target_cpa", 25),
    )


def recommendation_to_dict(rec, index: int = None) -> Dict[str, Any]:
    """
    Convert Recommendation object to dictionary.
    
    Standardized conversion used across keywords, ads, shopping routes.
    Uses getattr() with defaults for optional attributes.
    
    Args:
        rec: Recommendation object
        index: Optional index for 'id' field
        
    Returns:
        Dictionary representation of recommendation
    """
    result = {
        'rule_id': rec.rule_id,
        'rule_name': rec.rule_name,
        'entity_type': rec.entity_type,
        'entity_id': rec.entity_id,
        'action_type': rec.action_type,
        'risk_tier': rec.risk_tier,
        'confidence': getattr(rec, 'confidence', None) or 0.0,
        'current_value': getattr(rec, 'current_value', None),
        'recommended_value': getattr(rec, 'recommended_value', None),
        'change_pct': getattr(rec, 'change_pct', None),
        'rationale': getattr(rec, 'rationale', None) or '',
        'campaign_name': getattr(rec, 'campaign_name', None) or '',
        'blocked': getattr(rec, 'blocked', False),
        'block_reason': getattr(rec, 'block_reason', None) or '',
        'priority': getattr(rec, 'priority', 50),
        'constitution_refs': getattr(rec, 'constitution_refs', None) or [],
        'guardrails_checked': getattr(rec, 'guardrails_checked', None) or [],
        'evidence': getattr(rec, 'evidence', None) or {},
        'triggering_diagnosis': getattr(rec, 'triggering_diagnosis', None) or '',
        'triggering_confidence': getattr(rec, 'triggering_confidence', None) or 0.0,
        'expected_impact': getattr(rec, 'expected_impact', None) or '',
    }
    
    # Add index if provided
    if index is not None:
        result['id'] = index
    
    # Add ad_group_name if present (for ads)
    if hasattr(rec, 'ad_group_name'):
        result['ad_group_name'] = getattr(rec, 'ad_group_name', None) or ''
    
    return result


def cache_recommendations(page_name: str, recommendations: List[Dict[str, Any]]):
    """
    Store recommendations in server-side cache for execution API.
    
    Args:
        page_name: Cache key ('keywords', 'ads', 'shopping')
        recommendations: List of recommendation dictionaries
    """
    current_app.config['RECOMMENDATIONS_CACHE'][page_name] = recommendations


# ==================== Chat 22: Date Range Session Helpers ====================

_DATE_RE = re.compile(r'^\d{4}-\d{2}-\d{2}$')


def get_date_range_from_session() -> Tuple[int, any, any]:
    """
    Returns (days, date_from, date_to) tuple from Flask session.

    days      = 7 / 30 / 90 for preset ranges, 0 for custom date range.
    date_from = None for presets, ISO date string (YYYY-MM-DD) for custom.
    date_to   = None for presets, ISO date string (YYYY-MM-DD) for custom.

    Default: (30, None, None) if nothing stored in session.
    """
    dr = session.get('date_range')
    if not dr:
        return (30, None, None)

    range_type = dr.get('type', '30d')
    if range_type == 'custom':
        return (0, dr.get('date_from'), dr.get('date_to'))

    days = dr.get('days', 30)
    if days not in [7, 30, 90]:
        days = 30
    return (days, None, None)


# ==================== Chat 55 Module 3: Centralized Chart Data Function ====================


def get_performance_data(
    conn: 'duckdb.DuckDBPyConnection',
    customer_id: str,
    start_date: str,
    end_date: str,
    entity_type: str,
    campaign_type: str = None
) -> Dict[str, Any]:
    """
    Centralized function to build chart performance data for Module 3 charts.
    
    Replaces individual build_chart_data() functions in each route file.
    Supports all entity types with automatic date interval calculation.
    
    Args:
        conn: DuckDB connection with readonly database attached as 'ro'
        customer_id: Google Ads customer ID
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        entity_type: Type of entity ('campaign', 'keyword', 'ad_group', 'ad', 'shopping_product')
        campaign_type: Optional campaign type filter (e.g., 'Shopping', 'Search')
        
    Returns:
        Dictionary with structure:
        {
            'dates': ['Feb 1', 'Feb 2', ...],  # Formatted date labels
            'metrics': {
                'cost': [45.2, 47.8, ...],
                'impressions': [1800, 1950, ...],
                'clicks': [58, 60, ...],
                'avg_cpc': [0.77, 0.78, ...],
                'conversions': [5.8, 6.0, ...],
                'conv_value': [174, 180, ...],
                'cost_per_conv': [77.5, 78.3, ...],
                'conv_rate': [1.0, 1.0, ...],
                'ctr': [3.2, 3.1, ...],
                'roas': [0.39, 0.38, ...]
            }
        }
    """
    from datetime import datetime, timedelta
    
    # Parse dates
    try:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        # Invalid date format, return empty
        return _empty_chart_data()
    
    # Calculate total days and determine interval
    total_days = (end_dt - start_dt).days + 1
    
    if total_days <= 31:
        interval_days = 1      # Daily (up to 31 days)
        interval_label = 'daily'
    elif total_days <= 180:
        interval_days = 7      # Weekly
        interval_label = 'weekly'
    else:
        interval_days = 30     # Monthly
        interval_label = 'monthly'
    
    # Map entity type to database table
    table_map = {
        'campaign': 'ro.analytics.campaign_daily',
        'keyword': 'ro.analytics.keyword_daily',
        'ad_group': 'ro.analytics.ad_group_daily',
        'ad': 'ro.analytics.ad_daily',
        'shopping_product': 'ro.analytics.shopping_campaign_daily'
    }
    
    table_name = table_map.get(entity_type)
    if not table_name:
        print(f"[get_performance_data] Unknown entity_type: {entity_type}")
        return _empty_chart_data()
    
    # Special case: Shopping campaigns use separate table
    # Override table if entity_type='campaign' and campaign_type='SHOPPING'
    if entity_type == 'campaign' and campaign_type == 'SHOPPING':
        table_name = 'ro.analytics.shopping_campaign_daily'
        # No channel_type filter needed - entire table is Shopping campaigns
        campaign_type_filter = ""
        campaign_type_param = []
    # Build campaign_type filter if provided (only applies to campaign entity_type)
    # Uses channel_type column in database (e.g., 'SEARCH', 'DISPLAY')
    elif entity_type == 'campaign' and campaign_type:
        campaign_type_filter = "AND channel_type = ?"
        campaign_type_param = [campaign_type]
    else:
        campaign_type_filter = ""
        campaign_type_param = []
    
    # Build query based on interval
    if interval_days == 1:
        # Daily: One row per day
        query = f"""
            SELECT
                snapshot_date,
                SUM(cost_micros) / 1000000.0                                             AS cost,
                SUM(impressions)                                                          AS impressions,
                SUM(clicks)                                                               AS clicks,
                (SUM(cost_micros) / 1000000.0) / NULLIF(SUM(clicks), 0)                 AS avg_cpc,
                SUM(conversions)                                                          AS conversions,
                SUM(conversions_value)                                                    AS conv_value,
                (SUM(cost_micros) / 1000000.0) / NULLIF(SUM(conversions), 0)            AS cost_per_conv,
                (SUM(conversions) / NULLIF(SUM(clicks), 0)) * 100                        AS conv_rate,
                (SUM(clicks) / NULLIF(SUM(impressions), 0)) * 100                        AS ctr,
                SUM(conversions_value) / NULLIF(SUM(cost_micros) / 1000000.0, 0)        AS roas
            FROM {table_name}
            WHERE customer_id = ?
              AND snapshot_date BETWEEN CAST(? AS DATE) AND CAST(? AS DATE)
              {campaign_type_filter}
            GROUP BY snapshot_date
            ORDER BY snapshot_date ASC
        """
        params = [customer_id, start_date, end_date] + campaign_type_param
        
    elif interval_days == 7:
        # Weekly: Group by week (Mon-Sun)
        query = f"""
            SELECT
                DATE_TRUNC('week', snapshot_date) AS week_start,
                SUM(cost_micros) / 1000000.0                                             AS cost,
                SUM(impressions)                                                          AS impressions,
                SUM(clicks)                                                               AS clicks,
                (SUM(cost_micros) / 1000000.0) / NULLIF(SUM(clicks), 0)                 AS avg_cpc,
                SUM(conversions)                                                          AS conversions,
                SUM(conversions_value)                                                    AS conv_value,
                (SUM(cost_micros) / 1000000.0) / NULLIF(SUM(conversions), 0)            AS cost_per_conv,
                (SUM(conversions) / NULLIF(SUM(clicks), 0)) * 100                        AS conv_rate,
                (SUM(clicks) / NULLIF(SUM(impressions), 0)) * 100                        AS ctr,
                SUM(conversions_value) / NULLIF(SUM(cost_micros) / 1000000.0, 0)        AS roas
            FROM {table_name}
            WHERE customer_id = ?
              AND snapshot_date BETWEEN CAST(? AS DATE) AND CAST(? AS DATE)
              {campaign_type_filter}
            GROUP BY week_start
            ORDER BY week_start ASC
        """
        params = [customer_id, start_date, end_date] + campaign_type_param
        
    else:
        # Monthly: Group by month
        query = f"""
            SELECT
                DATE_TRUNC('month', snapshot_date) AS month_start,
                SUM(cost_micros) / 1000000.0                                             AS cost,
                SUM(impressions)                                                          AS impressions,
                SUM(clicks)                                                               AS clicks,
                (SUM(cost_micros) / 1000000.0) / NULLIF(SUM(clicks), 0)                 AS avg_cpc,
                SUM(conversions)                                                          AS conversions,
                SUM(conversions_value)                                                    AS conv_value,
                (SUM(cost_micros) / 1000000.0) / NULLIF(SUM(conversions), 0)            AS cost_per_conv,
                (SUM(conversions) / NULLIF(SUM(clicks), 0)) * 100                        AS conv_rate,
                (SUM(clicks) / NULLIF(SUM(impressions), 0)) * 100                        AS ctr,
                SUM(conversions_value) / NULLIF(SUM(cost_micros) / 1000000.0, 0)        AS roas
            FROM {table_name}
            WHERE customer_id = ?
              AND snapshot_date BETWEEN CAST(? AS DATE) AND CAST(? AS DATE)
              {campaign_type_filter}
            GROUP BY month_start
            ORDER BY month_start ASC
        """
        params = [customer_id, start_date, end_date] + campaign_type_param
    
    # Execute query
    try:
        rows = conn.execute(query, params).fetchall()
    except Exception as e:
        print(f"[get_performance_data] Query error: {e}")
        import traceback
        traceback.print_exc()
        return _empty_chart_data()
    
    if not rows:
        return _empty_chart_data()
    
    # Format dates based on interval
    dates = []
    for row in rows:
        date_val = row[0]
        if interval_label == 'daily':
            # Format: 'Feb 1', 'Feb 2' (cross-platform)
            dt = datetime.strptime(str(date_val), '%Y-%m-%d')
            dates.append(f"{dt.strftime('%b')} {dt.day}")
        elif interval_label == 'weekly':
            # Format: 'Week of Feb 1'
            dt = datetime.strptime(str(date_val), '%Y-%m-%d')
            dates.append(f"Week of {dt.strftime('%b')} {dt.day}")
        else:  # monthly
            # Format: 'Feb 2026', 'Mar 2026'
            dt = datetime.strptime(str(date_val), '%Y-%m-%d')
            dates.append(dt.strftime('%b %Y'))
    
    # Extract metric values (handle NULL with 0.0)
    def safe_float(val):
        return float(val) if val is not None else 0.0
    
    metrics = {
        'cost':          [safe_float(row[1]) for row in rows],
        'impressions':   [safe_float(row[2]) for row in rows],
        'clicks':        [safe_float(row[3]) for row in rows],
        'avg_cpc':       [safe_float(row[4]) for row in rows],
        'conversions':   [safe_float(row[5]) for row in rows],
        'conv_value':    [safe_float(row[6]) for row in rows],
        'cost_per_conv': [safe_float(row[7]) for row in rows],
        'conv_rate':     [safe_float(row[8]) for row in rows],
        'ctr':           [safe_float(row[9]) for row in rows],
        'roas':          [safe_float(row[10]) for row in rows],
    }
    
    # Calculate current period totals
    totals = {
        'cost':          sum(metrics['cost']),
        'impressions':   sum(metrics['impressions']),
        'clicks':        sum(metrics['clicks']),
        'avg_cpc':       sum(metrics['cost']) / sum(metrics['clicks']) if sum(metrics['clicks']) > 0 else 0.0,
        'conversions':   sum(metrics['conversions']),
        'conv_value':    sum(metrics['conv_value']),
        'cost_per_conv': sum(metrics['cost']) / sum(metrics['conversions']) if sum(metrics['conversions']) > 0 else 0.0,
        'conv_rate':     (sum(metrics['conversions']) / sum(metrics['clicks']) * 100) if sum(metrics['clicks']) > 0 else 0.0,
        'ctr':           (sum(metrics['clicks']) / sum(metrics['impressions']) * 100) if sum(metrics['impressions']) > 0 else 0.0,
        'roas':          sum(metrics['conv_value']) / sum(metrics['cost']) if sum(metrics['cost']) > 0 else 0.0,
    }
    
    # Calculate previous period dates for change_pct
    total_days = (end_dt - start_dt).days + 1
    prev_end_dt = start_dt - timedelta(days=1)
    prev_start_dt = prev_end_dt - timedelta(days=total_days - 1)
    prev_start_date = prev_start_dt.strftime('%Y-%m-%d')
    prev_end_date = prev_end_dt.strftime('%Y-%m-%d')
    
    # Query previous period totals
    prev_query = f"""
        SELECT
            SUM(cost_micros) / 1000000.0 AS cost,
            SUM(impressions) AS impressions,
            SUM(clicks) AS clicks,
            SUM(conversions) AS conversions,
            SUM(conversions_value) AS conv_value
        FROM {table_name}
        WHERE customer_id = ?
          AND snapshot_date BETWEEN CAST(? AS DATE) AND CAST(? AS DATE)
          {campaign_type_filter}
    """
    
    try:
        prev_row = conn.execute(prev_query, [customer_id, prev_start_date, prev_end_date] + campaign_type_param).fetchone()
    except Exception as e:
        print(f"[get_performance_data] Previous period query error: {e}")
        prev_row = None
    
    # Calculate change_pct
    def calc_change_pct(current, previous):
        if previous is None or previous == 0:
            return None
        if current is None:
            return -100.0
        return ((current - previous) / previous) * 100.0
    
    if prev_row:
        prev_cost = safe_float(prev_row[0])
        prev_impr = safe_float(prev_row[1])
        prev_clicks = safe_float(prev_row[2])
        prev_conv = safe_float(prev_row[3])
        prev_conv_val = safe_float(prev_row[4])
        prev_cpc = prev_cost / prev_clicks if prev_clicks > 0 else 0.0
        prev_cost_per_conv = prev_cost / prev_conv if prev_conv > 0 else 0.0
        prev_conv_rate = (prev_conv / prev_clicks * 100) if prev_clicks > 0 else 0.0
        prev_ctr = (prev_clicks / prev_impr * 100) if prev_impr > 0 else 0.0
        prev_roas = prev_conv_val / prev_cost if prev_cost > 0 else 0.0
    else:
        prev_cost = prev_impr = prev_clicks = prev_conv = prev_conv_val = 0.0
        prev_cpc = prev_cost_per_conv = prev_conv_rate = prev_ctr = prev_roas = 0.0
    
    change_pct = {
        'cost':          calc_change_pct(totals['cost'], prev_cost),
        'impressions':   calc_change_pct(totals['impressions'], prev_impr),
        'clicks':        calc_change_pct(totals['clicks'], prev_clicks),
        'avg_cpc':       calc_change_pct(totals['avg_cpc'], prev_cpc),
        'conversions':   calc_change_pct(totals['conversions'], prev_conv),
        'conv_value':    calc_change_pct(totals['conv_value'], prev_conv_val),
        'cost_per_conv': calc_change_pct(totals['cost_per_conv'], prev_cost_per_conv),
        'conv_rate':     calc_change_pct(totals['conv_rate'], prev_conv_rate),
        'ctr':           calc_change_pct(totals['ctr'], prev_ctr),
        'roas':          calc_change_pct(totals['roas'], prev_roas),
    }
    
    return {
        'dates': dates,
        'metrics': metrics,
        'totals': totals,
        'change_pct': change_pct
    }


def _empty_chart_data() -> Dict[str, Any]:
    """Returns empty chart data structure."""
    return {
        'dates': [],
        'metrics': {
            'cost': [],
            'impressions': [],
            'clicks': [],
            'avg_cpc': [],
            'conversions': [],
            'conv_value': [],
            'cost_per_conv': [],
            'conv_rate': [],
            'ctr': [],
            'roas': [],
        },
        'totals': {
            'cost': 0.0,
            'impressions': 0.0,
            'clicks': 0.0,
            'avg_cpc': 0.0,
            'conversions': 0.0,
            'conv_value': 0.0,
            'cost_per_conv': 0.0,
            'conv_rate': 0.0,
            'ctr': 0.0,
            'roas': 0.0,
        },
        'change_pct': {
            'cost': None,
            'impressions': None,
            'clicks': None,
            'avg_cpc': None,
            'conversions': None,
            'conv_value': None,
            'cost_per_conv': None,
            'conv_rate': None,
            'ctr': None,
            'roas': None,
        }
    }


# Blueprint for shared utility routes
bp = Blueprint('shared', __name__)


@bp.route('/set-date-range', methods=['POST'])
def set_date_range():
    """
    POST /set-date-range
    Body JSON: { range_type: '7'|'30'|'90'|'custom', date_from?, date_to? }
    Stores selection in Flask session.
    Returns JSON: { success: true }
    """
    data = request.get_json(silent=True) or request.form

    range_type = str(data.get('range_type', '')).strip()

    if range_type in ('7', '30', '90'):
        session['date_range'] = {
            'type': f'{range_type}d',
            'days': int(range_type),
            'date_from': None,
            'date_to': None,
        }
        return jsonify({'success': True, 'days': int(range_type)})

    if range_type == 'custom':
        date_from = str(data.get('date_from', '')).strip()
        date_to   = str(data.get('date_to',   '')).strip()

        if not _DATE_RE.match(date_from) or not _DATE_RE.match(date_to):
            return jsonify({'success': False, 'error': 'Invalid date format — expected YYYY-MM-DD'}), 400

        if date_from > date_to:
            return jsonify({'success': False, 'error': 'date_from must be on or before date_to'}), 400

        session['date_range'] = {
            'type': 'custom',
            'days': 0,
            'date_from': date_from,
            'date_to': date_to,
        }
        return jsonify({'success': True, 'days': 0, 'date_from': date_from, 'date_to': date_to})

    return jsonify({'success': False, 'error': f'Invalid range_type: {range_type!r}'}), 400


# ==================== Chat 23 M2: Metrics Collapse Session Helpers ====================


def get_metrics_collapsed(page_id: str) -> bool:
    """
    Returns the collapsed state for the Actions row on a given page.

    Args:
        page_id: Page identifier string e.g. 'campaigns', 'keywords'

    Returns:
        True if Actions row is collapsed, False (default) if expanded.
    """
    collapsed_map = session.get('metrics_collapsed', {})
    return bool(collapsed_map.get(page_id, False))


@bp.route('/set-metrics-collapse', methods=['POST'])
def set_metrics_collapse():
    """
    POST /set-metrics-collapse
    Body JSON: { page_id: str, collapsed: bool }
    Stores per-page collapse state in session['metrics_collapsed'][page_id].
    Returns JSON: { success: true }
    """
    data = request.get_json(silent=True) or {}

    page_id = str(data.get('page_id', '')).strip()
    collapsed = bool(data.get('collapsed', False))

    if not page_id:
        return jsonify({'success': False, 'error': 'page_id is required'}), 400

    # Read existing map, update, write back (Flask session requires reassignment)
    collapsed_map = dict(session.get('metrics_collapsed', {}))
    collapsed_map[page_id] = collapsed
    session['metrics_collapsed'] = collapsed_map

    return jsonify({'success': True, 'page_id': page_id, 'collapsed': collapsed})


# ==================== Chat 24 M3: Chart Metrics Session Helpers ====================


def get_chart_metrics(page_id: str) -> List[str]:
    """
    Returns the active chart metric keys for a given page.

    Args:
        page_id: Page identifier string e.g. 'campaigns', 'keywords'

    Returns:
        List of active metric keys. Default: ['cost', 'impressions']
    """
    key = f'chart_metrics_{page_id}'
    stored = session.get(key)
    if stored and isinstance(stored, list):
        # Validate — only allow known metric keys (Module 3: expanded to 10 metrics)
        valid = {
            'cost', 'impressions', 'clicks', 'avg_cpc',
            'conversions', 'conv_value', 'cost_per_conv',
            'conv_rate', 'ctr', 'roas'
        }
        filtered = [m for m in stored if m in valid]
        if filtered:
            return filtered
    return ['cost', 'impressions']


def _set_chart_metrics_session(page_id: str, metrics: List[str]) -> None:
    """
    Internal helper: Saves active chart metric keys for a given page to session.

    Args:
        page_id: Page identifier string e.g. 'campaigns'
        metrics: List of metric keys to store
    """
    # Module 3: Expanded valid metrics to 10 total
    valid = {
        'cost', 'impressions', 'clicks', 'avg_cpc',
        'conversions', 'conv_value', 'cost_per_conv',
        'conv_rate', 'ctr', 'roas'
    }
    filtered = [m for m in metrics if m in valid]
    session[f'chart_metrics_{page_id}'] = filtered


@bp.route('/set-chart-metrics', methods=['POST'])
def set_chart_metrics():
    """
    POST /set-chart-metrics
    Body JSON: { page_id: str, metrics: [str, ...] }
    Stores active chart metrics in session per page.
    Returns JSON: { status: 'ok' }
    """
    data = request.get_json(silent=True) or {}

    page_id = str(data.get('page_id', '')).strip()
    metrics = data.get('metrics', [])

    if not page_id:
        return jsonify({'status': 'error', 'error': 'page_id is required'}), 400

    if not isinstance(metrics, list):
        return jsonify({'status': 'error', 'error': 'metrics must be a list'}), 400

    _set_chart_metrics_session(page_id, metrics)
    return jsonify({'status': 'ok', 'page_id': page_id, 'metrics': get_chart_metrics(page_id)})
