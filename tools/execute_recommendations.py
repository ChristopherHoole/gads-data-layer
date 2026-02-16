"""
CLI Execution Tool for Recommendations
Manual interface for executing Google Ads recommendations.

Usage:
    python tools/execute_recommendations.py --help
    python tools/execute_recommendations.py --client client_001 --dry-run
    python tools/execute_recommendations.py --client client_001 --risk-tier LOW --live
    python tools/execute_recommendations.py --client client_001 --action-type update_budget --dry-run
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime
import json

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from act_autopilot.executor import Executor
from act_autopilot.models import Recommendation
import yaml


def print_header(title):
    """Print section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_recommendation_summary(recommendations):
    """Print summary of recommendations"""
    if not recommendations:
        print("\nNo recommendations found.")
        return

    print(f"\nTotal Recommendations: {len(recommendations)}")

    # Group by action type
    by_action = {}
    for rec in recommendations:
        action = rec.action_type
        if action not in by_action:
            by_action[action] = []
        by_action[action].append(rec)

    print("\nBy Action Type:")
    for action, recs in sorted(by_action.items()):
        print(f"  {action}: {len(recs)}")

    # Group by risk tier
    by_risk = {}
    for rec in recommendations:
        risk = rec.risk_tier
        if risk not in by_risk:
            by_risk[risk] = []
        by_risk[risk].append(rec)

    print("\nBy Risk Tier:")
    for risk, recs in sorted(by_risk.items()):
        print(f"  {risk}: {len(recs)}")


def print_recommendation_details(recommendations, max_display=10):
    """Print detailed view of recommendations"""
    print("\nRecommendation Details:")
    print("-" * 80)

    for i, rec in enumerate(recommendations[:max_display]):
        print(f"\n{i+1}. {rec.rule_id} - {rec.rule_name}")
        print(f"   Entity: {rec.campaign_name or 'Unknown'} ({rec.entity_id})")
        print(f"   Action: {rec.action_type}")
        print(f"   Risk: {rec.risk_tier} | Confidence: {rec.confidence:.1%}")

        if rec.current_value is not None and rec.recommended_value is not None:
            print(
                f"   Change: {rec.current_value:.2f} → {rec.recommended_value:.2f}"
            )
            if rec.change_pct:
                print(f"   Change %: {rec.change_pct * 100:+.1f}%")

        print(f"   Rationale: {rec.rationale}")

        if rec.blocked:
            print(f"   ⚠️  BLOCKED: {rec.block_reason}")

    if len(recommendations) > max_display:
        print(f"\n... and {len(recommendations) - max_display} more recommendations")


def filter_recommendations(recommendations, args):
    """Filter recommendations based on CLI arguments"""
    filtered = recommendations

    # Filter by risk tier
    if args.risk_tier:
        filtered = [r for r in filtered if r.risk_tier == args.risk_tier.upper()]

    # Filter by action type
    if args.action_type:
        filtered = [r for r in filtered if r.action_type == args.action_type]

    # Filter by campaign (partial match)
    if args.campaign:
        filtered = [
            r
            for r in filtered
            if r.campaign_name
            and args.campaign.lower() in r.campaign_name.lower()
        ]

    # Exclude blocked recommendations unless explicitly requested
    if not args.include_blocked:
        filtered = [r for r in filtered if not r.blocked]

    return filtered


def confirm_execution(recommendations, dry_run):
    """Ask user to confirm execution"""
    mode = "DRY-RUN" if dry_run else "LIVE"
    print(f"\n⚠️  About to execute {len(recommendations)} recommendations in {mode} mode")

    if not dry_run:
        print("⚠️  WARNING: This will make LIVE changes to your Google Ads account!")

    response = input("\nProceed? (yes/no): ").strip().lower()
    return response in ["yes", "y"]


def save_execution_log(results, args, output_file=None):
    """Save execution results to log file"""
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"execution_log_{timestamp}.json"

    log_data = {
        "timestamp": datetime.now().isoformat(),
        "client_id": args.client,
        "mode": "dry_run" if args.dry_run else "live",
        "filters": {
            "risk_tier": args.risk_tier,
            "action_type": args.action_type,
            "campaign": args.campaign,
        },
        "summary": {
            "total": results["total"],
            "successful": results["successful"],
            "failed": results["failed"],
        },
        "results": results["results"],
    }

    output_path = Path(output_file)
    with open(output_path, "w") as f:
        json.dump(log_data, f, indent=2)

    print(f"\n✓ Execution log saved to: {output_path}")


def generate_test_recommendations(customer_id):
    """
    Generate test recommendations for demonstration.
    
    In production, this would be replaced with:
        autopilot = Autopilot(customer_id=customer_id, config=config, db_path="warehouse.duckdb")
        recommendations = autopilot.generate_recommendations()
    """
    recommendations = [
        # Budget changes
        Recommendation(
            rule_id="BUD-001",
            rule_name="Increase High-Performing Campaign Budget",
            entity_type="campaign",
            entity_id="12345",
            action_type="update_budget",
            risk_tier="LOW",
            campaign_name="Brand Search Campaign",
            current_value=50.0,
            recommended_value=60.0,
            change_pct=0.20,
            confidence=0.95,
            rationale="Campaign ROAS 12.5 exceeds target 8.0, increase budget 20%",
        ),
        Recommendation(
            rule_id="BUD-002",
            rule_name="Decrease Underperforming Campaign Budget",
            entity_type="campaign",
            entity_id="67890",
            action_type="update_budget",
            risk_tier="MEDIUM",
            campaign_name="Generic Search Campaign",
            current_value=100.0,
            recommended_value=80.0,
            change_pct=-0.20,
            confidence=0.85,
            rationale="Campaign ROAS 3.2 below target 5.0, decrease budget 20%",
        ),
        # Keyword changes
        Recommendation(
            rule_id="KW-PAUSE-001",
            rule_name="Pause High CPA Keyword",
            entity_type="keyword",
            entity_id="111222333",
            action_type="pause_keyword",
            risk_tier="LOW",
            campaign_name="Brand Search Campaign",
            current_value=85.50,
            recommended_value=0,
            change_pct=-1.0,
            confidence=0.90,
            rationale="CPA £85.50 exceeds target £50.00 by 71%",
            evidence={
                "ad_group_id": 12345,
                "campaign_id": 12345,
                "keyword_text": "expensive keyword",
                "cpa": 85.50,
                "target_cpa": 50.00,
                "clicks_30d": 45,
                "conversions_30d": 2,
            },
        ),
        # Ad changes
        Recommendation(
            rule_id="AD-PAUSE-001",
            rule_name="Pause Low CTR Ad",
            entity_type="ad",
            entity_id="444555666",
            action_type="pause_ad",
            risk_tier="LOW",
            campaign_name="Brand Search Campaign",
            current_value=1.5,
            recommended_value=0,
            change_pct=-1.0,
            confidence=0.88,
            rationale="Ad CTR 1.5% significantly below ad group average 3.2%",
            evidence={
                "ad_group_id": 12345,
                "campaign_id": 12345,
                "ctr": 0.015,
                "ad_group_ctr": 0.032,
                "impressions_30d": 5000,
                "clicks_30d": 75,
                "active_ads_count": 5,
            },
        ),
        # Shopping changes
        Recommendation(
            rule_id="SHOP-BID-001",
            rule_name="Increase High ROAS Product Bid",
            entity_type="product",
            entity_id="777888999",
            action_type="update_product_bid",
            risk_tier="LOW",
            campaign_name="Shopping Campaign",
            current_value=2.00,
            recommended_value=2.30,
            change_pct=0.15,
            confidence=0.92,
            rationale="Product ROAS 8.5 exceeds target 5.0, increase bid 15%",
            evidence={
                "ad_group_id": 99999,
                "campaign_id": 99999,
                "product_id": "PROD-123",
                "current_bid_micros": 2000000,
                "new_bid_micros": 2300000,
                "roas": 8.5,
                "target_roas": 5.0,
                "out_of_stock": False,
                "feed_quality_issue": False,
            },
        ),
        # High risk example
        Recommendation(
            rule_id="BUD-003",
            rule_name="Large Budget Increase",
            entity_type="campaign",
            entity_id="99999",
            action_type="update_budget",
            risk_tier="HIGH",
            campaign_name="Shopping Campaign",
            current_value=200.0,
            recommended_value=300.0,
            change_pct=0.50,
            confidence=0.75,
            rationale="Strong performance but large change",
        ),
    ]
    
    return recommendations


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description="Execute Google Ads recommendations via CLI"
    )

    # Required arguments
    parser.add_argument(
        "--client", required=True, help="Client ID (e.g., client_001)"
    )

    # Execution mode
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        "--dry-run", action="store_true", help="Dry-run mode (simulate only)"
    )
    mode_group.add_argument(
        "--live", action="store_true", help="Live mode (make actual changes)"
    )

    # Filters
    parser.add_argument(
        "--risk-tier",
        choices=["LOW", "MEDIUM", "HIGH"],
        help="Filter by risk tier",
    )
    parser.add_argument(
        "--action-type",
        help="Filter by action type (e.g., update_budget, pause_keyword)",
    )
    parser.add_argument("--campaign", help="Filter by campaign name (partial match)")
    parser.add_argument(
        "--include-blocked",
        action="store_true",
        help="Include blocked recommendations",
    )

    # Output options
    parser.add_argument(
        "--no-confirm", action="store_true", help="Skip confirmation prompt"
    )
    parser.add_argument("--save-log", help="Save execution log to file")
    parser.add_argument(
        "--max-display", type=int, default=10, help="Max recommendations to display"
    )

    args = parser.parse_args()

    # Determine mode
    dry_run = args.dry_run

    print_header("ADS CONTROL TOWER - CLI Execution Tool")
    print(f"Client: {args.client}")
    print(f"Mode: {'DRY-RUN' if dry_run else 'LIVE'}")

    # Load client configuration
    try:
        config_path = Path(f"configs/{args.client}.yaml")
        if not config_path.exists():
            print(f"\n✗ Error: Config file not found: {config_path}")
            sys.exit(1)

        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f)
        
        customer_id = config_data.get("customer_id")
        if not customer_id:
            print(f"\n✗ Error: customer_id not found in config")
            sys.exit(1)
            
        print(f"Config loaded: {config_path}")
        print(f"Customer ID: {customer_id}")
    except Exception as e:
        print(f"\n✗ Error loading config: {e}")
        sys.exit(1)

    # Generate test recommendations (in production, load from Autopilot)
    print_header("Generating Test Recommendations")
    print("NOTE: Using test recommendations for demonstration")
    
    try:
        all_recommendations = generate_test_recommendations(customer_id)
        print(f"✓ Generated {len(all_recommendations)} test recommendations")

    except Exception as e:
        print(f"\n✗ Error generating recommendations: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

    # Filter recommendations
    print_header("Filtering Recommendations")
    filtered_recs = filter_recommendations(all_recommendations, args)

    if args.risk_tier:
        print(f"Risk Tier: {args.risk_tier}")
    if args.action_type:
        print(f"Action Type: {args.action_type}")
    if args.campaign:
        print(f"Campaign: {args.campaign}")

    print(f"\nFiltered: {len(filtered_recs)} recommendations")

    if not filtered_recs:
        print("\n✗ No recommendations match filters. Exiting.")
        sys.exit(0)

    # Display summary
    print_recommendation_summary(filtered_recs)

    # Display details
    print_recommendation_details(filtered_recs, max_display=args.max_display)

    # Confirm execution
    if not args.no_confirm:
        if not confirm_execution(filtered_recs, dry_run):
            print("\n✗ Execution cancelled by user.")
            sys.exit(0)

    # Execute recommendations
    print_header(f"Executing {len(filtered_recs)} Recommendations")
    print(f"Mode: {'DRY-RUN' if dry_run else 'LIVE'}")

    try:
        executor = Executor(
            customer_id=customer_id, db_path="warehouse.duckdb"
        )

        results = executor.execute(filtered_recs, dry_run=dry_run)

        # Print results
        print("\n" + "-" * 80)
        print(f"Total: {results['total']}")
        print(f"Successful: {results['successful']}")
        print(f"Failed: {results['failed']}")

        # Show any failures
        if results["failed"] > 0:
            print("\n⚠️  Failed Recommendations:")
            for result in results["results"]:
                if not result["success"]:
                    print(f"\n  {result['rule_id']} ({result['entity_id']})")
                    print(f"  Error: {result['error']}")

        # Save log if requested
        if args.save_log or not dry_run:
            output_file = args.save_log if args.save_log else None
            save_execution_log(results, args, output_file)

        # Success summary
        print_header("Execution Complete")
        if results["successful"] == results["total"]:
            print(f"✓ All {results['total']} recommendations executed successfully!")
        else:
            print(
                f"⚠️  {results['successful']}/{results['total']} recommendations executed successfully"
            )

        return 0

    except Exception as e:
        print(f"\n✗ Execution failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    sys.exit(main())
