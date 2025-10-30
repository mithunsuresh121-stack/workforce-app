from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry
import time
import asyncio
from app.services.redis_service import redis_service

# Create registry for metrics
registry = CollectorRegistry()

# WebSocket Metrics
ws_connections_active = Gauge(
    'workforce_ws_connections_active',
    'Number of active WebSocket connections',
    registry=registry
)

ws_messages_total = Counter(
    'workforce_ws_messages_total',
    'Total number of WebSocket messages sent',
    ['type'],
    registry=registry
)

ws_latency = Histogram(
    'workforce_ws_latency_seconds',
    'WebSocket message latency in seconds',
    buckets=(0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0),
    registry=registry
)

ws_errors_total = Counter(
    'workforce_ws_errors_total',
    'Total number of WebSocket errors',
    ['type'],
    registry=registry
)

# Redis Metrics
redis_publish_total = Counter(
    'workforce_redis_publish_total',
    'Total number of Redis publish operations',
    ['channel_type'],
    registry=registry
)

redis_queue_size = Gauge(
    'workforce_redis_queue_size',
    'Current size of Redis pubsub queues',
    ['channel'],
    registry=registry
)

redis_connection_errors_total = Counter(
    'workforce_redis_connection_errors_total',
    'Total number of Redis connection errors',
    registry=registry
)

# Redis pub/sub counters
redis_pubsub_messages_total = Counter(
    'workforce_redis_pubsub_messages_total',
    'Total number of Redis pub/sub messages',
    ['channel_type'],
    registry=registry
)

redis_pubsub_subscribers_active = Gauge(
    'workforce_redis_pubsub_subscribers_active',
    'Number of active Redis pub/sub subscribers',
    ['channel_type'],
    registry=registry
)

# Reliability Metrics
ws_reconnects_total = Counter(
    'workforce_ws_reconnects_total',
    'Total number of WebSocket reconnections',
    ['room_type'],
    registry=registry
)

ws_timeouts_total = Counter(
    'workforce_ws_timeouts_total',
    'Total number of WebSocket timeouts',
    ['room_type'],
    registry=registry
)

redis_reconnections_total = Counter(
    'workforce_redis_reconnections_total',
    'Total number of Redis reconnections',
    registry=registry
)

ws_backpressure_queue_size = Gauge(
    'workforce_ws_backpressure_queue_size',
    'Current size of WebSocket backpressure queue',
    ['room_type'],
    registry=registry
)

# Chat/Messaging Metrics
chat_messages_total = Counter(
    'workforce_chat_messages_total',
    'Total number of chat messages',
    ['channel_id'],
    registry=registry
)

typing_indicators_active = Gauge(
    'workforce_typing_indicators_active',
    'Number of active typing indicators',
    ['channel_id'],
    registry=registry
)

# Meeting Metrics
meeting_participants_active = Gauge(
    'workforce_meeting_participants_active',
    'Number of active meeting participants',
    ['meeting_id'],
    registry=registry
)

# Application Counters for external exporter - Redis-backed
messages_sent_total = Counter('workforce_messages_sent_total', 'Total messages sent', registry=registry)
meetings_joined_total = Counter('workforce_meetings_joined_total', 'Total meetings joined', registry=registry)

# Redis keys for persistent counters
MESSAGES_SENT_KEY = "metrics:messages_sent_total"
MEETINGS_JOINED_KEY = "metrics:meetings_joined_total"

# Helper functions
def increment_ws_connections():
    ws_connections_active.inc()

def decrement_ws_connections():
    ws_connections_active.dec()

def record_ws_message(msg_type: str):
    ws_messages_total.labels(type=msg_type).inc()

def record_ws_latency(latency_seconds: float):
    ws_latency.observe(latency_seconds)

def record_ws_error(error_type: str):
    ws_errors_total.labels(type=error_type).inc()

def record_redis_publish(channel_type: str):
    redis_publish_total.labels(channel_type=channel_type).inc()

def set_redis_queue_size(channel: str, size: int):
    redis_queue_size.labels(channel=channel).set(size)

def record_redis_error():
    redis_connection_errors_total.inc()

def record_chat_message(channel_id: int):
    chat_messages_total.labels(channel_id=str(channel_id)).inc()

def set_typing_indicators(channel_id: int, count: int):
    typing_indicators_active.labels(channel_id=str(channel_id)).set(count)

def set_meeting_participants(meeting_id: int, count: int):
    meeting_participants_active.labels(meeting_id=str(meeting_id)).set(count)

def record_ws_reconnect(room_type: str):
    ws_reconnects_total.labels(room_type=room_type).inc()

def record_ws_timeout(room_type: str):
    ws_timeouts_total.labels(room_type=room_type).inc()

def record_redis_reconnection():
    redis_reconnections_total.inc()

def set_ws_backpressure_queue_size(room_type: str, size: int):
    ws_backpressure_queue_size.labels(room_type=room_type).set(size)

async def increment_messages_sent():
    """Increment messages sent counter with Redis persistence"""
    try:
        # Increment in Redis for persistence
        current = await redis_service.redis.incr(MESSAGES_SENT_KEY)
        # Update in-memory counter to match
        messages_sent_total._value.set(current)
    except Exception:
        # Fallback to in-memory only
        messages_sent_total.inc()

async def increment_meetings_joined():
    """Increment meetings joined counter with Redis persistence"""
    try:
        # Increment in Redis for persistence
        current = await redis_service.redis.incr(MEETINGS_JOINED_KEY)
        # Update in-memory counter to match
        meetings_joined_total._value.set(current)
    except Exception:
        # Fallback to in-memory only
        meetings_joined_total.inc()

async def initialize_counters_from_redis():
    """Initialize counters from Redis on startup"""
    try:
        messages_count = await redis_service.redis.get(MESSAGES_SENT_KEY)
        if messages_count:
            messages_sent_total._value.set(int(messages_count))

        meetings_count = await redis_service.redis.get(MEETINGS_JOINED_KEY)
        if meetings_count:
            meetings_joined_total._value.set(int(meetings_count))
    except Exception:
        # Redis not available, start from 0
        pass
