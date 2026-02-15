"""
Generate Shopping Data for Dashboard Client
Creates synthetic Shopping data + runs Lighthouse for dashboard's active client
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import duckdb
import random

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from act_lighthouse.config import load_client_config
from act_lighthouse.shopping_features import build_product_features_daily


def generate_shopping_data_for_client(customer_id: str, conn):
    """Generate synthetic Shopping data for specific customer_id"""
    
    print(f"📦 Generating synthetic Shopping data for: {customer_id}\n")
    
    run_id = f"synthetic_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Campaign priority: 0=Low, 1=Medium, 2=High (INTEGER)
    campaigns = [
        {"id": 1001, "name": "Shopping - All Products", "priority": 1},  # Medium
        {"id": 1002, "name": "Shopping - Best Sellers", "priority": 2},  # High
        {"id": 1003, "name": "Shopping - Clearance", "priority": 0},     # Low
    ]
    
    brands = ["TechPro", "HomeStyle", "FitLife", "EcoWare", "PowerTech"]
    categories = ["Electronics", "Home & Garden", "Sports", "Beauty", "Appliances"]
    
    merchant_id = 123456789  # BIGINT
    
    # Generate 100 products
    products = []
    for i in range(100):
        product_id = f"prod_{i:04d}"
        brand = random.choice(brands)
        category = random.choice(categories)
        
        products.append({
            "id": product_id,
            "title": f"{brand} {category} - Model {random.randint(100, 999)}",
            "brand": brand,
            "category": category,
            "price": random.randint(20, 500) * 1_000_000,
        })
    
    # Generate 30 days of data
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=29)
    
    campaign_records = []
    product_records = []
    feed_records = []
    
    for single_date in [start_date + timedelta(days=x) for x in range(30)]:
        # Campaign data
        for camp in campaigns:
            impr = random.randint(1000, 5000)
            clicks = int(impr * random.uniform(0.02, 0.05))
            cost = clicks * random.randint(50000, 200000)
            conv = int(clicks * random.uniform(0.02, 0.08))
            conv_value = conv * random.randint(30, 150) * 1_000_000  # FIXED: Store in micros
            
            campaign_records.append((
                run_id,
                datetime.now(),
                customer_id,
                single_date,
                camp["id"],           # BIGINT
                camp["name"],
                camp["priority"],     # INTEGER (0, 1, or 2)
                False,                # enable_local (BOOLEAN)
                "US",                 # feed_label
                "US",                 # country_of_sale
                impr,
                clicks,
                cost,
                conv,
                conv_value,
                clicks / impr if impr > 0 else 0,
                cost / clicks if clicks > 0 else 0,
                conv_value / (cost / 1_000_000) if cost > 0 else 0,
            ))
        
        # Product data
        for product in products:
            camp = random.choice(campaigns)
            
            # Simulate different performance tiers
            perf_tier = random.random()
            if perf_tier < 0.1:  # 10% high performers
                impr = random.randint(500, 2000)
                ctr = random.uniform(0.04, 0.08)
                cvr = random.uniform(0.06, 0.12)
            elif perf_tier < 0.2:  # 10% low performers
                impr = random.randint(100, 500)
                ctr = random.uniform(0.01, 0.02)
                cvr = random.uniform(0.005, 0.02)
            else:  # 80% normal
                impr = random.randint(200, 1000)
                ctr = random.uniform(0.02, 0.04)
                cvr = random.uniform(0.02, 0.05)
            
            clicks = int(impr * ctr)
            cost = clicks * random.randint(50000, 150000)
            conv = int(clicks * cvr)
            conv_value = conv * random.randint(40, 120) * 1_000_000  # FIXED: Store in micros
            
            # Availability (10% out of stock)
            availability = "OUT_OF_STOCK" if random.random() < 0.1 else "IN_STOCK"
            
            product_records.append((
                run_id,
                datetime.now(),
                customer_id,
                single_date,
                camp["id"],           # BIGINT
                10001,                # ad_group_id (BIGINT)
                product["id"],        # product_id (VARCHAR - OK as string)
                product["title"],
                product["brand"],
                product["category"],
                product["category"],  # type_l1
                None,                 # type_l2
                product["price"],
                None,                 # sale_price
                availability,
                "NEW",                # condition
                "Margin_High",        # custom_label_0
                "Evergreen",          # custom_label_1
                impr,
                clicks,
                cost,
                conv,
                conv_value,
                ctr,
                cost / clicks if clicks > 0 else 0,
                conv_value / (cost / 1_000_000) if cost > 0 else 0,
                0.025,                # benchmark_ctr
            ))
    
    # Feed quality (once per product)
    for product in products:
        # 10% have issues
        has_issue = random.random() < 0.1
        
        if has_issue:
            issue_type = random.choice(['price', 'disapproved', 'missing'])
            if issue_type == 'price':
                status = "APPROVED"
                price_mismatch = True
                disapproval_reasons = []
            elif issue_type == 'disapproved':
                status = "DISAPPROVED"
                price_mismatch = False
                disapproval_reasons = ["policy_violation"]
            else:
                status = "APPROVED"
                price_mismatch = False
                disapproval_reasons = []
        else:
            status = "APPROVED"
            price_mismatch = False
            disapproval_reasons = []
        
        feed_records.append((
            run_id,
            datetime.now(),
            customer_id,
            merchant_id,          # BIGINT (not string!)
            end_date,
            product["id"],
            status,
            disapproval_reasons,
            [],                   # missing_attributes
            price_mismatch,
            [],                   # image_issues
            [],                   # shipping_issues
            "ACTIVE",             # feed_processing_status
        ))
    
    # Insert data
    print(f"   Inserting {len(campaign_records)} campaign records...")
    conn.executemany("""
        INSERT INTO raw_shopping_campaign_daily VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, campaign_records)
    
    print(f"   Inserting {len(product_records)} product performance records...")
    conn.executemany("""
        INSERT INTO raw_product_performance_daily VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, product_records)
    
    print(f"   Inserting {len(feed_records)} feed quality records...")
    conn.executemany("""
        INSERT INTO raw_product_feed_quality VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, feed_records)
    
    print(f"   ✅ Generated Shopping data for {len(products)} products over 30 days\n")


def main():
    print(f"\n{'='*60}")
    print(f"SHOPPING DATA + LIGHTHOUSE - Dashboard Client")
    print(f"{'='*60}\n")
    
    # Load dashboard's client config
    config_path = "configs/client_synthetic.yaml"
    cfg = load_client_config(config_path)
    
    print(f"Client: {cfg.client_id}")
    print(f"Customer ID: {cfg.customer_id}\n")
    
    # Connect to database
    db_path = Path("warehouse.duckdb")
    conn = duckdb.connect(str(db_path))
    
    # Clear old Shopping data for this client
    print("🗑️  Clearing old Shopping data...")
    conn.execute("DELETE FROM raw_shopping_campaign_daily WHERE customer_id = ?", (cfg.customer_id,))
    conn.execute("DELETE FROM raw_product_performance_daily WHERE customer_id = ?", (cfg.customer_id,))
    conn.execute("DELETE FROM raw_product_feed_quality WHERE customer_id = ?", (cfg.customer_id,))
    conn.execute("DELETE FROM analytics.product_features_daily WHERE customer_id = ?", (cfg.customer_id,))
    print("   ✅ Cleared old data\n")
    
    # Generate Shopping data
    generate_shopping_data_for_client(cfg.customer_id, conn)
    
    # Run Lighthouse
    snapshot_date = datetime.now().date()
    
    print(f"🔍 Building product features for {snapshot_date}...")
    
    result = build_product_features_daily(
        con=conn,
        cfg=cfg,
        snapshot_date=snapshot_date,
    )
    
    print(f"   ✅ Built {result.rows_inserted} product feature records")
    print(f"   Date range: {result.start_date} to {result.end_date}\n")
    
    conn.close()
    
    print(f"{'='*60}")
    print("COMPLETE ✅ - Refresh dashboard Shopping page!")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    main()
