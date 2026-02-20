#!/usr/bin/env python3
r"""
Synthetic Keyword + Search Term Data Generator
===============================================
Chat 10 - Ads Control Tower

Generates realistic keyword and search term data for testing keyword rules.

Output:
  - snap_keyword_daily:      20 campaigns × 50 keywords × 90 days = 90,000 rows
  - snap_search_term_daily:  20 campaigns × 25 search terms × 90 days = 45,000 rows

Keyword scenarios per campaign (50 keywords each):
  - 10 high performers    (low CPA, high ROAS, good QS)
  - 10 solid performers   (on-target CPA/ROAS, decent QS)
  - 8 underperformers     (high CPA, low ROAS)
  - 5 wasted spend        (clicks but zero conversions)
  - 5 new keywords        (< 30 days data)
  - 5 low quality score   (QS 1-3)
  - 4 low impression share (good CVR but few impressions)
  - 3 paused keywords     (status PAUSED)

Search term scenarios per campaign (25 search terms):
  - 8 winners       (high CVR, should add as keyword)
  - 7 decent        (moderate CVR)
  - 5 negatives     (wasted spend, zero conversions)
  - 3 competitor    (competitor brand terms, low QS signal)
  - 2 already added (status ADDED)

Usage:
  cd C:\Users\User\Desktop\gads-data-layer
  .\.venv\Scripts\Activate.ps1
  python tools/testing/generate_synthetic_keywords.py
  .\tools\refresh_readonly.ps1
"""

import random
import sys
import uuid
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import numpy as np

# ── Add project root to path ──────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import duckdb

# ── Constants ─────────────────────────────────────────────────────────
CUSTOMER_ID = "9999999999"
DB_PATH = str(PROJECT_ROOT / "warehouse.duckdb")

# Date range: 90 days ending yesterday
END_DATE = date(2026, 2, 13)
START_DATE = END_DATE - timedelta(days=89)  # 90 days inclusive
DAYS = 90

# Campaign IDs (same as existing synthetic campaigns 3001-3020)
CAMPAIGN_IDS = list(range(3001, 3021))

CAMPAIGN_NAMES = {
    3001: "Stable ROAS 2.0",
    3002: "Stable ROAS 3.0",
    3003: "Stable ROAS 4.0",
    3004: "Stable ROAS 5.0",
    3005: "Growth Strong",
    3006: "Growth Moderate",
    3007: "Growth Slow",
    3008: "Decline Fast",
    3009: "Decline Moderate",
    3010: "Decline Slow",
    3011: "Seasonal High Amplitude",
    3012: "Seasonal Low Amplitude",
    3013: "Volatile High",
    3014: "Volatile Medium",
    3015: "Volatile Low",
    3016: "Low Data Micro",
    3017: "Low Data Small",
    3018: "Budget Constrained High",
    3019: "Budget Constrained Medium",
    3020: "Recovery Turnaround",
}

MATCH_TYPES = ["EXACT", "PHRASE", "BROAD"]

# ── Keyword text pools ────────────────────────────────────────────────
# Realistic keyword stems by industry vertical
KEYWORD_STEMS = [
    "buy", "best", "cheap", "online", "near me", "reviews",
    "compare", "top", "affordable", "premium", "professional",
    "discount", "free shipping", "sale", "deals", "price",
    "custom", "quality", "fast", "reliable",
]

PRODUCT_TERMS = [
    "running shoes", "laptop", "insurance quote", "web hosting",
    "crm software", "office chair", "marketing agency",
    "accounting software", "gym membership", "meal delivery",
    "car insurance", "home security", "vpn service",
    "project management tool", "email marketing", "seo services",
    "cloud storage", "business phone", "payroll software",
    "digital camera",
]

COMPETITOR_NAMES = [
    "competitorx", "brandyz", "rivalco", "altbrand", "otherco",
]

# ── Search term pools ────────────────────────────────────────────────
SEARCH_TERM_MODIFIERS = [
    "best", "cheap", "how to", "what is", "reviews",
    "vs", "alternative", "free", "cost", "pricing",
    "near me", "online", "2026", "top rated", "compare",
]


# ── Helpers ───────────────────────────────────────────────────────────
def _generate_keyword_text(campaign_idx: int, kw_idx: int) -> str:
    """Generate a realistic keyword text string."""
    stem = KEYWORD_STEMS[kw_idx % len(KEYWORD_STEMS)]
    product = PRODUCT_TERMS[campaign_idx % len(PRODUCT_TERMS)]
    # Vary the combination
    if kw_idx < 15:
        return f"{stem} {product}"
    elif kw_idx < 30:
        return f"{product} {stem}"
    elif kw_idx < 40:
        # Long tail
        modifier = SEARCH_TERM_MODIFIERS[kw_idx % len(SEARCH_TERM_MODIFIERS)]
        return f"{modifier} {product} {stem}"
    else:
        return f"{product}"


def _generate_search_term(campaign_idx: int, st_idx: int, keyword_text: str) -> str:
    """Generate a realistic search term based on a keyword."""
    modifier = SEARCH_TERM_MODIFIERS[st_idx % len(SEARCH_TERM_MODIFIERS)]
    product = PRODUCT_TERMS[campaign_idx % len(PRODUCT_TERMS)]

    if st_idx < 8:
        # Winner terms: close to keyword
        return f"{modifier} {product}"
    elif st_idx < 15:
        # Decent terms
        return f"{keyword_text} {modifier}"
    elif st_idx < 20:
        # Negative terms: irrelevant
        irrelevant = ["jobs", "salary", "careers", "training", "certification"]
        return f"{product} {irrelevant[st_idx % len(irrelevant)]}"
    elif st_idx < 23:
        # Competitor terms
        comp = COMPETITOR_NAMES[st_idx % len(COMPETITOR_NAMES)]
        return f"{comp} {product}"
    else:
        # Already added
        return f"buy {product} online"


def _date_range(start: date, end: date) -> list[date]:
    """Generate inclusive date range."""
    out = []
    d = start
    while d <= end:
        out.append(d)
        d += timedelta(days=1)
    return out


# ── Keyword row generators ───────────────────────────────────────────

def _generate_keyword_scenario(
    campaign_id: int,
    campaign_idx: int,
    ad_group_id: int,
    kw_idx: int,
    keyword_id: int,
) -> dict:
    """
    Return a keyword config dict describing the scenario for this keyword.
    Used to generate daily rows.
    """
    keyword_text = _generate_keyword_text(campaign_idx, kw_idx)

    # ── Assign scenario based on kw_idx position ──
    if kw_idx < 10:
        # HIGH PERFORMERS (10)
        scenario = "high_performer"
        match_type = "EXACT" if kw_idx < 6 else "PHRASE"
        status = "ENABLED"
        quality_score = random.randint(7, 10)
        qs_creative = 3 if quality_score >= 8 else 2
        qs_landing = 3 if quality_score >= 7 else 2
        qs_relevance = 3 if quality_score >= 8 else 2
        base_impressions = random.randint(200, 800)
        base_ctr = random.uniform(0.06, 0.12)
        base_cvr = random.uniform(0.08, 0.18)
        base_cpc_micros = random.randint(400000, 1200000)
        base_conv_value_mult = random.uniform(40, 80)
        bid_micros = random.randint(1000000, 2500000)
        first_page_cpc = random.randint(500000, 1000000)
        top_page_cpc = random.randint(800000, 1500000)
        days_active = DAYS

    elif kw_idx < 20:
        # SOLID PERFORMERS (10)
        scenario = "solid_performer"
        match_type = random.choice(["EXACT", "PHRASE"])
        status = "ENABLED"
        quality_score = random.randint(5, 7)
        qs_creative = 2
        qs_landing = 2
        qs_relevance = 2 if quality_score >= 6 else 1
        base_impressions = random.randint(100, 400)
        base_ctr = random.uniform(0.03, 0.06)
        base_cvr = random.uniform(0.04, 0.08)
        base_cpc_micros = random.randint(600000, 1500000)
        base_conv_value_mult = random.uniform(25, 50)
        bid_micros = random.randint(1200000, 2000000)
        first_page_cpc = random.randint(700000, 1200000)
        top_page_cpc = random.randint(1000000, 1800000)
        days_active = DAYS

    elif kw_idx < 28:
        # UNDERPERFORMERS (8)
        scenario = "underperformer"
        match_type = random.choice(["PHRASE", "BROAD"])
        status = "ENABLED"
        quality_score = random.randint(3, 5)
        qs_creative = 1
        qs_landing = 2 if quality_score >= 4 else 1
        qs_relevance = 1
        base_impressions = random.randint(150, 500)
        base_ctr = random.uniform(0.02, 0.04)
        base_cvr = random.uniform(0.01, 0.03)
        base_cpc_micros = random.randint(800000, 2000000)
        base_conv_value_mult = random.uniform(15, 30)
        bid_micros = random.randint(1500000, 3000000)
        first_page_cpc = random.randint(1000000, 2000000)
        top_page_cpc = random.randint(1500000, 2500000)
        days_active = DAYS

    elif kw_idx < 33:
        # WASTED SPEND (5) - clicks but zero conversions
        scenario = "wasted_spend"
        match_type = "BROAD"
        status = "ENABLED"
        quality_score = random.randint(2, 4)
        qs_creative = 1
        qs_landing = 1
        qs_relevance = 1
        base_impressions = random.randint(100, 300)
        base_ctr = random.uniform(0.02, 0.04)
        base_cvr = 0.0  # Zero conversions!
        base_cpc_micros = random.randint(600000, 1800000)
        base_conv_value_mult = 0.0
        bid_micros = random.randint(1000000, 2500000)
        first_page_cpc = random.randint(800000, 1500000)
        top_page_cpc = random.randint(1200000, 2000000)
        days_active = DAYS

    elif kw_idx < 38:
        # NEW KEYWORDS (5) - less than 30 days of data
        scenario = "new_keyword"
        match_type = random.choice(["EXACT", "PHRASE"])
        status = "ENABLED"
        quality_score = random.randint(5, 7)
        qs_creative = 2
        qs_landing = 2
        qs_relevance = 2
        base_impressions = random.randint(50, 200)
        base_ctr = random.uniform(0.03, 0.07)
        base_cvr = random.uniform(0.03, 0.08)
        base_cpc_micros = random.randint(500000, 1200000)
        base_conv_value_mult = random.uniform(30, 60)
        bid_micros = random.randint(1000000, 2000000)
        first_page_cpc = random.randint(600000, 1000000)
        top_page_cpc = random.randint(900000, 1500000)
        # Only active for 10-25 days
        days_active = random.randint(10, 25)

    elif kw_idx < 43:
        # LOW QUALITY SCORE (5) - QS 1-3
        scenario = "low_qs"
        match_type = random.choice(["PHRASE", "BROAD"])
        status = "ENABLED"
        quality_score = random.randint(1, 3)
        qs_creative = 1
        qs_landing = 1
        qs_relevance = 1
        base_impressions = random.randint(80, 250)
        base_ctr = random.uniform(0.01, 0.03)
        base_cvr = random.uniform(0.02, 0.05)
        base_cpc_micros = random.randint(1000000, 2500000)
        base_conv_value_mult = random.uniform(20, 40)
        bid_micros = random.randint(2000000, 4000000)
        first_page_cpc = random.randint(1500000, 2500000)
        top_page_cpc = random.randint(2000000, 3500000)
        days_active = DAYS

    elif kw_idx < 47:
        # LOW IMPRESSION SHARE (4) - good CVR but low volume
        scenario = "low_impression_share"
        match_type = "EXACT"
        status = "ENABLED"
        quality_score = random.randint(6, 8)
        qs_creative = 2
        qs_landing = 3
        qs_relevance = 2
        base_impressions = random.randint(10, 40)  # Very low!
        base_ctr = random.uniform(0.08, 0.15)
        base_cvr = random.uniform(0.10, 0.20)
        base_cpc_micros = random.randint(300000, 800000)
        base_conv_value_mult = random.uniform(50, 90)
        bid_micros = random.randint(500000, 1000000)
        first_page_cpc = random.randint(800000, 1500000)
        top_page_cpc = random.randint(1200000, 2000000)
        days_active = DAYS

    else:
        # PAUSED (3)
        scenario = "paused"
        match_type = random.choice(["EXACT", "PHRASE"])
        status = "PAUSED"
        quality_score = random.randint(3, 5)
        qs_creative = 1
        qs_landing = 2
        qs_relevance = 1
        base_impressions = 0
        base_ctr = 0.0
        base_cvr = 0.0
        base_cpc_micros = 0
        base_conv_value_mult = 0.0
        bid_micros = random.randint(1000000, 2000000)
        first_page_cpc = random.randint(700000, 1200000)
        top_page_cpc = random.randint(1000000, 1800000)
        days_active = 0  # No daily data for paused

    return {
        "campaign_id": campaign_id,
        "campaign_name": CAMPAIGN_NAMES[campaign_id],
        "ad_group_id": ad_group_id,
        "ad_group_name": f"AG-{campaign_id}-{(kw_idx // 10) + 1}",
        "keyword_id": keyword_id,
        "keyword_text": keyword_text,
        "match_type": match_type,
        "status": status,
        "scenario": scenario,
        "quality_score": quality_score,
        "qs_creative": qs_creative,
        "qs_landing": qs_landing,
        "qs_relevance": qs_relevance,
        "base_impressions": base_impressions,
        "base_ctr": base_ctr,
        "base_cvr": base_cvr,
        "base_cpc_micros": base_cpc_micros,
        "base_conv_value_mult": base_conv_value_mult,
        "bid_micros": bid_micros,
        "first_page_cpc": first_page_cpc,
        "top_page_cpc": top_page_cpc,
        "days_active": days_active,
    }


def _generate_daily_keyword_row(
    kw_config: dict,
    snapshot_date: date,
    day_index: int,
    run_id: str,
    ingested_at: str,
) -> dict | None:
    """Generate one daily row for a keyword. Returns None if keyword not active on this day."""
    # Skip paused keywords entirely
    if kw_config["status"] == "PAUSED":
        return None

    # New keywords: only generate data for last N days
    if kw_config["scenario"] == "new_keyword":
        first_active_day = DAYS - kw_config["days_active"]
        if day_index < first_active_day:
            return None

    # Daily noise factor
    noise = np.random.normal(1.0, 0.15)
    noise = max(0.3, min(2.0, noise))  # Clamp

    impressions = max(0, int(kw_config["base_impressions"] * noise))
    clicks = max(0, int(impressions * kw_config["base_ctr"] * np.random.normal(1.0, 0.1)))
    clicks = min(clicks, impressions)

    cost_micros = int(clicks * kw_config["base_cpc_micros"] * np.random.normal(1.0, 0.08))
    cost_micros = max(0, cost_micros)

    # Conversions
    if kw_config["base_cvr"] > 0 and clicks > 0:
        # Use binomial for realistic conversion counts
        conversions = float(np.random.binomial(clicks, min(1.0, kw_config["base_cvr"])))
    else:
        conversions = 0.0

    conv_value = round(conversions * kw_config["base_conv_value_mult"] * np.random.normal(1.0, 0.1), 2)
    conv_value = max(0.0, conv_value)

    return {
        "run_id": run_id,
        "ingested_at": ingested_at,
        "customer_id": CUSTOMER_ID,
        "snapshot_date": snapshot_date.strftime("%Y-%m-%d"),
        "campaign_id": kw_config["campaign_id"],
        "campaign_name": kw_config["campaign_name"],
        "ad_group_id": kw_config["ad_group_id"],
        "ad_group_name": kw_config["ad_group_name"],
        "keyword_id": kw_config["keyword_id"],
        "keyword_text": kw_config["keyword_text"],
        "match_type": kw_config["match_type"],
        "status": kw_config["status"],
        "quality_score": kw_config["quality_score"],
        "quality_score_creative": kw_config["qs_creative"],
        "quality_score_landing_page": kw_config["qs_landing"],
        "quality_score_relevance": kw_config["qs_relevance"],
        "bid_micros": kw_config["bid_micros"],
        "first_page_cpc_micros": kw_config["first_page_cpc"],
        "top_of_page_cpc_micros": kw_config["top_page_cpc"],
        "impressions": impressions,
        "clicks": clicks,
        "cost_micros": cost_micros,
        "conversions": conversions,
        "conversions_value": conv_value,
        # Chat 23 M2: IS metrics — correlated to QS and impressions
        "search_impression_share":              round(min(1.0, impressions / max(1, impressions) * np.random.uniform(0.40, 0.90)), 4),
        "search_top_impression_share":          round(min(1.0, np.random.uniform(0.20, 0.55)), 4),
        "search_absolute_top_impression_share": round(min(1.0, np.random.uniform(0.08, 0.28)), 4),
        "click_share":                          round(min(1.0, np.random.uniform(0.30, 0.75)), 4),
    }


# ── Search term row generators ───────────────────────────────────────

def _generate_search_term_scenario(
    campaign_id: int,
    campaign_idx: int,
    ad_group_id: int,
    st_idx: int,
    triggering_keyword: dict,
) -> dict:
    """Return a search term config dict."""
    search_term_text = _generate_search_term(
        campaign_idx, st_idx, triggering_keyword["keyword_text"]
    )

    if st_idx < 8:
        # WINNERS (8) - high CVR, should add as keyword
        scenario = "winner"
        st_status = "NONE"
        base_impressions = random.randint(50, 200)
        base_ctr = random.uniform(0.05, 0.10)
        base_cvr = random.uniform(0.10, 0.25)
        base_cpc_micros = random.randint(400000, 1000000)
        base_conv_value_mult = random.uniform(40, 80)

    elif st_idx < 15:
        # DECENT (7) - moderate CVR
        scenario = "decent"
        st_status = "NONE"
        base_impressions = random.randint(30, 150)
        base_ctr = random.uniform(0.03, 0.06)
        base_cvr = random.uniform(0.03, 0.07)
        base_cpc_micros = random.randint(500000, 1200000)
        base_conv_value_mult = random.uniform(25, 50)

    elif st_idx < 20:
        # NEGATIVES (5) - wasted spend, zero conversions
        scenario = "negative"
        st_status = "NONE"
        base_impressions = random.randint(40, 200)
        base_ctr = random.uniform(0.02, 0.05)
        base_cvr = 0.0
        base_cpc_micros = random.randint(500000, 1500000)
        base_conv_value_mult = 0.0

    elif st_idx < 23:
        # COMPETITOR (3) - competitor brand terms
        scenario = "competitor"
        st_status = "NONE"
        base_impressions = random.randint(20, 100)
        base_ctr = random.uniform(0.01, 0.03)
        base_cvr = random.uniform(0.005, 0.02)
        base_cpc_micros = random.randint(800000, 2500000)
        base_conv_value_mult = random.uniform(15, 30)

    else:
        # ALREADY ADDED (2)
        scenario = "already_added"
        st_status = "ADDED"
        base_impressions = random.randint(80, 250)
        base_ctr = random.uniform(0.06, 0.10)
        base_cvr = random.uniform(0.08, 0.15)
        base_cpc_micros = random.randint(400000, 900000)
        base_conv_value_mult = random.uniform(40, 70)

    return {
        "campaign_id": campaign_id,
        "campaign_name": CAMPAIGN_NAMES[campaign_id],
        "ad_group_id": ad_group_id,
        "ad_group_name": triggering_keyword["ad_group_name"],
        "keyword_id": triggering_keyword["keyword_id"],
        "keyword_text": triggering_keyword["keyword_text"],
        "search_term": search_term_text,
        "search_term_status": st_status,
        "match_type": triggering_keyword["match_type"],
        "scenario": scenario,
        "base_impressions": base_impressions,
        "base_ctr": base_ctr,
        "base_cvr": base_cvr,
        "base_cpc_micros": base_cpc_micros,
        "base_conv_value_mult": base_conv_value_mult,
    }


def _generate_daily_search_term_row(
    st_config: dict,
    snapshot_date: date,
    day_index: int,
    run_id: str,
    ingested_at: str,
) -> dict:
    """Generate one daily row for a search term."""
    noise = np.random.normal(1.0, 0.20)
    noise = max(0.2, min(2.5, noise))

    impressions = max(0, int(st_config["base_impressions"] * noise))
    clicks = max(0, int(impressions * st_config["base_ctr"] * np.random.normal(1.0, 0.12)))
    clicks = min(clicks, impressions)

    cost_micros = int(clicks * st_config["base_cpc_micros"] * np.random.normal(1.0, 0.10))
    cost_micros = max(0, cost_micros)

    if st_config["base_cvr"] > 0 and clicks > 0:
        conversions = float(np.random.binomial(clicks, min(1.0, st_config["base_cvr"])))
    else:
        conversions = 0.0

    conv_value = round(conversions * st_config["base_conv_value_mult"] * np.random.normal(1.0, 0.12), 2)
    conv_value = max(0.0, conv_value)

    return {
        "run_id": run_id,
        "ingested_at": ingested_at,
        "customer_id": CUSTOMER_ID,
        "snapshot_date": snapshot_date.strftime("%Y-%m-%d"),
        "campaign_id": st_config["campaign_id"],
        "campaign_name": st_config["campaign_name"],
        "ad_group_id": st_config["ad_group_id"],
        "ad_group_name": st_config["ad_group_name"],
        "keyword_id": st_config["keyword_id"],
        "keyword_text": st_config["keyword_text"],
        "search_term": st_config["search_term"],
        "search_term_status": st_config["search_term_status"],
        "match_type": st_config["match_type"],
        "impressions": impressions,
        "clicks": clicks,
        "cost_micros": cost_micros,
        "conversions": conversions,
        "conversions_value": conv_value,
    }


# ── Main generator ───────────────────────────────────────────────────

def generate_all():
    """Generate all keyword + search term synthetic data."""
    random.seed(42)
    np.random.seed(42)

    run_id = str(uuid.uuid4())
    ingested_at = datetime.now(timezone.utc).isoformat()
    dates = _date_range(START_DATE, END_DATE)

    print(f"Generating synthetic keyword + search term data...")
    print(f"  Customer ID: {CUSTOMER_ID}")
    print(f"  Date range:  {START_DATE} to {END_DATE} ({DAYS} days)")
    print(f"  Campaigns:   {len(CAMPAIGN_IDS)}")
    print(f"  Keywords:    50 per campaign = {len(CAMPAIGN_IDS) * 50}")
    print(f"  Search terms: 25 per campaign = {len(CAMPAIGN_IDS) * 25}")
    print()

    # ── Step 1: Generate keyword configs ──
    print("Step 1: Generating keyword configurations...")
    all_keyword_configs = []
    keyword_id_counter = 100001

    for camp_idx, campaign_id in enumerate(CAMPAIGN_IDS):
        ad_group_base_id = campaign_id * 100

        for kw_idx in range(50):
            keyword_id = keyword_id_counter
            keyword_id_counter += 1

            # Distribute keywords across 5 ad groups per campaign
            ag_offset = kw_idx // 10
            ad_group_id = ad_group_base_id + ag_offset

            config = _generate_keyword_scenario(
                campaign_id=campaign_id,
                campaign_idx=camp_idx,
                ad_group_id=ad_group_id,
                kw_idx=kw_idx,
                keyword_id=keyword_id,
            )
            all_keyword_configs.append(config)

    print(f"  Created {len(all_keyword_configs)} keyword configs")

    # Count scenarios
    scenario_counts = {}
    for kc in all_keyword_configs:
        s = kc["scenario"]
        scenario_counts[s] = scenario_counts.get(s, 0) + 1
    for s, c in sorted(scenario_counts.items()):
        print(f"    {s}: {c}")

    # ── Step 2: Generate search term configs ──
    print("\nStep 2: Generating search term configurations...")
    all_search_term_configs = []

    for camp_idx, campaign_id in enumerate(CAMPAIGN_IDS):
        # Get this campaign's keyword configs for triggering keyword reference
        camp_keywords = [kc for kc in all_keyword_configs if kc["campaign_id"] == campaign_id]
        ad_group_id = campaign_id * 100  # Primary ad group

        for st_idx in range(25):
            # Pick a triggering keyword (cycle through first 25 keywords)
            triggering_kw = camp_keywords[st_idx % len(camp_keywords)]

            config = _generate_search_term_scenario(
                campaign_id=campaign_id,
                campaign_idx=camp_idx,
                ad_group_id=triggering_kw["ad_group_id"],
                st_idx=st_idx,
                triggering_keyword=triggering_kw,
            )
            all_search_term_configs.append(config)

    print(f"  Created {len(all_search_term_configs)} search term configs")

    st_scenario_counts = {}
    for sc in all_search_term_configs:
        s = sc["scenario"]
        st_scenario_counts[s] = st_scenario_counts.get(s, 0) + 1
    for s, c in sorted(st_scenario_counts.items()):
        print(f"    {s}: {c}")

    # ── Step 3: Generate daily rows ──
    print(f"\nStep 3: Generating daily keyword rows ({len(all_keyword_configs)} keywords × {DAYS} days)...")
    all_keyword_rows = []

    for day_idx, d in enumerate(dates):
        for kc in all_keyword_configs:
            row = _generate_daily_keyword_row(kc, d, day_idx, run_id, ingested_at)
            if row is not None:
                all_keyword_rows.append(row)

        if (day_idx + 1) % 30 == 0:
            print(f"    Day {day_idx + 1}/{DAYS} done ({len(all_keyword_rows)} rows so far)")

    print(f"  Total keyword rows: {len(all_keyword_rows)}")

    print(f"\nStep 4: Generating daily search term rows ({len(all_search_term_configs)} terms × {DAYS} days)...")
    all_search_term_rows = []

    for day_idx, d in enumerate(dates):
        for sc in all_search_term_configs:
            row = _generate_daily_search_term_row(sc, d, day_idx, run_id, ingested_at)
            all_search_term_rows.append(row)

        if (day_idx + 1) % 30 == 0:
            print(f"    Day {day_idx + 1}/{DAYS} done ({len(all_search_term_rows)} rows so far)")

    print(f"  Total search term rows: {len(all_search_term_rows)}")

    # ── Step 4: Write to DuckDB ──
    print(f"\nStep 5: Writing to DuckDB ({DB_PATH})...")

    conn = duckdb.connect(DB_PATH)

    # Delete existing synthetic keyword/search term data
    print("  Deleting existing synthetic keyword data...")
    conn.execute(
        "DELETE FROM snap_keyword_daily WHERE customer_id = ?", [CUSTOMER_ID]
    )
    conn.execute(
        "DELETE FROM raw_keyword_daily WHERE customer_id = ?", [CUSTOMER_ID]
    )
    print("  Deleting existing synthetic search term data...")
    conn.execute(
        "DELETE FROM snap_search_term_daily WHERE customer_id = ?", [CUSTOMER_ID]
    )
    conn.execute(
        "DELETE FROM raw_search_term_daily WHERE customer_id = ?", [CUSTOMER_ID]
    )

    # Insert keyword rows in batches
    print(f"  Inserting {len(all_keyword_rows)} keyword rows...")
    KEYWORD_COLS = [
        "run_id", "ingested_at", "customer_id", "snapshot_date",
        "campaign_id", "campaign_name", "ad_group_id", "ad_group_name",
        "keyword_id", "keyword_text", "match_type", "status",
        "quality_score", "quality_score_creative", "quality_score_landing_page",
        "quality_score_relevance", "bid_micros", "first_page_cpc_micros",
        "top_of_page_cpc_micros", "impressions", "clicks", "cost_micros",
        "conversions", "conversions_value",
        "search_impression_share", "search_top_impression_share",
        "search_absolute_top_impression_share", "click_share",
    ]

    cols_sql = ", ".join(KEYWORD_COLS)
    qmarks = ", ".join(["?"] * len(KEYWORD_COLS))
    kw_sql = f"INSERT INTO snap_keyword_daily ({cols_sql}) VALUES ({qmarks});"

    batch_size = 5000
    for i in range(0, len(all_keyword_rows), batch_size):
        batch = all_keyword_rows[i : i + batch_size]
        tuples = [tuple(row.get(c) for c in KEYWORD_COLS) for row in batch]
        conn.executemany(kw_sql, tuples)

    # Insert search term rows in batches
    print(f"  Inserting {len(all_search_term_rows)} search term rows...")
    ST_COLS = [
        "run_id", "ingested_at", "customer_id", "snapshot_date",
        "campaign_id", "campaign_name", "ad_group_id", "ad_group_name",
        "keyword_id", "keyword_text", "search_term", "search_term_status",
        "match_type", "impressions", "clicks", "cost_micros",
        "conversions", "conversions_value",
    ]

    st_cols_sql = ", ".join(ST_COLS)
    st_qmarks = ", ".join(["?"] * len(ST_COLS))
    st_sql = f"INSERT INTO snap_search_term_daily ({st_cols_sql}) VALUES ({st_qmarks});"

    for i in range(0, len(all_search_term_rows), batch_size):
        batch = all_search_term_rows[i : i + batch_size]
        tuples = [tuple(row.get(c) for c in ST_COLS) for row in batch]
        conn.executemany(st_sql, tuples)

    conn.close()

    # ── Summary ──
    print()
    print("=" * 60)
    print("SYNTHETIC KEYWORD DATA GENERATION COMPLETE")
    print("=" * 60)
    print(f"  Keyword rows:      {len(all_keyword_rows)}")
    print(f"  Search term rows:  {len(all_search_term_rows)}")
    print(f"  Campaigns:         {len(CAMPAIGN_IDS)}")
    print(f"  Unique keywords:   {len(all_keyword_configs)}")
    print(f"  Unique search terms: {len(all_search_term_configs)}")
    print(f"  Date range:        {START_DATE} to {END_DATE}")
    print()
    print("Keyword scenarios:")
    for s, c in sorted(scenario_counts.items()):
        print(f"  {s:25s} {c:4d} keywords")
    print()
    print("Search term scenarios:")
    for s, c in sorted(st_scenario_counts.items()):
        print(f"  {s:25s} {c:4d} terms")
    print()
    print("NEXT STEPS:")
    print("  1. Run: .\\tools\\refresh_readonly.ps1")
    print("  2. Verify in DBeaver:")
    print("     SELECT COUNT(*) FROM analytics.keyword_daily;")
    print("     SELECT COUNT(*) FROM analytics.search_term_daily;")
    print()


if __name__ == "__main__":
    generate_all()
