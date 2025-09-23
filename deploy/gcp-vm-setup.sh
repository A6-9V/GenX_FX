#!/bin/bash

# GenX Trading Platform - Google Cloud VM Setup Script
# This script sets up a complete production environment on Google Cloud Compute Engine

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
MONGO_PASSWORD=$(openssl rand -base64 32)

echo -e "${GREEN}Starting GenX Trading Platform setup on Google Cloud VM...${NC}"

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

# Install Google Cloud SDK
echo -e "${YELLOW}Installing Google Cloud SDK...${NC}"
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init

# Install essential tools
echo -e "${YELLOW}Installing essential tools...${NC}"
apt-get install -y git curl wget vim nano htop tree jq ufw fail2ban

# Configure firewall with Google Cloud specific rules
echo -e "${YELLOW}Configuring firewall...${NC}"
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 8000/tcp
ufw allow 3000/tcp  # Grafana
ufw allow 9090/tcp  # Prometheus
ufw --force enable

# Configure Google Cloud firewall rules
echo -e "${YELLOW}Configuring Google Cloud firewall rules...${NC}"
gcloud compute firewall-rules create genx-trading-http --allow tcp:80 --source-ranges 0.0.0.0/0 --description "Allow HTTP"
gcloud compute firewall-rules create genx-trading-https --allow tcp:443 --source-ranges 0.0.0.0/0 --description "Allow HTTPS"
gcloud compute firewall-rules create genx-trading-api --allow tcp:8000 --source-ranges 0.0.0.0/0 --description "Allow API"
gcloud compute firewall-rules create genx-trading-monitoring --allow tcp:3000,tcp:9090 --source-ranges 0.0.0.0/0 --description "Allow monitoring"

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
git clone https://github.com/Mouy-leng/GenX_FX.git .
chmod +x deploy/gcp-vm-setup.sh

# Create environment file
echo -e "${YELLOW}Creating environment configuration...${NC}"
cat > .env << EOF
# Database
DB_PASSWORD=${DB_PASSWORD}
DATABASE_URL=postgresql://genx_user:${DB_PASSWORD}@postgres:5432/genx_trading

# MongoDB
MONGO_PASSWORD=${MONGO_PASSWORD}
MONGODB_URL=mongodb://admin:${MONGO_PASSWORD}@mongo:27017/genx_trading?authSource=admin

# Redis
REDIS_PASSWORD=${REDIS_PASSWORD}
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379

# Security
SECRET_KEY=${SECRET_KEY}

# API Keys (TO BE CONFIGURED)
BYBIT_API_KEY=your_bybit_api_key_here
BYBIT_API_SECRET=your_bybit_api_secret_here
FXCM_API_KEY=your_fxcm_api_key_here
FXCM_API_SECRET=your_fxcm_api_secret_here

# Bot Tokens (TO BE CONFIGURED)
DISCORD_TOKEN=your_discord_token_here
TELEGRAM_TOKEN=your_telegram_token_here

# Monitoring
GRAFANA_PASSWORD=${REDIS_PASSWORD}

# Domain
DOMAIN=${DOMAIN}
EMAIL=${EMAIL}

# Google Cloud specific
GCP_PROJECT_ID=${GOOGLE_CLOUD_PROJECT}
GCP_REGION=${GOOGLE_CLOUD_REGION:-us-central1}
EOF

# Create necessary directories
echo -e "${YELLOW}Creating directories...${NC}"
mkdir -p logs data ai_models nginx/ssl monitoring/grafana monitoring/prometheus database

# Create Google Cloud specific Nginx configuration
echo -e "${YELLOW}Creating Nginx configuration...${NC}"
cat > nginx/nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    
    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log;
    
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    upstream api {
        server api:8000;
    }

    upstream grafana {
        server grafana:3000;
    }

    upstream prometheus {
        server prometheus:9090;
    }

    # Redirect HTTP to HTTPS
    server {
        listen 80;
        server_name _;
        return 301 https://$server_name$request_uri;
    }

    # Main HTTPS server
    server {
        listen 443 ssl http2;
        server_name _;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;

        # Security headers
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options DENY always;
        add_header X-Content-Type-Options nosniff always;
        add_header X-XSS-Protection "1; mode=block" always;

        # Main API
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

        # WebSocket support
        location /ws {
            proxy_pass http://api;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Health check
        location /health {
            proxy_pass http://api/health;
            access_log off;
        }

        # Metrics (restricted access)
        location /metrics {
            proxy_pass http://api/metrics;
            allow 127.0.0.1;
            allow 10.0.0.0/8;  # GCP internal network
            deny all;
        }

        # Grafana dashboard
        location /grafana/ {
            proxy_pass http://grafana/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Prometheus (restricted access)
        location /prometheus/ {
            proxy_pass http://prometheus/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            allow 127.0.0.1;
            allow 10.0.0.0/8;  # GCP internal network
            deny all;
        }
    }
}
EOF

# Create database initialization (same as before)
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

# Create Prometheus configuration with Google Cloud monitoring
echo -e "${YELLOW}Creating Prometheus configuration...${NC}"
cat > monitoring/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  external_labels:
    project_id: '${GOOGLE_CLOUD_PROJECT}'
    region: '${GOOGLE_CLOUD_REGION}'

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

  # Google Cloud monitoring integration
  - job_name: 'gcp-metadata'
    static_configs:
      - targets: ['metadata.google.internal:80']
    metrics_path: '/computeMetadata/v1/instance/attributes/'
    params:
      recursive: ['true']
    scrape_interval: 60s
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

# Create Google Cloud specific backup script
echo -e "${YELLOW}Creating backup script with Google Cloud Storage integration...${NC}"
cat > /usr/local/bin/backup-genx.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/backups/genx-trading"
GCS_BUCKET="genx-trading-backups-${GOOGLE_CLOUD_PROJECT}"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Create GCS bucket if it doesn't exist
gsutil mb -p ${GOOGLE_CLOUD_PROJECT} gs://${GCS_BUCKET} 2>/dev/null || true

# Backup databases
docker exec genx-postgres pg_dump -U genx_user genx_trading > $BACKUP_DIR/postgres_$DATE.sql
docker exec genx-mongo mongodump --db genx_trading --out $BACKUP_DIR/mongo_$DATE

# Backup AI models
cp -r /opt/genx-trading/ai_models $BACKUP_DIR/ai_models_$DATE

# Backup logs
cp -r /opt/genx-trading/logs $BACKUP_DIR/logs_$DATE

# Upload to Google Cloud Storage
gsutil -m cp -r $BACKUP_DIR/* gs://${GCS_BUCKET}/backups/

# Cleanup local backups (keep last 7 days)
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "mongo_*" -mtime +7 -exec rm -rf {} \;
find $BACKUP_DIR -name "ai_models_*" -mtime +7 -exec rm -rf {} \;
find $BACKUP_DIR -name "logs_*" -mtime +7 -exec rm -rf {} \;

# Cleanup old GCS backups (keep last 30 days)
gsutil -m rm gs://${GCS_BUCKET}/backups/**/*$(date -d '30 days ago' +%Y%m%d)* 2>/dev/null || true
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

# Get external IP
EXTERNAL_IP=$(curl -s http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip -H "Metadata-Flavor: Google")

# Display important information
echo -e "${GREEN}=== GenX Trading Platform Setup Complete ===${NC}"
echo -e "${GREEN}External IP: ${EXTERNAL_IP}${NC}"
echo -e "${GREEN}API URL: http://${EXTERNAL_IP}:8000${NC}"
echo -e "${GREEN}Grafana: http://${EXTERNAL_IP}:3000/grafana${NC}"
echo -e "${GREEN}Prometheus: http://${EXTERNAL_IP}:9090/prometheus${NC}"
echo ""
echo -e "${YELLOW}Important: Please update the following in your .env file:${NC}"
echo "- BYBIT_API_KEY"
echo "- BYBIT_API_SECRET"
echo "- FXCM_API_KEY"
echo "- FXCM_API_SECRET"
echo "- DISCORD_TOKEN"
echo "- TELEGRAM_TOKEN"
echo "- DOMAIN (if using custom domain)"
echo ""
echo -e "${YELLOW}Generated passwords:${NC}"
echo "Database: ${DB_PASSWORD}"
echo "Redis: ${REDIS_PASSWORD}"
echo "MongoDB: ${MONGO_PASSWORD}"
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
echo ""
echo -e "${GREEN}Google Cloud Console:${NC}"
echo "https://console.cloud.google.com/compute/instances?project=${GOOGLE_CLOUD_PROJECT}"
