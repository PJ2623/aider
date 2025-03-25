import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

# Import routers from src package
from src import articles, messages, users, posts, chat, councilor

from utils.websocket import WebsocketConnectionManager

# Import document models from schemas package
from schemas import articles as article_schemas
from schemas import messages as message_schemas
from schemas import users as user_schemas
from schemas import posts as post_schemas
from schemas import chat as chat_schemas
from schemas import councilor as councilor_schemas

@asynccontextmanager
async def lifespan(app: FastAPI):
    client = AsyncIOMotorClient("mongodb://localhost:27017")  # * Connect to MongoDB

    await init_beanie(
        database=client["Aider"],
        document_models=[
            article_schemas.Articles,
            message_schemas.Messages,
            user_schemas.Users,
            post_schemas.Posts,
            chat_schemas.Chats,
            councilor_schemas.Councilor,
        ],
    )  # * Initialize Beanie

    yield
    client.close()

connection_manager = WebsocketConnectionManager()
app = FastAPI(
    title="Addiction Aider API",
    description="API for Addiction Aider",
    version="0.1",
    lifespan=lifespan,
    debug=True,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/api/v1/chat/c/ws")
async def chat_to_councilor(self, websocket: WebSocket):
    await websocket.accept()  # *Accept the connection immediately
    
    # *Receive the initial JSON message with user_id
    init_data: dict = await websocket.receive_json()
    user_id = init_data.get("user_id")
    
    # *Register the WebSocket connection
    await connection_manager.connect(user_id, websocket)

    try:
        # *Continuously listen for incoming messages
        while True:
            pass

    except WebSocketDisconnect:
        connection_manager.disconnect(user_id)
        
        
@app.websocket("/api/v1/chat/g/ws")
async def chat_to_groups(self, websocket: WebSocket):
    await websocket.accept()  # *Accept the connection immediately
    
    # *Receive the initial JSON message with user_id
    init_data: dict = await websocket.receive_json()
    user_id = init_data.get("user_id")
    
    # *Register the WebSocket connection
    await connection_manager.connect(user_id, websocket)

    try:
        # *Continuously listen for incoming messages
        while True:
            pass

    except WebSocketDisconnect:
        connection_manager.disconnect(user_id)

# Include routers
app.include_router(articles.router)
app.include_router(messages.router)
app.include_router(users.router)
app.include_router(posts.router)
app.include_router(chat.router)
app.include_router(councilor.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)