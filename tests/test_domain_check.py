import unittest
from unittest.mock import patch, MagicMock
import subprocess
import os
import sys
from io import StringIO

# Add the plugin directory to the Python path
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "genx-cli", "plugins")
    )
)

from domain_check import check_domain_availability


class TestDomainCheck(unittest.TestCase):
    @patch("requests.get")
    def test_check_domain_availability_success(self, mock_get):
        # Mock the environment variables
        os.environ["NAMECHEAP_API_TOKEN"] = "test_token"
        os.environ["NAMECHEAP_API_USER"] = "test_user"

        # Mock the API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"""<?xml version="1.0" encoding="UTF-8"?>
<ApiResponse xmlns="http://api.namecheap.com/xml.response" Status="OK">
    <Errors />
    <CommandResponse Type="namecheap.domains.check">
        <DomainCheckResult Domain="google.com" Available="false" />
        <DomainCheckResult Domain="another-domain.com" Available="true" />
    </CommandResponse>
</ApiResponse>
"""
        mock_get.return_value = mock_response

        # Redirect stdout to capture the output
        captured_output = StringIO()
        sys.stdout = captured_output

        # Call the function
        check_domain_availability(["google.com", "another-domain.com"])

        # Restore stdout
        sys.stdout = sys.__stdout__

        # Check the output
        self.assertIn(
            "Domain: google.com, Available: false", captured_output.getvalue()
        )
        self.assertIn(
            "Domain: another-domain.com, Available: true", captured_output.getvalue()
        )

    @patch("subprocess.run")
    def test_domain_check_command_success(self, mock_run):
        # Mock the subprocess run
        mock_result = MagicMock()
        mock_result.stdout = "Domain: test.com, Available: true"
        mock_result.stderr = ""
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        # Run the command
        result = subprocess.run(
            ["node", "genx-cli/cli.js", "domain-check", "test.com"],
            capture_output=True,
            text=True,
        )

        # Check that the command was called with the correct arguments
        mock_run.assert_called_with(
            ["node", "genx-cli/cli.js", "domain-check", "test.com"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("Domain: test.com, Available: true", result.stdout)

    def test_domain_check_command_no_domains(self):
        # Run the command with no domains
        result = subprocess.run(
            ["node", "genx-cli/cli.js", "domain-check"], capture_output=True, text=True
        )

        # Check the error message
        self.assertIn(
            "Error: Please specify one or more domains to check.", result.stderr
        )
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
