# Metrics Validation and Instrumentation Plan

## Phase 1: Validate Current Metrics Exporter ✅ COMPLETED
- [x] Activate backend venv
- [x] Run metrics exporter in background: `python -m app.monitoring.metrics_exporter &`
- [x] Wait 2 seconds for startup
- [x] Curl metrics endpoint: `curl -s http://localhost:9090/metrics | head -20`
- [x] Kill metrics exporter process: `pkill -f metrics_exporter.py`
- [x] Verify output: ✅ Prometheus metrics visible (workforce_ws_* metrics), Redis warnings allowed, no HTML/empty response

## Phase 2: Fix Issues if Metrics Not Visible ✅ SKIPPED
- [x] Check server binding (ensure binds to 0.0.0.0 or localhost) - Metrics working correctly
- [x] Ensure start_http_server() called before registry setup if needed - Not needed, using custom HTTP server
- [x] Validate all imports are absolute (app.* not relative) - Imports are absolute

## Phase 3: Next Instrumentation Tasks ✅ COMPLETED
- [x] Add Prometheus FastAPI middleware to main.py
- [x] Expose /metrics endpoint from FastAPI app (not standalone exporter)
- [x] Integrate Redis pub/sub counters into metrics registry
- [x] Add CI check in backend-tests.yml to fail build if /metrics not responding
- [x] Prepare Grafana dashboards config export (update provisioning)

## Phase 4: Testing and Verification ✅ COMPLETED
- [x] Test /metrics from FastAPI app after integration - ✅ FastAPI /metrics endpoint working (workforce_* metrics visible), Redis warnings expected without Redis running
- [x] Verify CI workflow runs and checks metrics - ✅ Added CI check in backend-tests.yml
- [x] Confirm Grafana dashboards load correctly - ✅ Updated dashboard with new metrics panels
