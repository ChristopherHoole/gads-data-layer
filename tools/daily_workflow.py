"""
Daily Workflow - Automated pipeline from data to recommendations

Runs:
1. Lighthouse analysis (features + insights)
2. Autopilot suggestion engine (recommendations)
3. Report generation
"""

import sys
import subprocess
from datetime import date, datetime
from pathlib import Path


def run_daily_workflow(config_path: str, snapshot_date: date):
    """Run complete daily workflow"""

    print(f"\n{'='*80}")
    print(f"DAILY WORKFLOW - {snapshot_date}")
    print(f"{'='*80}\n")

    # Step 1: Lighthouse Analysis
    print("Step 1/2: Running Lighthouse analysis...")
    print("-" * 80)

    lighthouse_cmd = [
        sys.executable,
        "-m",
        "act_lighthouse.cli",
        "run-v0",
        config_path,
        "--snapshot-date",
        str(snapshot_date),
    ]

    result = subprocess.run(lighthouse_cmd, capture_output=False)

    if result.returncode != 0:
        print(f"❌ Lighthouse failed with exit code {result.returncode}")
        return False

    print("✅ Lighthouse complete\n")

    # Step 2: Autopilot Suggestions
    print("Step 2/2: Generating recommendations...")
    print("-" * 80)

    from act_autopilot.suggest_engine import SuggestEngine

    try:
        engine = SuggestEngine()
        report = engine.generate_suggestions(config_path, snapshot_date)
        output_path = engine.save_report(report)
        print("✅ Suggestions complete\n")

        # Summary
        print(f"\n{'='*80}")
        print(f"WORKFLOW COMPLETE")
        print(f"{'='*80}\n")

        print(f"📊 Recommendation Summary:")
        print(f"  Total: {report['summary']['total_recommendations']}")
        print(f"  Low Risk: {report['summary']['low_risk']}")
        print(f"  Medium Risk: {report['summary']['medium_risk']}")
        print(f"  High Risk: {report['summary']['high_risk']}")
        print(f"  Blocked: {report['summary']['blocked']}")
        print(f"  Executable: {report['summary']['executable']}\n")

        print(f"📄 Reports Generated:")
        print(
            f"  Lighthouse: reports/lighthouse/{report['client_name']}/{snapshot_date}.json"
        )
        print(f"  Suggestions: {output_path}\n")

        print(f"Next Steps:")
        print(f"  Review: python -m act_autopilot.approval_cli {output_path}")
        print(f"\n{'='*80}\n")

        return True

    except Exception as e:
        print(f"❌ Suggestions failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """CLI entry point"""
    if len(sys.argv) < 3:
        print("Usage: python tools/daily_workflow.py <config_path> <snapshot_date>")
        print(
            "Example: python tools/daily_workflow.py configs/client_synthetic.yaml 2026-02-11"
        )
        sys.exit(1)

    config_path = sys.argv[1]
    snapshot_date = datetime.strptime(sys.argv[2], "%Y-%m-%d").date()

    success = run_daily_workflow(config_path, snapshot_date)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
