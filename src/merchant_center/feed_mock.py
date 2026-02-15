"""
Merchant Center Feed Quality Mock Generator
Simulates product feed issues for testing Shopping optimization
Real Merchant Center API integration deferred to Chat 13

CORRECTED VERSION - Uses duckdb directly
"""

import random
import uuid
from datetime import datetime
from pathlib import Path
import duckdb


class MerchantCenterMock:
    """Generate mock product feed quality data"""
    
    # Realistic disapproval reasons
    DISAPPROVAL_REASONS = [
        "Misleading claims in title",
        "Prohibited product - weapons",
        "Adult content violation",
        "Trademark infringement",
        "Counterfeit product detected",
        "Price mismatch with landing page",
        "Image quality too low",
        "Missing GTIN for branded product",
        "Invalid product category"
    ]
    
    # Missing attribute scenarios
    MISSING_ATTRIBUTES = [
        "GTIN",
        "Brand",
        "MPN",
        "Product Type",
        "Google Product Category",
        "Shipping Weight",
        "Size",
        "Color",
        "Age Group",
        "Gender"
    ]
    
    # Image issues
    IMAGE_ISSUES = [
        "Image resolution too low (min 800x800px)",
        "Promotional overlay on main image",
        "Watermark on product image",
        "Image shows blurred product",
        "White background required"
    ]
    
    # Shipping issues
    SHIPPING_ISSUES = [
        "No shipping cost defined for US",
        "Free shipping threshold not clear",
        "Shipping cost exceeds product price",
        "Invalid shipping country code"
    ]
    
    def __init__(self, customer_id: str = 'test_client', db_path: str = "warehouse.duckdb"):
        self.customer_id = customer_id
        self.db_path = Path(db_path)
        self.conn = duckdb.connect(str(self.db_path))
        self.snapshot_date = datetime.now().date()
        self.run_id = str(uuid.uuid4())
        self.ingested_at = datetime.now()
        
    def generate_feed_quality(self, product_ids: list):
        """
        Generate mock feed quality data for product IDs
        
        Scenarios:
        - 85% APPROVED (clean)
        - 5% DISAPPROVED (policy violations)
        - 10% APPROVED but with warnings (price mismatch, missing optional attrs)
        """
        print(f"\n{'='*60}")
        print(f"MERCHANT CENTER MOCK - Feed Quality Generator")
        print(f"Customer ID: {self.customer_id}")
        print(f"Snapshot Date: {self.snapshot_date}")
        print(f"{'='*60}\n")
        
        results = {
            'approved': 0,
            'disapproved': 0,
            'price_mismatch': 0,
            'missing_attrs': 0,
            'image_issues': 0,
            'shipping_issues': 0
        }
        
        for product_id in product_ids:
            # Deterministic randomness based on product_id hash
            random.seed(hash(product_id))
            
            # Determine approval status
            rand = random.random()
            
            if rand < 0.05:
                # 5% DISAPPROVED
                approval_status = 'DISAPPROVED'
                disapproval_reasons = random.sample(self.DISAPPROVAL_REASONS, random.randint(1, 2))
                missing_attrs = []
                price_mismatch = False
                image_issues = []
                shipping_issues = []
                results['disapproved'] += 1
                
            elif rand < 0.15:
                # 10% APPROVED with price mismatch
                approval_status = 'APPROVED'
                disapproval_reasons = []
                missing_attrs = []
                price_mismatch = True
                image_issues = []
                shipping_issues = []
                results['price_mismatch'] += 1
                results['approved'] += 1
                
            elif rand < 0.23:
                # 8% APPROVED but missing optional attributes
                approval_status = 'APPROVED'
                disapproval_reasons = []
                missing_attrs = random.sample(self.MISSING_ATTRIBUTES, random.randint(1, 3))
                price_mismatch = False
                image_issues = []
                shipping_issues = []
                results['missing_attrs'] += 1
                results['approved'] += 1
                
            elif rand < 0.26:
                # 3% APPROVED but image issues
                approval_status = 'APPROVED'
                disapproval_reasons = []
                missing_attrs = []
                price_mismatch = False
                image_issues = random.sample(self.IMAGE_ISSUES, random.randint(1, 2))
                shipping_issues = []
                results['image_issues'] += 1
                results['approved'] += 1
                
            elif rand < 0.28:
                # 2% APPROVED but shipping issues
                approval_status = 'APPROVED'
                disapproval_reasons = []
                missing_attrs = []
                price_mismatch = False
                image_issues = []
                shipping_issues = random.sample(self.SHIPPING_ISSUES, random.randint(1, 2))
                results['shipping_issues'] += 1
                results['approved'] += 1
                
            else:
                # 72% APPROVED (clean)
                approval_status = 'APPROVED'
                disapproval_reasons = []
                missing_attrs = []
                price_mismatch = False
                image_issues = []
                shipping_issues = []
                results['approved'] += 1
            
            # Feed processing status
            feed_status = 'SUCCESS' if approval_status == 'APPROVED' else 'FAILURE'
            
            # Insert into database
            self.conn.execute("""
                INSERT INTO raw_product_feed_quality 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.run_id,
                self.ingested_at,
                self.customer_id,
                123456789,  # Mock merchant_id
                self.snapshot_date,
                product_id,
                approval_status,
                disapproval_reasons if disapproval_reasons else None,
                missing_attrs if missing_attrs else None,
                price_mismatch,
                image_issues if image_issues else None,
                shipping_issues if shipping_issues else None,
                feed_status
            ))
        
        # Print summary
        print(f"📊 Feed Quality Summary:")
        print(f"   Total products: {len(product_ids)}")
        print(f"   Approved: {results['approved']} ({results['approved']/len(product_ids)*100:.1f}%)")
        print(f"   Disapproved: {results['disapproved']} ({results['disapproved']/len(product_ids)*100:.1f}%)")
        print(f"   Price mismatches: {results['price_mismatch']} ({results['price_mismatch']/len(product_ids)*100:.1f}%)")
        print(f"   Missing attributes: {results['missing_attrs']} ({results['missing_attrs']/len(product_ids)*100:.1f}%)")
        print(f"   Image issues: {results['image_issues']} ({results['image_issues']/len(product_ids)*100:.1f}%)")
        print(f"   Shipping issues: {results['shipping_issues']} ({results['shipping_issues']/len(product_ids)*100:.1f}%)")
        print(f"\n✅ Inserted {len(product_ids)} feed quality records\n")
        
        self.conn.close()
        return results


def main():
    """Test the mock generator with sample products"""
    
    # Generate 100 sample product IDs for testing
    sample_products = [f"PROD_{i:05d}" for i in range(1, 101)]
    
    mock = MerchantCenterMock(customer_id='test_client')
    mock.generate_feed_quality(sample_products)
    
    # Verify insertion
    conn = duckdb.connect("warehouse.duckdb")
    result = conn.execute("SELECT COUNT(*) as cnt FROM raw_product_feed_quality").fetchone()
    print(f"📋 Verification: {result[0]} records in raw_product_feed_quality table")
    conn.close()


if __name__ == '__main__':
    main()
