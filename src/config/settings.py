"""Configuration settings for MCE Cluster Generator API."""

import os
from pathlib import Path
from typing import Optional, List


class Settings:
    """Application settings.
    
    This class centralizes all configuration for the application,
    loading from environment variables with sensible defaults.
    """
    
    # Application info
    APP_NAME: str = "MCE Cluster Generator API"
    APP_VERSION: str = "2.0.0"
    APP_DESCRIPTION: str = "API for generating MCE cluster configurations with UI"
    
    # Server settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Logging settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: Optional[str] = os.getenv("LOG_FILE")
    
    # Defaults settings
    DEFAULTS_DIR: Optional[str] = os.getenv("DEFAULTS_DIR")
    
    # Private registry settings
    PRIVATE_REGISTRY: str = os.getenv("PRIVATE_REGISTRY", "registry.internal.company.com")
    
    # Default DNS domain
    DEFAULT_DNS_DOMAIN: str = os.getenv("DEFAULT_DNS_DOMAIN", "example.company.com")
    
    # Default OpenShift version
    DEFAULT_OCP_VERSION: str = os.getenv("DEFAULT_OCP_VERSION", "4.16")
    
    # Security settings
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "*")
    
    # Operational settings
    MAX_NODES: int = int(os.getenv("MAX_NODES", "100"))
    
    # Supported versions (comma-separated in env var)
    SUPPORTED_VERSIONS: List[str] = os.getenv(
        "SUPPORTED_VERSIONS", "4.15,4.16"
    ).split(",")
    
    # Supported vendors (comma-separated in env var)
    SUPPORTED_VENDORS: List[str] = os.getenv(
        "SUPPORTED_VENDORS", 
        "cisco,dell,dell-data,h100-gpu,h200-gpu"
    ).split(",")
    
    @property
    def defaults_path(self) -> Path:
        """Get defaults directory path."""
        if self.DEFAULTS_DIR:
            return Path(self.DEFAULTS_DIR)
        return Path(__file__).parent / "defaults"
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Get CORS origins as a list."""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
    
    @property
    def static_files_path(self) -> Path:
        """Get static files directory path for UI."""
        return Path(__file__).parent / "static"


# Global settings instance
settings = Settings()
