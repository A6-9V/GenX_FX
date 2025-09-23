# Heroku SQL Database Setup Guide

## Overview
This guide will help you complete the SQL database setup for your AMP System on Heroku cloud platform.

## Prerequisites
- ✅ Heroku CLI installed
- ✅ Git repository initialized
- ✅ Heroku token: `HEROKU_TOKEN=HRKU-AAdx7OW4VQYFLAyNbE0_2jze4VpJbaTHK8sxEv1XDN3w_____ws77zaRyPXX`

## Quick Setup (Automated)

### Step 1: Run the Automated Setup Script
```bash
# Set your Heroku token
export HEROKU_TOKEN=HRKU-AAdx7OW4VQYFLAyNbE0_2jze4VpJbaTHK8sxEv1XDN3w_____ws77zaRyPXX

# Run the setup script
./setup_heroku_sql.sh
```

The script will:
- ✅ Add PostgreSQL database to your Heroku app
- ✅ Set up environment variables
- ✅ Create database schema and migrations
- ✅ Deploy the application
- ✅ Run database migrations

## Manual Setup (Step-by-Step)

### Step 1: Authenticate with Heroku
```bash
# Set your token
export HEROKU_TOKEN=HRKU-AAdx7OW4VQYFLAyNbE0_2jze4VpJbaTHK8sxEv1XDN3w_____ws77zaRyPXX
export HEROKU_API_KEY=$HEROKU_TOKEN

# Verify authentication
heroku auth:whoami
```

### Step 2: Create or Use Existing Heroku App
```bash
# List existing apps
heroku apps

# Create new app (if needed)
heroku create amp-system-$(date +%s) --region us

# Or use existing app
export HEROKU_APP_NAME="your-app-name"
```

### Step 3: Add PostgreSQL Database
```bash
# Add PostgreSQL addon
heroku addons:create heroku-postgresql:mini --app $HEROKU_APP_NAME

# Verify database
heroku pg:info --app $HEROKU_APP_NAME
```

### Step 4: Set Environment Variables
```bash
# Set basic environment variables
heroku config:set NODE_ENV=production --app $HEROKU_APP_NAME
heroku config:set PYTHON_ENV=production --app $HEROKU_APP_NAME
heroku config:set LOG_LEVEL=INFO --app $HEROKU_APP_NAME
heroku config:set CORS_ORIGINS="*" --app $HEROKU_APP_NAME

# Generate secret key
SECRET_KEY=$(openssl rand -hex 32)
heroku config:set SECRET_KEY=$SECRET_KEY --app $HEROKU_APP_NAME

# Get database URL
DATABASE_URL=$(heroku config:get DATABASE_URL --app $HEROKU_APP_NAME)
echo "Database URL: $DATABASE_URL"
```

### Step 5: Deploy Application
```bash
# Add Heroku remote
heroku git:remote -a $HEROKU_APP_NAME

# Deploy to Heroku
git add .
git commit -m "Add database setup"
git push heroku main
```

### Step 6: Run Database Migration
```bash
# Run migration on Heroku
heroku run python scripts/migrate_database.py --app $HEROKU_APP_NAME
```

### Step 7: Verify Setup
```bash
# Check app status
heroku ps --app $HEROKU_APP_NAME

# View logs
heroku logs --tail --app $HEROKU_APP_NAME

# Test database health
curl https://$HEROKU_APP_NAME.herokuapp.com/database/health
```

## Database Schema

The setup includes the following database tables:

### Core Tables
- **users** - User accounts and authentication
- **trading_accounts** - Trading broker accounts
- **trading_signals** - Trading signals and alerts
- **trades** - Actual trade executions
- **market_data** - Historical market data
- **ai_predictions** - AI model predictions
- **system_logs** - Application logs
- **api_keys** - API key management

### Features
- ✅ UUID primary keys
- ✅ Automatic timestamps
- ✅ Foreign key relationships
- ✅ Performance indexes
- ✅ Data validation constraints
- ✅ Sample data insertion

## API Endpoints

### Database Health Check
```bash
GET /database/health
```

### Database Tables
```bash
GET /database/tables
```

### Run Migration
```bash
POST /database/migrate
```

## Environment Variables

### Required Variables
- `DATABASE_URL` - PostgreSQL connection string (auto-set by Heroku)
- `NODE_ENV=production`
- `PYTHON_ENV=production`
- `SECRET_KEY` - Application secret key
- `LOG_LEVEL=INFO`

### Optional Variables
- `DB_HOST` - Database host
- `DB_PORT=5432` - Database port
- `DB_NAME` - Database name
- `DB_USER` - Database user
- `DB_PASSWORD` - Database password

## Troubleshooting

### Common Issues

#### 1. Authentication Failed
```bash
# Check token validity
heroku auth:whoami

# Re-authenticate if needed
heroku login
```

#### 2. Database Connection Failed
```bash
# Check database URL
heroku config:get DATABASE_URL --app $HEROKU_APP_NAME

# Test database connection
heroku run python -c "import psycopg2; print('Database connection test')" --app $HEROKU_APP_NAME
```

#### 3. Migration Failed
```bash
# Check migration script
heroku run python scripts/migrate_database.py --app $HEROKU_APP_NAME

# View detailed logs
heroku logs --tail --app $HEROKU_APP_NAME
```

#### 4. App Won't Start
```bash
# Check build logs
heroku logs --tail --app $HEROKU_APP_NAME

# Restart app
heroku restart --app $HEROKU_APP_NAME
```

### Debug Commands
```bash
# View app info
heroku info --app $HEROKU_APP_NAME

# Check configuration
heroku config --app $HEROKU_APP_NAME

# Access app shell
heroku run bash --app $HEROKU_APP_NAME

# View database info
heroku pg:info --app $HEROKU_APP_NAME
```

## Monitoring and Maintenance

### Database Monitoring
```bash
# View database stats
heroku pg:stats --app $HEROKU_APP_NAME

# Check database connections
heroku pg:ps --app $HEROKU_APP_NAME

# View database logs
heroku pg:logs --app $HEROKU_APP_NAME
```

### Backup and Restore
```bash
# Create database backup
heroku pg:backups:capture --app $HEROKU_APP_NAME

# List backups
heroku pg:backups --app $HEROKU_APP_NAME

# Restore from backup
heroku pg:backups:restore b001 --app $HEROKU_APP_NAME
```

## Security Considerations

### Database Security
- ✅ Use SSL connections (enabled by default on Heroku)
- ✅ Connection pooling for performance
- ✅ Prepared statements to prevent SQL injection
- ✅ Environment variable management

### API Security
- ✅ CORS configuration
- ✅ Input validation
- ✅ Error handling
- ✅ Rate limiting (implement as needed)

## Performance Optimization

### Database Optimization
- ✅ Indexes on frequently queried columns
- ✅ Connection pooling
- ✅ Query optimization
- ✅ Regular maintenance

### Application Optimization
- ✅ Async database operations
- ✅ Caching strategies
- ✅ Background task processing
- ✅ Monitoring and alerting

## Next Steps

After successful setup:

1. **Configure Trading API Keys**
   ```bash
   heroku config:set FXCM_API_KEY=your-fxcm-key --app $HEROKU_APP_NAME
   heroku config:set GEMINI_API_KEY=your-gemini-key --app $HEROKU_APP_NAME
   ```

2. **Set Up Monitoring**
   - Enable Heroku addons for monitoring
   - Set up log drains
   - Configure alerts

3. **Implement Additional Features**
   - User authentication
   - Real-time data feeds
   - Trading automation
   - Risk management

4. **Scale Application**
   - Upgrade dyno type as needed
   - Add Redis for caching
   - Implement load balancing

## Support

If you encounter issues:

1. Check the Heroku dashboard: https://dashboard.heroku.com/apps
2. Review application logs: `heroku logs --tail --app $HEROKU_APP_NAME`
3. Verify environment variables: `heroku config --app $HEROKU_APP_NAME`
4. Test database connection: `heroku run python scripts/init_database.py --app $HEROKU_APP_NAME`

## Useful URLs

- **Application**: `https://$HEROKU_APP_NAME.herokuapp.com`
- **API Documentation**: `https://$HEROKU_APP_NAME.herokuapp.com/docs`
- **Database Health**: `https://$HEROKU_APP_NAME.herokuapp.com/database/health`
- **Heroku Dashboard**: `https://dashboard.heroku.com/apps/$HEROKU_APP_NAME`

---

**Status**: ✅ Ready for deployment
**Last Updated**: $(date)
**Version**: 1.0.0