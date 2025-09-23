from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import logging
import uvicorn
from contextlib import asynccontextmanager
import asyncio
import os

from .config import settings
from .routers import predictions, trading, market_data, system, database
from .middleware.auth import auth_middleware
from .services.ml_service import MLService
from .services.data_service import DataService
from .services.gemini_service import GeminiService
from .services.reddit_service import RedditService
from .services.news_service import NewsService
from .services.websocket_service import WebSocketService
from .utils.logging_config import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize services
ml_service = MLService()
data_service = DataService()
gemini_service = GeminiService() if os.getenv("GEMINI_API_KEY") else None
reddit_service = RedditService() if os.getenv("REDDIT_CLIENT_ID") else None
news_service = NewsService() if os.getenv("NEWSDATA_API_KEY") or os.getenv("NEWSAPI_ORG_KEY") else None
websocket_service = WebSocketService() if os.getenv("ENABLE_WEBSOCKET_FEED", "false").lower() == "true" else None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Startup
    logger.info("Starting GenX-EA Trading Platform API...")
    
    # Initialize services
    await ml_service.initialize()
    await data_service.initialize()
    
    # Initialize optional services
    if gemini_service:
        await gemini_service.initialize()
    if reddit_service:
        await reddit_service.initialize()
    if news_service:
        await news_service.initialize()
    if websocket_service:
        await websocket_service.initialize()
    
    # Start background tasks
    asyncio.create_task(ml_service.start_model_monitoring())
    asyncio.create_task(data_service.start_data_feed())
    
    logger.info("API startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down GenX-EA Trading Platform API...")
    await ml_service.shutdown()
    await data_service.shutdown()
    
    # Shutdown optional services
    if gemini_service:
        await gemini_service.shutdown()
    if reddit_service:
        await reddit_service.shutdown()
    if news_service:
        await news_service.shutdown()
    if websocket_service:
        await websocket_service.shutdown()
    
    logger.info("API shutdown complete")

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure for production
)

# Add authentication middleware
@app.middleware("http")
async def auth_middleware_wrapper(request, call_next):
    """Wrapper for auth middleware"""
    try:
        # Skip auth for public endpoints
        public_endpoints = ["/", "/docs", "/redoc", "/openapi.json", "/health"]
        
        if request.url.path in public_endpoints:
            return await call_next(request)
        
        # For now, allow all requests (remove this in production)
        return await call_next(request)
    except Exception as e:
        logger.error(f"Auth middleware error: {str(e)}")
        return await call_next(request)

# Include routers
app.include_router(predictions.router, prefix=settings.API_V1_STR)
app.include_router(trading.router, prefix=settings.API_V1_STR)
app.include_router(market_data.router, prefix=settings.API_V1_STR)
app.include_router(system.router, prefix=settings.API_V1_STR)
app.include_router(database.router)

# Root endpoint
@app.get("/")
async def read_root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "status": "active",
        "docs": "/docs"
    }

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check ML service
        ml_status = await ml_service.health_check()
        
        # Check data service
        data_status = await data_service.health_check()
        
        return {
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z",
            "services": {
                "ml_service": ml_status,
                "data_service": data_status
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred"
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.LOG_LEVEL.lower()
    )
