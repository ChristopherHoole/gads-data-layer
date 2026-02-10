# src/gads_pipeline/cli.py
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .v1_runner import run_v1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="gads_pipeline")
    sub = p.add_subparsers(dest="command", required=True)

    p_run = sub.add_parser("run-v1", help="Run Vertical Slice v1 (Campaign Daily)")
    p_run.add_argument(
        "mode",
        choices=["mock", "test", "prod"],
        help="Run mode (mock/test/prod)",
    )
    p_run.add_argument(
        "config_path",
        help="Path to client config YAML (e.g. .\\configs\\client_001.yaml)",
    )
    p_run.add_argument(
        "--lookback-days",
        type=int,
        default=1,
        help="Refresh trailing N days (inclusive). Must be >= 1.",
    )
    p_run.add_argument(
        "--target-date",
        default=None,
        help="Optional override end date (YYYY-MM-DD). If omitted, config/default decides.",
    )

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "run-v1":
        if args.lookback_days < 1:
            print("ERROR: --lookback-days must be >= 1", file=sys.stderr)
            return 2

        return run_v1(
            mode=args.mode,
            config_path=Path(args.config_path),
            lookback_days=args.lookback_days,
            target_date_override=args.target_date,
        )

    print("ERROR: Unknown command", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
