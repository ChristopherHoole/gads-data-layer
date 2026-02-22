# Chat 27 (M6) — Detailed Summary
## Recommendations Engine + UI

**Date:** 2026-02-22
**Status:** ✅ COMPLETE AND APPROVED
**Last Commit Before Chat 27:** `025986a` (M5)

---

## 1. Files Created / Modified

### NEW FILES

| File | Full Windows Path | Approx Lines |
|------|-------------------|-------------|
| setup_recommendations_db.py | `C:\Users\User\Desktop\gads-data-layer\tools\testing\setup_recommendations_db.py` | ~140 |
| recommendations_engine.py | `C:\Users\User\Desktop\gads-data-layer\act_autopilot\recommendations_engine.py` | ~280 |
| recommendations.py (blueprint) | `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\recommendations.py` | ~210 |
| recommendations.html | `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\recommendations.html` | ~520 |

### MODIFIED FILES

| File | Full Windows Path | Changes |
|------|-------------------|---------|
| campaigns.html | `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\campaigns.html` | Added Recommendations tab: section header, 2-col card grids, full JS rendering (FILE B final) |

---

## 2. Architecture Decisions

### Dual-Layer Architecture (Maintained)
- **Readonly analytics DB:** `ro.analytics.*` prefix — all reads use `campaign_features_daily` view
- **Writable warehouse DB:** `warehouse.duckdb` — `recommendations` table lives here
- Engine reads from readonly, writes to writable. Templates never touch writable DB directly.

### Recommendations Table (warehouse.duckdb)
Created by `setup_recommendations_db.py`. Schema:
```
id, rule_id, campaign_id, campaign_name, rule_type, status,
action_direction, action_label, value_label, value_suffix,
trigger_summary, confidence, generated_at, acted_at,
monitoring_start_date, monitoring_total_days, monitoring_elapsed_days,
monitoring_remaining, monitoring_progress_pct, reverted
```

### Duplicate Prevention
Engine checks for existing `pending` or `monitoring` rows for same `(campaign_id, rule_id)` before inserting. Second run produces `SkippedDuplicate=48` — confirmed working.

### Proxy Column Mappings
Because `campaign_features_daily` lacks some direct columns, the engine uses:

| Needed Signal | Proxy Column Used |
|---|---|
| Cost spike/anomaly | `anomaly_cost_z` (z-score) |
| Pacing over cap | `pacing_flag_over_105` |
| CTR drop | `ctr_w7_vs_prev_pct` |
| CVR drop | `cvr_w7_vs_prev_pct` |
| Target ROAS (missing) | Fallback: `4.0` hardcoded |
| Budget micros (missing) | Fallback: `cost_micros_w7_mean` |

### /recommendations/cards Endpoint
New JSON endpoint added to `recommendations.py` blueprint. Returns `{pending: [...], monitoring: [...]}` with all enriched fields serialised (datetime → ISO string via `_serialise()` helper). Used by campaigns.html JS to render inline cards without page reload.

---

## 3. Engine Logic Summary

**File:** `C:\Users\User\Desktop\gads-data-layer\act_autopilot\recommendations_engine.py`
**Trigger:** POST `/recommendations/run` or direct Python call

**Flow:**
1. Load `rules_config.json` — filters to rules with `enabled: true`
2. Query `ro.analytics.campaign_features_daily` for latest snapshot per campaign
3. For each rule x campaign:
   - Check data sufficiency (min impressions, min days)
   - Evaluate trigger conditions against feature row
   - Check duplicate (skip if pending/monitoring already exists)
   - Insert new `pending` recommendation row to `warehouse.duckdb`
4. Return counts: `generated`, `skipped_duplicate`, `skipped_data`, `errors`

**Rule Types Supported:** `budget`, `bid`, `status`
**Confidence Levels:** `high`, `medium`, `low` (derived from data sufficiency score)

---

## 4. Test Results

### FILE 1 — setup_recommendations_db.py
| Test | Result |
|---|---|
| Creates recommendations table | ✅ |
| Seeds 22 rows (8 successful, 4 reverted, 6 declined, 4 monitoring) | ✅ |
| No errors on re-run | ✅ |

### FILE 2 — recommendations_engine.py
| Test | Result |
|---|---|
| Run 1: Generated=48 recommendations | ✅ |
| Run 2: SkippedDuplicate=48 (no dupes inserted) | ✅ |
| No errors in Flask log | ✅ |

### FILE 3 — recommendations.py blueprint
| Test | Result |
|---|---|
| GET /recommendations HTTP 200 | ✅ |
| POST /recommendations/run HTTP 200 | ✅ |
| GET /recommendations/data HTTP 200 | ✅ |
| GET /recommendations/cards HTTP 200 | ✅ |
| GET /changes HTTP 200 (preserved) | ✅ |

### FILE 4 — recommendations.html (global page)
| Test | Result |
|---|---|
| Pending tab loads 48 cards (2-col grid) | ✅ |
| Monitoring tab loads 4 cards with progress bars | ✅ |
| History tab loads 22 rows + 67% success banner | ✅ |

### FILE B — campaigns.html (Recommendations tab)
| Test | Result |
|---|---|
| Section header renders (title + Run button) | ✅ |
| Pending section: blue left border, count badge | ✅ |
| 48 pending cards in 2-col grid | ✅ |
| Coloured top bars by type (blue/green/red) | ✅ |
| Gradient change blocks by type | ✅ |
| Trigger blocks with "Why this triggered" label | ✅ |
| Footer: confidence badge + Campaigns pill + age + amber note | ✅ |
| 3 disabled action buttons (Modify/Decline/Accept) | ✅ |
| Monitoring section: purple left border, count badge | ✅ |
| 4 monitoring cards in 2-col grid | ✅ |
| Monitoring block: progress bar + 2-col outcome grid | ✅ |
| Summary strip: 4 cards populate on tab click | ✅ |
| Run button triggers engine + reloads cards | ✅ |
| Other Campaigns tabs unaffected | ✅ |

### Regression Tests (mid-chat fix)
| Test | Result |
|---|---|
| Keywords page HTTP 200 | ✅ |
| Ad Groups page HTTP 200 | ✅ |
| Ads page HTTP 200 | ✅ |
| Shopping page HTTP 200 | ✅ |

---

## 5. Known Issues (Pre-existing — NOT Chat 27 scope)

| Issue | Detail |
|---|---|
| favicon 500 error | Flask throws 500 when browser requests `/favicon.ico` — no favicon file exists. Pre-existing, all pages affected. |
| 404.html TemplateNotFound | `app.py` line 149 references `render_template('404.html')` but file doesn't exist. Triggered by favicon 404. Pre-existing. |
| Config validation warnings | `client_001.yaml`, `client_001_mcc.yaml`, `client_002.yaml`, `client_synthetic.yaml` have schema mismatches. App starts fine, synthetic client works. Pre-existing. |

---

## 6. What Chat 28 Must Build

### Action Buttons — Accept / Decline / Modify

The 3 action buttons on every pending card are currently **disabled** with amber note "Buttons active in Chat 28".

**Accept:**
- POST `/recommendations/<id>/accept`
- Updates `status` → `accepted`, sets `acted_at`
- If rule supports monitoring: transitions to `monitoring`, sets `monitoring_start_date` + `monitoring_total_days`
- Otherwise: marks `successful` directly
- Writes to `changes` table for audit trail

**Decline:**
- POST `/recommendations/<id>/decline`
- Updates `status` → `declined`, sets `acted_at`
- Removes card from pending grid

**Modify:**
- Modal UI: user edits proposed value (e.g. budget amount)
- POST `/recommendations/<id>/modify` with `{new_value: ...}`
- Updates recommendation with modified value, then proceeds as Accept

**UI Behaviour After Action:**
- Remove card from pending grid (animate out or re-render)
- Update badge counts in summary strip and section labels
- Show toast confirmation

**Files Chat 28 will need:**
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\recommendations.py` — add 3 POST routes
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\recommendations.html` — wire up buttons + Modify modal
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\templates\campaigns.html` — wire up buttons + Modify modal
