# Heroku Deployment Guide for AMP System

## Overview
This guide will help you deploy the Advanced Multi-Platform (AMP) Trading System to Heroku cloud platform.

## Prerequisites
- Heroku CLI installed ✅ (Already installed)
- Git repository initialized ✅ (Already initialized)
- Valid Heroku account and API token

## Files Created for Deployment
- `Procfile` - Defines how Heroku runs your application
- `runtime.txt` - Specifies Python version
- `requirements.txt` - Updated with Heroku-compatible dependencies
- `app.json` - Heroku app configuration
- `.env.example` - Environment variables template
- `deploy_heroku.sh` - Automated deployment script

## Manual Deployment Steps

### Step 1: Authentication
Since the provided token appears to be invalid, please authenticate manually:

```bash
# Login to Heroku (this will open a browser)
heroku login

# OR login with email/password
heroku login -i
```

### Step 2: Create Heroku Application
```bash
# Create a new Heroku app
heroku create amp-system-$(date +%s) --region us

# OR specify a custom name
heroku create your-app-name --region us
```

### Step 3: Configure Buildpacks
```bash
# Add Python buildpack (primary)
heroku buildpacks:add heroku/python

# Add Node.js buildpack (for frontend build)
heroku buildpacks:add heroku/nodejs
```

### Step 4: Add Database (Optional)
```bash
# Add PostgreSQL database
heroku addons:create heroku-postgresql:mini
```

### Step 5: Set Environment Variables
```bash
# Set production environment
heroku config:set NODE_ENV=production
heroku config:set PYTHON_ENV=production
heroku config:set LOG_LEVEL=INFO
heroku config:set CORS_ORIGINS="*"

# Generate and set secret key
heroku config:set SECRET_KEY=$(openssl rand -hex 32)

# Add any API keys you have
heroku config:set GEMINI_API_KEY=your-gemini-key
heroku config:set NEWSDATA_API_KEY=your-news-key
# ... add other API keys as needed
```

### Step 6: Deploy to Heroku
```bash
# Add Heroku as git remote
heroku git:remote -a your-app-name

# Deploy current branch to Heroku
git push heroku HEAD:main
```

### Step 7: Verify Deployment
```bash
# Check app status
heroku ps

# View logs
heroku logs --tail

# Open app in browser
heroku open
```

## Automated Deployment Script

You can also use the provided deployment script:

```bash
# Run the automated deployment script
./deploy_heroku.sh
```

**Note**: Make sure to set the `HEROKU_API_KEY` environment variable if using the script:
```bash
export HEROKU_API_KEY=your-valid-token
./deploy_heroku.sh
```

## Environment Variables Configuration

The application requires several environment variables. You can set them using:

```bash
# View current config
heroku config

# Set individual variables
heroku config:set VARIABLE_NAME=value

# Set multiple variables from file
heroku config:set $(cat .env | grep -v '^#' | xargs)
```

### Required Environment Variables:
- `NODE_ENV=production`
- `PYTHON_ENV=production`
- `SECRET_KEY=your-secret-key`
- `LOG_LEVEL=INFO`

### Optional Environment Variables:
- `DATABASE_URL` (automatically set with PostgreSQL addon)
- `REDIS_URL` (if using Redis)
- `GEMINI_API_KEY` (for AI services)
- `NEWSDATA_API_KEY` (for news data)
- `FXCM_API_KEY` (for trading)

## Application Structure

The application is configured to run as a Python FastAPI backend with the following structure:

- **Web Process**: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
- **Release Process**: Environment setup and migrations
- **Buildpacks**: Python (primary) + Node.js (for frontend build)

## Troubleshooting

### Common Issues and Solutions:

1. **Invalid Token Error**
   ```
   Error: The token provided to HEROKU_API_KEY is invalid
   ```
   **Solution**: Use `heroku login` to authenticate manually

2. **Build Failures**
   ```
   Error: Failed to install requirements
   ```
   **Solution**: Check `requirements.txt` for incompatible packages

3. **Port Binding Issues**
   ```
   Error R10 (Boot timeout) -> Web process failed to bind to $PORT
   ```
   **Solution**: Ensure your app binds to `0.0.0.0:$PORT`

4. **Memory Issues**
   ```
   Error R14 (Memory quota exceeded)
   ```
   **Solution**: Upgrade to a higher dyno type or optimize memory usage

### Debugging Commands:
```bash
# View app information
heroku info

# Check running processes
heroku ps

# View configuration
heroku config

# Access app shell
heroku run bash

# View real-time logs
heroku logs --tail

# Restart application
heroku restart
```

## Production Considerations

1. **Scaling**: Start with basic dynos, scale as needed
2. **Database**: Use PostgreSQL addon for persistence
3. **Monitoring**: Enable log drains and monitoring addons
4. **Security**: Set proper CORS origins and API keys
5. **Performance**: Consider Redis for caching

## Post-Deployment Steps

1. **Test the API endpoints**:
   ```bash
   curl https://your-app-name.herokuapp.com/health
   ```

2. **Monitor application logs**:
   ```bash
   heroku logs --tail
   ```

3. **Set up monitoring and alerts**

4. **Configure custom domain** (if needed):
   ```bash
   heroku domains:add your-domain.com
   ```

## Support

If you encounter issues:
1. Check the Heroku dashboard for app status
2. Review application logs: `heroku logs --tail`
3. Verify environment variables: `heroku config`
4. Check buildpack configuration: `heroku buildpacks`

## Next Steps

After successful deployment:
- Configure your trading API keys
- Set up monitoring and alerting
- Implement proper logging
- Configure backup strategies
- Set up CI/CD pipeline for automated deployments

---

**App URL**: Will be available at `https://your-app-name.herokuapp.com`
**Admin Dashboard**: Available at `https://dashboard.heroku.com/apps/your-app-name`