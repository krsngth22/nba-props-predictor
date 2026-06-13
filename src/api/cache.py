import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import json
import redis
from typing import Optional, Any
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
CACHE_TTL = 3600

try:
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=True,
        socket_connect_timeout=2
    )
    redis_client.ping()
    logger.info("Redis connected successfully")
    REDIS_AVAILABLE = True
except Exception as e:
    logger.warning(f"Redis not available: {e}. Caching disabled.")
    redis_client = None
    REDIS_AVAILABLE = False

def get_cached(key: str) -> Optional[Any]:
    if not REDIS_AVAILABLE or redis_client is None:
        return None
    try:
        value = redis_client.get(key)
        if value:
            return json.loads(value)
    except Exception:
        return None
    return None

def set_cached(key: str, value: Any, ttl: int = CACHE_TTL) -> bool:
    if not REDIS_AVAILABLE or redis_client is None:
        return False
    try:
        redis_client.setex(key, ttl, json.dumps(value, default=str))
        return True
    except Exception:
        return False

def invalidate_cache(pattern: str) -> int:
    if not REDIS_AVAILABLE or redis_client is None:
        return 0
    try:
        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)
        return len(keys)
    except Exception:
        return 0

def get_cache_stats() -> dict:
    if not REDIS_AVAILABLE or redis_client is None:
        return {"available": False}
    try:
        info = redis_client.info()
        return {
            "available": True,
            "connected_clients": info.get("connected_clients"),
            "used_memory_human": info.get("used_memory_human"),
            "total_keys": redis_client.dbsize()
        }
    except Exception:
        return {"available": False}
