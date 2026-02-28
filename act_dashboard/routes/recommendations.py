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
    
    # Campaign actions
    if entity_type == 'campaign':
        if action_direction == 'increase':
            if rule_type == 'budget':
                return f"Increase daily budget by {action_magnitude}%"
            elif rule_type == 'bid':
                return f"Increase tROAS target by {action_magnitude}%"
        elif action_direction == 'decrease':
            if rule_type == 'budget':
                return f"Decrease daily budget by {action_magnitude}%"
            elif rule_type == 'bid':
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
                return f"Increase shopping tROAS by {action_magnitude}%"
        elif action_direction == 'decrease':
            if rule_type == 'budget':
                return f"Decrease shopping budget by {action_magnitude}%"
            elif rule_type == 'bid':
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
    Read rules_config.json and return monitoring config for the given rule_id.
    Returns dict: {"monitoring_days": int, "monitoring_minutes": int}
    Returns {"monitoring_days": 0, "monitoring_minutes": 0} if rule not found.
    """
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
        return [dict(zip(columns, row)) for row in rows]
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

    # Value display
    rule_type = rec.get("rule_type", "")
    if rule_type == "budget":
        rec["value_label"]  = "£{:.2f} → £{:.2f}".format(
            rec["current_value"] or 0, rec["proposed_value"] or 0
        )
        rec["value_suffix"] = "daily"
    elif rule_type == "bid":
        rec["value_label"]  = "{:.2f}x → {:.2f}x tROAS".format(
            rec["current_value"] or 0, rec["proposed_value"] or 0
        )
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


@bp.route("/recommendations/cards")
@login_required
def recommendations_cards():
    """
    JSON endpoint returning enriched recommendation cards by status.
    Used by the Campaigns page Recommendations tab for inline card rendering.
    
    Chat 47: No changes needed - entity_type/entity_id/entity_name automatically included
    via _get_recommendations_data() extension.
    """
    config = get_current_config()

    pending_recs    = [_enrich_rec(r) for r in _get_recommendations_data(config, status_filter="pending")]
    monitoring_recs = [_enrich_rec(r) for r in _get_recommendations_data(config, status_filter="monitoring")]
    successful_recs = [_enrich_rec(r) for r in _get_recommendations_data(config, status_filter="successful", limit=200)]
    reverted_recs   = [_enrich_rec(r) for r in _get_recommendations_data(config, status_filter="reverted",   limit=200)]
    declined_recs   = [_enrich_rec(r) for r in _get_recommendations_data(config, status_filter="declined",   limit=200)]

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
