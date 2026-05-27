from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import JSONResponse
from app.routers import tasks, users, admin
from app.room_manager import room_manager
from app.schemas import HealthResponse, RoomUsersResponse
import os

app = FastAPI(title="Task Manager API")

app.include_router(tasks.router)
app.include_router(users.router)
app.include_router(admin.router)

@app.get("/health", response_model=HealthResponse)
async def health_check():
    env = os.getenv("APP_ENV", "development")
    return HealthResponse(status="ok", env=env)

@app.websocket("/ws/rooms/{room_id}")
async def websocket_room(
    websocket: WebSocket,
    room_id: str,
    username: str = Query(None)
):

    if not username or not username.strip():
        await websocket.close(code=1008)
        return
    
    username = username.strip()
    
    try:
        await room_manager.connect(room_id, username, websocket)
        
        while True:
            data = await websocket.receive_json()
            
            if "text" in data and len(data["text"]) > 300:
                await websocket.send_json({
                    "type": "error",
                    "detail": "Message is too long"
                })
                continue
            
            await room_manager.broadcast(room_id, {
                "type": "message",
                "room_id": room_id,
                "username": username,
                "text": data.get("text", "")
            })
            
    except WebSocketDisconnect:
        await room_manager.disconnect(room_id, username, websocket)

@app.get("/rooms/{room_id}/users", response_model=RoomUsersResponse)
async def get_room_users(room_id: str):
    users = room_manager.get_users(room_id)
    return RoomUsersResponse(room_id=room_id, users=users)