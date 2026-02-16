"""
Google Ads Data Pipeline - V1 Runner
Extended in Chat 11 to include ad group and ad-level data pulling.

Original: Pulls campaign, keyword, search term data
Chat 11 Addition: Pulls ad group and ad data

Usage:
    python v1_runner.py --mode mock --customer-id 9999999999 --date 2026-02-15
    python v1_runner.py --mode live --customer-id 7372844356 --date 2026-02-15
"""

import argparse
import duckdb
from datetime import datetime, timedelta
from pathlib import Path
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException


def load_google_ads_client(config_path: str = "secrets/google-ads.yaml") -> GoogleAdsClient:
    """Load Google Ads API client from YAML config."""
    return GoogleAdsClient.load_from_storage(config_path)


def pull_campaign_data(customer_id: str, start_date: str, end_date: str, con, mode: str = 'mock'):
    """Pull campaign-level data from Google Ads API."""
    print(f"[v1_runner] Pulling campaign data for customer {customer_id} ({start_date} to {end_date})...")
    
    if mode == 'mock':
        print("[v1_runner] MOCK MODE - No API call, no data inserted")
        return
    
    client = load_google_ads_client()
    ga_service = client.get_service("GoogleAdsService")
    
    query = f"""
        SELECT
            customer.id,
            campaign.id,
            campaign.name,
            campaign.status,
            campaign.bidding_strategy_type,
            campaign_budget.amount_micros,
            campaign.target_cpa.target_cpa_micros,
            campaign.target_roas.target_roas,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions,
            metrics.conversions_value,
            metrics.search_impression_share,
            metrics.search_budget_lost_impression_share,
            metrics.search_rank_lost_impression_share,
            segments.date
        FROM campaign
        WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
          AND campaign.status != 'REMOVED'
    """
    
    try:
        response = ga_service.search(customer_id=customer_id, query=query)
        
        rows_to_insert = []
        for row in response:
            impressions = row.metrics.impressions
            clicks = row.metrics.clicks
            cost_micros = row.metrics.cost_micros
            conversions = row.metrics.conversions
            conversion_value = row.metrics.conversions_value
            
            ctr = (clicks / impressions) if impressions > 0 else 0.0
            cpc = (cost_micros / clicks) if clicks > 0 else 0.0
            cpa = (cost_micros / conversions) if conversions > 0 else 0.0
            roas = (conversion_value / (cost_micros / 1_000_000)) if cost_micros > 0 else 0.0
            
            rows_to_insert.append({
                'customer_id': row.customer.id,
                'campaign_id': row.campaign.id,
                'campaign_name': row.campaign.name,
                'campaign_status': row.campaign.status.name,
                'bidding_strategy': row.campaign.bidding_strategy_type.name,
                'budget_micros': row.campaign_budget.amount_micros,
                'target_cpa_micros': getattr(row.campaign.target_cpa, 'target_cpa_micros', None),
                'target_roas': getattr(row.campaign.target_roas, 'target_roas', None),
                'impressions': impressions,
                'clicks': clicks,
                'cost_micros': cost_micros,
                'conversions': conversions,
                'conversions_value': conversion_value,
                'ctr': ctr,
                'cpc': cpc,
                'cpa': cpa,
                'roas': roas,
                'impression_share': row.metrics.search_impression_share,
                'budget_lost_is': row.metrics.search_budget_lost_impression_share,
                'rank_lost_is': row.metrics.search_rank_lost_impression_share,
                'snapshot_date': row.segments.date
            })
        
        if rows_to_insert:
            con.execute("""
                CREATE TABLE IF NOT EXISTS analytics.campaign_daily (
                    customer_id VARCHAR,
                    snapshot_date DATE,
                    campaign_id BIGINT,
                    campaign_name VARCHAR,
                    campaign_status VARCHAR,
                    bidding_strategy VARCHAR,
                    budget_micros BIGINT,
                    target_cpa_micros BIGINT,
                    target_roas DOUBLE,
                    impressions BIGINT,
                    clicks BIGINT,
                    cost_micros BIGINT,
                    conversions DOUBLE,
                    conversions_value DOUBLE,
                    ctr DOUBLE,
                    cpc DOUBLE,
                    cpa DOUBLE,
                    roas DOUBLE,
                    impression_share DOUBLE,
                    budget_lost_is DOUBLE,
                    rank_lost_is DOUBLE,
                    PRIMARY KEY (customer_id, snapshot_date, campaign_id)
                )
            """)
            
            con.executemany("""
                INSERT OR REPLACE INTO analytics.campaign_daily VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
            """, [
                (r['customer_id'], r['snapshot_date'], r['campaign_id'], r['campaign_name'],
                 r['campaign_status'], r['bidding_strategy'], r['budget_micros'],
                 r['target_cpa_micros'], r['target_roas'],
                 r['impressions'], r['clicks'], r['cost_micros'], r['conversions'], r['conversions_value'],
                 r['ctr'], r['cpc'], r['cpa'], r['roas'],
                 r['impression_share'], r['budget_lost_is'], r['rank_lost_is'])
                for r in rows_to_insert
            ])
            
            print(f"[v1_runner] Inserted {len(rows_to_insert)} campaign rows")
        else:
            print("[v1_runner] No campaign data found")
            
    except Exception as e:
        print(f"[v1_runner] ERROR pulling campaign data: {e}")
        raise


def pull_keyword_data(customer_id: str, start_date: str, end_date: str, con, mode: str = 'mock'):
    """Pull keyword-level data from Google Ads API."""
    print(f"[v1_runner] Pulling keyword data for customer {customer_id} ({start_date} to {end_date})...")
    
    if mode == 'mock':
        print("[v1_runner] MOCK MODE - No API call, no data inserted")
        return
    
    client = load_google_ads_client()
    ga_service = client.get_service("GoogleAdsService")
    
    query = f"""
        SELECT
            customer.id,
            campaign.id,
            campaign.name,
            ad_group.id,
            ad_group.name,
            ad_group_criterion.criterion_id,
            ad_group_criterion.keyword.text,
            ad_group_criterion.keyword.match_type,
            ad_group_criterion.status,
            ad_group_criterion.quality_info.quality_score,
            ad_group_criterion.quality_info.creative_quality_score,
            ad_group_criterion.quality_info.post_click_quality_score,
            ad_group_criterion.quality_info.search_predicted_ctr,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions,
            metrics.conversions_value,
            metrics.average_cpc,
            metrics.ctr,
            segments.date
        FROM keyword_view
        WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
          AND campaign.status != 'REMOVED'
          AND ad_group.status != 'REMOVED'
          AND ad_group_criterion.status != 'REMOVED'
    """
    
    try:
        response = ga_service.search(customer_id=customer_id, query=query)
        
        rows_to_insert = []
        for row in response:
            rows_to_insert.append({
                'customer_id': row.customer.id,
                'campaign_id': row.campaign.id,
                'campaign_name': row.campaign.name,
                'ad_group_id': row.ad_group.id,
                'ad_group_name': row.ad_group.name,
                'keyword_id': row.ad_group_criterion.criterion_id,
                'keyword_text': row.ad_group_criterion.keyword.text,
                'match_type': row.ad_group_criterion.keyword.match_type.name,
                'status': row.ad_group_criterion.status.name,
                'quality_score': row.ad_group_criterion.quality_info.quality_score,
                'quality_score_creative': row.ad_group_criterion.quality_info.creative_quality_score.name,
                'quality_score_landing_page': row.ad_group_criterion.quality_info.post_click_quality_score.name,
                'quality_score_relevance': row.ad_group_criterion.quality_info.search_predicted_ctr.name,
                'impressions': row.metrics.impressions,
                'clicks': row.metrics.clicks,
                'cost_micros': row.metrics.cost_micros,
                'conversions': row.metrics.conversions,
                'conversions_value': row.metrics.conversions_value,
                'average_cpc': row.metrics.average_cpc,
                'ctr': row.metrics.ctr,
                'snapshot_date': row.segments.date
            })
        
        if rows_to_insert:
            con.execute("""
                CREATE TABLE IF NOT EXISTS analytics.keyword_daily (
                    customer_id BIGINT,
                    campaign_id BIGINT,
                    campaign_name VARCHAR,
                    ad_group_id BIGINT,
                    ad_group_name VARCHAR,
                    keyword_id BIGINT,
                    keyword_text VARCHAR,
                    match_type VARCHAR,
                    status VARCHAR,
                    quality_score INTEGER,
                    quality_score_creative VARCHAR,
                    quality_score_landing_page VARCHAR,
                    quality_score_relevance VARCHAR,
                    impressions INTEGER,
                    clicks INTEGER,
                    cost_micros BIGINT,
                    conversions DOUBLE,
                    conversions_value DOUBLE,
                    average_cpc BIGINT,
                    ctr DOUBLE,
                    snapshot_date DATE,
                    PRIMARY KEY (customer_id, keyword_id, snapshot_date)
                )
            """)
            
            con.executemany("""
                INSERT OR REPLACE INTO analytics.keyword_daily VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
            """, [
                (r['customer_id'], r['campaign_id'], r['campaign_name'],
                 r['ad_group_id'], r['ad_group_name'], r['keyword_id'], r['keyword_text'],
                 r['match_type'], r['status'], r['quality_score'],
                 r['quality_score_creative'], r['quality_score_landing_page'], r['quality_score_relevance'],
                 r['impressions'], r['clicks'], r['cost_micros'], r['conversions'], r['conversions_value'],
                 r['average_cpc'], r['ctr'], r['snapshot_date'])
                for r in rows_to_insert
            ])
            
            print(f"[v1_runner] Inserted {len(rows_to_insert)} keyword rows")
        else:
            print("[v1_runner] No keyword data found")
            
    except Exception as e:
        print(f"[v1_runner] ERROR pulling keyword data: {e}")
        raise


def pull_search_term_data(customer_id: str, start_date: str, end_date: str, con, mode: str = 'mock'):
    """Pull search term data from Google Ads API."""
    print(f"[v1_runner] Pulling search term data for customer {customer_id} ({start_date} to {end_date})...")
    
    if mode == 'mock':
        print("[v1_runner] MOCK MODE - No API call, no data inserted")
        return
    
    client = load_google_ads_client()
    ga_service = client.get_service("GoogleAdsService")
    
    query = f"""
        SELECT
            customer.id,
            campaign.id,
            campaign.name,
            ad_group.id,
            ad_group.name,
            ad_group_criterion.criterion_id,
            ad_group_criterion.keyword.text,
            search_term_view.search_term,
            search_term_view.status,
            ad_group_criterion.keyword.match_type,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions,
            metrics.conversions_value,
            segments.date
        FROM search_term_view
        WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
          AND campaign.status != 'REMOVED'
          AND ad_group.status != 'REMOVED'
    """
    
    try:
        response = ga_service.search(customer_id=customer_id, query=query)
        
        rows_to_insert = []
        for row in response:
            rows_to_insert.append({
                'customer_id': row.customer.id,
                'campaign_id': row.campaign.id,
                'campaign_name': row.campaign.name,
                'ad_group_id': row.ad_group.id,
                'ad_group_name': row.ad_group.name,
                'keyword_id': row.ad_group_criterion.criterion_id,
                'keyword_text': row.ad_group_criterion.keyword.text,
                'search_term': row.search_term_view.search_term,
                'search_term_status': row.search_term_view.status.name,
                'match_type': row.ad_group_criterion.keyword.match_type.name,
                'impressions': row.metrics.impressions,
                'clicks': row.metrics.clicks,
                'cost_micros': row.metrics.cost_micros,
                'conversions': row.metrics.conversions,
                'conversions_value': row.metrics.conversions_value,
                'snapshot_date': row.segments.date
            })
        
        if rows_to_insert:
            con.execute("""
                CREATE TABLE IF NOT EXISTS analytics.search_term_daily (
                    customer_id BIGINT,
                    campaign_id BIGINT,
                    campaign_name VARCHAR,
                    ad_group_id BIGINT,
                    ad_group_name VARCHAR,
                    keyword_id BIGINT,
                    keyword_text VARCHAR,
                    search_term VARCHAR,
                    search_term_status VARCHAR,
                    match_type VARCHAR,
                    impressions INTEGER,
                    clicks INTEGER,
                    cost_micros BIGINT,
                    conversions DOUBLE,
                    conversions_value DOUBLE,
                    snapshot_date DATE,
                    PRIMARY KEY (customer_id, campaign_id, ad_group_id, search_term, snapshot_date)
                )
            """)
            
            con.executemany("""
                INSERT OR REPLACE INTO analytics.search_term_daily VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
            """, [
                (r['customer_id'], r['campaign_id'], r['campaign_name'],
                 r['ad_group_id'], r['ad_group_name'], r['keyword_id'], r['keyword_text'],
                 r['search_term'], r['search_term_status'], r['match_type'],
                 r['impressions'], r['clicks'], r['cost_micros'], r['conversions'], r['conversions_value'],
                 r['snapshot_date'])
                for r in rows_to_insert
            ])
            
            print(f"[v1_runner] Inserted {len(rows_to_insert)} search term rows")
        else:
            print("[v1_runner] No search term data found")
            
    except Exception as e:
        print(f"[v1_runner] ERROR pulling search term data: {e}")
        raise


# ============================================================================
# CHAT 11 ADDITIONS - AD GROUP AND AD DATA
# ============================================================================

def pull_ad_group_data(customer_id: str, start_date: str, end_date: str, con, mode: str = 'mock'):
    """
    Pull ad group-level data from Google Ads API.
    
    Metrics: impressions, clicks, cost, conversions, conversion_value
    Structure: ad_group_name, status, type, bids
    """
    print(f"[v1_runner] Pulling ad group data for customer {customer_id} ({start_date} to {end_date})...")
    
    if mode == 'mock':
        print("[v1_runner] MOCK MODE - No API call, no data inserted")
        return
    
    client = load_google_ads_client()
    ga_service = client.get_service("GoogleAdsService")
    
    query = f"""
        SELECT
            customer.id,
            campaign.id,
            campaign.name,
            ad_group.id,
            ad_group.name,
            ad_group.status,
            ad_group.type,
            ad_group.cpc_bid_micros,
            ad_group.target_cpa_micros,
            ad_group.target_roas,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions,
            metrics.conversions_value,
            segments.date
        FROM ad_group
        WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
          AND campaign.status != 'REMOVED'
          AND ad_group.status != 'REMOVED'
    """
    
    try:
        response = ga_service.search(customer_id=customer_id, query=query)
        
        rows_to_insert = []
        for row in response:
            # Calculate derived metrics
            impressions = row.metrics.impressions
            clicks = row.metrics.clicks
            cost_micros = row.metrics.cost_micros
            conversions = row.metrics.conversions
            conversion_value = row.metrics.conversions_value
            
            ctr = (clicks / impressions) if impressions > 0 else 0.0
            cpc = (cost_micros / clicks) if clicks > 0 else 0.0
            cpa = (cost_micros / conversions) if conversions > 0 else 0.0
            roas = (conversion_value / (cost_micros / 1_000_000)) if cost_micros > 0 else 0.0
            
            rows_to_insert.append({
                'customer_id': row.customer.id,
                'campaign_id': row.campaign.id,
                'campaign_name': row.campaign.name,
                'ad_group_id': row.ad_group.id,
                'ad_group_name': row.ad_group.name,
                'ad_group_status': row.ad_group.status.name,
                'ad_group_type': row.ad_group.type_.name,
                'cpc_bid_micros': row.ad_group.cpc_bid_micros if row.ad_group.cpc_bid_micros else None,
                'target_cpa_micros': row.ad_group.target_cpa_micros if row.ad_group.target_cpa_micros else None,
                'target_roas': row.ad_group.target_roas if row.ad_group.target_roas else None,
                'impressions': impressions,
                'clicks': clicks,
                'cost_micros': cost_micros,
                'conversions': conversions,
                'conversions_value': conversion_value,
                'ctr': ctr,
                'cpc': cpc,
                'cpa': cpa,
                'roas': roas,
                'snapshot_date': row.segments.date
            })
        
        if rows_to_insert:
            # Ensure table exists
            con.execute("""
                CREATE TABLE IF NOT EXISTS analytics.ad_group_daily (
                    customer_id VARCHAR,
                    snapshot_date DATE,
                    campaign_id BIGINT,
                    campaign_name VARCHAR,
                    ad_group_id BIGINT,
                    ad_group_name VARCHAR,
                    ad_group_status VARCHAR,
                    ad_group_type VARCHAR,
                    cpc_bid_micros BIGINT,
                    target_cpa_micros BIGINT,
                    target_roas DOUBLE,
                    impressions BIGINT,
                    clicks BIGINT,
                    cost_micros BIGINT,
                    conversions DOUBLE,
                    conversions_value DOUBLE,
                    ctr DOUBLE,
                    cpc DOUBLE,
                    cpa DOUBLE,
                    roas DOUBLE,
                    PRIMARY KEY (customer_id, snapshot_date, ad_group_id)
                )
            """)
            
            # Insert data
            con.executemany("""
                INSERT OR REPLACE INTO analytics.ad_group_daily VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
            """, [
                (r['customer_id'], r['snapshot_date'], r['campaign_id'], r['campaign_name'],
                 r['ad_group_id'], r['ad_group_name'], r['ad_group_status'], r['ad_group_type'],
                 r['cpc_bid_micros'], r['target_cpa_micros'], r['target_roas'],
                 r['impressions'], r['clicks'], r['cost_micros'], r['conversions'], r['conversions_value'],
                 r['ctr'], r['cpc'], r['cpa'], r['roas'])
                for r in rows_to_insert
            ])
            
            print(f"[v1_runner] Inserted {len(rows_to_insert)} ad group rows")
        else:
            print("[v1_runner] No ad group data found")
            
    except Exception as e:
        print(f"[v1_runner] ERROR pulling ad group data: {e}")
        raise


def pull_ad_data(customer_id: str, start_date: str, end_date: str, con, mode: str = 'mock'):
    """
    Pull ad-level data from Google Ads API.
    
    Includes:
    - Ad performance metrics
    - Ad creative details (RSA headlines/descriptions, ETA, etc.)
    - Ad strength (for RSA) - Note: not available in ad_group_ad query, will be None
    - Ad status
    """
    print(f"[v1_runner] Pulling ad data for customer {customer_id} ({start_date} to {end_date})...")
    
    if mode == 'mock':
        print("[v1_runner] MOCK MODE - No API call, no data inserted")
        return
    
    client = load_google_ads_client()
    ga_service = client.get_service("GoogleAdsService")
    
    query = f"""
        SELECT
            customer.id,
            campaign.id,
            campaign.name,
            ad_group.id,
            ad_group.name,
            ad_group_ad.ad.id,
            ad_group_ad.ad.type,
            ad_group_ad.status,
            ad_group_ad.ad.final_urls,
            ad_group_ad.ad.responsive_search_ad.headlines,
            ad_group_ad.ad.responsive_search_ad.descriptions,
            ad_group_ad.policy_summary.approval_status,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions,
            metrics.conversions_value,
            segments.date
        FROM ad_group_ad
        WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
          AND campaign.status != 'REMOVED'
          AND ad_group.status != 'REMOVED'
          AND ad_group_ad.status != 'REMOVED'
    """
    
    try:
        response = ga_service.search(customer_id=customer_id, query=query)
        
        rows_to_insert = []
        for row in response:
            # Calculate derived metrics
            impressions = row.metrics.impressions
            clicks = row.metrics.clicks
            cost_micros = row.metrics.cost_micros
            conversions = row.metrics.conversions
            conversion_value = row.metrics.conversions_value
            
            ctr = (clicks / impressions) if impressions > 0 else 0.0
            cpc = (cost_micros / clicks) if clicks > 0 else 0.0
            cvr = (conversions / clicks) if clicks > 0 else 0.0
            cpa = (cost_micros / conversions) if conversions > 0 else 0.0
            roas = (conversion_value / (cost_micros / 1_000_000)) if cost_micros > 0 else 0.0
            
            # Extract ad creative details
            ad_type = row.ad_group_ad.ad.type_.name
            final_url = row.ad_group_ad.ad.final_urls[0] if row.ad_group_ad.ad.final_urls else None
            
            # RSA-specific fields
            headlines = None
            descriptions = None
            ad_strength = None  # Not available in ad_group_ad query
            
            if ad_type == 'RESPONSIVE_SEARCH_AD':
                rsa = row.ad_group_ad.ad.responsive_search_ad
                if rsa.headlines:
                    headlines = [h.text for h in rsa.headlines]
                if rsa.descriptions:
                    descriptions = [d.text for d in rsa.descriptions]
            
            rows_to_insert.append({
                'customer_id': row.customer.id,
                'campaign_id': row.campaign.id,
                'campaign_name': row.campaign.name,
                'ad_group_id': row.ad_group.id,
                'ad_group_name': row.ad_group.name,
                'ad_id': row.ad_group_ad.ad.id,
                'ad_type': ad_type,
                'ad_status': row.ad_group_ad.status.name,
                'ad_strength': ad_strength,
                'headlines': headlines,
                'descriptions': descriptions,
                'final_url': final_url,
                'impressions': impressions,
                'clicks': clicks,
                'cost_micros': cost_micros,
                'conversions': conversions,
                'conversions_value': conversion_value,
                'ctr': ctr,
                'cpc': cpc,
                'cvr': cvr,
                'cpa': cpa,
                'roas': roas,
                'snapshot_date': row.segments.date
            })
        
        if rows_to_insert:
            # Ensure table exists
            con.execute("""
                CREATE TABLE IF NOT EXISTS analytics.ad_daily (
                    customer_id VARCHAR,
                    snapshot_date DATE,
                    campaign_id BIGINT,
                    campaign_name VARCHAR,
                    ad_group_id BIGINT,
                    ad_group_name VARCHAR,
                    ad_id BIGINT,
                    ad_type VARCHAR,
                    ad_status VARCHAR,
                    ad_strength VARCHAR,
                    headlines VARCHAR[],
                    descriptions VARCHAR[],
                    final_url VARCHAR,
                    impressions BIGINT,
                    clicks BIGINT,
                    cost_micros BIGINT,
                    conversions DOUBLE,
                    conversions_value DOUBLE,
                    ctr DOUBLE,
                    cpc DOUBLE,
                    cvr DOUBLE,
                    cpa DOUBLE,
                    roas DOUBLE,
                    PRIMARY KEY (customer_id, snapshot_date, ad_id)
                )
            """)
            
            # Insert data
            con.executemany("""
                INSERT OR REPLACE INTO analytics.ad_daily VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
            """, [
                (r['customer_id'], r['snapshot_date'], r['campaign_id'], r['campaign_name'],
                 r['ad_group_id'], r['ad_group_name'], r['ad_id'], r['ad_type'], r['ad_status'],
                 r['ad_strength'], r['headlines'], r['descriptions'], r['final_url'],
                 r['impressions'], r['clicks'], r['cost_micros'], r['conversions'], r['conversions_value'],
                 r['ctr'], r['cpc'], r['cvr'], r['cpa'], r['roas'])
                for r in rows_to_insert
            ])
            
            print(f"[v1_runner] Inserted {len(rows_to_insert)} ad rows")
        else:
            print("[v1_runner] No ad data found")
            
    except Exception as e:
        print(f"[v1_runner] ERROR pulling ad data: {e}")
        raise


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main entry point for v1_runner."""
    parser = argparse.ArgumentParser(description="Pull Google Ads data")
    parser.add_argument('--mode', choices=['mock', 'live'], default='mock',
                       help='Run mode: mock (no API calls) or live (real API)')
    parser.add_argument('--customer-id', required=True,
                       help='Google Ads customer ID')
    parser.add_argument('--date', required=True,
                       help='Date to pull data for (YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    # Parse date
    snapshot_date = datetime.strptime(args.date, '%Y-%m-%d')
    start_date = snapshot_date.strftime('%Y-%m-%d')
    end_date = snapshot_date.strftime('%Y-%m-%d')
    
    # Connect to readonly database
    db_path = Path('warehouse_readonly.duckdb')
    print(f"[v1_runner] Connecting to {db_path}...")
    ro_con = duckdb.connect(str(db_path))
    
    # Ensure analytics schema exists
    ro_con.execute("CREATE SCHEMA IF NOT EXISTS analytics")
    
    # Pull all data types
    print(f"\n[v1_runner] ===== PULLING DATA FOR {args.date} =====\n")
    
    pull_campaign_data(args.customer_id, start_date, end_date, ro_con, args.mode)
    pull_keyword_data(args.customer_id, start_date, end_date, ro_con, args.mode)
    pull_search_term_data(args.customer_id, start_date, end_date, ro_con, args.mode)
    
    # CHAT 11 ADDITIONS
    pull_ad_group_data(args.customer_id, start_date, end_date, ro_con, args.mode)
    pull_ad_data(args.customer_id, start_date, end_date, ro_con, args.mode)
    
    # Close connection
    ro_con.close()
    
    print(f"\n[v1_runner] ===== DATA PULL COMPLETE =====\n")
    
    if args.mode == 'mock':
        print("[v1_runner] NOTE: Mock mode - no data actually inserted.")
        print("[v1_runner] Run with --mode live to pull real data from Google Ads API.")


if __name__ == '__main__':
    main()
