#!/usr/bin/env python3
"""
Jules CLI - Simple Secret & Task Manager
Windows-compatible version without emojis
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

def create_jules_workspace():
    """Create Jules workspace directories"""
    project_root = Path.cwd()
    jules_dir = project_root / ".jules"
    
    for subdir in ["secrets", "tasks", "logs"]:
        (jules_dir / subdir).mkdir(parents=True, exist_ok=True)
    
    return jules_dir

def log_action(action):
    """Log Jules actions"""
    jules_dir = create_jules_workspace()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] Jules: {action}"
    
    log_file = jules_dir / "logs" / f"jules_{datetime.now().strftime('%Y%m%d')}.log"
    with open(log_file, "a") as f:
        f.write(log_entry + "\n")
    
    print(f"LOG: {log_entry}")

def set_secret(key, value):
    """Set a secret"""
    jules_dir = create_jules_workspace()
    secrets_file = jules_dir / "secrets" / "secrets.json"
    
    secrets = {}
    if secrets_file.exists():
        with open(secrets_file, "r") as f:
            secrets = json.load(f)
    
    secrets[key] = value
    
    with open(secrets_file, "w") as f:
        json.dump(secrets, f, indent=2)
    
    print(f"SUCCESS: Secret {key} set")
    log_action(f"Secret {key} set")

def get_secret(key):
    """Get a secret"""
    jules_dir = create_jules_workspace()
    secrets_file = jules_dir / "secrets" / "secrets.json"
    
    if not secrets_file.exists():
        print("ERROR: No secrets found")
        return
    
    with open(secrets_file, "r") as f:
        secrets = json.load(f)
    
    if key in secrets:
        value = secrets[key]
        masked = value[:4] + "*" * (len(value) - 8) + value[-4:] if len(value) > 8 else "*" * len(value)
        print(f"{key}: {masked}")
    else:
        print(f"ERROR: Secret {key} not found")

def list_secrets():
    """List all secrets"""
    jules_dir = create_jules_workspace()
    secrets_file = jules_dir / "secrets" / "secrets.json"
    
    print("JULES SECRET CATEGORIES:")
    print("=" * 40)
    
    categories = {
        "AUTH": ["GITHUB_TOKEN", "GITLAB_TOKEN", "AMP_TOKEN"],
        "CLOUD": ["GOOGLE_CLOUD_PROJECT", "FIREBASE_PROJECT_ID"],
        "AI": ["GEMINI_API_KEY", "OPENAI_API_KEY"],
        "TRADING": ["BYBIT_API_KEY", "FXCM_USERNAME"],
        "BOTS": ["DISCORD_TOKEN", "TELEGRAM_TOKEN"]
    }
    
    existing_secrets = {}
    if secrets_file.exists():
        with open(secrets_file, "r") as f:
            existing_secrets = json.load(f)
    
    for category, keys in categories.items():
        print(f"\n{category}:")
        for key in keys:
            status = "SET" if key in existing_secrets else "NOT SET"
            print(f"  {key}: {status}")

def deploy_task(target):
    """Deploy to target environment"""
    print(f"Jules deploying to {target}...")
    
    commands = {
        "aws": "python deploy_aws_complete.py",
        "gcp": "gcloud run deploy genx-fx-api --source . --region us-central1",
        "heroku": "git push heroku main",
        "docker": "docker build -t keamouyleng/genx-fx . && docker push keamouyleng/genx-fx"
    }
    
    if target in commands:
        try:
            result = subprocess.run(commands[target], shell=True)
            if result.returncode == 0:
                print(f"SUCCESS: Deployed to {target}")
                log_action(f"Deployed to {target}")
            else:
                print(f"ERROR: Deployment to {target} failed")
        except Exception as e:
            print(f"ERROR: {e}")
    else:
        print(f"ERROR: Unknown target {target}")

def status_task():
    """Show Jules status"""
    jules_dir = create_jules_workspace()
    
    print("JULES STATUS REPORT")
    print("=" * 40)
    print(f"Workspace: {jules_dir}")
    print(f"Secrets: {len(list((jules_dir / 'secrets').glob('*')))} files")
    print(f"Tasks: {len(list((jules_dir / 'tasks').glob('*')))} files")
    print(f"Logs: {len(list((jules_dir / 'logs').glob('*')))} files")
    
    # Check secrets
    secrets_file = jules_dir / "secrets" / "secrets.json"
    if secrets_file.exists():
        with open(secrets_file, "r") as f:
            secrets = json.load(f)
        print(f"Managed Secrets: {len(secrets)}")
    else:
        print("Managed Secrets: 0")

def main():
    """Main CLI function"""
    if len(sys.argv) < 2:
        print("JULES CLI - Secret & Task Manager")
        print("Usage:")
        print("  python jules_simple.py secrets list")
        print("  python jules_simple.py secrets set KEY VALUE")
        print("  python jules_simple.py secrets get KEY")
        print("  python jules_simple.py deploy TARGET")
        print("  python jules_simple.py status")
        print("  python jules_simple.py workspace")
        return
    
    command = sys.argv[1]
    
    if command == "secrets":
        if len(sys.argv) < 3:
            list_secrets()
        else:
            action = sys.argv[2]
            if action == "list":
                list_secrets()
            elif action == "set" and len(sys.argv) >= 5:
                set_secret(sys.argv[3], sys.argv[4])
            elif action == "get" and len(sys.argv) >= 4:
                get_secret(sys.argv[3])
            else:
                print("Usage: secrets [list|set KEY VALUE|get KEY]")
    
    elif command == "deploy" and len(sys.argv) >= 3:
        deploy_task(sys.argv[2])
    
    elif command == "status":
        status_task()
    
    elif command == "workspace":
        jules_dir = create_jules_workspace()
        print("JULES WORKSPACE")
        print("=" * 40)
        print(f"Location: {jules_dir}")
        print(f"Secrets: {jules_dir / 'secrets'}")
        print(f"Tasks: {jules_dir / 'tasks'}")
        print(f"Logs: {jules_dir / 'logs'}")
        status_task()
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()