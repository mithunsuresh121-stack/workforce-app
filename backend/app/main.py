import asyncio

import structlog
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.config import Base, engine, settings
from app.custom_json_response import CustomJSONResponse
from app.models import *
from app.routers import (admin, ai, approvals, attendance, auth, chat,
                         companies, dashboard)
from app.routers import documents_router as documents
from app.routers import employees, leaves, meetings, notification_preferences
from app.routers import notifications_router as notifications
from app.routers import (org, payroll, procurement, profile, shifts, tasks,
                         websocket_manager)

# Set up structured logging with structlog as primary logger
shared_processors = [
    structlog.stdlib.filter_by_level,
    structlog.stdlib.add_logger_name,
    structlog.stdlib.add_log_level,
    structlog.stdlib.PositionalArgumentsFormatter(),
    structlog.processors.TimeStamper(fmt="iso"),
    structlog.processors.StackInfoRenderer(),
    structlog.processors.format_exc_info,
    structlog.processors.UnicodeDecoder(),
    # Add contextual processors for user_id, endpoint, etc.
    structlog.processors.add_log_level,
    structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
    # Add mandatory fields processor
    lambda logger, method_name, event_dict: event_dict.update(
        {
            "event": event_dict.get("event", method_name),
            "timestamp": event_dict.get("timestamp"),
            "user_id": event_dict.get("user_id", None),
            "company_id": event_dict.get("company_id", None),
            "level": event_dict.get("level", "INFO"),
        }
    )
    or event_dict,
    structlog.processors.JSONRenderer(),  # For structured output
]

structlog.configure(
    processors=shared_processors,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Only create tables when running the app directly, not when imported for testing
if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Workforce App", version="1.0", default_response_class=CustomJSONResponse
)


# Add request logging middleware with contextual data
@app.middleware("http")
async def log_requests(request: Request, call_next):
    import time

    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    # Extract user_id from token if available (simplified for demo)
    user_id = None
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.startswith("Bearer "):
        # In real implementation, decode JWT to get user_id
        user_id = "extracted_user_id"  # Placeholder

    # Enhanced observability: log admin actions and request duration
    is_admin_endpoint = request.url.path.startswith("/api/admin")
    if is_admin_endpoint:
        from app.db import SessionLocal
        from app.services.audit_service import AuditService

        db = SessionLocal()
        try:
            AuditService.log_admin_action(
                db=db,
                action="ENDPOINT_ACCESS",
                user_id=(
                    int(user_id) if user_id and user_id != "extracted_user_id" else None
                ),
                company_id=None,  # Will be set in endpoint if needed
                details={
                    "endpoint": request.url.path,
                    "method": request.method,
                    "duration_ms": process_time * 1000,
                },
            )
        finally:
            db.close()

    logger.info(
        "HTTP Request",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        process_time=f"{process_time:.4f}s",
        user_agent=request.headers.get("user-agent", ""),
        remote_addr=request.client.host if request.client else None,
        user_id=user_id,
        endpoint=request.url.path,
        log_level="INFO",
    )
    return response


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS or [
        "http://localhost:3000",  # Development frontend
        "https://app.workforce.com",  # Production frontend
        "https://workforce-app.com",  # Alternative production domain
        "https://app.workforce-app.com",  # Specified production frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(tasks.router, prefix="/api")
app.include_router(companies.router, prefix="/api")
app.include_router(employees.router, prefix="/api")
app.include_router(leaves.router, prefix="/api")
app.include_router(shifts.router, prefix="/api")
app.include_router(payroll.router, prefix="/api")
app.include_router(attendance.router, prefix="/api")
app.include_router(notifications, prefix="/api")
app.include_router(notification_preferences.router, prefix="/api")
app.include_router(profile.router, prefix="/api")
app.include_router(documents, prefix="/api/documents")
app.include_router(chat.router, prefix="/api/chat")
app.include_router(meetings.router, prefix="/api/meetings")
app.include_router(org.router)
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(ai.router, prefix="/api/ai")
app.include_router(approvals.router, prefix="/api/approvals")
app.include_router(procurement.router, prefix="/api")
app.include_router(websocket_manager.router, prefix="/api/ws")

# Initialize Prometheus instrumentation
instrumentator = Instrumentator().instrument(app)


@app.on_event("startup")
async def startup_event():
    # Initialize Redis with health check
    try:
        await redis_service.initialize()
        healthy = await redis_service.health_check()
        if not healthy:
            logger.warning(
                "Redis health check failed, proceeding without Redis features"
            )
        else:
            logger.info("Redis initialized and healthy on startup")
    except Exception as e:
        logger.error(
            "Failed to initialize Redis on startup, proceeding without Redis features",
            error=str(e),
            exc_info=True,
        )
        # Do not raise to allow FastAPI to start; Redis-dependent features will be disabled

    # Initialize metrics counters from Redis
    try:
        await initialize_counters_from_redis()
        logger.info("Metrics counters initialized from Redis")
    except Exception as e:
        logger.warning("Failed to initialize metrics counters from Redis", error=str(e))

    # Seed demo user conditionally
    if settings.APP_ENV == "development":
        from app.seed_demo_user import seed_demo_user

        db = next(get_db())
        seed_demo_user(db)

    # Start Redis subscriber for chat channels
    asyncio.create_task(redis_subscriber())


async def redis_subscriber():
    """Subscribe to Redis pub/sub for chat channels and forward to WS"""

    async def callback(message_data: str):
        try:
            data = json.loads(message_data)
            channel_id = int(data.get("channel_id", 0))  # Extract from payload if needed
            await ws_manager.broadcast(channel_id, message_data)
            logger.info("redis_sub_forward", channel_id=channel_id)
        except Exception as e:
            logger.error("Error in Redis subscriber callback", error=str(e))

    await redis_service.psubscribe("chat:channel:*:pub", callback)


app.include_router(dashboard.router, prefix="/api")


@app.get("/")
def root():
    return {"message": f"Welcome to the Workforce App! Environment: {settings.APP_ENV}"}


@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/test")
def test_endpoint():
    return {"test": "value", "number": 123, "boolean": True}


@app.get("/welcome")
def welcome_endpoint(request: Request):
    logger.info(
        "Welcome endpoint accessed",
        method=request.method,
        path=request.url.path,
        user_agent=request.headers.get("user-agent", ""),
        remote_addr=request.client.host if request.client else None,
    )
    return {"message": "Welcome to the Workforce App!"}


@app.get("/hello")
def hello_endpoint(request: Request):
    logger.info(
        "Hello endpoint accessed",
        method=request.method,
        path=request.url.path,
        user_agent=request.headers.get("user-agent", ""),
        remote_addr=request.client.host if request.client else None,
    )
    return {"message": "Hello, welcome to the Workforce API!"}


@app.get("/metrics")
def metrics_endpoint():
    """Expose Prometheus metrics from FastAPI app"""
    from prometheus_client import generate_latest

    from app.metrics import registry

    return Response(
        content=generate_latest(registry), media_type="text/plain; charset=utf-8"
    )
