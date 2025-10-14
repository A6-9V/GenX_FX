"""
FastAPI Application for A6-9V GenX FX Trading System
Complete REST API with authentication, monitoring, and trading functionality
"""

from fastapi import FastAPI, Depends, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import os
from datetime import datetime

# Database and core imports
from api.database.connection import init_db, close_db, get_db_session
from api.models.trading import User

# Service imports
from api.services.external.namecheap import namecheap_service

# Authentication and security imports
from api.routers.auth import router as auth_router
from api.auth.dependencies import get_current_user
from api.middleware.security import SecurityMiddleware
from api.middleware.logging import LoggingMiddleware

# Monitoring and metrics
from api.utils.metrics import get_metrics_response, metrics
from api.utils.logging import logger, log_api_request, log_business_event

# Application lifecycle management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    # Startup
    logger.info("Starting A6-9V GenX FX API server")
    
    try:
        # Initialize database
        await init_db()
        logger.info("Database initialized successfully")
        
        # Initialize external services
        await namecheap_service.initialize()
        logger.info("External services initialized")
        
        # Log startup event
        log_business_event(
            "api_startup",
            "API server started successfully",
            additional_data={
                "startup_time": datetime.utcnow().isoformat(),
                "version": "1.0.0"
            }
        )
        
        yield
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    
    finally:
        # Shutdown
        logger.info("Shutting down A6-9V GenX FX API server")
        
        try:
            await close_db()
            logger.info("Database connections closed")
            
            log_business_event(
                "api_shutdown",
                "API server shutdown completed",
                additional_data={
                    "shutdown_time": datetime.utcnow().isoformat(),
                    "uptime_seconds": metrics.get_uptime_seconds()
                }
            )
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

# Create FastAPI application
app = FastAPI(
    title="A6-9V GenX FX Trading API",
    description="Advanced AI-powered Forex trading system API with ML signal generation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Security middleware
security = HTTPBearer()

# Add middleware in correct order (LIFO - Last In, First Out for middleware stack)
# CORS should be added last (processed first)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security middleware
app.add_middleware(SecurityMiddleware)

# Logging middleware
app.add_middleware(LoggingMiddleware)

# Include routers
app.include_router(auth_router)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint with database status"""
    try:
        # Test database connectivity
        async with get_db_session() as db:
            from sqlalchemy import text
            await db.execute(text("SELECT 1"))
        
        db_status = "healthy"
        
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"
    
    # Record health check in metrics
    metrics.record_http_request("GET", "/health", 200, 0.001)
    
    health_data = {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "services": {
            "database": db_status,
            "api": "healthy",
            "external_services": "healthy"
        },
        "uptime_seconds": metrics.get_uptime_seconds()
    }
    
    return health_data

# Metrics endpoint for Prometheus
@app.get("/metrics")
async def prometheus_metrics():
    """Prometheus metrics endpoint"""
    return get_metrics_response()

# Root endpoint
@app.get("/")
async def root():
    """API root endpoint with basic information"""
    return {
        "service": "A6-9V GenX FX Trading API",
        "version": "1.0.0",
        "status": "operational",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        },
        "endpoints": {
            "authentication": "/auth",
            "health": "/health",
            "metrics": "/metrics"
        },
        "organization": "A6-9V"
    }

# API information endpoint
@app.get("/api/info")
async def api_info():
    """Detailed API information"""
    return {
        "api": {
            "name": "GenX FX Trading API",
            "version": "1.0.0",
            "organization": "A6-9V",
            "description": "Advanced AI-powered Forex trading system"
        },
        "features": [
            "JWT Authentication",
            "User Management",
            "Trading Signals",
            "Risk Management",
            "Real-time Market Data",
            "AI/ML Predictions",
            "Prometheus Metrics",
            "Security Middleware",
            "Rate Limiting",
            "Structured Logging"
        ],
        "supported_exchanges": [
            "FXCM",
            "MetaTrader 4",
            "MetaTrader 5"
        ],
        "supported_currencies": [
            "EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF",
            "AUD/USD", "USD/CAD", "NZD/USD", "EUR/GBP",
            "EUR/JPY", "GBP/JPY", "CHF/JPY", "CAD/JPY"
        ],
        "system_info": {
            "uptime_seconds": metrics.get_uptime_seconds(),
            "environment": os.getenv("ENVIRONMENT", "development")
        }
    }

# Protected endpoint example
@app.get("/api/profile")
async def get_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile (protected endpoint)"""
    log_api_request(
        "profile_access",
        user_id=str(current_user.id),
        username=current_user.username
    )
    
    return {
        "user": {
            "id": str(current_user.id),
            "username": current_user.username,
            "email": current_user.email,
            "status": current_user.status.value,
            "verified": current_user.is_verified,
            "can_trade": current_user.can_trade,
            "risk_level": current_user.risk_level,
            "created_at": current_user.created_at.isoformat(),
            "last_login": current_user.last_login.isoformat() if current_user.last_login else None
        },
        "permissions": {
            "trading": current_user.can_trade,
            "withdrawal": current_user.can_withdraw,
            "two_factor": current_user.two_factor_enabled
        }
    }

# Development/testing endpoints (remove in production)
if os.getenv("ENVIRONMENT") == "development":
    
    @app.get("/api/dev/test-auth")
    async def test_auth_endpoint(current_user: User = Depends(get_current_user)):
        """Development endpoint to test authentication"""
        return {
            "message": "Authentication successful",
            "user_id": str(current_user.id),
            "username": current_user.username,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @app.get("/api/dev/test-metrics")
    async def test_metrics():
        """Development endpoint to test metrics collection"""
        # Record some test metrics
        metrics.record_http_request("GET", "/api/dev/test-metrics", 200, 0.05)
        metrics.record_auth_event("test", True, "access")
        metrics.update_active_sessions(5)
        
        return {
            "message": "Test metrics recorded",
            "uptime": metrics.get_uptime_seconds()
        }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler"""
    # Record error metrics
    metrics.record_error(
        error_type="http_exception",
        severity="medium" if exc.status_code >= 400 else "low",
        component="api"
    )
    
    return {
        "error": {
            "status_code": exc.status_code,
            "detail": exc.detail,
            "timestamp": datetime.utcnow().isoformat()
        }
    }

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    
    # Record error metrics
    metrics.record_error(
        error_type="unhandled_exception",
        severity="high",
        component="api"
    )
    
    return {
        "error": {
            "status_code": 500,
            "detail": "Internal server error",
            "timestamp": datetime.utcnow().isoformat()
        }
    }

# Startup event logging
@app.on_event("startup")
async def startup_event():
    """Log startup completion"""
    logger.info("A6-9V GenX FX API startup completed successfully")

if __name__ == "__main__":
    import uvicorn
    
    # Development server
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8080)),
        reload=True,
        log_level="info"
    )