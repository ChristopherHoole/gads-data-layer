-- ============================================================================
-- CHAT 13: Extend change_log table for keyword/ad/Shopping execution tracking
-- ============================================================================
-- 
-- Adds columns to analytics.change_log to track:
-- - Keyword operations (add, pause, bid changes, negatives)
-- - Ad operations (pause, enable)
-- - Shopping operations (bid changes, product exclusions)
--
-- New columns store comprehensive metadata (Q5 answer: B - Comprehensive)
-- ============================================================================

-- Add new columns to change_log table
ALTER TABLE analytics.change_log 
ADD COLUMN IF NOT EXISTS action_type VARCHAR;

ALTER TABLE analytics.change_log 
ADD COLUMN IF NOT EXISTS entity_type VARCHAR;

ALTER TABLE analytics.change_log 
ADD COLUMN IF NOT EXISTS entity_id VARCHAR;

ALTER TABLE analytics.change_log 
ADD COLUMN IF NOT EXISTS match_type VARCHAR;

ALTER TABLE analytics.change_log 
ADD COLUMN IF NOT EXISTS keyword_text VARCHAR;

ALTER TABLE analytics.change_log 
ADD COLUMN IF NOT EXISTS ad_group_id BIGINT;

ALTER TABLE analytics.change_log 
ADD COLUMN IF NOT EXISTS metadata JSON;

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_change_log_entity 
ON analytics.change_log(entity_type, entity_id);

CREATE INDEX IF NOT EXISTS idx_change_log_action 
ON analytics.change_log(action_type);

-- ============================================================================
-- Column descriptions:
-- ============================================================================
-- action_type: What action was performed
--   - add_keyword, pause_keyword, update_keyword_bid, add_negative_keyword
--   - pause_ad, enable_ad
--   - update_product_bid, exclude_product
--   - update_budget, update_bid_target (existing campaign actions)
--
-- entity_type: What was changed
--   - keyword, ad, product, campaign
--
-- entity_id: ID of the specific thing changed
--   - Keyword criterion ID
--   - Ad ID
--   - Product partition ID
--   - Campaign ID
--
-- match_type: For keywords only
--   - EXACT, PHRASE, BROAD
--   - NULL for non-keyword actions
--
-- keyword_text: Actual keyword text
--   - "running shoes", "buy nike shoes", etc.
--   - NULL for non-keyword actions
--
-- ad_group_id: Parent ad group ID
--   - Required for keywords and ads
--   - NULL for campaign-level actions
--
-- metadata: Comprehensive JSON storage (Q5 answer: B)
--   - rule_id: Which rule generated this recommendation
--   - confidence: Rule confidence score (0.0 to 1.0)
--   - risk_level: LOW, MEDIUM, HIGH
--   - evidence: Data supporting the change
--   - reasoning: Why this change was recommended
--   - old_values: Before state (bids, status, etc.)
--   - new_values: After state
--   - Example:
--     {
--       "rule_id": "KW_PAUSE_HIGH_CPA",
--       "confidence": 0.92,
--       "risk_level": "LOW",
--       "evidence": {
--         "cpa": 125.50,
--         "target_cpa": 75.00,
--         "clicks": 45,
--         "conversions": 2
--       },
--       "reasoning": "Keyword CPA $125.50 exceeds target $75.00 by 67% with sufficient data",
--       "old_values": {
--         "status": "ENABLED",
--         "bid_micros": 2500000
--       },
--       "new_values": {
--         "status": "PAUSED"
--       }
--     }
-- ============================================================================
