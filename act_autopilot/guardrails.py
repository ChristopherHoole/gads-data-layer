"""
Constitution guardrail validation with logging.

This module enforces the Constitution rules to prevent unsafe optimizations.
All guardrail violations are logged at WARNING level.
"""

from datetime import date, timedelta
from typing import Dict, Optional, List, Tuple
import duckdb

from .models import Recommendation, GuardrailCheck, AutopilotConfig
from .change_log import ChangeLog
from .logging_config import setup_logging

# Initialize logger
logger = setup_logging(__name__)


def _infer_lever(action_type: str) -> str:
    """Infer lever type from action_type"""
    if 'budget' in action_type.lower():
        return 'budget'
    elif 'bid' in action_type.lower() or 'troas' in action_type.lower() or 'tcpa' in action_type.lower():
        return 'bid'
    elif 'status' in action_type.lower() or 'pause' in action_type.lower() or 'enable' in action_type.lower():
        return 'status'
    else:
        return 'unknown'


def run_all_guardrails(
    rec: Recommendation,
    config: AutopilotConfig,
    customer_id: str,
    snapshot_date: date,
    db_path: str = "warehouse.duckdb"
) -> Tuple[bool, Optional[str], List[str]]:
    """
    Run all guardrails and return results as tuple.
    
    Args:
        rec: Recommendation to validate
        config: AutopilotConfig
        customer_id: Customer ID (redundant but kept for compatibility)
        snapshot_date: Date of snapshot
        db_path: Database path
    
    Returns:
        Tuple of (blocked: bool, block_reason: str, guardrails_checked: list)
    """
    blocked_reasons = []
    guardrails_checked = []
    
    # Infer lever from action_type
    lever = _infer_lever(rec.action_type)
    
    # Already blocked check
    guardrails_checked.append("pre_blocked_check")
    if rec.blocked:
        return (True, rec.block_reason or "Already blocked", guardrails_checked)
    
    # Check 1: Low data
    guardrails_checked.append("low_data_check")
    if not check_data_sufficiency(rec):
        reason = "Insufficient data: <30 clicks or <3 conversions"
        blocked_reasons.append(reason)
        logger.warning(f"Campaign {rec.entity_id}: {reason}")
    
    # Check 2: Protected entity
    guardrails_checked.append("protected_entity_check")
    if check_protected_entity(rec, config):
        reason = f"Protected entity: {rec.campaign_name or rec.entity_id}"
        blocked_reasons.append(reason)
        logger.warning(f"Campaign {rec.entity_id}: {reason}")
    
    # Check 3: Cooldown
    guardrails_checked.append("cooldown_check")
    change_log = ChangeLog(db_path)
    if change_log.check_cooldown(
        customer_id=config.customer_id,
        campaign_id=rec.entity_id,
        lever=lever,
        cooldown_days=7
    ):
        reason = f"Cooldown violation: {lever} changed in last 7 days"
        blocked_reasons.append(reason)
        logger.warning(f"Campaign {rec.entity_id}: {reason}")
    
    # Check 4: One-lever rule
    guardrails_checked.append("one_lever_check")
    if change_log.check_one_lever(
        customer_id=config.customer_id,
        campaign_id=rec.entity_id,
        proposed_lever=lever,
        cooldown_days=7
    ):
        opposite = "bid" if lever == "budget" else "budget"
        reason = f"One-lever violation: {opposite} changed in last 7 days"
        blocked_reasons.append(reason)
        logger.warning(f"Campaign {rec.entity_id}: {reason}")
    
    # Check 5: Change magnitude cap
    guardrails_checked.append("change_cap_check")
    if not check_change_cap(rec, config):
        cap_pct = get_change_cap(config.risk_tolerance) * 100
        reason = f"Change cap exceeded: ±{cap_pct}% limit ({config.risk_tolerance})"
        blocked_reasons.append(reason)
        logger.warning(f"Campaign {rec.entity_id}: {reason}")
    
    # Check 6: Daily change budget
    guardrails_checked.append("daily_change_limit_check")
    daily_changes_today = get_daily_change_count(
        customer_id=config.customer_id,
        check_date=snapshot_date,
        db_path=db_path
    )
    if daily_changes_today >= config.max_changes_per_day:
        reason = f"Daily change limit: {daily_changes_today}/{config.max_changes_per_day} used"
        blocked_reasons.append(reason)
        logger.warning(f"Campaign {rec.entity_id}: {reason}")
    
    # Return results
    is_blocked = len(blocked_reasons) > 0
    block_reason_str = "; ".join(blocked_reasons) if blocked_reasons else None
    
    if is_blocked:
        logger.warning(f"Campaign {rec.entity_id}: BLOCKED by {len(blocked_reasons)} guardrails")
    else:
        logger.debug(f"Campaign {rec.entity_id}: All guardrails PASSED")
    
    return (is_blocked, block_reason_str, guardrails_checked)


def check_data_sufficiency(rec: Recommendation) -> bool:
    """
    CONSTITUTION-4-1: Minimum data requirements.
    
    Requires:
        - ≥30 clicks in evaluation window
        - ≥3 conversions in evaluation window
    
    Returns True if sufficient, False otherwise.
    """
    evidence = rec.evidence or {}
    
    clicks = evidence.get('clicks_w7', 0) or evidence.get('clicks_w30', 0)
    conversions = evidence.get('conversions_w7', 0) or evidence.get('conversions_w30', 0)
    
    if clicks < 30:
        logger.debug(f"Low data: {clicks} clicks < 30")
        return False
    
    if conversions < 3:
        logger.debug(f"Low data: {conversions} conversions < 3")
        return False
    
    return True


def check_protected_entity(rec: Recommendation, config: AutopilotConfig) -> bool:
    """
    CONSTITUTION-4-2: Protected entities cannot be changed.
    
    Protected:
        - Brand campaigns (if brand_is_protected = True)
        - Explicit protected campaign IDs
    
    Returns True if protected, False otherwise.
    """
    # Check explicit protected list
    if rec.entity_id in config.protected_entities:
        logger.debug(f"Campaign {rec.entity_id} in protected list")
        return True
    
    # Check brand protection
    if config.brand_is_protected:
        campaign_name = (rec.campaign_name or '').lower()
        if 'brand' in campaign_name:
            logger.debug(f"Campaign {rec.entity_id} is brand campaign")
            return True
    
    return False


def check_change_cap(rec: Recommendation, config: AutopilotConfig) -> bool:
    """
    CONSTITUTION-5-5: Maximum change magnitude.
    
    Caps:
        - conservative: ±5%
        - balanced: ±10%
        - aggressive: ±15%
    
    Returns True if within cap, False otherwise.
    """
    cap = get_change_cap(config.risk_tolerance)
    
    # Get change_pct from rec directly
    change_pct = abs(rec.change_pct) if rec.change_pct else 0.0
    
    if change_pct > cap:
        logger.debug(f"Change {change_pct:.1%} exceeds cap {cap:.1%}")
        return False
    
    return True


def get_change_cap(risk_tolerance: str) -> float:
    """Get maximum change percentage for risk tolerance."""
    caps = {
        'conservative': 0.05,  # ±5%
        'balanced': 0.10,      # ±10%
        'aggressive': 0.15     # ±15%
    }
    return caps.get(risk_tolerance, 0.05)  # Default: conservative


def get_daily_change_count(
    customer_id: str,
    check_date: date,
    db_path: str = "warehouse.duckdb"
) -> int:
    """
    Get number of changes executed today.
    
    Used for CONSTITUTION-5-6: Daily change budget enforcement.
    """
    con = duckdb.connect(db_path, read_only=True)
    
    try:
        result = con.execute("""
            SELECT COUNT(*) as change_count
            FROM analytics.change_log
            WHERE customer_id = ?
              AND change_date = ?
        """, [customer_id, check_date]).fetchone()
        
        count = result[0] if result else 0
        logger.debug(f"Daily changes for {check_date}: {count}")
        return count
        
    except Exception as e:
        logger.error(f"Error querying daily change count: {e}")
        return 0
    finally:
        con.close()


def check_spend_caps(
    customer_id: str,
    proposed_budget_micros: int,
    snapshot_date: date,
    daily_cap: float,
    monthly_cap: float,
    db_path: str = "warehouse.duckdb"
) -> Dict[str, any]:
    """
    CONSTITUTION-2-2: Check if proposed budget exceeds spend caps.
    
    Returns:
        {
            'valid': bool,
            'reason': str (if invalid),
            'daily_projected': float,
            'monthly_projected': float
        }
    """
    logger.debug(f"Checking spend caps for customer {customer_id}")
    
    con = duckdb.connect(db_path, read_only=True)
    
    try:
        # Get current month's spend
        month_start = date(snapshot_date.year, snapshot_date.month, 1)
        
        result = con.execute("""
            SELECT 
                SUM(cost) as month_spend,
                COUNT(DISTINCT date) as days_in_month
            FROM analytics.campaign_daily
            WHERE customer_id = ?
              AND date >= ?
              AND date <= ?
        """, [customer_id, month_start, snapshot_date]).fetchone()
        
        month_spend = result[0] or 0.0
        days_elapsed = result[1] or 1
        
        # Calculate days remaining in month
        if snapshot_date.month == 12:
            next_month = date(snapshot_date.year + 1, 1, 1)
        else:
            next_month = date(snapshot_date.year, snapshot_date.month + 1, 1)
        
        days_remaining = (next_month - snapshot_date).days
        total_days = days_elapsed + days_remaining
        
        # Project monthly spend with new budget
        proposed_budget = proposed_budget_micros / 1_000_000
        daily_rate_after_change = proposed_budget
        projected_month_spend = month_spend + (daily_rate_after_change * days_remaining)
        
        logger.debug(f"Monthly projection: {projected_month_spend:.2f} / {monthly_cap:.2f}")
        logger.debug(f"Daily budget: {proposed_budget:.2f} / {daily_cap:.2f}")
        
        # Check daily cap
        if proposed_budget > daily_cap:
            reason = f"Exceeds daily cap: £{proposed_budget:.2f} > £{daily_cap:.2f}"
            logger.warning(f"Customer {customer_id}: {reason}")
            return {
                'valid': False,
                'reason': reason,
                'daily_projected': proposed_budget,
                'monthly_projected': projected_month_spend
            }
        
        # Check monthly cap
        if projected_month_spend > monthly_cap:
            reason = f"Exceeds monthly cap projection: £{projected_month_spend:.2f} > £{monthly_cap:.2f}"
            logger.warning(f"Customer {customer_id}: {reason}")
            return {
                'valid': False,
                'reason': reason,
                'daily_projected': proposed_budget,
                'monthly_projected': projected_month_spend
            }
        
        logger.debug("Spend caps: PASSED")
        return {
            'valid': True,
            'reason': None,
            'daily_projected': proposed_budget,
            'monthly_projected': projected_month_spend
        }
        
    except Exception as e:
        logger.error(f"Error checking spend caps: {e}")
        return {
            'valid': False,
            'reason': f"Error checking spend caps: {e}",
            'daily_projected': 0,
            'monthly_projected': 0
        }
    finally:
        con.close()
