from __future__ import annotations
import os
from dataclasses import dataclass

@dataclass
class Settings:
    deepseek_api_key: str | None = os.getenv("DEEPSEEK_API_KEY")
    db_path: str = os.getenv("DB_PATH", "backend/data/signalbot.db")
    cache_ttl_sec: int = int(os.getenv("CACHE_TTL_SEC", "120"))
    rate_limit_per_min: int = int(os.getenv("RATE_LIMIT_PER_MIN", "30"))

settings = Settings()
