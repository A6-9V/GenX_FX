"""
Authentication Dependencies for FastAPI
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from api.auth.jwt_auth import auth_service
from api.database.connection import get_db_session
from api.models.trading import User, UserStatus

# HTTP Bearer token security scheme
security = HTTPBearer(auto_error=False)


async def get_current_user_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> str:
    """Extract and validate bearer token from request"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify token format and extract payload
    try:
        payload = auth_service.verify_token(credentials.credentials)
        return credentials.credentials
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    token: str = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db_session),
) -> User:
    """Get current authenticated user from database"""
    try:
        # Extract user ID from token
        payload = auth_service.verify_token(token)
        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Fetch user from database
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check if user is active
        if not user.is_active or user.status == UserStatus.SUSPENDED:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is inactive or suspended",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active user (alias for consistency)"""
    return current_user


async def get_current_verified_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current verified user (for operations requiring verification)"""
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account verification required for this operation",
        )
    return current_user


async def get_current_trading_user(
    current_user: User = Depends(get_current_verified_user),
) -> User:
    """Get current user with trading permissions"""
    if not current_user.can_trade:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Trading permissions required for this operation",
        )
    return current_user


class RoleChecker:
    """Check if user has required role/permissions"""

    def __init__(self, required_role: str):
        self.required_role = required_role

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        # For now, we'll use a simple role system based on user settings
        user_role = (
            current_user.settings.get("role", "user")
            if current_user.settings
            else "user"
        )

        if user_role != self.required_role and user_role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{self.required_role}' required for this operation",
            )

        return current_user


# Common role checkers
require_admin = RoleChecker("admin")
require_trader = RoleChecker("trader")
require_analyst = RoleChecker("analyst")


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db_session),
) -> Optional[User]:
    """Get user if authenticated, None otherwise (for optional auth endpoints)"""
    if not credentials:
        return None

    try:
        payload = auth_service.verify_token(credentials.credentials)
        user_id = payload.get("sub")

        if not user_id:
            return None

        result = await db.execute(
            select(User).where(User.id == user_id, User.is_active == True)
        )
        return result.scalar_one_or_none()

    except Exception:
        return None
