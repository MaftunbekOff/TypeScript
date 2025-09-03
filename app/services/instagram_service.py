
import aiohttp
import os
import logging
from typing import Dict, Optional
from urllib.parse import urlencode
from app.encryption import encrypt_data, decrypt_data

logger = logging.getLogger(__name__)

class InstagramService:
    def __init__(self, db):
        self.db = db
        self.app_id = os.getenv("FACEBOOK_APP_ID", "")
        self.app_secret = os.getenv("FACEBOOK_APP_SECRET", "")
        self.redirect_uri = f"{os.getenv('BACKEND_URL', 'http://0.0.0.0:5000')}/api/auth/instagram/callback"
        
    def get_auth_url(self, user_id: str) -> str:
        params = {
            "client_id": self.app_id,
            "redirect_uri": self.redirect_uri,
            "scope": "instagram_basic,instagram_content_publish",  # Note: DM access is limited
            "response_type": "code",
            "state": user_id
        }
        return f"https://api.instagram.com/oauth/authorize?{urlencode(params)}"
        
    async def handle_callback(self, code: str, state: str) -> str:
        try:
            user_id = state
            
            # Exchange code for access token
            async with aiohttp.ClientSession() as session:
                data = {
                    "client_id": self.app_id,
                    "client_secret": self.app_secret,
                    "grant_type": "authorization_code",
                    "redirect_uri": self.redirect_uri,
                    "code": code
                }
                
                async with session.post("https://api.instagram.com/oauth/access_token", data=data) as resp:
                    result = await resp.json()
                    
                if "access_token" not in result:
                    raise Exception("Failed to get access token")
                    
                access_token = result["access_token"]
                user_data = result.get("user", {})
                platform_account_id = str(user_data.get("id", "unknown"))
                
                # Encrypt and store token
                encrypted_token = encrypt_data(access_token)
                account_id = await self.db.create_account(
                    user_id, "instagram", platform_account_id, encrypted_token
                )
                
                # Load mock chats (since Instagram DM access is limited)
                await self._load_mock_chats(account_id)
                
                return account_id
                
        except Exception as e:
            logger.error(f"Error handling Instagram callback: {e}")
            raise e
            
    async def _load_mock_chats(self, account_id: str):
        """Load mock chats since Instagram DM access is limited in Graph API"""
        mock_chats = [
            {"id": "instagram_chat_1", "title": "Instagram Chat 1 (Mock)"},
            {"id": "instagram_chat_2", "title": "Instagram Chat 2 (Mock)"}
        ]
        
        for chat in mock_chats:
            await self.db.create_chat(account_id, chat["id"], chat["title"])
            
            # Add mock messages
            await self.db.store_message(
                chat_id=chat["id"],
                platform="instagram",
                platform_message_id=f"mock_{chat['id']}_1",
                sender_id="mock_sender",
                sender_name="Mock User",
                text=f"This is a mock message from {chat['title']}. Replace with real Instagram Graph API calls when DM access is available.",
            )
            
    async def send_message(self, user_id: str, account_id: str, chat_id: str, text: str) -> str:
        """Mock send message - replace with real Graph API when available"""
        try:
            # For now, just store as sent message
            message_id = await self.db.store_message(
                chat_id=chat_id,
                platform="instagram",
                platform_message_id=f"sent_{chat_id}_{text[:10]}",
                sender_id="self",
                sender_name="You",
                text=f"[MOCK SENT] {text}",
            )
            
            logger.info(f"Mock Instagram message sent: {text}")
            return message_id
            
        except Exception as e:
            logger.error(f"Error sending Instagram message: {e}")
            raise e
