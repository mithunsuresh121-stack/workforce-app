import aioredis
import structlog
from typing import Optional, List
import os
import json
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = structlog.get_logger(__name__)

class RedisService:
    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None
        self._initialized = False

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10), retry=retry_if_exception_type(aioredis.RedisError))
    async def initialize(self):
        """Initialize Redis connection with retry logic"""
        try:
            redis_url = os.getenv("REDIS_URL", f"redis://:{os.getenv('REDIS_PASSWORD', 'workforce_redis_pw')}@localhost:6379")
            self.redis = await aioredis.create_redis_pool(
                redis_url,
                encoding='utf-8',
                minsize=5,
                maxsize=50,
                timeout=5.0
            )
            self._initialized = True
            logger.info("Redis service initialized", redis_url=redis_url.replace(os.getenv('REDIS_PASSWORD', ''), '***'), minsize=5, maxsize=50)
        except Exception as e:
            logger.error("Failed to initialize Redis after retries", error=str(e), exc_info=True)
            self._initialized = False
            raise

    async def health_check(self) -> bool:
        """Perform Redis health check"""
        if not self._initialized:
            return False
        try:
            pong = await self.redis.ping()
            logger.debug("Redis health check passed", pong=pong)
            return pong == 'PONG'
        except Exception as e:
            logger.error("Redis health check failed", error=str(e))
            return False

    async def close(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()
            self._initialized = False

    async def set_user_online(self, company_id: int, user_id: int, expire_seconds: int = 30):
        """Mark user as online with expiration"""
        if not self._initialized:
            return
        key = f"user:online:{company_id}:{user_id}"
        await self.redis.setex(key, expire_seconds, "1")
        logger.info("User marked online", company_id=company_id, user_id=user_id)

    async def is_user_online(self, company_id: int, user_id: int) -> bool:
        """Check if user is online"""
        if not self._initialized:
            return False
        key = f"user:online:{company_id}:{user_id}"
        result = await self.redis.exists(key)
        return bool(result)

    async def get_online_users(self, company_id: int) -> List[int]:
        """Get list of online user IDs for company"""
        if not self._initialized:
            return []
        pattern = f"user:online:{company_id}:*"
        keys = await self.redis.keys(pattern)
        user_ids = []
        for key in keys:
            try:
                user_id = int(key.split(":")[-1])
                user_ids.append(user_id)
            except ValueError:
                continue
        return user_ids

    async def set_typing_indicator(self, channel_id: int, user_id: int, expire_seconds: int = 5):
        """Set typing indicator for user in channel"""
        if not self._initialized:
            return
        key = f"channel:typing:{channel_id}:{user_id}"
        await self.redis.setex(key, expire_seconds, "1")

    async def get_typing_users(self, channel_id: int) -> List[int]:
        """Get list of users currently typing in channel"""
        if not self._initialized:
            return []
        pattern = f"channel:typing:{channel_id}:*"
        keys = await self.redis.keys(pattern)
        user_ids = []
        for key in keys:
            try:
                user_id = int(key.split(":")[-1])
                user_ids.append(user_id)
            except ValueError:
                continue
        return user_ids

    async def remove_typing_indicator(self, channel_id: int, user_id: int):
        """Remove typing indicator for user in channel"""
        if not self._initialized:
            return
        key = f"channel:typing:{channel_id}:{user_id}"
        await self.redis.delete(key)

    async def set_user_offline(self, company_id: int, user_id: int):
        """Mark user as offline"""
        if not self._initialized:
            return
        key = f"user:online:{company_id}:{user_id}"
        await self.redis.delete(key)
        logger.info("User marked offline", company_id=company_id, user_id=user_id)

    async def clear_typing_indicator(self, channel_id: int, user_id: int):
        """Clear typing indicator for user (alias for remove_typing_indicator)"""
        await self.remove_typing_indicator(channel_id, user_id)

    async def publish_event(self, channel: str, message: dict):
        """Publish event to Redis pub/sub channel"""
        if not self._initialized:
            return
        try:
            await self.redis.publish(channel, json.dumps(message))
            logger.info("Published event to Redis", channel=channel, message_size=len(json.dumps(message)), event_type=message.get('type', 'unknown'))
            from app.metrics import record_redis_publish
            record_redis_publish(channel.split(':')[0])  # chat or meeting
        except Exception as e:
            from app.metrics import record_redis_error
            record_redis_error()
            logger.error("Failed to publish event to Redis", channel=channel, error=str(e), exc_info=True)

    async def subscribe_to_events(self, channel: str):
        """Subscribe to Redis pub/sub channel (returns channel object for aioredis 1.3.1)"""
        if not self._initialized:
            return None
        try:
            # For aioredis 1.3.1, subscribe returns a list of channel objects
            channels = await self.redis.subscribe(channel)
            ch = channels[0] if channels else None
            logger.info("Subscribed to Redis channel", channel=channel)
            return ch
        except Exception as e:
            logger.error("Failed to subscribe to Redis channel", channel=channel, error=str(e), exc_info=True)
            return None

    async def store_read_receipt(self, channel_id: int, user_id: int, message_id: int):
        """Store read receipt in Redis"""
        if not self._initialized:
            return
        key = f"channel:read:{channel_id}:{user_id}"
        await self.redis.set(key, str(message_id), ex=86400)  # 24 hours TTL

    async def get_read_receipt(self, channel_id: int, user_id: int) -> Optional[int]:
        """Get last read message ID for user in channel"""
        if not self._initialized:
            return None
        key = f"channel:read:{channel_id}:{user_id}"
        result = await self.redis.get(key)
        return int(result) if result else None

    async def cleanup_stale_keys(self):
        """Cleanup stale Redis keys (run periodically)"""
        if not self._initialized:
            return
        # This would be called by a background task
        # For now, rely on TTL expiration
        pass

# Global Redis service instance
redis_service = RedisService()
