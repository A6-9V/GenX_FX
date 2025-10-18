#!/usr/bin/env python3
"""
KMS CLI - A Typer app for AWS KMS operations.
"""

import subprocess
import typer
from rich.console import Console

app = typer.Typer(
    help="🔒 KMS CLI - Encrypts a file using a specified KMS key.",
    rich_markup_mode="rich",
)

console = Console()

@app.callback(invoke_without_command=True)
def encrypt(
    key_id: str = typer.Option(..., "--key-id", help="The ID of the KMS key to use for encryption."),
    plaintext_file: str = typer.Option(..., "--plaintext-file", help="The path to the file to encrypt."),
    region: str = typer.Option(..., "--region", help="The AWS region."),
):
    """
    Encrypts a file using the specified KMS key.
    """
    console.print(f"🔐 Encrypting file: [cyan]{plaintext_file}[/cyan]...")

    aws_command = [
        "aws",
        "kms",
        "encrypt",
        "--key-id",
        key_id,
        "--plaintext",
        f"fileb://{plaintext_file}",
        "--region",
        region,
        "--output",
        "text",
        "--query",
        "CiphertextBlob",
    ]

    try:
        result = subprocess.run(
            aws_command,
            capture_output=True,
            text=True,
            check=True,
        )

        if result.stdout:
            console.print("✅ [green]Encryption successful.[/green]")
            console.print(result.stdout)
        else:
            console.print("❌ [red]Encryption failed.[/red]")
            if result.stderr:
                console.print(result.stderr)

    except FileNotFoundError:
        console.print("❌ [red]Error: 'aws' command not found. Please ensure AWS CLI is installed and in your PATH.[/red]")
        raise typer.Exit(1)
    except subprocess.CalledProcessError as e:
        console.print(f"❌ [red]Error executing AWS CLI command (Exit Code: {e.returncode}).[/red]")
        if e.stderr:
            console.print(e.stderr)
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"❌ [bold red]An unexpected error occurred: {e}[/bold red]")
        raise typer.Exit(1)

if __name__ == "__main__":
    app()
