# CHAT 25 BRIEF — M4 TABLE OVERHAUL

**Dashboard 3.0 | Module 4 | Table Overhaul**
**Date:** 2026-02-20
**Approved wireframe:** M4_WIREFRAME_v2.html
**Preceding chat:** Chat 24 (M3 Chart Overhaul — commit df7909c)

---

## MANDATORY INITIALISATION

Before doing anything else, request these 3 uploads:

1. **Codebase ZIP:** `C:\Users\User\Desktop\gads-data-layer`
2. **PROJECT_ROADMAP.md:** `C:\Users\User\Desktop\gads-data-layer\docs\PROJECT_ROADMAP.md`
3. **CHAT_WORKING_RULES.md:** `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_WORKING_RULES.md`

Do not proceed until all 3 are uploaded.

---

## OBJECTIVE

Overhaul all data tables across 5 dashboard pages to match the exact Google Ads UI column sets, with server-side sorting and a CSS sticky first column.

---

## WHAT M4 DELIVERS

| Feature | Detail |
|---|---|
| Full column sets | Exact Google Ads column order per page — see Section 3 |
| Server-side sort | URL params (sort_by, sort_dir) → ORDER BY in SQL → page 1 returned |
| Sticky first column | CSS position:sticky on first th/td — no JS library |
| Status filter | All / Enabled / Paused — standardised across all pages |
| Rows per page | 10 / 25 / 50 / 100 — standardised across all pages |
| Visual polish | Consistent hover states, badge styles, colour-coded metrics |

**Out of scope:** Inline editing (M6), bulk action execution (M6), column visibility toggles, export.

---

## CRITICAL TECHNICAL FACTS (verified from live DB)

These are confirmed from live `warehouse.duckdb` inspection — do not assume otherwise:

| Table | Rows | Notes |
|---|---|---|
| analytics.campaign_daily | 7,300 | Most columns already exist |
| analytics.ad_group_daily | 23,725 | IS columns already exist |
| analytics.keyword_daily | 77,368 | QS col names differ from spec — see Section 3 |
| analytics.ad_features_daily | 983 | Ads page — NOT ad_daily (does not exist). Uses windowed 30d columns |
| analytics.shopping_campaign_daily | **0 rows** | Missing 10 columns. Needs full generator build |

**Key corrections:**
- Ads page uses `analytics.ad_features_daily` — not `ad_daily`
- Ads table is windowed — use `impressions_30d`, `clicks_30d`, `cost_micros_30d`, `conversions_30d`, `conversions_value_30d`, `ctr_30d`, `cvr_30d`, `cpa_30d`, `roas_30d`
- `campaign_name` and `ad_group_name` already exist in `ad_features_daily` — no JOINs needed
- Keyword QS columns: `quality_score_creative` = Exp. CTR, `quality_score_relevance` = Ad relevance
- `campaign_daily` already has `all_conversions`, `all_conversions_value`, and all 4 IS columns from Chat 23
- `ad_group_daily` already has all 4 IS columns from Chat 23

---

## RULE 5 — MANDATORY BEFORE ANY BUILDING

Per CHAT_WORKING_RULES.md Rule 5, the worker MUST complete this two-stage process before writing a single line of code:

**STAGE 1 — 5 QUESTIONS**
1. Worker reviews brief + codebase + all docs
2. Worker writes exactly 5 questions (no more, no less) using the format below
3. Worker sends with header "5 QUESTIONS FOR MASTER CHAT" and STOPS
4. User copies questions → pastes into Master Chat
5. Master provides answers
6. User pastes answers back into worker chat

**Question format:**
```
5 QUESTIONS FOR MASTER CHAT

Q1. [CATEGORY] Question here?
Q2. [CATEGORY] Question here?
Q3. [CATEGORY] Question here?
Q4. [CATEGORY] Question here?
Q5. [CATEGORY] Question here?

Waiting for Master Chat answers before proceeding.
```

Question categories: `[DATABASE]` `[ROUTE]` `[DESIGN]` `[SCOPE]` `[RULES]`

Do NOT ask questions already answered in this brief.

**STAGE 2 — BUILD PLAN**
7. Worker writes detailed build plan (after receiving Q&A answers)
8. Worker sends with header "DETAILED BUILD PLAN FOR MASTER CHAT REVIEW" and STOPS
9. User copies build plan → pastes into Master Chat
10. Master reviews and approves (or requests changes)
11. User pastes approval back into worker chat
12. Worker then confirms workflow rules (word for word — see below) and ONLY THEN begins implementation

**Required workflow rules confirmation (worker must say this exactly before starting):**
> "I confirm I have read CHAT_WORKING_RULES.md in full. My workflow will be: (1) request current file version before touching any file, (2) make changes, (3) provide as download link — never code in chat, (4) give exact save path using full Windows path, (5) give PowerShell testing instructions, (6) wait for confirmation before moving to next file, (7) one file at a time — never batch, (8) stop and escalate to Master Chat if same error appears 3 times. I will not begin implementation until the build plan is approved by Master Chat."

**Build plan format:**
```
DETAILED BUILD PLAN FOR MASTER CHAT REVIEW

Files to create/modify:
- [Full Windows path] — [what changes]

Step-by-step implementation:
STEP A: [Task] (~X min)
  - [Specific action]
STEP B: [Task] (~X min)
  - [Specific action]
STEP C: Testing (~X min)
  - [Test 1]

Total estimated time: X minutes
Risks / unknowns: [Any remaining concerns]

Waiting for Master Chat approval before starting.
```

---

## BUILD ORDER

### ⚠ STEP A MUST COMPLETE AND BE VERIFIED BEFORE ANY ROUTE/TEMPLATE WORK

**Step A — Data prep (5 generator updates + 1 new generator)**
**Step B — Campaigns pilot**
**Steps C–F — Rollout one page at a time, test each before proceeding**

---

## STEP A — DATA PREP

### A1: Update `C:\Users\User\Desktop\gads-data-layer\tools\testing\generate_synthetic_data_v2.py`

Add to `analytics.campaign_daily` schema and INSERT:

| New column | Type | Synthetic value |
|---|---|---|
| optimization_score | DOUBLE | uniform(0.50, 0.95) |
| bid_strategy_type | VARCHAR | random choice: TARGET_CPA / TARGET_ROAS / MAXIMIZE_CONVERSIONS / MAXIMIZE_CONVERSION_VALUE / MANUAL_CPC |

---

### A2: Update `C:\Users\User\Desktop\gads-data-layer\tools\testing\generate_synthetic_ad_group_data.py`

Add to `analytics.ad_group_daily` schema and INSERT:

| New column | Type | Synthetic value |
|---|---|---|
| ad_group_type | VARCHAR | random choice: SEARCH_STANDARD / SHOPPING_PRODUCT_ADS / DISPLAY_STANDARD |
| all_conversions | DOUBLE | conversions × uniform(1.05, 1.15) |
| all_conversions_value | DOUBLE | conversions_value × same ratio as all_conversions |
| optimization_score | DOUBLE | uniform(0.50, 0.95) |
| bid_strategy_type | VARCHAR | same choices as campaign |

---

### A3: Update `C:\Users\User\Desktop\gads-data-layer\tools\testing\generate_synthetic_keywords.py`

Add to `analytics.keyword_daily` schema and INSERT:

| New column | Type | Synthetic value |
|---|---|---|
| all_conversions_value | DOUBLE | conversions_value × uniform(1.05, 1.15) |
| bid_strategy_type | VARCHAR | same choices as campaign |
| final_url | VARCHAR | "https://example.com/" + random slug from keyword category |

---

### A4: Update `C:\Users\User\Desktop\gads-data-layer\tools\testing\generate_synthetic_ads.py`

Add to `analytics.ad_features_daily` schema and INSERT:

| New column | Type | Synthetic value |
|---|---|---|
| all_conversions_30d | DOUBLE | conversions_30d × uniform(1.05, 1.15) |
| all_conversions_value_30d | DOUBLE | conversions_value_30d × same ratio |

---

### A5: CREATE NEW `C:\Users\User\Desktop\gads-data-layer\tools\testing\generate_synthetic_shopping_v2.py`

Build from scratch. Model on `generate_synthetic_data_v2.py` (20 campaigns × 365 days).

Add all missing columns to `analytics.shopping_campaign_daily`:

| New column | Type | Synthetic value |
|---|---|---|
| campaign_status | VARCHAR | ENABLED or PAUSED (80/20 split) |
| channel_type | VARCHAR | Always "SHOPPING" |
| all_conversions | DOUBLE | conversions × uniform(1.05, 1.15) |
| all_conversions_value | DOUBLE | conversions_value × same ratio |
| search_impression_share | DOUBLE | uniform(0.30, 0.90) |
| search_top_impression_share | DOUBLE | ≤ search_impression_share |
| search_absolute_top_impression_share | DOUBLE | ≤ search_top_impression_share |
| click_share | DOUBLE | uniform(search_is × 0.4, search_is × 0.9) |
| optimization_score | DOUBLE | uniform(0.50, 0.95) |
| bid_strategy_type | VARCHAR | TARGET_ROAS or MAXIMIZE_CONVERSION_VALUE (shopping appropriate) |

Shopping campaigns should use ROAS-based performance (conv_value / cost = 3.0–6.0 range).

---

### A — VERIFICATION (mandatory before Step B)

After all 5 generators are updated and run, verify each table with:

```python
import duckdb
conn = duckdb.connect('warehouse.duckdb')
for table in ['campaign_daily','ad_group_daily','keyword_daily','ad_features_daily','shopping_campaign_daily']:
    cols = [c[0] for c in conn.execute(f'DESCRIBE analytics.{table}').fetchall()]
    rows = conn.execute(f"SELECT COUNT(*) FROM analytics.{table} WHERE customer_id='9999999999'").fetchone()[0]
    print(f'{table}: {rows} rows | cols: {len(cols)}')
conn.close()
```

Expected: all 5 tables have correct row counts and new columns present.

Then run:
```powershell
Copy-Item -Force warehouse.duckdb warehouse_readonly.duckdb
```

**Only proceed to Step B after verification passes.**

---

## STEP B — CAMPAIGNS PILOT

### B1: Update `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\campaigns.py`

Add URL parameter handling:
- `sort_by` (default: `cost`)
- `sort_dir` (default: `desc`)
- `per_page` (default: `25`, options: 10/25/50/100)
- `status` filter (default: `all`)

SQL query must:
- Use `ORDER BY {sort_by} {sort_dir}` — whitelist allowed sort columns to prevent injection
- Calculate derived columns in SQL: conv_value_per_cost, cost_per_conv, conv_rate, cost_per_all_conv, all_conv_rate, all_conv_value_per_cost, avg_cpc, ctr
- Handle NULL division safely (CASE WHEN divisor > 0 THEN ... ELSE NULL END)
- Pass sort state back to template: `sort_by`, `sort_dir`

Allowed sort columns whitelist (campaigns):
```python
ALLOWED_SORT_COLS = {
    'campaign_name', 'cost', 'conversions_value', 'conversions',
    'conv_value_per_cost', 'cost_per_conv', 'conv_rate',
    'all_conversions', 'cost_per_all_conv', 'all_conv_rate',
    'all_conversions_value', 'all_conv_value_per_cost',
    'impressions', 'clicks', 'cpc', 'ctr',
    'search_impression_share', 'search_top_impression_share',
    'search_absolute_top_impression_share', 'click_share',
    'optimization_score'
}
```

### B2: Update `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\campaigns.html`

Full 24-column table:

| # | Column | DB source | Sort |
|---|---|---|---|
| 1 | 📌 Campaign (sticky) | campaign_name | ✅ |
| 2 | Status | campaign_status | — |
| 3 | Type | channel_type | — |
| 4 | Cost | cost | ✅ |
| 5 | Conv. value | conversions_value | ✅ |
| 6 | Conv. | conversions | ✅ |
| 7 | Conv. value / cost | CALC | ✅ |
| 8 | Cost / conv. | CALC | ✅ |
| 9 | Conv. rate | CALC | ✅ |
| 10 | All conv. | all_conversions | ✅ |
| 11 | Cost / all conv. | CALC | ✅ |
| 12 | All conv. rate | CALC | ✅ |
| 13 | All conv. value | all_conversions_value | ✅ |
| 14 | All conv. value / cost | CALC | ✅ |
| 15 | Impr. | impressions | ✅ |
| 16 | Clicks | clicks | ✅ |
| 17 | Avg. CPC | cpc | ✅ |
| 18 | CTR | ctr | ✅ |
| 19 | Search IS | search_impression_share | ✅ |
| 20 | Search top IS | search_top_impression_share | ✅ |
| 21 | Search abs. top IS | search_absolute_top_impression_share | ✅ |
| 22 | Click share | click_share | ✅ |
| 23 | Opt. score | optimization_score | ✅ |
| 24 | Bid strategy | bid_strategy_type | — |

Sort header click behaviour (JavaScript):
- Click unsorted → redirect with sort_by=[col]&sort_dir=desc&page=1
- Click sorted desc → redirect with sort_dir=asc&page=1
- Click sorted asc → redirect with sort_dir=desc&page=1
- Active sort column shows ↑ or ↓ indicator

Status badge colours:
- ENABLED → `badge bg-success` "Active"
- PAUSED → `badge bg-secondary` "Paused"
- REMOVED → `badge bg-danger` "Removed"

Type: plain muted text (no badge/pill) — `text-muted small`

Metric colour coding:
- Conv. value / cost (ROAS): ≥3.0 green, 2.0–2.9 orange, <2.0 red
- Cost / conv. (CPA): account-relative — green bottom third, orange middle, red top third
- Opt. score: ≥0.8 green, 0.6–0.79 orange, <0.6 red

### B3: Update `C:\Users\User\Desktop\gads-data-layer\act_dashboard\static\css\custom.css`

Add shared sticky column + sort indicator CSS (used by all pages):

```css
/* M4 — Sticky first column */
.act-table-wrapper {
    overflow-x: auto;
    position: relative;
}
.act-table th:first-child,
.act-table td:first-child {
    position: sticky;
    left: 0;
    z-index: 2;
    background: white;
    border-right: 2px solid #dee2e6;
}
.act-table thead th:first-child {
    z-index: 3;
    background: #f8f9fa;
}
.act-table tbody tr:hover td:first-child {
    background: #f0f4ff;
}

/* M4 — Sort indicators */
.act-table thead th.sortable {
    cursor: pointer;
    user-select: none;
    white-space: nowrap;
}
.act-table thead th.sortable:hover {
    background: #e9ecef;
}
.act-table thead th.sort-asc::after { content: ' ↑'; color: #0d6efd; }
.act-table thead th.sort-desc::after { content: ' ↓'; color: #0d6efd; }
.act-table thead th.sortable:not(.sort-asc):not(.sort-desc)::after {
    content: ' ↕';
    color: #ced4da;
    font-size: 10px;
}
```

**B — Test before proceeding to C:**
- Navigate to `http://localhost:5000/campaigns`
- All 24 columns visible ✅
- Scroll right — Campaign column stays frozen ✅
- Click Cost header — table re-sorts, ↓ indicator appears ✅
- Click Cost again — flips to ↑ ✅
- Enabled/Paused/All filter works ✅
- 10/25/50/100 rows per page works ✅
- No console errors ✅

---

## STEP C — AD GROUPS

### Update `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\ad_groups.py`

Same sort param pattern as campaigns. Use table `ro.analytics.ad_group_daily`.

26-column set — key notes:
- Status column is `ad_group_status` in DB (not `status`)
- Target CPA: `target_cpa_micros / 1000000.0` — handle NULL (many ad groups won't have it)
- All conv., all conv. value: new columns added in Step A

### Update `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\ad_groups.html`

Same sticky/sort pattern as campaigns. 26 columns per spec.

---

## STEP D — KEYWORDS

### Update `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\keywords.py`

Same sort param pattern. Use table `ro.analytics.keyword_daily`.

17-column set — key notes:
- **QS column name mapping (CRITICAL):**
  - Exp. CTR → `quality_score_creative`
  - Ad relevance → `quality_score_relevance`
  - Landing page exp. → `quality_score_landing_page`
- Match type pill stays inside Keyword column (not separate column)
- Match type pill colours: Exact=`bg-success`, Phrase=`bg-primary`, Broad=`bg-warning text-dark`
- QS colour coding: 8–10 green, 5–7 orange, 1–4 red, NULL grey

### Update `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\keywords_new.html`

Same sticky/sort pattern. 17 columns per spec.

---

## STEP E — ADS

### Update `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\ads.py`

Same sort param pattern. Use table `ro.analytics.ad_features_daily`.

Key notes:
- Table has ONE row per ad (not daily rows) — no date filtering needed
- Use 30d windowed columns: `impressions_30d`, `clicks_30d`, `cost_micros_30d / 1e6`, `conversions_30d`, `conversions_value_30d`, `ctr_30d`, `cvr_30d`, `cpa_30d / 1e6`, `roas_30d`
- `campaign_name` and `ad_group_name` already in table — no JOINs needed
- Ad strength colour coding: EXCELLENT=green, GOOD=blue, AVERAGE=orange, POOR=red
- Default sort: `impressions_30d DESC`

22-column set per spec.

### Update `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\ads_new.html`

Same sticky/sort pattern. 22 columns per spec. Sticky first col = Ad (final URL).

---

## STEP F — SHOPPING

### Update `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\shopping.py`

Same sort param pattern. Use table `ro.analytics.shopping_campaign_daily`.

Campaigns tab only — same 24-column set as Campaigns page.
Products tab: no changes in M4.

### Update `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\shopping_new.html`

Campaigns tab: same sticky/sort pattern, 24 columns. Products tab untouched.

---

## FILES — COMPLETE LIST

| File | Action | Step |
|---|---|---|
| `tools/testing/generate_synthetic_data_v2.py` | MODIFY | A1 |
| `tools/testing/generate_synthetic_ad_group_data.py` | MODIFY | A2 |
| `tools/testing/generate_synthetic_keywords.py` | MODIFY | A3 |
| `tools/testing/generate_synthetic_ads.py` | MODIFY | A4 |
| `tools/testing/generate_synthetic_shopping_v2.py` | **NEW** | A5 |
| `act_dashboard/routes/campaigns.py` | MODIFY | B1 |
| `act_dashboard/templates/campaigns.html` | MODIFY | B2 |
| `act_dashboard/static/css/custom.css` | MODIFY | B3 |
| `act_dashboard/routes/ad_groups.py` | MODIFY | C |
| `act_dashboard/templates/ad_groups.html` | MODIFY | C |
| `act_dashboard/routes/keywords.py` | MODIFY | D |
| `act_dashboard/templates/keywords_new.html` | MODIFY | D |
| `act_dashboard/routes/ads.py` | MODIFY | E |
| `act_dashboard/templates/ads_new.html` | MODIFY | E |
| `act_dashboard/routes/shopping.py` | MODIFY | F |
| `act_dashboard/templates/shopping_new.html` | MODIFY | F |

**Total: 16 files (15 modified + 1 new)**

---

## SUCCESS CRITERIA

| # | Criteria | How to verify |
|---|---|---|
| 1 | All 5 tables have new columns in live DB | check_db.py output |
| 2 | shopping_campaign_daily has >0 rows | check_db.py output |
| 3 | Campaigns page loads 200 OK | PowerShell server log |
| 4 | All 24 columns visible on Campaigns | Browser scroll right |
| 5 | Campaign Name stays sticky on scroll | Browser scroll right |
| 6 | Sort by Cost works (full dataset) | Click Cost header — check order |
| 7 | Sort indicator flips ↑↓ | Click same header twice |
| 8 | All/Enabled/Paused filter works | Click each filter button |
| 9 | 10/25/50/100 rows per page works | Change dropdown |
| 10 | Ad Groups page — all 26 columns, sticky, sort | Same checks |
| 11 | Keywords page — QS cols mapped correctly | Check Exp. CTR + Ad relevance display |
| 12 | Ads page — uses ad_features_daily 30d cols | Check data is non-zero |
| 13 | Shopping page — data showing (not empty) | Campaigns tab has rows |
| 14 | No browser console errors on any page | F12 → Console |
| 15 | Dashboard page unchanged | Navigate to / and confirm |

---

## COMMON PITFALLS TO AVOID

1. **Do not use `ad_daily`** — it does not exist. Ads page uses `ad_features_daily`.
2. **Keyword QS column names** — `quality_score_creative` and `quality_score_relevance` — not the spec names.
3. **SQL injection prevention** — always whitelist `sort_by` values before using in SQL.
4. **NULL division** — wrap all CALC columns in `CASE WHEN denominator > 0 THEN ... ELSE NULL END`.
5. **Shopping Step F depends on A5** — do not start F until A5 generator has run and rows verified.
6. **DB prefix** — use `ro.analytics.*` for readonly database queries in routes.
7. **Template base** — always extend `base_bootstrap.html` not `base.html`.

---

## GIT COMMIT (at end of chat)

```
feat(dashboard): M4 table overhaul - full column sets, server-side sort, sticky first col

WORKING:
- Full Google Ads column sets on all 5 pages
- Server-side sort (sort_by/sort_dir URL params) on all sortable columns
- CSS sticky first column on all pages
- All/Enabled/Paused filter standardised
- 10/25/50/100 rows per page standardised
- Metric colour coding (ROAS, CPA, opt. score, ad strength, QS)
- Shopping synthetic data generator built from scratch (365d × 20 campaigns)

NEW COLUMNS ADDED:
- campaign_daily: optimization_score, bid_strategy_type
- ad_group_daily: ad_group_type, all_conversions, all_conversions_value, optimization_score, bid_strategy_type
- keyword_daily: all_conversions_value, bid_strategy_type, final_url
- ad_features_daily: all_conversions_30d, all_conversions_value_30d
- shopping_campaign_daily: 10 new columns + full synthetic data

FILES CREATED:
- tools/testing/generate_synthetic_shopping_v2.py

FILES MODIFIED:
[list all 15 modified files]

TEST RESULTS:
- All 15 success criteria passing
- All 5 pages 200 OK
- Sort verified on all pages
- Sticky col verified on all pages

NEXT: Chat 26 — M5 Rules Upgrade
```

---

## HANDOFF DOCS REQUIRED

Worker must produce before closing:
1. `docs/CHAT_25_BRIEF.md` — this file
2. `docs/CHAT_25_DETAILED_SUMMARY.md` — what was built, issues encountered, decisions made
3. `docs/CHAT_25_HANDOFF.md` — what M5 needs to know

---

*Brief approved by Master Chat — 2026-02-20*
