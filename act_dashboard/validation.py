"""
Input validation utilities for API endpoints.

Validates recommendation data, execution requests, and prevents invalid/malicious inputs.
"""

from typing import Dict, Any, Tuple, List


# Allowed action types for execution
ALLOWED_ACTION_TYPES = {
    # Keyword actions
    'pause_keyword',
    'update_keyword_bid',
    'add_keyword',
    'add_negative_keyword',
    
    # Ad actions
    'pause_ad',
    'review_ad',
    'asset_insight',
    'review_ad_group',
    
    # Shopping actions
    'update_product_bid',
    'review_product',
    'pause_product',
}


def validate_recommendation_dict(rec: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate a recommendation dictionary has required fields.
    
    Args:
        rec: Recommendation dictionary to validate
        
    Returns:
        (is_valid, error_message) tuple
    """
    # Required fields
    required_fields = [
        'rule_id',
        'entity_type',
        'entity_id',
        'action_type',
    ]
    
    for field in required_fields:
        if field not in rec:
            return False, f"Missing required field: {field}"
        
        # Check not None and not empty string
        if rec[field] is None or (isinstance(rec[field], str) and not rec[field].strip()):
            return False, f"Field '{field}' cannot be empty"
    
    # Validate action_type is allowed
    action_type = rec['action_type']
    if action_type not in ALLOWED_ACTION_TYPES:
        return False, f"Invalid action_type: '{action_type}'. Allowed types: {sorted(ALLOWED_ACTION_TYPES)}"
    
    # Validate entity_type
    allowed_entity_types = ['keyword', 'ad', 'product', 'campaign', 'ad_group', 'search_term']
    if rec['entity_type'] not in allowed_entity_types:
        return False, f"Invalid entity_type: '{rec['entity_type']}'"
    
    return True, ""


def validate_execution_request(data: Dict[str, Any], recommendations: List[Dict]) -> Tuple[bool, str]:
    """
    Validate an execution request payload.
    
    Args:
        data: Request JSON data
        recommendations: Available recommendations list
        
    Returns:
        (is_valid, error_message) tuple
    """
    # Check recommendation_id exists
    if 'recommendation_id' not in data:
        return False, "Missing required field: recommendation_id"
    
    rec_id = data['recommendation_id']
    
    # Validate is integer
    if not isinstance(rec_id, int):
        return False, f"recommendation_id must be an integer, got {type(rec_id).__name__}"
    
    # Validate is in range
    if rec_id < 0:
        return False, f"recommendation_id must be >= 0, got {rec_id}"
    
    if rec_id >= len(recommendations):
        return False, f"recommendation_id {rec_id} out of range (max: {len(recommendations) - 1})"
    
    # Validate dry_run is boolean if present
    if 'dry_run' in data and not isinstance(data['dry_run'], bool):
        return False, f"dry_run must be a boolean, got {type(data['dry_run']).__name__}"
    
    return True, ""


def validate_batch_execution_request(data: Dict[str, Any], recommendations: List[Dict]) -> Tuple[bool, str]:
    """
    Validate a batch execution request payload.
    
    Args:
        data: Request JSON data
        recommendations: Available recommendations list
        
    Returns:
        (is_valid, error_message) tuple
    """
    # Check recommendation_ids exists
    if 'recommendation_ids' not in data:
        return False, "Missing required field: recommendation_ids"
    
    rec_ids = data['recommendation_ids']
    
    # Validate is list
    if not isinstance(rec_ids, list):
        return False, f"recommendation_ids must be a list, got {type(rec_ids).__name__}"
    
    # Validate not empty
    if not rec_ids:
        return False, "recommendation_ids cannot be empty"
    
    # Validate max batch size (prevent DoS)
    MAX_BATCH_SIZE = 100
    if len(rec_ids) > MAX_BATCH_SIZE:
        return False, f"Batch size {len(rec_ids)} exceeds maximum {MAX_BATCH_SIZE}"
    
    # Validate each ID
    for i, rec_id in enumerate(rec_ids):
        if not isinstance(rec_id, int):
            return False, f"recommendation_ids[{i}] must be an integer, got {type(rec_id).__name__}"
        
        if rec_id < 0:
            return False, f"recommendation_ids[{i}] must be >= 0, got {rec_id}"
        
        if rec_id >= len(recommendations):
            return False, f"recommendation_ids[{i}] = {rec_id} out of range (max: {len(recommendations) - 1})"
    
    # Check for duplicates
    if len(rec_ids) != len(set(rec_ids)):
        return False, "recommendation_ids contains duplicates"
    
    # Validate dry_run is boolean if present
    if 'dry_run' in data and not isinstance(data['dry_run'], bool):
        return False, f"dry_run must be a boolean, got {type(data['dry_run']).__name__}"
    
    return True, ""


def sanitize_string(s: str, max_length: int = 500) -> str:
    """
    Sanitize a string input by trimming and limiting length.
    
    Args:
        s: String to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string
    """
    if not isinstance(s, str):
        return str(s)
    
    # Trim whitespace
    s = s.strip()
    
    # Limit length
    if len(s) > max_length:
        s = s[:max_length]
    
    return s
