from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, status
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from typing import Optional
from app.routers import tasks, users, admin
from app.websocket.room_manager import room_manager
from app.schemas import HealthResponse, RoomUsersResponse
from app.storage import get_storage
import uvicorn


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Запуск программы...")
    yield
    print("Завершение работы программы...")


app = FastAPI(
    title="Task Manager API",
    description="API for managing tasks with WebSocket chat rooms",
    version="1.0.0",
    lifespan=lifespan
)
app.include_router(tasks.router)
app.include_router(users.router)
app.include_router(admin.router)


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check() -> HealthResponse:
    return HealthResponse(status="ok", version="1.0.0")


@app.get("/rooms/{room_id}/users", response_model=RoomUsersResponse, tags=["websocket"])
async def get_room_users(room_id: str) -> RoomUsersResponse:
    users = room_manager.get_users(room_id)
    return RoomUsersResponse(room_id=room_id, users=users)


@app.websocket("/ws/rooms/{room_id}")
async def websocket_chat(
    websocket: WebSocket,
    room_id: str,
    username: Optional[str] = None
):
    if not username or not username.strip():
        await websocket.close(code=1008, reason="username parameter is required")
        return
    
    username = username.strip()
    
    try:
        await room_manager.connect(room_id, username, websocket)
        while True:
            try:
                data = await websocket.receive_json()
                if data.get("type") != "message":
                    continue
                
                text = data.get("text", "")
                if len(text) > 300:
                    await websocket.send_json({
                        "type": "error",
                        "detail": "Message is too long"
                    })
                    continue
                await room_manager.broadcast(room_id, {
                    "type": "message",
                    "room_id": room_id,
                    "username": username,
                    "text": text
                })
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                print(f"Error processing message: {e}")
                break
                
    except WebSocketDisconnect:
        pass
    finally:
        await room_manager.disconnect(room_id, username, websocket)


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc)}
    )
