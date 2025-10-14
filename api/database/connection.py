"""
Database connection and session management for A6-9V GenX FX
"""
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import asyncpg
import logging

logger = logging.getLogger(__name__)

# Create declarative base for models
Base = declarative_base()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///genxdb_fx.db")
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://") if "postgresql://" in DATABASE_URL else "sqlite+aiosqlite:///genxdb_fx.db"

# Database connection settings
DATABASE_POOL_SIZE = int(os.getenv("DATABASE_POOL_SIZE", "5"))
DATABASE_MAX_OVERFLOW = int(os.getenv("DATABASE_MAX_OVERFLOW", "10"))
DATABASE_TIMEOUT = int(os.getenv("DATABASE_TIMEOUT", "30"))

class DatabaseManager:
    """Manages database connections and sessions"""
    
    def __init__(self):
        self.engine = None
        self.async_engine = None
        self.session_factory = None
        self.async_session_factory = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize database engines and session factories"""
        try:
            # Create async engine for async operations
            self.async_engine = create_async_engine(
                ASYNC_DATABASE_URL,
                pool_size=DATABASE_POOL_SIZE,
                max_overflow=DATABASE_MAX_OVERFLOW,
                pool_timeout=DATABASE_TIMEOUT,
                echo=os.getenv("DEBUG", "false").lower() == "true"
            )
            
            # Create sync engine for migrations and admin tasks
            self.engine = create_engine(
                DATABASE_URL,
                pool_size=DATABASE_POOL_SIZE,
                max_overflow=DATABASE_MAX_OVERFLOW,
                pool_timeout=DATABASE_TIMEOUT,
                echo=os.getenv("DEBUG", "false").lower() == "true"
            )
            
            # Create session factories
            self.async_session_factory = async_sessionmaker(
                self.async_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            self.session_factory = sessionmaker(
                bind=self.engine,
                autocommit=False,
                autoflush=False
            )
            
            self._initialized = True
            logger.info("Database connections initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    async def close(self):
        """Close all database connections"""
        if self.async_engine:
            await self.async_engine.dispose()
        if self.engine:
            self.engine.dispose()
        self._initialized = False
        logger.info("Database connections closed")
    
    @asynccontextmanager
    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get async database session context manager"""
        if not self._initialized:
            await self.initialize()
        
        async with self.async_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error(f"Database session error: {e}")
                raise
            finally:
                await session.close()
    
    def get_sync_session(self) -> Session:
        """Get synchronous database session"""
        if not self._initialized:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return self.session_factory()
    
    async def health_check(self) -> dict:
        """Check database health and connectivity"""
        try:
            if not self._initialized:
                return {"status": "not_initialized", "error": "Database not initialized"}
            
            async with self.get_async_session() as session:
                from sqlalchemy import text
                result = await session.execute(text("SELECT 1"))
                result.fetchone()
                
                return {
                    "status": "healthy",
                    "database": "connected",
                    "engine": "async",
                    "pool_size": DATABASE_POOL_SIZE,
                    "url": DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else DATABASE_URL
                }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy", 
                "error": str(e),
                "database": "disconnected"
            }

# Global database manager instance
db_manager = DatabaseManager()

# Dependency function for FastAPI
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency to get database session"""
    async with db_manager.get_async_session() as session:
        yield session

# Legacy sync session for backwards compatibility
def get_db_connection():
    """Legacy function for sync database connection"""
    return db_manager.get_sync_session()

# Utility functions
async def create_tables():
    """Create all tables in the database"""
    try:
        async with db_manager.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise

async def drop_tables():
    """Drop all tables in the database (use with caution!)"""
    try:
        async with db_manager.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        logger.info("Database tables dropped successfully")
    except Exception as e:
        logger.error(f"Failed to drop database tables: {e}")
        raise

# Application startup/shutdown handlers
async def startup_database():
    """Initialize database on application startup"""
    await db_manager.initialize()
    await create_tables()

async def shutdown_database():
    """Close database connections on application shutdown"""
    await db_manager.close()

# Aliases for app.py compatibility
async def init_db():
    """Initialize database - alias for startup_database"""
    await startup_database()

async def close_db():
    """Close database - alias for shutdown_database"""
    await shutdown_database()
