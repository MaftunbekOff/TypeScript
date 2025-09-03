
import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

client = TestClient(app)

def test_health_check():
    """Test that the API is running"""
    # Since we don't have a health endpoint, test the docs
    response = client.get("/docs")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_register_user():
    """Test user registration"""
    with patch('app.database.Database.get_user_by_email', return_value=None), \
         patch('app.database.Database.create_user', return_value="1"):
        
        response = client.post("/api/auth/register", json={
            "email": "test@example.com",
            "password": "testpassword123"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_telegram_start_auth():
    """Test Telegram auth start (mocked)"""
    # This test would require proper mocking of Telethon
    # For now, we just test the endpoint exists
    response = client.post("/api/auth/telegram/start", 
                          json={"phone": "+1234567890"},
                          headers={"Authorization": "Bearer fake_token"})
    
    # Should fail with 401 due to fake token, but endpoint exists
    assert response.status_code == 401

def test_api_endpoints_exist():
    """Test that all required endpoints exist"""
    endpoints = [
        "/api/auth/register",
        "/api/auth/login", 
        "/api/auth/telegram/start",
        "/api/auth/telegram/verify",
        "/api/auth/instagram/url",
        "/api/messages/send",
        "/api/chats",
        "/api/accounts"
    ]
    
    for endpoint in endpoints:
        # Just check that the endpoint doesn't return 404
        response = client.post(endpoint, json={}) if endpoint.endswith(('start', 'verify', 'send')) else client.get(endpoint)
        assert response.status_code != 404, f"Endpoint {endpoint} not found"

if __name__ == "__main__":
    pytest.main([__file__])
