"""
Generate synthetic ad_daily table - CHUNKED VERSION.

Generates data in smaller chunks with frequent commits to avoid memory issues.
This version commits after each day instead of batching thousands of rows.

Usage:
    python scripts/generate_ad_daily_chunked.py
"""

import duckdb
import random
from datetime import date, timedelta
from pathlib import Path

# Configuration
CUSTOMER_ID = "9999999999"
START_DATE = date(2025, 2, 22)
END_DATE = date(2026, 2, 21)
DAYS = (END_DATE - START_DATE).days + 1

# Ad type distribution
AD_TYPES = [
    ("RESPONSIVE_SEARCH_AD", 0.50),
    ("EXPANDED_TEXT_AD", 0.30),
    ("TEXT_AD", 0.20),
]

# Status distribution
AD_STATUS = [
    ("ENABLED", 0.80),
    ("PAUSED", 0.15),
    ("REMOVED", 0.05),
]

# Performance ranges
IMPRESSIONS_RANGE = (100, 10000)
CTR_RANGE = (0.01, 0.08)
CPC_RANGE = (0.50, 5.00)
CVR_RANGE = (0.01, 0.15)
CONV_VALUE_RANGE = (10, 100)
IMPR_SHARE_RANGE = (0.10, 0.90)


def get_random_choice(choices):
    """Select random item from weighted choices list."""
    total = sum(weight for _, weight in choices)
    rand = random.random() * total
    cumulative = 0
    for value, weight in choices:
        cumulative += weight
        if rand <= cumulative:
            return value
    return choices[-1][0]


def generate_ad_performance(status, base_impressions, day_offset, total_days):
    """Generate realistic performance metrics for one ad on one day."""
    if status in ("PAUSED", "REMOVED"):
        return {
            'impressions': 0, 'clicks': 0, 'cost_micros': 0,
            'conversions': 0.0, 'conversions_value': 0.0,
            'all_conversions': 0.0, 'all_conversions_value': 0.0,
            'search_impression_share': 0.0, 'search_top_impression_share': 0.0,
            'search_absolute_top_impression_share': 0.0, 'click_share': 0.0,
        }
    
    learning_factor = min(1.0, (day_offset + 1) / 30.0)
    fatigue_factor = 1.0
    if day_offset > 180:
        if random.random() < 0.3:
            fatigue_factor = 1.0 - ((day_offset - 180) / total_days) * 0.3
    
    current_date = START_DATE + timedelta(days=day_offset)
    weekend_factor = 0.7 if current_date.weekday() in (5, 6) else 1.0
    daily_variance = random.uniform(0.8, 1.2)
    
    impressions = int(base_impressions * learning_factor * fatigue_factor * weekend_factor * daily_variance)
    impressions = max(0, impressions)
    
    ctr = random.uniform(*CTR_RANGE)
    clicks = int(impressions * ctr)
    
    cpc = random.uniform(*CPC_RANGE)
    cost_micros = int(clicks * cpc * 1_000_000)
    
    cvr = random.uniform(*CVR_RANGE)
    conversions = clicks * cvr
    
    conv_value_per_conv = random.uniform(*CONV_VALUE_RANGE)
    conversions_value = conversions * conv_value_per_conv
    
    all_conversions = conversions * random.uniform(1.0, 1.2)
    all_conversions_value = conversions_value * random.uniform(1.0, 1.2)
    
    search_is = random.uniform(*IMPR_SHARE_RANGE)
    search_top_is = search_is * random.uniform(0.6, 0.9)
    search_abs_top_is = search_top_is * random.uniform(0.3, 0.7)
    click_share = search_is * random.uniform(0.8, 1.2)
    
    return {
        'impressions': impressions, 'clicks': clicks, 'cost_micros': cost_micros,
        'conversions': round(conversions, 2), 'conversions_value': round(conversions_value, 2),
        'all_conversions': round(all_conversions, 2),
        'all_conversions_value': round(all_conversions_value, 2),
        'search_impression_share': round(search_is, 4),
        'search_top_impression_share': round(search_top_is, 4),
        'search_absolute_top_impression_share': round(search_abs_top_is, 4),
        'click_share': round(click_share, 4),
    }


def main():
    """Main execution function."""
    print("=" * 80)
    print("SYNTHETIC AD_DAILY TABLE GENERATION - CHUNKED VERSION")
    print("=" * 80)
    print(f"Customer ID: {CUSTOMER_ID}")
    print(f"Date Range: {START_DATE} to {END_DATE} ({DAYS} days)")
    print()
    
    db_path = Path(__file__).parent.parent / 'warehouse.duckdb'
    print(f"Connecting to: {db_path}")
    conn = duckdb.connect(str(db_path))
    
    # Get ad groups
    print("\n[1/5] Fetching ad groups from ad_group_daily...")
    ad_groups = conn.execute("""
        SELECT DISTINCT ad_group_id, ad_group_name, campaign_id, campaign_name
        FROM analytics.ad_group_daily
        WHERE customer_id = ?
        ORDER BY ad_group_id
    """, [CUSTOMER_ID]).fetchall()
    print(f"Found {len(ad_groups)} unique ad groups")
    
    if len(ad_groups) == 0:
        print("ERROR: No ad groups found!")
        return
    
    # Generate ads
    print("\n[2/5] Generating ads for each ad group...")
    ads = []
    ad_counter = 1
    
    for ag_id, ag_name, camp_id, camp_name in ad_groups:
        num_ads = random.randint(2, 5)
        for i in range(num_ads):
            ad_type = get_random_choice(AD_TYPES)
            status = get_random_choice(AD_STATUS)
            ads.append({
                'ad_id': f"ad_{ad_counter:05d}",
                'ad_name': f"{ad_type.replace('_', ' ').title()} {i+1}",
                'ad_type': ad_type, 'ad_status': status,
                'ad_group_id': ag_id, 'ad_group_name': ag_name,
                'campaign_id': camp_id, 'campaign_name': camp_name,
                'base_impressions': random.randint(*IMPRESSIONS_RANGE),
            })
            ad_counter += 1
    
    print(f"Generated {len(ads)} ads ({len(ads) / len(ad_groups):.1f} avg per ad group)")
    
    status_counts = {}
    for ad in ads:
        status = ad['ad_status']
        status_counts[status] = status_counts.get(status, 0) + 1
    print("Status distribution:")
    for status, count in sorted(status_counts.items()):
        pct = (count / len(ads)) * 100
        print(f"  {status:10s}: {count:4d} ({pct:5.1f}%)")
    
    # Create table
    print("\n[3/5] Creating analytics.ad_daily table...")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS analytics.ad_daily (
            customer_id VARCHAR, snapshot_date DATE, ad_group_id VARCHAR,
            ad_id VARCHAR, ad_name VARCHAR, ad_type VARCHAR, ad_status VARCHAR,
            impressions BIGINT, clicks BIGINT, cost_micros BIGINT,
            conversions DOUBLE, conversions_value DOUBLE,
            all_conversions DOUBLE, all_conversions_value DOUBLE,
            search_impression_share DOUBLE, search_top_impression_share DOUBLE,
            search_absolute_top_impression_share DOUBLE, click_share DOUBLE,
            PRIMARY KEY (customer_id, snapshot_date, ad_id)
        );
    """)
    print("Table created successfully")
    
    # Generate data DAY BY DAY (commit after each day)
    print("\n[4/5] Generating 365 days of performance data...")
    print("Strategy: Insert one day at a time, commit frequently")
    print()
    
    total_rows = 0
    
    try:
        for day_offset in range(DAYS):
            current_date = START_DATE + timedelta(days=day_offset)
            day_rows = []
            
            # Generate all ads for this day
            for ad in ads:
                perf = generate_ad_performance(ad['ad_status'], ad['base_impressions'], day_offset, DAYS)
                row = (
                    CUSTOMER_ID, current_date.isoformat(), ad['ad_group_id'],
                    ad['ad_id'], ad['ad_name'], ad['ad_type'], ad['ad_status'],
                    perf['impressions'], perf['clicks'], perf['cost_micros'],
                    perf['conversions'], perf['conversions_value'],
                    perf['all_conversions'], perf['all_conversions_value'],
                    perf['search_impression_share'], perf['search_top_impression_share'],
                    perf['search_absolute_top_impression_share'], perf['click_share'],
                )
                day_rows.append(row)
            
            # Insert this day's data
            conn.executemany("""
                INSERT INTO analytics.ad_daily VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, day_rows)
            
            total_rows += len(day_rows)
            
            # Progress every 25 days
            if (day_offset + 1) % 25 == 0 or day_offset == DAYS - 1:
                print(f"  Day {day_offset + 1:3d}/{DAYS} complete ({total_rows:,} rows inserted)")
        
        print(f"\n✓ Inserted {total_rows:,} rows into warehouse.duckdb")
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        conn.close()
        return
    
    # Copy to readonly
    print("\n[5/5] Copying table to warehouse_readonly.duckdb...")
    readonly_path = Path(__file__).parent.parent / 'warehouse_readonly.duckdb'
    
    try:
        conn_readonly = duckdb.connect(str(readonly_path))
        conn_readonly.execute("DROP TABLE IF EXISTS analytics.ad_daily")
        conn_readonly.execute(f"CREATE TABLE analytics.ad_daily AS SELECT * FROM '{db_path}'.analytics.ad_daily")
        readonly_count = conn_readonly.execute("SELECT COUNT(*) FROM analytics.ad_daily").fetchone()[0]
        print(f"✓ Copied {readonly_count:,} rows to warehouse_readonly.duckdb")
        conn_readonly.close()
    except Exception as e:
        print(f"✗ ERROR copying to readonly: {e}")
        import traceback
        traceback.print_exc()
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("GENERATION COMPLETE")
    print("=" * 80)
    print(f"Total ads: {len(ads)}")
    print(f"Total rows: {total_rows:,}")
    print(f"Date range: {START_DATE} to {END_DATE} ({DAYS} days)")
    print()


if __name__ == "__main__":
    main()
