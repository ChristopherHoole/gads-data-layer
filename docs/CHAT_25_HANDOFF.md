# CHAT 25 HANDOFF — M4 TABLE OVERHAUL

**Date:** 2026-02-21
**Status:** COMPLETE — Ready for git commit
**For:** Master Chat + next worker chat

---

## GIT COMMIT COMMAND

```
cd C:\Users\User\Desktop\gads-data-layer
git add -A
git commit -m "feat: M4 table overhaul complete — exact Google Ads UI columns across all 5 pages

- Campaigns: 24-col (pre-existing, reference standard)
- Ad Groups: 26-col on ro.analytics.ad_group_daily
- Keywords: 17-col on keyword_features_daily, match type pill in keyword col
- Ads: 24-col on ad_features_daily, ad strength progress bar
- Shopping: 24-col migrated to ro.analytics.shopping_campaign_daily

All pages: sticky columns, server-side sort, status filter, per-page control
Generators A1-A5 run, warehouse_readonly.duckdb synced
Fixed: Keywords column count (was 24, spec says 17)
Fixed: Shopping compute_campaign_metrics KeyError conv_value->conversions_value
Fixed: Jinja nesting error in keywords_new.html from column removal"
```

---

## CURRENT STATE OF EACH PAGE

### Campaigns (`/campaigns`)
- **Route:** `act_dashboard/routes/campaigns.py`
- **Template:** `act_dashboard/templates/campaigns.html`
- **Table:** `ro.analytics.campaign_daily`
- **Cols:** 24 — unchanged in Chat 25, reference standard
- **Data:** 20 campaigns

### Ad Groups (`/ad-groups`)
- **Route:** `act_dashboard/routes/ad_groups.py`
- **Template:** `act_dashboard/templates/ad_groups.html` (or ad_groups_new.html)
- **Table:** `ro.analytics.ad_group_daily`
- **Cols:** 26
- **Data:** 65 ad groups

### Keywords (`/keywords`)
- **Route:** `act_dashboard/routes/keywords.py`
- **Template:** `act_dashboard/templates/keywords_new.html`
- **Table:** `ro.analytics.keyword_features_daily` (windowed `_w7` / `_w30`)
- **Cols:** 17 (exact spec)
- **Data:** 540 keywords (1,000 unique × snapshot)
- **Filters:** All / Exact / Phrase / Broad match type

### Ads (`/ads`)
- **Route:** `act_dashboard/routes/ads.py`
- **Template:** `act_dashboard/templates/ads_new.html`
- **Table:** `ro.analytics.ad_features_daily` (windowed 30d)
- **Cols:** 24
- **Data:** 983 ads
- **Special:** Ad Strength rendered as progress bar

### Shopping (`/shopping`)
- **Route:** `act_dashboard/routes/shopping.py`
- **Template:** `act_dashboard/templates/shopping_new.html`
- **Table (campaigns tab):** `ro.analytics.shopping_campaign_daily`
- **Cols:** 24
- **Data:** 20 shopping campaigns
- **Other tabs:** Products (100 rows), Feed Quality (6 issues), Rules (14) — untouched

---

## DATABASE STATE

| Table | Rows | Cols | Generator |
|---|---|---|---|
| analytics.campaign_daily | 7,300 | 21 | generate_synthetic_data_v2.py |
| analytics.ad_group_daily | 23,725 | 30 | generate_synthetic_ad_group_data.py |
| analytics.keyword_daily | 77,368 | 33 | generate_synthetic_keywords.py |
| analytics.ad_features_daily | 983 | 51 | generate_synthetic_ads.py |
| analytics.shopping_campaign_daily | 7,300 | 26 | generate_synthetic_shopping_v2.py |

`warehouse_readonly.duckdb` = synced copy of `warehouse.duckdb`

---

## KNOWN ISSUES / PRE-EXISTING (NOT M4 BUGS)

| Issue | Location | Status |
|---|---|---|
| favicon.ico 500 | All pages | Pre-existing — missing 404.html template |
| Config validation warnings | Startup | Pre-existing — yaml field name mismatches |
| All Conv. columns show `—` | All pages | Expected — columns not populated by generators |
| Shopping IS/Opt/Click Share show `—` | Shopping | Expected — NULL in SQL, no real data yet |

---

## WHAT THE NEXT CHAT SHOULD KNOW

### Column specs are now locked
Do not change column counts without Master Chat approval. Specs per page:
- Campaigns: 24
- Ad Groups: 26
- Keywords: 17
- Ads: 24
- Shopping campaigns: 24

### Keywords uses keyword_features_daily, not keyword_daily
The route queries `analytics.keyword_features_daily` with windowed columns (`_w7_sum`, `_w30_sum`). Do not switch to `keyword_daily` without understanding the schema difference.

### Shopping has 4 tabs — only Campaigns tab was changed
Products, Feed Quality, and Rules tabs in `shopping_new.html` were not touched. Any Shopping work must preserve these tabs.

### Sort whitelists must be maintained
Each route has an `ALLOWED_*_SORT` set. Any new sortable columns must be added to the whitelist or they will silently fall back to default sort.

### All Conv. block is intentionally NULL
All pages have `NULL AS all_conversions` etc. in SQL. This is by design — the columns will be populated in a future step when the all_conversions pipeline is built.

---

## LESSONS LEARNED THIS CHAT

1. **Search the right directory.** Generators are in `tools/testing/`, not `scripts/`.
2. **Column spec varies per page.** Keywords is 17, not 24. Always check the brief spec per page, not assume Campaigns spec applies everywhere.
3. **Scripted line removal from templates is risky.** The Python removal script missed stray `<td>` cells and orphaned Jinja tags. For future template edits: make targeted str_replace calls, then validate Jinja syntax before deploying.
4. **Always validate Jinja before handing off.** Use: `python3 -c "from jinja2 import Environment, FileSystemLoader; env = Environment(loader=FileSystemLoader('.')); env.get_template('template.html'); print('OK')"`

---

## NEXT STEPS (for Master Chat to assign)

M4 is complete. Potential next modules per PROJECT_ROADMAP.md:
- M5: Metrics cards polish / standardisation
- M6: Inline editing / bulk actions
- All Conv. pipeline (populating all_conversions columns across all tables)
- Shopping IS columns (populating search_impression_share etc. in shopping_campaign_daily)
