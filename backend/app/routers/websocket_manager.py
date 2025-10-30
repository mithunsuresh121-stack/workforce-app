import structlog
from fastapi import WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
import time
import asyncio
from collections import defaultdict, deque
from app.db import get_db
from app.deps import get_current_user
from app.services.redis_service import redis_service
from app.services.chat_service import chat_service
from app.services.meeting_service import meeting_service
from app.models.user import User
from app.crud.crud_channels import is_user_member_of_channel
from app.crud.crud_meetings import is_user_participant
from app.models.company import Company
from app.metrics import increment_ws_connections, decrement_ws_connections, record_ws_message, record_ws_error, record_ws_latency, record_ws_reconnect, record_ws_timeout, set_ws_backpressure_queue_size

logger = structlog.get_logger(__name__)

security = HTTPBearer()

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, Dict[int, WebSocket]] = {}  # room_type:room_id -> user_id -> websocket
        self.last_activity: Dict[str, Dict[int, float]] = {}  # connection_key -> user_id -> timestamp
        self.heartbeat_interval = 30  # seconds
        self.heartbeat_timeout = 60  # seconds
        self.rate_limit_window = 60  # seconds
        self.rate_limit_max = 10  # connections per window
        self.connection_attempts: Dict[int, List[float]] = {}  # user_id -> list of timestamps
        self.recently_disconnected: Dict[str, set] = {}  # connection_key -> set of user_ids
        self.heartbeat_tasks: Dict[str, asyncio.Task] = {}  # user_key -> task
        self.backpressure_queues: Dict[str, deque] = {}  # connection_key -> queue of pending messages
        self.cleanup_task = asyncio.create_task(self._periodic_cleanup())

    async def _periodic_cleanup(self):
        """Periodic cleanup of stale data and dead sockets"""
        while True:
            await asyncio.sleep(60)  # Every minute
            await self._cleanup_dead_sockets()
            await self._cleanup_rate_limits()

    async def _cleanup_dead_sockets(self):
        """Cleanup dead sockets based on last activity"""
        now = time.time()
        for connection_key, user_sockets in list(self.active_connections.items()):
            room_type = connection_key.split(':')[0]
            for user_id, websocket in list(user_sockets.items()):
                if connection_key not in self.last_activity:
                    self.last_activity[connection_key] = {}
                last_act = self.last_activity[connection_key].get(user_id, 0)
                if now - last_act > self.heartbeat_timeout * 2:  # Twice the timeout
                    try:
                        await websocket.close(code=1006, reason="Inactive connection")
                        logger.warning("Closed dead socket", user_id=user_id, room_type=room_type)
                        record_ws_timeout(room_type)
                    except:
                        pass
                    del user_sockets[user_id]
                    if not user_sockets:
                        del self.active_connections[connection_key]

    async def _cleanup_rate_limits(self):
        """Cleanup old connection attempts"""
        now = time.time()
        for user_id, attempts in list(self.connection_attempts.items()):
            recent = [t for t in attempts if now - t < self.rate_limit_window]
            self.connection_attempts[user_id] = recent
            if not recent:
                del self.connection_attempts[user_id]

    async def connect(self, websocket: WebSocket, room_type: str, room_id: int, user: User, db: Session):
        """Handle WebSocket connection with authentication and reliability features"""
        # Rate limiting check
        if not await self._check_rate_limit(user.id):
            record_ws_error("rate_limited")
            await websocket.close(code=4009, reason="Too many connection attempts")
            return

        start_time = time.time()
        await websocket.accept()
        connection_time = time.time() - start_time
        record_ws_latency(connection_time)

        increment_ws_connections()

        connection_key = f"{room_type}:{room_id}"
        user_key = f"{connection_key}:{user.id}"

        # Initialize data structures
        if connection_key not in self.active_connections:
            self.active_connections[connection_key] = {}
        if connection_key not in self.last_activity:
            self.last_activity[connection_key] = {}
        if connection_key not in self.backpressure_queues:
            self.backpressure_queues[connection_key] = deque()

        self.active_connections[connection_key][user.id] = websocket
        self.last_activity[connection_key][user.id] = time.time()

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

        # Start heartbeat task
        self.heartbeat_tasks[user_key] = asyncio.create_task(self._heartbeat_loop(websocket, connection_key, user.id, room_type))

        try:
            while True:
                msg_start = time.time()
                data = await websocket.receive_json()
                msg_time = time.time() - msg_start
                record_ws_latency(msg_time)
                record_ws_message(data.get("type", "unknown"))

                # Update last activity
                self.last_activity[connection_key][user.id] = time.time()

                # Handle pong responses
                if data.get("type") == "pong":
                    continue  # Heartbeat response, no further processing

                await self.handle_message(websocket, data, room_type, room_id, user, db)
        except WebSocketDisconnect:
            await self.disconnect(websocket, room_type, room_id, user.id, user.company_id)
            logger.info("User disconnected from WebSocket", user_id=user.id, room_type=room_type, room_id=room_id)
        except asyncio.TimeoutError:
            record_ws_timeout(room_type)
            await self.disconnect(websocket, room_type, room_id, user.id, user.company_id)
            logger.warning("WebSocket timeout", user_id=user.id, room_type=room_type, room_id=room_id)
        except Exception as e:
            record_ws_error("internal_error")
            logger.error("WebSocket error", error=str(e), user_id=user.id)
            await websocket.close(code=1011, reason="Internal error")
        finally:
            decrement_ws_connections()
            # Cleanup heartbeat task
            if user_key in self.heartbeat_tasks:
                self.heartbeat_tasks[user_key].cancel()
                del self.heartbeat_tasks[user_key]

    async def disconnect(self, websocket: WebSocket, room_type: str, room_id: int, user_id: int, company_id: int):
        """Handle disconnection with auto-resubscribe logic"""
        connection_key = f"{room_type}:{room_id}"
        user_key = f"{connection_key}:{user_id}"

        # Mark as recently disconnected for auto-resubscribe
        if connection_key not in self.recently_disconnected:
            self.recently_disconnected[connection_key] = set()
        self.recently_disconnected[connection_key].add(user_id)

        if connection_key in self.active_connections and user_id in self.active_connections[connection_key]:
            del self.active_connections[connection_key][user_id]
            if not self.active_connections[connection_key]:
                del self.active_connections[connection_key]

        # Cleanup heartbeat task
        if user_key in self.heartbeat_tasks:
            self.heartbeat_tasks[user_key].cancel()
            del self.heartbeat_tasks[user_key]

        # Set offline and publish event
        await redis_service.set_user_offline(company_id, user_id)
        await redis_service.publish_event(f"{room_type}:{room_id}", {
            "type": "user_disconnected",
            "user_id": user_id,
            f"{room_type}_id": room_id
        })

        # Auto-resubscribe attempt (simplified - in practice would need user context)
        # This would be triggered by client-side logic, but we can prepare for it
        record_ws_reconnect(room_type)

    async def _check_rate_limit(self, user_id: int) -> bool:
        """Check rate limit for connection attempts"""
        now = time.time()
        if user_id not in self.connection_attempts:
            self.connection_attempts[user_id] = []
        
        # Remove old attempts
        self.connection_attempts[user_id] = [t for t in self.connection_attempts[user_id] if now - t < self.rate_limit_window]
        
        if len(self.connection_attempts[user_id]) >= self.rate_limit_max:
            logger.warning("Rate limit exceeded", user_id=user_id)
            return False
        
        self.connection_attempts[user_id].append(now)
        return True

    async def _heartbeat_loop(self, websocket: WebSocket, connection_key: str, user_id: int, room_type: str):
        """Heartbeat ping-pong loop for connection health monitoring"""
        while True:
            try:
                await asyncio.sleep(self.heartbeat_interval)
                
                # Check if still connected
                if websocket.client_state != 1:  # OPEN
                    break
                
                # Send ping
                await websocket.send_json({"type": "ping", "timestamp": time.time()})
                
                # Wait for pong with timeout
                try:
                    await asyncio.wait_for(websocket.receive_json(), timeout=self.heartbeat_timeout)
                except asyncio.TimeoutError:
                    logger.warning("Heartbeat timeout", user_id=user_id, room_type=room_type)
                    record_ws_timeout(room_type)
                    await websocket.close(code=1006, reason="Heartbeat timeout")
                    break
                    
            except Exception as e:
                logger.error("Heartbeat loop error", error=str(e), user_id=user_id)
                break

    async def handle_message(self, websocket: WebSocket, data: dict, room_type: str, room_id: int, user: User, db: Session):
        """Handle incoming WebSocket messages with backpressure handling"""
        msg_type = data.get("type")

        # Add to backpressure queue if needed
        connection_key = f"{room_type}:{room_id}"
        if len(self.backpressure_queues[connection_key]) > 100:  # Threshold
            set_ws_backpressure_queue_size(room_type, len(self.backpressure_queues[connection_key]))
            logger.warning("Backpressure detected", room_type=room_type, queue_size=len(self.backpressure_queues[connection_key]))
            # Drop message or queue - for now log
            logger.warning("Message dropped due to backpressure", type=msg_type, user_id=user.id)
            return

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
                    from app.crud.crud_reactions import add_reaction
                    db_reaction = add_reaction(db, reaction_data["message_id"], user.id, reaction_data["emoji"])
                    await self.broadcast(websocket, {"type": "reaction_added", "reaction": {"id": db_reaction.id, "message_id": reaction_data["message_id"], "user_id": user.id, "emoji": reaction_data["emoji"]}}, room_type, room_id, user.id)
                elif reaction_data.get("action") == "remove":
                    from app.crud.crud_reactions import remove_reaction
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
