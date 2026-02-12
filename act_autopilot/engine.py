"""
Rule Engine — Orchestrates rule evaluation against Lighthouse insights + features.

Flow:
  1. Load Lighthouse JSON report
  2. Load feature rows from DuckDB
  3. Build RuleContext per campaign
  4. Run all rules (budget → bid → account → status)
  5. Resolve conflicts (one recommendation per lever per campaign)
  6. Output ranked recommendations
"""
from __future__ import annotations

import json
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import duckdb

from .models import AutopilotConfig, Recommendation, RuleContext, _safe_float
from .rules.budget_rules import BUDGET_RULES
from .rules.bid_rules import BID_RULES
from .rules.account_rules import ACCOUNT_RULES
from .rules.status_rules import STATUS_RULES


ALL_RULES = BUDGET_RULES + BID_RULES + ACCOUNT_RULES + STATUS_RULES


def load_autopilot_config(client_config_path: str) -> AutopilotConfig:
    """Load client config YAML and extract Autopilot-relevant fields."""
    import yaml

    p = Path(client_config_path)
    if not p.exists():
        raise FileNotFoundError(f"Client config not found: {p}")

    raw = yaml.safe_load(p.read_text(encoding="utf-8")) or {}

    client_id = str(raw.get("client_id") or raw.get("client_name") or "UNKNOWN")
    customer_id = str((raw.get("google_ads") or {}).get("customer_id") or raw.get("customer_id") or "")
    client_type = str(raw.get("client_type") or "ecom")
    primary_kpi = str(raw.get("primary_kpi") or "roas")
    automation_mode = str(raw.get("automation_mode") or "suggest")
    risk_tolerance = str(raw.get("risk_tolerance") or "conservative")
    currency = str(raw.get("currency") or "USD")
    tz = str(raw.get("timezone") or "UTC")

    targets = raw.get("targets") or {}
    target_roas = _to_float(targets.get("target_roas"))
    target_cpa = _to_float(targets.get("target_cpa"))

    caps = raw.get("spend_caps") or {}
    daily_cap = _to_float(caps.get("daily"))
    monthly_cap = _to_float(caps.get("monthly"))

    prot = raw.get("protected_entities") or {}
    brand_protected = bool(prot.get("brand_is_protected", True))
    prot_ids = prot.get("entities") or prot.get("campaign_ids") or []
    if isinstance(prot_ids, (str, int)):
        prot_ids = [prot_ids]
    protected_ids = [str(x).strip() for x in prot_ids if str(x).strip()]

    return AutopilotConfig(
        client_id=client_id,
        customer_id=customer_id,
        client_type=client_type,
        primary_kpi=primary_kpi,
        automation_mode=automation_mode,
        risk_tolerance=risk_tolerance,
        target_roas=target_roas,
        target_cpa=target_cpa,
        daily_cap=daily_cap,
        monthly_cap=monthly_cap,
        protected_campaign_ids=protected_ids,
        brand_is_protected=brand_protected,
        currency=currency,
        timezone=tz,
        raw=raw,
    )


def _to_float(x: Any) -> Optional[float]:
    if x is None:
        return None
    try:
        v = float(x)
        return v if v > 0 else None
    except (TypeError, ValueError):
        return None


def load_lighthouse_report(report_path: str) -> Dict[str, Any]:
    """Load a Lighthouse JSON report."""
    p = Path(report_path)
    if not p.exists():
        raise FileNotFoundError(f"Lighthouse report not found: {p}")
    return json.loads(p.read_text(encoding="utf-8"))


def load_feature_rows(
    con: duckdb.DuckDBPyConnection,
    client_id: str,
    customer_id: str,
    snapshot_date: date,
) -> List[Dict[str, Any]]:
    """Load all campaign feature rows for this client/date."""
    cur = con.execute(
        """
        SELECT * FROM analytics.campaign_features_daily
        WHERE client_id = ? AND customer_id = ? AND snapshot_date = ?;
        """,
        [client_id, customer_id, snapshot_date],
    )
    cols = [c[0] for c in cur.description]
    rows = cur.fetchall()
    return [dict(zip(cols, r)) for r in rows]


def _insights_for_campaign(all_insights: List[Dict], campaign_id: str) -> List[Dict]:
    """Filter insights relevant to a specific campaign (+ account-level)."""
    return [
        ins for ins in all_insights
        if ins.get("entity_type") == "ACCOUNT"
        or str(ins.get("entity_id")) == campaign_id
    ]


def run_rules(
    config: AutopilotConfig,
    lighthouse_report: Dict[str, Any],
    feature_rows: List[Dict[str, Any]],
    recent_changes: Optional[List[Dict[str, Any]]] = None,
) -> List[Recommendation]:
    """
    Run all rules against all campaigns. Returns list of Recommendations.
    """
    if recent_changes is None:
        recent_changes = []

    all_insights = lighthouse_report.get("insights", [])
    all_recs: List[Recommendation] = []

    for feat_row in feature_rows:
        campaign_id = str(feat_row.get("campaign_id"))

        ctx = RuleContext(
            config=config,
            insights=_insights_for_campaign(all_insights, campaign_id),
            features=feat_row,
            all_insights=all_insights,
            all_features=feature_rows,
            recent_changes=recent_changes,
        )

        for rule_fn in ALL_RULES:
            try:
                rec = rule_fn(ctx)
                if rec is not None:
                    all_recs.append(rec)
            except Exception as e:
                # Log but don't crash — one broken rule shouldn't kill the engine
                print(f"[Autopilot] WARN: Rule {rule_fn.__name__} failed on campaign {campaign_id}: {e}")

    # Resolve conflicts and deduplicate
    resolved = _resolve_conflicts(all_recs)

    # Sort by priority (lower = higher priority)
    resolved.sort(key=lambda r: (r.priority, -r.confidence, r.rule_id))

    return resolved


def _resolve_conflicts(recs: List[Recommendation]) -> List[Recommendation]:
    """
    Conflict resolution:
    - One active recommendation per (campaign, lever) combination
    - Keep highest-priority (lowest priority number) recommendation
    - "hold" and "no_action" recommendations don't conflict with each other
    - Account-level recommendations never conflict
    """
    # Group by (entity_id, lever)
    groups: Dict[str, List[Recommendation]] = {}

    for rec in recs:
        lever = _extract_lever(rec.action_type)
        if rec.entity_type == "ACCOUNT" or lever in ("hold", "review", "no_action"):
            # These don't conflict — always include
            key = f"_noconflict_{id(rec)}"
        else:
            key = f"{rec.entity_id}_{lever}"

        groups.setdefault(key, []).append(rec)

    resolved: List[Recommendation] = []
    for key, group in groups.items():
        if key.startswith("_noconflict_"):
            resolved.extend(group)
        else:
            # Prefer unblocked over blocked, then highest priority (lowest number)
            best = min(group, key=lambda r: (r.blocked, r.priority, -r.confidence))
            resolved.append(best)

    return resolved


def _extract_lever(action_type: str) -> str:
    """Extract the lever category from action type."""
    if "budget" in action_type or "pacing" in action_type:
        return "budget"
    if "bid" in action_type:
        return "bid"
    return action_type


def generate_autopilot_report(
    config: AutopilotConfig,
    recommendations: List[Recommendation],
    snapshot_date: date,
    lighthouse_report_path: str,
) -> Dict[str, Any]:
    """Generate the Autopilot JSON report."""
    return {
        "client_id": config.client_id,
        "customer_id": config.customer_id,
        "snapshot_date": snapshot_date.isoformat(),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "automation_mode": config.automation_mode,
        "risk_tolerance": config.risk_tolerance,
        "lighthouse_report": lighthouse_report_path,
        "total_recommendations": len(recommendations),
        "blocked_count": sum(1 for r in recommendations if r.blocked),
        "actionable_count": sum(1 for r in recommendations if not r.blocked and r.action_type not in ("no_action", "review", "budget_hold", "bid_hold")),
        "recommendations": [
            {
                "rule_id": r.rule_id,
                "rule_name": r.rule_name,
                "entity_type": r.entity_type,
                "entity_id": r.entity_id,
                "action_type": r.action_type,
                "risk_tier": r.risk_tier,
                "confidence": round(r.confidence, 4),
                "current_value": r.current_value,
                "recommended_value": r.recommended_value,
                "change_pct": r.change_pct,
                "rationale": r.rationale,
                "evidence": r.evidence,
                "constitution_refs": r.constitution_refs,
                "guardrails_checked": r.guardrails_checked,
                "triggering_diagnosis": r.triggering_diagnosis,
                "triggering_confidence": round(r.triggering_confidence, 4),
                "blocked": r.blocked,
                "block_reason": r.block_reason,
                "priority": r.priority,
            }
            for r in recommendations
        ],
    }
