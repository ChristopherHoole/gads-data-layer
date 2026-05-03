# Build brief — 2.1e AI Pass 3 (Sun 3 May 2026)

**For:** ACT Build session
**From:** PM session
**Source spec:** `docs/SCOPE_2.1e_AI_PASS_3.md`
**Effort:** 6–8h
**Goal:** replace the rule-based Pass 3 fragment generator with an AI pass that runs on the **full day's** Search+PMax dataset, returns ranked fragments + target-list assignments + a theme summary.

---

## Pre-resolved open questions (from scope §11)

| # | Question | Decision |
|---|---|---|
| 1 | Table name for current Pass 3 suggestions | **`act_v2_phrase_suggestions`** (existing). Reuse it. |
| 2 | Current rule-based generator location | **`act_dashboard/engine/negatives/pass3.py`** — leave intact as fallback (gated by debug flag) |
| 3 | Themes storage | **Separate table** `act_v2_pass3_themes`. Keyed by `client_id + snapshot_date`. Cols: `id, client_id, snapshot_date, theme_text, created_at` |
| 4 | Re-rank Pass 1+2? | **No.** Strictly downstream. Single concern per pass. |

---

## Pre-flight constraints

- **Don't overwrite** `act_dashboard/ai/prompts/search_terms_pass3_v1.txt` (it's the existing router prompt). New file = `search_terms_pass3_v2.txt`.
- **Don't delete** `pass3.py` rule-based engine. Add a feature flag: env var `ACT_PASS3_ENGINE` = `ai` (default new) or `rules` (fallback).
- **Auth:** reuse `CLAUDE_CODE_OAUTH_TOKEN` env var that Pass 1+2 already use.
- **Mirror** structure of existing AI Triage (`act_dashboard/ai/classifier.py` + prompt loaders). Don't reinvent.

---

## Architecture

**New module:** `act_dashboard/engine/pass3_ai.py`

**New endpoint:** `POST /v2/api/search-terms/run-pass3-ai`
- Replaces what "Run Pass 3" button currently calls
- Accepts: `{ client_id, snapshot_date }`
- Returns: `{ fragments: [...], themes: [...], cost_usd, tokens_in, tokens_out }`

**Storage:**
- Fragments → existing `act_v2_phrase_suggestions` (add cols if needed: `confidence DOUBLE`, `rationale TEXT`, `theme_id INTEGER NULL`, `source_count INTEGER`)
- Themes → new `act_v2_pass3_themes`

**UI (existing Search Term Review Pass 3 tab):**
- Add **Theme banner** at top of tab (queries `act_v2_pass3_themes` for current client+date, joins multiple themes with `<br><br>`)
- Existing fragment table renders unchanged. If migrating columns, surface `confidence` + `rationale` in tooltips.
- Push button mechanics unchanged.

---

## AI inputs (single Claude API call per client per day)

> **Pass 3 input = ALL search terms for the snapshot_date, regardless of their Pass 1/2 status. Pass 3 must NOT depend on Pass 1/2 having run. The `review_status` field is read for anti-duplicate context only — never used as a filter on which terms to consider.**

**Today's data:**
```sql
SELECT search_term, campaign_type, cost, clicks, impressions, conversions, match_type,
       review_status  -- pushed / didnt_block / pending / sticky_rejected (CONTEXT ONLY, NOT A FILTER)
FROM act_v2_search_terms
WHERE client_id = ? AND snapshot_date = ?
```

**Client profile:** load from `act_v2_client_settings`:
- `services_advertised`
- `rule_7_exclude_tokens`
- `services_not_advertised` (if present)
- Locations targeted (or inverse if exclusion-based — confirm from settings schema)

**Negative-list schema (per client):** load list names from existing schema so AI uses real list names not invented ones.

**History (anti-duplicate):**
- Yesterday's pushed Pass 3 fragments (`act_v2_phrase_suggestions WHERE review_status='pushed' AND snapshot_date = today-1`)
- All sticky-rejected fragments
- Last 30 days of pushed neg keywords (any list)

---

## AI output JSON

```json
{
  "themes": [
    "Cluster of sedation/anxiety queries today — 12 search terms reference sedation, IV sedation, sleep dentistry. Client doesn't offer sedation. Recommend pushing 'sedation' to Off Not Adv as priority.",
    "Increased finance-related queries (15 today vs 4 last week). Client offers 0% finance — these should NOT be blocked."
  ],
  "fragments": [
    {
      "fragment": "sedation",
      "words": 1,
      "target_list": "Off Not Adv \"ph\"",
      "confidence": 0.92,
      "occurrence_count": 8,
      "source_terms": ["sedation dental implants", "sleep dentistry sedation"],
      "rationale": "Sedation is in client's rule_7_exclude_tokens (service not offered). 8 occurrences across Search + PMax today. High-confidence off-not-advertised block.",
      "risk": "low"
    }
  ]
}
```

Validation: target_list must match a real list name in client's neg-list schema (validate in `pass3_ai.py` before insert).

---

## Ranking + filtering rules (encoded in system prompt)

1. **Stopword filter** — drop articles/conjunctions/modals/pronouns from candidates: `the, a, an, can, could, should, would, will, you, I, my, your, our, get, for, with, on, in, at, of, to, from, and, or, but, is, are, was, were, be, been, do, does, did, have, has, had, near, me`.
2. **Information-value ranking** — content tokens (nouns, services, locations, brands) outrank function words.
3. **Off-not-advertised priority** — 1-word fragments matching `rule_7_exclude_tokens` or `services_not_advertised` → route to `Off Not Adv` with confidence ≥ 0.85.
4. **Location detection** — UK city/town/region match → `Loc N word` target, confidence ≥ 0.80.
5. **Volume floor** — aim 20–50 fragments per 100 pushed terms (proportional). Empty list if no defensible fragments — no padding.
6. **Sticky-rejection respect** — never re-suggest rejected fragments.
7. **No high-intent blocks** — fragment must not match any client keyword or `services_advertised` token.

---

## Pause-gate brief pattern (REQUIRED — do not skip)

- **Pause 1:** confirm understanding of inputs/outputs/architecture before writing code. Show structural plan back to PM.
- **Pause 2:** show the v2 system prompt + a sample AI response on **DBD 2026-04-28** dataset before wiring to UI.
- **Pause 3:** show one full end-to-end run before pushing.

---

## Migration / housekeeping

1. Add columns to `act_v2_phrase_suggestions` if not present: `confidence`, `rationale`, `theme_id`, `source_count`. Migration `n8` (or next number).
2. Create `act_v2_pass3_themes` table.
3. Wipe DBD's 7 junk fragments before live test:
   ```sql
   DELETE FROM act_v2_phrase_suggestions
   WHERE client_id='dbd001' AND snapshot_date='2026-04-28' AND review_status='pending';
   ```
4. No new env var.

---

## Testing

**Unit:** fragment-shape validation, JSON schema check, target-list name validation.

**Integration on DBD 2026-04-28** dataset (already in DB). Expected:
- `sedation` → Off Not Adv ph, confidence ≥ 0.85 ✓
- `flipper` → Off Not Adv ph, confidence ≥ 0.85 ✓
- `fillings` → Off Not Adv ph, confidence ≥ 0.85 ✓
- `crewe` → Loc 1 word ph, confidence ≥ 0.80 ✓
- Zero stopword fragments (no `can`, `you`, `get`)
- 20–40 fragments total
- ≥ 1 theme surfaced

**Live test:** DBD 2026-05-03 (today's data) once shipped.

---

## Cost guardrails

- ~25–30k input tokens / call
- ~5–10k output tokens
- ~$0.10–0.15 per client per day
- Negligible at any client volume

---

## Out of scope

- Multi-day / weekly Pass 3
- Auto-push (keep human-in-loop)
- Cross-client learning
- Unified Pass 1+2+3 single-pass call

---

## Done = shippable when

- [ ] `pass3_ai.py` module exists, mirrors `classifier.py` structure
- [ ] `search_terms_pass3_v2.txt` prompt encodes all 7 rules + JSON output schema
- [ ] Migration adds `confidence/rationale/theme_id/source_count` cols + new themes table
- [ ] `POST /v2/api/search-terms/run-pass3-ai` endpoint works end-to-end
- [ ] UI renders theme banner + existing fragment table
- [ ] Integration test on DBD 2026-04-28 returns expected fragments
- [ ] Live test on DBD 2026-05-03 surfaces fresh fragments + theme
- [ ] Old rule-based engine still callable via `ACT_PASS3_ENGINE=rules` env var
- [ ] Commit pushed to `origin/main` with clean commit message
