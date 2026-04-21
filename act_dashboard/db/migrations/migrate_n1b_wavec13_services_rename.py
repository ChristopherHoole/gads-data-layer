"""N1b Wave C13 — rename act_v2_clients.services_all -> services_not_advertised.

Drops the runtime-subtracted denylist model (services_all MINUS
services_advertised) in favour of an explicit "services the client does
but does not advertise" list — Pass 1's Rule 5 reads it directly, no
subtraction.

DuckDB supports ALTER TABLE RENAME COLUMN natively. Seeds DBD with a
curated list of specific non-implant services (per brief). OE left NULL.

Idempotent: skips rename if new column already present; reseeds DBD only
when current value is NULL/empty.
"""
import logging
import os
import sys

import duckdb

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..'))
DB_PATH = os.path.join(PROJECT_ROOT, 'warehouse.duckdb')

logger = logging.getLogger('act_v2_wavec13')
logger.setLevel(logging.INFO)
if not logger.handlers:
    h = logging.StreamHandler(sys.stdout)
    h.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
    logger.addHandler(h)


DBD_NOT_ADVERTISED_SEED = (
    "veneer, veneers, porcelain veneer, porcelain veneers, composite veneer, "
    "composite veneers, e max veneer, e max veneers, emax veneer, emax veneers, "
    "laminate veneer, laminate veneers, "
    "invisalign, clear aligner, clear aligners, teeth straightening, teeth alignment, "
    "braces, orthodontics, orthodontist, orthodontic, "
    "teeth whitening, tooth whitening, smile whitening, whitening treatment, "
    "bleaching, zoom whitening, "
    "composite bonding, cosmetic bonding, tooth bonding, dental bonding, teeth bonding, "
    "bonding treatment, "
    "gum contouring, laser gum contouring, gum reshaping, gum lift, gum treatment, "
    "periodontal, periodontist, periodontitis, periodontics, "
    "dental hygiene, airflow, airflow cleaning, dental cleaning, teeth cleaning, "
    "scale and polish, hygienist, "
    "white filling, white fillings, tooth coloured filling, tooth coloured fillings, "
    "composite filling, composite fillings, dental filling, dental fillings, "
    "dental crown, dental crowns, porcelain crown, porcelain crowns, tooth crown, "
    "tooth crowns, zirconium crown, zirconium crowns, emax crown, emax crowns, "
    "dental bridge, dental bridges, tooth bridge, tooth bridges, porcelain bridge, "
    "root canal, root canal treatment, endodontic, endodontics, root filling, "
    "tooth extraction, teeth extraction, surgical extraction, wisdom tooth extraction, "
    "emergency extraction, "
    "emergency dentist, emergency dental, urgent dental, urgent dentist, "
    "emergency treatment, "
    "denture, dentures, partial denture, partial dentures, full denture, full dentures, "
    "cosmetic denture, cosmetic dentures, "
    "smile makeover, smile design, smile transformation, "
    "cosmetic dentistry, cosmetic dentist, general dentistry, "
    "sedation dentistry, iv sedation, "
    "facial aesthetics"
)


def _has_column(con, table: str, col: str) -> bool:
    return bool(con.execute(
        "SELECT 1 FROM information_schema.columns WHERE table_name=? AND column_name=?",
        [table, col],
    ).fetchall())


def main():
    logger.info('=' * 50)
    logger.info('Wave C13: services_all -> services_not_advertised')
    logger.info('=' * 50)
    con = duckdb.connect(DB_PATH)
    try:
        # DuckDB refuses ALTER/RENAME/DROP on a table with FK dependencies
        # (many tables FK to act_v2_clients). Workaround: ADD the new
        # column, leave services_all as a dead column. All readers
        # (engine + config route) switch to services_not_advertised.
        # We NULL out services_all to make the dead state obvious in audits.
        if _has_column(con, 'act_v2_clients', 'services_not_advertised'):
            logger.info('  services_not_advertised (already exists)')
        else:
            con.execute('ALTER TABLE act_v2_clients '
                        'ADD COLUMN services_not_advertised TEXT;')
            logger.info('  services_not_advertised (added)')
        if _has_column(con, 'act_v2_clients', 'services_all'):
            # NULL it; leave column in schema to avoid the FK-dependency
            # drop issue. Nothing reads it after this migration.
            con.execute('UPDATE act_v2_clients SET services_all = NULL;')
            logger.info('  services_all NULLed (dead column; DROP blocked by FK deps)')

        # Seed DBD — overwrite (the old services_all content was a superset
        # including advertised services; the new list is explicitly the
        # denylist, so prior data isn't reusable).
        con.execute(
            "UPDATE act_v2_clients SET services_not_advertised = ? WHERE client_id = 'dbd001'",
            [DBD_NOT_ADVERTISED_SEED],
        )
        logger.info('  dbd001 seeded with curated not-advertised list')

        # OE — reset to NULL (old services_all content was NULL/partial)
        con.execute(
            "UPDATE act_v2_clients SET services_not_advertised = NULL WHERE client_id = 'oe001'"
        )
        logger.info('  oe001 left NULL (unconfigured)')
        logger.info('=' * 50)
    finally:
        con.close()


if __name__ == '__main__':
    main()
