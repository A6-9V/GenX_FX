import subprocess
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
from pathlib import Path

from head_cli import app

runner = CliRunner()

def test_secure_exec_success():
    """Test the 'secure exec' command with a successful remote execution."""
    with patch("subprocess.run") as mock_run:
        # Mock a successful subprocess result
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Remote command output",
            stderr=""
        )

        result = runner.invoke(
            app,
            [
                "secure",
                "exec",
                "--key-file",
                "dummy_key.pem",
                "user@host",
                "ls -l",
            ],
        )

        assert result.exit_code == 0
        assert "Remote command executed successfully" in result.stdout
        assert "Remote command output" in result.stdout
        mock_run.assert_called_once()
        # Verify that the correct ssh command was constructed
        called_args = mock_run.call_args[0][0]
        assert called_args == [
            "ssh",
            "-i",
            "dummy_key.pem",
            "-o", "BatchMode=yes",
            "user@host",
            "ls -l",
        ]

def test_secure_exec_failure():
    """Test the 'secure exec' command with a failed remote execution."""
    with patch("subprocess.run") as mock_run:
        # Mock a failed subprocess result
        mock_run.return_value = MagicMock(
            returncode=127,
            stdout="",
            stderr="Command not found"
        )

        result = runner.invoke(
            app,
            [
                "secure",
                "exec",
                "--key-file",
                "dummy_key.pem",
                "user@host",
                "invalid-command",
            ],
        )

        # The runner captures typer.Exit(code=127) but reports it as exit_code=1
        assert result.exit_code == 1
        assert "Error executing remote command" in result.stdout
        assert "Command not found" in result.stdout
        mock_run.assert_called_once()

def test_secure_exec_key_not_found():
    """Test the 'secure exec' command when the key file does not exist."""
    result = runner.invoke(
        app,
        [
            "secure",
            "exec",
            "--key-file",
            "non_existent_key.pem",
            "user@host",
            "ls",
        ],
    )

    # Typer exits with code 2 for parameter validation errors
    assert result.exit_code == 2
    # The error message is printed to stderr, which might not be in stdout
    # but the exit code is a reliable indicator of the failure.
