import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration class"""

    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = os.getenv("FLASK_DEBUG", "True") == "True"

    # Supabase
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

    # Upload Configuration
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 10485760))  # 10MB
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

    # CORS
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

    # LLM Configuration (Phase 5)
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", None)  # openai, anthropic, groq
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", None)
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", None)
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", None)
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4")
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "1000"))

    @staticmethod
    def validate():
        """Validate required environment variables"""
        required = ["SUPABASE_URL", "SUPABASE_KEY"]
        missing = [var for var in required if not os.getenv(var)]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")


class DevelopmentConfig(Config):
    """Development configuration"""

    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""

    DEBUG = False
    FLASK_ENV = "production"


# Configuration dictionary
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
