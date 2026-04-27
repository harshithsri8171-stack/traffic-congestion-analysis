from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from typing import List
import json
import asyncio

from ..database import get_db
from ..models.traffic_record import TrafficRecord
from sqlalchemy import desc

router = APIRouter()


class ConnectionManager:
    """Manage WebSocket connections"""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass


manager = ConnectionManager()


@router.websocket("/traffic")
async def websocket_traffic_updates(websocket: WebSocket):
    """WebSocket endpoint for live traffic updates"""

    await manager.connect(websocket)

    try:
        # Send initial connection message
        await websocket.send_json({
            "type": "connection",
            "message": "Connected to traffic updates"
        })

        # Keep connection alive and send updates
        while True:
            # In a real implementation, this would be triggered by actual traffic updates
            # For now, we'll send periodic updates
            await asyncio.sleep(5)

            # Example: Send a ping to keep connection alive
            await websocket.send_json({
                "type": "ping",
                "timestamp": str(asyncio.get_event_loop().time())
            })

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)


async def broadcast_traffic_update(traffic_data: dict):
    """Broadcast traffic update to all connected clients"""
    message = json.dumps({
        "type": "traffic_update",
        "data": traffic_data
    })
    await manager.broadcast(message)
