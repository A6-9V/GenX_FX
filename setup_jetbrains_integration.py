#!/usr/bin/env python3
"""
JetBrains Integration Setup Script for GenX Trading Platform

This script automates the setup process for integrating JetBrains IDEs with the
GenX Trading Platform, focusing on a cost-optimized cloud development environment
using Gitpod.

Key Features:
- SSH Key Generation: Creates a new SSH key pair for secure authentication.
- Gitpod Integration: Provides a pre-configured Gitpod setup for a ready-to-code
  cloud environment with auto-sleep to save costs.
- JetBrains Gateway: Guides users on connecting their local JetBrains IDE to the
  Gitpod workspace.
- Cost Optimization: Emphasizes features like auto-sleep and resource monitoring.
"""

import os
import subprocess
from pathlib import Path

# Use rich for better console output
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Confirm, Prompt
    from rich.syntax import Syntax
    from rich.table import Table
    from rich.progress import Progress
except ImportError:
    print("Rich library not found. Please install it with 'pip install rich'")
    exit(1)

# Initialize Rich Console
console = Console()


class JetBrainsSetup:
    """Handles the JetBrains integration setup process."""

    def __init__(self):
        self.project_root = Path.cwd()
        self.ssh_key_name = "new_key"
        self.private_key_path = self.project_root / self.ssh_key_name
        self.public_key_path = self.project_root / f"{self.ssh_key_name}.pub"
        self.github_repo_url = self._get_github_repo_url()

    def _get_github_repo_url(self) -> str:
        """Get the GitHub repository URL from the .git/config file."""
        try:
            result = subprocess.run(
                ["git", "config", "--get", "remote.origin.url"],
                capture_output=True,
                text=True,
                check=True,
            )
            git_url = result.stdout.strip()
            if git_url.endswith(".git"):
                git_url = git_url[:-4]
            if git_url.startswith("git@"):
                git_url = git_url.replace(":", "/").replace("git@", "https://")
            return git_url
        except (subprocess.CalledProcessError, FileNotFoundError):
            return "https://github.com/your-username/your-repo"

    def run(self):
        """Execute the entire setup process."""
        self._show_welcome_message()

        # 1. SSH Key Generation
        self._handle_ssh_key_generation()

        # 2. Gitpod Integration
        self._show_gitpod_integration_guide()

        # 3. JetBrains Gateway Configuration
        self._show_jetbrains_gateway_guide()

        # 4. Cost Optimization Tips
        self._show_cost_optimization_tips()

        # 5. Final Summary
        self._show_summary_and_next_steps()

    def _show_welcome_message(self):
        """Display the welcome message and introduction."""
        console.print(
            Panel(
                "[bold green]🚀 Welcome to the JetBrains Integration Setup[/bold green]\n\n"
                "This script will guide you through setting up a professional, cost-optimized\n"
                "development environment for the GenX Trading Platform using JetBrains IDEs\n"
                "and Gitpod.",
                title="GenX Trading Platform",
                border_style="blue",
            )
        )
        console.print()

    def _handle_ssh_key_generation(self):
        """Manage the SSH key generation process."""
        console.print(
            Panel(
                "[bold]Step 1: SSH Key Generation for Secure Authentication[/bold]",
                border_style="cyan",
            )
        )
        console.print(
            "A dedicated SSH key is required for secure communication between your development\n"
            "environment (Gitpod) and services like GitHub."
        )

        if self.private_key_path.exists() or self.public_key_path.exists():
            console.print(
                f"\n[yellow]SSH key pair ('{self.ssh_key_name}' and '{self.ssh_key_name}.pub') already exists.[/yellow]"
            )
            if not Confirm.ask(
                "Do you want to overwrite the existing key pair?", default=False
            ):
                console.print("Skipping SSH key generation.")
                self._display_public_key()
                return

        self._generate_ssh_key()
        self._display_public_key()

    def _get_user_email(self) -> str:
        """
        Get the user's email from git config, or prompt if not available.
        """
        try:
            # First, try to get email from git config
            result = subprocess.run(
                ["git", "config", "user.email"],
                capture_output=True,
                text=True,
                check=True,
            )
            email = result.stdout.strip()
            if email:
                console.print(f"📧 Using email from git config: [cyan]{email}[/cyan]")
                return email
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Git might not be installed or email not set
            pass

        # If git config fails, prompt the user
        email = Prompt.ask(
            "✉️ Please enter your email address (for the SSH key comment)"
        )
        return email

    def _generate_ssh_key(self):
        """Generate a new ED25519 SSH key pair."""
        email = self._get_user_email()
        if not email:
            console.print("❌ [red]Email address is required to generate an SSH key. Aborting.[/red]")
            exit(1)

        console.print("\n[bold]Generating new ED25519 SSH key pair...[/bold]")
        try:
            with Progress(
                *Progress.get_default_columns(), transient=True
            ) as progress:
                task = progress.add_task("Running ssh-keygen...", total=None)
                subprocess.run(
                    [
                        "ssh-keygen",
                        "-t",
                        "ed25519",
                        "-C",
                        email,
                        "-f",
                        str(self.private_key_path),
                        "-N",
                        "",  # No passphrase
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                )
            console.print(
                f"✅ [green]Successfully generated SSH key pair:[/green]\n"
                f"   - Private Key: {self.private_key_path}\n"
                f"   - Public Key:  {self.public_key_path}"
            )
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            console.print(f"❌ [red]Error generating SSH key: {e}[/red]")
            console.print("Please ensure 'ssh-keygen' is installed and in your PATH.")
            exit(1)

    def _display_public_key(self):
        """Display the public key and instructions for adding it to GitHub."""
        if not self.public_key_path.exists():
            return

        console.print("\n[bold]Your SSH Public Key:[/bold]")
        public_key_content = self.public_key_path.read_text().strip()
        console.print(Panel(public_key_content, border_style="green"))

        console.print("[bold yellow]Action Required: Add SSH Key to GitHub[/bold yellow]")
        table = Table(show_header=False, box=None)
        table.add_row("1. Go to GitHub SSH keys:", "[link=https://github.com/settings/keys]https://github.com/settings/keys[/link]")
        table.add_row("2. Click 'New SSH key'.")
        table.add_row("3. Paste the public key above into the 'Key' field.")
        table.add_row("4. Give it a title (e.g., 'Gitpod Dev Environment').")
        table.add_row("5. Click 'Add SSH key'.")
        console.print(table)
        console.print()

    def _show_gitpod_integration_guide(self):
        """Display the guide for setting up Gitpod."""
        gitpod_url = f"https://gitpod.io/#{self.github_repo_url}"

        console.print(
            Panel(
                "[bold]Step 2: Cost-Optimized Cloud Development with Gitpod[/bold]",
                border_style="cyan",
            )
        )
        console.print(
            "Gitpod provides a ready-to-code cloud development environment that automatically\n"
            "shuts down after a period of inactivity, saving costs."
        )

        console.print("\n[bold]1. Launch Your Gitpod Workspace:[/bold]")
        console.print(
            f"   Click this link to start a new workspace:\n"
            f"   [link={gitpod_url}]{gitpod_url}[/link]"
        )

        console.print("\n[bold]2. Add Your SSH Private Key to Gitpod:[/bold]")
        private_key_content = self.private_key_path.read_text()
        console.print(
            "   - In your Gitpod workspace, go to 'User Settings' > 'Environment Variables'.\n"
            "   - Create a new variable with the following details:"
        )

        env_var_table = Table(title="Gitpod Environment Variable Setup")
        env_var_table.add_column("Field", style="cyan")
        env_var_table.add_column("Value", style="white")
        env_var_table.add_row("Name", "GITPOD_SSH_KEY")
        env_var_table.add_row("Value", "Paste the entire content of your private key here.")
        env_var_table.add_row("Scope", f"'{self.github_repo_url}' (or your repo)")
        console.print(env_var_table)

        console.print(
            "\n   [bold green]This makes your SSH key available for secure operations within Gitpod.[/bold green]"
        )
        console.print()

    def _show_jetbrains_gateway_guide(self):
        """Display the guide for connecting with JetBrains Gateway."""
        console.print(
            Panel(
                "[bold]Step 3: Connect Your Local JetBrains IDE with Gateway[/bold]",
                border_style="cyan",
            )
        )
        console.print(
            "JetBrains Gateway allows you to use your local IDE to develop on a remote\n"
            "machine, like your Gitpod workspace."
        )

        gateway_table = Table(show_header=False, box=None)
        gateway_table.add_row("1. [bold]Install JetBrains Gateway[/bold] on your local machine.")
        gateway_table.add_row("2. [bold]Find Your Gitpod SSH Connection String[/bold]:\n"
                              "   In your active Gitpod workspace, run 'gp ssh-gateway' in the terminal.\n"
                              "   Copy the provided SSH connection string.")
        gateway_table.add_row("3. [bold]Connect with Gateway[/bold]:\n"
                              "   - Open JetBrains Gateway.\n"
                              "   - Click 'Connect via SSH'.\n"
                              "   - Paste the connection string from Gitpod.")
        gateway_table.add_row("4. [bold]Configure Project[/bold]:\n"
                              "   - Gateway will connect and download the required IDE backend.\n"
                              "   - Once connected, open the project directory ('/workspace/GenX_FX').")
        console.print(gateway_table)
        console.print()

    def _show_cost_optimization_tips(self):
        """Display cost optimization tips."""
        console.print(
            Panel("[bold]Step 4: Best Practices for Cost Optimization[/bold]", border_style="cyan")
        )

        tips_table = Table(show_header=False, box=None)
        tips_table.add_row("✅ [bold]Gitpod Auto-Sleep[/bold]:", "Your Gitpod workspace will automatically stop after 30 minutes of inactivity. You are only billed for the time it's running.")
        tips_table.add_row("✅ [bold]Manual Stop[/bold]:", "Manually stop your workspace from the Gitpod dashboard when you're finished for the day.")
        tips_table.add_row("✅ [bold]Resource Monitoring[/bold]:", "Keep an eye on your cloud provider's billing dashboard and set up alerts to avoid unexpected costs.")
        tips_table.add_row("✅ [bold]Choose Appropriate Workspace Size[/bold]:", "Start with a standard Gitpod workspace and upgrade only if you need more resources.")
        console.print(tips_table)
        console.print()

    def _show_summary_and_next_steps(self):
        """Display the final summary and next steps."""
        console.print(
            Panel(
                "[bold green]🎉 Setup Complete! Your Development Environment is Ready.[/bold green]",
                title="Summary and Next Steps",
                border_style="green",
            )
        )

        summary_table = Table(title="Checklist")
        summary_table.add_column("Status", style="green")
        summary_table.add_column("Action", style="cyan")
        summary_table.add_row("✅", "SSH key pair generated.")
        summary_table.add_row("➡️", "[bold]Add your public key to GitHub.[/bold]")
        summary_table.add_row("➡️", "[bold]Launch Gitpod and set up the SSH key environment variable.[/bold]")
        summary_table.add_row("➡️", "[bold]Connect your JetBrains IDE using Gateway.[/bold]")

        console.print(summary_table)
        console.print(
            "\nYou are now set up with a powerful, secure, and cost-effective development environment!"
        )

if __name__ == "__main__":
    setup = JetBrainsSetup()
    setup.run()
