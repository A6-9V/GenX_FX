"""
A6-9V GenX FX Database Models

This module contains all database models for the trading platform.
"""

from api.models.trading import (
    User, UserStatus,
    TradingPair,
    Account,
    MarketData,
    Order, OrderType, OrderSide, OrderStatus,
    Position,
    MLPrediction
)

# Import the Base for external use
from api.database.connection import Base

# List of all models for easy reference
__all__ = [
    'Base',
    'User',
    'UserStatus', 
    'TradingPair',
    'Account',
    'MarketData',
    'Order',
    'OrderType',
    'OrderSide', 
    'OrderStatus',
    'Position',
    'MLPrediction',
]

# Model registry for migrations and admin
MODELS = [
    User,
    TradingPair,
    Account,
    MarketData,
    Order,
    Position,
    MLPrediction,
]
