"""
ACT v2 Schema Verification

Verifies that all act_v2_* tables, sequences, indexes, and seed data
are correctly created. Returns exit code 0 if all pass, 1 if any fail.

Prerequisites:
- Flask app must be stopped (DuckDB file lock)
- Run from project root: python -m act_dashboard.db.migrations.verify_act_v2_schema
"""

import os
import sys

import duckdb

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..'))
DB_PATH = os.path.join(PROJECT_ROOT, 'warehouse.duckdb')

# ---------------------------------------------------------------------------
# Expected schema
# ---------------------------------------------------------------------------
EXPECTED_TABLES = {
    'act_v2_clients': 10,
    'act_v2_client_level_state': 5,
    'act_v2_client_settings': 6,
    'act_v2_campaign_roles': 6,
    'act_v2_negative_keyword_lists': 8,
    'act_v2_snapshots': 9,
    'act_v2_checks': 8,
    'act_v2_recommendations': 20,
    'act_v2_executed_actions': 15,
    'act_v2_monitoring': 13,
    'act_v2_alerts': 11,
    'act_v2_search_terms': 20,
    'act_v2_campaign_segments': 17,
}

EXPECTED_SEQUENCES = [
    'seq_act_v2_snapshots',
    'seq_act_v2_recommendations',
    'seq_act_v2_executed_actions',
    'seq_act_v2_monitoring',
    'seq_act_v2_alerts',
    'seq_act_v2_search_terms',
    'seq_act_v2_campaign_segments',
]

EXPECTED_INDEXES = [
    'idx_act_v2_snapshots_lookup',
    'idx_act_v2_recs_client_status',
    'idx_act_v2_actions_client_date',
    'idx_act_v2_monitoring_active',
    'idx_act_v2_alerts_client',
    'idx_act_v2_search_terms_lookup',
    'idx_act_v2_segments_lookup',
]


def main():
    print('=' * 40)
    print('ACT v2 Schema Verification')
    print('=' * 40)

    try:
        con = duckdb.connect(DB_PATH, read_only=True)
    except duckdb.IOException:
        print('[FAIL] ERROR: Database is locked. Stop the Flask app first:')
        print('  taskkill /IM python.exe /F')
        sys.exit(1)

    passed = 0
    failed = 0

    def check(name, condition):
        nonlocal passed, failed
        if condition:
            print(f'[PASS] {name}')
            passed += 1
        else:
            print(f'[FAIL] {name}')
            failed += 1

    try:
        # Get existing tables
        all_tables = [
            row[0] for row in
            con.execute(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'main'"
            ).fetchall()
        ]

        # 1. Check each table exists and has correct column count
        for table_name, expected_cols in EXPECTED_TABLES.items():
            exists = table_name in all_tables
            check(f'Table {table_name} exists', exists)

            if exists:
                cols = con.execute(f"PRAGMA table_info('{table_name}')").fetchall()
                actual_cols = len(cols)
                check(
                    f'Table {table_name} has {expected_cols} columns (got {actual_cols})',
                    actual_cols == expected_cols,
                )
            else:
                check(f'Table {table_name} has {expected_cols} columns', False)

        # 2. Data checks
        checks_count = con.execute('SELECT COUNT(*) FROM act_v2_checks').fetchone()[0]
        check(f'act_v2_checks has 35 rows (got {checks_count})', checks_count == 35)

        client_count = con.execute(
            "SELECT COUNT(*) FROM act_v2_clients WHERE client_id = 'oe001'"
        ).fetchone()[0]
        check(f'Objection Experts client exists (got {client_count})', client_count == 1)

        level_count = con.execute(
            "SELECT COUNT(*) FROM act_v2_client_level_state WHERE client_id = 'oe001'"
        ).fetchone()[0]
        check(f'All 6 level states exist (got {level_count})', level_count == 6)

        non_off = con.execute(
            "SELECT COUNT(*) FROM act_v2_client_level_state "
            "WHERE client_id = 'oe001' AND state != 'off'"
        ).fetchone()[0]
        check(f'All level states are off (non-off: {non_off})', non_off == 0)

        settings_count = con.execute(
            "SELECT COUNT(*) FROM act_v2_client_settings WHERE client_id = 'oe001'"
        ).fetchone()[0]
        check(f'71 settings seeded (got {settings_count})', settings_count == 71)

        nkl_count = con.execute(
            "SELECT COUNT(*) FROM act_v2_negative_keyword_lists WHERE client_id = 'oe001'"
        ).fetchone()[0]
        check(f'9 negative keyword lists created (got {nkl_count})', nkl_count == 9)

        # 3. Check sequences
        seq_rows = con.execute('SELECT sequence_name FROM duckdb_sequences()').fetchall()
        existing_seqs = {row[0] for row in seq_rows}
        for seq_name in EXPECTED_SEQUENCES:
            check(f'Sequence {seq_name} exists', seq_name in existing_seqs)

        # 4. Check indexes
        idx_rows = con.execute('SELECT index_name FROM duckdb_indexes()').fetchall()
        existing_idxs = {row[0] for row in idx_rows}
        for idx_name in EXPECTED_INDEXES:
            check(f'Index {idx_name} exists', idx_name in existing_idxs)

        # Summary
        total = passed + failed
        print('=' * 40)
        if failed == 0:
            print(f'Result: ALL {total} CHECKS PASSED')
        else:
            print(f'Result: {failed} FAILED out of {total} checks')
        print('=' * 40)

    except Exception as e:
        print(f'[FAIL] Verification error: {e}')
        failed += 1

    finally:
        con.close()

    sys.exit(0 if failed == 0 else 1)


if __name__ == '__main__':
    main()
