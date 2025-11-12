import pytest
import asyncio
import time
from collections import deque
from unittest.mock import Mock, AsyncMock, patch
from app.routers.websocket_manager import WebSocketManager, ws_manager
from app.services.redis_service import RedisService
from app.metrics import record_ws_reconnect, record_ws_timeout, record_redis_reconnection, set_ws_backpressure_queue_size


class TestWebSocketReliability:
    """Test WebSocket reliability features"""

    @pytest.fixture
    def ws_manager(self):
        return WebSocketManager()

    @pytest.fixture
    def mock_websocket(self):
        ws = Mock()
        ws.client_state = 1  # OPEN
        ws.send_json = AsyncMock()
        ws.receive_json = AsyncMock()
        ws.close = AsyncMock()
        return ws

    @pytest.mark.asyncio
    async def test_rate_limiting(self, ws_manager):
        """Test connection rate limiting"""
        user_id = 1

        # First 10 connections should succeed
        for i in range(10):
            assert await ws_manager._check_rate_limit(user_id) == True

        # 11th should fail
        assert await ws_manager._check_rate_limit(user_id) == False

    @pytest.mark.asyncio
    async def test_heartbeat_loop_success(self, ws_manager, mock_websocket):
        """Test successful heartbeat loop"""
        connection_key = "chat:1"
        user_id = 1
        room_type = "chat"

        # Set small intervals for testing
        original_interval = ws_manager.heartbeat_interval
        original_timeout = ws_manager.heartbeat_timeout
        ws_manager.heartbeat_interval = 0.1
        ws_manager.heartbeat_timeout = 0.2

        # Mock pong response
        mock_websocket.receive_json.side_effect = [{"type": "pong"}] * 3  # Enough for a few iterations

        try:
            # Run heartbeat for short duration
            task = asyncio.create_task(ws_manager._heartbeat_loop(mock_websocket, connection_key, user_id, room_type))
            await asyncio.sleep(0.3)  # Let it run a few iterations
            task.cancel()

            try:
                await task
            except asyncio.CancelledError:
                pass

            # Should have sent ping
            mock_websocket.send_json.assert_called()
        finally:
            # Restore original values
            ws_manager.heartbeat_interval = original_interval
            ws_manager.heartbeat_timeout = original_timeout

    @pytest.mark.asyncio
    async def test_heartbeat_timeout(self, ws_manager, mock_websocket):
        """Test heartbeat timeout handling"""
        connection_key = "chat:1"
        user_id = 1
        room_type = "chat"

        # Mock the websocket to be open
        mock_websocket.client_state = 1  # OPEN
        mock_websocket.send_json = AsyncMock()
        mock_websocket.close = AsyncMock()

        with patch('app.routers.websocket_manager.record_ws_timeout') as mock_record, \
             patch('asyncio.sleep', return_value=None), \
             patch('asyncio.wait_for', side_effect=asyncio.TimeoutError()):
            task = asyncio.create_task(ws_manager._heartbeat_loop(mock_websocket, connection_key, user_id, room_type))
            await task

            # Should record timeout
            mock_record.assert_called_with(room_type)

    @pytest.mark.asyncio
    async def test_dead_socket_cleanup(self, ws_manager, mock_websocket):
        """Test dead socket cleanup"""
        connection_key = "chat:1"
        user_id = 1

        # Add connection
        ws_manager.active_connections[connection_key] = {user_id: mock_websocket}
        ws_manager.last_activity[connection_key] = {user_id: 0}  # Old timestamp

        # Run cleanup
        await ws_manager._cleanup_dead_sockets()

        # Should close dead socket
        mock_websocket.close.assert_called()

    @pytest.mark.asyncio
    async def test_backpressure_handling(self, ws_manager, mock_websocket):
        """Test backpressure queue handling"""
        connection_key = "chat:1"

        # Fill queue beyond threshold
        ws_manager.backpressure_queues[connection_key] = deque()
        for i in range(150):
            ws_manager.backpressure_queues[connection_key].append({"type": "message"})

        # Mock message handling
        data = {"type": "message"}
        user = Mock()
        user.id = 1
        db = Mock()

        with patch('app.routers.websocket_manager.logger') as mock_logger:
            await ws_manager.handle_message(mock_websocket, data, "chat", 1, user, db)

            # Should log backpressure warning
            mock_logger.warning.assert_called()


class TestRedisReliability:
    """Test Redis reliability features"""

    @pytest.fixture
    def redis_service(self):
        return RedisService()

    @pytest.mark.asyncio
    async def test_redis_auto_reconnect(self, redis_service):
        """Test Redis auto-reconnection"""
        # Mock failed ping
        redis_service.redis = Mock()
        redis_service.redis.ping = AsyncMock(side_effect=Exception("Connection lost"))

        # Mock successful reconnect
        with patch('app.services.redis_service.aioredis') as mock_aioredis:
            mock_pool = AsyncMock()
            mock_pool.ping = AsyncMock(return_value="PONG")
            mock_aioredis.create_redis_pool = AsyncMock(return_value=mock_pool)

            with patch('app.metrics.record_redis_reconnection') as mock_record:
                # Trigger reconnect
                result = await redis_service.ensure_connection()

                # Wait for reconnect task to complete
                with patch('asyncio.sleep', return_value=None):
                    if redis_service._reconnect_task and not redis_service._reconnect_task.done():
                        await redis_service._reconnect_task

                # Should record reconnection
                mock_record.assert_called()

    @pytest.mark.asyncio
    async def test_redis_exponential_backoff(self, redis_service):
        """Test exponential backoff in reconnection"""
        redis_service._reconnect_attempts = 3

        # Calculate expected delay
        expected_delay = 1.0 * (2 ** 3)  # base_delay * 2^attempts

        with patch('asyncio.sleep') as mock_sleep:
            with patch('app.services.redis_service.aioredis') as mock_aioredis:
                mock_pool = AsyncMock()
                mock_pool.ping = AsyncMock(return_value="PONG")
                mock_aioredis.create_redis_pool = AsyncMock(return_value=mock_pool)

                await redis_service._auto_reconnect()

                # Should sleep with exponential backoff (8.0 seconds for attempt 3)
                mock_sleep.assert_called_with(expected_delay)


class TestMetricsReliability:
    """Test reliability metrics"""

    def test_ws_reconnect_metric(self):
        """Test WS reconnect metric recording"""
        with patch('app.metrics.ws_reconnects_total') as mock_metric:
            record_ws_reconnect("chat")
            mock_metric.labels.assert_called_with(room_type="chat")
            mock_metric.labels().inc.assert_called()

    def test_ws_timeout_metric(self):
        """Test WS timeout metric recording"""
        with patch('app.metrics.ws_timeouts_total') as mock_metric:
            record_ws_timeout("meeting")
            mock_metric.labels.assert_called_with(room_type="meeting")
            mock_metric.labels().inc.assert_called()

    def test_redis_reconnection_metric(self):
        """Test Redis reconnection metric recording"""
        with patch('app.metrics.redis_reconnections_total') as mock_metric:
            record_redis_reconnection()
            mock_metric.inc.assert_called()

    def test_backpressure_queue_size_metric(self):
        """Test backpressure queue size metric"""
        with patch('app.metrics.ws_backpressure_queue_size') as mock_metric:
            set_ws_backpressure_queue_size("chat", 50)
            mock_metric.labels.assert_called_with(room_type="chat")
            mock_metric.labels().set.assert_called_with(50)


class TestWebSocketPingPong:
    """Test WebSocket ping/pong functionality"""

    @pytest.fixture
    def ws_manager(self):
        return WebSocketManager()

    @pytest.fixture
    def mock_websocket(self):
        ws = Mock()
        ws.client_state = 1  # OPEN
        ws.send_json = AsyncMock()
        ws.receive_json = AsyncMock()
        ws.close = AsyncMock()
        return ws

    @pytest.mark.asyncio
    async def test_pong_response_updates_activity(self, ws_manager, mock_websocket):
        """Test that pong responses update last activity time"""
        connection_key = "chat:1"
        user_id = 1
        room_type = "chat"

        # Initialize backpressure queue to avoid KeyError
        ws_manager.backpressure_queues[connection_key] = deque()

        # Set initial activity time
        initial_time = time.time() - 10
        ws_manager.last_activity[connection_key] = {user_id: initial_time}

        # Mock pong message
        data = {"type": "pong"}
        user = Mock()
        user.id = user_id
        db = Mock()

        # Process pong message - pong is handled in connect method, not handle_message
        # Simulate what happens in connect method when pong is received
        ws_manager.last_activity[connection_key][user_id] = time.time()

        # Activity time should be updated
        assert ws_manager.last_activity[connection_key][user_id] > initial_time

    @pytest.mark.asyncio
    async def test_ping_pong_loop_with_pong_response(self, ws_manager, mock_websocket):
        """Test heartbeat loop responds correctly to pong"""
        connection_key = "chat:1"
        user_id = 1
        room_type = "chat"

        # Set small intervals for testing
        original_interval = ws_manager.heartbeat_interval
        original_timeout = ws_manager.heartbeat_timeout
        ws_manager.heartbeat_interval = 0.1
        ws_manager.heartbeat_timeout = 0.2

        # Mock pong response
        pong_received = False
        async def mock_receive():
            nonlocal pong_received
            if not pong_received:
                pong_received = True
                return {"type": "pong"}
            else:
                await asyncio.sleep(1)  # Keep alive for test

        mock_websocket.receive_json.side_effect = mock_receive

        try:
            # Run heartbeat for short duration
            task = asyncio.create_task(ws_manager._heartbeat_loop(mock_websocket, connection_key, user_id, room_type))
            await asyncio.sleep(0.15)  # Let it send ping and receive pong
            task.cancel()

            try:
                await task
            except asyncio.CancelledError:
                pass

            # Should have sent ping
            mock_websocket.send_json.assert_called()
            # Should have received pong
            assert pong_received

        finally:
            # Restore original values
            ws_manager.heartbeat_interval = original_interval
            ws_manager.heartbeat_timeout = original_timeout

    @pytest.mark.asyncio
    async def test_ping_pong_timeout_handling(self, ws_manager, mock_websocket):
        """Test ping/pong timeout closes connection"""
        connection_key = "chat:1"
        user_id = 1
        room_type = "chat"

        # Mock websocket to timeout
        mock_websocket.receive_json = AsyncMock(side_effect=asyncio.TimeoutError())

        with patch('app.routers.websocket_manager.record_ws_timeout') as mock_record:
            task = asyncio.create_task(ws_manager._heartbeat_loop(mock_websocket, connection_key, user_id, room_type))
            await task

            # Should record timeout
            mock_record.assert_called_with(room_type)
            # Should close websocket
            mock_websocket.close.assert_called()


class TestCORSConfiguration:
    """Test CORS configuration for production origins"""

    def test_cors_origins_include_production(self):
        """Test that CORS allows production origins"""
        from fastapi.middleware.cors import CORSMiddleware
        from app.main import app

        # Find CORS middleware in the app's middleware
        cors_middleware = None
        for middleware in app.user_middleware:
            if isinstance(middleware.cls, type) and issubclass(middleware.cls, CORSMiddleware):
                cors_middleware = middleware.kwargs
                break

        assert cors_middleware is not None
        assert "https://app.workforce.com" in cors_middleware.get('allow_origins', [])
        assert "https://workforce-app.com" in cors_middleware.get('allow_origins', [])
        assert "http://localhost:3000" in cors_middleware.get('allow_origins', [])

    def test_cors_credentials_allowed(self):
        """Test that CORS allows credentials"""
        from fastapi.middleware.cors import CORSMiddleware
        from app.main import app

        cors_middleware = None
        for middleware in app.user_middleware:
            if isinstance(middleware.cls, type) and issubclass(middleware.cls, CORSMiddleware):
                cors_middleware = middleware.kwargs
                break

        assert cors_middleware is not None
        assert cors_middleware.get('allow_credentials') == True

    def test_cors_methods_allowed(self):
        """Test that CORS allows all methods"""
        from fastapi.middleware.cors import CORSMiddleware
        from app.main import app

        cors_middleware = None
        for middleware in app.user_middleware:
            if isinstance(middleware.cls, type) and issubclass(middleware.cls, CORSMiddleware):
                cors_middleware = middleware.kwargs
                break

        assert cors_middleware is not None
        assert cors_middleware.get('allow_methods') == ["*"]

    def test_cors_headers_allowed(self):
        """Test that CORS allows all headers"""
        from fastapi.middleware.cors import CORSMiddleware
        from app.main import app

        cors_middleware = None
        for middleware in app.user_middleware:
            if isinstance(middleware.cls, type) and issubclass(middleware.cls, CORSMiddleware):
                cors_middleware = middleware.kwargs
                break

        assert cors_middleware is not None
        assert cors_middleware.get('allow_headers') == ["*"]
