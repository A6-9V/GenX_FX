# GitHub Secrets Setup for Cloud Deployment

## Required Secrets for DigitalOcean Deployment

Go to your GitHub repository → Settings → Secrets and variables → Actions

### DigitalOcean Secrets:
- `DIGITALOCEAN_ACCESS_TOKEN` - Your DO personal access token
- `DIGITALOCEAN_APP_ID` - Your DO App Platform app ID
- `VPS_HOST` - Your droplet IP address
- `VPS_USERNAME` - Usually 'root'
- `VPS_SSH_KEY` - Your private SSH key
- `VPS_PORT` - Usually '22'

### Application Secrets:
- `SECRET_KEY` - Generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- `DB_PASSWORD` - Strong database password
- `MONGO_PASSWORD` - MongoDB password
- `REDIS_PASSWORD` - Redis password
- `GRAFANA_PASSWORD` - Grafana admin password

### API Keys:
- `GEMINI_API_KEY`
- `BYBIT_API_KEY`
- `BYBIT_API_SECRET`
- `DISCORD_TOKEN`
- `TELEGRAM_TOKEN`
- `NEWSDATA_API_KEY`
- `ALPHAVANTAGE_API_KEY`
- `NEWSAPI_ORG_KEY`
- `FINNHUB_API_KEY`
- `FMP_API_KEY`
- `REDDIT_CLIENT_ID`
- `REDDIT_CLIENT_SECRET`
- `REDDIT_USERNAME`
- `REDDIT_PASSWORD`

### Variables (not secrets):
- `APP_URL` - Your app URL (e.g., https://your-app.ondigitalocean.app)
- `DISCORD_WEBHOOK` - For deployment notifications