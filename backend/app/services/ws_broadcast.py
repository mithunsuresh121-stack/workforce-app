import json
from typing import Dict, Set

import structlog
from fastapi import WebSocket

logger = structlog.get_logger(__name__)


class WSManager:
    def __init__(self):
        self.active_connections: Dict[int, Set[WebSocket]] = (
            {}
        )  # channel_id -> set(WebSocket)
        self.user_connections: Dict[int, WebSocket] = {}  # user_id -> WebSocket

    async def connect(self, channel_id: int, user_id: int, websocket: WebSocket):
        """Connect a user to a channel"""
        if channel_id not in self.active_connections:
            self.active_connections[channel_id] = set()
        self.active_connections[channel_id].add(websocket)
        self.user_connections[user_id] = websocket
        logger.info("User connected to channel", user_id=user_id, channel_id=channel_id)

    async def disconnect(self, channel_id: int, user_id: int, websocket: WebSocket):
        """Disconnect a user from a channel"""
        if channel_id in self.active_connections:
            self.active_connections[channel_id].discard(websocket)
            if not self.active_connections[channel_id]:
                del self.active_connections[channel_id]
        if user_id in self.user_connections:
            del self.user_connections[user_id]
        logger.info(
            "User disconnected from channel", user_id=user_id, channel_id=channel_id
        )

    async def broadcast(self, channel_id: int, message_json: str):
        """Broadcast message to all connections in a channel"""
        if channel_id in self.active_connections:
            for websocket in self.active_connections[channel_id]:
                try:
                    await websocket.send_text(message_json)
                except Exception as e:
                    logger.error("Failed to send message to websocket", error=str(e))
        logger.info(
            "Broadcasted message to channel",
            channel_id=channel_id,
            message_size=len(message_json),
        )

    async def send_to_user(self, user_id: int, message_json: str):
        """Send message to a specific user"""
        if user_id in self.user_connections:
            try:
                await self.user_connections[user_id].send_text(message_json)
            except Exception as e:
                logger.error(
                    "Failed to send message to user", user_id=user_id, error=str(e)
                )


# Global instance
ws_manager = WSManager()
