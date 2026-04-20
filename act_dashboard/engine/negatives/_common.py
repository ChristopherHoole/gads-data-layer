"""Shared text-normalization helpers for the Negatives engine.

CRITICAL: these run symmetrically on both sides of any match.
- Data side: config fields (services_advertised, service_locations,
  client_brand_terms), negative-list keyword_text.
- Query side: the search_term being classified.

Example: service_locations stores "earl's court"; normalize -> "earl s court".
A query "Earl's Court dental" -> tokens [earl, s, court, dental].
Location membership check: "earl s court" IS NOT substring of the tokens
joined, but each token CAN match individually against the normalized set.
This asymmetry is why Pass 1 Rule 4 iterates tokens, while Rule 1/3/5/6 use
phrase-substring matching on the normalized string.
"""
import re

_PUNCT_RE = re.compile(r"[^\w\s]")


def normalize(text: str | None) -> str:
    """Lowercase, strip non-word chars (keeping spaces), collapse whitespace."""
    if not text:
        return ""
    text = text.lower()
    text = _PUNCT_RE.sub(" ", text)
    return " ".join(text.split())


def tokenize(text: str | None) -> list[str]:
    """Return normalize(text).split() — tokens in original order."""
    return normalize(text).split()


def normalize_set(items: list[str] | str | None) -> set[str]:
    """Normalize a list (or comma-separated string) of phrases into a set.
    Empty input -> empty set."""
    if not items:
        return set()
    if isinstance(items, str):
        items = [p for p in items.split(',') if p.strip()]
    return {normalize(x) for x in items if x and str(x).strip()}


def tokenize_set(items: list[str] | str | None) -> set[str]:
    """Flatten a list (or comma-separated string) of phrases into a set of tokens."""
    if not items:
        return set()
    if isinstance(items, str):
        items = [p for p in items.split(',') if p.strip()]
    result: set[str] = set()
    for item in items:
        result.update(tokenize(item))
    return result


def phrase_appears_in(phrases: set[str], text_normalized: str) -> bool:
    """True if any non-empty phrase in `phrases` is a substring of the
    already-normalized text. Empty set / empty text -> False."""
    if not phrases or not text_normalized:
        return False
    for p in phrases:
        if p and p in text_normalized:
            return True
    return False
