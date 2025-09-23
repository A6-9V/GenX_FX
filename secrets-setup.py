import os
import subprocess
import json

# Load environment variables
with open('.env', 'r') as f:
    for line in f:
        if '=' in line:
            key, value = line.strip().split('=', 1)
            os.environ[key] = value

# GitHub secrets to set
secrets = {
    'SECRET_KEY': os.getenv('SECRET_KEY', ''),
    'LOG_LEVEL': os.getenv('LOG_LEVEL', ''),
    'PORT': os.getenv('PORT', ''),
    'NODE_ENV': os.getenv('NODE_ENV', ''),
    'DB_PASSWORD': os.getenv('DB_PASSWORD', ''),
    'DATABASE_URL': os.getenv('DATABASE_URL', ''),
    'MONGO_PASSWORD': os.getenv('MONGO_PASSWORD', ''),
    'MONGODB_URL': os.getenv('MONGODB_URL', ''),
    'REDIS_PASSWORD': os.getenv('REDIS_PASSWORD', ''),
    'REDIS_URL': os.getenv('REDIS_URL', ''),
    'BYBIT_API_KEY': os.getenv('BYBIT_API_KEY', ''),
    'BYBIT_API_SECRET': os.getenv('BYBIT_API_SECRET', ''),
    'FXCM_API_TOKEN': os.getenv('FXCM_API_TOKEN', ''),
    'FXCM_URL': os.getenv('FXCM_URL', ''),
    'FXCM_SOCKET_URL': os.getenv('FXCM_SOCKET_URL', ''),
    'FXCM_USERNAME': os.getenv('FXCM_USERNAME', ''),
    'FXCM_PASSWORD': os.getenv('FXCM_PASSWORD', ''),
    'EXNESS_PASSWORD': os.getenv('EXNESS_PASSWORD', ''),
    'DISCORD_TOKEN': os.getenv('DISCORD_TOKEN', ''),
    'TELEGRAM_TOKEN': os.getenv('TELEGRAM_TOKEN', ''),
    'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY', ''),
    'GEMINI_MODEL': os.getenv('GEMINI_MODEL', ''),
    'GEMINI_MAX_TOKENS': os.getenv('GEMINI_MAX_TOKENS', ''),
    'GEMINI_RATE_LIMIT_RPM': os.getenv('GEMINI_RATE_LIMIT_RPM', ''),
    'GRAFANA_PASSWORD': os.getenv('GRAFANA_PASSWORD', ''),
    'AMP_TOKEN': os.getenv('AMP_TOKEN', ''),
    'AMP_ENV': os.getenv('AMP_ENV', ''),
    'AMP_LOG_LEVEL': os.getenv('AMP_LOG_LEVEL', ''),
    'AMP_API_PORT': os.getenv('AMP_API_PORT', ''),
    'FXCM_SECRET_KEY': os.getenv('FXCM_SECRET_KEY', ''),
    'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY', ''),
    'ALPHA_VANTAGE_API_KEY': os.getenv('ALPHA_VANTAGE_API_KEY', ''),
    'NEWS_API_KEY': os.getenv('NEWS_API_KEY', ''),
    'POSTGRES_DB': os.getenv('POSTGRES_DB', ''),
    'POSTGRES_USER': os.getenv('POSTGRES_USER', ''),
    'POSTGRES_PASSWORD': os.getenv('POSTGRES_PASSWORD', ''),
    'POSTGRES_HOST': os.getenv('POSTGRES_HOST', ''),
    'POSTGRES_PORT': os.getenv('POSTGRES_PORT', ''),
    'REDIS_HOST': os.getenv('REDIS_HOST', ''),
    'REDIS_PORT': os.getenv('REDIS_PORT', ''),
    'DEBUG': os.getenv('DEBUG', ''),
    'GOOGLE_PROJECT': os.getenv('GOOGLE_PROJECT', ''),
    'GOOGLE_REGION': os.getenv('GOOGLE_REGION', ''),
    'SERVICE_NAME': os.getenv('SERVICE_NAME', ''),
    'BUCKET_NAME': os.getenv('BUCKET_NAME', ''),
    'SERVICE_ACCOUNT_KEY': os.getenv('SERVICE_ACCOUNT_KEY', ''),
    'GITHUB_TOKEN': os.getenv('GITHUB_TOKEN', ''),
    'GITLAB_TOKEN': os.getenv('GITLAB_TOKEN', ''),
    'CURSOR_CLI_API_KEY': os.getenv('CURSOR_CLI_API_KEY', '')
}

print("GitHub secrets configured locally. Use GitHub web interface to set them.")
for key, value in secrets.items():
    if value:
        print(f"{key}: {'*' * len(value)}")