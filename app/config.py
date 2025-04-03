from pathlib import Path
import os
from pydantic_settings import BaseSettings
import secrets

class Settings(BaseSettings):
    # Base directory for the project
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    
    # QR Code settings
    QR_DIRECTORY: Path = BASE_DIR / "qr_codes"
    SERVER_BASE_URL: str = os.getenv("SERVER_BASE_URL", "http://localhost:8000")
    SERVER_DOWNLOAD_FOLDER: str = "downloads"
    
    # Authentication settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Admin credentials
    ADMIN_USER: str = os.getenv("ADMIN_USER", "admin")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "admin123")

    class Config:
        env_file = ".env"

# Create settings instance
settings = Settings()

# Create QR code directory if it doesn't exist
settings.QR_DIRECTORY.mkdir(parents=True, exist_ok=True)

# Export commonly used settings
QR_DIRECTORY = settings.QR_DIRECTORY
SERVER_BASE_URL = settings.SERVER_BASE_URL
SERVER_DOWNLOAD_FOLDER = settings.SERVER_DOWNLOAD_FOLDER
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
ADMIN_USER = settings.ADMIN_USER
ADMIN_PASSWORD = settings.ADMIN_PASSWORD
