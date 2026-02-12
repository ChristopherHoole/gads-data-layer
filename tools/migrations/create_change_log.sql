-- Change log table for tracking executed optimizations
-- Supports cooldown enforcement and one-lever-at-a-time rules

CREATE SEQUENCE IF NOT EXISTS change_log_seq START 1;

CREATE TABLE IF NOT EXISTS analytics.change_log (
    change_id INTEGER DEFAULT nextval('change_log_seq'),
    customer_id TEXT NOT NULL,
    campaign_id TEXT NOT NULL,
    change_date DATE NOT NULL,
    lever TEXT NOT NULL,
    old_value DOUBLE,
    new_value DOUBLE,
    change_pct DOUBLE,
    rule_id TEXT NOT NULL,
    risk_tier TEXT,
    approved_by TEXT,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_cooldown 
ON analytics.change_log(customer_id, campaign_id, lever, change_date);