
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import PhoneCodeInvalidError, PhoneNumberInvalidError
import asyncio
import os
import logging
from typing import Dict, Optional
from datetime import datetime
from app.encryption import encrypt_data, decrypt_data
from app.services.websocket_manager import websocket_manager

logger = logging.getLogger(__name__)

class TelegramService:
    def __init__(self, db):
        self.db = db
        self.api_id = int(os.getenv("API_ID", "0"))
        self.api_hash = os.getenv("API_HASH", "")
        self.clients: Dict[str, TelegramClient] = {}
        self.auth_sessions: Dict[str, Dict] = {}
        
    async def start(self):
        logger.info("Telegram service started")
        
    async def stop(self):
        for client in self.clients.values():
            await client.disconnect()
        logger.info("Telegram service stopped")
        
    async def start_auth(self, user_id: str, phone: str) -> str:
        try:
            client = TelegramClient(StringSession(), self.api_id, self.api_hash)
            await client.connect()
            
            result = await client.send_code_request(phone)
            self.auth_sessions[user_id] = {
                "client": client,
                "phone": phone,
                "phone_code_hash": result.phone_code_hash
            }
            
            return result.phone_code_hash
        except Exception as e:
            logger.error(f"Error starting Telegram auth: {e}")
            raise e
            
    async def verify_auth(self, user_id: str, phone: str, code: str) -> str:
        try:
            session_data = self.auth_sessions.get(user_id)
            if not session_data:
                raise Exception("No active auth session")
                
            client = session_data["client"]
            phone_code_hash = session_data["phone_code_hash"]
            
            await client.sign_in(phone, code, phone_code_hash=phone_code_hash)
            
            # Get user info
            me = await client.get_me()
            platform_account_id = str(me.id)
            
            # Save encrypted session
            session_string = client.session.save()
            encrypted_session = encrypt_data(session_string)
            
            account_id = await self.db.create_account(
                user_id, "telegram", platform_account_id, encrypted_session
            )
            
            # Start listening for messages
            await self._start_message_listener(account_id, client)
            self.clients[account_id] = client
            
            # Load recent chats
            await self._load_recent_chats(account_id, client)
            
            # Clean up auth session
            del self.auth_sessions[user_id]
            
            return account_id
            
        except PhoneCodeInvalidError:
            raise Exception("Invalid verification code")
        except Exception as e:
            logger.error(f"Error verifying Telegram auth: {e}")
            raise e
            
    async def _start_message_listener(self, account_id: str, client: TelegramClient):
        @client.on(events.NewMessage)
        async def handle_new_message(event):
            try:
                chat_id = str(event.chat_id)
                sender = await event.get_sender()
                sender_name = getattr(sender, 'first_name', '') or getattr(sender, 'title', 'Unknown')
                
                # Store message in DB
                await self.db.store_message(
                    chat_id=chat_id,
                    platform="telegram",
                    platform_message_id=str(event.id),
                    sender_id=str(sender.id),
                    sender_name=sender_name,
                    text=event.text or "",
                    timestamp=event.date
                )
                
                # Send to WebSocket
                message_data = {
                    "type": "message:new",
                    "platform": "telegram",
                    "chat_id": chat_id,
                    "sender_name": sender_name,
                    "text": event.text or "",
                    "timestamp": event.date.isoformat()
                }
                
                # Get user_id from account
                accounts = await self.db.get_user_accounts("")  # We need to modify this
                for account in accounts:
                    if account['id'] == account_id:
                        await websocket_manager.send_to_user(account['user_id'], message_data)
                        break
                        
            except Exception as e:
                logger.error(f"Error handling new message: {e}")
                
    async def _load_recent_chats(self, account_id: str, client: TelegramClient):
        try:
            async for dialog in client.iter_dialogs(limit=20):
                await self.db.create_chat(
                    account_id=account_id,
                    chat_id=str(dialog.id),
                    title=dialog.title or "Unknown Chat"
                )
                
                # Load recent messages
                async for message in client.iter_messages(dialog, limit=50):
                    if message.text:
                        sender = await message.get_sender()
                        sender_name = getattr(sender, 'first_name', '') or getattr(sender, 'title', 'Unknown')
                        
                        await self.db.store_message(
                            chat_id=str(dialog.id),
                            platform="telegram",
                            platform_message_id=str(message.id),
                            sender_id=str(sender.id),
                            sender_name=sender_name,
                            text=message.text,
                            timestamp=message.date
                        )
        except Exception as e:
            logger.error(f"Error loading recent chats: {e}")
            
    async def send_message(self, user_id: str, account_id: str, chat_id: str, text: str) -> str:
        try:
            client = self.clients.get(account_id)
            if not client:
                # Reconnect client
                session_encrypted = await self.db.get_account_session(account_id)
                session_string = decrypt_data(session_encrypted)
                client = TelegramClient(StringSession(session_string), self.api_id, self.api_hash)
                await client.connect()
                self.clients[account_id] = client
                
            message = await client.send_message(int(chat_id), text)
            return str(message.id)
            
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            raise e
