"""Exception handling utilities.

This package provides:
- Custom exception classes for the application
- Exception handling decorators for API endpoints
"""

from .exceptions import (
    MCEGeneratorError,
    TemplateError,
    ValidationError,
    GitOpsError,
    ConfigurationError,
    PathValidationError
)

from .decorators import (
    handle_api_exceptions,
    handle_api_exceptions_sync
)

__all__ = [
    # Exception classes
    "MCEGeneratorError",
    "TemplateError",
    "ValidationError",
    "GitOpsError",
    "ConfigurationError",
    "PathValidationError",
    # Decorators
    "handle_api_exceptions",
    "handle_api_exceptions_sync",
]
