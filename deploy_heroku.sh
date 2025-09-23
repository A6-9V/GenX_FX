#!/bin/bash

# Heroku Deployment Script for AMP System
# Advanced Multi-Platform Trading System

set -e  # Exit on any error

echo "🚀 Starting Heroku deployment for AMP System..."

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI is not installed. Installing..."
    curl https://cli-assets.heroku.com/install.sh | sh
fi

# Set the Heroku API key if provided
if [ -n "$HEROKU_API_KEY" ]; then
    echo "✅ Using provided Heroku API key"
    export HEROKU_API_KEY=$HEROKU_API_KEY
else
    echo "⚠️  No HEROKU_API_KEY provided. Please login manually:"
    echo "   Run: heroku login"
    echo "   Then re-run this script"
    exit 1
fi

# Check authentication
echo "🔐 Checking Heroku authentication..."
if ! heroku auth:whoami; then
    echo "❌ Heroku authentication failed. Please check your API key."
    exit 1
fi

# App name (you can customize this)
APP_NAME="amp-system-${USER:-$(whoami)}-$(date +%s)"
echo "📱 Creating Heroku app: $APP_NAME"

# Create Heroku app
echo "🏗️  Creating Heroku application..."
heroku create $APP_NAME --region us || {
    echo "⚠️  App creation failed, trying with a different name..."
    APP_NAME="amp-system-$(date +%s)"
    heroku create $APP_NAME --region us
}

echo "✅ Created Heroku app: $APP_NAME"

# Add buildpacks
echo "🔧 Adding buildpacks..."
heroku buildpacks:add heroku/python --app $APP_NAME
heroku buildpacks:add heroku/nodejs --app $APP_NAME

# Add PostgreSQL addon
echo "🗄️  Adding PostgreSQL database..."
heroku addons:create heroku-postgresql:mini --app $APP_NAME || {
    echo "⚠️  Failed to add PostgreSQL addon (might already exist or quota exceeded)"
}

# Set environment variables
echo "🌍 Setting environment variables..."
heroku config:set NODE_ENV=production --app $APP_NAME
heroku config:set PYTHON_ENV=production --app $APP_NAME
heroku config:set LOG_LEVEL=INFO --app $APP_NAME
heroku config:set CORS_ORIGINS="*" --app $APP_NAME

# Generate a secret key
SECRET_KEY=$(openssl rand -hex 32)
heroku config:set SECRET_KEY=$SECRET_KEY --app $APP_NAME

# Add git remote
echo "🔗 Adding Heroku git remote..."
heroku git:remote -a $APP_NAME

# Ensure we're on the correct branch
echo "🌿 Checking git branch..."
CURRENT_BRANCH=$(git branch --show-current)
if [ -z "$CURRENT_BRANCH" ]; then
    echo "📝 Creating initial commit..."
    git add .
    git commit -m "Initial commit for Heroku deployment" || echo "No changes to commit"
    CURRENT_BRANCH="main"
fi

# Deploy to Heroku
echo "🚀 Deploying to Heroku..."
git push heroku $CURRENT_BRANCH:main

# Run any post-deployment commands
echo "⚙️  Running post-deployment setup..."
heroku run python -c "print('Post-deployment setup completed')" --app $APP_NAME

# Open the app
echo "🌐 Opening application..."
heroku open --app $APP_NAME

# Show app info
echo "📊 Application information:"
heroku info --app $APP_NAME

# Show logs
echo "📋 Recent logs:"
heroku logs --tail --num=50 --app $APP_NAME

echo ""
echo "✅ Deployment completed successfully!"
echo "🌐 App URL: https://$APP_NAME.herokuapp.com"
echo "📱 App Name: $APP_NAME"
echo ""
echo "📝 Useful commands:"
echo "   heroku logs --tail --app $APP_NAME  # View live logs"
echo "   heroku restart --app $APP_NAME      # Restart the app"
echo "   heroku config --app $APP_NAME       # View environment variables"
echo "   heroku ps --app $APP_NAME           # View running processes"
echo ""