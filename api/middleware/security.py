"""
Security Middleware for A6-9V GenX FX
"""
import time
import os
from typing import Callable, Dict, Any
from fastapi import Request, Response, HTTPException, status
from fastapi.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import logging
from collections import defaultdict, deque
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # HSTS for HTTPS
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        
        # Content Security Policy
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        response.headers["Content-Security-Policy"] = csp
        
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware with sliding window"""
    
    def __init__(
        self, 
        app: ASGIApp,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        burst_limit: int = 10
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.burst_limit = burst_limit
        
        # Storage for request tracking
        self.minute_windows: Dict[str, deque] = defaultdict(deque)
        self.hour_windows: Dict[str, deque] = defaultdict(deque)
        self.burst_windows: Dict[str, deque] = defaultdict(deque)
        
        # Cleanup interval
        self.last_cleanup = time.time()
        self.cleanup_interval = 300  # 5 minutes
        
    def get_client_identifier(self, request: Request) -> str:
        """Get client identifier for rate limiting"""
        # Check for real IP behind proxy
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def cleanup_old_requests(self):
        """Remove old request records to prevent memory leaks"""
        current_time = time.time()
        
        # Only cleanup periodically
        if current_time - self.last_cleanup < self.cleanup_interval:
            return
        
        cutoff_minute = current_time - 60
        cutoff_hour = current_time - 3600
        cutoff_burst = current_time - 1  # 1 second burst window
        
        # Clean minute windows
        for client_id in list(self.minute_windows.keys()):
            window = self.minute_windows[client_id]
            while window and window[0] < cutoff_minute:
                window.popleft()
            if not window:
                del self.minute_windows[client_id]
        
        # Clean hour windows
        for client_id in list(self.hour_windows.keys()):
            window = self.hour_windows[client_id]
            while window and window[0] < cutoff_hour:
                window.popleft()
            if not window:
                del self.hour_windows[client_id]
        
        # Clean burst windows
        for client_id in list(self.burst_windows.keys()):
            window = self.burst_windows[client_id]
            while window and window[0] < cutoff_burst:
                window.popleft()
            if not window:
                del self.burst_windows[client_id]
        
        self.last_cleanup = current_time
    
    def is_rate_limited(self, client_id: str) -> tuple[bool, str, int]:
        """Check if client is rate limited"""
        current_time = time.time()
        
        # Check burst limit (requests per second)
        burst_window = self.burst_windows[client_id]
        burst_cutoff = current_time - 1
        
        while burst_window and burst_window[0] < burst_cutoff:
            burst_window.popleft()
        
        if len(burst_window) >= self.burst_limit:
            retry_after = int(burst_window[0] + 1 - current_time) + 1
            return True, "Too many requests in burst window", retry_after
        
        # Check minute limit
        minute_window = self.minute_windows[client_id]
        minute_cutoff = current_time - 60
        
        while minute_window and minute_window[0] < minute_cutoff:
            minute_window.popleft()
        
        if len(minute_window) >= self.requests_per_minute:
            retry_after = int(minute_window[0] + 60 - current_time) + 1
            return True, "Rate limit exceeded (per minute)", retry_after
        
        # Check hour limit
        hour_window = self.hour_windows[client_id]
        hour_cutoff = current_time - 3600
        
        while hour_window and hour_window[0] < hour_cutoff:
            hour_window.popleft()
        
        if len(hour_window) >= self.requests_per_hour:
            retry_after = int(hour_window[0] + 3600 - current_time) + 1
            return True, "Rate limit exceeded (per hour)", retry_after
        
        return False, "", 0
    
    def record_request(self, client_id: str):
        """Record a request for rate limiting"""
        current_time = time.time()
        
        self.burst_windows[client_id].append(current_time)
        self.minute_windows[client_id].append(current_time)
        self.hour_windows[client_id].append(current_time)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for health checks and static files
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        # Cleanup old records periodically
        self.cleanup_old_requests()
        
        # Get client identifier
        client_id = self.get_client_identifier(request)
        
        # Check rate limits
        is_limited, message, retry_after = self.is_rate_limited(client_id)
        
        if is_limited:
            logger.warning(f"Rate limit exceeded for client {client_id}: {message}")
            
            return Response(
                content=f'{{"error": "Rate limit exceeded", "message": "{message}", "retry_after": {retry_after}}}',
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit-Minute": str(self.requests_per_minute),
                    "X-RateLimit-Limit-Hour": str(self.requests_per_hour),
                    "X-RateLimit-Burst": str(self.burst_limit),
                    "Content-Type": "application/json"
                }
            )
        
        # Record the request
        self.record_request(client_id)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers to successful responses
        response.headers["X-RateLimit-Limit-Minute"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Limit-Hour"] = str(self.requests_per_hour)
        response.headers["X-RateLimit-Remaining-Minute"] = str(
            max(0, self.requests_per_minute - len(self.minute_windows[client_id]))
        )
        response.headers["X-RateLimit-Remaining-Hour"] = str(
            max(0, self.requests_per_hour - len(self.hour_windows[client_id]))
        )
        
        return response

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests for monitoring and security"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Get client info
        client_ip = request.client.host if request.client else "unknown"
        forwarded_for = request.headers.get("X-Forwarded-For")
        user_agent = request.headers.get("User-Agent", "")
        
        # Process request
        response = await call_next(request)
        
        # Calculate response time
        process_time = time.time() - start_time
        
        # Log request details
        log_data = {
            "method": request.method,
            "url": str(request.url),
            "client_ip": client_ip,
            "forwarded_for": forwarded_for,
            "user_agent": user_agent,
            "status_code": response.status_code,
            "response_time": round(process_time, 4),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Log level based on status code
        if response.status_code >= 500:
            logger.error(f"Request failed: {log_data}")
        elif response.status_code >= 400:
            logger.warning(f"Client error: {log_data}")
        else:
            logger.info(f"Request: {request.method} {request.url.path} -> {response.status_code} ({process_time:.3f}s)")
        
        # Add response time header
        response.headers["X-Response-Time"] = f"{process_time:.4f}s"
        
        return response

def get_rate_limit_config() -> dict:
    """Get rate limiting configuration from environment"""
    return {
        "requests_per_minute": int(os.getenv("RATE_LIMIT_REQUESTS", "60")),
        "requests_per_hour": int(os.getenv("RATE_LIMIT_WINDOW", "1000")),
        "burst_limit": int(os.getenv("RATE_LIMIT_BURST", "10"))
    }