"""
Configuration validator - validates client YAML configs on startup.

Prevents crashes from invalid or malformed configuration files.
"""

from pathlib import Path
from typing import Dict, Any, List, Tuple
import yaml


# Required top-level fields in client config
REQUIRED_FIELDS = {
    'client_id': str,
    'customer_id': str,
    'db_path': str,
}

# Optional fields with expected types
OPTIONAL_FIELDS = {
    'client_name': str,
    'client_type': str,
    'primary_kpi': str,
    'automation_mode': str,
    'risk_tolerance': str,
    'target_roas': (int, float, type(None)),
    'target_cpa': (int, float, type(None)),
}

# Valid enum values
VALID_CLIENT_TYPES = {'ecom', 'lead_gen', 'brand', 'saas', 'local'}
VALID_PRIMARY_KPIS = {'roas', 'cpa', 'ctr', 'conversions', 'revenue'}
VALID_AUTOMATION_MODES = {'suggest', 'auto_approve', 'full_auto'}
VALID_RISK_TOLERANCES = {'conservative', 'moderate', 'aggressive'}


def validate_config_file(config_path: Path) -> Tuple[bool, List[str]]:
    """
    Validate a client configuration YAML file.
    
    Args:
        config_path: Path to client YAML config file
        
    Returns:
        (is_valid, error_messages) tuple
    """
    errors = []
    
    # Check file exists
    if not config_path.exists():
        return False, [f"Config file not found: {config_path}"]
    
    # Check file is readable
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        return False, [f"Invalid YAML syntax: {e}"]
    except Exception as e:
        return False, [f"Cannot read config file: {e}"]
    
    # Check it's a dictionary
    if not isinstance(config, dict):
        return False, ["Config must be a YAML dictionary/object"]
    
    # Validate required fields
    for field, expected_type in REQUIRED_FIELDS.items():
        if field not in config:
            errors.append(f"Missing required field: '{field}'")
            continue
        
        value = config[field]
        if value is None or value == '':
            errors.append(f"Field '{field}' cannot be empty")
            continue
        
        if not isinstance(value, expected_type):
            errors.append(
                f"Field '{field}' must be {expected_type.__name__}, "
                f"got {type(value).__name__}"
            )
    
    # Validate optional fields if present
    for field, expected_type in OPTIONAL_FIELDS.items():
        if field not in config:
            continue
        
        value = config[field]
        if value is None:
            continue  # None is ok for optional fields
        
        # Handle union types (e.g., int or float or None)
        if isinstance(expected_type, tuple):
            if not isinstance(value, expected_type):
                type_names = ' or '.join(t.__name__ for t in expected_type if t is not type(None))
                errors.append(
                    f"Field '{field}' must be {type_names}, "
                    f"got {type(value).__name__}"
                )
        else:
            if not isinstance(value, expected_type):
                errors.append(
                    f"Field '{field}' must be {expected_type.__name__}, "
                    f"got {type(value).__name__}"
                )
    
    # Validate enum values
    if 'client_type' in config and config['client_type'] not in VALID_CLIENT_TYPES:
        errors.append(
            f"Invalid client_type: '{config['client_type']}'. "
            f"Must be one of: {sorted(VALID_CLIENT_TYPES)}"
        )
    
    if 'primary_kpi' in config and config['primary_kpi'] not in VALID_PRIMARY_KPIS:
        errors.append(
            f"Invalid primary_kpi: '{config['primary_kpi']}'. "
            f"Must be one of: {sorted(VALID_PRIMARY_KPIS)}"
        )
    
    if 'automation_mode' in config and config['automation_mode'] not in VALID_AUTOMATION_MODES:
        errors.append(
            f"Invalid automation_mode: '{config['automation_mode']}'. "
            f"Must be one of: {sorted(VALID_AUTOMATION_MODES)}"
        )
    
    if 'risk_tolerance' in config and config['risk_tolerance'] not in VALID_RISK_TOLERANCES:
        errors.append(
            f"Invalid risk_tolerance: '{config['risk_tolerance']}'. "
            f"Must be one of: {sorted(VALID_RISK_TOLERANCES)}"
        )
    
    # Validate database path exists (if it's a file path)
    if 'db_path' in config and config['db_path']:
        db_path = Path(config['db_path'])
        # Only check if it looks like an absolute path
        if db_path.is_absolute() and not db_path.exists():
            errors.append(f"Database file not found: {db_path}")
    
    # Validate spend caps structure if present
    if 'spend_caps' in config:
        spend_caps = config['spend_caps']
        if not isinstance(spend_caps, dict):
            errors.append("'spend_caps' must be a dictionary")
        else:
            for cap_type in ['daily', 'monthly']:
                if cap_type in spend_caps:
                    value = spend_caps[cap_type]
                    if value is not None and not isinstance(value, (int, float)):
                        errors.append(
                            f"spend_caps.{cap_type} must be a number, "
                            f"got {type(value).__name__}"
                        )
    
    # Validate targets structure if present
    if 'targets' in config:
        targets = config['targets']
        if not isinstance(targets, dict):
            errors.append("'targets' must be a dictionary")
        else:
            for target_type in ['target_roas', 'target_cpa']:
                if target_type in targets:
                    value = targets[target_type]
                    if value is not None and not isinstance(value, (int, float)):
                        errors.append(
                            f"targets.{target_type} must be a number, "
                            f"got {type(value).__name__}"
                        )
    
    return len(errors) == 0, errors


def validate_all_configs(config_dir: Path) -> Tuple[bool, Dict[str, List[str]]]:
    """
    Validate all client configuration files in a directory.
    
    Args:
        config_dir: Directory containing client_*.yaml files
        
    Returns:
        (all_valid, errors_by_file) tuple
    """
    config_files = list(config_dir.glob("client_*.yaml"))
    
    if not config_files:
        return False, {"_global": ["No client config files found in configs/ directory"]}
    
    all_errors = {}
    all_valid = True
    
    for config_path in config_files:
        is_valid, errors = validate_config_file(config_path)
        if not is_valid:
            all_valid = False
            all_errors[config_path.name] = errors
    
    return all_valid, all_errors


def print_validation_errors(errors_by_file: Dict[str, List[str]]) -> None:
    """
    Print validation errors in a readable format.
    
    Args:
        errors_by_file: Dictionary of filename -> error messages
    """
    print("\n" + "=" * 80)
    print("❌ CONFIGURATION VALIDATION ERRORS")
    print("=" * 80)
    
    for filename, errors in errors_by_file.items():
        print(f"\n📄 {filename}:")
        for error in errors:
            print(f"  ❌ {error}")
    
    print("\n" + "=" * 80)
    print("Please fix the configuration errors above and restart the application.")
    print("=" * 80 + "\n")
