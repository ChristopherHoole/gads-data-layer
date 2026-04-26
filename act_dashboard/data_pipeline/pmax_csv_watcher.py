"""Fix 1.6 — PMax CSV per-client folder watcher.

Per Fix 1.6 follow-up: replaced the unsafe Downloads-folder + on-start-scan
+ heuristic-client-detect design with a clean per-client folder model.

Layout (auto-created on watcher start for every row in
act_v2_clients WHERE active=true):

    <PROJECT_ROOT>/client_csvs/
        dbd001/
            incoming/       <-- drop or upload CSVs here
            archive/        <-- watcher moves successful ingests here
        oe001/
            incoming/
            archive/

Run as a long-lived background process via Windows Task Scheduler:

    Trigger:  At log on
    Action:   <project>\\.venv\\Scripts\\python.exe -m
              act_dashboard.data_pipeline.pmax_csv_watcher

Behaviour:
- Watches each <client_csvs>/<client_id>/incoming/ via one Observer with
  per-client schedule().
- Folder name == client_id (canonical). No content-based detection.
- on_created (and on_moved.dest) -> validate -> ingest_csv -> archive.
- NO on-start scan. Restarting the watcher with files already sitting in
  incoming/ does NOT process them — user must re-drop / re-upload to
  trigger an event. (Brief AC: "those files are NOT processed".)
- Per-stage entries to act_v2_csv_watch_log: detected / skipped (validation)
  / failed (ingest exception or archive move) / ingested.
- Survives any single-file error (per-file try/except).

Environment variables (rare overrides):
    ACT_CLIENT_CSVS_DIR     override root (default <project>/client_csvs)
"""
from __future__ import annotations

import logging
import os
import shutil
import sys
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path

import duckdb

# Keep watchdog as a deferred import so the folder helpers below remain
# importable from the Flask app (which doesn't need watchdog) on
# machines where it isn't installed yet. Only the daemon main() and the
# _Handler class require watchdog.
try:
    from watchdog.events import FileSystemEventHandler  # type: ignore
    from watchdog.observers import Observer  # type: ignore
    _HAS_WATCHDOG = True
except ImportError:
    FileSystemEventHandler = object  # type: ignore[assignment,misc]
    Observer = None  # type: ignore[assignment]
    _HAS_WATCHDOG = False

from act_dashboard.data_pipeline.pmax_csv_ingest import (
    DB_PATH,
    ingest_csv,
    validate_search_terms_csv,
)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
LOG_PATH = SCRIPT_DIR / 'pmax_csv_watcher.log'

CLIENT_CSVS_ROOT = Path(os.environ.get(
    'ACT_CLIENT_CSVS_DIR', str(PROJECT_ROOT / 'client_csvs')
)).resolve()

FILENAME_SUFFIX = '.csv'
SETTLE_SECONDS = 2.0

logger = logging.getLogger('pmax_csv_watcher')
logger.setLevel(logging.INFO)
_fmt = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
if not logger.handlers:
    sh = logging.StreamHandler(sys.stdout); sh.setFormatter(_fmt); logger.addHandler(sh)
    fh = logging.FileHandler(LOG_PATH, mode='a', encoding='utf-8'); fh.setFormatter(_fmt); logger.addHandler(fh)


# ---------------------------------------------------------------------------
# Folder helpers (importable so the upload endpoint reuses the same paths)
# ---------------------------------------------------------------------------
def incoming_dir(client_id: str) -> Path:
    return CLIENT_CSVS_ROOT / client_id / 'incoming'


def archive_dir(client_id: str) -> Path:
    return CLIENT_CSVS_ROOT / client_id / 'archive'


def get_active_clients() -> list[str]:
    """Read active client_ids. Short-lived connection.

    Stage 1.6.1: opens read-write (no read_only=True) because when the
    watcher runs as a Flask thread, other in-process modules (outreach
    poller, queue scheduler, request handlers) already hold read-write
    connections to the same DB file. DuckDB requires all in-process
    connections to share the same access mode — a read-only attempt
    against a read-write peer raises ConnectionException("different
    configuration than existing connections"). The query itself is a
    plain SELECT so the lost read-only safety check is purely cosmetic.
    """
    try:
        con = duckdb.connect(DB_PATH)
    except duckdb.IOException as e:
        logger.error(f"DB locked, cannot read active clients: {e}")
        return []
    try:
        rows = con.execute(
            "SELECT client_id FROM act_v2_clients WHERE active = TRUE "
            "ORDER BY client_id"
        ).fetchall()
        return [r[0] for r in rows]
    finally:
        con.close()


def ensure_client_folders(client_ids: list[str]) -> None:
    """Create incoming/ + archive/ for each client if missing. Also
    drops a .gitkeep so the directory is preserved in git when empty."""
    CLIENT_CSVS_ROOT.mkdir(parents=True, exist_ok=True)
    for cid in client_ids:
        for sub in (incoming_dir(cid), archive_dir(cid)):
            sub.mkdir(parents=True, exist_ok=True)
            keep = sub / '.gitkeep'
            if not keep.exists():
                try:
                    keep.touch()
                except Exception:
                    pass


# ---------------------------------------------------------------------------
# Log helpers
# ---------------------------------------------------------------------------
def _log_row(file_path: str, client_id: str | None, status: str,
             rows_ingested: int | None = None, error_message: str | None = None,
             processed: bool = False) -> None:
    """Insert one row into act_v2_csv_watch_log."""
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


# ---------------------------------------------------------------------------
# Per-file pipeline
# ---------------------------------------------------------------------------
def _is_target_file(path: Path) -> bool:
    name = path.name.lower()
    return name.endswith(FILENAME_SUFFIX) and not name.startswith('.')


def _archive_target(client_id: str, src: Path) -> Path:
    today = datetime.now().date().isoformat()
    ad = archive_dir(client_id)
    ad.mkdir(parents=True, exist_ok=True)
    target = ad / f"{today}_{src.name}"
    # Avoid clobbering: if a file with the same archive name already
    # exists (e.g. the user re-dropped the same file twice in one day),
    # append a numeric suffix.
    if target.exists():
        stem, suffix = target.stem, target.suffix
        n = 2
        while True:
            candidate = ad / f"{stem}_{n}{suffix}"
            if not candidate.exists():
                target = candidate
                break
            n += 1
    return target


def process_file(path: Path, client_id: str) -> None:
    """Validate, ingest, archive. client_id is canonical (folder name);
    no detection is attempted."""
    str_path = str(path)
    logger.info(f"[detect] {client_id} :: {str_path}")

    if not path.exists():
        logger.warning(f"  vanished before processing: {str_path}")
        return

    time.sleep(SETTLE_SECONDS)

    _log_row(str_path, client_id=client_id, status='detected')

    ok, reason = validate_search_terms_csv(str_path)
    if not ok:
        msg = f"validation failed: {reason}"
        logger.warning(f"  skipping: {msg}")
        _log_row(str_path, client_id=client_id, status='skipped',
                 error_message=msg, processed=True)
        return

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

    target = _archive_target(client_id, path)
    try:
        shutil.move(str_path, str(target))
        logger.info(f"  archived -> {target}")
    except Exception as e:
        err = f"archive failed (DB writes succeeded): {e}"
        logger.exception(f"  {err}")
        _log_row(str_path, client_id=client_id, status='failed',
                 rows_ingested=rows, error_message=err, processed=True)
        return

    _log_row(str(target), client_id=client_id, status='ingested',
             rows_ingested=rows, processed=True)


# ---------------------------------------------------------------------------
# watchdog handler — one instance per client_id
# ---------------------------------------------------------------------------
class _Handler(FileSystemEventHandler):
    def __init__(self, client_id: str):
        self.client_id = client_id

    def _maybe_process(self, src_path: str):
        path = Path(src_path)
        if not _is_target_file(path):
            return
        try:
            process_file(path, self.client_id)
        except Exception:
            # The watcher must survive any single-file error.
            logger.exception(f"unhandled error processing {src_path}")

    def on_created(self, event):
        if not event.is_directory:
            self._maybe_process(event.src_path)

    def on_moved(self, event):
        # Drag-drop from Explorer fires 'moved' on Windows when the source
        # path is on the same volume; the upload endpoint uses os.replace
        # which surfaces as 'moved' too. Treat dest_path as the new file.
        if not event.is_directory:
            dest = getattr(event, 'dest_path', None)
            if dest:
                self._maybe_process(dest)


# ---------------------------------------------------------------------------
# Stage 1.6.1 — Startup scan + Flask-thread entry point
# ---------------------------------------------------------------------------
# Window for the startup-scan to consider a sitting CSV "recent enough" to
# auto-process. Files older than this are logged-and-skipped (left in place
# so the user can decide whether to re-drop them).
_STARTUP_SCAN_WINDOW = timedelta(hours=24)

# Idempotency guard for start_csv_watcher_thread() — protects against
# multiple create_app() calls within a single process. The Werkzeug
# debug reloader fork is handled separately via the WERKZEUG_RUN_MAIN
# check (only the child process actually serves; parent just monitors).
_watcher_started = False
_watcher_lock = threading.Lock()


def _scan_incoming_for_recent_files() -> None:
    """One-shot scan of every active client's incoming/ for *.csv files
    with mtime within the last 24h. Per-file errors don't abort the
    scan — single-file failures get logged and the loop continues.

    Idempotency: process_file() does its own validate -> ingest -> archive
    sequence; ingest_csv() is itself idempotent (DELETE+INSERT keyed on
    (client_id, snapshot_date)). A file accidentally scanned twice would
    only re-write the same rows.
    """
    cutoff = datetime.now() - _STARTUP_SCAN_WINDOW
    try:
        clients = get_active_clients()
    except Exception:
        logger.exception('[csv_watcher] startup scan: get_active_clients failed')
        return

    for client_id in clients:
        try:
            incoming = incoming_dir(client_id)
            if not incoming.exists():
                continue
            for path in sorted(incoming.glob('*.csv')):
                if path.name.startswith('.'):
                    continue
                try:
                    mtime = datetime.fromtimestamp(path.stat().st_mtime)
                except OSError as e:
                    logger.warning(
                        f'[csv_watcher] startup scan: stat failed for {path}: {e}'
                    )
                    continue
                if mtime < cutoff:
                    logger.info(
                        f'[csv_watcher] startup scan: skipping {path.name} '
                        f'(mtime {mtime.isoformat(timespec="seconds")}, '
                        f'older than 24h)'
                    )
                    continue
                logger.info(
                    f'[csv_watcher] startup scan: processing {path.name} '
                    f'(mtime {mtime.isoformat(timespec="seconds")})'
                )
                try:
                    process_file(path, client_id)
                except Exception:
                    # process_file already logs + writes act_v2_csv_watch_log
                    # rows on its own failure paths; this is a belt-and-braces
                    # catch so one bad file doesn't kill the whole scan.
                    logger.exception(
                        f'[csv_watcher] startup scan: process_file raised for {path}'
                    )
        except Exception:
            logger.exception(
                f'[csv_watcher] startup scan: unhandled error for client {client_id}'
            )


def _run_watch_loop(blocking: bool = True) -> int:
    """Set up the watchdog Observer for every active client's incoming/
    folder. When blocking=True (standalone main entry), keeps the
    process alive with a 60s sleep loop until Ctrl+C. When blocking=
    False (Flask-thread entry), schedules + starts the Observer and
    returns immediately — the Observer's own threads keep watching.

    Returns process-style exit code (0 on success, 1 on setup failure).
    """
    if not _HAS_WATCHDOG:
        msg = (
            "'watchdog' is not installed. Run: pip install watchdog\n"
            "If using the project venv: "
            ".venv\\Scripts\\python.exe -m pip install watchdog"
        )
        # Both the standalone CLI and the Flask thread care about this —
        # log loudly + write to stderr for the CLI shell.
        logger.error(msg)
        if blocking:
            print(f'ERROR: {msg}', file=sys.stderr)
        return 1

    clients = get_active_clients()
    if not clients:
        logger.error('No active clients in act_v2_clients. Exiting.')
        return 1
    logger.info('=' * 60)
    logger.info('PMax CSV Watcher (per-client) — Starting')
    logger.info(f'  csv_root      : {CLIENT_CSVS_ROOT}')
    logger.info(f'  db_path       : {DB_PATH}')
    logger.info(f'  active clients: {clients}')
    logger.info('=' * 60)

    ensure_client_folders(clients)

    observer = Observer()
    for cid in clients:
        watch_path = incoming_dir(cid)
        observer.schedule(_Handler(cid), str(watch_path), recursive=False)
        logger.info(f'  watching {watch_path}')
    observer.start()
    logger.info('Watcher running.' + (' Ctrl+C to stop.' if blocking else ''))

    if not blocking:
        # Flask-thread mode: hand control back to the caller. The
        # watchdog Observer keeps running on its own daemon threads
        # until the parent process exits.
        return 0

    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info('Stopping watcher (KeyboardInterrupt)')
    finally:
        observer.stop()
        observer.join(timeout=5)
    return 0


def start_csv_watcher_thread() -> None:
    """Start the CSV watcher as a Flask daemon thread. Idempotent — safe
    to call multiple times (e.g. multiple create_app() invocations within
    one process).

    Reloader guard: when Flask runs with debug=True + use_reloader=True,
    Werkzeug forks parent (file-monitor) and child (server) processes.
    Both call create_app(). Werkzeug sets WERKZEUG_RUN_MAIN=true ONLY in
    the child process, so we use that to skip thread spawn in the parent.
    Without this guard the watcher would run twice (once per process)
    and each dropped CSV would be picked up by both — wasteful even if
    the underlying ingest is idempotent.

    Order matters: the startup scan completes BEFORE the Observer
    starts. If both ran in parallel a file could land in both queues
    and double-ingest before the DELETE+INSERT idempotency caught it.
    """
    global _watcher_started

    # Reloader guard. WERKZEUG_RUN_MAIN is set to 'true' by werkzeug
    # ONLY in the child reloader process. The parent process lacks
    # this var entirely. If we're not in debug-reloader mode at all
    # the var is absent — that's fine, we proceed normally.
    if (os.environ.get('WERKZEUG_RUN_MAIN') is None
            and os.environ.get('FLASK_DEBUG') in ('1', 'true', 'True')):
        # Debug mode parent process — child will start the thread.
        logger.info(
            '[csv_watcher] reloader-parent process — child will start watcher'
        )
        return

    with _watcher_lock:
        if _watcher_started:
            logger.info('[csv_watcher] already started — skipping')
            return
        _watcher_started = True

    if not _HAS_WATCHDOG:
        logger.error(
            "[csv_watcher] watchdog not installed; thread NOT started. "
            'Install: .venv\\Scripts\\python.exe -m pip install watchdog'
        )
        return

    def _runner():
        try:
            # ORDER IS CRITICAL — startup scan must complete BEFORE the
            # Observer starts (a file detected by both would risk a
            # double-ingest before the DB DELETE+INSERT idempotency
            # catches it).
            _scan_incoming_for_recent_files()
            # Non-blocking: schedules the Observer and returns immediately.
            # Observer's own threads keep the watch active until the
            # parent process (Flask) exits.
            _run_watch_loop(blocking=False)
        except Exception:
            logger.exception('[csv_watcher] thread crashed')

    t = threading.Thread(target=_runner, name='csv_watcher', daemon=True)
    t.start()
    logger.info('[csv_watcher] started as Flask daemon thread')


def main():
    """Standalone-process entry point. Same scan-then-watch order as the
    Flask thread, but blocks on a 60s sleep loop until Ctrl+C."""
    _scan_incoming_for_recent_files()
    return _run_watch_loop(blocking=True)


if __name__ == '__main__':
    sys.exit(main())
