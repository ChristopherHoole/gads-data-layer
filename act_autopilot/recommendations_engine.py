"""
Recommendations Engine — Chat 27 (M6)

Reads enabled rules from rules_config.json, evaluates each rule against
campaign data in the database, and writes new pending recommendations to
the `recommendations` table in warehouse.duckdb.

Usage:
    from act_autopilot.recommendations_engine import run_recommendations_engine
    result = run_recommendations_engine(customer_id="9999999999", db_path="warehouse.duckdb")

Returns dict:
    {
        "generated": N,
        "skipped_duplicate": N,
        "skipped_no_data": N,
        "skipped_no_target": N,
        "errors": [...],
        "customer_id": "...",
    }

Architecture:
    - Writable connection to warehouse.duckdb
    - ro.analytics.campaign_features_daily attached from warehouse_readonly.duckdb
    - rules_config.json read from act_autopilot/ directory
    - analytics.campaign_daily NOT used (budget_micros/target_roas not present for Synthetic)
    - budget proxy : cost_micros_w7_mean
    - target_roas  : fixed fallback 4.0 (no column available)
"""

import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import duckdb

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_HERE = Path(__file__).parent
RULES_CONFIG_PATH = _HERE / "rules_config.json"

# ---------------------------------------------------------------------------
# Metric → DB column mapping
# Proxy columns used when original flag columns don't exist in features table.
# ---------------------------------------------------------------------------

# Maps rule condition_metric → (db_column, override_operator, override_threshold)
# override_operator / override_threshold = None means use rule's own values
METRIC_MAP = {
    # Standard rolling metrics
    "roas_7d":              ("roas_w7_mean",        None,  None),
    "roas_30d":             ("roas_w30_mean",        None,  None),
    "clicks_7d":            ("clicks_w7_sum",        None,  None),
    "conversions_30d":      ("conversions_w30_sum",  None,  None),
    "cost_cv_14d":          ("cost_w14_cv",          None,  None),

    # Boolean-flag proxies — operator and threshold are FIXED regardless of rule values
    "cost_spike_confidence": ("anomaly_cost_z",       "gte", 2.0),   # z >= 2.0 = spike
    "cost_drop_detected":    ("anomaly_cost_z",       "lte", -2.0),  # z <= -2.0 = drop
    "pace_over_cap_detected":("pacing_flag_over_105", "eq",  True),  # boolean True
    "ctr_drop_detected":     ("ctr_w7_vs_prev_pct",   "lt",  -20.0), # pct < -20
    "cvr_drop_detected":     ("cvr_w7_vs_prev_pct",   "lt",  -20.0), # pct < -20
}

PROXY_METRICS = {
    "cost_spike_confidence", "cost_drop_detected",
    "pace_over_cap_detected", "ctr_drop_detected", "cvr_drop_detected",
}

# Confidence from risk_level
RISK_TO_CONFIDENCE = {
    "low":    "high",
    "medium": "medium",
    "high":   "low",
}

# ---------------------------------------------------------------------------
# Operator evaluation
# ---------------------------------------------------------------------------

def _evaluate(value, operator, threshold) -> bool:
    """Evaluate value op threshold. Returns False if value is None."""
    if value is None:
        return False
    try:
        if operator == "gt":  return float(value) >  float(threshold)
        if operator == "gte": return float(value) >= float(threshold)
        if operator == "lt":  return float(value) <  float(threshold)
        if operator == "lte": return float(value) <= float(threshold)
        if operator == "eq":
            if isinstance(threshold, bool):
                return bool(value) == threshold
            return float(value) == float(threshold)
    except (TypeError, ValueError):
        return False
    return False


# ---------------------------------------------------------------------------
# Metric fetching helpers
# ---------------------------------------------------------------------------

def _get_metric_value(features: dict, metric_name: str) -> tuple[Any, str]:
    """
    Resolve metric_name to a value using METRIC_MAP.
    Returns (value, db_column_used).
    """
    if metric_name not in METRIC_MAP:
        return None, metric_name

    db_col, override_op, override_threshold = METRIC_MAP[metric_name]
    value = features.get(db_col)
    return value, db_col


def _evaluate_condition(features: dict, metric: str, operator: str, threshold) -> tuple[bool, str]:
    """
    Evaluate a single condition. Handles proxy overrides.
    Returns (passed, description_for_summary).
    """
    if not metric:
        return True, ""

    if metric not in METRIC_MAP:
        return False, "unknown metric"

    db_col, override_op, override_threshold = METRIC_MAP[metric]
    value = features.get(db_col)

    # Use proxy operator/threshold if this is a flag metric
    effective_op = override_op if override_op else operator
    effective_threshold = override_threshold if override_threshold is not None else threshold

    passed = _evaluate(value, effective_op, effective_threshold)

    # Human-readable description for trigger_summary
    if value is None:
        desc = "{} = NULL".format(db_col)
    elif isinstance(value, bool):
        desc = "{} = {}".format(db_col, value)
    elif isinstance(effective_threshold, float) and effective_threshold < 0:
        desc = "{} {:.1f}%".format(db_col, float(value))
    else:
        try:
            desc = "{} {:.2f}".format(db_col, float(value))
        except (TypeError, ValueError):
            desc = "{} = {}".format(db_col, value)

    return passed, desc


# ---------------------------------------------------------------------------
# Proposed value calculation
# ---------------------------------------------------------------------------

def _calculate_proposed_value(rule: dict, current_value: float) -> float:
    """
    Calculate proposed_value from current_value and rule action.
    hold/flag rules: proposed = current (no change).
    """
    direction = rule["action_direction"]
    magnitude = rule.get("action_magnitude", 0) or 0

    if direction == "increase":
        return round(current_value * (1 + magnitude / 100.0), 4)
    elif direction == "decrease":
        return round(current_value * (1 - magnitude / 100.0), 4)
    else:
        # hold or flag — no change
        return round(current_value, 4)


# ---------------------------------------------------------------------------
# Trigger summary builder
# ---------------------------------------------------------------------------

def _build_trigger_summary(rule: dict, features: dict, target_roas: float) -> str:
    """Build the human-readable trigger summary string."""
    parts = []

    metric = rule["condition_metric"]
    op     = rule["condition_operator"]
    val    = rule["condition_value"]
    unit   = rule.get("condition_unit", "absolute")

    _passed, desc = _evaluate_condition(features, metric, op, val)

    if unit == "x_target":
        threshold_display = "{:.2f}x (target {:.1f}x x {:.2f})".format(
            target_roas * val, target_roas, val
        )
        # Get actual value for display
        db_col = METRIC_MAP.get(metric, (metric,))[0]
        actual = features.get(db_col)
        if actual is not None:
            try:
                parts.append("ROAS {:.2f}x {} {}".format(float(actual), op, threshold_display))
            except (TypeError, ValueError):
                parts.append(desc)
        else:
            parts.append(desc)
    elif metric in PROXY_METRICS:
        proxy_label = {
            "cost_spike_confidence": "Cost spike (anomaly z-score)",
            "cost_drop_detected":    "Cost drop (anomaly z-score)",
            "pace_over_cap_detected":"Pacing over cap flag",
            "ctr_drop_detected":     "CTR drop",
            "cvr_drop_detected":     "CVR drop",
        }.get(metric, metric)
        db_col = METRIC_MAP[metric][0]
        actual = features.get(db_col)
        if actual is not None:
            try:
                if isinstance(actual, bool):
                    parts.append("{} = {}".format(proxy_label, actual))
                else:
                    parts.append("{} {:.2f}".format(proxy_label, float(actual)))
            except (TypeError, ValueError):
                parts.append(desc)
        else:
            parts.append(desc)
    else:
        db_col = METRIC_MAP.get(metric, (metric,))[0]
        actual = features.get(db_col)
        if actual is not None:
            try:
                parts.append("{} {:.2f} {} {:.2f}".format(db_col, float(actual), op, float(val)))
            except (TypeError, ValueError):
                parts.append(desc)
        else:
            parts.append(desc)

    # Condition 2
    metric2 = rule.get("condition_2_metric")
    if metric2:
        op2   = rule["condition_2_operator"]
        val2  = rule["condition_2_value"]
        _p2, desc2 = _evaluate_condition(features, metric2, op2, val2)
        if metric2 in PROXY_METRICS:
            db_col2 = METRIC_MAP[metric2][0]
            actual2 = features.get(db_col2)
            if actual2 is not None:
                try:
                    parts.append("{} {:.2f}".format(db_col2, float(actual2)))
                except (TypeError, ValueError):
                    parts.append(desc2)
            else:
                parts.append(desc2)
        elif rule.get("condition_2_unit") == "absolute":
            db_col2 = METRIC_MAP.get(metric2, (metric2,))[0]
            actual2 = features.get(db_col2)
            if actual2 is not None:
                try:
                    parts.append("{} {:.0f} {} {:.0f}".format(
                        db_col2, float(actual2), op2, float(val2)
                    ))
                except (TypeError, ValueError):
                    parts.append(desc2)
            else:
                parts.append(desc2)
        else:
            parts.append(desc2)

    return " | ".join(parts) if parts else rule.get("name", rule["rule_id"])


# ---------------------------------------------------------------------------
# Main engine
# ---------------------------------------------------------------------------

def run_recommendations_engine(
    customer_id: str,
    db_path: str = "warehouse.duckdb",
    ro_db_path: str = None,
    rules_config_path: str = None,
) -> dict:
    """
    Run the recommendations engine for the given customer_id.

    Args:
        customer_id:       Google Ads customer ID (string)
        db_path:           Path to writable warehouse.duckdb
        ro_db_path:        Path to warehouse_readonly.duckdb (auto-derived if None)
        rules_config_path: Path to rules_config.json (defaults to act_autopilot/)

    Returns:
        Summary dict with generated/skipped/error counts.
    """
    db_path = str(Path(db_path).resolve())

    if ro_db_path is None:
        ro_db_path = db_path.replace("warehouse.duckdb", "warehouse_readonly.duckdb")

    cfg_path = Path(rules_config_path) if rules_config_path else RULES_CONFIG_PATH

    print("[ENGINE] Starting recommendations engine for customer {}".format(customer_id))
    print("[ENGINE] DB         : {}".format(db_path))
    print("[ENGINE] RO DB      : {}".format(ro_db_path))
    print("[ENGINE] Rules file : {}".format(cfg_path))

    # --- Load rules ---------------------------------------------------------
    if not cfg_path.exists():
        return {"error": "rules_config.json not found at {}".format(cfg_path)}

    with open(cfg_path, "r") as f:
        all_rules = json.load(f)

    enabled_rules = [r for r in all_rules if r.get("enabled", False)]
    print("[ENGINE] Loaded {} rules ({} enabled)".format(len(all_rules), len(enabled_rules)))

    # --- Open DB connection -------------------------------------------------
    conn = duckdb.connect(db_path, read_only=False)
    try:
        conn.execute("ATTACH '{}' AS ro (READ_ONLY);".format(ro_db_path))
        print("[ENGINE] Attached readonly DB as 'ro'")
    except Exception as e:
        print("[ENGINE] WARNING: Could not attach ro DB: {}".format(e))

    # --- Ensure recommendations table exists --------------------------------
    conn.execute("""
        CREATE TABLE IF NOT EXISTS recommendations (
            rec_id               VARCHAR PRIMARY KEY,
            rule_id              VARCHAR NOT NULL,
            rule_type            VARCHAR NOT NULL,
            campaign_id          BIGINT  NOT NULL,
            campaign_name        VARCHAR,
            customer_id          VARCHAR NOT NULL,
            status               VARCHAR NOT NULL DEFAULT 'pending',
            action_direction     VARCHAR,
            action_magnitude     INTEGER,
            current_value        FLOAT,
            proposed_value       FLOAT,
            trigger_summary      VARCHAR,
            confidence           VARCHAR,
            generated_at         TIMESTAMP,
            accepted_at          TIMESTAMP,
            monitoring_ends_at   TIMESTAMP,
            resolved_at          TIMESTAMP,
            outcome_metric       FLOAT,
            created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # --- Fetch latest campaign features -------------------------------------
    try:
        latest_date = conn.execute("""
            SELECT MAX(snapshot_date)
            FROM ro.analytics.campaign_features_daily
            WHERE customer_id = ?
        """, [customer_id]).fetchone()[0]

        if latest_date is None:
            print("[ENGINE] WARNING: No features data found for customer {}".format(customer_id))
            conn.close()
            return {
                "generated": 0,
                "skipped_duplicate": 0,
                "skipped_no_data": 0,
                "skipped_no_target": 0,
                "errors": ["No features data available"],
                "customer_id": customer_id,
            }

        print("[ENGINE] Latest features snapshot: {}".format(latest_date))

        feature_rows = conn.execute("""
            SELECT *
            FROM ro.analytics.campaign_features_daily
            WHERE customer_id = ?
              AND snapshot_date = ?
        """, [customer_id, latest_date]).fetchdf()

    except Exception as e:
        print("[ENGINE] ERROR fetching features: {}".format(e))
        conn.close()
        return {
            "generated": 0,
            "skipped_duplicate": 0,
            "skipped_no_data": 0,
            "skipped_no_target": 0,
            "errors": [str(e)],
            "customer_id": customer_id,
        }

    if feature_rows.empty:
        print("[ENGINE] No feature rows found for customer {} on {}".format(customer_id, latest_date))
        conn.close()
        return {
            "generated": 0,
            "skipped_duplicate": 0,
            "skipped_no_data": 0,
            "skipped_no_target": 0,
            "errors": [],
            "customer_id": customer_id,
        }

    print("[ENGINE] Found {} campaigns in features".format(len(feature_rows)))

    # --- Fetch existing pending recs to check duplicates --------------------
    existing_pending = set()
    try:
        pending_rows = conn.execute("""
            SELECT campaign_id, rule_id
            FROM recommendations
            WHERE customer_id = ?
              AND status = 'pending'
        """, [customer_id]).fetchall()
        for row in pending_rows:
            existing_pending.add((int(row[0]), row[1]))
    except Exception as e:
        print("[ENGINE] WARNING: Could not fetch existing pending recs: {}".format(e))

    print("[ENGINE] {} existing pending recs (duplicate check)".format(len(existing_pending)))

    # --- Process each campaign × rule ---------------------------------------
    generated        = 0
    skipped_duplicate = 0
    skipped_no_data  = 0
    skipped_no_target = 0
    errors           = []
    new_recs         = []
    now              = datetime.now()

    for _, feat_row in feature_rows.iterrows():
        features = feat_row.to_dict()
        campaign_id   = int(features.get("campaign_id", 0))
        campaign_name = features.get("campaign_name") or "Campaign_{}".format(campaign_id)

        # --- Resolve current_value proxies ----------------------------------

        # target_roas: no column — use fixed fallback
        target_roas = 4.0
        print("[ENGINE] No target_roas column — using fallback 4.0 for campaign {}".format(campaign_id))

        # budget proxy: cost_micros_w7_mean (convert micros to currency)
        cost_micros_mean = features.get("cost_micros_w7_mean")
        if cost_micros_mean is not None and float(cost_micros_mean) > 0:
            budget_value = float(cost_micros_mean) / 1_000_000
            print("[ENGINE] No budget_micros column — using cost_micros_w7_mean proxy for campaign {}".format(campaign_id))
        else:
            budget_value = 50.0  # absolute fallback: £50/day
            print("[ENGINE] cost_micros_w7_mean also unavailable for campaign {} — using £50 fallback".format(campaign_id))

        for rule in enabled_rules:
            rule_id   = rule["rule_id"]
            rule_type = rule["rule_type"]

            # Skip if pending rec already exists for this campaign + rule
            if (campaign_id, rule_id) in existing_pending:
                skipped_duplicate += 1
                continue

            # --- Evaluate primary condition ---------------------------------
            metric   = rule["condition_metric"]
            operator = rule["condition_operator"]
            value    = rule["condition_value"]
            unit     = rule.get("condition_unit", "absolute")

            # Resolve x_target threshold
            if unit == "x_target":
                effective_threshold = value * target_roas
            else:
                effective_threshold = value

            # Get actual metric value from features
            if metric not in METRIC_MAP:
                skipped_no_data += 1
                continue

            db_col, override_op, override_threshold = METRIC_MAP[metric]
            actual_value = features.get(db_col)

            # Log proxy usage
            if metric in PROXY_METRICS:
                print("[ENGINE] Using proxy '{}' for metric '{}' on campaign {}".format(
                    db_col, metric, campaign_id))

            # Determine effective operator and threshold (proxy overrides)
            eff_op        = override_op if override_op else operator
            eff_threshold = override_threshold if override_threshold is not None else effective_threshold

            if actual_value is None:
                skipped_no_data += 1
                continue

            cond1_passed = _evaluate(actual_value, eff_op, eff_threshold)

            if not cond1_passed:
                continue

            # --- Evaluate secondary condition (if present) ------------------
            metric2 = rule.get("condition_2_metric")
            if metric2:
                op2    = rule["condition_2_operator"]
                val2   = rule["condition_2_value"]
                unit2  = rule.get("condition_2_unit", "absolute")

                if metric2 not in METRIC_MAP:
                    skipped_no_data += 1
                    continue

                db_col2, override_op2, override_threshold2 = METRIC_MAP[metric2]
                actual2 = features.get(db_col2)

                if metric2 in PROXY_METRICS:
                    print("[ENGINE] Using proxy '{}' for condition_2 metric '{}' on campaign {}".format(
                        db_col2, metric2, campaign_id))

                eff_op2 = override_op2 if override_op2 else op2

                if unit2 == "x_target":
                    eff_threshold2 = val2 * target_roas
                else:
                    eff_threshold2 = override_threshold2 if override_threshold2 is not None else val2

                if actual2 is None:
                    skipped_no_data += 1
                    continue

                cond2_passed = _evaluate(actual2, eff_op2, eff_threshold2)
                if not cond2_passed:
                    continue

            # --- Both conditions passed — build recommendation --------------

            # current_value depends on rule_type
            if rule_type == "budget":
                current_value = budget_value
            elif rule_type in ("bid", "status"):
                current_value = target_roas
            else:
                current_value = target_roas

            proposed_value  = _calculate_proposed_value(rule, current_value)
            trigger_summary = _build_trigger_summary(rule, features, target_roas)
            confidence      = RISK_TO_CONFIDENCE.get(rule.get("risk_level", "medium"), "medium")

            rec = {
                "rec_id":            str(uuid.uuid4()),
                "rule_id":           rule_id,
                "rule_type":         rule_type,
                "campaign_id":       campaign_id,
                "campaign_name":     campaign_name,
                "customer_id":       customer_id,
                "status":            "pending",
                "action_direction":  rule["action_direction"],
                "action_magnitude":  rule.get("action_magnitude", 0),
                "current_value":     round(current_value, 4),
                "proposed_value":    round(proposed_value, 4),
                "trigger_summary":   trigger_summary,
                "confidence":        confidence,
                "generated_at":      now,
                "accepted_at":       None,
                "monitoring_ends_at":None,
                "resolved_at":       None,
                "outcome_metric":    None,
                "created_at":        now,
                "updated_at":        now,
            }

            new_recs.append(rec)
            existing_pending.add((campaign_id, rule_id))  # prevent duplicates within same run
            generated += 1

            print("[ENGINE] Generated: {} | campaign {} | {}".format(
                rule_id, campaign_id, rule["action_direction"]))

    # --- Bulk insert --------------------------------------------------------
    if new_recs:
        conn.executemany("""
            INSERT INTO recommendations (
                rec_id, rule_id, rule_type, campaign_id, campaign_name, customer_id,
                status, action_direction, action_magnitude,
                current_value, proposed_value, trigger_summary, confidence,
                generated_at, accepted_at, monitoring_ends_at, resolved_at,
                outcome_metric, created_at, updated_at
            ) VALUES (
                ?, ?, ?, ?, ?, ?,
                ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?
            )
        """, [
            (
                r["rec_id"], r["rule_id"], r["rule_type"],
                r["campaign_id"], r["campaign_name"], r["customer_id"],
                r["status"], r["action_direction"], r["action_magnitude"],
                r["current_value"], r["proposed_value"], r["trigger_summary"],
                r["confidence"], r["generated_at"], r["accepted_at"],
                r["monitoring_ends_at"], r["resolved_at"], r["outcome_metric"],
                r["created_at"], r["updated_at"],
            )
            for r in new_recs
        ])

    conn.close()

    result = {
        "generated":         generated,
        "skipped_duplicate": skipped_duplicate,
        "skipped_no_data":   skipped_no_data,
        "skipped_no_target": skipped_no_target,
        "errors":            errors,
        "customer_id":       customer_id,
    }

    print("[ENGINE] Done. Generated={} | SkippedDuplicate={} | SkippedNoData={} | Errors={}".format(
        generated, skipped_duplicate, skipped_no_data, len(errors)))

    return result
