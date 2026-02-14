"""
Suggest Engine - Generate daily recommendations from Lighthouse + Autopilot
"""

import json
from datetime import date, datetime
from pathlib import Path
from typing import Dict, Any, List
import duckdb

from .models import AutopilotConfig, Recommendation
from . import engine


class SuggestEngine:
    """Orchestrates Lighthouse → Autopilot → Recommendations pipeline"""

    def __init__(self, db_path: str = "warehouse.duckdb"):
        self.db_path = Path(db_path)

    def load_lighthouse_insights(
        self, customer_id: str, snapshot_date: date
    ) -> List[Dict[str, Any]]:
        """Load Lighthouse insights from DuckDB"""
        conn = duckdb.connect(str(self.db_path))

        results = conn.execute(
            """
            SELECT *
            FROM analytics.lighthouse_insights_daily
            WHERE customer_id = ?
              AND snapshot_date = ?
            ORDER BY insight_rank
        """,
            [customer_id, snapshot_date],
        ).fetchdf()

        conn.close()

        if results.empty:
            return []

        return results.to_dict("records")

    def generate_suggestions(
        self, config_path: str, snapshot_date: date
    ) -> Dict[str, Any]:
        """
        Main pipeline: Load data → Apply rules → Generate recommendations

        Returns: Suggestion report (dict)
        """
        # Load config
        config = engine.load_autopilot_config(config_path)
        customer_id = config.customer_id

        print(
            f"Generating suggestions for {config.client_name} ({customer_id}) on {snapshot_date}"
        )

        # Load Lighthouse insights
        insights = self.load_lighthouse_insights(customer_id, snapshot_date)

        # Load campaign features
        conn = duckdb.connect(str(self.db_path))
        features_df = conn.execute(
            """
            SELECT *
            FROM analytics.campaign_features_daily
            WHERE customer_id = ?
              AND snapshot_date = ?
        """,
            [customer_id, snapshot_date],
        ).fetchdf()
        conn.close()

        features = features_df.to_dict("records") if not features_df.empty else []

        print(f"  Loaded {len(insights)} insights, {len(features)} campaign features")

        if not insights:
            print("  ⚠️  No insights found - cannot generate suggestions")
            return self._empty_report(customer_id, snapshot_date, config)

        # Run rules
        recommendations = engine.run_rules(
            config=config,
            insights=insights,
            features=features,
            snapshot_date=snapshot_date,
            db_path=str(self.db_path),
        )

        print(f"  Generated {len(recommendations)} recommendations")

        # Build report
        report = self._build_report(
            customer_id=customer_id,
            snapshot_date=snapshot_date,
            config=config,
            recommendations=recommendations,
        )

        return report

    def _empty_report(
        self, customer_id: str, snapshot_date: date, config: AutopilotConfig
    ) -> Dict[str, Any]:
        """Empty report when no insights available"""
        return {
            "customer_id": customer_id,
            "snapshot_date": str(snapshot_date),
            "generated_at": datetime.now().isoformat(),
            "client_name": config.client_name,
            "automation_mode": config.automation_mode,
            "summary": {
                "total_recommendations": 0,
                "low_risk": 0,
                "medium_risk": 0,
                "high_risk": 0,
                "blocked": 0,
                "executable": 0,
            },
            "recommendations": [],
        }

    def _build_report(
        self,
        customer_id: str,
        snapshot_date: date,
        config: AutopilotConfig,
        recommendations: List[Recommendation],
    ) -> Dict[str, Any]:
        """Build suggestion report"""

        # Summary stats
        total = len(recommendations)
        low = sum(1 for r in recommendations if r.risk_tier == "low")
        med = sum(1 for r in recommendations if r.risk_tier == "med")
        high = sum(1 for r in recommendations if r.risk_tier == "high")
        blocked = sum(1 for r in recommendations if r.blocked)
        executable = total - blocked

        # Convert recommendations to dicts
        recs_json = []
        for rec in recommendations:
            recs_json.append(
                {
                    "rule_id": rec.rule_id,
                    "rule_name": rec.rule_name,
                    "entity_type": rec.entity_type,
                    "entity_id": rec.entity_id,
                    "campaign_name": rec.evidence.get("campaign_name", "N/A"),
                    "action_type": rec.action_type,
                    "risk_tier": rec.risk_tier,
                    "confidence": round(rec.confidence, 3),
                    "current_value": rec.current_value,
                    "recommended_value": rec.recommended_value,
                    "change_pct": round(rec.change_pct, 4) if rec.change_pct else None,
                    "rationale": rec.rationale,
                    "expected_impact": rec.evidence.get("expected_impact", "N/A"),
                    "blocked": rec.blocked,
                    "block_reason": rec.block_reason,
                    "priority": rec.priority,
                    "constitution_refs": rec.constitution_refs,
                    "guardrails_checked": rec.guardrails_checked,
                    "evidence": rec.evidence,
                    "triggering_diagnosis": rec.triggering_diagnosis,
                    "triggering_confidence": round(rec.triggering_confidence, 3),
                }
            )

        return {
            "customer_id": customer_id,
            "snapshot_date": str(snapshot_date),
            "generated_at": datetime.now().isoformat(),
            "client_name": config.client_name,
            "automation_mode": config.automation_mode,
            "summary": {
                "total_recommendations": total,
                "low_risk": low,
                "medium_risk": med,
                "high_risk": high,
                "blocked": blocked,
                "executable": executable,
            },
            "recommendations": recs_json,
        }

    def save_report(
        self, report: Dict[str, Any], output_dir: str = "reports/suggestions"
    ) -> Path:
        """Save report to JSON file"""
        client_name = report["client_name"]
        snapshot_date = report["snapshot_date"]

        output_path = Path(output_dir) / client_name / f"{snapshot_date}.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)

        print(f"  ✅ Saved report: {output_path}")

        return output_path


def main():
    """CLI entry point"""
    import sys
    from datetime import datetime

    if len(sys.argv) < 3:
        print(
            "Usage: python -m act_autopilot.suggest_engine <config_path> <snapshot_date>"
        )
        print(
            "Example: python -m act_autopilot.suggest_engine configs/client_synthetic.yaml 2026-02-11"
        )
        sys.exit(1)

    config_path = sys.argv[1]
    snapshot_date = datetime.strptime(sys.argv[2], "%Y-%m-%d").date()

    engine_instance = SuggestEngine()
    report = engine_instance.generate_suggestions(config_path, snapshot_date)
    engine_instance.save_report(report)

    print(f"\n📊 Summary:")
    print(f"  Total: {report['summary']['total_recommendations']}")
    print(f"  Low: {report['summary']['low_risk']}")
    print(f"  Medium: {report['summary']['medium_risk']}")
    print(f"  High: {report['summary']['high_risk']}")
    print(f"  Blocked: {report['summary']['blocked']}")
    print(f"  Executable: {report['summary']['executable']}")


if __name__ == "__main__":
    main()
