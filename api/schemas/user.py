"""
User Management Pydantic Schemas for A6-9V GenX FX
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field, validator
import re

class UserBase(BaseModel):
    """Base user schema"""
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: EmailStr = Field(..., description="Email address")
    first_name: Optional[str] = Field(None, max_length=100, description="First name")
    last_name: Optional[str] = Field(None, max_length=100, description="Last name")

class UserRegistration(UserBase):
    """User registration schema"""
    password: str = Field(..., min_length=8, description="Password")
    confirm_password: str = Field(..., description="Password confirmation")
    
    @validator("password")
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")
        
        return v
    
    @validator("username")
    def validate_username(cls, v):
        """Validate username format"""
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("Username can only contain letters, numbers, hyphens, and underscores")
        return v.lower()
    
    @validator("confirm_password")
    def passwords_match(cls, v, values):
        """Validate password confirmation"""
        if 'password' in values and v != values['password']:
            raise ValueError("Passwords do not match")
        return v

class UserLogin(BaseModel):
    """User login schema"""
    username_or_email: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password")
    remember_me: bool = Field(False, description="Remember login")

class UserResponse(UserBase):
    """User response schema"""
    id: str = Field(..., description="User ID")
    status: str = Field(..., description="Account status")
    is_verified: bool = Field(..., description="Email verification status")
    is_active: bool = Field(..., description="Account active status")
    can_trade: bool = Field(..., description="Trading permission")
    can_withdraw: bool = Field(..., description="Withdrawal permission")
    risk_level: str = Field(..., description="Risk level")
    two_factor_enabled: bool = Field(..., description="2FA status")
    created_at: datetime = Field(..., description="Account creation time")
    last_login: Optional[datetime] = Field(None, description="Last login time")
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    """User profile update schema"""
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = Field(None)

class PasswordChange(BaseModel):
    """Password change schema"""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")
    confirm_password: str = Field(..., description="New password confirmation")
    
    @validator("new_password")
    def validate_new_password(cls, v):
        """Validate new password strength"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")
        
        return v
    
    @validator("confirm_password")
    def passwords_match(cls, v, values):
        """Validate password confirmation"""
        if 'new_password' in values and v != values['new_password']:
            raise ValueError("Passwords do not match")
        return v

class PasswordReset(BaseModel):
    """Password reset request schema"""
    email: EmailStr = Field(..., description="Email address")

class PasswordResetConfirm(BaseModel):
    """Password reset confirmation schema"""
    token: str = Field(..., description="Reset token")
    new_password: str = Field(..., min_length=8, description="New password")
    confirm_password: str = Field(..., description="New password confirmation")
    
    @validator("new_password")
    def validate_new_password(cls, v):
        """Validate new password strength"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")
        
        return v
    
    @validator("confirm_password")
    def passwords_match(cls, v, values):
        """Validate password confirmation"""
        if 'new_password' in values and v != values['new_password']:
            raise ValueError("Passwords do not match")
        return v

class TokenResponse(BaseModel):
    """Token response schema"""
    access_token: str = Field(..., description="Access token")
    refresh_token: str = Field(..., description="Refresh token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")
    user: UserResponse = Field(..., description="User information")

class RefreshTokenRequest(BaseModel):
    """Refresh token request schema"""
    refresh_token: str = Field(..., description="Refresh token")

class EmailVerification(BaseModel):
    """Email verification schema"""
    token: str = Field(..., description="Verification token")

class TwoFactorSetup(BaseModel):
    """Two-factor authentication setup schema"""
    enable: bool = Field(..., description="Enable or disable 2FA")
    code: Optional[str] = Field(None, description="2FA code for verification")

class TwoFactorVerify(BaseModel):
    """Two-factor authentication verification schema"""
    code: str = Field(..., min_length=6, max_length=6, description="2FA code")

class UserPreferences(BaseModel):
    """User preferences schema"""
    timezone: Optional[str] = Field("UTC", description="User timezone")
    language: Optional[str] = Field("en", description="Preferred language")
    currency: Optional[str] = Field("USD", description="Base currency")
    notifications: Optional[Dict[str, bool]] = Field(
        default_factory=lambda: {
            "email_alerts": True,
            "trade_notifications": True,
            "price_alerts": True,
            "security_alerts": True
        },
        description="Notification preferences"
    )
    
class APIKeyRequest(BaseModel):
    """API key generation request"""
    name: str = Field(..., min_length=1, max_length=100, description="API key name")
    permissions: list[str] = Field(default_factory=list, description="API key permissions")

class APIKeyResponse(BaseModel):
    """API key response"""
    key_id: str = Field(..., description="API key ID")
    name: str = Field(..., description="API key name")
    key: str = Field(..., description="API key (only shown once)")
    permissions: list[str] = Field(..., description="API key permissions")
    created_at: datetime = Field(..., description="Creation timestamp")

class UserStats(BaseModel):
    """User statistics schema"""
    total_trades: int = Field(0, description="Total number of trades")
    successful_trades: int = Field(0, description="Number of successful trades")
    total_volume: float = Field(0.0, description="Total trading volume")
    profit_loss: float = Field(0.0, description="Total profit/loss")
    win_rate: float = Field(0.0, description="Win rate percentage")
    active_positions: int = Field(0, description="Number of active positions")
    account_balance: float = Field(0.0, description="Account balance")
    
class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")

class SuccessResponse(BaseModel):
    """Success response schema"""
    message: str = Field(..., description="Success message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")