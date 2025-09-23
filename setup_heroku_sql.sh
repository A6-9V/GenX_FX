#!/bin/bash

# Heroku SQL Database Setup Script for AMP System
# This script will set up PostgreSQL database, migrations, and environment variables

set -e  # Exit on any error

echo "🗄️  Setting up Heroku SQL Database for AMP System..."

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI is not installed. Installing..."
    curl https://cli-assets.heroku.com/install.sh | sh
fi

# Set the Heroku API key
if [ -n "$HEROKU_TOKEN" ]; then
    echo "✅ Using provided Heroku token"
    export HEROKU_API_KEY=$HEROKU_TOKEN
else
    echo "⚠️  No HEROKU_TOKEN provided. Please set it:"
    echo "   export HEROKU_TOKEN=your-token"
    echo "   Then re-run this script"
    exit 1
fi

# Check authentication
echo "🔐 Checking Heroku authentication..."
if ! heroku auth:whoami; then
    echo "❌ Heroku authentication failed. Please check your token."
    exit 1
fi

# Get app name from user or use default
if [ -z "$HEROKU_APP_NAME" ]; then
    echo "📱 Enter your Heroku app name (or press Enter for auto-detection):"
    read -r HEROKU_APP_NAME
fi

# Auto-detect app if not provided
if [ -z "$HEROKU_APP_NAME" ]; then
    echo "🔍 Auto-detecting Heroku app..."
    HEROKU_APP_NAME=$(heroku apps | grep -E "amp-system|genx" | head -1 | awk '{print $1}')
    if [ -z "$HEROKU_APP_NAME" ]; then
        echo "❌ No suitable app found. Please create one first:"
        echo "   heroku create your-app-name"
        exit 1
    fi
fi

echo "✅ Using Heroku app: $HEROKU_APP_NAME"

# Step 1: Add PostgreSQL addon
echo "🗄️  Adding PostgreSQL database..."
heroku addons:create heroku-postgresql:mini --app $HEROKU_APP_NAME || {
    echo "⚠️  PostgreSQL addon might already exist or quota exceeded"
    echo "   Checking current addons..."
    heroku addons --app $HEROKU_APP_NAME
}

# Step 2: Get database URL
echo "🔗 Getting database URL..."
DATABASE_URL=$(heroku config:get DATABASE_URL --app $HEROKU_APP_NAME)
if [ -z "$DATABASE_URL" ]; then
    echo "❌ Failed to get DATABASE_URL"
    exit 1
fi
echo "✅ Database URL obtained"

# Step 3: Set up environment variables
echo "🌍 Setting up environment variables..."
heroku config:set NODE_ENV=production --app $HEROKU_APP_NAME
heroku config:set PYTHON_ENV=production --app $HEROKU_APP_NAME
heroku config:set LOG_LEVEL=INFO --app $HEROKU_APP_NAME
heroku config:set CORS_ORIGINS="*" --app $HEROKU_APP_NAME

# Generate a secret key
SECRET_KEY=$(openssl rand -hex 32)
heroku config:set SECRET_KEY=$SECRET_KEY --app $HEROKU_APP_NAME

# Set database-specific variables
heroku config:set DB_HOST=$(echo $DATABASE_URL | sed 's/.*@\([^:]*\):.*/\1/') --app $HEROKU_APP_NAME
heroku config:set DB_PORT=5432 --app $HEROKU_APP_NAME
heroku config:set DB_NAME=$(echo $DATABASE_URL | sed 's/.*\/\([^?]*\)?.*/\1/') --app $HEROKU_APP_NAME
heroku config:set DB_USER=$(echo $DATABASE_URL | sed 's/.*:\/\/\([^:]*\):.*/\1/') --app $HEROKU_APP_NAME
heroku config:set DB_PASSWORD=$(echo $DATABASE_URL | sed 's/.*:\/\/[^:]*:\([^@]*\)@.*/\1/') --app $HEROKU_APP_NAME

# Step 4: Create database schema file
echo "📝 Creating database schema..."
cat > shared/database_schema.sql << 'EOF'
-- AMP System Database Schema
-- This file contains the complete database schema for the AMP Trading System

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    is_admin BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Trading accounts table
CREATE TABLE IF NOT EXISTS trading_accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    account_name VARCHAR(100) NOT NULL,
    broker VARCHAR(50) NOT NULL,
    account_number VARCHAR(100),
    api_key VARCHAR(255),
    api_secret VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Trading signals table
CREATE TABLE IF NOT EXISTS trading_signals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(20) NOT NULL,
    signal_type VARCHAR(10) NOT NULL CHECK (signal_type IN ('BUY', 'SELL', 'CLOSE')),
    entry_price DECIMAL(10, 5),
    stop_loss DECIMAL(10, 5),
    take_profit DECIMAL(10, 5),
    confidence DECIMAL(3, 2) CHECK (confidence >= 0 AND confidence <= 1),
    source VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'EXECUTED', 'CANCELLED', 'EXPIRED')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    executed_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE
);

-- Trades table
CREATE TABLE IF NOT EXISTS trades (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    trading_account_id UUID REFERENCES trading_accounts(id) ON DELETE CASCADE,
    signal_id UUID REFERENCES trading_signals(id) ON DELETE SET NULL,
    symbol VARCHAR(20) NOT NULL,
    trade_type VARCHAR(10) NOT NULL CHECK (trade_type IN ('BUY', 'SELL')),
    entry_price DECIMAL(10, 5) NOT NULL,
    exit_price DECIMAL(10, 5),
    quantity DECIMAL(10, 2) NOT NULL,
    stop_loss DECIMAL(10, 5),
    take_profit DECIMAL(10, 5),
    status VARCHAR(20) DEFAULT 'OPEN' CHECK (status IN ('OPEN', 'CLOSED', 'CANCELLED')),
    pnl DECIMAL(10, 2),
    pnl_percentage DECIMAL(5, 2),
    opened_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP WITH TIME ZONE,
    notes TEXT
);

-- Market data table
CREATE TABLE IF NOT EXISTS market_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(20) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    open_price DECIMAL(10, 5) NOT NULL,
    high_price DECIMAL(10, 5) NOT NULL,
    low_price DECIMAL(10, 5) NOT NULL,
    close_price DECIMAL(10, 5) NOT NULL,
    volume DECIMAL(15, 2),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- AI predictions table
CREATE TABLE IF NOT EXISTS ai_predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(20) NOT NULL,
    prediction_type VARCHAR(50) NOT NULL,
    prediction_value DECIMAL(10, 5),
    confidence DECIMAL(3, 2) CHECK (confidence >= 0 AND confidence <= 1),
    model_name VARCHAR(100),
    features JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- System logs table
CREATE TABLE IF NOT EXISTS system_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    level VARCHAR(10) NOT NULL CHECK (level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')),
    component VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    details JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- API keys table
CREATE TABLE IF NOT EXISTS api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    key_name VARCHAR(100) NOT NULL,
    api_key VARCHAR(255) NOT NULL,
    api_secret VARCHAR(255),
    provider VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_trading_signals_symbol ON trading_signals(symbol);
CREATE INDEX IF NOT EXISTS idx_trading_signals_status ON trading_signals(status);
CREATE INDEX IF NOT EXISTS idx_trading_signals_created_at ON trading_signals(created_at);
CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol);
CREATE INDEX IF NOT EXISTS idx_trades_status ON trades(status);
CREATE INDEX IF NOT EXISTS idx_trades_opened_at ON trades(opened_at);
CREATE INDEX IF NOT EXISTS idx_market_data_symbol_timestamp ON market_data(symbol, timestamp);
CREATE INDEX IF NOT EXISTS idx_ai_predictions_symbol ON ai_predictions(symbol);
CREATE INDEX IF NOT EXISTS idx_system_logs_level_created_at ON system_logs(level, created_at);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_trading_accounts_updated_at BEFORE UPDATE ON trading_accounts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_api_keys_updated_at BEFORE UPDATE ON api_keys FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default admin user (password: admin123)
INSERT INTO users (username, email, password_hash, is_admin) 
VALUES ('admin', 'admin@amp-system.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8qQqKqG', true)
ON CONFLICT (username) DO NOTHING;

-- Insert sample trading signals
INSERT INTO trading_signals (symbol, signal_type, entry_price, stop_loss, take_profit, confidence, source, status) VALUES
('EURUSD', 'BUY', 1.0850, 1.0800, 1.0950, 0.85, 'AI_MODEL', 'PENDING'),
('GBPUSD', 'SELL', 1.2650, 1.2700, 1.2550, 0.78, 'TECHNICAL_ANALYSIS', 'PENDING'),
('USDJPY', 'BUY', 150.50, 150.00, 151.50, 0.92, 'AI_MODEL', 'PENDING')
ON CONFLICT DO NOTHING;

echo "✅ Database schema created successfully"
EOF

# Step 5: Create database migration script
echo "🔄 Creating database migration script..."
cat > scripts/migrate_database.py << 'EOF'
#!/usr/bin/env python3
"""
Database Migration Script for AMP System
This script will set up the database schema and run migrations
"""

import os
import sys
import psycopg2
import logging
from urllib.parse import urlparse

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_database_url():
    """Get database URL from environment"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        logger.error("DATABASE_URL environment variable not set")
        sys.exit(1)
    return database_url

def run_migration(database_url):
    """Run database migration"""
    try:
        # Parse database URL
        parsed_url = urlparse(database_url)
        
        # Connect to database
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        logger.info("Connected to database successfully")
        
        # Read and execute schema file
        schema_file = "shared/database_schema.sql"
        if os.path.exists(schema_file):
            with open(schema_file, 'r') as f:
                schema_sql = f.read()
            
            # Execute schema
            cursor.execute(schema_sql)
            conn.commit()
            logger.info("Database schema applied successfully")
        else:
            logger.warning(f"Schema file {schema_file} not found")
        
        # Verify tables exist
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        logger.info(f"Database tables: {[table[0] for table in tables]}")
        
        cursor.close()
        conn.close()
        
        logger.info("Database migration completed successfully")
        
    except Exception as e:
        logger.error(f"Database migration failed: {e}")
        sys.exit(1)

def main():
    """Main function"""
    logger.info("Starting database migration...")
    
    database_url = get_database_url()
    run_migration(database_url)
    
    logger.info("Migration completed successfully!")

if __name__ == "__main__":
    main()
EOF

# Step 6: Create database connection utility
echo "🔧 Creating database connection utility..."
cat > api/utils/database.py << 'EOF'
"""
Database connection utility for AMP System
Handles PostgreSQL connections and connection pooling
"""

import os
import logging
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from contextlib import contextmanager
from typing import Optional

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Database connection manager"""
    
    def __init__(self):
        self.pool: Optional[SimpleConnectionPool] = None
        self.database_url = os.getenv('DATABASE_URL')
        
    def initialize(self):
        """Initialize connection pool"""
        if not self.database_url:
            logger.error("DATABASE_URL not found in environment variables")
            return
            
        try:
            # Create connection pool
            self.pool = SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                dsn=self.database_url
            )
            logger.info("Database connection pool initialized")
        except Exception as e:
            logger.error(f"Failed to initialize database pool: {e}")
            
    def get_connection(self):
        """Get a connection from the pool"""
        if not self.pool:
            self.initialize()
        return self.pool.getconn()
        
    def return_connection(self, conn):
        """Return a connection to the pool"""
        if self.pool:
            self.pool.putconn(conn)
            
    @contextmanager
    def get_db_connection(self):
        """Context manager for database connections"""
        conn = None
        try:
            conn = self.get_connection()
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database operation failed: {e}")
            raise
        finally:
            if conn:
                self.return_connection(conn)
                
    def close(self):
        """Close the connection pool"""
        if self.pool:
            self.pool.closeall()
            logger.info("Database connection pool closed")

# Global database manager instance
db_manager = DatabaseManager()

def get_db():
    """Get database connection"""
    return db_manager.get_db_connection()

def init_database():
    """Initialize database connection"""
    db_manager.initialize()

def close_database():
    """Close database connection"""
    db_manager.close()
EOF

# Step 7: Update requirements.txt to include database dependencies
echo "📦 Adding database dependencies to requirements.txt..."
if ! grep -q "psycopg2" requirements.txt; then
    echo "psycopg2-binary==2.9.9" >> requirements.txt
fi

if ! grep -q "sqlalchemy" requirements.txt; then
    echo "sqlalchemy==2.0.23" >> requirements.txt
fi

# Step 8: Create database initialization script
echo "🚀 Creating database initialization script..."
cat > scripts/init_database.py << 'EOF'
#!/usr/bin/env python3
"""
Database Initialization Script for AMP System
This script will initialize the database and create necessary tables
"""

import os
import sys
import logging
from api.utils.database import init_database, get_db

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    """Initialize database"""
    try:
        logger.info("Initializing database...")
        init_database()
        
        # Test connection
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()
                logger.info(f"Connected to PostgreSQL: {version[0]}")
                
                # Check if tables exist
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """)
                
                tables = cursor.fetchall()
                if tables:
                    logger.info(f"Found {len(tables)} tables: {[table[0] for table in tables]}")
                else:
                    logger.warning("No tables found in database")
                    
        logger.info("Database initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        sys.exit(1)

def main():
    """Main function"""
    logger.info("Starting database initialization...")
    init_db()
    logger.info("Database initialization completed!")

if __name__ == "__main__":
    main()
EOF

# Step 9: Update Procfile to include database initialization
echo "📝 Updating Procfile for database initialization..."
cat > Procfile << 'EOF'
web: uvicorn api.main:app --host 0.0.0.0 --port $PORT
release: python scripts/migrate_database.py
EOF

# Step 10: Create database health check endpoint
echo "🏥 Creating database health check endpoint..."
cat > api/routers/database.py << 'EOF'
"""
Database health check and management endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from api.utils.database import get_db
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/database", tags=["database"])

@router.get("/health")
async def database_health():
    """Check database health"""
    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                
        return {
            "status": "healthy",
            "database": "connected",
            "message": "Database is operational"
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        raise HTTPException(status_code=503, detail="Database connection failed")

@router.get("/tables")
async def get_tables():
    """Get list of database tables"""
    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """)
                tables = cursor.fetchall()
                
        return {
            "tables": [table[0] for table in tables],
            "count": len(tables)
        }
    except Exception as e:
        logger.error(f"Failed to get tables: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve tables")

@router.post("/migrate")
async def run_migration():
    """Run database migration"""
    try:
        import subprocess
        result = subprocess.run(
            ["python", "scripts/migrate_database.py"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return {"status": "success", "message": "Migration completed successfully"}
        else:
            raise HTTPException(status_code=500, detail=f"Migration failed: {result.stderr}")
            
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise HTTPException(status_code=500, detail=f"Migration failed: {str(e)}")
EOF

# Step 11: Update main.py to include database router
echo "🔗 Adding database router to main.py..."
# This will be done manually in the next step

# Step 12: Deploy to Heroku
echo "🚀 Deploying to Heroku..."
git add .
git commit -m "Add database setup and migrations" || echo "No changes to commit"

# Push to Heroku
git push heroku main

# Step 13: Run database migration on Heroku
echo "🔄 Running database migration on Heroku..."
heroku run python scripts/migrate_database.py --app $HEROKU_APP_NAME

# Step 14: Verify deployment
echo "✅ Verifying deployment..."
heroku logs --tail --num=50 --app $HEROKU_APP_NAME

echo ""
echo "🎉 Heroku SQL Database Setup Completed!"
echo ""
echo "📊 Database Information:"
echo "   App Name: $HEROKU_APP_NAME"
echo "   Database URL: $DATABASE_URL"
echo "   Health Check: https://$HEROKU_APP_NAME.herokuapp.com/database/health"
echo ""
echo "🔧 Useful Commands:"
echo "   heroku logs --tail --app $HEROKU_APP_NAME  # View live logs"
echo "   heroku run python scripts/migrate_database.py --app $HEROKU_APP_NAME  # Run migration"
echo "   heroku config --app $HEROKU_APP_NAME  # View environment variables"
echo "   heroku pg:info --app $HEROKU_APP_NAME  # Database info"
echo ""
echo "🌐 Application URLs:"
echo "   Main App: https://$HEROKU_APP_NAME.herokuapp.com"
echo "   API Docs: https://$HEROKU_APP_NAME.herokuapp.com/docs"
echo "   Database Health: https://$HEROKU_APP_NAME.herokuapp.com/database/health"
echo ""