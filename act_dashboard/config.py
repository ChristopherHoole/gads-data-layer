"""
Dashboard Configuration
Loads client config and provides dashboard settings.
"""

import yaml
from pathlib import Path


class DashboardConfig:
    """Dashboard configuration loaded from client YAML."""
    
    def __init__(self, config_path: str):
        """
        Load configuration from client YAML file.
        
        Args:
            config_path: Path to client config YAML
        """
        self.config_path = config_path
        
        # Load client config
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Extract key settings
        self.client_name = self.config.get('client_name', 'Unknown Client')
        self.customer_id = self._get_customer_id()
        self.client_type = self.config.get('client_type', 'ecom')
        self.primary_kpi = self.config.get('primary_kpi', 'roas')
        self.automation_mode = self.config.get('automation_mode', 'insights')
        self.risk_tolerance = self.config.get('risk_tolerance', 'conservative')
        
        # Targets
        targets = self.config.get('targets', {})
        self.target_roas = targets.get('target_roas')
        self.target_cpa = targets.get('target_cpa')
        
        # Spend caps
        spend_caps = self.config.get('spend_caps', {})
        self.daily_cap = spend_caps.get('daily', 0)
        self.monthly_cap = spend_caps.get('monthly', 0)
        
        # Protected entities
        protected = self.config.get('protected_entities', {})
        self.brand_protected = protected.get('brand_is_protected', True)
        self.protected_campaigns = protected.get('entities', [])
        
        # Database path
        self.db_path = "warehouse.duckdb"
        
        # Dashboard settings
        self.TEMPLATES_AUTO_RELOAD = True
        self.SEND_FILE_MAX_AGE_DEFAULT = 0
    
    def _get_customer_id(self) -> str:
        """Extract customer_id from config (handles nested structure)."""
        if 'customer_id' in self.config:
            return self.config['customer_id']
        elif 'google_ads' in self.config and 'customer_id' in self.config['google_ads']:
            return self.config['google_ads']['customer_id']
        else:
            return 'UNKNOWN'
    
    def get_suggestions_path(self, date: str) -> Path:
        """Get path to suggestions JSON file for given date."""
        return Path(f"reports/suggestions/{self.client_name}/{date}.json")
    
    def get_approvals_path(self, date: str) -> Path:
        """Get path to approvals JSON file for given date."""
        return Path(f"reports/suggestions/{self.client_name}/approvals/{date}_approvals.json")
    
    def save(self):
        """Save current configuration back to YAML file."""
        # Update config dict with current values
        self.config['client_name'] = self.client_name
        self.config['client_type'] = self.client_type
        self.config['primary_kpi'] = self.primary_kpi
        self.config['automation_mode'] = self.automation_mode
        self.config['risk_tolerance'] = self.risk_tolerance
        
        # Update targets
        if 'targets' not in self.config:
            self.config['targets'] = {}
        if self.target_roas is not None:
            self.config['targets']['target_roas'] = self.target_roas
        if self.target_cpa is not None:
            self.config['targets']['target_cpa'] = self.target_cpa
        
        # Update spend caps
        if 'spend_caps' not in self.config:
            self.config['spend_caps'] = {}
        self.config['spend_caps']['daily'] = self.daily_cap
        self.config['spend_caps']['monthly'] = self.monthly_cap
        
        # Update protected entities
        if 'protected_entities' not in self.config:
            self.config['protected_entities'] = {}
        self.config['protected_entities']['brand_is_protected'] = self.brand_protected
        self.config['protected_entities']['entities'] = self.protected_campaigns
        
        # Write back to file
        with open(self.config_path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
