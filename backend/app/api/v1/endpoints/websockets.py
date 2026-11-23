from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Dict, List
import json
import logging
from backend.app.core.security import decode_token

logger = logging.getLogger("finflow.websockets")
router = APIRouter()

class ConnectionManager:
    def __init__(self):
        # Map org_id -> list of active WebSockets
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, org_id: str, websocket: WebSocket):
        await websocket.accept()
        if org_id not in self.active_connections:
            self.active_connections[org_id] = []
        self.active_connections[org_id].append(websocket)
        logger.info(f"WebSocket connected for org: {org_id}")

    def disconnect(self, org_id: str, websocket: WebSocket):
        if org_id in self.active_connections:
            if websocket in self.active_connections[org_id]:
                self.active_connections[org_id].remove(websocket)
            if not self.active_connections[org_id]:
                del self.active_connections[org_id]
        logger.info(f"WebSocket disconnected for org: {org_id}")

    async def broadcast_to_org(self, org_id: str, message: dict):
        if org_id in self.active_connections:
            payload = json.dumps(message)
            for connection in self.active_connections[org_id]:
                try:
                    await connection.send_text(payload)
                except Exception as e:
                    logger.error(f"Error sending message over WebSocket: {e}")

ws_manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(None)):
    if not token:
        await websocket.close(code=4001)
        return

    payload = decode_token(token)
    if not payload:
        await websocket.close(code=4003)
        return

    org_id = payload.get("org_id", "default")
    await ws_manager.connect(org_id, websocket)

    try:
        # Send initial confirmation heartbeat
        await websocket.send_text(json.dumps({
            "type": "CONNECTION_ESTABLISHED",
            "message": "Connected to FinFlow live operational stream.",
            "org_id": org_id
        }))

        while True:
            data = await websocket.receive_text()
            # Handle client ping
            if data == "ping":
                await websocket.send_text(json.dumps({"type": "PONG"}))
    except WebSocketDisconnect:
        ws_manager.disconnect(org_id, websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        ws_manager.disconnect(org_id, websocket)
