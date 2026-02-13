"""
Radar Module: Command-Line Interface
Monitor changes and execute rollbacks.

Usage:
    python -m act_radar.cli check <config>
    python -m act_radar.cli rollback <config> [--dry-run|--live]
"""

import argparse
import yaml
import sys
from pathlib import Path
from datetime import datetime

from .monitor import ChangeMonitor, format_change_summary
from .triggers import should_rollback, format_rollback_decision
from .rollback_executor import RollbackExecutor
from .alerts import send_rollback_alert, send_monitoring_summary, generate_rollback_report


def load_config(config_path: str) -> dict:
    """Load client configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def cmd_check(args):
    """
    Check which changes are being monitored.
    
    Shows status of all changes in monitoring window.
    """
    config = load_config(args.config)
    customer_id = config['customer_id']
    
    print("\n" + "=" * 80)
    print("RADAR MONITORING CHECK")
    print("=" * 80)
    print(f"\nClient: {config['client_name']}")
    print(f"Customer ID: {customer_id}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Initialize monitor
    monitor = ChangeMonitor(db_path=args.db_path)
    
    # Get all changes to monitor
    changes = monitor.monitor_all_changes(customer_id)
    
    if not changes:
        print("\n✅ No changes currently in monitoring window")
        print("\n" + "=" * 80)
        return
    
    print(f"\n📊 CHANGES IN MONITORING WINDOW: {len(changes)}")
    
    # Analyze each change
    rollback_decisions = []
    changes_needing_rollback = []
    changes_confirmed_good = []
    changes_insufficient_data = []
    
    for change in changes:
        decision = should_rollback(change, config, db_path=args.db_path)
        rollback_decisions.append(decision)
        
        if decision.should_rollback:
            changes_needing_rollback.append((change, decision))
        elif decision.trigger == 'INSUFFICIENT_DATA':
            changes_insufficient_data.append((change, decision))
        elif decision.trigger == 'NONE':
            changes_confirmed_good.append((change, decision))
    
    # Print summary
    print("\n" + "-" * 80)
    print("SUMMARY:")
    print(f"  🚨 Rollback needed: {len(changes_needing_rollback)}")
    print(f"  ✅ Confirmed good: {len(changes_confirmed_good)}")
    print(f"  ⏳ Insufficient data: {len(changes_insufficient_data)}")
    
    # Show changes needing rollback (detailed)
    if changes_needing_rollback:
        print("\n" + "-" * 80)
        print("🚨 CHANGES NEEDING ROLLBACK:")
        print("-" * 80)
        
        for i, (change, decision) in enumerate(changes_needing_rollback, 1):
            print(f"\n[{i}] {format_change_summary(change)}")
            print("\n" + format_rollback_decision(decision))
    
    # Show confirmed good changes (summary only)
    if changes_confirmed_good:
        print("\n" + "-" * 80)
        print("✅ CONFIRMED GOOD CHANGES:")
        print("-" * 80)
        
        for change, decision in changes_confirmed_good:
            print(f"  • Campaign {change.campaign_name} ({change.campaign_id})")
            print(f"    Change {change.change_id}: {change.lever} {change.change_pct:+.1%}")
            if change.delta:
                print(f"    CPA: {change.delta['cpa_change_pct']:+.1%}, ROAS: {change.delta['roas_change_pct']:+.1%}, Conv: {change.delta['conversions_change_pct']:+.1%}")
    
    # Show insufficient data changes (summary only)
    if changes_insufficient_data:
        print("\n" + "-" * 80)
        print("⏳ INSUFFICIENT DATA:")
        print("-" * 80)
        
        for change, decision in changes_insufficient_data:
            print(f"  • Campaign {change.campaign_name} ({change.campaign_id})")
            print(f"    Change {change.change_id}: {change.lever} {change.change_pct:+.1%} on {change.change_date}")
            print(f"    Reason: {decision.reason}")
    
    # Next steps
    print("\n" + "-" * 80)
    print("NEXT STEPS:")
    if changes_needing_rollback:
        print(f"  🚨 {len(changes_needing_rollback)} change(s) need rollback")
        print(f"  Dry-run: python -m act_radar.cli rollback {args.config} --dry-run")
        print(f"  Live: python -m act_radar.cli rollback {args.config} --live")
    else:
        print("  ✅ No action needed - all changes performing within thresholds")
    
    print("\n" + "=" * 80)
    
    # Send monitoring summary alert
    send_monitoring_summary(changes, rollback_decisions, config)


def cmd_rollback(args):
    """
    Execute rollbacks for changes that have performance regressions.
    
    Dry-run mode (default): Simulates rollbacks, no actual changes
    Live mode (--live): Executes real Google Ads API changes
    """
    config = load_config(args.config)
    customer_id = config['customer_id']
    dry_run = not args.live
    
    print("\n" + "=" * 80)
    print(f"RADAR ROLLBACK {'[DRY-RUN]' if dry_run else '[LIVE MODE]'}")
    print("=" * 80)
    print(f"\nClient: {config['client_name']}")
    print(f"Customer ID: {customer_id}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if dry_run:
        print("\n⚠️  DRY-RUN MODE: No actual changes will be made")
    else:
        print("\n🚨 LIVE MODE: Real Google Ads changes will be executed")
        response = input("\n   Type 'CONFIRM' to proceed: ")
        if response != 'CONFIRM':
            print("\n   Aborted.")
            return
    
    # Initialize components
    monitor = ChangeMonitor(db_path=args.db_path)
    executor = RollbackExecutor(db_path=args.db_path)
    
    # Get all changes to monitor
    changes = monitor.monitor_all_changes(customer_id)
    
    if not changes:
        print("\n✅ No changes in monitoring window")
        print("\n" + "=" * 80)
        return
    
    # Analyze each change
    changes_to_rollback = []
    decisions = []
    
    for change in changes:
        decision = should_rollback(change, config, db_path=args.db_path)
        
        if decision.should_rollback:
            # Plan rollback
            change_dict = executor.plan_rollback(change.change_id)
            if change_dict:
                # Add campaign_name if not in dict
                if 'campaign_name' not in change_dict:
                    change_dict['campaign_name'] = change.campaign_name
                changes_to_rollback.append((change, change_dict, decision))
                decisions.append(decision)
    
    if not changes_to_rollback:
        print("\n✅ No changes need rollback - all performing within thresholds")
        print("\n" + "=" * 80)
        return
    
    print(f"\n🚨 FOUND {len(changes_to_rollback)} CHANGE(S) NEEDING ROLLBACK:")
    
    # Execute rollbacks
    results = []
    rollback_events = []
    
    for change, change_dict, decision in changes_to_rollback:
        print("\n" + "-" * 80)
        
        # Execute rollback
        result = executor.execute_rollback(
            change=change_dict,
            reason=decision.reason,
            dry_run=dry_run
        )
        
        results.append(result)
        
        # Log to database if successful and not dry-run
        if result.success and not dry_run:
            executor.log_rollback(result, decision.reason, change_dict)
        
        # Send alert
        send_rollback_alert(change_dict, decision, result, config)
        
        # Collect for report
        rollback_events.append({
            'change_id': change.change_id,
            'campaign_id': change.campaign_id,
            'campaign_name': change.campaign_name,
            'lever': change.lever,
            'trigger': decision.trigger,
            'reason': decision.reason,
            'confidence': decision.confidence,
            'success': result.success,
            'dry_run': dry_run,
            'evidence': decision.evidence,
        })
    
    # Summary
    print("\n" + "=" * 80)
    print("ROLLBACK SUMMARY:")
    print("=" * 80)
    
    successful = sum(1 for r in results if r.success)
    failed = len(results) - successful
    
    print(f"\n  Total rollbacks attempted: {len(results)}")
    print(f"  ✅ Successful: {successful}")
    print(f"  ❌ Failed: {failed}")
    
    if dry_run:
        print(f"\n  Mode: DRY-RUN (no actual changes made)")
        print(f"  To execute for real, run with --live flag")
    else:
        print(f"\n  Mode: LIVE (changes executed in Google Ads)")
    
    # Save report
    report_dir = Path(f"reports/radar/{config['client_name']}")
    report_dir.mkdir(parents=True, exist_ok=True)
    
    report_path = report_dir / f"{datetime.now().strftime('%Y-%m-%d_%H%M%S')}_rollbacks.json"
    generate_rollback_report(rollback_events, config, str(report_path))
    
    print(f"\n  📄 Report saved: {report_path}")
    
    print("\n" + "=" * 80)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Radar: Monitor changes and execute rollbacks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check monitoring status
  python -m act_radar.cli check configs/client_synthetic.yaml
  
  # Dry-run rollbacks (simulate only)
  python -m act_radar.cli rollback configs/client_synthetic.yaml --dry-run
  
  # Execute rollbacks (live mode)
  python -m act_radar.cli rollback configs/client_synthetic.yaml --live
        """
    )
    
    parser.add_argument(
        '--db-path',
        default='warehouse.duckdb',
        help='Path to DuckDB database (default: warehouse.duckdb)'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Check command
    parser_check = subparsers.add_parser(
        'check',
        help='Check which changes are being monitored'
    )
    parser_check.add_argument(
        'config',
        help='Path to client config YAML file'
    )
    parser_check.set_defaults(func=cmd_check)
    
    # Rollback command
    parser_rollback = subparsers.add_parser(
        'rollback',
        help='Execute rollbacks for regressed changes'
    )
    parser_rollback.add_argument(
        'config',
        help='Path to client config YAML file'
    )
    parser_rollback.add_argument(
        '--dry-run',
        action='store_true',
        default=True,
        help='Simulate rollbacks without making changes (default)'
    )
    parser_rollback.add_argument(
        '--live',
        action='store_true',
        help='Execute real rollbacks via Google Ads API'
    )
    parser_rollback.set_defaults(func=cmd_rollback)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == '__main__':
    main()
