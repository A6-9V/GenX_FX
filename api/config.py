from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional
import os

class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env",
        extra="ignore"  # Allow extra fields in .env file
    )
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "GenX-EA Trading Platform"
    VERSION: str = "2.0.0"
    DESCRIPTION: str = "Advanced AI-powered trading platform with real-time market analysis"
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/trading_db"
    MONGODB_URL: str = "mongodb://localhost:27017/trading_db"
    
    # Redis for caching
    REDIS_URL: str = "redis://localhost:6379"
    
    # AI Model Configuration
    MODEL_PATH: str = "ai_models/market_predictor.joblib"
    ENSEMBLE_MODEL_PATH: str = "ai_models/ensemble_model.joblib"
    
    # Trading Configuration
    DEFAULT_SYMBOL: str = "BTCUSDT" # Pydantic will automatically use the env var if present
    MAX_POSITION_SIZE: float = 0.1
    RISK_PERCENTAGE: float = 0.02
    
    # External APIs
    BYBIT_API_KEY: Optional[str] = None
    BYBIT_API_SECRET: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    NEWS_API_KEY: Optional[str] = None
    NEWSDATA_API_KEY: Optional[str] = None
    ALPHAVANTAGE_API_KEY: Optional[str] = None
    FINNHUB_API_KEY: Optional[str] = None
    
    # Social Media APIs
    REDDIT_CLIENT_ID: Optional[str] = None
    REDDIT_CLIENT_SECRET: Optional[str] = None
    REDDIT_USERNAME: Optional[str] = None
    REDDIT_PASSWORD: Optional[str] = None
    REDDIT_USER_AGENT: Optional[str] = None
    
    # Notification Services
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_USER_ID: Optional[str] = None
    GMAIL_USER: Optional[str] = None
    GMAIL_PASSWORD: Optional[str] = None
    GMAIL_APP_API_KEY: Optional[str] = None
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    JWT_SECRET_KEY: Optional[str] = None
    CRYPTION_KEY: Optional[str] = None
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Logging
    LOG_LEVEL: str = "INFO"

settings = Settings()
