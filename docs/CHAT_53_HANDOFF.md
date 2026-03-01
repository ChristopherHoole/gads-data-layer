# CHAT 53 HANDOFF DOCUMENT
## Backend Routes Metrics Fix - Technical Implementation Details

**Chat ID:** 53  
**Worker:** Chat 53 Backend Routes  
**Handoff To:** Master Chat / Chat 54  
**Date:** March 1, 2026  
**Status:** Complete - Ready for Git Commit

---

## 📋 TABLE OF CONTENTS

1. [Overview](#overview)
2. [Technical Architecture](#technical-architecture)
3. [File-by-File Changes](#file-by-file-changes)
4. [Database Schema](#database-schema)
5. [Testing Procedures](#testing-procedures)
6. [Git Commit Strategy](#git-commit-strategy)
7. [Known Issues & Limitations](#known-issues--limitations)
8. [Handoff to Chat 54](#handoff-to-chat-54)
9. [Appendix](#appendix)

---

## OVERVIEW

### Objective

Fix 3 backend routes to provide complete metrics cards data including:
- Period-over-period change percentages
- Colored sparklines from daily aggregated data
- Consistent helper function patterns
- Database-driven implementations (no hardcoded placeholders)

### Scope

**Routes Modified:**
1. Keywords (`/keywords`) - `act_dashboard/routes/keywords.py`
2. Shopping (`/shopping`) - `act_dashboard/routes/shopping.py`
3. Ad Groups (`/ad-groups`) - `act_dashboard/routes/ad_groups.py`

**Routes Deferred:**
1. Ads (`/ads`) - Requires `ad_daily` table creation → Chat 54

### Success Metrics

- ✅ 3/3 routes attempted = successfully fixed
- ✅ 100% success rate
- ✅ ~800 lines of code written
- ✅ 9 SQL queries added (3 current, 3 previous, 3 sparklines)
- ✅ 0 errors in console after fixes
- ✅ All visual bugs resolved

---

## TECHNICAL ARCHITECTURE

### Common Pattern Applied

All 3 routes now follow an identical pattern for metrics cards generation:

```
Helper Functions
    ↓
Date Filter Builder → Current Period Query → Extract Values
    ↓                      ↓                      ↓
Change Calculator ← Previous Period Query ← Extract Values
    ↓                      ↓                      ↓
Card Builder      ← Sparkline Query ───────→ Build Arrays
    ↓
Return (financial_cards, actions_cards)
```

### Helper Functions Architecture

**Five core helper functions added to each route:**

1. **`_build_date_filters(active_days, date_from, date_to)`**
   - Input: Date range parameters
   - Output: Tuple of (current_filter, prev_filter) SQL WHERE clauses
   - Purpose: Build consistent date filtering for all 3 queries

2. **`_calculate_change_pct(current, previous)`**
   - Input: Current and previous period values
   - Output: Percentage change (float) or None
   - Purpose: Calculate period-over-period change with None handling

3. **`_fmt(value, fmt)` or `_fmt_kw(value, fmt)` or `_fmt_sh(value, fmt)`**
   - Input: Value and format type (currency, percentage, ratio, number)
   - Output: Formatted string for display
   - Purpose: Consistent value formatting across all cards

4. **`_card()` or `_card_kw()` or `_card_sh()`**
   - Input: Label, current value, previous value, sparkline array, format, styling options
   - Output: Dictionary representing a metrics card
   - Purpose: Build card structure with change_pct and sparkline_data

5. **`_blank_card(card_type)`**
   - Input: Card type (financial or actions)
   - Output: Empty placeholder card dictionary
   - Purpose: Fill grid gaps in UI layout

### Database Query Pattern

**Each route executes 3 SQL queries:**

```sql
-- Query 1: Current Period Summary
SELECT SUM(cost_micros)/1000000.0 AS cost,
       SUM(conversions_value) AS revenue,
       SUM(conversions_value)/NULLIF(SUM(cost_micros)/1000000.0, 0) AS roas,
       SUM(conversions) AS conversions,
       (SUM(cost_micros)/1000000.0)/NULLIF(SUM(conversions), 0) AS cpa,
       SUM(clicks)*1.0/NULLIF(SUM(conversions), 0) AS cvr,
       SUM(impressions) AS impressions,
       SUM(clicks) AS clicks,
       (SUM(cost_micros)/1000000.0)/NULLIF(SUM(clicks), 0) AS cpc,
       SUM(clicks)*1.0/NULLIF(SUM(impressions), 0) AS ctr,
       AVG(search_impression_share) AS search_is,
       AVG(search_top_impression_share) AS search_top_is,
       AVG(search_absolute_top_impression_share) AS search_abs_top_is,
       AVG(click_share) AS click_share,
       SUM(CASE WHEN conversions = 0 AND cost_micros > 0
           THEN cost_micros/1000000.0 ELSE 0 END) AS wasted_spend
FROM ro.analytics.{table}_daily
WHERE customer_id = ? {current_filter}

-- Query 2: Previous Period Summary
[Same as Query 1 with prev_filter]

-- Query 3: Sparkline Data (Daily Aggregates)
SELECT snapshot_date,
       SUM(cost_micros)/1000000.0 AS cost,
       SUM(conversions_value) AS revenue,
       ... [14 metrics total]
FROM ro.analytics.{table}_daily
WHERE customer_id = ? {current_filter}
GROUP BY snapshot_date
ORDER BY snapshot_date ASC
```

### Data Flow

```
Route Handler
    ↓
Get date_from, date_to from session
    ↓
Call load_*_metrics_cards(conn, customer_id, active_days, date_from, date_to)
    ↓
_build_date_filters() → current_filter, prev_filter
    ↓
Execute 3 queries (current, previous, sparklines)
    ↓
Extract values: c[0..14], p[0..14], spark_rows[]
    ↓
Build sparkline arrays: _spark(col_idx, scale)
    ↓
Build cards: _card(label, c[i], p[i], sparkline, fmt, ...)
    ↓
Return (financial_cards, actions_cards)
    ↓
Pass to template via render_template()
```

---

## FILE-BY-FILE CHANGES

### 1. keywords.py

**File:** `act_dashboard/routes/keywords.py`  
**Path:** `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\keywords.py`  
**Lines Modified:** ~250 lines changed/added

#### Changes Made

**A. Helper Functions Added (Lines 555-592)**

```python
def _build_date_filters(active_days, date_from, date_to):
    """
    Build current and previous period date filters for SQL WHERE clauses.
    Returns tuple of (current_filter, prev_filter) starting with AND.
    """
    if date_from and date_to:
        _df = datetime.strptime(date_from, '%Y-%m-%d').date()
        _dt = datetime.strptime(date_to, '%Y-%m-%d').date()
        _span = (_dt - _df).days + 1
        _prev_to = (_df - timedelta(days=1)).isoformat()
        _prev_from = (_df - timedelta(days=_span)).isoformat()
        current_filter = f"AND snapshot_date >= '{date_from}' AND snapshot_date <= '{date_to}'"
        prev_filter = f"AND snapshot_date >= '{_prev_from}' AND snapshot_date <= '{_prev_to}'"
    else:
        days = active_days if active_days in [7, 30, 90] else 30
        current_filter = f"AND snapshot_date >= CURRENT_DATE - INTERVAL '{days} days'"
        prev_filter = (
            f"AND snapshot_date >= CURRENT_DATE - INTERVAL '{days * 2} days' "
            f"AND snapshot_date < CURRENT_DATE - INTERVAL '{days} days'"
        )
    return current_filter, prev_filter


def _calculate_change_pct(current, previous):
    """
    Calculate % change. Returns None (show dash) when no previous data.
    Never returns 0% to mask missing data.
    """
    if previous is None or previous == 0:
        return None
    if current is None:
        return -100.0
    return ((current - previous) / previous) * 100.0
```

**B. Updated `_card_kw()` Function (Lines 607-618)**

```python
# BEFORE:
def _card_kw(label, value, sparkline, fmt, invert=False, card_type='financial'):
    """Keywords cards have no prev period — change_pct always None (dash)."""
    return {
        'label': label,
        'value_display': _fmt_kw(value, fmt),
        'change_pct': None,  # ← Hardcoded None
        'sparkline_data': sparkline,
        'format_type': fmt,
        'invert_colours': invert,
        'card_type': card_type,
        'sub_label': None,
    }

# AFTER:
def _card_kw(label, value, prev, sparkline, fmt, invert=False, card_type='financial'):
    """Keywords cards with period-over-period comparison."""
    return {
        'label': label,
        'value_display': _fmt_kw(value, fmt),
        'change_pct': _calculate_change_pct(value, prev),  # ← Now calculates
        'sparkline_data': sparkline,
        'format_type': fmt,
        'invert_colours': invert,
        'card_type': card_type,
        'sub_label': None,
    }
```

**C. Updated `load_keyword_metrics_cards()` Function (Lines 594-715)**

**Function Signature Changed:**
```python
# BEFORE:
def load_keyword_metrics_cards(conn, customer_id, window_suffix, snapshot_date, active_days):

# AFTER:
def load_keyword_metrics_cards(conn, customer_id, window_suffix, snapshot_date, active_days, date_from=None, date_to=None):
```

**Query 1: Current Period Summary (Lines 645-673)**
```python
try:
    summary = conn.execute(f"""
        SELECT
            SUM(cost_micros) / 1000000.0                                      AS cost,
            SUM(conversions_value)                                             AS revenue,
            SUM(conversions_value) / NULLIF(SUM(cost_micros) / 1000000.0, 0)  AS roas,
            SUM(conversions)                                                   AS conversions,
            (SUM(cost_micros) / 1000000.0) / NULLIF(SUM(conversions), 0)      AS cpa,
            SUM(clicks) * 1.0 / NULLIF(SUM(conversions), 0)                   AS cvr,
            SUM(impressions)                                                   AS impressions,
            SUM(clicks)                                                        AS clicks,
            (SUM(cost_micros) / 1000000.0) / NULLIF(SUM(clicks), 0)           AS cpc,
            SUM(clicks) * 1.0 / NULLIF(SUM(impressions), 0)                   AS ctr,
            AVG(search_impression_share)                                       AS search_is,
            AVG(search_top_impression_share)                                   AS search_top_is,
            AVG(search_absolute_top_impression_share)                          AS search_abs_top_is,
            AVG(click_share)                                                   AS click_share,
            SUM(CASE WHEN conversions = 0 AND cost_micros > 0
                THEN cost_micros / 1000000.0 ELSE 0 END)                       AS wasted_spend
        FROM ro.analytics.keyword_daily
        WHERE customer_id = ?
          {current_filter}
    """, [customer_id]).fetchone()
except Exception as e:
    print(f"[Keywords M2] Current period query error: {e}")
    summary = None
```

**Query 2: Previous Period Summary (Lines 675-700)**
```python
try:
    prev_summary = conn.execute(f"""
        SELECT
            [Same 15 metrics as current period]
        FROM ro.analytics.keyword_daily
        WHERE customer_id = ?
          {prev_filter}
    """, [customer_id]).fetchone()
except Exception as e:
    print(f"[Keywords M2] Previous period query error: {e}")
    prev_summary = None
```

**Query 3: Sparkline Data (Lines 702-720)**
```python
try:
    spark_rows = conn.execute(f"""
        SELECT
            snapshot_date,
            SUM(cost_micros) / 1000000.0 AS cost,
            SUM(conversions_value) AS revenue,
            [... 14 metrics total ...]
        FROM ro.analytics.keyword_daily
        WHERE customer_id = ?
          {current_filter}
        GROUP BY snapshot_date
        ORDER BY snapshot_date ASC
    """, [customer_id]).fetchall()
except Exception as e:
    print(f"[Keywords M2] Sparkline query error: {e}")
    spark_rows = []
```

**Card Building (Lines 721-750)**
```python
def _v(row, i): return float(row[i]) if row and row[i] is not None else None
def pct(val): return val * 100 if val is not None else None

# Current period values
c = [_v(summary, i) for i in range(15)] if summary else [None] * 15

# Previous period values
p = [_v(prev_summary, i) for i in range(15)] if prev_summary else [None] * 15

# Build sparkline arrays
def _spark(col_idx, scale=1.0):
    return [float(r[col_idx]) * scale if r[col_idx] is not None else 0.0 for r in spark_rows]

financial_cards = [
    _card_kw('Cost',          c[0],        p[0],        _spark(1),        'currency',   invert=True),
    _card_kw('Revenue',       c[1],        p[1],        _spark(2),        'currency'),
    _card_kw('ROAS',          c[2],        p[2],        _spark(3),        'ratio'),
    _card_kw('Wasted Spend',  c[14],       p[14],       _spark(1),        'currency',   invert=True),
    _card_kw('Conversions',   c[3],        p[3],        _spark(4),        'number'),
    _card_kw('Cost / Conv',   c[4],        p[4],        _spark(5),        'currency',   invert=True),
    _card_kw('Conv Rate',     pct(c[5]),   pct(p[5]),   _spark(6, 100.0), 'percentage'),
    _blank_kw('financial'),
]

actions_cards = [
    _card_kw('Impressions',       c[6],        p[6],        _spark(7),         'number',     card_type='actions'),
    _card_kw('Clicks',            c[7],        p[7],        _spark(8),         'number',     card_type='actions'),
    _card_kw('Avg CPC',           c[8],        p[8],        _spark(9),         'currency',   card_type='actions'),
    _card_kw('Avg CTR',           pct(c[9]),   pct(p[9]),   _spark(10, 100.0), 'percentage', card_type='actions'),
    _card_kw('Search Impr Share', pct(c[10]),  pct(p[10]),  _spark(11, 100.0), 'percentage', card_type='actions'),
    _card_kw('Search Top IS',     pct(c[11]),  pct(p[11]),  _spark(12, 100.0), 'percentage', card_type='actions'),
    _card_kw('Search Abs Top IS', pct(c[12]),  pct(p[12]),  _spark(13, 100.0), 'percentage', card_type='actions'),
    _card_kw('Click Share',       pct(c[13]),  pct(p[13]),  _spark(14, 100.0), 'percentage', card_type='actions'),
]

return financial_cards, actions_cards
```

**D. Updated Function Call in Route (Line 1477-1479)**

```python
# BEFORE:
financial_cards, actions_cards = load_keyword_metrics_cards(
    conn, config.customer_id, window_suffix, snapshot_date, active_days
)

# AFTER:
financial_cards, actions_cards = load_keyword_metrics_cards(
    conn, config.customer_id, window_suffix, snapshot_date, active_days, date_from, date_to
)
```

#### Database Table Used

**Table:** `ro.analytics.keyword_daily`  
**Rows Available:** 77,368 rows  
**Date Range:** November 2025 - February 2026  
**Key Columns:**
- cost_micros (bigint)
- conversions_value (double)
- conversions (double)
- impressions (bigint)
- clicks (bigint)
- search_impression_share (double)
- search_top_impression_share (double)
- search_absolute_top_impression_share (double)
- click_share (double)
- snapshot_date (date)
- customer_id (varchar)

---

### 2. shopping.py

**File:** `act_dashboard/routes/shopping.py`  
**Path:** `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\shopping.py`  
**Lines Modified:** ~400 lines changed/added

#### Changes Made

**A. Helper Functions Added (Lines 517-575)**

```python
def _build_date_filters(active_days, date_from, date_to):
    """[Same as keywords.py]"""
    # ... implementation

def _calculate_change_pct(current, previous):
    """[Same as keywords.py]"""
    # ... implementation
```

**B. Updated `_card_sh()` Function (Lines 563-573)**

```python
# BEFORE:
def _card_sh(label, value, fmt, invert=False, card_type='financial', sub_label=None):
    return {
        'label': label,
        'value_display': _fmt_sh(value, fmt),
        'change_pct': None,  # ← Hardcoded None
        'sparkline_data': None,  # ← Hardcoded None
        'format_type': fmt,
        'invert_colours': invert,
        'card_type': card_type,
        'sub_label': sub_label,
    }

# AFTER:
def _card_sh(label, value, prev, sparkline, fmt, invert=False, card_type='financial', sub_label=None):
    """Shopping cards with period-over-period comparison."""
    return {
        'label': label,
        'value_display': _fmt_sh(value, fmt),
        'change_pct': _calculate_change_pct(value, prev),  # ← Now calculates
        'sparkline_data': sparkline,  # ← Now accepts data
        'format_type': fmt,
        'invert_colours': invert,
        'card_type': card_type,
        'sub_label': sub_label,
    }
```

**C. Replaced `build_campaign_metrics_cards()` Function (Lines 594-717)**

**Complete Function Replacement:**

```python
# BEFORE (Lines 556-587):
def build_campaign_metrics_cards(cm):
    total_cost       = cm.get('total_cost', 0) or 0
    total_conv_value = cm.get('total_conv_value', 0) or 0
    total_convs      = cm.get('total_conversions', 0) or 0
    total_impr       = cm.get('total_impressions', 0) or 0
    total_clicks     = cm.get('total_clicks', 0) or 0
    roas             = cm.get('overall_roas', 0) or 0
    cpa              = (total_cost / total_convs) if total_convs > 0 else None
    cvr              = (total_convs / total_clicks * 100) if total_clicks > 0 else None
    cpc              = (total_cost / total_clicks) if total_clicks > 0 else None
    ctr              = (total_clicks / total_impr * 100) if total_impr > 0 else None
    financial_cards = [
        _card_sh('Cost',         total_cost,       'currency',    invert=True),
        _card_sh('Conv Value',   total_conv_value, 'currency'),
        _card_sh('ROAS',         roas,             'ratio'),
        _blank_sh('financial'),
        _card_sh('Conversions',  total_convs,      'number'),
        _card_sh('Cost / Conv',  cpa,              'currency',    invert=True),
        _card_sh('Conv Rate',    cvr,              'percentage'),
        _blank_sh('financial'),
    ]
    actions_cards = [
        _card_sh('Impressions',  total_impr,   'number',     card_type='actions'),
        _card_sh('Clicks',       total_clicks, 'number',     card_type='actions'),
        _card_sh('Avg CPC',      cpc,          'currency',   card_type='actions'),
        _card_sh('Avg CTR',      ctr,          'percentage', card_type='actions'),
        _blank_sh('actions'),
        _blank_sh('actions'),
        _blank_sh('actions'),
        _blank_sh('actions'),
    ]
    return financial_cards, actions_cards

# AFTER (Lines 594-717):
def build_campaign_metrics_cards(
    conn: duckdb.DuckDBPyConnection,
    customer_id: str,
    active_days: int,
    date_from: Optional[str],
    date_to: Optional[str],
) -> Tuple[List[Dict], List[Dict]]:
    """
    Build financial_cards and actions_cards for Shopping Campaigns.
    
    Queries ro.analytics.shopping_campaign_daily for current, previous, and sparkline data.
    Returns tuple of (financial_cards, actions_cards).
    """
    current_filter, prev_filter = _build_date_filters(active_days, date_from, date_to)
    
    # Query 1: Current period
    try:
        summary = conn.execute(f"""
            SELECT
                SUM(cost_micros) / 1000000.0 AS cost,
                SUM(conversions_value) AS conv_value,
                [... 10 metrics total ...]
            FROM ro.analytics.shopping_campaign_daily
            WHERE customer_id = ? {current_filter}
        """, [customer_id]).fetchone()
    except Exception as e:
        print(f"[Shopping M2] Current period query error: {e}")
        summary = None
    
    # Query 2: Previous period
    try:
        prev_summary = conn.execute(f"""
            [Same query with prev_filter]
        """, [customer_id]).fetchone()
    except Exception as e:
        print(f"[Shopping M2] Previous period query error: {e}")
        prev_summary = None
    
    # Query 3: Sparklines
    try:
        spark_rows = conn.execute(f"""
            SELECT snapshot_date,
                   SUM(cost_micros)/1000000.0 AS cost,
                   [... 10 metrics total ...]
            FROM ro.analytics.shopping_campaign_daily
            WHERE customer_id = ? {current_filter}
            GROUP BY snapshot_date
            ORDER BY snapshot_date ASC
        """, [customer_id]).fetchall()
    except Exception as e:
        print(f"[Shopping M2] Sparkline query error: {e}")
        spark_rows = []
    
    # Extract values and build cards
    def _v(row, i): return float(row[i]) if row and row[i] is not None else None
    def pct(val): return val * 100 if val is not None else None
    
    c = [_v(summary, i) for i in range(10)] if summary else [None] * 10
    p = [_v(prev_summary, i) for i in range(10)] if prev_summary else [None] * 10
    
    def _spark(col_idx, scale=1.0):
        return [float(r[col_idx]) * scale if r[col_idx] is not None else 0.0 for r in spark_rows]
    
    financial_cards = [
        _card_sh('Cost',         c[0],        p[0],        _spark(1),        'currency',   invert=True),
        _card_sh('Revenue',      c[1],        p[1],        _spark(2),        'currency'),  # ← Fixed label
        _card_sh('ROAS',         c[2],        p[2],        _spark(3),        'ratio'),
        _blank_sh('financial'),
        _card_sh('Conversions',  c[3],        p[3],        _spark(4),        'number'),
        _card_sh('Cost / Conv',  c[4],        p[4],        _spark(5),        'currency',   invert=True),
        _card_sh('Conv Rate',    pct(c[5]),   pct(p[5]),   _spark(6, 100.0), 'percentage'),
        _blank_sh('financial'),
    ]
    
    actions_cards = [
        _card_sh('Impressions',  c[6],        p[6],        _spark(7),         'number',     card_type='actions'),
        _card_sh('Clicks',       c[7],        p[7],        _spark(8),         'number',     card_type='actions'),
        _card_sh('Avg CPC',      c[8],        p[8],        _spark(9),         'currency',   card_type='actions'),
        _card_sh('Avg CTR',      pct(c[9]),   pct(p[9]),   _spark(10, 100.0), 'percentage', card_type='actions'),
        _blank_sh('actions'),
        _blank_sh('actions'),
        _blank_sh('actions'),
        _blank_sh('actions'),
    ]
    
    return financial_cards, actions_cards
```

**D. Updated `build_product_metrics_cards()` (Lines 720-758)**

```python
def build_product_metrics_cards(pm):
    """
    Product metrics cards - incomplete (shopping_product_daily table doesn't exist yet).
    Uses None for prev (no period comparison) and [] for sparklines (no daily data).
    """
    total_cost    = pm.get('total_cost', 0) or 0
    total_convs   = pm.get('total_conversions', 0) or 0
    roas          = pm.get('overall_roas', 0) or 0
    oos           = pm.get('out_of_stock_count', 0) or 0
    feed_issues   = pm.get('feed_issues_count', 0) or 0
    total_prods   = pm.get('total_products', 0) or 0
    oos_sub       = 'Needs attention' if oos > 0 else 'All in stock'
    issues_sub    = 'Price mismatch/disapproved' if feed_issues > 0 else 'No issues'
    
    # No prev or sparkline data - product_daily table doesn't exist
    financial_cards = [
        _card_sh('Cost',          total_cost,  None, [], 'currency',  invert=True),
        _card_sh('ROAS',          roas,        None, [], 'ratio'),
        _blank_sh('financial'),
        _card_sh('Out of Stock',  oos,         None, [], 'number',    invert=True, sub_label=oos_sub),
        _card_sh('Conversions',   total_convs, None, [], 'number'),
        _blank_sh('financial'),
        _blank_sh('financial'),
        _blank_sh('financial'),
    ]
    actions_cards = [
        _card_sh('Products',    total_prods,  None, [], 'number',  card_type='actions'),
        _card_sh('Feed Issues', feed_issues,  None, [], 'number',  card_type='actions', invert=True, sub_label=issues_sub),
        _blank_sh('actions'),
        _blank_sh('actions'),
        _blank_sh('actions'),
        _blank_sh('actions'),
        _blank_sh('actions'),
        _blank_sh('actions'),
    ]
    return financial_cards, actions_cards
```

**E. Updated Function Call in Route (Lines 933-938) - CRITICAL FIX**

```python
# BEFORE (INCORRECT - caused "Connection already closed" error):
chart_data = _build_shopping_chart_data(conn, config.customer_id, active_days, date_from, date_to)

conn.close()  # ← Connection closed HERE

# ── Rules ──
try:
    rules = get_rules_for_page('shopping', customer_id=config.customer_id)
    rule_counts = count_rules_by_category(rules)
except Exception as e:
    print(f"[Shopping] Rules error: {e}")
    rules, rule_counts = [], {}

print(f"[Shopping] campaigns={len(all_campaigns)}, products={len(all_products)} ...")

# M2: Build metrics cards
camp_financial_cards, camp_actions_cards = build_campaign_metrics_cards(
    conn, config.customer_id, active_days, date_from, date_to  # ← Error! conn already closed
)

# AFTER (CORRECT):
chart_data = _build_shopping_chart_data(conn, config.customer_id, active_days, date_from, date_to)

# M2: Build metrics cards (MUST be before conn.close())
camp_financial_cards, camp_actions_cards = build_campaign_metrics_cards(
    conn, config.customer_id, active_days, date_from, date_to  # ← Works! conn still open
)
prod_financial_cards, prod_actions_cards = build_product_metrics_cards(product_metrics)
metrics_collapsed = get_metrics_collapsed('shopping')

conn.close()  # ← Connection closed AFTER all queries

# ── Rules ──
try:
    rules = get_rules_for_page('shopping', customer_id=config.customer_id)
    rule_counts = count_rules_by_category(rules)
except Exception as e:
    print(f"[Shopping] Rules error: {e}")
    rules, rule_counts = [], {}
```

**F. Label Fix for Border Color (Line 685)**

```python
# BEFORE:
_card_sh('Conv Value',   c[1],        p[1],        _spark(2),        'currency'),  # ← Blue border (wrong)

# AFTER:
_card_sh('Revenue',      c[1],        p[1],        _spark(2),        'currency'),  # ← Green border (correct)
```

#### Database Table Used

**Table:** `ro.analytics.shopping_campaign_daily`  
**Rows Available:** 7,300 rows  
**Date Range:** February 2025 - February 2026  
**Key Columns:**
- cost_micros (bigint)
- conversions_value (double)
- conversions (double)
- impressions (bigint)
- clicks (bigint)
- snapshot_date (date)
- customer_id (varchar)
- campaign_id (varchar)
- campaign_name (varchar)
- campaign_status (varchar)

---

### 3. ad_groups.py

**File:** `act_dashboard/routes/ad_groups.py`  
**Path:** `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\ad_groups.py`  
**Lines Modified:** ~300 lines changed/added

#### Changes Made

**A. Helper Functions Added (Lines 193-272)**

```python
def _build_date_filters(active_days, date_from, date_to):
    """[Same as keywords.py and shopping.py]"""
    # ... implementation

def _calculate_change_pct(current, previous):
    """[Same as keywords.py and shopping.py]"""
    # ... implementation

def _fmt(value, fmt):
    """Format values for display."""
    if value is None:
        return '—'
    v = float(value)
    if fmt == 'currency':
        if v >= 1_000_000: return f'${v/1_000_000:.1f}M'
        if v >= 1_000: return f'${v/1_000:.1f}k'
        return f'${v:,.2f}'
    if fmt in ('percentage', 'rate'): return f'{v:.1f}%'
    if fmt == 'ratio': return f'{v:.2f}x'
    if fmt == 'number':
        if v >= 1_000_000: return f'{v/1_000_000:.2f}M'
        if v >= 1_000: return f'{v/1_000:.1f}k'
        return f'{v:,.0f}'
    return str(v)

def _card(label, value, prev, sparkline, fmt, invert=False, card_type='financial'):
    """Build a metrics card with period-over-period comparison."""
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

def _blank_card(card_type='financial'):
    """Build a blank placeholder card."""
    return {
        'label': '', 'value_display': '', 'change_pct': None,
        'sparkline_data': None, 'format_type': 'blank',
        'invert_colours': False, 'card_type': card_type, 'sub_label': None,
    }
```

**B. Completely Replaced `load_ad_group_metrics_cards()` Function (Lines 275-406)**

**BEFORE (Lines 192-300) - Placeholder Implementation:**
```python
def load_ad_group_metrics_cards(conn, customer_id: str, date_filter: str, prev_filter: str):
    """
    Build financial_cards and actions_cards for M2 metrics_section macro on Ad Groups page.
    Uses ro.analytics.ad_group_daily (account-level totals).
    Includes sparklines and change indicators.
    """
    _empty_fin = [
        {'label':'Cost', 'value':'£0', 'change_pct':None, 'sparkline':[], 'card_type':'financial'},
        # ... hardcoded placeholders
    ]
    _empty_act = [
        {'label':'Impr.', 'value':'0', 'change_pct':None, 'sparkline':[], 'card_type':'actions'},
        # ... hardcoded placeholders
    ]
    
    # Queries using string replacement for filters
    q_cur = f"""SELECT ... FROM ro.analytics.ad_group_daily WHERE customer_id = ? {date_filter}"""
    q_prv = q_cur.replace(date_filter, prev_filter)
    q_sparkline = f"""SELECT ... FROM ro.analytics.ad_group_daily WHERE customer_id = ? {date_filter} ..."""
    
    try:
        c = conn.execute(q_cur, [customer_id]).fetchone()
        p = conn.execute(q_prv, [customer_id]).fetchone()
        sp_rows = conn.execute(q_sparkline, [customer_id]).fetchall()
    except Exception as e:
        print(f"[AdGroups M2] error: {e}")
        return _empty_fin, _empty_act
    
    # Manual value extraction with £ symbols
    financial_cards = [
        _card_ag('Cost', f"£{c_cost:,.0f}" if c_cost else '£0', _chg(c_cost,p_cost), _spark(1), 'currency'),
        # ... more manual formatting with £
    ]
    
    return financial_cards, actions_cards
```

**AFTER (Lines 275-406) - Database-Driven Implementation:**
```python
def load_ad_group_metrics_cards(conn, customer_id: str, active_days: int, date_from=None, date_to=None):
    """
    Build financial_cards and actions_cards for Ad Groups page.
    
    Uses ro.analytics.ad_group_daily for all queries (current, previous, sparklines).
    Compares current period vs previous period for change percentages.
    
    Financial (8): Cost | Revenue | ROAS | Wasted Spend | Conv | CPA | CVR | BLANK
    Actions  (8): Impressions | Clicks | CPC | CTR | Search IS | Top IS | Abs Top IS | Click Share
    """
    current_filter, prev_filter = _build_date_filters(active_days, date_from, date_to)
    
    # ── Query 1: Current period summary from ad_group_daily ──
    try:
        summary = conn.execute(f"""
            SELECT
                SUM(cost_micros) / 1000000.0 AS cost,
                SUM(conversions_value) AS revenue,
                SUM(conversions_value) / NULLIF(SUM(cost_micros) / 1000000.0, 0) AS roas,
                SUM(conversions) AS conversions,
                (SUM(cost_micros) / 1000000.0) / NULLIF(SUM(conversions), 0) AS cpa,
                SUM(clicks) * 1.0 / NULLIF(SUM(conversions), 0) AS cvr,
                SUM(impressions) AS impressions,
                SUM(clicks) AS clicks,
                (SUM(cost_micros) / 1000000.0) / NULLIF(SUM(clicks), 0) AS cpc,
                SUM(clicks) * 1.0 / NULLIF(SUM(impressions), 0) AS ctr,
                AVG(search_impression_share) AS search_is,
                AVG(search_top_impression_share) AS search_top_is,
                AVG(search_absolute_top_impression_share) AS search_abs_top_is,
                AVG(click_share) AS click_share,
                SUM(CASE WHEN conversions = 0 AND cost_micros > 0
                    THEN cost_micros / 1000000.0 ELSE 0 END) AS wasted_spend
            FROM ro.analytics.ad_group_daily
            WHERE customer_id = ?
              {current_filter}
        """, [customer_id]).fetchone()
    except Exception as e:
        print(f"[AdGroups M2] Current period query error: {e}")
        summary = None
    
    # ── Query 2: Previous period summary from ad_group_daily ──
    try:
        prev_summary = conn.execute(f"""
            [Same 15 metrics with prev_filter]
        """, [customer_id]).fetchone()
    except Exception as e:
        print(f"[AdGroups M2] Previous period query error: {e}")
        prev_summary = None
    
    # ── Query 3: Daily sparkline data from ad_group_daily ──
    try:
        spark_rows = conn.execute(f"""
            SELECT
                snapshot_date,
                SUM(cost_micros) / 1000000.0 AS cost,
                [... 14 metrics total ...]
            FROM ro.analytics.ad_group_daily
            WHERE customer_id = ?
              {current_filter}
            GROUP BY snapshot_date
            ORDER BY snapshot_date ASC
        """, [customer_id]).fetchall()
    except Exception as e:
        print(f"[AdGroups M2] Sparkline query error: {e}")
        spark_rows = []
    
    def _v(row, i): return float(row[i]) if row and row[i] is not None else None
    def pct(val): return val * 100 if val is not None else None
    
    # Current period values
    c = [_v(summary, i) for i in range(15)] if summary else [None] * 15
    
    # Previous period values
    p = [_v(prev_summary, i) for i in range(15)] if prev_summary else [None] * 15
    
    # Build sparkline arrays
    def _spark(col_idx, scale=1.0):
        return [float(r[col_idx]) * scale if r[col_idx] is not None else 0.0 for r in spark_rows]
    
    financial_cards = [
        _card('Cost',          c[0],        p[0],        _spark(1),        'currency',   invert=True),
        _card('Revenue',       c[1],        p[1],        _spark(2),        'currency'),
        _card('ROAS',          c[2],        p[2],        _spark(3),        'ratio'),
        _card('Wasted Spend',  c[14],       p[14],       _spark(1),        'currency',   invert=True),
        _card('Conversions',   c[3],        p[3],        _spark(4),        'number'),
        _card('Cost / Conv',   c[4],        p[4],        _spark(5),        'currency',   invert=True),
        _card('Conv Rate',     pct(c[5]),   pct(p[5]),   _spark(6, 100.0), 'percentage'),
        _blank_card('financial'),
    ]
    
    actions_cards = [
        _card('Impressions',       c[6],        p[6],        _spark(7),         'number',     card_type='actions'),
        _card('Clicks',            c[7],        p[7],        _spark(8),         'number',     card_type='actions'),
        _card('Avg CPC',           c[8],        p[8],        _spark(9),         'currency',   card_type='actions'),
        _card('Avg CTR',           pct(c[9]),   pct(p[9]),   _spark(10, 100.0), 'percentage', card_type='actions'),
        _card('Search Impr Share', pct(c[10]),  pct(p[10]),  _spark(11, 100.0), 'percentage', card_type='actions'),
        _card('Search Top IS',     pct(c[11]),  pct(p[11]),  _spark(12, 100.0), 'percentage', card_type='actions'),
        _card('Search Abs Top IS', pct(c[12]),  pct(p[12]),  _spark(13, 100.0), 'percentage', card_type='actions'),
        _card('Click Share',       pct(c[13]),  pct(p[13]),  _spark(14, 100.0), 'percentage', card_type='actions'),
    ]
    
    return financial_cards, actions_cards
```

**C. Updated Function Call in Route (Lines 530-532)**

```python
# BEFORE:
financial_cards, actions_cards = load_ad_group_metrics_cards(
    conn, config.customer_id, _date_filter, _prev_filter
)

# AFTER:
financial_cards, actions_cards = load_ad_group_metrics_cards(
    conn, config.customer_id, active_days, date_from, date_to
)
```

#### Database Table Used

**Table:** `ro.analytics.ad_group_daily`  
**Rows Available:** 23,725 rows  
**Date Range:** February 2025 - February 2026  
**Key Columns:**
- cost_micros (bigint)
- conversions_value (double)
- conversions (double)
- impressions (bigint)
- clicks (bigint)
- search_impression_share (double)
- search_top_impression_share (double)
- search_absolute_top_impression_share (double)
- click_share (double)
- snapshot_date (date)
- customer_id (varchar)
- ad_group_id (varchar)
- ad_group_name (varchar)
- ad_group_status (varchar)

---

## DATABASE SCHEMA

### Tables Utilized

#### 1. ro.analytics.keyword_daily

**Purpose:** Daily keyword-level performance metrics  
**Rows:** 77,368  
**Date Range:** November 2025 - February 2026

**Key Columns:**
```sql
customer_id VARCHAR
keyword_id VARCHAR
snapshot_date DATE
cost_micros BIGINT
conversions_value DOUBLE
conversions DOUBLE
impressions BIGINT
clicks BIGINT
search_impression_share DOUBLE
search_top_impression_share DOUBLE
search_absolute_top_impression_share DOUBLE
click_share DOUBLE
```

**Sample Query:**
```sql
SELECT COUNT(*), MIN(snapshot_date), MAX(snapshot_date)
FROM ro.analytics.keyword_daily
WHERE customer_id = '7372844356';
-- Result: 77,368 rows, 2025-11-01 to 2026-02-28
```

#### 2. ro.analytics.shopping_campaign_daily

**Purpose:** Daily shopping campaign performance metrics  
**Rows:** 7,300  
**Date Range:** February 2025 - February 2026

**Key Columns:**
```sql
customer_id VARCHAR
campaign_id VARCHAR
campaign_name VARCHAR
campaign_status VARCHAR
snapshot_date DATE
cost_micros BIGINT
conversions_value DOUBLE
conversions DOUBLE
impressions BIGINT
clicks BIGINT
```

**Sample Query:**
```sql
SELECT COUNT(*), MIN(snapshot_date), MAX(snapshot_date)
FROM ro.analytics.shopping_campaign_daily
WHERE customer_id = '7372844356';
-- Result: 7,300 rows, 2025-02-01 to 2026-02-28
```

#### 3. ro.analytics.ad_group_daily

**Purpose:** Daily ad group performance metrics  
**Rows:** 23,725  
**Date Range:** February 2025 - February 2026

**Key Columns:**
```sql
customer_id VARCHAR
ad_group_id VARCHAR
ad_group_name VARCHAR
ad_group_status VARCHAR
campaign_id VARCHAR
snapshot_date DATE
cost_micros BIGINT
conversions_value DOUBLE
conversions DOUBLE
impressions BIGINT
clicks BIGINT
search_impression_share DOUBLE
search_top_impression_share DOUBLE
search_absolute_top_impression_share DOUBLE
click_share DOUBLE
target_cpa_micros BIGINT
```

**Sample Query:**
```sql
SELECT COUNT(*), MIN(snapshot_date), MAX(snapshot_date)
FROM ro.analytics.ad_group_daily
WHERE customer_id = '7372844356';
-- Result: 23,725 rows, 2025-02-01 to 2026-02-28
```

### Tables NOT Used (Deferred)

#### ro.analytics.ad_daily

**Status:** Does not exist  
**Required For:** Ads page metrics cards  
**Deferred To:** Chat 54

**Expected Schema:**
```sql
CREATE TABLE ro.analytics.ad_daily (
    customer_id VARCHAR,
    ad_id VARCHAR,
    ad_group_id VARCHAR,
    campaign_id VARCHAR,
    snapshot_date DATE,
    cost_micros BIGINT,
    conversions_value DOUBLE,
    conversions DOUBLE,
    impressions BIGINT,
    clicks BIGINT,
    -- ... additional metrics
);
```

**Impact:** Ads page shows placeholder metrics until table is created

---

## TESTING PROCEDURES

### Pre-Deployment Testing Checklist

**Environment Setup:**
```powershell
cd C:\Users\User\Desktop\gads-data-layer
.\.venv\Scripts\Activate.ps1
python act_dashboard/app.py
```

**Browser:** Opera (primary), Chrome (fallback)  
**Test URL:** http://127.0.0.1:5000

### Test Cases

#### Test Case 1: Keywords Page Load

**Steps:**
1. Navigate to http://127.0.0.1:5000/keywords
2. Verify page loads without errors (200 status)
3. Verify Financial metrics section displays 8 cards
4. Verify Actions metrics section displays 8 cards

**Expected Results:**
- All 15 cards show real values (not "—" placeholders)
- Change percentages display actual values (+402.9%, +400.1%, etc.)
- Sparklines are colored (green/red/grey)
- No console errors (F12)

**Actual Results:**
✅ PASS - All metrics displaying correctly

#### Test Case 2: Keywords Date Range Changes

**Steps:**
1. Click "7d" button
2. Verify metrics update
3. Click "30d" button
4. Verify metrics update
5. Click "90d" button
6. Verify metrics update

**Expected Results:**
- Metrics values change for each date range
- Sparklines adjust to show appropriate number of days
- No errors in console
- Change percentages recalculate

**Actual Results:**
✅ PASS - Confirmed verbally by Christopher

#### Test Case 3: Keywords Actions Toggle

**Steps:**
1. Click "▼ Actions metrics" to collapse
2. Verify Actions section collapses
3. Click "▶ Actions metrics" to expand
4. Verify Actions section expands

**Expected Results:**
- Smooth collapse/expand animation
- State persists on page reload
- No JavaScript errors

**Actual Results:**
✅ PASS - Confirmed verbally by Christopher

#### Test Case 4: Shopping Page Load

**Steps:**
1. Navigate to http://127.0.0.1:5000/shopping
2. Verify page loads without errors (200 status)
3. Verify Campaign Financial metrics section displays 4 cards
4. Verify Campaign Leads metrics section displays 3 cards
5. Verify Campaign Actions metrics section displays 4 cards

**Expected Results:**
- All campaign cards show real values
- Revenue card has GREEN border (not blue)
- Change percentages display actual values
- Sparklines are colored
- No "Connection already closed" errors
- No console errors

**Actual Results:**
✅ PASS - All metrics displaying correctly, Revenue border green

#### Test Case 5: Shopping Date Range Changes

**Steps:**
1. Click "7d" button
2. Verify campaign metrics update
3. Click "30d" button
4. Verify campaign metrics update
5. Click "90d" button
6. Verify campaign metrics update

**Expected Results:**
- Campaign metrics values change
- Sparklines adjust appropriately
- No errors in console

**Actual Results:**
✅ PASS - Confirmed verbally by Christopher

#### Test Case 6: Ad Groups Page Load

**Steps:**
1. Navigate to http://127.0.0.1:5000/ad-groups
2. Verify page loads without errors (200 status)
3. Verify Financial metrics section displays 8 cards
4. Verify Actions metrics section displays 8 cards

**Expected Results:**
- All 15 cards show real values
- $ symbols used (not £)
- Change percentages display actual values
- Sparklines are colored
- No console errors

**Actual Results:**
✅ PASS - All metrics displaying correctly with $ symbols

#### Test Case 7: Ad Groups Date Range Changes

**Steps:**
1. Click "7d" button
2. Verify metrics update
3. Click "30d" button
4. Verify metrics update
5. Click "90d" button
6. Verify metrics update

**Expected Results:**
- Metrics values change appropriately
- Sparklines adjust to show appropriate data range
- No errors in console

**Actual Results:**
✅ PASS - Confirmed verbally by Christopher

#### Test Case 8: Cross-Page Consistency

**Steps:**
1. Visit Keywords, Shopping, and Ad Groups pages
2. Compare metrics card layouts
3. Verify border colors match categories
4. Verify currency symbols are consistent
5. Verify change percentage formatting is consistent

**Expected Results:**
- All pages use $ symbols (not £)
- Financial cards have green borders
- Leads cards have blue borders
- Actions cards have white borders
- Change percentages format as +12.5% or -3.2%

**Actual Results:**
✅ PASS - Confirmed through screenshots

#### Test Case 9: Sparkline Hover Interaction

**Steps:**
1. Hover mouse over any sparkline
2. Verify dot appears on line
3. Verify dot follows mouse movement
4. Verify tooltip displays with value

**Expected Results:**
- Dot appears instantly on hover
- Dot follows mouse smoothly
- Tooltip shows formatted value
- No JavaScript errors

**Actual Results:**
✅ PASS - Confirmed verbally by Christopher

#### Test Case 10: Console Error Check

**Steps:**
1. Open browser console (F12)
2. Navigate to Keywords page
3. Check for errors
4. Navigate to Shopping page
5. Check for errors
6. Navigate to Ad Groups page
7. Check for errors

**Expected Results:**
- No JavaScript errors
- No 500 server errors
- Only 200 status codes in Network tab

**Actual Results:**
✅ PASS - Confirmed verbally by Christopher

### Regression Testing

**Pages Not Modified (Should Still Work):**
- ✅ Dashboard page
- ✅ Campaigns page
- ⚠️ Ads page (incomplete but not broken)

**Verified:** All unmodified pages continue to function correctly

---

## GIT COMMIT STRATEGY

### Commit Message

```
feat(routes): Add period-over-period metrics and sparklines to Keywords, Shopping, Ad Groups

- Keywords: Add current/previous period queries from keyword_daily
- Shopping: Add current/previous period queries from shopping_campaign_daily
- Ad Groups: Rewrite metrics cards with database queries from ad_group_daily
- All routes: Add helper functions for date filters, change calculations, formatting
- All routes: Add sparkline queries with GROUP BY snapshot_date
- Fix: Move Shopping metrics cards before conn.close() to prevent connection errors
- Fix: Change Shopping Revenue label to fix border color categorization

Fixes metrics cards to show real change percentages and colored sparklines.
Chat 53 complete: 3/3 routes fixed, 5/6 pages fully functional.
Ads page deferred to Chat 54 (requires ad_daily table creation).
```

### Files to Commit

```bash
# Modified files
modified:   act_dashboard/routes/keywords.py
modified:   act_dashboard/routes/shopping.py
modified:   act_dashboard/routes/ad_groups.py

# New documentation files
new file:   docs/CHAT_53_SUMMARY.md
new file:   docs/CHAT_53_HANDOFF.md
```

### Git Commands

```bash
# Navigate to repository
cd C:\Users\User\Desktop\gads-data-layer

# Check current status
git status

# Add modified files
git add act_dashboard/routes/keywords.py
git add act_dashboard/routes/shopping.py
git add act_dashboard/routes/ad_groups.py

# Add documentation
git add docs/CHAT_53_SUMMARY.md
git add docs/CHAT_53_HANDOFF.md

# Commit with detailed message
git commit -m "feat(routes): Add period-over-period metrics and sparklines to Keywords, Shopping, Ad Groups

- Keywords: Add current/previous period queries from keyword_daily
- Shopping: Add current/previous period queries from shopping_campaign_daily
- Ad Groups: Rewrite metrics cards with database queries from ad_group_daily
- All routes: Add helper functions for date filters, change calculations, formatting
- All routes: Add sparkline queries with GROUP BY snapshot_date
- Fix: Move Shopping metrics cards before conn.close() to prevent connection errors
- Fix: Change Shopping Revenue label to fix border color categorization

Fixes metrics cards to show real change percentages and colored sparklines.
Chat 53 complete: 3/3 routes fixed, 5/6 pages fully functional.
Ads page deferred to Chat 54 (requires ad_daily table creation)."

# Push to remote (if applicable)
git push origin main
```

### Pre-Commit Checklist

- [x] All 3 routes tested and working
- [x] No console errors
- [x] All visual bugs fixed
- [x] Documentation created
- [x] Commit message prepared
- [ ] Git add executed
- [ ] Git commit executed
- [ ] Git push executed (if applicable)

---

## KNOWN ISSUES & LIMITATIONS

### Issue 1: Ads Page Incomplete

**Status:** Deferred to Chat 54  
**Severity:** Medium  
**Impact:** 1 of 6 pages shows placeholder data

**Description:**
The Ads page (`/ads`) metrics cards currently return hardcoded placeholder values with no change percentages or sparklines. This is because the `ro.analytics.ad_daily` table does not exist in the database.

**Current Behavior:**
- Page loads successfully
- Metrics cards display but show "—" for change percentages
- Sparklines show empty arrays (grey flat lines)
- Functionality is not broken, just incomplete

**Root Cause:**
```sql
-- Table does not exist:
SELECT * FROM ro.analytics.ad_daily;
-- Binder Error: Table "ro.analytics.ad_daily" does not exist!
```

**Workaround:**
None - page displays placeholder data until table is created

**Fix Required:**
1. Create synthetic `ad_daily` table with ~1 year of data
2. Apply same pattern as Chat 53 to `ads.py` route
3. Add helper functions and database queries
4. Test thoroughly

**Timeline:** Chat 54

### Issue 2: Shopping Products Metrics Incomplete

**Status:** Known limitation  
**Severity:** Low  
**Impact:** Products tab shows current values only

**Description:**
The Shopping Products tab metrics cards do not show period-over-period comparisons or sparklines because the `ro.analytics.shopping_product_daily` table does not exist.

**Current Behavior:**
- Products tab loads successfully
- Metrics cards show current values from `product_features_daily`
- Change percentages show "—" (None)
- Sparklines show empty arrays

**Root Cause:**
Table `ro.analytics.shopping_product_daily` does not exist

**Workaround:**
None - uses `product_features_daily` with windowed columns instead

**Fix Required:**
1. Create `shopping_product_daily` table in data pipeline
2. Populate with daily product-level metrics
3. Update `build_product_metrics_cards()` to query daily table
4. Add current/previous/sparkline queries

**Timeline:** Future - when product daily data pipeline is built

### Issue 3: Custom Date Ranges on Keywords Page

**Status:** Working as designed  
**Severity:** Low  
**Impact:** Custom ranges fall back to 30-day window

**Description:**
Keywords page uses pre-aggregated windowed columns (`_w7`, `_w30`) from `keyword_features_daily` table for the metrics bar (top section), but now uses `keyword_daily` for metrics cards. Custom date ranges work for metrics cards but the top metrics bar falls back to w30 columns.

**Current Behavior:**
- Custom date range selection works
- Metrics cards adjust correctly
- Top metrics bar falls back to 30-day window
- Warning printed: "[Keywords] Custom date range selected — using w30 windowed columns as approximation"

**Workaround:**
Use preset date ranges (7d, 30d, 90d) for full accuracy

**Fix Required:**
Refactor metrics bar to also query `keyword_daily` with custom date filters (low priority)

**Timeline:** Future enhancement

---

## HANDOFF TO CHAT 54

### Chat 54 Objective

Fix Ads page metrics cards by creating synthetic `ad_daily` table and implementing database queries.

### Required Actions for Chat 54

#### 1. Create Synthetic ad_daily Table

**Script:** Create Python script to generate synthetic data

**Schema:**
```sql
CREATE TABLE ro.analytics.ad_daily (
    customer_id VARCHAR,
    ad_id VARCHAR,
    ad_group_id VARCHAR,
    campaign_id VARCHAR,
    ad_type VARCHAR,
    ad_status VARCHAR,
    snapshot_date DATE,
    cost_micros BIGINT,
    conversions_value DOUBLE,
    conversions DOUBLE,
    impressions BIGINT,
    clicks BIGINT,
    -- Additional metrics as needed
);
```

**Data Requirements:**
- ~1 year of daily data (365 days)
- ~1,000 unique ads
- Realistic distributions (Pareto for cost, normal for CTR, etc.)
- Date range: March 2025 - February 2026
- Customer ID: 7372844356

**Estimated Rows:** ~365,000 (1,000 ads × 365 days)

#### 2. Apply Chat 53 Pattern to ads.py

**File:** `act_dashboard/routes/ads.py`

**Changes Required:**
1. Add helper functions (_build_date_filters, _calculate_change_pct, _fmt, _card, _blank_card)
2. Update or replace metrics cards function
3. Add 3 SQL queries (current, previous, sparklines) from `ro.analytics.ad_daily`
4. Update function call in route
5. Test thoroughly

**Pattern to Follow:**
Use ad_groups.py as reference (most complete implementation)

#### 3. Testing

**Test Cases:**
- Verify page loads without errors
- Verify all metrics cards show real values
- Verify change percentages calculate correctly
- Verify sparklines render with colors
- Verify date range buttons work
- Verify Actions toggle works
- Verify console shows no errors

**Success Criteria:**
- All 15 cards functional (8 financial + 7 actions + 1 blank)
- Change percentages showing actual values
- Sparklines colored appropriately
- No console errors
- All date ranges working

#### 4. Documentation

**Required Documents:**
- CHAT_54_SUMMARY.md (executive overview)
- CHAT_54_HANDOFF.md (technical details)

**Git Commit:**
```
feat(ads): Add metrics cards with period-over-period comparisons

- Create synthetic ad_daily table with 1 year of data
- Add helper functions for date filters, change calculations, formatting
- Add current/previous/sparkline queries from ad_daily
- Update ads.py route to query database instead of placeholder data
- Test all metrics cards functionality

Chat 54 complete: 6/6 pages fully functional.
All backend routes metrics cards now working with real data.
```

### Expected Outcome

After Chat 54:
- ✅ 6/6 pages fully functional (Dashboard, Campaigns, Keywords, Shopping, Ad Groups, Ads)
- ✅ All metrics cards show period-over-period comparisons
- ✅ All sparklines colored and interactive
- ✅ Consistent implementation pattern across all routes

---

## APPENDIX

### A. Helper Function Reference

#### _build_date_filters()

**Purpose:** Build SQL WHERE clause filters for current and previous periods

**Signature:**
```python
def _build_date_filters(active_days, date_from, date_to) -> Tuple[str, str]:
```

**Parameters:**
- `active_days` (int): Number of days for preset ranges (7, 30, 90)
- `date_from` (str, optional): Custom range start date (YYYY-MM-DD)
- `date_to` (str, optional): Custom range end date (YYYY-MM-DD)

**Returns:**
- Tuple of (current_filter, prev_filter) as SQL WHERE clauses starting with "AND"

**Logic:**
```python
if date_from and date_to:
    # Custom range mode
    span = (date_to - date_from).days + 1
    prev_to = date_from - 1 day
    prev_from = date_from - span days
    return (
        f"AND snapshot_date >= '{date_from}' AND snapshot_date <= '{date_to}'",
        f"AND snapshot_date >= '{prev_from}' AND snapshot_date <= '{prev_to}'"
    )
else:
    # Preset range mode
    days = active_days if active_days in [7, 30, 90] else 30
    return (
        f"AND snapshot_date >= CURRENT_DATE - INTERVAL '{days} days'",
        f"AND snapshot_date >= CURRENT_DATE - INTERVAL '{days * 2} days' "
        f"AND snapshot_date < CURRENT_DATE - INTERVAL '{days} days'"
    )
```

**Example:**
```python
# Preset 30-day range
current, prev = _build_date_filters(30, None, None)
# Returns:
# current = "AND snapshot_date >= CURRENT_DATE - INTERVAL '30 days'"
# prev = "AND snapshot_date >= CURRENT_DATE - INTERVAL '60 days' AND snapshot_date < CURRENT_DATE - INTERVAL '30 days'"

# Custom range
current, prev = _build_date_filters(30, '2026-01-01', '2026-01-31')
# Returns:
# current = "AND snapshot_date >= '2026-01-01' AND snapshot_date <= '2026-01-31'"
# prev = "AND snapshot_date >= '2025-12-01' AND snapshot_date <= '2025-12-31'"
```

#### _calculate_change_pct()

**Purpose:** Calculate percentage change between current and previous values

**Signature:**
```python
def _calculate_change_pct(current, previous) -> Optional[float]:
```

**Parameters:**
- `current` (float, optional): Current period value
- `previous` (float, optional): Previous period value

**Returns:**
- float: Percentage change (-100.0 to +infinity)
- None: When previous is None or 0 (show "—" in UI)

**Logic:**
```python
if previous is None or previous == 0:
    return None  # No baseline for comparison
if current is None:
    return -100.0  # Current period has no data
return ((current - previous) / previous) * 100.0
```

**Examples:**
```python
_calculate_change_pct(150, 100)  # Returns: 50.0 (+50%)
_calculate_change_pct(75, 100)   # Returns: -25.0 (-25%)
_calculate_change_pct(100, None) # Returns: None (show "—")
_calculate_change_pct(None, 100) # Returns: -100.0 (complete drop)
_calculate_change_pct(0, 0)      # Returns: None (no baseline)
```

### B. Metrics Card Structure

#### Financial Card Example

```python
{
    'label': 'Cost',
    'value_display': '$970.1k',
    'change_pct': 402.9,
    'sparkline_data': [182.3, 190.5, 185.2, ...],
    'format_type': 'currency',
    'invert_colours': True,
    'card_type': 'financial',
    'sub_label': None
}
```

**Field Descriptions:**
- `label` (str): Card title displayed to user
- `value_display` (str): Formatted current period value
- `change_pct` (float or None): Percentage change vs previous period
- `sparkline_data` (list): Array of daily values for sparkline chart
- `format_type` (str): Display format (currency, percentage, ratio, number)
- `invert_colours` (bool): If True, green=down/red=up (for costs)
- `card_type` (str): Category (financial, actions) affects border color
- `sub_label` (str or None): Optional subtitle text

#### Actions Card Example

```python
{
    'label': 'Impressions',
    'value_display': '18.34M',
    'change_pct': 403.6,
    'sparkline_data': [7.60, 7.80, 7.75, ...],
    'format_type': 'number',
    'invert_colours': False,
    'card_type': 'actions',
    'sub_label': None
}
```

### C. SQL Query Templates

#### Current Period Summary Query

```sql
SELECT
    SUM(cost_micros) / 1000000.0 AS cost,
    SUM(conversions_value) AS revenue,
    SUM(conversions_value) / NULLIF(SUM(cost_micros) / 1000000.0, 0) AS roas,
    SUM(conversions) AS conversions,
    (SUM(cost_micros) / 1000000.0) / NULLIF(SUM(conversions), 0) AS cpa,
    SUM(clicks) * 1.0 / NULLIF(SUM(conversions), 0) AS cvr,
    SUM(impressions) AS impressions,
    SUM(clicks) AS clicks,
    (SUM(cost_micros) / 1000000.0) / NULLIF(SUM(clicks), 0) AS cpc,
    SUM(clicks) * 1.0 / NULLIF(SUM(impressions), 0) AS ctr,
    AVG(search_impression_share) AS search_is,
    AVG(search_top_impression_share) AS search_top_is,
    AVG(search_absolute_top_impression_share) AS search_abs_top_is,
    AVG(click_share) AS click_share,
    SUM(CASE WHEN conversions = 0 AND cost_micros > 0
        THEN cost_micros / 1000000.0 ELSE 0 END) AS wasted_spend
FROM ro.analytics.{table}_daily
WHERE customer_id = ?
  {current_filter}
```

**Returns:** Single row with 15 aggregated metrics

#### Previous Period Summary Query

```sql
-- Identical to Current Period but with prev_filter
SELECT [same 15 metrics]
FROM ro.analytics.{table}_daily
WHERE customer_id = ?
  {prev_filter}
```

**Returns:** Single row with 15 aggregated metrics for comparison period

#### Sparkline Data Query

```sql
SELECT
    snapshot_date,
    SUM(cost_micros) / 1000000.0 AS cost,
    SUM(conversions_value) AS revenue,
    SUM(conversions_value) / NULLIF(SUM(cost_micros) / 1000000.0, 0) AS roas,
    SUM(conversions) AS conversions,
    (SUM(cost_micros) / 1000000.0) / NULLIF(SUM(conversions), 0) AS cpa,
    SUM(clicks) * 1.0 / NULLIF(SUM(conversions), 0) AS cvr,
    SUM(impressions) AS impressions,
    SUM(clicks) AS clicks,
    (SUM(cost_micros) / 1000000.0) / NULLIF(SUM(clicks), 0) AS cpc,
    SUM(clicks) * 1.0 / NULLIF(SUM(impressions), 0) AS ctr,
    AVG(search_impression_share) AS search_is,
    AVG(search_top_impression_share) AS search_top_is,
    AVG(search_absolute_top_impression_share) AS search_abs_top_is,
    AVG(click_share) AS click_share
FROM ro.analytics.{table}_daily
WHERE customer_id = ?
  {current_filter}
GROUP BY snapshot_date
ORDER BY snapshot_date ASC
```

**Returns:** Multiple rows (one per day) with 14 metrics for sparkline visualization

### D. Error Messages Reference

**Common Errors Encountered:**

1. **Connection already closed**
   ```
   [Shopping M2] Current period query error: Connection Error: Connection already closed!
   ```
   **Cause:** Metrics cards function called after `conn.close()`  
   **Fix:** Move metrics cards building before connection close

2. **Table does not exist**
   ```
   Binder Error: Catalog "ro" does not exist!
   ```
   **Cause:** Missing table prefix or table doesn't exist  
   **Fix:** Verify table name includes `ro.analytics.` prefix

3. **Invalid border color**
   ```
   (Visual bug - no error message)
   ```
   **Cause:** Label contains "Conv" triggering Leads category logic  
   **Fix:** Use "Revenue" instead of "Conv Value" for Financial cards

---

**Document Version:** 1.0  
**Last Updated:** March 1, 2026  
**Author:** Chat 53 Worker  
**Status:** Complete and Ready for Git Commit  
**Next Action:** Execute git commit sequence
