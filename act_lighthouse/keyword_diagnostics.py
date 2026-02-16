from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Dict, List, Optional

import duckdb

from .config import ClientConfig
from .diagnostics import Insight, _clamp01, _cap_low_data

# Constitution rule IDs
RULE_LOW_DATA_GATES = "CONSTITUTION-5-2"
RULE_LOW_DATA_APPENDIX = "CONSTITUTION-A-4"
RULE_KEYWORD_COOLDOWN = "CONSTITUTION-5-3"


# ── Keyword-level diagnostics ────────────────────────────────────────

def _score_keyword_volume(clicks_w7: float, conv_w30: float) -> float:
    """Volume confidence score for keywords (less data than campaigns)."""
    clicks_score = _clamp01((clicks_w7 - 5.0) / 45.0)   # 5->0, 50->1
    conv_score = _clamp01(conv_w30 / 15.0)               # 15 conv -> 1
    return 0.60 * clicks_score + 0.40 * conv_score


def run_keyword_diagnostics(
    row: Dict[str, Any],
    target_cpa_micros: Optional[float],
    target_roas: Optional[float],
    campaign_avg_ctr: Optional[float],
    protected_campaign_ids: List[str],
) -> List[Insight]:
    """
    Generate keyword-level insights from a keyword_features_daily row.

    Args:
        row: One row from analytics.keyword_features_daily
        target_cpa_micros: Client target CPA in micros (e.g., 25_000_000 = $25)
        target_roas: Client target ROAS (e.g., 3.0)
        campaign_avg_ctr: Average CTR for this keyword's campaign (7d)
        protected_campaign_ids: List of protected campaign IDs
    """
    insights: List[Insight] = []

    keyword_id = str(row.get("keyword_id", ""))
    campaign_id = str(row.get("campaign_id", ""))
    keyword_text = str(row.get("keyword_text", ""))
    match_type = str(row.get("match_type", ""))
    status = str(row.get("status", ""))

    # Skip paused keywords
    if status == "PAUSED":
        return insights

    # Skip protected campaigns
    if campaign_id in set(protected_campaign_ids):
        return insights

    low_data_flag = bool(row.get("low_data_flag", False))
    quality_score = row.get("quality_score")

    clicks_w7 = float(row.get("clicks_w7_sum") or 0)
    clicks_w30 = float(row.get("clicks_w30_sum") or 0)
    conv_w30 = float(row.get("conversions_w30_sum") or 0)
    cost_w30 = float(row.get("cost_micros_w30_sum") or 0)
    cost_w90 = float(row.get("cost_micros_w90_sum") or 0)
    conv_w90 = float(row.get("conversions_w90_sum") or 0)
    impr_w7 = float(row.get("impressions_w7_sum") or 0)

    cpa_w30 = float(row.get("cpa_w30") or 0)
    roas_w30 = float(row.get("roas_w30") or 0)
    ctr_w7 = float(row.get("ctr_w7") or 0)
    cvr_w30 = float(row.get("cvr_w30") or 0)

    volume = _score_keyword_volume(clicks_w7, conv_w30)
    base_labels: List[str] = []
    base_guardrails: List[str] = []

    if low_data_flag:
        base_labels.append("LOW_DATA")
        base_guardrails.extend([RULE_LOW_DATA_GATES, RULE_LOW_DATA_APPENDIX])

    # ── KEYWORD_HIGH_CPA ─────────────────────────────────────────
    # CPA > target × 1.5, at least 30 clicks in 30d
    if target_cpa_micros and target_cpa_micros > 0 and cpa_w30 > 0 and clicks_w30 >= 30:
        cpa_ratio = cpa_w30 / target_cpa_micros
        if cpa_ratio > 1.5:
            conf = _cap_low_data(
                _clamp01(0.30 + 0.40 * volume + 0.30 * min(1.0, (cpa_ratio - 1.5) / 1.0)),
                low_data_flag,
            )
            insights.append(Insight(
                insight_rank=0,
                entity_type="KEYWORD",
                entity_id=keyword_id,
                diagnosis_code="KEYWORD_HIGH_CPA",
                confidence=conf,
                risk_tier="med",
                labels=sorted(set(base_labels + ["HIGH_CPA"])),
                evidence={
                    "keyword_text": keyword_text,
                    "match_type": match_type,
                    "campaign_id": campaign_id,
                    "cpa_w30_micros": cpa_w30,
                    "target_cpa_micros": target_cpa_micros,
                    "cpa_ratio": round(cpa_ratio, 2),
                    "clicks_w30": clicks_w30,
                    "conversions_w30": conv_w30,
                    "cost_w30": cost_w30 / 1_000_000,
                },
                recommended_action=(
                    f"Keyword CPA is {cpa_ratio:.1f}x target. "
                    f"Consider bid reduction or pause if trend continues."
                ),
                guardrail_rule_ids=sorted(set(base_guardrails + [RULE_KEYWORD_COOLDOWN])),
            ))

    # ── KEYWORD_LOW_QS ───────────────────────────────────────────
    # Quality Score ≤ 3
    if quality_score is not None and int(quality_score) <= 3:
        qs = int(quality_score)
        # Higher confidence if also has high CPA
        has_high_cpa = (
            target_cpa_micros and cpa_w30 > 0
            and cpa_w30 > target_cpa_micros * 1.5
        )
        conf = 0.65 if has_high_cpa else 0.50
        conf = _cap_low_data(conf, low_data_flag)

        insights.append(Insight(
            insight_rank=0,
            entity_type="KEYWORD",
            entity_id=keyword_id,
            diagnosis_code="KEYWORD_LOW_QS",
            confidence=conf,
            risk_tier="low" if not has_high_cpa else "med",
            labels=sorted(set(base_labels + ["LOW_QS", "NEEDS_REVIEW"])),
            evidence={
                "keyword_text": keyword_text,
                "match_type": match_type,
                "campaign_id": campaign_id,
                "quality_score": qs,
                "quality_score_creative": row.get("quality_score_creative"),
                "quality_score_landing_page": row.get("quality_score_landing_page"),
                "quality_score_relevance": row.get("quality_score_relevance"),
                "has_high_cpa": bool(has_high_cpa),
            },
            recommended_action=(
                f"QS={qs}. Review ad relevance, landing page experience, and "
                f"keyword-to-ad alignment. {'CPA also elevated - consider pause.' if has_high_cpa else ''}"
            ),
            guardrail_rule_ids=sorted(set(base_guardrails)),
        ))

    # ── KEYWORD_WASTED_SPEND ─────────────────────────────────────
    # Cost > $50 in 30d AND zero conversions
    cost_30d_dollars = cost_w30 / 1_000_000
    if cost_30d_dollars > 50 and conv_w30 == 0 and clicks_w30 >= 10:
        conf = _clamp01(0.50 + 0.30 * min(1.0, cost_30d_dollars / 200) + 0.20 * min(1.0, clicks_w30 / 50))
        insights.append(Insight(
            insight_rank=0,
            entity_type="KEYWORD",
            entity_id=keyword_id,
            diagnosis_code="KEYWORD_WASTED_SPEND",
            confidence=conf,
            risk_tier="low",
            labels=sorted(set(base_labels + ["WASTED_SPEND"])),
            evidence={
                "keyword_text": keyword_text,
                "match_type": match_type,
                "campaign_id": campaign_id,
                "cost_w30_dollars": round(cost_30d_dollars, 2),
                "clicks_w30": clicks_w30,
                "conversions_w30": conv_w30,
                "cost_w90_dollars": round(cost_w90 / 1_000_000, 2),
                "conversions_w90": conv_w90,
            },
            recommended_action=(
                f"${cost_30d_dollars:.0f} spent in 30d with zero conversions. "
                f"Strong pause candidate."
            ),
            guardrail_rule_ids=sorted(set(base_guardrails)),
        ))

    # ── KEYWORD_LOW_CTR ──────────────────────────────────────────
    # CTR < campaign avg CTR - 30%, with sufficient impressions
    if (campaign_avg_ctr and campaign_avg_ctr > 0
            and ctr_w7 > 0 and impr_w7 >= 500):
        ctr_threshold = campaign_avg_ctr * 0.70  # 30% below avg
        if ctr_w7 < ctr_threshold:
            ctr_gap_pct = (campaign_avg_ctr - ctr_w7) / campaign_avg_ctr
            conf = _cap_low_data(
                _clamp01(0.30 + 0.40 * volume + 0.30 * min(1.0, ctr_gap_pct / 0.50)),
                low_data_flag,
            )
            insights.append(Insight(
                insight_rank=0,
                entity_type="KEYWORD",
                entity_id=keyword_id,
                diagnosis_code="KEYWORD_LOW_CTR",
                confidence=conf,
                risk_tier="low",
                labels=sorted(set(base_labels + ["LOW_CTR", "NEEDS_REVIEW"])),
                evidence={
                    "keyword_text": keyword_text,
                    "match_type": match_type,
                    "campaign_id": campaign_id,
                    "ctr_w7": round(ctr_w7, 4),
                    "campaign_avg_ctr": round(campaign_avg_ctr, 4),
                    "ctr_gap_pct": round(ctr_gap_pct, 2),
                    "impressions_w7": impr_w7,
                },
                recommended_action=(
                    f"CTR {ctr_w7:.2%} is {ctr_gap_pct:.0%} below campaign average. "
                    f"Review ad copy relevance and creative quality."
                ),
                guardrail_rule_ids=sorted(set(base_guardrails)),
            ))

    return insights


# ── Search term diagnostics ──────────────────────────────────────────

def load_search_term_aggregates(
    con: duckdb.DuckDBPyConnection,
    customer_id: str,
    snapshot_date: date,
    lookback_days: int = 30,
) -> List[Dict[str, Any]]:
    """
    Load aggregated search term performance for the last N days.
    Returns one row per (campaign_id, ad_group_id, search_term).
    """
    start_date = snapshot_date - timedelta(days=lookback_days - 1)

    sql = f"""
    SELECT
        CAST(customer_id AS VARCHAR) AS customer_id,
        CAST(campaign_id AS VARCHAR) AS campaign_id,
        campaign_name,
        CAST(ad_group_id AS VARCHAR) AS ad_group_id,
        ad_group_name,
        CAST(keyword_id AS VARCHAR) AS keyword_id,
        keyword_text,
        search_term,
        search_term_status,
        match_type,
        SUM(COALESCE(impressions, 0)) AS impressions_sum,
        SUM(COALESCE(clicks, 0)) AS clicks_sum,
        SUM(COALESCE(cost_micros, 0)) AS cost_micros_sum,
        SUM(COALESCE(conversions, 0)) AS conversions_sum,
        SUM(COALESCE(conversions_value, 0)) AS conversion_value_sum,
        CASE WHEN SUM(impressions) > 0
             THEN SUM(clicks)::DOUBLE / SUM(impressions)
             ELSE NULL END AS ctr,
        CASE WHEN SUM(clicks) > 0
             THEN SUM(conversions)::DOUBLE / SUM(clicks)
             ELSE NULL END AS cvr,
        CASE WHEN SUM(conversions) > 0
             THEN SUM(cost_micros)::DOUBLE / SUM(conversions)
             ELSE NULL END AS cpa_micros,
        CASE WHEN SUM(cost_micros) > 0
             THEN SUM(conversions_value)::DOUBLE / (SUM(cost_micros)::DOUBLE / 1000000.0)
             ELSE NULL END AS roas
    FROM ro.analytics.search_term_daily
    WHERE CAST(customer_id AS VARCHAR) = ?
      AND CAST(snapshot_date AS DATE) BETWEEN ? AND ?
    GROUP BY customer_id, campaign_id, campaign_name, ad_group_id,
             ad_group_name, keyword_id, keyword_text,
             search_term, search_term_status, match_type
    """

    rows = con.execute(sql, [customer_id, start_date, snapshot_date]).fetchall()
    col_names = [desc[0] for desc in con.description]

    return [dict(zip(col_names, r)) for r in rows]


def run_search_term_diagnostics(
    search_term_rows: List[Dict[str, Any]],
    campaign_avg_cvrs: Dict[str, float],
) -> List[Insight]:
    """
    Generate search term insights from aggregated search term data.

    Args:
        search_term_rows: Output from load_search_term_aggregates()
        campaign_avg_cvrs: Dict mapping campaign_id -> campaign average CVR (30d)
    """
    insights: List[Insight] = []

    for st in search_term_rows:
        search_term = str(st.get("search_term", ""))
        campaign_id = str(st.get("campaign_id", ""))
        ad_group_id = str(st.get("ad_group_id", ""))
        keyword_id = str(st.get("keyword_id", ""))
        keyword_text = str(st.get("keyword_text", ""))
        st_status = str(st.get("search_term_status", ""))

        clicks = float(st.get("clicks_sum") or 0)
        cost_micros = float(st.get("cost_micros_sum") or 0)
        conversions = float(st.get("conversions_sum") or 0)
        conv_value = float(st.get("conversion_value_sum") or 0)
        cvr = st.get("cvr")

        cost_dollars = cost_micros / 1_000_000

        # ── SEARCH_TERM_WINNER ───────────────────────────────────
        # High CVR search term NOT yet added as keyword
        # Threshold: CVR > campaign avg + 20%, ≥ 5 conversions
        if st_status != "ADDED" and conversions >= 5 and cvr is not None:
            campaign_cvr = campaign_avg_cvrs.get(campaign_id, 0)
            cvr_threshold = campaign_cvr * 1.20 if campaign_cvr > 0 else 0.05

            if cvr > cvr_threshold:
                conf = _clamp01(
                    0.40 + 0.30 * min(1.0, conversions / 15)
                    + 0.30 * min(1.0, (cvr - cvr_threshold) / cvr_threshold if cvr_threshold > 0 else 0)
                )
                insights.append(Insight(
                    insight_rank=0,
                    entity_type="SEARCH_TERM",
                    entity_id=search_term,
                    diagnosis_code="SEARCH_TERM_WINNER",
                    confidence=conf,
                    risk_tier="low",
                    labels=["WINNER", "ADD_CANDIDATE"],
                    evidence={
                        "search_term": search_term,
                        "campaign_id": campaign_id,
                        "ad_group_id": ad_group_id,
                        "keyword_id": keyword_id,
                        "keyword_text": keyword_text,
                        "cvr": round(float(cvr), 4),
                        "campaign_avg_cvr": round(campaign_cvr, 4),
                        "conversions": conversions,
                        "clicks": clicks,
                        "cost_dollars": round(cost_dollars, 2),
                        "conversion_value": round(conv_value, 2),
                    },
                    recommended_action=(
                        f"Search term '{search_term}' has CVR {float(cvr):.2%} "
                        f"({conversions:.0f} conv) - add as EXACT keyword."
                    ),
                    guardrail_rule_ids=[],
                ))

        # ── SEARCH_TERM_NEGATIVE ─────────────────────────────────
        # Wasted spend: cost > $50 in 30d, zero conversions
        if cost_dollars > 50 and conversions == 0 and clicks >= 5:
            conf = _clamp01(
                0.50 + 0.30 * min(1.0, cost_dollars / 200)
                + 0.20 * min(1.0, clicks / 30)
            )
            insights.append(Insight(
                insight_rank=0,
                entity_type="SEARCH_TERM",
                entity_id=search_term,
                diagnosis_code="SEARCH_TERM_NEGATIVE",
                confidence=conf,
                risk_tier="low",
                labels=["WASTED_SPEND", "NEGATIVE_CANDIDATE"],
                evidence={
                    "search_term": search_term,
                    "campaign_id": campaign_id,
                    "ad_group_id": ad_group_id,
                    "keyword_id": keyword_id,
                    "keyword_text": keyword_text,
                    "cost_dollars": round(cost_dollars, 2),
                    "clicks": clicks,
                    "conversions": conversions,
                },
                recommended_action=(
                    f"Search term '{search_term}' spent ${cost_dollars:.0f} with "
                    f"zero conversions - add as negative keyword."
                ),
                guardrail_rule_ids=[],
            ))

    return insights


# ── Helper: compute campaign-level average CTRs and CVRs ─────────────

def compute_campaign_averages(
    con: duckdb.DuckDBPyConnection,
    customer_id: str,
    snapshot_date: date,
    lookback_days: int = 7,
) -> tuple[Dict[str, float], Dict[str, float]]:
    """
    Compute campaign-level average CTR and CVR from keyword data.
    Returns: (campaign_avg_ctrs, campaign_avg_cvrs)
    Both are dicts mapping campaign_id -> average value.
    """
    start_date = snapshot_date - timedelta(days=lookback_days - 1)

    sql = """
    SELECT
        CAST(campaign_id AS VARCHAR) AS campaign_id,
        CASE WHEN SUM(impressions) > 0
             THEN SUM(clicks)::DOUBLE / SUM(impressions)
             ELSE NULL END AS avg_ctr,
        CASE WHEN SUM(clicks) > 0
             THEN SUM(conversions)::DOUBLE / SUM(clicks)
             ELSE NULL END AS avg_cvr
    FROM ro.analytics.keyword_daily
    WHERE CAST(customer_id AS VARCHAR) = ?
      AND CAST(snapshot_date AS DATE) BETWEEN ? AND ?
      AND status = 'ENABLED'
    GROUP BY campaign_id
    """

    rows = con.execute(sql, [customer_id, start_date, snapshot_date]).fetchall()

    avg_ctrs: Dict[str, float] = {}
    avg_cvrs: Dict[str, float] = {}

    for row in rows:
        cid = str(row[0])
        if row[1] is not None:
            avg_ctrs[cid] = float(row[1])
        if row[2] is not None:
            avg_cvrs[cid] = float(row[2])

    return avg_ctrs, avg_cvrs
