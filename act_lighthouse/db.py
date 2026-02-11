from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import duckdb


@dataclass(frozen=True)
class DBPaths:
    build_db: Path
    readonly_db: Path


def connect_build_with_readonly_attached(paths: DBPaths) -> duckdb.DuckDBPyConnection:
    build_db = paths.build_db.resolve()
    readonly_db = paths.readonly_db.resolve()

    if not build_db.exists():
        raise FileNotFoundError(f"Build DB not found: {build_db}")
    if not readonly_db.exists():
        raise FileNotFoundError(f"Readonly DB not found: {readonly_db}")

    con = duckdb.connect(str(build_db))
    con.execute(f"ATTACH '{readonly_db.as_posix()}' AS ro (READ_ONLY);")
    con.execute("CREATE SCHEMA IF NOT EXISTS analytics;")
    return con
