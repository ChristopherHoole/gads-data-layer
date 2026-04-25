"""30-second in-memory idempotency cache for classify-terms.

Lost on Flask restart — that's acceptable for MVP. Keys are SHA256 of a
sorted-by-id JSON payload so a duplicate POST in the same window with
the same ids and prompt_version short-circuits to the prior response
without re-firing Claude.
"""
from __future__ import annotations

import hashlib
import json
import threading
import time

_TTL_S = 30
_cache: dict[str, tuple[float, dict]] = {}
_cache_lock = threading.Lock()


def make_key(client_id: str, flow: str, ids: list[int],
             prompt_version: str, force_reclassify: bool) -> str:
    payload = json.dumps({
        'client_id': client_id,
        'flow': flow,
        'ids': sorted(ids),
        'prompt_version': prompt_version,
        'force': force_reclassify,
    }, sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()


def get(key: str) -> dict | None:
    now = time.monotonic()
    with _cache_lock:
        entry = _cache.get(key)
        if entry is None:
            return None
        ts, value = entry
        if now - ts > _TTL_S:
            del _cache[key]
            return None
        return value


def set(key: str, value: dict) -> None:
    with _cache_lock:
        # Opportunistic GC: drop expired entries on every set so the cache
        # doesn't grow unbounded under bursty traffic.
        now = time.monotonic()
        for k in [k for k, (ts, _) in _cache.items() if now - ts > _TTL_S]:
            del _cache[k]
        _cache[key] = (time.monotonic(), value)
