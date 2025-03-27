"""
Contains all code for websocket connectivity and management
"""
from fastapi import WebSocket
from typing import Dict


# Connection manager for handling WebSocket connections
class WebsocketConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        self.active_connections[user_id] = websocket
        
        print(f"Active connections: {self.active_connections.keys()}")

    async def disconnect(self, user_id: str):
        """Disconnect and remove a user's WebSocket connection"""
        if user_id in self.active_connections:
            await self.active_connections[user_id].close()
            del self.active_connections[user_id]

    async def send_to_user(self, user_id: str, data: dict):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_json(data)

    async def broadcast(self, data: str):
        for connection in self.active_connections.values():
            await connection.send_text(data)