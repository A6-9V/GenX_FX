#!/usr/bin/env python3

import os
import sys
import requests
import xml.etree.ElementTree as ET


def get_public_ip():
    """Fetches the public IP address from an external service."""
    try:
        response = requests.get("https://api.ipify.org")
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException:
        return "8.8.8.8"  # Fallback IP


def check_domain_availability(domains):
    """
    Checks the availability of a list of domains using the Namecheap API.
    """
    api_token = os.environ.get("NAMECHEAP_API_TOKEN")
    if not api_token:
        print("Error: NAMECHEAP_API_TOKEN environment variable not set.")
        sys.exit(1)

    # The Namecheap API URL for checking domains
    api_url = "https://api.namecheap.com/xml.response"

    api_user = os.environ.get("NAMECHEAP_API_USER")
    if not api_user:
        print("Error: NAMECHEAP_API_USER environment variable not set.")
        sys.exit(1)

    # For sandox url: https://api.sandbox.namecheap.com/xml.response
    params = {
        "ApiUser": api_user,
        "ApiKey": api_token,
        "UserName": api_user,
        "Command": "namecheap.domains.check",
        "ClientIp": get_public_ip(),
        "DomainList": ",".join(domains),
    }

    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Parse the XML response
        root = ET.fromstring(response.content)

        # Find all DomainCheckResult elements
        for result in root.findall(
            ".//{http://api.namecheap.com/xml.response}DomainCheckResult"
        ):
            domain = result.get("Domain")
            available = result.get("Available")
            print(f"Domain: {domain}, Available: {available}")

    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
        sys.exit(1)
    except ET.ParseError as e:
        print(f"Error parsing XML response: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python domain_check.py <domain1> <domain2> ...")
        sys.exit(1)

    domains_to_check = sys.argv[1:]
    check_domain_availability(domains_to_check)
