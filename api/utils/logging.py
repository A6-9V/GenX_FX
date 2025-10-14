"""
Structured Logging System for A6-9V GenX FX
"""
import json
import sys
import os
import logging
import structlog
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path

def setup_structured_logging(
    level: str = "INFO",
    json_format: bool = True,
    log_file: Optional[str] = None
) -> None:
    """Setup structured logging with JSON format"""
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="ISO"),
            structlog.processors.CallsiteParameterAdder(
                parameters=[structlog.processors.CallsiteParameter.FUNC_NAME]
            ),
            structlog.processors.JSONRenderer() if json_format else structlog.dev.ConsoleRenderer()
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, level.upper(), logging.INFO)
        ),
        logger_factory=structlog.WriteLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure standard logging
    logging_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create formatters
    if json_format:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    # Setup handlers
    handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging_level)
    handlers.append(console_handler)
    
    # File handler if specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging_level)
        handlers.append(file_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=logging_level,
        handlers=handlers,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Reduce noise from external libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record):
        """Format log record as JSON"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add extra fields
        if hasattr(record, 'user_id'):
            log_entry["user_id"] = record.user_id
        
        if hasattr(record, 'request_id'):
            log_entry["request_id"] = record.request_id
        
        if hasattr(record, 'client_ip'):
            log_entry["client_ip"] = record.client_ip
        
        if hasattr(record, 'duration'):
            log_entry["duration"] = record.duration
        
        if hasattr(record, 'status_code'):
            log_entry["status_code"] = record.status_code
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add any extra fields from extra parameter
        if hasattr(record, '__dict__'):
            for key, value in record.__dict__.items():
                if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 
                              'pathname', 'filename', 'module', 'lineno', 
                              'funcName', 'created', 'msecs', 'relativeCreated',
                              'thread', 'threadName', 'processName', 'process',
                              'exc_info', 'exc_text', 'stack_info']:
                    if not key.startswith('_') and key not in log_entry:
                        try:
                            json.dumps(value)  # Test if serializable
                            log_entry[key] = value
                        except (TypeError, ValueError):
                            log_entry[key] = str(value)
        
        return json.dumps(log_entry, ensure_ascii=False)

class LoggerMixin:
    """Mixin to add structured logging to classes"""
    
    @property
    def logger(self):
        """Get structured logger for this class"""
        if not hasattr(self, '_logger'):
            self._logger = structlog.get_logger(self.__class__.__name__)
        return self._logger

def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance"""
    return structlog.get_logger(name)

def log_api_request(
    method: str,
    path: str,
    status_code: int,
    duration: float,
    client_ip: str = None,
    user_id: str = None,
    request_id: str = None
):
    """Log API request with structured data"""
    logger = get_logger("api.request")
    
    log_data = {
        "method": method,
        "path": path,
        "status_code": status_code,
        "duration": round(duration, 4),
    }
    
    if client_ip:
        log_data["client_ip"] = client_ip
    
    if user_id:
        log_data["user_id"] = user_id
    
    if request_id:
        log_data["request_id"] = request_id
    
    if status_code >= 500:
        logger.error("API request failed", **log_data)
    elif status_code >= 400:
        logger.warning("API client error", **log_data)
    else:
        logger.info("API request", **log_data)

def log_authentication_event(
    event_type: str,
    user_id: str = None,
    username: str = None,
    client_ip: str = None,
    success: bool = True,
    reason: str = None
):
    """Log authentication events"""
    logger = get_logger("auth")
    
    log_data = {
        "event_type": event_type,
        "success": success,
    }
    
    if user_id:
        log_data["user_id"] = user_id
    
    if username:
        log_data["username"] = username
    
    if client_ip:
        log_data["client_ip"] = client_ip
    
    if reason:
        log_data["reason"] = reason
    
    if success:
        logger.info("Authentication event", **log_data)
    else:
        logger.warning("Authentication failed", **log_data)

def log_security_event(
    event_type: str,
    severity: str,
    description: str,
    client_ip: str = None,
    user_id: str = None,
    additional_data: Dict[str, Any] = None
):
    """Log security-related events"""
    logger = get_logger("security")
    
    log_data = {
        "event_type": event_type,
        "severity": severity,
        "description": description,
    }
    
    if client_ip:
        log_data["client_ip"] = client_ip
    
    if user_id:
        log_data["user_id"] = user_id
    
    if additional_data:
        log_data.update(additional_data)
    
    if severity in ["critical", "high"]:
        logger.error("Security event", **log_data)
    elif severity == "medium":
        logger.warning("Security event", **log_data)
    else:
        logger.info("Security event", **log_data)

def log_business_event(
    event_type: str,
    user_id: str,
    details: Dict[str, Any] = None
):
    """Log business logic events (trades, orders, etc.)"""
    logger = get_logger("business")
    
    log_data = {
        "event_type": event_type,
        "user_id": user_id,
    }
    
    if details:
        log_data.update(details)
    
    logger.info("Business event", **log_data)

def log_error(
    error: Exception,
    context: str = None,
    user_id: str = None,
    additional_data: Dict[str, Any] = None
):
    """Log errors with context"""
    logger = get_logger("error")
    
    log_data = {
        "error_type": type(error).__name__,
        "error_message": str(error),
    }
    
    if context:
        log_data["context"] = context
    
    if user_id:
        log_data["user_id"] = user_id
    
    if additional_data:
        log_data.update(additional_data)
    
    logger.error("Application error", **log_data, exc_info=True)

# Initialize logging based on environment
def initialize_logging():
    """Initialize logging system based on environment variables"""
    log_level = os.getenv("LOG_LEVEL", "INFO")
    json_format = os.getenv("LOG_FORMAT", "json").lower() == "json"
    log_file = os.getenv("LOG_FILE")
    
    setup_structured_logging(
        level=log_level,
        json_format=json_format,
        log_file=log_file
    )
    
    logger = get_logger("startup")
    logger.info("Logging system initialized", 
                level=log_level, 
                format="json" if json_format else "console",
                log_file=log_file)

# Auto-initialize if imported
if __name__ != "__main__":
    initialize_logging()