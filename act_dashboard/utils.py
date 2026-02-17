"""
Utility functions for the Ads Control Tower dashboard.

This module provides helper functions for data conversion and processing.
"""

from typing import Dict, Any, Optional
from act_autopilot.models import Recommendation


def dict_to_recommendation(rec_dict: Dict[str, Any]) -> Recommendation:
    """
    Convert a recommendation dictionary to a Recommendation object.
    
    This is needed because:
    - Dashboard routes generate recommendations as dicts
    - Executor expects Recommendation objects with attributes (rec.action_type)
    - Need conversion layer between frontend and backend
    
    Args:
        rec_dict: Dictionary containing recommendation data
        
    Returns:
        Recommendation object
        
    Raises:
        ValueError: If required fields are missing
        TypeError: If field types are invalid
        
    Example:
        >>> rec_dict = {
        ...     'rule_id': 'KW-PAUSE-001',
        ...     'action_type': 'pause_keyword',
        ...     'entity_id': 12345,
        ...     'risk_tier': 'low'
        ... }
        >>> rec_obj = dict_to_recommendation(rec_dict)
        >>> rec_obj.action_type  # Access as attribute
        'pause_keyword'
    """
    
    # Validate required fields (fields WITHOUT defaults in Recommendation class)
    required_fields = [
        'rule_id',
        'rule_name', 
        'entity_type',
        'entity_id',
        'action_type',
        'risk_tier'  # risk_tier is REQUIRED, not optional!
    ]
    
    missing_fields = [f for f in required_fields if f not in rec_dict]
    if missing_fields:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
    
    # Extract required fields
    try:
        rule_id = str(rec_dict['rule_id'])
        rule_name = str(rec_dict['rule_name'])
        entity_type = str(rec_dict['entity_type'])
        
        # entity_id can be int or str depending on entity type
        entity_id = rec_dict['entity_id']
        if isinstance(entity_id, (int, str)):
            entity_id = str(entity_id)  # Standardize to string
        else:
            raise TypeError(f"entity_id must be int or str, got {type(entity_id)}")
        
        action_type = str(rec_dict['action_type'])
        
        # risk_tier is REQUIRED
        risk_tier = str(rec_dict['risk_tier'])
        if risk_tier not in ['low', 'medium', 'high']:
            raise ValueError(f"Invalid risk_tier: {risk_tier}. Must be 'low', 'medium', or 'high'")
        
    except (KeyError, ValueError, TypeError) as e:
        raise ValueError(f"Invalid required field: {e}")
    
    # Extract optional fields with defaults
    # These are optional in the Recommendation class (have defaults)
    
    confidence = float(rec_dict.get('confidence', 0.0))
    
    current_value = rec_dict.get('current_value', None)
    if current_value is not None:
        try:
            current_value = float(current_value)
        except (ValueError, TypeError):
            current_value = None
    
    recommended_value = rec_dict.get('recommended_value', None)
    if recommended_value is not None:
        try:
            recommended_value = float(recommended_value)
        except (ValueError, TypeError):
            recommended_value = None
    
    change_pct = rec_dict.get('change_pct', None)
    if change_pct is not None:
        try:
            change_pct = float(change_pct)
        except (ValueError, TypeError):
            change_pct = None
    
    rationale = str(rec_dict.get('rationale', ''))
    
    campaign_name = rec_dict.get('campaign_name', None)
    if campaign_name is not None:
        campaign_name = str(campaign_name)
    
    blocked = rec_dict.get('blocked', False)
    if not isinstance(blocked, bool):
        blocked = bool(blocked)
    
    block_reason = rec_dict.get('block_reason', None)
    if block_reason is not None:
        block_reason = str(block_reason)
    
    priority = int(rec_dict.get('priority', 50))  # Default to medium priority
    
    # constitution_refs and guardrails_checked are lists
    constitution_refs = rec_dict.get('constitution_refs', [])
    if not isinstance(constitution_refs, list):
        constitution_refs = []
    
    guardrails_checked = rec_dict.get('guardrails_checked', [])
    if not isinstance(guardrails_checked, list):
        guardrails_checked = []
    
    # evidence is optional (can be None)
    evidence = rec_dict.get('evidence', None)
    if evidence is not None and not isinstance(evidence, dict):
        raise TypeError(f"evidence must be dict or None, got {type(evidence)}")
    
    # triggering_diagnosis is optional
    triggering_diagnosis = rec_dict.get('triggering_diagnosis', None)
    if triggering_diagnosis is not None:
        triggering_diagnosis = str(triggering_diagnosis)
    
    # triggering_confidence is optional with default 0.0
    triggering_confidence = float(rec_dict.get('triggering_confidence', 0.0))
    
    expected_impact = str(rec_dict.get('expected_impact', ''))
    
    # Create Recommendation object
    try:
        recommendation = Recommendation(
            # Required fields (no defaults)
            rule_id=rule_id,
            rule_name=rule_name,
            entity_type=entity_type,
            entity_id=entity_id,
            action_type=action_type,
            risk_tier=risk_tier,
            # Optional fields (with defaults)
            confidence=confidence,
            current_value=current_value,
            recommended_value=recommended_value,
            change_pct=change_pct,
            rationale=rationale,
            campaign_name=campaign_name,
            blocked=blocked,
            block_reason=block_reason,
            priority=priority,
            constitution_refs=constitution_refs,
            guardrails_checked=guardrails_checked,
            evidence=evidence,
            triggering_diagnosis=triggering_diagnosis,
            triggering_confidence=triggering_confidence,
            expected_impact=expected_impact
        )
        return recommendation
        
    except Exception as e:
        raise ValueError(f"Failed to create Recommendation object: {e}")


def validate_recommendation_dict(rec_dict: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validate a recommendation dictionary without converting it.
    
    Useful for checking if a dict can be converted before attempting conversion.
    
    Args:
        rec_dict: Dictionary to validate
        
    Returns:
        Tuple of (is_valid, error_message)
        - is_valid: True if valid, False if invalid
        - error_message: None if valid, error description if invalid
        
    Example:
        >>> is_valid, error = validate_recommendation_dict(rec_dict)
        >>> if not is_valid:
        ...     print(f"Invalid: {error}")
    """
    
    # Check if dict
    if not isinstance(rec_dict, dict):
        return False, f"Expected dict, got {type(rec_dict)}"
    
    # Check required fields (fields WITHOUT defaults in Recommendation class)
    required_fields = [
        'rule_id',
        'rule_name',
        'entity_type',
        'entity_id',
        'action_type',
        'risk_tier'  # risk_tier is REQUIRED!
    ]
    
    missing_fields = [f for f in required_fields if f not in rec_dict]
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    
    # Check evidence is dict (if provided - it's optional)
    if 'evidence' in rec_dict and rec_dict['evidence'] is not None:
        if not isinstance(rec_dict['evidence'], dict):
            return False, f"evidence must be dict, got {type(rec_dict['evidence'])}"
    
    # Check risk_tier is valid
    if rec_dict['risk_tier'] not in ['low', 'medium', 'high']:
        return False, f"Invalid risk_tier: {rec_dict['risk_tier']}. Must be 'low', 'medium', or 'high'"
    
    # All checks passed
    return True, None
