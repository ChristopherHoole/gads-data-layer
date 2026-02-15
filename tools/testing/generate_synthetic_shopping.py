"""
Synthetic Shopping Data Generator
Generates realistic Shopping campaign and product data for testing

Creates:
- 5 Shopping campaigns (different priorities)
- 500 products across 20 brands and 10 categories
- 90 days of performance data
- Realistic scenarios: best sellers, underperformers, out-of-stock, etc.
"""

import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path
import duckdb


# Constants
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

CUSTOM_LABELS_MARGIN = ["High Margin", "Medium Margin", "Low Margin", "Clearance"]
CUSTOM_LABELS_SEASONALITY = ["Evergreen", "Summer", "Winter", "Holiday", "Back-to-School"]


class SyntheticShoppingDataGenerator:
    """Generate realistic Shopping data"""
    
    def __init__(self, customer_id: str = 'test_client', db_path: str = "warehouse.duckdb"):
        self.customer_id = customer_id
        self.db_path = Path(db_path)
        self.conn = duckdb.connect(str(self.db_path))
        self.snapshot_date = datetime.now().date()
        self.run_id = str(uuid.uuid4())
        self.ingested_at = datetime.now()
        
    def generate_all(self):
        """Generate complete Shopping dataset"""
        print(f"\n{'='*60}")
        print(f"SYNTHETIC SHOPPING DATA GENERATOR")
        print(f"Customer ID: {self.customer_id}")
        print(f"Run ID: {self.run_id}")
        print(f"{'='*60}\n")
        
        # Step 1: Generate Shopping campaigns
        campaigns = self.generate_shopping_campaigns()
        
        # Step 2: Generate products
        products = self.generate_products(campaigns)
        
        # Step 3: Generate 90 days of product performance
        self.generate_product_performance(products, campaigns)
        
        # Step 4: Generate feed quality data
        self.generate_feed_quality(products)
        
        print(f"\n{'='*60}")
        print("SYNTHETIC DATA GENERATION COMPLETE")
        print(f"{'='*60}\n")
        
        self.conn.close()
        
    def generate_shopping_campaigns(self):
        """Generate 5 Shopping campaigns with different priorities"""
        print("📊 Generating Shopping campaigns...")
        
        campaigns = [
            {
                'id': 9000001,
                'name': 'Shopping - High Priority - All Products',
                'priority': 2,  # High
                'enable_local': False,
                'feed_label': 'primary_feed',
                'country': 'US'
            },
            {
                'id': 9000002,
                'name': 'Shopping - Medium Priority - Brands',
                'priority': 1,  # Medium
                'enable_local': False,
                'feed_label': 'primary_feed',
                'country': 'US'
            },
            {
                'id': 9000003,
                'name': 'Shopping - Low Priority - Clearance',
                'priority': 0,  # Low
                'enable_local': False,
                'feed_label': 'clearance_feed',
                'country': 'US'
            },
            {
                'id': 9000004,
                'name': 'Shopping - Local Inventory',
                'priority': 2,  # High
                'enable_local': True,
                'feed_label': 'local_feed',
                'country': 'US'
            },
            {
                'id': 9000005,
                'name': 'Shopping - Performance Max',
                'priority': 1,  # Medium
                'enable_local': False,
                'feed_label': 'pmax_feed',
                'country': 'US'
            }
        ]
        
        # Insert campaign data (90 days)
        for day_offset in range(90):
            snapshot = self.snapshot_date - timedelta(days=day_offset)
            
            for campaign in campaigns:
                # Realistic performance (varies by priority)
                base_impressions = 1000 * (campaign['priority'] + 1)
                impressions = random.randint(int(base_impressions * 0.8), int(base_impressions * 1.2))
                clicks = int(impressions * random.uniform(0.01, 0.03))
                cost_micros = clicks * random.randint(500000, 2000000)  # $0.50 - $2.00 CPC
                conversions = clicks * random.uniform(0.02, 0.05)
                conversion_value = conversions * random.uniform(50, 150)
                ctr = clicks / impressions if impressions > 0 else 0
                cpc = (cost_micros / 1000000) / clicks if clicks > 0 else 0
                roas = (conversion_value / (cost_micros / 1000000)) if cost_micros > 0 else 0
                
                self.conn.execute("""
                    INSERT INTO raw_shopping_campaign_daily VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    self.run_id,
                    self.ingested_at,
                    self.customer_id,
                    snapshot,
                    campaign['id'],
                    campaign['name'],
                    campaign['priority'],
                    campaign['enable_local'],
                    campaign['feed_label'],
                    campaign['country'],
                    impressions,
                    clicks,
                    cost_micros,
                    conversions,
                    conversion_value,
                    ctr,
                    cpc,
                    roas
                ))
        
        print(f"   ✅ Generated {len(campaigns)} Shopping campaigns × 90 days = {len(campaigns) * 90} records\n")
        return campaigns
        
    def generate_products(self, campaigns):
        """Generate 500 products"""
        print("📦 Generating 500 products...")
        
        products = []
        product_counter = 1
        
        # Distribute products across campaigns
        products_per_campaign = 500 // len(campaigns)
        
        for campaign in campaigns:
            for i in range(products_per_campaign):
                category = random.choice(CATEGORIES)
                brand = random.choice(BRANDS)
                product_type_l1 = random.choice(PRODUCT_TYPES_L1[category])
                
                product = {
                    'id': f"PROD_{product_counter:05d}",
                    'title': f"{brand} {product_type_l1} - Model {random.randint(100, 999)}",
                    'brand': brand,
                    'category': category,
                    'type_l1': product_type_l1,
                    'type_l2': f"{product_type_l1} Subcategory",
                    'price_micros': random.randint(10000000, 500000000),  # $10 - $500
                    'sale_price_micros': None,
                    'availability': random.choices(
                        ['IN_STOCK', 'OUT_OF_STOCK', 'PREORDER'],
                        weights=[85, 10, 5]
                    )[0],
                    'condition': random.choices(
                        ['NEW', 'USED', 'REFURBISHED'],
                        weights=[90, 8, 2]
                    )[0],
                    'custom_label_0': random.choice(CUSTOM_LABELS_MARGIN),
                    'custom_label_1': random.choice(CUSTOM_LABELS_SEASONALITY),
                    'campaign_id': campaign['id'],
                    'ad_group_id': campaign['id'] + 10000
                }
                
                # 15% of products have sale price
                if random.random() < 0.15:
                    product['sale_price_micros'] = int(product['price_micros'] * 0.8)
                
                products.append(product)
                product_counter += 1
        
        # Add remaining products to fill 500
        while len(products) < 500:
            category = random.choice(CATEGORIES)
            brand = random.choice(BRANDS)
            product_type_l1 = random.choice(PRODUCT_TYPES_L1[category])
            campaign = random.choice(campaigns)
            
            product = {
                'id': f"PROD_{product_counter:05d}",
                'title': f"{brand} {product_type_l1} - Model {random.randint(100, 999)}",
                'brand': brand,
                'category': category,
                'type_l1': product_type_l1,
                'type_l2': f"{product_type_l1} Subcategory",
                'price_micros': random.randint(10000000, 500000000),
                'sale_price_micros': None,
                'availability': 'IN_STOCK',
                'condition': 'NEW',
                'custom_label_0': random.choice(CUSTOM_LABELS_MARGIN),
                'custom_label_1': random.choice(CUSTOM_LABELS_SEASONALITY),
                'campaign_id': campaign['id'],
                'ad_group_id': campaign['id'] + 10000
            }
            products.append(product)
            product_counter += 1
        
        print(f"   ✅ Generated {len(products)} products\n")
        return products
        
    def generate_product_performance(self, products, campaigns):
        """Generate 90 days of product performance data"""
        print("📈 Generating 90 days of product performance...")
        
        total_records = 0
        
        for day_offset in range(90):
            snapshot = self.snapshot_date - timedelta(days=day_offset)
            
            for product in products:
                # Determine product scenario
                random.seed(hash(product['id']))
                scenario = random.random()
                
                if scenario < 0.10:
                    # 10% - Best sellers (high performance)
                    impressions = random.randint(500, 2000)
                    clicks = int(impressions * random.uniform(0.03, 0.05))
                    cost_micros = clicks * random.randint(800000, 1500000)
                    conversions = clicks * random.uniform(0.05, 0.10)
                    conversion_value = conversions * (product['price_micros'] / 1000000)
                    
                elif scenario < 0.20:
                    # 10% - Underperformers (low ROAS)
                    impressions = random.randint(100, 500)
                    clicks = int(impressions * random.uniform(0.01, 0.02))
                    cost_micros = clicks * random.randint(1500000, 3000000)
                    conversions = clicks * random.uniform(0.005, 0.01)
                    conversion_value = conversions * (product['price_micros'] / 1000000)
                    
                elif scenario < 0.30 and product['availability'] == 'OUT_OF_STOCK':
                    # 10% - Out of stock (wasted spend)
                    impressions = random.randint(50, 200)
                    clicks = int(impressions * random.uniform(0.01, 0.02))
                    cost_micros = clicks * random.randint(500000, 1000000)
                    conversions = 0  # No conversions when OOS
                    conversion_value = 0
                    
                else:
                    # 70% - Normal performance
                    impressions = random.randint(100, 800)
                    clicks = int(impressions * random.uniform(0.015, 0.025))
                    cost_micros = clicks * random.randint(600000, 1200000)
                    conversions = clicks * random.uniform(0.02, 0.04)
                    conversion_value = conversions * (product['price_micros'] / 1000000)
                
                ctr = clicks / impressions if impressions > 0 else 0
                cpc = (cost_micros / 1000000) / clicks if clicks > 0 else 0
                roas = (conversion_value / (cost_micros / 1000000)) if cost_micros > 0 else 0
                benchmark_ctr = random.uniform(0.015, 0.030)  # Industry benchmark
                
                self.conn.execute("""
                    INSERT INTO raw_product_performance_daily VALUES 
                    (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    self.run_id,
                    self.ingested_at,
                    self.customer_id,
                    snapshot,
                    product['campaign_id'],
                    product['ad_group_id'],
                    product['id'],
                    product['title'],
                    product['brand'],
                    product['category'],
                    product['type_l1'],
                    product['type_l2'],
                    product['price_micros'],
                    product['sale_price_micros'],
                    product['availability'],
                    product['condition'],
                    product['custom_label_0'],
                    product['custom_label_1'],
                    impressions,
                    clicks,
                    cost_micros,
                    conversions,
                    conversion_value,
                    ctr,
                    cpc,
                    roas,
                    benchmark_ctr
                ))
                
                total_records += 1
        
        print(f"   ✅ Generated {total_records} product performance records ({len(products)} × 90 days)\n")
        
    def generate_feed_quality(self, products):
        """Generate feed quality data using merchant_center mock"""
        print("🔍 Generating feed quality data...")
        
        # Import and run mock
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))
        
        from merchant_center.feed_mock import MerchantCenterMock
        
        product_ids = [p['id'] for p in products]
        mock = MerchantCenterMock(customer_id=self.customer_id, db_path=self.db_path)
        mock.generate_feed_quality(product_ids)


def main():
    """Generate complete synthetic Shopping dataset"""
    generator = SyntheticShoppingDataGenerator(customer_id='test_client')
    generator.generate_all()
    
    # Verification
    conn = duckdb.connect("warehouse.duckdb")
    
    shopping_campaigns = conn.execute("SELECT COUNT(*) FROM raw_shopping_campaign_daily").fetchone()[0]
    products = conn.execute("SELECT COUNT(DISTINCT product_id) FROM raw_product_performance_daily").fetchone()[0]
    product_records = conn.execute("SELECT COUNT(*) FROM raw_product_performance_daily").fetchone()[0]
    feed_quality = conn.execute("SELECT COUNT(*) FROM raw_product_feed_quality").fetchone()[0]
    
    print(f"\n📋 VERIFICATION:")
    print(f"   Shopping campaign records: {shopping_campaigns}")
    print(f"   Unique products: {products}")
    print(f"   Product performance records: {product_records}")
    print(f"   Feed quality records: {feed_quality}\n")
    
    conn.close()


if __name__ == '__main__':
    main()
