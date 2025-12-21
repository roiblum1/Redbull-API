"""Response models for API endpoints."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class ErrorResponse(BaseModel):
    """Error response model."""
    
    error: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")


class VendorInfo(BaseModel):
    """Vendor information model."""
    
    name: str = Field(..., description="Vendor identifier")
    display_name: str = Field(..., description="Human-readable vendor name")


class VersionInfo(BaseModel):
    """OpenShift version information."""
    
    version: str = Field(..., description="Version string (e.g., '4.16')")
    is_default: bool = Field(..., description="Whether this is the default version")


class ConfigInfo(BaseModel):
    """Configuration option information."""
    
    key: str = Field(..., description="Config key/identifier")
    name: str = Field(..., description="Config name as it appears in YAML")
    description: str = Field(..., description="Description of the config")
    is_optional: bool = Field(..., description="Whether this config is optional")


class DefaultsResponse(BaseModel):
    """Response model for getting default values."""
    
    vendors: List[VendorInfo] = Field(..., description="Available vendors")
    versions: List[VersionInfo] = Field(..., description="Available OpenShift versions")
    default_configs: List[str] = Field(..., description="Default configs always included")
    optional_configs: List[ConfigInfo] = Field(..., description="Optional configs")
    default_dns_domain: str = Field(..., description="Default DNS domain")


class GenerateClusterResponse(BaseModel):
    """Response model for cluster generation."""
    
    cluster_name: str = Field(..., description="Cluster name")
    yaml_content: str = Field(..., description="Generated YAML content")
    vendors_used: List[str] = Field(..., description="Vendors included in configuration")
    ocp_version: str = Field(..., description="OpenShift version used")
    nodepool_count: int = Field(..., description="Number of nodepools generated")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")
    message: str = Field(..., description="Success message")


class PreviewClusterResponse(BaseModel):
    """Response model for cluster preview."""
    
    cluster_name: str = Field(..., description="Cluster name")
    yaml_content: str = Field(..., description="Generated YAML content")
    vendors_used: List[str] = Field(..., description="Vendors included in configuration")
    ocp_version: str = Field(..., description="OpenShift version used")
    nodepool_count: int = Field(..., description="Number of nodepools generated")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")


class HealthResponse(BaseModel):
    """Health check response."""
    
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Application version")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Health check timestamp")
