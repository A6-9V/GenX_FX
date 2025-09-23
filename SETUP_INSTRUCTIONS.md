# 🚀 GenX FX Setup Instructions - **LIVE DEPLOYMENT**

## 🎯 **Quick Setup Overview**
Your deployment is **ready to go live**! Just follow these 3 main steps:

1. **Railway** - Deploy Python Trading API (5 minutes)
2. **Render** - Deploy Frontend & Server (5 minutes)  
3. **Configure** - Set environment variables (5 minutes)

---

## 🚄 **STEP 1: Railway Setup (Python API)**

### **Option A: Web Dashboard (Easiest)**

1. **Go to Railway:**
   - Visit: https://railway.app/dashboard
   - Sign up/login with your GitHub account

2. **Create New Project:**
   - Click "New Project" 
   - Select "Deploy from GitHub repo"
   - Choose repository: **`Mouy-leng/GenX_FX`**
   - Select branch: **`cursor/deploy-to-multiple-environments-with-cursor-agent-1f4e`**

3. **Configure Deployment:**
   - Railway will auto-detect it's a Python project
   - **Important:** Change Docker file to: `Dockerfile.railway`
   - Set build command: `docker build -f Dockerfile.railway .`

4. **Set Environment Variables:**
   ```
   PORT=8000
   ENVIRONMENT=production
   UVICORN_HOST=0.0.0.0
   UVICORN_PORT=8000
   ```

5. **Deploy:**
   - Click "Deploy"
   - Wait 3-5 minutes for build
   - Your API will be live at: `https://genx-api.railway.app`

### **Option B: CLI (For Advanced Users)**
```bash
railway login
railway init --name "genx-fx-api"
railway up --dockerfile Dockerfile.railway
```

---

## 🎨 **STEP 2: Render Setup (Frontend & Server)**

### **Frontend Deployment:**

1. **Go to Render:**
   - Visit: https://render.com/dashboard
   - Sign up/login with GitHub account

2. **Connect Repository:**
   - Click "New +" → "Web Service"
   - Connect GitHub → Select `Mouy-leng/GenX_FX`
   - Branch: `cursor/deploy-to-multiple-environments-with-cursor-agent-1f4e`

3. **Configure Frontend Service:**
   ```
   Name: genx-frontend
   Environment: Static Site
   Build Command: npm run build
   Publish Directory: ./dist
   ```

4. **Environment Variables (Frontend):**
   ```
   VITE_API_BASE_URL=https://genx-api.railway.app
   NODE_ENV=production
   ```

### **Node.js Server Deployment:**

1. **Create Second Service:**
   - Click "New +" → "Web Service"
   - Same repository: `Mouy-leng/GenX_FX`

2. **Configure Server Service:**
   ```
   Name: genx-server
   Environment: Node
   Build Command: npm run build
   Start Command: npm run start
   ```

3. **Environment Variables (Server):**
   ```
   NODE_ENV=production
   PORT=10000
   API_BASE_URL=https://genx-api.railway.app
   ```

### **Database Setup:**

1. **Add PostgreSQL:**
   - In Render dashboard → "New +" → "PostgreSQL"
   - Name: `genx-postgres`
   - Copy the connection URL

2. **Update Server Environment:**
   ```
   DATABASE_URL=<paste_postgresql_url_here>
   ```

---

## ☁️ **STEP 3: Google VM Coordination**

Your Google VM is already running some parts. Here's how to coordinate:

### **Current Setup:**
- **Google VM**: Heavy ML training, backtesting
- **Railway**: Live API, signal generation  
- **Render**: Frontend dashboard, user interface

### **VM Configuration:**
1. **Update VM to communicate with Railway API:**
   ```bash
   # On your Google VM
   export API_BASE_URL="https://genx-api.railway.app"
   export ENVIRONMENT="production"
   ```

2. **Install coordination scripts:**
   ```bash
   # Copy these files to your VM
   scp deploy_orchestrator.py your-vm:~/
   scp deployment_config.json your-vm:~/
   ```

---

## 🔧 **Environment Variables Summary**

### **Railway (API)** 
```bash
PORT=8000
ENVIRONMENT=production
UVICORN_HOST=0.0.0.0
UVICORN_PORT=8000
DATABASE_URL=<railway_database_url>
API_SECRET_KEY=your_secret_key_here
```

### **Render Frontend**
```bash
VITE_API_BASE_URL=https://genx-api.railway.app
NODE_ENV=production
```

### **Render Server**
```bash
NODE_ENV=production
PORT=10000
API_BASE_URL=https://genx-api.railway.app
DATABASE_URL=<render_postgres_url>
```

---

## 🔍 **Testing Your Deployment**

After setup, test these URLs:

```bash
# API Health Check
curl https://genx-api.railway.app/health

# Frontend (should load React app)
https://genx-frontend.onrender.com

# Server Status
curl https://genx-server.onrender.com/api/status
```

---

## 🚨 **Do You Need API Tokens?**

**NO** - Here's what authentication is required:

| Platform | Authentication Method | API Token Needed? |
|----------|----------------------|-------------------|
| **Railway** | GitHub OAuth | ❌ No |
| **Render** | GitHub OAuth | ❌ No |  
| **Google VM** | SSH Key | ❌ No (already setup) |

**All platforms use GitHub OAuth** - just login with your GitHub account!

---

## ⚡ **Quick Start (If You Want to Deploy RIGHT NOW)**

1. **Open these links in new tabs:**
   - Railway: https://railway.app/dashboard
   - Render: https://render.com/dashboard

2. **Railway Setup (2 minutes):**
   - Login → New Project → GitHub repo: `Mouy-leng/GenX_FX`
   - Use `Dockerfile.railway` → Deploy

3. **Render Setup (3 minutes):**
   - Login → New Web Service → Same repo
   - Create 2 services: frontend (static) + server (node)
   - Add PostgreSQL database

4. **Set Environment Variables** (from tables above)

5. **Test URLs** (from testing section above)

---

## 🆘 **Need Help?**

**Check these files for detailed guidance:**
- `deploy_live.sh` - Interactive deployment script
- `DEPLOYMENT_STATUS.md` - Complete deployment documentation  
- `deployment_report.md` - Deployment execution logs

**Common Issues:**
- Build failures → Check `Dockerfile.railway` syntax
- API not responding → Verify environment variables
- Frontend not loading → Check `VITE_API_BASE_URL`

---

## 🎯 **Expected Timeline**

- **Railway Setup**: 5 minutes
- **Render Setup**: 5 minutes  
- **Environment Config**: 5 minutes
- **Testing & Verification**: 5 minutes

**Total Time: ~20 minutes to full deployment! 🚀**

Your trading system will be **live across 3 platforms** with full coordination!