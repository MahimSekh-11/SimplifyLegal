import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Hugging Face Configuration
    huggingface_api_key: str = os.getenv("HUGGINGFACE_API_KEY", "")
    
    # Application Settings
    cors_origins: list = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    
    # File Upload Limits
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: list = ["pdf", "doc", "docx", "txt"]

def get_settings():
    return Settings()