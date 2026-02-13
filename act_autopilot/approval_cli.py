"""
Approval CLI - Review and approve/reject recommendations
"""

import json
from pathlib import Path
from datetime import date, datetime
from typing import Dict, Any, List


class ApprovalCLI:
    """Interactive CLI for reviewing recommendations"""
    
    def __init__(self, report_path: str):
        self.report_path = Path(report_path)
        self.report = self._load_report()
        self.decisions = []
    
    def _load_report(self) -> Dict[str, Any]:
        """Load suggestion report"""
        if not self.report_path.exists():
            raise FileNotFoundError(f"Report not found: {self.report_path}")
        
        with open(self.report_path) as f:
            return json.load(f)
    
    def review(self):
        """Interactive review session"""
        print(f"\n{'='*80}")
        print(f"RECOMMENDATION REVIEW - {self.report['client_name']}")
        print(f"Date: {self.report['snapshot_date']}")
        print(f"{'='*80}\n")
        
        print(f"Summary:")
        print(f"  Total: {self.report['summary']['total_recommendations']}")
        print(f"  Executable: {self.report['summary']['executable']}")
        print(f"  Blocked: {self.report['summary']['blocked']}")
        print(f"\n{'='*80}\n")
        
        recommendations = self.report['recommendations']
        
        # Filter to unblocked only
        unblocked = [r for r in recommendations if not r['blocked']]
        
        if not unblocked:
            print("No executable recommendations to review.\n")
            return
        
        print(f"Reviewing {len(unblocked)} executable recommendations...\n")
        
        for idx, rec in enumerate(unblocked, 1):
            decision = self._review_recommendation(idx, len(unblocked), rec)
            self.decisions.append({
                "rule_id": rec["rule_id"],
                "entity_id": rec["entity_id"],
                "campaign_name": rec["campaign_name"],
                "action_type": rec["action_type"],
                "decision": decision,
                "reviewed_at": datetime.now().isoformat()
            })
        
        # Save decisions
        self._save_decisions()
    
    def _review_recommendation(self, idx: int, total: int, rec: Dict[str, Any]) -> str:
        """Review single recommendation"""
        print(f"\n[{idx}/{total}] {rec['rule_id']}: {rec['rule_name']}")
        print(f"  Campaign: {rec['campaign_name']} ({rec['entity_id']})")
        print(f"  Action: {rec['action_type']}")
        print(f"  Risk: {rec['risk_tier']} | Confidence: {rec['confidence']:.2f}")
        
        # Only show change details if values exist
        if rec['current_value'] is not None and rec['recommended_value'] is not None and rec['change_pct'] is not None:
            print(f"  Change: {rec['current_value']:.2f} → {rec['recommended_value']:.2f} ({rec['change_pct']:+.1%})")
        
        print(f"  Rationale: {rec['rationale']}")
        print(f"  Expected Impact: {rec['expected_impact']}")
        
        while True:
            choice = input("\n  Decision? [a]pprove / [r]eject / [s]kip: ").lower().strip()
            
            if choice in ['a', 'approve']:
                return 'approved'
            elif choice in ['r', 'reject']:
                return 'rejected'
            elif choice in ['s', 'skip']:
                return 'skipped'
            else:
                print("  Invalid choice. Use 'a', 'r', or 's'.")
    
    def _save_decisions(self):
        """Save approval decisions to JSON"""
        output_dir = self.report_path.parent / "approvals"
        output_dir.mkdir(exist_ok=True)
        
        snapshot_date = self.report['snapshot_date']
        output_path = output_dir / f"{snapshot_date}_approvals.json"
        
        decisions_report = {
            "snapshot_date": snapshot_date,
            "client_name": self.report['client_name'],
            "reviewed_at": datetime.now().isoformat(),
            "total_reviewed": len(self.decisions),
            "approved": sum(1 for d in self.decisions if d['decision'] == 'approved'),
            "rejected": sum(1 for d in self.decisions if d['decision'] == 'rejected'),
            "skipped": sum(1 for d in self.decisions if d['decision'] == 'skipped'),
            "decisions": self.decisions
        }
        
        with open(output_path, 'w') as f:
            json.dump(decisions_report, f, indent=2)
        
        print(f"\n{'='*80}")
        print(f"✅ Decisions saved: {output_path}")
        print(f"\nSummary:")
        print(f"  Approved: {decisions_report['approved']}")
        print(f"  Rejected: {decisions_report['rejected']}")
        print(f"  Skipped: {decisions_report['skipped']}")
        print(f"{'='*80}\n")


def main():
    """CLI entry point"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m act_autopilot.approval_cli <suggestion_report_path>")
        print("Example: python -m act_autopilot.approval_cli reports/suggestions/Synthetic_Test_Client/2026-02-11.json")
        sys.exit(1)
    
    report_path = sys.argv[1]
    
    cli = ApprovalCLI(report_path)
    cli.review()


if __name__ == "__main__":
    main()