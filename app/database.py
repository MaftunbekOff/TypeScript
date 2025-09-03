
import asyncpg
import json
import os
from typing import List, Dict, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.pool = None
        
    async def init_pool(self):
        self.pool = await asyncpg.create_pool(
            os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/crossmessenger")
        )
        
    async def get_user_by_email(self, email: str) -> Optional[Dict]:
        logger.info(f"🔍 DB: Looking up user by email={email}")
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM users WHERE email = $1", email)
            result = dict(row) if row else None
            logger.info(f"{'✅' if result else '❌'} DB: User {'found' if result else 'not found'}")
            return result
            
    async def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
            return dict(row) if row else None
            
    async def create_user(self, email: str, password_hash: str) -> str:
        logger.info(f"💾 DB: Creating user with email={email}")
        async with self.pool.acquire() as conn:
            user_id = await conn.fetchval(
                "INSERT INTO users (email, password_hash, created_at) VALUES ($1, $2, $3) RETURNING id",
                email, password_hash, datetime.utcnow()
            )
            logger.info(f"✅ DB: User created with ID={user_id}")
            return str(user_id)
            
    async def create_account(self, user_id: str, platform: str, platform_account_id: str, session_encrypted: str) -> str:
        async with self.pool.acquire() as conn:
            account_id = await conn.fetchval(
                """INSERT INTO accounts (user_id, platform, platform_account_id, session_encrypted, created_at) 
                   VALUES ($1, $2, $3, $4, $5) RETURNING id""",
                user_id, platform, platform_account_id, session_encrypted, datetime.utcnow()
            )
            return str(account_id)
            
    async def get_user_accounts(self, user_id: str) -> List[Dict]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM accounts WHERE user_id = $1", user_id)
            return [dict(row) for row in rows]
            
    async def get_account_session(self, account_id: str) -> Optional[str]:
        async with self.pool.acquire() as conn:
            session = await conn.fetchval("SELECT session_encrypted FROM accounts WHERE id = $1", account_id)
            return session
            
    async def update_account_session(self, account_id: str, session_encrypted: str):
        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE accounts SET session_encrypted = $1 WHERE id = $2",
                session_encrypted, account_id
            )
            
    async def disconnect_account(self, user_id: str, account_id: str):
        async with self.pool.acquire() as conn:
            await conn.execute(
                "DELETE FROM accounts WHERE id = $1 AND user_id = $2",
                account_id, user_id
            )
            
    async def create_chat(self, account_id: str, chat_id: str, title: str) -> str:
        async with self.pool.acquire() as conn:
            try:
                await conn.execute(
                    """INSERT INTO chats (account_id, chat_id, title, last_message_at) 
                       VALUES ($1, $2, $3, $4) ON CONFLICT (account_id, chat_id) DO NOTHING""",
                    account_id, chat_id, title, datetime.utcnow()
                )
                return chat_id
            except Exception as e:
                logger.error(f"Error creating chat: {e}")
                return chat_id
                
    async def get_user_chats(self, user_id: str) -> List[Dict]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """SELECT c.*, a.platform FROM chats c 
                   JOIN accounts a ON c.account_id = a.id 
                   WHERE a.user_id = $1 ORDER BY c.last_message_at DESC""",
                user_id
            )
            return [dict(row) for row in rows]
            
    async def store_message(self, chat_id: str, platform: str, platform_message_id: str, 
                           sender_id: str, sender_name: str, text: str, 
                           attachments: List[Dict] = None, timestamp: datetime = None) -> str:
        async with self.pool.acquire() as conn:
            message_id = await conn.fetchval(
                """INSERT INTO messages (chat_id, platform, platform_message_id, sender_id, 
                   sender_name, text, attachments_json, timestamp, status) 
                   VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9) RETURNING id""",
                chat_id, platform, platform_message_id, sender_id, sender_name, text,
                json.dumps(attachments or []), timestamp or datetime.utcnow(), "delivered"
            )
            return str(message_id)
            
    async def get_chat_messages(self, chat_id: str, limit: int = 50) -> List[Dict]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM messages WHERE chat_id = $1 ORDER BY timestamp DESC LIMIT $2",
                chat_id, limit
            )
            messages = []
            for row in rows:
                msg = dict(row)
                msg['attachments'] = json.loads(msg.get('attachments_json', '[]'))
                messages.append(msg)
            return list(reversed(messages))
            
    async def send_internal_message(self, user_id: str, chat_id: str, text: str) -> str:
        # For internal messages, chat_id format: "internal_{user1_id}_{user2_id}"
        message_id = await self.store_message(
            chat_id, "internal", f"internal_{datetime.utcnow().timestamp()}", 
            user_id, "Internal User", text
        )
        return message_id

async def init_db():
    db = Database()
    await db.init_pool()
    
    # Create tables
    async with db.pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                platform VARCHAR(50) NOT NULL,
                platform_account_id VARCHAR(255) NOT NULL,
                session_encrypted TEXT,
                created_at TIMESTAMP DEFAULT NOW(),
                UNIQUE(user_id, platform, platform_account_id)
            )
        """)
        
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS chats (
                id SERIAL PRIMARY KEY,
                account_id INTEGER REFERENCES accounts(id) ON DELETE CASCADE,
                chat_id VARCHAR(255) NOT NULL,
                title VARCHAR(255),
                last_message_at TIMESTAMP DEFAULT NOW(),
                UNIQUE(account_id, chat_id)
            )
        """)
        
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                chat_id VARCHAR(255) NOT NULL,
                platform VARCHAR(50) NOT NULL,
                platform_message_id VARCHAR(255),
                sender_id VARCHAR(255),
                sender_name VARCHAR(255),
                text TEXT,
                attachments_json TEXT DEFAULT '[]',
                timestamp TIMESTAMP DEFAULT NOW(),
                status VARCHAR(50) DEFAULT 'sent'
            )
        """)
        
    logger.info("Database initialized")
    return db
