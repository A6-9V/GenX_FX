from fastapi import FastAPI, Request, status, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from contextlib import asynccontextmanager
import sqlite3
import os
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel
from jose import JWTError, jwt
from passlib.context import CryptContext

from api.services.ml_service import MLService
from api.routers import communication
from api.database.connection import (
    db_manager,
    startup_database,
    shutdown_database,
    get_db_session,
)
from api.models import Base, User, TradingPair, Account
from sqlalchemy.ext.asyncio import AsyncSession
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Auth Config
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-genx-fx-2025")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    return token_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("Starting A6-9V GenX FX API...")
    try:
        await startup_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down A6-9V GenX FX API...")
    await shutdown_database()
    logger.info("Database connections closed")


app = FastAPI(
    title="GenX-FX Trading Platform API",
    description="Trading platform with ML-powered predictions and multi-agent communication",
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Include the communication router
app.include_router(
    communication.router, prefix="/communication", tags=["communication"]
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body},
    )


@app.get("/")
async def root():
    return {
        "message": "GenX-FX Trading Platform API",
        "version": "1.0.0",
        "status": "active",
        "docs": "/docs",
        "github": "Mouy-leng",
        "repository": "https://github.com/A6-9V/GenX_FX",
    }


@app.get("/health")
async def health_check():
    """Enhanced health check with database manager"""
    db_health = await db_manager.health_check()

    overall_status = "healthy" if db_health.get("status") == "healthy" else "unhealthy"

    return {
        "status": overall_status,
        "timestamp": datetime.now().isoformat(),
        "version": "1.1.0",
        "environment": os.getenv("APP_ENV", "development"),
        "services": {
            "api": "active",
            "ml_service": "active",
            "database": db_health,
            "cache": "not_configured",  # TODO: Add Redis health check
        },
    }


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # Mock authentication for now, accepting any username/password
    # In production, verify against DB
    user_authenticated = True
    if not user_authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/api/v1/health")
async def api_health_check():
    return {
        "status": "healthy",
        "services": {"ml_service": "active", "data_service": "active"},
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/api/v1/predictions", dependencies=[Depends(get_current_user)])
async def get_predictions():
    return {
        "predictions": [],
        "status": "ready",
        "timestamp": datetime.now().isoformat(),
    }


@app.post("/api/v1/predictions/", dependencies=[Depends(get_current_user)])
async def post_predictions(request: Request):
    try:
        data = await request.json()
        if not data:
            return JSONResponse(
                status_code=400, content={"detail": "Empty JSON body received"}
            )
        return {"status": "received", "data": data}
    except Exception:
        return JSONResponse(status_code=400, content={"detail": "Malformed JSON"})


@app.post("/api/v1/predictions/predict", dependencies=[Depends(get_current_user)])
async def predict(request: Request):
    data = await request.json()
    service = MLService()
    await service.initialize()
    symbol = data.get("symbol", "")
    prediction = await service.predict(symbol, data)
    await service.shutdown()
    return JSONResponse(status_code=200, content=prediction)


@app.post("/api/v1/market-data/")
async def market_data(request: Request):
    data = await request.json()
    # Basic security check for SQL injection keywords
    payload_str = str(data).lower()
    if (
        "drop table" in payload_str
        or "' or '" in payload_str
        or "delete from" in payload_str
    ):
        return JSONResponse(
            status_code=400, content={"error": "Malicious payload detected"}
        )
    return {"status": "received", "data": data}


def get_db_connection():
    conn = sqlite3.connect("genxdb_fx.db")
    conn.row_factory = sqlite3.Row
    return conn


def initialize_market_data_table():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS market_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        timestamp DATETIME NOT NULL,
        open_price REAL,
        high_price REAL,
        low_price REAL,
        close_price REAL,
        volume REAL
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS trading_pairs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL UNIQUE,
        base_currency TEXT NOT NULL,
        quote_currency TEXT NOT NULL,
        is_active BOOLEAN NOT NULL CHECK (is_active IN (0, 1))
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        is_active BOOLEAN NOT NULL CHECK (is_active IN (0, 1))
    );
    """)

    # Check if there's any data
    cursor.execute("SELECT COUNT(*) FROM market_data")
    count = cursor.fetchone()[0]

    # Insert sample data if the table is empty
    if count == 0:
        sample_data = [
            (
                "EUR/USD",
                datetime.now() - timedelta(minutes=10),
                1.0550,
                1.0560,
                1.0540,
                1.0555,
                1000,
            ),
            (
                "EUR/USD",
                datetime.now() - timedelta(hours=1),
                1.0555,
                1.0575,
                1.0550,
                1.0570,
                1200,
            ),
            (
                "EUR/USD",
                datetime.now() - timedelta(hours=2),
                1.0570,
                1.0580,
                1.0565,
                1.0575,
                1100,
            ),
            (
                "EUR/USD",
                datetime.now() - timedelta(days=1),
                1.0500,
                1.0520,
                1.0490,
                1.0510,
                2500,
            ),
            (
                "GBP/USD",
                datetime.now() - timedelta(minutes=30),
                1.2150,
                1.2160,
                1.2140,
                1.2155,
                800,
            ),
        ]
        cursor.executemany(
            """
        INSERT INTO market_data (symbol, timestamp, open_price, high_price, low_price, close_price, volume)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            sample_data,
        )

    cursor.execute("SELECT COUNT(*) FROM trading_pairs")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO trading_pairs (symbol, base_currency, quote_currency, is_active) VALUES (?, ?, ?, ?)",
            ("EUR/USD", "EUR", "USD", 1),
        )

    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO users (username, email, is_active) VALUES (?, ?, ?)",
            ("testuser", "test@example.com", 1),
        )

    conn.commit()
    conn.close()


# Initialize the table on startup
initialize_market_data_table()


@app.get("/api/v1/market-data/{symbol:path}/{timeframe}")
async def get_historical_market_data(symbol: str, timeframe: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    time_delta = None
    if timeframe.upper() == "1H":
        time_delta = timedelta(hours=1)
    elif timeframe.upper() == "4H":
        time_delta = timedelta(hours=4)
    elif timeframe.upper() == "1D":
        time_delta = timedelta(days=1)

    if not time_delta:
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid timeframe. Use '1H', '4H', or '1D'."},
        )

    start_time = datetime.now() - time_delta

    cursor.execute(
        """
        SELECT timestamp, open_price, high_price, low_price, close_price, volume
        FROM market_data
        WHERE symbol = ? AND timestamp >= ?
        ORDER BY timestamp DESC
    """,
        (symbol, start_time),
    )

    data = cursor.fetchall()
    conn.close()

    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "data": [dict(row) for row in data],
    }


@app.get("/trading-pairs")
async def get_trading_pairs():
    try:
        conn = sqlite3.connect("genxdb_fx.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT symbol, base_currency, quote_currency FROM trading_pairs WHERE is_active = 1"
        )
        pairs = cursor.fetchall()
        conn.close()

        return {
            "trading_pairs": [
                {"symbol": pair[0], "base_currency": pair[1], "quote_currency": pair[2]}
                for pair in pairs
            ]
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/users")
async def get_users():
    try:
        conn = sqlite3.connect("genxdb_fx.db")
        cursor = conn.cursor()
        cursor.execute("SELECT username, email, is_active FROM users")
        users = cursor.fetchall()
        conn.close()

        return {
            "users": [
                {"username": user[0], "email": user[1], "is_active": bool(user[2])}
                for user in users
            ]
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/mt5-info")
async def get_mt5_info():
    return {
        "login": os.getenv("MT5_LOGIN", "default_login"),
        "server": os.getenv("MT5_SERVER", "default_server"),
        "status": "configured",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
