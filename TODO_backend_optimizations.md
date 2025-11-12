# Backend Optimizations TODO

## 1. Extend Redis Service for Caching
- [ ] Add notification caching methods to `redis_service.py` (set/get/invalidate)

## 2. Update Notifications Router
- [ ] Modify `/api/notifications/` endpoint in `notifications.py` to use Redis caching and implement pagination (limit/offset)

## 3. Implement WebSocket Ping/Pong
- [ ] Update `websocket_manager.py` to properly handle ping/pong messages for connection reliability

## 4. Configure Production CORS
- [ ] Update CORS middleware in `main.py` to allow production origins

## 5. Write Comprehensive Tests
- [ ] Create `backend/tests/test_notifications_caching.py` for caching and pagination tests
- [ ] Expand `backend/tests/test_websocket_reliability.py` for ping/pong functionality
- [ ] Add CORS tests

## 6. Update Integration TODO
- [ ] Mark backend optimizations as complete in `TODO_integration.md`

## 7. Testing & Verification
- [ ] Run pytest tests to verify functionality
- [ ] Test Redis caching behavior (cache hit/miss)
- [ ] Verify WebSocket ping/pong reliability
- [ ] Confirm CORS allows production origins
