"""
Recommendations routes — Chat 29 (M8) + Chat 47 Multi-Entity Extension

Changes from Chat 29:
  - /changes route REMOVED — now in act_dashboard/routes/changes.py
  - _load_monitoring_days() now returns dict with monitoring_days + monitoring_minutes
  - Accept/modify routes updated to use monitoring_minutes for fast-test deadline
  - reverted_recs query added
  - last_run bug fixed in _get_summary()
  - /recommendations/cards extended with reverted array
  - /recommendations/data fixed to include last_run
  - reverted_recs passed to template

Changes from Chat 47:
  - _ensure_changes_table() extended with entity_type, entity_id columns
  - _load_rec_by_id() extended to SELECT entity_type, entity_id, entity_name
  - _write_changes_row() extended to INSERT entity_type, entity_id
  - _get_recommendations_data() extended to SELECT entity_type, entity_id, entity_name
  - Backward compatibility maintained for campaign_id-only rows
"""

import json
import os
from datetime import datetime, timedelta
from typing import Optional

import duckdb
from flask import Blueprint, jsonify, render_template, request, session

from act_dashboard.auth import login_required
from act_dashboard.routes.shared import (
    get_available_clients,
    get_current_config,
    get_db_connection,
)

bp = Blueprint("recommendations", __name__)

# Path to rules config — relative to this file's package root
_RULES_CONFIG_PATH = os.path.join(
    os.path.dirname(__file__),        # act_dashboard/routes/
    "..", "..", "act_autopilot",       # act_autopilot/
    "rules_config.json"
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_action_label(rec: dict) -> str:
    """
    Generate entity-aware action label for recommendation.
    
    Database stores:
        - action_direction: 'increase', 'decrease', 'pause', 'flag', 'hold'
        - rule_type: 'budget', 'bid', 'status'
        - entity_type: 'campaign', 'keyword', 'shopping', 'ad_group'
    
    Returns human-readable label combining all three fields.
    """
    entity_type = rec.get('entity_type', 'campaign')
    action_direction = rec.get('action_direction', '')
    action_magnitude = rec.get('action_magnitude', 0)
    rule_type = rec.get('rule_type', '')
    
    action_type = rec.get('action_type', '')

    # Campaign actions
    if entity_type == 'campaign':
        if action_direction == 'increase':
            if rule_type == 'budget':
                return f"Increase daily budget by {action_magnitude}%"
            elif rule_type == 'bid':
                if 'max_cpc' in action_type:
                    return f"Increase Max CPC cap by {action_magnitude}%"
                elif 'tcpa' in action_type or 'target_cpa' in action_type:
                    return f"Increase tCPA target by {action_magnitude}%"
                else:
                    return f"Increase tROAS target by {action_magnitude}%"
        elif action_direction == 'decrease':
            if rule_type == 'budget':
                return f"Decrease daily budget by {action_magnitude}%"
            elif rule_type == 'bid':
                if 'max_cpc' in action_type:
                    return f"Lower Max CPC cap by {action_magnitude}%"
                elif 'tcpa' in action_type or 'target_cpa' in action_type:
                    return f"Decrease tCPA target by {action_magnitude}%"
                else:
                    return f"Decrease tROAS target by {action_magnitude}%"
        elif action_direction == 'pause':
            return "Pause campaign"
        elif action_direction == 'enable':
            return "Enable campaign"
        elif action_direction == 'flag':
            return "Flag campaign for review"
        elif action_direction == 'hold':
            return f"Hold {'budget' if rule_type == 'budget' else 'bid target'} — no change"
    
    # Keyword actions
    elif entity_type == 'keyword':
        if action_direction == 'pause':
            return "Pause"
        elif action_direction == 'enable':
            return "Enable keyword"
        elif action_direction == 'increase':
            return f"Increase keyword bid by {action_magnitude}%"
        elif action_direction == 'decrease':
            return f"Decrease keyword bid by {action_magnitude}%"
        elif action_direction == 'flag':
            return "Flag keyword for review"
    
    # Shopping actions
    elif entity_type == 'shopping':
        if action_direction == 'increase':
            if rule_type == 'budget':
                return f"Increase shopping budget by {action_magnitude}%"
            elif rule_type == 'bid':
                if 'max_cpc' in action_type:
                    return f"Increase Max CPC cap by {action_magnitude}%"
                elif 'tcpa' in action_type or 'target_cpa' in action_type:
                    return f"Increase tCPA target by {action_magnitude}%"
                else:
                    return f"Increase shopping tROAS by {action_magnitude}%"
        elif action_direction == 'decrease':
            if rule_type == 'budget':
                return f"Decrease shopping budget by {action_magnitude}%"
            elif rule_type == 'bid':
                if 'max_cpc' in action_type:
                    return f"Lower Max CPC cap by {action_magnitude}%"
                elif 'tcpa' in action_type or 'target_cpa' in action_type:
                    return f"Decrease tCPA target by {action_magnitude}%"
                else:
                    return f"Decrease shopping tROAS by {action_magnitude}%"
        elif action_direction == 'pause':
            return "Pause shopping campaign"
        elif action_direction == 'enable':
            return "Enable shopping campaign"
        elif action_direction == 'flag':
            return "Flag shopping campaign for review"
    
    # Ad Group actions
    elif entity_type == 'ad_group':
        if action_direction == 'pause':
            return "Pause ad group"
        elif action_direction == 'enable':
            return "Enable ad group"
        elif action_direction == 'increase':
            return f"Increase ad group bid by {action_magnitude}%"
        elif action_direction == 'decrease':
            return f"Decrease ad group bid by {action_magnitude}%"
        elif action_direction == 'flag':
            return "Flag ad group for review"
    
    # Final fallback
    if action_magnitude and action_magnitude > 0:
        return f"{action_direction.replace('_', ' ').title()} by {action_magnitude}%"
    else:
        return action_direction.replace('_', ' ').title()



# Register as Jinja template filter
@bp.app_template_filter('action_label')
def action_label_filter(rec):
    """Jinja2 template filter wrapper for get_action_label."""
    return get_action_label(rec)


def _ensure_changes_table(conn):
    """
    Create the writable changes table in warehouse.duckdb if it doesn't exist.
    
    Chat 47: Extended with entity_type, entity_id columns for multi-entity support.
    """
    conn.execute("""
        CREATE SEQUENCE IF NOT EXISTS changes_seq START 1
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS changes (
            change_id       INTEGER DEFAULT nextval('changes_seq'),
            customer_id     VARCHAR NOT NULL,
            campaign_id     VARCHAR,
            campaign_name   VARCHAR,
            entity_type     VARCHAR,
            entity_id       VARCHAR,
            rule_id         VARCHAR,
            action_type     VARCHAR,
            old_value       DOUBLE,
            new_value       DOUBLE,
            justification   VARCHAR,
            executed_by     VARCHAR,
            executed_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            dry_run         BOOLEAN DEFAULT FALSE,
            status          VARCHAR DEFAULT 'completed'
        )
    """)


def _load_monitoring_days(rule_id):
    """
    Return monitoring config for the given rule_id.
    - DB rules (rule_id starts with "db_campaign_"): query cooldown_days from warehouse.duckdb
    - JSON rules (e.g. "budget_1"): read from rules_config.json
    Returns dict: {"monitoring_days": int, "monitoring_minutes": int}
    Returns {"monitoring_days": 0, "monitoring_minutes": 0} if rule not found.
    """
    if rule_id.startswith("db_campaign_"):
        try:
            db_id = int(rule_id.split("db_campaign_")[1])
            conn = duckdb.connect("warehouse.duckdb")
            try:
                row = conn.execute("SELECT cooldown_days FROM rules WHERE id = ?", [db_id]).fetchone()
            finally:
                conn.close()
            if row:
                cooldown_days = int(row[0])
                print("[RECOMMENDATIONS] DB rule {} monitoring_days={}".format(rule_id, cooldown_days))
                return {"monitoring_days": cooldown_days, "monitoring_minutes": 0}
        except Exception as e:
            print("[RECOMMENDATIONS] Could not load DB rule {}: {}".format(rule_id, e))
        return {"monitoring_days": 0, "monitoring_minutes": 0}

    try:
        path = os.path.normpath(_RULES_CONFIG_PATH)
        with open(path, "r") as f:
            rules = json.load(f)
        for rule in rules:
            if rule.get("rule_id") == rule_id:
                return {
                    "monitoring_days":    int(rule.get("monitoring_days", 0)),
                    "monitoring_minutes": int(rule.get("monitoring_minutes", 0)),
                }
    except Exception as e:
        print("[RECOMMENDATIONS] Could not load rules_config.json: {}".format(e))
    return {"monitoring_days": 0, "monitoring_minutes": 0}


def _build_rule_name_map():
    """
    Build a dict of rule_id -> rule_name from both sources:
    - DB rules table: db_campaign_N -> rule name
    - JSON rules_config.json: rule_id -> rule name

    Used by _get_recommendations_data() to enrich rec dicts with rule_name.
    """
    name_map = {}

    # Load JSON rules
    try:
        path = os.path.normpath(_RULES_CONFIG_PATH)
        with open(path, "r") as f:
            rules = json.load(f)
        for rule in rules:
            rule_id = rule.get("rule_id")
            name = rule.get("name") or rule.get("display_name") or rule_id
            if rule_id:
                name_map[rule_id] = name
    except Exception as e:
        print("[RECOMMENDATIONS] Could not load rules_config.json for name map: {}".format(e))

    # Load DB rules (campaign entity)
    try:
        import duckdb as _duckdb
        conn = _duckdb.connect("warehouse.duckdb")
        rows = conn.execute(
            "SELECT id, name FROM rules WHERE entity_type = 'campaign' "
            "AND rule_or_flag = 'rule' AND is_template = FALSE"
        ).fetchall()
        conn.close()
        for row in rows:
            db_key = "db_campaign_{}".format(row[0])
            name_map[db_key] = row[1]
    except Exception as e:
        print("[RECOMMENDATIONS] Could not load DB rule names: {}".format(e))

    return name_map


def _load_rec_by_id(conn, rec_id, customer_id):
    """
    Load a single recommendation row by rec_id + customer_id.
    Returns dict or None.
    
    Chat 47: Extended to SELECT entity_type, entity_id, entity_name.
    """
    rows = conn.execute("""
        SELECT
            rec_id, rule_id, rule_type, campaign_id, campaign_name,
            entity_type, entity_id, entity_name,
            customer_id, status, action_direction, action_magnitude,
            current_value, proposed_value, trigger_summary, confidence,
            generated_at, accepted_at, monitoring_ends_at, resolved_at,
            outcome_metric, created_at, updated_at
        FROM recommendations
        WHERE rec_id = ? AND customer_id = ?
        LIMIT 1
    """, [rec_id, customer_id]).fetchall()

    if not rows:
        return None

    columns = [
        "rec_id", "rule_id", "rule_type", "campaign_id", "campaign_name",
        "entity_type", "entity_id", "entity_name",
        "customer_id", "status", "action_direction", "action_magnitude",
        "current_value", "proposed_value", "trigger_summary", "confidence",
        "generated_at", "accepted_at", "monitoring_ends_at", "resolved_at",
        "outcome_metric", "created_at", "updated_at",
    ]
    return dict(zip(columns, rows[0]))


def _write_changes_row(
    conn,
    rec: dict,
    executed_by: str = "system",
    justification: Optional[str] = None,
    new_value_override: Optional[float] = None,
):
    """
    Insert a row into the changes table.
    
    Chat 47: Extended to INSERT entity_type, entity_id for multi-entity support.
    Backward compatibility: For campaigns, populates BOTH campaign_id AND entity_id.
    """
    _ensure_changes_table(conn)

    rule_type = rec.get("rule_type", "")
    if rule_type == "budget":
        action_type = "budget_change"
    elif rule_type == "bid":
        action_type = "bid_change"
    else:
        action_type = "status_change"

    old_value = rec.get("current_value")
    new_value = new_value_override if new_value_override is not None else rec.get("proposed_value")
    jst = justification or rec.get("action_direction", "")

    # Chat 47: Extract entity_type and entity_id
    entity_type = rec.get("entity_type")
    entity_id = rec.get("entity_id")
    
    # Backward compatibility: if entity_type is NULL, assume campaign
    if not entity_type and rec.get("campaign_id"):
        entity_type = "campaign"
        entity_id = str(rec.get("campaign_id", ""))

    conn.execute("""
        INSERT INTO changes (
            customer_id, campaign_id, campaign_name,
            entity_type, entity_id,
            rule_id, action_type, old_value, new_value, justification,
            executed_by, executed_at, dry_run, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, FALSE, 'completed')
    """, [
        str(rec.get("customer_id", "")),
        str(rec.get("campaign_id", "")),  # Backward compatibility
        rec.get("campaign_name", ""),      # Backward compatibility
        entity_type,                       # NEW (Chat 47)
        entity_id,                         # NEW (Chat 47)
        rec.get("rule_id", ""),
        action_type,
        old_value,
        new_value,
        jst,
        executed_by,
        datetime.now(),
    ])


def _get_recommendations_data(config, status_filter=None, limit=5000):
    """
    Query the recommendations table for the current customer.
    Returns list of dicts.
    
    Chat 47: Extended to SELECT entity_type, entity_id, entity_name.
    """
    conn = get_db_connection(config, read_only=False)
    try:
        where = "WHERE customer_id = ?"
        params = [config.customer_id]

        if status_filter:
            if isinstance(status_filter, list):
                placeholders = ", ".join(["?" for _ in status_filter])
                where += " AND status IN ({})".format(placeholders)
                params.extend(status_filter)
            else:
                where += " AND status = ?"
                params.append(status_filter)

        rows = conn.execute("""
            SELECT
                rec_id, rule_id, rule_type, campaign_id, campaign_name,
                entity_type, entity_id, entity_name,
                customer_id, status, action_direction, action_magnitude,
                current_value, proposed_value, trigger_summary, confidence,
                generated_at, accepted_at, monitoring_ends_at, resolved_at,
                outcome_metric, created_at, updated_at
            FROM recommendations
            {where}
            ORDER BY generated_at DESC
            LIMIT {limit}
        """.format(where=where, limit=limit), params).fetchall()

        columns = [
            "rec_id", "rule_id", "rule_type", "campaign_id", "campaign_name",
            "entity_type", "entity_id", "entity_name",
            "customer_id", "status", "action_direction", "action_magnitude",
            "current_value", "proposed_value", "trigger_summary", "confidence",
            "generated_at", "accepted_at", "monitoring_ends_at", "resolved_at",
            "outcome_metric", "created_at", "updated_at",
        ]
        result = [dict(zip(columns, row)) for row in rows]

        # Enrich with rule_name from DB or JSON
        name_map = _build_rule_name_map()
        for rec in result:
            rule_id = rec.get("rule_id", "")
            rec["rule_name"] = name_map.get(rule_id, rule_id)

        return result
    except Exception as e:
        print("[RECOMMENDATIONS] Error querying recommendations: {}".format(e))
        return []
    finally:
        conn.close()


def _get_summary(config):
    """
    Build the summary strip data.
    Returns dict with pending, monitoring, successful, declined, reverted, last_run.
    """
    conn = get_db_connection(config, read_only=False)
    try:
        cid = config.customer_id

        pending = conn.execute(
            "SELECT COUNT(*) FROM recommendations WHERE customer_id = ? AND status = 'pending'",
            [cid]
        ).fetchone()[0]

        monitoring = conn.execute(
            "SELECT COUNT(*) FROM recommendations WHERE customer_id = ? AND status = 'monitoring'",
            [cid]
        ).fetchone()[0]

        successful = conn.execute(
            "SELECT COUNT(*) FROM recommendations WHERE customer_id = ? AND status = 'successful'",
            [cid]
        ).fetchone()[0]

        declined = conn.execute(
            "SELECT COUNT(*) FROM recommendations WHERE customer_id = ? AND status = 'declined'",
            [cid]
        ).fetchone()[0]

        reverted = conn.execute(
            "SELECT COUNT(*) FROM recommendations WHERE customer_id = ? AND status = 'reverted'",
            [cid]
        ).fetchone()[0]

        # Fix: last_run from most recent generated_at
        last_run_row = conn.execute(
            "SELECT MAX(generated_at) FROM recommendations WHERE customer_id = ?",
            [cid]
        ).fetchone()
        last_run = last_run_row[0] if last_run_row else None

        return {
            "pending":    pending,
            "monitoring": monitoring,
            "successful": successful,
            "declined":   declined,
            "reverted":   reverted,
            "last_run":   last_run,
        }
    except Exception as e:
        print("[RECOMMENDATIONS] Error building summary: {}".format(e))
        return {"pending": 0, "monitoring": 0, "successful": 0, "declined": 0, "reverted": 0, "last_run": None}
    finally:
        conn.close()


def _enrich_rec(rec):
    """Add computed fields used by the template."""
    now = datetime.now()

    # Monitoring progress
    if rec["status"] == "monitoring" and rec["accepted_at"] and rec["monitoring_ends_at"]:
        accepted_at     = rec["accepted_at"]
        monitoring_ends = rec["monitoring_ends_at"]

        if isinstance(accepted_at, str):
            accepted_at = datetime.fromisoformat(accepted_at)
        if isinstance(monitoring_ends, str):
            monitoring_ends = datetime.fromisoformat(monitoring_ends)

        total_days   = max((monitoring_ends - accepted_at).days, 1)
        elapsed_days = max((now - accepted_at).days, 0)
        remaining    = max((monitoring_ends - now).days, 0)
        progress_pct = min(round(elapsed_days / total_days * 100), 100)

        rec["monitoring_total_days"]   = total_days
        rec["monitoring_elapsed_days"] = elapsed_days
        rec["monitoring_remaining"]    = remaining
        rec["monitoring_progress_pct"] = progress_pct
    else:
        rec["monitoring_total_days"]   = 0
        rec["monitoring_elapsed_days"] = 0
        rec["monitoring_remaining"]    = 0
        rec["monitoring_progress_pct"] = 0

    # Round raw values to avoid float precision noise (e.g. 3.5999999046325684)
    if rec.get("current_value") is not None:
        rec["current_value"]  = round(rec["current_value"],  2)
    if rec.get("proposed_value") is not None:
        rec["proposed_value"] = round(rec["proposed_value"], 2)

    # Value display
    rule_type  = rec.get("rule_type", "")
    action_type = rec.get("action_type", "")
    cur  = rec["current_value"]  or 0
    prop = rec["proposed_value"] or 0
    if rule_type == "budget":
        rec["value_label"]  = "£{:.2f} → £{:.2f}".format(cur, prop)
        rec["value_suffix"] = "daily"
    elif rule_type == "bid":
        if "max_cpc" in action_type:
            rec["value_label"]  = "£{:.2f} → £{:.2f}".format(cur, prop)
            rec["value_suffix"] = "max CPC"
        elif "tcpa" in action_type or "target_cpa" in action_type:
            rec["value_label"]  = "£{:.2f} → £{:.2f}".format(cur, prop)
            rec["value_suffix"] = "tCPA"
        else:
            rec["value_label"]  = "{:.2f}x → {:.2f}x tROAS".format(cur, prop)
            rec["value_suffix"] = "target"
    else:
        rec["value_label"]  = ""
        rec["value_suffix"] = ""

    # Top bar colour class
    status = rec.get("status", "pending")
    if status == "monitoring":
        rec["bar_class"] = "rt-monitoring"
    elif status == "reverted":
        rec["bar_class"] = "rt-reverted"
    elif rule_type == "budget":
        rec["bar_class"] = "rt-budget"
    elif rule_type == "bid":
        rec["bar_class"] = "rt-bid"
    else:
        rec["bar_class"] = "rt-status"

    # Action label — used by JS card rendering
    rec["action_label"] = get_action_label(rec)

    # Relative timestamp
    generated = rec.get("generated_at")
    if generated:
        if isinstance(generated, str):
            generated = datetime.fromisoformat(generated)
        delta = now - generated
        if delta.days > 0:
            rec["generated_ago"] = "{}d ago".format(delta.days)
        elif delta.seconds > 3600:
            rec["generated_ago"] = "{}h ago".format(delta.seconds // 3600)
        else:
            rec["generated_ago"] = "{}m ago".format(max(delta.seconds // 60, 1))
    else:
        rec["generated_ago"] = "—"

    return rec


# ---------------------------------------------------------------------------
# Action routes
# ---------------------------------------------------------------------------

@bp.route("/recommendations/<rec_id>/accept", methods=["POST"])
@login_required
def recommendation_accept(rec_id):
    """Accept a pending recommendation. Transitions to monitoring or successful."""
    config = get_current_config()
    conn = get_db_connection(config, read_only=False)
    try:
        rec = _load_rec_by_id(conn, rec_id, config.customer_id)
        if not rec:
            return jsonify({"success": False, "message": "Recommendation not found."}), 404
        if rec["status"] != "pending":
            return jsonify({"success": False, "message": "Recommendation is not pending."}), 400

        now = datetime.now()
        monitoring_config   = _load_monitoring_days(rec["rule_id"])
        monitoring_days     = monitoring_config["monitoring_days"]
        monitoring_minutes  = monitoring_config["monitoring_minutes"]

        if monitoring_minutes > 0:
            new_status      = "monitoring"
            monitoring_ends = now + timedelta(minutes=monitoring_minutes)
            conn.execute("""
                UPDATE recommendations
                SET status = ?, accepted_at = ?, monitoring_ends_at = ?, updated_at = ?
                WHERE rec_id = ? AND customer_id = ?
            """, [new_status, now, monitoring_ends, now, rec_id, config.customer_id])
        elif monitoring_days > 0:
            new_status      = "monitoring"
            monitoring_ends = now + timedelta(days=monitoring_days)
            conn.execute("""
                UPDATE recommendations
                SET status = ?, accepted_at = ?, monitoring_ends_at = ?, updated_at = ?
                WHERE rec_id = ? AND customer_id = ?
            """, [new_status, now, monitoring_ends, now, rec_id, config.customer_id])
        else:
            new_status = "successful"
            conn.execute("""
                UPDATE recommendations
                SET status = ?, accepted_at = ?, resolved_at = ?, updated_at = ?
                WHERE rec_id = ? AND customer_id = ?
            """, [new_status, now, now, now, rec_id, config.customer_id])

        _write_changes_row(conn, rec, executed_by="user_accept")

        return jsonify({
            "success":    True,
            "new_status": new_status,
            "message":    "Recommendation accepted — status set to {}.".format(new_status),
        })
    except Exception as e:
        print("[RECOMMENDATIONS] Accept error: {}".format(e))
        return jsonify({"success": False, "message": "Error: {}".format(e)}), 500
    finally:
        conn.close()


@bp.route("/recommendations/<rec_id>/decline", methods=["POST"])
@login_required
def recommendation_decline(rec_id):
    """Decline a pending recommendation."""
    config = get_current_config()
    conn = get_db_connection(config, read_only=False)
    try:
        rec = _load_rec_by_id(conn, rec_id, config.customer_id)
        if not rec:
            return jsonify({"success": False, "message": "Recommendation not found."}), 404
        if rec["status"] != "pending":
            return jsonify({"success": False, "message": "Recommendation is not pending."}), 400

        now = datetime.now()
        conn.execute("""
            UPDATE recommendations
            SET status = 'declined', accepted_at = ?, updated_at = ?
            WHERE rec_id = ? AND customer_id = ?
        """, [now, now, rec_id, config.customer_id])

        _write_changes_row(conn, rec, executed_by="user_decline")

        return jsonify({
            "success": True,
            "message": "Recommendation declined.",
        })
    except Exception as e:
        print("[RECOMMENDATIONS] Decline error: {}".format(e))
        return jsonify({"success": False, "message": "Error: {}".format(e)}), 500
    finally:
        conn.close()


@bp.route("/recommendations/<rec_id>/modify", methods=["POST"])
@login_required
def recommendation_modify(rec_id):
    """Modify proposed_value then accept a pending recommendation."""
    config = get_current_config()

    data = request.get_json(silent=True)
    if not data or "new_value" not in data:
        return jsonify({"success": False, "message": "Missing new_value in request body."}), 400

    try:
        new_value = float(data["new_value"])
    except (TypeError, ValueError):
        return jsonify({"success": False, "message": "new_value must be a number."}), 400

    conn = get_db_connection(config, read_only=False)
    try:
        rec = _load_rec_by_id(conn, rec_id, config.customer_id)
        if not rec:
            return jsonify({"success": False, "message": "Recommendation not found."}), 404
        if rec["status"] != "pending":
            return jsonify({"success": False, "message": "Recommendation is not pending."}), 400

        now = datetime.now()
        monitoring_config   = _load_monitoring_days(rec["rule_id"])
        monitoring_days     = monitoring_config["monitoring_days"]
        monitoring_minutes  = monitoring_config["monitoring_minutes"]

        # Update proposed_value first
        conn.execute("""
            UPDATE recommendations
            SET proposed_value = ?, updated_at = ?
            WHERE rec_id = ? AND customer_id = ?
        """, [new_value, now, rec_id, config.customer_id])

        if monitoring_minutes > 0:
            new_status      = "monitoring"
            monitoring_ends = now + timedelta(minutes=monitoring_minutes)
            conn.execute("""
                UPDATE recommendations
                SET status = ?, accepted_at = ?, monitoring_ends_at = ?, updated_at = ?
                WHERE rec_id = ? AND customer_id = ?
            """, [new_status, now, monitoring_ends, now, rec_id, config.customer_id])
        elif monitoring_days > 0:
            new_status      = "monitoring"
            monitoring_ends = now + timedelta(days=monitoring_days)
            conn.execute("""
                UPDATE recommendations
                SET status = ?, accepted_at = ?, monitoring_ends_at = ?, updated_at = ?
                WHERE rec_id = ? AND customer_id = ?
            """, [new_status, now, monitoring_ends, now, rec_id, config.customer_id])
        else:
            new_status = "successful"
            conn.execute("""
                UPDATE recommendations
                SET status = ?, accepted_at = ?, resolved_at = ?, updated_at = ?
                WHERE rec_id = ? AND customer_id = ?
            """, [new_status, now, now, now, rec_id, config.customer_id])

        _write_changes_row(
            conn, rec,
            executed_by="user_modify",
            justification="Modified before accepting",
            new_value_override=new_value,
        )

        return jsonify({
            "success":    True,
            "new_status": new_status,
            "message":    "Recommendation modified and accepted — status set to {}.".format(new_status),
        })
    except Exception as e:
        print("[RECOMMENDATIONS] Modify error: {}".format(e))
        return jsonify({"success": False, "message": "Error: {}".format(e)}), 500
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Page routes
# ---------------------------------------------------------------------------

@bp.route("/recommendations")
@login_required
def recommendations():
    """
    Global Recommendations page — 5 tabs: Pending / Monitoring / Successful / Reverted / Declined.
    """
    config              = get_current_config()
    clients             = get_available_clients()
    current_client_path = session.get("current_client_config")

    summary         = _get_summary(config)
    pending_recs    = [_enrich_rec(r) for r in _get_recommendations_data(config, status_filter="pending")]
    monitoring_recs = [_enrich_rec(r) for r in _get_recommendations_data(config, status_filter="monitoring")]
    successful_recs = [_enrich_rec(r) for r in _get_recommendations_data(config, status_filter="successful", limit=200)]
    reverted_recs   = [_enrich_rec(r) for r in _get_recommendations_data(config, status_filter="reverted",   limit=200)]
    declined_recs   = [_enrich_rec(r) for r in _get_recommendations_data(config, status_filter="declined",   limit=200)]

    return render_template(
        "recommendations.html",
        client_name=config.client_name,
        available_clients=clients,
        current_client_config=current_client_path,
        summary=summary,
        pending_recs=pending_recs,
        monitoring_recs=monitoring_recs,
        successful_recs=successful_recs,
        reverted_recs=reverted_recs,
        declined_recs=declined_recs,
    )


@bp.route("/recommendations/run", methods=["POST"])
@login_required
def recommendations_run():
    """
    Trigger the recommendations engine for the current client.
    Returns JSON: { success, generated, skipped_duplicate, message, errors }
    """
    config = get_current_config()

    try:
        from act_autopilot.recommendations_engine import run_recommendations_engine
        result = run_recommendations_engine(
            customer_id=config.customer_id,
            db_path=config.db_path,
        )
        return jsonify({
            "success":           True,
            "generated":         result["generated"],
            "skipped_duplicate": result["skipped_duplicate"],
            "skipped_no_data":   result["skipped_no_data"],
            "errors":            result["errors"],
            "message":           "Generated {} new recommendation{}.".format(
                result["generated"],
                "s" if result["generated"] != 1 else ""
            ),
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Engine error: {}".format(str(e)),
            "errors":  [str(e)],
        }), 500


@bp.route("/recommendations/data")
@login_required
def recommendations_data():
    """
    JSON endpoint: pending count, monitoring count, last_run.
    Used by sidebar badge and post-run page refresh.
    """
    config  = get_current_config()
    summary = _get_summary(config)

    last_run = summary.get("last_run")
    if last_run and hasattr(last_run, "isoformat"):
        last_run = last_run.isoformat()

    return jsonify({
        "pending":    summary["pending"],
        "monitoring": summary["monitoring"],
        "reverted":   summary["reverted"],
        "last_run":   last_run,
    })


# ---------------------------------------------------------------------------
# Rule-data enrichment helpers (for /recommendations/cards only)
# ---------------------------------------------------------------------------

_ACTION_TYPE_TO_RULE_TYPE = {
    "increase_budget":      "budget",
    "decrease_budget":      "budget",
    "pacing_increase":      "budget",
    "pacing_reduction":     "budget",
    "increase_troas":       "bid",
    "decrease_troas":       "bid",
    "increase_target_cpa":  "bid",
    "decrease_target_cpa":  "bid",
    "increase_max_cpc_cap": "bid",
    "decrease_max_cpc_cap": "bid",
    "increase_max_cpc":     "bid",
    "decrease_max_cpc":     "bid",
    "pause":                "status",
    "enable":               "status",
}

_METRIC_LABELS = {
    "roas_7d": "ROAS (7d)", "roas_14d": "ROAS (14d)", "roas_28d": "ROAS (28d)",
    "clicks_7d": "Clicks (7d)", "clicks_14d": "Clicks (14d)", "clicks_28d": "Clicks (28d)",
    "cost_7d": "Cost (7d)", "cost_14d": "Cost (14d)", "cost_28d": "Cost (28d)",
    "avg_cpc": "Avg CPC", "avg_cpc_7d": "Avg CPC (7d)", "avg_cpc_14d": "Avg CPC (14d)",
    "cpc_7d": "CPC (7d)", "cpc_14d": "CPC (14d)",
    "conversions_7d": "Conversions (7d)", "conversions_14d": "Conversions (14d)",
    "conv_value_7d": "Conv. value (7d)", "conv_value_14d": "Conv. value (14d)",
    "cpa_7d": "CPA (7d)", "cpa_14d": "CPA (14d)",
    "quality_score": "Quality score", "qs": "Quality score",
    "impression_share": "Impression share",
    "pacing_ratio": "Pacing ratio",
    "budget_utilization": "Budget utilisation",
    "search_impr_share": "Search impr. share",
    "spend_7d": "Spend (7d)", "spend_14d": "Spend (14d)",
}

_OP_SYMBOLS = {">=": "≥", "<=": "≤", ">": ">", "<": "<", "==": "=", "=": "=", "!=": "≠", "gt": ">", "lt": "<", "gte": "≥", "lte": "≤", "eq": "="}

_CURRENCY_METRIC_PARTS = {"cost", "cpc", "cpa", "budget", "spend", "value"}


def _format_condition_item(cond):
    """Format a single condition dict into a plain-English string.
    
    Schema: metric + op + value (numeric threshold) + ref (unit type: x_target, absolute, pct)
    Also supports legacy: metric + operator + condition_value + condition_unit
    """
    metric = cond.get("metric", "") or cond.get("condition_metric", "")
    op = cond.get("op") or cond.get("operator", "")
    # value = numeric threshold; ref = unit/reference type
    value = cond.get("value") if cond.get("value") is not None else cond.get("ref")
    ref_type = cond.get("ref") if cond.get("value") is not None else cond.get("unit", "")
    unit = cond.get("unit", "") or ""

    metric_label = _METRIC_LABELS.get(metric, metric.replace("_", " ").title())
    op_symbol = _OP_SYMBOLS.get(str(op).strip(), str(op))

    if value is None:
        return metric_label

    ref_type_str = str(ref_type or unit or "").lower()

    # Determine how to format the value based on ref_type
    if "target" in ref_type_str or ref_type_str in ("x_target", "×target"):
        # e.g. value=1.2, ref=x_target -> "1.2× target"
        try:
            fval = float(value)
            ref_str = "{}× target".format(int(fval) if fval == int(fval) else fval)
        except (ValueError, TypeError):
            ref_str = "× target"
    elif ref_type_str in ("pct", "percent", "%"):
        ref_str = "{}%".format(value)
    elif ref_type_str in ("absolute", "") and any(p in metric for p in _CURRENCY_METRIC_PARTS):
        try:
            ref_str = "£{:,.2f}".format(float(value)).rstrip("0").rstrip(".")
        except (ValueError, TypeError):
            ref_str = str(value)
    else:
        try:
            fval = float(value)
            ref_str = str(int(fval)) if fval == int(fval) else str(fval)
        except (ValueError, TypeError):
            ref_str = str(value)

    return "{} {} {}".format(metric_label, op_symbol, ref_str).strip()


def _format_conditions(conditions_raw):
    """Parse conditions JSON string and return list of formatted strings."""
    if not conditions_raw:
        return []
    try:
        data = json.loads(conditions_raw) if isinstance(conditions_raw, str) else conditions_raw
        if isinstance(data, list):
            return [_format_condition_item(c) for c in data if isinstance(c, dict)]
    except Exception:
        pass
    return []


def _derive_rule_type_for_display(action_type, entity_type):
    """Map action_type + entity_type to display rule_type string."""
    if entity_type == "keyword":
        return "keyword"
    if entity_type in ("shopping_product", "shopping"):
        return "shopping"
    return _ACTION_TYPE_TO_RULE_TYPE.get(str(action_type or ""), "status")


def _build_rule_data_map():
    """
    Query rules table and return dict keyed by str(id) with enrichment fields.
    Used exclusively by recommendations_cards() to enrich response payload.
    """
    result = {}
    try:
        conn = duckdb.connect("warehouse.duckdb")
        try:
            rows = conn.execute(
                "SELECT id, plain_english, rule_or_flag, conditions, "
                "risk_level, cooldown_days, action_type, entity_type "
                "FROM rules"
            ).fetchall()
            for row in rows:
                result[str(row[0])] = {
                    "plain_english": row[1] or "",
                    "rule_or_flag":  row[2] or "rule",
                    "conditions_raw": row[3],
                    "risk_level":    row[4] or "",
                    "cooldown_days": row[5],
                    "action_type":   row[6] or "",
                    "rule_entity_type": row[7] or "",
                }
        finally:
            conn.close()
    except Exception as e:
        print("[RECOMMENDATIONS] _build_rule_data_map error: {}".format(e))
    return result


def _enrich_with_rule_data(rec, rule_data_map):
    """
    Add plain_english, rule_or_flag, rule_type_display, conditions,
    risk_level, cooldown_days, completed_at to rec in-place.
    Chat 96: enriches /recommendations/cards payload for new table UI.
    """
    # Extract DB rule integer ID from "db_campaign_N" format
    rule_id_str = str(rec.get("rule_id", ""))
    rule_db_id = None
    if rule_id_str.startswith("db_campaign_"):
        try:
            rule_db_id = str(int(rule_id_str[len("db_campaign_"):]))
        except ValueError:
            pass
    elif rule_id_str.isdigit():
        rule_db_id = rule_id_str

    rule_data = rule_data_map.get(rule_db_id, {}) if rule_db_id else {}

    rec["plain_english"]   = rule_data.get("plain_english", "")
    rec["rule_or_flag"]    = rule_data.get("rule_or_flag", "rule")
    rec["conditions"]      = _format_conditions(rule_data.get("conditions_raw"))
    rec["risk_level"]      = rule_data.get("risk_level") or rec.get("risk_level", "")
    rec["cooldown_days"]   = rule_data.get("cooldown_days")
    rec["action_type"]     = rule_data.get("action_type", "")

    # Derive display rule_type from action_type + entity_type
    action_type  = rule_data.get("action_type") or ""
    entity_type  = rec.get("entity_type") or rule_data.get("rule_entity_type") or ""
    rec["rule_type_display"] = _derive_rule_type_for_display(action_type, entity_type)

    # campaign_name: already present in rec from recommendations table
    # accepted_at: already in rec
    # completed_at: map from resolved_at
    rec["completed_at"] = rec.get("resolved_at")


@bp.route("/recommendations/cards")
@login_required
def recommendations_cards():
    """
    JSON endpoint returning enriched recommendation cards by status.
    Used by all entity pages and the full Recommendations page for table rendering.

    Chat 96: Extended with plain_english, rule_or_flag, rule_type_display,
    conditions (formatted list), risk_level, cooldown_days, completed_at.
    """
    config = get_current_config()

    pending_recs    = [_enrich_rec(r) for r in _get_recommendations_data(config, status_filter="pending")]
    monitoring_recs = [_enrich_rec(r) for r in _get_recommendations_data(config, status_filter="monitoring")]
    successful_recs = [_enrich_rec(r) for r in _get_recommendations_data(config, status_filter="successful", limit=200)]
    reverted_recs   = [_enrich_rec(r) for r in _get_recommendations_data(config, status_filter="reverted",   limit=200)]
    declined_recs   = [_enrich_rec(r) for r in _get_recommendations_data(config, status_filter="declined",   limit=200)]

    # Chat 96: Enrich all recs with rules table data
    rule_data_map = _build_rule_data_map()
    for rec in (pending_recs + monitoring_recs + successful_recs + reverted_recs + declined_recs):
        _enrich_with_rule_data(rec, rule_data_map)

    # Re-calculate action_label / value_label / value_suffix now that action_type is populated
    for rec in (pending_recs + monitoring_recs + successful_recs + reverted_recs + declined_recs):
        rec["action_label"] = get_action_label(rec)
        if rec.get("rule_type") == "bid":
            action_type = rec.get("action_type", "")
            cur  = rec.get("current_value")  or 0
            prop = rec.get("proposed_value") or 0
            if "max_cpc" in action_type:
                rec["value_label"]  = "£{:.2f} → £{:.2f}".format(cur, prop)
                rec["value_suffix"] = "max CPC"
            elif "tcpa" in action_type or "target_cpa" in action_type:
                rec["value_label"]  = "£{:.2f} → £{:.2f}".format(cur, prop)
                rec["value_suffix"] = "tCPA"
            else:
                rec["value_label"]  = "{:.2f}x → {:.2f}x tROAS".format(cur, prop)
                rec["value_suffix"] = "target"

    def _serialise(rec):
        out = {}
        for k, v in rec.items():
            if isinstance(v, datetime):
                out[k] = v.isoformat()
            else:
                out[k] = v
        return out

    return jsonify({
        "pending":    [_serialise(r) for r in pending_recs],
        "monitoring": [_serialise(r) for r in monitoring_recs],
        "successful": [_serialise(r) for r in successful_recs],
        "reverted":   [_serialise(r) for r in reverted_recs],
        "declined":   [_serialise(r) for r in declined_recs],
    })
