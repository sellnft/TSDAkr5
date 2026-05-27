from typing import Dict, Set
from fastapi import WebSocket

class RoomManager:
    def __init__(self):
        self.rooms: Dict[str, Dict[str, WebSocket]] = {}
    
    async def connect(self, room_id: str, username: str, websocket: WebSocket):
        await websocket.accept()
        
        if room_id not in self.rooms:
            self.rooms[room_id] = {}
        
        self.rooms[room_id][username] = websocket
        
        await self.broadcast(room_id, {
            "type": "system",
            "text": f"{username} joined the room"
        })
    
    async def disconnect(self, room_id: str, username: str, websocket: WebSocket):
        if room_id in self.rooms and username in self.rooms[room_id]:
            del self.rooms[room_id][username]
            
            if not self.rooms[room_id]:
                del self.rooms[room_id]
            else:

                await self.broadcast(room_id, {
                    "type": "system",
                    "text": f"{username} left the room"
                })
    
    async def broadcast(self, room_id: str, payload: dict):
        if room_id in self.rooms:
            for username, connection in self.rooms[room_id].items():
                try:
                    await connection.send_json(payload)
                except:
                    pass
    
    def get_users(self, room_id: str) -> list[str]:
        if room_id in self.rooms:
            return list(self.rooms[room_id].keys())
        return []

room_manager = RoomManager()