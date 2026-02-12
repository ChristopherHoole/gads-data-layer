"""
Autopilot data models — Recommendation, RuleResult, AutopilotConfig.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class AutopilotConfig:
    """Extended config for Autopilot (adds fields beyond Lighthouse ClientConfig)."""
    client_id: str
    customer_id: str
    client_type: str                    # ecom | lead_gen | mixed
    primary_kpi: str                    # roas | cpa | qualified_leads
    automation_mode: str                # insights | suggest | auto_low_risk | auto_expanded
    risk_tolerance: str                 # conservative | balanced | aggressive
    target_roas: Optional[float] = None
    target_cpa: Optional[float] = None
    daily_cap: Optional[float] = None   # in currency units (not micros)
    monthly_cap: Optional[float] = None # in currency units (not micros)
    protected_campaign_ids: List[str] = field(default_factory=list)
    brand_is_protected: bool = True
    currency: str = "USD"
    timezone: str = "UTC"
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Recommendation:
    """A single rule-generated recommendation."""
    rule_id: str
    rule_name: str
    entity_type: str                    # CAMPAIGN | ACCOUNT
    entity_id: Optional[str]            # campaign_id or None for ACCOUNT
    action_type: str                    # budget_increase | budget_decrease | bid_target_increase | bid_target_decrease | pause | enable | pacing_cut | review
    risk_tier: str                      # low | med | high
    confidence: float                   # 0-1 (inherited from triggering insight)
    current_value: Optional[float]      # current budget/bid/etc (micros or ratio)
    recommended_value: Optional[float]  # new budget/bid/etc
    change_pct: Optional[float]         # e.g. 0.10 = +10%
    rationale: str                      # human-readable explanation
    evidence: Dict[str, Any]            # supporting data
    constitution_refs: List[str]        # CONSTITUTION-X-Y rule IDs
    guardrails_checked: List[str]       # which guardrails were verified
    triggering_diagnosis: str           # Lighthouse diagnosis_code that triggered this
    triggering_confidence: float        # Lighthouse confidence score
    blocked: bool = False               # True if guardrail blocked execution
    block_reason: Optional[str] = None  # why it was blocked
    priority: int = 50                  # lower = higher priority (0-100)


@dataclass
class RuleContext:
    """Everything a rule needs to make a decision."""
    config: AutopilotConfig
    # Lighthouse insights for this campaign (list, may be empty)
    insights: List[Dict[str, Any]]
    # Feature row from campaign_features_daily (full row dict)
    features: Dict[str, Any]
    # All insights for the account (for account-level rules)
    all_insights: List[Dict[str, Any]]
    # All feature rows for all campaigns (for cross-campaign rules)
    all_features: List[Dict[str, Any]]
    # Change log (for cooldown checks) - list of recent changes
    recent_changes: List[Dict[str, Any]] = field(default_factory=list)


def _safe_float(x: Any, default: float = 0.0) -> float:
    if x is None:
        return default
    try:
        return float(x)
    except (TypeError, ValueError):
        return default
