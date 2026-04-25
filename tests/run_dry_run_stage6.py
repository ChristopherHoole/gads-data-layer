"""Stage 6 dry-run: classify Stage 0 fixture rows, measure agreement
vs human triage.

Re-runnable. Pass --iter <N> to save with a unique suffix during prompt
iteration. Always uses force_reclassify=True so prompt edits take effect.

Set STAGE6_API_BASE env var to point at a different Flask port if needed
(default: http://localhost:5000).
"""
from __future__ import annotations

import argparse
import json
import os
import time
from collections import defaultdict
from pathlib import Path

import requests

FIXTURE_PATH = Path("tests/fixtures/ai_classifier_ground_truth_24_apr.json")
RESULTS_DIR = Path("tests/fixtures")
API_BASE = os.environ.get('STAGE6_API_BASE', 'http://localhost:5000')
BATCH_SIZE = 25  # 50-row batches were hitting subprocess 60s timeout on pmax_block
CLIENT_ID = "dbd001"
ANALYSIS_DATE = "2026-04-23"   # date in fixture; classifier writes this to AI table


def chunked(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


def call_classify(flow, ids):
    """POST /v2/api/ai/classify-terms with force_reclassify=True. Returns parsed response."""
    if flow == 'pass3':
        body = {
            "client_id": CLIENT_ID, "analysis_date": ANALYSIS_DATE,
            "flow": flow, "phrase_suggestion_ids": ids,
            "force_reclassify": True,
        }
    else:
        body = {
            "client_id": CLIENT_ID, "analysis_date": ANALYSIS_DATE,
            "flow": flow, "review_ids": ids,
            "force_reclassify": True,
        }
    r = requests.post(
        f"{API_BASE}/v2/api/ai/classify-terms",
        json=body, timeout=180,
    )
    if r.status_code != 200:
        print(f"  ERROR {r.status_code}: {r.text[:300]}")
        return None
    return r.json()


def run_against_fixture(fixture):
    """Group fixture rows by (source_table, primary_flow), call classify per
    pair in batches. Returns: dict mapping (source_table, source_id) -> ai
    result dict.

    Why group by primary flow: each row's classification gets written to
    act_v2_ai_classifications with the request body's `flow`. If we lumped
    everything under 'pmax_review' the AI table would have wrong flow tags
    for search_block / search_review rows, polluting Stage 7's UI filters.
    """
    by_table_flow = defaultdict(set)   # (source_table, primary_flow) -> set of source_ids
    for row in fixture['rows']:
        flows = row.get('flows') or []
        if not flows:
            continue   # skip rows with empty flows (e.g., rejected_sticky)
        primary_flow = flows[0]
        by_table_flow[(row['source_table'], primary_flow)].add(row['source_id'])

    ai_results = {}   # (source_table, source_id) -> result dict

    for (source_table, flow), ids in by_table_flow.items():
        ids = sorted(ids)
        print(f"\n=== {source_table} / {flow} ({len(ids)} ids) ===")
        for batch_idx, batch in enumerate(chunked(ids, BATCH_SIZE)):
            print(f"  batch {batch_idx + 1} ({len(batch)} ids)... ",
                  end='', flush=True)
            t0 = time.monotonic()
            resp = call_classify(flow, batch)
            elapsed = time.monotonic() - t0
            if resp is None:
                print("FAILED")
                continue
            print(f"OK ({elapsed:.1f}s, "
                  f"{resp.get('tokens_used', 0)} tokens)")
            for item in resp.get('results', []):
                src_id = (
                    item.get('review_id')
                    or item.get('phrase_suggestion_id')
                )
                ai_results[(source_table, src_id)] = item

    return ai_results


def compare(fixture, ai_results):
    """Per-row + aggregate metrics."""
    rows = []
    for fxr in fixture['rows']:
        key = (fxr['source_table'], fxr['source_id'])
        ai = ai_results.get(key)
        if ai is None:
            rows.append({**fxr, 'ai': None, 'agreement': None})
            continue

        if fxr['source_table'] == 'act_v2_phrase_suggestions':
            # Pass3: compare AI's target_list_role vs engine's suggestion
            # (which Chris approved/rejected)
            human_verdict = fxr['human_verdict']
            engine_role = fxr.get('engine_suggested_target_list_role')
            ai_role = ai.get('ai_target_list_role')
            if human_verdict == 'approved':
                agreement = (ai_role == engine_role)
            else:
                agreement = None  # ambiguous metric for rejected pass3
        else:
            # block/review flows: compare verdicts
            human_verdict = fxr['human_verdict']   # 'approved' or 'rejected'
            ai_verdict = ai.get('ai_verdict')      # 'approve' / 'reject' / 'unsure'
            # Map ACT terminology: human 'approved' = block (push neg) = AI 'approve'
            #                      human 'rejected' = keep running       = AI 'reject'
            # AI 'unsure' counts as no agreement (deferred to human)
            if ai_verdict == 'unsure':
                agreement = None  # excluded from agreement metric
            else:
                expected = 'approve' if human_verdict == 'approved' else 'reject'
                agreement = (ai_verdict == expected)

        rows.append({
            **fxr,
            'ai_verdict': ai.get('ai_verdict'),
            'ai_target_list_role': ai.get('ai_target_list_role'),
            'ai_confidence': ai.get('ai_confidence'),
            'ai_intent_tag': ai.get('ai_intent_tag'),
            'ai_reasoning': ai.get('ai_reasoning'),
            'agreement': agreement,
        })

    return rows


def summarize(rows):
    """Print metrics. Returns dict for JSON dump."""
    total = len(rows)
    classified = sum(1 for r in rows if r.get('ai_confidence') is not None)
    overall_with_verdict = [r for r in rows if r['agreement'] is not None]
    overall_agree = sum(1 for r in overall_with_verdict if r['agreement'])
    hc = [r for r in rows if r.get('ai_confidence') == 'high'
          and r['agreement'] is not None]
    hc_agree = sum(1 for r in hc if r['agreement'])
    by_flow_tot = defaultdict(int)
    by_flow_agree = defaultdict(int)
    for r in rows:
        if r['agreement'] is None:
            continue
        flow = (r.get('flows') or ['(unknown)'])[0]
        by_flow_tot[flow] += 1
        if r['agreement']:
            by_flow_agree[flow] += 1
    sna_rows = [r for r in rows
                if (r.get('pass1_reason') == 'service_not_advertised'
                    and r['agreement'] is not None)]
    sna_agree = sum(1 for r in sna_rows if r['agreement'])
    hc_disagree = [r for r in hc if not r['agreement']]

    print(f"\n{'=' * 70}")
    print("AGREEMENT SUMMARY")
    print(f"{'=' * 70}")
    print(f"Total fixture rows:          {total}")
    print(f"AI classified:               {classified}/{total}")
    print()
    print("OVERALL agreement (excl 'unsure' / pass3-rejected):")
    if overall_with_verdict:
        print(f"  {overall_agree}/{len(overall_with_verdict)} = "
              f"{100 * overall_agree / len(overall_with_verdict):.1f}%")
    else:
        print("  N/A")
    print()
    print("HIGH-CONFIDENCE subset (the metric that matters --target >=85%):")
    if hc:
        print(f"  {hc_agree}/{len(hc)} = {100 * hc_agree / len(hc):.1f}%")
    else:
        print("  N/A --no high-confidence verdicts")
    print()
    print("Per-flow breakdown:")
    for flow in sorted(by_flow_tot):
        tot = by_flow_tot[flow]
        agr = by_flow_agree[flow]
        pct = 100 * agr / tot if tot else 0
        print(f"  {flow:18s}: {agr}/{tot} = {pct:.1f}%")
    print()
    print("HARD FLOOR: service_not_advertised rows (target >=95%):")
    if sna_rows:
        print(f"  {sna_agree}/{len(sna_rows)} = "
              f"{100 * sna_agree / len(sna_rows):.1f}%")
    else:
        print("  N/A --no sna rows in fixture")
    print()
    print(f"HIGH-CONFIDENCE DISAGREEMENTS ({len(hc_disagree)}):")
    print("  These are the most useful rows to inspect for prompt iteration:")
    for r in hc_disagree[:20]:
        st = r.get('search_term') or r.get('fragment') or '?'
        print(f"  - [{r['source_id']}] \"{st}\"")
        print(f"      human={r['human_verdict']} | "
              f"ai={r.get('ai_verdict') or r.get('ai_target_list_role')} "
              f"({r.get('ai_intent_tag')})")
        print(f"      reasoning: {(r.get('ai_reasoning') or '')[:200]}")
    if len(hc_disagree) > 20:
        print(f"  ... +{len(hc_disagree) - 20} more")

    return {
        'total': total,
        'classified': classified,
        'overall_agreement': {
            'numerator': overall_agree,
            'denominator': len(overall_with_verdict),
            'pct': (100 * overall_agree / len(overall_with_verdict)
                    if overall_with_verdict else None),
        },
        'high_confidence_agreement': {
            'numerator': hc_agree, 'denominator': len(hc),
            'pct': 100 * hc_agree / len(hc) if hc else None,
        },
        'per_flow': {
            flow: {'agree': by_flow_agree[flow], 'total': by_flow_tot[flow]}
            for flow in by_flow_tot
        },
        'service_not_advertised_floor': {
            'numerator': sna_agree, 'denominator': len(sna_rows),
            'pct': 100 * sna_agree / len(sna_rows) if sna_rows else None,
        },
        'high_confidence_disagreements': [
            {k: r.get(k) for k in (
                'source_table', 'source_id', 'search_term', 'fragment',
                'human_verdict', 'ai_verdict', 'ai_target_list_role',
                'ai_confidence', 'ai_intent_tag', 'ai_reasoning',
            )}
            for r in hc_disagree
        ],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        '--iter', type=int, default=0,
        help="iteration number (0 = first run; saves to "
             "ai_classifier_run_v1.json; >0 saves to "
             "ai_classifier_run_v1_iter{N}.json)",
    )
    args = ap.parse_args()

    print(f"Loading fixture: {FIXTURE_PATH}")
    with open(FIXTURE_PATH) as f:
        fixture = json.load(f)
    print(f"  {len(fixture['rows'])} ground-truth rows")
    print(f"API: {API_BASE}")

    print(f"\nClassifying via {API_BASE}/v2/api/ai/classify-terms "
          f"(force_reclassify=True)...")
    t0 = time.monotonic()
    ai_results = run_against_fixture(fixture)
    print(f"\nClassify pass took {time.monotonic() - t0:.1f}s. "
          f"Got {len(ai_results)} AI results.")

    rows = compare(fixture, ai_results)
    summary = summarize(rows)

    out_name = (
        "ai_classifier_run_v1.json"
        if args.iter == 0
        else f"ai_classifier_run_v1_iter{args.iter}.json"
    )
    out_path = RESULTS_DIR / out_name
    with open(out_path, 'w') as f:
        json.dump({
            'summary': summary,
            'rows': rows,
        }, f, indent=2, default=str)
    print(f"\nSaved detail to {out_path}")


if __name__ == '__main__':
    main()
