import json
from typing import Dict, List

import structlog
from fastapi import WebSocket

logger = structlog.get_logger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = (
            {}
        )  # company_id -> list of websockets

    async def connect(self, websocket: WebSocket, company_id: int):
        await websocket.accept()
        if company_id not in self.active_connections:
            self.active_connections[company_id] = []
        self.active_connections[company_id].append(websocket)

    def disconnect(self, websocket: WebSocket, company_id: int):
        if company_id in self.active_connections:
            self.active_connections[company_id].remove(websocket)
            if not self.active_connections[company_id]:
                del self.active_connections[company_id]

    async def broadcast_to_company(self, company_id: int, message: dict):
        if company_id in self.active_connections:
            for connection in self.active_connections[company_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    # Handle disconnected clients
                    pass

    async def broadcast_to_user(self, user_id: int, message: dict):
        # If needed, broadcast to specific user across companies
        pass


manager = ConnectionManager()
