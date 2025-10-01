from fastapi import FastAPI, APIRouter, Response, status, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Any, Dict, List
import sqlite3
import os
import json
from datetime import datetime

STATIC_DIR = "client/dist"

app = FastAPI(
    title="GenX-FX Trading Platform API",
    description="Trading platform with ML-powered predictions",
    version="1.0.0"
)

# --- Pydantic Models ---
class PredictionRequest(BaseModel):
    symbol: str
    data: Dict | List | str

# --- Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_server_error_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except BaseException as e: # Catch BaseException to include asyncio.TimeoutError
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error", "error": str(e)},
        )

# --- API Router ---
router = APIRouter(prefix="/api")

async def get_liveness_status():
    """A dummy dependency for testing purposes."""
    return True

@router.get("/")
async def root():
    return {
        "message": "GenX-FX Trading Platform API",
        "version": "1.0.0",
        "status": "running",
        "github": "Mouy-leng",
        "repository": "https://github.com/Mouy-leng/GenX_FX.git"
    }

@router.get("/health")
async def health_check(is_live: bool = Depends(get_liveness_status)):
    return {
        "status": "healthy",
        "database": "connected", # Mocked
        "timestamp": datetime.now().isoformat()
    }


@router.get("/v1/health")
async def api_health_check():
    return {
        "status": "healthy",
        "services": {
            "ml_service": "active",
            "data_service": "active"
        },
        "timestamp": datetime.now().isoformat()
    }

@router.get("/v1/predictions")
async def get_predictions():
    return {
        "predictions": [],
        "status": "ready",
        "timestamp": datetime.now().isoformat()
    }

@router.post("/v1/predictions")
async def post_predictions(request: PredictionRequest):
    return {"status": "received", "symbol": request.symbol}


@router.get("/trading-pairs")
async def get_trading_pairs():
    return {
        "trading_pairs": [
            {"symbol": "EURUSD", "base_currency": "EUR", "quote_currency": "USD"},
            {"symbol": "BTCUSD", "base_currency": "BTC", "quote_currency": "USD"}
        ]
    }

@router.get("/users")
async def get_users():
    return {
        "users": [
            {"username": "testuser", "email": "test@example.com", "is_active": True}
        ]
    }

@router.get("/mt5-info")
async def get_mt5_info():
    return {
        "login": "279023502",
        "server": "Exness-MT5Trial8",
        "status": "configured"
    }

# Include the router in the main app
app.include_router(router)

# --- SPA Serving ---
if os.path.exists(STATIC_DIR):
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

    @app.get("/{catchall:path}", response_class=FileResponse, include_in_schema=False)
    def serve_spa(catchall: str):
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))

else:
    @app.get("/", include_in_schema=False)
    def serve_fallback_for_spa():
        return {"message": "SPA not built. Run `npm run build`."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)