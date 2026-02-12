"""
Autopilot CLI — Run rule engine against Lighthouse output.

Usage:
    python -m act_autopilot.cli run-v0 configs/client_synthetic.yaml --snapshot-date 2026-02-11
"""
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from .engine import (
    load_autopilot_config,
    load_lighthouse_report,
    load_feature_rows,
    run_rules,
    generate_autopilot_report,
)

import duckdb


def _parse_date(s: str) -> date:
    parts = s.split("-")
    if len(parts) != 3:
        raise ValueError("snapshot_date must be YYYY-MM-DD")
    return date(int(parts[0]), int(parts[1]), int(parts[2]))


def cmd_run_v0(args: argparse.Namespace) -> int:
    config = load_autopilot_config(args.client_config)
    snapshot_date = _parse_date(args.snapshot_date)

    # Locate Lighthouse report
    report_dir = Path("reports") / "lighthouse" / config.client_id
    report_path = report_dir / f"{snapshot_date.isoformat()}.json"
    if not report_path.exists():
        print(f"[Autopilot] ERROR: Lighthouse report not found: {report_path}")
        print(f"[Autopilot] Run Lighthouse first: python -m act_lighthouse.cli run-v0 {args.client_config} --snapshot-date {snapshot_date.isoformat()}")
        return 1

    lighthouse_report = load_lighthouse_report(str(report_path))
    print(f"[Autopilot] Loaded Lighthouse report: {report_path}")
    print(f"[Autopilot]   insights: {len(lighthouse_report.get('insights', []))}")

    # Connect to build DB (features are there)
    build_db = Path(args.build_db)
    if not build_db.exists():
        print(f"[Autopilot] ERROR: Build DB not found: {build_db}")
        return 1

    con = duckdb.connect(str(build_db))

    # Load feature rows
    feature_rows = load_feature_rows(con, config.client_id, config.customer_id, snapshot_date)
    print(f"[Autopilot] Loaded {len(feature_rows)} feature rows for {snapshot_date.isoformat()}")

    if len(feature_rows) == 0:
        print("[Autopilot] ERROR: No feature rows found. Run Lighthouse first.")
        con.close()
        return 1

    # Run rules
    recs = run_rules(config, lighthouse_report, feature_rows)
    print(f"[Autopilot] Generated {len(recs)} recommendations")

    # Summary
    blocked = sum(1 for r in recs if r.blocked)
    actionable = sum(1 for r in recs if not r.blocked and r.action_type not in ("no_action", "review", "budget_hold", "bid_hold"))
    holds = sum(1 for r in recs if r.action_type in ("budget_hold", "bid_hold", "no_action"))
    reviews = sum(1 for r in recs if r.action_type == "review")

    print(f"[Autopilot]   actionable: {actionable}")
    print(f"[Autopilot]   blocked:    {blocked}")
    print(f"[Autopilot]   holds:      {holds}")
    print(f"[Autopilot]   reviews:    {reviews}")

    # Generate report
    report = generate_autopilot_report(config, recs, snapshot_date, str(report_path))

    out_dir = Path("reports") / "autopilot" / config.client_id
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{snapshot_date.isoformat()}.json"
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    print(f"[Autopilot] Report saved: {out_path}")

    # Print top recommendations
    print(f"\n{'='*70}")
    print(f"TOP RECOMMENDATIONS (priority order)")
    print(f"{'='*70}")
    for i, r in enumerate(recs[:10], 1):
        status = "BLOCKED" if r.blocked else "OK"
        print(f"\n  #{i} [{r.rule_id}] {r.rule_name}")
        print(f"     Entity:     {r.entity_type} {r.entity_id or '(account)'}")
        print(f"     Action:     {r.action_type} | Risk: {r.risk_tier} | Confidence: {r.confidence:.2f}")
        if r.change_pct is not None and r.change_pct != 0:
            print(f"     Change:     {r.change_pct:+.0%}")
        print(f"     Status:     {status}" + (f" — {r.block_reason}" if r.block_reason else ""))
        print(f"     Triggered:  {r.triggering_diagnosis}")
        print(f"     Rationale:  {r.rationale[:120]}...")

    con.close()
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="act_autopilot", description="Ads Control Tower — Autopilot Rule Engine v0")
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("run-v0", help="Run rules against Lighthouse output + features")
    r.add_argument("client_config", help="Path to client config YAML")
    r.add_argument("--snapshot-date", required=True, help="YYYY-MM-DD")
    r.add_argument("--build-db", default="warehouse.duckdb", help="Build DuckDB path")
    r.set_defaults(func=cmd_run_v0)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
