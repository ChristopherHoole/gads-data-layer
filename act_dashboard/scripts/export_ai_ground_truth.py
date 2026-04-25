"""Tier 2.1 Stage 0 — Export Friday 24 Apr manual triage as AI ground-truth.

Reads:
  - act_v2_search_term_reviews
  - act_v2_phrase_suggestions

Filter: client_id='dbd001', review_status IN ('approved','pushed','rejected'),
reviewed_at on 2026-04-24 (UTC, naive).

NOTE: 'pushed' is included as an APPROVED verdict from the human reviewer's
perspective — the status flow is approved -> pushed when the row gets sent
to Google Ads, so all 'pushed' rows reflect a Chris-approved decision. The
brief's literal filter (approved/rejected only) excluded the bulk of
Friday's approve actions (165 of them on 24 Apr) and produced ~43 rows
against the brief's loose target of ~200. We map 'pushed' -> 'approved'
in the human_verdict field so Stage 6 sees the full decision set.

Each review row is annotated with one or more flow tags:
  search_block / search_review / pmax_block / pmax_review (review-table rows)
  pass3 (phrase-suggestions rows)

Flow split mirrors v2_negatives_api.list_search_term_reviews's
campaign_source filter: JOIN act_v2_search_terms on
(client_id, search_term, snapshot_date BETWEEN first_seen_date AND
last_seen_date), group by review id + campaign_type, keep buckets where
SUM(impressions) > 0 OR SUM(clicks) > 0. A row may appear in BOTH search
and pmax flows — that's expected.

Run:
    .venv\\Scripts\\python.exe -m act_dashboard.scripts.export_ai_ground_truth
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

import duckdb

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = str(PROJECT_ROOT / 'warehouse.duckdb')
OUT_PATH = PROJECT_ROOT / 'tests' / 'fixtures' / 'ai_classifier_ground_truth_24_apr.json'

CLIENT_ID = 'dbd001'
WINDOW_START = '2026-04-24 00:00:00'
WINDOW_END   = '2026-04-25 00:00:00'

ALL_FLOWS = ('search_block', 'search_review', 'pmax_block', 'pmax_review', 'pass3')


def _f(v):
    """DECIMAL/Decimal -> float for JSON; pass through None / int."""
    if v is None:
        return None
    if isinstance(v, Decimal):
        return float(v)
    return v


def _iso(dt):
    if dt is None:
        return None
    if isinstance(dt, str):
        return dt
    return dt.isoformat()


def main() -> int:
    if not Path(DB_PATH).exists():
        print(f"warehouse.duckdb not found at {DB_PATH}", file=sys.stderr)
        return 1
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect(DB_PATH, read_only=True)
    try:
        # ------------------------------------------------------------------
        # 1. Review-table rows (block/review flows)
        # ------------------------------------------------------------------
        review_rows = con.execute(
            """
            SELECT id, client_id, search_term, analysis_date,
                   first_seen_date, last_seen_date,
                   total_impressions, total_clicks, total_cost, total_conversions,
                   pass1_status, pass1_reason, pass1_reason_detail,
                   pass2_target_list_role, review_status, reviewed_at, reviewed_by
              FROM act_v2_search_term_reviews
             WHERE client_id = ?
               AND review_status IN ('approved', 'pushed', 'rejected')
               AND reviewed_at >= ?
               AND reviewed_at <  ?
             ORDER BY reviewed_at, id
            """,
            [CLIENT_ID, WINDOW_START, WINDOW_END],
        ).fetchall()

        review_ids = [r[0] for r in review_rows]

        # Per-review per-campaign-type contribution. Same join the API uses.
        # Returns rows like (review_id, campaign_type) where the term had
        # impressions>0 OR clicks>0 in act_v2_search_terms within its
        # first_seen..last_seen range. A review id may surface twice — once
        # SEARCH, once PERFORMANCE_MAX.
        per_id_types: dict[int, set[str]] = {rid: set() for rid in review_ids}
        if review_ids:
            placeholders = ','.join(['?'] * len(review_ids))
            split_rows = con.execute(
                f"""
                SELECT r.id, st.campaign_type
                  FROM act_v2_search_term_reviews r
                  JOIN act_v2_search_terms st
                    ON st.client_id   = r.client_id
                   AND st.search_term = r.search_term
                   AND st.snapshot_date BETWEEN r.first_seen_date
                                            AND r.last_seen_date
                 WHERE r.id IN ({placeholders})
                 GROUP BY r.id, st.campaign_type
                HAVING COALESCE(SUM(st.impressions), 0) > 0
                    OR COALESCE(SUM(st.clicks), 0) > 0
                """,
                review_ids,
            ).fetchall()
            for rid, ctype in split_rows:
                per_id_types.setdefault(rid, set()).add(ctype)

        # ------------------------------------------------------------------
        # 2. Pass 3 rows (phrase suggestions)
        # ------------------------------------------------------------------
        phrase_rows = con.execute(
            """
            SELECT id, client_id, analysis_date, fragment, word_count,
                   target_list_role, source_search_terms,
                   occurrence_count, risk_level,
                   review_status, reviewed_at, reviewed_by
              FROM act_v2_phrase_suggestions
             WHERE client_id = ?
               AND review_status IN ('approved', 'pushed', 'rejected')
               AND reviewed_at >= ?
               AND reviewed_at <  ?
             ORDER BY reviewed_at, id
            """,
            [CLIENT_ID, WINDOW_START, WINDOW_END],
        ).fetchall()
    finally:
        con.close()

    # ----------------------------------------------------------------------
    # Build output
    # ----------------------------------------------------------------------
    totals = {flow: {'approved': 0, 'rejected': 0} for flow in ALL_FLOWS}
    rows_out: list[dict] = []

    for r in review_rows:
        (rid, _cid, search_term, analysis_date,
         _fs, _ls,
         impr, clicks, cost, conv,
         pass1_status, pass1_reason, pass1_reason_detail,
         pass2_role, raw_status, reviewed_at, reviewed_by) = r

        # 'pushed' is post-approval: human said approve, ACT then pushed
        # to GAds. For ground-truth purposes the human verdict is approved.
        verdict = 'approved' if raw_status == 'pushed' else raw_status

        ctypes = per_id_types.get(rid, set())
        flows: list[str] = []
        if pass1_status in ('block', 'review'):
            if 'SEARCH' in ctypes:
                flows.append(f'search_{pass1_status}')
            if 'PERFORMANCE_MAX' in ctypes:
                flows.append(f'pmax_{pass1_status}')
        # Edge: review row with no matching source-term row (term aged out
        # of the snapshot window or the join misses for some reason). We
        # still include the row but with an empty flows list so the count
        # is honest.

        for flow in flows:
            if flow in totals and verdict in totals[flow]:
                totals[flow][verdict] += 1

        rows_out.append({
            'source_table': 'act_v2_search_term_reviews',
            'source_id': rid,
            'flows': flows,
            'analysis_date': analysis_date.isoformat() if analysis_date else None,
            'search_term': search_term,
            'pass1_status': pass1_status,
            'pass1_reason': pass1_reason,
            'pass1_reason_detail': pass1_reason_detail,
            'pass2_target_list_role': pass2_role,
            'total_cost': _f(cost),
            'total_clicks': _f(clicks),
            'total_impressions': _f(impr),
            'total_conversions': _f(conv),
            'human_verdict': verdict,
            'reviewed_at': _iso(reviewed_at),
            'reviewed_by': reviewed_by,
        })

    for r in phrase_rows:
        (rid, _cid, analysis_date, fragment, word_count,
         target_role, source_terms_raw,
         occ_count, risk,
         raw_status, reviewed_at, reviewed_by) = r

        verdict = 'approved' if raw_status == 'pushed' else raw_status

        if verdict in totals['pass3']:
            totals['pass3'][verdict] += 1

        # source_search_terms is JSON (DuckDB JSON or string)
        if isinstance(source_terms_raw, (list, dict)):
            source_terms = source_terms_raw
        else:
            try:
                source_terms = json.loads(source_terms_raw) if source_terms_raw else None
            except (TypeError, ValueError):
                source_terms = source_terms_raw

        rows_out.append({
            'source_table': 'act_v2_phrase_suggestions',
            'source_id': rid,
            'flows': ['pass3'],
            'analysis_date': analysis_date.isoformat() if analysis_date else None,
            'fragment': fragment,
            'word_count': word_count,
            'engine_suggested_target_list_role': target_role,
            'occurrence_count': occ_count,
            'risk_level': risk,
            'human_verdict': verdict,
            'reviewed_at': _iso(reviewed_at),
            'reviewed_by': reviewed_by,
        })

    payload = {
        'exported_at': datetime.now(timezone.utc).replace(tzinfo=None).isoformat(timespec='seconds'),
        'client_id': CLIENT_ID,
        'human_reviewer': 'chris',
        'review_window_start': WINDOW_START.replace(' ', 'T'),
        'review_window_end':   WINDOW_END.replace(' ', 'T'),
        'totals_by_flow': totals,
        'rows': rows_out,
    }

    OUT_PATH.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding='utf-8',
    )

    # ----------------------------------------------------------------------
    # Sanity output
    # ----------------------------------------------------------------------
    rel = OUT_PATH.relative_to(PROJECT_ROOT).as_posix()
    print(f"Exported to {rel}")
    print("Totals by flow:")
    width = max(len(f) for f in ALL_FLOWS)
    for flow in ALL_FLOWS:
        t = totals[flow]
        print(f"  {flow.ljust(width)}: {t['approved']} approved / {t['rejected']} rejected")
    distinct_reviews = len(review_rows)
    distinct_pass3   = len(phrase_rows)
    sum_flows = sum(t['approved'] + t['rejected'] for t in totals.values())
    print(
        f"  TOTAL DISTINCT REVIEW ROWS: "
        f"{distinct_reviews} (block/review) + {distinct_pass3} (pass3) = "
        f"{distinct_reviews + distinct_pass3}"
    )
    print(
        f"  (sum-of-flows = {sum_flows}; "
        f"may exceed distinct rows when a term appears in both Search + PMax)"
    )
    return 0


if __name__ == '__main__':
    sys.exit(main())
