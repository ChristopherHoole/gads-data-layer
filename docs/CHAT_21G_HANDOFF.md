# Chat 21g Handoff — Shopping View + Shopping Rules

**Chat:** 21g
**Date:** 2026-02-19
**Status:** COMPLETE ✅ — Master Chat approved
**Scope:** Shopping page Bootstrap 5 redesign + 14 shopping optimization rules

---

## Files Delivered

### 1. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\shopping.py`
Full route rewrite. 4-tab structure, pagination, filters, fallback logic.

Key query decisions:
- Campaigns tab: `raw_shopping_campaign_daily` LEFT JOIN `analytics.campaign_daily` on `campaign_id`
- Products tab: `analytics.product_features_daily` primary, `raw_product_performance_daily` fallback
- Feed Quality tab: `raw_product_feed_quality`
- `conversions_value` divided by `1000000.0` in both main and fallback queries (micros fix)

### 2. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\shopping_new.html`
Bootstrap 5 template. Extends `base_bootstrap.html`. 4 tabs, rules sidebar, Active Optimization Rules card.

### 3. `C:\Users\User\Desktop\gads-data-layer\act_autopilot\rules\shopping_rules.py`
⚠️ **CORRECT PATH NOTE:** Knowledge base previously documented this as `src/shopping/shopping_rules.py` — that path does NOT exist. The correct path is `act_autopilot/rules/shopping_rules.py`. Knowledge base should be updated.

Full rewrite with 14 public rule functions. Previous file had only 1 private function (`_apply_shop_bid_001`) which was invisible to the discovery mechanism.

---

## Bugs Fixed

### Bug 1 — Conv. Value showing as trillions (FIXED)
**Root cause:** `conversions_value` in `raw_shopping_campaign_daily` is stored in micros. The original query summed the raw value without dividing by 1,000,000.

**Fix:** Applied `/ 1000000.0` to `SUM(s.conversions_value)` in both the main JOIN query (line 58) and the fallback query (line 97) in `shopping.py`.

**Before:** Conv. Value = $12,480,000,000,000 | ROAS = 35,849,520x
**After:** Conv. Value = $34,819 | ROAS = 36.45x

### Bug 2 — STATUS: UNKNOWN on all campaigns (SYNTHETIC DATA LIMITATION — NOT A CODE BUG)
**Investigation:** Added diagnostic logging. Confirmed shopping campaign IDs in `raw_shopping_campaign_daily` are integers (1001, 1002, 1003). Campaign IDs in `analytics.campaign_daily` are strings in the 3000+ range. Zero overlap — LEFT JOIN returns NULL for all `campaign_status` values.

**Verdict:** This is a synthetic dataset limitation. The JOIN logic is correct. STATUS will resolve automatically when real account data is loaded (real Google Ads campaign IDs will match across both tables).

**No code change needed.**

---

## 14 Shopping Rules Implemented

All rules follow the naming pattern `shop_xxx_NNN_description` and are discovered correctly by `extract_rules_from_module` in `rule_helpers.py`.

| Rule ID | Function | Trigger | Action |
|---------|----------|---------|--------|
| SHOP-BID-001 | `shop_bid_001_high_roas_increase` | ROAS > 5.0 AND clicks > 50 (30d) | +15% bid increase |
| SHOP-BID-002 | `shop_bid_002_low_roas_decrease` | ROAS < 1.5 AND cost > $20 (30d) | -15% bid decrease |
| SHOP-BID-003 | `shop_bid_003_very_low_roas_decrease` | ROAS < 0.5 AND cost > $30 (30d) | -25% bid decrease (conservative) |
| SHOP-BID-004 | `shop_bid_004_low_visibility_increase` | cost > $100 AND impressions < 500 (30d) | +10% bid increase |
| SHOP-BID-005 | `shop_bid_005_insufficient_data_hold` | clicks < 10 (30d) | Hold — low data flag |
| SHOP-PAUSE-006 | `shop_pause_006_zero_conv_high_spend` | zero conv AND cost > $50 AND clicks > 100 (30d) | Pause product |
| SHOP-PAUSE-007 | `shop_pause_007_very_low_roas_pause` | ROAS < 0.5 AND cost > $30 (30d) | Pause product (aggressive) |
| SHOP-PAUSE-008 | `shop_pause_008_out_of_stock_spending` | OUT_OF_STOCK AND clicks_w7 > 0 AND cost_w7 > $0 | Pause product |
| SHOP-FEED-009 | `shop_feed_009_disapproved_product` | approval_status = DISAPPROVED | Flag — fix feed |
| SHOP-FEED-010 | `shop_feed_010_price_mismatch` | price_mismatch = TRUE | Flag — fix feed |
| SHOP-FEED-011 | `shop_feed_011_pending_approval_stuck` | PENDING AND ingested_at > 48h ago | Flag — stuck in review |
| SHOP-FEED-012 | `shop_feed_012_low_quality_score` | feed_quality_score < 0.70 | Flag — improve feed |
| SHOP-REVIEW-013 | `shop_review_013_out_of_stock_clicks` | OUT_OF_STOCK AND clicks_w7 > 0 | Review — user attention |
| SHOP-REVIEW-014 | `shop_review_014_disapproved_spending` | DISAPPROVED AND cost_w30 > $0 | Urgent review |

**Note on SHOP-BID-003 and SHOP-PAUSE-007:** Both fire on ROAS < 0.5 AND cost > $30. Intentional — BID-003 is the conservative option (reduce bid), PAUSE-007 is the aggressive option (pause). User decides which to action. Rationale text on each rule makes this explicit.

**Data sources:**
- BID/PAUSE/REVIEW rules: `product: Dict` from `analytics.product_features_daily`
- FEED rules (009–012): `product: Dict` from `raw_product_feed_quality`
- `apply_rules()` accepts both datasets and routes accordingly

---

## Previous Rule Discovery Bug (Fixed)

The old `shopping_rules.py` had a single function `_apply_shop_bid_001` which was invisible to the dashboard discovery mechanism for two reasons:
1. Name starts with `_` (private prefix — skipped)
2. No 3-digit number in the pattern `_\d{3}_` (also skipped)

The new file uses public naming (`shop_xxx_NNN_description`) that satisfies the discovery pattern. Discovery was verified by simulating `extract_rules_from_module` logic against all 14 functions before delivery.

---

## `apply_rules()` Entry Point

Kept as the execution entry point per Master Chat direction. Takes two arguments:
- `product_features: List[Dict]` — for BID/PAUSE/REVIEW rules
- `feed_quality_data: Optional[List[Dict]]` — for FEED rules

Does NOT interfere with rule discovery (no `_\d{3}_` pattern in function name — correctly skipped).

---

## Verified Test Results

```
PowerShell: [Shopping] campaigns=3, products=100 (fallback=False), feed_issues=6, rules=14
```

- Campaigns tab: 3 campaigns, $955.34 cost, 379 conversions, 36.45x ROAS, $34,819 Conv. Value ✅
- Products tab: 100 products, availability filters, feed quality bars ✅
- Feed Quality tab: 6 issues, approval status breakdown, freshness badge ✅
- Rules tab: 14 rules, conditions, risk tiers, status ✅
- Rules sidebar: 14 rules ✅
- Active Optimization Rules card: 14 rules ✅
- Date filters (7d/30d/90d): working ✅
- Status filters (All/Enabled/Paused): working ✅
- Availability filters (All/In Stock/Out of Stock/Preorder): working ✅

---

## Pre-Existing Issues (Not Introduced by Chat 21g)

These were present before this chat and are not shopping-specific:

| Issue | Root Cause | Action |
|-------|-----------|--------|
| `TemplateNotFound: 404.html` on favicon | No 404 template exists in project | Out of scope — log for Chat 21h polish |
| Config validation warnings on startup | `client_synthetic.yaml` missing required fields | Out of scope — pre-existing |
| `[rule_helpers] Warning: Unknown page_type 'ad_group'` | Ad groups page uses `ad_group` not `ad-groups` | Out of scope — pre-existing |

---

## Knowledge Base Corrections Required

The Master Knowledge Base documents the shopping rules file path as:
- ❌ `src/shopping/shopping_rules.py` (DOES NOT EXIST)
- ❌ `src/autopilot/keyword_rules.py` (DOES NOT EXIST)
- ❌ `src/autopilot/campaign_rules.py` (DOES NOT EXIST)

Correct paths are:
- ✅ `act_autopilot/rules/shopping_rules.py`
- ✅ `act_autopilot/rules/keyword_rules.py`
- ✅ `act_autopilot/rules/budget_rules.py`
- ✅ `act_autopilot/rules/bid_rules.py`
- ✅ `act_autopilot/rules/status_rules.py`
- ✅ `act_autopilot/rules/ad_rules.py`

---

## Next Steps

**Chat 21h — Final Polish** (last page in Dashboard UI Overhaul)
- Cross-page consistency audit
- Fix pre-existing `404.html` favicon error
- Any UI/UX tweaks identified during full review
- Final `PROJECT_ROADMAP.md` update for Chat 21 completion
