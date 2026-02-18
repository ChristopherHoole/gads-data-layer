"""
Expiring cache implementation with TTL (Time To Live).

Prevents stale recommendations from being executed and fixes memory leaks.
"""

from time import time
from typing import Any, Dict, Optional


class ExpiringCache:
    """
    Cache with automatic expiration after TTL.
    
    Stores recommendations with timestamps and automatically removes expired entries.
    """
    
    def __init__(self, default_ttl: int = 3600):
        """
        Initialize expiring cache.
        
        Args:
            default_ttl: Default time-to-live in seconds (default: 1 hour)
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._default_ttl = default_ttl
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Store a value in cache with expiration.
        
        Args:
            key: Cache key
            value: Value to store
            ttl: Time-to-live in seconds (uses default if not specified)
        """
        ttl = ttl if ttl is not None else self._default_ttl
        expires_at = time() + ttl
        
        self._cache[key] = {
            'value': value,
            'expires_at': expires_at,
            'created_at': time()
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieve a value from cache.
        
        Args:
            key: Cache key
            default: Default value if key not found or expired
            
        Returns:
            Cached value or default
        """
        if key not in self._cache:
            return default
        
        entry = self._cache[key]
        
        # Check if expired
        if time() > entry['expires_at']:
            # Remove expired entry
            del self._cache[key]
            return default
        
        return entry['value']
    
    def delete(self, key: str) -> bool:
        """
        Delete a key from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if deleted, False if not found
        """
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    def clear(self) -> None:
        """Clear all cached items."""
        self._cache.clear()
    
    def cleanup_expired(self) -> int:
        """
        Remove all expired entries.
        
        Returns:
            Number of entries removed
        """
        now = time()
        expired_keys = [
            key for key, entry in self._cache.items()
            if now > entry['expires_at']
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dict with cache stats (size, expired count, etc.)
        """
        now = time()
        total = len(self._cache)
        expired = sum(1 for entry in self._cache.values() if now > entry['expires_at'])
        active = total - expired
        
        return {
            'total_entries': total,
            'active_entries': active,
            'expired_entries': expired,
            'ttl_seconds': self._default_ttl
        }
    
    def __len__(self) -> int:
        """Return number of cache entries (including expired)."""
        return len(self._cache)
    
    def __contains__(self, key: str) -> bool:
        """Check if key exists and is not expired."""
        return self.get(key) is not None
    
    def __setitem__(self, key: str, value: Any) -> None:
        """Allow dict-like assignment: cache[key] = value"""
        self.set(key, value)
    
    def __getitem__(self, key: str) -> Any:
        """Allow dict-like access: value = cache[key]"""
        result = self.get(key)
        if result is None:
            raise KeyError(key)
        return result
