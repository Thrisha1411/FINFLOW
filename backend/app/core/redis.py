"""
Redis connection manager with resilient in-memory fallback for caching and pub/sub.
Ensures zero runtime errors when external Redis instance is starting or not configured.
"""
from typing import Optional, Dict, Any, Callable, List
import json
import logging
from backend.app.core.config import settings

logger = logging.getLogger("finflow.redis")

class MemoryCachePubSub:
    def __init__(self):
        self._store: Dict[str, Any] = {}
        self._listeners: Dict[str, List[Callable[[str], Any]]] = {}

    def get(self, key: str) -> Optional[str]:
        return self._store.get(key)

    def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        self._store[key] = value
        return True

    def delete(self, key: str) -> bool:
        if key in self._store:
            del self._store[key]
            return True
        return False

    def publish(self, channel: str, message: str) -> int:
        listeners = self._listeners.get(channel, [])
        for listener in listeners:
            try:
                listener(message)
            except Exception as e:
                logger.error(f"Error in pubsub listener: {e}")
        return len(listeners)

    def subscribe(self, channel: str, callback: Callable[[str], Any]):
        if channel not in self._listeners:
            self._listeners[channel] = []
        self._listeners[channel].append(callback)


class RedisService:
    def __init__(self):
        self._client = None
        self._memory = MemoryCachePubSub()
        self._is_redis_live = False
        self._connect()

    def _connect(self):
        if settings.REDIS_URL:
            try:
                import redis
                client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True, socket_connect_timeout=1)
                client.ping()
                self._client = client
                self._is_redis_live = True
                logger.info("Connected to Redis server.")
            except Exception as e:
                logger.warning(f"Live Redis not reached ({e}). Using in-memory PubSub/Cache engine.")
                self._is_redis_live = False

    def get(self, key: str) -> Optional[str]:
        if self._is_redis_live and self._client:
            try:
                return self._client.get(key)
            except Exception:
                pass
        return self._memory.get(key)

    def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        if self._is_redis_live and self._client:
            try:
                return bool(self._client.set(key, value, ex=ex))
            except Exception:
                pass
        return self._memory.set(key, value, ex=ex)

    def delete(self, key: str) -> bool:
        if self._is_redis_live and self._client:
            try:
                return bool(self._client.delete(key))
            except Exception:
                pass
        return self._memory.delete(key)

    def publish(self, channel: str, message: Any) -> int:
        payload = json.dumps(message) if not isinstance(message, str) else message
        if self._is_redis_live and self._client:
            try:
                return self._client.publish(channel, payload)
            except Exception:
                pass
        return self._memory.publish(channel, payload)

redis_service = RedisService()
