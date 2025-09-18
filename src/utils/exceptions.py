"""Custom exceptions for MCE cluster generator."""


class MCEGeneratorError(Exception):
    """Base exception for MCE cluster generator errors."""
    
    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class TemplateError(MCEGeneratorError):
    """Exception raised for template-related errors."""
    
    def __init__(self, message: str, template_name: str = None, details: dict = None):
        super().__init__(message, details)
        self.template_name = template_name


class ValidationError(MCEGeneratorError):
    """Exception raised for validation errors."""
    
    def __init__(self, message: str, field_name: str = None, details: dict = None):
        super().__init__(message, details)
        self.field_name = field_name


class GitOpsError(MCEGeneratorError):
    """Exception raised for GitOps operations errors."""
    
    def __init__(self, message: str, operation: str = None, details: dict = None):
        super().__init__(message, details)
        self.operation = operation


class ConfigurationError(MCEGeneratorError):
    """Exception raised for configuration errors."""
    
    def __init__(self, message: str, config_key: str = None, details: dict = None):
        super().__init__(message, details)
        self.config_key = config_key


class PathValidationError(MCEGeneratorError):
    """Exception raised for path validation errors."""
    
    def __init__(self, message: str, path: str = None, details: dict = None):
        super().__init__(message, details)
        self.path = path