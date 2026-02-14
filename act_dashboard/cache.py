"""
In-memory caching layer for dashboard performance.
"""

import time
from typing import Any, Optional, Callable
from functools import wraps


class SimpleCache:
    """
    Simple in-memory cache with TTL (time-to-live).

    Thread-safe is NOT guaranteed - suitable for single-threaded Flask dev server.
    For production, use Redis or memcached.
    """

    def __init__(self, default_ttl: int = 300):
        """
        Initialize cache.

        Args:
            default_ttl: Default time-to-live in seconds (default: 5 minutes)
        """
        self._cache = {}
        self.default_ttl = default_ttl

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value if exists and not expired, None otherwise
        """
        if key not in self._cache:
            return None

        value, expiry = self._cache[key]

        if time.time() > expiry:
            # Expired - remove from cache
            del self._cache[key]
            return None

        return value

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (None = use default)
        """
        ttl = ttl if ttl is not None else self.default_ttl
        expiry = time.time() + ttl
        self._cache[key] = (value, expiry)

    def delete(self, key: str):
        """Delete key from cache."""
        if key in self._cache:
            del self._cache[key]

    def clear(self):
        """Clear all cached values."""
        self._cache.clear()

    def size(self) -> int:
        """Get number of cached items."""
        return len(self._cache)


# Global cache instance
cache = SimpleCache(default_ttl=300)  # 5 minutes


def cached(ttl: int = 300, key_prefix: str = ""):
    """
    Decorator to cache function results.

    Args:
        ttl: Time-to-live in seconds
        key_prefix: Prefix for cache key

    Usage:
        @cached(ttl=60, key_prefix='dashboard')
        def get_dashboard_data(customer_id):
            # expensive operation
            return data
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            key_parts = [key_prefix, func.__name__]

            # Add args to key
            for arg in args:
                if isinstance(arg, (str, int, float, bool)):
                    key_parts.append(str(arg))
                else:
                    # For complex objects, use hash
                    key_parts.append(str(hash(str(arg))))

            # Add kwargs to key (sorted for consistency)
            for k in sorted(kwargs.keys()):
                v = kwargs[k]
                if isinstance(v, (str, int, float, bool)):
                    key_parts.append(f"{k}:{v}")
                else:
                    key_parts.append(f"{k}:{hash(str(v))}")

            cache_key = ":".join(key_parts)

            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result

            # Cache miss - call function
            result = func(*args, **kwargs)

            # Store in cache
            cache.set(cache_key, result, ttl=ttl)

            return result

        return wrapper

    return decorator


def cache_client_config(config_path: str, ttl: int = 300) -> Any:
    """
    Cache client config with TTL.

    Args:
        config_path: Path to config file
        ttl: Time-to-live in seconds

    Returns:
        Cached config or newly loaded config
    """
    cache_key = f"config:{config_path}"

    # Try cache
    config = cache.get(cache_key)
    if config is not None:
        return config

    # Load from file
    import yaml

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    # Cache it
    cache.set(cache_key, config, ttl=ttl)

    return config
