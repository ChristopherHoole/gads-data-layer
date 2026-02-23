"""
Radar — Background Monitoring Job
Chat 29 (M8)

Runs as a daemon thread. Every 60 seconds:
  1. Queries all recommendations with status = 'monitoring'
  2. For each, checks if the monitoring deadline has passed
  3. If deadline passed: evaluates KPI performance
     - KPI drop >= 15% vs baseline at accepted_at → revert
     - No drop (or status rule, no KPI check) → successful
  4. Updates recommendations table and writes to changes table

No Google Ads API calls in Chat 29 — DB status updates only.
"""

import json
import logging
import os
import time
from datetime import datetime, timedelta

import duckdb

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_DB_PATH = os.path.normpath(os.path.join(
    os.path.dirname(__file__),   # act_autopilot/
    "..", "warehouse.duckdb"
))

_RO_DB_PATH = os.path.normpath(os.path.join(
    os.path.dirname(__file__),   # act_autopilot/
    "..", "warehouse_readonly.duckdb"
))

_RULES_CONFIG_PATH = os.path.normpath(os.path.join(
    os.path.dirname(__file__),   # act_autopilot/
    "rules_config.json"
))

# KPI drop threshold — 15% decline triggers revert
_REVERT_THRESHOLD = 0.15


# ---------------------------------------------------------------------------
# DB connection helper
# ---------------------------------------------------------------------------

def _open_conn(db_path, ro_db_path):
    """
    Open warehouse.duckdb (read_write) and attach warehouse_readonly.duckdb as 'ro'.
    Returns connection. Caller must close.
    """
    conn = duckdb.connect(db_path)
    try:
        conn.execute(f"ATTACH '{ro_db_path}' AS ro (READ_ONLY);")
    except Exception:
        pass  # Already attached or not available
    return conn


# ---------------------------------------------------------------------------
# Rules config loader
# ---------------------------------------------------------------------------

def _load_rule_config(rule_id):
    """
    Load a single rule's config from rules_config.json.
    Returns dict or None if rule not found.
    """
    try:
        with open(_RULES_CONFIG_PATH, "r") as f:
            rules = json.load(f)
        for rule in rules:
            if rule.get("rule_id") == rule_id:
                return rule
    except Exception as e:
        logger.error("[RADAR] Could not load rules_config.json: %s", e)
    return None


# ---------------------------------------------------------------------------
# Deadline calculation
# ---------------------------------------------------------------------------

def _compute_deadline(rec, rule_config):
    """
    Returns the datetime deadline for this monitoring rec.
    If monitoring_minutes > 0: deadline = accepted_at + timedelta(minutes=monitoring_minutes)
    Else: deadline = monitoring_ends_at from the rec row
    """
    monitoring_minutes = int(rule_config.get("monitoring_minutes", 0))
    accepted_at = rec["accepted_at"]

    if isinstance(accepted_at, str):
        accepted_at = datetime.fromisoformat(accepted_at)

    if monitoring_minutes > 0:
        return accepted_at + timedelta(minutes=monitoring_minutes)

    monitoring_ends_at = rec.get("monitoring_ends_at")
    if monitoring_ends_at:
        if isinstance(monitoring_ends_at, str):
            monitoring_ends_at = datetime.fromisoformat(monitoring_ends_at)
        return monitoring_ends_at

    # No deadline data — treat as immediately due
    logger.warning("[RADAR] rec_id=%s has no deadline data, treating as due now", rec["rec_id"])
    return datetime.now() - timedelta(seconds=1)


# ---------------------------------------------------------------------------
# KPI evaluation
# ---------------------------------------------------------------------------

def _get_kpi_at_date(campaign_id, customer_id, target_date, conn):
    """
    Query campaign_features_daily for the most recent row on or before target_date.
    Returns dict with roas_w7, cvr_w7 or None if no data.
    """
    try:
        if isinstance(target_date, str):
            target_date = datetime.fromisoformat(target_date)

        date_str = target_date.strftime("%Y-%m-%d")

        rows = conn.execute("""
            SELECT roas_w7, cvr_w7
            FROM ro.analytics.campaign_features_daily
            WHERE campaign_id = ?
              AND customer_id = ?
              AND date <= ?
            ORDER BY date DESC
            LIMIT 1
        """, [str(campaign_id), str(customer_id), date_str]).fetchall()

        if rows:
            return {"roas_w7": rows[0][0], "cvr_w7": rows[0][1]}
    except Exception as e:
        logger.error("[RADAR] KPI query error for campaign_id=%s: %s", campaign_id, e)
    return None


def _get_latest_kpi(campaign_id, customer_id, conn):
    """
    Query campaign_features_daily for the most recent row.
    Returns dict with roas_w7, cvr_w7 or None if no data.
    """
    try:
        rows = conn.execute("""
            SELECT roas_w7, cvr_w7
            FROM ro.analytics.campaign_features_daily
            WHERE campaign_id = ?
              AND customer_id = ?
            ORDER BY date DESC
            LIMIT 1
        """, [str(campaign_id), str(customer_id)]).fetchall()

        if rows:
            return {"roas_w7": rows[0][0], "cvr_w7": rows[0][1]}
    except Exception as e:
        logger.error("[RADAR] Latest KPI query error for campaign_id=%s: %s", campaign_id, e)
    return None


def _should_revert(rec, rule_config, conn):
    """
    Determines if a monitoring rec should be reverted based on KPI performance.

    Returns (should_revert: bool, reason: str)

    Status rules: never revert — always successful.
    Budget rules: revert if roas_w7 dropped >= 15% vs baseline.
    Bid rules:    revert if roas_w7 OR cvr_w7 dropped >= 15% vs baseline.
    """
    rule_type = rule_config.get("rule_type", "")

    # Status rules: no KPI check, always successful
    if rule_type == "status":
        return False, ""

    campaign_id = rec["campaign_id"]
    customer_id = rec["customer_id"]
    accepted_at = rec["accepted_at"]

    baseline = _get_kpi_at_date(campaign_id, customer_id, accepted_at, conn)
    if baseline is None:
        logger.warning(
            "[RADAR] No baseline KPI for campaign_id=%s rec_id=%s — marking successful",
            campaign_id, rec["rec_id"]
        )
        return False, ""

    latest = _get_latest_kpi(campaign_id, customer_id, conn)
    if latest is None:
        logger.warning(
            "[RADAR] No latest KPI for campaign_id=%s rec_id=%s — marking successful",
            campaign_id, rec["rec_id"]
        )
        return False, ""

    baseline_roas = baseline.get("roas_w7") or 0
    latest_roas   = latest.get("roas_w7") or 0
    baseline_cvr  = baseline.get("cvr_w7") or 0
    latest_cvr    = latest.get("cvr_w7") or 0

    if rule_type == "budget":
        if baseline_roas > 0:
            roas_drop = (baseline_roas - latest_roas) / baseline_roas
            if roas_drop >= _REVERT_THRESHOLD:
                return True, "roas_w7 dropped {:.1f}% (baseline {:.3f} → current {:.3f})".format(
                    roas_drop * 100, baseline_roas, latest_roas
                )

    elif rule_type == "bid":
        if baseline_roas > 0:
            roas_drop = (baseline_roas - latest_roas) / baseline_roas
            if roas_drop >= _REVERT_THRESHOLD:
                return True, "roas_w7 dropped {:.1f}% (baseline {:.3f} → current {:.3f})".format(
                    roas_drop * 100, baseline_roas, latest_roas
                )
        if baseline_cvr > 0:
            cvr_drop = (baseline_cvr - latest_cvr) / baseline_cvr
            if cvr_drop >= _REVERT_THRESHOLD:
                return True, "cvr_w7 dropped {:.1f}% (baseline {:.3f} → current {:.3f})".format(
                    cvr_drop * 100, baseline_cvr, latest_cvr
                )

    return False, ""


# ---------------------------------------------------------------------------
# Changes table writer
# ---------------------------------------------------------------------------

def _ensure_changes_table(conn):
    """Create changes table if it doesn't exist."""
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


def _write_changes_row(conn, rec, executed_by, justification):
    """Write audit row to changes table."""
    _ensure_changes_table(conn)

    rule_type = rec.get("rule_type", "")
    if rule_type == "budget":
        action_type = "budget_change"
    elif rule_type == "bid":
        action_type = "bid_change"
    else:
        action_type = "status_change"

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
        rec.get("current_value"),
        rec.get("proposed_value"),
        justification,
        executed_by,
        datetime.now(),
    ])


# ---------------------------------------------------------------------------
# Schema check
# ---------------------------------------------------------------------------

def _ensure_revert_reason_column(conn):
    """Add revert_reason column to recommendations if it doesn't exist."""
    try:
        col_names = [row[0] for row in conn.execute(
            "SELECT column_name FROM information_schema.columns WHERE table_name = 'recommendations'"
        ).fetchall()]
        if "revert_reason" not in col_names:
            logger.info("[RADAR] Adding revert_reason column to recommendations table")
            conn.execute("ALTER TABLE recommendations ADD COLUMN revert_reason VARCHAR")
    except Exception as e:
        logger.error("[RADAR] Schema check error: %s", e)


# ---------------------------------------------------------------------------
# Per-recommendation evaluation
# ---------------------------------------------------------------------------

def _evaluate_monitoring_rec(rec, conn):
    """
    Evaluate a single monitoring recommendation using the shared connection.
    conn is a single read_write connection with ro catalog attached.
    """
    rec_id      = rec["rec_id"]
    customer_id = rec["customer_id"]
    rule_id     = rec["rule_id"]

    rule_config = _load_rule_config(rule_id)
    if rule_config is None:
        logger.warning("[RADAR] No rule config for rule_id=%s — skipping rec_id=%s", rule_id, rec_id)
        return

    # Check deadline
    try:
        deadline = _compute_deadline(rec, rule_config)
    except Exception as e:
        logger.error("[RADAR] Deadline error for rec_id=%s: %s", rec_id, e)
        return

    now = datetime.now()
    if now < deadline:
        logger.debug("[RADAR] rec_id=%s not yet due (deadline=%s)", rec_id, deadline.isoformat())
        return

    logger.info("[RADAR] rec_id=%s deadline passed — evaluating KPI", rec_id)

    # KPI evaluation
    try:
        revert, reason = _should_revert(rec, rule_config, conn)
    except Exception as e:
        logger.error("[RADAR] KPI evaluation error for rec_id=%s: %s — skipping", rec_id, e)
        return

    # Write result
    try:
        now_ts = datetime.now()
        if revert:
            logger.info("[RADAR] rec_id=%s REVERTED — %s", rec_id, reason)
            conn.execute("""
                UPDATE recommendations
                SET status = 'reverted', resolved_at = ?, revert_reason = ?, updated_at = ?
                WHERE rec_id = ? AND customer_id = ?
            """, [now_ts, reason, now_ts, rec_id, str(customer_id)])
            _write_changes_row(conn, rec, "radar_revert", reason)
        else:
            logger.info("[RADAR] rec_id=%s SUCCESSFUL", rec_id)
            conn.execute("""
                UPDATE recommendations
                SET status = 'successful', resolved_at = ?, updated_at = ?
                WHERE rec_id = ? AND customer_id = ?
            """, [now_ts, now_ts, rec_id, str(customer_id)])
            _write_changes_row(conn, rec, "radar_resolved", "Monitoring period completed — KPI stable")

    except Exception as e:
        logger.error("[RADAR] Write error for rec_id=%s: %s", rec_id, e)


# ---------------------------------------------------------------------------
# Evaluate all monitoring recs
# ---------------------------------------------------------------------------

def _evaluate_all_monitoring_recs(db_path, ro_db_path):
    """
    Open a single read_write connection to warehouse.duckdb with ro catalog attached.
    Fetch all monitoring recs, evaluate each, write results.
    Single connection open → process all → close.
    """
    columns = [
        "rec_id", "rule_id", "rule_type", "campaign_id", "campaign_name",
        "customer_id", "status", "action_direction", "action_magnitude",
        "current_value", "proposed_value", "trigger_summary", "confidence",
        "generated_at", "accepted_at", "monitoring_ends_at", "resolved_at",
        "outcome_metric", "created_at", "updated_at",
    ]

    conn = None
    try:
        conn = _open_conn(db_path, ro_db_path)

        # Ensure schema is up to date
        _ensure_revert_reason_column(conn)

        # Fetch all monitoring recs
        rows = conn.execute("""
            SELECT
                rec_id, rule_id, rule_type, campaign_id, campaign_name,
                customer_id, status, action_direction, action_magnitude,
                current_value, proposed_value, trigger_summary, confidence,
                generated_at, accepted_at, monitoring_ends_at, resolved_at,
                outcome_metric, created_at, updated_at
            FROM recommendations
            WHERE status = 'monitoring'
        """).fetchall()

        if not rows:
            logger.debug("[RADAR] No monitoring recommendations found")
            return

        logger.info("[RADAR] Found %d monitoring recommendation(s) to evaluate", len(rows))

        for row in rows:
            rec = dict(zip(columns, row))
            try:
                _evaluate_monitoring_rec(rec, conn)
            except Exception as e:
                logger.error("[RADAR] Unhandled error for rec_id=%s: %s — continuing", rec.get("rec_id"), e)

    except Exception as e:
        logger.error("[RADAR] Error in evaluate cycle: %s", e)
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def radar_loop():
    """
    Infinite loop — runs every 60 seconds.
    Designed to run as a daemon thread.
    Never raises — all exceptions caught and logged.
    """
    logger.info("[RADAR] Background thread started — cycle every 60 seconds")

    db_path    = _DB_PATH
    ro_db_path = _RO_DB_PATH

    while True:
        try:
            logger.info("[RADAR] Cycle start — %s", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            _evaluate_all_monitoring_recs(db_path, ro_db_path)
            logger.info("[RADAR] Cycle complete")
        except Exception as e:
            logger.error("[RADAR] Unexpected error in cycle: %s", e)

        time.sleep(60)
