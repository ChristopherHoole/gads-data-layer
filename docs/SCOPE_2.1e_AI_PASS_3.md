# SCOPE 2.1e — AI-Driven Pass 3 (full-dataset n-gram routing)

**Status:** drafted 2026-04-29. Build target: Sunday 3 May 2026.
**Owner:** ACT Build session.
**Estimated effort:** 6–8h.
**Supersedes:** the rule-based fragment generator currently behind the "Run Pass 3" button.

---

## 1. Why we're rebuilding this

Pass 3 today is a rule-based n-gram generator over **only the day's pushed terms**. Tested on DBD 2026-04-28 with 122 pushed terms it produced **7 fragments**, of which:

- 5 were stopword junk (`can`, `can you`, `you get`, `can you get`, `can you get veneers`)
- 1 was location-mis-routed (`crewe` → generic `1 WRD ph` instead of `Loc 1 word ph`)
- 1 was acceptable (`you get veneers` → `Off Not Adv ph`)

Real off-not-advertised tokens visible in the day's data — `sedation`, `flipper`, `fillings` — were missed entirely.

Root causes:
- No stopword filter
- No information-value ranking (frequency-only)
- No location intent detection
- No service-not-offered detection
- Looks only at pushed terms, not the full day's dataset (so themes only emerge after manual blocking, defeating the point)

## 2. What changes

Pass 3 becomes an **AI pass**, run **after Pass 1+2 are complete for the day**, fed the **full day's search-term dataset across Search + PMax** (not just pushed terms).

The AI's job: pattern-detect across all of today's queries, propose n-gram fragments, route each fragment to the correct target negative list, return a confidence score and rationale.

Human still approves before push (existing UI flow stays).

## 3. Inputs to the AI call

Single Claude API call per client per day. Inputs:

**Today's data:**
- All Search + PMax search-term rows for the snapshot_date being processed (`act_v2_search_terms WHERE client_id = ? AND snapshot_date = ?`). Columns needed: `search_term`, `campaign_type`, `cost`, `clicks`, `impressions`, `conversions`, `match_type`.
- The day's Pass 1+2 outcomes per term: `pushed` / `didnt_block` / `pending` / `sticky_rejected`. (Already in `act_v2_search_terms` or related table — confirm during build.)

**Client profile (for context the AI uses to route correctly):**
- `services_advertised` (list of services the client actually offers)
- `rule_7_exclude_tokens` (off-not-advertised token list)
- `services_not_advertised` (inverse of services_advertised, if maintained)
- Location list — UK cities/towns/regions the client targets (or its inverse if exclusion-based)
- The client's full neg-list schema with target list names: e.g. `1 WRD "ph"`, `2 WRDS "ph"`, `3 WRDS "ph"`, `Loc 1 word "ph"`, `Loc 2 word "ph"`, `Off Not Adv "ph"`, plus any client-specific lists

**History (so AI doesn't re-suggest):**
- Yesterday's Pass 3 fragments that were pushed (don't suggest again)
- All sticky-rejected fragments (don't suggest again)
- Last 30 days of pushed neg keywords across all lists (avoid duplicates)

## 4. Output the AI returns

JSON. One object per fragment:

```json
[
  {
    "fragment": "sedation",
    "words": 1,
    "target_list": "Off Not Adv \"ph\"",
    "confidence": 0.92,
    "occurrence_count": 8,
    "source_terms": ["sedation dental implants", "sleep dentistry sedation", ...],
    "rationale": "Sedation is in client's rule_7_exclude_tokens (service not offered). 8 occurrences across Search + PMax today. High-confidence off-not-advertised block.",
    "risk": "low"
  },
  {
    "fragment": "crewe",
    "words": 1,
    "target_list": "Loc 1 word \"ph\"",
    "confidence": 0.88,
    "occurrence_count": 1,
    "source_terms": ["dental implants crewe"],
    "rationale": "Crewe is a UK town outside the client's targeted locations (Hammersmith). Route to Loc 1 word list.",
    "risk": "medium"
  }
]
```

Plus a top-level theme summary:

```json
{
  "themes": [
    "Cluster of sedation/anxiety queries today — 12 search terms reference sedation, IV sedation, sleep dentistry. Client doesn't offer sedation. Recommend pushing 'sedation' to Off Not Adv as priority.",
    "Increased finance-related queries (15 today vs 4 last week). Client offers 0% finance — these should NOT be blocked."
  ],
  "fragments": [...as above...]
}
```

## 5. Ranking + filtering rules the AI must apply

Encoded in the system prompt:

1. **Stopword filter** — drop articles, conjunctions, modals, pronouns from candidate fragments before ranking. List: `the, a, an, can, could, should, would, will, you, I, my, your, our, get, for, with, on, in, at, of, to, from, and, or, but, is, are, was, were, be, been, do, does, did, have, has, had, near, me`.
2. **Information-value ranking** — content tokens (nouns, service names, locations, brands) outrank function words. AI's natural language understanding handles this implicitly; the prompt should tell it to ignore stopwords and rank by signal.
3. **Off-not-advertised priority** — any 1-word fragment matching `rule_7_exclude_tokens` or `services_not_advertised` → must route to `Off Not Adv` target with confidence ≥ 0.85.
4. **Location detection** — UK city/town/region match → must route to `Loc N word` target. Confidence ≥ 0.80.
5. **Volume floor** — aim for 20–50 fragments per 100 pushed terms (proportional to dataset size). Output empty list if no defensible fragments rather than padding with junk.
6. **Sticky-rejection respect** — never re-suggest a fragment that's been rejected before.
7. **No pushing high-intent terms** — fragment must not match any existing client keyword or any term in services_advertised.

## 6. Architecture / where it sits

**File:** new module `act_dashboard/engine/pass3_ai.py`. Mirrors the structure of existing AI Triage in Pass 1+2 (`act_dashboard/engine/ai_triage.py` — confirm path during build).

**Trigger:** "Run Pass 3" button in the Search Term Review UI calls a new endpoint `POST /v2/api/search-terms/run-pass3-ai` (replacing whatever the current rule-based endpoint is).

**Auth:** uses the same `CLAUDE_CODE_OAUTH_TOKEN` env var that Pass 1+2 already use.

**Storage:** AI-returned fragments land in the existing `act_v2_pass3_suggestions` table (or whatever it's called — verify during build). Add columns if needed: `confidence`, `rationale`, `theme_id`, `source_count`. Themes go in a new sibling table `act_v2_pass3_themes` keyed by client_id + snapshot_date.

**UI:** the Pass 3 Suggestions tab renders the same way it does today (Fragment / Words / Target list / Risk / Status / Source terms columns), plus a new **Theme banner** at the top of the tab showing the AI's pattern summary. Push button mechanics unchanged.

## 7. Migration / one-time housekeeping

1. Don't delete the existing rule-based engine — leave it as a fallback. New AI endpoint is the default; rule-based stays callable via a debug flag.
2. Wipe today's 7 junk fragments before going live: `DELETE FROM act_v2_pass3_suggestions WHERE client_id='dbd001' AND snapshot_date='2026-04-28' AND status='pending'`.
3. New env var? No — reuses `CLAUDE_CODE_OAUTH_TOKEN`.

## 8. Testing

**Unit:** fragment-shape validation, JSON schema check on AI response, target-list-name validation against client's neg-list schema.

**Integration:** run on DBD 2026-04-28 dataset (already in DB). Expected outcomes:
- `sedation` → Off Not Adv ph, confidence ≥ 0.85
- `flipper` → Off Not Adv ph, confidence ≥ 0.85
- `fillings` → Off Not Adv ph, confidence ≥ 0.85
- `crewe` → Loc 1 word ph, confidence ≥ 0.80
- Zero stopword fragments (no `can`, `you`, `get`, etc.)
- 20–40 fragments total (vs today's 7)
- At least 1 theme surfaced

**Live test on:** DBD 2026-05-03 (Sunday's data) once shipped.

## 9. Pause-gate brief pattern (for Sunday's build)

- **Pause 1:** confirm understanding of inputs/outputs/architecture before writing any code.
- **Pause 2:** show the system prompt + a sample AI response on DBD 2026-04-28 data before wiring it to the UI.
- **Pause 3:** show one full end-to-end run before pushing.

## 10. Cost estimate

- ~25–30k input tokens per call (full day's search terms + client profile + history)
- ~5–10k output tokens (20–50 fragments + themes + rationales)
- ~$0.10–0.15 per client per day at current Claude API pricing
- Negligible at any client volume

## 11. Open questions to resolve at start of Sunday session

1. Confirm the table name for current Pass 3 suggestions (`act_v2_pass3_suggestions` or similar).
2. Confirm the file path of the current rule-based generator so we can leave it intact as fallback.
3. Decide: themes table separate, or themes inlined in suggestions table as JSON column?
4. Decide: does AI also re-rank Pass 1+2 outcomes or stay strictly downstream? (Recommendation: strictly downstream for now — single concern per pass.)

## 12. Out of scope (defer)

- Multi-day / weekly Pass 3 (today's scope = daily only)
- Auto-push without human approval (keep human-in-loop)
- Cross-client learning (each client gets own context, no shared model state)
- Replacing Pass 1+2 AI with a unified single-pass call (separate future scope)
