"""N1b Wave C12 — Rule 7 exclusion + reason detail + auto-block toggle.

Schema additions:
 - act_v2_search_term_reviews.pass1_reason_detail  (VARCHAR, nullable)
 - act_v2_clients.rule_7_exclude_tokens             (TEXT,    nullable)
 - act_v2_client_settings: rule_7_auto_block        (bool, default 'true')

Seed: DBD gets a default exclusion-token list for industry-universal words
that block bare-query searches via Rule 2 equality but should NOT extrapolate
via Rule 7 soft-signal. OE keeps NULL.

DuckDB: ALTER TABLE ADD COLUMN is native - no table rebuild. Idempotent.
"""
import logging
import os
import sys

import duckdb

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..'))
DB_PATH = os.path.join(PROJECT_ROOT, 'warehouse.duckdb')

logger = logging.getLogger('act_v2_wavec12')
logger.setLevel(logging.INFO)
if not logger.handlers:
    h = logging.StreamHandler(sys.stdout)
    h.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
    logger.addHandler(h)


def _has_column(con, table: str, col: str) -> bool:
    return bool(con.execute(
        "SELECT 1 FROM information_schema.columns WHERE table_name=? AND column_name=?",
        [table, col],
    ).fetchall())


DBD_EXCLUDE_SEED = ('teeth, dental, tooth, smile, implant, implants, mouth, '
                    'gum, gums, dentistry, dentist, dentists, oral')


def main():
    logger.info('=' * 50)
    logger.info('Wave C12: Rule 7 exclusion + reason detail')
    logger.info('=' * 50)
    con = duckdb.connect(DB_PATH)
    try:
        # 1a. pass1_reason_detail
        if _has_column(con, 'act_v2_search_term_reviews', 'pass1_reason_detail'):
            logger.info('  reviews.pass1_reason_detail (already exists)')
        else:
            con.execute('ALTER TABLE act_v2_search_term_reviews '
                        'ADD COLUMN pass1_reason_detail VARCHAR;')
            logger.info('  reviews.pass1_reason_detail (added)')

        # 1b. rule_7_exclude_tokens
        if _has_column(con, 'act_v2_clients', 'rule_7_exclude_tokens'):
            logger.info('  clients.rule_7_exclude_tokens (already exists)')
        else:
            con.execute('ALTER TABLE act_v2_clients '
                        'ADD COLUMN rule_7_exclude_tokens TEXT;')
            logger.info('  clients.rule_7_exclude_tokens (added)')

        # 1c. DBD seed (overwrite only if currently NULL)
        cur = con.execute(
            "SELECT rule_7_exclude_tokens FROM act_v2_clients WHERE client_id='dbd001'"
        ).fetchone()
        if cur and cur[0] in (None, ''):
            con.execute(
                "UPDATE act_v2_clients SET rule_7_exclude_tokens = ? WHERE client_id = 'dbd001'",
                [DBD_EXCLUDE_SEED],
            )
            logger.info('  dbd001 exclude tokens seeded')
        else:
            logger.info(f'  dbd001 exclude tokens already set: {cur[0] if cur else "n/a"}')

        # 1d. rule_7_auto_block setting for every existing client (default true)
        for cid in [r[0] for r in con.execute('SELECT client_id FROM act_v2_clients').fetchall()]:
            exists = con.execute(
                "SELECT 1 FROM act_v2_client_settings "
                "WHERE client_id = ? AND setting_key = 'rule_7_auto_block'",
                [cid],
            ).fetchone()
            if not exists:
                con.execute(
                    """INSERT INTO act_v2_client_settings
                       (client_id, setting_key, setting_value, setting_type, level)
                       VALUES (?, 'rule_7_auto_block', 'true', 'bool', 'account')""",
                    [cid],
                )
                logger.info(f'  {cid}: rule_7_auto_block = true (inserted)')
            else:
                logger.info(f'  {cid}: rule_7_auto_block (already present)')

        logger.info('=' * 50)
    finally:
        con.close()


if __name__ == '__main__':
    main()
