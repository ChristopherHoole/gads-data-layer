"""Phase 1 (2.2 neg-list audit) — register `neg_remove` check row.

Idempotent. Adds a row to act_v2_checks so executed_actions logging from the
remove-from-list endpoint satisfies the check_id FK.

Run:
  python -m act_dashboard.db.migrations.add_neg_remove_check
"""
import os
import duckdb

DB_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), '..', '..', '..', 'warehouse.duckdb')
)

CHECK_ID = 'neg_remove_via_audit'


def run():
    con = duckdb.connect(DB_PATH)
    try:
        existing = con.execute(
            'SELECT check_id FROM act_v2_checks WHERE check_id = ?',
            [CHECK_ID],
        ).fetchone()
        if existing:
            print(f'[add_neg_remove_check] {CHECK_ID} already present, no-op')
            return
        con.execute(
            """INSERT INTO act_v2_checks
               (check_id, level, check_name, description,
                action_category, auto_execute, cooldown_hours, active)
               VALUES (?, 'keyword', ?, ?, 'act', FALSE, NULL, TRUE)""",
            [
                CHECK_ID,
                'Neg list audit remove',
                'Removes a single shared-criterion from a neg list via the 2.2 audit workflow. Idempotent — NOT_FOUND / DOES_NOT_EXIST treated as success.',
            ],
        )
        print(f'[add_neg_remove_check] inserted {CHECK_ID}')
    finally:
        con.close()


if __name__ == '__main__':
    run()
