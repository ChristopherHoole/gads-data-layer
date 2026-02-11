from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
import hashlib
import json

import yaml


@dataclass(frozen=True)
class SpendCaps:
    daily: Optional[float] = None
    monthly: Optional[float] = None


@dataclass(frozen=True)
class ClientConfig:
    client_id: str
    customer_id: str
    client_type: Optional[str] = None
    primary_kpi: Optional[str] = None
    currency: Optional[str] = None
    timezone: Optional[str] = None
    spend_caps: SpendCaps = field(default_factory=SpendCaps)
    protected_campaign_ids: List[str] = field(default_factory=list)

    raw: Dict[str, Any] = field(default_factory=dict)
    config_hash: str = ""


def _stable_hash(obj: Dict[str, Any]) -> str:
    payload = json.dumps(obj, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:12]


def _dig(d: Dict[str, Any], path: List[str]) -> Any:
    cur: Any = d
    for p in path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(p)
    return cur


def load_client_config(path: str | Path) -> ClientConfig:
    """
    Supports your current Chunk 1 config shape, e.g.:

    client_name: "Test_Client_001"
    client_type: "ecom"
    primary_kpi: "roas"
    google_ads:
      customer_id: "7372844356"
    spend_caps:
      daily: 50
      monthly: 1500
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Client config not found: {p}")

    raw = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        raise ValueError("Client config YAML must be a mapping/object at top level.")

    client_id = str(raw.get("client_id") or raw.get("client_name") or raw.get("name") or "UNKNOWN_CLIENT").strip()

    customer_id = _dig(raw, ["google_ads", "customer_id"]) or raw.get("customer_id")
    if customer_id is None or str(customer_id).strip() == "":
        raise ValueError("Client config must include google_ads.customer_id (or legacy top-level customer_id).")
    customer_id = str(customer_id).strip()

    client_type = raw.get("client_type")
    if client_type is not None:
        client_type = str(client_type).strip()

    primary_kpi = raw.get("primary_kpi")
    if primary_kpi is not None:
        primary_kpi = str(primary_kpi).strip()

    currency = raw.get("currency")
    if currency is not None:
        currency = str(currency).strip()

    timezone = raw.get("timezone")
    if timezone is not None:
        timezone = str(timezone).strip()

    spend_caps_raw = raw.get("spend_caps") or {}
    daily = spend_caps_raw.get("daily")
    monthly = spend_caps_raw.get("monthly")

    def _to_float(x: Any) -> Optional[float]:
        if x is None:
            return None
        try:
            v = float(x)
            if v <= 0:
                return None
            return v
        except Exception:
            return None

    spend_caps = SpendCaps(daily=_to_float(daily), monthly=_to_float(monthly))

    prot = raw.get("protected_entities") or {}
    campaign_ids = prot.get("campaign_ids") or prot.get("campaign_id_list") or []
    if isinstance(campaign_ids, (str, int)):
        campaign_ids = [campaign_ids]
    protected_campaign_ids = [str(x).strip() for x in campaign_ids if str(x).strip()]

    cfg_hash = _stable_hash(raw)

    return ClientConfig(
        client_id=client_id,
        customer_id=customer_id,
        client_type=client_type,
        primary_kpi=primary_kpi,
        currency=currency,
        timezone=timezone,
        spend_caps=spend_caps,
        protected_campaign_ids=protected_campaign_ids,
        raw=raw,
        config_hash=cfg_hash,
    )
