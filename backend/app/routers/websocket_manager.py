import structlog
from fastapi import WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
import time
from ..db import get_db
from ..deps import get_current_user
from ..services.redis_service import redis_service
from ..services.chat_service import chat_service
from ..services.meeting_service import meeting_service
from ..models.user import User
from ..crud.crud_channels import is_user_member_of_channel
from ..crud.crud_meetings import is_user_participant
from ..models.company import Company
from ..metrics import increment_ws_connections, decrement_ws_connections, record_ws_message, record_ws_error, record_ws_latency

logger = structlog.get_logger(__name__)

security = HTTPBearer()

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, Dict[int, WebSocket]] = {}  # room_type:room_id -> user_id -> websocket

    async def connect(self, websocket: WebSocket, room_type: str, room_id: int, user: User, db: Session):
        """Handle WebSocket connection with authentication"""
        start_time = time.time()
        await websocket.accept()
        connection_time = time.time() - start_time
        record_ws_latency(connection_time)

        increment_ws_connections()

        connection_key = f"{room_type}:{room_id}"
        if connection_key not in self.active_connections:
            self.active_connections[connection_key] = {}

        self.active_connections[connection_key][user.id] = websocket

        # Set presence
        company_id = user.company_id
        await redis_service.set_user_online(company_id, user.id)

        # Validate access
        if room_type == "chat":
            if not is_user_member_of_channel(db, room_id, user.id):
                record_ws_error("unauthorized_channel")
                await websocket.close(code=4003, reason="Not authorized for this channel")
                decrement_ws_connections()
                return
            logger.info("User connected to chat WebSocket", user_id=user.id, channel_id=room_id, company_id=company_id)
        elif room_type == "meeting":
            if not is_user_participant(db, room_id, user.id):
                record_ws_error("unauthorized_meeting")
                await websocket.close(code=4003, reason="Not authorized for this meeting")
                decrement_ws_connections()
                return
            logger.info("User connected to meeting WebSocket", user_id=user.id, meeting_id=room_id, company_id=company_id)

        try:
            while True:
                msg_start = time.time()
                data = await websocket.receive_json()
                msg_time = time.time() - msg_start
                record_ws_latency(msg_time)
                record_ws_message(data.get("type", "unknown"))
                await self.handle_message(websocket, data, room_type, room_id, user, db)
        except WebSocketDisconnect:
            await self.disconnect(websocket, room_type, room_id, user.id, user.company_id)
            logger.info("User disconnected from WebSocket", user_id=user.id, room_type=room_type, room_id=room_id)
        except Exception as e:
            record_ws_error("internal_error")
            logger.error("WebSocket error", error=str(e), user_id=user.id)
            await websocket.close(code=1011, reason="Internal error")
        finally:
            decrement_ws_connections()

    async def disconnect(self, websocket: WebSocket, room_type: str, room_id: int, user_id: int, company_id: int):
        """Handle disconnection"""
        connection_key = f"{room_type}:{room_id}"
        if connection_key in self.active_connections and user_id in self.active_connections[connection_key]:
            del self.active_connections[connection_key][user_id]
            if not self.active_connections[connection_key]:
                del self.active_connections[connection_key]

        # Set offline and publish event
        await redis_service.set_user_offline(company_id, user_id)
        await redis_service.publish_event(f"{room_type}:{room_id}", {
            "type": "user_disconnected",
            "user_id": user_id,
            f"{room_type}_id": room_id
        })

    async def handle_message(self, websocket: WebSocket, data: dict, room_type: str, room_id: int, user: User, db: Session):
        """Handle incoming WebSocket messages"""
        msg_type = data.get("type")

        if room_type == "chat":
            if msg_type == "typing":
                await chat_service.set_typing_indicator(room_id, user.id, data.get("is_typing", False))
                await self.broadcast(websocket, {"type": "typing", "user_id": user.id, "channel_id": room_id, "is_typing": data.get("is_typing", False)}, room_type, room_id, user.id)
            elif msg_type == "read_receipt":
                chat_service.mark_channel_messages_read(db, room_id, user.id)
                await self.broadcast(websocket, {"type": "read_receipt", "user_id": user.id, "channel_id": room_id}, room_type, room_id, user.id)
            elif msg_type == "reaction":
                # Handle reaction add/remove via service
                reaction_data = data.get("reaction")
                if reaction_data.get("action") == "add":
                    from ..crud.crud_reactions import add_reaction
                    db_reaction = add_reaction(db, reaction_data["message_id"], user.id, reaction_data["emoji"])
                    await self.broadcast(websocket, {"type": "reaction_added", "reaction": {"id": db_reaction.id, "message_id": reaction_data["message_id"], "user_id": user.id, "emoji": reaction_data["emoji"]}}, room_type, room_id, user.id)
                elif reaction_data.get("action") == "remove":
                    from ..crud.crud_reactions import remove_reaction
                    success = remove_reaction(db, reaction_data["message_id"], user.id, reaction_data["emoji"])
                    if success:
                        await self.broadcast(websocket, {"type": "reaction_removed", "reaction": {"message_id": reaction_data["message_id"], "user_id": user.id, "emoji": reaction_data["emoji"]}}, room_type, room_id, user.id)
            else:
                logger.warning("Unknown chat message type", type=msg_type, user_id=user.id, company_id=user.company_id)

        elif room_type == "meeting":
            if msg_type in ["offer", "answer", "ice-candidate"]:
                await self.broadcast(websocket, {"type": msg_type, "from": user.id, "data": data.get("data")}, room_type, room_id, user.id)
            elif msg_type == "presence":
                online_users = await meeting_service.get_online_participants(room_id, user.company_id)
                await self.broadcast(websocket, {"type": "presence_update", "online_users": online_users}, room_type, room_id, user.id)
            elif msg_type == "join_meeting":
                await meeting_service.join_meeting(db, room_id, user.id)
                await self.broadcast(websocket, {"type": "user_joined", "user_id": user.id, "meeting_id": room_id}, room_type, room_id, user.id)
            elif msg_type == "leave_meeting":
                await meeting_service.leave_meeting(db, room_id, user.id)
                await self.broadcast(websocket, {"type": "user_left", "user_id": user.id, "meeting_id": room_id}, room_type, room_id, user.id)
            else:
                logger.warning("Unknown meeting message type", type=msg_type, user_id=user.id, company_id=user.company_id)

    async def broadcast(self, sender_websocket: WebSocket, message: dict, room_type: str, room_id: int, sender_id: int):
        """Broadcast message to room excluding sender via Redis pub/sub"""
        # Publish to Redis pub/sub for scalability
        await redis_service.publish_event(f"{room_type}:{room_id}", message)

        # Also broadcast to active connections (fallback for immediate delivery)
        connection_key = f"{room_type}:{room_id}"
        if connection_key in self.active_connections:
            for user_id, websocket in self.active_connections[connection_key].items():
                if user_id != sender_id:
                    try:
                        await websocket.send_json(message)
                    except Exception as e:
                        logger.error("Broadcast failed", error=str(e), user_id=user_id)

# Global manager instance
ws_manager = WebSocketManager()

# Dependency for authenticated WebSocket
async def get_websocket_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """Extract user from JWT token for WebSocket"""
    try:
        # Assuming JWT validation similar to get_current_user
        # In practice, decode token here
        token = credentials.credentials
        # user = decode_jwt_token(token)  # Implement JWT decode
        # return get_current_user(db, user_id=user.id)  # Mock for now
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

from fastapi import APIRouter

router = APIRouter()

# Chat WebSocket route
@router.websocket("/chat/{channel_id}")
async def chat_websocket(websocket: WebSocket, channel_id: int, user=Depends(get_websocket_user), db: Session = Depends(get_db)):
    await ws_manager.connect(websocket, "chat", channel_id, user, db)

# Meeting WebSocket route
@router.websocket("/meetings/{meeting_id}")
async def meeting_websocket(websocket: WebSocket, meeting_id: int, user=Depends(get_websocket_user), db: Session = Depends(get_db)):
    await ws_manager.connect(websocket, "meeting", meeting_id, user, db)
