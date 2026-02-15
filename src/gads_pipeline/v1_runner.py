"""
Google Ads Data Pipeline - V1 Runner
Pulls campaign, ad group, keyword, ad, and Shopping data from Google Ads API
Stores in DuckDB for analysis

CORRECTED VERSION - Matches project structure with duckdb direct connection
"""

import os
import sys
from datetime import datetime, timedelta
import duckdb
from pathlib import Path
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
import uuid


class GoogleAdsDataPuller:
    """Pull Google Ads data and store in DuckDB"""
    
    def __init__(self, customer_id: str, db_path: str = "warehouse.duckdb"):
        self.customer_id = customer_id.replace('-', '')
        self.client = GoogleAdsClient.load_from_storage()
        self.db_path = Path(db_path)
        self.conn = duckdb.connect(str(self.db_path))
        self.snapshot_date = datetime.now().date()
        self.run_id = str(uuid.uuid4())
        self.ingested_at = datetime.now()
        
    def pull_all_data(self):
        """Pull all data types"""
        print(f"\n{'='*60}")
        print(f"GOOGLE ADS DATA PULL - {self.snapshot_date}")
        print(f"Customer ID: {self.customer_id}")
        print(f"Run ID: {self.run_id}")
        print(f"{'='*60}\n")
        
        try:
            # Pull standard data
            self.pull_campaigns()
            self.pull_ad_groups()
            self.pull_keywords()
            self.pull_ads()
            
            # Pull Shopping data (NEW)
            self.pull_shopping_campaigns()
            self.pull_shopping_products()
            
            print(f"\n{'='*60}")
            print("DATA PULL COMPLETE")
            print(f"{'='*60}\n")
            
        finally:
            self.conn.close()
        
    def pull_campaigns(self):
        """Pull campaign-level data"""
        print("📊 Pulling campaign data...")
        
        query = """
            SELECT
                campaign.id,
                campaign.name,
                campaign.status,
                campaign.advertising_channel_type,
                metrics.impressions,
                metrics.clicks,
                metrics.cost_micros,
                metrics.conversions,
                metrics.conversions_value
            FROM campaign
            WHERE segments.date DURING LAST_90_DAYS
                AND campaign.status != 'REMOVED'
                AND campaign.advertising_channel_type != 'SHOPPING'
        """
        
        rows = self._execute_query(query)
        print(f"   Retrieved {len(rows)} campaign records")
        
        for row in rows:
            campaign = row.campaign
            metrics = row.metrics
            
            self.conn.execute("""
                INSERT INTO raw_campaign_daily VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.run_id,
                self.ingested_at,
                self.customer_id,
                self.snapshot_date,
                campaign.id,
                campaign.name,
                campaign.status.name,
                campaign.advertising_channel_type.name,
                metrics.impressions,
                metrics.clicks,
                metrics.cost_micros,
                metrics.conversions,
                metrics.conversions_value
            ))
        
        print(f"   ✅ Inserted {len(rows)} campaign records\n")
        
    def pull_ad_groups(self):
        """Pull ad group-level data - placeholder"""
        print("📊 Skipping ad group data (not needed for Shopping)\n")
        
    def pull_keywords(self):
        """Pull keyword-level data - placeholder"""
        print("📊 Skipping keyword data (not needed for Shopping)\n")
        
    def pull_ads(self):
        """Pull ad-level data - placeholder"""
        print("📊 Skipping ad data (not needed for Shopping)\n")
        
    def pull_shopping_campaigns(self):
        """Pull Shopping campaign-level data"""
        print("🛒 Pulling Shopping campaign data...")
        
        query = """
            SELECT
                campaign.id,
                campaign.name,
                campaign.shopping_setting.campaign_priority,
                campaign.shopping_setting.enable_local,
                campaign.shopping_setting.feed_label,
                campaign.shopping_setting.sales_country,
                metrics.impressions,
                metrics.clicks,
                metrics.cost_micros,
                metrics.conversions,
                metrics.conversions_value,
                metrics.ctr,
                metrics.average_cpc
            FROM campaign
            WHERE segments.date DURING LAST_90_DAYS
                AND campaign.advertising_channel_type = 'SHOPPING'
                AND campaign.status != 'REMOVED'
        """
        
        try:
            rows = self._execute_query(query)
            print(f"   Retrieved {len(rows)} Shopping campaign records")
            
            for row in rows:
                campaign = row.campaign
                metrics = row.metrics
                shopping = campaign.shopping_setting
                
                # Calculate ROAS
                roas = (metrics.conversions_value / (metrics.cost_micros / 1000000)) if metrics.cost_micros > 0 else 0
                
                self.conn.execute("""
                    INSERT INTO raw_shopping_campaign_daily VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    self.run_id,
                    self.ingested_at,
                    self.customer_id,
                    self.snapshot_date,
                    campaign.id,
                    campaign.name,
                    shopping.campaign_priority if shopping else None,
                    shopping.enable_local if shopping else None,
                    shopping.feed_label if shopping else None,
                    shopping.sales_country if shopping else None,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros,
                    metrics.conversions,
                    metrics.conversions_value,
                    roas
                ))
            
            print(f"   ✅ Inserted {len(rows)} Shopping campaign records\n")
            
        except GoogleAdsException as e:
            print(f"   ⚠️  No Shopping campaigns found or API error\n")
        
    def pull_shopping_products(self):
        """Pull product-level Shopping data"""
        print("🛒 Pulling Shopping product data...")
        
        query = """
            SELECT
                campaign.id,
                ad_group.id,
                segments.product_item_id,
                segments.product_title,
                segments.product_brand,
                segments.product_category_level1,
                segments.product_type_l1,
                segments.product_type_l2,
                segments.product_custom_attribute0,
                segments.product_custom_attribute1,
                shopping_performance_view.benchmark_ctr,
                metrics.impressions,
                metrics.clicks,
                metrics.cost_micros,
                metrics.conversions,
                metrics.conversions_value,
                metrics.ctr,
                metrics.average_cpc
            FROM shopping_performance_view
            WHERE segments.date DURING LAST_90_DAYS
                AND campaign.status != 'REMOVED'
        """
        
        try:
            rows = self._execute_query(query)
            print(f"   Retrieved {len(rows)} product records")
            
            for row in rows:
                campaign = row.campaign
                ad_group = row.ad_group
                segments = row.segments
                metrics = row.metrics
                
                # Calculate ROAS
                roas = (metrics.conversions_value / (metrics.cost_micros / 1000000)) if metrics.cost_micros > 0 else 0
                
                # Note: Price and availability require Merchant Center API (populated by mock)
                
                self.conn.execute("""
                    INSERT INTO raw_product_performance_daily VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    self.run_id,
                    self.ingested_at,
                    self.customer_id,
                    self.snapshot_date,
                    campaign.id,
                    ad_group.id,
                    segments.product_item_id,
                    segments.product_title,
                    segments.product_brand,
                    segments.product_category_level1,
                    segments.product_type_l1,
                    segments.product_type_l2,
                    None,  # product_price_micros (from Merchant Center)
                    None,  # product_sale_price_micros (from Merchant Center)
                    None,  # availability (from Merchant Center)
                    None,  # condition (from Merchant Center)
                    segments.product_custom_attribute0,
                    segments.product_custom_attribute1,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros,
                    metrics.conversions,
                    metrics.conversions_value,
                    metrics.ctr,
                    roas
                ))
            
            print(f"   ✅ Inserted {len(rows)} product records\n")
            
        except GoogleAdsException as e:
            print(f"   ⚠️  No Shopping products found or API error\n")
        
    def _execute_query(self, query: str):
        """Execute GAQL query and return rows"""
        ga_service = self.client.get_service("GoogleAdsService")
        
        request = self.client.get_type("SearchGoogleAdsRequest")
        request.customer_id = self.customer_id
        request.query = query
        
        try:
            response = ga_service.search(request=request)
            return list(response)
        except GoogleAdsException as ex:
            print(f"   ❌ Query failed: {ex}")
            return []


def main():
    """Main execution"""
    customer_id = os.getenv('GOOGLE_ADS_CUSTOMER_ID', '1234567890')
    
    puller = GoogleAdsDataPuller(customer_id)
    puller.pull_all_data()


if __name__ == '__main__':
    main()
