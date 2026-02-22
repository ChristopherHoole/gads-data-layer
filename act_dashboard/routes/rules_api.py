"""
Rules API — CRUD routes for rules_config.json.

Chat 26 (M5): UI config layer for campaign optimization rules.
Reads/writes act_autopilot/rules_config.json only.
Does NOT touch act_autopilot/rules/*.py (execution layer).

Routes:
  GET  /api/rules                     — return all rules as JSON
  POST /api/rules/add                 — add a new rule
  PUT  /api/rules/<rule_id>/update    — update an existing rule
  PUT  /api/rules/<rule_id>/toggle    — toggle enabled/disabled
  DELETE /api/rules/<rule_id>         — delete a rule
"""

import json
import os
import logging
from datetime import datetime
from pathlib import Path
from flask import Blueprint, jsonify, request
from act_dashboard.auth import login_required
from act_dashboard.routes.shared import get_page_context, get_db_connection

logger = logging.getLogger(__name__)

bp = Blueprint('rules_api', __name__)

# Path to rules config file
RULES_CONFIG_PATH = Path(__file__).parent.parent.parent / 'act_autopilot' / 'rules_config.json'

VALID_RULE_TYPES = {'budget', 'bid', 'status'}
VALID_OPERATORS = {'gt', 'lt', 'gte', 'lte', 'eq'}
VALID_UNITS = {'x_target', 'absolute'}
VALID_DIRECTIONS = {'increase', 'decrease', 'hold', 'flag'}
VALID_COOLDOWNS = {7, 14, 30}
VALID_RISK_LEVELS = {'low', 'medium', 'high', 'unknown'}


# ─────────────────────────────────────────────────────────────────────────────
# File I/O helpers
# ─────────────────────────────────────────────────────────────────────────────

def load_rules() -> list:
    """Load rules from rules_config.json. Returns empty list on error."""
    try:
        if not RULES_CONFIG_PATH.exists():
            logger.warning(f"rules_config.json not found at {RULES_CONFIG_PATH}")
            return []
        with open(RULES_CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"[rules_api] Error loading rules: {e}")
        return []


def save_rules(rules: list) -> bool:
    """Save rules list to rules_config.json. Returns True on success."""
    try:
        with open(RULES_CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(rules, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"[rules_api] Error saving rules: {e}")
        return False


def next_rule_number(rules: list, rule_type: str) -> int:
    """Return the next sequential rule number for a given type."""
    existing = [r['rule_number'] for r in rules if r.get('rule_type') == rule_type]
    return max(existing, default=0) + 1


def find_rule(rules: list, rule_id: str) -> tuple:
    """
    Find a rule by ID. Returns (index, rule_dict) or (None, None).
    """
    for i, rule in enumerate(rules):
        if rule.get('rule_id') == rule_id:
            return i, rule
    return None, None


def validate_rule(data: dict) -> tuple:
    """
    Validate rule payload. Returns (is_valid: bool, error_message: str).
    Only validates fields that are present — used for both add and update.
    """
    rule_type = data.get('rule_type')
    if rule_type and rule_type not in VALID_RULE_TYPES:
        return False, f"Invalid rule_type '{rule_type}'. Must be: budget, bid, status"

    direction = data.get('action_direction')
    if direction and direction not in VALID_DIRECTIONS:
        return False, f"Invalid action_direction '{direction}'"

    magnitude = data.get('action_magnitude')
    if magnitude is not None:
        try:
            m = float(magnitude)
            if m < 0 or m > 20:
                return False, "action_magnitude must be between 0 and 20"
        except (TypeError, ValueError):
            return False, "action_magnitude must be a number"

    cooldown = data.get('cooldown_days')
    if cooldown is not None:
        if int(cooldown) not in VALID_COOLDOWNS:
            return False, f"cooldown_days must be 7, 14, or 30"

    risk = data.get('risk_level')
    if risk and risk not in VALID_RISK_LEVELS:
        return False, f"Invalid risk_level '{risk}'"

    op = data.get('condition_operator')
    if op and op not in VALID_OPERATORS:
        return False, f"Invalid condition_operator '{op}'"

    op2 = data.get('condition_2_operator')
    if op2 and op2 not in VALID_OPERATORS:
        return False, f"Invalid condition_2_operator '{op2}'"

    return True, ''


# ─────────────────────────────────────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────────────────────────────────────

@bp.route('/api/rules', methods=['GET'])
@login_required
def get_rules():
    """Return all rules as JSON array."""
    rules = load_rules()
    return jsonify({'success': True, 'rules': rules, 'count': len(rules)})


@bp.route('/api/rules/add', methods=['POST'])
@login_required
def add_rule():
    """
    Add a new rule.

    Required fields: rule_type, name, action_direction
    Optional: scope, campaign_id, condition_*, cooldown_days, risk_level, enabled
    """
    data = request.get_json(silent=True) or {}

    # Required fields
    missing = [f for f in ['rule_type', 'name', 'action_direction'] if not data.get(f)]
    if missing:
        return jsonify({'success': False, 'message': f"Missing required fields: {', '.join(missing)}"}), 400

    is_valid, err = validate_rule(data)
    if not is_valid:
        return jsonify({'success': False, 'message': err}), 400

    rules = load_rules()
    rule_type = data['rule_type']
    num = next_rule_number(rules, rule_type)
    now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')

    new_rule = {
        'rule_id': f"{rule_type}_{num}",
        'rule_type': rule_type,
        'rule_number': num,
        'display_name': f"{rule_type.capitalize()} {num}",
        'name': str(data['name']).strip(),
        'scope': data.get('scope', 'blanket'),
        'campaign_id': data.get('campaign_id') or None,
        'condition_metric': data.get('condition_metric') or None,
        'condition_operator': data.get('condition_operator') or None,
        'condition_value': float(data['condition_value']) if data.get('condition_value') is not None else None,
        'condition_unit': data.get('condition_unit') or None,
        'condition_2_metric': data.get('condition_2_metric') or None,
        'condition_2_operator': data.get('condition_2_operator') or None,
        'condition_2_value': float(data['condition_2_value']) if data.get('condition_2_value') is not None else None,
        'condition_2_unit': data.get('condition_2_unit') or None,
        'action_direction': data['action_direction'],
        'action_magnitude': float(data.get('action_magnitude', 0)),
        'risk_level': data.get('risk_level', 'unknown'),
        'cooldown_days': int(data.get('cooldown_days', 7)),
        'enabled': bool(data.get('enabled', True)),
        'created_at': now,
        'updated_at': now,
    }

    rules.append(new_rule)

    if not save_rules(rules):
        return jsonify({'success': False, 'message': 'Failed to save rules file'}), 500

    logger.info(f"[rules_api] Added rule: {new_rule['rule_id']}")
    return jsonify({'success': True, 'rule': new_rule, 'message': f"Rule '{new_rule['display_name']}' created"})


@bp.route('/api/rules/<rule_id>/update', methods=['PUT'])
@login_required
def update_rule(rule_id):
    """Update an existing rule by rule_id."""
    data = request.get_json(silent=True) or {}

    is_valid, err = validate_rule(data)
    if not is_valid:
        return jsonify({'success': False, 'message': err}), 400

    rules = load_rules()
    idx, existing = find_rule(rules, rule_id)

    if idx is None:
        return jsonify({'success': False, 'message': f"Rule '{rule_id}' not found"}), 404

    now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')

    # Updatable fields — do not allow changing rule_id, rule_type, rule_number, display_name
    updatable = [
        'name', 'scope', 'campaign_id',
        'condition_metric', 'condition_operator', 'condition_value', 'condition_unit',
        'condition_2_metric', 'condition_2_operator', 'condition_2_value', 'condition_2_unit',
        'action_direction', 'action_magnitude', 'risk_level', 'cooldown_days', 'enabled'
    ]

    for field in updatable:
        if field in data:
            val = data[field]
            if field in ('condition_value', 'condition_2_value', 'action_magnitude') and val is not None:
                val = float(val)
            elif field == 'cooldown_days' and val is not None:
                val = int(val)
            elif field == 'enabled':
                val = bool(val)
            existing[field] = val

    existing['updated_at'] = now
    rules[idx] = existing

    if not save_rules(rules):
        return jsonify({'success': False, 'message': 'Failed to save rules file'}), 500

    logger.info(f"[rules_api] Updated rule: {rule_id}")
    return jsonify({'success': True, 'rule': existing, 'message': f"Rule '{existing['display_name']}' updated"})


@bp.route('/api/rules/<rule_id>/toggle', methods=['PUT'])
@login_required
def toggle_rule(rule_id):
    """Toggle a rule's enabled/disabled state."""
    rules = load_rules()
    idx, existing = find_rule(rules, rule_id)

    if idx is None:
        return jsonify({'success': False, 'message': f"Rule '{rule_id}' not found"}), 404

    existing['enabled'] = not existing.get('enabled', True)
    existing['updated_at'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
    rules[idx] = existing

    if not save_rules(rules):
        return jsonify({'success': False, 'message': 'Failed to save rules file'}), 500

    state = 'enabled' if existing['enabled'] else 'disabled'
    logger.info(f"[rules_api] Toggled rule {rule_id} → {state}")
    return jsonify({
        'success': True,
        'rule_id': rule_id,
        'enabled': existing['enabled'],
        'message': f"Rule '{existing['display_name']}' {state}"
    })


@bp.route('/api/rules/<rule_id>', methods=['DELETE'])
@login_required
def delete_rule(rule_id):
    """Delete a rule by rule_id."""
    rules = load_rules()
    idx, existing = find_rule(rules, rule_id)

    if idx is None:
        return jsonify({'success': False, 'message': f"Rule '{rule_id}' not found"}), 404

    display_name = existing.get('display_name', rule_id)
    rules.pop(idx)

    if not save_rules(rules):
        return jsonify({'success': False, 'message': 'Failed to save rules file'}), 500

    logger.info(f"[rules_api] Deleted rule: {rule_id}")
    return jsonify({'success': True, 'rule_id': rule_id, 'message': f"Rule '{display_name}' deleted"})


@bp.route('/api/campaigns-list', methods=['GET'])
@login_required
def get_campaigns_list():
    """
    Return distinct campaign names and IDs for the campaign picker dropdown.
    Uses the current client's warehouse (ro.analytics.campaign_daily).
    """
    try:
        config, _, _ = get_page_context()
        conn = get_db_connection(config)
        rows = conn.execute("""
            SELECT DISTINCT campaign_id, campaign_name
            FROM ro.analytics.campaign_daily
            WHERE customer_id = ?
              AND campaign_status = 'ENABLED'
            ORDER BY campaign_name ASC
        """, [config.customer_id]).fetchall()
        conn.close()
        campaigns = [{'campaign_id': str(r[0]), 'campaign_name': r[1]} for r in rows]
        return jsonify({'success': True, 'campaigns': campaigns})
    except Exception as e:
        logger.error(f"[rules_api] Error loading campaigns list: {e}")
        return jsonify({'success': False, 'campaigns': [], 'message': str(e)})
