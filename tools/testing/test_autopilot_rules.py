"""
Autopilot Rule Test Runner

Validates which rules fire for each of the 8 synthetic scenarios.

Usage:
    python tools/testing/test_autopilot_rules.py
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path
from typing import Any, Dict, List

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import duckdb

from act_autopilot.engine import (
    load_autopilot_config,
    load_lighthouse_report,
    load_feature_rows,
    run_rules,
    generate_autopilot_report,
)
from act_autopilot.models import Recommendation

# ─────────────────────────────────────────────────────────────
# Expected rule outcomes per scenario
# ─────────────────────────────────────────────────────────────
EXPECTED_OUTCOMES = {
    "2001": {
        "name": "STABLE_A",
        "should_fire": ["STATUS-003"],  # healthy — no action
        "should_not_fire": ["BUDGET-003", "BUDGET-005"],  # no spikes, no pacing crisis
    },
    "2002": {
        "name": "STABLE_B",
        "should_fire": ["STATUS-003"],
        "should_not_fire": ["BUDGET-003", "BUDGET-005"],
    },
    "2003": {
        "name": "COST_SPIKE",
        "should_fire": ["BUDGET-003"],  # emergency budget cut
        "should_not_fire": [
            "BUDGET-001",
            "BUDGET-004",
        ],  # not a recovery/increase scenario
    },
    "2004": {
        "name": "COST_DROP",
        "should_fire": ["BUDGET-004"],  # recovery budget increase
        "should_not_fire": ["BUDGET-003"],  # not a spike
    },
    "2005": {
        "name": "CTR_DROP",
        "should_fire": ["BID-003"],  # hold bids — investigate CTR
        "should_not_fire": ["BUDGET-001"],  # no budget increase
    },
    "2006": {
        "name": "CVR_DROP",
        "should_fire": ["BID-003"],  # hold bids — investigate CVR
        "should_not_fire": ["BID-001", "BID-002"],  # no bid target changes
    },
    "2007": {
        "name": "VOLATILE",
        "should_fire": [],  # cost_w14_cv is NULL in synthetic data — BUDGET-006 cannot fire
        "should_not_fire": ["BUDGET-001", "BUDGET-002"],  # no budget changes
    },
    "2008": {
        "name": "LOW_DATA",
        "should_fire": ["BID-004"],  # hold bids — low data
        "should_not_fire": ["BUDGET-001", "BUDGET-002", "BID-001", "BID-002"],
    },
}


def run_tests() -> Dict[str, Any]:
    """Run Autopilot rules against synthetic data and validate expectations."""
    config_path = str(project_root / "configs" / "client_synthetic.yaml")
    snapshot_date = date(2026, 2, 11)

    # Load config
    config = load_autopilot_config(config_path)
    print(f"[Test] Config loaded: {config.client_id}")

    # Load Lighthouse report
    report_path = (
        project_root
        / "reports"
        / "lighthouse"
        / config.client_id
        / f"{snapshot_date.isoformat()}.json"
    )
    if not report_path.exists():
        print(f"[Test] ERROR: Lighthouse report not found: {report_path}")
        print(f"[Test] Run Lighthouse first.")
        return {"passed": 0, "failed": 0, "errors": ["Lighthouse report not found"]}

    lighthouse_report = load_lighthouse_report(str(report_path))
    print(
        f"[Test] Lighthouse report loaded: {len(lighthouse_report.get('insights', []))} insights"
    )

    # Connect to build DB
    build_db = project_root / "warehouse.duckdb"
    if not build_db.exists():
        print(f"[Test] ERROR: warehouse.duckdb not found")
        return {"passed": 0, "failed": 0, "errors": ["warehouse.duckdb not found"]}

    con = duckdb.connect(str(build_db))
    feature_rows = load_feature_rows(
        con, config.client_id, config.customer_id, snapshot_date
    )
    print(f"[Test] Feature rows loaded: {len(feature_rows)}")

    if len(feature_rows) == 0:
        print("[Test] ERROR: No feature rows found")
        con.close()
        return {"passed": 0, "failed": 0, "errors": ["No feature rows"]}

    # Run all rules
    all_recs = run_rules(config, lighthouse_report, feature_rows)
    print(f"[Test] Total recommendations: {len(all_recs)}")

    # Group recommendations by campaign
    recs_by_campaign: Dict[str, List[Recommendation]] = {}
    account_recs: List[Recommendation] = []

    for rec in all_recs:
        if rec.entity_type == "ACCOUNT":
            account_recs.append(rec)
        elif rec.entity_id:
            recs_by_campaign.setdefault(rec.entity_id, []).append(rec)

    # Print all recommendations grouped by campaign
    print(f"\n{'='*70}")
    print("ALL RECOMMENDATIONS BY CAMPAIGN")
    print(f"{'='*70}")

    for cid in sorted(recs_by_campaign.keys()):
        recs = recs_by_campaign[cid]
        feat = next((f for f in feature_rows if str(f.get("campaign_id")) == cid), {})
        name = feat.get("campaign_name", "?")
        print(f"\n  Campaign {cid} ({name}):")
        for r in recs:
            status = "BLOCKED" if r.blocked else "OK"
            print(
                f"    [{r.rule_id}] {r.action_type} | risk={r.risk_tier} | conf={r.confidence:.2f} | {status}"
            )

    if account_recs:
        print(f"\n  ACCOUNT-level:")
        for r in account_recs:
            print(
                f"    [{r.rule_id}] {r.action_type} | risk={r.risk_tier} | conf={r.confidence:.2f}"
            )

    # Validate expectations
    print(f"\n{'='*70}")
    print("VALIDATION RESULTS")
    print(f"{'='*70}")

    passed = 0
    failed = 0
    details: List[Dict] = []

    for campaign_id, expected in EXPECTED_OUTCOMES.items():
        scenario_name = expected["name"]
        campaign_recs = recs_by_campaign.get(campaign_id, [])
        fired_rule_ids = set(r.rule_id for r in campaign_recs)

        # Check should_fire
        for rule_id in expected["should_fire"]:
            if rule_id in fired_rule_ids:
                passed += 1
                status = "PASS"
            else:
                failed += 1
                status = "FAIL"
            detail = {
                "campaign_id": campaign_id,
                "scenario": scenario_name,
                "check": "should_fire",
                "rule_id": rule_id,
                "result": status,
                "fired_rules": sorted(fired_rule_ids),
            }
            details.append(detail)
            icon = "✅" if status == "PASS" else "❌"
            print(
                f"  {icon} Campaign {campaign_id} ({scenario_name}): {rule_id} should fire → {status}"
            )

        # Check should_not_fire
        for rule_id in expected["should_not_fire"]:
            if rule_id not in fired_rule_ids:
                passed += 1
                status = "PASS"
            else:
                failed += 1
                status = "FAIL"
            detail = {
                "campaign_id": campaign_id,
                "scenario": scenario_name,
                "check": "should_not_fire",
                "rule_id": rule_id,
                "result": status,
                "fired_rules": sorted(fired_rule_ids),
            }
            details.append(detail)
            icon = "✅" if status == "PASS" else "❌"
            print(
                f"  {icon} Campaign {campaign_id} ({scenario_name}): {rule_id} should NOT fire → {status}"
            )

    total = passed + failed
    pct = (passed / total * 100) if total > 0 else 0

    print(f"\n{'='*70}")
    print(f"SUMMARY: {passed}/{total} checks passed ({pct:.0f}%)")
    print(f"{'='*70}")

    # Save report
    report = generate_autopilot_report(
        config, all_recs, snapshot_date, str(report_path)
    )
    out_dir = project_root / "reports" / "autopilot" / config.client_id
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{snapshot_date.isoformat()}.json"
    out_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False, default=str), encoding="utf-8"
    )
    print(f"\n[Test] Autopilot report saved: {out_path}")

    # Save test results
    test_report = {
        "snapshot_date": snapshot_date.isoformat(),
        "total_checks": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": round(pct, 1),
        "details": details,
    }
    test_path = out_dir / f"test_results_{snapshot_date.isoformat()}.json"
    test_path.write_text(
        json.dumps(test_report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"[Test] Test results saved: {test_path}")

    con.close()
    return test_report


if __name__ == "__main__":
    results = run_tests()
    sys.exit(0 if results.get("failed", 1) == 0 else 1)
