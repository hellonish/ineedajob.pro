"""
WebSocket Manager for Real-time Updates
"""

import os
import json
from typing import Dict, Set
from fastapi import WebSocket
import redis
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


class ConnectionManager:
    """Manages WebSocket connections per user."""
    
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.redis_client = None
    
    def _get_redis(self):
        if self.redis_client is None:
            self.redis_client = redis.from_url(REDIS_URL)
        return self.redis_client
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept and register a WebSocket connection."""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
    
    def disconnect(self, websocket: WebSocket, user_id: str):
        """Remove a WebSocket connection."""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
    
    async def send_to_user(self, user_id: str, message: dict):
        """Send message to all connections for a user."""
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except:
                    pass  # Connection may be closed
    
    async def broadcast_job_update(self, job_id: str, status: str, data: dict = None):
        """Broadcast job update to subscribed users."""
        message = {
            "type": "job_update",
            "job_id": job_id,
            "status": status,
            "data": data or {}
        }
        # Send to all connected users (in production, filter by job owner)
        for user_id in self.active_connections:
            await self.send_to_user(user_id, message)


# Global manager
manager = ConnectionManager()


def notify_job_status(job_id: str, status: str, data: dict = None):
    """
    Publish job status update to Redis (for Celery workers to call).
    The WebSocket handler will pick this up and broadcast.
    """
    try:
        r = redis.from_url(REDIS_URL)
        message = json.dumps({
            "job_id": job_id,
            "status": status,
            "data": data or {}
        })
        r.publish("job_updates", message)
    except Exception as e:
        print(f"Failed to publish job status: {e}")
