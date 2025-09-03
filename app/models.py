
from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict, Optional, Any

class User(BaseModel):
    id: str
    email: str
    created_at: datetime

class Account(BaseModel):
    id: str
    user_id: str
    platform: str
    platform_account_id: str
    created_at: datetime

class Chat(BaseModel):
    id: str
    account_id: str
    chat_id: str
    title: str
    last_message_at: datetime

class Message(BaseModel):
    id: str
    chat_id: str
    platform: str
    platform_message_id: Optional[str]
    sender_id: str
    sender_name: str
    text: str
    attachments: List[Dict[str, Any]] = []
    timestamp: datetime
    status: str

class UnifiedMessage(BaseModel):
    platform: str
    account_id: str
    chat_id: str
    sender_id: str
    sender_name: str
    message_id: str
    text: str
    attachments: List[Dict[str, Any]] = []
    timestamp: str
    status: str
