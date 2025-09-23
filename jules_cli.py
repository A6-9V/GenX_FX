#!/usr/bin/env python3
"""
Jules CLI - Secret & Task Management Workspace
Specialized CLI for Jules as secret and deployment manager
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn

app = typer.Typer(help="🔐 Jules CLI - Secret & Task Management", rich_markup_mode="rich")
console = Console()

class JulesWorkspace:
    def __init__(self):
        self.project_root = Path.cwd()
        self.secrets_dir = self.project_root / ".jules" / "secrets"
        self.tasks_dir = self.project_root / ".jules" / "tasks"
        self.logs_dir = self.project_root / ".jules" / "logs"
        
        # Create Jules workspace
        for dir_path in [self.secrets_dir, self.tasks_dir, self.logs_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        self.secret_categories = {
            "auth": ["GITHUB_TOKEN", "GITLAB_TOKEN", "AMP_TOKEN"],
            "cloud": ["GOOGLE_CLOUD_PROJECT", "FIREBASE_PROJECT_ID", "AWS_ACCESS_KEY_ID"],
            "ai": ["GEMINI_API_KEY", "OPENAI_API_KEY"],
            "trading": ["BYBIT_API_KEY", "FXCM_USERNAME", "FXCM_PASSWORD"],
            "bots": ["DISCORD_TOKEN", "TELEGRAM_TOKEN"],
            "deployment": ["DOCKER_USERNAME", "DOCKER_PASSWORD"]
        }
        
        self.available_tasks = {
            "deploy": "Execute deployment to specified environment",
            "secrets": "Manage secrets and environment variables", 
            "monitor": "Monitor system health and performance",
            "backup": "Create system backups",
            "cleanup": "Clean up temporary files and logs",
            "status": "Check deployment and system status"
        }

    def log_action(self, action: str, details: str = ""):
        """Log Jules actions"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] Jules: {action}"
        if details:
            log_entry += f" - {details}"
        
        log_file = self.logs_dir / f"jules_{datetime.now().strftime('%Y%m%d')}.log"
        with open(log_file, "a") as f:
            f.write(log_entry + "\n")
        
        console.print(f"[dim]{log_entry}[/dim]")

    def execute_task(self, task: str, args: List[str] = None) -> bool:
        """Execute a Jules task"""
        self.log_action(f"Executing task: {task}", " ".join(args or []))
        
        if task == "deploy":
            return self._deploy_task(args)
        elif task == "secrets":
            return self._secrets_task(args)
        elif task == "monitor":
            return self._monitor_task()
        elif task == "backup":
            return self._backup_task()
        elif task == "cleanup":
            return self._cleanup_task()
        elif task == "status":
            return self._status_task()
        else:
            console.print(f"❌ Unknown task: {task}")
            return False

    def _deploy_task(self, args: List[str]) -> bool:
        """Handle deployment tasks"""
        if not args:
            console.print("❌ Deployment target required: aws, gcp, heroku, docker")
            return False
        
        target = args[0]
        console.print(f"🚀 [blue]Jules deploying to {target}...[/blue]")
        
        deploy_commands = {
            "aws": "python deploy_aws_complete.py",
            "gcp": "gcloud run deploy genx-fx-api --source . --region us-central1",
            "heroku": "git push heroku main",
            "docker": "docker build -t keamouyleng/genx-fx . && docker push keamouyleng/genx-fx"
        }
        
        if target in deploy_commands:
            try:
                result = subprocess.run(deploy_commands[target], shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    console.print(f"✅ [green]Deployment to {target} successful[/green]")
                    self.log_action(f"Deployment to {target} successful")
                    return True
                else:
                    console.print(f"❌ [red]Deployment failed: {result.stderr}[/red]")
                    return False
            except Exception as e:
                console.print(f"❌ [red]Deployment error: {e}[/red]")
                return False
        else:
            console.print(f"❌ Unknown deployment target: {target}")
            return False

    def _secrets_task(self, args: List[str]) -> bool:
        """Handle secrets management"""
        if not args:
            self._list_secrets()
            return True
        
        action = args[0]
        if action == "set" and len(args) >= 3:
            key, value = args[1], args[2]
            return self._set_secret(key, value)
        elif action == "get" and len(args) >= 2:
            key = args[1]
            return self._get_secret(key)
        elif action == "list":
            self._list_secrets()
            return True
        elif action == "sync":
            return self._sync_secrets()
        else:
            console.print("❌ Usage: secrets [set KEY VALUE | get KEY | list | sync]")
            return False

    def _set_secret(self, key: str, value: str) -> bool:
        """Set a secret value"""
        secrets_file = self.secrets_dir / "secrets.json"
        
        # Load existing secrets
        secrets = {}
        if secrets_file.exists():
            with open(secrets_file, "r") as f:
                secrets = json.load(f)
        
        # Set new secret
        secrets[key] = value
        
        # Save secrets
        with open(secrets_file, "w") as f:
            json.dump(secrets, f, indent=2)
        
        console.print(f"✅ [green]Secret {key} set successfully[/green]")
        self.log_action(f"Secret {key} set")
        return True

    def _get_secret(self, key: str) -> bool:
        """Get a secret value"""
        secrets_file = self.secrets_dir / "secrets.json"
        
        if not secrets_file.exists():
            console.print("❌ No secrets file found")
            return False
        
        with open(secrets_file, "r") as f:
            secrets = json.load(f)
        
        if key in secrets:
            # Mask the value for security
            value = secrets[key]
            masked = value[:4] + "*" * (len(value) - 8) + value[-4:] if len(value) > 8 else "*" * len(value)
            console.print(f"🔐 {key}: {masked}")
            return True
        else:
            console.print(f"❌ Secret {key} not found")
            return False

    def _list_secrets(self):
        """List all secrets by category"""
        console.print("🔐 [bold]Jules Secret Categories:[/bold]")
        
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Category")
        table.add_column("Secrets")
        table.add_column("Status")
        
        secrets_file = self.secrets_dir / "secrets.json"
        existing_secrets = {}
        if secrets_file.exists():
            with open(secrets_file, "r") as f:
                existing_secrets = json.load(f)
        
        for category, secret_keys in self.secret_categories.items():
            status_list = []
            for key in secret_keys:
                if key in existing_secrets:
                    status_list.append(f"✅ {key}")
                else:
                    status_list.append(f"❌ {key}")
            
            table.add_row(
                category.upper(),
                ", ".join(secret_keys),
                "\n".join(status_list)
            )
        
        console.print(table)

    def _sync_secrets(self) -> bool:
        """Sync secrets to environment variables"""
        secrets_file = self.secrets_dir / "secrets.json"
        
        if not secrets_file.exists():
            console.print("❌ No secrets file found")
            return False
        
        with open(secrets_file, "r") as f:
            secrets = json.load(f)
        
        # Create .env file
        env_file = self.project_root / ".env"
        with open(env_file, "w") as f:
            for key, value in secrets.items():
                f.write(f"{key}={value}\n")
        
        console.print(f"✅ [green]Synced {len(secrets)} secrets to .env[/green]")
        self.log_action(f"Synced {len(secrets)} secrets to .env")
        return True

    def _monitor_task(self) -> bool:
        """Monitor system status"""
        console.print("📊 [blue]Jules System Monitor[/blue]")
        
        # Check live deployments
        try:
            result = subprocess.run("python check_live_deployments.py", shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                console.print(result.stdout)
            else:
                console.print("⚠️ Could not check live deployments")
        except:
            console.print("⚠️ Monitor script not available")
        
        return True

    def _backup_task(self) -> bool:
        """Create system backup"""
        backup_dir = self.project_root / "backups" / f"jules_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Backup important files
        important_files = [".env", "requirements.txt", "main.py", "genx_cli.py", "amp_cli.py"]
        backed_up = 0
        
        for file_name in important_files:
            src = self.project_root / file_name
            if src.exists():
                dst = backup_dir / file_name
                try:
                    import shutil
                    shutil.copy2(src, dst)
                    backed_up += 1
                except Exception as e:
                    console.print(f"⚠️ Could not backup {file_name}: {e}")
        
        console.print(f"✅ [green]Backup created: {backed_up} files backed up to {backup_dir}[/green]")
        self.log_action(f"Backup created with {backed_up} files")
        return True

    def _cleanup_task(self) -> bool:
        """Clean up temporary files"""
        cleanup_patterns = ["*.pyc", "__pycache__", "*.log", ".pytest_cache"]
        cleaned = 0
        
        for pattern in cleanup_patterns:
            try:
                import glob
                files = glob.glob(str(self.project_root / "**" / pattern), recursive=True)
                for file_path in files:
                    try:
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                            cleaned += 1
                        elif os.path.isdir(file_path):
                            import shutil
                            shutil.rmtree(file_path)
                            cleaned += 1
                    except:
                        pass
            except:
                pass
        
        console.print(f"✅ [green]Cleanup completed: {cleaned} items removed[/green]")
        self.log_action(f"Cleanup completed: {cleaned} items removed")
        return True

    def _status_task(self) -> bool:
        """Check system status"""
        console.print("📋 [bold]Jules Status Report[/bold]")
        
        # Check workspace
        console.print(f"📁 Jules Workspace: {self.project_root / '.jules'}")
        console.print(f"🔐 Secrets: {len(list(self.secrets_dir.glob('*')))} files")
        console.print(f"📝 Tasks: {len(list(self.tasks_dir.glob('*')))} files") 
        console.print(f"📋 Logs: {len(list(self.logs_dir.glob('*')))} files")
        
        # Check secrets
        secrets_file = self.secrets_dir / "secrets.json"
        if secrets_file.exists():
            with open(secrets_file, "r") as f:
                secrets = json.load(f)
            console.print(f"🔑 Managed Secrets: {len(secrets)}")
        else:
            console.print("🔑 Managed Secrets: 0")
        
        return True

# Create Jules workspace instance
jules = JulesWorkspace()

@app.command()
def task(
    name: str = typer.Argument(help="Task name: deploy, secrets, monitor, backup, cleanup, status"),
    args: Optional[List[str]] = typer.Argument(None, help="Task arguments")
):
    """Execute a Jules task"""
    console.print(f"🔧 [blue]Jules executing task: {name}[/blue]")
    
    if name not in jules.available_tasks:
        console.print(f"❌ Unknown task: {name}")
        console.print("Available tasks:", ", ".join(jules.available_tasks.keys()))
        raise typer.Exit(1)
    
    success = jules.execute_task(name, args)
    if not success:
        raise typer.Exit(1)

@app.command()
def secrets(
    action: str = typer.Argument("list", help="Action: set, get, list, sync"),
    key: Optional[str] = typer.Argument(None, help="Secret key"),
    value: Optional[str] = typer.Argument(None, help="Secret value")
):
    """Manage secrets"""
    args = [action]
    if key:
        args.append(key)
    if value:
        args.append(value)
    
    jules.execute_task("secrets", args)

@app.command()
def deploy(
    target: str = typer.Argument(help="Deployment target: aws, gcp, heroku, docker")
):
    """Deploy to specified environment"""
    jules.execute_task("deploy", [target])

@app.command()
def workspace():
    """Show Jules workspace information"""
    console.print(Panel.fit(
        "[bold blue]Jules Workspace[/bold blue]\n"
        f"Location: {jules.project_root / '.jules'}\n"
        f"Secrets: {jules.secrets_dir}\n"
        f"Tasks: {jules.tasks_dir}\n"
        f"Logs: {jules.logs_dir}",
        border_style="blue"
    ))
    
    jules.execute_task("status")

@app.command()
def logs(
    lines: int = typer.Option(20, help="Number of lines to show")
):
    """Show Jules logs"""
    log_file = jules.logs_dir / f"jules_{datetime.now().strftime('%Y%m%d')}.log"
    
    if log_file.exists():
        with open(log_file, "r") as f:
            log_lines = f.readlines()
        
        console.print(f"📋 [bold]Jules Logs (last {lines} lines):[/bold]")
        for line in log_lines[-lines:]:
            console.print(line.strip())
    else:
        console.print("📋 No logs found for today")

@app.callback()
def main():
    """
    🔐 Jules CLI - Secret & Task Management Workspace
    
    Specialized CLI for Jules as the secret and deployment manager.
    Provides secure secret management and task execution capabilities.
    """
    pass

if __name__ == "__main__":
    app()