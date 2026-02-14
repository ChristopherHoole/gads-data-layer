from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

import yaml

from .warehouse_duckdb import (
    connect_warehouse,
    init_warehouse,
    insert_raw_campaign_daily,
    insert_snap_campaign_daily,
    count_latest_rows,
)

# ----------------------------
# v1 Runner
# ----------------------------
# Modes:
# - mock: deterministic fake data into raw_/snap_ tables
# - test: real Google Ads API pull (campaign daily) into same raw_/snap_ tables
# - prod: reserved (not implemented in v1)
# ----------------------------


@dataclass(frozen=True)
class RunContext:
    warehouse_path: str
    customer_id: Optional[
        str
    ]  # In test mode, may be resolved via MCC discovery if omitted
    end_date: date
    lookback_days: int
    mode: str  # mock | test | prod

    # test/prod only
    google_ads_yaml: Optional[str] = None
    mcc_id: Optional[str] = None  # login_customer_id (manager account), digits only


def run_v1(
    mode: str,
    config_path: str,
    lookback_days: int = 1,
    target_date_override: str | None = None,
) -> int:
    ctx = _build_run_context(
        mode=mode,
        config_path=config_path,
        lookback_days=lookback_days,
        target_date_override=target_date_override,
    )

    conn = connect_warehouse(ctx.warehouse_path)
    init_warehouse(conn)

    if ctx.mode == "mock":
        return _run_mock(conn, ctx)

    if ctx.mode == "test":
        return _run_test(conn, ctx)

    raise NotImplementedError(
        "Only mock and test modes are supported right now for v1."
    )


# ----------------------------
# Config helpers
# ----------------------------


def _load_cfg(path: str) -> dict[str, Any]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Config not found: {path}")
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _cfg_get(cfg: dict[str, Any], paths: list[list[str]], default: Any) -> Any:
    for parts in paths:
        cur: Any = cfg
        ok = True
        for k in parts:
            if isinstance(cur, dict) and k in cur:
                cur = cur[k]
            else:
                ok = False
                break
        if ok and cur is not None:
            return cur
    return default


def _parse_iso_date(s: str) -> date:
    # expects YYYY-MM-DD
    return datetime.strptime(s, "%Y-%m-%d").date()


def _today_utc() -> date:
    return datetime.now(timezone.utc).date()


def _digits_only(s: str) -> str:
    return "".join(ch for ch in s if ch.isdigit())


def _build_run_context(
    mode: str, config_path: str, lookback_days: int, target_date_override: str | None
) -> RunContext:
    mode = (mode or "").strip().lower()
    if mode not in {"mock", "test", "prod"}:
        raise ValueError("mode must be one of: mock | test | prod")

    if lookback_days < 1:
        raise ValueError("--lookback-days must be >= 1")

    cfg = _load_cfg(config_path)

    # warehouse path
    warehouse_path = _cfg_get(
        cfg,
        paths=[
            ["warehouse_path"],
            ["warehouse_duckdb_path"],
            ["warehouse", "duckdb_path"],
            ["run", "warehouse_path"],
        ],
        default="./warehouse.duckdb",
    )

    # customer id (may be optional in test mode if you want discovery-driven selection)
    customer_id = _cfg_get(
        cfg,
        paths=[
            ["customer_id"],
            ["google_ads", "customer_id"],
            ["run", "customer_id"],
        ],
        default=None,
    )
    if customer_id is not None:
        customer_id = _digits_only(str(customer_id))

    # target_date / snapshot_date => end_date
    if target_date_override:
        end_date = _parse_iso_date(target_date_override)
    else:
        cfg_date = _cfg_get(
            cfg,
            paths=[
                ["target_date"],
                ["snapshot_date"],
                ["run", "target_date"],
                ["mock", "target_date"],
                ["mock", "snapshot_date"],
            ],
            default=None,
        )
        if cfg_date:
            end_date = _parse_iso_date(str(cfg_date))
        else:
            end_date = _today_utc() - timedelta(days=1)

    # test/prod: google ads credentials yaml + optional mcc/login_customer_id
    google_ads_yaml = _cfg_get(
        cfg,
        paths=[
            ["google_ads_yaml"],
            ["google_ads", "yaml"],
            ["google_ads", "credentials_yaml"],
            ["secrets", "google_ads_yaml"],
        ],
        default="./secrets/google-ads.yaml",
    )
    mcc_id = _cfg_get(
        cfg,
        paths=[
            ["mcc_id"],
            ["login_customer_id"],
            ["google_ads", "mcc_id"],
            ["google_ads", "login_customer_id"],
        ],
        default=None,
    )
    if mcc_id is not None:
        mcc_id = _digits_only(str(mcc_id)) or None

    # mock mode MUST have customer_id for deterministic data + warehouse
    if mode == "mock" and not customer_id:
        raise ValueError("Config must include customer_id for mock mode")

    return RunContext(
        warehouse_path=str(warehouse_path),
        customer_id=customer_id,
        end_date=end_date,
        lookback_days=int(lookback_days),
        mode=mode,
        google_ads_yaml=str(google_ads_yaml) if google_ads_yaml else None,
        mcc_id=mcc_id,
    )


def _date_range_inclusive(end_date: date, lookback_days: int) -> list[date]:
    start = end_date - timedelta(days=(lookback_days - 1))
    d = start
    out: list[date] = []
    while d <= end_date:
        out.append(d)
        d = d + timedelta(days=1)
    return out


# ----------------------------
# MOCK mode
# ----------------------------


def _mock_campaign_daily_rows(
    run_id: str, ingested_at: str, customer_id: str, snapshot_date: date, seed: int
) -> list[dict[str, Any]]:
    # deterministic "random-ish" but stable
    base = int(_digits_only(customer_id)[-4:] or "1111")
    rows: list[dict[str, Any]] = []
    for i in range(1, 6):
        campaign_id = 1000 + i
        impressions = (base * i * 7 + seed) % 10000 + 100
        clicks = max(1, impressions // 80)
        cost_micros = int(clicks * (500000 + (i * 25000)))
        conversions = round(clicks * 0.35, 2)
        conv_value = round(conversions * (42 + i), 2)
        rows.append(
            {
                "run_id": run_id,
                "ingested_at": ingested_at,
                "customer_id": customer_id,
                "snapshot_date": snapshot_date.strftime("%Y-%m-%d"),
                "campaign_id": campaign_id,
                "campaign_name": f"Mock Campaign {i}",
                "campaign_status": "ENABLED",
                "channel_type": "SEARCH",
                "impressions": int(impressions),
                "clicks": int(clicks),
                "cost_micros": int(cost_micros),
                "conversions": float(conversions),
                "conversions_value": float(conv_value),
                "all_conversions": float(conversions),
                "all_conversions_value": float(conv_value),
            }
        )
    return rows


def _run_mock(conn, ctx: RunContext) -> int:
    run_id = str(uuid.uuid4())
    ingested_at = datetime.now(timezone.utc).isoformat()

    dates = _date_range_inclusive(ctx.end_date, ctx.lookback_days)
    all_rows: list[dict[str, Any]] = []
    for d in dates:
        all_rows.extend(
            _mock_campaign_daily_rows(
                run_id, ingested_at, ctx.customer_id or "0", d, seed=42
            )
        )

    insert_raw_campaign_daily(conn, all_rows)
    insert_snap_campaign_daily(conn, all_rows)

    latest_rows = count_latest_rows(conn)
    _print_summary(
        target_date=ctx.end_date,
        lookback_days=ctx.lookback_days,
        dates_refreshed=dates,
        campaign_rows_loaded=len(all_rows),
        latest_view_rows=latest_rows,
        cost=sum(float(r["cost_micros"]) for r in all_rows) / 1_000_000.0,
        conversions=sum(float(r["conversions"]) for r in all_rows),
        conversion_value=sum(float(r["conversions_value"]) for r in all_rows),
    )
    return 0


# ----------------------------
# TEST mode (Google Ads API)
# ----------------------------


def _require_google_ads() -> Any:
    try:
        from google.ads.googleads.client import GoogleAdsClient  # type: ignore

        return GoogleAdsClient
    except Exception as e:  # pragma: no cover
        raise RuntimeError(
            "google-ads library not available. Install deps and retry. "
            "Expected: `python -m pip install google-ads`"
        ) from e


def _load_google_ads_client_from_yaml(creds_path: str, mcc_id: str | None) -> Any:
    GoogleAdsClient = _require_google_ads()

    p = Path(creds_path)
    if not p.exists():
        raise FileNotFoundError(f"Google Ads credentials YAML not found: {creds_path}")

    with p.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}

    # Hard requirements for GoogleAdsClient
    missing = [
        k
        for k in ["developer_token", "client_id", "client_secret", "refresh_token"]
        if not cfg.get(k)
    ]
    if missing:
        raise ValueError(
            "Your secrets/google-ads.yaml is missing required fields: "
            + ", ".join(missing)
            + ". Add them, then retry."
        )

    if mcc_id:
        cfg["login_customer_id"] = _digits_only(mcc_id)

    # Strong default
    if "use_proto_plus" not in cfg:
        cfg["use_proto_plus"] = True

    return GoogleAdsClient.load_from_dict(cfg)


def _list_accessible_customers(client: Any) -> list[str]:
    customer_service = client.get_service("CustomerService")
    resp = customer_service.list_accessible_customers()
    out: list[str] = []
    for rn in getattr(resp, "resource_names", []):
        # "customers/1234567890"
        parts = str(rn).split("/")
        if parts and parts[-1].isdigit():
            out.append(parts[-1])
    return out


def _fetch_campaign_daily_rows(
    client: Any,
    customer_id: str,
    start_date: date,
    end_date: date,
    run_id: str,
    ingested_at: str,
) -> list[dict[str, Any]]:
    google_ads_service = client.get_service("GoogleAdsService")

    query = f"""
    SELECT
      segments.date,
      customer.id,
      campaign.id,
      campaign.name,
      campaign.status,
      campaign.advertising_channel_type,
      metrics.impressions,
      metrics.clicks,
      metrics.cost_micros,
      metrics.conversions,
      metrics.conversions_value,
      metrics.all_conversions,
      metrics.all_conversions_value
    FROM campaign
    WHERE segments.date BETWEEN '{start_date.strftime("%Y-%m-%d")}' AND '{end_date.strftime("%Y-%m-%d")}'
    """

    rows: list[dict[str, Any]] = []
    stream = google_ads_service.search_stream(customer_id=customer_id, query=query)
    for batch in stream:
        for r in batch.results:
            snap_date = str(r.segments.date)  # YYYY-MM-DD
            rows.append(
                {
                    "run_id": run_id,
                    "ingested_at": ingested_at,
                    "customer_id": _digits_only(str(r.customer.id)),
                    "snapshot_date": snap_date,
                    "campaign_id": int(r.campaign.id),
                    "campaign_name": str(r.campaign.name),
                    "campaign_status": str(r.campaign.status),
                    "channel_type": str(r.campaign.advertising_channel_type),
                    "impressions": int(r.metrics.impressions),
                    "clicks": int(r.metrics.clicks),
                    "cost_micros": int(r.metrics.cost_micros),
                    "conversions": float(r.metrics.conversions),
                    "conversions_value": float(r.metrics.conversions_value),
                    "all_conversions": float(r.metrics.all_conversions),
                    "all_conversions_value": float(r.metrics.all_conversions_value),
                }
            )
    return rows


def _run_test(conn, ctx: RunContext) -> int:
    if not ctx.google_ads_yaml:
        raise ValueError(
            "test mode requires google_ads_yaml (defaults to ./secrets/google-ads.yaml)"
        )

    # 1) Auth + build client
    client = _load_google_ads_client_from_yaml(ctx.google_ads_yaml, ctx.mcc_id)

    # 2) MCC discovery (always run, always print)
    accessible = _list_accessible_customers(client)
    print(f"Accessible customers: {len(accessible)}")
    if accessible:
        print("First 10 accessible customer IDs:", ", ".join(accessible[:10]))

    # 3) Select customer_id
    customer_id = ctx.customer_id
    if not customer_id:
        if not accessible:
            raise RuntimeError(
                "No accessible customers returned. Check your OAuth + developer token + account access."
            )
        customer_id = accessible[0]
        print(f"customer_id not set in config, using first accessible: {customer_id}")

    # 4) Fetch GAQL for trailing days
    run_id = str(uuid.uuid4())
    ingested_at = datetime.now(timezone.utc).isoformat()
    dates = _date_range_inclusive(ctx.end_date, ctx.lookback_days)
    start_date = dates[0]
    end_date = dates[-1]

    rows = _fetch_campaign_daily_rows(
        client, customer_id, start_date, end_date, run_id, ingested_at
    )

    # 5) Load into same DuckDB raw/snap tables (idempotency is handled in insert_*)
    insert_raw_campaign_daily(conn, rows)
    insert_snap_campaign_daily(conn, rows)

    latest_rows = count_latest_rows(conn)

    _print_summary(
        target_date=ctx.end_date,
        lookback_days=ctx.lookback_days,
        dates_refreshed=dates,
        campaign_rows_loaded=len(rows),
        latest_view_rows=latest_rows,
        cost=sum(float(r["cost_micros"]) for r in rows) / 1_000_000.0,
        conversions=sum(float(r["conversions"]) for r in rows),
        conversion_value=sum(float(r["conversions_value"]) for r in rows),
    )
    return 0


# ----------------------------
# Output
# ----------------------------


def _print_summary(
    target_date: date,
    lookback_days: int,
    dates_refreshed: list[date],
    campaign_rows_loaded: int,
    latest_view_rows: int,
    cost: float,
    conversions: float,
    conversion_value: float,
) -> None:
    # Minimal, stable, machine-readable-ish output (matches earlier UX)
    if dates_refreshed:
        dr = f"{dates_refreshed[0].strftime('%Y-%m-%d')}..{dates_refreshed[-1].strftime('%Y-%m-%d')}"
    else:
        dr = ""

    print("")
    print("Vertical Slice v1 (Campaign Daily)")
    print("")
    print(f"target_date        {target_date.strftime('%Y-%m-%d')}")
    print(f"lookback_days      {lookback_days}")
    print(f"dates_refreshed    {dr}")
    print(f"campaign_rows_loaded {campaign_rows_loaded}")
    print(f"latest_view_rows   {latest_view_rows}")
    print(f"cost               {cost:.6f}")
    print(f"conversions         {conversions:.2f}")
    print(f"conversion_value    {conversion_value:.2f}")
    print("")
