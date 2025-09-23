# GenX_FX Trading Platform - API Key Setup Guide

## 🚀 Complete API Key Configuration

### **Step 1: Create Environment File**

Create a `.env` file in your project root by copying the example file:

```bash
cp .env.example .env
```

Then, open the `.env` file and fill in the required values for the environment variables. The `.env.example` file contains a complete list of all the environment variables used by the application.

## 🔑 **API Key Sources & Setup Instructions**

### **1. Google Gemini AI (Required)**
- **Purpose**: Primary AI for market analysis, sentiment analysis, trading insights
- **Get API Key**: https://makersuite.google.com/app/apikey
- **Cost**: Free tier available, pay-per-use
- **Setup**: 
  ```bash
  export GEMINI_API_KEY="your-gemini-api-key-here"
  ```

### **2. Bybit Exchange (Required for Crypto Trading)**
- **Purpose**: Real-time market data and trading execution
- **Get API Key**: https://www.bybit.com/en/account/api-key
- **Setup**:
  ```bash
  export BYBIT_API_KEY="your-bybit-api-key-here"
  export BYBIT_API_SECRET="your-bybit-api-secret-here"
  ```

### **3. FXCM (Required for Forex Trading)**
- **Purpose**: Forex market data and trading
- **Get API Key**: https://www.fxcm.com/markets/forex-trading-demo/
- **Setup**:
  ```bash
  export FXCM_API_KEY="your-fxcm-api-key-here"
  export FXCM_ACCESS_TOKEN="your-fxcm-access-token-here"
  export FXCM_ACCOUNT_ID="your-fxcm-account-id-here"
  ```

### **4. News APIs (Optional but Recommended)**
- **NewsData.io**: https://newsdata.io/
- **Alpha Vantage**: https://www.alphavantage.co/support/#api-key
- **NewsAPI.org**: https://newsapi.org/
- **Finnhub**: https://finnhub.io/
- **Financial Modeling Prep**: https://financialmodelingprep.com/

### **5. Reddit API (Optional)**
- **Purpose**: Social sentiment analysis
- **Get API Key**: https://www.reddit.com/prefs/apps
- **Setup**:
  ```bash
  export REDDIT_CLIENT_ID="your-reddit-client-id-here"
  export REDDIT_CLIENT_SECRET="your-reddit-client-secret-here"
  export REDDIT_USERNAME="your-reddit-username-here"
  export REDDIT_PASSWORD="your-reddit-password-here"
  ```

### **6. Notification Services (Optional)**
- **Telegram Bot**: https://core.telegram.org/bots#how-do-i-create-a-bot
- **Discord Bot**: https://discord.com/developers/applications

## 🛠️ **Setup Script**

Create a setup script to validate your API keys:

```bash
#!/bin/bash
# setup_api_keys.sh

echo "🔧 GenX_FX API Key Setup Script"
echo "=================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please create it first."
    exit 1
fi

# Load environment variables
source .env

# Function to check API key
check_api_key() {
    local key_name=$1
    local key_value=$2
    local required=$3
    
    if [ -z "$key_value" ]; then
        if [ "$required" = "true" ]; then
            echo "❌ $key_name: MISSING (Required)"
            return 1
        else
            echo "⚠️  $key_name: Not set (Optional)"
            return 0
        fi
    else
        echo "✅ $key_name: Set"
        return 0
    fi
}

echo ""
echo "📋 API Key Status:"
echo "=================="

# Required API Keys
check_api_key "GEMINI_API_KEY" "$GEMINI_API_KEY" "true"
check_api_key "BYBIT_API_KEY" "$BYBIT_API_KEY" "true"
check_api_key "BYBIT_API_SECRET" "$BYBIT_API_SECRET" "true"

# Optional but recommended
check_api_key "FXCM_API_KEY" "$FXCM_API_KEY" "false"
check_api_key "NEWSDATA_API_KEY" "$NEWSDATA_API_KEY" "false"
check_api_key "REDDIT_CLIENT_ID" "$REDDIT_CLIENT_ID" "false"

echo ""
echo "🎯 Next Steps:"
echo "1. Configure your trading strategy in api/config.py"
echo "2. Test your API connections"
echo "3. Start the trading platform"
```

## 🧪 **Testing API Connections**

Create a test script to verify your API keys work:

```python
# test_api_keys.py
import os
import asyncio
from api.services.gemini_service import GeminiService
from api.services.news_service import NewsService
from core.execution.bybit import BybitAPI

async def test_api_connections():
    print("🧪 Testing API Connections...")
    
    # Test Gemini AI
    try:
        gemini = GeminiService()
        await gemini.initialize()
        print("✅ Gemini AI: Connected")
    except Exception as e:
        print(f"❌ Gemini AI: Failed - {e}")
    
    # Test Bybit
    try:
        bybit = BybitAPI()
        data = bybit.get_market_data("BTCUSDT", "1", 1)
        if data:
            print("✅ Bybit API: Connected")
        else:
            print("❌ Bybit API: Failed")
    except Exception as e:
        print(f"❌ Bybit API: Failed - {e}")
    
    # Test News Service
    try:
        news = NewsService()
        print("✅ News Service: Initialized")
    except Exception as e:
        print(f"❌ News Service: Failed - {e}")

if __name__ == "__main__":
    asyncio.run(test_api_connections())
```

## 🔒 **Security Best Practices**

1. **Never commit API keys to version control**
2. **Use environment variables for all sensitive data**
3. **Rotate API keys regularly**
4. **Use different API keys for development and production**
5. **Monitor API usage to avoid rate limits**

## 🚀 **Quick Start**

1. **Copy the environment template**:
   ```bash
   cp .env.example .env
   ```

2. **Fill in your API keys** in the `.env` file

3. **Test your setup**:
   ```bash
   python test_api_keys.py
   ```

4. **Start the platform**:
   ```bash
   uvicorn api.main:app --reload
   ```

## 📊 **API Key Priority Matrix**

| API Service | Priority | Purpose | Cost |
|-------------|----------|---------|------|
| **Gemini AI** | 🔴 Critical | AI-powered analysis | Free tier |
| **Bybit** | 🔴 Critical | Crypto trading | Free |
| **FXCM** | 🟡 Important | Forex trading | Free demo |
| **News APIs** | 🟢 Optional | Market sentiment | Free tiers |
| **Reddit** | 🟢 Optional | Social sentiment | Free |
| **Telegram/Discord** | 🟢 Optional | Notifications | Free |

This setup will give you a fully functional GenX_FX trading platform with AI-powered analysis, real-time market data, and automated trading capabilities! 