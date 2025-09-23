# 🚀 GenX FX Multi-Cloud Deployment Guide

## 📋 Overview

This guide will help you deploy your GenX FX trading system across multiple cloud providers for maximum cost efficiency and reliability.

## 🎯 **Recommended Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   Database      │
│   (Vercel)      │◄──►│   (Railway)     │◄──►│   (Supabase)    │
│   FREE          │    │   $5/month      │    │   FREE          │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AI/ML         │    │   Signal        │    │   File Storage  │
│   Processing    │    │   Processing    │    │   (Oracle)      │
│   (Oracle)      │    │   (GCP Run)     │    │   FREE          │
│   FREE          │    │   $1-5/month    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 💰 **Total Cost: ~$6-10/month**

---

## 🚀 **Phase 1: Backend API (Railway) - $5/month**

### Step 1: Set up Railway Account
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Create a new project

### Step 2: Deploy Backend
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Deploy to Railway
railway up
```

### Step 3: Configure Environment Variables
In Railway dashboard, add these environment variables:
```
DATABASE_URL=your_supabase_url
REDIS_URL=your_redis_url
API_KEY=your_api_key
```

---

## 🗄️ **Phase 2: Database (Supabase) - FREE**

### Step 1: Set up Supabase
1. Go to [supabase.com](https://supabase.com)
2. Create new project
3. Get your database URL

### Step 2: Create Database Schema
```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Trading signals table
CREATE TABLE trading_signals (
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
CREATE TABLE performance_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    total_trades INTEGER,
    win_rate DECIMAL(5,4),
    profit_loss DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Step 3: Connect to Backend
Update your Railway environment variables with Supabase URL.

---

## 🤖 **Phase 3: AI/ML Processing (Oracle Cloud) - FREE**

### Step 1: Set up Oracle Cloud
1. Go to [oracle.com/cloud](https://oracle.com/cloud)
2. Sign up for free tier (2 AMD VMs, 24GB RAM)
3. Create Ubuntu instance

### Step 2: Deploy AI Services
```bash
# SSH into your Oracle instance
ssh ubuntu@your-oracle-ip

# Clone your repository
git clone https://github.com/your-username/genx-fx.git
cd genx-fx

# Run deployment script
chmod +x oracle-deploy.sh
./oracle-deploy.sh
```

### Step 3: Configure Services
The script will start:
- AI Processor (Port 8001)
- Model Server (Port 8002)
- Backtester (Port 8003)
- Redis Cache (Port 6379)

---

## ⚡ **Phase 4: Signal Processing (Google Cloud Run) - $1-5/month**

### Step 1: Set up Google Cloud
1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create new project
3. Enable Cloud Run API

### Step 2: Deploy Signal Service
```bash
# Build and deploy
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/genx-signals
gcloud run deploy genx-signals \
  --image gcr.io/YOUR_PROJECT_ID/genx-signals \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1
```

---

## 🌐 **Phase 5: Frontend (Vercel) - FREE**

### Step 1: Set up Vercel
1. Go to [vercel.com](https://vercel.com)
2. Connect your GitHub repository
3. Deploy automatically

### Step 2: Configure Frontend
Create `vercel.json`:
```json
{
  "version": 2,
  "builds": [
    {
      "src": "client/package.json",
      "use": "@vercel/static-build"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/client/$1"
    }
  ]
}
```

---

## 🔧 **Configuration Files**

### Railway Configuration (`railway.json`)
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile.railway"
  },
  "deploy": {
    "startCommand": "python main.py",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 300
  }
}
```

### Oracle Cloud Configuration (`docker-compose.oracle.yml`)
```yaml
version: '3.8'
services:
  ai-processor:
    build:
      context: .
      dockerfile: Dockerfile.oracle
    ports:
      - "8001:8000"
    environment:
      - ORACLE_CLOUD=true
```

### Google Cloud Configuration (`cloudbuild.yaml`)
```yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-f', 'Dockerfile.gcp', '-t', 'gcr.io/$PROJECT_ID/genx-signals', '.']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/genx-signals']
```

---

## 🔗 **Service Communication**

### Environment Variables for Each Service

#### Railway Backend
```bash
DATABASE_URL=postgresql://supabase_url
REDIS_URL=redis://oracle-ip:6379
AI_SERVICE_URL=http://oracle-ip:8001
SIGNAL_SERVICE_URL=https://genx-signals-xxx.run.app
```

#### Oracle AI Services
```bash
DATABASE_URL=postgresql://supabase_url
BACKEND_API_URL=https://your-railway-app.railway.app
```

#### Google Cloud Run
```bash
DATABASE_URL=postgresql://supabase_url
BACKEND_API_URL=https://your-railway-app.railway.app
AI_SERVICE_URL=http://oracle-ip:8001
```

---

## 📊 **Monitoring & Health Checks**

### Health Check Endpoints
- Railway Backend: `https://your-app.railway.app/health`
- Oracle AI: `http://oracle-ip:8001/health`
- Google Cloud Run: `https://genx-signals-xxx.run.app/health`

### Monitoring Setup
```bash
# Monitor Railway logs
railway logs

# Monitor Oracle services
docker-compose -f docker-compose.oracle.yml logs -f

# Monitor Google Cloud Run
gcloud logs tail --service=genx-signals
```

---

## 🚨 **Troubleshooting**

### Common Issues

1. **Database Connection Failed**
   - Check Supabase URL and credentials
   - Verify network connectivity

2. **AI Service Not Responding**
   - Check Oracle instance status
   - Verify Docker containers are running

3. **Signal Processing Errors**
   - Check Google Cloud Run logs
   - Verify environment variables

### Debug Commands
```bash
# Check Railway status
railway status

# Check Oracle services
docker-compose -f docker-compose.oracle.yml ps

# Check Google Cloud Run
gcloud run services describe genx-signals
```

---

## 💡 **Cost Optimization Tips**

1. **Use Oracle Cloud Free Tier** for heavy computation
2. **Supabase Free Tier** for database (500MB)
3. **Vercel Free Tier** for frontend hosting
4. **Google Cloud Run** pay-per-use for signal processing
5. **Railway** $5 plan for reliable backend

### Scaling Strategy
- Start with free tiers
- Monitor usage and costs
- Scale up only when needed
- Use auto-scaling where available

---

## 🎯 **Next Steps**

1. **Deploy Phase 1** (Railway Backend)
2. **Set up Phase 2** (Supabase Database)
3. **Configure Phase 3** (Oracle AI Processing)
4. **Deploy Phase 4** (Google Cloud Run)
5. **Launch Phase 5** (Vercel Frontend)
6. **Monitor and optimize**

This architecture gives you a robust, scalable system for under $10/month! 🚀