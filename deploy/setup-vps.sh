#!/bin/bash

# GenX Trading Platform - DigitalOcean VPS Setup Script
# This script sets up a complete production environment on DigitalOcean

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
DOMAIN="your-domain.com"
EMAIL="your-email@example.com"
DB_PASSWORD=$(openssl rand -base64 32)
REDIS_PASSWORD=$(openssl rand -base64 32)
SECRET_KEY=$(openssl rand -base64 32)

echo -e "${GREEN}Starting GenX Trading Platform setup on DigitalOcean VPS...${NC}"

# Update system
echo -e "${YELLOW}Updating system packages...${NC}"
apt-get update && apt-get upgrade -y

# Install Docker
echo -e "${YELLOW}Installing Docker...${NC}"
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
systemctl start docker
systemctl enable docker
usermod -aG docker $USER

# Install Docker Compose
echo -e "${YELLOW}Installing Docker Compose...${NC}"
curl -L "https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose

# Install essential tools
echo -e "${YELLOW}Installing essential tools...${NC}"
apt-get install -y git curl wget vim nano htop tree jq ufw fail2ban

# Configure firewall
echo -e "${YELLOW}Configuring firewall...${NC}"
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 8000/tcp
ufw --force enable

# Install Nginx
echo -e "${YELLOW}Installing Nginx...${NC}"
apt-get install -y nginx
systemctl start nginx
systemctl enable nginx

# Install Certbot for SSL
echo -e "${YELLOW}Installing Certbot for SSL...${NC}"
apt-get install -y certbot python3-certbot-nginx

# Create application directory
echo -e "${YELLOW}Creating application directory...${NC}"
mkdir -p /opt/genx-trading
cd /opt/genx-trading

# Clone repository
echo -e "${YELLOW}Cloning repository...${NC}"
git clone https://github.com/Mouy-leng/GenX-EA_Script.git .
chmod +x deploy/setup-vps.sh

# Create environment file
echo -e "${YELLOW}Creating environment configuration...${NC}"
cat > .env << EOF
# Database
DB_PASSWORD=${DB_PASSWORD}
DATABASE_URL=postgresql://genx_user:${DB_PASSWORD}@postgres:5432/genx_trading

# MongoDB
MONGO_PASSWORD=${REDIS_PASSWORD}
MONGODB_URL=mongodb://mongo:27017/genx_trading

# Redis
REDIS_PASSWORD=${REDIS_PASSWORD}
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379

# Security
SECRET_KEY=${SECRET_KEY}

# API Keys (TO BE CONFIGURED)
BYBIT_API_KEY=your_bybit_api_key_here
BYBIT_API_SECRET=your_bybit_api_secret_here

# Bot Tokens (TO BE CONFIGURED)
DISCORD_TOKEN=your_discord_token_here
TELEGRAM_TOKEN=your_telegram_token_here

# Monitoring
GRAFANA_PASSWORD=${REDIS_PASSWORD}

# Domain
DOMAIN=${DOMAIN}
EMAIL=${EMAIL}
EOF

# Create necessary directories
echo -e "${YELLOW}Creating directories...${NC}"
mkdir -p logs data ai_models nginx/ssl monitoring/grafana monitoring/prometheus database

# Create Nginx configuration
echo -e "${YELLOW}Creating Nginx configuration...${NC}"
cat > nginx/nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream api {
        server api:8000;
    }

    server {
        listen 80;
        server_name _;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name _;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
        ssl_prefer_server_ciphers off;
        ssl_session_cache shared:SSL:10m;

        location / {
            proxy_pass http://api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
        }

        location /health {
            proxy_pass http://api/health;
            access_log off;
        }

        location /metrics {
            proxy_pass http://api/metrics;
            allow 127.0.0.1;
            deny all;
        }
    }
}
EOF

# Create database initialization
echo -e "${YELLOW}Creating database initialization...${NC}"
cat > database/init.sql << 'EOF'
-- Initialize GenX Trading Database
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trading signals table
CREATE TABLE IF NOT EXISTS trading_signals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(20) NOT NULL,
    signal_type VARCHAR(10) NOT NULL,
    entry_price DECIMAL(18,8) NOT NULL,
    stop_loss DECIMAL(18,8),
    take_profit DECIMAL(18,8),
    confidence DECIMAL(4,3) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    executed_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending'
);

-- Trading positions table
CREATE TABLE IF NOT EXISTS positions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    symbol VARCHAR(20) NOT NULL,
    position_type VARCHAR(10) NOT NULL,
    quantity DECIMAL(18,8) NOT NULL,
    entry_price DECIMAL(18,8) NOT NULL,
    current_price DECIMAL(18,8),
    stop_loss DECIMAL(18,8),
    take_profit DECIMAL(18,8),
    unrealized_pnl DECIMAL(18,8) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP
);

-- Model performance table
CREATE TABLE IF NOT EXISTS model_performance (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_name VARCHAR(100) NOT NULL,
    accuracy DECIMAL(6,4) NOT NULL,
    precision_score DECIMAL(6,4) NOT NULL,
    recall_score DECIMAL(6,4) NOT NULL,
    f1_score DECIMAL(6,4) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_signals_symbol ON trading_signals(symbol);
CREATE INDEX IF NOT EXISTS idx_signals_created_at ON trading_signals(created_at);
CREATE INDEX IF NOT EXISTS idx_positions_user_id ON positions(user_id);
CREATE INDEX IF NOT EXISTS idx_positions_symbol ON positions(symbol);
CREATE INDEX IF NOT EXISTS idx_positions_status ON positions(status);
EOF

# Create Prometheus configuration
echo -e "${YELLOW}Creating Prometheus configuration...${NC}"
cat > monitoring/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'genx-api'
    static_configs:
      - targets: ['api:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
EOF

# Create systemd service
echo -e "${YELLOW}Creating systemd service...${NC}"
cat > /etc/systemd/system/genx-trading.service << 'EOF'
[Unit]
Description=GenX Trading Platform
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/genx-trading
ExecStart=/usr/local/bin/docker-compose -f docker-compose.production.yml up -d
ExecStop=/usr/local/bin/docker-compose -f docker-compose.production.yml down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
systemctl daemon-reload
systemctl enable genx-trading.service

# --- Gitpod Self-Hosted Runner Setup ---
echo -e "${YELLOW}Setting up Gitpod Self-Hosted Runner...${NC}"

# 1. Create a dedicated user for the runner for security
echo -e "${YELLOW}Creating 'gitpod' user...${NC}"
if ! id "gitpod" &>/dev/null; then
    useradd -m -s /bin/bash gitpod
    usermod -aG docker gitpod
    echo -e "${GREEN}'gitpod' user created and added to docker group.${NC}"
else
    echo -e "${GREEN}'gitpod' user already exists.${NC}"
fi

# 2. Install Gitpod CLI
echo -e "${YELLOW}Installing Gitpod CLI...${NC}"
wget -O /tmp/gitpod "https://releases.gitpod.io/cli/stable/gitpod-linux-amd64"
chmod +x /tmp/gitpod
mv /tmp/gitpod /usr/local/bin/gitpod

# 3. Create systemd service for the Gitpod runner
echo -e "${YELLOW}Creating systemd service for Gitpod runner...${NC}"
cat > /etc/systemd/system/gitpod-runner.service << 'EOF'
[Unit]
Description=Gitpod Self-Hosted Runner
After=network.target docker.service
Requires=docker.service

[Service]
User=gitpod
Group=gitpod
ExecStart=/usr/local/bin/gitpod runner run
Restart=always
RestartSec=10
Environment="HOME=/home/gitpod"

[Install]
WantedBy=multi-user.target
EOF

# Enable the service (but don't start it yet, requires setup)
systemctl daemon-reload
systemctl enable gitpod-runner.service
echo -e "${GREEN}Gitpod runner service created and enabled. Manual setup is required to start.${NC}"

# Create backup script
echo -e "${YELLOW}Creating backup script...${NC}"
cat > /usr/local/bin/backup-genx.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/backups/genx-trading"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup databases
docker exec genx-postgres pg_dump -U genx_user genx_trading > $BACKUP_DIR/postgres_$DATE.sql
docker exec genx-mongo mongodump --db genx_trading --out $BACKUP_DIR/mongo_$DATE

# Backup AI models
cp -r /opt/genx-trading/ai_models $BACKUP_DIR/ai_models_$DATE

# Backup logs
cp -r /opt/genx-trading/logs $BACKUP_DIR/logs_$DATE

# Cleanup old backups (keep last 7 days)
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "mongo_*" -mtime +7 -exec rm -rf {} \;
find $BACKUP_DIR -name "ai_models_*" -mtime +7 -exec rm -rf {} \;
find $BACKUP_DIR -name "logs_*" -mtime +7 -exec rm -rf {} \;
EOF

chmod +x /usr/local/bin/backup-genx.sh

# Setup daily backup cron
echo -e "${YELLOW}Setting up daily backup cron...${NC}"
echo "0 2 * * * /usr/local/bin/backup-genx.sh" | crontab -

# Build and start services
echo -e "${YELLOW}Building and starting services...${NC}"
docker-compose -f docker-compose.production.yml build
docker-compose -f docker-compose.production.yml up -d

# Wait for services to be ready
echo -e "${YELLOW}Waiting for services to be ready...${NC}"
sleep 30

# Check service status
echo -e "${YELLOW}Checking service status...${NC}"
docker-compose -f docker-compose.production.yml ps

# Create monitoring dashboard
echo -e "${YELLOW}Setting up monitoring dashboard...${NC}"
echo "Grafana will be available at: http://your-server-ip:3000"
echo "Default login: admin / ${REDIS_PASSWORD}"

# Display important information
echo -e "${GREEN}=== GenX Trading Platform Setup Complete ===${NC}"
echo -e "${GREEN}API URL: http://your-server-ip:8000${NC}"
echo -e "${GREEN}Grafana: http://your-server-ip:3000${NC}"
echo -e "${GREEN}Prometheus: http://your-server-ip:9090${NC}"
echo ""
echo -e "${YELLOW}Important: Please update the following in your .env file:${NC}"
echo "- BYBIT_API_KEY"
echo "- BYBIT_API_SECRET"
echo "- DISCORD_TOKEN"
echo "- TELEGRAM_TOKEN"
echo "- DOMAIN (if using custom domain)"
echo ""
echo -e "${YELLOW}Generated passwords:${NC}"
echo "Database: ${DB_PASSWORD}"
echo "Redis: ${REDIS_PASSWORD}"
echo "Grafana: ${REDIS_PASSWORD}"
echo ""
echo -e "${GREEN}To configure SSL with Let's Encrypt, run:${NC}"
echo "certbot --nginx -d ${DOMAIN}"
echo ""
echo -e "${GREEN}To view logs:${NC}"
echo "docker-compose -f docker-compose.production.yml logs -f"
echo ""
echo -e "${GREEN}To restart services:${NC}"
echo "systemctl restart genx-trading"
