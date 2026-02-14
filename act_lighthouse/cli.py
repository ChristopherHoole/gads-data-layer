from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from .config import load_client_config
from .db import DBPaths, connect_build_with_readonly_attached
from .features import build_campaign_features_daily
from .report import write_lighthouse_insights_and_report


def _parse_date(s: str) -> date:
    parts = s.split("-")
    if len(parts) != 3:
        raise ValueError("snapshot_date must be YYYY-MM-DD")
    y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
    return date(y, m, d)


def cmd_run_v0(args: argparse.Namespace) -> int:
    cfg = load_client_config(args.client_config)
    snapshot_date = _parse_date(args.snapshot_date)

    build_db = Path(args.build_db) if args.build_db else Path("warehouse.duckdb")
    readonly_db = (
        Path(args.readonly_db)
        if args.readonly_db
        else Path("warehouse_readonly.duckdb")
    )

    con = connect_build_with_readonly_attached(
        DBPaths(build_db=build_db, readonly_db=readonly_db)
    )

    print(
        f"[Lighthouse] client_id={cfg.client_id} customer_id={cfg.customer_id} snapshot_date={snapshot_date.isoformat()}"
    )
    print("[Lighthouse] Step 1/2: build campaign features into warehouse.duckdb ...")
    res = build_campaign_features_daily(con, cfg, snapshot_date=snapshot_date)
    print(
        f"[Lighthouse] Features rows inserted: {res.rows_inserted} (has_conversion_value={res.has_conversion_value})"
    )

    print("[Lighthouse] Step 2/2: generate top insights + emit report ...")
    out = write_lighthouse_insights_and_report(
        con, cfg, snapshot_date=snapshot_date, max_insights=int(args.max_insights)
    )
    print(f"[Lighthouse] Insights written: {out['insights_written']}")
    print(f"[Lighthouse] Report JSON: {out['report_path']}")

    print(
        "\n[Lighthouse] Proof SQL (run in DBeaver on warehouse_readonly AFTER refresh_readonly):"
    )
    print(
        f"SELECT COUNT(*) AS feature_rows FROM analytics.campaign_features_daily WHERE client_id='{cfg.client_id}' AND customer_id='{cfg.customer_id}' AND snapshot_date='{snapshot_date.isoformat()}';"
    )
    print(
        f"SELECT * FROM analytics.lighthouse_insights_daily WHERE client_id='{cfg.client_id}' AND customer_id='{cfg.customer_id}' AND snapshot_date='{snapshot_date.isoformat()}' ORDER BY insight_rank;"
    )

    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="act_lighthouse", description="Ads Control Tower (A.C.T) — Lighthouse v0"
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser(
        "run-v0",
        help="Build features + emit Lighthouse top insights (minimal vertical slice).",
    )
    r.add_argument("client_config", help="Path to configs/client_001.yaml")
    r.add_argument(
        "--snapshot-date", required=True, help="YYYY-MM-DD (the snapshot_date to score)"
    )
    r.add_argument(
        "--max-insights", default=5, help="How many ranked insights to emit (default 5)"
    )
    r.add_argument(
        "--readonly-db",
        default="warehouse_readonly.duckdb",
        help="Readonly DuckDB path",
    )
    r.add_argument("--build-db", default="warehouse.duckdb", help="Build DuckDB path")
    r.set_defaults(func=cmd_run_v0)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
