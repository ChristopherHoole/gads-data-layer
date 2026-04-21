"""N1b Wave C12 — Reclassify CLI.

Re-runs Pass 1 (idempotent, preserves acted-on rows) + Pass 2 (re-routes
blocks) for a specified (client, analysis_date). Useful after config
changes (exclusion tokens, toggles) to apply the new engine without
triggering a full overnight cycle.

Usage:
    python -m act_dashboard.engine.negatives.reclassify \
        --client dbd001 --analysis-date 2026-04-20
"""
import argparse
import logging
import os
import sys
from datetime import date, datetime

from act_dashboard.engine.negatives.pass1 import run_pass1
from act_dashboard.engine.negatives.pass2 import run_pass2

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
DB_PATH = os.path.join(PROJECT_ROOT, 'warehouse.duckdb')

logger = logging.getLogger('act_v2_reclassify')
logger.setLevel(logging.INFO)
if not logger.handlers:
    h = logging.StreamHandler(sys.stdout)
    h.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
    logger.addHandler(h)


def main():
    p = argparse.ArgumentParser(description='Re-classify search terms for a given client + date')
    p.add_argument('--client', required=True, help='client_id (e.g. dbd001)')
    p.add_argument('--analysis-date', help='YYYY-MM-DD (default: today)')
    args = p.parse_args()

    if args.analysis_date:
        d = datetime.strptime(args.analysis_date, '%Y-%m-%d').date()
    else:
        d = date.today()

    logger.info(f'Reclassifying {args.client} for analysis_date={d}')
    s1 = run_pass1(args.client, DB_PATH, d)
    logger.info(f'  pass1: {s1["status_counts"]}  '
                f'(ins={s1["inserted"]} upd={s1["updated"]} preserved={s1["preserved"]})')
    for reason, n in sorted(s1['reason_histogram'].items(), key=lambda x: -x[1]):
        logger.info(f'    {n:>5}  {reason}')
    s2 = run_pass2(args.client, DB_PATH, d)
    logger.info(f'  pass2: routed {s2["routed"]} blocks -> {s2["role_histogram"]}')


if __name__ == '__main__':
    main()
