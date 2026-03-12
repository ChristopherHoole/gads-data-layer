#!/usr/bin/env python3
"""
tools/seed_ad_daily.py

Drops and recreates analytics.ad_daily in warehouse.duckdb with synthetic
data covering 90 days, 15 ads across 3 campaigns and 6 ad groups.

Schema is extended to include ctr, roas, ad_strength, campaign_id,
campaign_name, ad_group_name — required by the recommendations engine.

Run from project root:
    python tools/seed_ad_daily.py
"""

import random
from datetime import date, timedelta
from pathlib import Path

import duckdb

random.seed(42)

WAREHOUSE_PATH = Path(__file__).parent.parent / "warehouse.duckdb"
CUSTOMER_ID = "9999999999"

# ── Campaign / ad-group / ad definitions ────────────────────────────────────

CAMPAIGNS = [
    {"campaign_id": 1001, "campaign_name": "Brand Search"},
    {"campaign_id": 1002, "campaign_name": "Non-Brand Search"},
    {"campaign_id": 1003, "campaign_name": "Competitor Targeting"},
]

AD_GROUPS = [
    {"ad_group_id": 2001, "ad_group_name": "Brand Core",         "campaign_id": 1001},
    {"ad_group_id": 2002, "ad_group_name": "Brand Products",     "campaign_id": 1001},
    {"ad_group_id": 2003, "ad_group_name": "Generic Keywords",   "campaign_id": 1002},
    {"ad_group_id": 2004, "ad_group_name": "Long Tail",          "campaign_id": 1002},
    {"ad_group_id": 2005, "ad_group_name": "Competitor A",       "campaign_id": 1003},
    {"ad_group_id": 2006, "ad_group_name": "Competitor B",       "campaign_id": 1003},
]

# ad_group_id → campaign lookup
AG_TO_CAMP = {ag["ad_group_id"]: ag["campaign_id"] for ag in AD_GROUPS}

ADS = [
    # Brand Core — 2 ads
    {"ad_id": 30001, "ad_name": "Brand Core RSA 1",      "ad_group_id": 2001, "ad_type": "RESPONSIVE_SEARCH_AD", "ad_strength": "EXCELLENT", "base_ctr": 0.085, "base_roas": 6.2,  "base_conv_rate": 0.045},
    {"ad_id": 30002, "ad_name": "Brand Core RSA 2",      "ad_group_id": 2001, "ad_type": "RESPONSIVE_SEARCH_AD", "ad_strength": "AVERAGE",   "base_ctr": 0.042, "base_roas": 3.1,  "base_conv_rate": 0.022},
    # Brand Products — 2 ads
    {"ad_id": 30003, "ad_name": "Brand Products RSA 1",  "ad_group_id": 2002, "ad_type": "RESPONSIVE_SEARCH_AD", "ad_strength": "GOOD",      "base_ctr": 0.071, "base_roas": 5.4,  "base_conv_rate": 0.038},
    {"ad_id": 30004, "ad_name": "Brand Products RSA 2",  "ad_group_id": 2002, "ad_type": "RESPONSIVE_SEARCH_AD", "ad_strength": "POOR",      "base_ctr": 0.008, "base_roas": 0.9,  "base_conv_rate": 0.005},
    # Generic Keywords — 3 ads
    {"ad_id": 30005, "ad_name": "Generic Main RSA",      "ad_group_id": 2003, "ad_type": "RESPONSIVE_SEARCH_AD", "ad_strength": "GOOD",      "base_ctr": 0.062, "base_roas": 4.1,  "base_conv_rate": 0.031},
    {"ad_id": 30006, "ad_name": "Generic Alt RSA",       "ad_group_id": 2003, "ad_type": "RESPONSIVE_SEARCH_AD", "ad_strength": "AVERAGE",   "base_ctr": 0.038, "base_roas": 1.7,  "base_conv_rate": 0.019},
    {"ad_id": 30007, "ad_name": "Generic Promo RSA",     "ad_group_id": 2003, "ad_type": "RESPONSIVE_SEARCH_AD", "ad_strength": "POOR",      "base_ctr": 0.006, "base_roas": 0.7,  "base_conv_rate": 0.004},
    # Long Tail — 3 ads
    {"ad_id": 30008, "ad_name": "Long Tail RSA 1",       "ad_group_id": 2004, "ad_type": "RESPONSIVE_SEARCH_AD", "ad_strength": "GOOD",      "base_ctr": 0.055, "base_roas": 3.8,  "base_conv_rate": 0.028},
    {"ad_id": 30009, "ad_name": "Long Tail RSA 2",       "ad_group_id": 2004, "ad_type": "RESPONSIVE_SEARCH_AD", "ad_strength": "EXCELLENT", "base_ctr": 0.079, "base_roas": 5.9,  "base_conv_rate": 0.041},
    {"ad_id": 30010, "ad_name": "Long Tail RSA 3",       "ad_group_id": 2004, "ad_type": "RESPONSIVE_SEARCH_AD", "ad_strength": "AVERAGE",   "base_ctr": 0.031, "base_roas": 1.3,  "base_conv_rate": 0.015},
    # Competitor A — 2 ads
    {"ad_id": 30011, "ad_name": "Competitor A RSA 1",    "ad_group_id": 2005, "ad_type": "RESPONSIVE_SEARCH_AD", "ad_strength": "GOOD",      "base_ctr": 0.048, "base_roas": 2.9,  "base_conv_rate": 0.024},
    {"ad_id": 30012, "ad_name": "Competitor A RSA 2",    "ad_group_id": 2005, "ad_type": "RESPONSIVE_SEARCH_AD", "ad_strength": "POOR",      "base_ctr": 0.005, "base_roas": 0.6,  "base_conv_rate": 0.003},
    # Competitor B — 3 ads
    {"ad_id": 30013, "ad_name": "Competitor B RSA 1",    "ad_group_id": 2006, "ad_type": "RESPONSIVE_SEARCH_AD", "ad_strength": "AVERAGE",   "base_ctr": 0.035, "base_roas": 1.8,  "base_conv_rate": 0.018},
    {"ad_id": 30014, "ad_name": "Competitor B RSA 2",    "ad_group_id": 2006, "ad_type": "RESPONSIVE_SEARCH_AD", "ad_strength": "GOOD",      "base_ctr": 0.058, "base_roas": 3.5,  "base_conv_rate": 0.029},
    {"ad_id": 30015, "ad_name": "Competitor B RSA 3",    "ad_group_id": 2006, "ad_type": "RESPONSIVE_SEARCH_AD", "ad_strength": "POOR",      "base_ctr": 0.007, "base_roas": 0.8,  "base_conv_rate": 0.004},
]

CREATE_SQL = """
CREATE TABLE analytics.ad_daily (
    customer_id                          VARCHAR,
    snapshot_date                        DATE,
    ad_id                                BIGINT,
    ad_name                              VARCHAR,
    ad_group_id                          BIGINT,
    ad_group_name                        VARCHAR,
    campaign_id                          BIGINT,
    campaign_name                        VARCHAR,
    ad_type                              VARCHAR,
    ad_status                            VARCHAR,
    ad_strength                          VARCHAR,
    impressions                          BIGINT,
    clicks                               BIGINT,
    cost_micros                          BIGINT,
    conversions                          DOUBLE,
    conversions_value                    DOUBLE,
    ctr                                  DOUBLE,
    cpc                                  DOUBLE,
    roas                                 DOUBLE,
    search_impression_share              DOUBLE,
    search_top_impression_share          DOUBLE,
    search_absolute_top_impression_share DOUBLE,
    click_share                          DOUBLE
)
"""

# ── Ad group & campaign lookup helpers ──────────────────────────────────────

def _ag_name(ag_id: int) -> str:
    for ag in AD_GROUPS:
        if ag["ad_group_id"] == ag_id:
            return ag["ad_group_name"]
    return "Unknown"


def _camp(ad_group_id: int) -> dict:
    camp_id = AG_TO_CAMP[ad_group_id]
    for c in CAMPAIGNS:
        if c["campaign_id"] == camp_id:
            return c
    return {"campaign_id": 0, "campaign_name": "Unknown"}


# ── Row generator ────────────────────────────────────────────────────────────

def _jitter(base: float, pct: float = 0.20) -> float:
    """Return base ± pct * base using a uniform random perturbation."""
    return base * (1 + random.uniform(-pct, pct))


def generate_rows(days: int = 90) -> list[tuple]:
    today = date.today()
    rows = []

    # Build ad_group/campaign lookup maps
    ag_name_map = {ag["ad_group_id"]: ag["ad_group_name"] for ag in AD_GROUPS}
    camp_map = {c["campaign_id"]: c["campaign_name"] for c in CAMPAIGNS}

    for ad in ADS:
        ad_id       = ad["ad_id"]
        ad_name     = ad["ad_name"]
        ag_id       = ad["ad_group_id"]
        ag_name     = ag_name_map[ag_id]
        camp_id     = AG_TO_CAMP[ag_id]
        camp_name   = camp_map[camp_id]
        ad_type     = ad["ad_type"]
        ad_strength = ad["ad_strength"]
        ad_status   = "PAUSED" if ad_strength == "POOR" else "ENABLED"

        base_ctr       = ad["base_ctr"]
        base_roas      = ad["base_roas"]
        base_conv_rate = ad["base_conv_rate"]

        # Base daily impressions — realistic scale for active account
        if camp_id == 1001:       # Brand — highest volume
            base_impressions = 25000
        elif camp_id == 1002:     # Non-brand — high volume
            base_impressions = 18000
        else:                     # Competitor — medium volume
            base_impressions = 10000

        for day_offset in range(days):
            snap_date = today - timedelta(days=days - day_offset - 1)

            impressions  = max(0, int(_jitter(base_impressions, 0.30)))
            ctr          = max(0.001, _jitter(base_ctr, 0.15))
            clicks       = max(0, round(impressions * ctr))
            avg_cpc      = max(0.10, _jitter(1.20, 0.25))   # £ per click
            cost         = round(clicks * avg_cpc, 2)
            cost_micros  = int(cost * 1_000_000)

            conv_rate    = max(0.001, _jitter(base_conv_rate, 0.20))
            conversions  = round(clicks * conv_rate, 2)
            roas         = _jitter(base_roas, 0.15) if cost > 0 else 0.0
            conv_value   = round(cost * roas, 2) if cost > 0 else 0.0
            cpc          = round(cost / clicks, 4) if clicks > 0 else 0.0

            # Impression share metrics (realistic synthetic values)
            search_is     = max(0.0, min(1.0, _jitter(0.62, 0.15)))
            search_top_is = max(0.0, min(search_is, _jitter(0.35, 0.15)))
            search_abs_is = max(0.0, min(search_top_is, _jitter(0.16, 0.20)))
            click_sh      = max(0.0, min(1.0, _jitter(0.42, 0.15)))

            rows.append((
                CUSTOMER_ID,
                snap_date,
                ad_id,
                ad_name,
                ag_id,
                ag_name,
                camp_id,
                camp_name,
                ad_type,
                ad_status,
                ad_strength,
                impressions,
                clicks,
                cost_micros,
                conversions,
                conv_value,
                round(ctr, 6),
                cpc,
                round(roas, 4),
                round(search_is, 4),
                round(search_top_is, 4),
                round(search_abs_is, 4),
                round(click_sh, 4),
            ))

    return rows


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("SEED: analytics.ad_daily -> warehouse.duckdb")
    print("=" * 70)

    conn = duckdb.connect(str(WAREHOUSE_PATH))

    # Drop existing table
    conn.execute("DROP TABLE IF EXISTS analytics.ad_daily")
    print("[seed] Dropped existing analytics.ad_daily (if any)")

    # Create fresh table
    conn.execute(CREATE_SQL)
    print("[seed] Created analytics.ad_daily")

    # Generate rows
    rows = generate_rows(days=90)
    print(f"[seed] Generated {len(rows):,} rows ({len(ADS)} ads × 90 days)")

    # Bulk insert
    conn.executemany("""
        INSERT INTO analytics.ad_daily VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
    """, rows)

    # Verify
    count = conn.execute("SELECT COUNT(*) FROM analytics.ad_daily").fetchone()[0]
    print(f"[seed] Rows inserted: {count:,}")

    ad_count = conn.execute("SELECT COUNT(DISTINCT ad_id) FROM analytics.ad_daily").fetchone()[0]
    print(f"[seed] Distinct ads: {ad_count}")

    date_range = conn.execute(
        "SELECT MIN(snapshot_date), MAX(snapshot_date) FROM analytics.ad_daily"
    ).fetchone()
    print(f"[seed] Date range: {date_range[0]} to {date_range[1]}")

    print("\n[seed] Ad strength distribution:")
    strengths = conn.execute("""
        SELECT ad_strength, COUNT(DISTINCT ad_id) AS ads
        FROM analytics.ad_daily
        GROUP BY ad_strength
        ORDER BY ad_strength
    """).fetchall()
    for s, c in strengths:
        print(f"  {s}: {c} ads")

    print("\n[seed] Sample metrics (latest snapshot per ad):")
    sample = conn.execute("""
        SELECT ad_name, ad_strength, ROUND(AVG(ctr),4) AS avg_ctr,
               ROUND(AVG(roas),2) AS avg_roas, ROUND(AVG(conversions),1) AS avg_conv
        FROM analytics.ad_daily
        GROUP BY ad_name, ad_strength
        ORDER BY ad_name
        LIMIT 5
    """).fetchall()
    for row in sample:
        print(f"  {row[0]} | {row[1]} | CTR={row[2]:.4f} | ROAS={row[3]:.2f} | Conv={row[4]:.1f}")

    conn.close()
    print("\n[seed] Done.")


if __name__ == "__main__":
    main()
