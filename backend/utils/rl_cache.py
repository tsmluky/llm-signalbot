from __future__ import annotations
import time, threading
from collections import deque
from typing import Any

class RateLimiter:
    def __init__(self, max_per_min: int):
        self.max = max_per_min
        self.win = 60.0
        self.q = deque()
        self.lock = threading.Lock()

    def allow(self) -> bool:
        now = time.time()
        with self.lock:
            while self.q and now - self.q[0] > self.win:
                self.q.popleft()
            if len(self.q) < self.max:
                self.q.append(now)
                return True
            return False

class TTLCache:
    def __init__(self, ttl_sec: int = 120, max_items: int = 256):
        self.ttl = ttl_sec
        self.max_items = max_items
        self.store: dict[str, tuple[float, Any]] = {}
        self.lock = threading.Lock()

    def get(self, key: str):
        now = time.time()
        with self.lock:
            v = self.store.get(key)
            if not v: return None
            ts, data = v
            if now - ts > self.ttl:
                del self.store[key]
                return None
            return data

    def set(self, key: str, value: Any):
        with self.lock:
            if len(self.store) >= self.max_items:
                oldest = min(self.store.items(), key=lambda kv: kv[1][0])[0]
                self.store.pop(oldest, None)
            self.store[key] = (time.time(), value)
