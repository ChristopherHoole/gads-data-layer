-- sql/analytics_views.sql
-- Purpose: stable analytics views for downstream usage

CREATE SCHEMA IF NOT EXISTS analytics;

CREATE OR REPLACE VIEW analytics.campaign_daily AS
SELECT
  run_id,
  ingested_at,
  customer_id,
  snapshot_date,
  campaign_id,
  campaign_name,
  campaign_status,
  channel_type,
  impressions,
  clicks,
  cost_micros,
  cost_micros / 1000000.0 AS cost,
  conversions,
  conversions_value,
  all_conversions,
  all_conversions_value,

  CASE WHEN impressions > 0 THEN clicks * 1.0 / impressions ELSE NULL END AS ctr,
  CASE WHEN clicks > 0 THEN (cost_micros / 1000000.0) / clicks ELSE NULL END AS cpc,
  CASE WHEN impressions > 0 THEN (cost_micros / 1000.0) / impressions ELSE NULL END AS cpm,
  CASE WHEN cost_micros > 0 THEN conversions_value * 1.0 / (cost_micros / 1000000.0) ELSE NULL END AS roas
FROM snap_campaign_daily;
