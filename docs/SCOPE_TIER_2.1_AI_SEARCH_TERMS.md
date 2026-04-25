# Scope — Tier 2.1: AI analysis inside ACT (Search Terms)

**Captured:** Friday 24 April 2026, end of session.
**Updated:** Saturday 25 April 2026 — second pass, error fixes + gap-fills + decisions on the 4 open questions (now resolved at section 13).
**Purpose:** Scope doc for the MVP build over the weekend (Sat PM + Sunday).
**Review before build:** Chris.

---

## 1. Why we're building this

Today Chris manually triaged ~185 search terms by pasting term lists into a separate Claude chat, getting verdicts back, then manually actioning each row in ACT.

The goal is to **bring that AI triage loop inside ACT** so:
- The AI has full context (term + cost + campaign + triggering keyword + client config) without Chris copy-pasting
- Verdicts are written back to the DB with reasoning, confidence, and audit trail
- Chris actions suggestions with one click, not by typing verdicts
- The system learns from his Approve/Reject history over time

MVP success metric: Chris can triage 100 PMax Review terms in <15 min (today took ~40 min).

---

## 2. Architecture decision — Option B (Claude Agent SDK + Max plan)

| Choice | Implementation | Auth | Cost |
|---|---|---|---|
| **A (not chosen)** | Anthropic API direct | Separate API key | Extra billing |
| **✅ B (MVP)** | Claude Agent SDK (subprocess/SDK) | Chris's Max plan via Claude Code auth | Covered by Max plan |

### How Option B plugs into ACT

ACT's Flask app spawns a Claude subprocess per classification batch (decision in Q1):
```
claude -p --output-format json --model claude-sonnet-4-6 < prompt.txt
```
- Stdin = combined system + user prompt
- Stdout = JSON object with `result`, `usage`, `model`, etc.
- Flask parses `result` (which itself contains the structured classification array)
- Writes per-term rows to `act_v2_ai_classifications`
- Returns aggregate to UI

**Why subprocess over the Python SDK (`claude-agent-sdk`):** subprocess is dependency-free, has trivial error handling (exit code + parse), and the SDK's added value (streaming, tool use, multi-turn) is unused for batch classification. If we later need streaming progress, we revisit.

**When to revisit Option A (Anthropic API):** when ACT moves to a live server hosting multiple clients beyond Chris's machine. At that point the subprocess approach stops working (shared auth, multi-user, no per-tenant rate limits), and we port to Anthropic API with billing per client. Expected ~1 month out per Chris.

### Failure modes (and what we do)

| Failure | Behaviour |
|---|---|
| `claude` CLI not in PATH | API returns 503 with clear message: "AI not configured on this server" — UI hides AI buttons gracefully |
| Subprocess exit code != 0 | Retry once with same input. If second attempt fails, log to `act_v2_ai_errors` (new lightweight table — see §5.3) and return rows un-classified. Manual triage continues uninterrupted. |
| Claude returns invalid JSON | Same retry-then-skip pattern. UI shows row as un-classified (`—` in AI columns). |
| Subprocess hangs > 60s | Kill, mark batch as failed, log. Chris falls back to manual. |
| Max plan quota exhausted | CLI returns specific error code → API returns 429 with "AI quota reached, try later" — UI surfaces the message in the AI panel header. |

In all failures: **manual triage path is unchanged**. AI is purely additive — never blocks core triage.

---

## 3. The daily Search Terms workflow

What Chris does today, flow by flow, with proposed AI touch points marked ⭐.

### 3.1 Morning Review → Search Terms (entry point)

**Current:**
- Morning Review page shows "Search Terms Awaiting Review: N"
- Click → Search Terms page opens with today's analysis_date

**Proposed:**
- ⭐ AI classifications are NOT auto-fired overnight in MVP (decision: keep AI explicit for now to control quota use). Post-MVP we can add an opt-in `auto_classify_overnight` setting per client.
- First page load: AI columns show `—` until Chris clicks `🤖 AI Triage`
- Top banner shown after triage: "AI classified N of M rows — X need your review"

### 3.2 Flow: Search > Block

**Current:**
- Typical 5–10 rows per day, reasons: `service_not_advertised`, `contains_neg_vocabulary`, `existing_exact_neg_match`, `existing_phrase_neg_match`
- Chris walks row by row, decides Approve / Reject

**Proposed:**
- ⭐ AI verdict column populated (Approve / Reject / Unsure)
- ⭐ AI reasoning tooltip per row
- ⭐ Confidence pill (green/amber/red)
- Action buttons:
  - `🤖 AI triage` — pre-sort all pending rows
  - `✅ Apply AI calls` — action every high-confidence AI verdict
  - `🔍 Only show unsure` — filter to rows AI flagged as needing human review
- Canned replies in the AI panel:
  - "Approve all except rows [X, Y]"
  - "Reject the finance-intent ones"
  - "Why is row 5 Approve?"

### 3.3 Flow: Search > Review

Same pattern as 3.2, but `pass1_status='review'` rows. These are the ambiguous ones where AI value-add is highest.

### 3.4 Flow: PMax > Block

Typical volume: 50–80 rows/day. Broken into sub-filters (reason facets: `service_not_advertised`, `contains_neg_vocabulary`, `location_outside_service_area`, `existing_exact_neg_match`).

**Proposed additions:**
- ⭐ AI triage **on button click** (not auto on page load — avoids surprise quota burn)
- ⭐ Per-reason-bucket batch action: `"🤖 AI-approve all 34 service_not_advertised rows"` — one click
- Canned replies for AI panel:
  - "Show me only the rows you're unsure about"
  - "Explain the cluster of veneer-intent rows"
  - "Any anomalies in today's batch?"

**Auto-classification policy:** Never run a classification batch without an explicit user click. Caching exception: if classifications already exist for these review_ids and the prompt_version matches the current code constant, the AI columns populate from cache without re-firing the classifier.

### 3.5 Flow: PMax > Review

Highest-volume flow (303 today). Chris capped at 100/day to avoid shocking the system.

**Proposed:**
- ⭐ AI triage in batches of 50 (matches current workflow)
- ⭐ "Hold budget" feature — AI flags terms where blocking could lose a converting pattern, holds them for human review
- Canned replies:
  - "Triage first 50, show me only the rejects"
  - "Any terms that look like converting intent?"
  - "Group by intent so I can batch-approve"

### 3.6 Flow: Pass 3 Phrase Suggestions

Today's run produced 6 suggestions, all location-outside-service-area. We approved 5, rejected 1 (`k2` — too ambiguous).

**Proposed:**
- ⭐ AI assigns target list by intent — location tokens go to `Loc 1 WRD [ph]`, competitor tokens to `Comp [ph]`, etc. **(Fixes 2.1e — the bug we saw today where `gloucester` landed in `1_word_phrase` not `Loc 1 WRD [ph]`.)**
- ⭐ AI flags ambiguous single tokens as "review before push" (would have caught `k2`)
- Action buttons:
  - `🤖 Route to correct lists` — AI re-assigns target list role for all pending
  - `✅ Approve AI routing` — accepts the re-routing

---

## 4. Split-screen UX (65% main / 35% AI panel)

### 4.1 Layout

```
┌─────────────────────────────────────────┬────────────────────┐
│ Main ACT (65%)                          │ AI Panel (35%)     │
│                                         │                    │
│  [Search Terms table]                   │  💬 AI chat log    │
│  - Row-level AI verdict pill            │                    │
│  - Row-level AI confidence              │  Action buttons:   │
│  - Normal triage controls               │  [🤖 Triage batch] │
│                                         │  [✅ Apply calls]  │
│                                         │  [🔍 Only unsure]  │
│                                         │                    │
│                                         │  Canned replies:   │
│                                         │  [Approve X]       │
│                                         │  [Reject finance]  │
│                                         │  [Explain row 5]   │
│                                         │                    │
│                                         │  Custom prompt:    │
│                                         │  [________]  [▶]   │
└─────────────────────────────────────────┴────────────────────┘
```

### 4.2 Behaviour rules

- **Resizable divider** (drag to adjust)
- **Collapsible** via button (collapses to a slim 40px strip with "🤖 Expand AI")
- **Persistent across nav** — Chris stays in AI context as he moves between flows
- **Scoped context** — AI panel "knows" what page/flow Chris is on, adjusts prompts accordingly
- **Not a modal** — main ACT remains fully usable alongside

### 4.3 What lives in the AI panel

1. **Context header** — "PMax Review · 50 rows · dbd001 · analysis_date 2026-04-23"
2. **Conversation log** — every AI prompt + response + user action, scrollable
3. **Action buttons** (context-aware — different per flow)
4. **Canned replies** (context-aware — different per flow)
5. **Custom prompt input** — free-text fallback for anything not covered by canned replies

---

## 5. Data model additions

### 5.1 New table: `act_v2_ai_classifications`

```sql
CREATE TABLE act_v2_ai_classifications (
    id INTEGER PRIMARY KEY,
    review_id INTEGER NOT NULL,         -- FK to act_v2_search_term_reviews.id
    client_id VARCHAR NOT NULL,
    analysis_date DATE NOT NULL,
    search_term VARCHAR NOT NULL,
    flow VARCHAR NOT NULL,              -- 'search_block', 'search_review', 'pmax_block', 'pmax_review', 'pass3'
    ai_verdict VARCHAR NOT NULL,        -- 'approve', 'reject', 'unsure'
    ai_target_list_role VARCHAR,        -- for Pass 3: '1_word_phrase', 'location_phrase', etc.
    ai_reasoning TEXT,
    ai_confidence VARCHAR NOT NULL,     -- 'high', 'medium', 'low'
    ai_intent_tag VARCHAR,              -- see §7.1 for full enum (researcher | price_shopper | ready_to_book | competitor | location_wrong | service_wrong | noise | converting)
    model_version VARCHAR NOT NULL,     -- e.g. 'claude-sonnet-4-6'
    prompt_version VARCHAR NOT NULL,    -- our internal prompt template version
    tokens_in INTEGER,
    tokens_out INTEGER,
    latency_ms INTEGER,                 -- per-row attribution of batch latency (batch_total / row_count)
    classified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_action VARCHAR,                -- 'accepted', 'overridden', 'ignored' — populated when user actions
    user_actioned_at TIMESTAMP,
    UNIQUE (review_id, prompt_version)  -- one classification per (row, prompt version) — re-classification with new prompt creates new row
);
CREATE INDEX idx_ai_class_review_id ON act_v2_ai_classifications(review_id);
CREATE INDEX idx_ai_class_client_date_flow ON act_v2_ai_classifications(client_id, analysis_date, flow);
CREATE INDEX idx_ai_class_user_action ON act_v2_ai_classifications(user_action) WHERE user_action IS NOT NULL;
```

### 5.2 Why separate table (not columns on review table)

- Rollback-friendly — drop table, re-run, no schema migrations on main review table
- Multiple AI runs per term possible (re-classify after prompt update — `UNIQUE (review_id, prompt_version)` allows it)
- Clean training corpus later (user_action column = ground truth for feedback loop)
- Cache lookup: when rendering review table, LEFT JOIN on `(review_id, current_prompt_version)` — if a row exists, render the cached verdict; if not, show `—`

### 5.3 Lightweight error table: `act_v2_ai_errors`

For observability of failed classifications (silent failures kill iteration speed):

```sql
CREATE TABLE act_v2_ai_errors (
    id INTEGER PRIMARY KEY,
    client_id VARCHAR,
    analysis_date DATE,
    flow VARCHAR,
    review_ids_in_batch TEXT,           -- JSON array of attempted IDs
    error_type VARCHAR NOT NULL,        -- 'subprocess_failed', 'invalid_json', 'timeout', 'quota_exhausted'
    error_message TEXT,
    raw_output TEXT,                    -- truncated to 4KB for diagnostics
    occurred_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Read this in a `/v2/ai-health` admin view (post-MVP, just collect for now).

---

## 6. MVP scope — 2.1a + 2.1b + 2.1d

Out of the 9 sub-items under 2.1, weekend MVP ships these three:

### 6.1 [2.1a] Classification endpoint

`POST /v2/api/ai/classify-terms`

**Request:**
```json
{
  "client_id": "dbd001",
  "analysis_date": "2026-04-23",
  "flow": "pmax_review",
  "review_ids": [1234, 1235, ...]  // rows to classify
}
```

**Response:**
```json
{
  "classified": 50,
  "results": [
    {
      "review_id": 1234,
      "search_term": "best dentist uk",
      "ai_verdict": "reject",
      "ai_confidence": "high",
      "ai_reasoning": "Already converted at £2.56 CPA. Blocking would lose a proven winner.",
      "ai_intent_tag": "researcher"
    },
    ...
  ],
  "tokens_used": 23450,
  "wall_clock_ms": 12300
}
```

**Acceptance criteria:**
- Handles 50-row batches in < 20s
- Writes every result to `act_v2_ai_classifications`
- Returns `ai_verdict` ∈ {approve, reject, unsure}
- Invokes Claude via subprocess `claude -p --output-format json` (Q1 decision)
- Graceful failure if Claude returns invalid JSON (retry once, then log to `act_v2_ai_errors` and return rows un-classified)
- **Skips already-actioned rows** — filters `review_status = 'pending'` in the SQL that fetches inputs
- **Skips already-classified rows by default** — if a row has a classification with `prompt_version = current`, it's reused unless `force_reclassify=true` in the request body
- **Idempotency** — if the same payload arrives twice within 30s, the second call returns the first call's results from cache (in-memory dict keyed on hash of `review_ids` + `prompt_version`)
- **Concurrency lock** — a per-`client_id` lock prevents two simultaneous classification batches from the same client (returns 409 Conflict on second simultaneous call)
- **Telemetry** — every call logs to `act_v2_ai_classifications` (per row) + `act_v2_ai_errors` on failure

### 6.2 [2.1b] AI reasoning shown per row

**UI change:** Add 3 columns to Pass 1/2 Review + PMax Review tables:
- `AI Verdict` (pill: green=approve, red=reject, grey=unsure)
- `AI Confidence` (pill: high/med/low)
- `AI Reasoning` (tooltip on hover — first 200 chars + "read full")

Full reasoning opens in a sidebar click-expand.

**Acceptance criteria:**
- Columns render without hitting API (read from `act_v2_ai_classifications` via join)
- If no classification exists for a row, columns show `—`
- Hover shows full reasoning within 100ms

### 6.3 [2.1d] "Bulk AI triage" action button

**UI:** Button at top of each flow table: `🤖 AI Triage (N pending)`

**Behaviour:**
1. Click → fires POST to `/v2/api/ai/classify-terms` with all pending review IDs in the current filter
2. Button enters loading state ("Classifying… N rows"), table rows show skeleton state in AI columns
3. On completion → reload AI columns only (not full table — preserve scroll/sort)
4. Toast: "AI classified N terms in Xs — Y need your review"
5. Follow-up button appears: `✅ Apply high-confidence AI verdicts (Z)` — actions every row where `ai_confidence='high'`. Reuses existing `/v2/api/negatives/search-term-review/bulk-update` endpoint — does NOT reinvent action logic.

**Acceptance criteria:**
- Works on any filter combination (reason, campaign source, status)
- Respects Chris's "no batches over 100" preference — modal warning if > 100, with "Continue / Cancel". Defaults to first 100 by `total_cost DESC`.
- Writes to DB incrementally so a mid-batch failure doesn't lose progress (per-row INSERT, not bulk transaction)
- **Loading states:** button disabled while in flight; rows show skeleton (grey pill placeholders) in AI columns
- **Error states:** if classification fails, button returns to enabled with red error tooltip, rows return to `—`
- **Re-click:** clicking again skips already-classified rows by default (uses cache from §6.1 acceptance criteria)
- **"Apply high-confidence" reuse:** internally maps `ai_verdict='approve' AND ai_confidence='high'` → `review_status='approved'`, then `ai_verdict='reject' AND ai_confidence='high'` → `review_status='rejected'`. Calls existing bulk-update endpoint (single round-trip per verdict bucket). Sets `user_action='accepted'` on each classification row.

---

## 7. Prompt engineering spec

### 7.1 System prompt — block/review flows (`search_block`, `search_review`, `pmax_block`, `pmax_review`)

Save to: `act_dashboard/ai/prompts/search_terms_v1.txt`

```
You are ACT's search-terms triage assistant for a Google Ads client.

Your job: for each search term in the batch, decide whether the client should:
  - APPROVE the block (push the term as a negative keyword — stop ads showing for it)
  - REJECT the block (keep the term running — it's worth the spend)
  - UNSURE (needs human judgement)

Important — ACT terminology is INVERTED from colloquial language:
  - "approve" = block the term (push as negative keyword)
  - "reject" = reject the block (keep the term running)
  - "unsure" = ambiguous, escalate to human

Always use ACT terminology in your output.

==========================================================================
CLIENT CONTEXT
==========================================================================

Client ID: {{client_id}}
Client name: {{client_name}}
Persona: {{persona}}                            # e.g. lead_gen_cpa
Target CPA: £{{target_cpa}}
Service area: {{service_area}}                  # e.g. "London / UK-wide"
Clinic location: {{clinic_location}}            # e.g. "45 Beadon Road, Hammersmith W6"

Services ADVERTISED (we want these queries):
  {{services_advertised_csv}}

Services NOT advertised (we don't want these queries):
  {{services_not_advertised_csv}}

Brand terms (always keep — never block):
  {{brand_terms_csv}}

Competitor brands (always block):
  {{competitor_brands_csv}}

Today's converters (search terms that drove conversions in the last 30 days — never block):
  {{converters_last_30d_csv}}

==========================================================================
DECISION HEURISTICS (apply in this order)
==========================================================================

APPROVE the block (push as negative) when ANY of:
  1. The term contains a service that's NOT in the advertised list
     — e.g. "veneers cost", "dental crown price", "teeth whitening", "invisalign"
  2. The term references a wrong location outside the service area
     — e.g. "dental implants manchester", "dentist edinburgh", "cancun dental"
  3. The term contains a competitor brand
     — e.g. "bluebell dental", "k2 dental", "instamile", "mydentist"
  4. The term is in a non-English language (we don't run multi-language ads)
     — e.g. Polish, Spanish, Romanian, Arabic queries
  5. The term is research-only and clearly not transactional
     — e.g. "how does a bridge work", "different types of teeth shapes", "dental laboratory near me" (B2B)
  6. The term is a generic price/quality shopper with no implant signal
     — e.g. "cheap dentist near me", "best dentist uk", "budget friendly dentist near me"
  7. The term is novelty/unrelated noise
     — e.g. "vampire fangs", "balamory dentist", "big teeth"

REJECT the block (keep running) when ANY of:
  1. The term is in the converters list — already converted, never block a winner
  2. The term contains a clearly advertised service
     — e.g. "dental implants london", "all on 4 cost", "vivo bridge"
  3. The term has implant intent even if loosely worded
     — e.g. "screw in teeth uk", "permanent dental bridge", "replace missing molars",
       "full set of new teeth", "all for one teeth"
  4. The term has finance/payment intent (this client offers 0% finance)
     — e.g. "dental loan", "dentist that take payment plans", "teeth on finance",
       "dental finance plans uk"
  5. The term has same-day-treatment intent (this client offers Teeth-in-a-Day)
     — e.g. "one day dentist near me", "same day teeth replacement"
  6. The term is the client's own brand or location
     — e.g. "dentist hammersmith" (DBD location), "dental by design reviews"
  7. The term is a comparison shopper considering implants
     — e.g. "tooth implant vs crown cost", "implants vs dentures cost"

UNSURE (escalate to human) when:
  - Signals conflict (e.g. competitor brand AND implant intent)
  - The term is technical and you can't tell if it's relevant
  - Single-token brand fragments without context
  - Term is in client's services list but with a strongly negative qualifier you don't understand

==========================================================================
CONFIDENCE LEVELS
==========================================================================

HIGH: Multiple heuristics align unambiguously. Examples:
  - "veneers cost" → APPROVE (heuristic #1, service not advertised)
  - "dental implants london" → REJECT (heuristic #2, advertised service in service area)

MEDIUM: One clear heuristic, but with one minor counter-signal. Examples:
  - "best dentist uk" with 1 conversion → REJECT (heuristic #1 — converter — but "best dentist uk" alone is broad)
  - "permanent dental bridge" → REJECT (implant intent likely, but "dental bridge" alone is in not-advertised)

LOW: Genuine ambiguity. Examples:
  - "tooth doc" → likely approve (unclear brand) but signal is weak

If confidence is LOW you should usually output UNSURE.

==========================================================================
INTENT TAGS (pick exactly one)
==========================================================================

  - researcher          : information-seeking, not buying yet
  - price_shopper       : comparison/budget query (cheap, affordable, cheapest, etc.)
  - ready_to_book       : transactional, near-bottom-of-funnel
  - competitor          : query mentions a competitor brand
  - location_wrong      : wrong geography
  - service_wrong       : service we don't offer
  - noise               : nonsense, novelty, B2B, non-English
  - converting          : matches the converters list

==========================================================================
OUTPUT FORMAT
==========================================================================

Respond with ONLY a JSON array — no preamble, no markdown fences. One object per term, in the same order as input.

Each object:
{
  "review_id": <integer matching input>,
  "ai_verdict": "approve" | "reject" | "unsure",
  "ai_confidence": "high" | "medium" | "low",
  "ai_reasoning": "<1-2 sentences referencing the specific heuristic that drove the decision>",
  "ai_intent_tag": "researcher" | "price_shopper" | "ready_to_book" | "competitor" | "location_wrong" | "service_wrong" | "noise" | "converting"
}

Reasoning style guide:
  - State the heuristic that fired ("Veneers not in advertised services")
  - Reference specific data when relevant ("Already converted at £2.56 CPA — proven winner")
  - Keep to 1–2 sentences, no fluff
  - No hedging language ("I think", "probably") — be decisive at high/medium confidence
```

### 7.2 System prompt — Pass 3 phrase routing flow

Save to: `act_dashboard/ai/prompts/search_terms_pass3_v1.txt`

Different output schema — no verdict, just target list assignment.

```
You are ACT's Pass 3 phrase-suggestion router.

Pass 3 generates phrase-level negative keyword suggestions from approved
single-term blocks. Your job is to assign each suggested phrase to the
correct negative-keyword list based on intent.

==========================================================================
TARGET LISTS (pick exactly one per phrase)
==========================================================================

  - location_phrase     : phrase represents a wrong-geography token
                          (e.g. "gloucester", "stafford", "bl3", "hartlepool")
  - competitor_phrase   : phrase represents a competitor brand
                          (e.g. "bluebell", "instamile", "k2 dental")
  - service_phrase      : phrase represents a service not advertised
                          (e.g. "veneers", "crowns", "fillings")
  - generic_1_word      : single broad noise token (catch-all when others don't fit)
  - generic_2_word      : two-word phrase that doesn't fit the above
  - generic_3_word      : three-word phrase that doesn't fit the above
  - generic_phrase      : longer phrases that don't fit the above
  - hold_for_review     : phrase is too ambiguous to route automatically

==========================================================================
ROUTING HEURISTICS
==========================================================================

Rule 1: If the phrase is a single token that's a UK city/town/postcode →
        location_phrase (regardless of word count).

Rule 2: If the phrase contains a known competitor brand →
        competitor_phrase.

Rule 3: If the phrase is a non-advertised dental service (veneers, crowns,
        bridges, fillings, ortho, periodontal) → service_phrase.

Rule 4: If the phrase is a single ambiguous token (e.g. "k2", "ag",
        2-character abbreviations) → hold_for_review.
        (Single tokens as phrase negatives risk false positives.)

Rule 5: Otherwise → fall back to generic_Nword based on word count.

==========================================================================
OUTPUT FORMAT
==========================================================================

Respond with ONLY a JSON array. One object per input phrase.

Each object:
{
  "phrase_id": <integer matching input>,
  "fragment": "<input phrase verbatim>",
  "ai_target_list_role": "location_phrase" | "competitor_phrase" | "service_phrase" | "generic_1_word" | "generic_2_word" | "generic_3_word" | "generic_phrase" | "hold_for_review",
  "ai_confidence": "high" | "medium" | "low",
  "ai_reasoning": "<1 sentence>"
}
```

### 7.3 User prompt template (per batch — block/review flows)

Save to: `act_dashboard/ai/prompts/search_terms_user_v1.txt`

```
Triage these {{count}} search terms for {{client_id}} on {{analysis_date}}, flow={{flow}}.

Format for each row:
  [<review_id>] "<search_term>"
    pass1_reason: <reason> / detail: <pass1_reason_detail>
    cost: £<total_cost> | clicks: <total_clicks> | impressions: <total_impressions> | conversions: <total_conversions>
    triggered by keyword: "<keywords or '—' if none>"
    campaigns: <campaigns or '—'>

Terms:

{{rendered_term_list}}

Return JSON array as specified in the system prompt. One object per term, same order as input.
```

### 7.4 Few-shot examples (anchor in system prompt before "OUTPUT FORMAT")

Insert before the OUTPUT FORMAT section:

```
==========================================================================
EXAMPLES (anchored on Friday 24 Apr triage by the human PM)
==========================================================================

INPUT:
[101] "veneers on finance"
  pass1_reason: service_not_advertised / detail: veneers
  cost: £6.08 | clicks: 1 | impressions: 1 | conv: 0
  triggered by keyword: "finance dental treatment"

OUTPUT:
{
  "review_id": 101,
  "ai_verdict": "approve",
  "ai_confidence": "high",
  "ai_reasoning": "Veneers are not in the advertised services list. Despite the finance qualifier, the core intent is veneers, which we don't offer.",
  "ai_intent_tag": "service_wrong"
}

---

INPUT:
[102] "best dentist uk"
  pass1_reason: ambiguous / detail: no_match
  cost: £2.56 | clicks: 1 | impressions: 1 | conv: 1
  triggered by keyword: "—"

OUTPUT:
{
  "review_id": 102,
  "ai_verdict": "reject",
  "ai_confidence": "high",
  "ai_reasoning": "Already converted at £2.56 CPA — proven winner. Never block a converter even if the query is broad.",
  "ai_intent_tag": "converting"
}

---

INPUT:
[103] "permanent dental bridge"
  pass1_reason: service_not_advertised / detail: dental bridge
  cost: £0 | clicks: 0 | impressions: 0 | conv: 0
  triggered by keyword: "solutions for missing teeth"

OUTPUT:
{
  "review_id": 103,
  "ai_verdict": "reject",
  "ai_confidence": "medium",
  "ai_reasoning": "'Permanent' qualifier signals implant-supported intent (Vivo Bridge fit), not tooth-supported bridge. Worth keeping despite the not-advertised flag on 'dental bridge'.",
  "ai_intent_tag": "ready_to_book"
}

---

INPUT:
[104] "dental implants taunton"
  pass1_reason: location_outside_service_area / detail: taunton
  cost: £0 | clicks: 0 | impressions: 1 | conv: 0
  triggered by keyword: "—"

OUTPUT:
{
  "review_id": 104,
  "ai_verdict": "approve",
  "ai_confidence": "high",
  "ai_reasoning": "Taunton (Devon) is well outside the West London service area.",
  "ai_intent_tag": "location_wrong"
}

---

INPUT:
[105] "k2 dental"
  pass1_reason: location_outside_service_area / detail: k2
  cost: £0 | clicks: 0 | impressions: 2 | conv: 0
  triggered by keyword: "—"

OUTPUT:
{
  "review_id": 105,
  "ai_verdict": "unsure",
  "ai_confidence": "low",
  "ai_reasoning": "'k2' is too short to disambiguate confidently — could be a postcode fragment or a competitor brand. Escalate.",
  "ai_intent_tag": "competitor"
}
```

### 7.5 Prompt template versioning

- Prompts live as text files in `act_dashboard/ai/prompts/`
- During MVP build (Sat/Sun): Flask reads file at request time → hot-reload, no restart needed
- After MVP: switch to module-load-time read with `PROMPT_VERSION = "v1"` constant
- Every classification logs `prompt_version` in `act_v2_ai_classifications` so we can attribute agreement-rate changes to specific prompt revisions
- To bump version: copy `search_terms_v1.txt` → `search_terms_v2.txt`, edit, update constant. Old classifications remain attributed to v1.

---

## 8. Test corpus (for MVP validation)

Use Friday 24/4's actual triage as ground truth:
- Search Block: 7 terms, 5 approve / 2 reject
- Search Review: 24 terms, 11 approve / 13 reject
- PMax Block (sample 30 of 68): all approve
- PMax Review batch 1: 50 terms, 40 approve / 10 reject
- PMax Review batch 2: 50 terms, 42 approve / 8 reject
- Pass 3: 6 terms, 5 approve / 1 reject (rejected `k2` as ambiguous)

**Save this before context is lost.** Friday's triage table contents are recoverable from `act_v2_search_term_reviews` WHERE `client_id='dbd001'` AND `analysis_date='2026-04-23'` AND `reviewed_at >= '2026-04-24 00:00:00'`. First task in Saturday PM build = export to `tests/fixtures/ai_classifier_ground_truth_24_apr.json` so we have a stable corpus across prompt iterations.

**Success metric:** AI agrees with Chris's verdict on ≥ 85% of high-confidence rows. Review/iterate prompt until we hit that. Track per-iteration agreement rate in a simple log file in `tests/fixtures/`.

**Stretch metric:** ≥ 70% agreement on medium-confidence rows.

**Hard floor:** ≥ 95% agreement on Approves with `pass1_reason = 'service_not_advertised'` AND `pass1_reason_detail` matches a token in `services_not_advertised`. This category should be near-trivial — if AI gets these wrong, prompt is broken.

---

## 9. Feedback loop (2.1g — post-MVP, but prep now)

When Chris accepts / overrides an AI verdict, log it:
- `user_action='accepted'` → positive reinforcement example
- `user_action='overridden'` → negative example for prompt tuning

Weekly: export a sample of overrides, feed back into prompt examples (few-shot learning). No model fine-tuning needed — just better prompts.

---

## 10. Out of scope for MVP

Deferred to later sprints, still in Tier 2.1:
- **2.1c** AI confidence scoring variance by intent tag
- **2.1e** AI-driven target-list assignment for Pass 3 (post-MVP, high value — do next)
- **2.1f** AI intent tagging surfaced in UI beyond the tag column
- **2.1g** Feedback loop (data collected in MVP, action loop built later)
- **2.1h** Cross-client learning (OE → DBD insight transfer)
- **2.1i** AI brand-term auto-detection

Also out of scope:
- Morning Review / Account / Campaign AI touch points (next after Search Terms MVP proves the pattern)
- Long-horizon "daily / weekly / monthly workflow system" per Chris's note (future foundation)

---

## 11. Build order over the weekend

**Saturday PM (~4 hours):**
1. DB migration — create `act_v2_ai_classifications` table
2. Backend — `/v2/api/ai/classify-terms` endpoint scaffolding
3. Prompt template v1 — system + user prompts, stored as code constant
4. Claude Agent SDK integration — subprocess invocation + JSON parsing
5. Dry-run against today's 100-term PMax Review test corpus — measure agreement rate

**Sunday AM (~4 hours):**
6. UI — split-screen layout (65/35) on Search Terms Review page
7. UI — new columns (AI Verdict / Confidence / Reasoning) on the review tables
8. UI — `🤖 AI Triage` button + progress indicator
9. Integration test — click button, see AI column populate

**Sunday PM (~4 hours):**
10. Polish — canned replies library, action buttons per flow
11. QA pass — Chris walks a full triage session end to end
12. Iterate on prompt if agreement rate < 85%

---

## 12. Success criteria for MVP

**Must have (weekend delivery):**
- `/v2/api/ai/classify-terms` works for a 50-term batch in < 20s
- Split-screen UI on Search Terms pages (65/35, resizable, collapsible)
- `🤖 AI Triage` button populates AI verdict/confidence/reasoning columns
- Chris can triage 100 PMax Review terms in < 15 min
- Agreement rate with human verdicts ≥ 85% on high-confidence rows
- All classifications logged to `act_v2_ai_classifications` for later feedback-loop use

**Nice to have (stretch):**
- `Apply high-confidence AI verdicts` one-click button (2.1d extended)
- AI intent tag column surfaced in UI
- Initial canned-reply library with 5–10 presets per flow

---

## 13. The 4 open questions — RESOLVED

### Q1. Agent SDK vs subprocess → **Subprocess (`claude -p --output-format json`)**

**Why:** Dependency-free, trivial error handling (exit code + JSON parse), no Python binding version lock-in. The SDK's value (streaming, multi-turn tool use, file context) is unused for batch classification. Reconsider if we later need streaming progress for huge batches.

**Implementation note:** Build 2 should use Python's `subprocess.run` with `timeout=60`, capture stdout, parse `json.loads(result_field)`. Stdin = the combined prompt. NOT shell=True — pass argv directly to avoid escaping bugs.

### Q2. Prompt hot-reload → **Hot-reload during MVP build, version-lock after**

**Why:** Saturday/Sunday will have rapid prompt iteration. Restart Flask between every prompt change wastes time. After MVP we lock prompt to a `prompt_version` constant in code, increment when we change it, and the `act_v2_ai_classifications.prompt_version` column tracks which prompt classified which row.

**Implementation note:** Prompt lives in `act_dashboard/ai/prompts/search_terms_v1.txt`. Flask reads it at request time (not module import) during MVP. Post-MVP, switch to module-load + version constant.

### Q3. Canned reply library → **Ship a small starter set (4 per flow)**

**Why:** Empty = Chris guesses what's useful. Pre-populated wrong = friction. Starter set based on patterns observed in Friday's actual triage. Chris adds/removes as he goes via a Settings page (post-MVP).

**Starter set per flow:**

**Search > Block / Search > Review:**
- "Approve all veneer/crown/bridge intent rows"
- "Reject finance-intent rows (we offer 0% finance)"
- "Show me only the rows you flagged as Unsure"
- "Explain why row {N} is {verdict}"

**PMax > Block:**
- "Approve all `service_not_advertised` rows"
- "Approve all `location_outside_service_area` rows"
- "Show competitor brand rows"
- "Show non-English-language queries"

**PMax > Review:**
- "Triage first 50 by cost"
- "Reject any rows that already converted"
- "Show me only implant-intent rows you flagged Reject"
- "Group rejects by intent tag"

**Pass 3:**
- "Re-route target list by intent"
- "Flag ambiguous single tokens for human review"
- "Approve all clear location tokens"

### Q4. Model choice → **Opus 4.7 for both batch classify AND explain-row** (revised 25 Apr PM)

**Original decision (24 Apr):** Hybrid — Sonnet 4.6 for batch, Opus 4.7 for explain-row.
**Revised (25 Apr PM):** Use Opus 4.7 for everything. Reasoning:
  - Max plan quota covers both — no cost differentiator
  - ACT's primary value is classification accuracy, not throughput
  - Latency delta (~10-20s per batch) is negligible against Chris's manual 40-min baseline
  - Simpler model surface — one model to iterate prompts against, one set of telemetry

**Implementation:** `classifier.py` constant `MODEL_BATCH = 'claude-opus-4-7'`. Stage 5 explain-row uses the same model.

---

## 14. Privacy / data handling

Search terms occasionally contain partial PII (e.g. patient surnames, location specifics). Mitigations:
- All classification happens locally on Chris's machine via Claude Code (Max plan terms apply — Anthropic's data retention policy for Claude Code applies)
- No PII export beyond what already goes through Claude in Chris's manual triage today
- `act_v2_ai_classifications.search_term` mirrors what's already stored in `act_v2_search_term_reviews` — no new sensitive surface area

Post-MVP if we move to Anthropic API multi-tenant cloud: revisit data processing agreement.

---

## 15. Telemetry and cost tracking

Every classification row writes:
- `tokens_in` + `tokens_out` (extracted from CLI's `usage` block in JSON output)
- `latency_ms` (per-row attribution: `batch_total_ms / row_count`)
- `model_version`
- `prompt_version`

Daily aggregates view (post-MVP, just collect for now):
- Total tokens used per day per client
- % of Max plan quota burned
- p50 / p95 latency per batch
- Agreement rate (where `user_action` is set) per prompt version

This becomes the iteration substrate — "Prompt v3 hit 91% agreement, ship it" type calls.

---

## 16. Rollback plan

If MVP misses the ≥85% agreement target by EOD Sunday:
1. Keep the endpoint + table — no code rollback
2. Hide the `🤖 AI Triage` button behind a feature flag (per-client `ai_triage_enabled` bool in `act_v2_clients`)
3. Continue manual triage as before
4. Iterate on prompt during weekday work without UI exposure
5. Re-enable when agreement rate target hit on the test corpus

This way no built code is wasted; we just don't surface the feature until quality bar is met.

---

**End of original scope.** Resolved + ready for build. Build 2 can start Saturday PM directly from this doc.

---

## 17. Addendum (25 Apr PM — post-replan)

After Tier 1 wrapped, Chris confirmed the FULL Tier 2.1 scope ships this weekend (not a stripped MVP). The previous "out of scope" carve-out in §10 is REVERSED for split-screen, canned replies, and Opus explain-row — all three ship now.

### 17.1 Additional decisions (Q5–Q10)

| # | Question | Decision |
|---|---|---|
| Q5 | Concurrency lock scope | **Per-client.** A `threading.Lock` keyed by `client_id`, shared by `classify-terms` + `explain-row` + `chat`. 409 on contention. |
| Q6 | Skip-if-classified cache | **Skip if `(review_id, prompt_version)` already exists** in `act_v2_ai_classifications`. Re-running with same prompt = no Claude call. Bumping prompt version forces re-classify. `force_reclassify=true` request flag bypasses. |
| Q7 | Agreement metric | **High-confidence subset only.** ≥85% target on rows where `ai_confidence='high'`. Low-confidence will be human-reviewed anyway. (Hard floor in §8 — ≥95% on `service_not_advertised` — stands.) |
| Q8 | Stage order — dry-run vs UI | **Dry-run via curl/Postman BEFORE UI build.** Cheaper to rip out a bad prompt than a UI built around one. |
| Q9 | Chat panel persistence | **New `act_v2_ai_chat_log` table.** Survives restarts, supports feedback loop (§9), provides audit trail. Schema in `docs/TIER_2.1_BUILD_PLAN.md` Stage 1. |
| Q10 | Split-screen UX | **Fixed-width right panel first** (35%, collapsible to 40px strip). Drag-to-resize divider is a stretch goal — only if Stage 8 wraps under budget. |

### 17.2 Schema gap fixes

Two §5.1 changes required in Stage 1:

**(a) `ai_verdict` must be nullable** — Pass 3 rows (flow=`pass3`) have no verdict, only `ai_target_list_role`.
- Change `ai_verdict VARCHAR NOT NULL` → `ai_verdict VARCHAR` (nullable)
- Add: `CHECK ((flow = 'pass3' AND ai_target_list_role IS NOT NULL) OR (flow != 'pass3' AND ai_verdict IS NOT NULL))`

**(b) Source row reference must support both block/review and Pass 3 rows** — original §5.1 only has `review_id` FK to `act_v2_search_term_reviews.id`. Pass 3 phrases live in a different table.
- Change `review_id INTEGER NOT NULL` → `review_id INTEGER` (nullable, FK to `act_v2_search_term_reviews.id`)
- Add `phrase_suggestion_id INTEGER` (nullable, FK to the Pass 3 phrase suggestions table)
- Add: `CHECK ((flow = 'pass3' AND phrase_suggestion_id IS NOT NULL AND review_id IS NULL) OR (flow != 'pass3' AND review_id IS NOT NULL AND phrase_suggestion_id IS NULL))`
- Update UNIQUE constraint to: `UNIQUE (review_id, prompt_version)` AND `UNIQUE (phrase_suggestion_id, prompt_version)` (two partial uniques, one per source type)
- Add index: `CREATE INDEX idx_ai_class_phrase_suggestion_id ON act_v2_ai_classifications(phrase_suggestion_id) WHERE phrase_suggestion_id IS NOT NULL;`

This keeps Pass 3 in the same table cleanly without polymorphic ambiguity. Both columns are queryable.

### 17.3 New endpoints (in addition to §6.1)

- `POST /v2/api/ai/explain-row` — Opus 4.7, single review_id + optional question, longer reasoning, persisted to `act_v2_ai_chat_log` with `related_review_id`.
- `POST /v2/api/ai/chat` — Sonnet 4.6, free-text prompt from chat panel, scoped to current `(client_id, flow, analysis_date)` context, persisted to `act_v2_ai_chat_log`.
- `GET /v2/api/ai/chat-history?client_id&flow&analysis_date` — hydrates the chat panel on page load (last 50 messages, excluding `cleared_at IS NOT NULL`).

### 17.4 New prompt files (in addition to §7)

- `act_dashboard/ai/prompts/explain_row_v1.txt` — Opus system prompt for deep single-row reasoning. Receives full row context (term + cost + keyword + campaign + client config) plus optional user question. Returns 3–5 sentence reasoning, no JSON wrapper required.
- `act_dashboard/ai/prompts/chat_v1.txt` — Sonnet system prompt for the panel chat. Scoped to current flow, has access to the rendered review table as context. Free-text in, free-text out (no JSON).

### 17.5 Canned reply types (clarification)

Canned replies are NOT all chat invocations. Two types:
- `{type: 'chat', text: '...'}` → pre-fills chat input, auto-submits to `/v2/api/ai/chat`
- `{type: 'filter', action: {column, value}}` → manipulates the main-table filter, no Claude call

Examples:
- "Show only unsure" → `filter` (no Claude call, just sets `ai_verdict='unsure'` filter)
- "Approve all veneer/crown/bridge intent" → `chat` (asks AI to identify, then user clicks Apply)

### 17.6 Confirmed split-screen scope (overrides §10 deferral)

§10 listed "Morning Review / Account / Campaign AI touch points" as out of scope — **still true for those pages**. The split-screen panel ships ONLY on:
- Pass 1/2 Search Term Review (Search > Block + Search > Review flows)
- PMax Search Term Review (PMax > Block + PMax > Review flows)
- Pass 3 Phrase Suggestions

Not on Morning Review, Account Level, or Campaign Level — those remain out of scope until Tier 2.2+.

---

**End of addendum. Plan + scope are now consistent. Build 2 starts at Stage 0 (fixture export).**
