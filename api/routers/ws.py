"""
WebSocket Router - Real-time Updates
"""

import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
import redis.asyncio as redis

from ..database import get_db
from ..auth import verify_token
from ..websocket import manager
import os

router = APIRouter(tags=["WebSocket"])

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


@router.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str):
    """
    WebSocket endpoint for real-time job updates.
    Connect with JWT token to authenticate.
    """
    # Verify token
    payload = verify_token(token)
    if not payload:
        await websocket.close(code=4001)
        return
    
    user_id = payload.get("sub")
    await manager.connect(websocket, user_id)
    
    try:
        # Subscribe to Redis for job updates
        r = redis.from_url(REDIS_URL)
        pubsub = r.pubsub()
        await pubsub.subscribe("job_updates")
        
        # Send initial confirmation
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to job updates"
        })
        
        # Listen for updates
        async def listen_redis():
            async for message in pubsub.listen():
                if message["type"] == "message":
                    data = json.loads(message["data"])
                    await websocket.send_json({
                        "type": "job_update",
                        **data
                    })
        
        # Listen for client messages (ping/pong)
        async def listen_client():
            while True:
                data = await websocket.receive_text()
                if data == "ping":
                    await websocket.send_text("pong")
        
        # Run both listeners
        await asyncio.gather(
            listen_redis(),
            listen_client()
        )
        
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception as e:
        manager.disconnect(websocket, user_id)
        await websocket.close()
