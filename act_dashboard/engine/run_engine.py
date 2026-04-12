"""
ACT v2 Engine Runner

Runs optimization checks for a client.

Usage (from project root):
    # Run Account Level for yesterday:
    python -m act_dashboard.engine.run_engine --client oe001 --level account

    # Run Account Level for a specific date:
    python -m act_dashboard.engine.run_engine --client oe001 --level account --date 2026-04-11

    # Run all levels:
    python -m act_dashboard.engine.run_engine --client oe001 --level all

Prerequisites:
    - Flask app must be stopped (DuckDB lock)
    - Data must be ingested (Session A2) for the evaluation date
"""

import argparse
import logging
import sys
import time
from datetime import datetime, timedelta

logger = logging.getLogger('act_v2_engine')


def main():
    parser = argparse.ArgumentParser(description="ACT v2 Engine Runner")
    parser.add_argument('--client', required=True, help='ACT client_id (e.g., oe001)')
    parser.add_argument('--level', default='account', help='Level to run: account, campaign, all (default: account)')
    parser.add_argument('--date', help='Evaluation date YYYY-MM-DD (default: yesterday)')
    args = parser.parse_args()

    eval_date = args.date or (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    t0 = time.time()

    if args.level in ('account', 'all'):
        from act_dashboard.engine.account_level import AccountLevelEngine
        engine = AccountLevelEngine(args.client)
        try:
            result = engine.run(eval_date)
        finally:
            engine.close()

    elapsed = time.time() - t0

    print()
    print('=' * 40)
    print('ACT v2 Engine Run Complete')
    print('=' * 40)
    print(f'Client: {args.client}')
    print(f'Level: {args.level}')
    print(f'Date: {eval_date}')
    print(f'Time: {elapsed:.1f}s')
    print('=' * 40)


if __name__ == '__main__':
    main()
