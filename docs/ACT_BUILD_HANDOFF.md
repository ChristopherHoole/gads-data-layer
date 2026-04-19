# ACT Build — Session Handoff

## 1. Where we are

- **Branch:** `main`
- **Last commit:** `873207e` (Two micro-fixes: left-align impact line; gain-frame Budget Position pending for primary)

### Active clients

| Client ID | Name | Status |
|-----------|------|--------|
| `oe001` | Objection Experts | 305 days data · Account level `monitor_only` · 1 ENABLED campaign (GLO) — edge case, no recs |
| `dbd001` | Dental by Design | 180 days data · Account level `monitor_only` · 3 ENABLED campaigns (Brand / PMax / DII) · engine produces 1 rec |

### Active pending recommendation

- **rec id = 3** · client `dbd001` · Account level · status `pending`
- Budget shift: **£65/day from Dental Implants Intent → Brand**
- Based on score differential: Brand +70.5 vs DII −210.4
- Referenced by both slide-ins: Brand sees "+£65/day incoming from DII"; DII sees "−£65/day outgoing to Brand"

### F1 Overnight Scheduler

- Running via **Windows Task Scheduler** on user's localhost
- Trigger: **at logon** (not time-based — user chose this over 6:30 AM cron)
- Script: `python -m act_dashboard.scheduler.overnight_run`
- Status table: `act_v2_scheduler_runs` (per-client, per-phase running/success/failed)
- Idempotent via `CAST(started_at AS DATE) = CURRENT_DATE` check — won't re-run the same day unless `--force`

---

## 2. What was delivered this session (commit-by-commit)

| Hash | Title |
|------|-------|
| `a77043d` | Fix PK crash on approve/decline + wire View Details on Account Level |
| `8de9ffd` | Unify Decision Details slide-in across Morning Review + Account Level |
| `b1e8092` | Move Awaiting Approval buttons to top-right on `/v2/account` |
| `c6926cc` | Campaign Detail slide-in: clickable campaign rows on `/v2/account` |
| `2e292ec` | Campaign slide-in 7 refinements (padding, trend, budget ghost marker, score breakdown, section order, 5 levers, cross-campaign recs) |
| `fddda8d` | Campaign slide-in + awaiting card — 6 visual refinements (trend padding, impact row, View Details button, primary perspective, button order) |
| `873207e` | Two micro-fixes: left-align impact line; gain-frame Budget Position pending for primary |

---

## 3. Key architecture

### Campaign slide-in (reusable)

Component is structured so `/v2/campaigns` can reuse it later without porting.

- **Partial:** `act_dashboard/templates/v2/_campaign_slidein.html`
- **CSS:** `act_dashboard/static/css/v2_campaign_slidein.css`
- **JS:** `act_dashboard/static/js/v2_campaign_slidein.js` — exports `window.openCampaignSlidein(clientId, campaignId)`
- **Endpoint:** `GET /v2/api/account/campaign-slidein/<client_id>/<campaign_id>` in `act_dashboard/routes/v2_api.py`
- **Returns one JSON blob** with all 10 body sections: campaign meta, health, score, budget_position, budget_proposed, pending_shift, trend, awaiting, executed, monitoring, alerts, levers

### Decision Details shared panel

Used by both Morning Review and Account Level — single source of truth prevents drift.

- **Partial:** `act_dashboard/templates/v2/_decision_details.html`
- **Shared renderer:** `act_dashboard/static/js/v2_decision_details.js` — exports `window.openDecisionDetails(item)`
- Handler reads `data-*` attrs from the `.act-item`: `data-entity-name`, `data-level`, `data-risk`, `data-action-category`, `data-summary`, `data-recommendation-text`, `data-estimated-impact`, `data-current-value` (JSON), `data-proposed-value` (JSON), `data-decision-tree` (JSON)
- Formatter maps known keys (daily_budget → "Daily budget: £X/day", share_pct → "Share of total: Y%", target_cpa, target_roas, etc.) with before→after rendering. Unknown keys humanise to `key: value`, never raw JSON.

### Role assignment

- **Table:** `act_v2_campaign_roles` (client_id, google_ads_campaign_id PK)
- **Endpoint:** `POST /v2/config/roles/save` in `act_dashboard/routes/v2_config.py`
- **Role codes (5):** `BD` Brand Defence · `CP` Core Performance · `RT` Retargeting · `PR` Prospecting · `TS` Testing
- Each role has `budget_band_<role>_min_pct` and `_max_pct` settings driving Budget Position bands

### Perspective framing (budget shifts)

Computed in `campaign_slidein_data()` route — `act_dashboard/routes/v2_api.py`.

Given a budget-shift rec, the `current_value_json` and `proposed_value_json` both contain `{campaign_name: {daily_budget, share_pct}}` for the TWO campaigns involved. The endpoint fires for each campaign independently:

- **If this campaign is a key in cv/pv:** compute `delta = proposed_daily - current_daily`
- `delta > 0` → gain framing: `"+£X/day incoming from <counterparty>"`
- `delta < 0` → loss framing: `"−£X/day outgoing to <counterparty>"`
- Works for primary entity AND counterparty (same logic, runs for both)
- Both slide-ins reference the SAME `recommendation_id` — approve/decline from either resolves the single underlying rec

`pending_shift` (drives Budget Position "Pending:" line) prefers `awaiting[0].perspective` over the raw primary summary so Brand and DII both show gain/loss-framed text.

### Budget Position data shape

```
budget_position = {
  role, role_label, band_min_pct, band_max_pct,
  monthly_budget_total, band_min_abs, band_max_abs,
  current_mtd, current_pct, status  // in_band | over_band | under_band
}
budget_proposed = {             // null if no pending shift
  mtd, pct, status
}
pending_shift = "<perspective or summary>"
```

Frontend renders a horizontal bar with band range shaded + solid marker (current) + dashed ghost marker (proposed).

### DuckDB gotcha — UPDATE + secondary index

**Bug:** DuckDB 1.1.0 raises a spurious PK-constraint violation on UPDATE of a column that's part of a secondary index.

**Fix applied:** narrowed `idx_act_v2_recs_client_status` from `(client_id, status, identified_at)` to `(client_id, identified_at)` — see commit `a77043d`. Do NOT add `status` back to that index until DuckDB releases the fix.

**Defensive layers also in place** in `v2_api.py`:
1. `WHERE ... AND status = 'pending'` makes duplicate calls silent no-ops
2. `threading.Lock` serialises writes within the Flask process
3. Frontend disables Approve/Decline on first click (re-enabled on failure)

---

## 4. Known issues / deferred

### View Details panel collides with campaign slide-in

Both are 800px right-side panels. Clicking View Details inside the campaign slide-in opens the Decision Details panel ON TOP of the campaign slide-in — they overlap exactly.

Needs redesign: either (a) Decision Details becomes a modal/different edge, (b) Decision Details renders inline inside the campaign slide-in body, or (c) campaign slide-in auto-closes when Decision Details opens.

### Commit `a77043d` — stray files

That commit accidentally swept in many untracked client/prototype files (Objection Experts weekly reports, Inserta Dental onboarding drafts, Dental by Design report pptx versions, screenshots). The bug fix itself is sound but the commit is noisy. User should review before cherry-picking or rebasing.

### Morning Review "Overnight run had failures" banner

Red scheduler-failed banner appears on `/v2/morning-review` when `act_v2_scheduler_runs` has any `status='failed'` row for today. Earlier test runs with DBD's placeholder customer_id left failed rows in the table; banner will clear after the next clean overnight run (next logon).

---

## 5. Next on the build roadmap

Per `memory/MEMORY.md`:

1. **C1 Campaign Level Engine** — 7 strategy-specific checks: Manual CPC, tCPA, tROAS, Max Conversions, Max Clicks, PMax, Standard Shopping. DBD's PMax campaign will produce real recs from day one.
2. **C2 Campaign Level UI** — campaign-level page (likely at `/v2/campaigns`), reusing the campaign slide-in component already delivered.
3. **D-series:** Ad Group (D1-D2), Keyword (D3), Ad (D4) engines + UIs.
4. **E-series:** Shopping engine + UI.
5. **R1 Weekly Reports module** — auto-generates client .pptx from session summaries + DB data.
6. **G-series:** Execution layer — actual Google Ads API writes, rollback/undo wiring.

---

## 6. Token economy

Read `memory/feedback_token_economy.md` at session start. Apply the rules listed there: Edit not Write, Grep not Read, batch tool calls, short status updates.
