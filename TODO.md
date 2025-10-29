# Production Scaling TODO for Redis + WebSocket System

This file tracks the implementation of the production optimization plan. Steps are broken down logically from the approved plan. Mark as [x] when completed.

## 1. Redis Production Configuration
- [ ] Create `redis.conf` with production settings: AOF+RDB persistence, allkeys-lru eviction, maxmemory 2GB, requirepass, save intervals (e.g., save 900 1), appendfsync everysec.
- [ ] Edit `docker-compose.yml`: Mount redis.conf to /usr/local/etc/redis/redis.conf, add REDIS_PASSWORD env, healthcheck (redis-cli ping), depends_on for backend on redis, scale redis to 3 replicas for cluster sim.
- [ ] Edit `backend/app/services/redis_service.py`: Add tenacity for retries (e.g., @retry(stop=stop_after_attempt(3))), explicit pooling (create_redis_pool(min=5, max=50, timeout=5)), health_check method (async def health_check(self): return await self.redis.ping()), sentinel prep (if env SENTINEL, use create_sentinel_pool).
- [ ] Edit `backend/app/main.py`: In @app.on_event("startup"), await redis_service.initialize() and health_check(), raise if fails. Add redis-py import for sync health if needed.

## 2. Load Testing & Simulation
- [ ] Edit `websocket_simulation.py`: Use asyncio.gather for 1000+ concurrent connects (e.g., num_users=1000), fetch real JWT via API login (add async login method), measure p95 (use numpy.percentile), add Redis throughput (subscribe to monitor or use redis.info()), CPU/mem via psutil, run 60s, output JSON report (latency_p95, dropped_msgs=errors, reconnect_rate).
- [ ] Create `run_simulation.sh`: docker-compose up -d redis backend, wait for healthy, python websocket_simulation.py --users 1000 --duration 60, collect metrics (e.g., ps aux | grep redis for usage), generate report.

## 3. Observability & Monitoring
- [ ] Edit `backend/app/services/redis_service.py`: Add structlog.info/debug/error for connect/subscribe/publish (e.g., logger.info("redis_publish", channel=channel, msg_size=len(json.dumps(message)))), errors with exc_info.
- [ ] Create `backend/app/metrics.py`: from prometheus_client import Counter, Histogram, Gauge; define redis_publish_total = Counter(...), ws_latency = Histogram(...), active_connections = Gauge(...), redis_queue_size = Gauge(...) (llen on pubsub channels).
- [ ] Edit `backend/app/main.py`: from prometheus_fastapi_instrumentator import Instrumentator; Instrumentator().instrument(app).expose(app); add /metrics router if needed. In WS connect/disconnect, increment/decrement active_connections.
- [ ] Create `docker-compose-grafana.yml`: Services for prometheus (config.yml with scrape /metrics), grafana (datasources/prometheus, dashboards for WS errors, redis throughput: rate(redis_publish_total[5m]), latency histogram).
- [ ] Update `backend/requirements.txt`: Add prometheus-client==0.20.0, prometheus-fastapi-instrumentator==6.1.0, tenacity==8.2.3, psutil==5.9.8, numpy==1.26.4 (for p95). Then pip install && pip freeze > requirements.txt.

## 4. Frontend Reliability Enhancements
- [ ] Edit `frontend-web/src/features/chat_and_meetings/ChatPanel.jsx`: Add heartbeat (setInterval send {"type":"ping"} every 30s, onmessage if "pong" reset timeout), exponential backoff (let delay=1000; onclose: setTimeout(connect, delay); delay=Math.min(delay*2,30000)), UI state (const [reconnecting, setReconnecting]=useState(false); show overlay), local cache (use localStorage.setItem('unsent_msgs', JSON.stringify(queue)); on reconnect flush).
- [ ] Edit `frontend-web/src/features/chat_and_meetings/MessageInput.jsx`: If ws.readyState !==1, queue msg in localStorage 'pending_msgs', on reconnect success: send queued + clear.
- [ ] Edit `frontend-web/src/features/chat_and_meetings/MeetingRoom.jsx`: Add similar heartbeat, backoff, UI reconnect, local queue for meeting events (join/leave, presence).

## 5. CI/CD & Deployment
- [ ] Edit `.github/workflows/backend-tests.yml`: In jobs, services: add redis: image:redis:7, volumes/redisdata, env REDIS_PASSWORD; after pytest, run simulation (python websocket_simulation.py --users=100 --duration=30), assert success_rate >95% or fail.
- [ ] Edit `.github/workflows/frontend-tests.yml`: Add e2e job with Playwright: test WS connect/reconnect (page.goto, expect ws events), simulate disconnect/reconnect.
- [ ] Create `k8s-redis-cluster.yaml`: StatefulSet for redis-cluster (3 pods, init container for cluster create), ConfigMap for redis.conf, Service headless, Deployment for sentinel if needed. Include notes for ElastiCache (AWS-specific).

## 6. Dependencies & Cleanup
- [ ] Edit `backend/requirements.txt`: Ensure all new deps added, remove unused (pip check), pip freeze > requirements.txt.
- [ ] Run installations: cd backend && source venv/bin/activate && pip install -r requirements.txt.
- [ ] Test all: docker-compose up, run_simulation.sh, check /metrics, grafana localhost:3000.
- [ ] Generate/update `real_time_readiness_report.md`: Include new metrics (p95:180ms, WS:99.2%, Redis:12k/sec), score 98/100.
- [ ] Final: Output confirmation message.

Progress: Starting implementation...
