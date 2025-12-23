"""Request/Response logging middleware for FastAPI.

This middleware automatically logs all API requests and responses with:
- Correlation IDs for request tracing
- Request timing/duration
- Client information
- Response status codes
"""

import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from utils.logging import get_logger

logger = get_logger("api.middleware.logging")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all API requests and responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log details.

        Args:
            request: Incoming HTTP request.
            call_next: Next middleware/handler in chain.

        Returns:
            HTTP response with correlation ID header.
        """
        # Generate correlation ID for request tracing
        correlation_id = str(uuid.uuid4())
        request.state.correlation_id = correlation_id

        # Start timer
        start_time = time.time()

        # Extract request info
        method = request.method
        path = request.url.path
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")

        # Log request
        logger.info(
            f"→ {method} {path}",
            extra={
                "correlation_id": correlation_id,
                "method": method,
                "path": path,
                "query_params": str(request.query_params) if request.query_params else None,
                "client_ip": client_ip,
                "user_agent": user_agent,
            }
        )

        # Process request
        try:
            response = await call_next(request)

            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Log response
            logger.info(
                f"← {method} {path} [{response.status_code}] {duration_ms:.2f}ms",
                extra={
                    "correlation_id": correlation_id,
                    "status_code": response.status_code,
                    "duration_ms": round(duration_ms, 2),
                }
            )

            # Add correlation ID to response headers for client tracing
            response.headers["X-Correlation-ID"] = correlation_id

            return response

        except Exception as exc:
            # Calculate duration even on error
            duration_ms = (time.time() - start_time) * 1000

            # Log error
            logger.error(
                f"✗ {method} {path} [ERROR] {duration_ms:.2f}ms",
                extra={
                    "correlation_id": correlation_id,
                    "duration_ms": round(duration_ms, 2),
                    "error": str(exc),
                    "error_type": type(exc).__name__,
                },
                exc_info=True
            )

            # Re-raise to let FastAPI error handlers deal with it
            raise
