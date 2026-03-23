# CHAT 110: Shopping Product Rules & Flags — Summary

**Date:** 2026-03-22
**Status:** Complete
**Entity:** Products (entity_type='product')

---

## What Was Built

Product-level Rules & Flags for Shopping, accessed via Campaign/Product toggle inside the existing Rules tab. This is the final entity in the 4-entity expansion (Ad Groups → Keywords → Ads → Products).

## Files Created

| File | Purpose |
|------|---------|
| `templates/components/product_rules_flow_builder.html` | Combined rules/flags tab + 5-step flow builder (single file) |
| `scripts/seed_product_rules.py` | Seeds 10 rules + 8 flags |

## Files Modified

| File | Changes |
|------|---------|
| `templates/shopping_new.html` | Added rules.css, replaced Rules tab with Campaign/Product toggle, added toggle JS |
| `routes/shopping.py` | Added rfb_products context, 7 CRUD routes, /api/products-list |
| `static/css/rules.css` | Added `#prd-rules-flow-overlay`, `#prd-rules-toast-wrap` |
| `app.py` | Added 7 CSRF exemptions for Chat 110 routes |
| `act_autopilot/recommendations_engine.py` | Added PRODUCT_METRIC_MAP (50+ metrics), added 'product' to ENTITY_TABLES/ENTITY_ID_COLUMNS/metric map selector |

## Database

- **18 rows** seeded: 10 rules + 8 flags
- **4 rule categories:** Feed Quality (1), Performance (6), Lifecycle (1), Stock (2)
- **3 flag categories:** Feed Quality (3), Lifecycle (3), Stock (2)
- Product-specific metrics: stock_out_flag, has_price_mismatch, has_disapproval, feed_quality_score, new_product_flag, days_live, availability

## Key Design Decisions

- **Toggle UI** instead of separate tab — Products rules share the Rules tab with Campaign rules via toggle buttons
- **4 categories** for products: Feed Quality, Performance, Lifecycle, Stock (not the standard Bid/Status)
- **No WoW %** metrics used (DuckDB nested window limitation — columns are all 0.0)
- **PRODUCT_METRIC_MAP** with 50+ metrics covering all w7/w14/w30/w90 windows

## Verification

| Test | Result |
|------|--------|
| Toggle buttons | Campaign/Product toggle works |
| Rules data | 18 total, 10 rules in 4 groups |
| Flags data | 8 flags in 3 groups |
| Flow builder | Opens as centered popup, 25 products in picker |
| Type cards | 4: Feed Quality, Performance, Lifecycle, Stock |
| Console errors | 0 |
| Server errors | 0 |
