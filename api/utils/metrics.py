"""
Prometheus Metrics for A6-9V GenX FX Application Monitoring
"""

import time
from typing import Dict, Optional
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    Info,
    Summary,
    CollectorRegistry,
    generate_latest,
    CONTENT_TYPE_LATEST,
)
from fastapi import Request, Response

# Create a custom registry for our application metrics
REGISTRY = CollectorRegistry()

# Application info
APP_INFO = Info("genx_fx_app", "Application information", registry=REGISTRY)
APP_INFO.info({"version": "1.2.0", "name": "GenX_FX", "organization": "A6-9V"})

# HTTP Request Metrics
HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
    registry=REGISTRY,
)

HTTP_REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint", "status"],
    buckets=[0.001, 0.01, 0.1, 0.5, 1.0, 2.5, 5.0, 10.0],
    registry=REGISTRY,
)

HTTP_REQUEST_SIZE = Summary(
    "http_request_size_bytes",
    "HTTP request size in bytes",
    ["method", "endpoint"],
    registry=REGISTRY,
)

HTTP_RESPONSE_SIZE = Summary(
    "http_response_size_bytes",
    "HTTP response size in bytes",
    ["method", "endpoint", "status"],
    registry=REGISTRY,
)

# Authentication Metrics
AUTH_REQUESTS_TOTAL = Counter(
    "auth_requests_total",
    "Total authentication requests",
    ["type", "status"],
    registry=REGISTRY,
)

AUTH_TOKEN_GENERATION = Counter(
    "auth_tokens_generated_total",
    "Total tokens generated",
    ["token_type"],
    registry=REGISTRY,
)

ACTIVE_SESSIONS = Gauge(
    "active_sessions_current",
    "Current number of active user sessions",
    registry=REGISTRY,
)

# Database Metrics
DB_CONNECTIONS = Gauge(
    "database_connections_active", "Active database connections", registry=REGISTRY
)

DB_QUERY_DURATION = Histogram(
    "database_query_duration_seconds",
    "Database query duration in seconds",
    ["operation", "table"],
    buckets=[0.001, 0.01, 0.1, 0.5, 1.0, 2.5, 5.0],
    registry=REGISTRY,
)

DB_QUERY_TOTAL = Counter(
    "database_queries_total",
    "Total database queries",
    ["operation", "table", "status"],
    registry=REGISTRY,
)

# Trading Metrics
TRADES_TOTAL = Counter(
    "trades_total",
    "Total number of trades executed",
    ["symbol", "side", "status"],
    registry=REGISTRY,
)

TRADE_VOLUME = Summary(
    "trade_volume_usd", "Trading volume in USD", ["symbol", "side"], registry=REGISTRY
)

ORDERS_TOTAL = Counter(
    "orders_total",
    "Total number of orders placed",
    ["symbol", "side", "type", "status"],
    registry=REGISTRY,
)

ACCOUNT_BALANCE = Gauge(
    "account_balance_usd",
    "Account balance in USD",
    ["user_id", "currency"],
    registry=REGISTRY,
)

POSITIONS_OPEN = Gauge(
    "positions_open_current",
    "Current number of open positions",
    ["symbol"],
    registry=REGISTRY,
)

# Market Data Metrics
MARKET_DATA_UPDATES = Counter(
    "market_data_updates_total",
    "Total market data updates received",
    ["symbol", "source"],
    registry=REGISTRY,
)

MARKET_DATA_LATENCY = Histogram(
    "market_data_latency_seconds",
    "Market data update latency in seconds",
    ["symbol", "source"],
    buckets=[0.001, 0.01, 0.1, 0.5, 1.0],
    registry=REGISTRY,
)

WEBSOCKET_CONNECTIONS = Gauge(
    "websocket_connections_active",
    "Active WebSocket connections",
    ["type"],
    registry=REGISTRY,
)

# System Metrics
MEMORY_USAGE = Gauge(
    "memory_usage_bytes", "Memory usage in bytes", ["type"], registry=REGISTRY
)

CPU_USAGE = Gauge("cpu_usage_percent", "CPU usage percentage", registry=REGISTRY)

DISK_USAGE = Gauge(
    "disk_usage_bytes",
    "Disk usage in bytes",
    ["mount_point", "type"],
    registry=REGISTRY,
)

# Error Metrics
ERRORS_TOTAL = Counter(
    "errors_total",
    "Total number of errors",
    ["type", "severity", "component"],
    registry=REGISTRY,
)

SECURITY_EVENTS = Counter(
    "security_events_total",
    "Total security events",
    ["event_type", "severity"],
    registry=REGISTRY,
)

# Rate Limiting Metrics
RATE_LIMIT_HITS = Counter(
    "rate_limit_hits_total",
    "Total rate limit hits",
    ["endpoint", "client_ip"],
    registry=REGISTRY,
)

RATE_LIMIT_BLOCKS = Counter(
    "rate_limit_blocks_total",
    "Total requests blocked by rate limiting",
    ["endpoint", "client_ip"],
    registry=REGISTRY,
)

# API Key Usage Metrics
API_KEY_USAGE = Counter(
    "api_key_usage_total",
    "API key usage count",
    ["key_id", "endpoint"],
    registry=REGISTRY,
)

# External Service Metrics
EXTERNAL_API_CALLS = Counter(
    "external_api_calls_total",
    "Total external API calls",
    ["service", "endpoint", "status"],
    registry=REGISTRY,
)

EXTERNAL_API_DURATION = Histogram(
    "external_api_duration_seconds",
    "External API call duration in seconds",
    ["service", "endpoint"],
    buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0],
    registry=REGISTRY,
)


class MetricsCollector:
    """Centralized metrics collection and management"""

    def __init__(self):
        self.start_time = time.time()

    def record_http_request(
        self,
        method: str,
        endpoint: str,
        status_code: int,
        duration: float,
        request_size: Optional[int] = None,
        response_size: Optional[int] = None,
    ):
        """Record HTTP request metrics"""
        status = str(status_code)

        HTTP_REQUESTS_TOTAL.labels(
            method=method, endpoint=endpoint, status=status
        ).inc()

        HTTP_REQUEST_DURATION.labels(
            method=method, endpoint=endpoint, status=status
        ).observe(duration)

        if request_size is not None:
            HTTP_REQUEST_SIZE.labels(method=method, endpoint=endpoint).observe(
                request_size
            )

        if response_size is not None:
            HTTP_RESPONSE_SIZE.labels(
                method=method, endpoint=endpoint, status=status
            ).observe(response_size)

    def record_auth_event(
        self, auth_type: str, success: bool, token_type: Optional[str] = None
    ):
        """Record authentication metrics"""
        status = "success" if success else "failure"

        AUTH_REQUESTS_TOTAL.labels(type=auth_type, status=status).inc()

        if success and token_type:
            AUTH_TOKEN_GENERATION.labels(token_type=token_type).inc()

    def update_active_sessions(self, count: int):
        """Update active sessions count"""
        ACTIVE_SESSIONS.set(count)

    def record_db_query(
        self, operation: str, table: str, duration: float, success: bool = True
    ):
        """Record database query metrics"""
        status = "success" if success else "failure"

        DB_QUERY_TOTAL.labels(operation=operation, table=table, status=status).inc()

        if success:
            DB_QUERY_DURATION.labels(operation=operation, table=table).observe(duration)

    def update_db_connections(self, count: int):
        """Update database connections count"""
        DB_CONNECTIONS.set(count)

    def record_trade(
        self, symbol: str, side: str, status: str, volume_usd: Optional[float] = None
    ):
        """Record trading metrics"""
        TRADES_TOTAL.labels(symbol=symbol, side=side, status=status).inc()

        if volume_usd is not None and status == "filled":
            TRADE_VOLUME.labels(symbol=symbol, side=side).observe(volume_usd)

    def record_order(self, symbol: str, side: str, order_type: str, status: str):
        """Record order metrics"""
        ORDERS_TOTAL.labels(
            symbol=symbol, side=side, type=order_type, status=status
        ).inc()

    def update_account_balance(self, user_id: str, currency: str, balance: float):
        """Update account balance"""
        ACCOUNT_BALANCE.labels(user_id=user_id, currency=currency).set(balance)

    def update_open_positions(self, symbol: str, count: int):
        """Update open positions count"""
        POSITIONS_OPEN.labels(symbol=symbol).set(count)

    def record_market_data_update(
        self, symbol: str, source: str, latency: Optional[float] = None
    ):
        """Record market data metrics"""
        MARKET_DATA_UPDATES.labels(symbol=symbol, source=source).inc()

        if latency is not None:
            MARKET_DATA_LATENCY.labels(symbol=symbol, source=source).observe(latency)

    def update_websocket_connections(self, connection_type: str, count: int):
        """Update WebSocket connections count"""
        WEBSOCKET_CONNECTIONS.labels(type=connection_type).set(count)

    def record_error(self, error_type: str, severity: str, component: str):
        """Record error metrics"""
        ERRORS_TOTAL.labels(
            type=error_type, severity=severity, component=component
        ).inc()

    def record_security_event(self, event_type: str, severity: str):
        """Record security event metrics"""
        SECURITY_EVENTS.labels(event_type=event_type, severity=severity).inc()

    def record_rate_limit_hit(
        self, endpoint: str, client_ip: str, blocked: bool = False
    ):
        """Record rate limiting metrics"""
        RATE_LIMIT_HITS.labels(endpoint=endpoint, client_ip=client_ip).inc()

        if blocked:
            RATE_LIMIT_BLOCKS.labels(endpoint=endpoint, client_ip=client_ip).inc()

    def record_api_key_usage(self, key_id: str, endpoint: str):
        """Record API key usage"""
        API_KEY_USAGE.labels(key_id=key_id, endpoint=endpoint).inc()

    def record_external_api_call(
        self, service: str, endpoint: str, status_code: int, duration: float
    ):
        """Record external API call metrics"""
        EXTERNAL_API_CALLS.labels(
            service=service, endpoint=endpoint, status=str(status_code)
        ).inc()

        EXTERNAL_API_DURATION.labels(service=service, endpoint=endpoint).observe(
            duration
        )

    def update_system_metrics(
        self,
        memory_rss: Optional[int] = None,
        memory_vms: Optional[int] = None,
        cpu_percent: Optional[float] = None,
        disk_usage: Optional[Dict[str, int]] = None,
    ):
        """Update system resource metrics"""
        if memory_rss is not None:
            MEMORY_USAGE.labels(type="rss").set(memory_rss)

        if memory_vms is not None:
            MEMORY_USAGE.labels(type="vms").set(memory_vms)

        if cpu_percent is not None:
            CPU_USAGE.set(cpu_percent)

        if disk_usage:
            for mount_point, usage_data in disk_usage.items():
                for usage_type, value in usage_data.items():
                    DISK_USAGE.labels(mount_point=mount_point, type=usage_type).set(
                        value
                    )

    def get_metrics_content(self) -> bytes:
        """Get Prometheus metrics in the expected format"""
        return generate_latest(REGISTRY)

    def get_uptime_seconds(self) -> float:
        """Get application uptime in seconds"""
        return time.time() - self.start_time


# Global metrics collector instance
metrics = MetricsCollector()


def get_metrics_response() -> Response:
    """Generate Prometheus metrics response"""
    content = metrics.get_metrics_content()
    return Response(content=content, media_type=CONTENT_TYPE_LATEST)
