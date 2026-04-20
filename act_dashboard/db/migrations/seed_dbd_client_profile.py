"""N1a — Seed Dental by Design's 4 client-profile fields.

Writes:
 - services_all        (everything DBD does)
 - services_advertised (current ad scope = implants only; Pass 1 allowlist)
 - service_locations   (Layers 1 + 2 + 3 combined & deduped)
 - client_brand_terms  (brand-match protection list)

OE gets no seed — the 4 fields remain NULL and will be filled via /v2/config.

Idempotent: re-writing is safe (always overwrites the 4 columns for DBD).
Run: python -m act_dashboard.db.migrations.seed_dbd_client_profile
"""
import logging
import os
import sys

import duckdb

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..'))
DB_PATH = os.path.join(PROJECT_ROOT, 'warehouse.duckdb')

logger = logging.getLogger('seed_dbd_profile')
logger.setLevel(logging.INFO)
if not logger.handlers:
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
    logger.addHandler(sh)


# ---------------------------------------------------------------------------
# DBD seed content — lowercase, comma-separated on save
# ---------------------------------------------------------------------------
DBD_SERVICES_ALL = [
    'dental implants', 'single arch', 'double arch', 'full arch', 'teeth in a day',
    'all-on-4', 'all-on-6', 'bone grafting', 'sinus lift', 'soft tissue grafting',
    'cbct scan', '3d scan', 'intraoral scan', 'digital smile design',
    'general dentistry', 'cosmetic dentistry', 'preventive care', 'hygiene',
    'check up', 'check-up', 'endodontics', 'root canal', 'root canal treatment',
    'oral surgery', 'extraction', 'tooth extraction', 'surgical extraction',
    'sedation dentistry', 'iv sedation', 'invisalign', 'clear aligners',
    'orthodontics', 'veneers', 'crowns', 'bridges', 'dentures', 'fillings',
    'whitening', 'smile makeover',
]

DBD_SERVICES_ADVERTISED = [
    'dental implant', 'dental implants', 'implant', 'implants', 'tooth implant',
    'teeth implants', 'single implant', 'multiple implants', 'implant bridge',
    'implant crown', 'implant fixture', 'single arch', 'double arch', 'full arch',
    'full mouth', 'full arch implants', 'full mouth implants',
    'full mouth restoration', 'teeth in a day', 'teeth-in-a-day', 'all on 4',
    'all-on-4', 'all on 6', 'all-on-6', 'vivo bridge', 'vivo crown', 'vivo guided',
    'zirconia implant', 'ceramic implant', 'titanium implant', 'missing teeth',
    'missing tooth', 'tooth loss', 'replace missing teeth', 'teeth replacement',
    'tooth replacement', 'permanent teeth', 'fixed teeth', 'bone graft',
    'bone grafting', 'sinus lift', 'sinus elevation', 'implant cost',
    'implant price', 'implant consultation', 'implant dentist',
    'implant dentistry', 'implantology', 'osseointegration', 'abutment',
]

DBD_BRAND_TERMS = [
    'dental by design', 'dental by design hammersmith', 'dental by design london',
    'dentalbydesign', 'dentalbydesign.co.uk',
]

# Layer 1 — raw Google Ads targeting (270 terms: outcodes + named areas)
DBD_LAYER1 = [
    'al2', 'belgravia', 'br1', 'br2', 'br3', 'br4', 'br5', 'br6', 'br7', 'br8',
    'city of london', 'cm16', 'cr0', 'cr2', 'cr3', 'cr4', 'cr5', 'cr6', 'cr7',
    'cr8', 'da1', 'da14', 'da15', 'da16', 'da17', 'da2', 'da5', 'da6', 'da7',
    'da8', 'e1', 'e10', 'e11', 'e12', 'e13', 'e14', 'e15', 'e16', 'e17', 'e18',
    'e1w', 'e2', 'e20', 'e3', 'e4', 'e5', 'e6', 'e7', 'e8', 'e9', "earl's court",
    'en1', 'en2', 'en3', 'en4', 'en5', 'en6', 'en7', 'en9', 'ha0', 'ha1', 'ha2',
    'ha3', 'ha4', 'ha5', 'ha6', 'ha7', 'ha8', 'ha9', 'ig1', 'ig10', 'ig11',
    'ig2', 'ig3', 'ig6', 'ig7', 'ig8', 'ig9', 'kt1', 'kt10', 'kt11', 'kt12',
    'kt13', 'kt15', 'kt16', 'kt17', 'kt18', 'kt19', 'kt2', 'kt20', 'kt21',
    'kt22', 'kt3', 'kt4', 'kt5', 'kt6', 'kt7', 'kt8', 'kt9', 'marylebone',
    'mayfair', 'n1', 'n10', 'n11', 'n12', 'n13', 'n14', 'n15', 'n16', 'n17',
    'n18', 'n19', 'n2', 'n20', 'n21', 'n22', 'n3', 'n4', 'n5', 'n6', 'n7', 'n8',
    'n9', 'nw1', 'nw10', 'nw11', 'nw2', 'nw3', 'nw4', 'nw5', 'nw6', 'nw7', 'nw8',
    'nw9', 'rh1', 'rh2', 'rh8', 'rh9', 'rm1', 'rm10', 'rm11', 'rm12', 'rm13',
    'rm14', 'rm15', 'rm19', 'rm2', 'rm3', 'rm4', 'rm5', 'rm6', 'rm7', 'rm8',
    'rm9', 'se1', 'se10', 'se11', 'se12', 'se13', 'se14', 'se15', 'se16', 'se17',
    'se18', 'se19', 'se2', 'se20', 'se21', 'se22', 'se23', 'se24', 'se25', 'se26',
    'se27', 'se28', 'se3', 'se4', 'se5', 'se6', 'se7', 'se8', 'se9', 'sl0', 'sm1',
    'sm2', 'sm3', 'sm4', 'sm5', 'sm6', 'sm7', 'sw10', 'sw11', 'sw12', 'sw13',
    'sw14', 'sw15', 'sw16', 'sw17', 'sw18', 'sw19', 'sw1a', 'sw1p', 'sw1v', 'sw2',
    'sw20', 'sw3', 'sw4', 'sw6', 'sw7', 'sw8', 'sw9', 'tn14', 'tn16', 'tw1',
    'tw10', 'tw10 5hz', 'tw11', 'tw12', 'tw13', 'tw14', 'tw15', 'tw16', 'tw17',
    'tw18', 'tw19', 'tw2', 'tw20', 'tw3', 'tw4', 'tw5', 'tw6', 'tw7', 'tw8',
    'tw9', 'ub1', 'ub10', 'ub11', 'ub2', 'ub3', 'ub4', 'ub5', 'ub6', 'ub7', 'ub8',
    'ub9', 'w10', 'w11', 'w12', 'w13', 'w14', 'w2', 'w3', 'w4', 'w5', 'w6', 'w7',
    'w8', 'w9', 'wd17', 'wd18', 'wd19', 'wd23', 'wd24', 'wd25', 'wd3', 'wd4',
    'wd5', 'wd6', 'wd7', 'westminster',
]

# Layer 2 — London umbrella terms (11)
DBD_LAYER2 = [
    'london', 'greater london', 'central london', 'west london', 'north london',
    'south london', 'east london', 'north west london', 'south west london',
    'south east london', 'north east london',
]


def _dedupe(items):
    seen = set()
    out = []
    for it in items:
        v = it.strip().lower()
        if v and v not in seen:
            seen.add(v)
            out.append(v)
    return out


def main():
    from act_dashboard.data_pipeline.postcode_lookup import build_layer3

    logger.info('Building Layer 3 placenames via postcodes.io (cached)...')
    layer3, cache = build_layer3(DBD_LAYER1)
    logger.info(f'  Cache entries: {len(cache)}')
    logger.info(f'  Layer 3 placenames: {len(layer3)}')

    service_locations = _dedupe(DBD_LAYER1 + DBD_LAYER2 + layer3)
    logger.info(f'  service_locations total (L1+L2+L3 deduped): {len(service_locations)}')

    services_all = _dedupe(DBD_SERVICES_ALL)
    services_advertised = _dedupe(DBD_SERVICES_ADVERTISED)
    brand_terms = _dedupe(DBD_BRAND_TERMS)

    try:
        con = duckdb.connect(DB_PATH)
    except duckdb.IOException:
        logger.error('DB locked. Stop the Flask app first.')
        sys.exit(1)
    try:
        exists = con.execute(
            'SELECT 1 FROM act_v2_clients WHERE client_id = ?', ['dbd001']
        ).fetchone()
        if not exists:
            logger.error('dbd001 not found — run seed_dental_by_design first.')
            sys.exit(1)
        con.execute("""
            UPDATE act_v2_clients SET
                services_all = ?,
                services_advertised = ?,
                service_locations = ?,
                client_brand_terms = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE client_id = 'dbd001'
        """, [
            ', '.join(services_all),
            ', '.join(services_advertised),
            ', '.join(service_locations),
            ', '.join(brand_terms),
        ])
        logger.info('DBD client profile fields populated.')
    finally:
        con.close()


if __name__ == '__main__':
    main()
