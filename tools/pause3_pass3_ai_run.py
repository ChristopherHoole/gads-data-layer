"""Pause-3 end-to-end run for Tier 2.1e — runs AI Pass 3 against DBD
2026-04-28 with DB writes PERSISTING (no rollback).

Captures usage + cost on success and writes a post-run state report
showing row counts in act_v2_phrase_suggestions + act_v2_pass3_themes.

Usage:
    python -m tools.pause3_pass3_ai_run
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import duckdb

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / 'warehouse.duckdb'
OUT_DIR = PROJECT_ROOT / 'tools' / 'pause3_pass3_ai'
OUT_DIR.mkdir(parents=True, exist_ok=True)

CLIENT = 'dbd001'
ANALYSIS_DATE = '2026-04-28'


def main():
    sys.path.insert(0, str(PROJECT_ROOT))

    # --- Pre-run state ---
    pre_con = duckdb.connect(str(DB_PATH), read_only=True)
    try:
        pre_sugg = pre_con.execute(
            """SELECT review_status, COUNT(*) FROM act_v2_phrase_suggestions
               WHERE client_id = ? AND analysis_date = ?
               GROUP BY review_status""",
            [CLIENT, ANALYSIS_DATE],
        ).fetchall()
        pre_themes = pre_con.execute(
            """SELECT COUNT(*) FROM act_v2_pass3_themes
               WHERE client_id = ? AND analysis_date = ?""",
            [CLIENT, ANALYSIS_DATE],
        ).fetchone()[0]
    finally:
        pre_con.close()

    print('=== PRE-RUN STATE ===')
    print(f'  phrase_suggestions by status: {dict(pre_sugg)}')
    print(f'  themes:                       {pre_themes}')

    # --- Bust idempotency cache + run ---
    from act_dashboard.ai import idempotency
    idempotency._cache.clear()  # type: ignore[attr-defined]
    from act_dashboard.engine.pass3_ai import run_pass3_ai

    con = duckdb.connect(str(DB_PATH))
    try:
        result = run_pass3_ai(con, CLIENT, ANALYSIS_DATE)
    finally:
        con.close()

    (OUT_DIR / 'orchestrator_result.json').write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')

    # --- Post-run state ---
    post_con = duckdb.connect(str(DB_PATH), read_only=True)
    try:
        post_sugg_by_status = post_con.execute(
            """SELECT review_status, COUNT(*) FROM act_v2_phrase_suggestions
               WHERE client_id = ? AND analysis_date = ?
               GROUP BY review_status""",
            [CLIENT, ANALYSIS_DATE],
        ).fetchall()
        post_themes_count = post_con.execute(
            """SELECT COUNT(*) FROM act_v2_pass3_themes
               WHERE client_id = ? AND analysis_date = ?""",
            [CLIENT, ANALYSIS_DATE],
        ).fetchone()[0]
        sample_sugg = post_con.execute(
            """SELECT id, fragment, target_list_role, confidence,
                      occurrence_count, risk_level, review_status,
                      LEFT(rationale, 100)
               FROM act_v2_phrase_suggestions
               WHERE client_id = ? AND analysis_date = ?
                 AND review_status = 'pending'
               ORDER BY confidence DESC, fragment
               LIMIT 5""",
            [CLIENT, ANALYSIS_DATE],
        ).fetchall()
        sample_themes = post_con.execute(
            """SELECT id, LEFT(theme_text, 200) FROM act_v2_pass3_themes
               WHERE client_id = ? AND analysis_date = ?
               ORDER BY id""",
            [CLIENT, ANALYSIS_DATE],
        ).fetchall()
    finally:
        post_con.close()

    print()
    print('=== POST-RUN STATE ===')
    print(f'  phrase_suggestions by status: {dict(post_sugg_by_status)}')
    print(f'  themes:                       {post_themes_count}')
    print()
    print('  --- top 5 pending suggestions by confidence ---')
    for r in sample_sugg:
        print(f'    id={r[0]:4d} {r[1]:30s} role={r[2]:30s} conf={r[3]:.2f} '
              f'occ={r[4]} risk={r[5]:6s} status={r[6]}')
        print(f'           rationale: {r[7]}')
    print()
    print('  --- themes ---')
    for r in sample_themes:
        print(f'    id={r[0]} :: {r[1]}')

    print()
    print('=== ORCHESTRATOR RESULT ===')
    for k in ('engine','suggestions_created','fragments_returned',
              'fragments_dropped_invalid_role','skipped_dedup',
              'terms_considered','tokens_in','tokens_out','cost_usd',
              'wall_clock_ms','prompt_version','model_version'):
        print(f'  {k}: {result.get(k)}')


if __name__ == '__main__':
    main()
