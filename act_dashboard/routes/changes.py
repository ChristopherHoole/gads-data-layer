"""
Changes routes — Chat 29 (M8)

New blueprint. Moved /changes route out of recommendations.py.
Adds:
  - My Actions tab: queries changes table, JOINs to recommendations for full card data
  - System Changes tab: queries ro.analytics.change_log (existing)
  - Summary strip counts: total, accepted, declined, modified
"""

import duckdb
from flask import Blueprint, render_template, request, session

from act_dashboard.auth import login_required
from act_dashboard.routes.shared import (
    get_available_clients,
    get_current_config,
    get_db_connection,
)

bp = Blueprint("changes", __name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_my_actions(config):
    """
    Query changes table and JOIN to recommendations to get full card data.
    JOIN on campaign_id + rule_id — no recommendation_id FK exists.
    Returns list of dicts.
    """
    conn = get_db_connection(config, read_only=False)
    try:
        rows = conn.execute("""
            SELECT
                ch.change_id,
                ch.customer_id,
                ch.campaign_id,
                ch.campaign_name,
                ch.rule_id,
                ch.action_type,
                ch.old_value,
                ch.new_value,
                ch.justification,
                ch.executed_by,
                ch.executed_at,
                ch.dry_run,
                ch.status         AS change_status,
                rec.rec_id,
                rec.rule_type,
                rec.action_direction,
                rec.action_magnitude,
                rec.current_value,
                rec.proposed_value,
                rec.trigger_summary,
                rec.confidence,
                rec.generated_at,
                rec.accepted_at,
                rec.monitoring_ends_at,
                rec.resolved_at,
                rec.outcome_metric,
                rec.status        AS rec_status,
                rec.revert_reason
            FROM changes ch
            LEFT JOIN (
                SELECT *
                FROM recommendations
                WHERE customer_id = ?
                QUALIFY ROW_NUMBER() OVER (
                    PARTITION BY campaign_id, rule_id
                    ORDER BY generated_at DESC
                ) = 1
            ) rec ON rec.campaign_id = ch.campaign_id
                 AND rec.rule_id     = ch.rule_id
            WHERE ch.customer_id = ?
              AND ch.executed_by IN ('user_accept', 'user_modify', 'user_decline')
            ORDER BY ch.executed_at DESC
            LIMIT 200
        """, [config.customer_id, config.customer_id]).fetchall()

        columns = [
            "change_id", "customer_id", "campaign_id", "campaign_name",
            "rule_id", "action_type", "old_value", "new_value",
            "justification", "executed_by", "executed_at", "dry_run",
            "change_status",
            "rec_id", "rule_type", "action_direction", "action_magnitude",
            "current_value", "proposed_value", "trigger_summary", "confidence",
            "generated_at", "accepted_at", "monitoring_ends_at", "resolved_at",
            "outcome_metric", "rec_status", "revert_reason",
        ]
        return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        print("[CHANGES] Error querying my_actions: {}".format(e))
        return []
    finally:
        conn.close()


def _get_system_changes(config):
    """
    Query ro.analytics.change_log for system-executed changes.
    Returns list of dicts.
    """
    conn = get_db_connection(config, read_only=True)
    try:
        rows = conn.execute("""
            SELECT
                change_id,
                change_date,
                campaign_id,
                lever,
                old_value / 1000000.0  AS old_value,
                new_value / 1000000.0  AS new_value,
                change_pct,
                rule_id,
                risk_tier,
                rollback_status,
                executed_at
            FROM ro.analytics.change_log
            WHERE customer_id = ?
            ORDER BY change_date DESC, executed_at DESC
            LIMIT 200
        """, [config.customer_id]).fetchall()

        columns = [
            "change_id", "change_date", "campaign_id", "lever",
            "old_value", "new_value", "change_pct", "rule_id",
            "risk_tier", "rollback_status", "executed_at",
        ]
        return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        print("[CHANGES] Error querying system_changes: {}".format(e))
        return []
    finally:
        conn.close()


def _get_summary_counts(config):
    """
    Compute summary strip counts from changes table.
    Returns dict: total, accepted, declined, modified.
    """
    conn = get_db_connection(config, read_only=False)
    try:
        cid = config.customer_id

        total = conn.execute("""
            SELECT COUNT(*) FROM changes
            WHERE customer_id = ?
              AND executed_by IN ('user_accept', 'user_modify', 'user_decline')
        """, [cid]).fetchone()[0]

        accepted = conn.execute("""
            SELECT COUNT(*) FROM changes
            WHERE customer_id = ? AND executed_by = 'user_accept'
        """, [cid]).fetchone()[0]

        declined = conn.execute("""
            SELECT COUNT(*) FROM changes
            WHERE customer_id = ? AND executed_by = 'user_decline'
        """, [cid]).fetchone()[0]

        modified = conn.execute("""
            SELECT COUNT(*) FROM changes
            WHERE customer_id = ? AND executed_by = 'user_modify'
        """, [cid]).fetchone()[0]

        return {
            "total":    total,
            "accepted": accepted,
            "declined": declined,
            "modified": modified,
        }
    except Exception as e:
        print("[CHANGES] Error computing summary: {}".format(e))
        return {"total": 0, "accepted": 0, "declined": 0, "modified": 0}
    finally:
        conn.close()


def _enrich_action(action):
    """Add computed display fields to a my_actions row."""
    from datetime import datetime

    executed_by = action.get("executed_by", "")
    rec_status  = action.get("rec_status") or ""
    rule_type   = action.get("rule_type") or ""

    # User action label
    if executed_by == "user_accept":
        action["action_label_user"] = "Accepted"
        action["action_badge_class"] = "ab-accepted"
    elif executed_by == "user_modify":
        action["action_label_user"] = "Modified"
        action["action_badge_class"] = "ab-modified"
    elif executed_by == "user_decline":
        action["action_label_user"] = "Declined"
        action["action_badge_class"] = "ab-declined"
    else:
        action["action_label_user"] = executed_by
        action["action_badge_class"] = "ab-declined"

    # Card top bar class — based on rec outcome status
    if rec_status == "monitoring":
        action["bar_class"] = "rt-monitoring"
    elif rec_status == "successful":
        action["bar_class"] = "rt-successful"
    elif rec_status == "reverted":
        action["bar_class"] = "rt-reverted"
    elif rec_status == "declined":
        action["bar_class"] = "rt-declined"
    elif rule_type == "budget":
        action["bar_class"] = "rt-budget"
    elif rule_type == "bid":
        action["bar_class"] = "rt-bid"
    else:
        action["bar_class"] = "rt-status"

    # Card border class
    status_border = {
        "monitoring": "card-monitoring",
        "successful": "card-success",
        "reverted":   "card-reverted",
        "declined":   "card-declined",
    }
    action["card_class"] = status_border.get(rec_status, "")

    # Change block colour
    cb_map = {"budget": "cb-budget", "bid": "cb-bid", "status": "cb-status"}
    action["cb_class"]  = cb_map.get(rule_type, "cb-grey")
    ciw_map = {"budget": "ciw-budget", "bid": "ciw-bid", "status": "ciw-status"}
    action["ciw_class"] = ciw_map.get(rule_type, "ciw-grey")

    # Rule tag colour
    rrt_map = {"budget": "rrt-budget", "bid": "rrt-bid", "status": "rrt-status"}
    action["rrt_class"] = rrt_map.get(rule_type, "rrt-budget")

    # Value display
    old_v = action.get("old_value") or 0
    new_v = action.get("new_value") or 0
    if rule_type == "budget":
        action["value_label"]  = "£{:.2f} → £{:.2f}".format(old_v, new_v)
        action["value_suffix"] = "daily"
    elif rule_type == "bid":
        action["value_label"]  = "{:.2f}x → {:.2f}x tROAS".format(old_v, new_v)
        action["value_suffix"] = "target"
    else:
        action["value_label"]  = ""
        action["value_suffix"] = ""

    # Outcome dot class
    dot_map = {
        "monitoring": "od-monitoring",
        "successful": "od-success",
        "reverted":   "od-reverted",
        "declined":   "od-declined",
    }
    action["outcome_dot_class"] = dot_map.get(rec_status, "od-declined")

    # Relative timestamp
    now = datetime.now()
    executed_at = action.get("executed_at")
    if executed_at:
        if isinstance(executed_at, str):
            from datetime import datetime as dt
            executed_at = dt.fromisoformat(executed_at)
        delta = now - executed_at
        if delta.days > 0:
            action["executed_ago"] = "{}d ago".format(delta.days)
        elif delta.seconds > 3600:
            action["executed_ago"] = "{}h ago".format(delta.seconds // 3600)
        else:
            action["executed_ago"] = "{}m ago".format(max(delta.seconds // 60, 1))
    else:
        action["executed_ago"] = "—"

    # Source pill — always User for this tab
    action["source_label"] = "User"
    action["source_class"] = "sp-user"

    return action


def _enrich_system_change(ch):
    """Add computed display fields to a system_changes row."""
    lever = (ch.get("lever") or "").lower()
    rollback = ch.get("rollback_status") or ""

    # Source pill — Autopilot for analytics.change_log
    ch["source_label"] = "Autopilot"
    ch["source_class"] = "sp-system"

    # Status display
    if rollback == "reverted":
        ch["status_label"] = "Reverted"
        ch["status_dot"]   = "od-reverted"
    elif rollback in ("monitoring", ""):
        ch["status_label"] = "Monitoring"
        ch["status_dot"]   = "od-monitoring"
    else:
        ch["status_label"] = "Successful"
        ch["status_dot"]   = "od-success"

    # Top bar
    if lever == "budget":
        ch["bar_class"] = "rt-budget"
        ch["cb_class"]  = "cb-budget"
    elif lever == "bid":
        ch["bar_class"] = "rt-bid"
        ch["cb_class"]  = "cb-bid"
    else:
        ch["bar_class"] = "rt-status"
        ch["cb_class"]  = "cb-grey"

    return ch


# ---------------------------------------------------------------------------
# Route
# ---------------------------------------------------------------------------

@bp.route("/changes")
@login_required
def changes():
    """
    Changes page — 2 tabs: My Actions (user decisions) / System Changes (autopilot).
    """
    config              = get_current_config()
    clients             = get_available_clients()
    current_client_path = session.get("current_client_config")

    summary        = _get_summary_counts(config)
    my_actions_raw = _get_my_actions(config)
    my_actions     = [_enrich_action(a) for a in my_actions_raw]
    system_changes = [_enrich_system_change(c) for c in _get_system_changes(config)]

    return render_template(
        "changes.html",
        client_name=config.client_name,
        available_clients=clients,
        current_client_config=current_client_path,
        summary=summary,
        my_actions=my_actions,
        system_changes=system_changes,
    )
