"""
Synthetic Ad Data Generator for Chat 11
Generates realistic ad group and ad performance data for testing.

Output:
- 100 ad groups (20 campaigns × 5 ad groups)
- 1,000 ads (100 ad groups × 10 ads)
- 90 days of performance data
- Multiple ad scenarios (high CTR, low CTR, RSA strengths, stale ads, etc.)

Usage:
    python tools/testing/generate_synthetic_ads.py
"""

import duckdb
import random
from datetime import datetime, timedelta
from pathlib import Path


# Configuration
CUSTOMER_ID = "9999999999"
NUM_CAMPAIGNS = 20
AD_GROUPS_PER_CAMPAIGN = 5
ADS_PER_AD_GROUP = 10
DAYS_OF_DATA = 90
END_DATE = datetime(2026, 2, 15)
START_DATE = END_DATE - timedelta(days=DAYS_OF_DATA - 1)


# Ad group types distribution
AD_GROUP_TYPES = [
    "SEARCH_STANDARD",  # 70%
    "DISPLAY_STANDARD",  # 20%
    "SHOPPING_PRODUCT_ADS",  # 10%
]

# Ad types distribution
AD_TYPES = [
    ("RESPONSIVE_SEARCH_AD", 0.60),  # 60% RSA
    ("EXPANDED_TEXT_AD", 0.30),      # 30% ETA (legacy)
    ("RESPONSIVE_DISPLAY_AD", 0.10), # 10% Display
]

# RSA ad strength distribution
RSA_STRENGTHS = [
    ("POOR", 0.15),
    ("AVERAGE", 0.35),
    ("GOOD", 0.35),
    ("EXCELLENT", 0.15),
]

# Sample RSA headlines and descriptions
RSA_HEADLINES = [
    "Buy Now and Save", "Limited Time Offer", "Free Shipping Today",
    "Best Prices Online", "Shop Our Sale", "Premium Quality Products",
    "Trusted by Millions", "Fast Delivery", "Satisfaction Guaranteed",
    "Expert Customer Service", "New Arrivals Daily", "Exclusive Deals",
    "Top Rated Products", "Industry Leader", "Compare and Save"
]

RSA_DESCRIPTIONS = [
    "Find the best deals on top products. Shop now!",
    "Quality guaranteed. Fast shipping. Easy returns.",
    "Join thousands of satisfied customers today.",
    "Browse our selection and save big on your order."
]

# Sample final URLs
FINAL_URLS = [
    "https://example.com/products",
    "https://example.com/sale",
    "https://example.com/new-arrivals",
    "https://example.com/featured",
    "https://example.com/bestsellers",
]


def generate_ad_group_name(campaign_name, index):
    """Generate ad group name."""
    themes = ["Products", "Services", "Features", "Benefits", "Solutions"]
    return f"{campaign_name} - {themes[index % len(themes)]} {index + 1}"


def generate_ad_scenarios():
    """
    Define ad performance scenarios for testing.
    Returns list of (scenario_name, count, config).
    """
    return [
        ("high_ctr_winners", 150, {
            "ctr_multiplier": 1.5,  # 50% above ad group average
            "cvr_multiplier": 1.0,
            "impressions_range": (5000, 15000),
        }),
        ("low_ctr_losers", 150, {
            "ctr_multiplier": 0.5,  # 50% below ad group average
            "cvr_multiplier": 1.0,
            "impressions_range": (3000, 10000),
        }),
        ("high_cvr_performers", 100, {
            "ctr_multiplier": 1.0,
            "cvr_multiplier": 1.4,  # 40% above ad group average
            "impressions_range": (4000, 12000),
        }),
        ("low_cvr_underperformers", 100, {
            "ctr_multiplier": 1.0,
            "cvr_multiplier": 0.6,  # 40% below ad group average
            "impressions_range": (4000, 12000),
        }),
        ("new_ads_low_data", 100, {
            "ctr_multiplier": 1.0,
            "cvr_multiplier": 1.0,
            "impressions_range": (200, 800),  # < 1000 impressions
            "days_active": 20,  # Only last 20 days
        }),
        ("low_impression_share", 150, {
            "ctr_multiplier": 1.0,
            "cvr_multiplier": 1.0,
            "impressions_range": (500, 900),  # < 1000 impressions
        }),
        ("rsa_poor_strength", 100, {
            "ctr_multiplier": 0.7,
            "cvr_multiplier": 0.8,
            "impressions_range": (3000, 10000),
            "force_ad_strength": "POOR",
        }),
        ("rsa_average_strength", 150, {
            "ctr_multiplier": 1.0,
            "cvr_multiplier": 1.0,
            "impressions_range": (4000, 12000),
            "force_ad_strength": "AVERAGE",
        }),
        ("stale_ads_180plus", 100, {
            "ctr_multiplier": 0.85,  # Declining CTR
            "cvr_multiplier": 0.9,
            "impressions_range": (5000, 15000),
            "days_since_creation": 200,  # Created 200 days ago
            "ctr_decline": True,  # CTR declining over time
        }),
    ]


def select_scenario_for_ad(ad_index, scenarios):
    """Select which scenario this ad belongs to based on index."""
    total_ads = 0
    for scenario_name, count, config in scenarios:
        total_ads += count
        if ad_index < total_ads:
            return scenario_name, config
    # Default scenario for remaining ads
    return "baseline", {
        "ctr_multiplier": 1.0,
        "cvr_multiplier": 1.0,
        "impressions_range": (4000, 12000),
    }


def generate_ad_type_and_strength():
    """Generate ad type and strength (if RSA)."""
    rand = random.random()
    cumulative = 0
    for ad_type, prob in AD_TYPES:
        cumulative += prob
        if rand < cumulative:
            if ad_type == "RESPONSIVE_SEARCH_AD":
                rand_strength = random.random()
                cumulative_strength = 0
                for strength, prob_strength in RSA_STRENGTHS:
                    cumulative_strength += prob_strength
                    if rand_strength < cumulative_strength:
                        return ad_type, strength
            return ad_type, None
    return "RESPONSIVE_SEARCH_AD", "AVERAGE"


def generate_rsa_creative():
    """Generate RSA headlines and descriptions."""
    num_headlines = random.randint(8, 15)  # RSA requires 3-15 headlines
    num_descriptions = random.randint(2, 4)  # RSA requires 2-4 descriptions
    
    headlines = random.sample(RSA_HEADLINES, min(num_headlines, len(RSA_HEADLINES)))
    descriptions = random.sample(RSA_DESCRIPTIONS, min(num_descriptions, len(RSA_DESCRIPTIONS)))
    
    return headlines, descriptions


def calculate_metrics(base_impressions, base_ctr, base_cvr, ctr_mult, cvr_mult):
    """Calculate ad metrics based on multipliers."""
    impressions = int(base_impressions * random.uniform(0.8, 1.2))
    ctr = base_ctr * ctr_mult * random.uniform(0.9, 1.1)
    clicks = int(impressions * ctr)
    
    cvr = base_cvr * cvr_mult * random.uniform(0.9, 1.1)
    conversions = clicks * cvr
    
    cpc_micros = int(random.uniform(1_000_000, 5_000_000))  # $1-$5
    cost_micros = clicks * cpc_micros
    
    conversion_value_per = random.uniform(50, 200)  # $50-$200 per conversion
    conversions_value = conversions * conversion_value_per
    
    cpa = cost_micros / conversions if conversions > 0 else 0
    roas = conversions_value / (cost_micros / 1_000_000) if cost_micros > 0 else 0
    
    return {
        'impressions': impressions,
        'clicks': clicks,
        'cost_micros': cost_micros,
        'conversions': round(conversions, 2),
        'conversions_value': round(conversions_value, 2),
        'ctr': round(ctr, 4),
        'cpc': cpc_micros,
        'cvr': round(cvr, 4),
        'cpa': int(cpa),
        'roas': round(roas, 2),
    }


def main():
    """Generate synthetic ad data."""
    print("[SyntheticAds] Starting ad data generation...")
    
    # Connect to readonly database
    ro_con = duckdb.connect('warehouse_readonly.duckdb')
    
    # Get existing campaigns
    campaigns = ro_con.execute("""
        SELECT DISTINCT campaign_id, campaign_name
        FROM analytics.campaign_daily
        WHERE customer_id = ?
        ORDER BY campaign_id
        LIMIT ?
    """, [CUSTOMER_ID, NUM_CAMPAIGNS]).fetchall()
    
    if len(campaigns) < NUM_CAMPAIGNS:
        print(f"[SyntheticAds] ERROR: Only {len(campaigns)} campaigns found, need {NUM_CAMPAIGNS}")
        print("[SyntheticAds] Run generate_campaign_synthetic.py first")
        return
    
    print(f"[SyntheticAds] Found {len(campaigns)} campaigns")
    
    # Define scenarios
    scenarios = generate_ad_scenarios()
    
    # Generate ad groups and ads
    ad_group_rows = []
    ad_rows = []
    
    ad_group_id_counter = 5000  # Start ad group IDs at 5000
    ad_id_counter = 10000  # Start ad IDs at 10000
    global_ad_counter = 0  # For scenario selection
    
    for campaign_id, campaign_name in campaigns:
        print(f"[SyntheticAds] Generating data for campaign {campaign_id}: {campaign_name}")
        
        # Generate ad groups for this campaign
        for ag_index in range(AD_GROUPS_PER_CAMPAIGN):
            ad_group_id = ad_group_id_counter
            ad_group_id_counter += 1
            
            ad_group_name = generate_ad_group_name(campaign_name, ag_index)
            ad_group_type = AD_GROUP_TYPES[ag_index % len(AD_GROUP_TYPES)]
            
            # Ad group base metrics (for calculating ad group averages)
            ag_base_ctr = random.uniform(0.03, 0.08)  # 3-8% CTR
            ag_base_cvr = random.uniform(0.02, 0.06)  # 2-6% CVR
            
            # Generate ad group daily data (90 days)
            for day_offset in range(DAYS_OF_DATA):
                date = START_DATE + timedelta(days=day_offset)
                
                # Ad group performance (aggregate of its ads)
                ag_impressions = random.randint(10000, 30000)
                ag_metrics = calculate_metrics(
                    ag_impressions,
                    ag_base_ctr,
                    ag_base_cvr,
                    1.0,
                    1.0
                )
                
                ad_group_rows.append({
                    'customer_id': CUSTOMER_ID,
                    'snapshot_date': date.strftime('%Y-%m-%d'),
                    'campaign_id': campaign_id,
                    'campaign_name': campaign_name,
                    'ad_group_id': ad_group_id,
                    'ad_group_name': ad_group_name,
                    'ad_group_status': 'ENABLED',
                    'ad_group_type': ad_group_type,
                    'cpc_bid_micros': random.randint(1_500_000, 4_000_000),
                    'target_cpa_micros': None,
                    'target_roas': None,
                    **ag_metrics
                })
            
            # Generate ads for this ad group
            for ad_index in range(ADS_PER_AD_GROUP):
                ad_id = ad_id_counter
                ad_id_counter += 1
                
                # Select scenario for this ad
                scenario_name, scenario_config = select_scenario_for_ad(global_ad_counter, scenarios)
                global_ad_counter += 1
                
                # Generate ad type and strength
                ad_type, ad_strength = generate_ad_type_and_strength()
                
                # Override ad strength if scenario specifies
                if 'force_ad_strength' in scenario_config:
                    if ad_type == "RESPONSIVE_SEARCH_AD":
                        ad_strength = scenario_config['force_ad_strength']
                
                # Generate creative
                headlines = None
                descriptions = None
                if ad_type == "RESPONSIVE_SEARCH_AD":
                    headlines, descriptions = generate_rsa_creative()
                
                final_url = random.choice(FINAL_URLS)
                
                # Determine active days for this ad
                days_active = scenario_config.get('days_active', DAYS_OF_DATA)
                days_since_creation = scenario_config.get('days_since_creation', 0)
                start_day = max(0, DAYS_OF_DATA - days_active - days_since_creation)
                end_day = min(DAYS_OF_DATA, start_day + days_active)
                
                # Generate ad daily data
                for day_offset in range(start_day, end_day):
                    date = START_DATE + timedelta(days=day_offset)
                    
                    # Get scenario multipliers
                    ctr_mult = scenario_config.get('ctr_multiplier', 1.0)
                    cvr_mult = scenario_config.get('cvr_multiplier', 1.0)
                    
                    # Apply CTR decline if specified
                    if scenario_config.get('ctr_decline', False):
                        days_since_start = day_offset - start_day
                        decline_factor = 1.0 - (days_since_start / days_active * 0.2)  # 20% decline over period
                        ctr_mult *= decline_factor
                    
                    # Get impressions range
                    imp_min, imp_max = scenario_config.get('impressions_range', (4000, 12000))
                    daily_impressions = random.randint(imp_min, imp_max) // days_active
                    
                    # Calculate metrics
                    ad_metrics = calculate_metrics(
                        daily_impressions,
                        ag_base_ctr,
                        ag_base_cvr,
                        ctr_mult,
                        cvr_mult
                    )
                    
                    ad_rows.append({
                        'customer_id': CUSTOMER_ID,
                        'snapshot_date': date.strftime('%Y-%m-%d'),
                        'campaign_id': campaign_id,
                        'campaign_name': campaign_name,
                        'ad_group_id': ad_group_id,
                        'ad_group_name': ad_group_name,
                        'ad_id': ad_id,
                        'ad_type': ad_type,
                        'ad_status': 'ENABLED',
                        'ad_strength': ad_strength,
                        'headlines': headlines,
                        'descriptions': descriptions,
                        'final_url': final_url,
                        **ad_metrics
                    })
    
    print(f"\n[SyntheticAds] Generated:")
    print(f"  {len(set(r['ad_group_id'] for r in ad_group_rows))} ad groups")
    print(f"  {len(set(r['ad_id'] for r in ad_rows))} ads")
    print(f"  {len(ad_group_rows)} ad group performance rows")
    print(f"  {len(ad_rows)} ad performance rows")
    
    # Insert ad group data
    print("\n[SyntheticAds] Inserting ad group data...")
    ro_con.executemany("""
        INSERT OR REPLACE INTO analytics.ad_group_daily VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
    """, [
        (r['customer_id'], r['snapshot_date'], r['campaign_id'], r['campaign_name'],
         r['ad_group_id'], r['ad_group_name'], r['ad_group_status'], r['ad_group_type'],
         r['cpc_bid_micros'], r['target_cpa_micros'], r['target_roas'],
         r['impressions'], r['clicks'], r['cost_micros'], r['conversions'], r['conversions_value'],
         r['ctr'], r['cpc'], r['cpa'], r['roas'])
        for r in ad_group_rows
    ])
    
    # Insert ad data
    print("[SyntheticAds] Inserting ad data...")
    ro_con.executemany("""
        INSERT OR REPLACE INTO analytics.ad_daily VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
    """, [
        (r['customer_id'], r['snapshot_date'], r['campaign_id'], r['campaign_name'],
         r['ad_group_id'], r['ad_group_name'], r['ad_id'], r['ad_type'], r['ad_status'],
         r['ad_strength'], r['headlines'], r['descriptions'], r['final_url'],
         r['impressions'], r['clicks'], r['cost_micros'], r['conversions'], r['conversions_value'],
         r['ctr'], r['cpc'], r['cvr'], r['cpa'], r['roas'])
        for r in ad_rows
    ])
    
    # Verify
    ag_count = ro_con.execute("SELECT COUNT(DISTINCT ad_group_id) FROM analytics.ad_group_daily WHERE customer_id = ?", [CUSTOMER_ID]).fetchone()[0]
    ad_count = ro_con.execute("SELECT COUNT(DISTINCT ad_id) FROM analytics.ad_daily WHERE customer_id = ?", [CUSTOMER_ID]).fetchone()[0]
    ag_row_count = ro_con.execute("SELECT COUNT(*) FROM analytics.ad_group_daily WHERE customer_id = ?", [CUSTOMER_ID]).fetchone()[0]
    ad_row_count = ro_con.execute("SELECT COUNT(*) FROM analytics.ad_daily WHERE customer_id = ?", [CUSTOMER_ID]).fetchone()[0]
    
    print(f"\n✅ Synthetic ad data generated:")
    print(f"  Ad groups: {ag_count}")
    print(f"  Ads: {ad_count}")
    print(f"  Ad group rows: {ag_row_count}")
    print(f"  Ad rows: {ad_row_count}")
    
    ro_con.close()
    print("\n✅ Part 4 Complete")


if __name__ == '__main__':
    main()
