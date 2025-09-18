"""Configuration settings for MCE Cluster Generator API."""

import os
from pathlib import Path
from typing import Optional


class Settings:
    """Application settings."""
    
    # Application info
    APP_NAME: str = "MCE Cluster Generator API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "API for generating MCE cluster configurations with GitOps integration"
    
    # Server settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Logging settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: Optional[str] = os.getenv("LOG_FILE")
    
    # GitOps Repository Configuration
    GITOPS_REPO_URL: str = os.getenv("GITOPS_REPO_URL", "")
    GITOPS_REPO_PATH: str = os.getenv("GITOPS_REPO_PATH", "")
    GITOPS_BRANCH_BASE: str = os.getenv("GITOPS_BRANCH_BASE", "main")
    
    # Git authentication
    GIT_SSH_KEY_PATH: Optional[str] = os.getenv("GIT_SSH_KEY_PATH")  # Path to SSH private key
    GIT_USERNAME: Optional[str] = os.getenv("GIT_USERNAME")  # For HTTPS auth
    GIT_PASSWORD: Optional[str] = os.getenv("GIT_PASSWORD")  # For HTTPS auth or token
    
    # Git commit settings
    DEFAULT_AUTHOR_NAME: str = os.getenv("DEFAULT_AUTHOR_NAME", "MCE API")
    DEFAULT_AUTHOR_EMAIL: str = os.getenv("DEFAULT_AUTHOR_EMAIL", "mce-api@company.com")
    
    # Repository access mode
    REPO_ACCESS_MODE: str = os.getenv("REPO_ACCESS_MODE", "ssh")  # "ssh" or "https"
    
    # Template settings
    TEMPLATES_DIR: Optional[str] = os.getenv("TEMPLATES_DIR")
    
    # Private registry settings
    PRIVATE_REGISTRY: str = os.getenv("PRIVATE_REGISTRY", "registry.internal.company.com")
    
    # Security settings
    API_KEY: Optional[str] = os.getenv("API_KEY")
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "*")
    
    # Operational settings
    MAX_NODES: int = int(os.getenv("MAX_NODES", "100"))
    DEFAULT_FLAVOR: str = os.getenv("DEFAULT_FLAVOR", "default")
    
    @property
    def templates_path(self) -> Path:
        """Get templates directory path."""
        if self.TEMPLATES_DIR:
            return Path(self.TEMPLATES_DIR)
        return Path(__file__).parent / "templates"
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Get CORS origins as a list."""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


# Global settings instance
settings = Settings()