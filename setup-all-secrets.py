import os

# Set all environment variables from provided credentials
os.environ['GITHUB_TOKEN'] = os.getenv('GITHUB_TOKEN')
os.environ['GITLAB_TOKEN'] = os.getenv('GITLAB_TOKEN')
os.environ['CURSOR_CLI_API_KEY'] = os.getenv('CURSOR_CLI_API_KEY')
os.environ['AMP_TOKEN'] = os.getenv('AMP_TOKEN')

# Update .env file with all credentials
env_content = f"""
GITHUB_TOKEN={os.environ.get('GITHUB_TOKEN', '')}
GITLAB_TOKEN={os.environ.get('GITLAB_TOKEN', '')}
CURSOR_CLI_API_KEY={os.environ.get('CURSOR_CLI_API_KEY', '')}
AMP_TOKEN={os.environ.get('AMP_TOKEN', '')}
BYBIT_API_KEY=your_bybit_key
BYBIT_SECRET=your_bybit_secret
FXCM_USERNAME=your_fxcm_username
FXCM_PASSWORD=your_fxcm_password
GEMINI_API_KEY=your_gemini_key
TELEGRAM_BOT_TOKEN=your_telegram_token
DISCORD_BOT_TOKEN=your_discord_token
"""

with open('.env', 'w') as f:
    f.write(env_content.strip())

print("All credentials configured in .env file")
print("GitHub profile setup ready")