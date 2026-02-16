"""
Ad Features Module - Chat 11
Computes ad-level features with rolling windows and ad group comparisons.

Features:
- Rolling windows: 7d, 14d, 30d, 90d
- CTR/CVR trends
- Performance vs ad group average
- RSA ad strength tracking
- Days since creation
"""

import duckdb
from datetime import datetime, timedelta
from typing import Dict, List


def build_ad_features_daily(con, customer_id: str, snapshot_date: str):
    """
    Compute ad features for a given snapshot date.
    
    Args:
        con: DuckDB connection (main warehouse.duckdb)
        customer_id: Google Ads customer ID
        snapshot_date: Date to compute features for (YYYY-MM-DD)
    
    Returns:
        List of feature dicts (one per ad)
    """
    print(f"[AdFeatures] Computing ad features for {snapshot_date}...")
    
    # Attach readonly database
    try:
        con.execute("ATTACH 'warehouse_readonly.duckdb' AS ro (READ_ONLY)")
    except:
        pass  # Already attached
    
    # Get date as datetime
    snap_dt = datetime.strptime(snapshot_date, '%Y-%m-%d')
    
    # Define lookback windows
    date_7d = (snap_dt - timedelta(days=7)).strftime('%Y-%m-%d')
    date_14d = (snap_dt - timedelta(days=14)).strftime('%Y-%m-%d')
    date_30d = (snap_dt - timedelta(days=30)).strftime('%Y-%m-%d')
    date_90d = (snap_dt - timedelta(days=90)).strftime('%Y-%m-%d')
    
    # Get all active ads for this customer
    ads = con.execute("""
        SELECT DISTINCT
            ad_id,
            campaign_id,
            campaign_name,
            ad_group_id,
            ad_group_name,
            ad_type,
            ad_status,
            ad_strength,
            headlines,
            descriptions,
            final_url
        FROM ro.analytics.ad_daily
        WHERE customer_id = ?
          AND snapshot_date = ?
          AND ad_status = 'ENABLED'
    """, [customer_id, snapshot_date]).fetchall()
    
    print(f"[AdFeatures] Found {len(ads)} active ads")
    
    # Compute ad group averages (for comparison)
    ad_group_avgs = _compute_ad_group_averages(con, customer_id, snapshot_date)
    
    features = []
    
    for ad in ads:
        (ad_id, campaign_id, campaign_name, ad_group_id, ad_group_name,
         ad_type, ad_status, ad_strength, headlines, descriptions, final_url) = ad
        
        # Get ad group averages
        ag_avg = ad_group_avgs.get(ad_group_id, {})
        ag_avg_ctr_30d = ag_avg.get('ctr_30d', 0.05)  # Default 5% if missing
        ag_avg_cvr_30d = ag_avg.get('cvr_30d', 0.03)  # Default 3% if missing
        
        # Compute rolling window metrics
        metrics_7d = _compute_window_metrics(con, customer_id, ad_id, date_7d, snapshot_date)
        metrics_14d = _compute_window_metrics(con, customer_id, ad_id, date_14d, snapshot_date)
        metrics_30d = _compute_window_metrics(con, customer_id, ad_id, date_30d, snapshot_date)
        metrics_90d = _compute_window_metrics(con, customer_id, ad_id, date_90d, snapshot_date)
        
        # Compute trends (7d vs 30d)
        ctr_trend = metrics_7d['ctr'] - metrics_30d['ctr'] if metrics_7d['ctr'] and metrics_30d['ctr'] else 0
        cvr_trend = metrics_7d['cvr'] - metrics_30d['cvr'] if metrics_7d['cvr'] and metrics_30d['cvr'] else 0
        
        # Performance vs ad group average
        ctr_vs_group = (metrics_30d['ctr'] / ag_avg_ctr_30d) if ag_avg_ctr_30d > 0 and metrics_30d['ctr'] else 1.0
        cvr_vs_group = (metrics_30d['cvr'] / ag_avg_cvr_30d) if ag_avg_cvr_30d > 0 and metrics_30d['cvr'] else 1.0
        
        # Days since creation (estimate from first appearance in data)
        days_since_creation = _get_days_since_creation(con, customer_id, ad_id, snapshot_date)
        
        # Low data flags
        low_data_impressions = metrics_30d['impressions'] < 1000
        low_data_clicks = metrics_30d['clicks'] < 100
        low_data_flag = low_data_impressions or low_data_clicks
        
        # Build feature dict
        feature = {
            # Identity
            'customer_id': customer_id,
            'snapshot_date': snapshot_date,
            'ad_id': ad_id,
            'campaign_id': campaign_id,
            'campaign_name': campaign_name,
            'ad_group_id': ad_group_id,
            'ad_group_name': ad_group_name,
            'ad_type': ad_type,
            'ad_status': ad_status,
            'ad_strength': ad_strength,
            'headlines': headlines,
            'descriptions': descriptions,
            'final_url': final_url,
            
            # 7-day metrics
            'impressions_7d': metrics_7d['impressions'],
            'clicks_7d': metrics_7d['clicks'],
            'cost_micros_7d': metrics_7d['cost_micros'],
            'conversions_7d': metrics_7d['conversions'],
            'conversions_value_7d': metrics_7d['conversions_value'],
            'ctr_7d': metrics_7d['ctr'],
            'cvr_7d': metrics_7d['cvr'],
            'cpa_7d': metrics_7d['cpa'],
            'roas_7d': metrics_7d['roas'],
            
            # 14-day metrics
            'impressions_14d': metrics_14d['impressions'],
            'clicks_14d': metrics_14d['clicks'],
            'cost_micros_14d': metrics_14d['cost_micros'],
            'conversions_14d': metrics_14d['conversions'],
            'conversions_value_14d': metrics_14d['conversions_value'],
            
            # 30-day metrics
            'impressions_30d': metrics_30d['impressions'],
            'clicks_30d': metrics_30d['clicks'],
            'cost_micros_30d': metrics_30d['cost_micros'],
            'conversions_30d': metrics_30d['conversions'],
            'conversions_value_30d': metrics_30d['conversions_value'],
            'ctr_30d': metrics_30d['ctr'],
            'cvr_30d': metrics_30d['cvr'],
            'cpa_30d': metrics_30d['cpa'],
            'roas_30d': metrics_30d['roas'],
            
            # 90-day metrics
            'impressions_90d': metrics_90d['impressions'],
            'clicks_90d': metrics_90d['clicks'],
            'cost_micros_90d': metrics_90d['cost_micros'],
            'conversions_90d': metrics_90d['conversions'],
            'conversions_value_90d': metrics_90d['conversions_value'],
            
            # Trends
            'ctr_trend_7d_vs_30d': ctr_trend,
            'cvr_trend_7d_vs_30d': cvr_trend,
            
            # Performance vs ad group
            'ctr_vs_ad_group': ctr_vs_group,
            'cvr_vs_ad_group': cvr_vs_group,
            '_ad_group_avg_ctr_30d': ag_avg_ctr_30d,
            '_ad_group_avg_cvr_30d': ag_avg_cvr_30d,
            
            # Age
            'days_since_creation': days_since_creation,
            
            # Low data flags
            'low_data_impressions': low_data_impressions,
            'low_data_clicks': low_data_clicks,
            'low_data_flag': low_data_flag,
        }
        
        features.append(feature)
    
    print(f"[AdFeatures] Computed features for {len(features)} ads")
    return features


def _compute_window_metrics(con, customer_id: str, ad_id: int, start_date: str, end_date: str) -> Dict:
    """Compute metrics for a given time window."""
    result = con.execute("""
        SELECT
            COALESCE(SUM(impressions), 0) as impressions,
            COALESCE(SUM(clicks), 0) as clicks,
            COALESCE(SUM(cost_micros), 0) as cost_micros,
            COALESCE(SUM(conversions), 0) as conversions,
            COALESCE(SUM(conversions_value), 0) as conversions_value
        FROM ro.analytics.ad_daily
        WHERE customer_id = ?
          AND ad_id = ?
          AND snapshot_date BETWEEN CAST(? AS DATE) AND CAST(? AS DATE)
    """, [customer_id, ad_id, start_date, end_date]).fetchone()
    
    impressions, clicks, cost_micros, conversions, conversions_value = result
    
    # Calculate rates
    ctr = (clicks / impressions) if impressions > 0 else 0.0
    cvr = (conversions / clicks) if clicks > 0 else 0.0
    cpa = (cost_micros / conversions) if conversions > 0 else 0.0
    roas = (conversions_value / (cost_micros / 1_000_000)) if cost_micros > 0 else 0.0
    
    return {
        'impressions': impressions,
        'clicks': clicks,
        'cost_micros': cost_micros,
        'conversions': conversions,
        'conversions_value': conversions_value,
        'ctr': round(ctr, 4),
        'cvr': round(cvr, 4),
        'cpa': int(cpa),
        'roas': round(roas, 2),
    }


def _compute_ad_group_averages(con, customer_id: str, snapshot_date: str) -> Dict[int, Dict]:
    """
    Compute ad group average CTR and CVR (30-day window).
    Returns dict: {ad_group_id: {'ctr_30d': X, 'cvr_30d': Y}}
    """
    date_30d = (datetime.strptime(snapshot_date, '%Y-%m-%d') - timedelta(days=30)).strftime('%Y-%m-%d')
    
    results = con.execute("""
        SELECT
            ad_group_id,
            COALESCE(SUM(clicks)::DOUBLE / NULLIF(SUM(impressions), 0), 0) as ctr_30d,
            COALESCE(SUM(conversions)::DOUBLE / NULLIF(SUM(clicks), 0), 0) as cvr_30d
        FROM ro.analytics.ad_daily
        WHERE customer_id = ?
          AND snapshot_date BETWEEN CAST(? AS DATE) AND CAST(? AS DATE)
        GROUP BY ad_group_id
    """, [customer_id, date_30d, snapshot_date]).fetchall()
    
    return {
        ad_group_id: {'ctr_30d': ctr, 'cvr_30d': cvr}
        for ad_group_id, ctr, cvr in results
    }


def _get_days_since_creation(con, customer_id: str, ad_id: int, snapshot_date: str) -> int:
    """Get days since ad was first seen in data."""
    first_date = con.execute("""
        SELECT MIN(snapshot_date)
        FROM ro.analytics.ad_daily
        WHERE customer_id = ?
          AND ad_id = ?
    """, [customer_id, ad_id]).fetchone()[0]
    
    if not first_date:
        return 0
    
    snap_dt = datetime.strptime(snapshot_date, '%Y-%m-%d')
    first_dt = datetime.strptime(str(first_date), '%Y-%m-%d')
    
    return (snap_dt - first_dt).days


def save_ad_features(con, features: List[Dict]):
    """Save ad features to warehouse.duckdb."""
    if not features:
        print("[AdFeatures] No features to save")
        return
    
    # Create table if not exists
    con.execute("""
        CREATE TABLE IF NOT EXISTS analytics.ad_features_daily (
            customer_id VARCHAR,
            snapshot_date DATE,
            ad_id BIGINT,
            campaign_id BIGINT,
            campaign_name VARCHAR,
            ad_group_id BIGINT,
            ad_group_name VARCHAR,
            ad_type VARCHAR,
            ad_status VARCHAR,
            ad_strength VARCHAR,
            headlines VARCHAR[],
            descriptions VARCHAR[],
            final_url VARCHAR,
            impressions_7d BIGINT,
            clicks_7d BIGINT,
            cost_micros_7d BIGINT,
            conversions_7d DOUBLE,
            conversions_value_7d DOUBLE,
            ctr_7d DOUBLE,
            cvr_7d DOUBLE,
            cpa_7d BIGINT,
            roas_7d DOUBLE,
            impressions_14d BIGINT,
            clicks_14d BIGINT,
            cost_micros_14d BIGINT,
            conversions_14d DOUBLE,
            conversions_value_14d DOUBLE,
            impressions_30d BIGINT,
            clicks_30d BIGINT,
            cost_micros_30d BIGINT,
            conversions_30d DOUBLE,
            conversions_value_30d DOUBLE,
            ctr_30d DOUBLE,
            cvr_30d DOUBLE,
            cpa_30d BIGINT,
            roas_30d DOUBLE,
            impressions_90d BIGINT,
            clicks_90d BIGINT,
            cost_micros_90d BIGINT,
            conversions_90d DOUBLE,
            conversions_value_90d DOUBLE,
            ctr_trend_7d_vs_30d DOUBLE,
            cvr_trend_7d_vs_30d DOUBLE,
            ctr_vs_ad_group DOUBLE,
            cvr_vs_ad_group DOUBLE,
            days_since_creation INTEGER,
            low_data_impressions BOOLEAN,
            low_data_clicks BOOLEAN,
            low_data_flag BOOLEAN,
            PRIMARY KEY (customer_id, snapshot_date, ad_id)
        )
    """)
    
    # Delete existing data for this snapshot
    customer_id = features[0]['customer_id']
    snapshot_date = features[0]['snapshot_date']
    
    con.execute("""
        DELETE FROM analytics.ad_features_daily
        WHERE customer_id = ? AND snapshot_date = ?
    """, [customer_id, snapshot_date])
    
    # Insert features
    con.executemany("""
        INSERT INTO analytics.ad_features_daily VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?, ?
        )
    """, [
        (f['customer_id'], f['snapshot_date'], f['ad_id'], f['campaign_id'], f['campaign_name'],
         f['ad_group_id'], f['ad_group_name'], f['ad_type'], f['ad_status'], f['ad_strength'],
         f['headlines'], f['descriptions'], f['final_url'],
         f['impressions_7d'], f['clicks_7d'], f['cost_micros_7d'], f['conversions_7d'], f['conversions_value_7d'],
         f['ctr_7d'], f['cvr_7d'], f['cpa_7d'], f['roas_7d'],
         f['impressions_14d'], f['clicks_14d'], f['cost_micros_14d'], f['conversions_14d'], f['conversions_value_14d'],
         f['impressions_30d'], f['clicks_30d'], f['cost_micros_30d'], f['conversions_30d'], f['conversions_value_30d'],
         f['ctr_30d'], f['cvr_30d'], f['cpa_30d'], f['roas_30d'],
         f['impressions_90d'], f['clicks_90d'], f['cost_micros_90d'], f['conversions_90d'], f['conversions_value_90d'],
         f['ctr_trend_7d_vs_30d'], f['cvr_trend_7d_vs_30d'],
         f['ctr_vs_ad_group'], f['cvr_vs_ad_group'],
         f['days_since_creation'], f['low_data_impressions'], f['low_data_clicks'], f['low_data_flag'])
        for f in features
    ])
    
    print(f"[AdFeatures] Saved {len(features)} ad features to warehouse.duckdb")


if __name__ == '__main__':
    # Test with synthetic data
    con = duckdb.connect('warehouse.duckdb')
    
    customer_id = '9999999999'
    snapshot_date = '2026-02-15'
    
    features = build_ad_features_daily(con, customer_id, snapshot_date)
    save_ad_features(con, features)
    
    con.close()
    print("✅ Ad features test complete")
