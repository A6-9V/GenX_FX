
-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Trading signals table
CREATE TABLE IF NOT EXISTS trading_signals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol TEXT NOT NULL,
    signal_type TEXT NOT NULL,
    entry_price DECIMAL(10,5),
    stop_loss DECIMAL(10,5),
    take_profit DECIMAL(10,5),
    confidence DECIMAL(5,4),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Performance metrics table
CREATE TABLE IF NOT EXISTS performance_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    total_trades INTEGER,
    win_rate DECIMAL(5,4),
    profit_loss DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT NOW()
);

-- AI model predictions table
CREATE TABLE IF NOT EXISTS ai_predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol TEXT NOT NULL,
    prediction_type TEXT NOT NULL,
    confidence DECIMAL(5,4),
    prediction_data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
