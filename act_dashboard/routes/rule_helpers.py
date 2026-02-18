"""
Rule Helpers - Extract and format rule metadata for dashboard display.

Parses rule docstrings to extract:
- Trigger conditions → Thresholds
- Action descriptions → What the rule does
- Risk levels → Risk tier
- Categories → Budget/Bid/Status/etc.

Chat 21c: Rule visibility system foundation
"""

import re
import inspect
from typing import List, Dict, Any, Optional


def parse_rule_docstring(docstring: str) -> Dict[str, Any]:
    """
    Parse rule function docstring to extract metadata.
    
    Expected format:
        '''
        Brief description line.
        
        Trigger: Condition1 AND Condition2
        Action:  What the rule does
        Risk:    low/medium/high
        '''
    
    Args:
        docstring: Raw docstring from rule function
        
    Returns:
        Dict with extracted metadata:
        {
            'description': 'Brief description',
            'trigger': 'Full trigger text',
            'action': 'What the rule does',
            'risk_tier': 'low',
            'thresholds': ['Condition1', 'Condition2']
        }
    """
    if not docstring:
        return {
            'description': '',
            'trigger': '',
            'action': '',
            'risk_tier': 'unknown',
            'thresholds': []
        }
    
    # Clean docstring
    docstring = inspect.cleandoc(docstring)
    lines = docstring.split('\n')
    
    # Extract first line as description
    description = lines[0].strip() if lines else ''
    
    # Extract sections
    trigger_text = ''
    action_text = ''
    risk_text = ''
    
    for line in lines:
        line = line.strip()
        
        if line.startswith('Trigger:'):
            trigger_text = line.replace('Trigger:', '').strip()
        elif line.startswith('Action:'):
            action_text = line.replace('Action:', '').strip()
        elif line.startswith('Risk:'):
            risk_text = line.replace('Risk:', '').strip()
    
    # Parse thresholds from trigger text
    thresholds = []
    if trigger_text:
        # Split by AND/OR and clean up
        parts = re.split(r'\s+AND\s+|\s+OR\s+', trigger_text, flags=re.IGNORECASE)
        thresholds = [p.strip() for p in parts if p.strip()]
    
    # Extract risk tier (first word of risk text, lowercase)
    risk_tier = 'unknown'
    if risk_text:
        risk_match = re.match(r'(low|medium|high)', risk_text, re.IGNORECASE)
        if risk_match:
            risk_tier = risk_match.group(1).lower()
    
    return {
        'description': description,
        'trigger': trigger_text,
        'action': action_text,
        'risk_tier': risk_tier,
        'thresholds': thresholds
    }


def format_rule_metadata(rule_fn, category: str, rule_id: str = None) -> Dict[str, Any]:
    """
    Format rule function into display metadata.
    
    Args:
        rule_fn: Rule function object
        category: Category (BUDGET/BID/STATUS/KEYWORD/AD/SHOPPING)
        rule_id: Optional rule ID override
        
    Returns:
        Formatted metadata dict for display
    """
    # Parse docstring
    docstring = inspect.getdoc(rule_fn) or ''
    parsed = parse_rule_docstring(docstring)
    
    # Extract rule ID from function name if not provided
    # Example: budget_001_increase_high_roas → BUDGET-001
    if not rule_id:
        func_name = rule_fn.__name__
        # Try to extract number from function name
        num_match = re.search(r'_(\d{3})_', func_name)
        if num_match:
            rule_number = num_match.group(1)
            rule_id = f"{category}-{rule_number}"
        else:
            rule_id = f"{category}-{func_name}"
    
    # Extract rule name from description or function name
    rule_name = parsed['description']
    if not rule_name:
        # Fallback: humanize function name
        func_name = rule_fn.__name__
        # Remove prefix like "budget_001_"
        name_part = re.sub(r'^[a-z]+_\d{3}_', '', func_name)
        rule_name = name_part.replace('_', ' ').title()
    
    return {
        'rule_id': rule_id,
        'name': rule_name,
        'description': parsed['action'] or parsed['description'],
        'category': category,
        'thresholds': parsed['thresholds'],
        'risk_tier': parsed['risk_tier'],
        'enabled': True,  # Placeholder - all rules enabled for now
        'guardrails': [],  # Placeholder - could extract from constitution_refs
        'last_triggered': None,  # Placeholder - requires change log lookup
        'rec_count_week': 0  # Placeholder - requires recommendations count
    }


def extract_rules_from_module(module_name: str, category: str) -> List[Dict[str, Any]]:
    """
    Extract all rule functions from a module.
    
    Args:
        module_name: Module to import (e.g., 'act_autopilot.rules.budget_rules')
        category: Rule category for this module
        
    Returns:
        List of formatted rule metadata dicts
    """
    rules = []
    
    try:
        # Import module
        module = __import__(module_name, fromlist=[''])
        
        # Find all functions in module
        for name, obj in inspect.getmembers(module, inspect.isfunction):
            # Skip private functions and helpers
            if name.startswith('_'):
                continue
            
            # Skip helper functions that don't follow rule naming pattern
            # Rule functions: category_NNN_description OR category_action_NNN
            if not re.search(r'_\d{3}(?:_|$)', name):
                continue
            
            # Format metadata
            rule_meta = format_rule_metadata(obj, category)
            rules.append(rule_meta)
            
    except ImportError as e:
        print(f"[rule_helpers] Warning: Could not import {module_name}: {e}")
    except Exception as e:
        print(f"[rule_helpers] Error extracting rules from {module_name}: {e}")
    
    return rules


def get_rules_for_page(page_type: str, customer_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get all rules for a specific page type.
    
    Args:
        page_type: Page type - 'campaign', 'keyword', 'ad', 'shopping'
        customer_id: Optional customer ID (for future stats lookup)
        
    Returns:
        List of rule metadata dicts, sorted by category then rule_id
    """
    all_rules = []
    
    if page_type == 'campaign':
        # Campaign rules come from 3 modules
        all_rules.extend(extract_rules_from_module('act_autopilot.rules.budget_rules', 'BUDGET'))
        all_rules.extend(extract_rules_from_module('act_autopilot.rules.bid_rules', 'BID'))
        all_rules.extend(extract_rules_from_module('act_autopilot.rules.status_rules', 'STATUS'))
        
    elif page_type == 'keyword':
        # Keyword rules (includes search term rules)
        all_rules.extend(extract_rules_from_module('act_autopilot.rules.keyword_rules', 'KEYWORD'))
        
    elif page_type == 'ad':
        # Ad rules
        all_rules.extend(extract_rules_from_module('act_autopilot.rules.ad_rules', 'AD'))
        
    elif page_type == 'shopping':
        # Shopping rules
        all_rules.extend(extract_rules_from_module('act_autopilot.rules.shopping_rules', 'SHOPPING'))
    
    else:
        print(f"[rule_helpers] Warning: Unknown page_type '{page_type}'")
    
    # Sort by category, then rule_id
    all_rules.sort(key=lambda r: (r['category'], r['rule_id']))
    
    return all_rules


def count_rules_by_category(rules: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Count rules by category.
    
    Args:
        rules: List of rule metadata dicts
        
    Returns:
        Dict of category → count
    """
    counts = {}
    for rule in rules:
        category = rule.get('category', 'OTHER')
        counts[category] = counts.get(category, 0) + 1
    return counts


def get_enabled_rules(rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filter to only enabled rules.
    
    Args:
        rules: List of rule metadata dicts
        
    Returns:
        List of enabled rules only
    """
    return [r for r in rules if r.get('enabled', False)]


def group_rules_by_category(rules: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Group rules by category.
    
    Args:
        rules: List of rule metadata dicts
        
    Returns:
        Dict of category → list of rules
    """
    grouped = {}
    for rule in rules:
        category = rule.get('category', 'OTHER')
        if category not in grouped:
            grouped[category] = []
        grouped[category].append(rule)
    return grouped
