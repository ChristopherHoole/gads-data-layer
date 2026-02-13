-- Migration: Add rollback tracking to change_log
-- Date: 2026-02-13
-- Purpose: Track monitoring and rollback status of executed changes

-- Add rollback_status column
-- Values: NULL (default), 'monitoring', 'rolled_back', 'confirmed_good'
ALTER TABLE analytics.change_log 
ADD COLUMN IF NOT EXISTS rollback_status TEXT DEFAULT NULL;

-- Add rollback metadata columns
ALTER TABLE analytics.change_log
ADD COLUMN IF NOT EXISTS rollback_id INTEGER DEFAULT NULL;

ALTER TABLE analytics.change_log
ADD COLUMN IF NOT EXISTS rollback_reason TEXT DEFAULT NULL;

ALTER TABLE analytics.change_log
ADD COLUMN IF NOT EXISTS rollback_executed_at TIMESTAMP DEFAULT NULL;

ALTER TABLE analytics.change_log
ADD COLUMN IF NOT EXISTS monitoring_started_at TIMESTAMP DEFAULT NULL;

ALTER TABLE analytics.change_log
ADD COLUMN IF NOT EXISTS monitoring_completed_at TIMESTAMP DEFAULT NULL;

-- Create index for efficient rollback queries
CREATE INDEX IF NOT EXISTS idx_rollback_status 
ON analytics.change_log(rollback_status, change_date);

-- Validation query (optional - run after migration)
-- SELECT change_id, lever, change_date, rollback_status 
-- FROM analytics.change_log 
-- LIMIT 5;
