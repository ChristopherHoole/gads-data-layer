"""
Data models for Autopilot module.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import date


def _safe_float(value: Any, default: float = 0.0) -> float:
    """
    Safely convert value to float.

    Args:
        value: Value to convert (can be None, int, float, str)
        default: Default value to return if conversion fails (default: 0.0)

    Returns:
        Float value or default if conversion fails
    """
    if value is None:
        return default

    try:
        return float(value)
    except (ValueError, TypeError):
        return default


@dataclass
class AutopilotConfig:
    """Configuration for Autopilot execution."""

    customer_id: str
    automation_mode: str  # 'insights', 'suggest', 'auto_low_risk', 'auto_expanded'
    risk_tolerance: str  # 'conservative', 'balanced', 'aggressive'
    daily_spend_cap: float
    monthly_spend_cap: float
    brand_is_protected: bool
    protected_entities: List[str]

    # Additional fields used by engine and reporting
    client_name: str = "UNKNOWN"
    client_type: str = "ecom"
    primary_kpi: str = "roas"
    target_roas: Optional[float] = None
    target_cpa: Optional[float] = None
    max_changes_per_day: int = 10


@dataclass
class Recommendation:
    """
    A single optimization recommendation.

    Fields with defaults MUST come after fields without defaults.
    """

    # Required fields (no defaults)
    rule_id: str
    rule_name: str
    entity_type: str
    entity_id: str
    action_type: str
    risk_tier: str

    # Optional fields (with defaults)
    confidence: float = 0.0
    current_value: Optional[float] = None
    recommended_value: Optional[float] = None
    change_pct: Optional[float] = None
    rationale: str = ""
    campaign_name: Optional[str] = None
    blocked: bool = False
    block_reason: Optional[str] = None
    priority: int = 50
    constitution_refs: List[str] = field(default_factory=list)
    guardrails_checked: List[str] = field(default_factory=list)
    evidence: Optional[Dict[str, Any]] = None
    triggering_diagnosis: Optional[str] = None
    triggering_confidence: float = 0.0
    expected_impact: str = ""


@dataclass
class GuardrailCheck:
    """Result of guardrail validation."""

    valid: bool
    blocked_reasons: List[str] = field(default_factory=list)


@dataclass
class RuleContext:
    """
    Context passed to each rule function.

    Contains all information needed to make a recommendation decision.
    """

    # Campaign identification
    customer_id: str
    campaign_id: str

    # Data snapshots
    snapshot_date: date
    features: Dict[str, Any]  # Campaign features from Lighthouse
    insights: List[Dict[str, Any]]  # Lighthouse insights for this campaign

    # Configuration
    config: AutopilotConfig

    # All campaigns data (for account-level rules)
    all_features: List[Dict[str, Any]] = field(default_factory=list)
    all_insights: List[Dict[str, Any]] = field(default_factory=list)

    # Database access
    db_path: str = "warehouse.duckdb"
