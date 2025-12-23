"""API decorators for cross-cutting concerns.

This module provides decorators for common API patterns:
- Exception handling
- Request validation
- Response formatting
"""

from functools import wraps
from typing import Callable, Any
from fastapi import HTTPException, status

from .exceptions import MCEGeneratorError
from utils.logging import get_logger

logger = get_logger(__name__)


def handle_api_exceptions(func: Callable) -> Callable:
    """Decorator to handle common API exceptions.

    This decorator provides consistent exception handling across all API endpoints:
    - MCEGeneratorError → 400 Bad Request
    - HTTPException → Re-raise as-is
    - Other exceptions → 500 Internal Server Error

    Usage:
        @router.post("/endpoint")
        @handle_api_exceptions
        async def my_endpoint(service: ClusterService = Depends(...)):
            return service.do_something()

    Args:
        func: The endpoint function to wrap

    Returns:
        Wrapped function with exception handling
    """
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await func(*args, **kwargs)
        except MCEGeneratorError as e:
            logger.error(f"Generator error in {func.__name__}: {e.message}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=e.message
            )
        except HTTPException:
            # Re-raise HTTPExceptions as-is (don't wrap them)
            raise
        except KeyError as e:
            # Handle flavor/resource not found errors
            logger.warning(f"Resource not found in {func.__name__}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        except Exception as e:
            # Catch-all for unexpected errors
            logger.error(
                f"Unexpected error in {func.__name__}: {e}",
                exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unexpected error: {str(e)}"
            )

    return wrapper


def handle_api_exceptions_sync(func: Callable) -> Callable:
    """Decorator to handle exceptions for synchronous endpoints.

    Similar to handle_api_exceptions but for synchronous (non-async) endpoints.

    Usage:
        @router.get("/endpoint")
        @handle_api_exceptions_sync
        def my_sync_endpoint(service: ClusterService = Depends(...)):
            return service.do_something()

    Args:
        func: The endpoint function to wrap

    Returns:
        Wrapped function with exception handling
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except MCEGeneratorError as e:
            logger.error(f"Generator error in {func.__name__}: {e.message}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=e.message
            )
        except HTTPException:
            raise
        except KeyError as e:
            logger.warning(f"Resource not found in {func.__name__}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        except Exception as e:
            logger.error(
                f"Unexpected error in {func.__name__}: {e}",
                exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unexpected error: {str(e)}"
            )

    return wrapper
