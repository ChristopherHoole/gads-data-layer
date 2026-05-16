"""KW + Search Term History — mapping pipeline (Phase 2).

Brief: docs/BRIEF_KW_ST_HISTORY_VIEWER.md

Fail-fast, cheapest-first chain that fills kw_st_history mapping
columns for every eligible row:

    skip_brand   →  is_brand_campaign = TRUE
    (mapped)     →  in_new_ex         = TRUE   (no proposal needed)
    skip_low_vol →  impressions < 5 AND clicks = 0
    rule         →  substring-match an anchor; pick CORE/COST/LOCATION
                    sub-group from intent tokens
    ai           →  Sonnet 4.6 for everything rule can't map

AI cost controls:
    - Dedupe is already done at ingest (one row per term).
    - Skip low-volume before AI.
    - Batch 50 unique terms per Sonnet call.
    - Cache via kw_st_history.ai_cached_at — re-runs skip cached rows
      unless run with force=True.
    - HARD CAP: if estimated AI-eligible volume > AI_HARD_CAP (5000)
      after rule pass, the pipeline halts BEFORE issuing any API call
      and returns {'overall': 'halted'} so Chris can review.

DBD-only for v1 via ALLOWED_CLIENTS_V1.
"""
from __future__ import annotations

import json
import logging
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import duckdb

from act_dashboard.ai import claude_subprocess

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
DB_PATH = os.path.join(PROJECT_ROOT, 'warehouse.duckdb')
LOG_PATH = SCRIPT_DIR / 'kw_history_mapping.log'

ALLOWED_CLIENTS_V1 = {'dbd001'}

# Per the brief: Sonnet (NOT Haiku). Mapping accuracy matters because
# Chris will act on the suggestions.
MODEL_MAPPING_AI = 'claude-sonnet-4-6'
AI_BATCH_SIZE = 50
AI_TIMEOUT_S = 300  # 50-term batch is a heavier prompt; 5-min ceiling
AI_HARD_CAP = 5000  # halt-and-surface before any call if exceeded

# Pricing (USD per million tokens) — Sonnet 4.6 list price at time of
# build (16 May 2026). Used to estimate run cost in the report.
SONNET_INPUT_PER_MTOK_USD = 3.0
SONNET_OUTPUT_PER_MTOK_USD = 15.0
USD_TO_GBP = 0.79

# Campaigns folder — the canonical parent-theme directory tree.
CAMPAIGNS_DIR = (
    PROJECT_ROOT / 'potential_clients' / 'Inserta Dental' / 'Campaigns'
)


logger = logging.getLogger('kw_history_mapping')
logger.setLevel(logging.INFO)
_fmt = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
if not logger.handlers:
    sh = logging.StreamHandler(sys.stdout); sh.setFormatter(_fmt); logger.addHandler(sh)
    try:
        fh = logging.FileHandler(LOG_PATH, mode='a', encoding='utf-8')
        fh.setFormatter(_fmt); logger.addHandler(fh)
    except OSError:
        pass


# ---------------------------------------------------------------------------
# Rule-pass static data
# ---------------------------------------------------------------------------
# (anchor_lower, parent_display)
# Longest patterns first so "dental implants" beats "implant".
# parent_display is the parent slug used in live [ex]/[*] ad-group names.
ANCHORS: list[tuple[str, str]] = [
    ('implants for elderly', 'Implants for Elderly'),
    ('senior dental implant', 'Implants for Elderly'),
    ('elderly dental implant', 'Implants for Elderly'),
    ('dentures to implants', 'Dentures to Implants'),
    ('dental reconstruction', 'Dental Reconstruction'),
    ('full mouth reconstruction', 'Dental Reconstruction'),
    ('mouth reconstruction', 'Dental Reconstruction'),
    ('affordable dental implant', 'Affordable Implants'),
    ('cheap dental implant', 'Affordable Implants'),
    ('molar replacement', 'Molar Replacement'),
    ('molar implant', 'Molar Replacement'),
    ('missing tooth replacement', 'Missing Teeth'),
    ('missing teeth replacement', 'Missing Teeth'),
    ('missing teeth', 'Missing Teeth'),
    ('missing tooth', 'Missing Teeth'),
    ('tooth replacement', 'Tooth Replacement'),
    ('teeth replacement', 'Teeth Replacement'),
    ('best dental implants', 'Best Dental Implants'),
    ('best dental implant', 'Best Dental Implants'),
    ('dental implant clinic', 'Implant Clinic'),
    ('implant clinic', 'Implant Clinic'),
    ('dental implant specialist', 'Implant Specialist'),
    ('implant specialist', 'Implant Specialist'),
    ('dental implant surgeon', 'Implant Surgeon'),
    ('implant surgeon', 'Implant Surgeon'),
    ('dental implant dentist', 'Implant Dentist'),
    ('implant dentist', 'Implant Dentist'),
    ('dental implant', 'Dental Implants'),
    ('dental implants', 'Dental Implants'),
    ('teeth implants', 'Teeth Implants'),
    ('teeth implant', 'Teeth Implants'),
    ('tooth implants', 'Tooth Implant'),
    ('tooth implant', 'Tooth Implant'),
    ('all on 4 dental implants', 'All on 4'),
    ('all on 4', 'All on 4'),
    ('all-on-4', 'All on 4'),
    ('all on four', 'All on 4'),
    ('all-on-four', 'All on 4'),
    ('all on 6', 'All on 6'),
    ('all-on-6', 'All on 6'),
    ('all on six', 'All on 6'),
    ('all-on-six', 'All on 6'),
    ('full mouth dental implants', 'Full Mouth'),
    ('full mouth implants', 'Full Mouth'),
    ('full mouth', 'Full Mouth'),
    ('full set of teeth', 'Full/Complete Set'),
    ('full set teeth', 'Full/Complete Set'),
    ('complete set of teeth', 'Full/Complete Set'),
    ('full arch', 'Full Arch'),
    ('single arch', 'Single Arch'),
    ('double arch', 'Double Arch'),
    ('upper jaw', 'Upper Jaw'),
    ('lower jaw', 'Lower Jaw'),
    ('new teeth in a day', 'Same Day Teeth'),
    ('same day teeth', 'Same Day Teeth'),
    ('same day implants', 'Same Day Teeth'),
    ('teeth in a day', 'Same Day Teeth'),
    ('new teeth', 'New Teeth'),
    ('screwless', 'Screwless'),
    ('screw-less', 'Screwless'),
    ('vivo bridge', 'Vivo Bridge'),
    ('permanent teeth', 'Permanent Teeth'),
    ('fixed teeth', 'Fixed Teeth'),
    ('smile in a day', 'Smile'),
    ('smile makeover', 'Smile'),
    ('fix my teeth', 'Fix My Teeth'),
    ('fix teeth', 'Fix My Teeth'),
    ('implant + bridge', 'Implant + Bridge'),
    ('implant bridge', 'Implant + Bridge'),
    ('bone graft', 'Bone Graft'),
    ('failed implant', 'Implant Replacement'),
    ('replace implant', 'Implant Replacement'),
    ('implant replacement', 'Implant Replacement'),
    ('nhs dental implant', 'NHS Implants'),
    ('nhs implant', 'NHS Implants'),
]

# Sort longest-first so multi-word anchors win over single-word.
ANCHORS = sorted(ANCHORS, key=lambda x: -len(x[0]))

# Intent tokens → sub-group label. Checked in priority order.
INTENT_TOKENS: list[tuple[str, str]] = [
    # Sub-group COST signals (price, finance, affordability)
    ('finance', 'FINANCE'),
    ('payment plan', 'FINANCE'),
    ('monthly payment', 'FINANCE'),
    ('on finance', 'FINANCE'),
    ('£', 'COST'),
    ('cost', 'COST'),
    ('price', 'COST'),
    ('prices', 'COST'),
    ('cheap', 'COST'),
    ('affordable', 'COST'),
    ('how much', 'COST'),
    # Sub-group LOCATION
    ('near me', 'LOCATION'),
    ('london', 'LOCATION'),
    ('manchester', 'LOCATION'),
    ('birmingham', 'LOCATION'),
    ('liverpool', 'LOCATION'),
    ('bristol', 'LOCATION'),
    ('leeds', 'LOCATION'),
    ('sheffield', 'LOCATION'),
    ('glasgow', 'LOCATION'),
    ('edinburgh', 'LOCATION'),
    ('cardiff', 'LOCATION'),
    ('uk', 'LOCATION'),
    # Sub-group NHS
    ('nhs', 'NHS'),
    # Sub-group INFO
    ('how long', 'INFO'),
    ('how does', 'INFO'),
    ('what is', 'INFO'),
    ('procedure', 'INFO'),
    ('recovery', 'INFO'),
]


def _detect_subgroup(term: str) -> str:
    """Return CORE / COST / LOCATION / NHS / FINANCE / INFO."""
    t = term.lower()
    for token, sub in INTENT_TOKENS:
        if token in t:
            return sub
    return 'CORE'


def _propose_via_rule(term: str, live_ad_groups: set[str]
                      ) -> tuple[str | None, str | None]:
    """Return (proposed_ad_group, rationale) or (None, None) if no rule
    matched. Tries each anchor in order; the FIRST match wins."""
    for anchor, parent in ANCHORS:
        if anchor in term:
            sub = _detect_subgroup(term)
            # Try `[*]` and `[ex]` prefixes. Pick the one that exists in
            # the live set; fall back to `[*]` if neither variant exists
            # yet (signal to Chris that the ad group may need creating).
            candidates = [
                f"[*] {parent} - {sub}",
                f"[ex] {parent} - {sub}",
                # Fallback to CORE if intent-sub doesn't match a real group.
                f"[*] {parent} - CORE",
                f"[ex] {parent} - CORE",
            ]
            for c in candidates:
                if c in live_ad_groups:
                    rationale = (f"anchor '{anchor}' -> parent '{parent}'; "
                                 f"sub '{sub}' (rule)")
                    return c, rationale
            # No live variant — propose the most specific one anyway.
            rationale = (f"anchor '{anchor}' -> parent '{parent}'; "
                         f"sub '{sub}' (rule, ad group may need creating)")
            return candidates[0], rationale
    return None, None


# ---------------------------------------------------------------------------
# Campaigns/ folder tree → parent-theme list (for AI prompt grounding)
# ---------------------------------------------------------------------------
def parse_campaigns_themes() -> list[str]:
    """Return the list of parent-theme names from Campaigns/ folder tree.

    Folders matching `^\\d+_` are canonical parents. `[on hold]` and
    underscored helper folders are skipped. The folder name is converted
    to display form (underscores → spaces, `+` stays literal).
    """
    if not CAMPAIGNS_DIR.exists():
        logger.warning('Campaigns folder missing: %s', CAMPAIGNS_DIR)
        return []
    themes: list[str] = []
    for entry in sorted(CAMPAIGNS_DIR.iterdir()):
        if not entry.is_dir():
            continue
        name = entry.name
        if name.startswith('_') or name.startswith('.'):
            continue
        if name.startswith('[on hold]') or 'on hold' in name.lower():
            continue
        m = re.match(r'^(\d+)_(.+)$', name)
        if not m:
            # Non-numbered folder (e.g. "Near Me - All Implants") — keep
            # the literal display name minus the numeric prefix.
            display = name.replace('_', ' ').strip()
        else:
            display = m.group(2).replace('_', ' ').strip()
        themes.append(display)
    return themes


# ---------------------------------------------------------------------------
# Sonnet call wrapper
# ---------------------------------------------------------------------------
SYSTEM_PROMPT_TEMPLATE = """You are an expert Google Ads strategist for Dental \
By Design (a UK private dental implant clinic).

Your job: for a batch of search terms, propose the best target ad group from \
the clinic's existing [ex] structure (Dental Implants Intent campaign). Each \
[ex] ad group is a (parent theme) x (sub-group). Sub-groups: CORE, COST, \
LOCATION, NHS, FINANCE, INFO.

PARENT THEMES (only these are valid for new mappings; pick the closest fit):
{themes_list}

LIVE [ex] AD GROUPS (these already exist — prefer these exact names):
{live_ad_groups}

RULES
- Output exactly one JSON object per input term. Use the term verbatim as the key.
- The value is `{{"ad_group": "<name>", "rationale": "<one short sentence>"}}`.
- Preferred: pick an existing live [ex] ad group from the list above. Use the \
exact string verbatim, including the `[*]` or `[ex]` prefix.
- If no existing ad group fits, propose `NEW: <Parent Theme> - <SUB>` using a \
parent theme from the list. Sub must be one of CORE / COST / LOCATION / NHS / \
FINANCE / INFO.
- Sub-group rules: COST = terms with cost/price/cheap/affordable/£/finance; \
LOCATION = city names + "near me" + "uk"; NHS = explicit nhs mention; \
FINANCE = payment plan / monthly payment / "on finance"; INFO = recovery / \
"how long" / "what is" / procedure questions; CORE = everything else.
- Do NOT propose new sub-groups. Do NOT invent parent themes.
- One rationale sentence, max 80 chars, no em-dashes (hyphens only).

OUTPUT
Return ONE JSON object whose top-level keys are the input terms, in the same \
order they were given. Example:
{{"dental implant cost london": {{"ad_group": "[*] Dental Implants - COST", \
"rationale": "cost intent + london; matches live COST group"}}}}

FEW-SHOT EXAMPLES
{{"affordable dental implants uk": {{"ad_group": "[ex] Affordable Implants - LOCATION", \
"rationale": "affordable + uk -> Affordable Implants LOCATION"}}}}
{{"how long does a dental implant procedure take": {{"ad_group": "[*] Dental Implants - INFO", \
"rationale": "informational -> Dental Implants INFO"}}}}
{{"nhs implants for over 60s": {{"ad_group": "[ex] NHS Implants - CORE", \
"rationale": "nhs + general -> NHS Implants CORE"}}}}

No prose. No markdown. JSON ONLY.
"""


def _build_system_prompt(themes: list[str], live_ad_groups: list[str]) -> str:
    themes_block = '\n'.join(f"- {t}" for t in themes) or '(none)'
    # Cap live ad-group list so the prompt stays bounded; Sonnet's 200k
    # context easily covers it, but the cleaner the list the better.
    live_block = '\n'.join(f"- {g}" for g in sorted(live_ad_groups)) or '(none)'
    return SYSTEM_PROMPT_TEMPLATE.format(
        themes_list=themes_block,
        live_ad_groups=live_block,
    )


def _build_user_message(terms: list[str]) -> str:
    lines = ['Map each of these search terms:']
    for t in terms:
        lines.append(f"- {t}")
    return '\n'.join(lines)


def _parse_ai_response(raw: str) -> dict[str, dict]:
    """Sonnet sometimes wraps JSON in prose / code fences. Strip both."""
    raw = raw.strip()
    # Strip ```json fences if present.
    if raw.startswith('```'):
        raw = re.sub(r'^```(?:json)?\s*', '', raw)
        raw = re.sub(r'\s*```$', '', raw)
    # If extra prose precedes the JSON, find the first `{` and last `}`.
    if not raw.startswith('{'):
        i = raw.find('{')
        j = raw.rfind('}')
        if i >= 0 and j > i:
            raw = raw[i:j+1]
    return json.loads(raw)


def _ai_map_batch(terms: list[str], system_prompt: str
                  ) -> tuple[dict[str, dict], dict, int]:
    """Send one batch to Sonnet. Returns (mapping, usage, wall_ms)."""
    user_msg = _build_user_message(terms)
    result_text, usage, wall_ms = claude_subprocess.run_claude(
        MODEL_MAPPING_AI, system_prompt, user_msg, timeout_s=AI_TIMEOUT_S)
    mapping = _parse_ai_response(result_text)
    return mapping, usage, wall_ms


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------
def run_mapping(client_id: str, force: bool = False,
                top_n: int | None = None) -> dict:
    """Run the full skip_brand -> exact -> rule -> AI chain.

    force=False: AI-cached rows are NOT re-sent. Eligible AI rows that
    already have ai_cached_at set are skipped.
    force=True: re-process every eligible row regardless of cache.

    top_n: if set, cap AI volume to the top-N highest-click eligible
    rows (rest stay unmapped). Useful when the long tail blows past
    AI_HARD_CAP — Chris's explicit override per the brief's "halt and
    surface for review" guidance. When None, the AI_HARD_CAP halts the
    pipeline before any API call.

    Returns a summary dict with phase counts + AI cost report.
    """
    if client_id not in ALLOWED_CLIENTS_V1:
        logger.info('skipped (not in v1 allowlist): client=%s', client_id)
        return {'overall': 'skipped',
                'reason': f'{client_id!r} not in v1 allowlist'}

    summary = {
        'client_id': client_id, 'started_at': datetime.now().isoformat(timespec='seconds'),
        'skip_brand': 0, 'mapped_in_ex': 0,
        'skip_low_volume': 0,
        'rule_mapped': 0,
        'ai_sent': 0, 'ai_mapped': 0, 'ai_cached_skipped': 0,
        'ai_batches': 0, 'ai_tokens_in': 0, 'ai_tokens_out': 0,
        'ai_cost_usd': 0.0, 'ai_cost_gbp': 0.0,
        'ai_wall_clock_ms': 0,
    }

    con = duckdb.connect(DB_PATH)
    try:
        # ----- 1. skip_brand: brand-campaign rows get a 'skip_brand' tag.
        n = con.execute(
            """UPDATE kw_st_history
               SET proposal_method = 'skip_brand',
                   proposed_ad_group = NULL,
                   proposal_rationale = 'brand campaign — never block / map',
                   last_updated = CURRENT_TIMESTAMP
               WHERE client_id = ?
                 AND is_brand_campaign = TRUE
                 AND (proposal_method IS NULL
                      OR proposal_method NOT IN ('manual'))""",
            [client_id],
        ).fetchone()
        summary['skip_brand'] = int(n[0]) if n else 0
        logger.info('skip_brand: %d rows tagged', summary['skip_brand'])

        # ----- 2. mapped (in_new_ex=TRUE): nothing to propose; leave method NULL.
        summary['mapped_in_ex'] = int(con.execute(
            "SELECT COUNT(*) FROM kw_st_history "
            "WHERE client_id = ? AND in_new_ex = TRUE",
            [client_id],
        ).fetchone()[0])

        # ----- 3. skip_low_volume: impressions < 5 AND clicks = 0 (and not mapped/brand).
        n = con.execute(
            """UPDATE kw_st_history
               SET proposal_method = 'skip_low_volume',
                   proposed_ad_group = NULL,
                   proposal_rationale = 'low-volume; not worth proposing',
                   last_updated = CURRENT_TIMESTAMP
               WHERE client_id = ?
                 AND in_new_ex = FALSE
                 AND is_brand_campaign = FALSE
                 AND impressions_total < 5
                 AND clicks_total = 0
                 AND (proposal_method IS NULL
                      OR proposal_method NOT IN ('manual'))""",
            [client_id],
        ).fetchone()
        summary['skip_low_volume'] = int(n[0]) if n else 0
        logger.info('skip_low_volume: %d rows tagged',
                    summary['skip_low_volume'])

        # ----- 4. Build live ad-group set (used by rule + AI).
        live_ad_groups = {
            r[0] for r in con.execute(
                "SELECT DISTINCT current_new_ex_ad_group FROM kw_st_history "
                "WHERE client_id = ? AND in_new_ex = TRUE "
                "  AND current_new_ex_ad_group IS NOT NULL",
                [client_id],
            ).fetchall()
        }
        logger.info('live ad-group count: %d', len(live_ad_groups))

        # ----- 5. Rule-pass: fetch eligible terms, propose in Python,
        #          write back in one UPDATE per chunk.
        eligible = con.execute(
            """SELECT term, type
               FROM kw_st_history
               WHERE client_id = ?
                 AND in_new_ex = FALSE
                 AND is_brand_campaign = FALSE
                 AND proposal_method IS NULL
               ORDER BY impressions_total DESC, clicks_total DESC""",
            [client_id],
        ).fetchall()
        logger.info('rule-pass eligible: %d', len(eligible))

        rule_updates: list[tuple[str, str, str, str]] = []
        unmapped: list[tuple[str, str]] = []
        for term, t in eligible:
            proposed, rationale = _propose_via_rule(term, live_ad_groups)
            if proposed:
                rule_updates.append((proposed, rationale, term, t))
            else:
                unmapped.append((term, t))

        # Batch the rule writes (DuckDB UPDATE per-row is slow at scale).
        if rule_updates:
            con.executemany(
                """UPDATE kw_st_history
                   SET proposed_ad_group = ?,
                       proposal_method = 'rule',
                       proposal_rationale = ?,
                       last_updated = CURRENT_TIMESTAMP
                   WHERE client_id = ? AND term = ? AND type = ?""",
                [(p, r, client_id, term, t)
                 for (p, r, term, t) in rule_updates],
            )
        summary['rule_mapped'] = len(rule_updates)
        logger.info('rule_mapped: %d', summary['rule_mapped'])

        # ----- 6. AI cache check + hard cap guard.
        ai_eligible_q = con.execute(
            f"""SELECT term, type, ai_cached_at FROM kw_st_history
               WHERE client_id = ?
                 AND in_new_ex = FALSE
                 AND is_brand_campaign = FALSE
                 AND proposal_method IS NULL
               ORDER BY impressions_total DESC, clicks_total DESC""",
            [client_id],
        ).fetchall()

        if not force:
            ai_to_send = [(t, ty) for (t, ty, cached) in ai_eligible_q
                          if cached is None]
            summary['ai_cached_skipped'] = (
                len(ai_eligible_q) - len(ai_to_send))
        else:
            ai_to_send = [(t, ty) for (t, ty, _) in ai_eligible_q]
            summary['ai_cached_skipped'] = 0

        logger.info('ai_eligible: %d (cached_skipped: %d)',
                    len(ai_to_send), summary['ai_cached_skipped'])

        # top_n override (Chris's explicit decision per the brief's
        # "halt-and-surface" guidance): trim AI volume to the top-N
        # highest-click eligible rows. ai_eligible_q is already ordered
        # by impressions_total DESC, clicks_total DESC so the first N is
        # the highest-value slice.
        if top_n is not None and top_n > 0 and len(ai_to_send) > top_n:
            summary['ai_top_n_override'] = top_n
            summary['ai_volume_before_top_n'] = len(ai_to_send)
            ai_to_send = ai_to_send[:top_n]
            logger.info('top_n override: AI volume trimmed to %d', top_n)

        if len(ai_to_send) > AI_HARD_CAP:
            logger.error(
                'AI volume %d exceeds hard cap %d. Halting BEFORE any '
                'API call. Re-run with a stricter low-volume filter, '
                'extend rule coverage, or pass --top-n N to override.',
                len(ai_to_send), AI_HARD_CAP,
            )
            summary['overall'] = 'halted'
            summary['halt_reason'] = (
                f'ai_volume {len(ai_to_send)} > AI_HARD_CAP {AI_HARD_CAP}')
            summary['ai_volume_at_halt'] = len(ai_to_send)
            return summary

        # ----- 7. AI pass (Sonnet).
        if ai_to_send:
            themes = parse_campaigns_themes()
            system_prompt = _build_system_prompt(themes, list(live_ad_groups))

            batches = [ai_to_send[i:i+AI_BATCH_SIZE]
                       for i in range(0, len(ai_to_send), AI_BATCH_SIZE)]
            logger.info('ai batches: %d (size=%d, model=%s)',
                        len(batches), AI_BATCH_SIZE, MODEL_MAPPING_AI)

            ai_writes: list[tuple[str, str, str, str, str]] = []
            for bi, batch in enumerate(batches):
                terms_only = [t for (t, _) in batch]
                t0 = time.monotonic()
                try:
                    mapping, usage, wall_ms = _ai_map_batch(
                        terms_only, system_prompt)
                except claude_subprocess.ClaudeError as e:
                    logger.error('AI batch %d/%d failed (%s): %s',
                                 bi+1, len(batches), e.error_type, e)
                    # Surface partial results; don't blow up the whole run.
                    summary['ai_error'] = f'{e.error_type}: {str(e)[:200]}'
                    break
                except Exception as e:  # noqa: BLE001
                    logger.exception('AI batch %d/%d crashed', bi+1, len(batches))
                    summary['ai_error'] = str(e)[:300]
                    break

                summary['ai_batches'] += 1
                summary['ai_sent'] += len(batch)
                summary['ai_tokens_in']  += int(usage.get('input_tokens', 0) or 0)
                summary['ai_tokens_out'] += int(usage.get('output_tokens', 0) or 0)
                summary['ai_wall_clock_ms'] += int(wall_ms)

                for term, ty in batch:
                    rec = mapping.get(term)
                    if not rec:
                        # Sonnet missed this term — leave for next run.
                        continue
                    ag = rec.get('ad_group') or ''
                    rat = (rec.get('rationale') or '')[:300]
                    if not ag:
                        continue
                    # No em-dashes anywhere — hyphens only.
                    rat = rat.replace('—', '-').replace('–', '-')
                    ai_writes.append((ag, rat, client_id, term, ty))
                    summary['ai_mapped'] += 1

                logger.info(
                    'ai batch %d/%d: mapped %d/%d (in_tok=%s, out_tok=%s, %dms)',
                    bi+1, len(batches),
                    sum(1 for (t, _) in batch if mapping.get(t)),
                    len(batch),
                    usage.get('input_tokens'), usage.get('output_tokens'),
                    int((time.monotonic() - t0) * 1000),
                )

            if ai_writes:
                con.executemany(
                    """UPDATE kw_st_history
                       SET proposed_ad_group = ?,
                           proposal_method = 'ai',
                           proposal_rationale = ?,
                           ai_cached_at = CURRENT_TIMESTAMP,
                           last_updated = CURRENT_TIMESTAMP
                       WHERE client_id = ? AND term = ? AND type = ?""",
                    ai_writes,
                )
                logger.info('ai writes: %d rows updated', len(ai_writes))

        # ----- 8. Cost report.
        cost_in  = (summary['ai_tokens_in']  / 1_000_000) * SONNET_INPUT_PER_MTOK_USD
        cost_out = (summary['ai_tokens_out'] / 1_000_000) * SONNET_OUTPUT_PER_MTOK_USD
        summary['ai_cost_usd'] = round(cost_in + cost_out, 4)
        summary['ai_cost_gbp'] = round(summary['ai_cost_usd'] * USD_TO_GBP, 4)

        summary['overall'] = 'success' if not summary.get('ai_error') else 'partial'
        return summary
    except Exception as e:  # noqa: BLE001
        logger.exception('run_mapping failed: %s', e)
        summary['overall'] = 'failed'
        summary['error'] = str(e)[:500]
        return summary
    finally:
        con.close()


def cli_main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    force = '--force' in argv
    top_n: int | None = None
    for a in argv:
        if a.startswith('--top-n='):
            try:
                top_n = int(a.split('=', 1)[1])
            except ValueError:
                logger.error('Bad --top-n value: %s', a)
                return 2
    client_id = next((a for a in argv if not a.startswith('--')), 'dbd001')
    result = run_mapping(client_id, force=force, top_n=top_n)
    logger.info('FINAL: %s', json.dumps(result, indent=2, default=str))
    return 0 if result.get('overall') in ('success', 'partial', 'halted') else 1


if __name__ == '__main__':
    sys.exit(cli_main())
