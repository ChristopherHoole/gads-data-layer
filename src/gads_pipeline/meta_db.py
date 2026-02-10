"""
Postgres metadata store for the read-only pipeline (Chunk 1).

This file MUST remain compatible with imports used by:
- src/gads_pipeline/cli.py
- src/gads_pipeline/v1_runner.py

So we expose these function names:
- meta_engine(settings)
- init_metadata_schema(engine)
- insert_run_start(engine, ...)
- finish_run(engine, ...)
- log_error(engine, ...)
- log_validation(engine, ...)

Important fix:
- Use CAST(:param AS jsonb) instead of :param::jsonb, because the latter can
  break parameter compilation and cause Postgres syntax errors.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from .settings import Settings


# -----------------------------
# Engine
# -----------------------------

def meta_engine(settings: Settings) -> Engine:
    """
    Create SQLAlchemy engine to Postgres metadata DB.
    """
    url = (
        f"postgresql+psycopg2://{settings.meta_db_user}:{settings.meta_db_password}"
        f"@{settings.meta_db_host}:{settings.meta_db_port}/{settings.meta_db_name}"
    )
    return create_engine(url, pool_pre_ping=True)


# -----------------------------
# Helpers
# -----------------------------

def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _to_json_str(value: Any) -> Optional[str]:
    """
    Convert Python objects (dict/list/etc) into a JSON string.
    Returns None if value is None.
    """
    if value is None:
        return None
    try:
        return json.dumps(value, ensure_ascii=False, default=str)
    except Exception:
        return json.dumps({"_fallback": str(value)}, ensure_ascii=False)


# -----------------------------
# Schema
# -----------------------------

def init_metadata_schema(engine: Engine) -> None:
    """
    Create minimal metadata tables for v1: runs, errors, validations.
    Safe to run multiple times (idempotent).
    """
    ddl = [
        """
        CREATE TABLE IF NOT EXISTS pipeline_runs (
            run_id TEXT PRIMARY KEY,
            created_at TIMESTAMPTZ NOT NULL,
            finished_at TIMESTAMPTZ NULL,
            status TEXT NOT NULL,
            mode TEXT NOT NULL,
            client_name TEXT NOT NULL,
            customer_id TEXT NULL,
            target_date DATE NULL,
            config_hash TEXT NULL,
            summary_json JSONB NULL
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS pipeline_errors (
            id BIGSERIAL PRIMARY KEY,
            run_id TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL,
            severity TEXT NOT NULL,
            message TEXT NOT NULL,
            details_json JSONB NULL
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS validation_results (
            id BIGSERIAL PRIMARY KEY,
            run_id TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL,
            name TEXT NOT NULL,
            passed BOOLEAN NOT NULL,
            details_json JSONB NULL
        );
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_pipeline_runs_created_at ON pipeline_runs(created_at);
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_pipeline_errors_run_id ON pipeline_errors(run_id);
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_validation_results_run_id ON validation_results(run_id);
        """,
    ]
    with engine.begin() as cxn:
        for stmt in ddl:
            cxn.execute(text(stmt))


# -----------------------------
# Run logging
# -----------------------------

def insert_run_start(
    engine: Engine,
    run_id: str,
    mode: str,
    client_name: str,
    customer_id: Optional[str],
    target_date,
    config_hash: Optional[str],
) -> None:
    """
    Insert the start of a pipeline run.

    Uses ON CONFLICT DO UPDATE so re-running with same run_id doesn't crash.
    """
    with engine.begin() as cxn:
        cxn.execute(
            text(
                """
                INSERT INTO pipeline_runs
                    (run_id, created_at, status, mode, client_name, customer_id, target_date, config_hash)
                VALUES
                    (:run_id, :created_at, :status, :mode, :client_name, :customer_id, :target_date, :config_hash)
                ON CONFLICT (run_id) DO UPDATE SET
                    status = EXCLUDED.status,
                    mode = EXCLUDED.mode,
                    client_name = EXCLUDED.client_name,
                    customer_id = EXCLUDED.customer_id,
                    target_date = EXCLUDED.target_date,
                    config_hash = EXCLUDED.config_hash
                """
            ),
            {
                "run_id": run_id,
                "created_at": now_utc(),
                "status": "RUNNING",
                "mode": mode,
                "client_name": client_name,
                "customer_id": customer_id,
                "target_date": target_date,
                "config_hash": config_hash,
            },
        )


def finish_run(engine: Engine, run_id: str, status: str, summary: Optional[dict]) -> None:
    """
    Mark run as finished + store summary JSONB (safe casting).
    """
    summary_json = _to_json_str(summary)

    with engine.begin() as cxn:
        cxn.execute(
            text(
                """
                UPDATE pipeline_runs
                SET finished_at = :finished_at,
                    status = :status,
                    summary_json =
                        CASE
                            WHEN :summary_json IS NULL THEN NULL
                            ELSE CAST(:summary_json AS jsonb)
                        END
                WHERE run_id = :run_id
                """
            ),
            {
                "run_id": run_id,
                "finished_at": now_utc(),
                "status": status,
                "summary_json": summary_json,
            },
        )


# -----------------------------
# Errors + validations
# -----------------------------

def log_error(engine: Engine, run_id: str, severity: str, message: str, details: Optional[dict] = None) -> None:
    """
    Log an error row with JSONB details (safe casting).
    """
    details_json = _to_json_str(details)

    with engine.begin() as cxn:
        cxn.execute(
            text(
                """
                INSERT INTO pipeline_errors (run_id, created_at, severity, message, details_json)
                VALUES (
                    :run_id,
                    :created_at,
                    :severity,
                    :message,
                    CASE
                        WHEN :details_json IS NULL THEN NULL
                        ELSE CAST(:details_json AS jsonb)
                    END
                )
                """
            ),
            {
                "run_id": run_id,
                "created_at": now_utc(),
                "severity": severity,
                "message": message,
                "details_json": details_json,
            },
        )


def log_validation(engine: Engine, run_id: str, name: str, passed: bool, details: Optional[dict] = None) -> None:
    """
    Log a validation row with JSONB details (safe casting).
    """
    details_json = _to_json_str(details)

    with engine.begin() as cxn:
        cxn.execute(
            text(
                """
                INSERT INTO validation_results (run_id, created_at, name, passed, details_json)
                VALUES (
                    :run_id,
                    :created_at,
                    :name,
                    :passed,
                    CASE
                        WHEN :details_json IS NULL THEN NULL
                        ELSE CAST(:details_json AS jsonb)
                    END
                )
                """
            ),
            {
                "run_id": run_id,
                "created_at": now_utc(),
                "name": name,
                "passed": passed,
                "details_json": details_json,
            },
        )
