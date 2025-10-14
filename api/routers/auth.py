"""
Authentication and User Management API Routes for A6-9V GenX FX
"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.exc import IntegrityError

from api.database.connection import get_db_session
from api.models.trading import User, UserStatus
from api.schemas.user import (
    UserRegistration, UserLogin, UserResponse, TokenResponse,
    RefreshTokenRequest, ErrorResponse
)
from api.auth.jwt_auth import auth_service
from api.auth.dependencies import get_current_user, get_current_active_user
from api.utils.logging import log_authentication_event, log_security_event

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse)
async def register_user(
    user_data: UserRegistration,
    request: Request,
    db: AsyncSession = Depends(get_db_session)
):
    """Register a new user"""
    client_ip = request.client.host if request.client else "unknown"
    
    try:
        # Check if username or email already exists
        existing_user = await db.execute(
            select(User).where(
                or_(User.username == user_data.username, User.email == user_data.email)
            )
        )
        if existing_user.scalar_one_or_none():
            log_authentication_event(
                "registration_failed",
                username=user_data.username,
                client_ip=client_ip,
                success=False,
                reason="Username or email already exists"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already exists"
            )
        
        # Hash password
        password_hash = auth_service.get_password_hash(user_data.password)
        
        # Create new user
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=password_hash,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            status=UserStatus.PENDING,  # Require email verification
            is_verified=False,
            is_active=True,
            can_trade=False,  # Require verification for trading
            can_withdraw=False,
            risk_level="low"
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        # Generate tokens
        token_data = auth_service.create_token_pair(
            str(new_user.id),
            additional_claims={
                "username": new_user.username,
                "email": new_user.email,
                "verified": new_user.is_verified
            }
        )
        
        # Create user response
        user_response = UserResponse(
            id=str(new_user.id),
            username=new_user.username,
            email=new_user.email,
            first_name=new_user.first_name,
            last_name=new_user.last_name,
            status=new_user.status,
            is_verified=new_user.is_verified,
            is_active=new_user.is_active,
            can_trade=new_user.can_trade,
            can_withdraw=new_user.can_withdraw,
            risk_level=new_user.risk_level,
            two_factor_enabled=new_user.two_factor_enabled,
            created_at=new_user.created_at,
            last_login=new_user.last_login
        )
        
        # Log successful registration
        log_authentication_event(
            "registration_success",
            user_id=str(new_user.id),
            username=new_user.username,
            client_ip=client_ip,
            success=True
        )
        
        return TokenResponse(
            access_token=token_data["access_token"],
            refresh_token=token_data["refresh_token"],
            token_type=token_data["token_type"],
            expires_in=token_data["expires_in"],
            user=user_response
        )
        
    except IntegrityError as e:
        await db.rollback()
        log_authentication_event(
            "registration_failed",
            username=user_data.username,
            client_ip=client_ip,
            success=False,
            reason="Database constraint violation"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists"
        )
    except Exception as e:
        await db.rollback()
        log_security_event(
            "registration_error",
            "medium",
            f"User registration failed: {str(e)}",
            client_ip=client_ip,
            additional_data={"username": user_data.username}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login", response_model=TokenResponse)
async def login_user(
    login_data: UserLogin,
    request: Request,
    db: AsyncSession = Depends(get_db_session)
):
    """User login"""
    client_ip = request.client.host if request.client else "unknown"
    
    try:
        # Find user by username or email
        user = await db.execute(
            select(User).where(
                or_(
                    User.username == login_data.username_or_email.lower(),
                    User.email == login_data.username_or_email.lower()
                )
            )
        )
        user = user.scalar_one_or_none()
        
        if not user:
            log_authentication_event(
                "login_failed",
                username=login_data.username_or_email,
                client_ip=client_ip,
                success=False,
                reason="User not found"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Verify password
        if not auth_service.verify_password(login_data.password, user.password_hash):
            log_authentication_event(
                "login_failed",
                user_id=str(user.id),
                username=user.username,
                client_ip=client_ip,
                success=False,
                reason="Invalid password"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Check if user is active
        if not user.is_active or user.status == UserStatus.SUSPENDED:
            log_authentication_event(
                "login_failed",
                user_id=str(user.id),
                username=user.username,
                client_ip=client_ip,
                success=False,
                reason="Account inactive or suspended"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is inactive or suspended"
            )
        
        # Update last login
        user.last_login = datetime.now(timezone.utc)
        await db.commit()
        
        # Generate tokens
        token_expiry = 7200 if login_data.remember_me else 1800  # 2 hours vs 30 minutes
        token_data = auth_service.create_token_pair(
            str(user.id),
            additional_claims={
                "username": user.username,
                "email": user.email,
                "verified": user.is_verified,
                "remember": login_data.remember_me
            }
        )
        
        # Create user response
        user_response = UserResponse(
            id=str(user.id),
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            status=user.status,
            is_verified=user.is_verified,
            is_active=user.is_active,
            can_trade=user.can_trade,
            can_withdraw=user.can_withdraw,
            risk_level=user.risk_level,
            two_factor_enabled=user.two_factor_enabled,
            created_at=user.created_at,
            last_login=user.last_login
        )
        
        # Log successful login
        log_authentication_event(
            "login_success",
            user_id=str(user.id),
            username=user.username,
            client_ip=client_ip,
            success=True
        )
        
        return TokenResponse(
            access_token=token_data["access_token"],
            refresh_token=token_data["refresh_token"],
            token_type=token_data["token_type"],
            expires_in=token_data["expires_in"],
            user=user_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log_security_event(
            "login_error",
            "medium",
            f"User login failed: {str(e)}",
            client_ip=client_ip,
            additional_data={"username_or_email": login_data.username_or_email}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.post("/refresh", response_model=dict)
async def refresh_token(
    token_request: RefreshTokenRequest,
    request: Request
):
    """Refresh access token"""
    client_ip = request.client.host if request.client else "unknown"
    
    try:
        # Refresh the token
        new_token_data = auth_service.refresh_access_token(token_request.refresh_token)
        
        # Extract user ID for logging
        payload = auth_service.verify_token(token_request.refresh_token, "refresh")
        user_id = payload.get("sub")
        
        log_authentication_event(
            "token_refresh",
            user_id=user_id,
            client_ip=client_ip,
            success=True
        )
        
        return new_token_data
        
    except HTTPException as e:
        log_authentication_event(
            "token_refresh_failed",
            client_ip=client_ip,
            success=False,
            reason=str(e.detail)
        )
        raise
    except Exception as e:
        log_security_event(
            "token_refresh_error",
            "medium",
            f"Token refresh failed: {str(e)}",
            client_ip=client_ip
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user information"""
    return UserResponse(
        id=str(current_user.id),
        username=current_user.username,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        status=current_user.status,
        is_verified=current_user.is_verified,
        is_active=current_user.is_active,
        can_trade=current_user.can_trade,
        can_withdraw=current_user.can_withdraw,
        risk_level=current_user.risk_level,
        two_factor_enabled=current_user.two_factor_enabled,
        created_at=current_user.created_at,
        last_login=current_user.last_login
    )

@router.post("/logout")
async def logout_user(
    request: Request,
    current_user: User = Depends(get_current_active_user)
):
    """User logout (client-side token invalidation)"""
    client_ip = request.client.host if request.client else "unknown"
    
    # Note: In a production system, you might want to maintain a token blacklist
    # For now, we'll just log the logout event and let the client handle token removal
    
    log_authentication_event(
        "logout",
        user_id=str(current_user.id),
        username=current_user.username,
        client_ip=client_ip,
        success=True
    )
    
    return {"message": "Successfully logged out"}

@router.get("/verify-token")
async def verify_token(
    current_user: User = Depends(get_current_active_user)
):
    """Verify if the current token is valid"""
    return {
        "valid": True,
        "user_id": str(current_user.id),
        "username": current_user.username
    }