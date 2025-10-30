import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from backend.app.routers.websocket_manager import WebSocketManager, ws_manager
from backend.app.services.redis_service import RedisService
from backend.app.metrics import record_ws_reconnect, record_ws_timeout, record_redis_reconnection, set_ws_backpressure_queue_size


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

        # Mock pong response
        mock_websocket.receive_json.side_effect = [{"type": "pong"}]

        # Run heartbeat for short duration
        task = asyncio.create_task(ws_manager._heartbeat_loop(mock_websocket, connection_key, user_id, room_type))
        await asyncio.sleep(0.1)  # Let it run briefly
        task.cancel()

        try:
            await task
        except asyncio.CancelledError:
            pass

        # Should have sent ping
        mock_websocket.send_json.assert_called()

    @pytest.mark.asyncio
    async def test_heartbeat_timeout(self, ws_manager, mock_websocket):
        """Test heartbeat timeout handling"""
        connection_key = "chat:1"
        user_id = 1
        room_type = "chat"

        # Mock timeout
        mock_websocket.receive_json.side_effect = asyncio.TimeoutError()

        with patch('backend.app.routers.websocket_manager.record_ws_timeout') as mock_record:
            task = asyncio.create_task(ws_manager._heartbeat_loop(mock_websocket, connection_key, user_id, room_type))
            await asyncio.sleep(0.1)
            task.cancel()

            try:
                await task
            except asyncio.CancelledError:
                pass

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
    async def test_backpressure_handling(self, ws_manager):
        """Test backpressure queue handling"""
        connection_key = "chat:1"

        # Fill queue beyond threshold
        ws_manager.backpressure_queues[connection_key] = asyncio.Queue(maxsize=200)
        for i in range(150):
            await ws_manager.backpressure_queues[connection_key].put({"type": "message"})

        # Mock message handling
        data = {"type": "message"}
        user = Mock()
        user.id = 1
        db = Mock()

        with patch('backend.app.routers.websocket_manager.logger') as mock_logger:
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
        with patch('backend.app.services.redis_service.aioredis') as mock_aioredis:
            mock_pool = AsyncMock()
            mock_pool.ping.return_value = "PONG"
            mock_aioredis.create_redis_pool.return_value = mock_pool

            with patch('backend.app.services.redis_service.record_redis_reconnection') as mock_record:
                # Trigger reconnect
                result = await redis_service.ensure_connection()

                # Should attempt reconnect
                assert redis_service._reconnect_attempts > 0
                # Should record reconnection
                mock_record.assert_called()

    @pytest.mark.asyncio
    async def test_redis_exponential_backoff(self, redis_service):
        """Test exponential backoff in reconnection"""
        redis_service._reconnect_attempts = 3

        # Calculate expected delay
        expected_delay = 1.0 * (2 ** 3)  # base_delay * 2^attempts

        with patch('asyncio.sleep') as mock_sleep:
            with patch('backend.app.services.redis_service.aioredis') as mock_aioredis:
                mock_pool = AsyncMock()
                mock_pool.ping.return_value = "PONG"
                mock_aioredis.create_redis_pool.return_value = mock_pool

                await redis_service._auto_reconnect()

                # Should sleep with exponential backoff
                mock_sleep.assert_called_with(expected_delay)


class TestMetricsReliability:
    """Test reliability metrics"""

    def test_ws_reconnect_metric(self):
        """Test WS reconnect metric recording"""
        with patch('backend.app.metrics.ws_reconnects_total') as mock_metric:
            record_ws_reconnect("chat")
            mock_metric.labels.assert_called_with(room_type="chat")
            mock_metric.labels().inc.assert_called()

    def test_ws_timeout_metric(self):
        """Test WS timeout metric recording"""
        with patch('backend.app.metrics.ws_timeouts_total') as mock_metric:
            record_ws_timeout("meeting")
            mock_metric.labels.assert_called_with(room_type="meeting")
            mock_metric.labels().inc.assert_called()

    def test_redis_reconnection_metric(self):
        """Test Redis reconnection metric recording"""
        with patch('backend.app.metrics.redis_reconnections_total') as mock_metric:
            record_redis_reconnection()
            mock_metric.inc.assert_called()

    def test_backpressure_queue_size_metric(self):
        """Test backpressure queue size metric"""
        with patch('backend.app.metrics.ws_backpressure_queue_size') as mock_metric:
            set_ws_backpressure_queue_size("chat", 50)
            mock_metric.labels.assert_called_with(room_type="chat")
            mock_metric.labels().set.assert_called_with(50)
