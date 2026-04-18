"""
ACT v2 Seed — Dental by Design

Thin wrapper around the generalised seed_client.py for Dental by Design.

Usage (from project root):
    python -m act_dashboard.db.migrations.seed_dental_by_design --customer-id 1234567890

The customer_id must be supplied at runtime (Google Ads customer ID, digits only).
All other values are hardcoded for this client.
"""

import argparse
import sys

from act_dashboard.db.migrations.seed_client import seed_client


def main():
    parser = argparse.ArgumentParser(description='Seed Dental by Design into ACT v2')
    parser.add_argument('--customer-id', required=True,
                        help='Google Ads customer ID for Dental by Design (digits only, no dashes)')
    args = parser.parse_args()

    seed_client(
        client_id='dbd001',
        client_name='Dental by Design',
        customer_id=args.customer_id,
        persona='lead_gen_cpa',
        monthly_budget=45000.00,
        target_cpa=75.00,
        target_roas=None,
    )


if __name__ == '__main__':
    main()
