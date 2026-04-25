"""N4 — PMax CSV ingestion CLI.

Google Ads API's campaign_search_term_insight resource returns NULL cost
for every PMax term (the metric is prohibited on that resource). The GAds
UI's scheduled "Search terms report" CSV export DOES contain real cost,
conversions and conversion value per term. This CLI ingests that CSV into
the warehouse so the existing negatives engine picks up real PMax cost
data without any engine-code change.

Usage:
    python -m act_dashboard.data_pipeline.pmax_csv_ingest \\
        --client-id dbd001 \\
        --file "C:/Users/User/Downloads/Search terms report (8).csv"

Behaviour:
  1. Detect encoding (UTF-16 BOM, else UTF-8 with possible BOM).
  2. Detect delimiter (tab vs comma — count in header row).
  3. Parse row 2 for the date ("DD Month YYYY - DD Month YYYY"). Only
     single-day reports are accepted; cross-day reports abort with a
     clear error.
  4. Read rows from header onwards. Rows whose first column starts with
     "Total:" go to the totals bucket (one of them populates the Other
     bucket cost we've been missing); everything else is a per-term row.
  5. Per-term rows: insert into raw_pmax_search_term_csv; upsert the
     PMax slice of act_v2_search_terms (DELETE WHERE campaign_type =
     'PERFORMANCE_MAX' + INSERT).
  6. Totals: upsert the Other-bucket cost for this (client, date).
  7. Idempotent: re-running on the same file delete-then-inserts, so
     counts stay stable and there's no duplication.

Search campaign ingestion (API) is unchanged — this script only touches
PMax rows in act_v2_search_terms and the Other bucket.
"""
import argparse
import csv
import logging
import os
import re
import sys
from datetime import datetime
from decimal import Decimal, InvalidOperation

import duckdb

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))
DB_PATH = os.path.join(PROJECT_ROOT, 'warehouse.duckdb')

logger = logging.getLogger('pmax_csv_ingest')
logger.setLevel(logging.INFO)
_fmt = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
if not logger.handlers:
    _sh = logging.StreamHandler(sys.stdout)
    _sh.setFormatter(_fmt)
    logger.addHandler(_sh)


# ---------------------------------------------------------------------------
# Low-level parsing helpers
# ---------------------------------------------------------------------------
_MONTHS = {
    'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
    'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12,
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'jun': 6, 'jul': 7, 'aug': 8, 'sep': 9,
    'sept': 9, 'oct': 10, 'nov': 11, 'dec': 12,
}


def _detect_encoding(path: str) -> str:
    """UTF-16 if a BOM is present (both LE and BE), UTF-8 with optional BOM
    otherwise. Covers the two shapes Chris has seen: manual download
    (UTF-8 + comma) vs scheduled-email link (UTF-16 + tab)."""
    with open(path, 'rb') as f:
        head = f.read(4)
    if head[:2] in (b'\xff\xfe', b'\xfe\xff'):
        return 'utf-16'
    # utf-8-sig strips a leading BOM if present, plain UTF-8 otherwise.
    return 'utf-8-sig'


def _detect_delimiter(line: str) -> str:
    """Tab vs comma based on the header line's counts. Fall back to comma
    when tied at zero (pathological, but avoids crashing on an empty row)."""
    tabs = line.count('\t')
    commas = line.count(',')
    return '\t' if tabs > commas else ','


def _parse_report_date(title_line: str) -> str:
    """Accept a single-day range like '22 April 2026 - 22 April 2026' (or the
    same with en-dash / slash variants Google sometimes emits). Raise on
    multi-day ranges — the scheduler splits by campaign/day so the correct
    ingest is one CSV per day per client."""
    s = (title_line or '').strip().replace('\u2013', '-').replace('\u2014', '-')
    # Match 'DD Mon[th] YYYY' pairs separated by ' - '
    m = re.match(
        r'^\s*(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})\s*-\s*(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})\s*$',
        s,
    )
    if not m:
        raise ValueError(
            f"Could not parse report date from row 2: {title_line!r}. "
            f"Expected 'DD Month YYYY - DD Month YYYY'."
        )
    d1, mo1, y1, d2, mo2, y2 = m.groups()
    try:
        start = datetime(int(y1), _MONTHS[mo1.lower()], int(d1)).date()
        end = datetime(int(y2), _MONTHS[mo2.lower()], int(d2)).date()
    except (KeyError, ValueError) as e:
        raise ValueError(f"Bad date in row 2: {title_line!r} — {e}")
    if start != end:
        raise ValueError(
            f"CSV covers a date range ({start} to {end}), not a single day. "
            f"Re-export the report as a one-day window before ingesting."
        )
    return start.isoformat()


def _clean_number_str(raw) -> str | None:
    """Return a stripped string suitable for Decimal parsing, or None when the
    cell is empty / '--' / '" --"' / a literal dash. Google's CSV uses ' --'
    (leading space) for N/A and ',' as a thousands separator inside quoted
    cells — handle both."""
    if raw is None:
        return None
    s = str(raw).strip()
    if not s or s in ('--', '-', '—'):
        return None
    # Strip currency symbols, commas (thousands), %, surrounding quotes
    s = s.replace(',', '').replace('£', '').replace('$', '').replace('€', '')
    s = s.replace('%', '').strip()
    if not s:
        return None
    return s


def _to_decimal(raw) -> Decimal | None:
    s = _clean_number_str(raw)
    if s is None:
        return None
    try:
        return Decimal(s)
    except (InvalidOperation, ValueError):
        return None


def _to_int(raw) -> int | None:
    d = _to_decimal(raw)
    if d is None:
        return None
    try:
        return int(d)
    except (ValueError, OverflowError):
        return None


def _to_ratio(raw) -> Decimal | None:
    """Percent cells ('12.86%') arrive without the % after _clean_number_str;
    divide by 100 so what we store is a fraction (matches the API-ingested
    shape where ctr/conversion_rate are fractions)."""
    s = _clean_number_str(raw)
    if s is None:
        return None
    try:
        return Decimal(s) / Decimal(100)
    except (InvalidOperation, ValueError):
        return None


# ---------------------------------------------------------------------------
# Campaign resolution
# ---------------------------------------------------------------------------
def _resolve_pmax_campaigns(con, client_id: str, snapshot_date: str) -> list[tuple[str, str]]:
    """Return [(campaign_id, campaign_name), …] for active PMax campaigns on
    this snapshot_date. Used as the fallback when the CSV doesn't carry a
    Campaign column (the manual single-campaign export shape)."""
    import json
    rows = con.execute(
        """SELECT entity_id, entity_name, metrics_json
           FROM act_v2_snapshots
           WHERE client_id = ? AND snapshot_date = ? AND level = 'campaign'""",
        [client_id, snapshot_date],
    ).fetchall()
    out = []
    for eid, name, mjson in rows:
        try:
            meta = json.loads(mjson) if isinstance(mjson, str) else mjson
        except Exception:
            continue
        if (meta or {}).get('campaign_type') == 'PERFORMANCE_MAX':
            out.append((eid, name))
    return out


def _load_role_name_to_id(con, client_id: str) -> dict[str, str]:
    """Map campaign_name (lower) → google_ads_campaign_id via
    act_v2_campaign_roles (the canonical per-client name registry)."""
    rows = con.execute(
        """SELECT campaign_name, google_ads_campaign_id
           FROM act_v2_campaign_roles
           WHERE client_id = ? AND campaign_name IS NOT NULL""",
        [client_id],
    ).fetchall()
    return {(n or '').strip().lower(): cid for n, cid in rows if n}


# ---------------------------------------------------------------------------
# Main ingestion
# ---------------------------------------------------------------------------
def ingest(path: str, client_id: str) -> dict:
    if not os.path.exists(path):
        raise FileNotFoundError(f"CSV not found: {path}")

    encoding = _detect_encoding(path)
    logger.info(f"Encoding detected: {encoding}")

    with open(path, 'r', encoding=encoding, newline='') as f:
        raw_lines = f.read().splitlines()

    if len(raw_lines) < 4:
        raise ValueError(
            f"CSV has fewer than 4 rows ({len(raw_lines)}); expected "
            f"title / date / header / ≥1 data row."
        )

    # Row 1 = title, Row 2 = date range, Row 3 = header, Row 4+ = data / totals
    title = raw_lines[0]
    date_line = raw_lines[1]
    header_line = raw_lines[2]

    delimiter = _detect_delimiter(header_line)
    logger.info(f"Delimiter detected: {delimiter!r}")

    snapshot_date = _parse_report_date(date_line)
    logger.info(f"Report title: {title!r} / date: {snapshot_date}")

    # csv.reader over the remaining lines — respects quoted fields with
    # embedded commas (Google quotes "1,205" impressions).
    reader = csv.reader(raw_lines[2:], delimiter=delimiter)
    header = next(reader)
    header_norm = [h.strip() for h in header]
    idx = {h: i for i, h in enumerate(header_norm)}

    # Required columns — search_term is mandatory; the rest are resolved
    # defensively via .get() so missing optional cols fall back to None.
    if 'Search term' not in idx:
        raise ValueError(
            f"CSV header missing required column 'Search term'. "
            f"Found columns: {header_norm}"
        )

    def cell(row, name):
        i = idx.get(name)
        if i is None or i >= len(row):
            return None
        return row[i]

    term_rows = []  # dicts per per-term row
    totals = {}     # 'Total: Search terms' / 'Total: Other search terms' / 'Total: Campaign' → dict
    for raw_row in reader:
        if not raw_row or not any((c or '').strip() for c in raw_row):
            continue
        term = (cell(raw_row, 'Search term') or '').strip()
        if not term:
            continue
        if term.startswith('Total:'):
            totals[term] = raw_row
            continue
        # Defensive filter: if the CSV ever carries a Campaign type column
        # OR the Match type column serves as the type label (as in the
        # manual export shape), skip non-PMax rows.
        ctype = (cell(raw_row, 'Campaign type') or '').strip().lower()
        mtype = (cell(raw_row, 'Match type') or '').strip().lower()
        if ctype:
            if ctype != 'performance max':
                continue
        elif mtype and mtype != 'performance max':
            # No Campaign type column, and Match type isn't PMax-labeled →
            # this CSV is Search or mixed; skip defensively.
            continue
        term_rows.append(raw_row)

    logger.info(f"Parsed {len(term_rows)} per-term rows + {len(totals)} totals row(s)")

    # ------------------------------------------------------------------
    # DB writes — DELETE+INSERT for full idempotency
    # ------------------------------------------------------------------
    try:
        con = duckdb.connect(DB_PATH)
    except duckdb.IOException:
        logger.error("DuckDB is locked. Stop the Flask app first: "
                     "taskkill /IM python.exe /F")
        raise

    try:
        # Resolve a default (campaign_id, campaign_name) pair. If the CSV
        # has a Campaign column we'll prefer it per-row; otherwise we
        # fallback to the single PMax campaign for this client/date.
        name_to_id = _load_role_name_to_id(con, client_id)
        pmax_campaigns = _resolve_pmax_campaigns(con, client_id, snapshot_date)
        default_campaign_id = pmax_campaigns[0][0] if pmax_campaigns else None
        default_campaign_name = pmax_campaigns[0][1] if pmax_campaigns else None
        if default_campaign_id is None:
            logger.warning(
                f"No active PMax campaign in act_v2_snapshots for "
                f"{client_id}@{snapshot_date}. campaign_id will be NULL "
                f"for any row whose Campaign name isn't in act_v2_campaign_roles."
            )

        unknown_campaigns = set()

        def resolve_campaign(row):
            name = (cell(row, 'Campaign') or '').strip()
            if name:
                cid = name_to_id.get(name.lower())
                if cid:
                    return cid, name
                unknown_campaigns.add(name)
                return (default_campaign_id, name or default_campaign_name)
            return (default_campaign_id, default_campaign_name)

        # -------- 1. raw_pmax_search_term_csv (archival, full fidelity)
        con.execute(
            """DELETE FROM raw_pmax_search_term_csv
               WHERE client_id = ? AND snapshot_date = ?""",
            [client_id, snapshot_date],
        )
        raw_inserts = []
        source_file = os.path.basename(path)
        seen_terms = set()
        dupes_in_file = 0
        for row in term_rows:
            term = (cell(row, 'Search term') or '').strip()
            if term in seen_terms:
                # Google occasionally emits the same term twice when a
                # campaign ran it under two different match types; keep
                # the first (highest cost tends to come first) and drop
                # subsequent duplicates to satisfy the PK.
                dupes_in_file += 1
                continue
            seen_terms.add(term)
            campaign_id, campaign_name = resolve_campaign(row)
            raw_inserts.append((
                client_id, snapshot_date,
                campaign_id, campaign_name,
                (cell(row, 'Campaign type') or 'Performance Max'),
                term,
                cell(row, 'Match type'),
                cell(row, 'Added/Excluded'),
                _to_decimal(cell(row, 'Cost')),
                _to_int(cell(row, 'Impr.')),
                _to_int(cell(row, 'Clicks')),
                _to_decimal(cell(row, 'Avg. CPC')),
                _to_ratio(cell(row, 'CTR')),
                cell(row, 'Device click summary'),
                _to_decimal(cell(row, 'Conversions')),
                _to_decimal(cell(row, 'Cost / conv.')),
                _to_ratio(cell(row, 'Conv. rate')),
                _to_decimal(cell(row, 'Conv. value')),
                _to_decimal(cell(row, 'Conv. value / cost')),
                cell(row, 'Currency code'),
                source_file,
            ))
        if raw_inserts:
            con.executemany(
                """INSERT INTO raw_pmax_search_term_csv
                   (client_id, snapshot_date, campaign_id, campaign_name,
                    campaign_type, search_term, match_type, added_excluded,
                    cost, impressions, clicks, avg_cpc, ctr,
                    device_click_summary, conversions, cost_per_conversion,
                    conversion_rate, conversion_value, conversion_value_per_cost,
                    currency, source_file)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                raw_inserts,
            )

        if dupes_in_file:
            logger.warning(
                f"Dropped {dupes_in_file} duplicate (same search_term) row(s) "
                f"while loading raw_pmax_search_term_csv."
            )
        if unknown_campaigns:
            logger.warning(
                f"CSV referenced {len(unknown_campaigns)} campaign name(s) not "
                f"found in act_v2_campaign_roles; fell back to default "
                f"campaign_id={default_campaign_id}. Names: "
                f"{sorted(unknown_campaigns)[:5]}"
                f"{' …' if len(unknown_campaigns) > 5 else ''}"
            )

        # -------- 2. act_v2_search_terms — replace the PMax slice for this day
        con.execute(
            """DELETE FROM act_v2_search_terms
               WHERE client_id = ? AND snapshot_date = ?
                 AND campaign_type = 'PERFORMANCE_MAX'""",
            [client_id, snapshot_date],
        )
        st_inserts = []
        for ins in raw_inserts:
            (_cid, _sd, campaign_id, campaign_name, _ctype, term,
             match_type, added_excl,
             cost, impressions, clicks, avg_cpc, ctr,
             _dev, conversions, cost_per_conv, conv_rate,
             conv_value, _cvpc, _cur, _sf) = ins
            if not campaign_id:
                # Skip terms that can't be attributed to a campaign — they
                # would violate act_v2_search_terms.campaign_id NOT NULL.
                continue
            status = added_excl if (added_excl and added_excl.strip() not in ('--', '-', '—')) else None
            st_inserts.append((
                client_id, snapshot_date,
                campaign_id, campaign_name,
                term,
                _round(cost, 2),
                impressions, clicks,
                _round(conversions, 2),
                _round(conv_value, 2),
                _round(ctr, 6),
                _round(avg_cpc, 2),
                _round(cost_per_conv, 2),
                _round(conv_rate, 4),
                status,
            ))
        if st_inserts:
            con.executemany(
                """INSERT INTO act_v2_search_terms
                   (client_id, snapshot_date, campaign_id, campaign_name,
                    campaign_type, ad_group_id, ad_group_name, search_term,
                    match_type, keyword_text, keyword_id,
                    cost, impressions, clicks, conversions, conversion_value,
                    ctr, avg_cpc, cost_per_conversion, conversion_rate,
                    status)
                   VALUES (?, ?, ?, ?, 'PERFORMANCE_MAX',
                           'PMAX_ASSET_GROUP', 'PMAX_ASSET_GROUP', ?,
                           'PMAX', NULL, NULL,
                           ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                st_inserts,
            )

        # -------- 3. act_v2_pmax_other_bucket — fill in the real cost
        other_row = totals.get('Total: Other search terms')
        other_summary = None
        if other_row is not None:
            # Resolve campaign_id for this Other row. The CSV's Total row
            # doesn't carry a per-campaign attribution in the single-
            # campaign export shape, so fall back to the day's PMax
            # campaign. If a Campaign column IS present and populated,
            # honour it.
            campaign_id, campaign_name = resolve_campaign(other_row)
            if campaign_id is None and default_campaign_id:
                campaign_id, campaign_name = default_campaign_id, default_campaign_name
            if campaign_id is None:
                logger.warning(
                    "Other-bucket row has no resolvable campaign_id; skipping."
                )
            else:
                con.execute(
                    """DELETE FROM act_v2_pmax_other_bucket
                       WHERE client_id = ? AND snapshot_date = ? AND campaign_id = ?""",
                    [client_id, snapshot_date, str(campaign_id)],
                )
                cost = _to_decimal(cell(other_row, 'Cost'))
                impressions = _to_int(cell(other_row, 'Impr.'))
                clicks = _to_int(cell(other_row, 'Clicks'))
                conversions = _to_decimal(cell(other_row, 'Conversions'))
                con.execute(
                    """INSERT INTO act_v2_pmax_other_bucket
                       (client_id, snapshot_date, campaign_id, campaign_name,
                        impressions, clicks, cost, conversions, distinct_term_count)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, NULL)""",
                    [client_id, snapshot_date, str(campaign_id), campaign_name,
                     impressions, clicks, _round(cost, 2), _round(conversions, 2)],
                )
                other_summary = {
                    'impressions': impressions, 'clicks': clicks,
                    'cost': cost, 'conversions': conversions,
                    'campaign_id': campaign_id, 'campaign_name': campaign_name,
                }

        # -------- Summary log
        total_term_cost = sum(
            (i[8] or Decimal(0)) for i in raw_inserts  # raw_inserts[8] = Cost
        )
        logger.info(
            f"Ingested {len(st_inserts)} PMax terms for client={client_id}, "
            f"date={snapshot_date}, total cost £{total_term_cost} "
            f"(from per-term rows); from file={source_file}. "
            f"Other bucket: "
            f"{(other_summary or {}).get('impressions')} impr / "
            f"£{(other_summary or {}).get('cost')} cost updated."
        )
        return {
            'client_id': client_id,
            'snapshot_date': snapshot_date,
            'raw_rows': len(raw_inserts),
            'search_term_rows_inserted': len(st_inserts),
            'total_cost_from_terms': str(total_term_cost),
            'other_bucket': other_summary,
            'unknown_campaigns': sorted(unknown_campaigns),
            'duplicates_dropped': dupes_in_file,
        }
    finally:
        con.close()


# ---------------------------------------------------------------------------
# Public API for watcher / other importers (Fix 1.6)
# ---------------------------------------------------------------------------
def ingest_csv(file_path: str, client_id: str) -> dict:
    """Brief-compliant alias for ingest(). Same return shape.

    Watcher code imports this name; the pre-existing CLI keeps using
    ingest() so legacy callers don't break.
    """
    return ingest(file_path, client_id)


def validate_search_terms_csv(file_path: str) -> tuple[bool, str | None]:
    """Cheap pre-flight: open the file in detected encoding, confirm row 1
    contains 'Search terms report' (case-insensitive). Returns
    (ok, reason_if_not).

    Used by the watcher to filter out files that match the glob but aren't
    actually GAds Search-terms exports (e.g. a user's own spreadsheet
    happened to have a similar name).
    """
    try:
        encoding = _detect_encoding(file_path)
        with open(file_path, 'r', encoding=encoding, newline='') as f:
            first = f.readline()
    except Exception as e:
        return False, f"could not read file: {e}"
    if 'search terms report' not in (first or '').lower():
        return False, (
            f"row 1 doesn't look like a Search-terms-report header: "
            f"{first!r}"
        )
    return True, None


def detect_client_from_csv(file_path: str, db_path: str | None = None) -> str | None:
    """Best-effort client_id detection from CSV content.

    Reads the Campaign column (if present), looks up each name in
    act_v2_campaign_roles across all clients, returns the first matching
    client_id. Returns None when:
      - CSV has no Campaign column (single-campaign manual export shape)
      - no Campaign name matches any client's role registry
      - DB unreachable

    The watcher uses this for routing on multi-client setups. Today only
    DBD is onboarded so the watcher can fall back to a configured default.
    """
    db = db_path or DB_PATH
    try:
        encoding = _detect_encoding(file_path)
        with open(file_path, 'r', encoding=encoding, newline='') as f:
            raw_lines = f.read().splitlines()
    except Exception:
        return None
    if len(raw_lines) < 4:
        return None
    delimiter = _detect_delimiter(raw_lines[2])
    reader = csv.reader(raw_lines[2:], delimiter=delimiter)
    try:
        header = next(reader)
    except StopIteration:
        return None
    header_norm = [h.strip() for h in header]
    if 'Campaign' not in header_norm:
        return None
    campaign_idx = header_norm.index('Campaign')
    seen_names = set()
    for row in reader:
        if len(row) <= campaign_idx:
            continue
        name = (row[campaign_idx] or '').strip().lower()
        if not name or name.startswith('total:'):
            continue
        seen_names.add(name)
        if len(seen_names) >= 50:  # cap; we only need a couple of hits
            break
    if not seen_names:
        return None
    try:
        con = duckdb.connect(db, read_only=True)
    except duckdb.IOException:
        return None
    try:
        rows = con.execute(
            """SELECT DISTINCT client_id, LOWER(TRIM(campaign_name))
               FROM act_v2_campaign_roles
               WHERE campaign_name IS NOT NULL"""
        ).fetchall()
    finally:
        con.close()
    for client_id, cname in rows:
        if cname in seen_names:
            return client_id
    return None


def _round(val, places: int):
    if val is None:
        return None
    try:
        q = Decimal(10) ** -places
        return Decimal(val).quantize(q)
    except (InvalidOperation, ValueError):
        return None


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main(argv=None):
    p = argparse.ArgumentParser(description='Ingest a Google Ads PMax Search-terms CSV.')
    p.add_argument('--client-id', required=True, help='ACT client_id (e.g. dbd001)')
    p.add_argument('--file', required=True, help='Path to the CSV file to ingest')
    args = p.parse_args(argv)

    try:
        result = ingest(args.file, args.client_id)
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        sys.exit(2)

    # Friendly final summary on stdout
    print('-' * 60)
    print(f"client_id:            {result['client_id']}")
    print(f"snapshot_date:        {result['snapshot_date']}")
    print(f"raw_pmax_csv rows:    {result['raw_rows']}")
    print(f"act_v2_search_terms:  {result['search_term_rows_inserted']} PMax rows upserted")
    print(f"total per-term cost:  £{result['total_cost_from_terms']}")
    if result['other_bucket']:
        ob = result['other_bucket']
        print(f"other_bucket:         impr={ob['impressions']} clicks={ob['clicks']} cost=£{ob['cost']} conv={ob['conversions']}")
    if result['unknown_campaigns']:
        print(f"unknown campaigns:    {result['unknown_campaigns'][:5]}{' …' if len(result['unknown_campaigns']) > 5 else ''}")
    if result['duplicates_dropped']:
        print(f"duplicates dropped:   {result['duplicates_dropped']}")


if __name__ == '__main__':
    main()
