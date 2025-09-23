#!/usr/bin/env python3
"""
AMP Authentication Module
Handles user authentication and session management
"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pathlib import Path

class AMPAuth:
    def __init__(self):
        self.session_token = os.getenv("AMP_TOKEN")
        self.user_id = None
        self.session_hash = None
        if self.session_token:
            self._parse_and_set_token(self.session_token)

    def _parse_and_set_token(self, token: str):
        """Helper to parse a token and set instance variables."""
        token_data = self.parse_token(token)
        if token_data:
            self.user_id = token_data.get("user_id")
            self.session_hash = token_data.get("session_hash")
            self.session_token = token_data.get("full_token")

    def parse_token(self, token: str) -> Dict[str, str]:
        """Parse the session token into components"""
        try:
            # Remove prefix if present
            if token.startswith("sgamp_user_"):
                token = token[11:]  # Remove "sgamp_user_" prefix
            
            # Split by underscore to separate user ID and hash
            parts = token.split("_")
            if len(parts) >= 2:
                user_id = parts[0]
                session_hash = "_".join(parts[1:])
                
                return {
                    "user_id": user_id,
                    "session_hash": session_hash,
                    "full_token": f"sgamp_user_{token}"
                }
            else:
                raise ValueError("Invalid token format")
                
        except Exception as e:
            print(f"Error parsing token: {e}")
            return {}
    
    def authenticate(self, token: str) -> bool:
        """Authenticate using the provided token"""
        print(f"🔐 Authenticating with token...")
        
        # Parse the token
        self._parse_and_set_token(token)
        if not self.user_id:
            print("❌ Invalid token format")
            return False
        
        print(f"✅ Authentication successful!")
        print(f"   User ID: {self.user_id}")
        print(f"   Session: {self.session_hash[:16]}...")
        
        return True
    
    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated"""
        return bool(self.session_token)
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for API requests"""
        if not self.is_authenticated():
            return {}
        
        return {
            "Authorization": f"Bearer {self.session_token}",
            "X-User-ID": self.user_id,
            "X-Session-Hash": self.session_hash
        }
    
    def logout(self):
        """Logout and clear session"""
        self.session_token = None
        self.user_id = None
        self.session_hash = None
        
        print("✅ Logged out successfully")
    
    def get_user_info(self) -> Dict[str, Any]:
        """Get current user information"""
        if not self.is_authenticated():
            return {}
        
        return {
            "user_id": self.user_id,
            "session_hash": self.session_hash,
            "authenticated": self.is_authenticated()
        }

# Global auth instance
amp_auth = AMPAuth()

def authenticate_user(token: str) -> bool:
    """Authenticate user with provided token"""
    return amp_auth.authenticate(token)

def check_auth() -> bool:
    """Check if user is authenticated"""
    return amp_auth.is_authenticated()

def get_auth_headers() -> Dict[str, str]:
    """Get authentication headers"""
    return amp_auth.get_auth_headers()

def logout_user():
    """Logout current user"""
    amp_auth.logout()

def get_user_info() -> Dict[str, Any]:
    """Get current user information"""
    return amp_auth.get_user_info()