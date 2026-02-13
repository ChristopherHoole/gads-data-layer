"""
Autopilot CLI – Run rule engine against Lighthouse output.

Usage:
    python -m act_autopilot.cli run-v0 configs/client_synthetic.yaml --snapshot-date 2026-02-11
    python -m act_autopilot.cli execute configs/client_synthetic.yaml 2026-02-11
"""
from __future__ import annotations

import argparse
import json
import yaml
from datetime import date, datetime
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
    recs = run_rules(config, lighthouse_report, feature_rows, snapshot_date, args.build_db)
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
        print(f"     Status:     {status}" + (f" – {r.block_reason}" if r.block_reason else ""))
        print(f"     Triggered:  {r.triggering_diagnosis}")
        print(f"     Rationale:  {r.rationale[:120]}...")

    con.close()
    return 0


def cmd_execute(args: argparse.Namespace) -> int:
    """Execute approved budget changes."""
    from .executor import BudgetExecutor
    from .models import Recommendation
    from .google_ads_api import load_google_ads_client
    
    snapshot_date = _parse_date(args.snapshot_date)
    
    # Load client config
    with open(args.config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    client_name = config['client_name']
    
    # Handle nested customer_id structure
    if 'customer_id' in config:
        customer_id = config['customer_id']
    elif 'google_ads' in config and 'customer_id' in config['google_ads']:
        customer_id = config['google_ads']['customer_id']
    else:
        print("Error: customer_id not found in config")
        return 1
    
    print("=" * 80)
    print(f"EXECUTION ENGINE - {client_name}")
    print(f"Date: {args.snapshot_date}")
    print(f"Mode: {'LIVE' if args.live else 'DRY-RUN'}")
    print("=" * 80)
    print()
    
    # Load recommendations from suggest engine output
    suggest_report_path = Path(f"reports/suggestions/{client_name}/{args.snapshot_date}.json")
    
    if not suggest_report_path.exists():
        print(f"Error: Suggestions not found at {suggest_report_path}")
        print("Run suggest engine first: python -m act_autopilot.suggest_engine")
        return 1
    
    with open(suggest_report_path, 'r') as f:
        suggest_data = json.load(f)
    
    # Convert to Recommendation objects
    recommendations = []
    for rec_data in suggest_data['recommendations']:
        rec = Recommendation(
            rule_id=rec_data['rule_id'],
            rule_name=rec_data['rule_name'],
            entity_type=rec_data['entity_type'],
            entity_id=rec_data['entity_id'],
            action_type=rec_data['action_type'],
            risk_tier=rec_data['risk_tier'],
            confidence=rec_data['confidence'],
            current_value=rec_data.get('current_value'),
            recommended_value=rec_data.get('recommended_value'),
            change_pct=rec_data.get('change_pct'),
            rationale=rec_data['rationale'],
            evidence=rec_data['evidence'],
            constitution_refs=rec_data['constitution_refs'],
            guardrails_checked=rec_data['guardrails_checked'],
            triggering_diagnosis=rec_data['triggering_diagnosis'],
            triggering_confidence=rec_data['triggering_confidence'],
            campaign_name=rec_data.get('campaign_name', 'N/A'),
            expected_impact=rec_data['expected_impact'],
            blocked=rec_data['blocked'],
            block_reason=rec_data.get('block_reason'),
            priority=rec_data['priority']
        )
        recommendations.append(rec)
    
    print(f"Loaded {len(recommendations)} recommendations from suggest engine")
    
    # Filter to executable only (not blocked)
    executable = [r for r in recommendations if not r.blocked]
    print(f"  Executable (not blocked): {len(executable)}")
    
    # Filter to budget changes only
    budget_recs = [r for r in executable if r.action_type in ['budget_increase', 'budget_decrease']]
    print(f"  Budget changes: {len(budget_recs)}")
    
    if len(budget_recs) == 0:
        print("\nNo budget changes to execute.")
        return 0
    
    # Parse rule_ids filter
    rule_ids_list = None
    if args.rule_ids:
        rule_ids_list = [r.strip() for r in args.rule_ids.split(',')]
        print(f"  Filtered to rule IDs: {rule_ids_list}")
    
    print()
    
    # Live mode: Confirmation prompt
    google_ads_client = None
    if args.live:
        print("⚠️  LIVE MODE - This will make REAL changes to Google Ads")
        print()
        
        # Show what will be executed
        to_execute = budget_recs
        if rule_ids_list:
            to_execute = [r for r in to_execute if r.rule_id in rule_ids_list]
        
        print(f"About to execute {len(to_execute)} changes:")
        for rec in to_execute:
            print(f"  - {rec.rule_id}: {rec.campaign_name} ({rec.entity_id})")
            print(f"    {rec.current_value / 1_000_000:.2f} → {rec.recommended_value / 1_000_000:.2f} ({rec.change_pct:+.1%})")
        
        print()
        confirm = input("Proceed with live execution? [y/N]: ").strip().lower()
        
        if confirm != 'y':
            print("Execution cancelled.")
            return 0
        
        print()
        print("Loading Google Ads API client...")
        
        try:
            google_ads_client = load_google_ads_client("secrets/google-ads.yaml")
        except Exception as e:
            print(f"Error: Failed to load Google Ads client: {e}")
            return 1
    
    # Execute
    executor = BudgetExecutor(
        customer_id=customer_id,
        db_path=args.db_path,
        google_ads_client=google_ads_client
    )
    
    print("Executing...")
    print()
    
    summary = executor.execute(
        recommendations=budget_recs,
        dry_run=not args.live,
        rule_ids=rule_ids_list
    )
    
    # Print results
    print("=" * 80)
    print("RESULTS")
    print("=" * 80)
    print()
    
    for result in summary['results']:
        if result['success']:
            print(f"✅ {result['rule_id']} - {result['campaign_name']}")
        else:
            print(f"❌ {result['rule_id']} - {result['campaign_name']}")
            print(f"   Error: {result['error']}")
        print()
    
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total: {summary['total']}")
    print(f"Successful: {summary['successful']}")
    print(f"Failed: {summary['failed']}")
    print(f"Mode: {'LIVE' if args.live else 'DRY-RUN'}")
    print()
    
    if not args.live:
        print("This was a DRY-RUN. No changes were made.")
        print("To execute for real, add --live flag")
    
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="act_autopilot", description="Ads Control Tower – Autopilot Rule Engine v0")
    sub = p.add_subparsers(dest="cmd", required=True)

    # run-v0 command
    r = sub.add_parser("run-v0", help="Run rules against Lighthouse output + features")
    r.add_argument("client_config", help="Path to client config YAML")
    r.add_argument("--snapshot-date", required=True, help="YYYY-MM-DD")
    r.add_argument("--build-db", default="warehouse.duckdb", help="Build DuckDB path")
    r.set_defaults(func=cmd_run_v0)

    # execute command
    e = sub.add_parser("execute", help="Execute approved budget changes")
    e.add_argument("config_path", help="Path to client config YAML")
    e.add_argument("snapshot_date", help="Snapshot date (YYYY-MM-DD)")
    e.add_argument("--live", action="store_true", help="Execute changes via API (default: dry-run)")
    e.add_argument("--rule-ids", type=str, default=None, help="Comma-separated rule IDs to execute")
    e.add_argument("--db-path", default="warehouse.duckdb", help="Path to DuckDB database")
    e.set_defaults(func=cmd_execute)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
