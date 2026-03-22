r"""
Christopher Hoole Shopping Data Generator (CORRECTED VERSION)
Master Chat 13 - Phase 1

FIXES:
- Added run_id and ingested_at columns (CRITICAL - old version would fail)
- Added progress indicators every 30 days
- Added batch inserts for better performance
- Added detailed validation summary
- Added error handling with traceback
- Added product distribution summary

Generates complete Shopping dataset for customer_id "1254895944":
- 20 Shopping campaigns × 90 days = 1,800 rows in analytics.shopping_campaign_daily
- 100 products with full attributes
- 90 days × 100 products = 9,000 rows in raw_product_performance_daily

Usage (PowerShell):
    cd C:\Users\User\Desktop\gads-data-layer
    .\.venv\Scripts\Activate.ps1
    python generate_christopher_hoole_shopping_data_v2.py
"""

import random
import uuid
from datetime import datetime, date, timedelta
import duckdb

# ── Config ────────────────────────────────────────────────────────────────────
CUSTOMER_ID = "1254895944"  # Christopher Hoole
CLIENT_ID = "Christopher Hoole"
DB_PATH = "warehouse.duckdb"
END_DATE = date.today()
START_DATE = END_DATE - timedelta(days=89)
DAYS = 90

random.seed(1254)

# ── Bid strategy options ──────────────────────────────────────────────────────
BID_STRATEGY_TYPES = ["TARGET_ROAS", "MAXIMIZE_CONVERSION_VALUE"]

# ── 20 Shopping campaigns ─────────────────────────────────────────────────────
CAMPAIGNS = [
    {"id": "1001", "name": "Shopping – All Products", "priority": 1, "target_roas": 4.0, "status": "ENABLED"},
    {"id": "1002", "name": "Shopping – Best Sellers", "priority": 2, "target_roas": 5.0, "status": "ENABLED"},
    {"id": "1003", "name": "Shopping – Clearance", "priority": 0, "target_roas": 3.0, "status": "ENABLED"},
    {"id": "1004", "name": "Shopping – Electronics", "priority": 2, "target_roas": 4.5, "status": "ENABLED"},
    {"id": "1005", "name": "Shopping – Home & Garden", "priority": 1, "target_roas": 3.5, "status": "ENABLED"},
    {"id": "1006", "name": "Shopping – Apparel", "priority": 1, "target_roas": 4.0, "status": "ENABLED"},
    {"id": "1007", "name": "Shopping – Seasonal Promos", "priority": 2, "target_roas": 5.5, "status": "ENABLED"},
    {"id": "1008", "name": "Shopping – Brand Protection", "priority": 2, "target_roas": 6.0, "status": "ENABLED"},
    {"id": "1009", "name": "Shopping – New Arrivals", "priority": 1, "target_roas": 3.5, "status": "ENABLED"},
    {"id": "1010", "name": "Shopping – High Margin", "priority": 2, "target_roas": 5.0, "status": "ENABLED"},
    {"id": "1011", "name": "Shopping – Low Margin", "priority": 0, "target_roas": 3.0, "status": "ENABLED"},
    {"id": "1012", "name": "Shopping – Sports & Outdoors", "priority": 1, "target_roas": 4.0, "status": "ENABLED"},
    {"id": "1013", "name": "Shopping – Beauty", "priority": 1, "target_roas": 4.5, "status": "ENABLED"},
    {"id": "1014", "name": "Shopping – Kitchen", "priority": 1, "target_roas": 3.5, "status": "ENABLED"},
    {"id": "1015", "name": "Shopping – Toys & Games", "priority": 0, "target_roas": 3.2, "status": "ENABLED"},
    {"id": "1016", "name": "Shopping – Automotive", "priority": 0, "target_roas": 3.0, "status": "PAUSED"},
    {"id": "1017", "name": "Shopping – Office Supplies", "priority": 1, "target_roas": 3.8, "status": "PAUSED"},
    {"id": "1018", "name": "Shopping – Health & Wellness", "priority": 1, "target_roas": 4.2, "status": "ENABLED"},
    {"id": "1019", "name": "Shopping – Luxury", "priority": 2, "target_roas": 5.8, "status": "ENABLED"},
    {"id": "1020", "name": "Shopping – Budget Range", "priority": 0, "target_roas": 3.1, "status": "ENABLED"},
]

# ── Product data ──────────────────────────────────────────────────────────────
BRANDS = [
    "TechPro", "HomeStyle", "FitLife", "EcoWare", "LuxeLine",
    "SmartHome", "ActiveGear", "GreenChoice", "PureBeauty", "ModernLiving",
    "UrbanStyle", "NaturalWay", "TechGear", "ComfortZone", "StyleHub",
    "FreshStart", "PowerTech", "CozyHome", "FitGear", "EcoLife"
]

CATEGORIES = [
    "Electronics", "Home & Garden", "Sports & Outdoors", "Beauty & Personal Care",
    "Clothing & Accessories", "Kitchen & Dining", "Health & Wellness", "Office Supplies",
    "Toys & Games", "Automotive"
]

PRODUCT_TYPES_L1 = {
    "Electronics": ["Smartphones", "Laptops", "Tablets", "Headphones", "Cameras"],
    "Home & Garden": ["Furniture", "Bedding", "Gardening Tools", "Decor", "Lighting"],
    "Sports & Outdoors": ["Fitness Equipment", "Camping Gear", "Cycling", "Running", "Yoga"],
    "Beauty & Personal Care": ["Skincare", "Makeup", "Hair Care", "Fragrances", "Tools"],
    "Clothing & Accessories": ["Shirts", "Pants", "Shoes", "Bags", "Watches"],
    "Kitchen & Dining": ["Cookware", "Appliances", "Utensils", "Storage", "Tableware"],
    "Health & Wellness": ["Vitamins", "Fitness Trackers", "Massage Tools", "Air Purifiers", "Scales"],
    "Office Supplies": ["Desks", "Chairs", "Stationery", "Electronics", "Storage"],
    "Toys & Games": ["Action Figures", "Board Games", "Puzzles", "Educational", "Outdoor"],
    "Automotive": ["Car Accessories", "Tools", "Cleaning", "Electronics", "Parts"]
}

CUSTOM_LABELS_MARGIN = ["Margin_High", "Margin_Medium", "Margin_Low", "Clearance"]
CUSTOM_LABELS_SEASONALITY = ["Evergreen", "Summer", "Winter", "Holiday", "Back_to_School"]


def generate_campaign_day(campaign: dict, snapshot_date: date, day_index: int) -> dict:
    """Generate one day of Shopping campaign data."""
    status = campaign["status"]
    target_roas = campaign["target_roas"]

    if status == "PAUSED":
        impressions = random.randint(0, 100)
        clicks = 0
        cost = 0.0
        conversions = 0.0
        conv_value = 0.0
    else:
        base_impr = 3000 + campaign["priority"] * 1500
        noise = random.uniform(0.80, 1.20)
        impressions = max(100, int(base_impr * noise))
        ctr = random.uniform(0.015, 0.040)
        clicks = max(0, int(impressions * ctr))
        avg_cpc = random.uniform(0.40, 1.80)
        cost = round(clicks * avg_cpc, 2)
        roas_actual = target_roas * random.uniform(0.85, 1.15)
        roas_actual = max(3.0, min(6.5, roas_actual))
        conv_value = round(cost * roas_actual, 2)
        avg_order = random.uniform(45, 120)
        conversions = round(conv_value / avg_order, 2) if avg_order > 0 else 0.0

    if status == "PAUSED":
        sis = round(random.uniform(0.10, 0.30), 4)
    else:
        sis = round(random.uniform(0.30, 0.90), 4)

    top_is = round(random.uniform(0.15, sis * 0.85), 4)
    abs_top_is = round(random.uniform(0.05, top_is * 0.75), 4)
    click_share = round(random.uniform(sis * 0.40, sis * 0.90), 4)

    all_conv_ratio = random.uniform(1.05, 1.15)
    all_conversions = round(conversions * all_conv_ratio, 2)
    all_conversions_value = round(conv_value * all_conv_ratio, 2)

    return {
        "customer_id": CUSTOMER_ID,
        "snapshot_date": snapshot_date,
        "campaign_id": campaign["id"],
        "campaign_name": campaign["name"],
        "campaign_priority": campaign["priority"],
        "enable_local": False,
        "feed_label": "US",
        "country_of_sale": "US",
        "impressions": impressions,
        "clicks": clicks,
        "cost_micros": int(cost * 1_000_000),
        "conversions": conversions,
        "conversions_value": round(conv_value, 2),
        "campaign_status": status,
        "channel_type": "SHOPPING",
        "all_conversions": all_conversions,
        "all_conversions_value": all_conversions_value,
        "search_impression_share": sis,
        "search_top_impression_share": top_is,
        "search_absolute_top_impression_share": abs_top_is,
        "click_share": click_share,
        "optimization_score": round(random.uniform(0.50, 0.95), 4),
        "bid_strategy_type": random.choice(BID_STRATEGY_TYPES),
    }


def generate_products(campaigns):
    """Generate 100 products distributed across campaigns."""
    products = []
    product_counter = 1
    products_per_campaign = 100 // len(campaigns)

    for campaign in campaigns:
        for i in range(products_per_campaign):
            category = random.choice(CATEGORIES)
            brand = random.choice(BRANDS)
            product_type_l1 = random.choice(PRODUCT_TYPES_L1[category])

            product = {
                "id": f"prod_{product_counter:04d}",
                "title": f"{brand} {product_type_l1} - Model {random.randint(100, 999)}",
                "brand": brand,
                "category": category,
                "type_l1": product_type_l1,
                "type_l2": f"{product_type_l1} Subcategory",
                "price_micros": random.randint(10000000, 500000000),
                "sale_price_micros": None,
                "availability": random.choices(
                    ["IN_STOCK", "OUT_OF_STOCK", "PREORDER"],
                    weights=[85, 10, 5]
                )[0],
                "condition": random.choices(
                    ["NEW", "USED", "REFURBISHED"],
                    weights=[90, 8, 2]
                )[0],
                "custom_label_0": random.choice(CUSTOM_LABELS_MARGIN),
                "custom_label_1": random.choice(CUSTOM_LABELS_SEASONALITY),
                "campaign_id": campaign["id"],
                "ad_group_id": str(int(campaign["id"]) + 10000),
            }

            if random.random() < 0.15:
                product["sale_price_micros"] = int(product["price_micros"] * 0.8)

            products.append(product)
            product_counter += 1

    # Fill to exactly 100
    while len(products) < 100:
        category = random.choice(CATEGORIES)
        brand = random.choice(BRANDS)
        product_type_l1 = random.choice(PRODUCT_TYPES_L1[category])
        campaign = random.choice(campaigns)

        product = {
            "id": f"prod_{product_counter:04d}",
            "title": f"{brand} {product_type_l1} - Model {random.randint(100, 999)}",
            "brand": brand,
            "category": category,
            "type_l1": product_type_l1,
            "type_l2": f"{product_type_l1} Subcategory",
            "price_micros": random.randint(10000000, 500000000),
            "sale_price_micros": None,
            "availability": "IN_STOCK",
            "condition": "NEW",
            "custom_label_0": random.choice(CUSTOM_LABELS_MARGIN),
            "custom_label_1": random.choice(CUSTOM_LABELS_SEASONALITY),
            "campaign_id": campaign["id"],
            "ad_group_id": str(int(campaign["id"]) + 10000),
        }
        products.append(product)
        product_counter += 1

    return products


def generate_product_day(product: dict, snapshot_date: date, run_id: str, ingested_at: datetime) -> tuple:
    """Generate one day of product performance data - returns tuple for direct insert."""
    random.seed(hash(product["id"] + str(snapshot_date)))
    scenario = random.random()

    if scenario < 0.10:
        # 10% - Best sellers
        impressions = random.randint(500, 2000)
        clicks = int(impressions * random.uniform(0.03, 0.05))
        cost_micros = clicks * random.randint(800000, 1500000)
        conversions = clicks * random.uniform(0.05, 0.10)
        conversion_value = conversions * (product["price_micros"] / 1000000)
    elif scenario < 0.20:
        # 10% - Underperformers
        impressions = random.randint(100, 500)
        clicks = int(impressions * random.uniform(0.01, 0.02))
        cost_micros = clicks * random.randint(1500000, 3000000)
        conversions = clicks * random.uniform(0.005, 0.01)
        conversion_value = conversions * (product["price_micros"] / 1000000)
    elif scenario < 0.30 and product["availability"] == "OUT_OF_STOCK":
        # 10% - Out of stock (wasted spend)
        impressions = random.randint(50, 200)
        clicks = int(impressions * random.uniform(0.01, 0.02))
        cost_micros = clicks * random.randint(500000, 1000000)
        conversions = 0
        conversion_value = 0
    else:
        # 70% - Normal performance
        impressions = random.randint(100, 800)
        clicks = int(impressions * random.uniform(0.015, 0.025))
        cost_micros = clicks * random.randint(600000, 1200000)
        conversions = clicks * random.uniform(0.02, 0.04)
        conversion_value = conversions * (product["price_micros"] / 1000000)

    ctr = clicks / impressions if impressions > 0 else 0
    cpc = (cost_micros / 1000000) / clicks if clicks > 0 else 0
    roas = (conversion_value / (cost_micros / 1000000)) if cost_micros > 0 else 0
    benchmark_ctr = random.uniform(0.015, 0.030)

    # Return tuple in exact column order for raw_product_performance_daily
    return (
        run_id,                             # 1
        ingested_at,                        # 2
        CUSTOMER_ID,                        # 3
        snapshot_date,                      # 4
        product["campaign_id"],             # 5
        product["ad_group_id"],             # 6
        product["id"],                      # 7
        product["title"],                   # 8
        product["brand"],                   # 9
        product["category"],                # 10
        product["type_l1"],                 # 11
        product["type_l2"],                 # 12
        product["price_micros"],            # 13
        product["sale_price_micros"],       # 14
        product["availability"],            # 15
        product["condition"],               # 16
        product["custom_label_0"],          # 17
        product["custom_label_1"],          # 18
        impressions,                        # 19
        clicks,                             # 20
        cost_micros,                        # 21
        conversions,                        # 22
        conversion_value,                   # 23
        ctr,                                # 24
        cpc,                                # 25
        roas,                               # 26
        benchmark_ctr,                      # 27
    )


def main():
    print("=" * 70)
    print("CHRISTOPHER HOOLE SHOPPING DATA GENERATOR (CORRECTED)")
    print("=" * 70)
    print(f"Customer ID: {CUSTOMER_ID}")
    print(f"Client: {CLIENT_ID}")
    print(f"Date Range: {START_DATE} to {END_DATE} ({DAYS} days)")
    print(f"Campaigns: {len(CAMPAIGNS)}")
    print(f"Products: 100")
    print("=" * 70)
    print()

    # Generate run metadata
    run_id = str(uuid.uuid4())
    ingested_at = datetime.now()
    print(f"Run ID: {run_id}")
    print(f"Ingested At: {ingested_at}")
    print()

    try:
        conn = duckdb.connect(DB_PATH)

        # ── PART 1: SHOPPING CAMPAIGNS ───────────────────────────────────────
        print("PART 1: SHOPPING CAMPAIGNS")
        print("-" * 70)

        # Add columns if needed
        print("1.1 Ensuring all columns exist...")
        new_cols = [
            ("campaign_status", "VARCHAR"),
            ("channel_type", "VARCHAR"),
            ("all_conversions", "DOUBLE"),
            ("all_conversions_value", "DOUBLE"),
            ("search_impression_share", "DOUBLE"),
            ("search_top_impression_share", "DOUBLE"),
            ("search_absolute_top_impression_share", "DOUBLE"),
            ("click_share", "DOUBLE"),
            ("optimization_score", "DOUBLE"),
            ("bid_strategy_type", "VARCHAR"),
        ]
        for col_name, col_type in new_cols:
            conn.execute(
                f"ALTER TABLE analytics.shopping_campaign_daily "
                f"ADD COLUMN IF NOT EXISTS {col_name} {col_type}"
            )
        print("    ✅ All columns verified\n")

        # Delete existing
        print(f"1.2 Deleting existing rows for customer {CUSTOMER_ID}...")
        deleted = conn.execute(
            "DELETE FROM analytics.shopping_campaign_daily WHERE customer_id = ?",
            [CUSTOMER_ID]
        ).rowcount
        print(f"    Deleted {deleted} existing rows\n")

        # Generate campaign data
        print(f"1.3 Generating {len(CAMPAIGNS)} campaigns × {DAYS} days...")
        campaign_rows = []
        for day_index in range(DAYS):
            snap = START_DATE + timedelta(days=day_index)
            for camp in CAMPAIGNS:
                campaign_rows.append(generate_campaign_day(camp, snap, day_index))
            if (day_index + 1) % 30 == 0:
                print(f"    Progress: {day_index + 1}/{DAYS} days...")
        print(f"    ✅ Generated {len(campaign_rows)} rows\n")

        # Insert campaign data
        print("1.4 Inserting campaign data...")
        CAMP_COLS = [
            "customer_id", "snapshot_date", "campaign_id", "campaign_name",
            "campaign_priority", "enable_local", "feed_label", "country_of_sale",
            "impressions", "clicks", "cost_micros", "conversions", "conversions_value",
            "campaign_status", "channel_type",
            "all_conversions", "all_conversions_value",
            "search_impression_share", "search_top_impression_share",
            "search_absolute_top_impression_share", "click_share",
            "optimization_score", "bid_strategy_type",
        ]
        tuples = [tuple(r[c] for c in CAMP_COLS) for r in campaign_rows]
        placeholders = ", ".join(["?"] * len(CAMP_COLS))
        cols_sql = ", ".join(CAMP_COLS)
        conn.executemany(
            f"INSERT INTO analytics.shopping_campaign_daily ({cols_sql}) VALUES ({placeholders})",
            tuples
        )
        print(f"    ✅ Inserted {len(campaign_rows)} rows\n")

        # Verify campaigns
        total_camp = conn.execute(
            "SELECT COUNT(*) FROM analytics.shopping_campaign_daily WHERE customer_id = ?",
            [CUSTOMER_ID]
        ).fetchone()[0]
        enabled_camp = conn.execute(
            "SELECT COUNT(*) FROM analytics.shopping_campaign_daily WHERE customer_id = ? AND campaign_status = 'ENABLED'",
            [CUSTOMER_ID]
        ).fetchone()[0]
        avg_roas = conn.execute(
            """SELECT AVG(CASE WHEN cost_micros > 0
                        THEN conversions_value / (cost_micros / 1000000.0)
                        ELSE NULL END)
               FROM analytics.shopping_campaign_daily WHERE customer_id = ?""",
            [CUSTOMER_ID]
        ).fetchone()[0]

        print(f"1.5 Verification:")
        print(f"    Total rows: {total_camp}")
        print(f"    ENABLED rows: {enabled_camp}")
        print(f"    Average ROAS: {avg_roas:.2f}" if avg_roas else "    Average ROAS: N/A")
        print()

        # ── PART 2: PRODUCTS ──────────────────────────────────────────────────
        print("PART 2: PRODUCTS")
        print("-" * 70)

        print("2.1 Generating 100 products...")
        products = generate_products(CAMPAIGNS)
        
        # Product distribution summary
        brands_count = {}
        categories_count = {}
        availability_count = {}
        for p in products:
            brands_count[p["brand"]] = brands_count.get(p["brand"], 0) + 1
            categories_count[p["category"]] = categories_count.get(p["category"], 0) + 1
            availability_count[p["availability"]] = availability_count.get(p["availability"], 0) + 1
        
        print(f"    ✅ Generated {len(products)} products")
        print(f"    Brands: {len(brands_count)} unique")
        print(f"    Categories: {len(categories_count)} unique")
        print(f"    Availability: IN_STOCK={availability_count.get('IN_STOCK', 0)}, "
              f"OUT_OF_STOCK={availability_count.get('OUT_OF_STOCK', 0)}, "
              f"PREORDER={availability_count.get('PREORDER', 0)}")
        print()

        # Delete existing product data
        print(f"2.2 Deleting existing product data for customer {CUSTOMER_ID}...")
        deleted_prod = conn.execute(
            "DELETE FROM raw_product_performance_daily WHERE customer_id = ?",
            [CUSTOMER_ID]
        ).rowcount
        print(f"    Deleted {deleted_prod} existing rows\n")

        # Generate and insert product performance
        print(f"2.3 Generating and inserting {len(products)} products × {DAYS} days...")
        total_inserted = 0
        
        # Insert in batches for better performance
        batch_size = 1000
        batch = []
        
        for day_index in range(DAYS):
            snap = START_DATE + timedelta(days=day_index)
            for product in products:
                batch.append(generate_product_day(product, snap, run_id, ingested_at))
                
                if len(batch) >= batch_size:
                    placeholders_27 = ", ".join(["?"] * 27)
                    conn.executemany(
                        f"INSERT INTO raw_product_performance_daily VALUES ({placeholders_27})",
                        batch
                    )
                    total_inserted += len(batch)
                    batch = []
            
            if (day_index + 1) % 30 == 0:
                print(f"    Progress: {day_index + 1}/{DAYS} days, {total_inserted} rows inserted...")
        
        # Insert remaining batch
        if batch:
            placeholders_27 = ", ".join(["?"] * 27)
            conn.executemany(
                f"INSERT INTO raw_product_performance_daily VALUES ({placeholders_27})",
                batch
            )
            total_inserted += len(batch)
        
        print(f"    ✅ Inserted {total_inserted} rows\n")

        # Verify products
        total_prod = conn.execute(
            "SELECT COUNT(*) FROM raw_product_performance_daily WHERE customer_id = ?",
            [CUSTOMER_ID]
        ).fetchone()[0]
        unique_prod = conn.execute(
            "SELECT COUNT(DISTINCT product_id) FROM raw_product_performance_daily WHERE customer_id = ?",
            [CUSTOMER_ID]
        ).fetchone()[0]
        oos_products = conn.execute(
            "SELECT COUNT(DISTINCT product_id) FROM raw_product_performance_daily WHERE customer_id = ? AND availability = 'OUT_OF_STOCK'",
            [CUSTOMER_ID]
        ).fetchone()[0]
        
        print(f"2.4 Verification:")
        print(f"    Total rows: {total_prod}")
        print(f"    Unique products: {unique_prod}")
        print(f"    OUT_OF_STOCK products: {oos_products}")
        print()

        conn.close()

        # ── FINAL SUMMARY ─────────────────────────────────────────────────────
        print("=" * 70)
        print("GENERATION COMPLETE")
        print("=" * 70)
        print(f"✅ Campaign data: {total_camp} rows in analytics.shopping_campaign_daily")
        print(f"✅ Product data: {total_prod} rows in raw_product_performance_daily")
        print()
        print("NEXT STEPS:")
        print("1. Copy to readonly DB:")
        print("   Copy-Item -Force warehouse.duckdb warehouse_readonly.duckdb")
        print()
        print("2. Build product features:")
        print("   python act_lighthouse/shopping_features.py")
        print()
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
