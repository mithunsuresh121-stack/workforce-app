import aioredis
import structlog
from typing import Optional, List
import os

logger = structlog.get_logger(__name__)

class RedisService:
    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None
        self._initialized = False

    async def initialize(self):
        """Initialize Redis connection"""
        try:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
            self.redis = aioredis.from_url(redis_url, decode_responses=True)
            self._initialized = True
            logger.info("Redis service initialized", redis_url=redis_url)
        except Exception as e:
            logger.error("Failed to initialize Redis", error=str(e))
            self._initialized = False

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

# Global Redis service instance
redis_service = RedisService()
