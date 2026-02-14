from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

# Constitution rule IDs (referenced in outputs)
RULE_CONFIG_GATED = "CONSTITUTION-0-1"
RULE_CLIENT_TYPE_REQUIRED = "CONSTITUTION-3-1"
RULE_LOW_DATA_GATES = "CONSTITUTION-5-2"
RULE_LOW_DATA_APPENDIX = "CONSTITUTION-A-4"
RULE_SPEND_CAPS_PACING = "CONSTITUTION-5-5"


@dataclass(frozen=True)
class Insight:
    insight_rank: int
    entity_type: str  # ACCOUNT | CAMPAIGN
    entity_id: Optional[str]  # campaign_id for CAMPAIGN
    diagnosis_code: str
    confidence: float
    risk_tier: str  # low | med | high
    labels: List[str]
    evidence: Dict[str, Any]
    recommended_action: str
    guardrail_rule_ids: List[str]


def _clamp01(x: float) -> float:
    if x < 0:
        return 0.0
    if x > 1:
        return 1.0
    return x


def _score_volume(
    clicks_w7: float, conversions_w30: float, impressions_w7: float
) -> float:
    clicks_score = _clamp01((clicks_w7 - 10.0) / 90.0)  # 10->0, 100->1
    conv_score = _clamp01(conversions_w30 / 30.0)  # 30 conv -> 1
    impr_score = _clamp01(impressions_w7 / 2000.0)  # 2k impr -> 1
    return 0.65 * clicks_score + 0.25 * conv_score + 0.10 * impr_score


def _score_stability(cost_cv14: Optional[float]) -> float:
    if cost_cv14 is None:
        return 0.5
    return _clamp01(1.0 - (float(cost_cv14) / 1.0))  # CV>=1 => 0


def _score_effect_size(pct_change: Optional[float], scale: float) -> float:
    if pct_change is None:
        return 0.0
    return _clamp01(abs(float(pct_change)) / scale)


def _cap_low_data(conf: float, low_data_flag: bool) -> float:
    if low_data_flag:
        return min(conf, 0.40)
    return conf


def run_diagnostics_for_features_row(
    row: Dict[str, Any],
    needs_config: bool,
    protected_campaign_ids: List[str],
    client_type: Optional[str],
) -> List[Insight]:
    insights: List[Insight] = []

    campaign_id = str(row["campaign_id"])
    low_data_flag = bool(row.get("low_data_flag", False))
    cost_cv14 = row.get("cost_w14_cv")

    clicks_w7 = float(row.get("clicks_w7_sum") or 0.0)
    conv_w30 = float(row.get("conversions_w30_sum") or 0.0)
    impr_w7 = float(row.get("impressions_w7_sum") or 0.0)

    volume = _score_volume(clicks_w7, conv_w30, impr_w7)
    stability = _score_stability(cost_cv14)

    labels: List[str] = []
    guardrails: List[str] = []

    if needs_config:
        labels.append("NEEDS_CONFIG")
        guardrails.extend([RULE_CONFIG_GATED, RULE_CLIENT_TYPE_REQUIRED])

    if low_data_flag:
        labels.extend(["LOW_DATA", "NEEDS_REVIEW"])
        guardrails.extend([RULE_LOW_DATA_GATES, RULE_LOW_DATA_APPENDIX])

    if campaign_id in set(protected_campaign_ids):
        labels.append("PROTECTED")

    # VOLATILE
    if cost_cv14 is not None and float(cost_cv14) > 0.60:
        conf = _cap_low_data(
            0.30 + 0.30 * volume + 0.40 * (1.0 - stability), low_data_flag
        )
        insights.append(
            Insight(
                insight_rank=0,
                entity_type="CAMPAIGN",
                entity_id=campaign_id,
                diagnosis_code="VOLATILE",
                confidence=conf,
                risk_tier="med",
                labels=sorted(set(labels + ["VOLATILE", "NEEDS_REVIEW"])),
                evidence={
                    "cost_w14_cv": float(cost_cv14),
                    "threshold": 0.60,
                    "clicks_w7_sum": clicks_w7,
                    "impressions_w7_sum": impr_w7,
                },
                recommended_action="Review recent changes and avoid reacting to short-term swings; confirm tracking stability.",
                guardrail_rule_ids=sorted(set(guardrails)),
            )
        )

    # COST_SPIKE / COST_DROP (1d vs prior 1d)
    cost_w1_pct = row.get("cost_micros_w1_vs_prev_pct")
    if cost_w1_pct is not None:
        cost_w1_pct = float(cost_w1_pct)
        eff = _score_effect_size(cost_w1_pct, 0.50)
        base_conf = 0.20 + 0.45 * volume + 0.35 * eff
        if cost_w1_pct >= 0.50:
            conf = _cap_low_data(base_conf, low_data_flag)
            insights.append(
                Insight(
                    insight_rank=0,
                    entity_type="CAMPAIGN",
                    entity_id=campaign_id,
                    diagnosis_code="COST_SPIKE",
                    confidence=conf,
                    risk_tier="med",
                    labels=sorted(
                        set(labels + (["NEEDS_REVIEW"] if conf < 0.45 else []))
                    ),
                    evidence={
                        "cost_micros_w1_vs_prev_pct": cost_w1_pct,
                        "threshold": 0.50,
                    },
                    recommended_action="Confirm the driver: budget cap, bidding changes, demand spike, or tracking anomalies.",
                    guardrail_rule_ids=sorted(set(guardrails)),
                )
            )
        elif cost_w1_pct <= -0.50:
            conf = _cap_low_data(base_conf, low_data_flag)
            insights.append(
                Insight(
                    insight_rank=0,
                    entity_type="CAMPAIGN",
                    entity_id=campaign_id,
                    diagnosis_code="COST_DROP",
                    confidence=conf,
                    risk_tier="med",
                    labels=sorted(
                        set(labels + (["NEEDS_REVIEW"] if conf < 0.45 else []))
                    ),
                    evidence={
                        "cost_micros_w1_vs_prev_pct": cost_w1_pct,
                        "threshold": -0.50,
                    },
                    recommended_action="Check budget, eligibility, disapprovals, and demand changes; verify tracking.",
                    guardrail_rule_ids=sorted(set(guardrails)),
                )
            )

    # CTR_DROP (7d vs prior 7d)
    ctr_pct = row.get("ctr_w7_vs_prev_pct")
    if ctr_pct is not None:
        ctr_pct = float(ctr_pct)
        if ctr_pct <= -0.20 and clicks_w7 >= 30 and impr_w7 >= 500:
            eff = _score_effect_size(ctr_pct, 0.30)
            conf = _cap_low_data(0.20 + 0.45 * volume + 0.35 * eff, low_data_flag)
            insights.append(
                Insight(
                    insight_rank=0,
                    entity_type="CAMPAIGN",
                    entity_id=campaign_id,
                    diagnosis_code="CTR_DROP",
                    confidence=conf,
                    risk_tier="low",
                    labels=sorted(set(labels)),
                    evidence={"ctr_w7_vs_prev_pct": ctr_pct, "threshold": -0.20},
                    recommended_action="Review ad relevance and landing alignment; search term inspection comes later.",
                    guardrail_rule_ids=sorted(set(guardrails)),
                )
            )

    # CVR_DROP (14d vs prior 14d)
    cvr_pct = row.get("cvr_w14_vs_prev_pct")
    clicks_w14 = float(row.get("clicks_w14_sum") or 0.0)
    if cvr_pct is not None:
        cvr_pct = float(cvr_pct)
        if cvr_pct <= -0.20 and clicks_w14 >= 60:
            eff = _score_effect_size(cvr_pct, 0.30)
            conf = _cap_low_data(0.20 + 0.45 * volume + 0.35 * eff, low_data_flag)
            insights.append(
                Insight(
                    insight_rank=0,
                    entity_type="CAMPAIGN",
                    entity_id=campaign_id,
                    diagnosis_code="CVR_DROP",
                    confidence=conf,
                    risk_tier="med",
                    labels=sorted(set(labels + ["NEEDS_REVIEW"])),
                    evidence={"cvr_w14_vs_prev_pct": cvr_pct, "threshold": -0.20},
                    recommended_action="Check landing page/offer and confirm tracking; avoid major changes if low data.",
                    guardrail_rule_ids=sorted(set(guardrails)),
                )
            )

    return insights


def run_account_level_diagnostics(
    any_row: Dict[str, Any], needs_config: bool
) -> List[Insight]:
    insights: List[Insight] = []
    labels: List[str] = []
    guardrails: List[str] = []

    if needs_config:
        labels.append("NEEDS_CONFIG")
        guardrails.extend([RULE_CONFIG_GATED, RULE_CLIENT_TYPE_REQUIRED])

    pacing_flag = any_row.get("pacing_flag_over_105")
    if pacing_flag is True:
        insights.append(
            Insight(
                insight_rank=0,
                entity_type="ACCOUNT",
                entity_id=None,
                diagnosis_code="PACE_OVER_CAP",
                confidence=0.85,
                risk_tier="high",
                labels=sorted(set(labels + ["NEEDS_REVIEW"])),
                evidence={
                    "acct_projected_month_cost_micros": any_row.get(
                        "acct_projected_month_cost_micros"
                    ),
                    "acct_monthly_cap_micros": any_row.get("acct_monthly_cap_micros"),
                    "acct_pacing_vs_cap_pct": any_row.get("acct_pacing_vs_cap_pct"),
                    "threshold": 0.05,
                },
                recommended_action="Pacing risk: review spend caps and planned expansions (human decision).",
                guardrail_rule_ids=sorted(set(guardrails + [RULE_SPEND_CAPS_PACING])),
            )
        )

    return insights
