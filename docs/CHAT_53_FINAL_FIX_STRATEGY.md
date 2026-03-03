# FINAL FIX STRATEGY - BACKEND ROUTES

**Date:** 2026-02-28  
**Database Verified:** warehouse_readonly.duckdb  
**Customer:** 9999999999 (Synthetic Test Client)

---

## ✅ DATABASE VERIFICATION RESULTS

### **Tables with FULL YEAR of data (Feb 2025 - Feb 2026):**
1. ✅ `analytics.campaign_daily`: 7,300 rows - **PERFECT for period comparison**
2. ✅ `analytics.ad_group_daily`: 23,725 rows - **PERFECT for period comparison**
3. ✅ `analytics.shopping_campaign_daily`: 7,300 rows - **PERFECT for period comparison**

### **Tables with PARTIAL data (Nov 2025 - Feb 2026):**
4. ⚠️ `analytics.keyword_daily`: 77,368 rows - **3 months - enough for comparison**

### **Tables with SINGLE DAY only (cannot do period comparison):**
5. ❌ `analytics.keyword_features_daily`: 940 rows (Feb 13, 2026 only)
6. ❌ `analytics.ad_features_daily`: 983 rows (Feb 15, 2026 only)
7. ❌ `analytics.product_features_daily`: 100 rows (Feb 15, 2026 only)

### **Tables that DON'T EXIST:**
- ❌ `analytics.shopping_product_daily`
- ❌ `analytics.shopping_campaign_features_daily`

---

## 🎯 ROUTE FIX STRATEGY

### **ROUTE 1: KEYWORDS (/keywords) - EASY FIX (1 hour)**

**Current Status:** 40% complete
- ✅ Has sparkline query (queries `keyword_daily`)
- ❌ Missing previous period query
- ❌ Hardcodes `change_pct = None`

**Available Data:** `keyword_daily` has 77,368 rows (Nov 2025 - Feb 2026)

**Fix Required:**
1. Add previous period query from `keyword_daily` (copy pattern from campaigns.py)
2. Add `_calculate_change_pct()` function
3. Update `_card_kw()` to accept `prev` parameter
4. Call `_calculate_change_pct(value, prev)` instead of hardcoding None
5. Pass previous values to all card definitions

**Files to modify:**
- `act_dashboard/routes/keywords.py` (lines 572-715)

**Estimated time:** 1 hour

---

### **ROUTE 2: AD GROUPS (/ad-groups) - COMPLETE REWRITE (2 hours)**

**Current Status:** 0% complete
- ❌ Returns hardcoded placeholder data
- ❌ Doesn't query database at all

**Available Data:** `ad_group_daily` has 23,725 rows (Feb 2025 - Feb 2026) - PERFECT!

**Fix Required:**
1. **DELETE** `build_adgroup_metrics_cards()` function entirely (lines 193-217)
2. **CREATE NEW** `load_ad_group_metrics_cards()` function
3. Copy entire pattern from `campaigns.py`:
   - Add function parameters: (conn, customer_id, active_days, date_from, date_to)
   - Add `_build_date_filters()` function
   - Add `_calculate_change_pct()` function
   - Add `_card()` and `_blank_card()` helper functions
   - Add `_fmt()` formatting function
4. Add 3 SQL queries:
   - Current period: `SELECT ... FROM analytics.ad_group_daily WHERE ... {current_filter}`
   - Previous period: `SELECT ... FROM analytics.ad_group_daily WHERE ... {prev_filter}`
   - Sparklines: `SELECT snapshot_date, ... FROM analytics.ad_group_daily ... GROUP BY snapshot_date`
5. Build cards from query results (not hardcoded data)

**Metrics to include:**
- Financial: Cost, Revenue, ROAS, Wasted Spend, Conv., CPA, CVR, [blank]
- Actions: Impressions, Clicks, CPC, CTR, Search IS, Top IS, Abs Top IS, Click Share

**Files to modify:**
- `act_dashboard/routes/ad_groups.py` (lines 193-300)

**Estimated time:** 2 hours

---

### **ROUTE 3: SHOPPING (/shopping) - MEDIUM FIX (1.5 hours)**

**Current Status:** 30% complete
- ✅ Has current period query (but queries wrong table!)
- ❌ Missing previous period query
- ❌ Missing sparkline query
- ❌ Hardcodes `change_pct = None`

**Current Problem:** Queries `shopping_campaign_features_daily` (doesn't exist!)

**Available Data:** `shopping_campaign_daily` has 7,300 rows (Feb 2025 - Feb 2026) - PERFECT!

**Fix Required:**
1. **CHANGE** current period query from `shopping_campaign_features_daily` → `shopping_campaign_daily`
2. Add previous period query from `shopping_campaign_daily`
3. Add sparkline query from `shopping_campaign_daily` GROUP BY snapshot_date
4. Add `_calculate_change_pct()` function
5. Update `_card_sh()` to accept `prev` and `sparkline` parameters
6. Pass sparkline arrays to card builders (instead of empty arrays)

**Files to modify:**
- `act_dashboard/routes/shopping.py` (lines 535-619)

**Note:** Shopping has TWO metrics sections (campaign + product). Product metrics will remain incomplete until `shopping_product_daily` table is created.

**Estimated time:** 1.5 hours

---

### **ROUTE 4: ADS (/ads) - CHECK FIRST, THEN FIX (2 hours)**

**Current Status:** 30% complete
- ✅ Has current period query (from `ad_features_daily`)
- ❌ Missing previous period query
- ❌ Missing sparkline query
- ❌ Hardcodes `change_pct = None`

**Current Problem:** Queries `ad_features_daily` (only 1 day of data - Feb 15)

**FIRST - Check if `ad_daily` exists:**

```sql
SELECT COUNT(*) FROM analytics.ad_daily WHERE customer_id = '9999999999'
```

**Option A: If `ad_daily` EXISTS with historical data:**
1. Query `ad_daily` instead of `ad_features_daily`
2. Add previous period query
3. Add sparkline query
4. Update `_card_ads()` to accept prev/sparkline
5. Calculate change_pct

**Option B: If `ad_daily` does NOT exist:**
1. **Cannot fix** - need synthetic data generation first
2. Document as limitation
3. Keep current hardcoded None values

**Files to modify:**
- `act_dashboard/routes/ads.py` (lines 238-313)

**Estimated time:** 2 hours (if ad_daily exists), 0 hours (if it doesn't)

---

## 📋 IMPLEMENTATION ORDER

**Recommended fix order (easiest → hardest):**

1. **Keywords** (1 hour) - 40% done, small changes
2. **Shopping** (1.5 hours) - Table swap + period comparison
3. **Ads** (2 hours) - Check ad_daily table first
4. **Ad Groups** (2 hours) - Complete rewrite

**Total estimated time:** 6.5 hours (assuming ad_daily exists)

---

## 🔧 CODE PATTERNS TO COPY

### **Pattern 1: Date Filters (copy from campaigns.py lines 230-248)**

```python
def _build_date_filters(active_days, date_from, date_to):
    if date_from and date_to:
        current_filter = f"AND snapshot_date >= '{date_from}' AND snapshot_date <= '{date_to}'"
        # Calculate previous period dates
        from datetime import datetime, timedelta
        d1 = datetime.strptime(date_from, '%Y-%m-%d')
        d2 = datetime.strptime(date_to, '%Y-%m-%d')
        delta = (d2 - d1).days + 1
        p1 = d1 - timedelta(days=delta)
        p2 = d1 - timedelta(days=1)
        prev_filter = f"AND snapshot_date >= '{p1.strftime('%Y-%m-%d')}' AND snapshot_date <= '{p2.strftime('%Y-%m-%d')}'"
    else:
        days = active_days if active_days in [7, 30, 90] else 30
        current_filter = f"AND snapshot_date >= CURRENT_DATE - INTERVAL '{days} days' AND snapshot_date < CURRENT_DATE"
        prev_filter = f"AND snapshot_date >= CURRENT_DATE - INTERVAL '{days * 2} days' AND snapshot_date < CURRENT_DATE - INTERVAL '{days} days'"
    return current_filter, prev_filter
```

### **Pattern 2: Calculate Change % (copy from campaigns.py lines 250-259)**

```python
def _calculate_change_pct(current, previous):
    if previous is None or previous == 0:
        return None
    if current is None:
        return -100.0
    return ((current - previous) / previous) * 100.0
```

### **Pattern 3: Card Builder (copy from campaigns.py lines 295-308)**

```python
def _card(label, value, prev, sparkline, fmt, invert=False, card_type='financial'):
    return {
        'label': label,
        'value_display': _fmt(value, fmt),
        'change_pct': _calculate_change_pct(value, prev),
        'sparkline_data': sparkline,
        'format_type': fmt,
        'invert_colours': invert,
        'card_type': card_type,
        'sub_label': None,
    }
```

### **Pattern 4: SQL Queries (3 queries per route)**

```python
# Query 1: Current period
q_current = f"""
    SELECT
        SUM(cost_micros) / 1000000.0 AS cost,
        SUM(conversions_value) AS revenue,
        -- ... all metrics
    FROM analytics.TABLENAME_daily
    WHERE customer_id = ?
      {current_filter}
"""

# Query 2: Previous period
q_prev = f"""
    SELECT
        SUM(cost_micros) / 1000000.0 AS cost,
        -- ... same metrics
    FROM analytics.TABLENAME_daily
    WHERE customer_id = ?
      {prev_filter}
"""

# Query 3: Sparklines
q_spark = f"""
    SELECT
        snapshot_date,
        SUM(cost_micros) / 1000000.0 AS cost,
        -- ... all metrics
    FROM analytics.TABLENAME_daily
    WHERE customer_id = ?
      {current_filter}
    GROUP BY snapshot_date
    ORDER BY snapshot_date ASC
"""
```

---

## ✅ SUCCESS CRITERIA (per route)

After fixing each route, verify:

1. ✅ Page loads without errors
2. ✅ Metrics cards show current values (not "—")
3. ✅ Change percentages show actual % (not "—")
4. ✅ Sparklines are COLORED (green/red/gray, not all grey)
5. ✅ Hover over sparklines shows dot + tooltip
6. ✅ No JavaScript console errors
7. ✅ PowerShell test: `python -m flask run` → navigate to page → screenshot

---

## 🚨 KNOWN LIMITATIONS (after fix)

**These will remain broken until synthetic data is generated:**

1. **Ads page:** If `ad_daily` table doesn't exist
2. **Shopping products:** `shopping_product_daily` doesn't exist
3. **Keyword/Ad features tables:** Only have 1 day of data (can't do comparisons using features tables)

**Workaround:** All routes should query `*_daily` tables (not `*_features_daily`)

---

## 📝 NEXT STEP: CHECK AD_DAILY TABLE

Before creating Chat 53 brief, run this final check:

```powershell
python -c "import duckdb; conn = duckdb.connect('warehouse_readonly.duckdb', read_only=True); result = conn.execute(\"SELECT COUNT(*), MIN(snapshot_date), MAX(snapshot_date) FROM analytics.ad_daily WHERE customer_id = '9999999999'\").fetchone(); print(f'ad_daily: {result[0]} rows from {result[1]} to {result[2]}') if result[0] > 0 else print('ad_daily: Table does not exist or has no data'); conn.close()"
```

**If ad_daily exists with data:** Fix all 4 routes (6.5 hours)  
**If ad_daily doesn't exist:** Fix 3 routes, document Ads limitation (4.5 hours)

---

**Document:** FINAL_FIX_STRATEGY.md  
**Created:** 2026-02-28  
**Status:** Ready for Chat 53 brief creation  
**Next:** Check ad_daily table, then create worker brief
