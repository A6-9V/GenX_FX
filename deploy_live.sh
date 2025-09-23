#!/bin/bash

# GenX FX Live Deployment Script
# Automated deployment across Railway, Render, and Google VM coordination

echo "🚀 GenX FX Multi-Platform Deployment Script"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_section() {
    echo -e "\n${BLUE}📋 $1${NC}"
    echo "----------------------------------------"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_section "Deployment Architecture Overview"
echo "🏗️  This system deploys across three environments:"
echo "   🚄 Railway: Python Trading API (FastAPI)"
echo "   🎨 Render: Frontend (React) + Node.js Server"
echo "   ☁️  Google VM: ML Training & Backtesting (coordinated)"

print_section "Pre-deployment Setup"

# Check if necessary files exist
echo "🔍 Checking deployment files..."
files_to_check=("railway-deployment.json" "render.yaml" "Dockerfile.railway" "requirements-free-tier.txt")
for file in "${files_to_check[@]}"; do
    if [ -f "$file" ]; then
        print_success "Found $file"
    else
        print_error "Missing $file"
    fi
done

print_section "Railway Deployment (Python API)"
echo "🚄 Deploying to Railway..."
echo ""
echo "Railway deployment options:"
echo "Option 1 (Manual):"
echo "  1. Visit: https://railway.app"
echo "  2. Connect your GitHub repository"
echo "  3. Deploy from branch: $(git branch --show-current)"
echo "  4. Use Dockerfile: Dockerfile.railway"
echo ""
echo "Option 2 (CLI - requires login):"
echo "  railway login"
echo "  railway init"
echo "  railway up --dockerfile Dockerfile.railway"
echo ""

# Test if we can deploy via CLI
if command -v railway &> /dev/null; then
    echo "🔍 Testing Railway CLI..."
    if railway whoami &> /dev/null; then
        print_success "Railway CLI is authenticated"
        echo "🚀 Attempting Railway deployment..."
        
        # Initialize Railway project if needed
        if [ ! -d ".railway" ]; then
            railway init --name "genx-fx-api" || print_warning "Railway init failed - continuing"
        fi
        
        # Deploy to Railway
        railway up --dockerfile Dockerfile.railway && print_success "Railway deployment successful!" || print_warning "Railway deployment needs manual intervention"
    else
        print_warning "Railway CLI not authenticated - using manual deployment"
        echo "📝 Manual Railway deployment instructions:"
        echo "  1. Go to https://railway.app/dashboard"
        echo "  2. Create new project from GitHub repo"
        echo "  3. Select this repository: $(git remote get-url origin 2>/dev/null || echo 'Current repository')"
        echo "  4. Use Dockerfile: Dockerfile.railway"
        echo "  5. Set environment variables from railway-deployment.json"
    fi
else
    print_warning "Railway CLI not installed"
fi

print_section "Render Deployment (Frontend + Node.js)"
echo "🎨 Deploying to Render..."

# Push latest changes to trigger Render deployment
git add . 2>/dev/null
git commit -m "Deploy: $(date '+%Y-%m-%d %H:%M:%S')" 2>/dev/null || echo "No new changes to commit"
if git push origin HEAD 2>/dev/null; then
    print_success "Code pushed to repository"
else
    print_warning "Git push failed - ensure you have push access"
fi

echo ""
echo "Render deployment instructions:"
echo "  1. Go to https://render.com/dashboard"
echo "  2. Connect your GitHub account"
echo "  3. Import repository: $(git remote get-url origin 2>/dev/null || echo 'Current repository')"
echo "  4. Use render.yaml for blueprint deployment"
echo "  5. Services will auto-deploy from configuration"

print_section "Google VM Coordination"
echo "☁️  Coordinating with existing Google VM..."
echo ""
echo "Google VM Role: AI Training & Backtesting"
echo "- Heavy ML model training"
echo "- Historical data backtesting"  
echo "- Resource-intensive computations"
echo ""
echo "Coordination Setup:"
echo "- API Communication: Use secure endpoints"
echo "- Data Sync: Share market data via secure channels"
echo "- Load Distribution: Route heavy tasks to VM"

print_section "Environment Variables Setup"
echo "🔧 Environment variables needed:"
echo ""
echo "Railway (Python API):"
cat << 'EOF'
  PORT=8000
  ENVIRONMENT=production
  DATABASE_URL=<railway_database_url>
  API_SECRET_KEY=<your_secret_key>
EOF

echo ""
echo "Render (Frontend):"
cat << 'EOF'
  VITE_API_BASE_URL=https://genx-api.railway.app
  NODE_ENV=production
EOF

echo ""
echo "Render (Node.js Server):"
cat << 'EOF'
  NODE_ENV=production
  PORT=10000
  API_BASE_URL=https://genx-api.railway.app
  DATABASE_URL=<render_postgres_url>
EOF

print_section "Service URLs"
echo "🌐 Expected service URLs:"
echo "  API (Railway): https://genx-api.railway.app"
echo "  Frontend (Render): https://genx-frontend.onrender.com"
echo "  Server (Render): https://genx-server.onrender.com"
echo "  Google VM: <your_vm_ip>:8080"

print_section "Post-Deployment Verification"
echo "🔍 Verification steps:"
echo "  1. Test API health: curl https://genx-api.railway.app/health"
echo "  2. Check frontend loading: visit https://genx-frontend.onrender.com"
echo "  3. Verify server endpoints: https://genx-server.onrender.com/api/status"
echo "  4. Test VM communication: check logs for cross-service calls"

print_section "Monitoring & Logs"
echo "📊 Monitoring locations:"
echo "  Railway: https://railway.app/project/<project-id>"
echo "  Render: https://dashboard.render.com/services"
echo "  Google VM: SSH access + application logs"

print_section "Deployment Complete"
print_success "Deployment script execution finished!"
echo ""
echo "📝 Next steps:"
echo "  1. Complete manual deployments for any failed automated steps"
echo "  2. Configure environment variables in platform dashboards"
echo "  3. Test all service endpoints"
echo "  4. Monitor deployment logs for any issues"
echo ""
echo "🆘 Support:"
echo "  - Check deployment_report.md for detailed logs"
echo "  - Review platform-specific documentation"
echo "  - Verify network connectivity between services"

echo ""
print_success "Happy trading with GenX FX! 🚀📈"