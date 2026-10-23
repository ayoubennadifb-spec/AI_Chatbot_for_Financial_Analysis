"""
Thread-safe LRU cache for LLM responses.
Identical queries return cached results instantly — no redundant API calls.
"""

import time
import hashlib
import threading
from collections import OrderedDict
import config


class LRUCache:
    def __init__(self, max_size: int = 256, ttl_secs: int = 3600):
        self._cache   = OrderedDict()
        self._lock    = threading.Lock()
        self._max     = max_size
        self._ttl     = ttl_secs
        self.hits     = 0
        self.misses   = 0

    def _key(self, query: str, intent: str) -> str:
        raw = f"{query.lower().strip()}::{intent}"
        return hashlib.md5(raw.encode()).hexdigest()

    def get(self, query: str, intent: str):
        key = self._key(query, intent)
        with self._lock:
            if key not in self._cache:
                self.misses += 1
                return None
            value, ts = self._cache[key]
            if time.time() - ts > self._ttl:
                del self._cache[key]
                self.misses += 1
                return None
            # Move to end (most recently used)
            self._cache.move_to_end(key)
            self.hits += 1
            return value

    def set(self, query: str, intent: str, value: str):
        key = self._key(query, intent)
        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
            self._cache[key] = (value, time.time())
            if len(self._cache) > self._max:
                self._cache.popitem(last=False)  # evict oldest

    def stats(self) -> dict:
        total = self.hits + self.misses
        return {
            'size':      len(self._cache),
            'max_size':  self._max,
            'hits':      self.hits,
            'misses':    self.misses,
            'hit_rate':  f'{(self.hits/total*100):.1f}%' if total else '0%',
        }


# Singleton shared across all requests
response_cache = LRUCache(
    max_size = config.CACHE_MAX_SIZE,
    ttl_secs = config.CACHE_TTL_SECS,
)
