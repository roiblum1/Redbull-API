"""Logging configuration for MCE cluster generator."""

import logging
import logging.handlers
import sys
import time
from pathlib import Path
from typing import Optional, Callable, Any
from functools import wraps
from rich.logging import RichHandler
from rich.console import Console


def setup_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    enable_rich: bool = True,
    console: Optional[Console] = None
) -> logging.Logger:
    """Setup comprehensive logging configuration.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_file: Optional file path for logging to file.
        enable_rich: Whether to use rich console logging.
        console: Optional Rich console instance.
        
    Returns:
        Configured logger instance.
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create root logger
    logger = logging.getLogger("mce_cluster_generator")
    logger.setLevel(numeric_level)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Console handler
    if enable_rich:
        console_handler = RichHandler(
            console=console,
            show_time=True,
            show_path=False,
            rich_tracebacks=True
        )
        console_handler.setFormatter(
            logging.Formatter(fmt="%(message)s", datefmt="[%X]")
        )
    else:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
    
    console_handler.setLevel(numeric_level)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)  # File gets all levels
        logger.addHandler(file_handler)
    
    # Set levels for external libraries
    logging.getLogger("git").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    
    logger.info(f"Logging initialized with level: {level}")
    if log_file:
        logger.info(f"File logging enabled: {log_file}")
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a specific module.
    
    Args:
        name: Logger name (typically __name__).
        
    Returns:
        Logger instance.
    """
    return logging.getLogger(f"mce_cluster_generator.{name}")


class LoggingMixin:
    """Mixin class to add logging capabilities to any class."""
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class."""
        return get_logger(self.__class__.__name__)
    
    def log_operation_start(self, operation: str, **kwargs) -> None:
        """Log the start of an operation.
        
        Args:
            operation: Name of the operation.
            **kwargs: Additional context to log.
        """
        context = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
        self.logger.info(f"Starting {operation}" + (f" with {context}" if context else ""))
    
    def log_operation_success(self, operation: str, **kwargs) -> None:
        """Log successful completion of an operation.
        
        Args:
            operation: Name of the operation.
            **kwargs: Additional context to log.
        """
        context = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
        self.logger.info(f"Successfully completed {operation}" + (f" with {context}" if context else ""))
    
    def log_operation_error(self, operation: str, error: Exception, **kwargs) -> None:
        """Log an error during operation.

        Args:
            operation: Name of the operation.
            error: Exception that occurred.
            **kwargs: Additional context to log.
        """
        context = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
        self.logger.error(
            f"Error in {operation}: {error}" + (f" (context: {context})" if context else ""),
            exc_info=True
        )


def log_execution(level: str = "INFO", include_args: bool = True, include_result: bool = False):
    """Decorator to automatically log function entry, exit, and execution time.

    This decorator reduces boilerplate logging code by automatically logging:
    - Function entry with arguments (optional)
    - Function exit with result (optional)
    - Execution time
    - Any exceptions that occur

    Args:
        level: Logging level to use (DEBUG, INFO, WARNING, ERROR)
        include_args: Whether to log function arguments (default: True)
        include_result: Whether to log the return value (default: False, to avoid logging large responses)

    Example:
        @log_execution(level="INFO", include_args=True)
        def generate_cluster(self, request):
            # Automatically logs:
            # - "Executing generate_cluster with args: request=..."
            # - "Completed generate_cluster in 1.23s"
            return result

    Usage:
        from utils.logging import log_execution

        @log_execution(level="INFO")
        def my_function(arg1, arg2):
            return result
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            logger = get_logger(func.__module__)
            func_name = func.__name__

            # Build argument string for logging
            arg_str = ""
            if include_args and (args or kwargs):
                # Skip 'self' or 'cls' arguments for cleaner logs
                start_idx = 1 if args and hasattr(args[0], func_name) else 0
                args_repr = [repr(a) for a in args[start_idx:]]
                kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
                arg_str = ", ".join(args_repr + kwargs_repr)
                if arg_str:
                    arg_str = f" with args: {arg_str}"

            # Log entry
            log_method = getattr(logger, level.lower(), logger.info)
            log_method(f"Executing {func_name}{arg_str}")

            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time

                # Log successful completion
                result_str = ""
                if include_result:
                    result_str = f" with result: {result!r}"
                log_method(f"Completed {func_name} in {execution_time:.2f}s{result_str}")

                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"Error in {func_name} after {execution_time:.2f}s: {e}", exc_info=True)
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            logger = get_logger(func.__module__)
            func_name = func.__name__

            # Build argument string for logging
            arg_str = ""
            if include_args and (args or kwargs):
                # Skip 'self' or 'cls' arguments for cleaner logs
                start_idx = 1 if args and hasattr(args[0], func_name) else 0
                args_repr = [repr(a) for a in args[start_idx:]]
                kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
                arg_str = ", ".join(args_repr + kwargs_repr)
                if arg_str:
                    arg_str = f" with args: {arg_str}"

            # Log entry
            log_method = getattr(logger, level.lower(), logger.info)
            log_method(f"Executing {func_name}{arg_str}")

            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time

                # Log successful completion
                result_str = ""
                if include_result:
                    result_str = f" with result: {result!r}"
                log_method(f"Completed {func_name} in {execution_time:.2f}s{result_str}")

                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"Error in {func_name} after {execution_time:.2f}s: {e}", exc_info=True)
                raise

        # Return appropriate wrapper based on function type
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator