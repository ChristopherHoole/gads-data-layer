-- Performance Optimization Indexes
-- Add indexes to improve query performance across the platform

-- ============================================================================
-- CHANGE_LOG TABLE INDEXES
-- ============================================================================

-- Index for customer + campaign lookups (used by guardrails)
CREATE INDEX IF NOT EXISTS idx_change_log_customer_campaign 
ON analytics.change_log(customer_id, campaign_id);

-- Index for date-based queries (used by Radar monitoring)
CREATE INDEX IF NOT EXISTS idx_change_log_change_date 
ON analytics.change_log(change_date DESC);

-- Index for recent changes queries (dashboard)
CREATE INDEX IF NOT EXISTS idx_change_log_executed_at 
ON analytics.change_log(executed_at DESC);

-- Composite index for cooldown checks (most common query pattern)
CREATE INDEX IF NOT EXISTS idx_change_log_cooldown 
ON analytics.change_log(customer_id, campaign_id, lever, change_date DESC);

-- Index for rollback status monitoring
CREATE INDEX IF NOT EXISTS idx_change_log_rollback_status 
ON analytics.change_log(rollback_status) 
WHERE rollback_status IS NOT NULL;


-- ============================================================================
-- CAMPAIGN_DAILY TABLE INDEXES
-- ============================================================================

-- Composite index for customer + date queries (most common pattern)
CREATE INDEX IF NOT EXISTS idx_campaign_daily_customer_date 
ON analytics.campaign_daily(customer_id, snapshot_date DESC);

-- Composite index for campaign performance queries
CREATE INDEX IF NOT EXISTS idx_campaign_daily_campaign_date 
ON analytics.campaign_daily(campaign_id, snapshot_date DESC);

-- Index for date range queries
CREATE INDEX IF NOT EXISTS idx_campaign_daily_snapshot_date 
ON analytics.campaign_daily(snapshot_date DESC);

-- Composite index for campaign + customer lookups
CREATE INDEX IF NOT EXISTS idx_campaign_daily_customer_campaign 
ON analytics.campaign_daily(customer_id, campaign_id, snapshot_date DESC);


-- ============================================================================
-- CAMPAIGN_METADATA TABLE INDEXES
-- ============================================================================

-- Index for campaign ID lookups
CREATE INDEX IF NOT EXISTS idx_campaign_metadata_campaign_id 
ON analytics.campaign_metadata(campaign_id);

-- Index for customer + campaign lookups
CREATE INDEX IF NOT EXISTS idx_campaign_metadata_customer_campaign 
ON analytics.campaign_metadata(customer_id, campaign_id);

-- Index for campaign type filtering
CREATE INDEX IF NOT EXISTS idx_campaign_metadata_campaign_type 
ON analytics.campaign_metadata(campaign_type);


-- ============================================================================
-- VERIFY INDEXES
-- ============================================================================

-- Query to verify all indexes were created
SELECT 
    table_name,
    index_name,
    COUNT(*) as column_count
FROM duckdb_indexes()
WHERE schema_name = 'analytics'
GROUP BY table_name, index_name
ORDER BY table_name, index_name;
