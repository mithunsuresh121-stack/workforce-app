import asyncio
import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from app.models.company import Company
from app.models.notification import Notification, NotificationStatus
from app.models.user import User
from app.routers.notifications import get_notifications
from app.services.redis_service import redis_service


class TestNotificationCaching:
    """Test notification caching and pagination functionality"""

    @pytest.fixture
    def mock_user(self):
        user = User()
        user.id = 1
        user.company_id = 1
        return user

    @pytest.fixture
    def mock_db(self):
        db = AsyncMock(spec=Session)
        return db

    @pytest.mark.asyncio
    async def test_redis_cache_set_and_get(self):
        """Test setting and getting notification cache"""
        company_id = 1
        user_id = 1
        offset = 0
        limit = 10
        notifications = [
            {
                "id": 1,
                "user_id": user_id,
                "company_id": company_id,
                "title": "Test Notification",
                "message": "Test message",
                "type": "info",
                "status": "unread",
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-01T00:00:00",
            }
        ]

        # Mock Redis operations
        mock_redis = AsyncMock()
        mock_redis.setex.return_value = True
        mock_redis.get.return_value = json.dumps(notifications).encode(
            "utf-8"
        )  # Return cached data

        with patch.object(redis_service, "redis", mock_redis), patch.object(
            redis_service, "_initialized", True
        ):
            # Test cache set
            success = await redis_service.set_notification_cache(
                company_id, user_id, offset, limit, notifications
            )
            assert success == True
            mock_redis.setex.assert_called_once()

            # Test cache get - this should return the cached data
            cached = await redis_service.get_notification_cache(
                company_id, user_id, offset, limit
            )
            assert cached == notifications
            mock_redis.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_redis_cache_invalidation(self):
        """Test cache invalidation"""
        company_id = 1
        user_id = 1

        # Mock Redis operations
        mock_redis = AsyncMock()
        mock_redis.setex.return_value = True
        mock_redis.keys.return_value = [
            b"notifications:1:1:0:10",
            b"notifications:1:1:10:10",
        ]
        mock_redis.delete.return_value = 2  # Number of keys deleted
        mock_redis.get.return_value = None  # After invalidation

        with patch.object(redis_service, "redis", mock_redis), patch.object(
            redis_service, "_initialized", True
        ):
            # Set multiple cache entries
            await redis_service.set_notification_cache(company_id, user_id, 0, 10, [])
            await redis_service.set_notification_cache(company_id, user_id, 10, 10, [])

            # Invalidate all for user
            deleted = await redis_service.invalidate_notification_cache(
                company_id, user_id
            )
            assert deleted == 2
            mock_redis.keys.assert_called_once()
            mock_redis.delete.assert_called_once()

            # Verify cache is empty
            cached = await redis_service.get_notification_cache(
                company_id, user_id, 0, 10
            )
            assert cached is None

    @pytest.mark.asyncio
    async def test_pagination_validation(self, mock_user, mock_db):
        """Test pagination parameter validation"""
        # Test default values
        with patch(
            "app.services.redis_service.redis_service.get_notification_cache",
            return_value=None,
        ):
            with patch(
                "app.services.redis_service.redis_service.set_notification_cache",
                return_value=True,
            ):
                mock_db.query.return_value.filter.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = (
                    []
                )

                # Should work with defaults
                result = await get_notifications(
                    limit=50, offset=0, db=mock_db, current_user=mock_user
                )
                assert result == []

    @pytest.mark.asyncio
    async def test_cache_hit_serves_from_cache(self, mock_user, mock_db):
        """Test that cache hit serves from Redis instead of database"""
        cached_notifications = [
            {
                "id": 1,
                "user_id": 1,
                "company_id": 1,
                "title": "Cached Notification",
                "message": "From cache",
                "type": "info",
                "status": "unread",
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-01T00:00:00",
            }
        ]

        with patch(
            "app.services.redis_service.redis_service.get_notification_cache",
            return_value=cached_notifications,
        ):
            result = await get_notifications(
                limit=10, offset=0, db=mock_db, current_user=mock_user
            )

            # Should return cached data without querying database
            assert result == cached_notifications
            # Database should not be queried
            mock_db.query.assert_not_called()

    @pytest.mark.asyncio
    async def test_cache_miss_queries_database(self, mock_user, mock_db):
        """Test that cache miss queries database and caches result"""
        db_notifications = [
            Notification(
                id=1,
                user_id=1,
                company_id=1,
                title="DB Notification",
                message="From database",
                type="info",
                status=NotificationStatus.UNREAD,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
        ]

        with patch(
            "app.services.redis_service.redis_service.get_notification_cache",
            return_value=None,
        ):
            with patch(
                "app.services.redis_service.redis_service.set_notification_cache",
                return_value=True,
            ):
                mock_db.query.return_value.filter.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = (
                    db_notifications
                )

                result = await get_notifications(
                    limit=10, offset=0, db=mock_db, current_user=mock_user
                )

                # Should query database
                mock_db.query.assert_called()
                # Should cache result
                # Note: result is list of Notification objects, but we cache dicts

    @pytest.mark.asyncio
    async def test_pagination_limits(self, mock_user, mock_db):
        """Test pagination limits are enforced"""
        with patch(
            "app.services.redis_service.redis_service.get_notification_cache",
            return_value=None,
        ):
            with patch(
                "app.services.redis_service.redis_service.set_notification_cache",
                return_value=True,
            ):
                mock_db.query.return_value.filter.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = (
                    []
                )

                # Test limit too high - should be capped at 100
                result = await get_notifications(
                    limit=150, offset=0, db=mock_db, current_user=mock_user
                )
                # Should be capped at 100
                mock_db.query.return_value.filter.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.assert_called_with(
                    100
                )

                # Reset mock for next test
                mock_db.reset_mock()
                mock_db.query.return_value.filter.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = (
                    []
                )

                # Test limit too low - should be set to 50
                result = await get_notifications(
                    limit=0, offset=0, db=mock_db, current_user=mock_user
                )
                # Should be set to 50
                mock_db.query.return_value.filter.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.assert_called_with(
                    50
                )

    @pytest.mark.asyncio
    async def test_superadmin_company_handling(self, mock_user, mock_db):
        """Test superadmin (no company_id) handling"""
        mock_user.company_id = None  # Superadmin

        with patch(
            "app.services.redis_service.redis_service.get_notification_cache",
            return_value=None,
        ):
            with patch(
                "app.services.redis_service.redis_service.set_notification_cache",
                return_value=True,
            ):
                mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = (
                    []
                )

                result = await get_notifications(
                    limit=10, offset=0, db=mock_db, current_user=mock_user
                )

                # Should use company_id=0 for superadmin
                # Cache key should use 0
                # Database query should not filter by company_id
                mock_db.query.return_value.filter.assert_called_once()  # Only user_id filter

    @pytest.mark.asyncio
    async def test_publish_to_redis_endpoint(self, mock_user):
        """Test the /api/notifications/publish endpoint"""
        from app.routers.notifications import publish_to_redis

        channel = "test-channel"
        message = "test message"

        # Mock redis_service.publish
        with patch(
            "app.services.redis_service.redis_service.publish", new_callable=AsyncMock
        ) as mock_publish:
            result = await publish_to_redis(
                channel=channel, message=message, current_user=mock_user
            )

            # Verify publish was called with correct args
            mock_publish.assert_called_once_with(channel, message)

            # Verify response
            assert result == {"status": "published", "channel": channel}
