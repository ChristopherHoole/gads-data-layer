"""
Configuration validation with clear error messages.

Validates client configs before use to prevent crashes from:
- Negative target_roas
- Zero spend caps
- Invalid customer_id format
- Missing required fields
- Invalid enum values

Usage:
    from act_autopilot.config_validator import validate_config

    errors = validate_config(config_dict)
    if errors:
        print("Invalid config:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
"""

from typing import Dict, List, Any

from .logging_config import setup_logging

logger = setup_logging(__name__)


def validate_config(config: Dict[str, Any]) -> List[str]:
    """
    Validate client configuration.

    Args:
        config: Configuration dictionary loaded from YAML

    Returns:
        List of error messages (empty if valid)

    If errors found, raises ValueError with details.
    """
    logger.info("Validating configuration...")

    errors = []

    # Required fields
    errors.extend(_check_required_fields(config))

    # Google Ads config
    if "google_ads" in config:
        errors.extend(_validate_google_ads_config(config["google_ads"]))
    else:
        errors.append("Missing required section: google_ads")

    # Targets
    if "targets" in config:
        errors.extend(_validate_targets(config["targets"]))

    # Spend caps
    if "spend_caps" in config:
        errors.extend(_validate_spend_caps(config["spend_caps"]))
    else:
        errors.append("Missing required section: spend_caps")

    # Automation mode
    if "automation_mode" in config:
        errors.extend(_validate_automation_mode(config["automation_mode"]))
    else:
        errors.append("Missing required field: automation_mode")

    # Risk tolerance
    if "risk_tolerance" in config:
        errors.extend(_validate_risk_tolerance(config["risk_tolerance"]))
    else:
        errors.append("Missing required field: risk_tolerance")

    # Client type
    if "client_type" in config:
        errors.extend(_validate_client_type(config["client_type"]))
    else:
        errors.append("Missing required field: client_type")

    # Primary KPI
    if "primary_kpi" in config:
        errors.extend(_validate_primary_kpi(config["primary_kpi"]))
    else:
        errors.append("Missing required field: primary_kpi")

    # Protected entities
    if "protected_entities" in config:
        errors.extend(_validate_protected_entities(config["protected_entities"]))

    if errors:
        logger.error(f"Config validation failed: {len(errors)} errors")
        for error in errors:
            logger.error(f"  - {error}")
    else:
        logger.info("Config validation passed ✅")

    return errors


def _check_required_fields(config: Dict[str, Any]) -> List[str]:
    """Check all required top-level fields exist."""
    required = [
        "client_name",
        "client_type",
        "primary_kpi",
        "google_ads",
        "automation_mode",
        "risk_tolerance",
        "spend_caps",
        "currency",
        "timezone",
    ]

    errors = []
    for field in required:
        if field not in config:
            errors.append(f"Missing required field: {field}")

    return errors


def _validate_google_ads_config(ga_config: Dict[str, Any]) -> List[str]:
    """Validate google_ads section."""
    errors = []

    # Required fields
    if "customer_id" not in ga_config:
        errors.append("google_ads.customer_id is required")
    else:
        customer_id = str(ga_config["customer_id"])

        # Must be digits only (no dashes)
        if not customer_id.isdigit():
            errors.append(
                f"google_ads.customer_id must be digits only (no dashes): '{customer_id}'"
            )

        # Must be 10 digits
        if len(customer_id) != 10:
            errors.append(
                f"google_ads.customer_id must be 10 digits: '{customer_id}' ({len(customer_id)} digits)"
            )

    # MCC ID (optional, but if present must be valid)
    if "mcc_id" in ga_config:
        mcc_id = str(ga_config["mcc_id"])
        if not mcc_id.isdigit() or len(mcc_id) != 10:
            errors.append(f"google_ads.mcc_id must be 10 digits: '{mcc_id}'")

    return errors


def _validate_targets(targets: Dict[str, Any]) -> List[str]:
    """Validate targets section."""
    errors = []

    # Target ROAS
    if "target_roas" in targets:
        target_roas = targets["target_roas"]

        # Must be positive
        if not isinstance(target_roas, (int, float)) or target_roas <= 0:
            errors.append(f"targets.target_roas must be positive number: {target_roas}")

        # Reasonable range (0.1 to 20.0)
        if isinstance(target_roas, (int, float)) and (
            target_roas < 0.1 or target_roas > 20.0
        ):
            errors.append(
                f"targets.target_roas seems unrealistic: {target_roas} (expected 0.1-20.0)"
            )

    # Target CPA
    if "target_cpa" in targets:
        target_cpa = targets["target_cpa"]

        # Must be positive
        if not isinstance(target_cpa, (int, float)) or target_cpa <= 0:
            errors.append(f"targets.target_cpa must be positive number: {target_cpa}")

    return errors


def _validate_spend_caps(spend_caps: Dict[str, Any]) -> List[str]:
    """Validate spend_caps section."""
    errors = []

    # Daily cap
    if "daily" not in spend_caps:
        errors.append("spend_caps.daily is required")
    else:
        daily = spend_caps["daily"]

        # Must be positive
        if not isinstance(daily, (int, float)) or daily <= 0:
            errors.append(f"spend_caps.daily must be positive: {daily}")

    # Monthly cap
    if "monthly" not in spend_caps:
        errors.append("spend_caps.monthly is required")
    else:
        monthly = spend_caps["monthly"]

        # Must be positive
        if not isinstance(monthly, (int, float)) or monthly <= 0:
            errors.append(f"spend_caps.monthly must be positive: {monthly}")

        # Monthly should be >= daily × 20 (sanity check)
        if "daily" in spend_caps:
            daily = spend_caps["daily"]
            if monthly < daily * 20:
                errors.append(
                    f"spend_caps.monthly ({monthly}) seems low for daily ({daily}). "
                    f"Expected >= {daily * 20:.0f}"
                )

    return errors


def _validate_automation_mode(mode: str) -> List[str]:
    """Validate automation_mode."""
    valid_modes = ["insights", "suggest", "auto_low_risk", "auto_expanded"]

    if mode not in valid_modes:
        return [
            f"Invalid automation_mode: '{mode}'. "
            f"Must be one of: {', '.join(valid_modes)}"
        ]

    return []


def _validate_risk_tolerance(tolerance: str) -> List[str]:
    """Validate risk_tolerance."""
    valid_tolerances = ["conservative", "balanced", "aggressive"]

    if tolerance not in valid_tolerances:
        return [
            f"Invalid risk_tolerance: '{tolerance}'. "
            f"Must be one of: {', '.join(valid_tolerances)}"
        ]

    return []


def _validate_client_type(client_type: str) -> List[str]:
    """Validate client_type."""
    valid_types = ["ecom", "lead_gen", "mixed"]

    if client_type not in valid_types:
        return [
            f"Invalid client_type: '{client_type}'. "
            f"Must be one of: {', '.join(valid_types)}"
        ]

    return []


def _validate_primary_kpi(kpi: str) -> List[str]:
    """Validate primary_kpi."""
    valid_kpis = ["roas", "cpa", "conversions", "revenue", "qualified_leads"]

    if kpi not in valid_kpis:
        return [
            f"Invalid primary_kpi: '{kpi}'. " f"Must be one of: {', '.join(valid_kpis)}"
        ]

    return []


def _validate_protected_entities(protected: Dict[str, Any]) -> List[str]:
    """Validate protected_entities section."""
    errors = []

    # brand_is_protected
    if "brand_is_protected" in protected:
        if not isinstance(protected["brand_is_protected"], bool):
            errors.append(
                f"protected_entities.brand_is_protected must be boolean: "
                f"{protected['brand_is_protected']}"
            )

    # entities list
    if "entities" in protected:
        if not isinstance(protected["entities"], list):
            errors.append(
                f"protected_entities.entities must be a list: "
                f"{type(protected['entities'])}"
            )

    return errors


def validate_config_file(config_path: str) -> Dict[str, Any]:
    """
    Load and validate config file.

    Args:
        config_path: Path to YAML config file

    Returns:
        Validated config dictionary

    Raises:
        ValueError: If config is invalid
        FileNotFoundError: If file not found
    """
    import yaml
    from pathlib import Path

    logger.info(f"Loading config from {config_path}")

    # Check file exists
    if not Path(config_path).exists():
        error_msg = f"Config file not found: {config_path}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)

    # Load YAML
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
    except Exception as e:
        error_msg = f"Failed to parse YAML config: {e}"
        logger.error(error_msg)
        raise ValueError(error_msg)

    # Validate
    errors = validate_config(config)

    if errors:
        error_msg = "Invalid configuration:\n" + "\n".join(f"  - {e}" for e in errors)
        logger.error(error_msg)
        raise ValueError(error_msg)

    logger.info(f"Config loaded and validated: {config.get('client_name', 'Unknown')}")
    return config
