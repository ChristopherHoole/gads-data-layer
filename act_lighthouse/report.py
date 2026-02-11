from __future__ import annotations

from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import duckdb

from .config import ClientConfig
from .diagnostics import (
    Insight,
    run_account_level_diagnostics,
    run_diagnostics_for_features_row,
    RULE_CONFIG_GATED,
    RULE_CLIENT_TYPE_REQUIRED,
    RULE_LOW_DATA_GATES,
    RULE_LOW_DATA_APPENDIX,
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_insights_table(con: duckdb.DuckDBPyConnection) -> None:
    con.execute("CREATE SCHEMA IF NOT EXISTS analytics;")
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS analytics.lighthouse_insights_daily (
          client_id TEXT NOT NULL,
          customer_id TEXT NOT NULL,
          snapshot_date DATE NOT NULL,
          insight_rank INTEGER NOT NULL,
          entity_type TEXT NOT NULL,
          entity_id TEXT,
          diagnosis_code TEXT NOT NULL,
          confidence DOUBLE NOT NULL,
          risk_tier TEXT NOT NULL,
          labels_json TEXT NOT NULL,
          evidence_json TEXT NOT NULL,
          recommended_action TEXT NOT NULL,
          guardrail_rule_ids_json TEXT NOT NULL,
          generated_at_utc TIMESTAMP NOT NULL
        );
        """
    )


def _rows_to_dicts(con: duckdb.DuckDBPyConnection, sql: str, params: list[Any]) -> List[Dict[str, Any]]:
    cur = con.execute(sql, params)
    cols = [c[0] for c in cur.description]
    rows = cur.fetchall()
    return [dict(zip(cols, r)) for r in rows]


def _safe_float(x: Any) -> float:
    try:
        if x is None:
            return 0.0
        return float(x)
    except Exception:
        return 0.0


def _make_filler_insight(
    cfg: ClientConfig,
    snapshot_date: date,
    row: Dict[str, Any],
    needs_config: bool,
) -> Insight:
    campaign_id = str(row["campaign_id"])
    low_data_flag = bool(row.get("low_data_flag", False))

    clicks_w7 = _safe_float(row.get("clicks_w7_sum"))
    impr_w7 = _safe_float(row.get("impressions_w7_sum"))
    cost_w7 = _safe_float(row.get("cost_micros_w7_sum"))

    labels: List[str] = []
    guardrails: List[str] = []

    if needs_config:
        labels.append("NEEDS_CONFIG")
        guardrails.extend([RULE_CONFIG_GATED, RULE_CLIENT_TYPE_REQUIRED])

    if low_data_flag:
        labels.extend(["LOW_DATA", "NEEDS_REVIEW"])
        guardrails.extend([RULE_LOW_DATA_GATES, RULE_LOW_DATA_APPENDIX])
        diagnosis_code = "LOW_DATA"
        confidence = 0.35
        recommended = "Low data: collect more volume before making decisions. Review tracking and traffic stability."
        risk = "low"
    else:
        labels.append("NEEDS_REVIEW")
        diagnosis_code = "NEEDS_REVIEW"
        confidence = 0.25
        recommended = "No strong rule-based triggers fired. Monitor trends and ensure config completeness."
        risk = "low"

    evidence = {
        "clicks_w7_sum": clicks_w7,
        "impressions_w7_sum": impr_w7,
        "cost_micros_w7_sum": cost_w7,
        "note": "Filler insight to ensure top-N output (no suppression).",
    }

    return Insight(
        insight_rank=0,
        entity_type="CAMPAIGN",
        entity_id=campaign_id,
        diagnosis_code=diagnosis_code,
        confidence=float(confidence),
        risk_tier=risk,
        labels=sorted(set(labels)),
        evidence=evidence,
        recommended_action=recommended,
        guardrail_rule_ids=sorted(set(guardrails)),
    )


def write_lighthouse_insights_and_report(
    con: duckdb.DuckDBPyConnection,
    cfg: ClientConfig,
    snapshot_date: date,
    max_insights: int = 5,
) -> Dict[str, Any]:
    ensure_insights_table(con)

    needs_config = (cfg.client_type is None or str(cfg.client_type).strip() == "")

    feature_rows = _rows_to_dicts(
        con,
        """
        SELECT *
        FROM analytics.campaign_features_daily
        WHERE client_id = ?
          AND customer_id = ?
          AND snapshot_date = ?;
        """,
        [cfg.client_id, cfg.customer_id, snapshot_date],
    )

    if len(feature_rows) == 0:
        raise RuntimeError("No feature rows found. Build features first for this client/date.")

    # 1) Run real diagnostics
    insights: List[Insight] = []
    insights.extend(run_account_level_diagnostics(feature_rows[0], needs_config))

    for r in feature_rows:
        insights.extend(
            run_diagnostics_for_features_row(
                r,
                needs_config=needs_config,
                protected_campaign_ids=cfg.protected_campaign_ids,
                client_type=cfg.client_type,
            )
        )

    # Track which campaigns already have an insight
    seen_campaigns = set()
    for ins in insights:
        if ins.entity_type == "CAMPAIGN" and ins.entity_id:
            seen_campaigns.add(str(ins.entity_id))

    # 2) Fill to reach max_insights (top campaigns by spend/clicks)
    if len(insights) < max_insights:
        ranked_campaign_rows = sorted(
            feature_rows,
            key=lambda r: (
                -_safe_float(r.get("cost_micros_w7_sum")),
                -_safe_float(r.get("clicks_w7_sum")),
                str(r.get("campaign_id")),
            ),
        )
        for r in ranked_campaign_rows:
            cid = str(r["campaign_id"])
            if cid in seen_campaigns:
                continue
            insights.append(_make_filler_insight(cfg, snapshot_date, r, needs_config))
            seen_campaigns.add(cid)
            if len(insights) >= max_insights:
                break

    # If still short (edge case), add account fillers
    while len(insights) < max_insights:
        insights.append(
            Insight(
                insight_rank=0,
                entity_type="ACCOUNT",
                entity_id=None,
                diagnosis_code="NEEDS_REVIEW",
                confidence=0.20,
                risk_tier="low",
                labels=["NEEDS_REVIEW"] + (["NEEDS_CONFIG"] if needs_config else []),
                evidence={"note": "Filler insight to ensure top-N output."},
                recommended_action="Review config completeness and data availability.",
                guardrail_rule_ids=[RULE_CONFIG_GATED, RULE_CLIENT_TYPE_REQUIRED] if needs_config else [],
            )
        )

    # 3) Sort + take top N
    insights_sorted = sorted(
        insights,
        key=lambda x: (-float(x.confidence), x.diagnosis_code, x.entity_type, x.entity_id or ""),
    )[:max_insights]

    ranked: List[Insight] = []
    for i, ins in enumerate(insights_sorted, start=1):
        ranked.append(
            Insight(
                insight_rank=i,
                entity_type=ins.entity_type,
                entity_id=ins.entity_id,
                diagnosis_code=ins.diagnosis_code,
                confidence=float(ins.confidence),
                risk_tier=ins.risk_tier,
                labels=ins.labels,
                evidence=ins.evidence,
                recommended_action=ins.recommended_action,
                guardrail_rule_ids=ins.guardrail_rule_ids,
            )
        )

    # 4) Write to DuckDB
    con.execute(
        """
        DELETE FROM analytics.lighthouse_insights_daily
        WHERE client_id = ? AND customer_id = ? AND snapshot_date = ?;
        """,
        [cfg.client_id, cfg.customer_id, snapshot_date],
    )

    now_utc = datetime.now(timezone.utc).replace(tzinfo=None)

    for ins in ranked:
        con.execute(
            """
            INSERT INTO analytics.lighthouse_insights_daily (
              client_id, customer_id, snapshot_date,
              insight_rank, entity_type, entity_id,
              diagnosis_code, confidence, risk_tier,
              labels_json, evidence_json,
              recommended_action, guardrail_rule_ids_json,
              generated_at_utc
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            [
                cfg.client_id,
                cfg.customer_id,
                snapshot_date,
                ins.insight_rank,
                ins.entity_type,
                ins.entity_id,
                ins.diagnosis_code,
                ins.confidence,
                ins.risk_tier,
                json.dumps(ins.labels, ensure_ascii=False),
                json.dumps(ins.evidence, ensure_ascii=False),
                ins.recommended_action,
                json.dumps(ins.guardrail_rule_ids, ensure_ascii=False),
                now_utc,
            ],
        )

    # 5) Emit JSON report file
    out_dir = Path("reports") / "lighthouse" / cfg.client_id
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{snapshot_date.isoformat()}.json"

    payload = {
        "client_id": cfg.client_id,
        "customer_id": cfg.customer_id,
        "snapshot_date": snapshot_date.isoformat(),
        "generated_at_utc": _utc_now_iso(),
        "needs_config": bool(needs_config),
        "config_hash": cfg.config_hash,
        "insights": [
            {
                "rank": ins.insight_rank,
                "entity_type": ins.entity_type,
                "entity_id": ins.entity_id,
                "diagnosis_code": ins.diagnosis_code,
                "confidence": ins.confidence,
                "risk_tier": ins.risk_tier,
                "labels": ins.labels,
                "evidence": ins.evidence,
                "recommended_action": ins.recommended_action,
                "guardrail_rule_ids": ins.guardrail_rule_ids,
            }
            for ins in ranked
        ],
    }

    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    return {"insights_written": len(ranked), "report_path": str(out_path)}
