"""
NameCheap API Service Integration for A6-9V GenX FX
"""

import os
import aiohttp
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class NameCheapService:
    """NameCheap API service for domain management"""

    def __init__(self):
        self.api_key = os.getenv("NAMECHEAP_API_TOKEN")
        self.api_user = os.getenv("NAMECHEAP_API_USER", "A6-9V")
        self.client_ip = os.getenv("NAMECHEAP_CLIENT_IP", "127.0.0.1")

        # Use sandbox for development
        self.api_url = os.getenv(
            "NAMECHEAP_API_URL", "https://api.sandbox.namecheap.com/xml.response"
        )

        self.session = None

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def _make_request(self, command: str, extra_params: Dict = None) -> Dict:
        """Make authenticated request to NameCheap API"""
        if not self.api_key:
            raise ValueError("NameCheap API token not configured")

        params = {
            "ApiUser": self.api_user,
            "ApiKey": self.api_key,
            "UserName": self.api_user,
            "Command": command,
            "ClientIp": self.client_ip,
        }

        if extra_params:
            params.update(extra_params)

        try:
            async with self.session.get(self.api_url, params=params) as response:
                response_text = await response.text()

                # Parse XML response
                root = ET.fromstring(response_text)

                # Check for API errors
                errors = root.find(".//Errors")
                if errors is not None and len(errors) > 0:
                    error_msg = (
                        errors[0].text if errors[0].text else "Unknown API error"
                    )
                    logger.error(f"NameCheap API error: {error_msg}")
                    raise Exception(f"NameCheap API error: {error_msg}")

                return self._parse_xml_response(root, command)

        except Exception as e:
            logger.error(f"NameCheap API request failed: {e}")
            raise

    def _parse_xml_response(self, root: ET.Element, command: str) -> Dict:
        """Parse XML response based on command type"""
        result = {"status": "success", "timestamp": datetime.now().isoformat()}

        if command == "namecheap.domains.getList":
            domains = []
            domain_list = root.find(".//DomainGetListResult")
            if domain_list is not None:
                for domain in domain_list.findall("Domain"):
                    domains.append(
                        {
                            "name": domain.get("Name"),
                            "user": domain.get("User"),
                            "created": domain.get("Created"),
                            "expires": domain.get("Expires"),
                            "is_expired": domain.get("IsExpired") == "true",
                            "is_locked": domain.get("IsLocked") == "true",
                            "auto_renew": domain.get("AutoRenew") == "true",
                        }
                    )
            result["domains"] = domains

        elif command == "namecheap.domains.check":
            availability = []
            check_result = root.find(".//DomainCheckResult")
            if check_result is not None:
                for domain in check_result.findall("Domain"):
                    availability.append(
                        {
                            "domain": domain.get("Domain"),
                            "available": domain.get("Available") == "true",
                            "error_no": domain.get("ErrorNo"),
                            "description": domain.get("Description"),
                        }
                    )
            result["availability"] = availability

        elif command == "namecheap.domains.dns.getHosts":
            hosts = []
            dns_result = root.find(".//DomainDNSGetHostsResult")
            if dns_result is not None:
                for host in dns_result.findall("Host"):
                    hosts.append(
                        {
                            "host_id": host.get("HostId"),
                            "name": host.get("Name"),
                            "type": host.get("Type"),
                            "address": host.get("Address"),
                            "mx_pref": host.get("MXPref"),
                            "ttl": host.get("TTL"),
                        }
                    )
            result["hosts"] = hosts

        return result

    async def get_domain_list(self) -> Dict:
        """Get list of domains in account"""
        return await self._make_request("namecheap.domains.getList")

    async def check_domain_availability(self, domains: List[str]) -> Dict:
        """Check if domains are available for registration"""
        domain_list = ",".join(domains)
        return await self._make_request(
            "namecheap.domains.check", {"DomainList": domain_list}
        )

    async def get_dns_hosts(self, domain: str) -> Dict:
        """Get DNS host records for a domain"""
        # Extract domain parts
        parts = domain.split(".")
        if len(parts) < 2:
            raise ValueError("Invalid domain format")

        sld = ".".join(parts[:-1])  # Second Level Domain
        tld = parts[-1]  # Top Level Domain

        return await self._make_request(
            "namecheap.domains.dns.getHosts", {"SLD": sld, "TLD": tld}
        )

    async def set_dns_hosts(self, domain: str, hosts: List[Dict]) -> Dict:
        """Set DNS host records for a domain"""
        parts = domain.split(".")
        if len(parts) < 2:
            raise ValueError("Invalid domain format")

        sld = ".".join(parts[:-1])
        tld = parts[-1]

        params = {"SLD": sld, "TLD": tld}

        # Add host parameters
        for i, host in enumerate(hosts, 1):
            params[f"HostName{i}"] = host.get("name", "@")
            params[f"RecordType{i}"] = host.get("type", "A")
            params[f"Address{i}"] = host["address"]
            params[f"TTL{i}"] = host.get("ttl", "1800")
            if host.get("mx_pref"):
                params[f"MXPref{i}"] = str(host["mx_pref"])

        return await self._make_request("namecheap.domains.dns.setHosts", params)

    async def health_check(self) -> Dict:
        """Check NameCheap API connectivity"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()

            # Simple API test - get domain list
            result = await self.get_domain_list()

            return {
                "service": "namecheap",
                "status": "healthy",
                "api_url": self.api_url,
                "domain_count": len(result.get("domains", [])),
                "last_check": datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                "service": "namecheap",
                "status": "unhealthy",
                "error": str(e),
                "api_url": self.api_url,
                "last_check": datetime.now().isoformat(),
            }


# Singleton instance
namecheap_service = NameCheapService()


# Dependency for FastAPI
async def get_namecheap_service() -> NameCheapService:
    """FastAPI dependency to get NameCheap service"""
    async with namecheap_service as service:
        yield service
