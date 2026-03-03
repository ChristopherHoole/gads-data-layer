# BACKEND ROUTES DIAGNOSIS - MISSING METRICS CARDS DATA

**Investigation Date:** 2026-02-28  
**Issue:** Keywords, Ad Groups, Ads, Shopping pages missing change_pct and sparkline_data  
**Status:** ROOT CAUSE IDENTIFIED

---

## EXECUTIVE SUMMARY

4 out of 6 pages have incomplete metrics cards data:
- ❌ **Keywords:** Has sparkline_data, but change_pct hardcoded to None
- ❌ **Ad Groups:** Completely broken - hardcoded placeholder data
- ❌ **Ads:** Has sparkline_data, but change_pct hardcoded to None  
- ❌ **Shopping:** Has sparkline_data, but change_pct hardcoded to None

All 4 routes have intentional comments indicating this is **NOT a bug** - it's **incomplete implementation**.

---

## WORKING ROUTES PATTERN (Dashboard + Campaigns)

### Helper Functions

**1. `_calculate_change_pct(current, previous)` - Calculates percentage change**
```python
def _calculate_change_pct(current: Optional[float], previous: Optional[float]) -> Optional[float]:
    if previous is None or previous == 0:
        return None
    if current is None:
        return -100.0
    return ((current - previous) / previous) * 100.0
```

**2. `_card(label, value, prev, sparkline, fmt, invert, card_type)` - Builds card dict**
```python
def _card(label, value, prev, sparkline, fmt, invert=False, card_type='financial'):
    return {
        'label': label,
        'value_display': _fmt(value, fmt),
        'change_pct': _calculate_change_pct(value, prev),  # ← CALCULATES HERE
        'sparkline_data': sparkline,
        'format_type': fmt,
        'invert_colours': invert,
        'card_type': card_type,
        'sub_label': None,
    }
```

### SQL Query Pattern

**Three queries per page:**

1. **Current Period (aggregate):**
```sql
SELECT
    SUM(cost_micros) / 1000000.0 AS cost,
    SUM(conversions_value) AS revenue,
    -- ... all metrics
FROM ro.analytics.campaign_daily
WHERE customer_id = ?
  {date_filter}  -- e.g., "AND snapshot_date >= '2026-01-29' AND snapshot_date <= '2026-02-27'"
```

2. **Previous Period (aggregate):**
```sql
SELECT
    SUM(cost_micros) / 1000000.0 AS cost,
    -- ... same metrics
FROM ro.analytics.campaign_daily
WHERE customer_id = ?
  {prev_filter}  -- e.g., "AND snapshot_date >= '2025-12-31' AND snapshot_date <= '2026-01-28'"
```

3. **Sparkline Data (daily breakdown):**
```sql
SELECT
    snapshot_date,
    SUM(cost_micros) / 1000000.0 AS cost,
    -- ... all metrics
FROM ro.analytics.campaign_daily
WHERE customer_id = ?
  {date_filter}
GROUP BY snapshot_date
ORDER BY snapshot_date ASC
```

### Data Extraction Pattern

```python
# Execute queries
cur = conn.execute(q_current, [customer_id]).fetchone()
prv = conn.execute(q_prev, [customer_id]).fetchone()
spark_rows = conn.execute(q_spark, [customer_id]).fetchall()

# Extract current and previous values
c_cost = _c(cur, 0)
p_cost = _p(prv, 0)

# Build sparkline arrays
def _spark(col_idx, scale=1.0):
    return [float(row[col_idx]) * scale if row[col_idx] is not None else 0.0 
            for row in spark_rows]

sp_cost = _spark(1)  # Column 1 is cost in sparkline query

# Build cards
financial_cards = [
    _card('Cost', c_cost, p_cost, sp_cost, 'currency', invert=True),
    # ... more cards
]
```

---

## BROKEN ROUTE #1: KEYWORDS.PY

**File:** `act_dashboard/routes/keywords.py`  
**Function:** `load_keyword_metrics_cards()` (lines 594-715)  
**Symptom:** Sparklines show as GREY, change percentages show "—"

### Root Cause

**Line 573:** Intentional comment - "Keywords cards have no prev period"
```python
def _card_kw(label, value, sparkline, fmt, invert=False, card_type='financial'):
    """Keywords cards have no prev period — change_pct always None (dash)."""
    return {
        'label': label,
        'value_display': _fmt_kw(value, fmt),
        'change_pct': None,  # ← HARDCODED TO NONE
        'sparkline_data': sparkline,
        'format_type': fmt,
        'invert_colours': invert,
        'card_type': card_type,
        'sub_label': None,
    }
```

**Line 601:** Comment confirms this is intentional
> "No prev period comparison — change indicators show dash (None)."

### What's Missing

1. **No previous period query** - Only queries current period summary
2. **No `_calculate_change_pct()` function**
3. **`_card_kw()` doesn't accept `prev` parameter** - only takes (label, value, sparkline, fmt)

### Current Implementation

```python
# Only ONE period queried (no comparison)
summary = conn.execute(f"""
    SELECT
        SUM(cost_micros_{window_suffix}_sum) / 1000000.0 AS cost,
        -- ... other metrics
    FROM ro.analytics.keyword_features_daily
    WHERE customer_id = ? AND snapshot_date = ?
""", [customer_id, snapshot_date]).fetchone()

# Cards built without previous values
financial_cards = [
    _card_kw('Cost', c[0], _spark(1), 'currency', invert=True),
    # No p[0] parameter for previous cost
]
```

### Fix Required

1. Add `_build_date_filters()` function (copy from campaigns.py)
2. Add previous period query (similar to `q_prev` in campaigns.py)
3. Update `_card_kw()` to accept `prev` parameter
4. Update `_card_kw()` to call `_calculate_change_pct(value, prev)`
5. Update all card definitions to pass previous values

---

## BROKEN ROUTE #2: AD_GROUPS.PY

**File:** `act_dashboard/routes/ad_groups.py`  
**Function:** Lines 194-217  
**Symptom:** NO sparklines render, change percentages show "—"

### Root Cause

**Completely hardcoded placeholder data** - not even querying database!

```python
def build_adgroup_metrics_cards():
    """
    Build financial_cards and actions_cards for M2 metrics_section macro on Ad Groups page.
    Currently returns placeholder static data.
    """
    financial_cards = [
        {'label':'Cost',         'value':'£0',     'change_pct':None,'sparkline':[],'card_type':'financial'},
        {'label':'Revenue',      'value':'£0',     'change_pct':None,'sparkline':[],'card_type':'financial'},
        {'label':'ROAS',         'value':'0.00',   'change_pct':None,'sparkline':[],'card_type':'financial'},
        # ... all hardcoded
    ]
    actions_cards = [
        {'label':'Impr.',        'value':'0',      'change_pct':None,'sparkline':[],'card_type':'actions'},
        # ... all hardcoded
    ]
    return financial_cards, actions_cards
```

### What's Missing

**EVERYTHING:**
1. No database connection parameter
2. No SQL queries at all
3. No current period query
4. No previous period query
5. No sparkline query
6. Returns static hardcoded dictionaries

### Fix Required

1. **Complete rewrite** - copy entire pattern from campaigns.py
2. Add function parameters: `(conn, customer_id, active_days, date_from, date_to)`
3. Add `_build_date_filters()` function
4. Add `_calculate_change_pct()` function
5. Add `_card()` helper function
6. Add `_blank_card()` helper function
7. Add 3 SQL queries (current, previous, sparkline)
8. Query `ro.analytics.ad_group_daily` table
9. Build cards dynamically from query results

---

## BROKEN ROUTE #3: ADS.PY

**File:** `act_dashboard/routes/ads.py`  
**Function:** `load_ads_metrics_cards()` (lines 260-313)  
**Symptom:** NO sparklines render, change percentages show "—"

### Root Cause

**Line 239:** Intentional comment - "Ads cards have no prev period"
```python
def _card_ads(label, value, sparkline, fmt, invert=False, card_type='financial', sub_label=None):
    """Ads cards have no prev period — change_pct always None (dash)."""
    return {
        'label': label,
        'value_display': _fmt_ads(value, fmt),
        'change_pct': None,  # ← HARDCODED TO NONE
        'sparkline_data': sparkline,
        'format_type': fmt,
        'invert_colours': invert,
        'card_type': card_type,
        'sub_label': sub_label,
    }
```

### Current Implementation

```python
# Only current period, no sparkline query at all
summary = conn.execute(f"""
    SELECT
        SUM(cost_micros_{window_suffix}_sum) / 1000000.0 AS cost,
        -- ... other metrics
    FROM ro.analytics.ad_features_daily
    WHERE customer_id = ? AND snapshot_date = ?
""", [customer_id, snapshot_date]).fetchone()

# Cards built with EMPTY sparkline arrays
financial_cards = [
    _card_ads('Cost', c[0], [], 'currency', invert=True),  # ← Empty list []
]
```

### What's Missing

1. No previous period query
2. No sparkline query
3. `_card_ads()` doesn't accept `prev` parameter
4. No `_calculate_change_pct()` function

### Fix Required

1. Add previous period query from `ro.analytics.ad_features_daily`
2. Add daily sparkline query from `ro.analytics.ad_daily`
3. Update `_card_ads()` to accept `prev` parameter
4. Add `_calculate_change_pct()` function
5. Build sparkline arrays from daily data
6. Update card definitions to pass prev and sparkline data

---

## BROKEN ROUTE #4: SHOPPING.PY

**File:** `act_dashboard/routes/shopping.py`  
**Function:** `build_campaign_metrics_cards()` + `build_product_metrics_cards()` (lines 535-619)  
**Symptom:** NO sparklines render, change percentages show "—"

### Root Cause

**Line 535:** Similar pattern - no prev parameter
```python
def _card_sh(label, value, fmt, invert=False, card_type='financial', sub_label=None):
    return {
        'label': label,
        'value_display': _fmt_sh(value, fmt),
        'change_pct': None,  # ← HARDCODED TO NONE
        'sparkline_data': [],  # ← HARDCODED EMPTY ARRAY
        'format_type': fmt,
        'invert_colours': invert,
        'card_type': card_type,
        'sub_label': sub_label,
    }
```

### Current Implementation

```python
# Only current period summary
campaign_metrics = conn.execute(f"""
    SELECT
        SUM(cost_micros_{window_suffix}_sum) / 1000000.0 AS cost,
        -- ... other metrics
    FROM ro.analytics.shopping_campaign_features_daily
    WHERE customer_id = ? AND snapshot_date = ?
""", [customer_id, snapshot_date]).fetchone()

# Cards built with no sparklines
camp_financial_cards = [
    _card_sh('Cost', c[0], 'currency', invert=True),  # No sparkline parameter
]
```

### What's Missing

1. No previous period queries
2. No sparkline queries
3. `_card_sh()` doesn't accept `prev` or `sparkline` parameters
4. No `_calculate_change_pct()` function

### Fix Required

1. Add previous period queries for both campaign and product metrics
2. Add daily sparkline queries from `ro.analytics.shopping_campaign_daily` and `ro.analytics.shopping_product_daily`
3. Update `_card_sh()` to accept `prev` and `sparkline` parameters
4. Add `_calculate_change_pct()` function
5. Build sparkline arrays from daily breakdown
6. Update all card definitions to pass prev and sparkline data

---

## DATABASE TABLES TO QUERY

### Dashboard & Campaigns (WORKING)
- Current/Previous: `ro.analytics.campaign_daily`
- Sparklines: `ro.analytics.campaign_daily` (GROUP BY snapshot_date)

### Keywords (BROKEN)
- Current: `ro.analytics.keyword_features_daily` (uses windowed columns)
- **Previous: NEEDS TO BE ADDED** - Same table, different date filter
- Sparklines: `ro.analytics.keyword_daily` (already queried, but change_pct missing)

### Ad Groups (BROKEN)
- **Current: NEEDS TO BE ADDED** - `ro.analytics.ad_group_features_daily`
- **Previous: NEEDS TO BE ADDED** - Same table, different date filter
- **Sparklines: NEEDS TO BE ADDED** - `ro.analytics.ad_group_daily`

### Ads (BROKEN)
- Current: `ro.analytics.ad_features_daily` (already queried)
- **Previous: NEEDS TO BE ADDED** - Same table, different date filter
- **Sparklines: NEEDS TO BE ADDED** - `ro.analytics.ad_daily`

### Shopping (BROKEN)
- Current Campaigns: `ro.analytics.shopping_campaign_features_daily` (already queried)
- Current Products: `ro.analytics.shopping_product_features_daily` (already queried)
- **Previous: NEEDS TO BE ADDED** - Both tables, different date filter
- **Sparklines: NEEDS TO BE ADDED** - `ro.analytics.shopping_campaign_daily`, `ro.analytics.shopping_product_daily`

---

## FIX STRATEGY

### Approach 1: Copy-Paste Pattern (RECOMMENDED)

**For each broken route:**
1. Copy `_build_date_filters()` from campaigns.py
2. Copy `_calculate_change_pct()` from campaigns.py
3. Copy `_card()` helper pattern from campaigns.py
4. Copy `_blank_card()` from campaigns.py
5. Add previous period query (copy structure from campaigns.py)
6. Add sparkline query if missing
7. Update function signatures to accept conn, customer_id, active_days, date_from, date_to
8. Extract current and previous values
9. Build sparkline arrays
10. Pass all 3 parameters to card builders

### Approach 2: Create Shared Utility Module

**Create:** `act_dashboard/routes/metrics_helpers.py`

```python
def calculate_change_pct(current, previous):
    """Shared across all routes"""
    if previous is None or previous == 0:
        return None
    if current is None:
        return -100.0
    return ((current - previous) / previous) * 100.0

def build_card(label, value, prev, sparkline, fmt, invert=False, card_type='financial'):
    """Shared card builder"""
    return {
        'label': label,
        'value_display': format_value(value, fmt),
        'change_pct': calculate_change_pct(value, prev),
        'sparkline_data': sparkline,
        'format_type': fmt,
        'invert_colours': invert,
        'card_type': card_type,
        'sub_label': None,
    }

# ... other shared functions
```

Then import in all routes and use consistently.

---

## TESTING VERIFICATION

### After Fix, Test Each Page:

**PowerShell Command:**
```powershell
cd C:\Users\User\Desktop\gads-data-layer
venv\Scripts\activate
python -m flask run
```

**Browser Test:**
1. Navigate to each page
2. Verify metrics cards show:
   - ✅ Colored sparklines (green/red/gray, not all grey)
   - ✅ Change percentages (not "—")
   - ✅ Interactive hover (dot follows mouse)
   - ✅ Tooltips show values

**SQL Verification:**
```python
import duckdb
conn = duckdb.connect('warehouse.duckdb', read_only=True)

# Verify tables exist
tables = conn.execute("SHOW TABLES").fetchall()
print("Available tables:", tables)

# Verify keyword_daily has data
result = conn.execute("""
    SELECT COUNT(*), MIN(snapshot_date), MAX(snapshot_date) 
    FROM ro.analytics.keyword_daily
""").fetchone()
print(f"keyword_daily: {result[0]} rows, {result[1]} to {result[2]}")

# Same for ad_group_daily, ad_daily, shopping tables
```

---

## ESTIMATED EFFORT

**Per Route:**
- Keywords: 1-2 hours (has sparklines, just needs prev period)
- Ad Groups: 3-4 hours (complete rewrite needed)
- Ads: 2-3 hours (needs prev + sparklines)
- Shopping: 2-3 hours (needs prev + sparklines, but 2 metrics types)

**Total:** 8-12 hours for all 4 routes

**Recommendation:** Fix in order of complexity:
1. Keywords (easiest - 40% done)
2. Ads (medium - 30% done)
3. Shopping (medium - 30% done)
4. Ad Groups (hardest - 0% done)

---

**Document:** BACKEND_ROUTES_DIAGNOSIS.md  
**Created:** 2026-02-28  
**Next Step:** Create worker brief for Chat 53
