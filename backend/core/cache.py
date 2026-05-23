import logging
import redis
from django.conf import settings

logger = logging.getLogger(__name__)


class CacheManager:
    """Redis cache manager with rate limiting and check-and-set locks."""

    def __init__(self):
        try:
            self._redis = redis.Redis.from_url(
                getattr(settings, "REDIS_URL", "redis://localhost:6379/0"),
                decode_responses=True,
            )
            self._redis.ping()
        except Exception as e:
            logger.warning("Redis not available in core CacheManager: %s", e)
            self._redis = None

    def get(self, key):
        if not self._redis:
            return None
        try:
            return self._redis.get(key)
        except Exception as e:
            logger.error("Redis get error for key %s: %s", key, e)
            return None

    def set(self, key, value, timeout=None):
        if not self._redis:
            return False
        try:
            if timeout:
                return self._redis.setex(key, timeout, value)
            return self._redis.set(key, value)
        except Exception as e:
            logger.error("Redis set error for key %s: %s", key, e)
            return False

    def delete(self, key):
        if not self._redis:
            return False
        try:
            return bool(self._redis.delete(key))
        except Exception as e:
            logger.error("Redis delete error for key %s: %s", key, e)
            return False

    def exists(self, key):
        if not self._redis:
            return False
        try:
            return bool(self._redis.exists(key))
        except Exception as e:
            logger.error("Redis exists error for key %s: %s", key, e)
            return False

    def rate_limit(self, key, max_requests, window_seconds):
        """
        Check rate limiting for a specific key.
        Returns True if request is allowed, False if throttled.
        """
        if not self._redis:
            return True  # Fallback: allow request if cache is down
        try:
            limit_key = f"rate_limit:{key}"
            requests = self._redis.get(limit_key)

            if requests is None:
                # First request in window
                self._redis.setex(limit_key, window_seconds, "1")
                return True
            
            if int(requests) < max_requests:
                self._redis.incr(limit_key)
                return True

            return False
        except Exception as e:
            logger.error("Redis rate_limit error: %s", e)
            return True
class AlertDeduplication:
    """Redis-backed sliding window deduplication manager for generated alerts."""

    def __init__(self):
        try:
            self._redis = redis.Redis.from_url(
                getattr(settings, "REDIS_URL", "redis://localhost:6379/0"),
                decode_responses=True,
            )
            self._redis.ping()
        except Exception:
            self._redis = None

    def check_and_set(self, source_ip, alert_type, severity, ttl=300):
        if not self._redis:
            return False  # Do not dedup if Redis is down
        try:
            key = f"alert:dedup:{source_ip}:{alert_type}:{severity}"
            if self._redis.exists(key):
                self._redis.incr(f"{key}:count")
                return True
            self._redis.setex(key, ttl, "1")
            self._redis.setex(f"{key}:count", ttl, "1")
            return False
        except Exception as e:
            logger.error("Deduplication error in Redis check_and_set: %s", e)
            return False
