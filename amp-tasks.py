# AMP Task 2: Upload secrets to GitHub
import requests
import os

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
REPO = 'Mouy-leng/GenX_FX'

secrets = {
    'BYBIT_API_KEY': os.getenv('BYBIT_API_KEY'),
    'BYBIT_SECRET': os.getenv('BYBIT_SECRET'),
    'FXCM_USERNAME': os.getenv('FXCM_USERNAME'),
    'FXCM_PASSWORD': os.getenv('FXCM_PASSWORD'),
    'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY'),
    'TELEGRAM_BOT_TOKEN': os.getenv('TELEGRAM_BOT_TOKEN')
}

print("AMP: Upload secrets to GitHub repository")
print("Run: python github-secrets-api.py")