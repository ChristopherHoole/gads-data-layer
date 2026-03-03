"""
Generate synthetic ad_daily table with 365 days of ad-level performance data.

This script:
1. Queries ad_group_daily to get list of unique ad groups
2. Generates 2-5 ads per ad group with realistic distribution
3. Creates 365 days of performance data (Feb 22, 2025 to Feb 21, 2026)
4. Inserts into warehouse.duckdb
5. Copies table to warehouse_readonly.duckdb

Usage:
    python scripts/generate_ad_daily.py
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
    ("RESPONSIVE_SEARCH_AD", 0.50),  # 50% RSA (modern standard)
    ("EXPANDED_TEXT_AD", 0.30),       # 30% ETA (legacy)
    ("TEXT_AD", 0.20),                # 20% standard text
]

# Status distribution
AD_STATUS = [
    ("ENABLED", 0.80),   # 80% enabled
    ("PAUSED", 0.15),    # 15% paused
    ("REMOVED", 0.05),   # 5% removed
]

# Performance ranges
IMPRESSIONS_RANGE = (100, 10000)
CTR_RANGE = (0.01, 0.08)  # 1-8%
CPC_RANGE = (0.50, 5.00)   # $0.50-$5.00
CVR_RANGE = (0.01, 0.15)   # 1-15% of clicks
CONV_VALUE_RANGE = (10, 100)  # $10-$100 per conversion
IMPR_SHARE_RANGE = (0.10, 0.90)  # 10-90%


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
    """
    Generate realistic performance metrics for one ad on one day.
    
    Args:
        status: Ad status (ENABLED, PAUSED, REMOVED)
        base_impressions: Base impressions level for this ad
        day_offset: Days since start (for trends)
        total_days: Total days in dataset
        
    Returns:
        Dict with performance metrics
    """
    # Paused/removed ads have zero metrics
    if status in ("PAUSED", "REMOVED"):
        return {
            'impressions': 0,
            'clicks': 0,
            'cost_micros': 0,
            'conversions': 0.0,
            'conversions_value': 0.0,
            'all_conversions': 0.0,
            'all_conversions_value': 0.0,
            'search_impression_share': 0.0,
            'search_top_impression_share': 0.0,
            'search_absolute_top_impression_share': 0.0,
            'click_share': 0.0,
        }
    
    # Calculate learning phase effect (ads improve over first 30 days)
    learning_factor = min(1.0, (day_offset + 1) / 30.0)
    
    # Add ad fatigue effect (some ads decline after 180 days)
    fatigue_factor = 1.0
    if day_offset > 180:
        fatigue_chance = random.random()
        if fatigue_chance < 0.3:  # 30% of ads experience fatigue
            fatigue_factor = 1.0 - ((day_offset - 180) / total_days) * 0.3
    
    # Weekend effect (lower volume on Sat/Sun)
    current_date = START_DATE + timedelta(days=day_offset)
    weekend_factor = 0.7 if current_date.weekday() in (5, 6) else 1.0
    
    # Daily variance (±20%)
    daily_variance = random.uniform(0.8, 1.2)
    
    # Calculate impressions with all factors
    impressions = int(
        base_impressions 
        * learning_factor 
        * fatigue_factor 
        * weekend_factor 
        * daily_variance
    )
    impressions = max(0, impressions)  # Never negative
    
    # Calculate clicks (CTR varies by ad quality)
    ctr = random.uniform(*CTR_RANGE)
    clicks = int(impressions * ctr)
    
    # Calculate cost
    cpc = random.uniform(*CPC_RANGE)
    cost_micros = int(clicks * cpc * 1_000_000)
    
    # Calculate conversions
    cvr = random.uniform(*CVR_RANGE)
    conversions = clicks * cvr
    
    # Calculate conversion value
    conv_value_per_conv = random.uniform(*CONV_VALUE_RANGE)
    conversions_value = conversions * conv_value_per_conv
    
    # All conversions (slightly higher, includes view-through)
    all_conversions = conversions * random.uniform(1.0, 1.2)
    all_conversions_value = conversions_value * random.uniform(1.0, 1.2)
    
    # Impression share metrics
    search_is = random.uniform(*IMPR_SHARE_RANGE)
    search_top_is = search_is * random.uniform(0.6, 0.9)  # Top IS < overall IS
    search_abs_top_is = search_top_is * random.uniform(0.3, 0.7)  # Abs top IS < top IS
    click_share = search_is * random.uniform(0.8, 1.2)  # Click share similar to IS
    
    return {
        'impressions': impressions,
        'clicks': clicks,
        'cost_micros': cost_micros,
        'conversions': round(conversions, 2),
        'conversions_value': round(conversions_value, 2),
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
    print("SYNTHETIC AD_DAILY TABLE GENERATION")
    print("=" * 80)
    print(f"Customer ID: {CUSTOMER_ID}")
    print(f"Date Range: {START_DATE} to {END_DATE} ({DAYS} days)")
    print()
    
    # Connect to main database
    db_path = Path(__file__).parent.parent / 'warehouse.duckdb'
    print(f"Connecting to: {db_path}")
    conn = duckdb.connect(str(db_path))
    
    # ── Step 1: Get unique ad groups from ad_group_daily ──────────────────
    print("\n[1/5] Fetching ad groups from ad_group_daily...")
    
    ad_groups = conn.execute("""
        SELECT DISTINCT 
            ad_group_id,
            ad_group_name,
            campaign_id,
            campaign_name
        FROM analytics.ad_group_daily
        WHERE customer_id = ?
        ORDER BY ad_group_id
    """, [CUSTOMER_ID]).fetchall()
    
    print(f"Found {len(ad_groups)} unique ad groups")
    
    if len(ad_groups) == 0:
        print("ERROR: No ad groups found in ad_group_daily!")
        print("Cannot generate ads without ad groups.")
        return
    
    # ── Step 2: Generate ads for each ad group ────────────────────────────
    print("\n[2/5] Generating ads for each ad group...")
    
    ads = []
    ad_counter = 1
    
    for ag_id, ag_name, camp_id, camp_name in ad_groups:
        # Generate 2-5 ads per ad group
        num_ads = random.randint(2, 5)
        
        for i in range(num_ads):
            ad_type = get_random_choice(AD_TYPES)
            status = get_random_choice(AD_STATUS)
            
            # Generate unique ad ID
            ad_id = f"ad_{ad_counter:05d}"
            ad_name = f"{ad_type.replace('_', ' ').title()} {i+1}"
            
            # Base impressions for this ad (varies by ad group activity)
            base_impressions = random.randint(*IMPRESSIONS_RANGE)
            
            ads.append({
                'ad_id': ad_id,
                'ad_name': ad_name,
                'ad_type': ad_type,
                'ad_status': status,
                'ad_group_id': ag_id,
                'ad_group_name': ag_name,
                'campaign_id': camp_id,
                'campaign_name': camp_name,
                'base_impressions': base_impressions,
            })
            
            ad_counter += 1
    
    print(f"Generated {len(ads)} ads ({len(ads) / len(ad_groups):.1f} ads per ad group avg)")
    
    # Status distribution check
    status_counts = {}
    for ad in ads:
        status = ad['ad_status']
        status_counts[status] = status_counts.get(status, 0) + 1
    
    print("Status distribution:")
    for status, count in sorted(status_counts.items()):
        pct = (count / len(ads)) * 100
        print(f"  {status:10s}: {count:4d} ({pct:5.1f}%)")
    
    # ── Step 3: Create ad_daily table ──────────────────────────────────────
    print("\n[3/5] Creating analytics.ad_daily table...")
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS analytics.ad_daily (
            customer_id VARCHAR,
            snapshot_date DATE,
            ad_group_id VARCHAR,
            ad_id VARCHAR,
            ad_name VARCHAR,
            ad_type VARCHAR,
            ad_status VARCHAR,
            
            -- Performance metrics
            impressions BIGINT,
            clicks BIGINT,
            cost_micros BIGINT,
            conversions DOUBLE,
            conversions_value DOUBLE,
            
            -- Calculated metrics
            all_conversions DOUBLE,
            all_conversions_value DOUBLE,
            
            -- Impression share metrics
            search_impression_share DOUBLE,
            search_top_impression_share DOUBLE,
            search_absolute_top_impression_share DOUBLE,
            click_share DOUBLE,
            
            PRIMARY KEY (customer_id, snapshot_date, ad_id)
        );
    """)
    
    print("Table created successfully")
    
    # ── Step 4: Generate and insert daily data ────────────────────────────
    print("\n[4/5] Generating 365 days of performance data...")
    print("(This may take 1-2 minutes...)")
    
    rows_inserted = 0
    batch_size = 1000
    batch = []
    
    try:
        # For each day
        for day_offset in range(DAYS):
            current_date = START_DATE + timedelta(days=day_offset)
            
            # For each ad
            for ad in ads:
                # Generate performance metrics for this ad on this day
                perf = generate_ad_performance(
                    ad['ad_status'],
                    ad['base_impressions'],
                    day_offset,
                    DAYS
                )
                
                # Build row tuple
                row = (
                    CUSTOMER_ID,
                    current_date.isoformat(),
                    ad['ad_group_id'],
                    ad['ad_id'],
                    ad['ad_name'],
                    ad['ad_type'],
                    ad['ad_status'],
                    perf['impressions'],
                    perf['clicks'],
                    perf['cost_micros'],
                    perf['conversions'],
                    perf['conversions_value'],
                    perf['all_conversions'],
                    perf['all_conversions_value'],
                    perf['search_impression_share'],
                    perf['search_top_impression_share'],
                    perf['search_absolute_top_impression_share'],
                    perf['click_share'],
                )
                
                batch.append(row)
                
                # Insert in batches
                if len(batch) >= batch_size:
                    conn.executemany("""
                        INSERT INTO analytics.ad_daily VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, batch)
                    rows_inserted += len(batch)
                    batch = []
                    
                    # Progress indicator
                    if rows_inserted % 5000 == 0:
                        print(f"  Inserted {rows_inserted:,} rows... (day {day_offset + 1}/{DAYS})")
        
        # Insert remaining rows
        if batch:
            conn.executemany("""
                INSERT INTO analytics.ad_daily VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, batch)
            rows_inserted += len(batch)
        
        print(f"✓ Inserted {rows_inserted:,} rows into warehouse.duckdb")
        
    except Exception as e:
        print(f"\n✗ ERROR during data generation: {e}")
        print(f"  Rows inserted before error: {rows_inserted:,}")
        import traceback
        traceback.print_exc()
        conn.close()
        return
    
    # ── Step 5: Copy table to warehouse_readonly.duckdb ───────────────────
    print("\n[5/5] Copying table to warehouse_readonly.duckdb...")
    
    readonly_path = Path(__file__).parent.parent / 'warehouse_readonly.duckdb'
    
    try:
        # Connect to readonly database
        conn_readonly = duckdb.connect(str(readonly_path))
        
        # Drop table if exists, then create from main database
        conn_readonly.execute("DROP TABLE IF EXISTS analytics.ad_daily")
        conn_readonly.execute(f"""
            CREATE TABLE analytics.ad_daily AS 
            SELECT * FROM '{db_path}'.analytics.ad_daily
        """)
        
        # Verify row count
        readonly_count = conn_readonly.execute(
            "SELECT COUNT(*) FROM analytics.ad_daily"
        ).fetchone()[0]
        
        print(f"✓ Copied {readonly_count:,} rows to warehouse_readonly.duckdb")
        
        # Close connections
        conn_readonly.close()
        
    except Exception as e:
        print(f"\n✗ ERROR copying to readonly database: {e}")
        import traceback
        traceback.print_exc()
        print("\nWARNING: Main database has data, but readonly copy failed.")
        print("You may need to manually copy the table.")
    
    # Close main connection
    conn.close()
    
    # ── Summary ────────────────────────────────────────────────────────────
    print("\n" + "=" * 80)
    print("GENERATION COMPLETE")
    print("=" * 80)
    print(f"Total ads created: {len(ads)}")
    print(f"Total rows inserted: {rows_inserted:,}")
    print(f"Date range: {START_DATE} to {END_DATE} ({DAYS} days)")
    print(f"Average rows per day: {rows_inserted / DAYS:.0f}")
    print()
    print("Next steps:")
    print("1. Verify data: Run verification queries (see CHAT_54_BRIEF.md)")
    print("2. Fix ads.py route: Add helper functions and update metrics cards")
    print("3. Test: http://127.0.0.1:5000/ads")
    print()


if __name__ == "__main__":
    main()
