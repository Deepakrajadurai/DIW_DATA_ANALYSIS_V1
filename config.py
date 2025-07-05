import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    # API Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./dashboard.db")
    DATABASE_PATH: str = "./dashboard.db"
    
    # Application Configuration
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # File Upload Configuration
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS: set = {".pdf"}
    UPLOAD_DIR: Path = Path("uploads")
    
    # AI Configuration
    AI_MODEL: str = "gemini-2.5-flash"
    MAX_TOKENS: int = 8192
    
    def __init__(self):
        # Create necessary directories
        self.UPLOAD_DIR.mkdir(exist_ok=True)
        
        # Validate required settings
        if not self.GEMINI_API_KEY:
            print("Warning: GEMINI_API_KEY not set. AI features will be disabled.")

settings = Settings()