# Build 2 Brief — PMax CSV Ingestion Pipeline (P1)

**Priority:** Today — Chris wants it working against yesterday's real PMax data (22 Apr) this afternoon.
**Effort estimate:** 2–4 hours.

---

## 1. Context

Google Ads API (`campaign_search_term_insight` resource, used in `ingest_pmax_search_terms()` at `act_dashboard/data_pipeline/google_ads_ingestion.py:605`) returns PMax search terms with **NULL cost, avg_cpc, cost_per_conversion**. This is why every PMax row in `act_v2_search_terms` has `cost = NULL` and our classification engine can't use cost-based signals for PMax.

Meanwhile, the GAds UI's scheduled "Search terms report" export delivers a CSV with **real cost, conversions, conversion value per term** — validated against the UI totals in `C:\Users\User\Desktop\gads-data-layer\potential_clients\Inserta Dental\Search Terms\` (reference CSV: `C:\Users\User\Downloads\Search terms report (8).csv`; totals match UI for 22 Apr: Total Campaign £1,194.41, Total Search terms £398.30, Total Other £273.23).

GAds emails Chris a one-time signed link each morning. Chris clicks it, CSV lands in `C:\Users\User\Downloads`. **Automation of the link-click is not in scope.** This ticket ships a manual CLI ingestion only — Chris points the command at a CSV file and it loads.

---

## 2. Acceptance criteria

1. Chris can run `python -m act_dashboard.data_pipeline.pmax_csv_ingest --client-id dbd001 --file "<path>"`. The file is parsed and loaded into a new DB table `raw_pmax_search_term_csv`.
2. The ingestion also upserts PMax rows in `act_v2_search_terms` for the same `(client_id, snapshot_date)`, populating cost/conversions/value from the CSV (these were previously NULL or 0). **Must NOT touch Search rows in the same table.**
3. The ingestion also updates `act_v2_pmax_other_bucket` for that `(client_id, snapshot_date)` from the CSV `Total: Other search terms` row — currently this table has NULL cost; after ingestion it should have the CSV's cost value.
4. The negatives engine (pass1 + pass2) continues to read from `act_v2_search_terms` unchanged — no engine-code changes needed because the upsert makes CSV data visible there.
5. The Search Term Review UI for `dbd001` + date `2026-04-22` shows PMax rows with real £-cost visible in the cost column (previously blank/zero).
6. Running ingestion twice on the same file is idempotent (no duplicate rows, no double-counting).
7. Search campaign ingestion (API-based) is unchanged. Regression: running overnight scheduler next morning must not break.

---

## 3. Files to change

### NEW — DB migration (Python pattern, matches existing migrations)
**File:** `act_dashboard/db/migrations/migrate_n4_pmax_csv.py`

Follows the same pattern as `migrate_n3_sticky_rejections.py`. Creates:

```sql
CREATE TABLE IF NOT EXISTS raw_pmax_search_term_csv (
    client_id VARCHAR NOT NULL,
    snapshot_date DATE NOT NULL,
    campaign_id VARCHAR(30),
    campaign_name VARCHAR(500),
    campaign_type VARCHAR,
    search_term VARCHAR NOT NULL,
    match_type VARCHAR,
    added_excluded VARCHAR,
    cost DECIMAL(18,2),
    impressions INTEGER,
    clicks INTEGER,
    avg_cpc DECIMAL(10,4),
    ctr DECIMAL(10,6),
    device_click_summary VARCHAR,
    conversions DECIMAL(10,2),
    cost_per_conversion DECIMAL(10,2),
    conversion_rate DECIMAL(10,6),
    conversion_value DECIMAL(18,2),
    conversion_value_per_cost DECIMAL(10,4),
    currency VARCHAR(3),
    source_file VARCHAR,
    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (client_id, snapshot_date, search_term)
);

CREATE INDEX IF NOT EXISTS idx_raw_pmax_csv_lookup
    ON raw_pmax_search_term_csv(client_id, snapshot_date);
```

PK is `(client_id, snapshot_date, search_term)` — all VARCHAR/DATE, no DECIMAL PK issues. Use `DELETE WHERE client_id=? AND snapshot_date=?` then bulk `INSERT` — same idempotency pattern as existing ingestion code.

### NEW — Ingestion script
**File:** `act_dashboard/data_pipeline/pmax_csv_ingest.py`

CLI signature:
```
python -m act_dashboard.data_pipeline.pmax_csv_ingest --client-id dbd001 --file "C:/Users/User/Downloads/Search terms report (8).csv"
```

Logic:
1. **Detect encoding.** Read first 4 bytes. If BOM `\xff\xfe` or `\xfe\xff` → `utf-16`. Else `utf-8-sig`.
2. **Detect delimiter.** After reading, count tabs vs commas in line 3 (header row). Use whichever is higher.
3. **Parse title row 2** (e.g. `22 April 2026 - 22 April 2026`) to extract `snapshot_date`. Accept single-day reports only — if start != end date, raise an error with a clear message.
4. **Read CSV from line 3 onwards** using detected delimiter. Column headers to expect (from Search terms report (8).csv):
   `Search term, Match type, Added/Excluded, Campaign, Ad group, Keyword, Campaign type, Currency code, Cost, Impr., Clicks, Avg. CPC, CTR, Device click summary, Conversions, Cost / conv., Conv. rate, Conv. value, Conv. value / cost`
5. **For each row**, decide disposition:
   - If `Search term` starts with `Total:` → candidate for totals table (see step 8), skip for main insert.
   - If `Campaign type` != `Performance Max` → skip (defensive).
   - Otherwise → insert into `raw_pmax_search_term_csv`.
6. **Numeric parsing helper:** strip commas from numbers; treat `" --"`, `--`, empty string as NULL; parse `£` symbols if present; coerce to Decimal/int. Avg CPC / CTR / rate may be tiny numbers — use Decimal, not float, to avoid precision issues.
7. **Campaign ID lookup.** CSV has only campaign NAME. Look up the campaign_id by joining CSV's Campaign against `act_v2_campaign_roles.campaign_name` WHERE `client_id = ?`. Log a warning if a row has a campaign name not in `act_v2_campaign_roles`. If multiple rows share the same unknown campaign, log once.
8. **Totals handling.** From the `Total: Other search terms` row (if present), extract cost/impressions/clicks/conversions. Upsert into `act_v2_pmax_other_bucket` for `(client_id, snapshot_date, campaign_id)` where campaign_id came from the CSV's own Campaign name lookup. The table currently has NULL cost — this fills it in. Use `DELETE WHERE client_id=? AND snapshot_date=? AND campaign_id=?` then INSERT.
9. **Insert into raw_pmax_search_term_csv.** Delete-then-insert by `(client_id, snapshot_date)`. Store `source_file` = basename of path.
10. **Upsert into act_v2_search_terms.** Delete existing PMax rows with `DELETE FROM act_v2_search_terms WHERE client_id=? AND snapshot_date=? AND campaign_type='PERFORMANCE_MAX'`. Then insert fresh from CSV rows using the same column structure as the existing PMax insert at line 605:
    - `campaign_type = 'PERFORMANCE_MAX'`
    - `ad_group_id = 'PMAX_ASSET_GROUP'`, `ad_group_name = 'PMAX_ASSET_GROUP'` (match existing pattern — Google doesn't expose asset group in CSV either; all values are ` --`)
    - `match_type = 'PMAX'` (match existing pattern — CSV match_type column mostly blank for PMax)
    - `status` = CSV's `Added/Excluded` value, NULL if blank/`--`
    - `keyword_text`, `keyword_id` = NULL
    - `cost`, `impressions`, `clicks`, `conversions`, `conversion_value` = from CSV
    - `ctr`, `avg_cpc`, `cost_per_conversion`, `conversion_rate` = from CSV
11. **Log a summary** at INFO level: `Ingested N PMax terms for client=dbd001, date=2026-04-22, total cost £X, from file=F. Other bucket: Y impr / £Z cost updated.`

### NO CHANGES to pass1, pass2, UI, API
The engine already reads from `act_v2_search_terms`. Upserting CSV data into that table means pass1, pass2, and UI all see the new cost values without code change.

---

## 4. Commit sequence

1. `N4a: migration — raw_pmax_search_term_csv table + index`
2. `N4b: pmax CSV ingestion CLI — detect encoding/delimiter, parse, upsert to raw + act_v2_search_terms + other_bucket`
3. `N4-hotfix-N: any bug fixes from Chris's testing`

Branch: `main`. Push after Chris confirms end-to-end test passes.

---

## 5. Test sequence (Chris will run)

1. `git pull` to get Build 2's work.
2. Apply migration: `python -m act_dashboard.db.migrations.migrate_n4_pmax_csv`.
3. Run ingestion on the reference CSV:
   ```
   python -m act_dashboard.data_pipeline.pmax_csv_ingest --client-id dbd001 --file "C:/Users/User/Downloads/Search terms report (8).csv"
   ```
   Expect log line:
   `Ingested ~641 PMax terms for client=dbd001, date=2026-04-22, total cost £921.19 (from per-term rows); Other bucket: 779 impr / £273.23 cost updated`
   (exact counts may vary by 1-2; £921 is total minus the Other bucket)
4. Verify via SQL:
   ```sql
   SELECT COUNT(*), SUM(cost) FROM act_v2_search_terms
   WHERE client_id='dbd001' AND snapshot_date='2026-04-22' AND campaign_type='PERFORMANCE_MAX';
   -- expect count ~641, sum ~£921
   
   SELECT * FROM act_v2_pmax_other_bucket
   WHERE client_id='dbd001' AND snapshot_date='2026-04-22';
   -- expect cost = 273.23, impressions = 779, clicks = 98
   ```
5. Re-run the same ingestion command — expect same counts, no duplicates (idempotency check).
6. Start Flask. Navigate to `/v2/search-terms`, date-pick `22/4/2026`, filter to PMax. Verify:
   - Row count ≈ 641 PMax terms
   - Cost column shows real £-values (not blank)
   - Conversions column populated where non-zero
7. Click "Reclassify today's terms" to re-run pass1/pass2 against the newly-populated cost data. Verify review queue refreshes and top-cost leaks rise to the top of the sort.
8. Push-approved-to-Google-Ads flow for 1-2 test terms to confirm no regression in the negatives push pipeline.

---

## 6. Out of scope (file as follow-ups)

- **Auto-watch `C:\Users\User\Downloads`** for new `Search terms report*.csv` files — separate ticket
- **Scheduler phase integration** — add `pmax_csv_ingest` phase to `act_dashboard/scheduler/overnight_run.py` after the watcher ships
- **Multi-client support** — currently CLI takes one `--client-id`. When OE starts using this, we'll add multi-client lookup via filename or CSV contents
- **Archive processed CSVs** to `potential_clients/<client>/PMax reports/`
- **Auto-suppress recently-pushed terms from review queue** — deferred because real cost data lets us sort by £-value instead, reducing the noise pressure
- **Error alerting** if today's CSV is missing by N:NN UK time — Chris explicitly said silent-skip is fine for now
- **Cost-weighted Pass 3 thresholds** — Pass 3 currently uses impression thresholds; with real cost we can consider £-thresholds too
- **Today's scheduler-truncation bug** (pipeline stopped after `engine` phase on 23 Apr — only ingestion + engine ran, skipped neg_pass phases) — separate ticket

---

## 7. Notes for Build 2

- **Reference file for testing:** `C:\Users\User\Downloads\Search terms report (8).csv`. UTF-16 encoded, tab-delimited. Confirmed totals match the UI: Total Campaign £1,194.41, Total Search terms £398.30, Total Other search terms £273.23.
- **Delimiter and encoding vary.** A manually-downloaded CSV is UTF-8 + comma. A scheduled-email-link CSV is UTF-16 + tab. Parser must handle both.
- **Currency.** Don't hardcode GBP — read the `Currency code` column and store. DBD is GBP; future clients may differ.
- **`act_v2_search_terms` has auto-increment PK `search_term_id`.** No need to pass it; use the same pattern as `google_ads_ingestion.py:478-488` (explicit column list, no search_term_id in INSERT).
- **Campaign ID must be resolved from campaign name** via `act_v2_campaign_roles.campaign_name`. For DBD PMax it's `22272295086`. If you need to handle a case where the campaign name isn't in `act_v2_campaign_roles`, log a warning and use NULL campaign_id rather than failing the whole ingestion.
- **DuckDB 1.1.0 UPDATE-on-UNIQUE bug note:** not applicable here — no UPDATE statements, only DELETE + INSERT. Clean.
- **Do not push to origin/main until Chris confirms the full test sequence passes.**
