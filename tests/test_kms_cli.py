import unittest.mock
import subprocess
import os
from typer.testing import CliRunner
from kms_cli import app

runner = CliRunner()


@unittest.mock.patch("subprocess.run")
def test_encrypt_success(mock_subprocess_run):
    # Mock the subprocess.run call to simulate a successful AWS CLI execution
    mock_subprocess_run.return_value = subprocess.CompletedProcess(
        args=["aws", "kms", "encrypt"],
        returncode=0,
        stdout="mocked-ciphertext-blob",
        stderr="",
    )

    test_file = "test_secret.txt"
    with open(test_file, "w") as f:
        f.write("this is a secret")

    result = runner.invoke(
        app,
        [
            "--key-id",
            "arn:aws:kms:us-east-1:252321105186:key/63f61139-a332-489b-9969-6df08fed4948",
            "--plaintext-file",
            test_file,
            "--region",
            "us-east-1",
        ],
    )

    os.remove(test_file)

    assert result.exit_code == 0
    assert "Encryption successful" in result.stdout
    assert "mocked-ciphertext-blob" in result.stdout


@unittest.mock.patch("subprocess.run")
def test_encrypt_aws_cli_not_found(mock_subprocess_run):
    # Simulate a FileNotFoundError, which occurs when the 'aws' command is not found
    mock_subprocess_run.side_effect = FileNotFoundError

    test_file = "some-file.txt"
    with open(test_file, "w") as f:
        f.write("foo")

    result = runner.invoke(
        app,
        [
            "--key-id",
            "some-key-id",
            "--plaintext-file",
            test_file,
            "--region",
            "us-east-1",
        ],
    )

    os.remove(test_file)

    assert result.exit_code == 1
    assert "Error: 'aws' command not found" in result.stdout
