#!/bin/bash

# Quick Heroku Deployment for AMP System
# Run this after: heroku login

set -e

echo "🚀 Quick Heroku Deployment Starting..."

# Generate unique app name
APP_NAME="amp-system-$(date +%s)"
echo "📱 App name: $APP_NAME"

# Create app
echo "🏗️  Creating Heroku app..."
heroku create $APP_NAME --region us

# Add buildpacks
echo "🔧 Adding buildpacks..."
heroku buildpacks:add heroku/python --app $APP_NAME
heroku buildpacks:add heroku/nodejs --app $APP_NAME

# Add database
echo "🗄️  Adding PostgreSQL..."
heroku addons:create heroku-postgresql:mini --app $APP_NAME || echo "Database addon skipped"

# Set config
echo "⚙️  Setting configuration..."
heroku config:set NODE_ENV=production --app $APP_NAME
heroku config:set PYTHON_ENV=production --app $APP_NAME
heroku config:set LOG_LEVEL=INFO --app $APP_NAME
heroku config:set CORS_ORIGINS="*" --app $APP_NAME
heroku config:set SECRET_KEY=$(openssl rand -hex 32) --app $APP_NAME

# Deploy
echo "🚀 Deploying..."
git push heroku HEAD:main

# Show results
echo ""
echo "✅ Deployment Complete!"
echo "🌐 URL: https://$APP_NAME.herokuapp.com"
echo "📊 Dashboard: https://dashboard.heroku.com/apps/$APP_NAME"
echo ""
echo "📋 Quick commands:"
echo "  heroku logs --tail --app $APP_NAME"
echo "  heroku open --app $APP_NAME"
echo "  heroku ps --app $APP_NAME"