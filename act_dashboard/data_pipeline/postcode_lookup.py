"""N1a — Postcode -> placename lookup (Layer 3 for service_locations).

Uses postcodes.io free public API (https://api.postcodes.io/outcodes/{outcode}).
Caches results to postcode_cache.json so subsequent clients with overlapping
postcodes reuse the data (and we're friendly to the free API).

Usage:
    from act_dashboard.data_pipeline.postcode_lookup import (
        extract_outcode, placenames_for_outcode, build_layer3,
    )

Run as a script to pre-warm the cache for an outcode list:
    python -m act_dashboard.data_pipeline.postcode_lookup
"""
import json
import re
import time
from pathlib import Path
from typing import Iterable

import urllib.request
import urllib.error

CACHE_PATH = Path(__file__).resolve().parent / "postcode_cache.json"
API_URL = "https://api.postcodes.io/outcodes/{outcode}"

# Outcode pattern: 1-2 letters, 1 digit, optional letter/digit suffix.
# Matches sw4, sw1a, e1w, ec1, n10, al2, wd17 etc.
_OUTCODE_RE = re.compile(r"^[a-z]{1,2}[0-9][a-z0-9]?$", re.IGNORECASE)

# Central-London named areas don't map to single outcodes; hand-curate coverage
# so searches like "implants holborn" still resolve via the named area.
# Values are lowercase placenames added to the location list.
NAMED_AREA_MAPPINGS: dict[str, list[str]] = {
    "westminster": [
        "westminster", "victoria", "pimlico", "st james's", "st james",
        "charing cross", "whitehall",
    ],
    "mayfair": ["mayfair", "grosvenor", "park lane", "bond street"],
    "marylebone": [
        "marylebone", "regents park", "regent's park", "baker street",
        "portman square",
    ],
    "belgravia": ["belgravia", "knightsbridge", "eaton square"],
    "earl's court": ["earls court", "earl's court", "west brompton"],
    "city of london": [
        "city of london", "the city", "holborn", "covent garden",
        "farringdon", "barbican", "smithfield", "moorgate",
    ],
}


def _load_cache() -> dict:
    if CACHE_PATH.exists():
        return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    return {}


def _save_cache(cache: dict) -> None:
    CACHE_PATH.write_text(
        json.dumps(cache, indent=2, sort_keys=True, ensure_ascii=False),
        encoding="utf-8",
    )


def extract_outcode(term: str) -> str | None:
    """Return the outcode from a raw term if it contains one, else None.

    Handles entries like 'sw4', 'SW1A', 'tw10 5hz' (-> tw10), 'westminster' (None).
    """
    if not term:
        return None
    first = term.strip().split()[0].lower()
    return first if _OUTCODE_RE.match(first) else None


def placenames_for_outcode(outcode: str, cache: dict | None = None,
                           sleep_between: float = 0.1) -> list[str]:
    """Look up an outcode via postcodes.io, returning a deduped list of
    lowercase placenames (admin_ward + admin_district + parish).
    Missing / API-failed outcodes cache an empty list so we don't retry.
    """
    outcode = outcode.lower()
    cache_local = cache if cache is not None else _load_cache()
    if outcode in cache_local:
        return list(cache_local[outcode])

    names: list[str] = []
    try:
        req = urllib.request.Request(
            API_URL.format(outcode=outcode.upper()),
            headers={"User-Agent": "ACT/1.0 (postcode-lookup)"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        if payload.get("status") == 200 and isinstance(payload.get("result"), dict):
            result = payload["result"]
            for key in ("admin_ward", "admin_district", "parish"):
                vals = result.get(key) or []
                if isinstance(vals, str):
                    vals = [vals]
                for v in vals:
                    if v and isinstance(v, str):
                        names.append(v.strip().lower())
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError):
        pass  # cache empty list on failure

    # Dedupe, preserve order
    seen = set()
    deduped = []
    for n in names:
        if n and n not in seen:
            seen.add(n)
            deduped.append(n)

    cache_local[outcode] = deduped
    if cache is None:  # only auto-persist if we loaded it ourselves
        _save_cache(cache_local)
    if sleep_between:
        time.sleep(sleep_between)
    return deduped


def _clean_placename(name: str) -> str | None:
    """Filter raw placenames before they enter Layer 3.

    Rules:
    - drop 'X, unparished area' admin rows (not useful placenames; would also
      break the comma-separated storage format for service_locations)
    - drop any remaining entry that contains a literal comma (same reason)
    """
    n = (name or '').strip().lower()
    if not n:
        return None
    if n.endswith(', unparished area'):
        return None
    if ',' in n:
        return None
    return n


def build_layer3(raw_terms: Iterable[str]) -> tuple[list[str], dict]:
    """Given Layer 1 raw targeting terms, return a deduped lowercase list of
    Layer 3 placenames (from postcodes.io + named-area mappings). Also returns
    the cache dict (caller can inspect / persist).
    """
    cache = _load_cache()
    layer3: list[str] = []
    seen = set()

    def _add(name: str) -> None:
        cleaned = _clean_placename(name)
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            layer3.append(cleaned)

    for term in raw_terms:
        t = term.strip().lower()
        if not t:
            continue
        outcode = extract_outcode(t)
        if outcode:
            for name in placenames_for_outcode(outcode, cache=cache):
                _add(name)
        else:
            # Named area — add hard-coded mapping if known
            for name in NAMED_AREA_MAPPINGS.get(t, []):
                _add(name)

    _save_cache(cache)
    return layer3, cache


if __name__ == "__main__":
    # Self-test: build Layer 3 for DBD's full Layer 1.
    import sys
    # Import the seed list from the seed script if present; else a tiny sample.
    try:
        from act_dashboard.db.migrations.seed_dbd_client_profile import DBD_LAYER1
    except ImportError:
        DBD_LAYER1 = ["sw4", "nw3", "w6", "westminster", "mayfair"]
    layer3, cache = build_layer3(DBD_LAYER1)
    print(f"Cache entries: {len(cache)}")
    print(f"Layer 3 placename count: {len(layer3)}")
    print("First 30:", layer3[:30])
