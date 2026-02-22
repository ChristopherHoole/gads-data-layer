"""
Recommendations routes — Chat 27 (M6)

Replaces the old JSON-file-based /recommendations route with a
DuckDB-backed implementation reading from the `recommendations` table.

Routes:
    GET  /recommendations          — Global recommendations page (3 tabs)
    POST /recommendations/run      — Trigger engine, returns JSON
    GET  /recommendations/data     — JSON endpoint for tab counts/data
    GET  /changes                  — Change history (preserved from pre-Chat 27)
"""

from datetime import datetime
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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

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

        resolved = conn.execute("""
            SELECT
                COUNT(*) FILTER (WHERE status = 'successful') AS successful,
                COUNT(*) FILTER (WHERE status IN ('successful', 'reverted')) AS accepted
            FROM recommendations
            WHERE customer_id = ?
              AND resolved_at >= CURRENT_TIMESTAMP - INTERVAL 30 DAYS
        """, [cid]).fetchone()

        successful_count = resolved[0] or 0
        accepted_count   = resolved[1] or 0
        success_rate = round((successful_count / accepted_count * 100)) if accepted_count > 0 else 0

        last_run_row = conn.execute(
            "SELECT MAX(generated_at) FROM recommendations WHERE customer_id = ?",
            [cid]
        ).fetchone()
        last_run = last_run_row[0] if last_run_row else None

        return {
            "pending":      pending,
            "monitoring":   monitoring,
            "success_rate": success_rate,
            "last_run":     last_run,
        }
    except Exception as e:
        print("[RECOMMENDATIONS] Error building summary: {}".format(e))
        return {"pending": 0, "monitoring": 0, "success_rate": 0, "last_run": None}
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
# Routes
# ---------------------------------------------------------------------------

@bp.route("/recommendations")
@login_required
def recommendations():
    """
    Global Recommendations page — 3 tabs: Pending / Monitoring / History.
    Query param: ?tab=pending|monitoring|history  (default: pending)
    """
    config              = get_current_config()
    clients             = get_available_clients()
    current_client_path = session.get("current_client_config")
    active_tab          = request.args.get("tab", "pending")

    summary         = _get_summary(config)
    pending_recs    = [_enrich_rec(r) for r in _get_recommendations_data(config, status_filter="pending")]
    monitoring_recs = [_enrich_rec(r) for r in _get_recommendations_data(config, status_filter="monitoring")]
    history_recs    = [_enrich_rec(r) for r in _get_recommendations_data(
        config,
        status_filter=["successful", "reverted", "declined"],
        limit=100,
    )]

    # Success rate banner for history tab (30d window already in _get_summary,
    # but compute here from full history_recs list for the banner)
    successful_count     = sum(1 for r in history_recs if r["status"] == "successful")
    accepted_count       = sum(1 for r in history_recs if r["status"] in ("successful", "reverted"))
    history_success_rate = round(successful_count / accepted_count * 100) if accepted_count > 0 else 0

    return render_template(
        "recommendations.html",
        client_name=config.client_name,
        available_clients=clients,
        current_client_config=current_client_path,
        active_tab=active_tab,
        summary=summary,
        pending_recs=pending_recs,
        monitoring_recs=monitoring_recs,
        history_recs=history_recs,
        history_success_rate=history_success_rate,
        history_successful_count=successful_count,
        history_accepted_count=accepted_count,
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
    JSON endpoint returning enriched pending + monitoring cards.
    Used by the Campaigns page Recommendations tab for inline card rendering.
    """
    config = get_current_config()

    pending_recs    = [_enrich_rec(r) for r in _get_recommendations_data(config, status_filter="pending")]
    monitoring_recs = [_enrich_rec(r) for r in _get_recommendations_data(config, status_filter="monitoring")]

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
