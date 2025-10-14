"""
Database models for A6-9V GenX FX trading platform
"""
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Optional

from sqlalchemy import (
    Column, Integer, String, DateTime, Numeric, Boolean, Text, 
    ForeignKey, Index, UniqueConstraint, CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from api.database.connection import Base

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"

class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"

class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"

class OrderStatus(str, Enum):
    PENDING = "pending"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

class User(Base):
    """User account model"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    
    # Account status and verification
    status = Column(String(20), nullable=False, default=UserStatus.PENDING)
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Trading permissions
    can_trade = Column(Boolean, default=False)
    can_withdraw = Column(Boolean, default=False)
    risk_level = Column(String(20), default="low")  # low, medium, high
    
    # Account settings
    api_key_hash = Column(String(255))
    two_factor_enabled = Column(Boolean, default=False)
    settings = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login = Column(DateTime(timezone=True))
    
    # Relationships
    accounts = relationship("Account", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('ix_users_status_active', 'status', 'is_active'),
    )

class TradingPair(Base):
    """Trading pair model (e.g., EUR/USD, BTC/USD)"""
    __tablename__ = "trading_pairs"
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), unique=True, nullable=False, index=True)  # EUR/USD
    base_currency = Column(String(10), nullable=False)  # EUR
    quote_currency = Column(String(10), nullable=False)  # USD
    
    # Trading specifications
    min_order_size = Column(Numeric(18, 8), nullable=False, default=0.01)
    max_order_size = Column(Numeric(18, 8), nullable=False, default=1000000)
    tick_size = Column(Numeric(18, 8), nullable=False, default=0.00001)
    
    # Status and settings
    is_active = Column(Boolean, default=True)
    is_tradable = Column(Boolean, default=True)
    leverage_available = Column(Boolean, default=True)
    max_leverage = Column(Integer, default=100)
    
    # Market data settings
    price_precision = Column(Integer, default=5)
    quantity_precision = Column(Integer, default=2)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    market_data = relationship("MarketData", back_populates="trading_pair", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="trading_pair")

class Account(Base):
    """User trading account model"""
    __tablename__ = "accounts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Account details
    account_number = Column(String(50), unique=True, nullable=False, index=True)
    account_type = Column(String(20), nullable=False, default="demo")  # demo, live, paper
    currency = Column(String(10), nullable=False, default="USD")
    
    # Balance information
    balance = Column(Numeric(18, 2), nullable=False, default=0.00)
    equity = Column(Numeric(18, 2), nullable=False, default=0.00)
    margin_used = Column(Numeric(18, 2), nullable=False, default=0.00)
    margin_available = Column(Numeric(18, 2), nullable=False, default=0.00)
    
    # Trading settings
    leverage = Column(Integer, default=1)
    margin_call_level = Column(Numeric(5, 2), default=50.00)
    stop_out_level = Column(Numeric(5, 2), default=20.00)
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_locked = Column(Boolean, default=False)
    
    # MT5 Integration
    mt5_login = Column(String(50))
    mt5_server = Column(String(100))
    mt5_password_hash = Column(String(255))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="accounts")
    orders = relationship("Order", back_populates="account")
    positions = relationship("Position", back_populates="account")
    
    __table_args__ = (
        Index('ix_accounts_user_type', 'user_id', 'account_type'),
        CheckConstraint('balance >= 0', name='ck_accounts_balance_positive'),
    )

class MarketData(Base):
    """Market data/price history model"""
    __tablename__ = "market_data"
    
    id = Column(Integer, primary_key=True)
    trading_pair_id = Column(Integer, ForeignKey("trading_pairs.id"), nullable=False)
    
    # Price data
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    open_price = Column(Numeric(18, 8), nullable=False)
    high_price = Column(Numeric(18, 8), nullable=False)
    low_price = Column(Numeric(18, 8), nullable=False)
    close_price = Column(Numeric(18, 8), nullable=False)
    volume = Column(Numeric(18, 2), nullable=False, default=0)
    
    # Additional data
    bid = Column(Numeric(18, 8))
    ask = Column(Numeric(18, 8))
    spread = Column(Numeric(18, 8))
    tick_volume = Column(Integer, default=0)
    
    # Timeframe indicator
    timeframe = Column(String(10), nullable=False, default="1M")  # 1M, 5M, 15M, 1H, 4H, 1D
    
    # Data source
    source = Column(String(50), default="internal")
    
    # Relationships
    trading_pair = relationship("TradingPair", back_populates="market_data")
    
    __table_args__ = (
        Index('ix_market_data_pair_time', 'trading_pair_id', 'timestamp', 'timeframe'),
        UniqueConstraint('trading_pair_id', 'timestamp', 'timeframe', name='uq_market_data_unique'),
    )

class Order(Base):
    """Trading order model"""
    __tablename__ = "orders"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    trading_pair_id = Column(Integer, ForeignKey("trading_pairs.id"), nullable=False)
    
    # Order identification
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    client_order_id = Column(String(100))
    mt5_ticket = Column(Integer)
    
    # Order details
    order_type = Column(String(20), nullable=False)  # market, limit, stop, stop_limit
    side = Column(String(10), nullable=False)  # buy, sell
    quantity = Column(Numeric(18, 8), nullable=False)
    price = Column(Numeric(18, 8))
    stop_price = Column(Numeric(18, 8))
    
    # Execution details
    filled_quantity = Column(Numeric(18, 8), nullable=False, default=0)
    avg_fill_price = Column(Numeric(18, 8))
    status = Column(String(20), nullable=False, default=OrderStatus.PENDING)
    
    # Risk management
    stop_loss = Column(Numeric(18, 8))
    take_profit = Column(Numeric(18, 8))
    
    # Timing
    time_in_force = Column(String(10), default="GTC")  # GTC, IOC, FOK, DAY
    expires_at = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    filled_at = Column(DateTime(timezone=True))
    cancelled_at = Column(DateTime(timezone=True))
    
    # Additional data
    commission = Column(Numeric(18, 8), default=0)
    swap = Column(Numeric(18, 8), default=0)
    notes = Column(Text)
    order_metadata = Column(JSON, default=dict)
    
    # Relationships
    user = relationship("User", back_populates="orders")
    account = relationship("Account", back_populates="orders")
    trading_pair = relationship("TradingPair", back_populates="orders")
    position = relationship("Position", back_populates="order", uselist=False)
    
    __table_args__ = (
        Index('ix_orders_user_status', 'user_id', 'status'),
        Index('ix_orders_account_status', 'account_id', 'status'),
        Index('ix_orders_pair_status', 'trading_pair_id', 'status'),
        CheckConstraint('quantity > 0', name='ck_orders_quantity_positive'),
    )

class Position(Base):
    """Trading position model"""
    __tablename__ = "positions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"))
    trading_pair_id = Column(Integer, ForeignKey("trading_pairs.id"), nullable=False)
    
    # Position identification
    position_number = Column(String(50), unique=True, nullable=False, index=True)
    mt5_ticket = Column(Integer)
    
    # Position details
    side = Column(String(10), nullable=False)  # buy, sell
    quantity = Column(Numeric(18, 8), nullable=False)
    entry_price = Column(Numeric(18, 8), nullable=False)
    current_price = Column(Numeric(18, 8))
    
    # Risk management
    stop_loss = Column(Numeric(18, 8))
    take_profit = Column(Numeric(18, 8))
    
    # P&L calculation
    unrealized_pnl = Column(Numeric(18, 2), default=0)
    realized_pnl = Column(Numeric(18, 2), default=0)
    commission = Column(Numeric(18, 8), default=0)
    swap = Column(Numeric(18, 8), default=0)
    
    # Position status
    is_open = Column(Boolean, default=True)
    
    # Timestamps
    opened_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    closed_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Additional data
    position_metadata = Column(JSON, default=dict)
    
    # Relationships
    account = relationship("Account", back_populates="positions")
    order = relationship("Order", back_populates="position")
    trading_pair = relationship("TradingPair")
    
    __table_args__ = (
        Index('ix_positions_account_open', 'account_id', 'is_open'),
        Index('ix_positions_pair_open', 'trading_pair_id', 'is_open'),
        CheckConstraint('quantity > 0', name='ck_positions_quantity_positive'),
    )

class MLPrediction(Base):
    """ML model predictions storage"""
    __tablename__ = "ml_predictions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trading_pair_id = Column(Integer, ForeignKey("trading_pairs.id"), nullable=False)
    
    # Prediction details
    model_name = Column(String(100), nullable=False)
    model_version = Column(String(20), nullable=False)
    prediction_type = Column(String(50), nullable=False)  # price, direction, volatility
    timeframe = Column(String(10), nullable=False)  # 1H, 4H, 1D
    
    # Prediction data
    predicted_value = Column(Numeric(18, 8))
    confidence_score = Column(Numeric(5, 4))  # 0.0 to 1.0
    prediction_data = Column(JSON)  # Full prediction details
    
    # Input features
    features_used = Column(JSON)
    market_conditions = Column(JSON)
    
    # Validation
    actual_value = Column(Numeric(18, 8))
    accuracy = Column(Numeric(5, 4))
    validated = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    prediction_for = Column(DateTime(timezone=True), nullable=False)
    validated_at = Column(DateTime(timezone=True))
    
    __table_args__ = (
        Index('ix_predictions_pair_model', 'trading_pair_id', 'model_name'),
        Index('ix_predictions_timeframe', 'timeframe', 'created_at'),
    )