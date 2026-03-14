#!/usr/bin/env python3
"""
tools/seed_campaign_rules.py

Chat 91: Seeds all 54 campaign rules and flags into warehouse.duckdb.
         24 rules (15 budget, 6 bid, 3 status) + 30 flags (16 perf, 8 anomaly, 6 technical).
         Safe to re-run (DELETE all then INSERT).

Run from project root:
    python tools/seed_campaign_rules.py
"""

import json
import sys
from pathlib import Path
import duckdb

WAREHOUSE_PATH = Path(__file__).parent.parent / "warehouse.duckdb"
CLIENT_CONFIG = "client_christopher_hoole"
ENTITY_SCOPE = json.dumps({"scope": "all"})


def j(conditions_list):
    """Serialise conditions list to JSON string."""
    return json.dumps(conditions_list)


# ── BUDGET RULES — tROAS (5) ──────────────────────────────────────────────────
BUDGET_TROAS = [
    {
        "name": "Increase Budget – Strong ROAS",
        "campaign_type_lock": "troas",
        "conditions": j([
            {"metric": "roas_7d", "operator": ">=", "value": 1.15, "unit": "x_target"},
            {"metric": "clicks_7d", "operator": ">=", "value": 30, "unit": "absolute"},
        ]),
        "action_type": "increase_budget",
        "action_magnitude": 10.0,
        "cooldown_days": 7,
        "risk_level": "low",
    },
    {
        "name": "Decrease Budget – Weak ROAS",
        "campaign_type_lock": "troas",
        "conditions": j([
            {"metric": "roas_7d", "operator": "<", "value": 0.85, "unit": "x_target"},
            {"metric": "clicks_7d", "operator": ">=", "value": 30, "unit": "absolute"},
        ]),
        "action_type": "decrease_budget",
        "action_magnitude": 10.0,
        "cooldown_days": 7,
        "risk_level": "low",
    },
    {
        "name": "Emergency Budget Cut – Critical ROAS",
        "campaign_type_lock": "troas",
        "conditions": j([
            {"metric": "roas_7d", "operator": "<", "value": 0.50, "unit": "x_target"},
            {"metric": "cost_7d", "operator": ">=", "value": 100, "unit": "absolute"},
        ]),
        "action_type": "decrease_budget",
        "action_magnitude": 25.0,
        "cooldown_days": 14,
        "risk_level": "medium",
    },
    {
        "name": "Pacing Reduction – Over Budget",
        "campaign_type_lock": "troas",
        "conditions": j([
            {"metric": "pacing_vs_cap", "operator": ">", "value": 105, "unit": "percent"},
        ]),
        "action_type": "decrease_budget",
        "action_magnitude": 15.0,
        "cooldown_days": 7,
        "risk_level": "medium",
    },
    {
        "name": "Pacing Increase – Under Budget",
        "campaign_type_lock": "troas",
        "conditions": j([
            {"metric": "pacing_vs_cap", "operator": "<", "value": 80, "unit": "percent"},
            {"metric": "roas_7d", "operator": ">=", "value": 1.0, "unit": "x_target"},
        ]),
        "action_type": "increase_budget",
        "action_magnitude": 10.0,
        "cooldown_days": 7,
        "risk_level": "low",
    },
]

# ── BUDGET RULES — tCPA (5) ───────────────────────────────────────────────────
BUDGET_TCPA = [
    {
        "name": "Increase Budget – Strong CPA",
        "campaign_type_lock": "tcpa",
        "conditions": j([
            {"metric": "cpa_7d", "operator": "<=", "value": 0.90, "unit": "x_target"},
            {"metric": "conversions_7d", "operator": ">=", "value": 10, "unit": "absolute"},
        ]),
        "action_type": "increase_budget",
        "action_magnitude": 10.0,
        "cooldown_days": 7,
        "risk_level": "low",
    },
    {
        "name": "Decrease Budget – Weak CPA",
        "campaign_type_lock": "tcpa",
        "conditions": j([
            {"metric": "cpa_7d", "operator": ">", "value": 1.20, "unit": "x_target"},
            {"metric": "conversions_7d", "operator": ">=", "value": 5, "unit": "absolute"},
        ]),
        "action_type": "decrease_budget",
        "action_magnitude": 10.0,
        "cooldown_days": 7,
        "risk_level": "low",
    },
    {
        "name": "Emergency Budget Cut – Critical CPA",
        "campaign_type_lock": "tcpa",
        "conditions": j([
            {"metric": "cpa_7d", "operator": ">", "value": 2.0, "unit": "x_target"},
            {"metric": "cost_7d", "operator": ">=", "value": 100, "unit": "absolute"},
        ]),
        "action_type": "decrease_budget",
        "action_magnitude": 25.0,
        "cooldown_days": 14,
        "risk_level": "medium",
    },
    {
        "name": "Pacing Reduction – Over Budget",
        "campaign_type_lock": "tcpa",
        "conditions": j([
            {"metric": "pacing_vs_cap", "operator": ">", "value": 105, "unit": "percent"},
        ]),
        "action_type": "decrease_budget",
        "action_magnitude": 15.0,
        "cooldown_days": 7,
        "risk_level": "medium",
    },
    {
        "name": "Pacing Increase – Under Budget",
        "campaign_type_lock": "tcpa",
        "conditions": j([
            {"metric": "pacing_vs_cap", "operator": "<", "value": 80, "unit": "percent"},
            {"metric": "cpa_7d", "operator": "<=", "value": 1.0, "unit": "x_target"},
        ]),
        "action_type": "increase_budget",
        "action_magnitude": 10.0,
        "cooldown_days": 7,
        "risk_level": "low",
    },
]

# ── BUDGET RULES — Max Clicks (5) ─────────────────────────────────────────────
BUDGET_MAX_CLICKS = [
    {
        "name": "Increase Budget – Strong CTR",
        "campaign_type_lock": "max_clicks",
        "conditions": j([
            {"metric": "ctr_7d", "operator": ">=", "value": 5.0, "unit": "percent"},
            {"metric": "clicks_7d", "operator": ">=", "value": 50, "unit": "absolute"},
        ]),
        "action_type": "increase_budget",
        "action_magnitude": 10.0,
        "cooldown_days": 7,
        "risk_level": "low",
    },
    {
        "name": "Decrease Budget – Weak CTR",
        "campaign_type_lock": "max_clicks",
        "conditions": j([
            {"metric": "ctr_7d", "operator": "<", "value": 2.0, "unit": "percent"},
            {"metric": "clicks_7d", "operator": ">=", "value": 50, "unit": "absolute"},
        ]),
        "action_type": "decrease_budget",
        "action_magnitude": 10.0,
        "cooldown_days": 7,
        "risk_level": "low",
    },
    {
        "name": "Emergency Budget Cut – Very Low CTR",
        "campaign_type_lock": "max_clicks",
        "conditions": j([
            {"metric": "ctr_7d", "operator": "<", "value": 1.0, "unit": "percent"},
            {"metric": "cost_7d", "operator": ">=", "value": 100, "unit": "absolute"},
        ]),
        "action_type": "decrease_budget",
        "action_magnitude": 25.0,
        "cooldown_days": 14,
        "risk_level": "medium",
    },
    {
        "name": "Pacing Reduction – Over Budget",
        "campaign_type_lock": "max_clicks",
        "conditions": j([
            {"metric": "pacing_vs_cap", "operator": ">", "value": 105, "unit": "percent"},
        ]),
        "action_type": "decrease_budget",
        "action_magnitude": 15.0,
        "cooldown_days": 7,
        "risk_level": "medium",
    },
    {
        "name": "Pacing Increase – Under Budget",
        "campaign_type_lock": "max_clicks",
        "conditions": j([
            {"metric": "pacing_vs_cap", "operator": "<", "value": 80, "unit": "percent"},
            {"metric": "ctr_7d", "operator": ">=", "value": 3.0, "unit": "percent"},
        ]),
        "action_type": "increase_budget",
        "action_magnitude": 10.0,
        "cooldown_days": 7,
        "risk_level": "low",
    },
]

# ── BID RULES — tROAS (2) ─────────────────────────────────────────────────────
BID_TROAS = [
    {
        "name": "Tighten tROAS Target – Strong Performance",
        "campaign_type_lock": "troas",
        "conditions": j([
            {"metric": "roas_14d", "operator": ">=", "value": 1.20, "unit": "x_target"},
            {"metric": "conversions_14d", "operator": ">=", "value": 15, "unit": "absolute"},
        ]),
        "action_type": "increase_target_roas",
        "action_magnitude": 5.0,
        "cooldown_days": 14,
        "risk_level": "medium",
    },
    {
        "name": "Loosen tROAS Target – Constrained Volume",
        "campaign_type_lock": "troas",
        "conditions": j([
            {"metric": "roas_14d", "operator": ">=", "value": 1.05, "unit": "x_target"},
            {"metric": "impression_share_lost_rank", "operator": ">", "value": 20, "unit": "percent"},
        ]),
        "action_type": "decrease_target_roas",
        "action_magnitude": 5.0,
        "cooldown_days": 14,
        "risk_level": "medium",
    },
]

# ── BID RULES — tCPA (2) ──────────────────────────────────────────────────────
BID_TCPA = [
    {
        "name": "Tighten tCPA Target – Strong CPA",
        "campaign_type_lock": "tcpa",
        "conditions": j([
            {"metric": "cpa_14d", "operator": "<=", "value": 0.85, "unit": "x_target"},
            {"metric": "conversions_14d", "operator": ">=", "value": 15, "unit": "absolute"},
        ]),
        "action_type": "decrease_target_cpa",
        "action_magnitude": 5.0,
        "cooldown_days": 14,
        "risk_level": "medium",
    },
    {
        "name": "Loosen tCPA Target – Volume Constrained",
        "campaign_type_lock": "tcpa",
        "conditions": j([
            {"metric": "cpa_14d", "operator": "<=", "value": 1.05, "unit": "x_target"},
            {"metric": "impression_share_lost_rank", "operator": ">", "value": 20, "unit": "percent"},
        ]),
        "action_type": "increase_target_cpa",
        "action_magnitude": 5.0,
        "cooldown_days": 14,
        "risk_level": "medium",
    },
]

# ── BID RULES — Max Clicks (2) ────────────────────────────────────────────────
BID_MAX_CLICKS = [
    {
        "name": "Increase Max CPC Cap – Low Impression Share",
        "campaign_type_lock": "max_clicks",
        "conditions": j([
            {"metric": "impression_share_lost_rank", "operator": ">", "value": 30, "unit": "percent"},
            {"metric": "clicks_7d", "operator": ">=", "value": 20, "unit": "absolute"},
        ]),
        "action_type": "increase_max_cpc",
        "action_magnitude": 10.0,
        "cooldown_days": 7,
        "risk_level": "medium",
    },
    {
        "name": "Decrease Max CPC Cap – High CPC Low CTR",
        "campaign_type_lock": "max_clicks",
        "conditions": j([
            {"metric": "cpc_avg_7d", "operator": ">", "value": 3.0, "unit": "absolute"},
            {"metric": "ctr_7d", "operator": "<", "value": 2.0, "unit": "percent"},
        ]),
        "action_type": "decrease_max_cpc",
        "action_magnitude": 10.0,
        "cooldown_days": 7,
        "risk_level": "medium",
    },
]

# ── STATUS RULES (3) ──────────────────────────────────────────────────────────
STATUS_RULES = [
    {
        "name": "Pause – Poor ROAS",
        "campaign_type_lock": "troas",
        "conditions": j([
            {"metric": "roas_14d", "operator": "<", "value": 0.50, "unit": "x_target"},
            {"metric": "cost_14d", "operator": ">=", "value": 200, "unit": "absolute"},
        ]),
        "action_type": "pause_campaign",
        "action_magnitude": None,
        "cooldown_days": 14,
        "risk_level": "high",
    },
    {
        "name": "Pause – High CPA",
        "campaign_type_lock": "tcpa",
        "conditions": j([
            {"metric": "cpa_14d", "operator": ">", "value": 2.0, "unit": "x_target"},
            {"metric": "cost_14d", "operator": ">=", "value": 200, "unit": "absolute"},
        ]),
        "action_type": "pause_campaign",
        "action_magnitude": None,
        "cooldown_days": 14,
        "risk_level": "high",
    },
    {
        "name": "Pause – High CPC",
        "campaign_type_lock": "max_clicks",
        "conditions": j([
            {"metric": "cpc_avg_14d", "operator": ">", "value": 5.0, "unit": "absolute"},
            {"metric": "cost_14d", "operator": ">=", "value": 200, "unit": "absolute"},
        ]),
        "action_type": "pause_campaign",
        "action_magnitude": None,
        "cooldown_days": 14,
        "risk_level": "high",
    },
]

# ── PERFORMANCE FLAGS (16) ────────────────────────────────────────────────────
PERFORMANCE_FLAGS = [
    ("ROAS Drop",             j([{"metric": "roas_w7_vs_prev_pct", "operator": "<", "value": -20, "unit": "percent"}])),
    ("ROAS Spike",            j([{"metric": "roas_w7_vs_prev_pct", "operator": ">", "value": 50, "unit": "percent"}])),
    ("CPA Spike",             j([{"metric": "cpa_w7_vs_prev_pct", "operator": ">", "value": 30, "unit": "percent"}])),
    ("CPA Drop",              j([{"metric": "cpa_w7_vs_prev_pct", "operator": "<", "value": -20, "unit": "percent"}])),
    ("CTR Drop",              j([{"metric": "ctr_w7_vs_prev_pct", "operator": "<", "value": -20, "unit": "percent"}])),
    ("CTR Spike",             j([{"metric": "ctr_w7_vs_prev_pct", "operator": ">", "value": 50, "unit": "percent"}])),
    ("CVR Drop",              j([{"metric": "cvr_w7_vs_prev_pct", "operator": "<", "value": -20, "unit": "percent"}])),
    ("CVR Spike",             j([{"metric": "cvr_w7_vs_prev_pct", "operator": ">", "value": 50, "unit": "percent"}])),
    ("Conversion Drop",       j([{"metric": "conversions_w7_vs_prev_pct", "operator": "<", "value": -30, "unit": "percent"}])),
    ("Conversion Spike",      j([{"metric": "conversions_w7_vs_prev_pct", "operator": ">", "value": 50, "unit": "percent"}])),
    ("Spend Drop",            j([{"metric": "cost_w7_vs_prev_pct", "operator": "<", "value": -30, "unit": "percent"}])),
    ("Spend Spike",           j([{"metric": "cost_w7_vs_prev_pct", "operator": ">", "value": 50, "unit": "percent"}])),
    ("Impression Share Drop", j([{"metric": "impression_share_w7_vs_prev_pct", "operator": "<", "value": -20, "unit": "percent"}])),
    ("Impression Share Spike",j([{"metric": "impression_share_w7_vs_prev_pct", "operator": ">", "value": 30, "unit": "percent"}])),
    ("Zero Impressions",      j([{"metric": "impressions_7d", "operator": "=", "value": 0, "unit": "absolute"}])),
    ("CPC Spike",             j([{"metric": "cpc_w7_vs_prev_pct", "operator": ">", "value": 40, "unit": "percent"}])),
]

# ── ANOMALY FLAGS (8) ─────────────────────────────────────────────────────────
ANOMALY_FLAGS = [
    ("Cost Spike",               j([{"metric": "cost_z_score", "operator": ">=", "value": 2.0, "unit": "absolute"}])),
    ("Cost Drop",                j([{"metric": "cost_z_score", "operator": "<=", "value": -2.0, "unit": "absolute"}])),
    ("Click Volume Spike",       j([{"metric": "click_z_score", "operator": ">=", "value": 2.0, "unit": "absolute"}])),
    ("Click Volume Drop",        j([{"metric": "click_z_score", "operator": "<=", "value": -2.0, "unit": "absolute"}])),
    ("Impression Spike",         j([{"metric": "impression_z_score", "operator": ">=", "value": 2.0, "unit": "absolute"}])),
    ("Impression Drop",          j([{"metric": "impression_z_score", "operator": "<=", "value": -2.0, "unit": "absolute"}])),
    ("Zero Conversions",         j([{"metric": "conversions_7d", "operator": "=", "value": 0, "unit": "absolute"}])),
    ("Conversion Tracking Loss", j([{"metric": "conv_tracking_loss_detected", "operator": "=", "value": 1, "unit": "absolute"}])),
]

# ── TECHNICAL FLAGS (6) ───────────────────────────────────────────────────────
TECHNICAL_FLAGS = [
    ("Landing Page Down",    j([{"metric": "landing_page_status", "operator": "=", "value": 0, "unit": "absolute"}])),
    ("Landing Page Slow",    j([{"metric": "landing_page_load_ms", "operator": ">", "value": 3000, "unit": "absolute"}])),
    ("Ad Disapproved",       j([{"metric": "ads_disapproved_count", "operator": ">", "value": 0, "unit": "absolute"}])),
    ("Budget Exhausted Early",j([{"metric": "budget_exhausted_hour", "operator": "<", "value": 18, "unit": "absolute"}])),
    ("Billing Issue",        j([{"metric": "billing_issue_detected", "operator": "=", "value": 1, "unit": "absolute"}])),
    ("Tracking Tag Missing", j([{"metric": "tracking_tag_present", "operator": "=", "value": 0, "unit": "absolute"}])),
]


def build_rows():
    rows = []
    rid = 1

    # Budget rules
    for r in BUDGET_TROAS + BUDGET_TCPA + BUDGET_MAX_CLICKS:
        rows.append((
            rid, CLIENT_CONFIG, "campaign", r["name"],
            "rule", "budget", r["campaign_type_lock"],
            ENTITY_SCOPE, r["conditions"],
            r["action_type"], r["action_magnitude"],
            r["cooldown_days"], r["risk_level"], True,
        ))
        rid += 1

    # Bid rules
    for r in BID_TROAS + BID_TCPA + BID_MAX_CLICKS:
        rows.append((
            rid, CLIENT_CONFIG, "campaign", r["name"],
            "rule", "bid", r["campaign_type_lock"],
            ENTITY_SCOPE, r["conditions"],
            r["action_type"], r["action_magnitude"],
            r["cooldown_days"], r["risk_level"], True,
        ))
        rid += 1

    # Status rules
    for r in STATUS_RULES:
        rows.append((
            rid, CLIENT_CONFIG, "campaign", r["name"],
            "rule", "status", r["campaign_type_lock"],
            ENTITY_SCOPE, r["conditions"],
            r["action_type"], r["action_magnitude"],
            r["cooldown_days"], r["risk_level"], True,
        ))
        rid += 1

    # Performance flags
    for name, conds in PERFORMANCE_FLAGS:
        rows.append((
            rid, CLIENT_CONFIG, "campaign", name,
            "flag", "performance", "all",
            ENTITY_SCOPE, conds,
            None, None, 1, None, True,
        ))
        rid += 1

    # Anomaly flags
    for name, conds in ANOMALY_FLAGS:
        rows.append((
            rid, CLIENT_CONFIG, "campaign", name,
            "flag", "anomaly", "all",
            ENTITY_SCOPE, conds,
            None, None, 1, None, True,
        ))
        rid += 1

    # Technical flags
    for name, conds in TECHNICAL_FLAGS:
        rows.append((
            rid, CLIENT_CONFIG, "campaign", name,
            "flag", "technical", "all",
            ENTITY_SCOPE, conds,
            None, None, 1, None, True,
        ))
        rid += 1

    return rows


def main():
    print("=" * 60)
    print("Chat 91: seed_campaign_rules.py")
    print("=" * 60)

    if not WAREHOUSE_PATH.exists():
        print(f"ERROR: warehouse.duckdb not found at {WAREHOUSE_PATH}")
        sys.exit(1)

    conn = duckdb.connect(str(WAREHOUSE_PATH))

    try:
        # Check rules table exists
        tables = [row[0] for row in conn.execute("SHOW TABLES").fetchall()]
        if "rules" not in tables:
            print("ERROR: rules table not found. Run migrate_rules_schema.py first.")
            sys.exit(1)

        # Wipe existing rows
        conn.execute("DELETE FROM rules")
        print("  Wiped existing rules rows")

        # Build all 54 rows
        rows = build_rows()
        assert len(rows) == 54, f"Expected 54 rows, got {len(rows)}"

        rules_count = sum(1 for r in rows if r[4] == "rule")
        flags_count = sum(1 for r in rows if r[4] == "flag")
        assert rules_count == 24, f"Expected 24 rules, got {rules_count}"
        assert flags_count == 30, f"Expected 30 flags, got {flags_count}"

        # Insert all rows
        conn.executemany("""
            INSERT INTO rules (
                id, client_config, entity_type, name,
                rule_or_flag, type, campaign_type_lock,
                entity_scope, conditions,
                action_type, action_magnitude,
                cooldown_days, risk_level, enabled
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, rows)

        conn.commit()

        print(f"Seeded {len(rows)} rows: {rules_count} rules, {flags_count} flags")
        print()
        print("Breakdown:")
        print(f"  Budget rules (tROAS):      {len(BUDGET_TROAS)}")
        print(f"  Budget rules (tCPA):       {len(BUDGET_TCPA)}")
        print(f"  Budget rules (Max Clicks): {len(BUDGET_MAX_CLICKS)}")
        print(f"  Bid rules (tROAS):         {len(BID_TROAS)}")
        print(f"  Bid rules (tCPA):          {len(BID_TCPA)}")
        print(f"  Bid rules (Max Clicks):    {len(BID_MAX_CLICKS)}")
        print(f"  Status rules:              {len(STATUS_RULES)}")
        print(f"  Performance flags:         {len(PERFORMANCE_FLAGS)}")
        print(f"  Anomaly flags:             {len(ANOMALY_FLAGS)}")
        print(f"  Technical flags:           {len(TECHNICAL_FLAGS)}")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        conn.close()


if __name__ == "__main__":
    main()
