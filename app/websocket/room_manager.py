from typing import Dict, List
from fastapi import WebSocket, WebSocketDisconnect


class RoomManager:
    def __init__(self):
        self._rooms: Dict[str, Dict[str, WebSocket]] = {}
    
    async def connect(self, room_id: str, username: str, websocket: WebSocket) -> None:
        await websocket.accept()
        
        if room_id not in self._rooms:
            self._rooms[room_id] = {}
        
        self._rooms[room_id][username] = websocket
        await self._broadcast_join(room_id, username)
    
    async def disconnect(self, room_id: str, username: str, websocket: WebSocket) -> None:
        if room_id in self._rooms:
            if username in self._rooms[room_id]:
                del self._rooms[room_id][username]
                
                if not self._rooms[room_id]:
                    del self._rooms[room_id]
                
                await self._broadcast_leave(room_id, username)
    
    async def broadcast(self, room_id: str, payload: dict) -> None:
        if room_id not in self._rooms:
            return
        
        disconnected_users = []
        
        for username, websocket in self._rooms[room_id].items():
            try:
                await websocket.send_json(payload)
            except WebSocketDisconnect:
                disconnected_users.append(username)
            except Exception:
                pass
        
        for username in disconnected_users:
            if room_id in self._rooms and username in self._rooms[room_id]:
                del self._rooms[room_id][username]
    
    def get_users(self, room_id: str) -> List[str]:
        if room_id not in self._rooms:
            return []
        return list(self._rooms[room_id].keys())
    
    async def _broadcast_join(self, room_id: str, username: str) -> None:
        await self.broadcast(room_id, {
            "type": "system",
            "message": f"{username} joined the room"
        })
    
    async def _broadcast_leave(self, room_id: str, username: str) -> None:
        await self.broadcast(room_id, {
            "type": "system",
            "message": f"{username} left the room"
        })


room_manager = RoomManager()