# Tier 2.1 AI MVP — Build Plan

**Status as of 25 April 2026 (Sat afternoon, post-compact, post-replan):**

## Tier 1 — DONE ✅
All shipped to `origin/main`:
- 1.1 Scheduler truncation ✅
- 1.2 CHECK constraint ✅
- 1.3 Rate limiter IP exemption ✅
- 1.4 Row-number drift in Pass 1/2 Review UI ✅
- 1.5 Task Scheduler wiring ✅
- 1.6 Auto-watch CSV (per-client folder structure) ✅
- 1.7 Coverage button — **scrapped** (not ACT-fit)
- 1.8 Date picker tooltip ✅

---

## Tier 2.1 AI MVP — FULL SCOPE this weekend

**Decision (25 Apr PM):** ship the FULL Tier 2.1 scope this weekend, not a stripped MVP. That means:
- Classification endpoint + DB tables ✅
- Prompt files + Sonnet batch ✅
- Opus explain-row endpoint ✅
- Pass 3 routing prompt + UI ✅
- Split-screen 65/35 layout (resizable, collapsible) ✅
- AI chat panel with conversation log + custom prompt input ✅
- Canned replies library (4 per flow) ✅
- All UI columns + buttons ✅

Source of truth for the spec: `docs/SCOPE_TIER_2.1_AI_SEARCH_TERMS.md`

**Locked decisions (full list):**
| # | Question | Decision |
|---|---|---|
| Q1 | Agent SDK vs subprocess | Subprocess (`claude -p --output-format json`) |
| Q2 | Prompt hot-reload | Hot-reload during MVP build, version-lock after |
| Q3 | Canned reply library | Ship starter set of 4 per flow |
| Q4 | Model choice | Opus 4.7 for both batch + explain-row (revised 25 Apr PM — see scope §13 Q4) |
| Q5 | Concurrency lock scope | Per-client (409 on duplicate batch from same client) |
| Q6 | Skip-if-classified cache | Skip if `(review_id, prompt_version)` already exists; bumping prompt = re-classify |
| Q7 | Agreement metric | High-confidence subset only (≥85% target) |
| Q8 | Stage order | Dry-run before UI build (cheaper to rip out a bad prompt than a bad UI built around it) |
| Q9 | Chat panel persistence | New `act_v2_ai_chat_log` table (audit trail + feedback loop) |
| Q10 | Split-screen UX | Fixed right panel first, resizable upgrade if time allows |

---

## 13-stage build plan (one brief at a time, test as we go)

### Stage 0 — Ground-truth fixture export (FIRST BRIEF)
- Query `act_v2_search_term_reviews` for `client_id='dbd001'` AND Friday 24-Apr triage actions
- Export to `tests/fixtures/ai_classifier_ground_truth_24_apr.json`
- Stable corpus across prompt iterations — must exist BEFORE any classification runs
- Per scope §8 ("First task in Saturday PM build")
- ~5 min Build 2

### Stage 1 — DB migration
- Create `act_v2_ai_classifications` per scope §5.1
- Create `act_v2_ai_errors` per scope §5.3
- Create `act_v2_ai_chat_log` (NEW — see below)
- Update `create_act_v2_schema.py` for fresh installs
- Pure schema, zero behaviour change
- ~15 min Build 2

**`act_v2_ai_chat_log` schema:**
```sql
CREATE TABLE act_v2_ai_chat_log (
    id INTEGER PRIMARY KEY,
    client_id VARCHAR NOT NULL,
    flow VARCHAR NOT NULL,
    analysis_date DATE NOT NULL,
    role VARCHAR NOT NULL,           -- 'user' | 'assistant' | 'system'
    message TEXT NOT NULL,
    model_version VARCHAR,           -- only on assistant rows
    prompt_version VARCHAR,
    tokens_in INTEGER,
    tokens_out INTEGER,
    latency_ms INTEGER,
    related_review_id INTEGER,       -- if explain-row triggered the message
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_ai_chat_client_flow_date ON act_v2_ai_chat_log(client_id, flow, analysis_date, created_at);
```

### Stage 2 — Endpoint scaffolding
- `POST /v2/api/ai/classify-terms` skeleton (Sonnet batch — scope §6.1)
- `POST /v2/api/ai/explain-row` skeleton (Opus single-row deep reasoning)
- `POST /v2/api/ai/chat` skeleton (free-text custom prompt → Sonnet, logs to chat table)
- `GET /v2/api/ai/chat-history?client_id&flow&analysis_date` (returns chat log for panel hydration)
- All four validate request shape, return stub response, no Claude integration yet
- ~45 min Build 2

### Stage 3 — Prompt files on disk
- `act_dashboard/ai/prompts/search_terms_v1.txt` (scope §7.1, with §7.4 few-shots baked in before OUTPUT FORMAT)
- `act_dashboard/ai/prompts/search_terms_pass3_v1.txt` (scope §7.2)
- `act_dashboard/ai/prompts/search_terms_user_v1.txt` (scope §7.3)
- `act_dashboard/ai/prompts/explain_row_v1.txt` (NEW — Opus deep-reasoning system prompt for single-row explanations)
- `act_dashboard/ai/prompts/chat_v1.txt` (NEW — Sonnet system prompt for free-text panel chat, scoped to current flow context)
- ~15 min Build 2

### Stage 4 — Claude subprocess (Sonnet batch classify)
- Wire `subprocess.run(['claude', '-p', '--output-format', 'json', '--model', 'claude-sonnet-4-6'], stdin=..., timeout=60)`
- Pass system + user prompt via stdin
- Parse JSON output (extract `result` field, then JSON-parse the array inside)
- Persist verdicts/confidence/reasoning/intent_tag to `act_v2_ai_classifications`
- Log failures to `act_v2_ai_errors` (subprocess fail / invalid JSON / timeout / quota)
- Implement retry-once-then-skip
- Implement skip-if-`(review_id, prompt_version)`-exists cache (force_reclassify=true bypass)
- Implement per-client in-process lock (threading.Lock keyed by client_id, 409 on contention)
- Implement 30s idempotency cache keyed on `hash(review_ids + prompt_version)`
- ~1.5h Build 2

### Stage 5 — Claude subprocess (Opus explain-row)
- Wire `claude -p --model claude-opus-4-7` for `/v2/api/ai/explain-row`
- Input: single review_id + optional user question ("why approve?", "what if I keep it?")
- Output: longer-form reasoning (~3-5 sentences), persisted to `act_v2_ai_chat_log` with role='assistant'
- Same error handling pattern as Stage 4
- Same per-client lock so explain-row doesn't race with batch classify
- ~30 min Build 2

### Stage 6 — Dry-run test against fixture
- Fire `/v2/api/ai/classify-terms` against today's 529 PMax Review terms (analysis_date 2026-04-25 = data 24-Apr)
- Compare verdicts against Stage 0 ground-truth fixture
- Measure HIGH-CONFIDENCE agreement rate (the metric that matters per Q7)
- Measure all-rows agreement (sanity check)
- Iterate prompt until ≥85% high-confidence agreement (hot-reload, no restart)
- Hard floor: ≥95% agreement on `service_not_advertised` rows (scope §8)
- Save first run + final run results to `tests/fixtures/ai_classifier_run_v1.json`
- ~1h test/iterate

### Stage 7 — UI columns + action buttons (in main table)
- Add columns to Pass 1/2 Review + PMax Review tables:
  - `AI Verdict` pill (green=approve, red=reject, grey=unsure)
  - `AI Confidence` pill (high/med/low)
  - `AI Reasoning` tooltip (first 200 chars + "expand" link to chat panel)
  - `AI Intent Tag` (subtle subtitle under verdict)
  - Per-row `🔍 Explain` link → fires Opus explain-row, response lands in chat panel
- Render via LEFT JOIN on `act_v2_ai_classifications` at request time, filtered by current `prompt_version`
- Empty state: `—` if no classification exists
- Action bar buttons:
  - `🤖 AI Triage (N pending)` — fires batch classify
  - `✅ Apply high-confidence (Z)` — appears post-classify
  - `🔍 Only show unsure` — filter pill
- Loading states: skeleton pills in AI columns during classify
- Error states: red error pill + retry button
- Modal warning if N > 100 (scope §6.3)
- Reuse existing `/v2/api/negatives/search-term-review/bulk-update` for Apply
- ~2h Build 2

### Stage 8 — Split-screen layout (65/35)
- Right-side AI panel injected into Pass 1/2 + PMax Review pages
- Layout: fixed right panel, 35% width, full-height, sticky header
- Collapsible: button collapses to 40px slim strip with `🤖 Expand AI`
- Persistent across nav (state stored in localStorage: `act_ai_panel_collapsed`, `act_ai_panel_width`)
- Context header inside panel: "PMax Review · N rows · {client_name} · analysis_date {date}"
- **Stretch:** drag-to-resize divider (only if Stage 8 wraps under budget — fixed width is acceptable MVP)
- Mobile fallback: panel goes full-width modal under 1024px
- ~2h Build 2

### Stage 9 — AI chat panel (inside split-screen)
- Conversation log: rendered from `GET /v2/api/ai/chat-history`, scrollable, newest at bottom
- Message bubbles: user-right (grey), assistant-left (blue), system-centred (muted)
- Custom prompt textarea + send button → `POST /v2/api/ai/chat` (Sonnet)
- Send-on-Enter, Shift-Enter for newline
- Loading state: typing indicator while Claude responds
- Auto-scroll to bottom on new message
- Hydrate panel on page load with last 50 messages for current `(client, flow, analysis_date)` triple
- `🗑️ Clear chat` button (soft-delete: sets a `cleared_at` flag on chat rows, doesn't actually delete)
- ~1.5h Build 2

### Stage 10 — Canned replies library
- 4 buttons per flow per scope §13 Q3 starter set:
  - **Search > Block / Search > Review:** Approve veneer/crown/bridge intent | Reject finance-intent | Show only unsure | Explain row {N}
  - **PMax > Block:** Approve all `service_not_advertised` | Approve all `location_outside_service_area` | Show competitor brands | Show non-English queries
  - **PMax > Review:** Triage first 50 by cost | Reject converters | Show only implant-intent rejects | Group rejects by intent tag
  - **Pass 3:** Re-route by intent | Flag ambiguous single tokens | Approve clear location tokens
- Each button = pre-fills the chat input with the canned text + auto-submits
- Some canned replies are filter-actions (e.g. "Show only unsure") — these manipulate the table filter directly without hitting Claude
- Canned replies render as horizontal pill row above the chat input
- Context-aware: panel shows different canned set based on current page/flow
- ~1h Build 2

### Stage 11 — Pass 3 routing wiring
- Add `🤖 Route phrases by intent` button to Pass 3 phrase suggestions table
- Fires Sonnet with `search_terms_pass3_v1.txt` prompt
- Output written to `act_v2_ai_classifications` (uses `ai_target_list_role` column, leaves `ai_verdict` NULL for Pass 3 rows)
- UI shows AI-suggested target list per phrase + `✅ Approve AI routing` bulk button
- Specifically tested against Friday's `gloucester` and `k2` cases (scope §3.6) — `gloucester` should route to `location_phrase`, `k2` should route to `hold_for_review`
- ~1h Build 2

### Stage 12 — End-to-end QA
- Chris drives full triage session against today's 529 PMax Review terms
- Verify: AI Triage button works, verdicts make sense, Apply high-confidence works, chat panel responds, canned replies fire, Opus explain-row works on a tricky row, Pass 3 routing handles ambiguous tokens correctly
- Time the session — target <15 min for 100 PMax Review terms (vs ~40 min manual yesterday)
- Log any UX papercuts → backlog for Tier 2.2 polish sprint
- ~1h Chris

---

## Time budget

| Stage | Estimate |
|---|---|
| 0  | 5 min |
| 1  | 15 min |
| 2  | 45 min |
| 3  | 15 min |
| 4  | 1.5h |
| 5  | 30 min |
| 6  | 1h |
| 7  | 2h |
| 8  | 2h |
| 9  | 1.5h |
| 10 | 1h |
| 11 | 1h |
| 12 | 1h Chris |
| **Total Build 2** | **~12h** |
| **Total Chris** | **~1h** |

**Saturday PM (~5h):** stages 0–6 (DB + endpoints + Sonnet + Opus + dry-run done)
**Sunday (~7h):** stages 7–12 (UI + chat + canned + Pass 3 + QA)

---

## Risk register

1. **Stage 4 prompt iteration loop** — biggest unknown. If Sonnet hits ≥85% on first run we save hours. If we need 5+ iterations, eats into Sunday. Mitigation: hot-reload means each iteration is ~30s, not a restart cycle.
2. **Stage 8 split-screen layout** — biggest UI lift. Mitigation: fixed-width panel first, drag-resize only if time. Mobile fallback to modal keeps responsive scope tiny.
3. **Stage 4 + Stage 5 lock contention** — explain-row could race with batch classify. Mitigation: per-client `threading.Lock`, both endpoints acquire same lock.
4. **Stage 9 chat history hydration** — if 50 messages × 5 flows × 30 days grows, page load slows. Mitigation: pagination later, MVP loads last 50 only.
5. **Stage 10 canned replies for filter-actions** — "Show only unsure" needs to manipulate table, not call Claude. Need clear separation in canned-reply config (`{type: 'filter', action: ...}` vs `{type: 'chat', text: ...}`).
6. **Pass 3 schema overload** — `act_v2_ai_classifications` row with NULL `ai_verdict` and populated `ai_target_list_role` is a different shape. Acceptable for MVP since the table already allows it (verdict is NOT NULL in scope §5.1 — **flagged as a gap, must change to nullable in Stage 1**).

---

## Schema gap fixes (caught during airtight review)

Two changes from scope §5.1 — both must land in Stage 1 brief:

**(1) `ai_verdict` nullable** — Pass 3 rows have no verdict, only `ai_target_list_role`.
- `ai_verdict VARCHAR` (nullable)
- CHECK: `(flow = 'pass3' AND ai_target_list_role IS NOT NULL) OR (flow != 'pass3' AND ai_verdict IS NOT NULL)`

**(2) Source row reference supports both source tables** — review_id FK only fits block/review flows. Pass 3 phrases live elsewhere.
- `review_id INTEGER` (nullable, FK to `act_v2_search_term_reviews.id`)
- `phrase_suggestion_id INTEGER` (nullable, FK to Pass 3 phrase suggestions table)
- CHECK: `(flow = 'pass3' AND phrase_suggestion_id IS NOT NULL AND review_id IS NULL) OR (flow != 'pass3' AND review_id IS NOT NULL AND phrase_suggestion_id IS NULL)`
- Two UNIQUE constraints: `UNIQUE (review_id, prompt_version)` + `UNIQUE (phrase_suggestion_id, prompt_version)`
- Index: `idx_ai_class_phrase_suggestion_id` (partial WHERE phrase_suggestion_id IS NOT NULL)

Stage 1 brief MUST verify the actual Pass 3 phrase suggestions table name before writing the FK — the codebase has the real name (Build 2 will check `act_dashboard/data_pipeline/` or wherever Pass 3 lives).

## Prompt version constants (Stage 3 implementation detail)

Stage 3 brief includes creating `act_dashboard/ai/prompts/__init__.py`:
```python
PROMPT_VERSION_CLASSIFY = "v1"
PROMPT_VERSION_PASS3 = "v1"
PROMPT_VERSION_EXPLAIN = "v1"
PROMPT_VERSION_CHAT = "v1"
```
Imported by the endpoint code. Bump version → file rename + constant change → next classify run re-classifies all rows under new version (cache miss is intentional).

---

## Process reminders
- Chris is PM, never codes
- One stage/brief at a time, test + approve as we go
- No big batches of briefs
- Always reduce screenshot size before inspection (`docs/screenshots/tier_2.1_ai_mvp/_resize.py`)
- ACT terminology: Approve = block (push neg), Reject = keep running
- Date picker convention: picker 25/4 = data for 24/4 (intentional)

## Screenshots folder for this build
`C:\Users\User\Desktop\gads-data-layer\docs\screenshots\tier_2.1_ai_mvp\`

## Test corpus reference
- Friday 24 Apr triage: Search Block 5/2, Search Review 11/13, PMax Block 68/0, PMax Review batch 1 40/10, batch 2 42/8, Pass 3 5/1
- Today's 529 PMax terms (analysis_date 2026-04-25, data 24-Apr) — clean test set with known characteristics
- Stage 0 fixture = ground truth for prompt iteration

## Resume instruction
When Chris says "go", write the **Stage 0 brief** (ground-truth fixture export) for Build 2.
