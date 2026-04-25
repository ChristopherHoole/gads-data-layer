"""Per-client lock manager.

Same Lock instance is shared across classify-terms, explain-row, and chat
for a given client_id, so any two AI calls on the same client serialise
naturally without contending across clients.

Lost on Flask restart — that's acceptable for a single-instance MVP.
"""
from __future__ import annotations

import threading

_locks: dict[str, threading.Lock] = {}
_meta_lock = threading.Lock()


def get_client_lock(client_id: str) -> threading.Lock:
    """Return the (singleton-per-client) Lock for this client."""
    with _meta_lock:
        if client_id not in _locks:
            _locks[client_id] = threading.Lock()
        return _locks[client_id]


class LockContentionError(Exception):
    """Raised when a per-client lock is already held. Endpoint maps to 409."""

    def __init__(self, client_id: str):
        super().__init__(
            f"another AI batch is in flight for client {client_id}"
        )
        self.client_id = client_id
