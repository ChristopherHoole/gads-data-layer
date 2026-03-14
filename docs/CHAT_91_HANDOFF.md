# Chat 91 Handoff — Campaign Rules & Flags

## What was built

Full replacement of the old JSON-backed rules system (41 rules, `rules_config.json`) with a database-backed Campaign Rules & Flags system.

---

## Files created / modified

### New files
| File | Purpose |
|---|---|
| `tools/migrate_rules_schema.py` | Creates `rules` + `rule_evaluation_log` tables; adds `rule_id` FK to `recommendations`; wipes old recommendations |
| `tools/seed_campaign_rules.py` | Seeds 54 rows: 24 rules + 30 flags for `client_christopher_hoole` |
| `act_dashboard/templates/components/rules_flags_tab.html` | Rules & Flags tab pane (sub-tabs: Rules / Flags / Templates; two data tables; JS CRUD handlers) |
| `act_dashboard/templates/components/rules_flow_builder.html` | 5-step full-page overlay flow builder (add / edit rules & flags) |
| `act_dashboard/static/css/rules.css` | All CSS for flow builder, tables, badges (no body/html/utility class overrides) |

### Modified files
| File | Change |
|---|---|
| `act_dashboard/routes/campaigns.py` | Added 5 API endpoints + `_get_warehouse()` + `_serialize_rule()` helpers |
| `act_dashboard/app.py` | Added Chat 91 CSRF exemption block for all 5 new routes |
| `act_dashboard/templates/campaigns.html` | Added `rules.css` link; renamed Rules tab to "Rules & Flags"; replaced `rules_tab.html` include with `rules_flags_tab.html`; added `rules_flow_builder.html` include before `{% endblock %}` |

---

## API endpoints (all under Blueprint `campaigns`)

| Method | URL | Function | Purpose |
|---|---|---|---|
| GET | `/campaigns/rules` | `list_rules` | Returns all rules/flags for current client |
| POST | `/campaigns/rules` | `create_rule` | Creates a new rule or flag |
| PUT | `/campaigns/rules/<id>` | `update_rule` | Updates an existing rule or flag |
| DELETE | `/campaigns/rules/<id>` | `delete_rule` | Deletes a rule or flag |
| POST | `/campaigns/rules/<id>/toggle` | `toggle_rule` | Flips `enabled` boolean |

All return `{"success": true/false, "data": ...}`.

---

## Database schema

### `rules` table
```sql
id                INTEGER PRIMARY KEY
client_config     VARCHAR NOT NULL
entity_type       VARCHAR NOT NULL DEFAULT 'campaign'
name              VARCHAR NOT NULL
rule_or_flag      VARCHAR NOT NULL   -- 'rule' | 'flag'
type              VARCHAR NOT NULL   -- 'budget' | 'bid' | 'status' | 'performance' | 'anomaly' | 'technical'
campaign_type_lock VARCHAR            -- 'troas' | 'tcpa' | 'max_clicks' | 'all'
entity_scope      JSON NOT NULL      -- {"scope":"all"} | {"scope":"specific","campaigns":[...]}
conditions        JSON NOT NULL      -- [{metric, op, value, ref}, ...]
action_type       VARCHAR            -- 'increase_budget' | 'decrease_budget' | 'pause' | etc.
action_magnitude  FLOAT
cooldown_days     INTEGER DEFAULT 7
risk_level        VARCHAR            -- 'low' | 'medium' | 'high'
enabled           BOOLEAN NOT NULL DEFAULT TRUE
created_at        TIMESTAMP
updated_at        TIMESTAMP
last_evaluated_at TIMESTAMP
last_fired_at     TIMESTAMP
```

### `rule_evaluation_log` table
```sql
id                INTEGER PRIMARY KEY
rule_id           INTEGER NOT NULL
entity_type       VARCHAR NOT NULL
entity_id         VARCHAR NOT NULL
evaluated_at      TIMESTAMP
conditions_met    BOOLEAN NOT NULL
recommendation_id INTEGER
skip_reason       VARCHAR
```

---

## Seed data summary

54 rows seeded for `client_christopher_hoole`:
- Budget rules (tROAS): 5
- Budget rules (tCPA): 5
- Budget rules (Max Clicks): 5
- Bid rules (tROAS): 2
- Bid rules (tCPA): 2
- Bid rules (Max Clicks): 2
- Status rules: 3
- Performance flags: 16
- Anomaly flags: 8
- Technical flags: 6

---

## Key technical patterns

- **DuckDB IDs**: `SELECT COALESCE(MAX(id), 0) + 1 FROM rules` (no AUTO_INCREMENT)
- **JSON columns**: stored as VARCHAR; `_serialize_rule()` calls `json.loads()` before returning
- **Session**: always `session.get("current_client_config")` — never `get_current_config()`
- **DuckDB connection**: `duckdb.connect(str(path))` — never `read_only=True`
- **CSRF**: all 5 routes exempted via `app.view_functions[route_name]` pattern in `app.py`
- **Plain English**: generated client-side by `rfPlainEnglish(row)` in `rules_flags_tab.html`

---

## What is NOT built yet

- **Rule evaluation engine**: the worker that evaluates `rules` against live campaign data and writes to `rule_evaluation_log` + `recommendations`. This is a future chat.
- **Recommendations integration**: the Recommendations tab currently shows seeded data from before Chat 91 wiped it; it will be repopulated by the evaluation engine.
- **Rule editing in flow builder**: `openRulesFlow(row)` populates the form from an existing row — but the full round-trip PUT hasn't been tested end-to-end against the DB.

---

## Testing checklist

1. `python tools/migrate_rules_schema.py` → should print 4 green checkmarks
2. `python tools/seed_campaign_rules.py` → should print "Seeded 54 rows: 24 rules, 30 flags"
3. Navigate to Campaigns → Rules & Flags tab
4. Rules sub-tab: 24 rules grouped by Budget / Bid / Status
5. Flags sub-tab: 30 flags grouped by Performance / Anomaly / Technical
6. Toggle on/off → PATCH `/campaigns/rules/<id>/toggle` returns 200
7. Delete a rule → `DELETE /campaigns/rules/<id>` → row removed without reload
8. "+ Add rule or flag" → 5-step overlay opens, all steps navigate, Save posts to `/campaigns/rules`
9. Main tab badge shows total count of rules + flags
