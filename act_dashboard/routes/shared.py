"""
Shared helper functions used across dashboard routes.
"""

from flask import session, current_app
from act_dashboard.config import DashboardConfig
from google.ads.googleads.client import GoogleAdsClient
from pathlib import Path


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
