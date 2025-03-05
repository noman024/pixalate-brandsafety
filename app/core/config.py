import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """
    Application settings.
    
    These settings are loaded from environment variables and .env file.
    """
    
    # API settings
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    
    # OpenAI settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")
    
    # Image settings
    MAX_IMAGE_SIZE: int = 10 * 1024 * 1024  # 10 MB
    SUPPORTED_FORMATS: list = ["jpg", "jpeg", "png", "webp"]
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Data directory
    DATA_DIR: str = os.getenv("DATA_DIR", "data")
    
    class Config:
        env_file = ".env"

# Create a global settings object
settings = Settings()