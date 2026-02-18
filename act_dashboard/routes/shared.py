"""
Shared helper functions used across dashboard routes.
"""

from flask import session, current_app
from act_dashboard.config import DashboardConfig
from google.ads.googleads.client import GoogleAdsClient
from pathlib import Path
import duckdb
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
