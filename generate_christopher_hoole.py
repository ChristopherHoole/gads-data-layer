"""
Generate 90 days of synthetic data for Christopher Hoole client
customer_id: 1254895944 | GBP | Lead gen | 4 campaigns

Tables generated:
  - analytics.campaign_daily
  - analytics.ad_group_daily
  - analytics.keyword_daily
  - analytics.ad_daily
  - analytics.search_term_daily

Run from project root: gads-data-layer
"""

import duckdb
import random
import uuid
from datetime import date, timedelta, datetime
from pathlib import Path

random.seed(42)

# ── Config ────────────────────────────────────────────────────────────────────
CUSTOMER_ID = "1254895944"
CLIENT_ID   = "client_christopher_hoole"
END_DATE    = date(2026, 3, 16)
START_DATE  = END_DATE - timedelta(days=89)
DAYS        = 90
CURRENCY    = "GBP"
INGESTED_AT = datetime(2026, 3, 16, 6, 0, 0)
RUN_ID      = str(uuid.uuid4())

print("=" * 70)
print("SYNTHETIC DATA GENERATOR — Christopher Hoole")
print("=" * 70)
print(f"  customer_id : {CUSTOMER_ID}")
print(f"  date range  : {START_DATE} → {END_DATE} ({DAYS} days)")
print(f"  currency    : {CURRENCY}")
print()

# ── Account structure ─────────────────────────────────────────────────────────
CAMPAIGNS = [
    {"id": 1001, "name": "Google Ads Specialist",      "strategy": "TARGET_ROAS",               "budget": 50, "target_roas": 3.0,  "target_cpa": None},
    {"id": 1002, "name": "PPC Freelancer",             "strategy": "MAXIMIZE_CLICKS",            "budget": 50, "target_roas": None, "target_cpa": None},
    {"id": 1003, "name": "Google Ads Consultant",      "strategy": "TARGET_CPA",                 "budget": 50, "target_roas": None, "target_cpa": 50.0},
    {"id": 1004, "name": "PPC Management Services",    "strategy": "MAXIMIZE_CONVERSION_VALUE",  "budget": 50, "target_roas": None, "target_cpa": None},
]

AD_GROUPS = {
    1001: [
        {"id": 2001, "name": "Google Ads Specialist UK"},
        {"id": 2002, "name": "Google Ads Expert London"},
        {"id": 2003, "name": "Certified Google Ads Specialist"},
        {"id": 2004, "name": "Google Ads Account Specialist"},
    ],
    1002: [
        {"id": 2005, "name": "PPC Freelancer UK"},
        {"id": 2006, "name": "Freelance Google Ads Manager"},
        {"id": 2007, "name": "Google Ads Freelancer London"},
        {"id": 2008, "name": "PPC Contractor Services"},
    ],
    1003: [
        {"id": 2009, "name": "Google Ads Consultant UK"},
        {"id": 2010, "name": "PPC Consultant London"},
        {"id": 2011, "name": "Google Ads Strategy Consultant"},
        {"id": 2012, "name": "Independent Google Ads Consultant"},
    ],
    1004: [
        {"id": 2013, "name": "Google Ads Management UK"},
        {"id": 2014, "name": "PPC Management Agency"},
        {"id": 2015, "name": "Google Ads Campaign Management"},
        {"id": 2016, "name": "Managed PPC Services"},
    ],
}

KEYWORDS_BY_AG = {
    2001: [
        ("google ads specialist", "EXACT"), ("google ads specialist uk", "EXACT"),
        ("hire google ads specialist", "BROAD"), ("google ads specialist near me", "BROAD"),
        ("google ads specialist london", "PHRASE"), ("certified google ads specialist", "EXACT"),
        ("google ads specialist freelancer", "PHRASE"), ("google ads specialist for hire", "BROAD"),
        ("google ads specialist services", "PHRASE"), ("google ads specialist rates", "BROAD"),
        ("google ads account specialist", "EXACT"), ("google ads campaign specialist", "PHRASE"),
        ("specialist google ads management", "BROAD"), ("google ads ppc specialist", "EXACT"),
        ("google ads specialist uk prices", "BROAD"), ("independent google ads specialist", "PHRASE"),
        ("google ads specialist help", "BROAD"), ("google ads specialist cost", "BROAD"),
        ("google ads expert specialist", "PHRASE"), ("local google ads specialist", "BROAD"),
    ],
    2002: [
        ("google ads expert", "EXACT"), ("google ads expert uk", "EXACT"),
        ("google ads expert london", "PHRASE"), ("hire google ads expert", "BROAD"),
        ("google ads expert freelancer", "PHRASE"), ("google ads expert help", "BROAD"),
        ("adwords expert uk", "EXACT"), ("ppc expert uk", "EXACT"),
        ("google ads expert near me", "BROAD"), ("certified google ads expert", "EXACT"),
        ("google ads expert rates", "BROAD"), ("google ads expert cost", "BROAD"),
        ("best google ads expert uk", "BROAD"), ("google ads expert services", "PHRASE"),
        ("google ads expert for small business", "BROAD"), ("google ads expert london price", "BROAD"),
        ("experienced google ads expert", "PHRASE"), ("google ads management expert", "BROAD"),
        ("google ads expert review", "BROAD"), ("top google ads expert", "BROAD"),
    ],
    2003: [
        ("certified google ads professional", "EXACT"), ("google ads certified", "EXACT"),
        ("google ads certification", "BROAD"), ("google partner certified", "PHRASE"),
        ("google ads certified specialist", "EXACT"), ("certified ppc specialist", "EXACT"),
        ("google ads professional uk", "EXACT"), ("google ads professional services", "PHRASE"),
        ("certified adwords professional", "EXACT"), ("google ads qualified specialist", "PHRASE"),
        ("google ads certification uk", "BROAD"), ("google ads professional rates", "BROAD"),
        ("google ads professional freelancer", "PHRASE"), ("certified google ads manager", "EXACT"),
        ("google ads professional help", "BROAD"), ("hire certified google ads specialist", "BROAD"),
        ("google ads professional cost", "BROAD"), ("certified ppc professional", "EXACT"),
        ("google ads certified professional uk", "EXACT"), ("google ads badge holder", "BROAD"),
    ],
    2004: [
        ("google ads account manager", "EXACT"), ("google ads account management", "EXACT"),
        ("google ads account specialist uk", "PHRASE"), ("google ads account help", "BROAD"),
        ("manage google ads account", "BROAD"), ("google ads account optimisation", "PHRASE"),
        ("google ads account setup", "BROAD"), ("google ads account review", "BROAD"),
        ("google ads account audit", "EXACT"), ("google ads account management uk", "EXACT"),
        ("google ads account manager freelance", "PHRASE"), ("google ads account manager rates", "BROAD"),
        ("google ads account manager cost", "BROAD"), ("google ads account manager london", "PHRASE"),
        ("outsource google ads management", "BROAD"), ("google ads account manager hire", "BROAD"),
        ("google ads account management services", "PHRASE"), ("google ads account health", "BROAD"),
        ("google ads account performance", "BROAD"), ("google ads account management price", "BROAD"),
    ],
    2005: [
        ("ppc freelancer uk", "EXACT"), ("freelance ppc manager", "EXACT"),
        ("ppc freelancer london", "PHRASE"), ("hire ppc freelancer", "BROAD"),
        ("ppc freelancer rates", "BROAD"), ("ppc freelancer cost", "BROAD"),
        ("freelance ppc specialist", "EXACT"), ("ppc freelancer near me", "BROAD"),
        ("ppc freelancer services", "PHRASE"), ("ppc freelancer help", "BROAD"),
        ("freelance paid search specialist", "EXACT"), ("freelance ppc consultant", "EXACT"),
        ("ppc freelancer day rate", "BROAD"), ("ppc freelancer hourly rate", "BROAD"),
        ("freelance ppc manager uk", "EXACT"), ("ppc freelancer for hire", "BROAD"),
        ("freelance ppc expert", "EXACT"), ("ppc freelancer portfolio", "BROAD"),
        ("best ppc freelancer uk", "BROAD"), ("ppc freelancer review", "BROAD"),
    ],
    2006: [
        ("freelance google ads manager", "EXACT"), ("google ads manager freelance", "PHRASE"),
        ("hire freelance google ads manager", "BROAD"), ("freelance google ads manager uk", "EXACT"),
        ("freelance google ads manager rates", "BROAD"), ("freelance google ads manager london", "PHRASE"),
        ("freelance google ads manager cost", "BROAD"), ("freelance adwords manager", "EXACT"),
        ("freelance google ads management", "PHRASE"), ("freelance google ads manager help", "BROAD"),
        ("google ads manager for hire", "BROAD"), ("freelance campaign manager google ads", "PHRASE"),
        ("part time google ads manager", "BROAD"), ("remote google ads manager", "BROAD"),
        ("freelance google ads manager services", "PHRASE"), ("google ads manager freelancer uk", "EXACT"),
        ("freelance sem manager", "EXACT"), ("freelance paid media manager", "EXACT"),
        ("google ads manager contract", "BROAD"), ("google ads manager day rate", "BROAD"),
    ],
    2007: [
        ("google ads freelancer", "EXACT"), ("google ads freelancer uk", "EXACT"),
        ("google ads freelancer london", "PHRASE"), ("hire google ads freelancer", "BROAD"),
        ("google ads freelancer rates", "BROAD"), ("google ads freelancer cost", "BROAD"),
        ("google ads freelancer near me", "BROAD"), ("google ads freelancer services", "PHRASE"),
        ("google ads freelancer help", "BROAD"), ("best google ads freelancer", "BROAD"),
        ("google ads freelancer hourly rate", "BROAD"), ("google ads freelancer day rate", "BROAD"),
        ("experienced google ads freelancer", "PHRASE"), ("google ads freelancer for small business", "BROAD"),
        ("affordable google ads freelancer", "BROAD"), ("google ads freelancer portfolio", "BROAD"),
        ("google ads freelancer review", "BROAD"), ("google ads freelancer testimonials", "BROAD"),
        ("trusted google ads freelancer uk", "PHRASE"), ("google ads freelancer contract", "BROAD"),
    ],
    2008: [
        ("ppc contractor uk", "EXACT"), ("google ads contractor", "EXACT"),
        ("ppc contractor services", "PHRASE"), ("hire ppc contractor", "BROAD"),
        ("ppc contractor rates", "BROAD"), ("ppc contractor day rate", "BROAD"),
        ("google ads contractor uk", "PHRASE"), ("ppc contractor london", "PHRASE"),
        ("paid search contractor", "EXACT"), ("ppc contractor for hire", "BROAD"),
        ("google ads contract work", "BROAD"), ("ppc contract specialist", "EXACT"),
        ("google ads contractor services", "PHRASE"), ("ppc contractor cost", "BROAD"),
        ("remote ppc contractor", "BROAD"), ("ppc contractor help", "BROAD"),
        ("google ads interim manager", "EXACT"), ("ppc interim specialist", "EXACT"),
        ("paid media contractor uk", "EXACT"), ("sem contractor uk", "EXACT"),
    ],
    2009: [
        ("google ads consultant", "EXACT"), ("google ads consultant uk", "EXACT"),
        ("google ads consultant london", "PHRASE"), ("hire google ads consultant", "BROAD"),
        ("google ads consultant rates", "BROAD"), ("google ads consultant cost", "BROAD"),
        ("google ads consultant near me", "BROAD"), ("google ads consultant services", "PHRASE"),
        ("google ads consultant help", "BROAD"), ("best google ads consultant", "BROAD"),
        ("independent google ads consultant", "EXACT"), ("google ads consultant review", "BROAD"),
        ("google ads consultant hourly rate", "BROAD"), ("google ads consultant day rate", "BROAD"),
        ("experienced google ads consultant", "PHRASE"), ("google ads strategy consultant", "EXACT"),
        ("google ads consultant for small business", "BROAD"), ("affordable google ads consultant", "BROAD"),
        ("google ads audit consultant", "PHRASE"), ("google ads consultant testimonials", "BROAD"),
    ],
    2010: [
        ("ppc consultant uk", "EXACT"), ("ppc consultant london", "PHRASE"),
        ("hire ppc consultant", "BROAD"), ("ppc consultant rates", "BROAD"),
        ("ppc consultant cost", "BROAD"), ("ppc consultant near me", "BROAD"),
        ("ppc consultant services", "PHRASE"), ("ppc consultant help", "BROAD"),
        ("best ppc consultant uk", "BROAD"), ("independent ppc consultant", "EXACT"),
        ("ppc consultant review", "BROAD"), ("ppc consultant hourly rate", "BROAD"),
        ("ppc consultant day rate", "BROAD"), ("experienced ppc consultant", "PHRASE"),
        ("ppc strategy consultant", "EXACT"), ("ppc consultant for small business", "BROAD"),
        ("affordable ppc consultant", "BROAD"), ("paid search consultant uk", "EXACT"),
        ("adwords consultant uk", "EXACT"), ("sem consultant uk", "EXACT"),
    ],
    2011: [
        ("google ads strategy", "EXACT"), ("google ads strategy consultant", "EXACT"),
        ("google ads strategy uk", "PHRASE"), ("google ads strategy help", "BROAD"),
        ("google ads growth strategy", "BROAD"), ("google ads campaign strategy", "PHRASE"),
        ("google ads bidding strategy", "BROAD"), ("google ads account strategy", "PHRASE"),
        ("ppc strategy uk", "EXACT"), ("ppc strategy consultant uk", "EXACT"),
        ("paid search strategy", "EXACT"), ("google ads strategic consultant", "PHRASE"),
        ("google ads strategy review", "BROAD"), ("google ads strategy audit", "BROAD"),
        ("google ads planning consultant", "PHRASE"), ("google ads performance strategy", "BROAD"),
        ("google ads optimisation strategy", "PHRASE"), ("google ads scaling strategy", "BROAD"),
        ("google ads strategy services", "PHRASE"), ("google ads strategy cost", "BROAD"),
    ],
    2012: [
        ("independent google ads consultant", "EXACT"), ("google ads independent consultant", "PHRASE"),
        ("freelance google ads consultant", "EXACT"), ("google ads consultant freelance", "PHRASE"),
        ("self employed google ads consultant", "BROAD"), ("google ads consultant sole trader", "BROAD"),
        ("google ads consultant no agency", "BROAD"), ("direct google ads consultant", "BROAD"),
        ("google ads consultant personal service", "BROAD"), ("boutique google ads consultant", "BROAD"),
        ("google ads consultant one person", "BROAD"), ("google ads consultant owner managed", "BROAD"),
        ("google ads consultant not agency", "BROAD"), ("google ads consultant dedicated", "BROAD"),
        ("google ads personal consultant", "PHRASE"), ("google ads consultant bespoke", "BROAD"),
        ("google ads consultant hands on", "BROAD"), ("google ads consultant tailored", "BROAD"),
        ("google ads consultant small business specialist", "BROAD"), ("google ads consultant uk based", "BROAD"),
    ],
    2013: [
        ("google ads management", "EXACT"), ("google ads management uk", "EXACT"),
        ("google ads management services", "PHRASE"), ("google ads management london", "PHRASE"),
        ("google ads management cost", "BROAD"), ("google ads management rates", "BROAD"),
        ("google ads management near me", "BROAD"), ("google ads management help", "BROAD"),
        ("outsource google ads", "BROAD"), ("google ads managed service", "EXACT"),
        ("google ads management company uk", "PHRASE"), ("google ads management pricing", "BROAD"),
        ("google ads management packages", "BROAD"), ("monthly google ads management", "PHRASE"),
        ("google ads management for small business", "BROAD"), ("google ads management agency alternative", "BROAD"),
        ("google ads management freelancer", "PHRASE"), ("professional google ads management", "PHRASE"),
        ("google ads management review", "BROAD"), ("google ads management testimonials", "BROAD"),
    ],
    2014: [
        ("ppc management uk", "EXACT"), ("ppc management agency", "EXACT"),
        ("ppc management services uk", "PHRASE"), ("ppc management london", "PHRASE"),
        ("ppc management cost", "BROAD"), ("ppc management rates", "BROAD"),
        ("ppc management near me", "BROAD"), ("ppc management help", "BROAD"),
        ("ppc management company uk", "PHRASE"), ("ppc management pricing", "BROAD"),
        ("ppc management packages", "BROAD"), ("monthly ppc management", "PHRASE"),
        ("ppc management for small business", "BROAD"), ("ppc management freelancer", "PHRASE"),
        ("professional ppc management", "PHRASE"), ("ppc management review", "BROAD"),
        ("outsource ppc management", "BROAD"), ("ppc managed service uk", "EXACT"),
        ("adwords management uk", "EXACT"), ("paid search management uk", "EXACT"),
    ],
    2015: [
        ("google ads campaign management", "EXACT"), ("google ads campaign management uk", "PHRASE"),
        ("manage google ads campaigns", "BROAD"), ("google ads campaign management services", "PHRASE"),
        ("google ads campaign manager uk", "EXACT"), ("google ads campaign management cost", "BROAD"),
        ("google ads campaign management rates", "BROAD"), ("google ads campaign optimisation", "PHRASE"),
        ("google ads campaign management london", "PHRASE"), ("google ads campaign management help", "BROAD"),
        ("google ads campaign setup and management", "PHRASE"), ("google ads campaign management pricing", "BROAD"),
        ("google ads campaign management packages", "BROAD"), ("google ads campaign management freelancer", "PHRASE"),
        ("professional google ads campaign management", "PHRASE"), ("google ads campaign management review", "BROAD"),
        ("google ads campaign management company", "BROAD"), ("google ads campaign management agency", "BROAD"),
        ("google ads search campaign management", "PHRASE"), ("google ads campaign management monthly", "BROAD"),
    ],
    2016: [
        ("managed ppc services", "EXACT"), ("managed ppc uk", "EXACT"),
        ("managed google ads", "EXACT"), ("managed google ads uk", "PHRASE"),
        ("managed ppc services uk", "PHRASE"), ("managed ppc london", "PHRASE"),
        ("managed ppc cost", "BROAD"), ("managed ppc rates", "BROAD"),
        ("managed google ads services", "PHRASE"), ("managed ppc help", "BROAD"),
        ("managed paid search uk", "EXACT"), ("managed ppc pricing", "BROAD"),
        ("managed ppc packages", "BROAD"), ("managed ppc for small business", "BROAD"),
        ("managed ppc freelancer", "PHRASE"), ("professional managed ppc", "PHRASE"),
        ("managed ppc review", "BROAD"), ("fully managed google ads", "PHRASE"),
        ("fully managed ppc uk", "PHRASE"), ("managed adwords uk", "EXACT"),
    ],
}

SEARCH_TERMS_BY_AG = {
    2001: ["google ads specialist uk", "hire a google ads specialist", "google ads specialist london price",
           "google ads specialist freelance uk", "certified google ads specialist near me"],
    2002: ["google ads expert uk freelance", "best google ads expert london", "hire google ads expert uk",
           "google ads expert hourly rate uk", "ppc expert freelancer uk"],
    2003: ["google ads certified professional uk", "hire certified google ads", "google partner certified uk",
           "certified ppc specialist uk", "google ads qualified professional"],
    2004: ["google ads account manager hire", "freelance google ads account manager uk", "google ads account audit uk",
           "google ads account management freelance", "google ads account specialist london"],
    2005: ["ppc freelancer uk rates", "hire ppc freelancer uk", "freelance ppc specialist uk",
           "ppc freelancer day rate uk", "best ppc freelancer london"],
    2006: ["freelance google ads manager uk", "google ads manager freelance london", "hire freelance google ads manager",
           "freelance google ads manager day rate", "google ads manager contract uk"],
    2007: ["google ads freelancer uk rates", "google ads freelancer london", "hire google ads freelancer uk",
           "google ads freelancer hourly rate", "experienced google ads freelancer uk"],
    2008: ["ppc contractor uk rates", "google ads contractor uk", "hire ppc contractor",
           "paid search contractor uk", "ppc interim specialist uk"],
    2009: ["google ads consultant uk rates", "hire google ads consultant london", "google ads consultant freelance uk",
           "google ads consultant day rate", "independent google ads consultant uk"],
    2010: ["ppc consultant uk rates", "hire ppc consultant london", "freelance ppc consultant uk",
           "ppc consultant day rate uk", "paid search consultant uk rates"],
    2011: ["google ads strategy consultant uk", "ppc strategy consultant london", "google ads strategic consultant",
           "google ads growth strategy uk", "paid search strategy consultant"],
    2012: ["independent google ads consultant uk", "freelance google ads consultant uk",
           "google ads consultant no agency", "personal google ads consultant uk", "direct google ads consultant"],
    2013: ["google ads management uk cost", "outsource google ads uk", "google ads managed service uk",
           "google ads management freelancer uk", "professional google ads management uk"],
    2014: ["ppc management uk cost", "outsource ppc uk", "ppc managed service uk",
           "ppc management freelancer uk", "professional ppc management uk"],
    2015: ["google ads campaign management uk cost", "manage google ads campaigns uk",
           "google ads campaign manager freelance", "google ads campaign optimisation uk",
           "professional google ads campaign management"],
    2016: ["managed google ads uk cost", "fully managed ppc uk", "managed ppc freelancer uk",
           "professional managed ppc uk", "managed google ads services uk"],
}

# ── Performance profiles (deliberately varied to trigger rules) ───────────────
# Campaign performance multipliers — some strong, some weak, to trigger recommendations
CAMP_PERF = {
    1001: {"imp_base": 800,  "ctr": 0.045, "cpc": 5.50, "cvr": 0.032, "conv_val": 0,   "is": 0.62, "notes": "strong ROAS — triggers increase budget"},
    1002: {"imp_base": 1200, "ctr": 0.038, "cpc": 3.20, "cvr": 0.018, "conv_val": 0,   "is": 0.45, "notes": "clicks focused, moderate performance"},
    1003: {"imp_base": 600,  "ctr": 0.055, "cpc": 6.80, "cvr": 0.041, "conv_val": 0,   "is": 0.71, "notes": "strong CPA — triggers tighten"},
    1004: {"imp_base": 900,  "ctr": 0.042, "cpc": 4.10, "cvr": 0.025, "conv_val": 0,   "is": 0.58, "notes": "moderate, mixed signals"},
}

# ── Connect ───────────────────────────────────────────────────────────────────
db_path = Path('warehouse.duckdb')
conn = duckdb.connect(str(db_path))

def delete_existing():
    print(f"Dropping and recreating analytics tables for customer {CUSTOMER_ID}...")
    tables = ['campaign_daily','ad_group_daily','keyword_daily','ad_daily','search_term_daily']
    for t in tables:
        try:
            # Check if view or table
            result = conn.execute(
                "SELECT table_type FROM information_schema.tables "
                "WHERE table_schema = 'analytics' AND table_name = ?", [t]
            ).fetchone()
            if result:
                if result[0] == 'VIEW':
                    conn.execute(f"DROP VIEW analytics.{t}")
                    print(f"  Dropped VIEW analytics.{t}")
                else:
                    conn.execute(f"DELETE FROM analytics.{t} WHERE customer_id = ?", [CUSTOMER_ID])
                    print(f"  Cleared analytics.{t}")
            else:
                print(f"  analytics.{t} does not exist yet — will create")
        except Exception as e:
            print(f"  analytics.{t} — {e}")

def weekend_factor(d):
    return 0.65 if d.weekday() in (5, 6) else 1.0

def day_variance():
    return random.uniform(0.82, 1.18)

# ─────────────────────────────────────────────────────────────────────────────
# 1. CAMPAIGN_DAILY
# ─────────────────────────────────────────────────────────────────────────────
def generate_campaign_daily():
    print("\n[1/5] Generating campaign_daily...")
    rows = []
    for camp in CAMPAIGNS:
        p = CAMP_PERF[camp["id"]]
        for day_offset in range(DAYS):
            d = START_DATE + timedelta(days=day_offset)
            wf = weekend_factor(d)
            dv = day_variance()
            imps = int(p["imp_base"] * wf * dv)
            clicks = int(imps * p["ctr"] * random.uniform(0.9, 1.1))
            cost_micros = int(clicks * p["cpc"] * 1_000_000 * random.uniform(0.92, 1.08))
            convs = round(clicks * p["cvr"] * random.uniform(0.85, 1.15), 2)
            conv_val = round(convs * random.uniform(80, 200), 2)  # lead value estimate
            is_ = round(min(p["is"] * random.uniform(0.88, 1.12), 1.0), 4)
            is_top = round(is_ * random.uniform(0.55, 0.75), 4)
            is_abs = round(is_top * random.uniform(0.35, 0.55), 4)
            cs = round(min(is_ * random.uniform(0.82, 1.05), 1.0), 4)
            rows.append((
                RUN_ID, INGESTED_AT, CUSTOMER_ID, d.isoformat(),
                str(camp["id"]), camp["name"], "ENABLED", "SEARCH",
                imps, clicks, cost_micros,
                convs, conv_val, round(convs*1.05,2), round(conv_val*1.05,2),
                is_, is_top, is_abs, cs,
                round(random.uniform(0.55, 0.85), 2),
                camp["strategy"],
            ))
    conn.execute("""
        CREATE OR REPLACE TABLE analytics.campaign_daily (
            run_id VARCHAR, ingested_at TIMESTAMP, customer_id VARCHAR,
            snapshot_date DATE, campaign_id VARCHAR, campaign_name VARCHAR,
            campaign_status VARCHAR, channel_type VARCHAR,
            impressions BIGINT, clicks BIGINT, cost_micros BIGINT,
            conversions DOUBLE, conversions_value DOUBLE,
            all_conversions DOUBLE, all_conversions_value DOUBLE,
            search_impression_share DOUBLE, search_top_impression_share DOUBLE,
            search_absolute_top_impression_share DOUBLE, click_share DOUBLE,
            optimization_score DOUBLE, bid_strategy_type VARCHAR
        )
    """)
    conn.executemany("INSERT INTO analytics.campaign_daily VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", rows)
    print(f"  Inserted {len(rows):,} rows")

# ─────────────────────────────────────────────────────────────────────────────
# 2. AD_GROUP_DAILY
# ─────────────────────────────────────────────────────────────────────────────
def generate_ad_group_daily():
    print("\n[2/5] Generating ad_group_daily...")
    rows = []
    for camp in CAMPAIGNS:
        p = CAMP_PERF[camp["id"]]
        ags = AD_GROUPS[camp["id"]]
        for ag in ags:
            ag_mult = random.uniform(0.7, 1.3)
            for day_offset in range(DAYS):
                d = START_DATE + timedelta(days=day_offset)
                wf = weekend_factor(d)
                dv = day_variance()
                imps = int(p["imp_base"] * ag_mult * wf * dv / 4)
                clicks = max(0, int(imps * p["ctr"] * random.uniform(0.9, 1.1)))
                cost_micros = int(clicks * p["cpc"] * 1_000_000 * random.uniform(0.92, 1.08))
                cost = round(cost_micros / 1_000_000, 4)
                convs = round(clicks * p["cvr"] * random.uniform(0.85, 1.15), 2)
                conv_val = round(convs * random.uniform(80, 200), 2)
                ctr = round(clicks / imps, 4) if imps > 0 else 0.0
                cpc = round(cost / clicks, 4) if clicks > 0 else 0.0
                cpa = round(cost / convs, 2) if convs > 0 else 0.0
                roas = round(conv_val / cost, 4) if cost > 0 else 0.0
                is_ = round(min(p["is"] * random.uniform(0.85, 1.15), 1.0), 4)
                is_top = round(is_ * random.uniform(0.55, 0.75), 4)
                is_abs = round(is_top * random.uniform(0.35, 0.55), 4)
                cs = round(min(is_ * random.uniform(0.82, 1.05), 1.0), 4)
                bid_micros = int(p["cpc"] * 1_000_000 * random.uniform(0.8, 1.2))
                tcpa_micros = int(camp["target_cpa"] * 1_000_000) if camp["target_cpa"] else 0
                rows.append((
                    RUN_ID, INGESTED_AT, CUSTOMER_ID, d.isoformat(),
                    camp["id"], camp["name"],
                    ag["id"], ag["name"],
                    "ENABLED", bid_micros, tcpa_micros,
                    imps, clicks, cost_micros, cost,
                    convs, conv_val, ctr, cpc, roas, cpa,
                    is_, is_top, is_abs, cs,
                    "SEARCH_STANDARD",
                    round(convs*1.05,2), round(conv_val*1.05,2),
                    round(random.uniform(0.55, 0.85), 2),
                    camp["strategy"],
                ))
    conn.execute("""
        CREATE OR REPLACE TABLE analytics.ad_group_daily (
            run_id VARCHAR, ingested_at TIMESTAMP, customer_id VARCHAR,
            snapshot_date DATE, campaign_id BIGINT, campaign_name VARCHAR,
            ad_group_id BIGINT, ad_group_name VARCHAR,
            ad_group_status VARCHAR, cpc_bid_micros BIGINT, target_cpa_micros BIGINT,
            impressions BIGINT, clicks BIGINT, cost_micros BIGINT, cost DOUBLE,
            conversions DOUBLE, conversions_value DOUBLE,
            ctr DOUBLE, cpc DOUBLE, roas DOUBLE, cpa DOUBLE,
            search_impression_share DOUBLE, search_top_impression_share DOUBLE,
            search_absolute_top_impression_share DOUBLE, click_share DOUBLE,
            ad_group_type VARCHAR, all_conversions DOUBLE, all_conversions_value DOUBLE,
            optimization_score DOUBLE, bid_strategy_type VARCHAR
        )
    """)
    conn.executemany("INSERT INTO analytics.ad_group_daily VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", rows)
    print(f"  Inserted {len(rows):,} rows")

# ─────────────────────────────────────────────────────────────────────────────
# 3. KEYWORD_DAILY
# ─────────────────────────────────────────────────────────────────────────────
def generate_keyword_daily():
    print("\n[3/5] Generating keyword_daily...")
    rows = []
    kw_id = 3001
    for camp in CAMPAIGNS:
        p = CAMP_PERF[camp["id"]]
        for ag in AD_GROUPS[camp["id"]]:
            kws = KEYWORDS_BY_AG[ag["id"]]
            for kw_text, match_type in kws:
                # Some keywords deliberately weak to trigger recommendations
                is_weak = random.random() < 0.15  # 15% of keywords are weak
                is_high_cost_no_conv = random.random() < 0.10  # 10% high cost, 0 conv
                qs = random.randint(2, 4) if is_weak else random.randint(5, 10)
                kw_mult = random.uniform(0.3, 0.7) if is_weak else random.uniform(0.8, 1.4)
                bid_micros = int(p["cpc"] * 1_000_000 * random.uniform(0.7, 1.3))
                for day_offset in range(DAYS):
                    d = START_DATE + timedelta(days=day_offset)
                    wf = weekend_factor(d)
                    dv = day_variance()
                    imps = max(0, int(p["imp_base"] * kw_mult * wf * dv / 20))
                    clicks = max(0, int(imps * p["ctr"] * random.uniform(0.85, 1.15)))
                    cost_micros = int(clicks * p["cpc"] * 1_000_000 * random.uniform(0.9, 1.1))
                    cost = round(cost_micros / 1_000_000, 4)
                    if is_high_cost_no_conv:
                        convs = 0.0
                    else:
                        convs = round(clicks * p["cvr"] * random.uniform(0.7, 1.3), 2) if not is_weak else round(clicks * p["cvr"] * 0.3, 2)
                    conv_val = round(convs * random.uniform(80, 200), 2)
                    ctr = round(clicks / imps, 4) if imps > 0 else 0.0
                    cpc = round(cost / clicks, 4) if clicks > 0 else 0.0
                    cpa = round(cost / convs, 2) if convs > 0 else 0.0
                    roas = round(conv_val / cost, 4) if cost > 0 else 0.0
                    is_ = round(min(p["is"] * kw_mult * random.uniform(0.8, 1.2), 1.0), 4)
                    is_top = round(is_ * random.uniform(0.5, 0.7), 4)
                    is_abs = round(is_top * random.uniform(0.3, 0.5), 4)
                    cs = round(min(is_ * random.uniform(0.8, 1.1), 1.0), 4)
                    rows.append((
                        RUN_ID, INGESTED_AT, CUSTOMER_ID, d.isoformat(),
                        camp["id"], camp["name"],
                        ag["id"], ag["name"],
                        kw_id, kw_text, match_type,
                        "ENABLED", qs,
                        max(1, qs + random.randint(-1,1)),
                        max(1, qs + random.randint(-1,1)),
                        max(1, qs + random.randint(-1,1)),
                        bid_micros,
                        int(bid_micros * 1.1),
                        int(bid_micros * 1.3),
                        imps, clicks, cost_micros, cost,
                        convs, conv_val, ctr, cpc, roas, cpa,
                        is_, is_top, is_abs, cs,
                    ))
                kw_id += 1
    conn.execute("""
        CREATE OR REPLACE TABLE analytics.keyword_daily (
            run_id VARCHAR, ingested_at TIMESTAMP, customer_id VARCHAR,
            snapshot_date DATE, campaign_id BIGINT, campaign_name VARCHAR,
            ad_group_id BIGINT, ad_group_name VARCHAR,
            keyword_id BIGINT, keyword_text VARCHAR, match_type VARCHAR,
            status VARCHAR, quality_score INTEGER,
            quality_score_creative INTEGER, quality_score_landing_page INTEGER,
            quality_score_relevance INTEGER,
            bid_micros BIGINT, first_page_cpc_micros BIGINT, top_of_page_cpc_micros BIGINT,
            impressions BIGINT, clicks BIGINT, cost_micros BIGINT, cost DOUBLE,
            conversions DOUBLE, conversions_value DOUBLE,
            ctr DOUBLE, cpc DOUBLE, roas DOUBLE, cpa DOUBLE,
            search_impression_share DOUBLE, search_top_impression_share DOUBLE,
            search_absolute_top_impression_share DOUBLE, click_share DOUBLE
        )
    """)
    conn.executemany("INSERT INTO analytics.keyword_daily VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", rows)
    print(f"  Inserted {len(rows):,} rows  ({kw_id - 3001} unique keywords)")

# ─────────────────────────────────────────────────────────────────────────────
# 4. AD_DAILY
# ─────────────────────────────────────────────────────────────────────────────
def generate_ad_daily():
    print("\n[4/5] Generating ad_daily...")
    AD_TYPES = ["RESPONSIVE_SEARCH_AD", "RESPONSIVE_SEARCH_AD", "EXPANDED_TEXT_AD"]
    AD_STRENGTHS = ["EXCELLENT", "GOOD", "AVERAGE", "POOR"]
    rows = []
    ad_id = 5001
    for camp in CAMPAIGNS:
        p = CAMP_PERF[camp["id"]]
        for ag in AD_GROUPS[camp["id"]]:
            for i in range(3):  # 3 ads per ad group
                ad_type = AD_TYPES[i]
                ad_strength = random.choice(AD_STRENGTHS[:3] if i < 2 else AD_STRENGTHS)
                ad_mult = random.uniform(0.7, 1.3)
                for day_offset in range(DAYS):
                    d = START_DATE + timedelta(days=day_offset)
                    wf = weekend_factor(d)
                    dv = day_variance()
                    imps = max(0, int(p["imp_base"] * ad_mult * wf * dv / 12))
                    clicks = max(0, int(imps * p["ctr"] * random.uniform(0.88, 1.12)))
                    cost_micros = int(clicks * p["cpc"] * 1_000_000 * random.uniform(0.9, 1.1))
                    convs = round(clicks * p["cvr"] * random.uniform(0.8, 1.2), 2)
                    conv_val = round(convs * random.uniform(80, 200), 2)
                    ctr = round(clicks / imps, 4) if imps > 0 else 0.0
                    cpc = round(cost_micros / 1_000_000 / clicks, 4) if clicks > 0 else 0.0
                    roas = round(conv_val / (cost_micros/1_000_000), 4) if cost_micros > 0 else 0.0
                    is_ = round(min(p["is"] * ad_mult * random.uniform(0.85, 1.15), 1.0), 4)
                    is_top = round(is_ * random.uniform(0.5, 0.7), 4)
                    is_abs = round(is_top * random.uniform(0.3, 0.5), 4)
                    cs = round(min(is_ * random.uniform(0.82, 1.05), 1.0), 4)
                    rows.append((
                        CUSTOMER_ID, d.isoformat(),
                        ad_id, f"Ad {i+1} — {ag['name'][:30]}",
                        ag["id"], ag["name"],
                        camp["id"], camp["name"],
                        ad_type, "ENABLED", ad_strength,
                        imps, clicks, cost_micros,
                        convs, conv_val, ctr, cpc, roas,
                        is_, is_top, is_abs, cs,
                    ))
                ad_id += 1
    conn.execute("""
        CREATE OR REPLACE TABLE analytics.ad_daily (
            customer_id VARCHAR, snapshot_date DATE,
            ad_id BIGINT, ad_name VARCHAR,
            ad_group_id BIGINT, ad_group_name VARCHAR,
            campaign_id BIGINT, campaign_name VARCHAR,
            ad_type VARCHAR, ad_status VARCHAR, ad_strength VARCHAR,
            impressions BIGINT, clicks BIGINT, cost_micros BIGINT,
            conversions DOUBLE, conversions_value DOUBLE,
            ctr DOUBLE, cpc DOUBLE, roas DOUBLE,
            search_impression_share DOUBLE, search_top_impression_share DOUBLE,
            search_absolute_top_impression_share DOUBLE, click_share DOUBLE
        )
    """)
    conn.executemany("INSERT INTO analytics.ad_daily VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", rows)
    print(f"  Inserted {len(rows):,} rows  ({ad_id - 5001} unique ads)")

# ─────────────────────────────────────────────────────────────────────────────
# 5. SEARCH_TERM_DAILY
# ─────────────────────────────────────────────────────────────────────────────
def generate_search_term_daily():
    print("\n[5/5] Generating search_term_daily...")
    rows = []
    kw_id = 3001
    for camp in CAMPAIGNS:
        p = CAMP_PERF[camp["id"]]
        for ag in AD_GROUPS[camp["id"]]:
            search_terms = SEARCH_TERMS_BY_AG[ag["id"]]
            kws = KEYWORDS_BY_AG[ag["id"]]
            for i, (kw_text, match_type) in enumerate(kws):
                # Assign search terms round-robin to keywords
                st = search_terms[i % len(search_terms)]
                st_status = random.choice(["NONE", "NONE", "ADDED", "EXCLUDED"])
                for day_offset in range(DAYS):
                    d = START_DATE + timedelta(days=day_offset)
                    wf = weekend_factor(d)
                    dv = day_variance()
                    imps = max(0, int(p["imp_base"] * wf * dv / 80))
                    clicks = max(0, int(imps * p["ctr"] * random.uniform(0.85, 1.15)))
                    cost_micros = int(clicks * p["cpc"] * 1_000_000 * random.uniform(0.9, 1.1))
                    cost = round(cost_micros / 1_000_000, 4)
                    convs = round(clicks * p["cvr"] * random.uniform(0.7, 1.3), 2)
                    conv_val = round(convs * random.uniform(80, 200), 2)
                    ctr = round(clicks / imps, 4) if imps > 0 else 0.0
                    cpc = round(cost / clicks, 4) if clicks > 0 else 0.0
                    cpa = round(cost / convs, 2) if convs > 0 else 0.0
                    roas = round(conv_val / cost, 4) if cost > 0 else 0.0
                    rows.append((
                        RUN_ID, INGESTED_AT, CUSTOMER_ID, d.isoformat(),
                        camp["id"], camp["name"],
                        ag["id"], ag["name"],
                        kw_id, kw_text, st, st_status, match_type,
                        imps, clicks, cost_micros, cost,
                        convs, conv_val, ctr, cpc, cpa, roas,
                    ))
                kw_id += 1
    conn.execute("""
        CREATE OR REPLACE TABLE analytics.search_term_daily (
            run_id VARCHAR, ingested_at TIMESTAMP, customer_id VARCHAR,
            snapshot_date DATE, campaign_id BIGINT, campaign_name VARCHAR,
            ad_group_id BIGINT, ad_group_name VARCHAR,
            keyword_id BIGINT, keyword_text VARCHAR,
            search_term VARCHAR, search_term_status VARCHAR, match_type VARCHAR,
            impressions BIGINT, clicks BIGINT, cost_micros BIGINT, cost DOUBLE,
            conversions DOUBLE, conversions_value DOUBLE,
            ctr DOUBLE, cpc DOUBLE, cpa DOUBLE, roas DOUBLE
        )
    """)
    conn.executemany("INSERT INTO analytics.search_term_daily VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", rows)
    print(f"  Inserted {len(rows):,} rows")

# ── Run ───────────────────────────────────────────────────────────────────────
delete_existing()
generate_campaign_daily()
generate_ad_group_daily()
generate_keyword_daily()
generate_ad_daily()
generate_search_term_daily()
conn.close()

print("\n" + "=" * 70)
print("✅ GENERATION COMPLETE")
print("=" * 70)
print(f"  customer_id : {CUSTOMER_ID}")
print(f"  campaigns   : {len(CAMPAIGNS)}")
print(f"  ad groups   : {sum(len(v) for v in AD_GROUPS.values())}")
print(f"  date range  : {START_DATE} → {END_DATE}")
print()
print("NEXT STEPS:")
print("  1. python scripts/copy_all_to_readonly.py")
print("  2. Switch to Christopher Hoole client in ACT")
print("  3. Run features pipeline (or run recommendations directly)")
print("  4. Run Recommendations Engine in ACT")
