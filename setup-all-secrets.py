import os
from dotenv import load_dotenv

load_dotenv()

# Set all environment variables from provided credentials
os.environ['GITHUB_TOKEN'] = os.getenv("GITHUB_TOKEN", "your_github_token_here")
os.environ['GITLAB_TOKEN'] = os.getenv("GITLAB_TOKEN", "your_gitlab_token_here")
os.environ['CURSOR_CLI_API_KEY'] = os.getenv("CURSOR_CLI_API_KEY", "your_cursor_api_key_here")
os.environ['AMP_TOKEN'] = os.getenv("AMP_TOKEN", "your_amp_token_here")

# Update .env file with all credentials
env_content = f"""
GITHUB_TOKEN={os.environ['GITHUB_TOKEN']}
GITLAB_TOKEN={os.environ['GITLAB_TOKEN']}
CURSOR_CLI_API_KEY={os.environ['CURSOR_CLI_API_KEY']}
AMP_TOKEN={os.environ['AMP_TOKEN']}
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