-- Shopping & Feed Optimization Schema
-- Creates 3 tables for Shopping campaign analysis
-- Part of Chat 12: Shopping optimization module

-- =============================================================================
-- TABLE 1: Shopping Campaign Daily Performance
-- =============================================================================

CREATE TABLE IF NOT EXISTS raw_shopping_campaign_daily (
    run_id VARCHAR,
    ingested_at TIMESTAMP,
    customer_id VARCHAR NOT NULL,
    snapshot_date DATE NOT NULL,
    campaign_id BIGINT NOT NULL,
    campaign_name VARCHAR NOT NULL,
    campaign_priority INTEGER,  -- 0=Low, 1=Medium, 2=High
    enable_local BOOLEAN,
    feed_label VARCHAR,
    country_of_sale VARCHAR,
    impressions BIGINT DEFAULT 0,
    clicks BIGINT DEFAULT 0,
    cost_micros BIGINT DEFAULT 0,
    conversions DOUBLE DEFAULT 0,
    conversions_value DOUBLE DEFAULT 0,
    ctr DOUBLE DEFAULT 0,
    cpc DOUBLE DEFAULT 0,
    roas DOUBLE DEFAULT 0
);

-- Index for fast lookups
CREATE INDEX IF NOT EXISTS idx_shopping_campaign_date 
ON raw_shopping_campaign_daily(customer_id, snapshot_date);

CREATE INDEX IF NOT EXISTS idx_shopping_campaign_priority 
ON raw_shopping_campaign_daily(campaign_priority, roas);


-- =============================================================================
-- TABLE 2: Product Performance Daily
-- =============================================================================

CREATE TABLE IF NOT EXISTS raw_product_performance_daily (
    run_id VARCHAR,
    ingested_at TIMESTAMP,
    customer_id VARCHAR NOT NULL,
    snapshot_date DATE NOT NULL,
    campaign_id BIGINT NOT NULL,
    ad_group_id BIGINT NOT NULL,
    product_id VARCHAR NOT NULL,  -- Merchant Center product ID
    product_title VARCHAR,
    product_brand VARCHAR,
    product_category VARCHAR,
    product_type_l1 VARCHAR,  -- Product type tier 1
    product_type_l2 VARCHAR,  -- Product type tier 2
    product_price_micros BIGINT,
    product_sale_price_micros BIGINT,
    availability VARCHAR,  -- IN_STOCK, OUT_OF_STOCK, PREORDER
    condition VARCHAR,  -- NEW, USED, REFURBISHED
    custom_label_0 VARCHAR,  -- e.g., Margin tier
    custom_label_1 VARCHAR,  -- e.g., Seasonality
    impressions BIGINT DEFAULT 0,
    clicks BIGINT DEFAULT 0,
    cost_micros BIGINT DEFAULT 0,
    conversions DOUBLE DEFAULT 0,
    conversions_value DOUBLE DEFAULT 0,
    ctr DOUBLE DEFAULT 0,
    cpc DOUBLE DEFAULT 0,
    roas DOUBLE DEFAULT 0,
    benchmark_ctr DOUBLE DEFAULT 0  -- Industry benchmark from Google
);

-- Indexes for fast queries
CREATE INDEX IF NOT EXISTS idx_product_perf_date 
ON raw_product_performance_daily(customer_id, snapshot_date);

CREATE INDEX IF NOT EXISTS idx_product_id 
ON raw_product_performance_daily(product_id);

CREATE INDEX IF NOT EXISTS idx_product_brand_category 
ON raw_product_performance_daily(product_brand, product_category);

CREATE INDEX IF NOT EXISTS idx_product_availability 
ON raw_product_performance_daily(availability, roas);

CREATE INDEX IF NOT EXISTS idx_product_roas 
ON raw_product_performance_daily(roas DESC);


-- =============================================================================
-- TABLE 3: Product Feed Quality
-- =============================================================================

CREATE TABLE IF NOT EXISTS raw_product_feed_quality (
    run_id VARCHAR,
    ingested_at TIMESTAMP,
    customer_id VARCHAR NOT NULL,
    merchant_id BIGINT NOT NULL,
    snapshot_date DATE NOT NULL,
    product_id VARCHAR NOT NULL,
    approval_status VARCHAR NOT NULL,  -- APPROVED, DISAPPROVED, PENDING
    disapproval_reasons VARCHAR[],  -- Array of reasons
    missing_attributes VARCHAR[],  -- Array of missing attrs
    price_mismatch BOOLEAN DEFAULT FALSE,
    image_issues VARCHAR[],  -- Array of image problems
    shipping_issues VARCHAR[],  -- Array of shipping problems
    feed_processing_status VARCHAR  -- SUCCESS, FAILURE, PROCESSING
);

-- Indexes for feed quality queries
CREATE INDEX IF NOT EXISTS idx_feed_quality_date 
ON raw_product_feed_quality(customer_id, snapshot_date);

CREATE INDEX IF NOT EXISTS idx_feed_quality_approval 
ON raw_product_feed_quality(approval_status);

CREATE INDEX IF NOT EXISTS idx_feed_quality_issues 
ON raw_product_feed_quality(price_mismatch, approval_status);
