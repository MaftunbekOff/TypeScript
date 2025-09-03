
# CrossMessenger

A unified messaging platform that integrates Telegram, Instagram, and internal chat in a single web application.

## Features

- **Telegram Integration**: Connect via MTProto using Telethon
- **Instagram Integration**: OAuth-based connection (with DM limitations noted)
- **Internal Chat**: Built-in messaging between platform users
- **Real-time Updates**: WebSocket-based live message updates
- **Unified Interface**: Single dashboard for all messaging platforms
- **Secure**: AES-256 encryption for session storage

## Tech Stack

- **Backend**: Python 3.11 + FastAPI
- **Frontend**: React + TypeScript + Vite
- **Database**: PostgreSQL with asyncpg
- **Real-time**: WebSockets
- **Authentication**: JWT tokens
- **Encryption**: Cryptography library (Fernet)

## Quick Start

### Prerequisites

1. **Python 3.11+**
2. **Node.js 18+**
3. **PostgreSQL**
4. **Telegram API credentials** from [my.telegram.org](https://my.telegram.org)
5. **Facebook App credentials** from [developers.facebook.com](https://developers.facebook.com)

### Installation

1. **Clone and setup environment**:
   ```bash
   git clone <repository-url>
   cd crossmessenger
   cp .env.example .env
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install frontend dependencies**:
   ```bash
   npm run install:frontend
   ```

4. **Setup PostgreSQL database**:
   ```sql
   CREATE DATABASE crossmessenger;
   CREATE USER crossmessenger WITH PASSWORD 'password';
   GRANT ALL PRIVILEGES ON DATABASE crossmessenger TO crossmessenger;
   ```

### Configuration

Edit the `.env` file with your credentials:

#### Telegram API Setup
1. Go to [my.telegram.org](https://my.telegram.org)
2. Login with your phone number
3. Go to "API Development tools"
4. Create a new application
5. Copy `api_id` and `api_hash` to your `.env` file

#### Instagram/Facebook App Setup
1. Go to [developers.facebook.com](https://developers.facebook.com)
2. Create a new app
3. Add Instagram Basic Display product
4. Configure OAuth redirect URI: `http://0.0.0.0:5000/api/auth/instagram/callback`
5. Copy App ID and App Secret to your `.env` file

#### Generate Encryption Key
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### Running the Application

1. **Start the backend**:
   ```bash
   python main.py
   ```

2. **Start the frontend** (in a new terminal):
   ```bash
   npm run dev:frontend
   ```

3. **Access the application**:
   - Frontend: http://0.0.0.0:3000
   - Backend API: http://0.0.0.0:5000
   - API Documentation: http://0.0.0.0:5000/docs

## Usage Guide

### 1. Account Registration
- Register a new account with email and password
- Login to access the dashboard

### 2. Connect Telegram
- Click "Connect Account" → "Telegram"
- Enter your phone number
- Enter the verification code sent to your Telegram app
- Your recent chats and messages will be loaded

### 3. Connect Instagram (Limited)
- Click "Connect Account" → "Instagram"
- Complete OAuth flow in the popup window
- **Note**: Instagram DM access is limited by Meta's API policies
- Mock data is shown for demonstration

### 4. Send Messages
- Select a chat from the sidebar
- Choose which connected account to send from
- Type and send messages
- Messages appear in real-time across all connected clients

## API Reference

### Authentication
```bash
# Register
curl -X POST http://0.0.0.0:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'

# Login
curl -X POST http://0.0.0.0:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'
```

### Telegram Integration
```bash
# Start Telegram auth
curl -X POST http://0.0.0.0:5000/api/auth/telegram/start \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"phone":"+1234567890"}'

# Verify code
curl -X POST http://0.0.0.0:5000/api/auth/telegram/verify \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"phone":"+1234567890","code":"12345"}'
```

### Send Message
```bash
curl -X POST http://0.0.0.0:5000/api/messages/send \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "telegram",
    "account_id": "account_id_here",
    "chat_id": "chat_id_here",
    "text": "Hello from CrossMessenger!"
  }'
```

## Development

### Project Structure
```
crossmessenger/
├── main.py                 # FastAPI application entry point
├── app/
│   ├── database.py         # Database operations
│   ├── models.py           # Pydantic models
│   ├── auth.py             # Authentication utilities
│   ├── encryption.py       # Encryption utilities
│   └── services/
│       ├── telegram_service.py    # Telegram integration
│       ├── instagram_service.py   # Instagram integration
│       └── websocket_manager.py   # WebSocket management
├── frontend/
│   ├── src/
│   │   ├── App.tsx         # Main React component
│   │   ├── components/     # React components
│   │   └── services/       # API and WebSocket services
│   └── package.json
├── tests/
│   └── test_api.py         # API tests
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
└── README.md
```

### Running Tests
```bash
pytest tests/
```

### Code Quality
```bash
# Format code
black .

# Lint
flake8 .

# Type checking
mypy .
```

## Instagram DM Limitations

**Important**: Instagram's Graph API has strict limitations on Direct Message access:

1. **Business Verification Required**: DM access requires business verification
2. **App Review Process**: Meta must approve DM permissions
3. **Limited Use Cases**: Only approved business use cases get DM access

### Current Implementation
- Uses mock data to demonstrate the interface
- OAuth flow is functional for basic Instagram API access
- Ready to integrate real DM endpoints when permissions are available

### To Enable Real Instagram DMs
1. Complete Facebook Business Verification
2. Submit App Review for `instagram_manage_messages` permission
3. Replace mock functions in `instagram_service.py` with real Graph API calls:
   ```python
   # Replace mock_send_message with:
   async def send_message(self, user_id: str, account_id: str, chat_id: str, text: str):
       async with aiohttp.ClientSession() as session:
           url = f"https://graph.instagram.com/v18.0/{chat_id}/messages"
           data = {"message": {"text": text}, "access_token": access_token}
           async with session.post(url, data=data) as resp:
               return await resp.json()
   ```

## Security Features

### Data Protection
- **Session Encryption**: All Telegram sessions encrypted with AES-256
- **Token Security**: OAuth tokens encrypted before database storage
- **Secure Headers**: HTTPS enforcement in production
- **Rate Limiting**: API endpoint protection

### Privacy Controls
- **Data Deletion**: Complete user data removal on request
- **Session Management**: Individual account disconnection
- **Audit Logging**: Optional activity tracking

### Delete User Data
```bash
curl -X DELETE http://0.0.0.0:5000/api/users/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Deployment on Replit

This project is optimized for Replit deployment:

1. **Fork this Repl**
2. **Set Environment Variables**:
   - Go to Secrets tab in Replit
   - Add all variables from `.env.example`
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   npm run install:frontend
   ```
4. **Run the Application**:
   - Backend automatically starts on port 5000
   - Frontend builds and serves via proxy

### Replit Configuration
The `.replit` file is configured to:
- Run the FastAPI backend on startup
- Proxy frontend requests
- Handle WebSocket connections
- Deploy to Replit's cloud infrastructure

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   ```bash
   # Check PostgreSQL is running
   sudo service postgresql start
   
   # Verify database exists
   psql -U crossmessenger -d crossmessenger -c "\dt"
   ```

2. **Telegram Auth Errors**
   ```bash
   # Verify API credentials
   python -c "
   import os
   from telethon import TelegramClient
   api_id = int(os.getenv('API_ID', 0))
   api_hash = os.getenv('API_HASH', '')
   print(f'API ID: {api_id}')
   print(f'API Hash: {api_hash[:10]}...')
   "
   ```

3. **Frontend Build Issues**
   ```bash
   # Clear cache and reinstall
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   npm run dev
   ```

4. **WebSocket Connection Issues**
   - Check if port 5000 is accessible
   - Verify JWT token is valid
   - Check browser console for errors

### Logs and Debugging
```bash
# Backend logs
python main.py  # Check console output

# Frontend logs
npm run dev:frontend  # Check browser console

# Database logs
sudo tail -f /var/log/postgresql/postgresql-*.log
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes and add tests
4. Run tests: `pytest`
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
1. Check the troubleshooting section
2. Search existing GitHub issues
3. Create a new issue with:
   - Environment details
   - Error messages
   - Steps to reproduce

---

**Note**: This is a prototype implementation. For production use, additional security hardening, error handling, and scalability considerations are recommended.
