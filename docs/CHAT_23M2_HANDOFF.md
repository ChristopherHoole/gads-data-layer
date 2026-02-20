# CHAT_23_HANDOFF.md
## Dashboard 3.0 — Module 2 (M2): Metrics Cards — Full Rollout

**Chat:** 23
**Module:** M2 — Metrics Cards
**Status:** COMPLETE ✅
**Date:** 2026-02-20
**Approved by:** Master Chat

---

## 1. OBJECTIVE

Deploy the M2 Metrics Cards macro system across all 6 dashboard pages:
- Replace all legacy static metrics bars with the unified `metrics_section` Jinja2 macro
- Each page gets: **Financial row** (8 cards) + **collapsible Actions row** (8 cards) + sparklines
- Consistent collapse/expand state per page stored in Flask session
- All change indicators show `—` for windowed-column pages (no prev period available)

---

## 2. PAGES COMPLETED THIS SESSION

| Page | Route | Template | Prior Session |
|------|-------|----------|---------------|
| Dashboard | `dashboard.py` | `dashboard_new.html` | ✅ |
| Campaigns | `campaigns.py` | `campaigns.html` | ✅ |
| Ad Groups | `ad_groups.py` | `ad_groups.html` | ✅ |
| Keywords | `keywords.py` | `keywords_new.html` | ✅ |
| **Ads** | `ads.py` | `ads_new.html` | **This session** |
| **Shopping** | `shopping.py` | `shopping_new.html` | **This session** |

---

## 3. FILES MODIFIED THIS SESSION

### `act_dashboard/routes/ads.py`
**Changes:**
- Added `get_metrics_collapsed` to shared imports
- Added helper functions: `_fmt_ads()`, `_card_ads()`, `_blank_ads()`
- Added `load_ads_metrics_cards()` function
- Financial row (8): Cost | Revenue | ROAS | blank | Conversions | Cost/Conv | Conv Rate | blank
- Actions row (8): Impressions | Clicks | Avg CPC | Avg CTR | Ad Strength | blank | blank | blank
- Ad Strength card: `good_count/total` label (e.g. "240/983"), sub_label shows poor count
- Ad Strength is in **Actions row ONLY** (not Financial) — deliberate design decision
- Added `financial_cards`, `actions_cards`, `metrics_collapsed` to `render_template`
- Data source: `all_ads` list (already loaded) — no extra DB queries

**Key logic:**
```python
good_strength  = sum(1 for a in all_ads if a.get('ad_strength') in ('GOOD', 'EXCELLENT'))
poor_strength  = sum(1 for a in all_ads if a.get('ad_strength') == 'POOR')
strength_label = f"{good_strength}/{total_ads}"
strength_sub   = f"{poor_strength} Poor" if poor_strength > 0 else "Good/Excellent"
```

### `act_dashboard/templates/ads_new.html`
**Changes:**
- Added `{% from "macros/metrics_cards.html" import metrics_section %}` import
- Replaced old 7-card static metrics bar (lines 47–141) with:
  `{{ metrics_section(financial_cards, actions_cards, 'ads', metrics_collapsed) }}`

### `act_dashboard/routes/shopping.py`
**Changes:**
- Added `get_metrics_collapsed` to shared imports
- Added helper functions: `_fmt_sh()`, `_card_sh()`, `_blank_sh()`
- Added `build_campaign_metrics_cards()` function
- Added `build_product_metrics_cards()` function
- Updated `compute_campaign_metrics()` to include `total_clicks` field
- Added M2 build calls before `render_template`
- Added 4 new template vars: `camp_financial_cards`, `camp_actions_cards`, `prod_financial_cards`, `prod_actions_cards`, `metrics_collapsed`

**Campaigns tab cards:**
- Financial (8): Cost | Conv Value | ROAS | blank | Conversions | Cost/Conv | Conv Rate | blank
- Actions (8): Impressions | Clicks | Avg CPC | Avg CTR | blank x4

**Products tab cards:**
- Financial (8): Cost | ROAS | blank | Out of Stock | Conversions | blank x3
- Actions (8): Products | Feed Issues | blank x6

**Shopping data note:** All M2 values derived from pre-computed `campaign_metrics` / `product_metrics` dicts — no extra DB queries needed.

**Important fix:** `compute_campaign_metrics()` was missing `total_clicks`. Added to both empty return dict and computed return dict.

### `act_dashboard/templates/shopping_new.html`
**Changes:**
- Added macro import
- Replaced Campaigns metrics bar (lines 73–139) with:
  `{{ metrics_section(camp_financial_cards, camp_actions_cards, 'shopping_campaigns', metrics_collapsed) }}`
- Replaced Products metrics bar (lines 355–431) with:
  `{{ metrics_section(prod_financial_cards, prod_actions_cards, 'shopping_products', metrics_collapsed) }}`
- Two independent macro calls with different page IDs (`shopping_campaigns` vs `shopping_products`) — separate collapse state per tab

---

## 4. CARD LAYOUTS BY PAGE (REFERENCE)

| Page | Financial Row (8) | Actions Row (8) |
|------|-------------------|-----------------|
| Dashboard | Cost\|Revenue\|ROAS\|Wasted Spend\|Conversions\|CPA\|Conv Rate\|blank | Impr\|Clicks\|CPC\|CTR\|Search IS\|Top IS\|Abs Top IS\|Click Share |
| Campaigns | Cost\|Revenue\|ROAS\|Wasted Spend\|Conversions\|CPA\|Conv Rate\|blank | Impr\|Clicks\|CPC\|CTR\|Search IS\|Top IS\|Abs Top IS\|Click Share |
| Ad Groups | Cost\|Revenue\|ROAS\|Wasted Spend\|Conversions\|CPA\|Conv Rate\|blank | Impr\|Clicks\|CPC\|CTR\|Search IS\|Top IS\|Abs Top IS\|Click Share |
| Keywords | Cost\|Revenue\|ROAS\|Wasted Spend\|Conversions\|CPA\|Conv Rate\|blank | Impr\|Clicks\|CPC\|CTR\|Search IS\|Top IS\|Abs Top IS\|Click Share |
| Ads | Cost\|Revenue\|ROAS\|blank\|Conversions\|CPA\|Conv Rate\|blank | Impr\|Clicks\|CPC\|CTR\|Ad Strength\|blank\|blank\|blank |
| Shopping (Campaigns) | Cost\|Conv Value\|ROAS\|blank\|Conversions\|Cost/Conv\|Conv Rate\|blank | Impr\|Clicks\|CPC\|CTR\|blank x4 |
| Shopping (Products) | Cost\|ROAS\|blank\|Out of Stock\|Conversions\|blank x3 | Products\|Feed Issues\|blank x6 |

---

## 5. ARCHITECTURE — M2 MACRO SYSTEM

### Macro file
`act_dashboard/templates/macros/metrics_cards.html`
- `metrics_section(financial_cards, actions_cards, page_id, collapsed)`
- Renders Financial row always visible
- Actions row toggleable via collapse button (session-persisted)
- Each card: label, value_display, change_pct (or `—`), sparkline (Chart.js inline)

### Card dict structure
```python
{
    'label': 'Cost',
    'value_display': '$295.9k',
    'change_pct': -5.2,          # None → shows '—'
    'sparkline_data': [1,2,3],   # None → no sparkline
    'format_type': 'currency',
    'invert_colours': True,       # True = red for positive (cost = bad when up)
    'card_type': 'financial',     # or 'actions'
    'sub_label': None,            # optional secondary text
}
```

### Session collapse state
`shared.py` → `get_metrics_collapsed(page_id)` / `set_metrics_collapsed(page_id, state)`
Page IDs used: `dashboard`, `campaigns`, `ad_groups`, `keywords`, `ads`, `shopping_campaigns`, `shopping_products`

### Data source by page type
| Type | Pages | Change Indicators | Sparklines |
|------|-------|-------------------|------------|
| Date-range (raw SQL) | Dashboard, Campaigns, Ad Groups | ✅ vs prev period | ✅ from daily snapshots |
| Windowed columns | Keywords, Ads, Shopping | `—` (no prev period) | Limited/None |

---

## 6. KNOWN PATTERNS & PITFALLS

1. **Route decorator quote style matters** — Shopping uses single quotes `@bp.route('/shopping')`. String replacement in Python must match exactly.
2. **Shopping needs `total_clicks` in `compute_campaign_metrics`** — was missing, added this session. Both empty-return and computed-return dicts must include it.
3. **Ad Strength format** — uses `'ad_strength'` format_type. The macro renders it as plain string (e.g. "240/983"). Do NOT put it in Financial row — it belongs in Actions only.
4. **Two macro calls on Shopping** — use different page IDs to maintain independent collapse state per tab.
5. **`_empty_ctx` dict in shopping.py** — does NOT include M2 card vars (they're built after the try/except block). The error path renders without them — acceptable, error template doesn't show cards.

---

## 7. TESTING COMPLETED

All pages visually confirmed via Opera screenshots:
- ✅ Financial row: correct 8 cards, correct values
- ✅ Actions row: correct 8 cards, collapses/expands
- ✅ Change indicators: `—` on windowed pages, % values on date-range pages
- ✅ Ad Strength: Actions row only (not Financial)
- ✅ Shopping: both tabs independent

---

## 8. NEXT STEPS (per PROJECT_ROADMAP.md)

**Dashboard 3.0 remaining modules:**
- M3: Chart overhauls (Chart.js upgrades per page)
- M4: Table improvements (sortable columns, better pagination)
- M5: Rules panel upgrades
- M6: Action buttons

**Git commit** — pending Master Chat working document updates.

---

## 9. GIT COMMIT (PENDING APPROVAL)

**Suggested commit message:**
```
feat(dashboard): M2 metrics cards rollout - all 6 pages complete

- Add M2 metrics_section macro to Ads and Shopping pages
- Ads: Financial(8) + Actions(8) incl Ad Strength in actions only
- Shopping: separate macro calls for Campaigns and Products tabs
- Add total_clicks to compute_campaign_metrics for CPC/CTR calculation
- All pages: unified collapse/expand with session persistence
- All pages tested and visually confirmed

Chat-23 | Module-M2 | Status: COMPLETE
```

**Files to commit:**
- `act_dashboard/routes/ads.py`
- `act_dashboard/templates/ads_new.html`
- `act_dashboard/routes/shopping.py`
- `act_dashboard/templates/shopping_new.html`
