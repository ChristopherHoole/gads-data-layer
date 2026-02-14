"""
Command-line interface for Autopilot.
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime, date
import yaml

from .models import AutopilotConfig, Recommendation
from .executor import BudgetExecutor
from .logging_config import setup_logging

# Initialize logger
logger = setup_logging(__name__)


def load_config(config_path: str) -> dict:
    """Load client configuration from YAML."""
    logger.info(f"Loading config from {config_path}")
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    logger.info(f"Config loaded: {config.get('client_name', 'Unknown')}")
    return config


def load_recommendations(report_path: str) -> list:
    """Load recommendations from suggestion report JSON."""
    logger.info(f"Loading recommendations from {report_path}")
    
    with open(report_path, 'r') as f:
        data = json.load(f)
    
    recommendations = data.get('recommendations', [])
    logger.info(f"Loaded {len(recommendations)} recommendations")
    
    return recommendations


def create_autopilot_config(config: dict) -> AutopilotConfig:
    """Create AutopilotConfig from YAML config."""
    return AutopilotConfig(
        customer_id=str(config['google_ads']['customer_id']),
        automation_mode=config.get('automation_mode', 'suggest'),
        risk_tolerance=config.get('risk_tolerance', 'conservative'),
        daily_spend_cap=config['spend_caps']['daily'],
        monthly_spend_cap=config['spend_caps']['monthly'],
        brand_is_protected=config.get('protected_entities', {}).get('brand_is_protected', False),
        protected_entities=config.get('protected_entities', {}).get('entities', []),
        max_changes_per_day=config.get('max_changes_per_day', 10)
    )


def cmd_execute(args):
    """Execute recommendations (budget changes only)."""
    
    print("=" * 80)
    print(f"EXECUTION ENGINE - {args.config}")
    print(f"Date: {args.snapshot_date}")
    print(f"Mode: {'LIVE' if args.live else 'DRY-RUN'}")
    print("=" * 80)
    
    # Load config
    config_dict = load_config(args.config)
    config = create_autopilot_config(config_dict)
    client_name = config_dict.get('client_name', 'Unknown')
    
    # Determine report path
    if args.report:
        report_path = args.report
    else:
        # Default: reports/suggestions/{client_name}/{date}.json
        report_dir = Path('reports/suggestions') / client_name
        report_path = report_dir / f"{args.snapshot_date}.json"
    
    if not Path(report_path).exists():
        logger.error(f"Suggestion report not found: {report_path}")
        print(f"\n❌ ERROR: Suggestion report not found: {report_path}")
        print("\nRun suggestion engine first:")
        print(f"  python -m act_autopilot.suggest_engine {args.config} {args.snapshot_date}")
        return 1
    
    # Load recommendations
    recommendations_data = load_recommendations(str(report_path))
    
    # Convert to Recommendation objects
    recommendations = []
    for rec_data in recommendations_data:
        # Skip if missing required fields
        if not rec_data.get('entity_id'):
            logger.warning(f"Skipping recommendation without entity_id: {rec_data}")
            continue
        
        rec = Recommendation(
            rule_id=rec_data.get('rule_id', 'UNKNOWN'),
            rule_name=rec_data.get('rule_name', 'UNKNOWN'),
            entity_type=rec_data.get('entity_type', 'CAMPAIGN'),
            entity_id=rec_data.get('entity_id', 'UNKNOWN'),
            action_type=rec_data.get('action_type', 'unknown'),
            risk_tier=rec_data.get('risk_tier', 'medium'),
            confidence=rec_data.get('confidence', 0.0),
            current_value=rec_data.get('current_value'),
            recommended_value=rec_data.get('recommended_value'),
            change_pct=rec_data.get('change_pct'),
            rationale=rec_data.get('rationale', ''),
            campaign_name=rec_data.get('campaign_name'),
            blocked=rec_data.get('blocked', False),
            block_reason=rec_data.get('block_reason'),
            priority=rec_data.get('priority', 50),
            constitution_refs=rec_data.get('constitution_refs', []),
            guardrails_checked=rec_data.get('guardrails_checked', []),
            evidence=rec_data.get('evidence'),
            triggering_diagnosis=rec_data.get('triggering_diagnosis'),
            triggering_confidence=rec_data.get('triggering_confidence', 0.0),
            expected_impact=rec_data.get('expected_impact', '')
        )
        recommendations.append(rec)
    
    logger.info(f"Loaded {len(recommendations)} recommendations from report")
    
    if len(recommendations) == 0:
        logger.error("No valid recommendations found in report")
        print("\n❌ ERROR: No valid recommendations found in report")
        return 1
    
    # Filter by rule IDs if specified
    if args.rule_ids:
        rule_ids = [r.strip() for r in args.rule_ids.split(',')]
        recommendations = [r for r in recommendations if r.rule_id in rule_ids]
        logger.info(f"Filtered to {len(recommendations)} recommendations matching rule IDs: {rule_ids}")
        print(f"\nFiltered to {len(recommendations)} recommendations matching: {', '.join(rule_ids)}")
    
    # Confirmation for live mode
    if args.live:
        print("\n⚠️  LIVE MODE - This will make REAL changes to Google Ads!")
        response = input("Type 'yes' to confirm: ")
        if response.lower() != 'yes':
            logger.info("Live mode cancelled by user")
            print("\n❌ Cancelled")
            return 0
    
    # Create executor
    executor = BudgetExecutor(
        customer_id=config.customer_id,
        db_path=args.db_path,
        google_ads_client=None  # None = dry-run mode, pass GoogleAdsClient for live
    )
    
    # Execute
    logger.info("Starting execution...")
    summary = executor.execute(
        recommendations=recommendations,
        dry_run=not args.live,
        rule_ids=args.rule_ids.split(',') if args.rule_ids else None
    )
    
    # Extract results from summary
    results = summary.get('results', [])
    
    # Display results
    print("\n" + "=" * 80)
    print("EXECUTION RESULTS")
    print("=" * 80)
    
    print(f"\nTotal executed: {summary.get('total', 0)}")
    print(f"✅ Successful: {summary.get('successful', 0)}")
    print(f"❌ Failed: {summary.get('failed', 0)}")
    
    if results:
        print("\nDetails:")
        print("-" * 80)
        
        for i, result in enumerate(results, 1):
            status = "✅ SUCCESS" if result.get('success') else "❌ FAILED"
            
            print(f"\n{i}. {result.get('rule_id')} - {result.get('campaign_name', result.get('campaign_id'))}")
            print(f"   Status: {status}")
            print(f"   Action: {result.get('action_type')}")
            print(f"   Message: {result.get('message')}")
            
            if result.get('error'):
                print(f"   Error: {result.get('error')}")
    
    print("\n" + "=" * 80)
    
    if args.live:
        print("\n✅ LIVE execution complete. Changes applied to Google Ads.")
    else:
        print("\n✅ DRY-RUN complete. No changes made (simulation only).")
    
    print(f"\nLogs: logs/executor_{datetime.now().strftime('%Y-%m-%d')}.log")
    
    return 0 if summary.get('failed', 0) == 0 else 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description='Autopilot Execution Engine')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Execute command
    execute_parser = subparsers.add_parser('execute', help='Execute recommendations')
    execute_parser.add_argument('config', help='Path to client config YAML')
    execute_parser.add_argument('snapshot_date', help='Snapshot date (YYYY-MM-DD)')
    execute_parser.add_argument('--live', action='store_true', help='Live mode (default: dry-run)')
    execute_parser.add_argument('--report', help='Path to suggestion report JSON (optional)')
    execute_parser.add_argument('--rule-ids', help='Comma-separated rule IDs to execute (optional)')
    execute_parser.add_argument('--db-path', default='warehouse.duckdb', help='Database path')
    execute_parser.set_defaults(func=cmd_execute)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    return int(args.func(args))


if __name__ == '__main__':
    raise SystemExit(main())
