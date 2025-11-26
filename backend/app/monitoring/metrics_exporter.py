import time
import psutil
import asyncio
from prometheus_client import Gauge, Histogram, generate_latest
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import structlog
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.redis_service import redis_service
from app.metrics import registry, MESSAGES_SENT_KEY, MEETINGS_JOINED_KEY

logger = structlog.get_logger(__name__)

# System Metrics (local to exporter)
cpu_usage = Gauge('workforce_cpu_usage_percent', 'Current CPU usage percentage', registry=registry)
memory_usage = Gauge('workforce_memory_usage_percent', 'Current memory usage percentage', registry=registry)
memory_used_bytes = Gauge('workforce_memory_used_bytes', 'Memory used in bytes', registry=registry)

# Redis Metrics
redis_ping_latency = Histogram(
    'workforce_redis_ping_latency_seconds',
    'Redis ping latency in seconds',
    buckets=(0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0),
    registry=registry
)

# API Uptime
api_uptime_seconds = Gauge('workforce_api_uptime_seconds', 'API uptime in seconds', registry=registry)

# Start time for uptime calculation
start_time = time.time()

class MetricsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/metrics':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            output = generate_latest(registry)
            self.wfile.write(output)
        elif self.path == '/app_metrics':
            # Optional: Read structured logs (structlog JSON)
            # For now, return basic app metrics
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "app_metrics_endpoint"}')
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Suppress default HTTP server logs
        pass

def update_system_metrics():
    """Update system metrics periodically"""
    while True:
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_usage.set(cpu_percent)

            # Memory usage
            memory = psutil.virtual_memory()
            memory_usage.set(memory.percent)
            memory_used_bytes.set(memory.used)

            # API uptime
            uptime = time.time() - start_time
            api_uptime_seconds.set(uptime)

            time.sleep(5)  # Update every 5 seconds
        except Exception as e:
            logger.error("Error updating system metrics", error=str(e))

async def update_redis_metrics():
    """Update Redis metrics periodically"""
    while True:
        try:
            start = time.time()
            healthy = await redis_service.health_check()
            latency = time.time() - start

            if healthy:
                redis_ping_latency.observe(latency)
            else:
                logger.warning("Redis health check failed")

            await asyncio.sleep(10)  # Update every 10 seconds
        except Exception as e:
            logger.error("Error updating Redis metrics", error=str(e))

def run_metrics_server():
    """Run the metrics HTTP server"""
    server_address = ('', 9090)
    httpd = HTTPServer(server_address, MetricsHandler)
    logger.info("Metrics exporter server starting on port 9090")
    httpd.serve_forever()

def start_metrics_exporter():
    """Start the metrics exporter service"""
    # Start system metrics updater in background thread
    system_thread = threading.Thread(target=update_system_metrics, daemon=True)
    system_thread.start()

    # Start Redis metrics updater in background thread (not async for simplicity)
    redis_thread = threading.Thread(target=lambda: asyncio.run(update_redis_metrics_loop()), daemon=True)
    redis_thread.start()

    # Start HTTP server in background thread
    server_thread = threading.Thread(target=run_metrics_server, daemon=True)
    server_thread.start()

    logger.info("Metrics exporter service started")

async def update_redis_metrics_loop():
    """Loop for Redis metrics updates"""
    while True:
        try:
            start = time.time()
            healthy = await redis_service.health_check()
            latency = time.time() - start

            if healthy:
                redis_ping_latency.observe(latency)

                # Update persistent counters from Redis
                try:
                    messages_count = await redis_service.redis.get(MESSAGES_SENT_KEY)
                    meetings_count = await redis_service.redis.get(MEETINGS_JOINED_KEY)

                    # Update in-memory counters if Redis has values
                    if messages_count:
                        from app.metrics import messages_sent_total
                        messages_sent_total._value.set(int(messages_count))

                    if meetings_count:
                        from app.metrics import meetings_joined_total
                        meetings_joined_total._value.set(int(meetings_count))

                except Exception as e:
                    logger.debug("Could not update persistent counters from Redis", error=str(e))

            else:
                logger.warning("Redis health check failed")

            await asyncio.sleep(10)  # Update every 10 seconds
        except Exception as e:
            logger.error("Error updating Redis metrics", error=str(e))

if __name__ == "__main__":
    # Run standalone
    start_metrics_exporter()
    # Keep main thread alive
    while True:
        time.sleep(1)
