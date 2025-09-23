# Jules CLI - Secret & Task Manager Setup

## Overview
Jules CLI is now configured as your dedicated secret and task management workspace within the GenX FX project.

## What is Jules CLI?
- **Secret Manager**: Secure storage and management of API keys, tokens, and credentials
- **Task Executor**: Automated deployment and system management tasks
- **Workspace Manager**: Organized workspace with logs, tasks, and secrets

## Jules Workspace Structure
```
.jules/
├── secrets/     # Encrypted secret storage
├── tasks/       # Task definitions and scripts
└── logs/        # Jules activity logs
```

## Available Commands

### Direct Jules Commands
```bash
# Secret Management
python jules_simple.py secrets list
python jules_simple.py secrets set GITHUB_TOKEN your_token_here
python jules_simple.py secrets get GITHUB_TOKEN

# Deployment Tasks
python jules_simple.py deploy aws
python jules_simple.py deploy gcp
python jules_simple.py deploy heroku
python jules_simple.py deploy docker

# Status & Workspace
python jules_simple.py status
python jules_simple.py workspace

# Windows Wrapper
cmd /c jules.bat status
cmd /c jules.bat secrets list
```

### Via Head CLI Integration
```bash
# Through Head CLI (recommended)
python head_cli.py jules secrets list
python head_cli.py jules secrets set API_KEY value
python head_cli.py jules deploy aws
python head_cli.py jules status
```

## Secret Categories Managed by Jules

### Authentication
- GITHUB_TOKEN
- GITLAB_TOKEN  
- AMP_TOKEN

### Cloud Services
- GOOGLE_CLOUD_PROJECT
- FIREBASE_PROJECT_ID

### AI APIs
- GEMINI_API_KEY
- OPENAI_API_KEY

### Trading APIs
- BYBIT_API_KEY
- FXCM_USERNAME

### Bot Tokens
- DISCORD_TOKEN
- TELEGRAM_TOKEN

## Deployment Targets

Jules can deploy to:
- **AWS**: `jules deploy aws`
- **Google Cloud**: `jules deploy gcp` 
- **Heroku**: `jules deploy heroku`
- **Docker Hub**: `jules deploy docker`

## Security Features

1. **Masked Display**: Secrets are masked when displayed (shows first 4 and last 4 characters)
2. **Secure Storage**: Secrets stored in JSON format in protected .jules directory
3. **Activity Logging**: All Jules actions are logged with timestamps
4. **Environment Sync**: Can sync secrets to .env file for application use

## Integration with Head CLI

Jules is fully integrated into the Head CLI system:
- Access via `python head_cli.py jules COMMAND`
- Unified interface with other CLI tools (AMP, GenX, Chat)
- Consistent logging and error handling

## Example Workflow

1. **Set up secrets**:
   ```bash
   python head_cli.py jules secrets set GITHUB_TOKEN ghp_your_token
   python head_cli.py jules secrets set GEMINI_API_KEY your_api_key
   ```

2. **Check status**:
   ```bash
   python head_cli.py jules status
   ```

3. **Deploy to cloud**:
   ```bash
   python head_cli.py jules deploy gcp
   ```

4. **View logs**:
   ```bash
   # Check .jules/logs/jules_YYYYMMDD.log
   ```

## Files Created
- `jules_simple.py` - Main Jules CLI implementation
- `jules.bat` - Windows wrapper script
- `.jules/` - Jules workspace directory
- Integration in `head_cli.py`

## Recommendations

1. **Use Head CLI**: Always use `python head_cli.py jules` for consistency
2. **Secure Secrets**: Never commit the `.jules/secrets/` directory to Git
3. **Regular Backups**: Backup your `.jules/` directory regularly
4. **Log Monitoring**: Check Jules logs for deployment and task status

Jules CLI is now ready as your centralized secret and task management system!