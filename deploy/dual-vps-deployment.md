# Dual VPS Deployment Architecture for GenX Trading Platform

This document outlines the deployment strategy for running the GenX Trading Platform across two VPS environments: a DigitalOcean VPS for the AI backend and a dedicated Forex VPS for MT4/MT5 operations.

## Architecture Overview

```
┌─────────────────────────────────┐    ┌─────────────────────────────────┐
│         DigitalOcean VPS        │    │        Forex VPS (Windows)      │
│           (Linux)               │    │                                 │
│                                 │    │                                 │
│  ┌─────────────────────────────┐│    │ ┌─────────────────────────────┐ │
│  │      FastAPI Backend       ││    │ │         MT4/MT5             │ │
│  │   ┌─────────────────────┐   ││    │ │      Trading Terminal       │ │
│  │   │  AI Ensemble Model  │   ││    │ │                             │ │
│  │   │  - XGBoost          │   ││    │ │  ┌─────────────────────────┐│ │
│  │   │  - LSTM             │   ││    │ │  │     GenX AI EA          ││ │
│  │   │  - CNN              │   ││    │ │  │  (Socket Client)        ││ │
│  │   └─────────────────────┘   ││    │ │  └─────────────────────────┘│ │
│  │                             ││    │ │                             │ │
│  │  ┌─────────────────────────┐││    │ └─────────────────────────────┘ │
│  │  │    FXCM API Service     │││    │                                 │
│  │  │   - WebSocket Stream    │││    │ ┌─────────────────────────────┐ │
│  │  │   - Historical Data     │││    │ │     Local File System       │ │
│  │  └─────────────────────────┘││    │ │   - Trade Status Files      │ │
│  │                             ││    │ │   - Position Updates        │ │
│  │  ┌─────────────────────────┐││    │ └─────────────────────────────┘ │
│  │  │  Enhanced Gemini AI     │││    │                                 │
│  │  │   - Sentiment Analysis  │││    └─────────────────────────────────┘
│  │  │   - Signal Validation   │││               │
│  │  └─────────────────────────┘││               │ TCP/IP Socket
│  │                             ││               │ (Port 9090)
│  │  ┌─────────────────────────┐││               │
│  │  │   EA Communication      │││←──────────────┘
│  │  │   - Socket Server       │││
│  │  │   - Signal Broadcasting │││
│  │  └─────────────────────────┘││
│  │                             ││
│  │  ┌─────────────────────────┐││
│  │  │   Asset Manager         │││
│  │  │   - Google Sheets API   │││
│  │  │   - Portfolio Tracking  │││
│  │  └─────────────────────────┘││
│  └─────────────────────────────┘│
│                                 │
│  ┌─────────────────────────────┐│
│  │      Monitoring Stack      ││
│  │   - Prometheus             ││
│  │   - Grafana                ││
│  │   - Redis Cache            ││
│  └─────────────────────────────┘│
└─────────────────────────────────┘
```

## VPS Requirements

### DigitalOcean VPS (AI Backend)
- **Instance Type**: CPU-Optimized Droplet
- **Minimum Specs**: 
  - 4 vCPUs
  - 8GB RAM
  - 160GB SSD
  - Ubuntu 22.04 LTS
- **Recommended Location**: 
  - London (LON1) for European markets
  - New York (NYC1/NYC3) for US markets
- **Network**: High-bandwidth for real-time data processing

### Forex VPS (Trading Terminal)
- **Provider**: Specialized Forex VPS (FXVM, AccuWebHosting, or Forex VPS)
- **Minimum Specs**:
  - 2 vCPUs
  - 4GB RAM
  - 50GB SSD
  - Windows Server 2019/2022
- **Location**: Same region as FXCM servers (London/New York)
- **Latency**: <10ms to broker servers
- **Uptime**: 99.9%+ guaranteed

## Deployment Steps

### 1. DigitalOcean VPS Setup

```bash
# 1. Create droplet
doctl compute droplet create genx-ai-backend \
  --image ubuntu-22-04-x64 \
  --size c-4 \
  --region lon1 \
  --ssh-keys $SSH_KEY_ID \
  --enable-monitoring \
  --enable-backups

# 2. Setup firewall rules
doctl compute firewall create genx-firewall \
  --inbound-rules "protocol:tcp,ports:22,address:0.0.0.0/0" \
  --inbound-rules "protocol:tcp,ports:80,address:0.0.0.0/0" \
  --inbound-rules "protocol:tcp,ports:443,address:0.0.0.0/0" \
  --inbound-rules "protocol:tcp,ports:9090,address:FOREX_VPS_IP/32" \
  --outbound-rules "protocol:tcp,ports:all,address:0.0.0.0/0"

# 3. Apply firewall to droplet
doctl compute firewall add-droplets genx-firewall --droplet-ids DROPLET_ID
```

### 2. AI Backend Deployment

```bash
# Connect to DigitalOcean VPS
ssh root@YOUR_DROPLET_IP

# Clone repository
git clone https://github.com/Mouy-leng/GenX-EA_Script.git
cd GenX-EA_Script

# Run setup script
chmod +x deploy/setup-vps.sh
./deploy/setup-vps.sh

# Deploy with Docker
docker-compose -f docker-compose.production.yml up -d
```

### 3. Environment Configuration

Create `/opt/genx/.env.production`:

```env
# FXCM API Configuration
FXCM_API_KEY=your_api_key_here
FXCM_ACCESS_TOKEN=your_access_token_here
FXCM_ACCOUNT_ID=your_account_id_here
FXCM_ENVIRONMENT=demo  # or "real"

# Google Sheets Integration
GOOGLE_SHEETS_CREDENTIALS_PATH=/opt/genx/credentials/google-sheets.json
GOOGLE_SHEETS_SPREADSHEET_KEY=your_spreadsheet_key_here

# Gemini AI
GEMINI_API_KEY=your_gemini_api_key_here

# EA Communication
EA_SERVER_HOST=0.0.0.0
EA_SERVER_PORT=9090

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/genx_trading

# Redis
REDIS_URL=redis://localhost:6379

# Monitoring
PROMETHEUS_ENABLED=true
GRAFANA_ENABLED=true

# Logging
LOG_LEVEL=INFO
LOG_TO_FILE=true
```

### 4. Forex VPS Setup

1. **Order Forex VPS**:
   ```
   Provider: FXVM or AccuWebHosting
   Location: London (for FXCM Europe) or New York (for FXCM US)
   Plan: Standard (2GB RAM, 2 vCPU minimum)
   OS: Windows Server 2019/2022
   ```

2. **Install MT4/MT5**:
   - Download FXCM MT4/MT5 from broker
   - Install on Forex VPS
   - Login with trading account credentials

3. **Deploy EA**:
   ```
   1. Copy GenX_AI_EA.mq5 to VPS
   2. Compile in MetaEditor
   3. Add to chart with parameters:
      - AI_Server_Host: YOUR_DIGITALOCEAN_VPS_IP
      - AI_Server_Port: 9090
      - Magic_Number: 12345
      - Enable_Auto_Trading: true
   ```

### 5. Network Configuration

#### DigitalOcean VPS Firewall
```bash
# Allow EA connections
ufw allow from FOREX_VPS_IP to any port 9090

# Allow HTTPS for APIs
ufw allow 443

# Allow SSH
ufw allow 22

# Enable firewall
ufw enable
```

#### Windows Forex VPS Firewall
```powershell
# Allow outbound connection to AI server
New-NetFirewallRule -DisplayName "GenX AI Server" -Direction Outbound -Protocol TCP -RemoteAddress YOUR_DIGITALOCEAN_VPS_IP -RemotePort 9090 -Action Allow

# Allow MT4/MT5 broker connections
New-NetFirewallRule -DisplayName "FXCM Trading" -Direction Outbound -Protocol TCP -RemotePort 443,80 -Action Allow
```

## Monitoring and Maintenance

### 1. Health Checks

Create `/opt/genx/scripts/health-check.sh`:
```bash
#!/bin/bash

# Check AI backend services
curl -f http://localhost:8000/health || exit 1

# Check EA connection
python3 -c "
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
result = sock.connect_ex(('localhost', 9090))
sock.close()
exit(0 if result == 0 else 1)
"

# Check database
psql $DATABASE_URL -c "SELECT 1;" > /dev/null || exit 1

echo "All services healthy"
```

### 2. Automated Backups

```bash
#!/bin/bash
# /opt/genx/scripts/backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/genx/backups"

# Backup database
pg_dump $DATABASE_URL > $BACKUP_DIR/db_backup_$DATE.sql

# Backup models
tar -czf $BACKUP_DIR/models_backup_$DATE.tar.gz /opt/genx/models/

# Upload to cloud storage
aws s3 cp $BACKUP_DIR/ s3://genx-backups/ --recursive

# Cleanup old backups (keep 30 days)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

### 3. Grafana Dashboards

Key metrics to monitor:
- AI prediction accuracy
- Signal generation rate
- EA connection status
- Trade execution latency
- Account balance/equity
- System resource usage

## Security Considerations

### 1. Network Security
- Use private networking between VPS when possible
- Implement IP whitelisting for EA connections
- Use SSL/TLS for all external communications
- Regular security updates

### 2. Credential Management
```bash
# Store sensitive credentials in encrypted files
echo "FXCM_API_KEY=xxx" | gpg --symmetric --cipher-algo AES256 > /opt/genx/secrets/fxcm.gpg

# Create decryption script
cat > /opt/genx/scripts/decrypt-secrets.sh << 'EOF'
#!/bin/bash
gpg --quiet --batch --decrypt /opt/genx/secrets/fxcm.gpg > /tmp/fxcm.env
source /tmp/fxcm.env
rm /tmp/fxcm.env
EOF
```

### 3. Trading Security
- Enable two-factor authentication on trading accounts
- Use demo accounts for testing
- Implement position size limits
- Set maximum daily loss limits
- Regular audit of trading activities

## Troubleshooting

### Common Issues

1. **EA Connection Failed**
   ```bash
   # Check if AI server is listening
   netstat -tlnp | grep 9090
   
   # Check firewall rules
   ufw status numbered
   
   # Test connection from Forex VPS
   telnet YOUR_DIGITALOCEAN_VPS_IP 9090
   ```

2. **High Latency**
   ```bash
   # Test network latency
   ping YOUR_DIGITALOCEAN_VPS_IP
   
   # Check for packet loss
   mtr YOUR_DIGITALOCEAN_VPS_IP
   ```

3. **Google Sheets API Errors**
   ```bash
   # Verify credentials
   python3 -c "
   from google.oauth2.service_account import Credentials
   creds = Credentials.from_service_account_file('/opt/genx/credentials/google-sheets.json')
   print('Credentials valid')
   "
   ```

### Log Locations
- AI Backend: `/opt/genx/logs/genx-backend.log`
- EA Communication: `/opt/genx/logs/ea-server.log`
- System: `/var/log/syslog`
- Docker: `docker logs genx-backend`

## Performance Optimization

### 1. AI Backend Optimization
```python
# Optimize model inference
import tensorflow as tf
tf.config.optimizer.set_experimental_options({'layout_optimizer': False})
tf.config.optimizer.set_experimental_options({'constant_folding': False})
```

### 2. Database Optimization
```sql
-- Create indexes for frequent queries
CREATE INDEX idx_trades_timestamp ON trades(created_at);
CREATE INDEX idx_signals_instrument ON signals(instrument);
```

### 3. Caching Strategy
```python
# Redis caching for market data
import redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Cache market data for 5 seconds
def get_cached_price(instrument):
    cached = redis_client.get(f"price:{instrument}")
    if cached:
        return json.loads(cached)
    # Fetch from API and cache
```

This dual VPS architecture provides the optimal balance of performance, reliability, and cost-effectiveness for the GenX Trading Platform while maintaining low latency and high availability.
