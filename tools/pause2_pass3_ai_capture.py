"""Pause-2 capture for Tier 2.1e — runs the AI-driven Pass 3 pipeline
end-to-end against DBD 2026-04-28 with a single monkeypatch on
claude_subprocess.run_claude that captures (system_prompt, user_message,
raw_response, usage, wall_ms) to disk before passing through to the
real implementation. Then rolls back the DB writes so Pause 3 starts clean.

Outputs go to: tools/pause2_pass3_ai/
  - system_prompt.txt
  - user_message.txt
  - raw_response.txt
  - parsed_response.json
  - summary.json (counts + 4-row check + stopword junk count)

Usage:
    python -m tools.pause2_pass3_ai_capture
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import duckdb

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / 'warehouse.duckdb'
OUT_DIR = PROJECT_ROOT / 'tools' / 'pause2_pass3_ai'
OUT_DIR.mkdir(parents=True, exist_ok=True)

CLIENT = 'dbd001'
ANALYSIS_DATE = '2026-04-28'

EXPECTED_FRAGMENTS = ['sedation', 'flipper', 'fillings', 'crewe']
STOPWORDS = {
    'the', 'a', 'an', 'can', 'could', 'should', 'would', 'will',
    'you', 'i', 'my', 'your', 'our', 'get', 'for', 'with', 'on',
    'in', 'at', 'of', 'to', 'from', 'and', 'or', 'but', 'is',
    'are', 'was', 'were', 'be', 'been', 'do', 'does', 'did',
    'have', 'has', 'had', 'near', 'me',
}


def main():
    sys.path.insert(0, str(PROJECT_ROOT))

    # --- Monkeypatch claude_subprocess.run_claude to capture + pass through ---
    from act_dashboard.ai import claude_subprocess
    real_run_claude = claude_subprocess.run_claude
    captured = {'system_prompt': None, 'user_message': None,
                'raw_response': None, 'usage': None, 'wall_ms': None}

    def capturing_run_claude(model, system_prompt, user_message, **kw):
        captured['system_prompt'] = system_prompt
        captured['user_message'] = user_message
        # Persist prompts BEFORE the call so a timeout still leaves us
        # reviewable artifacts.
        (OUT_DIR / 'system_prompt.txt').write_text(system_prompt or '', encoding='utf-8')
        (OUT_DIR / 'user_message.txt').write_text(user_message or '', encoding='utf-8')
        result_text, usage, wall_ms = real_run_claude(
            model, system_prompt, user_message, **kw,
        )
        captured['raw_response'] = result_text
        captured['usage'] = usage
        captured['wall_ms'] = wall_ms
        (OUT_DIR / 'raw_response.txt').write_text(result_text or '', encoding='utf-8')
        return result_text, usage, wall_ms

    claude_subprocess.run_claude = capturing_run_claude

    # --- Run the orchestrator ---
    from act_dashboard.engine.pass3_ai import run_pass3_ai
    from act_dashboard.ai import idempotency
    # Bust idempotency cache to ensure a fresh call.
    idempotency._cache.clear()  # type: ignore[attr-defined]

    con = duckdb.connect(str(DB_PATH))
    result = None
    run_error = None
    try:
        result = run_pass3_ai(con, CLIENT, ANALYSIS_DATE)
    except Exception as e:  # noqa: BLE001
        run_error = repr(e)
        print(f'[capture] run_pass3_ai raised: {run_error}', file=sys.stderr)
    finally:
        con.close()

    # --- Persist captures to disk ---
    (OUT_DIR / 'system_prompt.txt').write_text(
        captured['system_prompt'] or '', encoding='utf-8')
    (OUT_DIR / 'user_message.txt').write_text(
        captured['user_message'] or '', encoding='utf-8')
    (OUT_DIR / 'raw_response.txt').write_text(
        captured['raw_response'] or '', encoding='utf-8')

    # Parse the response separately for analysis
    raw = (captured['raw_response'] or '').strip()
    if raw.startswith('```'):
        nl = raw.find('\n')
        if nl != -1:
            raw = raw[nl + 1:]
        if raw.endswith('```'):
            raw = raw[:-3]
        raw = raw.strip()
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as e:
        parsed = {'_parse_error': str(e)}
    (OUT_DIR / 'parsed_response.json').write_text(
        json.dumps(parsed, indent=2, ensure_ascii=False), encoding='utf-8')

    # --- 4-row check + stopword junk + counts ---
    fragments_returned = parsed.get('fragments', []) if isinstance(parsed, dict) else []
    by_frag = {f.get('fragment'): f for f in fragments_returned if isinstance(f, dict)}

    expected_check = []
    for ef in EXPECTED_FRAGMENTS:
        if ef in by_frag:
            f = by_frag[ef]
            expected_check.append({
                'fragment': ef,
                'present': True,
                'target_list_role': f.get('target_list_role'),
                'confidence': f.get('confidence'),
                'rationale': (f.get('rationale') or '')[:200],
            })
        else:
            expected_check.append({'fragment': ef, 'present': False})

    stopword_junk = []
    for f in fragments_returned:
        if not isinstance(f, dict):
            continue
        frag = (f.get('fragment') or '').strip().lower()
        if not frag:
            stopword_junk.append('(empty)')
            continue
        toks = frag.split()
        if all(t in STOPWORDS for t in toks):
            stopword_junk.append(frag)

    summary = {
        'client': CLIENT,
        'analysis_date': ANALYSIS_DATE,
        'run_error': run_error,
        'orchestrator_result': result,
        'fragments_returned_count': len(fragments_returned),
        'themes_count': len(parsed.get('themes', []) if isinstance(parsed, dict) else []),
        'stopword_junk_count': len(stopword_junk),
        'stopword_junk_examples': stopword_junk[:10],
        'expected_fragment_check': expected_check,
        'tokens_in': captured['usage'].get('input_tokens') if captured['usage'] else None,
        'tokens_out': captured['usage'].get('output_tokens') if captured['usage'] else None,
        'wall_ms': captured['wall_ms'],
    }
    (OUT_DIR / 'summary.json').write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding='utf-8')

    # --- Roll back DB writes (suggestions + themes for this run) ---
    # Mirror the FK precursor pattern from pass3_ai.py: any pending
    # phrase_suggestion that has a Stage 11 router classification
    # attached needs that classification deleted first. Otherwise the
    # FK constraint blocks the suggestions DELETE.
    con = duckdb.connect(str(DB_PATH))
    try:
        before_sugg = con.execute(
            "SELECT COUNT(*) FROM act_v2_phrase_suggestions "
            "WHERE client_id = ? AND analysis_date = ? AND review_status = 'pending'",
            [CLIENT, ANALYSIS_DATE],
        ).fetchone()[0]
        before_themes = con.execute(
            "SELECT COUNT(*) FROM act_v2_pass3_themes "
            "WHERE client_id = ? AND analysis_date = ?",
            [CLIENT, ANALYSIS_DATE],
        ).fetchone()[0]
        con.execute(
            """DELETE FROM act_v2_ai_classifications
               WHERE phrase_suggestion_id IN (
                   SELECT id FROM act_v2_phrase_suggestions
                   WHERE client_id = ? AND analysis_date = ?
                     AND review_status = 'pending'
               )""",
            [CLIENT, ANALYSIS_DATE],
        )
        con.execute(
            "DELETE FROM act_v2_phrase_suggestions "
            "WHERE client_id = ? AND analysis_date = ? AND review_status = 'pending'",
            [CLIENT, ANALYSIS_DATE],
        )
        con.execute(
            "DELETE FROM act_v2_pass3_themes "
            "WHERE client_id = ? AND analysis_date = ?",
            [CLIENT, ANALYSIS_DATE],
        )
        rollback = {
            'pending_suggestions_deleted': before_sugg,
            'themes_deleted': before_themes,
        }
    finally:
        con.close()

    summary['rollback'] = rollback
    (OUT_DIR / 'summary.json').write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding='utf-8')

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
