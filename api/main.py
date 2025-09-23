"""
FastAPI application for the GenX Trading Platform
"""

import logging
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional

# Import schemas and services
from .models.schemas import (
    SystemStatus, TradeSignal, OrderRequest, OrderResponse, PortfolioStatus,
    PredictionResponse, MarketData
)
from .services.trading_service import TradingService
from .services.ml_service import MLService
from .services.data_service import DataService
from .utils.auth import get_current_user

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- FastAPI App Initialization ---

app = FastAPI(
    title="GenX Trading Platform API",
    description="A modern, high-performance API for AI-powered trading.",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Service Instantiation ---

trading_service = TradingService()
ml_service = MLService()
data_service = DataService()

# --- API Endpoints ---

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Initializing API services...")
    await trading_service.initialize()
    await ml_service.initialize()
    await data_service.initialize()
    logger.info("API services initialized.")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown services gracefully"""
    logger.info("Shutting down API services...")
    await ml_service.shutdown()
    logger.info("API services shut down.")


# --- System Endpoints ---

@app.get("/", tags=["System"])
async def root():
    """Root endpoint with basic API information."""
    return {
        "message": "Welcome to the GenX Trading Platform API",
        "version": app.version,
        "docs_url": "/docs"
    }

@app.get("/health", response_model=SystemStatus, tags=["System"])
async def health_check():
    """Provides a detailed health check of the API and its services."""
    return SystemStatus(
        api_status="healthy",
        database_status="connected",  # This would be checked by a data service
        model_status=await ml_service.health_check(),
        trading_enabled=True, # This would come from config
    )


# --- Trading Endpoints ---

@app.get("/trading/signals", response_model=List[TradeSignal], tags=["Trading"])
async def get_trading_signals(symbol: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    """Get active trading signals."""
    return await trading_service.get_active_signals(symbol)

@app.post("/trading/orders", response_model=OrderResponse, tags=["Trading"])
async def place_order(order_request: OrderRequest, current_user: dict = Depends(get_current_user)):
    """Place a new trading order."""
    return await trading_service.place_order(order_request)

@app.get("/trading/orders/{order_id}", response_model=OrderResponse, tags=["Trading"])
async def get_order(order_id: str, current_user: dict = Depends(get_current_user)):
    """Get details of a specific order."""
    order = await trading_service.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.delete("/trading/orders/{order_id}", tags=["Trading"])
async def cancel_order(order_id: str, current_user: dict = Depends(get_current_user)):
    """Cancel an existing order."""
    success = await trading_service.cancel_order(order_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to cancel order")
    return {"message": "Order cancelled successfully"}

@app.get("/trading/portfolio", response_model=PortfolioStatus, tags=["Trading"])
async def get_portfolio(current_user: dict = Depends(get_current_user)):
    """Get the current portfolio status."""
    return await trading_service.get_portfolio_status()


# --- Machine Learning Endpoints ---

@app.post("/ml/predict/{symbol}", response_model=PredictionResponse, tags=["Machine Learning"])
async def get_prediction(symbol: str, current_user: dict = Depends(get_current_user)):
    """Get a prediction for a given symbol."""
    # In a real app, you'd pass real market data
    market_data = await data_service.get_market_data(symbol)
    if not market_data:
        raise HTTPException(status_code=404, detail="Market data not found for symbol")
        
    prediction = await ml_service.predict(symbol, market_data)
    return PredictionResponse(**prediction)

@app.get("/ml/metrics", tags=["Machine Learning"])
async def get_ml_metrics(current_user: dict = Depends(get_current_user)):
    """Get performance metrics for the ML models."""
    return await ml_service.get_model_metrics()


# --- Data Endpoints ---

@app.get("/data/market/{symbol}", response_model=MarketData, tags=["Data"])
async def get_market_data(symbol: str, current_user: dict = Depends(get_current_user)):
    """Get market data for a given symbol."""
    data = await data_service.get_market_data(symbol)
    if not data:
        raise HTTPException(status_code=404, detail="Market data not found")
    return data

# --- Main execution ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
