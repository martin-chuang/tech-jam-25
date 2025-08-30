"""Redis service for caching and session management."""

import json
import logging
from typing import Optional, Any, Dict
import redis
from ..common.config.config_loader import ConfigLoader

class RedisEngine:
    """Redis service for caching and session management."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._client: Optional[redis.Redis] = None
        self.config = ConfigLoader.load_config()
        self._connect()

    def _connect(self) -> None:
        """Establish Redis connection."""
        try:
            self._client = redis.Redis(
                host=self.config.redis_host,
                port=self.config.redis_port,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30,
            )
            # Test connection
            self._client.ping()
            self.logger.info("Successfully connected to Redis")
        except Exception as e:
            self.logger.warning(
                f"Redis not available: {str(e)} - Running in fallback mode"
            )
            self._client = None

    def _ensure_connection(self) -> None:
        """Ensure Redis connection is alive."""
        if not self._client:
            self._connect()
        else:
            try:
                self._client.ping()
            except redis.ConnectionError:
                self.logger.warning("Redis connection lost, reconnecting...")
                self._connect()

        # If still no client after connection attempt, we're in fallback mode
        if not self._client:
            raise redis.ConnectionError(
                "Redis not available - running in fallback mode"
            )

    def get(self, key: str) -> Optional[str]:
        """Get value by key."""
        try:
            self._ensure_connection()
            return self._client.get(key)
        except Exception as e:
            self.logger.error(f"Redis GET error for key {key}: {str(e)}")
            return None

    def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        """Set key-value pair with optional TTL."""
        try:
            self._ensure_connection()
            if ttl:
                return self._client.setex(key, ttl, value)
            else:
                return self._client.set(key, value)
        except Exception as e:
            self.logger.error(f"Redis SET error for key {key}: {str(e)}")
            return False

    def delete(self, key: str) -> bool:
        """Delete key."""
        try:
            self._ensure_connection()
            return bool(self._client.delete(key))
        except Exception as e:
            self.logger.error(f"Redis DELETE error for key {key}: {str(e)}")
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists."""
        try:
            self._ensure_connection()
            return bool(self._client.exists(key))
        except Exception as e:
            self.logger.error(f"Redis EXISTS error for key {key}: {str(e)}")
            return False

    def get_json(self, key: str) -> Optional[Dict[str, Any]]:
        """Get JSON value by key."""
        try:
            value = self.get(key)
            if value:
                return json.loads(value)
            return None
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decode error for key {key}: {str(e)}")
            return None

    def set_json(
        self, key: str, value: Dict[str, Any], ttl: Optional[int] = None
    ) -> bool:
        """Set JSON value with optional TTL."""
        try:
            json_str = json.dumps(value)
            return self.set(key, json_str, ttl)
        except json.JSONEncodeError as e:
            self.logger.error(f"JSON encode error for key {key}: {str(e)}")
            return False

    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment counter."""
        try:
            self._ensure_connection()
            return self._client.incr(key, amount)
        except Exception as e:
            self.logger.error(f"Redis INCR error for key {key}: {str(e)}")
            return None

    def expire(self, key: str, ttl: int) -> bool:
        """Set TTL for existing key."""
        try:
            self._ensure_connection()
            return bool(self._client.expire(key, ttl))
        except Exception as e:
            self.logger.error(f"Redis EXPIRE error for key {key}: {str(e)}")
            return False

    def get_session_key(self, user_id: str, session_type: str = "chat") -> str:
        """Generate session key for user."""
        return f"session:{session_type}:{user_id}"

    def get_file_cache_key(self, user_id: str, file_hash: str) -> str:
        """Generate file cache key."""
        return f"file_cache:{user_id}:{file_hash}"

    def get_anonymization_cache_key(self, content_hash: str) -> str:
        """Generate anonymization cache key."""
        return f"anon_cache:{content_hash}"

    def health_check(self) -> bool:
        """Check Redis health."""
        try:
            self._ensure_connection()
            self._client.ping()
            return True
        except Exception:
            return False
