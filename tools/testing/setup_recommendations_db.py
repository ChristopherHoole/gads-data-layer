"""
Setup Recommendations DB — Chat 27 (M6)

Creates the `recommendations` table in warehouse.duckdb and seeds
historical data for Synthetic_Test_Client so History / Monitoring tabs
are not empty on first load.

Run from project root:
    python tools/testing/setup_recommendations_db.py

Optional flags:
    --db         Path to warehouse.duckdb  (default: warehouse.duckdb)
    --customer   Customer ID               (default: 9999999999)
    --drop       Drop and recreate table   (use if schema has changed)
"""

import argparse
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import duckdb

# ---------------------------------------------------------------------------
# DDL
# ---------------------------------------------------------------------------
RECOMMENDATIONS_DDL = """
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
"""

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _id():
    return str(uuid.uuid4())


def _ts(days_offset=0, hour=9):
    """
    Return datetime relative to now.
    Positive days_offset = past. Negative = future.
    """
    base = datetime.now().replace(hour=hour, minute=0, second=0, microsecond=0)
    return base - timedelta(days=days_offset)


def get_real_campaigns(conn, customer_id):
    """Fetch campaigns from analytics.campaign_daily (warehouse.duckdb)."""
    try:
        rows = conn.execute("""
            SELECT DISTINCT
                campaign_id,
                campaign_name,
                budget_micros,
                target_roas
            FROM analytics.campaign_daily
            WHERE customer_id = ?
            ORDER BY campaign_id
        """, [customer_id]).fetchall()
        result = []
        for r in rows:
            result.append({
                "campaign_id":   r[0],
                "campaign_name": r[1] or "Campaign_{}".format(r[0]),
                "budget_micros": r[2] if r[2] else 50_000_000,
                "target_roas":   r[3] if r[3] else 4.0,
            })
        return result
    except Exception as e:
        print("  WARNING: Could not query analytics.campaign_daily: {}".format(e))
        return []


def build_seed_rows(customer_id, campaigns):
    """
    Build 22 historical rows.
    Mix: 8 successful, 4 reverted, 6 declined, 4 monitoring.
    """
    fallback = [
        {"campaign_id": 2001, "campaign_name": "Campaign_2001_STABLE",     "budget_micros": 50_000_000, "target_roas": 4.0},
        {"campaign_id": 2002, "campaign_name": "Campaign_2002_STABLE",     "budget_micros": 75_000_000, "target_roas": 3.5},
        {"campaign_id": 2003, "campaign_name": "Campaign_2003_COST_SPIKE", "budget_micros": 40_000_000, "target_roas": 4.0},
        {"campaign_id": 2005, "campaign_name": "Campaign_2005_CTR_DROP",   "budget_micros": 30_000_000, "target_roas": 3.0},
        {"campaign_id": 2006, "campaign_name": "Campaign_2006_CVR_DROP",   "budget_micros": 60_000_000, "target_roas": 5.0},
        {"campaign_id": 2007, "campaign_name": "Campaign_2007_VOLATILE",   "budget_micros": 45_000_000, "target_roas": 4.5},
    ]
    if len(campaigns) < 4:
        print("  WARNING: Only {} campaigns in DB — using synthetic fallbacks.".format(len(campaigns)))
        campaigns = fallback

    def c(idx):
        return campaigns[idx % len(campaigns)]

    def bv(cam):
        return round(cam["budget_micros"] / 1_000_000, 2)

    def rv(cam):
        return cam["target_roas"]

    rows = []

    # =========================================================================
    # SUCCESSFUL (8)
    # =========================================================================
    cam = c(0)
    rows.append({"rec_id": _id(), "rule_id": "budget_1", "rule_type": "budget",
        "campaign_id": cam["campaign_id"], "campaign_name": cam["campaign_name"],
        "customer_id": customer_id, "status": "successful",
        "action_direction": "increase", "action_magnitude": 10,
        "current_value": bv(cam), "proposed_value": round(bv(cam) * 1.10, 2),
        "trigger_summary": "ROAS (7d) 5.8x > target 4.0x x 1.15 | Clicks (7d) 45 >= 30",
        "confidence": "high",
        "generated_at": _ts(28), "accepted_at": _ts(27), "monitoring_ends_at": _ts(20),
        "resolved_at": _ts(21), "outcome_metric": 5.9, "created_at": _ts(28), "updated_at": _ts(21)})

    cam = c(1)
    rows.append({"rec_id": _id(), "rule_id": "bid_1", "rule_type": "bid",
        "campaign_id": cam["campaign_id"], "campaign_name": cam["campaign_name"],
        "customer_id": customer_id, "status": "successful",
        "action_direction": "increase", "action_magnitude": 8,
        "current_value": rv(cam), "proposed_value": round(rv(cam) * 1.08, 2),
        "trigger_summary": "ROAS (30d) 4.2x > target 3.5x x 1.15",
        "confidence": "high",
        "generated_at": _ts(26), "accepted_at": _ts(25), "monitoring_ends_at": _ts(18),
        "resolved_at": _ts(19), "outcome_metric": 4.5, "created_at": _ts(26), "updated_at": _ts(19)})

    cam = c(2)
    rows.append({"rec_id": _id(), "rule_id": "budget_1", "rule_type": "budget",
        "campaign_id": cam["campaign_id"], "campaign_name": cam["campaign_name"],
        "customer_id": customer_id, "status": "successful",
        "action_direction": "increase", "action_magnitude": 10,
        "current_value": bv(cam), "proposed_value": round(bv(cam) * 1.10, 2),
        "trigger_summary": "ROAS (7d) 6.1x > target 4.0x x 1.15 | Clicks (7d) 52 >= 30",
        "confidence": "high",
        "generated_at": _ts(22), "accepted_at": _ts(21), "monitoring_ends_at": _ts(14),
        "resolved_at": _ts(14), "outcome_metric": 6.3, "created_at": _ts(22), "updated_at": _ts(14)})

    cam = c(3)
    rows.append({"rec_id": _id(), "rule_id": "bid_2", "rule_type": "bid",
        "campaign_id": cam["campaign_id"], "campaign_name": cam["campaign_name"],
        "customer_id": customer_id, "status": "successful",
        "action_direction": "decrease", "action_magnitude": 8,
        "current_value": rv(cam), "proposed_value": round(rv(cam) * 0.92, 2),
        "trigger_summary": "ROAS (30d) 1.9x < target 3.0x x 0.75",
        "confidence": "medium",
        "generated_at": _ts(20), "accepted_at": _ts(19), "monitoring_ends_at": _ts(12),
        "resolved_at": _ts(12), "outcome_metric": 2.8, "created_at": _ts(20), "updated_at": _ts(12)})

    cam = c(4)
    rows.append({"rec_id": _id(), "rule_id": "budget_4", "rule_type": "budget",
        "campaign_id": cam["campaign_id"], "campaign_name": cam["campaign_name"],
        "customer_id": customer_id, "status": "successful",
        "action_direction": "decrease", "action_magnitude": 10,
        "current_value": bv(cam), "proposed_value": round(bv(cam) * 0.90, 2),
        "trigger_summary": "ROAS (7d) 1.8x < target 5.0x x 0.75",
        "confidence": "high",
        "generated_at": _ts(18), "accepted_at": _ts(17), "monitoring_ends_at": _ts(10),
        "resolved_at": _ts(10), "outcome_metric": 2.1, "created_at": _ts(18), "updated_at": _ts(10)})

    cam = c(5)
    rows.append({"rec_id": _id(), "rule_id": "bid_1", "rule_type": "bid",
        "campaign_id": cam["campaign_id"], "campaign_name": cam["campaign_name"],
        "customer_id": customer_id, "status": "successful",
        "action_direction": "increase", "action_magnitude": 8,
        "current_value": rv(cam), "proposed_value": round(rv(cam) * 1.08, 2),
        "trigger_summary": "ROAS (30d) 5.9x > target 4.5x x 1.15",
        "confidence": "high",
        "generated_at": _ts(15), "accepted_at": _ts(14), "monitoring_ends_at": _ts(7),
        "resolved_at": _ts(7), "outcome_metric": 6.1, "created_at": _ts(15), "updated_at": _ts(7)})

    cam = c(0)
    rows.append({"rec_id": _id(), "rule_id": "budget_1", "rule_type": "budget",
        "campaign_id": cam["campaign_id"], "campaign_name": cam["campaign_name"],
        "customer_id": customer_id, "status": "successful",
        "action_direction": "increase", "action_magnitude": 10,
        "current_value": round(bv(cam) * 1.10, 2), "proposed_value": round(bv(cam) * 1.21, 2),
        "trigger_summary": "ROAS (7d) 6.4x > target 4.0x x 1.15 | Clicks (7d) 61 >= 30",
        "confidence": "high",
        "generated_at": _ts(12), "accepted_at": _ts(11), "monitoring_ends_at": _ts(4),
        "resolved_at": _ts(4), "outcome_metric": 6.6, "created_at": _ts(12), "updated_at": _ts(4)})

    cam = c(1)
    rows.append({"rec_id": _id(), "rule_id": "budget_2", "rule_type": "budget",
        "campaign_id": cam["campaign_id"], "campaign_name": cam["campaign_name"],
        "customer_id": customer_id, "status": "successful",
        "action_direction": "decrease", "action_magnitude": 10,
        "current_value": bv(cam), "proposed_value": round(bv(cam) * 0.90, 2),
        "trigger_summary": "ROAS (7d) 2.1x < target 3.5x x 0.75 | Clicks (7d) 38 >= 30 | Conversions (30d) 18 >= 15",
        "confidence": "high",
        "generated_at": _ts(10), "accepted_at": _ts(9), "monitoring_ends_at": _ts(2),
        "resolved_at": _ts(2), "outcome_metric": 3.1, "created_at": _ts(10), "updated_at": _ts(2)})

    # =========================================================================
    # REVERTED (4)
    # =========================================================================
    cam = c(2)
    rows.append({"rec_id": _id(), "rule_id": "budget_1", "rule_type": "budget",
        "campaign_id": cam["campaign_id"], "campaign_name": cam["campaign_name"],
        "customer_id": customer_id, "status": "reverted",
        "action_direction": "increase", "action_magnitude": 10,
        "current_value": bv(cam), "proposed_value": round(bv(cam) * 1.10, 2),
        "trigger_summary": "ROAS (7d) 5.2x > target 4.0x x 1.15 | Clicks (7d) 33 >= 30",
        "confidence": "high",
        "generated_at": _ts(25), "accepted_at": _ts(24), "monitoring_ends_at": _ts(17),
        "resolved_at": _ts(20), "outcome_metric": 2.9, "created_at": _ts(25), "updated_at": _ts(20)})

    cam = c(3)
    rows.append({"rec_id": _id(), "rule_id": "bid_2", "rule_type": "bid",
        "campaign_id": cam["campaign_id"], "campaign_name": cam["campaign_name"],
        "customer_id": customer_id, "status": "reverted",
        "action_direction": "decrease", "action_magnitude": 8,
        "current_value": rv(cam), "proposed_value": round(rv(cam) * 0.92, 2),
        "trigger_summary": "ROAS (30d) 1.7x < target 3.0x x 0.75",
        "confidence": "medium",
        "generated_at": _ts(17), "accepted_at": _ts(16), "monitoring_ends_at": _ts(9),
        "resolved_at": _ts(13), "outcome_metric": 1.1, "created_at": _ts(17), "updated_at": _ts(13)})

    cam = c(4)
    rows.append({"rec_id": _id(), "rule_id": "budget_3", "rule_type": "budget",
        "campaign_id": cam["campaign_id"], "campaign_name": cam["campaign_name"],
        "customer_id": customer_id, "status": "reverted",
        "action_direction": "decrease", "action_magnitude": 10,
        "current_value": bv(cam), "proposed_value": round(bv(cam) * 0.90, 2),
        "trigger_summary": "Cost spike detected: anomaly z-score 2.4 >= 2.0",
        "confidence": "medium",
        "generated_at": _ts(14), "accepted_at": _ts(13), "monitoring_ends_at": _ts(6),
        "resolved_at": _ts(9), "outcome_metric": None, "created_at": _ts(14), "updated_at": _ts(9)})

    cam = c(5)
    rows.append({"rec_id": _id(), "rule_id": "status_1", "rule_type": "status",
        "campaign_id": cam["campaign_id"], "campaign_name": cam["campaign_name"],
        "customer_id": customer_id, "status": "reverted",
        "action_direction": "flag", "action_magnitude": 0,
        "current_value": rv(cam), "proposed_value": rv(cam),
        "trigger_summary": "ROAS (30d) 1.2x < target 4.5x x 0.50",
        "confidence": "low",
        "generated_at": _ts(11), "accepted_at": _ts(10), "monitoring_ends_at": _ts(3),
        "resolved_at": _ts(6), "outcome_metric": 1.4, "created_at": _ts(11), "updated_at": _ts(6)})

    # =========================================================================
    # DECLINED (6)
    # =========================================================================
    cam = c(0)
    rows.append({"rec_id": _id(), "rule_id": "budget_4", "rule_type": "budget",
        "campaign_id": cam["campaign_id"], "campaign_name": cam["campaign_name"],
        "customer_id": customer_id, "status": "declined",
        "action_direction": "decrease", "action_magnitude": 10,
        "current_value": bv(cam), "proposed_value": round(bv(cam) * 0.90, 2),
        "trigger_summary": "ROAS (7d) 2.3x < target 4.0x x 0.75",
        "confidence": "high",
        "generated_at": _ts(29), "accepted_at": None, "monitoring_ends_at": None,
        "resolved_at": _ts(29), "outcome_metric": None, "created_at": _ts(29), "updated_at": _ts(29)})

    cam = c(1)
    rows.append({"rec_id": _id(), "rule_id": "bid_4", "rule_type": "bid",
        "campaign_id": cam["campaign_id"], "campaign_name": cam["campaign_name"],
        "customer_id": customer_id, "status": "declined",
        "action_direction": "decrease", "action_magnitude": 8,
        "current_value": rv(cam), "proposed_value": round(rv(cam) * 0.92, 2),
        "trigger_summary": "Conversions (30d) 8 < 15 (low volume threshold)",
        "confidence": "medium",
        "generated_at": _ts(23), "accepted_at": None, "monitoring_ends_at": None,
        "resolved_at": _ts(23), "outcome_metric": None, "created_at": _ts(23), "updated_at": _ts(23)})

    cam = c(2)
    rows.append({"rec_id": _id(), "rule_id": "status_3", "rule_type": "status",
        "campaign_id": cam["campaign_id"], "campaign_name": cam["campaign_name"],
        "customer_id": customer_id, "status": "declined",
        "action_direction": "flag", "action_magnitude": 0,
        "current_value": rv(cam), "proposed_value": rv(cam),
        "trigger_summary": "ROAS (30d) 5.1x > target 4.0x x 1.20 sustained",
        "confidence": "low",
        "generated_at": _ts(19), "accepted_at": None, "monitoring_ends_at": None,
        "resolved_at": _ts(19), "outcome_metric": None, "created_at": _ts(19), "updated_at": _ts(19)})

    cam = c(3)
    rows.append({"rec_id": _id(), "rule_id": "budget_6", "rule_type": "budget",
        "campaign_id": cam["campaign_id"], "campaign_name": cam["campaign_name"],
        "customer_id": customer_id, "status": "declined",
        "action_direction": "hold", "action_magnitude": 0,
        "current_value": bv(cam), "proposed_value": bv(cam),
        "trigger_summary": "Cost volatility (CV 14d) 0.42 >= 0.35 threshold",
        "confidence": "medium",
        "generated_at": _ts(16), "accepted_at": None, "monitoring_ends_at": None,
        "resolved_at": _ts(16), "outcome_metric": None, "created_at": _ts(16), "updated_at": _ts(16)})

    cam = c(4)
    rows.append({"rec_id": _id(), "rule_id": "bid_3", "rule_type": "bid",
        "campaign_id": cam["campaign_id"], "campaign_name": cam["campaign_name"],
        "customer_id": customer_id, "status": "declined",
        "action_direction": "hold", "action_magnitude": 0,
        "current_value": rv(cam), "proposed_value": rv(cam),
        "trigger_summary": "CVR drop detected: cvr_w7_vs_prev_pct -24.1% <= -20%",
        "confidence": "medium",
        "generated_at": _ts(8), "accepted_at": None, "monitoring_ends_at": None,
        "resolved_at": _ts(8), "outcome_metric": None, "created_at": _ts(8), "updated_at": _ts(8)})

    cam = c(5)
    rows.append({"rec_id": _id(), "rule_id": "status_2", "rule_type": "status",
        "campaign_id": cam["campaign_id"], "campaign_name": cam["campaign_name"],
        "customer_id": customer_id, "status": "declined",
        "action_direction": "flag", "action_magnitude": 0,
        "current_value": rv(cam), "proposed_value": rv(cam),
        "trigger_summary": "CTR drop detected: ctr_w7_vs_prev_pct -31.2% <= -20%",
        "confidence": "low",
        "generated_at": _ts(5), "accepted_at": None, "monitoring_ends_at": None,
        "resolved_at": _ts(5), "outcome_metric": None, "created_at": _ts(5), "updated_at": _ts(5)})

    # =========================================================================
    # MONITORING (4) — accepted, period still active (monitoring_ends_at is future)
    # =========================================================================
    cam = c(0)
    rows.append({"rec_id": _id(), "rule_id": "budget_1", "rule_type": "budget",
        "campaign_id": cam["campaign_id"], "campaign_name": cam["campaign_name"],
        "customer_id": customer_id, "status": "monitoring",
        "action_direction": "increase", "action_magnitude": 10,
        "current_value": bv(cam), "proposed_value": round(bv(cam) * 1.10, 2),
        "trigger_summary": "ROAS (7d) 5.5x > target 4.0x x 1.15 | Clicks (7d) 48 >= 30",
        "confidence": "high",
        "generated_at": _ts(9), "accepted_at": _ts(8),
        "monitoring_ends_at": _ts(-6),
        "resolved_at": None, "outcome_metric": 5.7, "created_at": _ts(9), "updated_at": _ts(1)})

    cam = c(1)
    rows.append({"rec_id": _id(), "rule_id": "bid_1", "rule_type": "bid",
        "campaign_id": cam["campaign_id"], "campaign_name": cam["campaign_name"],
        "customer_id": customer_id, "status": "monitoring",
        "action_direction": "increase", "action_magnitude": 8,
        "current_value": rv(cam), "proposed_value": round(rv(cam) * 1.08, 2),
        "trigger_summary": "ROAS (30d) 4.4x > target 3.5x x 1.15",
        "confidence": "high",
        "generated_at": _ts(7), "accepted_at": _ts(6),
        "monitoring_ends_at": _ts(-8),
        "resolved_at": None, "outcome_metric": 4.3, "created_at": _ts(7), "updated_at": _ts(1)})

    cam = c(2)
    rows.append({"rec_id": _id(), "rule_id": "budget_2", "rule_type": "budget",
        "campaign_id": cam["campaign_id"], "campaign_name": cam["campaign_name"],
        "customer_id": customer_id, "status": "monitoring",
        "action_direction": "decrease", "action_magnitude": 10,
        "current_value": bv(cam), "proposed_value": round(bv(cam) * 0.90, 2),
        "trigger_summary": "ROAS (7d) 1.9x < target 4.0x x 0.75 | Clicks (7d) 41 >= 30 | Conversions (30d) 16 >= 15",
        "confidence": "high",
        "generated_at": _ts(5), "accepted_at": _ts(4),
        "monitoring_ends_at": _ts(-3),
        "resolved_at": None, "outcome_metric": 2.2, "created_at": _ts(5), "updated_at": _ts(1)})

    cam = c(3)
    rows.append({"rec_id": _id(), "rule_id": "bid_2", "rule_type": "bid",
        "campaign_id": cam["campaign_id"], "campaign_name": cam["campaign_name"],
        "customer_id": customer_id, "status": "monitoring",
        "action_direction": "decrease", "action_magnitude": 8,
        "current_value": rv(cam), "proposed_value": round(rv(cam) * 0.92, 2),
        "trigger_summary": "ROAS (30d) 1.6x < target 3.0x x 0.75",
        "confidence": "medium",
        "generated_at": _ts(3), "accepted_at": _ts(2),
        "monitoring_ends_at": _ts(-5),
        "resolved_at": None, "outcome_metric": 1.8, "created_at": _ts(3), "updated_at": _ts(1)})

    return rows


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def setup(db_path, customer_id, drop=False):
    print("\n" + "=" * 60)
    print("  Recommendations DB Setup")
    print("  DB      : {}".format(db_path))
    print("  Customer: {}".format(customer_id))
    print("=" * 60 + "\n")

    conn = duckdb.connect(db_path, read_only=False)

    if drop:
        print("  Dropping existing recommendations table...")
        conn.execute("DROP TABLE IF EXISTS recommendations;")
        print("  Done.\n")

    print("  Creating recommendations table (if not exists)...")
    conn.execute(RECOMMENDATIONS_DDL)
    print("  Table ready.\n")

    existing = conn.execute(
        "SELECT COUNT(*) FROM recommendations WHERE customer_id = ?", [customer_id]
    ).fetchone()[0]

    if existing > 0 and not drop:
        print("  {} rows already exist for customer {}.".format(existing, customer_id))
        print("  Use --drop to wipe and re-seed. Skipping.\n")
        conn.close()
        return

    print("  Fetching campaigns from analytics.campaign_daily...")
    campaigns = get_real_campaigns(conn, customer_id)
    if campaigns:
        print("  Found {} campaigns: {}\n".format(len(campaigns), [c["campaign_id"] for c in campaigns]))
    else:
        print("  No campaigns in DB — using synthetic fallback IDs.\n")

    print("  Building seed rows...")
    rows = build_seed_rows(customer_id, campaigns)
    print("  Built {} rows.\n".format(len(rows)))

    print("  Inserting rows...")
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
        for r in rows
    ])
    conn.close()

    # Verify
    conn2 = duckdb.connect(db_path, read_only=True)

    def count(status):
        return conn2.execute(
            "SELECT COUNT(*) FROM recommendations WHERE customer_id = ? AND status = ?",
            [customer_id, status]
        ).fetchone()[0]

    total = conn2.execute(
        "SELECT COUNT(*) FROM recommendations WHERE customer_id = ?", [customer_id]
    ).fetchone()[0]

    print("\n  Seed complete!")
    print("  Total rows  : {}".format(total))
    print("  Successful  : {}".format(count("successful")))
    print("  Reverted    : {}".format(count("reverted")))
    print("  Declined    : {}".format(count("declined")))
    print("  Monitoring  : {}".format(count("monitoring")))
    print("  Pending     : {}".format(count("pending")))
    conn2.close()
    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create and seed the recommendations table.")
    parser.add_argument("--db",       default="warehouse.duckdb", help="Path to warehouse.duckdb")
    parser.add_argument("--customer", default="9999999999",        help="Customer ID to seed")
    parser.add_argument("--drop",     action="store_true",         help="Drop and recreate table")
    args = parser.parse_args()

    db_path = str(Path(args.db).resolve())
    setup(db_path, args.customer, drop=args.drop)
