-- Create campaign_metadata table for caching campaign names
-- This ensures campaign names are always available without querying Google Ads API
-- Run: python tools/run_migration.py tools/migrations/create_campaign_metadata.sql

CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS analytics.campaign_metadata (
    customer_id TEXT NOT NULL,
    campaign_id TEXT NOT NULL,
    campaign_name TEXT NOT NULL,
    campaign_status TEXT,  -- ENABLED, PAUSED, REMOVED
    campaign_type TEXT,    -- SEARCH, SHOPPING, PMAX, etc.
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (customer_id, campaign_id)
);

CREATE INDEX IF NOT EXISTS idx_campaign_lookup 
ON analytics.campaign_metadata (customer_id, campaign_id);

-- Insert synthetic data campaign names
INSERT OR REPLACE INTO analytics.campaign_metadata (customer_id, campaign_id, campaign_name, campaign_status, campaign_type)
VALUES
    ('9999999999', '3001', 'Stable ROAS 2.0', 'ENABLED', 'SEARCH'),
    ('9999999999', '3002', 'Stable ROAS 3.0', 'ENABLED', 'SEARCH'),
    ('9999999999', '3003', 'Stable ROAS 4.0', 'ENABLED', 'SEARCH'),
    ('9999999999', '3004', 'Stable ROAS 5.0', 'ENABLED', 'SEARCH'),
    ('9999999999', '3005', 'Growth Strong', 'ENABLED', 'SEARCH'),
    ('9999999999', '3006', 'Growth Moderate', 'ENABLED', 'SEARCH'),
    ('9999999999', '3007', 'Growth Slow', 'ENABLED', 'SEARCH'),
    ('9999999999', '3008', 'Decline Fast', 'ENABLED', 'SEARCH'),
    ('9999999999', '3009', 'Decline Moderate', 'ENABLED', 'SEARCH'),
    ('9999999999', '3010', 'Decline Slow', 'ENABLED', 'SEARCH'),
    ('9999999999', '3011', 'Seasonal High Amplitude', 'ENABLED', 'SEARCH'),
    ('9999999999', '3012', 'Seasonal Low Amplitude', 'ENABLED', 'SEARCH'),
    ('9999999999', '3013', 'Volatile High', 'ENABLED', 'SEARCH'),
    ('9999999999', '3014', 'Volatile Medium', 'ENABLED', 'SEARCH'),
    ('9999999999', '3015', 'Volatile Low', 'ENABLED', 'SEARCH'),
    ('9999999999', '3016', 'Low Data Micro', 'ENABLED', 'SEARCH'),
    ('9999999999', '3017', 'Low Data Small', 'ENABLED', 'SEARCH'),
    ('9999999999', '3018', 'Budget Constrained High', 'ENABLED', 'SEARCH'),
    ('9999999999', '3019', 'Budget Constrained Medium', 'ENABLED', 'SEARCH'),
    ('9999999999', '3020', 'Recovery Turnaround', 'ENABLED', 'SEARCH');
