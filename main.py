from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import asyncio
import json
import jwt
import bcrypt
import logging
from datetime import datetime, timedelta
import os
from contextlib import asynccontextmanager

# Import our modules
from app.database import Database, init_db
from app.models import User, Account, Chat, Message
from app.services.telegram_service import TelegramService
from app.services.instagram_service import InstagramService
from app.services.websocket_manager import WebSocketManager
from app.auth import create_access_token, verify_token

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database instance
db = Database()
telegram_service = TelegramService(db)
instagram_service = InstagramService(db)
websocket_manager = WebSocketManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 BACKEND: Starting CrossMessenger...")
    try:
        global db
        db = await init_db()
        logger.info("✅ BACKEND: Database initialized")

        try:
            await telegram_service.start()
            logger.info("✅ BACKEND: Telegram service started")
        except Exception as e:
            logger.warning(f"⚠️  BACKEND: Telegram service failed to start: {e}")

        logger.info("🎉 BACKEND: CrossMessenger started successfully on port 5000")
        yield
    except Exception as e:
        logger.error(f"❌ BACKEND: Startup failed: {e}")
        yield
    finally:
        # Shutdown
        logger.info("🛑 BACKEND: Shutting down...")
        try:
            await telegram_service.stop()
        except:
            pass

app = FastAPI(title="CrossMessenger API", lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://0.0.0.0:5000", "http://localhost:5000", "http://127.0.0.1:5000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (frontend build)
import os
if os.path.exists("frontend/dist"):
    app.mount("/static", StaticFiles(directory="frontend/dist"), name="static")
    app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="frontend")

security = HTTPBearer()

# Pydantic models
class TelegramStartRequest(BaseModel):
    phone: str

class TelegramVerifyRequest(BaseModel):
    phone: str
    code: str

class SendMessageRequest(BaseModel):
    platform: str
    account_id: str
    chat_id: str
    text: str
    attachments: Optional[List[Dict[str, Any]]] = []

class UserRegistration(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

# Auth dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    user_id = verify_token(credentials.credentials)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = await db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# Auth endpoints
@app.post("/api/auth/register")
async def register(user_data: UserRegistration):
    logger.info(f"🔐 REGISTER ATTEMPT: Email={user_data.email}")

    try:
        # Check if user exists
        existing_user = await db.get_user_by_email(user_data.email)
        if existing_user:
            logger.warning(f"❌ REGISTER FAILED: User {user_data.email} already exists")
            raise HTTPException(status_code=400, detail="User already exists")

        # Hash password
        password_hash = bcrypt.hashpw(user_data.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Create user
        user_id = await db.create_user(user_data.email, password_hash)
        token = create_access_token(user_id)

        logger.info(f"✅ REGISTER SUCCESS: User ID={user_id}, Email={user_data.email}")
        return {"access_token": token, "token_type": "bearer"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ REGISTER ERROR: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")

@app.post("/api/auth/login")
async def login(user_data: UserLogin):
    logger.info(f"🔑 LOGIN ATTEMPT: Email={user_data.email}")

    user = await db.get_user_by_email(user_data.email)
    if not user or not bcrypt.checkpw(user_data.password.encode('utf-8'), user['password_hash'].encode('utf-8')):
        logger.warning(f"❌ LOGIN FAILED: Invalid credentials for {user_data.email}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(user['id'])
    logger.info(f"✅ LOGIN SUCCESS: User ID={user['id']}, Email={user_data.email}")
    return {"access_token": token, "token_type": "bearer"}

# Telegram auth endpoints
@app.post("/api/auth/telegram/start")
async def telegram_start(request: TelegramStartRequest, user: dict = Depends(get_current_user)):
    try:
        result = await telegram_service.start_auth(user['id'], request.phone)
        return {"message": "Code sent", "phone_code_hash": result}
    except Exception as e:
        logger.error(f"Telegram start error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/auth/telegram/verify")
async def telegram_verify(request: TelegramVerifyRequest, user: dict = Depends(get_current_user)):
    try:
        account_id = await telegram_service.verify_auth(user['id'], request.phone, request.code)
        return {"message": "Telegram connected", "account_id": account_id}
    except Exception as e:
        logger.error(f"Telegram verify error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# Instagram auth endpoints
@app.get("/api/auth/instagram/url")
async def instagram_url(user: dict = Depends(get_current_user)):
    url = instagram_service.get_auth_url(user['id'])
    return {"auth_url": url}

@app.get("/api/auth/instagram/callback")
async def instagram_callback(code: str, state: str, user: dict = Depends(get_current_user)):
    try:
        account_id = await instagram_service.handle_callback(code, state)
        return {"message": "Instagram connected", "account_id": account_id}
    except Exception as e:
        logger.error(f"Instagram callback error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# Message endpoints
@app.post("/api/messages/send")
async def send_message(request: SendMessageRequest, user: dict = Depends(get_current_user)):
    logger.info(f"📤 SENDING MESSAGE: User={user['email']}, Platform={request.platform}, Chat={request.chat_id}")

    try:
        if request.platform == "telegram":
            message_id = await telegram_service.send_message(
                user['id'], request.account_id, request.chat_id, request.text
            )
        elif request.platform == "instagram":
            message_id = await instagram_service.send_message(
                user['id'], request.account_id, request.chat_id, request.text
            )
        elif request.platform == "internal":
            message_id = await db.send_internal_message(
                user['id'], request.chat_id, request.text
            )
        else:
            logger.error(f"❌ INVALID PLATFORM: {request.platform}")
            raise HTTPException(status_code=400, detail="Invalid platform")

        logger.info(f"✅ MESSAGE SENT: ID={message_id}, Platform={request.platform}")
        return {"message_id": message_id}
    except Exception as e:
        logger.error(f"❌ SEND MESSAGE ERROR: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/chats")
async def get_chats(user: dict = Depends(get_current_user)):
    chats = await db.get_user_chats(user['id'])
    return {"chats": chats}

@app.get("/api/chats/{chat_id}/messages")
async def get_messages(chat_id: str, limit: int = 50, user: dict = Depends(get_current_user)):
    messages = await db.get_chat_messages(chat_id, limit)
    return {"messages": messages}

@app.get("/api/accounts")
async def get_accounts(user: dict = Depends(get_current_user)):
    accounts = await db.get_user_accounts(user['id'])
    return {"accounts": accounts}

@app.delete("/api/accounts/{account_id}")
async def disconnect_account(account_id: str, user: dict = Depends(get_current_user)):
    await db.disconnect_account(user['id'], account_id)
    return {"message": "Account disconnected"}

# WebSocket endpoint
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await websocket_manager.connect(websocket, user_id)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        websocket_manager.disconnect(user_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)