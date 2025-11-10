import aioredis
import structlog
from typing import Optional, List, Callable
import os
import json
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential, wait_exponential_jitter, retry_if_exception_type

logger = structlog.get_logger(__name__)

class RedisService:
    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None
        self.pubsub: Optional[aioredis.Redis] = None
        self.sentinel: Optional[aioredis.sentinel.Sentinel] = None
        self._initialized = False
        self._reconnect_task: Optional[asyncio.Task] = None
        self._reconnect_attempts = 0
        self._max_reconnect_attempts = 10
        self._base_reconnect_delay = 1.0

    def _build_redis_url(self) -> str:
        """Build Redis URL conditionally based on password presence"""
        password = os.getenv('REDIS_PASSWORD', '').strip()
        if password:
            return f"redis://:{password}@localhost:6379"
        else:
            return "redis://localhost:6379"

    @retry(stop=stop_after_attempt(5), wait=wait_exponential_jitter(initial=1, max=10), retry=retry_if_exception_type((aioredis.RedisError, aioredis.errors.ReplyError)))
    async def initialize(self):
        """Initialize Redis connection with retry logic and Sentinel support"""
        redis_url = os.getenv("REDIS_URL") or self._build_redis_url()
        password = os.getenv('REDIS_PASSWORD', '').strip()
        sanitized_url = redis_url.replace(password, '***') if password else redis_url
        try:
            sentinel_hosts = os.getenv("REDIS_SENTINEL_HOSTS")  # e.g., "host1:26379,host2:26379"
            sentinel_master = os.getenv("REDIS_SENTINEL_MASTER", "mymaster")

            if sentinel_hosts:
                # Use Redis Sentinel for HA
                sentinel_hosts_list = [(host.split(':')[0], int(host.split(':')[1])) for host in sentinel_hosts.split(',')]
                self.sentinel = aioredis.sentinel.Sentinel(
                    sentinel_hosts_list,
                    password=password if password else None,
                    socket_timeout=5,
                )
                self.redis = self.sentinel.master_for(sentinel_master)
                self.pubsub = self.sentinel.slave_for(sentinel_master)
                logger.info("Redis Sentinel initialized", sentinel_hosts=sentinel_hosts, master=sentinel_master)
            else:
                # Standard Redis pool - pass password explicitly if set
                self.redis = await aioredis.create_redis_pool(
                    redis_url,
                    password=password if password else None,
                    encoding='utf-8',
                    minsize=5,
                    maxsize=50,
                    timeout=5.0
                )

                # Create separate pubsub connection
                self.pubsub = await aioredis.create_redis_pool(
                    redis_url,
                    password=password if password else None,
                    encoding='utf-8',
                    minsize=2,
                    maxsize=10,
                    timeout=5.0
                )

            self._initialized = True
            logger.info("Redis service initialized", redis_url=sanitized_url, minsize=5, maxsize=50, sentinel=bool(sentinel_hosts), password_set=bool(password))
        except (aioredis.errors.ReplyError, aioredis.AuthenticationError) as e:
            logger.error("Redis authentication failed", error=str(e), redis_url=sanitized_url, password_set=bool(password))
            self._initialized = False
            raise
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
        if self._reconnect_task and not self._reconnect_task.done():
            self._reconnect_task.cancel()
            try:
                await self._reconnect_task
            except asyncio.CancelledError:
                pass
        if self.redis:
            await self.redis.close()
            self._initialized = False

    async def _auto_reconnect(self):
        """Auto-reconnect to Redis with exponential backoff"""
        password = os.getenv('REDIS_PASSWORD', '').strip()
        redis_url = os.getenv("REDIS_URL") or self._build_redis_url()
        while self._reconnect_attempts < self._max_reconnect_attempts:
            try:
                delay = self._base_reconnect_delay * (2 ** self._reconnect_attempts)
                logger.info(f"Attempting Redis reconnection in {delay:.1f}s (attempt {self._reconnect_attempts + 1}/{self._max_reconnect_attempts})")
                await asyncio.sleep(delay)

                self.redis = await aioredis.create_redis_pool(
                    redis_url,
                    password=password if password else None,
                    encoding='utf-8',
                    minsize=5,
                    maxsize=50,
                    timeout=5.0
                )

                # Test connection
                pong = await self.redis.ping()
                if pong == 'PONG':
                    self._initialized = True
                    self._reconnect_attempts = 0
                    from app.metrics import record_redis_reconnection
                    record_redis_reconnection()
                    logger.info("Redis reconnected successfully")
                    return
                else:
                    raise Exception("Ping failed")

            except Exception as e:
                self._reconnect_attempts += 1
                logger.error(f"Redis reconnection attempt {self._reconnect_attempts} failed", error=str(e))

        logger.error("Max Redis reconnection attempts reached, giving up")
        self._initialized = False

    async def ensure_connection(self):
        """Ensure Redis connection is alive, trigger reconnect if needed"""
        if not self._initialized:
            if not self._reconnect_task or self._reconnect_task.done():
                self._reconnect_task = asyncio.create_task(self._auto_reconnect())
            return False

        try:
            pong = await self.redis.ping()
            return pong == 'PONG'
        except Exception as e:
            logger.warning("Redis connection lost, triggering reconnect", error=str(e))
            self._initialized = False
            if not self._reconnect_task or self._reconnect_task.done():
                self._reconnect_task = asyncio.create_task(self._auto_reconnect())
            return False

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
        """Publish event to Redis pub/sub channel with connection health check"""
        await self.ensure_connection()
        if not self._initialized:
            return
        try:
            await self.redis.publish(channel, json.dumps(message))
            logger.info("Published event to Redis", channel=channel, message_size=len(json.dumps(message)), event_type=message.get('type', 'unknown'))
            from app.metrics import record_redis_publish, redis_pubsub_messages_total
            record_redis_publish(channel.split(':')[0])  # chat or meeting
            channel_type = channel.split(':')[0]  # e.g., 'chat' or 'meeting'
            redis_pubsub_messages_total.labels(channel_type=channel_type).inc()
        except Exception as e:
            from app.metrics import record_redis_error
            record_redis_error()
            logger.error("Failed to publish event to Redis", channel=channel, error=str(e), exc_info=True)

    async def create_redis_pool(self, url: str, password: Optional[str] = None) -> Optional[aioredis.Redis]:
        """Create a new Redis pool connection"""
        try:
            redis_pool = await aioredis.create_redis_pool(
                url,
                password=password,
                encoding='utf-8',
                minsize=5,
                maxsize=50,
                timeout=5.0
            )
            sanitized_url = url.replace(password or '', '***') if password else url
            logger.info("Created Redis pool", url=sanitized_url)
            return redis_pool
        except Exception as e:
            logger.error("Failed to create Redis pool", error=str(e), exc_info=True)
            return None

    async def publish(self, channel_name: str, message: str):
        """Publish message to Redis pub/sub channel"""
        await self.ensure_connection()
        if not self._initialized:
            return
        try:
            await self.redis.publish(channel_name, message)
            logger.info("Published message to Redis", channel=channel_name, message_size=len(message))
        except Exception as e:
            from app.metrics import record_redis_error
            record_redis_error()
            logger.error("Failed to publish message to Redis", channel=channel_name, error=str(e), exc_info=True)

    async def psubscribe(self, pattern: str, callback: Callable[[str], None]):
        """Subscribe to Redis pub/sub pattern and call callback on messages"""
        if not self._initialized:
            return
        try:
            redis_url = os.getenv("REDIS_URL") or self._build_redis_url()
            password = os.getenv('REDIS_PASSWORD', '').strip()
            pool = await self.create_redis_pool(redis_url, password=password if password else None)
            if not pool:
                return
            pubsub = await pool.pubsub()
            await pubsub.psubscribe(pattern)
            logger.info("Subscribed to Redis pattern", pattern=pattern)
            async for message in pubsub.listen():
                if message['type'] == 'pmessage':
                    await callback(message['data'])
        except Exception as e:
            logger.error("Failed to psubscribe to Redis pattern", pattern=pattern, error=str(e), exc_info=True)

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

    async def get(self, key: str) -> Optional[str]:
        """Get value from Redis by key"""
        await self.ensure_connection()
        if not self._initialized:
            return None
        try:
            result = await self.redis.get(key)
            return result.decode('utf-8') if result else None
        except Exception as e:
            logger.error("Failed to get from Redis", key=key, error=str(e))
            return None

    async def setex(self, key: str, seconds: int, value: str):
        """Set value in Redis with expiration"""
        await self.ensure_connection()
        if not self._initialized:
            return
        try:
            await self.redis.setex(key, seconds, value)
            logger.debug("Setex in Redis", key=key, seconds=seconds)
        except Exception as e:
            logger.error("Failed to setex in Redis", key=key, error=str(e))

    async def delete(self, key: str) -> int:
        """Delete key from Redis"""
        await self.ensure_connection()
        if not self._initialized:
            return 0
        try:
            deleted = await self.redis.delete(key)
            logger.debug("Deleted from Redis", key=key, deleted=deleted)
            return deleted
        except Exception as e:
            logger.error("Failed to delete from Redis", key=key, error=str(e))
            return 0

# Global Redis service instance
redis_service = RedisService()
