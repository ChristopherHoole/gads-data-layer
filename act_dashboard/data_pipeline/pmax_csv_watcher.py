"""Fix 1.6 — PMax CSV Downloads-folder watcher.

Detects new "Search terms report*.csv" files in ~/Downloads/, validates
they're a GAds Search-terms export, detects the client (today: DBD only,
falls back to ACT_PMAX_DEFAULT_CLIENT_ID), runs the existing
pmax_csv_ingest.ingest_csv() pipeline, and archives the file on success.

Run as a long-lived background process via Windows Task Scheduler:

    Trigger:  At log on
    Action:   <project>\\.venv\\Scripts\\python.exe -m
              act_dashboard.data_pipeline.pmax_csv_watcher

The watcher is INTENTIONALLY separate from the Flask app and the
overnight scheduler — it has its own lifecycle and its own DuckDB
short-lived connections.

Environment variables:
    ACT_PMAX_WATCH_DIR         override watch dir (default ~/Downloads)
    ACT_PMAX_DEFAULT_CLIENT_ID fallback when CSV content has no Campaign
                                column or none of its campaigns match
                                act_v2_campaign_roles. Default 'dbd001'.
    ACT_PMAX_ARCHIVE_DIR       override archive root (default
                                <watch_dir>/_act_archive)

Idempotency / restart behaviour:
- On startup, scans the watch dir once for any matching files newer than
  the most recent processed entry in act_v2_csv_watch_log so files dropped
  while the watcher was down still get picked up.
- Already-archived files (file_path containing '_act_archive' or that
  no longer exist in the watch dir) are not reprocessed.
- The ingest itself is idempotent (DELETE+INSERT by client+snapshot_date),
  so a duplicate trigger is harmless beyond an extra log entry.
"""
from __future__ import annotations

import logging
import os
import shutil
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import duckdb

try:
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer
except ImportError:
    print(
        "ERROR: 'watchdog' is not installed. Run: pip install watchdog\n"
        "If using the project venv: "
        ".venv\\Scripts\\python.exe -m pip install watchdog",
        file=sys.stderr,
    )
    sys.exit(1)

from act_dashboard.data_pipeline.pmax_csv_ingest import (
    DB_PATH,
    detect_client_from_csv,
    ingest_csv,
    validate_search_terms_csv,
)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
LOG_PATH = SCRIPT_DIR / 'pmax_csv_watcher.log'

WATCH_DIR = Path(os.environ.get(
    'ACT_PMAX_WATCH_DIR', os.path.expanduser('~/Downloads')
)).resolve()
DEFAULT_CLIENT_ID = os.environ.get('ACT_PMAX_DEFAULT_CLIENT_ID', 'dbd001')
ARCHIVE_DIR = Path(os.environ.get(
    'ACT_PMAX_ARCHIVE_DIR', str(WATCH_DIR / '_act_archive')
)).resolve()

# Glob pattern as a substring check on lowercase basename.
FILENAME_PREFIX = 'search terms report'
FILENAME_SUFFIX = '.csv'

# Settle delay between detection and ingest — gives the OS time to flush
# the file fully (Chrome writes the .crdownload first, then renames).
SETTLE_SECONDS = 2.0

logger = logging.getLogger('pmax_csv_watcher')
logger.setLevel(logging.INFO)
_fmt = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
if not logger.handlers:
    sh = logging.StreamHandler(sys.stdout); sh.setFormatter(_fmt); logger.addHandler(sh)
    fh = logging.FileHandler(LOG_PATH, mode='a', encoding='utf-8'); fh.setFormatter(_fmt); logger.addHandler(fh)


# ---------------------------------------------------------------------------
# Log helpers
# ---------------------------------------------------------------------------
def _log_row(file_path: str, client_id: str | None, status: str,
             rows_ingested: int | None = None, error_message: str | None = None,
             processed: bool = False) -> None:
    """Insert one row into act_v2_csv_watch_log. Short-lived connection so
    the Flask app / overnight scheduler aren't locked out."""
    try:
        con = duckdb.connect(DB_PATH)
    except duckdb.IOException as e:
        logger.error(f"DB locked, cannot write watch log: {e}")
        return
    try:
        con.execute(
            """INSERT INTO act_v2_csv_watch_log
               (file_path, client_id, status, rows_ingested,
                error_message, detected_at, processed_at)
               VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?)""",
            [
                file_path, client_id, status, rows_ingested,
                error_message,
                datetime.now() if processed else None,
            ],
        )
    except Exception:
        logger.exception("Failed writing to act_v2_csv_watch_log")
    finally:
        con.close()


def _file_already_logged(file_path: str) -> bool:
    """Did we already process this exact path (by basename) in the last
    24h with a terminal status (ingested / failed / skipped)? Used by the
    on-start scan to avoid reprocessing files we handled before."""
    try:
        con = duckdb.connect(DB_PATH, read_only=True)
    except duckdb.IOException:
        return False
    try:
        row = con.execute(
            """SELECT 1 FROM act_v2_csv_watch_log
               WHERE file_path = ?
                 AND status IN ('ingested', 'failed', 'skipped')
                 AND detected_at > CURRENT_TIMESTAMP - INTERVAL '24 hours'
               LIMIT 1""",
            [file_path],
        ).fetchone()
        return bool(row)
    finally:
        con.close()


# ---------------------------------------------------------------------------
# Per-file pipeline
# ---------------------------------------------------------------------------
def _is_target_file(path: Path) -> bool:
    name = path.name.lower()
    if not name.startswith(FILENAME_PREFIX) or not name.endswith(FILENAME_SUFFIX):
        return False
    # Skip files already inside the archive subtree (a no-op safety in
    # case the watcher is briefly pointed at a parent of the archive dir).
    try:
        path.relative_to(ARCHIVE_DIR)
        return False
    except ValueError:
        pass
    return True


def _archive_path(client_id: str, src: Path) -> Path:
    today = datetime.now().date().isoformat()
    sub = ARCHIVE_DIR / client_id
    sub.mkdir(parents=True, exist_ok=True)
    return sub / f"{today}_{src.name}"


def process_file(path: Path) -> None:
    """Validate, detect client, ingest, archive. One-shot — failures stay
    in place + are logged; the next OS event for the same file will
    re-trigger this function (e.g. if the user manually edits and saves).
    """
    str_path = str(path)
    logger.info(f"[detect] {str_path}")

    if not path.exists():
        logger.warning(f"  vanished before processing: {str_path}")
        return

    # Wait for OS to finish writing
    time.sleep(SETTLE_SECONDS)

    # Stage: detected
    _log_row(str_path, client_id=None, status='detected')

    # Stage: validate
    ok, reason = validate_search_terms_csv(str_path)
    if not ok:
        msg = f"validation failed: {reason}"
        logger.warning(f"  skipping: {msg}")
        _log_row(str_path, client_id=None, status='skipped',
                 error_message=msg, processed=True)
        return

    # Stage: detect client
    client_id = detect_client_from_csv(str_path) or DEFAULT_CLIENT_ID
    if not client_id:
        msg = "no client_id detected and no default configured"
        logger.error(f"  {msg}")
        _log_row(str_path, client_id=None, status='failed',
                 error_message=msg, processed=True)
        return
    logger.info(f"  client_id resolved -> {client_id}")

    # Stage: ingest
    try:
        result = ingest_csv(str_path, client_id)
    except Exception as e:
        err = str(e)[:1000]
        logger.exception(f"  ingest failed: {err}")
        _log_row(str_path, client_id=client_id, status='failed',
                 error_message=err, processed=True)
        return

    rows = int(result.get('search_term_rows_inserted') or 0)
    logger.info(f"  ingested {rows} rows for {client_id}@{result.get('snapshot_date')}")

    # Stage: archive
    archive_to = _archive_path(client_id, path)
    try:
        shutil.move(str_path, str(archive_to))
        logger.info(f"  archived -> {archive_to}")
    except Exception as e:
        # Non-fatal — DB writes already succeeded. Log a separate failed
        # row so the banner surfaces it; the user can manually move/delete.
        err = f"archive failed (DB writes succeeded): {e}"
        logger.exception(f"  {err}")
        _log_row(str_path, client_id=client_id, status='failed',
                 rows_ingested=rows, error_message=err, processed=True)
        return

    _log_row(str(archive_to), client_id=client_id, status='ingested',
             rows_ingested=rows, processed=True)


# ---------------------------------------------------------------------------
# watchdog handler
# ---------------------------------------------------------------------------
class _Handler(FileSystemEventHandler):
    def _maybe_process(self, src_path: str):
        path = Path(src_path)
        if not _is_target_file(path):
            return
        try:
            process_file(path)
        except Exception:
            # The watcher must survive any single-file error.
            logger.exception(f"unhandled exception while processing {src_path}")

    def on_created(self, event):
        if not event.is_directory:
            self._maybe_process(event.src_path)

    def on_moved(self, event):
        # Chrome's Downloads writes a .crdownload then renames to the
        # final name — we'll see this as a 'moved' event with dest_path
        # set to the final filename.
        if not event.is_directory:
            dest = getattr(event, 'dest_path', None)
            if dest:
                self._maybe_process(dest)


# ---------------------------------------------------------------------------
# On-start scan: catch up on files dropped while we were down
# ---------------------------------------------------------------------------
def _startup_scan() -> None:
    if not WATCH_DIR.exists():
        logger.warning(f"watch dir does not exist: {WATCH_DIR}")
        return
    candidates = []
    try:
        for entry in WATCH_DIR.iterdir():
            if entry.is_file() and _is_target_file(entry):
                candidates.append(entry)
    except Exception:
        logger.exception(f"startup scan iterdir failed for {WATCH_DIR}")
        return

    if not candidates:
        logger.info("startup scan: no matching files in watch dir")
        return

    # Process oldest-first so newer overrides land last in the log
    candidates.sort(key=lambda p: p.stat().st_mtime)
    logger.info(f"startup scan: {len(candidates)} candidate file(s)")
    for p in candidates:
        if _file_already_logged(str(p)):
            logger.info(f"  skip (already logged in last 24h): {p.name}")
            continue
        try:
            process_file(p)
        except Exception:
            logger.exception(f"startup scan failed on {p}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    logger.info('=' * 60)
    logger.info('PMax CSV Watcher — Starting')
    logger.info(f'  watch_dir          : {WATCH_DIR}')
    logger.info(f'  archive_dir        : {ARCHIVE_DIR}')
    logger.info(f'  default_client_id  : {DEFAULT_CLIENT_ID}')
    logger.info(f'  db_path            : {DB_PATH}')
    logger.info('=' * 60)

    if not WATCH_DIR.exists():
        logger.error(f"Watch dir does not exist: {WATCH_DIR}")
        return 1
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    _startup_scan()

    observer = Observer()
    observer.schedule(_Handler(), str(WATCH_DIR), recursive=False)
    observer.start()
    logger.info("Watcher running. Ctrl+C to stop.")
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("Stopping watcher (KeyboardInterrupt)")
    finally:
        observer.stop()
        observer.join(timeout=5)
    return 0


if __name__ == '__main__':
    sys.exit(main())
