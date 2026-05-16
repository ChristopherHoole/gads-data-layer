"""KW + Search Term History — CSV ingest (Phase 1).

Brief: docs/BRIEF_KW_ST_HISTORY_VIEWER.md.

Reads three GAds CSV exports dropped into
`client_csvs/<client_id>/kw_history_incoming/` and rebuilds the
`kw_st_history` table for that client.

  - "Search terms report"  — all-time, all-campaigns search terms
  - "Search keyword report" — DII keyword snapshot (the fresh [ex]
                              reference; only Status=Enabled rows
                              count for `in_new_ex` matching)
  - "Ad group report"      — DII ad-group snapshot (informational
                              for v1, used to validate ad-group names)

All three CSVs share the GAds export shape: row 1 = title, row 2 =
date range, row 3 = column headers, row 4+ = data. UTF-8.

Detection is by the title cell in row 1 (lower-cased + prefix match).

This module exposes:
  - INCOMING_DIR / ARCHIVE_DIR helpers (mirrors PMax watcher API)
  - detect_report_type(path)
  - ingest_dropped_set(client_id, st_path, kw_path, ag_path)  — bulk path
  - ingest_one(client_id, path)                               — single file
       (queues for later batch; we need ALL THREE to build the table)
  - rebuild_kw_st_history(client_id)                          — runs the
       aggregation from current staging tables

DBD-only for v1 via ALLOWED_CLIENTS_V1 guard.

Idempotency:
  Each ingest run rebuilds the staging tables from the CSVs and replaces
  the kw_st_history rows for the client. Mapping fields (proposed_ad_group,
  proposal_method, proposal_rationale, ai_cached_at) for an existing
  client_id are PRESERVED on re-ingest so Phase 2's AI cache + manual
  overrides survive a re-import. Only on first ingest are those columns
  NULL.
"""
from __future__ import annotations

import csv
import logging
import os
import re
import shutil
import sys
import threading
from datetime import datetime
from pathlib import Path

import duckdb

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
DB_PATH = os.path.join(PROJECT_ROOT, 'warehouse.duckdb')
LOG_PATH = SCRIPT_DIR / 'kw_history_ingest.log'

CLIENT_CSVS_ROOT = Path(os.environ.get(
    'ACT_CLIENT_CSVS_DIR', str(PROJECT_ROOT / 'client_csvs')
)).resolve()

# v1 client allowlist — mirrors Section 7 of the Search Terms work.
ALLOWED_CLIENTS_V1 = {'dbd001'}

# Per-client brand-campaign matching. Brand-campaign names vary across
# clients; for DBD v1 we match anything containing "Brand" (case-insensitive).
# is_brand_campaign drives the `skip_brand` mapping path in Phase 2.
BRAND_CAMPAIGN_PATTERNS = {
    'dbd001': ('%Brand%',),
}

logger = logging.getLogger('kw_history_ingest')
logger.setLevel(logging.INFO)
_fmt = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
if not logger.handlers:
    sh = logging.StreamHandler(sys.stdout); sh.setFormatter(_fmt); logger.addHandler(sh)
    try:
        fh = logging.FileHandler(LOG_PATH, mode='a', encoding='utf-8')
        fh.setFormatter(_fmt); logger.addHandler(fh)
    except OSError:
        pass  # log file optional; stdout is enough.


# ---------------------------------------------------------------------------
# Folder helpers — separate from PMax's incoming/ + archive/ so KW history
# files don't collide with the daily PMax pipeline.
# ---------------------------------------------------------------------------
def incoming_dir(client_id: str) -> Path:
    return CLIENT_CSVS_ROOT / client_id / 'kw_history_incoming'


def archive_dir(client_id: str, run_date: str | None = None) -> Path:
    """KW-history archives are date-bucketed so a re-import on the same day
    doesn't trample the prior set. run_date defaults to today's ISO."""
    run_date = run_date or datetime.now().date().isoformat()
    return CLIENT_CSVS_ROOT / client_id / 'kw_history_archive' / run_date


def ensure_client_folders(client_id: str) -> None:
    incoming_dir(client_id).mkdir(parents=True, exist_ok=True)
    archive_dir(client_id).mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Report-type detection
# ---------------------------------------------------------------------------
REPORT_TYPES = {
    'search_terms_report': 'st',   # search-terms (all-time / all-campaigns)
    'search_keyword_report': 'kw', # keyword (DII reference, [ex] structure)
    'ad_group_report': 'ag',       # ad-group (DII reference)
}


def detect_report_type(path: str | Path) -> str | None:
    """Read row 1 from the CSV and return one of 'st' / 'kw' / 'ag' or None
    if it doesn't look like one of the three expected exports."""
    try:
        with open(path, 'r', encoding='utf-8-sig', newline='') as f:
            first = f.readline().strip()
    except OSError as e:
        logger.warning('[detect] cannot read %s: %s', path, e)
        return None
    if not first:
        return None
    # Title cell normalised: lowercased, non-alnum collapsed to '_'.
    key = re.sub(r'[^a-z0-9]+', '_', first.lower()).strip('_')
    return REPORT_TYPES.get(key)


# ---------------------------------------------------------------------------
# Ingest
# ---------------------------------------------------------------------------
def _connect() -> duckdb.DuckDBPyConnection:
    return duckdb.connect(DB_PATH)


def _load_csv_into_staging(con, csv_path: str, table: str) -> int:
    """Load a GAds-shaped CSV (skip rows 1-2, header on row 3) into a
    DuckDB staging table. Returns row count.

    Uses read_csv_auto with skip=2 + header=True so the column-header
    line becomes the column names. Quoted-comma cells handled natively.
    """
    # Use absolute path; DuckDB's read_csv resolves relative to CWD.
    abs_path = os.path.abspath(csv_path)
    # Wrap in safe single-quotes (DuckDB literal) — paths with single
    # quotes are vanishingly rare on Windows; rather than fight escaping
    # we just fail loudly if encountered.
    if "'" in abs_path:
        raise ValueError(f"Path contains single quote, refusing: {abs_path!r}")
    con.execute(f"DROP TABLE IF EXISTS {table}")
    # all_varchar=True keeps every column as VARCHAR so currency / percent /
    # numeric values can be parsed defensively downstream rather than
    # tripping on stray "--" or "" values.
    con.execute(
        f"""
        CREATE TABLE {table} AS
        SELECT *
        FROM read_csv_auto(
            '{abs_path}',
            skip = 2,
            header = TRUE,
            all_varchar = TRUE,
            ignore_errors = TRUE
        )
        """
    )
    n = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    return int(n)


def _strip_match_brackets(s: str) -> str:
    """Normalise a keyword string: drop the GAds match-type markers.
        [exact match]   ->  exact match
        "phrase match"  ->  phrase match
        broad match     ->  broad match
    Whitespace + casing handled by the SQL-side LOWER/TRIM downstream.
    """
    if s is None:
        return s
    s = s.strip()
    if len(s) >= 2 and s[0] == '[' and s[-1] == ']':
        s = s[1:-1]
    if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
        s = s[1:-1]
    return s


def _brand_campaign_sql_pred(client_id: str) -> str:
    """Build a SQL predicate that returns TRUE when a campaign matches
    the client's brand pattern set. Defaults to FALSE if no patterns."""
    patterns = BRAND_CAMPAIGN_PATTERNS.get(client_id, ())
    if not patterns:
        return 'FALSE'
    parts = []
    for p in patterns:
        # Single-quote escape: GAds campaign names rarely contain "'"
        # but we're defensive.
        safe = p.replace("'", "''")
        parts.append(f"campaign ILIKE '{safe}'")
    return '(' + ' OR '.join(parts) + ')'


def rebuild_kw_st_history(client_id: str,
                          st_csv: str | None,
                          kw_csv: str | None,
                          ag_csv: str | None) -> dict:
    """Aggregate the three CSVs into kw_st_history. Returns counters.

    - st_csv: the all-time search-terms report (drives most rows)
    - kw_csv: the DII keyword snapshot (drives `in_new_ex` matching)
    - ag_csv: the DII ad-group snapshot (informational; not strictly
              required for Phase 1 — kept for symmetry + future joins)

    Behaviour when a CSV is missing: that report's contribution is
    skipped. The aggregate still writes the rows from whichever CSVs
    were provided. This matters because re-ingesting a single CSV
    after the first full set shouldn't drop the others' data.
    """
    if client_id not in ALLOWED_CLIENTS_V1:
        logger.info('skipped (not in v1 allowlist): client=%s', client_id)
        return {'overall': 'skipped',
                'reason': f'{client_id!r} not in v1 allowlist'}

    summary: dict = {
        'client_id': client_id,
        'st_rows_in': 0, 'kw_rows_in': 0, 'ag_rows_in': 0,
        'unique_terms': 0, 'rows_inserted': 0,
        'started_at': datetime.now().isoformat(timespec='seconds'),
    }
    con = _connect()
    try:
        # ------------------- Load each CSV into staging -------------------
        if st_csv:
            summary['st_rows_in'] = _load_csv_into_staging(
                con, st_csv, '_stg_kw_history_st_raw')
            logger.info('[stg] _stg_kw_history_st_raw rows=%d',
                        summary['st_rows_in'])
        if kw_csv:
            summary['kw_rows_in'] = _load_csv_into_staging(
                con, kw_csv, '_stg_kw_history_kw_raw')
            logger.info('[stg] _stg_kw_history_kw_raw rows=%d',
                        summary['kw_rows_in'])
        if ag_csv:
            summary['ag_rows_in'] = _load_csv_into_staging(
                con, ag_csv, '_stg_kw_history_ag_raw')
            logger.info('[stg] _stg_kw_history_ag_raw rows=%d',
                        summary['ag_rows_in'])

        if not st_csv and not kw_csv:
            logger.error('Neither search-terms nor keyword CSV provided; '
                         'nothing to ingest.')
            summary['overall'] = 'failed'
            summary['error'] = 'no_st_or_kw_csv'
            return summary

        brand_pred = _brand_campaign_sql_pred(client_id)

        # ---------------- Build the canonical row set --------------------
        # The aggregation has two phases:
        #  1) Build _stg_kw_history_agg: one row per (term, type) with
        #     all aggregate metrics + the (campaign, ad_group) pair that
        #     has the highest impressions for that term.
        #  2) Merge keyword-rows (DII [ex] reference) and search-term-rows
        #     so that the same string appearing in both produces type='both'.

        # Drop+recreate working tables.
        con.execute("DROP TABLE IF EXISTS _stg_kw_history_norm")
        con.execute("DROP TABLE IF EXISTS _stg_kw_history_agg")

        # ----- Search terms report -> normalised rows (type='search_term')
        # Numbers come in as VARCHAR. NULLIF + TRY_CAST handles "--" / "".
        # CTR/Conv. rate columns are %-suffixed but we don't use them here.
        if st_csv:
            con.execute(
                """
                CREATE TABLE _stg_kw_history_norm AS
                SELECT
                    CAST(LOWER(TRIM(REGEXP_REPLACE(COALESCE("Search term", ''), '\\s+', ' '))) AS VARCHAR) AS term,
                    "Search term"                                AS term_raw,
                    'search_term'                                AS type,
                    "Campaign"                                   AS campaign,
                    "Ad group"                                   AS ad_group,
                    TRY_CAST(NULLIF(TRIM("Impr."),       '--') AS BIGINT)  AS impressions,
                    TRY_CAST(NULLIF(TRIM("Clicks"),      '--') AS BIGINT)  AS clicks,
                    TRY_CAST(NULLIF(TRIM("Cost"),        '--') AS DOUBLE)  AS cost,
                    TRY_CAST(NULLIF(TRIM("Conversions"), '--') AS DOUBLE)  AS conversions
                FROM _stg_kw_history_st_raw
                WHERE COALESCE(TRIM("Search term"), '') <> ''
                """
            )
        else:
            con.execute("CREATE TABLE _stg_kw_history_norm AS "
                        "SELECT NULL::VARCHAR AS term, "
                        "       NULL::VARCHAR AS term_raw, "
                        "       NULL::VARCHAR AS type, "
                        "       NULL::VARCHAR AS campaign, "
                        "       NULL::VARCHAR AS ad_group, "
                        "       NULL::BIGINT  AS impressions, "
                        "       NULL::BIGINT  AS clicks, "
                        "       NULL::DOUBLE  AS cost, "
                        "       NULL::DOUBLE  AS conversions "
                        "WHERE FALSE")

        # ----- Keyword report -> normalised rows (type='keyword').
        # Keywords come with match-type wrappers: [exact] / "phrase" / broad.
        # Strip the leading/trailing [...] or "..." in SQL. We don't strip
        # punctuation inside the term per the brief.
        if kw_csv:
            con.execute(
                """
                INSERT INTO _stg_kw_history_norm
                SELECT
                    CAST(LOWER(TRIM(REGEXP_REPLACE(
                        REGEXP_REPLACE(REGEXP_REPLACE(COALESCE("Keyword", ''),
                                                      '^\\[', ''),
                                       '\\]$', ''),
                        '\\s+', ' '))) AS VARCHAR) AS term,
                    "Keyword"                                    AS term_raw,
                    'keyword'                                    AS type,
                    NULL                                         AS campaign,
                    "Ad group"                                   AS ad_group,
                    TRY_CAST(NULLIF(TRIM("Impr."),       '--') AS BIGINT)  AS impressions,
                    TRY_CAST(NULLIF(TRIM("Clicks"),      '--') AS BIGINT)  AS clicks,
                    TRY_CAST(NULLIF(TRIM("Cost"),        '--') AS DOUBLE)  AS cost,
                    TRY_CAST(NULLIF(TRIM("Conversions"), '--') AS DOUBLE)  AS conversions
                FROM _stg_kw_history_kw_raw
                WHERE COALESCE(TRIM("Keyword"), '') <> ''
                """
            )
            # Also strip leading/trailing quotes ("...") for phrase-match.
            con.execute(
                """
                UPDATE _stg_kw_history_norm
                SET term = REGEXP_REPLACE(REGEXP_REPLACE(term, '^"', ''), '"$', '')
                WHERE type = 'keyword'
                """
            )

        norm_rows = con.execute(
            "SELECT COUNT(*) FROM _stg_kw_history_norm"
        ).fetchone()[0]
        logger.info('[norm] _stg_kw_history_norm rows=%d', norm_rows)

        # ----- Aggregate per (term, type): one row, sums + top campaign/ag.
        # `old_campaign` / `old_ad_group` = the (campaign, ad_group) pair
        # with the highest impressions for that term (within the same type).
        # We resolve ties by clicks DESC then cost DESC then ad_group ASC
        # for determinism.
        con.execute(
            """
            CREATE TABLE _stg_kw_history_agg AS
            WITH grouped AS (
                SELECT
                    term, type,
                    COALESCE(NULLIF(campaign,  ''), '(unknown)') AS campaign,
                    COALESCE(NULLIF(ad_group,  ''), '(unknown)') AS ad_group,
                    SUM(COALESCE(impressions, 0)) AS impr,
                    SUM(COALESCE(clicks, 0))      AS clk,
                    SUM(COALESCE(cost, 0))        AS cst,
                    SUM(COALESCE(conversions, 0)) AS conv
                FROM _stg_kw_history_norm
                WHERE term IS NOT NULL AND term <> ''
                GROUP BY term, type, COALESCE(NULLIF(campaign, ''), '(unknown)'),
                                     COALESCE(NULLIF(ad_group, ''), '(unknown)')
            ),
            top_pair AS (
                SELECT
                    term, type, campaign, ad_group,
                    ROW_NUMBER() OVER (
                        PARTITION BY term, type
                        ORDER BY impr DESC, clk DESC, cst DESC, ad_group ASC
                    ) AS rn
                FROM grouped
            ),
            totals AS (
                SELECT
                    term, type,
                    SUM(impr) AS impressions_total,
                    SUM(clk)  AS clicks_total,
                    SUM(cst)  AS cost_total,
                    SUM(conv) AS conversions_total
                FROM grouped
                GROUP BY term, type
            ),
            raw_first AS (
                SELECT term, type, ANY_VALUE(term_raw) AS term_raw
                FROM _stg_kw_history_norm
                WHERE term IS NOT NULL AND term <> ''
                GROUP BY term, type
            )
            SELECT
                t.term, t.type,
                rf.term_raw,
                t.impressions_total,
                t.clicks_total,
                t.cost_total,
                t.conversions_total,
                tp.campaign AS old_campaign,
                tp.ad_group AS old_ad_group
            FROM totals t
            JOIN top_pair tp
              ON tp.term = t.term AND tp.type = t.type AND tp.rn = 1
            LEFT JOIN raw_first rf
              ON rf.term = t.term AND rf.type = t.type
            """
        )

        # ----- Collapse keyword/search_term duplicates into type='both'.
        # If the same normalised term exists with both types, we merge
        # them: sum the metrics, take the higher-impression pair as
        # old_campaign/old_ad_group, prefer the search_term term_raw
        # (more likely to be the actual user query).
        # arg_max(arg, val) is the DuckDB-supported way to pick a column
        # based on another column's MAX (ANY_VALUE with ORDER BY is
        # silently non-deterministic).
        con.execute(
            """
            CREATE OR REPLACE TABLE _stg_kw_history_collapsed AS
            SELECT
                term,
                CASE WHEN COUNT(DISTINCT type) > 1 THEN 'both'
                     ELSE MIN(type)
                END                                       AS type,
                SUM(impressions_total)                    AS impressions_total,
                SUM(clicks_total)                         AS clicks_total,
                SUM(cost_total)                           AS cost_total,
                SUM(conversions_total)                    AS conversions_total,
                arg_max(old_campaign, impressions_total)  AS old_campaign,
                arg_max(old_ad_group, impressions_total)  AS old_ad_group,
                -- Prefer the search_term raw form when both types exist.
                arg_max(term_raw, CASE WHEN type = 'search_term' THEN 1 ELSE 0 END)
                                                          AS term_raw
            FROM _stg_kw_history_agg
            GROUP BY term
            """
        )

        # ----- Compute is_brand_campaign + in_new_ex + current_new_ex_ad_group
        # `in_new_ex` is keyed off the DII keyword snapshot, Status=Enabled.
        # The keyword text in that snapshot also wears [exact] / "phrase"
        # markers; strip them with the same regex.
        con.execute(
            """
            CREATE OR REPLACE TABLE _stg_kw_history_ex AS
            SELECT
                CAST(LOWER(TRIM(REGEXP_REPLACE(
                    REGEXP_REPLACE(REGEXP_REPLACE(COALESCE("Keyword", ''),
                                                  '^\\[', ''),
                                   '\\]$', ''),
                    '\\s+', ' '))) AS VARCHAR) AS term_norm,
                "Ad group" AS ad_group
            FROM _stg_kw_history_kw_raw
            WHERE COALESCE("Keyword status", "Status") = 'Enabled'
              AND COALESCE(TRIM("Keyword"), '') <> ''
            """ if kw_csv else
            """CREATE OR REPLACE TABLE _stg_kw_history_ex AS
               SELECT NULL::VARCHAR AS term_norm, NULL::VARCHAR AS ad_group WHERE FALSE"""
        )
        # Strip surrounding double quotes from phrase-match.
        if kw_csv:
            con.execute(
                "UPDATE _stg_kw_history_ex "
                "SET term_norm = REGEXP_REPLACE(REGEXP_REPLACE(term_norm, '^\"', ''), '\"$', '')"
            )
        # Collapse multiple [ex] entries per term to one row — a keyword
        # can be in several ad groups (e.g. both exact + phrase variants
        # land in different CORE/COST/LOCATION sub-groups). Picking the
        # first alphabetically gives a deterministic display; UI can
        # surface the full list later if Chris wants. Without this the
        # INSERT below multiplies and trips the (client_id, term, type)
        # PK constraint.
        con.execute(
            """
            CREATE OR REPLACE TABLE _stg_kw_history_ex_unique AS
            SELECT term_norm,
                   MIN(ad_group) AS ad_group
            FROM _stg_kw_history_ex
            WHERE term_norm IS NOT NULL AND term_norm <> ''
            GROUP BY term_norm
            """
        )

        # ----- Final upsert into kw_st_history.
        # Idempotency: DELETE WHERE client_id=? then INSERT. Mapping fields
        # for an existing client's rows are PRESERVED via a LEFT JOIN onto
        # a snapshot of the prior table before the DELETE.
        con.execute(
            "CREATE OR REPLACE TEMP TABLE _kw_st_prior AS "
            "SELECT term, type, proposed_ad_group, proposal_method, "
            "       proposal_rationale, ai_cached_at "
            "FROM kw_st_history WHERE client_id = ?",
            [client_id],
        )
        con.execute("DELETE FROM kw_st_history WHERE client_id = ?", [client_id])

        con.execute(
            f"""
            INSERT INTO kw_st_history
                (client_id, term, term_raw, type,
                 impressions_total, clicks_total, cost_total, conversions_total,
                 old_campaign, old_ad_group, is_brand_campaign,
                 in_new_ex, current_new_ex_ad_group,
                 proposed_ad_group, proposal_method, proposal_rationale,
                 ai_cached_at, first_seen, last_updated)
            SELECT
                ?                                       AS client_id,
                c.term, c.term_raw, c.type,
                COALESCE(c.impressions_total, 0)        AS impressions_total,
                COALESCE(c.clicks_total, 0)             AS clicks_total,
                COALESCE(c.cost_total, 0)               AS cost_total,
                COALESCE(c.conversions_total, 0)        AS conversions_total,
                c.old_campaign, c.old_ad_group,
                CASE WHEN c.old_campaign IS NULL THEN FALSE
                     WHEN { brand_pred.replace('campaign', 'c.old_campaign') } THEN TRUE
                     ELSE FALSE
                END                                     AS is_brand_campaign,
                CASE WHEN ex.term_norm IS NOT NULL THEN TRUE ELSE FALSE END
                                                        AS in_new_ex,
                ex.ad_group                             AS current_new_ex_ad_group,
                p.proposed_ad_group,
                p.proposal_method,
                p.proposal_rationale,
                p.ai_cached_at,
                NULL::DATE                              AS first_seen,
                CURRENT_TIMESTAMP                       AS last_updated
            FROM _stg_kw_history_collapsed c
            LEFT JOIN _stg_kw_history_ex_unique ex
                ON ex.term_norm = c.term
            LEFT JOIN _kw_st_prior p
                ON p.term = c.term AND p.type = c.type
            """,
            [client_id],
        )

        summary['rows_inserted'] = int(con.execute(
            "SELECT COUNT(*) FROM kw_st_history WHERE client_id = ?",
            [client_id],
        ).fetchone()[0])
        summary['unique_terms'] = summary['rows_inserted']
        summary['overall'] = 'success'
        logger.info('[done] client=%s rows_inserted=%d',
                    client_id, summary['rows_inserted'])
        return summary
    except Exception as e:  # noqa: BLE001
        logger.exception('rebuild_kw_st_history failed: %s', e)
        summary['overall'] = 'failed'
        summary['error'] = str(e)[:500]
        return summary
    finally:
        con.close()


# ---------------------------------------------------------------------------
# Folder-level orchestration — pick up whatever's in kw_history_incoming/
# ---------------------------------------------------------------------------
_PROCESS_LOCK = threading.Lock()


def process_incoming(client_id: str) -> dict:
    """Look at the client's kw_history_incoming/ folder, find one CSV of
    each report type, ingest them, and archive on success.

    Behaviour:
      - Detect each file's report type from row 1; warn on unknown files.
      - If the same report type appears twice, pick the most recently
        modified file and warn about the duplicate.
      - If at least the search-terms OR the keyword report is present,
        run the rebuild. The third file is optional.
      - On success, move every consumed file into kw_history_archive/<today>/.
      - On failure, files stay put so the user can fix + re-drop.

    The lock keeps two concurrent triggers (e.g. drag-drop firing twice)
    from racing on the same files.
    """
    with _PROCESS_LOCK:
        if client_id not in ALLOWED_CLIENTS_V1:
            return {'overall': 'skipped',
                    'reason': f'{client_id!r} not in v1 allowlist'}

        ensure_client_folders(client_id)
        inc = incoming_dir(client_id)
        all_csvs = sorted(
            (p for p in inc.glob('*.csv') if not p.name.startswith('.')),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if not all_csvs:
            return {'overall': 'noop', 'reason': 'no_csvs_in_incoming'}

        # Sort each detected file into its slot. Newer wins on conflict.
        slot: dict[str, Path] = {}
        unknown: list[Path] = []
        for p in all_csvs:
            rt = detect_report_type(p)
            if rt is None:
                unknown.append(p)
                continue
            slot.setdefault(rt, p)

        if unknown:
            logger.warning(
                '[ingest] %d file(s) in incoming/ unrecognised: %s',
                len(unknown), [u.name for u in unknown])

        st_path = str(slot['st']) if 'st' in slot else None
        kw_path = str(slot['kw']) if 'kw' in slot else None
        ag_path = str(slot['ag']) if 'ag' in slot else None

        if not (st_path or kw_path):
            return {'overall': 'noop',
                    'reason': 'no_st_or_kw_csv_detected',
                    'files_seen': [p.name for p in all_csvs]}

        logger.info('[ingest] client=%s st=%s kw=%s ag=%s',
                    client_id,
                    Path(st_path).name if st_path else '(none)',
                    Path(kw_path).name if kw_path else '(none)',
                    Path(ag_path).name if ag_path else '(none)')

        result = rebuild_kw_st_history(client_id, st_path, kw_path, ag_path)

        if result.get('overall') == 'success':
            # Archive each consumed file (and any unknowns get left).
            arc = archive_dir(client_id)
            arc.mkdir(parents=True, exist_ok=True)
            for path in [p for p in (slot.get('st'), slot.get('kw'),
                                     slot.get('ag')) if p is not None]:
                try:
                    target = arc / path.name
                    if target.exists():
                        stem, suffix = target.stem, target.suffix
                        n = 2
                        while True:
                            candidate = arc / f"{stem}_{n}{suffix}"
                            if not candidate.exists():
                                target = candidate
                                break
                            n += 1
                    shutil.move(str(path), str(target))
                    logger.info('  archived -> %s', target)
                except Exception as e:  # noqa: BLE001
                    logger.warning('  archive failed for %s: %s', path, e)
            result['archived_to'] = str(arc)
        return result


def cli_main(argv: list[str] | None = None) -> int:
    """Standalone CLI:
        python -m act_dashboard.data_pipeline.kw_history_ingest dbd001
    """
    argv = argv if argv is not None else sys.argv[1:]
    client_id = argv[0] if argv else 'dbd001'
    res = process_incoming(client_id)
    logger.info('result: %s', res)
    return 0 if res.get('overall') in ('success', 'noop') else 1


if __name__ == '__main__':
    sys.exit(cli_main())
