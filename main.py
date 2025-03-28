from pprint import pprint
import uvicorn
import json

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie, PydanticObjectId
from beanie.operators import And, In, Push

# Import routers from src package
from src import articles, messages, users, posts, councilor, auth

from utils.websocket import WebsocketConnectionManager

# Import document models from schemas package
from schemas import articles as article_schemas
from schemas import messages as message_schemas
from schemas import users as user_schemas
from schemas import posts as post_schemas
from schemas import councilor as councilor_schemas

from fastapi.responses import HTMLResponse

from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.runnables import RunnablePassthrough, Runnable
from langchain_core.prompts import ChatPromptTemplate
from langchain.vectorstores import FAISS
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain

embeddings = OllamaEmbeddings(
    model="gemma2:2b",
)

model = ChatOllama(
    model="gemma2:2b",
)

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://192.168.64.1:8000/api/v1/bot/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""

chat_bot = {}


file_path = "./porn-addict.pdf"
loader = PyPDFLoader(file_path, extract_images=True)

data = loader.load()


def init_bot():
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    splits = text_splitter.split_documents(data)

    print("Done splitting")

    vector_store = FAISS.from_documents(documents=splits, embedding=embeddings)

    print("Done creating vector store")

    retriever = vector_store.as_retriever()

    print("Done creating retriever")

    system_prompt = (
        """Act as a compassionate, non-judgmental AI assistant specializing in substance abuse support for
        porn addiction, cocaine, marijuana, and prescription drug misuse.
        Provide science-based facts, harm-reduction strategies, and actionable
        resources (e.g., Speaking to Addiction Aider councilors.
        Acknowledge the complexity of addiction, emphasize confidentiality, and encourage professional care for severe cases.
        Never diagnose or replace medical advice.
        Prioritize empathy and user safety in all responses."""
        "Use the following pieces of retrieved context to answer"
        "the question. If you don't know the answer, you can suggest the user to speak to one of Addiction Aider councillors."
        "\n\n"
        "{context}"
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{input}"),
        ]
    )

    qa_chain = create_stuff_documents_chain(model, prompt)
    rag_chain = create_retrieval_chain(retriever, qa_chain)

    print("Done creating chains")
    return rag_chain


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
            councilor_schemas.Councilor,
        ],
    )  # * Initialize Beanie
    chat_bot["rag_chain"] = init_bot()

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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/bot/", tags=["Bot"])
async def get():
    return HTMLResponse(html)


@app.websocket("/api/v1/chat/ws")
async def chat_to_councilor_or_group(websocket: WebSocket):
    groups = ["explicit-quitters", "grass-quitters"]
    await websocket.accept()

    try:
        # Validate initial connection
        init_data: dict = await websocket.receive_json()
        user_id = init_data.get("user_id")
        
        if not user_id:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        await connection_manager.connect(user_id, websocket)
        print(f"Active connections: {connection_manager.active_connections.keys()}")

        while True:
            data: dict = await websocket.receive_json()
            
            # Validate connection status
            if user_id not in connection_manager.active_connections:
                await websocket.close()
                break

            # Force sender to be authenticated user
            data["sender"] = user_id
            recipient = data.get("recipient")

            if recipient in groups:
                # Group message logic
                past_conversations = await message_schemas.Messages.find_many(
                    message_schemas.Messages.recipient == recipient
                ).to_list()
                
                active_users = set(connection_manager.active_connections.keys())
                past_participants = {conv.sender for conv in past_conversations}
                recipients = active_users & past_participants

                print(f"Sending to group {recipient}, recipients: {recipients}")
                for user in recipients:
                    await connection_manager.send_to_user(user, data)
                    
                # Save message to database
                new_message = await message_schemas.Messages(
                    sender=user_id,
                    recipient=recipient,
                    content=data.get("message")
                ).insert()
                
                # Add message ID to group's chats list
                group_in_db = await user_schemas.Users.find_one(
                    In(user_schemas.Users.username, groups),
                )
                await group_in_db.update(Push({user_schemas.Users.chats: new_message.id}))
                await group_in_db.save()
            else:
                # Individual message logic
                target_user = recipient
                print(f"Attempting to send to individual: {target_user}")
                
                if target_user in connection_manager.active_connections:
                    print(f"Sending to {target_user}: {data}")
                    await connection_manager.send_to_user(target_user, data)
                else:
                    print(f"Target user {target_user} not connected")
                    # Optionally notify sender about failed delivery
                    await connection_manager.send_to_user(user_id, {
                        "status": "error",
                        "message": f"Recipient {target_user} is not connected"
                    })
                    
                # Save message to database
                new_message = await message_schemas.Messages(
                    sender=user_id,
                    recipient=recipient,
                    content=data.get("message")
                ).insert()
                
                user_in_db = await user_schemas.Users.find_one(
                    user_schemas.Users.id == PydanticObjectId(user_id)
                )
                await user_in_db.update(Push({user_schemas.Users.chats: new_message.id}))
                await user_in_db.save()

    except (WebSocketDisconnect, json.JSONDecodeError) as e:
        print(f"WebSocket error: {str(e)}")
        
        
@app.websocket("/api/v1/chat/g/ws")
async def chat_to_groups(websocket: WebSocket):
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
        
@app.websocket('/api/v1/bot/ws')
async def chat_to_bot(websocket: WebSocket):
    await websocket.accept()

    while True:
        data = await websocket.receive_text()
        response = chat_bot["rag_chain"].invoke({"input": data})
        await websocket.send_text(response["answer"])

# Include routers
app.include_router(articles.router)
app.include_router(messages.router)
app.include_router(users.router)
app.include_router(posts.router)
app.include_router(councilor.router)
app.include_router(auth.router)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)