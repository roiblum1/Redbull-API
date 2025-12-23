"""Utilities package for MCE Cluster Generator.

This package is organized by domain:
- exceptions/ - Exception classes and error handling decorators
- logging/ - Logging configuration and utilities

For convenience, commonly used items are re-exported at package level.
"""

# Re-export commonly used items for convenience
from .exceptions import (
    MCEGeneratorError,
    TemplateError,
    ValidationError,
    GitOpsError,
    ConfigurationError,
    PathValidationError,
    handle_api_exceptions,
    handle_api_exceptions_sync,
)

from .logging import (
    get_logger,
    setup_logging,
    LoggingMixin,
)

__all__ = [
    # Exception classes
    "MCEGeneratorError",
    "TemplateError",
    "ValidationError",
    "GitOpsError",
    "ConfigurationError",
    "PathValidationError",
    # Exception decorators
    "handle_api_exceptions",
    "handle_api_exceptions_sync",
    # Logging
    "get_logger",
    "setup_logging",
    "LoggingMixin",
]