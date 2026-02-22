"""
Recommendations routes — Chat 28 (M7)

Adds 3 POST action routes wired to recommendation cards:
    POST /recommendations/<rec_id>/accept
    POST /recommendations/<rec_id>/decline
    POST /recommendations/<rec_id>/modify

All other routes preserved from Chat 27.
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

def _ensure_changes_table(conn):
    """Create the writable changes table in warehouse.duckdb if it doesn't exist."""
    conn.execute("""
        CREATE SEQUENCE IF NOT EXISTS changes_seq START 1
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS changes (
            change_id       INTEGER DEFAULT nextval('changes_seq'),
            customer_id     VARCHAR NOT NULL,
            campaign_id     VARCHAR,
            campaign_name   VARCHAR,
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
    Read rules_config.json and return monitoring_days for the given rule_id.
    Returns 0 if rule not found or field missing.
    """
    try:
        path = os.path.normpath(_RULES_CONFIG_PATH)
        with open(path, "r") as f:
            rules = json.load(f)
        for rule in rules:
            if rule.get("rule_id") == rule_id:
                return int(rule.get("monitoring_days", 0))
    except Exception as e:
        print("[RECOMMENDATIONS] Could not load rules_config.json: {}".format(e))
    return 0


def _load_rec_by_id(conn, rec_id, customer_id):
    """
    Load a single recommendation row by rec_id + customer_id.
    Returns dict or None.
    """
    rows = conn.execute("""
        SELECT
            rec_id, rule_id, rule_type, campaign_id, campaign_name,
            customer_id, status, action_direction, action_magnitude,
            current_value, proposed_value, trigger_summary, confidence,
            generated_at, accepted_at, monitoring_ends_at, resolved_at,
            outcome_metric, created_at, updated_at
        FROM recommendations
        WHERE rec_id = ? AND customer_id = ?
    """, [rec_id, customer_id]).fetchall()

    if not rows:
        return None

    columns = [
        "rec_id", "rule_id", "rule_type", "campaign_id", "campaign_name",
        "customer_id", "status", "action_direction", "action_magnitude",
        "current_value", "proposed_value", "trigger_summary", "confidence",
        "generated_at", "accepted_at", "monitoring_ends_at", "resolved_at",
        "outcome_metric", "created_at", "updated_at",
    ]
    return dict(zip(columns, rows[0]))


def _write_changes_row(conn, rec, executed_by, justification=None, new_value_override=None):
    """Write a single audit row to the changes table."""
    _ensure_changes_table(conn)

    # Determine action_type from rule_type
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

    conn.execute("""
        INSERT INTO changes (
            customer_id, campaign_id, campaign_name, rule_id,
            action_type, old_value, new_value, justification,
            executed_by, executed_at, dry_run, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, FALSE, 'completed')
    """, [
        str(rec.get("customer_id", "")),
        str(rec.get("campaign_id", "")),
        rec.get("campaign_name", ""),
        rec.get("rule_id", ""),
        action_type,
        old_value,
        new_value,
        jst,
        executed_by,
        datetime.now(),
    ])


def _get_recommendations_data(config, status_filter=None, limit=200):
    """
    Query the recommendations table for the current customer.
    Returns list of dicts.
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
    Build the 4-card summary strip data.
    Returns dict with pending, monitoring, success_rate, last_run.
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

        return {
            "pending":    pending,
            "monitoring": monitoring,
            "successful": successful,
            "declined":   declined,
        }
    except Exception as e:
        print("[RECOMMENDATIONS] Error building summary: {}".format(e))
        return {"pending": 0, "monitoring": 0, "successful": 0, "declined": 0}
    finally:
        conn.close()


def _enrich_rec(rec):
    """Add computed fields used by the template."""
    now = datetime.now()

    # Monitoring progress: days elapsed / total days
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

    # Human-readable action label
    direction = rec.get("action_direction", "")
    magnitude = rec.get("action_magnitude", 0) or 0
    rule_type = rec.get("rule_type", "")

    if direction == "increase":
        rec["action_label"] = "Increase {} by {}%".format(
            "daily budget" if rule_type == "budget" else "tROAS target", magnitude
        )
    elif direction == "decrease":
        rec["action_label"] = "Decrease {} by {}%".format(
            "daily budget" if rule_type == "budget" else "tROAS target", magnitude
        )
    elif direction == "hold":
        rec["action_label"] = "Hold {} — no change".format(
            "budget" if rule_type == "budget" else "bid target"
        )
    elif direction == "flag":
        rec["action_label"] = "Flag campaign for review"
    else:
        rec["action_label"] = direction.title()

    # Value display
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
        rec["bar_class"] = "bar-monitoring"
    elif rule_type == "budget":
        rec["bar_class"] = "bar-budget"
    elif rule_type == "bid":
        rec["bar_class"] = "bar-bid"
    else:
        rec["bar_class"] = "bar-status"

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
# Action routes — Chat 28
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
        monitoring_days = _load_monitoring_days(rec["rule_id"])

        if monitoring_days > 0:
            new_status = "monitoring"
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
        monitoring_days = _load_monitoring_days(rec["rule_id"])

        # Update proposed_value first
        conn.execute("""
            UPDATE recommendations
            SET proposed_value = ?, updated_at = ?
            WHERE rec_id = ? AND customer_id = ?
        """, [new_value, now, rec_id, config.customer_id])

        # Then transition status (same as accept)
        if monitoring_days > 0:
            new_status = "monitoring"
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
# Routes — preserved from Chat 27
# ---------------------------------------------------------------------------

@bp.route("/recommendations")
@login_required
def recommendations():
    """
    Global Recommendations page — 4 tabs: Pending / Monitoring / Successful / Declined.
    Tab switching is pure JS — no query param routing needed.
    """
    config              = get_current_config()
    clients             = get_available_clients()
    current_client_path = session.get("current_client_config")

    summary          = _get_summary(config)
    pending_recs     = [_enrich_rec(r) for r in _get_recommendations_data(config, status_filter="pending")]
    monitoring_recs  = [_enrich_rec(r) for r in _get_recommendations_data(config, status_filter="monitoring")]
    successful_recs  = [_enrich_rec(r) for r in _get_recommendations_data(config, status_filter="successful", limit=200)]
    declined_recs    = [_enrich_rec(r) for r in _get_recommendations_data(config, status_filter="declined",   limit=200)]

    return render_template(
        "recommendations.html",
        client_name=config.client_name,
        available_clients=clients,
        current_client_config=current_client_path,
        summary=summary,
        pending_recs=pending_recs,
        monitoring_recs=monitoring_recs,
        successful_recs=successful_recs,
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
    JSON endpoint: pending count, monitoring count, success_rate, last_run.
    Used by sidebar badge and post-run page refresh.
    """
    config  = get_current_config()
    summary = _get_summary(config)

    last_run = summary["last_run"]
    if last_run and hasattr(last_run, "isoformat"):
        last_run = last_run.isoformat()

    return jsonify({
        "pending":      summary["pending"],
        "monitoring":   summary["monitoring"],
        "success_rate": summary["success_rate"],
        "last_run":     last_run,
    })


@bp.route("/recommendations/cards")
@login_required
def recommendations_cards():
    """
    JSON endpoint returning enriched recommendation cards by status.
    Used by the Campaigns page Recommendations tab for inline card rendering.
    """
    config = get_current_config()

    pending_recs    = [_enrich_rec(r) for r in _get_recommendations_data(config, status_filter="pending")]
    monitoring_recs = [_enrich_rec(r) for r in _get_recommendations_data(config, status_filter="monitoring")]
    successful_recs = [_enrich_rec(r) for r in _get_recommendations_data(config, status_filter="successful", limit=200)]
    declined_recs   = [_enrich_rec(r) for r in _get_recommendations_data(config, status_filter="declined",   limit=200)]

    def _serialise(rec):
        """Convert datetime fields to ISO strings for JSON serialisation."""
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
        "declined":   [_serialise(r) for r in declined_recs],
    })


# ---------------------------------------------------------------------------
# /changes — preserved exactly from pre-Chat 27
# ---------------------------------------------------------------------------

@bp.route("/changes")
@login_required
def changes():
    """
    Change history page showing all executed changes.
    """
    config              = get_current_config()
    clients             = get_available_clients()
    current_client_path = session.get("current_client_config")

    search        = request.args.get("search", "")
    status_filter = request.args.get("status", "all")
    lever_filter  = request.args.get("lever", "all")

    conn = duckdb.connect(config.db_path, read_only=True)

    query = """
    SELECT
        change_id,
        change_date,
        campaign_id,
        lever,
        old_value / 1000000 as old_value,
        new_value / 1000000 as new_value,
        change_pct,
        rule_id,
        risk_tier,
        rollback_status,
        executed_at
    FROM analytics.change_log
    WHERE customer_id = ?
    """
    params = [config.customer_id]

    if status_filter != "all":
        if status_filter == "active":
            query += " AND (rollback_status IS NULL OR rollback_status = 'monitoring')"
        else:
            query += " AND rollback_status = ?"
            params.append(status_filter)

    if lever_filter != "all":
        query += " AND lever = ?"
        params.append(lever_filter)

    if search:
        query += " AND campaign_id LIKE ?"
        params.append("%{}%".format(search))

    query += " ORDER BY change_date DESC, executed_at DESC LIMIT 100"

    changes_data = conn.execute(query, params).fetchall()
    conn.close()

    return render_template(
        "changes.html",
        client_name=config.client_name,
        available_clients=clients,
        current_client_config=current_client_path,
        changes=changes_data,
        search=search,
        status_filter=status_filter,
        lever_filter=lever_filter,
    )
