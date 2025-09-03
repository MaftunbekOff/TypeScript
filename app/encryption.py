
from cryptography.fernet import Fernet
import os
import base64

# Get encryption key from environment
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    # Generate a key for development
    ENCRYPTION_KEY = Fernet.generate_key().decode()
    print(f"Generated encryption key: {ENCRYPTION_KEY}")
    print("Add this to your .env file as ENCRYPTION_KEY")

fernet = Fernet(ENCRYPTION_KEY.encode() if isinstance(ENCRYPTION_KEY, str) else ENCRYPTION_KEY)

def encrypt_data(data: str) -> str:
    """Encrypt sensitive data like session tokens"""
    encrypted = fernet.encrypt(data.encode())
    return base64.b64encode(encrypted).decode()

def decrypt_data(encrypted_data: str) -> str:
    """Decrypt sensitive data"""
    decoded = base64.b64decode(encrypted_data.encode())
    decrypted = fernet.decrypt(decoded)
    return decrypted.decode()
